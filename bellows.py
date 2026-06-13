"""Entry point. Initializes watcher and starts the orchestration loop."""

import fcntl
import json
import logging
from logging.handlers import RotatingFileHandler
import os
import pathlib
import re
import shutil
import sqlite3
import subprocess
import sys
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

# Prevent Claude Code auto-updater from shifting agent behavior mid-plan.
# setdefault respects explicit operator overrides.  (executable-disable-autoupdater-2026-05-27)
os.environ.setdefault("DISABLE_AUTOUPDATER", "1")

BELLOWS_ROOT = Path(__file__).parent.resolve()
DB_PATH = str(BELLOWS_ROOT / "bellows.db")
SHADOW_CACHE_DIR = BELLOWS_ROOT / ".bellows-cache"
MODULE_FINGERPRINT_HEARTBEAT_INTERVAL = 10

# --- Misplaced verdict scan ---
_NOTIFIED_MISPLACED: set[tuple[str, str]] = set()
MISPLACED_VERDICT_SCAN_VERBOSE = False

# --- No-match verdict WARN dedup ---
# Suppresses repeat "no verdict-pending plan found" WARNs for the same resolved/ filename.
# Logged once per file; cleared when the file leaves resolved/ (match or stale move).
# Module-level scope means daemon startup automatically resets the set.
_warned_no_match: set[str] = set()


# --- Terminal output infrastructure ---
_last_plan_event_time = 0.0
_plan_event_lock = threading.Lock()


def _log(level: str, message: str, slug: Optional[str] = None, suppress_timer_update: bool = False) -> None:
    """Emit a log line: HH:MM:SS [LEVEL] [slug] message

    level: one of EVENT, INFO, WARN, ERROR, PAUSE
    message: the message text
    slug: optional plan slug for plan-related events
    suppress_timer_update: if True, skip _last_plan_event_time update (for runner heartbeats)
    """
    global _last_plan_event_time
    valid_levels = {"EVENT", "INFO", "WARN", "ERROR", "PAUSE"}
    if level not in valid_levels:
        raise ValueError(f"Invalid log level '{level}', must be one of {valid_levels}")
    ts = datetime.now().strftime('%H:%M:%S')
    if slug:
        formatted = f"{ts} [{level}] [{slug}] {message}"
    else:
        formatted = f"{ts} [{level}] {message}"
    logger = logging.getLogger("bellows")
    if logger.handlers:
        logger.info(formatted)
    else:
        print(formatted)
    if not suppress_timer_update and level in {"EVENT", "WARN", "ERROR", "PAUSE"} and slug is not None:
        with _plan_event_lock:
            _last_plan_event_time = time.time()


def slug_for(plan_name: str) -> str:
    """Derive a short slug from plan filename for log tagging."""
    s = plan_name
    if s.endswith(".md"):
        s = s[:-3]
    for prefix in ("in-progress-", "verdict-pending-", "halted-"):
        if s.startswith(prefix):
            s = s[len(prefix):]
            break
    s = re.sub(r'-\d{4}-\d{2}-\d{2}$', '', s)
    return s[:30]


def _rotate_logs() -> None:
    """Age-based cleanup at startup. Logs deletions via print() (logger not yet configured)."""
    now = time.time()
    terminal_dir = os.path.join(str(BELLOWS_ROOT), "logs", "terminal")
    if os.path.isdir(terminal_dir):
        for fname in os.listdir(terminal_dir):
            fpath = os.path.join(terminal_dir, fname)
            if os.path.isfile(fpath) and (now - os.path.getmtime(fpath)) > 14 * 86400:
                os.remove(fpath)
                print(f"Bellows: rotated terminal log {fname} (>14 days)")
    logs_dir = os.path.join(str(BELLOWS_ROOT), "logs")
    if os.path.isdir(logs_dir):
        for fname in os.listdir(logs_dir):
            if not fname.endswith(".json"):
                continue
            fpath = os.path.join(logs_dir, fname)
            if os.path.isfile(fpath) and (now - os.path.getmtime(fpath)) > 30 * 86400:
                os.remove(fpath)
                print(f"Bellows: rotated step JSON {fname} (>30 days)")
    consult_path = os.path.join(logs_dir, "planner-consultation.jsonl")
    if os.path.isfile(consult_path) and os.path.getsize(consult_path) > 10 * 1024 * 1024:
        old_path = consult_path + ".1"
        if os.path.exists(old_path):
            os.remove(old_path)
        os.rename(consult_path, old_path)
        print(f"Bellows: rotated planner-consultation.jsonl (>10MB)")


class WorktreeCreationError(Exception):
    """Raised when git worktree creation fails after retry."""
    pass


class WorktreeTeardownError(Exception):
    """Raised when worktree teardown fails (e.g. merge conflict, legacy worktree)."""
    pass

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

import runner
import parser
import gates
import verdict
import notifier
import server
import validators
import lifecycle


def load_config(path: str = "config.json") -> dict:
    # Two-file config layout:
    #   config.json          — operational settings (committed to git)
    #   config.secrets.json  — credentials & sensitive values (gitignored)
    # The loader reads both and deep-merges secrets into operational.
    # If config.secrets.json is missing, operational config is returned
    # as-is (Pushover notifications will silently no-op).
    config_path = BELLOWS_ROOT / path
    with open(config_path, "r") as f:
        config = json.load(f)

    secrets_path = config_path.parent / "config.secrets.json"
    if secrets_path.exists():
        with open(secrets_path, "r") as f:
            secrets = json.load(f)
        for key, value in secrets.items():
            if isinstance(value, dict) and isinstance(config.get(key), dict):
                config[key].update(value)
            else:
                config[key] = value
    else:
        _log("WARN", "config.secrets.json not found — running without secrets (Pushover disabled)")

    return config


def migrate_db():
    """Ensure bellows.db schema is current. Safe to run on every startup."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """CREATE TABLE IF NOT EXISTS runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            plan_path TEXT,
            project TEXT,
            session_id TEXT,
            step INTEGER,
            status TEXT,
            cost REAL,
            plan_slug TEXT
        )"""
    )
    # Add any missing columns idempotently
    existing = {row[1] for row in conn.execute("PRAGMA table_info(runs)")}
    additions = {
        "timestamp": "TEXT",
        "plan_path": "TEXT",
        "project": "TEXT",
        "session_id": "TEXT",
        "step": "INTEGER",
        "status": "TEXT",
        "cost": "REAL",
        "plan_slug": "TEXT",
    }
    for col, col_type in additions.items():
        if col not in existing:
            conn.execute(f"ALTER TABLE runs ADD COLUMN {col} {col_type}")
            _log("INFO", f"migrated DB — added column {col}")
    conn.commit()
    conn.close()


def load_file(path: str) -> str:
    try:
        with open(path, "r") as f:
            return f.read()
    except FileNotFoundError:
        return ""


def extract_step_number(plan_text: str, result_text: str) -> int:
    match = re.search(r"\*\*Step:\*\*\s*(\d+)", result_text)
    if match:
        return int(match.group(1))
    return 1


def strip_fenced_code_blocks(text: str) -> str:
    """Remove fenced code blocks (``` ... ```) from text, preserving line structure.

    Used by plan-text parsers to prevent example/fixture headers inside code fences
    from being parsed as structural elements.
    Duplicated in gates.py and verdict.py to avoid circular import — keep in sync.
    """
    return re.sub(r"^```[^\n]*\n.*?^```[^\n]*$", "", text, flags=re.MULTILINE | re.DOTALL)


def extract_total_steps(plan_text: str) -> int:
    plan_text = strip_fenced_code_blocks(plan_text)
    case_insensitive_count = len(re.findall(r"^## STEP\s+\d+", plan_text, re.MULTILINE | re.IGNORECASE))
    case_sensitive_count = len(re.findall(r"^## STEP\s+\d+", plan_text, re.MULTILINE))
    if case_insensitive_count > 0 and case_sensitive_count == 0:
        _log("WARN", f"⚠️ plan has step headers but case does not match expected '## STEP N' — count={case_insensitive_count} matched case-insensitively")
    return case_insensitive_count


def _shadow_path(plan_filename: str) -> Path:
    """Return the shadow cache path for a given plan filename."""
    # Strip lifecycle prefixes to get the canonical name
    canonical = plan_filename
    for prefix in ("in-progress-", "verdict-pending-", "halted-"):
        if canonical.startswith(prefix):
            canonical = canonical[len(prefix):]
            break
    return SHADOW_CACHE_DIR / f"{canonical}.pristine"


def _write_shadow(plan_filename: str, plan_text: str):
    """Write pristine plan content to shadow cache."""
    SHADOW_CACHE_DIR.mkdir(exist_ok=True)
    path = _shadow_path(plan_filename)
    path.write_text(plan_text)


def _read_shadow(plan_filename: str) -> Optional[str]:
    """Read shadow copy if it exists, else return None."""
    path = _shadow_path(plan_filename)
    if path.exists():
        return path.read_text()
    return None


def _delete_shadow(plan_filename: str):
    """Delete shadow copy if it exists."""
    path = _shadow_path(plan_filename)
    if path.exists():
        path.unlink()


def _cleanup_verdicts_for_slug(slug: str, verdicts_root: Optional[Path] = None) -> int:
    """Remove all verdict-request files for a given plan slug from verdicts/pending/.
    Returns count of files removed."""
    pending_dir = verdicts_root if verdicts_root is not None else BELLOWS_ROOT / "verdicts" / "pending"
    matches = list(pending_dir.glob(f"verdict-request-{slug}-step-*.md"))
    for f in matches:
        f.unlink()
    count = len(matches)
    if count > 0:
        _log("INFO", f"cleaned {count} pending verdict(s)", slug=slug)
    return count


def record_run(
    db_path: str,
    plan_path: str,
    project: str,
    session_id: str,
    step: int,
    status: str,
    cost: float,
    plan_slug: str,
):
    conn = sqlite3.connect(db_path)
    conn.execute(
        """CREATE TABLE IF NOT EXISTS runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            plan_path TEXT,
            project TEXT,
            session_id TEXT,
            step INTEGER,
            status TEXT,
            cost REAL,
            plan_slug TEXT
        )"""
    )
    conn.execute(
        "INSERT INTO runs (timestamp, plan_path, project, session_id, step, status, cost, plan_slug) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (datetime.now().isoformat(), plan_path, project, session_id, step, status, cost, plan_slug),
    )
    conn.commit()
    conn.close()


def is_final_step(step: int, total_steps: int) -> bool:
    return step >= total_steps


def recover_plan_id_from_filename(plan_filename: str) -> Optional[int]:
    """Recover the integer plan_id from an id-canonical in-progress filename of
    the form in-progress-<type>-<id>.md (G1, diagnostic 6).

    The resume path re-enters run_plan() with the plan file already named
    in-progress-*, so the mint-and-claim block is skipped and plan_id would
    otherwise stay None — silently dropping every lifecycle write (and the [id]
    commit tag) for resumed steps. This recovers the id from the filename.

    Legacy slug+date in-progress names (e.g. in-progress-executable-foo-bar-
    2026-05-28.md) are tolerated indefinitely: only the exact <type>-<int>.md
    form matches, so anything else returns None and lifecycle writes degrade
    silently exactly as before — no exception, no WARN spam.
    """
    m = re.fullmatch(r"in-progress-(?:diagnostic|executable|qa)-(\d+)\.md", plan_filename)
    return int(m.group(1)) if m else None


def header_says_pause(header: dict, current_step: int, total_steps: int, is_qa_step: bool) -> bool:
    """Return True if plan header's pause_for_verdict field matches current step."""
    pv = header.get("pause_for_verdict", "")
    if pv == "always":
        return True
    if pv == "after_step_1":
        return current_step == 1
    if pv == "after_qa_step":
        return is_qa_step
    if pv:
        _log("WARN", f"⚠️ unrecognized pause_for_verdict value: {pv!r} (recognized: 'always', 'after_step_1', 'after_qa_step') — treating as no-pause")
    return False


