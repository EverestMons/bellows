"""Executes plan steps via claude -p. Manages session IDs."""

import json
import os
import re
import subprocess
import threading
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional
from zoneinfo import ZoneInfo

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


def _parse_session_reset(result_text: str, plan_slug: Optional[str] = None) -> float:
    """Extract reset wall-clock time + IANA zone from a session-limit result string.

    Returns the next-future epoch for that wall-clock time in that zone.
    Falls back to now + 5h if the time or zone cannot be parsed.
    """
    m = re.search(
        r'resets\s+(\d{1,2})(?::(\d{2}))?\s*(am|pm)\s*\(([^)]+)\)',
        result_text, re.IGNORECASE,
    )
    if not m:
        _log("WARN", f"runner: could not parse session-limit reset time from: {result_text[:200]}", slug=plan_slug)
        return time.time() + 5 * 3600

    hour = int(m.group(1))
    minute = int(m.group(2)) if m.group(2) else 0
    ampm = m.group(3).lower()
    tz_name = m.group(4).strip()

    if ampm == "pm" and hour != 12:
        hour += 12
    elif ampm == "am" and hour == 12:
        hour = 0

    try:
        tz = ZoneInfo(tz_name)
    except Exception:
        _log("WARN", f"runner: unknown timezone {tz_name!r} in session-limit reset; using 5h fallback", slug=plan_slug)
        return time.time() + 5 * 3600

    now = datetime.now(tz)
    reset_today = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    if reset_today <= now:
        reset_today += timedelta(days=1)

    return reset_today.timestamp()


def _check_session_limit(result_event: dict) -> Optional[dict]:
    """Check whether a result event represents a parkable session limit.

    Returns a dict with session_limit fields if parkable, None otherwise.
    A 429 session-limit result with progress (turns/cost > 0) is NOT parkable.
    """
    if not (result_event.get("is_error") and result_event.get("api_error_status") == 429):
        return None

    result_lower = (result_event.get("result") or "").lower()
    if "session limit" not in result_lower and "usage limit" not in result_lower:
        return None

    num_turns = result_event.get("num_turns") or 0
    total_cost = float(result_event.get("total_cost_usd") or 0)
    output_tokens = int((result_event.get("usage") or {}).get("output_tokens") or 0)

    if num_turns > 1 or total_cost > 0 or output_tokens > 0:
        return None

    resets_at_raw = result_event.get("result", "")
    resets_at_epoch = _parse_session_reset(resets_at_raw)

    return {
        "session_limit": True,
        "resets_at_epoch": resets_at_epoch,
        "resets_at_raw": resets_at_raw,
    }


def _reset_epoch_from_rate_limit_event(rate_limit_info: dict, plan_slug: Optional[str] = None) -> float:
    """Extract reset epoch from a rate_limit_event's rate_limit_info dict."""
    resets_at = rate_limit_info.get("resetsAt")
    if isinstance(resets_at, (int, float)) and resets_at > 0:
        return float(resets_at)
    _log("WARN", "runner: rate_limit_event missing/invalid resetsAt, using 5h fallback", slug=plan_slug)
    return time.time() + 5 * 3600


