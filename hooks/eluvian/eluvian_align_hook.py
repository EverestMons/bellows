#!/usr/bin/env python3
"""
Eluvian alignment — Claude Code `SessionStart` hook.

Emits a compact context block at session start: doctrine pointer, daemon
status, parked-arc count, and a nudge to type /eluvian.  FAIL-OPEN: any
internal error prints a one-line warning and exits 0.
"""
from __future__ import annotations

import datetime
import json
import os
import re
import subprocess
import sys
from pathlib import Path

_GOV_ROOT = Path("/Users/marklehn/Developer/GitHub")
_DOCTRINE = _GOV_ROOT / "ELUVIAN_PATH.md"
_BATON = _GOV_ROOT / "shop_next_session.md"
_STATUS_PY = _GOV_ROOT / "bellows" / "status.py"
_DEFAULT_LOG = Path("/Users/marklehn/.claude/eluvian/hooks.log")

_PARKED_RE = re.compile(r"⏸|PARKED|RESUME AT", re.IGNORECASE)


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


def _daemon_status():
    try:
        res = subprocess.run(
            [sys.executable, str(_STATUS_PY)],
            capture_output=True, text=True, timeout=10,
        )
        first = (res.stdout or "").strip().split("\n")[0]
        return first or "unknown"
    except Exception:
        return "unknown"


def _parked_count():
    try:
        text = _BATON.read_text(encoding="utf-8")
        return sum(1 for line in text.splitlines() if _PARKED_RE.search(line))
    except Exception:
        return 0


def main():
    try:
        sys.stdin.read()
    except Exception:
        pass

    daemon = _daemon_status()
    parked = _parked_count()

    parts = [
        f"Eluvian doctrine: {_DOCTRINE}",
        f"Daemon: {daemon}",
    ]
    if parked:
        parts.append(f"Parked arcs: {parked}")
    parts.append("Type /eluvian for the full alignment pass.")

    hooklog("SessionStart-align", f"parked={parked}")
    emit("\n".join(parts))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        print("⚠️ eluvian_align_hook: internal error (FAIL-OPEN, continuing)")
        print("{}")
        sys.exit(0)