def _apply_defensive_header_defaults(header: dict, total_steps: int) -> dict:
    """Apply defensive defaults for sparse multi-step plan headers.

    If header parse returned < 3 keys for a multi-step plan and pause_for_verdict
    is missing, default to after_step_1 (safe-pause). Returns the mutated header.
    """
    if total_steps > 1 and len(header) < 3:
        if not header.get("pause_for_verdict", "").strip():
            header["pause_for_verdict"] = "after_step_1"
    return header


def _is_plan_stranded(inprogress_path: str, expected_done_path: str) -> bool:
    return os.path.exists(inprogress_path) or not os.path.exists(expected_done_path)


def run_plan(plan_path: str, config: dict, response_server: server.ResponseServer, resume_step: Optional[int] = None, bellows=None):
    app_key = config.get("pushover", {}).get("app_key", "")
    user_key = config.get("pushover", {}).get("user_key", "")
    plan_name = os.path.basename(plan_path)
    db_path = DB_PATH

    try:
        _log("EVENT", f"⏳ RUNNING", slug=slug_for(plan_name))
        plan_text = load_file(plan_path)

        # Extract project path (parent of knowledge/decisions/)
        plan_p = pathlib.Path(plan_path)
        project_path = str(plan_p.parents[2])

        plan_dir = str(pathlib.Path(plan_path).parent)
        plan_filename = os.path.basename(plan_path)
        # Canonicalize: strip lifecycle prefix for path construction
        base_filename = plan_filename
        for prefix in ("in-progress-", "verdict-pending-", "halted-"):
            if base_filename.startswith(prefix):
                base_filename = base_filename[len(prefix):]
                break
        inprogress_path = os.path.join(plan_dir, f"in-progress-{base_filename}")
        plan_slug = verdict.slug_from_path(base_filename)

        # Check for shadow copy — use pristine content for metadata if available
        shadow_text = _read_shadow(plan_filename)
        if shadow_text is not None:
            metadata_text = shadow_text
        else:
            metadata_text = plan_text

        is_diagnostic = os.path.basename(plan_path).startswith("diagnostic-")
        total_steps = extract_total_steps(metadata_text)
        # NOTE 2026-05-03: Narrow override — fires only when extract_total_steps()
        # returned 0 (no `## STEP N` headers). Multi-step diagnostics with headers
        # count correctly. Header-less diagnostics flow through Phase 8.1 pause-or-close
        # logic via this single-step fallback. Test fixtures that depend on this:
        # test_diagnostic_auto_close_moves_to_done, test_clean_diagnostic_no_header_posts_verdict,
        # test_clean_diagnostic_auto_close_true_moves_to_done.
        if total_steps == 0 and is_diagnostic:
            total_steps = 1

        header = gates._parse_plan_header(metadata_text)
        # Defensive default (Shape g, BACKLOG 2026-05-10 closure): if header
        # parse looks sparse for a multi-step plan, default to safe-pause
        # rather than auto-advance. Catches future parser-miss classes.
        prev_len = len(header)
        _apply_defensive_header_defaults(header, total_steps)
        if "pause_for_verdict" in header and len(header) > prev_len:
            _log("WARN", f"⚠️ sparse header ({prev_len} keys) for {total_steps}-step plan — defaulting pause_for_verdict to after_step_1 (safe-pause)", slug=slug_for(plan_name))
        model = header.get("Model", header.get("model", config["default_model"]))

        # Claim-time dispatch mode validation (Rule 35)
        if not plan_filename.startswith("in-progress-"):
            validation_result = validators.validate_at_claim(header, plan_path, config, metadata_text)
            if validation_result["rejected"]:
                halted_path = os.path.join(plan_dir, f"halted-{base_filename}")
                shutil.move(plan_path, halted_path)
                if bellows is not None:
                    bellows._seen.discard(verdict.slug_from_path(plan_path))
                _log("ERROR", f"plan rejected by dispatch-mode validator: {validation_result['reject_reason']}", slug=slug_for(plan_name))
                notifier.push(app_key, user_key, "Bellows — Plan Rejected", f"Plan: {plan_name}\nReason: {validation_result['reject_reason']}")
                return
            for w in validation_result["warnings"]:
                _log("WARN", f"dispatch-validator: {w['check']} — {w['message']}", slug=slug_for(plan_name))

        # Claim the plan atomically before calling the runner.
        # If already in-progress (e.g. resume path), skip the move.
        plan_id = None
        if not plan_filename.startswith("in-progress-"):
            # Parse plan type from filename prefix
            plan_type = "executable"
            for _tp in ("diagnostic-", "executable-", "qa-"):
                if base_filename.startswith(_tp):
                    plan_type = _tp.rstrip("-")
                    break
            # Extract title from the plan's first # heading
            plan_title = None
            for _line in plan_text.splitlines():
                if _line.startswith("# "):
                    plan_title = _line[2:].strip()
                    break
            # Mint id + write plans row atomically
            dispatch_mode = header.get("dispatch_mode", header.get("Dispatch Mode", ""))
            tier = header.get("tier", header.get("Tier", ""))
            plan_id = lifecycle.mint_and_claim(
                plan_type=plan_type,
                target_project=project_path,
                title=plan_title,
                dispatch_mode=dispatch_mode,
                tier=tier,
                total_steps=total_steps,
                deposit_placeholder_name=base_filename,
            )
            # Single rename: deposit placeholder → in-progress-<type>-<id>.md
            id_canonical = f"{plan_type}-{plan_id}.md"
            inprogress_path = os.path.join(plan_dir, f"in-progress-{id_canonical}")
            shutil.move(plan_path, inprogress_path)
            # G4: write in_progress state immediately after claim rename
            _claim_doc_ref = os.path.relpath(inprogress_path, project_path)
            try:
                lifecycle.mark_plan_state(plan_id, "in_progress", plan_doc_ref=_claim_doc_ref)
            except Exception:
                logger.warning(f"lifecycle: failed to write in_progress for plan {plan_id}")
            plan_path = inprogress_path
            # Update derived names to reflect the id-canonical form
            base_filename = id_canonical
            plan_filename = os.path.basename(plan_path)
            plan_slug = verdict.slug_from_path(base_filename)
            _log("INFO", f"minted id {plan_id} — renamed to {plan_filename}", slug=slug_for(plan_filename))
            # Write shadow copy immediately after claim — preserves pristine content
            _write_shadow(plan_filename, plan_text)
            # Lifecycle DB: record meta + derivations at claim
            lifecycle.record_meta(plan_id, plan_type, header)
            diag_ids = lifecycle.parse_derivations(plan_text)
            if diag_ids:
                lifecycle.record_derivations(plan_id, diag_ids)
        else:
            # Resume path (G1, diagnostic 6): the file is already named
            # in-progress-<type>-<id>.md, so the mint-and-claim block above is
            # skipped. Recover plan_id from the id-canonical filename so that
            # resumed-step lifecycle writes (step start/end, gate events,
            # deposits, commits) and the [id] commit tag (G4) are restored.
            # Legacy slug+date in-progress names recover nothing → plan_id stays
            # None and lifecycle writes degrade silently, exactly as before.
            plan_id = recover_plan_id_from_filename(plan_filename)

        if shadow_text is not None:
            _log("INFO", f"using cached plan content ({total_steps} steps)", slug=slug_for(plan_name))

        if total_steps == 0:
            _log("WARN", f"⚠️ SKIPPED — no ## STEP headers — not a standard executable", slug=slug_for(plan_name))
            notifier.notify_plan_skipped(plan_name)
            shutil.move(plan_path, os.path.join(plan_dir, "Done", base_filename))
            _delete_shadow(plan_filename)
            return
        _log("INFO", f"plan has {total_steps} steps", slug=slug_for(plan_name))
        if total_steps > 1 and "pause_for_verdict" not in header:
            _log("WARN", f"⚠️ {total_steps}-step plan missing pause_for_verdict — plan will auto-advance without pausing at intermediate steps", slug=slug_for(plan_name))
        if model != config["default_model"]:
            _log("INFO", f"using model override: {model}", slug=slug_for(plan_name))

        shadow_prompt_path = str(_shadow_path(plan_filename))

        _id_tag_instruction = f" Tag all commits with [{plan_id}] in the commit message." if plan_id else ""
        if is_diagnostic:
            bootstrap_prompt = f"Read the diagnostic at {shadow_prompt_path}. Execute it fully — this is a single-step investigation. Deposit your findings and report Complete when done.{_id_tag_instruction}"
        elif resume_step is not None:
            bootstrap_prompt = f"Read the plan at {shadow_prompt_path}. Execute Step {resume_step}. After completing Step {resume_step}, STOP and wait for my confirmation.{_id_tag_instruction}"
        else:
            bootstrap_prompt = f"Read the plan at {shadow_prompt_path}. Execute Step 1 ONLY. After completing Step 1, STOP and wait for my confirmation before proceeding to Step 2.{_id_tag_instruction}"

        # Create per-plan worktree for isolation
        try:
            wt_path = _create_worktree(project_path, plan_slug)
        except WorktreeCreationError as e:
            _log("ERROR", f"❌ worktree creation failed: {e}", slug=slug_for(plan_name))
            log_path = str(BELLOWS_ROOT / "logs")
            gate_result = {"failures": [{"gate": "worktree_creation", "evidence": str(e)}], "files_changed": [], "passed": False, "is_qa_step": False}
            # Rename-first ordering (RV-1 closure, 2026-05-24): rename plan BEFORE posting verdict-request,
            # so a daemon restart between these ops cannot leave plan as in-progress-* with a verdict-request pending.
            verdict_pending_path = os.path.join(plan_dir, f"verdict-pending-{base_filename}")
            if os.path.exists(inprogress_path):
                shutil.move(inprogress_path, verdict_pending_path)
            # Precondition-failure signal (item #5, 2026-05-24): worktree creation failed → step never ran → consumer must retry, not advance.
            _vr_path = verdict.post_verdict_request(plan_path, project_path, 1, log_path, gate_result,
                                         pause_reason="gate_failure", total_steps=total_steps, step_text=plan_text,
                                         precondition_failure=True)
            lifecycle.record_verdict_request(plan_id, 1, pause_reason_code="gate_failure", verdict_file_ref=_vr_path)
            _log("PAUSE", f"⏸️ worktree creation failed, awaiting CEO verdict", slug=slug_for(plan_name))
            return

        # Capture plan diff baseline — stored once at dispatch start (per-plan isolation, plan 28)
        plan_baseline_sha = _capture_git_diff(wt_path)
        pre_diff = plan_baseline_sha

        current_step = resume_step if resume_step is not None else 1
        # Lifecycle DB: record step start
        _lc_step_id = lifecycle.record_step_start(plan_id, current_step) if plan_id else None
        _lc_step_start = time.monotonic()

        parsed = runner.run_step(bootstrap_prompt, wt_path, model,
                                  timeout=config.get("step_inactivity_timeout_seconds",
                                                     config.get("step_timeout_seconds", 300)),
                                  plan_slug=slug_for(plan_name),
                                  step_num=current_step)

        total_cost = parsed["cost_usd"] or 0.0

        record_run(
            db_path, plan_path, project_path,
            parsed.get("session_id", ""), current_step,
            parsed["receipt_status"], parsed["cost_usd"], plan_slug,
        )

        # Mode A detection: did the agent move the plan to Done/ during execution?
        # Outcome-based check: in-progress file missing AND Done/ file present indicates
        # unauthorized agent move. Per Failure 3 closure design 2026-05-06 (Option B2).
        mode_a_detected = False
        if not os.path.exists(inprogress_path):
            done_check = os.path.join(plan_dir, "Done", base_filename)
            if os.path.exists(done_check):
                _log("ERROR", f"❌ Mode A detected — agent moved to Done/ without authorization, recovering", slug=slug_for(plan_name))
                try:
                    shutil.move(done_check, inprogress_path)
                    mode_a_detected = True
                except Exception as e:
                    _log("WARN", f"⚠ Mode A recovery failed: {e}", slug=slug_for(plan_name))
                    mode_a_detected = True  # still flag the failure even if recovery failed
            else:
                _log("WARN", f"⚠ in-progress file missing — possible agent file deletion", slug=slug_for(plan_name))

        # Auto-stage declared deposits before gates (deposit-loss fix)
        _auto_stage_deposits(plan_text, header, project_path, wt_path, plan_slug, plan_id=plan_id)

        # Capture post-step file state and run gates
        post_diff = _capture_git_diff(wt_path)
        files_changed = _parse_diff_stat(post_diff, pre_diff, wt_path)
        gate_result = gates.check(parsed, plan_text, current_step, project_path, files_changed=files_changed, wt_path=wt_path)
        if mode_a_detected:
            gate_result["failures"].append({
                "gate": "unauthorized_done_move",
                "evidence": f"Agent moved {base_filename} to Done/ during step execution. File recovered to in-progress. This is a Failure 3 Mode A violation."
            })
            gate_result["passed"] = False
        failure_gates = ", ".join(f["gate"] for f in gate_result["failures"]) if gate_result["failures"] else "none"
        _log("EVENT", f"gates step {current_step}: passed={gate_result['passed']}, failures={len(gate_result['failures'])} ({failure_gates}), files_changed={len(gate_result.get('files_changed', []))}", slug=slug_for(plan_name))

        # Lifecycle DB: record step end + gate events + deposits
        _lc_step_duration = time.monotonic() - _lc_step_start if _lc_step_id else None
        lifecycle.record_step_end(_lc_step_id, status="complete" if gate_result["passed"] else "awaiting_verdict",
                                  cost_usd=parsed.get("cost_usd"), turns=parsed.get("turns"), duration_s=_lc_step_duration)
        lifecycle.record_gate_events(_lc_step_id, gate_result)
        _lc_deposits = _build_deposit_records(plan_text, header, project_path, wt_path)
        lifecycle.record_deposits(_lc_step_id, _lc_deposits)

        header = gate_result.get("plan_header", {})
        _apply_defensive_header_defaults(header, total_steps)
        effective_auto_close = str(header.get("auto_close", "false")).lower() == "true"

        while not is_final_step(current_step, total_steps):
            # Check gates: if failed, QA step, verdict-request file, or header says pause
            if (not gate_result["passed"]
                    or gate_result["is_qa_step"]
                    or gate_result.get("verdict_requested", {}).get("requested", False)
                    or header_says_pause(header, current_step, total_steps, gate_result["is_qa_step"])):
                log_path = str(BELLOWS_ROOT / "logs")
                if not gate_result["passed"]:
                    if all(isinstance(f, dict) and f.get("gate") == "rule_22_verification" for f in gate_result["failures"]):
                        _pause_reason = "rule_22_check_failed"
                    else:
                        _pause_reason = "gate_failure"
                elif gate_result["is_qa_step"]:
                    _pause_reason = "qa_checkpoint"
                elif gate_result.get("verdict_requested", {}).get("requested", False):
                    _pause_reason = "agent_verdict_request"
                else:
                    _pause_reason = "header_pause"
                # Tear down worktree before pausing
                try:
                    _lc_commit_shas = _teardown_worktree(project_path, wt_path, plan_slug, plan_id=plan_id)
                    lifecycle.record_commits(_lc_step_id, os.path.basename(project_path), _lc_commit_shas)
                except WorktreeTeardownError as e:
                    _pause_reason = "gate_failure"
                    gate_result["failures"].append({"gate": "worktree_teardown", "evidence": str(e)})
                # Rename-first ordering (RV-1 closure, 2026-05-24): rename plan BEFORE posting verdict-request,
                # so a daemon restart between these ops cannot leave plan as in-progress-* with a verdict-request pending.
                verdict_pending_path = os.path.join(plan_dir, f"verdict-pending-{base_filename}")
                if os.path.exists(inprogress_path):
                    shutil.move(inprogress_path, verdict_pending_path)
                _vr_path = verdict.post_verdict_request(plan_path, project_path, current_step, log_path, gate_result, pause_reason=_pause_reason, total_steps=total_steps, step_text=plan_text, intermediate_decisions=parsed.get("intermediate_decisions", []))
                lifecycle.record_verdict_request(plan_id, current_step, pause_reason_code=_pause_reason, verdict_file_ref=_vr_path)
                notifier.notify_verdict_request(
                    app_key, user_key, plan_name, current_step, gate_result["failures"]
                )
                record_run(db_path, plan_path, project_path,
                           parsed.get("session_id", ""), current_step, "VerdictPending", parsed["cost_usd"], plan_slug)
                _log("PAUSE", f"⏸️ step {current_step} — waiting for CEO verdict", slug=slug_for(plan_name))
                return

            # All gates passed and not QA — continue to next step
            default_next_prompt = f"Read the plan at {shadow_prompt_path}. Execute Step {current_step + 1}.{_id_tag_instruction}"

            # Capture pre-step file state
            pre_diff = _capture_git_diff(wt_path)

            # Lifecycle DB: record next step start
            _lc_step_id = lifecycle.record_step_start(plan_id, current_step + 1) if plan_id else None
            _lc_step_start = time.monotonic()

            parsed = runner.run_step(
                default_next_prompt, wt_path, model,
                session_id=parsed.get("session_id"),
                timeout=config.get("step_inactivity_timeout_seconds",
                                   config.get("step_timeout_seconds", 300)),
                plan_slug=slug_for(plan_name),
                step_num=current_step + 1,
            )
            current_step += 1
            total_cost += parsed["cost_usd"] or 0.0

            record_run(
                db_path, plan_path, project_path,
                parsed.get("session_id", ""), current_step,
                parsed["receipt_status"], parsed["cost_usd"], plan_slug,
            )

            # Mode A detection: did the agent move the plan to Done/ during execution?
            mode_a_detected = False
            if not os.path.exists(inprogress_path):
                done_check = os.path.join(plan_dir, "Done", base_filename)
                if os.path.exists(done_check):
                    _log("ERROR", f"❌ Mode A detected — agent moved to Done/ without authorization, recovering", slug=slug_for(plan_name))
                    try:
                        shutil.move(done_check, inprogress_path)
                        mode_a_detected = True
                    except Exception as e:
                        _log("WARN", f"⚠ Mode A recovery failed: {e}", slug=slug_for(plan_name))
                        mode_a_detected = True
                else:
                    _log("WARN", f"⚠ in-progress file missing — possible agent file deletion", slug=slug_for(plan_name))

            # Auto-stage declared deposits before gates (deposit-loss fix)
            _auto_stage_deposits(plan_text, header, project_path, wt_path, plan_slug, plan_id=plan_id)

            # Capture post-step file state and run gates
            post_diff = _capture_git_diff(wt_path)
            files_changed = _parse_diff_stat(post_diff, pre_diff, wt_path)
            gate_result = gates.check(parsed, plan_text, current_step, project_path, files_changed=files_changed, wt_path=wt_path)
            if mode_a_detected:
                gate_result["failures"].append({
                    "gate": "unauthorized_done_move",
                    "evidence": f"Agent moved {base_filename} to Done/ during step execution. File recovered to in-progress. This is a Failure 3 Mode A violation."
                })
                gate_result["passed"] = False
            failure_gates = ", ".join(f["gate"] for f in gate_result["failures"]) if gate_result["failures"] else "none"
            _log("EVENT", f"gates step {current_step}: passed={gate_result['passed']}, failures={len(gate_result['failures'])} ({failure_gates}), files_changed={len(gate_result.get('files_changed', []))}", slug=slug_for(plan_name))

            # Lifecycle DB: record step end + gate events + deposits (while-loop step)
            _lc_step_duration = time.monotonic() - _lc_step_start if _lc_step_id else None
            lifecycle.record_step_end(_lc_step_id, status="complete" if gate_result["passed"] else "awaiting_verdict",
                                      cost_usd=parsed.get("cost_usd"), turns=parsed.get("turns"), duration_s=_lc_step_duration)
            lifecycle.record_gate_events(_lc_step_id, gate_result)
            _lc_deposits = _build_deposit_records(plan_text, header, project_path, wt_path)
            lifecycle.record_deposits(_lc_step_id, _lc_deposits)

        # Final step completed — check gates one last time. Mirrors the while-loop
        # pause conditions plus `not effective_auto_close` so single-step plans
        # (where the loop is never entered) get the full set of pause checks.
        if (not gate_result["passed"]
                or gate_result["is_qa_step"]
                or gate_result.get("verdict_requested", {}).get("requested", False)
                or header_says_pause(header, current_step, total_steps, gate_result["is_qa_step"])
                or not effective_auto_close):
            log_path = str(BELLOWS_ROOT / "logs")
            if not gate_result["passed"]:
                if all(isinstance(f, dict) and f.get("gate") == "rule_22_verification" for f in gate_result["failures"]):
                    _pause_reason = "rule_22_check_failed"
                else:
                    _pause_reason = "gate_failure"
            elif gate_result["is_qa_step"]:
                _pause_reason = "qa_checkpoint"
            elif gate_result.get("verdict_requested", {}).get("requested", False):
                _pause_reason = "agent_verdict_request"
            elif header_says_pause(header, current_step, total_steps, gate_result["is_qa_step"]):
                _pause_reason = "header_pause"
            else:
                _pause_reason = "auto_close_disabled"
            # Tear down worktree before pausing
            try:
                _lc_commit_shas = _teardown_worktree(project_path, wt_path, plan_slug, plan_id=plan_id)
                lifecycle.record_commits(_lc_step_id, os.path.basename(project_path), _lc_commit_shas)
            except WorktreeTeardownError as e:
                _pause_reason = "gate_failure"
                gate_result["failures"].append({"gate": "worktree_teardown", "evidence": str(e)})
            # Rename-first ordering (RV-1 closure, 2026-05-24): rename plan BEFORE posting verdict-request,
            # so a daemon restart between these ops cannot leave plan as in-progress-* with a verdict-request pending.
            verdict_pending_path = os.path.join(plan_dir, f"verdict-pending-{base_filename}")
            if os.path.exists(inprogress_path):
                shutil.move(inprogress_path, verdict_pending_path)
            _vr_path = verdict.post_verdict_request(plan_path, project_path, current_step, log_path, gate_result, pause_reason=_pause_reason, total_steps=total_steps, step_text=plan_text, intermediate_decisions=parsed.get("intermediate_decisions", []))
            lifecycle.record_verdict_request(plan_id, current_step, pause_reason_code=_pause_reason, verdict_file_ref=_vr_path)
            notifier.notify_verdict_request(
                app_key, user_key, plan_name, current_step, gate_result["failures"]
            )
            record_run(db_path, plan_path, project_path,
                       parsed.get("session_id", ""), current_step, "VerdictPending", parsed["cost_usd"], plan_slug)
            _log("PAUSE", f"⏸️ step {current_step} — waiting for CEO verdict", slug=slug_for(plan_name))
            return

        # Auto-close: clean gates, no QA checkpoint, no header/verdict-request pause, and
        # effective_auto_close is True. Diagnostics default to NOT auto-close (pause for
        # verdict) unless auto_close: true is set in the plan header.
        if (gate_result["passed"]
                and not gate_result["is_qa_step"]
                and not header_says_pause(header, current_step, total_steps, gate_result["is_qa_step"])
                and not gate_result.get("verdict_requested", {}).get("requested", False)
                and effective_auto_close):
            # Tear down worktree before auto-close
            try:
                _lc_commit_shas = _teardown_worktree(project_path, wt_path, plan_slug, plan_id=plan_id)
                lifecycle.record_commits(_lc_step_id, os.path.basename(project_path), _lc_commit_shas)
            except WorktreeTeardownError as e:
                # Cherry-pick conflict on auto-close — convert to gate_failure pause
                _log("ERROR", f"❌ worktree teardown failed on auto-close: {e}", slug=slug_for(plan_name))
                log_path = str(BELLOWS_ROOT / "logs")
                gate_result["failures"].append({"gate": "worktree_teardown", "evidence": str(e)})
                gate_result["passed"] = False
                # Rename-first ordering (RV-1 closure, 2026-05-24): rename plan BEFORE posting verdict-request,
                # so a daemon restart between these ops cannot leave plan as in-progress-* with a verdict-request pending.
                verdict_pending_path = os.path.join(plan_dir, f"verdict-pending-{base_filename}")
                if os.path.exists(inprogress_path):
                    shutil.move(inprogress_path, verdict_pending_path)
                _vr_path = verdict.post_verdict_request(plan_path, project_path, current_step, log_path, gate_result,
                                             pause_reason="gate_failure", total_steps=total_steps, step_text=plan_text, intermediate_decisions=parsed.get("intermediate_decisions", []))
                lifecycle.record_verdict_request(plan_id, current_step, pause_reason_code="gate_failure", verdict_file_ref=_vr_path)
                _log("PAUSE", f"⏸️ worktree teardown failed, awaiting CEO verdict", slug=slug_for(plan_name))
                return
            verdict.log_to_ledger(plan_path, current_step, gate_result, "auto-close",
                                  "all gates passed, auto_close enabled — auto-closing",
                                  pause_reason_code="auto_close")
            done_dir = os.path.join(plan_dir, "Done")
            os.makedirs(done_dir, exist_ok=True)
            done_path = os.path.join(done_dir, base_filename)
            source = inprogress_path if os.path.exists(inprogress_path) else plan_path
            _cleanup_verdicts_for_slug(verdict.slug_from_path(plan_path))
            if bellows is not None:
                bellows._seen.discard(verdict.slug_from_path(plan_path))
            if os.path.exists(source):
                shutil.move(source, done_path)
            _delete_shadow(plan_filename)
            _done_doc_ref = os.path.relpath(done_path, project_path)
            lifecycle.mark_plan_state(plan_id, "closed", closed_at=datetime.now().isoformat(), plan_doc_ref=_done_doc_ref) if plan_id else None
            notifier.notify_plan_complete(plan_name, total_cost)
            _log("EVENT", f"✅ AUTO-CLOSED", slug=slug_for(plan_name))
            return

    except Exception as e:
        _log("ERROR", f"❌ FAILED: {e}", slug=slug_for(plan_name))
        notifier.notify_failure(app_key, user_key, plan_name, current_step if 'current_step' in dir() else 0, str(e))