def _check_exit1_rate_limit(result_stdout: str, plan_slug: Optional[str] = None) -> Optional[dict]:
    """Scan an exit-1 NDJSON stream for a parkable five_hour rate-limit cap hit.

    Returns {session_limit, resets_at_epoch, resets_at_raw} when a five_hour
    rate_limit_event is found AND the stream shows zero committable progress.
    Returns None otherwise (falls through to gate_failure).
    """
    five_hour_event = None
    num_turns = 0
    total_output_tokens = 0
    has_mutating_tool_use = False
    mutating_tools = {"Write", "Edit", "Bash", "NotebookEdit"}

    for line in result_stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            event = json.loads(line)
        except (json.JSONDecodeError, ValueError):
            continue
        if not isinstance(event, dict):
            continue

        event_type = event.get("type")

        if event_type == "rate_limit_event":
            info = event.get("rate_limit_info", {})
            if info.get("rateLimitType") == "five_hour":
                five_hour_event = event

        elif event_type == "user":
            content = event.get("message", {}).get("content", [])
            if isinstance(content, list):
                for block in content:
                    if isinstance(block, dict) and block.get("type") == "tool_result":
                        num_turns += 1
                        break

        elif event_type == "assistant":
            usage = event.get("message", {}).get("usage", {})
            total_output_tokens += int(usage.get("output_tokens", 0) or 0)
            content = event.get("message", {}).get("content", [])
            if isinstance(content, list):
                for block in content:
                    if isinstance(block, dict) and block.get("type") == "tool_use":
                        if block.get("name") in mutating_tools:
                            has_mutating_tool_use = True

    if five_hour_event is None:
        return None

    # Only committable progress (mutating tool use) blocks a park.
    # turns/tokens are log-only — exec-194 proved read-only tool_results
    # (turns=4, mutating=False) false-blocked every real step.
    # bellows._maybe_park_session_limit has a commit-check backstop
    # (worktree HEAD vs baseline) that catches any stranded commits.
    if has_mutating_tool_use:
        _log("INFO", f"runner: five_hour rate_limit_event found but step made committable progress "
             f"(mutating tool use; turns={num_turns}, tokens={total_output_tokens}); "
             f"not parking", slug=plan_slug)
        return None

    rate_limit_info = five_hour_event.get("rate_limit_info", {})
    resets_at_epoch = _reset_epoch_from_rate_limit_event(rate_limit_info, plan_slug)

    _log("INFO", f"runner: five_hour event + no committable progress "
         f"(turns={num_turns}, tokens={total_output_tokens}, mutating=False); parking",
         slug=plan_slug)

    return {
        "session_limit": True,
        "resets_at_epoch": resets_at_epoch,
        "resets_at_raw": rate_limit_info,
    }


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
        # Transient-failure retry guard (stderr only). Session-limit 429s arrive on
        # the stdout result event in the success path — they never reach here.
        transient_patterns = ["401", "unauthorized", "authentication", "429", "rate limit", "too many requests"]
        stderr_lower = (result_stderr or "").lower()
        transient_hit = next((p for p in transient_patterns if p in stderr_lower), None)
        if transient_hit is not None and not _retry_attempted:
            _log("INFO", f"runner: transient failure detected ({transient_hit!r} in stderr); retrying once in 5s (step {step_num})", slug=plan_slug)
            time.sleep(5)
            _log("INFO", f"runner: retry dispatch starting (step {step_num})", slug=plan_slug)
            return run_step(prompt, project_path, model, session_id, allowed_tools, timeout, plan_slug, step_num, _retry_attempted=True)

        # Exit-1 rate-limit park detection: scan stdout stream for five_hour cap event
        exit1_sl = _check_exit1_rate_limit(result_stdout, plan_slug)
        if exit1_sl is not None:
            _log("INFO", f"runner: exit-1 rate-limit detected (five_hour cap), "
                 f"resets_at_epoch={exit1_sl['resets_at_epoch']:.0f} (step {step_num})", slug=plan_slug)
            if result_stderr:
                _log("WARN", f"runner: stderr from claude -p: {result_stderr[:500]}", slug=plan_slug)
            _write_log(log_path, {
                "success": False,
                "error": f"non_zero_exit_{proc.returncode}",
                "session_limit": True,
                "resets_at_epoch": exit1_sl["resets_at_epoch"],
                "resets_at_raw": exit1_sl["resets_at_raw"],
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
                "stop_reason": "session_limit",
                "result_text": "",
                "permission_denials": [],
                "verdict_requested": {"requested": False, "reason": None},
                "session_limit": True,
                "resets_at_epoch": exit1_sl["resets_at_epoch"],
                "resets_at_raw": exit1_sl["resets_at_raw"],
            }

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
                    # Plan 60 fix: also capture content from Write/Edit tool_use
                    # blocks — an Output Receipt emitted inside a file-write was
                    # invisible to _all_assistant_text (plan 57 root cause).
                    elif isinstance(block, dict) and block.get("type") == "tool_use":
                        tool_name = block.get("name", "")
                        tool_input = block.get("input") or {}
                        if tool_name == "Write":
                            tc = tool_input.get("content", "")
                            if tc:
                                assistant_text_parts.append(tc)
                        elif tool_name == "Edit":
                            tc = tool_input.get("new_string", "")
                            if tc:
                                assistant_text_parts.append(tc)

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

    # --- Session-limit detection (stdout result event, distinct from stderr transient retry) ---
    sl = _check_session_limit(raw)
    if sl is not None:
        _log("INFO", f"runner: session-limit detected, resets_at_epoch={sl['resets_at_epoch']:.0f} (step {step_num})", slug=plan_slug)
        _write_log(log_path, {
            "success": False,
            "session_limit": True,
            "resets_at_epoch": sl["resets_at_epoch"],
            "resets_at_raw": sl["resets_at_raw"],
            "raw_output": result_stdout[:5000],
            "stderr": result_stderr[:5000],
        })
        parsed["session_limit"] = True
        parsed["resets_at_epoch"] = sl["resets_at_epoch"]
        parsed["resets_at_raw"] = sl["resets_at_raw"]
        parsed["stop_reason"] = "session_limit"
        parsed["is_error"] = True
        parsed["receipt_status"] = "Blocked"
        parsed["escalate"] = True
        parsed["intermediate_decisions"] = []
        return parsed

    if raw.get("is_error") and raw.get("api_error_status") == 429:
        result_lower = (raw.get("result") or "").lower()
        if "session limit" in result_lower or "usage limit" in result_lower:
            _log("WARN", f"runner: session-limit 429 but step had progress (turns={raw.get('num_turns')}, cost={raw.get('total_cost_usd')}); not parking (step {step_num})", slug=plan_slug)

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
