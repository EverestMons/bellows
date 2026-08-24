#!/usr/bin/env python3
"""
Eluvian unwrapped-debt gate — Claude Code `SessionStart` hook.

Runs when a new session begins. A `SessionStart` hook cannot veto the session,
but it CAN inject context. If a prior session left wrap debt (untracked Done/
plans, uncommitted verdicts/baton/memory, unpushed commits), this surfaces the
debt at the top of the new session as a directive to resolve it before new work —
closing the one gap the Stop-hook lock structurally cannot (a terminal closed
without ever arming a wrap).

Signal-only when clean: emits nothing, so a fresh session isn't nagged.
FAIL-OPEN: any error stays silent rather than injecting noise.
"""
from __future__ import annotations

import datetime
import json
import os
import re
import subprocess
import sys
from pathlib import Path

CHECK = Path(__file__).with_name("wrap_check.py")
_DEFAULT_LOG = Path("/Users/marklehn/.claude/eluvian/hooks.log")

_BELLOWS_DISPATCH_ALLOW = {"1", "true", "yes"}
_VALID_SESSION_ID = re.compile(r"^[A-Za-z0-9-]+$")


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


def _parse_session_id(raw):
    try:
        if raw and raw.strip():
            data = json.loads(raw)
            if isinstance(data, dict):
                sid = data.get("session_id")
                if sid:
                    return str(sid)
    except Exception:
        pass
    return "unknown"


def main():
    try:
        raw = sys.stdin.read()
    except Exception:
        raw = ""

    session_id = _parse_session_id(raw)

    if os.environ.get("BELLOWS_DISPATCH", "").strip().lower() in _BELLOWS_DISPATCH_ALLOW:
        hooklog("SessionStart", f"daemon-exempt sid={session_id}")
        emit(None)

    check_sid = "" if session_id == "unknown" else session_id
    if check_sid and not _VALID_SESSION_ID.match(check_sid):
        check_sid = ""
    try:
        res = subprocess.run(
            [sys.executable, str(CHECK), check_sid],
            capture_output=True, text=True, timeout=120,
        )
    except Exception:
        emit(None)

    if res.returncode == 0:
        hooklog("SessionStart", f"clean sid={session_id}")
        emit(None)

    hooklog("SessionStart", f"DEBT-injected sid={session_id}")
    checklist = (res.stdout or "").strip()
    emit(
        "⚠️ UNWRAPPED SESSION DEBT DETECTED. A prior session ended without "
        "completing the wrap ritual. Resolve this BEFORE starting new work:\n\n"
        f"{checklist}\n\n"
        "This is not a fresh-session state. Treat it as a wrap in progress: "
        "you may run `/wrap` to arm the completion lock and finish the ritual."
    )


if __name__ == "__main__":
    try:
        main()
    except Exception:
        print("{}")
        sys.exit(0)
