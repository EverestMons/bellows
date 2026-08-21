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
import subprocess
import sys
from pathlib import Path

CHECK = Path(__file__).with_name("wrap_check.py")
LOG = Path("/Users/marklehn/.claude/eluvian/hooks.log")


def hooklog(event: str, detail: str = "") -> None:
    """Append-only trace proving the HARNESS invoked this hook. Never raises."""
    try:
        ts = datetime.datetime.now().isoformat(timespec="seconds")
        with LOG.open("a") as f:
            f.write(f"{ts}\t{event}\t{detail}\n")
    except Exception:
        pass


def emit(context: str | None):
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


def main():
    try:
        sys.stdin.read()
    except Exception:
        pass
    try:
        res = subprocess.run(
            [sys.executable, str(CHECK)],
            capture_output=True, text=True, timeout=120,
        )
    except Exception:
        emit(None)  # fail open, silent

    if res.returncode == 0:
        hooklog("SessionStart", "clean")
        emit(None)  # no debt -> stay quiet

    hooklog("SessionStart", "DEBT-injected")
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
