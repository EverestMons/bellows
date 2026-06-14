"""Executes plan steps via claude -p. Manages session IDs."""

import json
import os
import subprocess
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

from bellows import _log
from bellows_root import resolve_bellows_root
from parser import parse
import decisions

# Prevent Claude Code auto-updater from shifting agent behavior mid-plan.
# setdefault respects explicit operator overrides.  (executable-disable-autoupdater-2026-05-27)
os.environ.setdefault("DISABLE_AUTOUPDATER", "1")

BELLOWS_ROOT = resolve_bellows_root()
LOGS_DIR = BELLOWS_ROOT / "logs"

BELLOWS_AGENT_SYSTEM_PROMPT = """You are executing as a Bellows-dispatched agent. BINDING CONSTRAINT: You must NEVER move plan files to Done/. You must NEVER execute mv, shutil.move, os.rename, or any equivalent operation targeting a Done/ directory within the knowledge/decisions/ tree. The Planner performs all Done/ moves after verification. Your final operation is ALWAYS the commit. If you find yourself reasoning about moving files to Done/, STOP — that is not your responsibility."""


def _write_log(log_path: Path, data: dict):
    """Write a JSON log file. Called on every code path (success, timeout, error)."""
    LOGS_DIR.mkdir(exist_ok=True)
    with open(log_path, "w") as f:
        json.dump(data, f, indent=2, default=str)


