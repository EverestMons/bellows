"""
Shared helpers for the Eluvian harness hooks (hooks/eluvian/).

Contains: _DEFAULT_LOG, _VALID_SESSION_ID, _default_root, _log_path, hooklog,
emit, _validate_session_id, _OK_PREFIXES, advisory_lines, compose_advisory_message.

Imported by every hook through its own directory (via sys.path.insert before
the import). A hook that needs a helper adds it here, never inline.
"""
from __future__ import annotations

import datetime
import json
import os
import re
import sys
from pathlib import Path

_DEFAULT_LOG = Path("/Users/marklehn/.claude/eluvian/hooks.log")

_VALID_SESSION_ID = re.compile(r"^[A-Za-z0-9-]+$")


def _default_root() -> Path:
    """The governance root when $ELUVIAN_WRAP_ROOT is unset: the two known homes,
    admitted only by their COMPANY.md marker; the first if neither holds it — a
    hook must never crash a session. Shared by the hooks through `_common.py`
    since plan hooks-shared-common (2026-09-10); the hooks load from
    `hooks/eluvian/` on every machine — a symlink on the mini, the repo path
    in the shop's settings (MACHINE_SETUP v1.1a). Plan 100015 duplicated this
    body on the copies premise; `test_hook_default_root` (d) now asserts the
    four hooks that resolve a root bind THIS function."""
    for cand in (Path.home() / "Developer" / "eluvian-governance",
                 Path.home() / "Developer" / "GitHub"):
        if (cand / "COMPANY.md").is_file():
            return cand
    return Path.home() / "Developer" / "eluvian-governance"


def _log_path():
    return Path(os.environ.get("ELUVIAN_HOOKS_LOG") or str(_DEFAULT_LOG))


def hooklog(event, detail=""):
    try:
        ts = datetime.datetime.now().isoformat(timespec="seconds")
        with _log_path().open("a") as f:
            f.write(f"{ts}\t{event}\t{detail}\n")
    except Exception:
        pass


def emit(context):
    out = {}
    if context:
        out = {
            "hookSpecificOutput": {
                "hookEventName": "SessionStart",
                "additionalContext": context,
            }
        }
    print(json.dumps(out))
    sys.exit(0)


def _validate_session_id(raw_id):
    """Return raw_id if non-empty and [A-Za-z0-9-] only, else None."""
    if not raw_id or not isinstance(raw_id, str):
        return None
    raw_id = raw_id.strip()
    if not raw_id or not _VALID_SESSION_ID.match(raw_id):
        return None
    return raw_id


# Deny-list: lines whose leading text begins with one of these prefixes are OK
# status lines and are excluded from advisory surfacing (thread 427).
# A deny-list fails loud — a new print site surfaces by default; an allow-list
# would fail silent, which is the defect this module exists to end.
_OK_PREFIXES = ("wrap_check: OK", "[2r/receipts] OK")


def advisory_lines(checker_stdout: str) -> list:
    """Return non-blank, right-stripped lines from checker_stdout that are not OK.

    A line is OK when its text with leading whitespace removed begins with one
    of _OK_PREFIXES.  None or '' yields [].  The deny-list means a print site
    added later surfaces by default (thread 427).
    """
    if not checker_stdout:
        return []
    result = []
    for line in checker_stdout.splitlines():
        stripped = line.rstrip()
        if not stripped.strip():
            continue
        if any(stripped.lstrip().startswith(p) for p in _OK_PREFIXES):
            continue
        result.append(stripped)
    return result


def compose_advisory_message(lines: list) -> str:
    """Compose a message from non-OK lines a passing checker printed (thread 427).

    When any line begins with the crash prefix the wrap state is UNVERIFIED —
    the checker passed open after an internal error, so any failure it had
    found before the crash was discarded.  The header never says 'debt' and
    never directs a /wrap (plan 100129 item 2(b)).
    """
    has_crash = any(
        ln.lstrip().startswith("wrap_check: internal error") for ln in lines
    )
    if has_crash:
        header = (
            "⚠️ WRAP CHECK CRASHED AND PASSED OPEN — the wrap state is "
            "UNVERIFIED. Its verdict is UNKNOWN: any failure it found before the "
            "crash was discarded. Lines it printed (thread 427):"
        )
    else:
        header = (
            "The wrap check passed (exit 0). The lines below are additional "
            "output — warnings or checks it could not complete. What each "
            "names was NOT verified (thread 427):"
        )
    return "\n".join([header] + lines)