def _capture_git_diff(project_path: str) -> str:
    """Capture the current HEAD commit SHA, scoped to the directory at project_path.

    Returns the short SHA as a string, or empty string on subprocess error or
    missing git. The function name and signature are preserved from a prior
    implementation; "diff" in the name is now anachronistic but the contract
    change is necessary to fix the file_change_audit false-negative documented
    in BACKLOG 2026-05-21 (diagnostic: knowledge/research/file-change-audit-false-negative-2026-05-25.md).
    Prior implementation returned `git diff --stat` output, which was blind to
    committed changes — agents commit during their step as standard practice,
    leaving both pre- and post-step working trees clean.
    """
    try:
        result = subprocess.run(
            ["git", "--no-pager", "rev-parse", "HEAD"],
            cwd=project_path, capture_output=True, text=True, timeout=10,
        )
        if result.returncode != 0:
            return ""
        return result.stdout.strip()
    except Exception:
        return ""


def _parse_diff_stat(post_diff: str, pre_diff: str, project_path: Optional[str] = None) -> list:
    """Return list of files changed between pre_diff and post_diff, scoped to project_path.

    When post_diff is provided (non-empty), diffs between two commit SHAs:
    `git diff --stat <pre_diff> <post_diff> -- .`. This isolates the diff to committed
    changes between the two captures, excluding concurrent plan commits that land after
    post_diff capture (per-plan diff baseline fix, plan 28).

    When post_diff is empty, falls back to diffing against the working tree:
    `git diff --stat <pre_diff> -- .`, which captures both committed and uncommitted
    changes since pre_diff.

    Parameters:
      - `post_diff`: HEAD SHA captured at step end by `_capture_git_diff`. When non-empty,
        used as the diff endpoint to isolate from concurrent plan changes.
      - `pre_diff`: HEAD SHA captured at step start by `_capture_git_diff`.
      - `project_path`: directory to run git in AND the scope filter for `..` paths.

    Files outside `project_path` (paths with `..` components after normalization) are
    excluded — same filter as the prior implementation. Returns sorted list. Returns
    [] on subprocess error, empty pre_diff, or no changes.

    Closes BACKLOG 2026-05-21 file_change_audit false-negative (root cause: prior
    implementation used `git diff --stat` working-tree-vs-index, blind to commits).
    """
    if not pre_diff:
        return []
    # cwd must be the same directory where _capture_git_diff captured pre_diff.
    # Callers pass project_path consistently across both calls.
    cwd = project_path if project_path else None
    # When post_diff is provided, diff between two commits to isolate from concurrent
    # plan changes (plan 28). When empty, fall back to diffing against working tree.
    if post_diff:
        cmd = ["git", "--no-pager", "diff", "--stat=300", "--relative", pre_diff, post_diff, "--", "."]
    else:
        cmd = ["git", "--no-pager", "diff", "--stat=300", "--relative", pre_diff, "--", "."]
    try:
        result = subprocess.run(
            cmd, cwd=cwd, capture_output=True, text=True, timeout=10,
        )
    except Exception:
        return []
    if result.returncode != 0:
        return []

    changed = []
    for line in result.stdout.strip().splitlines():
        line = line.strip()
        if "|" not in line:
            continue
        filename, _stat = line.split("|", 1)
        filename = filename.strip()
        if not filename:
            continue
        changed.append(filename)

    if project_path is not None:
        changed = [
            f for f in changed
            if ".." not in os.path.normpath(f).split(os.sep)
        ]

    return sorted(changed)