def run_step(
    prompt: str,
    project_path: str,
    model: str,
    session_id: Optional[str] = None,
    allowed_tools: str = "Read,Edit,Write,Bash",
    timeout: int = 300,
    plan_slug: Optional[str] = None,
    step_num: Optional[int] = None,
    _retry_attempted: bool = False,  # internal retry guard — do NOT pass externally
) -> dict:
    cmd = [
        "claude", "-p", prompt,
        "--output-format", "stream-json",
        "--verbose",
        "--model", model,
        "--allowedTools", allowed_tools,
        "--append-system-prompt", BELLOWS_AGENT_SYSTEM_PROMPT,
    ]
    if session_id is not None:
        cmd += ["--resume", session_id]

    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    log_path = LOGS_DIR / f"{timestamp}-step.json"
    start_time = time.monotonic()
    max_wall_clock = timeout * 10

    try:
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=project_path,
        )
    except Exception as e:
        _write_log(log_path, {
            "success": False,
            "error": str(e),
            "exception_type": type(e).__name__,
        })
        return {
            "is_error": True,
            "error": str(e),
            "session_id": None,
            "escalate": True,
            "receipt_status": "Blocked",
            "ceo_flags": [f"Step failed: {str(e)[:200]}"],
            "cost_usd": None,
            "stop_reason": "error",
            "result_text": "",
            "permission_denials": [],
            "verdict_requested": {"requested": False, "reason": None},
        }

    # Shared state for streaming reader threads
    stdout_buf = []
    stderr_buf = []
    last_output_time = time.monotonic()
    lock = threading.Lock()

    def _read_stream(stream, buf):
        nonlocal last_output_time
        try:
            for line in stream:
                with lock:
                    buf.append(line)
                    last_output_time = time.monotonic()
        except Exception:
            pass

    stdout_thread = threading.Thread(target=_read_stream, args=(proc.stdout, stdout_buf), daemon=True)
    stderr_thread = threading.Thread(target=_read_stream, args=(proc.stderr, stderr_buf), daemon=True)
    stdout_thread.start()
    stderr_thread.start()

    last_heartbeat = start_time
    timed_out = False
    wall_clock_hit = False

    while proc.poll() is None:
        time.sleep(1)
        now = time.monotonic()
        elapsed = now - start_time

        with lock:
            age = now - last_output_time

        # Heartbeat every 60s
        if now - last_heartbeat >= 60:
            _log("INFO", f"runner: {int(elapsed)}s elapsed, last output {int(age)}s ago (step {step_num})", slug=plan_slug, suppress_timer_update=True)
            last_heartbeat = now

        # Inactivity timeout
        if age >= timeout:
            _log("ERROR", f"runner: inactivity timeout ({timeout}s with no output), killing process (step {step_num})", slug=plan_slug, suppress_timer_update=True)
            proc.kill()
            timed_out = True
            break

        # Hard wall-clock safety cap
        if elapsed >= max_wall_clock:
            _log("ERROR", f"runner: hard wall-clock cap reached ({max_wall_clock}s), killing process (step {step_num})", slug=plan_slug, suppress_timer_update=True)
            proc.kill()
            timed_out = True
            wall_clock_hit = True
            break

    # Wait for reader threads to finish draining
    stdout_thread.join(timeout=5)
    stderr_thread.join(timeout=5)

    result_stdout = "".join(stdout_buf)
    result_stderr = "".join(stderr_buf)
    elapsed = time.monotonic() - start_time

    # --- Timeout path ---
    if timed_out:
        timeout_type = "wall_clock_cap" if wall_clock_hit else "inactivity"
        _write_log(log_path, {
            "success": False,
            "error": "timeout",
            "timeout_type": timeout_type,
            "elapsed_seconds": round(elapsed, 1),
            "stderr_partial": result_stderr[:5000],
            "raw_output": result_stdout[:5000],
        })
        return {
            "is_error": True,
            "error": "timeout",
            "session_id": None,
            "escalate": True,
            "receipt_status": "Blocked",
            "ceo_flags": [f"Step timed out ({timeout_type}) after {int(elapsed)}s"],
            "cost_usd": None,
            "stop_reason": "timeout",
            "result_text": result_stdout[:5000],
            "permission_denials": [],
            "verdict_requested": {"requested": False, "reason": None},
        }

    # --- Non-zero exit path ---
    if proc.returncode != 0:
        # Transient-failure retry guard. Eligibility is implicit inside this branch
        # (no parsed result event yet means no cost or permission decisions have landed).
        transient_patterns = ["401", "unauthorized", "authentication", "429", "rate limit", "too many requests"]
        stderr_lower = (result_stderr or "").lower()
        transient_hit = next((p for p in transient_patterns if p in stderr_lower), None)
        if transient_hit is not None and not _retry_attempted:
            _log("INFO", f"runner: transient failure detected ({transient_hit!r} in stderr); retrying once in 5s (step {step_num})", slug=plan_slug)
            time.sleep(5)
            _log("INFO", f"runner: retry dispatch starting (step {step_num})", slug=plan_slug)
            return run_step(prompt, project_path, model, session_id, allowed_tools, timeout, plan_slug, step_num, _retry_attempted=True)

        if result_stderr:
            _log("WARN", f"runner: stderr from claude -p: {result_stderr[:500]}", slug=plan_slug)
        _write_log(log_path, {
            "success": False,
            "error": f"non_zero_exit_{proc.returncode}",
            "raw_output": result_stdout[:5000],
            "stderr": result_stderr[:5000],
        })
        return {
            "is_error": True,
            "error": f"claude -p exited with code {proc.returncode}",
            "session_id": None,
            "escalate": True,
            "receipt_status": "Blocked",
            "ceo_flags": [f"claude -p exit code {proc.returncode}"],
            "cost_usd": None,
            "stop_reason": "error",
            "result_text": "",
            "permission_denials": [],
            "verdict_requested": {"requested": False, "reason": None},
        }

    # --- Success path ---
    if result_stderr:
        _log("WARN", f"runner: stderr from claude -p: {result_stderr[:500]}", slug=plan_slug)

    # --- Parse NDJSON stream, extract terminal result event ---
    result_event = None
    assistant_text_parts = []
    for line in result_stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            _log("WARN", f"runner: skipping malformed NDJSON line: {line[:200]}", slug=plan_slug)
            continue
        if isinstance(event, dict):
            if event.get("type") == "result":
                result_event = event
            elif event.get("type") == "assistant":
                # Collect text from intermediate assistant turns so ### Ledger Updates
                # is found even when emitted in a non-final turn (plan 54 fix).
                for block in event.get("message", {}).get("content", []):
                    if isinstance(block, dict) and block.get("type") == "text":
                        assistant_text_parts.append(block.get("text", ""))

    if result_event is None:
        _write_log(log_path, {
            "success": False,
            "error": "no_result_event",
            "raw_output": result_stdout[:5000],
            "stderr": result_stderr[:5000],
        })
        return {
            "is_error": True,
            "error": "no_result_event: stream completed without a result event",
            "session_id": None,
            "escalate": True,
            "receipt_status": "Blocked",
            "ceo_flags": ["claude -p stream ended without result event"],
            "cost_usd": None,
            "stop_reason": "error",
            "result_text": "",
            "permission_denials": [],
            "verdict_requested": {"requested": False, "reason": None},
        }

    # Concatenate all assistant text (intermediate turns + final result) so the
    # parser can find ### Ledger Updates regardless of which turn carried it.
    _all_text = "\n".join(assistant_text_parts)
    if result_event.get("result"):
        _all_text += "\n" + result_event["result"]
    result_event["_all_assistant_text"] = _all_text

    raw = result_event

    try:
        parsed = parse(raw)
    except Exception as e:
        _write_log(log_path, {
            "success": False,
            "error": f"parse_error: {str(e)[:200]}",
            "raw_output": result_stdout[:5000],
            "stderr": result_stderr[:5000],
        })
        return {
            "is_error": True,
            "error": f"parse_error: {str(e)[:200]}",
            "session_id": None,
            "escalate": True,
            "receipt_status": "Blocked",
            "ceo_flags": ["Parser failed on claude -p output"],
            "cost_usd": None,
            "stop_reason": "error",
            "result_text": "",
            "permission_denials": [],
            "verdict_requested": {"requested": False, "reason": None},
        }

    # Extract intermediate decisions from assistant text blocks
    intermediate_decisions = decisions.extract_decision_blocks(
        result_stdout, decisions.load_phrases()
    )

    _write_log(log_path, {
        "success": True,
        "raw_output": result_stdout,
        "stderr": result_stderr,
        "parsed": parsed,
    })

    parsed["intermediate_decisions"] = intermediate_decisions
    return parsed
