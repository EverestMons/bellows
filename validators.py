"""Claim-time plan validators. Runs before a plan is claimed (moved to in-progress).

Distinct from gates.py which runs post-step. This module enforces header-level
authoring rules at deposit/claim time.
"""

import re
from pathlib import Path
from typing import Optional


STOP_PROSE_PATTERNS = [
    re.compile(r"STOP\.", re.IGNORECASE),
    re.compile(r"wait for confirmation", re.IGNORECASE),
    re.compile(r"do not proceed", re.IGNORECASE),
]


def _get_dispatch_mode(header: dict) -> Optional[str]:
    """Extract dispatch_mode from parsed plan header, normalizing key variants."""
    raw = header.get("dispatch_mode") or header.get("Dispatch Mode")
    if raw is None:
        return None
    return str(raw).strip().lower()


def check_missing_dispatch_mode(header: dict) -> Optional[dict]:
    """Check (c): dispatch_mode field entirely absent from plan header."""
    mode = _get_dispatch_mode(header)
    if mode is None:
        return {
            "check": "missing_dispatch_mode",
            "severity": "reject",
            "message": "Plan header missing **Dispatch Mode:** field. Per Rule 35, this field is required. Plan will not be claimed."
        }
    if mode not in ("bellows", "manual_bootstrap"):
        return {
            "check": "missing_dispatch_mode",
            "severity": "reject",
            "message": f"Plan header has invalid dispatch_mode='{mode}'. Must be 'bellows' or 'manual_bootstrap'. Plan will not be claimed."
        }
    return None


def check_dispatch_mismatch(header: dict, plan_path: str, config: dict) -> Optional[dict]:
    """Check (a): manual_bootstrap plan in a Bellows-watched directory."""
    mode = _get_dispatch_mode(header)
    if mode != "manual_bootstrap":
        return None

    plan_dir = str(Path(plan_path).parent)
    watched = config.get("watched_projects", [])
    plan_dir_resolved = str(Path(plan_dir).resolve())
    for wp in watched:
        wp_resolved = str(Path(wp).resolve())
        if plan_dir_resolved == wp_resolved:
            return {
                "check": "dispatch_mismatch",
                "severity": "warn",
                "message": f"Plan declares dispatch_mode=manual_bootstrap but is deposited in Bellows-watched directory {wp}"
            }
    return None


def check_stop_prose(header: dict, plan_text: str) -> list[dict]:
    """Check (b): STOP-prose patterns in step bodies under bellows dispatch mode."""
    mode = _get_dispatch_mode(header)
    if mode != "bellows":
        return []

    warnings = []
    in_step_body = False
    in_fenced_block = False
    in_deposits_block = False

    for line in plan_text.splitlines():
        # Detect step header boundaries
        if re.match(r"^## STEP \d+", line, re.IGNORECASE):
            in_step_body = True
            in_fenced_block = False
            in_deposits_block = False
            continue

        if not in_step_body:
            continue

        # Track fenced code blocks
        if line.strip().startswith("```"):
            in_fenced_block = not in_fenced_block
            continue
        if in_fenced_block:
            continue

        # Track **Deposits:** blocks — from marker through consecutive bullet lines
        if re.match(r'\s*\*\*Deposits:\*\*', line):
            in_deposits_block = True
            continue
        if in_deposits_block:
            stripped = line.strip()
            if stripped.startswith("- ") or stripped == "":
                continue
            else:
                in_deposits_block = False
                # Fall through to scan this line

        # Strip inline backtick content before scanning
        scan_line = re.sub(r'`[^`]*`', '', line)

        for pattern in STOP_PROSE_PATTERNS:
            if pattern.search(scan_line):
                warnings.append({
                    "check": "stop_prose",
                    "severity": "warn",
                    "message": f"STOP-prose detected in step body: '{pattern.pattern}' matched in line: {line.strip()[:80]}"
                })
                break  # One warning per line is sufficient

    return warnings


VALID_PAUSE_FOR_VERDICT_VALUES = {"always", "after_step_1", "after_qa_step", "after_each_step", ""}

STRING_TYPED_HEADER_FIELDS = ("auto_close", "pause_for_verdict", "dispatch_mode")


def check_pause_for_verdict_value(header: dict) -> Optional[dict]:
    """Check: pause_for_verdict value (if present) is a recognized enum member."""
    raw = header.get("pause_for_verdict")
    if raw is None:
        return None
    value = str(raw).strip().lower()
    if value not in VALID_PAUSE_FOR_VERDICT_VALUES:
        return {
            "check": "pause_for_verdict_value",
            "severity": "warn",
            "message": f"Plan header has unrecognized pause_for_verdict='{raw}'. Recognized values: {sorted(VALID_PAUSE_FOR_VERDICT_VALUES - {''})}. The defensive default will apply, but the Planner may have intended a different pause behavior."
        }
    return None


def check_header_field_types(header: dict) -> list[dict]:
    """Check: known header fields are string-typed after _parse_plan_header() returns."""
    warnings = []
    for field in STRING_TYPED_HEADER_FIELDS:
        value = header.get(field)
        if value is not None and not isinstance(value, str):
            warnings.append({
                "check": "header_field_type",
                "severity": "warn",
                "message": f"Header field '{field}' has type {type(value).__name__} (value: {value!r}) — expected str. YAML frontmatter may have coerced the value. Downstream code may crash on .lower() or string operations."
            })
    return warnings


def validate_at_claim(header: dict, plan_path: str, config: dict, plan_text: str) -> dict:
    """Run all claim-time validators on a plan.

    Args:
        header: Parsed plan header dict (from gates._parse_plan_header())
        plan_path: Absolute path to the plan file
        config: Bellows config dict (with watched_projects list)
        plan_text: Full plan text (for STOP-prose body scan)

    Returns:
        {
            "rejected": bool,         # True if any check returned reject
            "reject_reason": str,     # Human-readable reason (empty if not rejected)
            "warnings": [             # List of warn-level findings
                {"check": str, "severity": "warn", "message": str},
                ...
            ]
        }
    """
    warnings = []

    # Check (c): missing or invalid dispatch_mode — reject
    missing_result = check_missing_dispatch_mode(header)
    if missing_result is not None:
        return {
            "rejected": True,
            "reject_reason": missing_result["message"],
            "warnings": [],
        }

    # Check (a): mismatch — warn
    mismatch_result = check_dispatch_mismatch(header, plan_path, config)
    if mismatch_result is not None:
        warnings.append(mismatch_result)

    # Check (b): STOP-prose — warn
    stop_warnings = check_stop_prose(header, plan_text)
    warnings.extend(stop_warnings)

    # Check: pause_for_verdict enum value — warn
    pause_result = check_pause_for_verdict_value(header)
    if pause_result is not None:
        warnings.append(pause_result)

    # Check: header field types — warn
    type_warnings = check_header_field_types(header)
    warnings.extend(type_warnings)

    return {
        "rejected": False,
        "reject_reason": "",
        "warnings": warnings,
    }