def _create_worktree(project_path: str, slug: str) -> str:
    """Create a named-branch git worktree for a plan execution.

    Returns the worktree path on success. Retries once on failure with a 2s delay.
    Raises WorktreeCreationError if both attempts fail or on timeout/OS error.

    If project_path has no project-local .git (directory or file), worktree
    creation is skipped and project_path is returned as-is.  The caller uses
    wt_path == project_path as the sentinel for "no worktree created".
    """
    if not os.path.exists(os.path.join(project_path, ".git")):
        project_name = os.path.basename(project_path)
        _log("WARN", f"⚠ {project_name} has no project-local .git — running in-place without worktree isolation", slug=slug)
        return project_path

    wt_path = os.path.join(project_path, ".bellows-worktrees", slug)
    parent_dir = os.path.join(project_path, ".bellows-worktrees")
    os.makedirs(parent_dir, exist_ok=True)

    # Clean stranded worktree from a prior failed dispatch (mirrors __init__ prune style)
    if os.path.exists(wt_path):
        _log("WARN", f"⚠ stranded worktree found at {wt_path}, removing before re-creation", slug=slug)
        # --- Gap 2a: preserve un-landed commits before stranded-cleanup ---
        try:
            wt_head_result = subprocess.run(
                ["git", "--no-pager", "-C", wt_path, "rev-parse", "--verify", "HEAD"],
                capture_output=True, text=True, timeout=10,
            )
        except Exception:
            wt_head_result = None
        if wt_head_result and wt_head_result.returncode == 0:
            wt_head = wt_head_result.stdout.strip()
            try:
                ancestor_result = subprocess.run(
                    ["git", "--no-pager", "-C", project_path, "merge-base", "--is-ancestor", wt_head, "main"],
                    capture_output=True, text=True, timeout=10,
                )
                already_landed = (ancestor_result.returncode == 0)
            except Exception:
                already_landed = False  # fail-safe: preserve under uncertainty
            if not already_landed:
                ts = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
                branch_name = f"bellows-preserved/{slug}-{ts}"
                try:
                    br_result = subprocess.run(
                        ["git", "--no-pager", "-C", project_path, "branch", branch_name, wt_head],
                        capture_output=True, text=True, timeout=10,
                    )
                    if br_result.returncode == 0:
                        _log("WARN", f"⚠ preserved un-landed worktree commits at {wt_head} on branch {branch_name} before stranded-cleanup", slug=slug)
                    else:
                        _log("ERROR", f"⚠ failed to create preservation branch {branch_name} for worktree HEAD {wt_head}: {br_result.stderr.strip()}", slug=slug)
                except Exception as e:
                    _log("ERROR", f"⚠ failed to create preservation branch {branch_name} for worktree HEAD {wt_head}: {e}", slug=slug)
        try:
            subprocess.run(
                ["git", "--no-pager", "worktree", "remove", "--force", wt_path],
                cwd=project_path, capture_output=True, text=True, timeout=10,
            )
        except Exception:
            pass  # path may not be a registered worktree
        shutil.rmtree(wt_path, ignore_errors=True)
        try:
            subprocess.run(
                ["git", "--no-pager", "worktree", "prune"],
                cwd=project_path, capture_output=True, text=True, timeout=10,
            )
        except Exception:
            pass
        # Clean up the named branch if it exists (prevents sequential-invariant failure)
        try:
            subprocess.run(
                ["git", "--no-pager", "branch", "-D", f"bellows-wt/{slug}"],
                cwd=project_path, capture_output=True, text=True, timeout=10,
            )
        except Exception:
            pass  # branch may not exist (legacy detached-HEAD worktree)

    branch_name = f"bellows-wt/{re.sub(r'[^a-zA-Z0-9._/-]', '-', slug)}"

    # Fail-fast: branch bellows-wt/<slug> must not pre-exist (sequential invariant)
    branch_check = subprocess.run(
        ["git", "--no-pager", "rev-parse", "--verify", f"refs/heads/{branch_name}"],
        cwd=project_path, capture_output=True, text=True, timeout=10,
    )
    if branch_check.returncode == 0:
        raise WorktreeCreationError(
            f"branch '{branch_name}' already exists — sequential invariant violated "
            f"(prior worktree for this slug was not fully cleaned up)"
        )

    try:
        cmd = ["git", "--no-pager", "worktree", "add", wt_path, "-b", branch_name, "HEAD"]
        result = subprocess.run(cmd, cwd=project_path, capture_output=True, text=True, timeout=60)

        if result.returncode != 0:
            _log("WARN", f"⚠ worktree creation failed, retrying in 2s: {result.stderr.strip()}", slug=slug)
            time.sleep(2)
            result = subprocess.run(cmd, cwd=project_path, capture_output=True, text=True, timeout=60)
            if result.returncode != 0:
                raise WorktreeCreationError(f"worktree creation failed after retry for {slug}: {result.stderr.strip()}")

        return wt_path

    except subprocess.TimeoutExpired as e:
        raise WorktreeCreationError(f"worktree creation timed out for {slug}: {e}") from e
    except OSError as e:
        raise WorktreeCreationError(f"worktree creation OS error for {slug}: {e}") from e


