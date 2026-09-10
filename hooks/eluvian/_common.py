"""
Shared helpers for the Eluvian harness hooks (hooks/eluvian/).

Contains: _DEFAULT_LOG, _VALID_SESSION_ID, _default_root, _log_path, hooklog,
emit, _validate_session_id.

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
