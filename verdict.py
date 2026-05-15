"""Verdict queue for async Planner review. Posts requests, checks resolved verdicts, logs to ledger."""

import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

import notifier

BELLOWS_ROOT = Path(__file__).parent.resolve()
VERDICTS_DIR = BELLOWS_ROOT / "verdicts"

VERDICT_PARSE_LOG_VERBOSE = False
_NOTIFIED_MALFORMED: set[tuple[str, str]] = set()

# DEPOSITS_BLOCK_RE and BLOCK_BULLET_RE duplicated in gates.py::_extract_plan_required_deposits — keep in sync.
DEPOSITS_BLOCK_RE = re.compile(r'[> ]*\*\*Deposits:\*\*\s*\n(?:[> ]*\n)*((?:[> ]*-\s+.*\n?)+)')
BLOCK_BULLET_RE = re.compile(r'-\s+`([^`]+)`')

STRICT_DEPOSIT_RE = re.compile(r'\*\*Deposits?:\*\*\s+(?:.*?\s+)?`([^`]+\.md)`')
BOLD_NOUN_DEPOSIT_RE = re.compile(r'\*\*(?:Deposit|Write)[^*]+\*\*\s+(?:to|at)\s+`([^`]+\.md)`', re.IGNORECASE)
INLINE_DEPOSIT_RE = re.compile(r'[Dd]eposit(?:ing)?\s+(?:[\w]+\s+)*(?:to:?|at|as)\s+`([^`]+\.md)`')
FEEDBACK_EXCLUSION_RE = re.compile(r'[Ss]tandard prompt feedback protocol')


def strip_fenced_code_blocks(text: str) -> str:
    """Remove fenced code blocks (``` ... ```) from text, preserving line structure.

    Used by plan-text parsers to prevent example/fixture headers inside code fences
    from being parsed as structural elements.
    Duplicated from bellows.py — keep in sync.
    """
    return re.sub(r"^```[^\n]*\n.*?^```[^\n]*$", "", text, flags=re.MULTILINE | re.DOTALL)


def _extract_step_text_from_plan(plan_text: str, step_number: int):
    """Extract text of a single step from a plan, bounded by ## STEP N headers.

    Returns the step text or None if no match.
    Duplicated from gates.py::_extract_step_text to avoid circular import — keep in sync.
    """
    plan_text = strip_fenced_code_blocks(plan_text)
    pattern = rf"^## STEP {step_number}\b.*?(?=^## STEP |\Z)"
    match = re.search(pattern, plan_text, re.DOTALL | re.MULTILINE)
    return match.group(0) if match else None


def extract_primary_deposit(step_text: str) -> Optional[str]:
    """Extract the primary deposit path from a plan step's text."""
    # Rule 26: prefer declared **Deposits:** block when present — block is authoritative,
    # legacy regexes not applied as fallback.
    block_match = DEPOSITS_BLOCK_RE.search(step_text)
    if block_match:
        for m in BLOCK_BULLET_RE.finditer(block_match.group(1)):
            path = m.group(1)
            if path.endswith('.md'):
                if '/Desktop/GitHub/' in path:
                    parts = path.split('/Desktop/GitHub/')
                    if len(parts) == 2:
                        path = parts[1]
                return path
        return None

    for line in step_text.splitlines():
        if FEEDBACK_EXCLUSION_RE.search(line):
            continue
        for pattern in (STRICT_DEPOSIT_RE, BOLD_NOUN_DEPOSIT_RE, INLINE_DEPOSIT_RE):
            match = pattern.search(line)
            if match:
                path = match.group(1)
                if '/Desktop/GitHub/' in path:
                    parts = path.split('/Desktop/GitHub/')
                    if len(parts) == 2:
                        path = parts[1]
                return path
    return None


def slug_from_path(plan_path):
    """Extract a slug from a plan path for use in verdict filenames."""
    basename = os.path.basename(plan_path)
    # Strip common prefixes
    for prefix in ("in-progress-", "verdict-pending-", "executable-", "diagnostic-"):
        if basename.startswith(prefix):
            basename = basename[len(prefix):]
    # Strip .md extension
    if basename.endswith(".md"):
        basename = basename[:-3]
    return basename