def _auto_stage_deposits(plan_text, plan_header, project_path, wt_path, slug, plan_id=None):
    """Auto-stage and commit plan-declared deposits that are uncommitted in the worktree.

    Called immediately before gates.check() at step completion so that
    deposit_exists evaluates post-commit state and the teardown merge lands them.
    Clean no-op when all declared deposits are already committed.
    """
    if wt_path == project_path:
        return  # In-place execution, no worktree — nothing to protect

    # (1) Extract plan-declared deposit paths from both sources
    deposit_paths = []
    prose_deposits = gates._extract_plan_required_deposits(plan_text)
    if prose_deposits:
        deposit_paths.extend(prose_deposits)
    frontmatter_deposits = plan_header.get("deposits") if plan_header else None
    if frontmatter_deposits and isinstance(frontmatter_deposits, list):
        for p in frontmatter_deposits:
            if p not in deposit_paths:
                deposit_paths.append(p)

    if not deposit_paths:
        return

    staged_any = False
    for path in deposit_paths:
        # (2) Resolve against worktree
        resolved = gates._resolve_deposit_path(path, project_path, wt_path=wt_path)
        if resolved is None:
            continue  # File doesn't exist on disk — nothing to stage

        # (3) Check if untracked/unstaged via git status --porcelain
        try:
            result = subprocess.run(
                ["git", "--no-pager", "status", "--porcelain", "--", resolved],
                cwd=wt_path, capture_output=True, text=True, timeout=10,
            )
        except Exception:
            continue

        if result.returncode != 0 or not result.stdout.strip():
            continue  # Already committed or git error

        # File has uncommitted changes — path-scoped git add (NEVER git add -A)
        try:
            add_result = subprocess.run(
                ["git", "--no-pager", "add", "--", resolved],
                cwd=wt_path, capture_output=True, text=True, timeout=10,
            )
            if add_result.returncode == 0:
                staged_any = True
                _log("INFO", f"auto-staged declared deposit: {path}", slug=slug)
        except Exception:
            _log("WARN", f"⚠ failed to auto-stage deposit: {path}", slug=slug)

    # (4) Commit if anything was staged
    if staged_any:
        try:
            result = subprocess.run(
                ["git", "--no-pager", "commit", "-m",
                 f"bellows: auto-stage declared deposits before teardown{f' [{plan_id}]' if plan_id else ''}"],
                cwd=wt_path, capture_output=True, text=True, timeout=30,
            )
            if result.returncode == 0:
                _log("INFO", "committed auto-staged deposits", slug=slug)
            else:
                _log("WARN", f"⚠ auto-stage commit failed: {result.stderr.strip()}", slug=slug)
        except Exception as e:
            _log("WARN", f"⚠ auto-stage commit exception: {e}", slug=slug)


def _build_deposit_records(plan_text, plan_header, project_path, wt_path):
    """Build deposit records list for lifecycle DB from plan-declared deposits.

    Returns list of dicts: [{declared_path, type, landed}, ...].
    """
    records = []
    prose_deposits = gates._extract_plan_required_deposits(plan_text)
    if prose_deposits:
        for p in prose_deposits:
            resolved = gates._resolve_deposit_path(p, project_path, wt_path=wt_path)
            records.append({
                "declared_path": p,
                "type": "plan_required",
                "landed": resolved is not None and os.path.exists(resolved),
            })
    frontmatter_deposits = plan_header.get("deposits") if plan_header else None
    if frontmatter_deposits and isinstance(frontmatter_deposits, list):
        seen = {r["declared_path"] for r in records}
        for p in frontmatter_deposits:
            if p not in seen:
                resolved = gates._resolve_deposit_path(p, project_path, wt_path=wt_path)
                records.append({
                    "declared_path": p,
                    "type": "frontmatter",
                    "landed": resolved is not None and os.path.exists(resolved),
                })
    return records


def _teardown_worktree(project_path: str, wt_path: str, slug: str, plan_id: int = None) -> list:
    """Tear down a worktree: merge commits back to main, remove worktree and branch.

    Raises WorktreeTeardownError on merge conflict (worktree + branch left alive for manual resolution).
    No-op when wt_path == project_path (in-place execution, no worktree was created).
    Returns list of commit SHAs that were landed (empty list if no commits or no-op).
    """
    if wt_path == project_path:
        return []

    # (a) Detect main branch
    main_branch = "main"
    try:
        result = subprocess.run(
            ["git", "--no-pager", "symbolic-ref", "--short", "refs/remotes/origin/HEAD"],
            cwd=project_path, capture_output=True, text=True, timeout=10,
        )
        if result.returncode == 0 and result.stdout.strip():
            detected = result.stdout.strip()
            if detected.startswith("origin/"):
                detected = detected[len("origin/"):]
            main_branch = detected
        else:
            _log("WARN", f"⚠ could not detect main branch, falling back to 'main'", slug=slug)
    except Exception:
        _log("WARN", f"⚠ could not detect main branch, falling back to 'main'", slug=slug)

    # Legacy-worktree migration: detect pre-merge-model detached-HEAD worktrees
    branch_name = f"bellows-wt/{slug}"
    branch_check = subprocess.run(
        ["git", "--no-pager", "rev-parse", "--verify", f"refs/heads/{branch_name}"],
        cwd=project_path, capture_output=True, text=True, timeout=10,
    )
    if branch_check.returncode != 0:
        raise WorktreeTeardownError(
            f"legacy detached-HEAD worktree detected for slug {slug}: "
            f"expected branch '{branch_name}' does not exist. "
            f"This worktree was created by a pre-merge-model Bellows daemon. "
            f"Manual resolution required: land commits from the worktree, "
            f"then remove it with 'git worktree remove --force {wt_path}'."
        )

    # (b) Collect commits made in worktree
    # Fail-safe (2026-06-05): a git-log failure here must NOT silently default to
    # an empty commit list — that would skip the merge and still remove the
    # worktree, losing un-landed commits with NO recorded worktree_teardown failure
    # (uncatchable by the Gap-1b continue-block, which keys off a recorded failure).
    # Raise so the failure routes to the 1b halt, matching this function's
    # land-or-raise contract. A successful-but-empty result (returncode 0,
    # no commits made) is legitimate and proceeds.
    try:
        result = subprocess.run(
            ["git", "--no-pager", "log", "--format=%H", "HEAD", "--not", main_branch],
            cwd=wt_path, capture_output=True, text=True, timeout=30,
        )
    except Exception as e:
        raise WorktreeTeardownError(
            f"worktree commit enumeration failed (git log exception) for slug {slug}: {e}"
        ) from e
    if result.returncode != 0:
        raise WorktreeTeardownError(
            f"worktree commit enumeration failed (git log rc={result.returncode}) for slug {slug}: {result.stderr.strip()}"
        )
    commit_shas = result.stdout.strip().splitlines()  # enumerated for logging; merge uses branch name

    # Detect stale .git/index.lock that would block merge
    lock_path = os.path.join(project_path, ".git", "index.lock")
    if os.path.exists(lock_path):
        lock_age = time.time() - os.path.getmtime(lock_path)
        if lock_age > 5:
            try:
                os.remove(lock_path)
                _log("WARN", f"⚠ removed stale .git/index.lock ({lock_age:.0f}s old)", slug=slug)
            except OSError as e:
                _log("WARN", f"⚠ could not remove .git/index.lock: {e}", slug=slug)
        else:
            # Fresh lock — wait briefly, then remove if still present
            time.sleep(3)
            if os.path.exists(lock_path):
                try:
                    os.remove(lock_path)
                    _log("WARN", f"⚠ removed .git/index.lock after 3s wait", slug=slug)
                except OSError as e:
                    _log("WARN", f"⚠ could not remove .git/index.lock: {e}", slug=slug)

    # (c) Merge worktree branch onto main
    # Primary: --ff-only (linear history when main has not advanced)
    result = subprocess.run(
        ["git", "--no-pager", "merge", "--ff-only", branch_name],
        cwd=project_path, capture_output=True, text=True, timeout=60,
    )
    if result.returncode != 0:
        # Fallback: --no-ff when main advanced (merge commit preserves worktree SHAs as parents)
        result = subprocess.run(
            ["git", "--no-pager", "merge", "--no-ff", "-m",
             f"Merge branch '{branch_name}'{f' [{plan_id}]' if plan_id else ''}", branch_name],
            cwd=project_path, capture_output=True, text=True, timeout=60,
        )
        if result.returncode != 0:
            # True content conflict or dirty-tree overlap — abort cleanly
            subprocess.run(
                ["git", "--no-pager", "merge", "--abort"],
                cwd=project_path, capture_output=True, text=True, timeout=10,
            )
            raise WorktreeTeardownError(
                f"merge conflict on {branch_name} for slug {slug}: {result.stderr.strip()}"
            )

    # (d) Remove the worktree
    try:
        result = subprocess.run(
            ["git", "--no-pager", "worktree", "remove", wt_path, "--force"],
            cwd=project_path, capture_output=True, text=True, timeout=30,
        )
        if result.returncode != 0:
            _log("WARN", f"⚠ worktree removal failed: {result.stderr.strip()} — next startup prune will clean it", slug=slug)
    except Exception as e:
        _log("WARN", f"⚠ worktree removal failed: {e} — next startup prune will clean it", slug=slug)

    # Fallback: if `git worktree remove` failed and the directory still exists, force-remove it
    if os.path.exists(wt_path):
        try:
            shutil.rmtree(wt_path, ignore_errors=True)
        except Exception as e:
            _log("WARN", f"⚠ could not force-remove orphaned worktree dir {wt_path}: {e}", slug=slug)

    # Clean up the worktree branch (safe: branch is fully merged)
    try:
        subprocess.run(
            ["git", "--no-pager", "branch", "-d", branch_name],
            cwd=project_path, capture_output=True, text=True, timeout=10,
        )
    except Exception:
        _log("WARN", f"⚠ branch cleanup failed for {branch_name}", slug=slug)

    return commit_shas


def _source_sha() -> str:
    """Return the short git SHA for bellows.py, or 'unknown' on any failure."""
    try:
        result = subprocess.run(
            ["git", "log", "-1", "--format=%h", "--", "bellows.py"],
            cwd=str(BELLOWS_ROOT),
            capture_output=True,
            text=True,
            timeout=5,
        )
        sha = result.stdout.strip()
        return sha if sha else "unknown"
    except Exception:
        return "unknown"


def _module_fingerprints() -> dict:
    """Return a dict mapping each core module filename to its fingerprint string.

    Fingerprint is git:<short-sha> when git is available, mtime:<timestamp> as
    fallback, or literal "unknown" on unexpected error.
    """
    modules = ["bellows.py", "gates.py", "verdict.py", "parser.py", "runner.py", "decisions.py"]
    bellows_dir = os.path.dirname(os.path.abspath(__file__))
    fingerprints = {}
    for mod in modules:
        try:
            mod_path = os.path.join(bellows_dir, mod)
            try:
                result = subprocess.run(
                    ["git", "--no-pager", "log", "-1", "--format=%h", "--", mod_path],
                    cwd=bellows_dir,
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                if result.returncode == 0 and result.stdout.strip():
                    fingerprints[mod] = f"git:{result.stdout.strip()}"
                    continue
            except Exception:
                pass
            mtime = os.path.getmtime(mod_path)
            ts = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S")
            fingerprints[mod] = f"mtime:{ts}"
        except Exception:
            fingerprints[mod] = "unknown"
    return fingerprints


def is_runnable_plan(filename: str) -> bool:
    if filename.startswith("in-progress-") or filename.startswith("verdict-pending-") or filename.startswith("halted-"):
        return False
    return bool(re.match(r"^(parallel-\d+-)?(executable|diagnostic|qa)-.*\.md$", filename))


def extract_parallel_group(filename: str) -> Optional[str]:
    match = re.match(r"^(parallel-\d+)-", filename)
    return match.group(1) if match else None


class PlanHandler(FileSystemEventHandler):
    def __init__(self, orchestrator):
        super().__init__()
        self.orchestrator = orchestrator
        self._pending_groups: dict = {}  # group prefix → first-seen timestamp (float)

    def collect_group(self, decisions_path: str, group: str) -> list:
        files = os.listdir(decisions_path)
        result = []
        for fname in files:
            if fname.startswith(group + "-") and is_runnable_plan(fname):
                full_path = os.path.join(decisions_path, fname)
                if verdict.slug_from_path(full_path) not in self.orchestrator._seen:
                    result.append(full_path)
        return result

    def _handle(self, path: str, from_rescan: bool = False):
        path_parent = str(Path(path).parent)
        watched = self.orchestrator.config.get("watched_projects", [])
        if path_parent not in watched:
            return
        filename = os.path.basename(path)
        if not is_runnable_plan(filename):
            if (filename.endswith(".md")
                    and not filename.startswith(("in-progress-", "verdict-pending-", "halted-", "roadmap-"))
                    and verdict.slug_from_path(path) not in self.orchestrator._seen):
                _log("WARN", f"⚠️ skipped — prefix not in dispatch whitelist", slug=slug_for(filename))
                self.orchestrator._seen.add(verdict.slug_from_path(path))
            return
        if verdict.slug_from_path(path) in self.orchestrator._seen:
            return
        group = extract_parallel_group(filename)
        if group:
            if not from_rescan:
                # Defer parallel dispatch to the rescan settle-window check.
                if group not in self._pending_groups:
                    self._pending_groups[group] = time.time()
                return
            # from_rescan=True: if group is still pending, let the settle-window
            # check in _rescan handle it; don't dispatch prematurely.
            if group in self._pending_groups:
                return
            decisions_path = str(pathlib.Path(path).parent)
            siblings = self.collect_group(decisions_path, group)
            all_paths = [p for p in siblings if verdict.slug_from_path(p) not in self.orchestrator._seen]
            [self.orchestrator._seen.add(verdict.slug_from_path(p)) for p in all_paths]
            _log("EVENT", f"parallel group {group} — {len(all_paths)} plans")
            self.orchestrator.handle_parallel_group(all_paths)
        else:
            self.orchestrator._seen.add(verdict.slug_from_path(path))
            _log("EVENT", f"⏳ detected plan", slug=slug_for(filename))
            self.orchestrator.handle_new_plan(path)

    def _invalidate_seen_on_redeposit(self, path: str):
        # Invalidate _seen on a re-deposit at an already-seen slug so a genuinely new plan
        # file (e.g. a follow-on executable deposited at the same base slug after the prior
        # plan was closed OUT-OF-BAND via a Planner-direct move to Done/, which the daemon
        # never observes) can be re-dispatched. Guard: never invalidate on Bellows-managed
        # lifecycle renames (in-progress-/verdict-pending-/halted-) — that would loop.
        filename = os.path.basename(path)
        LIFECYCLE_PREFIXES = ("in-progress-", "verdict-pending-", "halted-")
        if any(filename.startswith(p) for p in LIFECYCLE_PREFIXES):
            return
        slug = verdict.slug_from_path(path)
        if slug in self.orchestrator._seen:
            self.orchestrator._seen.discard(slug)
            _log("INFO", f"re-deposit at seen slug — invalidated _seen so plan can re-dispatch", slug=slug_for(filename))

    def on_created(self, event):
        if not event.is_directory:
            self._invalidate_seen_on_redeposit(event.src_path)
            self._handle(event.src_path)

    def on_modified(self, event):
        if not event.is_directory:
            self._invalidate_seen_on_redeposit(event.src_path)
            self._handle(event.src_path)

    def on_moved(self, event):
        if not event.is_directory:
            self._invalidate_seen_on_redeposit(event.dest_path)
            self._handle(event.dest_path)


class Bellows:
    def __init__(self, config: dict):
        self.config = config
        self.response_server = server.ResponseServer(config["callback_port"])
        self._active_lock = threading.Lock()
        self._active_count = 0
        self._seen = set()

        # Startup: prune stale worktree registrations from prior crashes
        for wp in config.get("watched_projects", []):
            # watched_projects entries are <project>/knowledge/decisions/ — go up 2 levels
            project_root = str(pathlib.Path(wp).parent.parent)
            try:
                subprocess.run(
                    ["git", "--no-pager", "worktree", "prune"],
                    cwd=project_root, capture_output=True, text=True, timeout=10,
                )
            except Exception as e:
                _log("WARN", f"⚠ worktree prune failed for {project_root}: {e}")

    def _run_tracked(self, path: str, resume_step: Optional[int] = None):
        with self._active_lock:
            self._active_count += 1
        try:
            run_plan(path, self.config, self.response_server, resume_step=resume_step, bellows=self)
        finally:
            with self._active_lock:
                self._active_count -= 1
            self._check_queue_drain()

    def _check_queue_drain(self):
        with self._active_lock:
            if self._active_count > 0:
                return
        pending = []
        for d in self.config.get("watched_projects", []):
            if os.path.isdir(d):
                pending.extend([f for f in os.listdir(d) if is_runnable_plan(f)])
        if not pending:
            app_key = self.config.get("pushover", {}).get("app_key", "")
            user_key = self.config.get("pushover", {}).get("user_key", "")
            # Check for plans paused awaiting verdict
            verdict_pending = []
            for d in self.config.get("watched_projects", []):
                if os.path.isdir(d):
                    verdict_pending.extend([f for f in os.listdir(d) if f.startswith("verdict-pending-")])
            if verdict_pending:
                _log("EVENT", f"⏸️ {len(verdict_pending)} plan(s) awaiting verdict")
            _log("EVENT", "🏁 queue empty — all plans complete")
            notifier.notify_queue_empty()

    def handle_new_plan(self, path: str, resume_step: Optional[int] = None):
        t = threading.Thread(target=self._run_tracked, args=(path,), kwargs={"resume_step": resume_step}, daemon=True)
        t.start()
        time.sleep(2)  # Stagger thread starts to avoid simultaneous claude -p auth hits
        _log("EVENT", f"▶ started", slug=slug_for(os.path.basename(path)))

    def handle_parallel_group(self, paths: list):
        threads = [threading.Thread(target=self._run_tracked, args=(p,), daemon=True) for p in paths]
        for t in threads:
            t.start()
            time.sleep(2)
        _log("EVENT", f"▶ started {len(threads)} parallel threads")

    def _rescan(self, handler):
        # Check for resolved verdicts
        self._consume_verdicts()
        # Dispatch pending parallel groups that have passed the 5-second settle window.
        now = time.time()
        for group in list(handler._pending_groups.keys()):
            if now - handler._pending_groups[group] > 5:
                for decisions_path in self.config.get("watched_projects", []):
                    if os.path.isdir(decisions_path):
                        siblings = handler.collect_group(decisions_path, group)
                        if siblings:
                            all_paths = [p for p in siblings if verdict.slug_from_path(p) not in self._seen]
                            [self._seen.add(verdict.slug_from_path(p)) for p in all_paths]
                            _log("EVENT", f"parallel group {group} — {len(all_paths)} plans (deferred dispatch)")
                            self.handle_parallel_group(all_paths)
                del handler._pending_groups[group]
        for decisions_path in self.config.get("watched_projects", []):
            if os.path.isdir(decisions_path):
                for fname in os.listdir(decisions_path):
                    if is_runnable_plan(fname):
                        full_path = os.path.join(decisions_path, fname)
                        handler._handle(full_path, from_rescan=True)

    def _scan_misplaced_verdicts(self, pending_dir):
        """Scan pending_dir for verdict response files that belong in resolved/."""
        if not os.path.isdir(pending_dir):
            return
        misplaced = []
        for fname in os.listdir(pending_dir):
            if fname.startswith("verdict-") and fname.endswith(".md") and not fname.startswith("verdict-request-"):
                misplaced.append(fname)
        if MISPLACED_VERDICT_SCAN_VERBOSE:
            _log("INFO", f"misplaced-verdict scan: pending_dir={pending_dir} — found={len(misplaced)}")
        for fname in misplaced:
            full_filepath = os.path.join(pending_dir, fname)
            _log("WARN", f"verdict file in wrong directory: {full_filepath} — expected location: verdicts/resolved/ — file will be silently ignored by verdict consumption until moved")
            dedup_key = (fname, "misplaced_directory")
            if dedup_key not in _NOTIFIED_MISPLACED:
                try:
                    app_key = self.config.get("pushover", {}).get("app_key", "")
                    user_key = self.config.get("pushover", {}).get("user_key", "")
                    notifier.push(app_key, user_key, "Bellows — Misplaced Verdict", f"{fname} found in pending/ — should be in resolved/")
                    _NOTIFIED_MISPLACED.add(dedup_key)
                except Exception:
                    pass

    def _consume_verdicts(self):
        """Scan verdicts/resolved/ for verdict files and act on them."""
        pending_dir = BELLOWS_ROOT / "verdicts" / "pending"
        self._scan_misplaced_verdicts(pending_dir)

        resolved_dir = BELLOWS_ROOT / "verdicts" / "resolved"
        if not resolved_dir.is_dir():
            return
        app_key = self.config.get("pushover", {}).get("app_key", "")
        user_key = self.config.get("pushover", {}).get("user_key", "")

        for fname in os.listdir(resolved_dir):
            if not fname.startswith("verdict-") or not fname.endswith(".md"):
                continue
            if fname.startswith("verdict-request-"):
                continue
            # Parse slug and step from filename: verdict-{slug}-step-{N}.md
            match = re.match(r"^verdict-(.+)-step-(\d+)\.md$", fname)
            if not match:
                _log("WARN", f"verdict filename format mismatch: {fname} — expected pattern: ^verdict-{{slug}}-step-{{N}}.md$ — file will be skipped")
                verdict._notify_malformed_verdict(resolved_dir / fname, f"filename format mismatch — expected: verdict-{{slug}}-step-{{N}}.md")
                continue
            plan_slug = match.group(1)
            step_number = int(match.group(2))

            # Scope search to the plan's project directory via pending request file
            # Normalize slug: strip plan-type prefix so lookup matches verdict-request filenames
            lookup_slug = plan_slug
            for prefix in ("diagnostic-", "executable-"):
                if lookup_slug.startswith(prefix):
                    lookup_slug = lookup_slug[len(prefix):]
                    break
            pending_req_file = BELLOWS_ROOT / "verdicts" / "pending" / f"verdict-request-{lookup_slug}-step-{step_number}.md"
            scoped_decisions_path = None
            total_steps_from_request = None
            pause_reason_code_from_request = None
            precondition_failure_from_request = False
            gate_result_from_request = None
            if pending_req_file.exists():
                pending_req_file_text = pending_req_file.read_text()
                for req_line in pending_req_file_text.splitlines():
                    if req_line.startswith("**Plan:**"):
                        plan_path_from_request = req_line.split("**Plan:**", 1)[1].strip()
                        scoped_decisions_path = str(pathlib.Path(plan_path_from_request).parent)
                    # Legacy tolerance: pre-2026-04-18 verdict files may contain literal "None".
                    if req_line.startswith("**Total Steps:**"):
                        raw_val = req_line.split(":**", 1)[1].strip()
                        if raw_val == "None":
                            total_steps_from_request = None
                        else:
                            try:
                                total_steps_from_request = int(raw_val)
                            except (ValueError, IndexError):
                                pass
                    if req_line.startswith("**Pause Reason Code:**"):
                        pause_reason_code_from_request = req_line.split(":**", 1)[1].strip() or None
                    if req_line.startswith("**Precondition Failure:**"):
                        precondition_failure_from_request = req_line.split(":**", 1)[1].strip().lower() == "true"
                    if req_line.startswith("**Gate Result JSON:**"):
                        try:
                            gate_result_from_request = json.loads(req_line.split(":**", 1)[1].strip())
                        except (json.JSONDecodeError, IndexError):
                            pass

            verdict_result = verdict.check_verdict(plan_slug, step_number)
            if not verdict_result.get("found"):
                continue

            v = verdict_result["verdict"]
            reason = verdict_result.get("reason", "")

            # Find the verdict-pending plan — scoped to plan's project if pending file exists
            search_dirs = [scoped_decisions_path] if scoped_decisions_path else self.config.get("watched_projects", [])
            plan_matched = False
            for decisions_path in search_dirs:
                if not os.path.isdir(decisions_path):
                    continue
                for pname in os.listdir(decisions_path):
                    if pname.startswith("verdict-pending-") and verdict.slug_from_path(pname) == lookup_slug:
                        plan_matched = True
                        full_plan_path = os.path.join(decisions_path, pname)
                        original_name = pname.replace("verdict-pending-", "", 1)
                        cleanup_slug = verdict.slug_from_path(original_name)
                        gate_result = gate_result_from_request or {"failures": [], "files_changed": []}
                        # Derive plan_id from slug for lifecycle DB writes (id-native plans only)
                        _lc_plan_id = None
                        try:
                            _lc_plan_id = int(lookup_slug)
                        except (ValueError, TypeError):
                            pass  # legacy plan — no lifecycle DB id
                        lifecycle.record_verdict_outcome(_lc_plan_id, step_number, v, decided_by="ceo", disposition_summary=reason)

                        if v == "continue":
                            # Guard: block continue when prior step's worktree teardown failed (Gap 1b).
                            # An uncleared worktree_teardown failure means Step N's commits were never
                            # merged to main — advancing would orphan them. Route to halted-
                            # for manual R2 recovery instead of silently advancing.
                            if any(f.get("gate") == "worktree_teardown" for f in gate_result.get("failures", [])):
                                _log("ERROR", f"continue verdict REJECTED — prior step's worktree_teardown failure uncleared (commits not landed); routing to halted- for manual R2 recovery", slug=plan_slug)
                                verdict.log_to_ledger(full_plan_path, step_number, gate_result,
                                                      "continue-blocked-worktree-teardown",
                                                      f"continue verdict rejected — prior-step worktree_teardown failure uncleared; Step {step_number} commits not landed; manual R2 recovery required",
                                                      pause_reason_code=pause_reason_code_from_request)
                                halted_name = f"halted-{original_name}"
                                halted_path = os.path.join(decisions_path, halted_name)
                                _cleanup_verdicts_for_slug(cleanup_slug)
                                self._seen.discard(cleanup_slug)
                                shutil.move(full_plan_path, halted_path)
                                _delete_shadow(original_name)
                                _halt_project_root = str(pathlib.Path(decisions_path).parents[1])
                                _halt_doc_ref = os.path.relpath(halted_path, _halt_project_root)
                                lifecycle.mark_plan_state(_lc_plan_id, "halted", closed_at=datetime.now().isoformat(), plan_doc_ref=_halt_doc_ref) if _lc_plan_id else None
                                notifier.notify_plan_halted(original_name)
                                break
                            is_diag = original_name.startswith("diagnostic-")
                            # Fallback chain: shadow → verdict metadata → load_file
                            shadow_text_c = _read_shadow(original_name)
                            if shadow_text_c is not None:
                                total_steps_c = extract_total_steps(shadow_text_c)
                                _log("INFO", f"using cached plan content ({total_steps_c} steps)", slug=plan_slug)
                            elif total_steps_from_request is not None:
                                total_steps_c = total_steps_from_request
                            else:
                                plan_text_c = load_file(full_plan_path)
                                total_steps_c = extract_total_steps(plan_text_c)
                            # NOTE 2026-05-03: Narrow override — mirrors run_plan site.
                            # Fires only when extract_total_steps() returned 0 (no headers).
                            if total_steps_c == 0 and is_diag:
                                total_steps_c = 1
                            if step_number >= total_steps_c:
                                # Final step — continue verdict means proceed to Done
                                verdict.log_to_ledger(full_plan_path, step_number, gate_result,
                                                      "continue-to-done",
                                                      "continue verdict on final step — moving to Done",
                                                      pause_reason_code=pause_reason_code_from_request)
                                done_dir = os.path.join(decisions_path, "Done")
                                os.makedirs(done_dir, exist_ok=True)
                                done_path = os.path.join(done_dir, original_name)
                                _cleanup_verdicts_for_slug(cleanup_slug)
                                self._seen.discard(cleanup_slug)
                                shutil.move(full_plan_path, done_path)
                                _delete_shadow(original_name)
                                _done_project_root = str(pathlib.Path(decisions_path).parents[1])
                                _done_doc_ref = os.path.relpath(done_path, _done_project_root)
                                lifecycle.mark_plan_state(_lc_plan_id, "closed", closed_at=datetime.now().isoformat(), plan_doc_ref=_done_doc_ref) if _lc_plan_id else None
                                notifier.notify_plan_complete(original_name, 0.0)
                                _log("EVENT", f"verdict continue-to-done", slug=slug_for(original_name))
                            else:
                                verdict.log_to_ledger(full_plan_path, step_number, gate_result, v, reason,
                                                      pause_reason_code=pause_reason_code_from_request)
                                inprogress_name = f"in-progress-{original_name}"
                                inprogress_path = os.path.join(decisions_path, inprogress_name)
                                shutil.move(full_plan_path, inprogress_path)
                                # Precondition-failure handling (item #5, 2026-05-24): if the prior step never ran due to
                                # a precondition gate failure (e.g., worktree creation), retry the same step rather than advance.
                                if precondition_failure_from_request:
                                    next_step = step_number
                                    _log("EVENT", f"verdict continue — retrying step {step_number} (precondition failure)", slug=slug_for(original_name))
                                else:
                                    next_step = step_number + 1
                                    _log("EVENT", f"verdict continue — resuming", slug=slug_for(original_name))
                                self.handle_new_plan(inprogress_path, resume_step=next_step)
                        else:
                            verdict.log_to_ledger(full_plan_path, step_number, gate_result, v, reason,
                                                  pause_reason_code=pause_reason_code_from_request)
                            halted_name = f"halted-{original_name}"
                            halted_path = os.path.join(decisions_path, halted_name)
                            _cleanup_verdicts_for_slug(cleanup_slug)
                            self._seen.discard(cleanup_slug)
                            shutil.move(full_plan_path, halted_path)
                            _delete_shadow(original_name)
                            _stop_project_root = str(pathlib.Path(decisions_path).parents[1])
                            _stop_doc_ref = os.path.relpath(halted_path, _stop_project_root)
                            lifecycle.mark_plan_state(_lc_plan_id, "halted", closed_at=datetime.now().isoformat(), plan_doc_ref=_stop_doc_ref) if _lc_plan_id else None
                            _log("EVENT", f"verdict stop — halting", slug=slug_for(original_name))
                            notifier.notify_plan_halted(original_name)
                        break  # only one match per verdict
                if plan_matched:
                    break  # also break directory loop

            if plan_matched:
                # Clean up pending verdict request file — stale after verdict consumption
                pending_file = BELLOWS_ROOT / "verdicts" / "pending" / f"verdict-request-{cleanup_slug}-step-{step_number}.md"
                if pending_file.exists():
                    pending_file.unlink()
                # Move the verdict file out of resolved to prevent re-processing
                processed_path = resolved_dir / f"processed-{fname}"
                shutil.move(str(resolved_dir / fname), str(processed_path))
                _warned_no_match.discard(fname)
            else:
                # No match — check if plan is already in Done/ OR halted in decisions/ (stale verdict)
                stale = False
                for decisions_path in search_dirs:
                    done_dir = os.path.join(decisions_path, "Done")
                    if os.path.isdir(done_dir):
                        for dname in os.listdir(done_dir):
                            if verdict.slug_from_path(dname) == lookup_slug:
                                stale = True
                                break
                    if stale:
                        break
                    # Also check decisions/ itself for halted-* plans (S3 Bug C fix)
                    if os.path.isdir(decisions_path):
                        for dname in os.listdir(decisions_path):
                            if dname.startswith("halted-") and verdict.slug_from_path(dname[len("halted-"):]) == lookup_slug:
                                stale = True
                                break
                    if stale:
                        break
                if stale:
                    processed_path = resolved_dir / f"processed-{fname}"
                    shutil.move(str(resolved_dir / fname), str(processed_path))
                    _warned_no_match.discard(fname)
                    _log("WARN", f"⚠️ stale verdict step {step_number} — plan in Done/ or halted-, moving to processed", slug=plan_slug)
                else:
                    if fname not in _warned_no_match:
                        _log("WARN", f"⚠️ no verdict-pending plan found step {step_number} — leaving in resolved/ for retry", slug=plan_slug)
                        _warned_no_match.add(fname)

    def _perform_startup_sweep(self) -> list[str]:
        """Remove orphaned verdict-request files from verdicts/pending/.

        Returns the list of removed filenames (basenames only, no path).
        A verdict-request file is orphaned if its slug does not appear in any
        active plan in the watched-project decisions directories (active = the
        plan is in-progress, verdict-pending, or a runnable un-claimed plan).
        Plans in Done/ are NOT considered active, so their orphaned verdict
        requests are removed.
        """
        active_slugs = set()
        for decisions_path in self.config.get("watched_projects", []):
            if not os.path.isdir(decisions_path):
                continue
            for fname in os.listdir(decisions_path):
                if fname.startswith("in-progress-") or fname.startswith("verdict-pending-"):
                    stripped = fname
                    for pfx in ("in-progress-", "verdict-pending-"):
                        if stripped.startswith(pfx):
                            stripped = stripped[len(pfx):]
                            break
                    active_slugs.add(verdict.slug_from_path(stripped))
                elif is_runnable_plan(fname):
                    active_slugs.add(verdict.slug_from_path(fname))
        pending_dir = BELLOWS_ROOT / "verdicts" / "pending"
        orphaned_removed = []
        if pending_dir.is_dir():
            for pf in os.listdir(pending_dir):
                m = re.match(r"^verdict-request-(.+)-step-\d+\.md$", pf)
                if m:
                    extracted_slug = m.group(1)
                    if extracted_slug not in active_slugs:
                        (pending_dir / pf).unlink()
                        orphaned_removed.append(pf)
        return orphaned_removed

    def start(self, session_log_path: str = "", log_existed: bool = False):
        self.response_server.start()
        observer = Observer()
        handler = PlanHandler(self)
        for decisions_path in self.config.get("watched_projects", []):
            observer.schedule(handler, decisions_path, recursive=False)
        observer.start()
        print("=" * 50)
        print("  🔥 Bellows is running")
        print(f"  Source: bellows.py @ {_source_sha()}")
        print(f"  Watching {len(self.config.get('watched_projects', []))} projects")
        print(f"  Rescan interval: 30s")
        print(f"  Callback: http://{self.config.get('tailscale_ip','localhost')}:{self.config.get('callback_port',5000)}/respond")
        for mod_name, fp in sorted(_module_fingerprints().items()):
            print(f"  Module: {mod_name} @ {fp}")
        print("=" * 50)
        if log_existed:
            _log("INFO", "── session restart ──────────────────────────────")
        _log("INFO", f"session log: {session_log_path}")
        # Brief pause to allow keychain and Claude Code auth to settle
        time.sleep(3)
        # One-time startup sweep: remove orphaned verdict requests
        orphaned_removed = self._perform_startup_sweep()
        if orphaned_removed:
            _log("INFO", f"startup cleanup — {len(orphaned_removed)} orphaned verdict requests removed")
            for rm_name in orphaned_removed:
                _log("INFO", f"  - {rm_name}")

        # Scan for plans already on disk at startup
        for decisions_path in self.config.get("watched_projects", []):
            if os.path.isdir(decisions_path):
                for fname in os.listdir(decisions_path):
                    if is_runnable_plan(fname):
                        full_path = os.path.join(decisions_path, fname)
                        _log("EVENT", f"startup scan found {fname}")
                        handler._handle(full_path)
        rescan_interval = 30
        last_rescan = time.time()
        last_heartbeat = time.time()
        heartbeat_counter = 0
        try:
            while True:
                time.sleep(1)
                if time.time() - last_rescan >= rescan_interval:
                    self._rescan(handler)
                    last_rescan = time.time()
                if time.time() - last_heartbeat >= 300:
                    with _plan_event_lock:
                        _plan_event_age = time.time() - _last_plan_event_time
                    if _plan_event_age >= 120:
                        with self._active_lock:
                            n_in_flight = self._active_count
                        n_pending = 0
                        for d in self.config.get("watched_projects", []):
                            if os.path.isdir(d):
                                n_pending += sum(1 for f in os.listdir(d) if f.startswith("verdict-pending-"))
                        if n_in_flight > 0 or n_pending > 0:
                            _log("INFO", f"heartbeat: {n_in_flight} in-flight, {n_pending} awaiting verdict")
                        else:
                            _log("INFO", "heartbeat: idle")
                        if heartbeat_counter % MODULE_FINGERPRINT_HEARTBEAT_INTERVAL == 0:
                            for mod_name, fp in sorted(_module_fingerprints().items()):
                                _log("INFO", f"  Module: {mod_name} @ {fp}")
                        heartbeat_counter += 1
                    last_heartbeat = time.time()
        except KeyboardInterrupt:
            observer.stop()
        observer.join()


if __name__ == "__main__":
    config = load_config()
    _rotate_logs()

    # Configure bellows logger
    _bellows_logger = logging.getLogger("bellows")
    _bellows_logger.setLevel(logging.DEBUG)
    _bellows_logger.propagate = False

    _stdout_handler = logging.StreamHandler(sys.stdout)
    _stdout_handler.setLevel(logging.DEBUG)
    _stdout_handler.setFormatter(logging.Formatter('%(message)s'))
    _bellows_logger.addHandler(_stdout_handler)

    os.makedirs(os.path.join(str(BELLOWS_ROOT), "logs", "terminal"), exist_ok=True)
    _session_log_path = os.path.join(
        str(BELLOWS_ROOT), "logs", "terminal",
        f"bellows-{datetime.now().strftime('%Y-%m-%d')}.log",
    )
    _log_existed = os.path.exists(_session_log_path)
    _file_handler = RotatingFileHandler(_session_log_path, maxBytes=50*1024*1024, backupCount=5)
    _file_handler.setLevel(logging.DEBUG)
    _file_handler.setFormatter(logging.Formatter('%(message)s'))
    _bellows_logger.addHandler(_file_handler)

    # G2: flock single-instance guard — must precede all DB/recovery/watcher work
    _lock_path = str(BELLOWS_ROOT / ".bellows.lock")
    _lock_fd = open(_lock_path, "w")
    try:
        fcntl.flock(_lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except (BlockingIOError, OSError):
        _log("ERROR", "another Bellows instance holds .bellows.lock — exiting")
        sys.exit(1)
    # _lock_fd intentionally kept open — kernel releases flock on process death

    migrate_db()
    lifecycle.init_lifecycle_db()
    # Startup recovery: re-rename half-claimed plans (blueprint 2.4a)
    for decisions_path in config.get("watched_projects", []):
        if os.path.isdir(decisions_path):
            _project_root = str(Path(decisions_path).parent.parent)
            actions = lifecycle.recover_half_claimed(
                decisions_path, project_root=_project_root,
            )
            for pid, action in actions:
                _log("INFO", f"lifecycle recovery: plan {pid} — {action}")
    notifier.init_notifications(config)
    b = Bellows(config)
    b.start(_session_log_path, _log_existed)