def post_verdict_request(plan_path, project_path, step_number, log_path, gate_result, pause_reason="auto_close_disabled", planner_py_decision=None, total_steps=None, step_text="", intermediate_decisions=None):
    """Create a verdict request file in verdicts/pending/."""
    pending_dir = VERDICTS_DIR / "pending"
    pending_dir.mkdir(parents=True, exist_ok=True)

    slug = slug_from_path(plan_path)
    filename = f"verdict-request-{slug}-step-{step_number}.md"
    filepath = pending_dir / filename

    _pause_reason_labels = {
        "gate_failure": "Gate failure",
        "qa_checkpoint": "QA checkpoint",
        "agent_verdict_request": "Agent verdict request",
        "header_pause": "Header pause (pause_for_verdict)",
        "auto_close_disabled": "Auto-close disabled",
    }
    pause_reason_label = _pause_reason_labels.get(pause_reason, pause_reason)

    if total_steps is None:
        raise ValueError("total_steps must be an integer, got None")

    if pause_reason == "gate_failure" and gate_result.get("failures"):
        failures_text = ""
        for f in gate_result["failures"]:
            failures_text += f"- **{f['gate']}**: {f['evidence']}\n"
        pause_section = f"## Gate Failures\n\n{failures_text}"
    else:
        _pause_descriptions = {
            "qa_checkpoint": "This step is a QA checkpoint. All gates passed — CEO review requested before proceeding.",
            "agent_verdict_request": "The agent deposited a verdict-request file during execution and is requesting\nCEO guidance before proceeding to the next step.",
            "header_pause": "The plan header specifies `pause_for_verdict`. This step is complete;\nCEO review is required before the next step begins.",
            "auto_close_disabled": "Plan completed. Auto-close is disabled for this plan (diagnostic default or\n`auto_close: false` in header). CEO review required before closing.",
        }
        desc = _pause_descriptions.get(pause_reason, f"Pause reason: {pause_reason}")
        pause_section = f"## Pause Reason\n\n{desc}"

    # Scope deposit extraction to the current step's text, not the full plan
    current_step_text = _extract_step_text_from_plan(step_text, step_number) or step_text

    content = (
        f"# Verdict Request\n\n"
        f"**Plan:** {plan_path}\n"
        f"**Project:** {project_path}\n"
        f"**Step:** {step_number}\n"
        f"**Log:** {log_path}\n"
        f"**Timestamp:** {datetime.now().isoformat()}\n"
        f"**Pause Reason:** {pause_reason_label}\n"
        f"**Pause Reason Code:** {pause_reason}\n"
        f"**Deposit:** {extract_primary_deposit(current_step_text) or 'none'}\n"
        f"**Gate Result Passed:** {gate_result.get('passed', False)}\n"
        f"**Total Steps:** {total_steps}\n\n"
        f"{pause_section}\n\n"
        f"## Files Changed\n\n"
    )
    for fc in gate_result.get("files_changed", []):
        content += f"- {fc}\n"

    if intermediate_decisions:
        content += f"\n## Intermediate Decisions Detected\n\n"
        content += f"{len(intermediate_decisions)} phrase-matched blocks. Review for agent decisions narrated mid-step:\n\n"
        for block in intermediate_decisions:
            phrases_str = ", ".join(block["matched_phrases"])
            content += f"- **Event {block['event_idx']}:** {block['text']} _(matched: {phrases_str})_\n"

    if planner_py_decision:
        content += f"\n## Planner.py Decision (legacy)\n\n{json.dumps(planner_py_decision)}\n"

    filepath.write_text(content)
    return str(filepath)


def _log_stderr(level: str, message: str) -> None:
    """Emit a log line to stderr: HH:MM:SS [LEVEL] message."""
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"{ts} [{level}] {message}", file=sys.stderr)


def _notify_malformed_verdict(filepath, first_line):
    """Post Pushover notification for malformed verdict, deduped per (filepath, failure-type)."""
    key = (str(filepath), "malformed_content")
    if key in _NOTIFIED_MALFORMED:
        return
    try:
        notifier.push(
            notifier._app_key, notifier._user_key,
            "Bellows — Malformed Verdict",
            f"{filepath.name} — first line: {first_line}",
        )
        _NOTIFIED_MALFORMED.add(key)
    except Exception:
        pass


def check_verdict(plan_slug, step_number):
    """Check if a verdict file exists in verdicts/resolved/."""
    resolved_dir = VERDICTS_DIR / "resolved"
    filename = f"verdict-{plan_slug}-step-{step_number}.md"
    filepath = resolved_dir / filename

    if not filepath.exists():
        if VERDICT_PARSE_LOG_VERBOSE:
            _log_stderr("DEBUG", f"verdict scan: {filepath} — exists=False — outcome=not_found")
        return {"found": False}

    text = filepath.read_text()
    lines = text.strip().splitlines()
    if not lines:
        if VERDICT_PARSE_LOG_VERBOSE:
            _log_stderr("DEBUG", f"verdict scan: {filepath} — exists=True — outcome=empty")
        return {"found": False}

    first_line = lines[0].strip()
    match = re.match(r"^(?:verdict:\s*)?(continue|stop)$", first_line, re.IGNORECASE)
    if not match:
        _log_stderr("WARN", f"verdict file malformed: {filepath} — first line: {first_line!r} — expected pattern: 'continue', 'stop', 'verdict: continue', or 'verdict: stop' (case-insensitive)")
        _notify_malformed_verdict(filepath, first_line)
        if VERDICT_PARSE_LOG_VERBOSE:
            _log_stderr("DEBUG", f"verdict scan: {filepath} — exists=True — outcome=malformed")
        return {"found": False}

    verdict = match.group(1).lower()
    reason = "\n".join(lines[1:]).strip() if len(lines) > 1 else ""
    if VERDICT_PARSE_LOG_VERBOSE:
        _log_stderr("DEBUG", f"verdict scan: {filepath} — exists=True — outcome=parsed_{verdict}")
    return {"found": True, "verdict": verdict, "reason": reason}


def log_to_ledger(plan_path, step_number, gate_result, verdict, reason, pause_reason_code: Optional[str] = None):
    """Append a JSON line to verdicts/ledger.jsonl."""
    VERDICTS_DIR.mkdir(parents=True, exist_ok=True)
    ledger_path = VERDICTS_DIR / "ledger.jsonl"

    entry = {
        "timestamp": datetime.now().isoformat(),
        "plan_path": plan_path,
        "step": step_number,
        "gate_failures": gate_result.get("failures", []),
        "files_changed": gate_result.get("files_changed", []),
        "verdict": verdict,
        "reason": reason,
        "pause_reason_code": pause_reason_code,
    }

    with open(ledger_path, "a") as f:
        f.write(json.dumps(entry) + "\n")
