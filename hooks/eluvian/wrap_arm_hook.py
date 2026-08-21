#!/usr/bin/env python3
"""
Eluvian wrap-arm — Claude Code `UserPromptSubmit` hook.

Makes the PHRASE the trigger, not the model's memory. When the user's message is a
wrap command ("/wrap", "session wrap", "wrap the session", "wrap up"), this drops
the `.wrap-in-progress` sentinel so the Stop-hook completion lock engages — WITHOUT
relying on the model to remember to arm it.

Match policy (deliberate bias toward arming):
  - A false ARM is cheap: the next turn gets blocked with the checklist; abort with
    `rm .wrap-in-progress`.
  - A false MISS is the failure we're eliminating (a silent skip).
  So we match liberally BUT anchor to the message start, so command-style messages
  ("session wrap") arm while questions/discussion ("when I say session wrap...",
  "can you explain the wrap") do not.

FAIL-OPEN: never blocks the prompt; on any error it just lets the prompt through.

No daemon-exemption guard: a daemon prompt never matches the arm trigger,
and adding one would be an untested change with no failure it prevents.
"""
from __future__ import annotations

import datetime
import json
import os
import re
import sys
from pathlib import Path

_DEFAULT_ROOT = Path("/Users/marklehn/Developer/GitHub")
_DEFAULT_LOG = Path("/Users/marklehn/.claude/eluvian/hooks.log")

# Anchored at message start. Allows a short polite/lead-in prefix only.
TRIGGER = re.compile(
    r"^\s*(please\s+|ok(ay)?\s+|now\s+|let'?s\s+|go\s+ahead\s+and\s+)*"
    r"(/wrap\b|do\s+(the\s+|a\s+)?session\s*wrap|session\s*wrap|"
    r"wrap\s+(up\s+)?(the\s+)?session|wrap\s+up)\b",
    re.IGNORECASE,
)


def _wrap_root():
    return Path(os.environ.get("ELUVIAN_WRAP_ROOT") or str(_DEFAULT_ROOT))


def _sentinel_path():
    return _wrap_root() / ".wrap-in-progress"


def _log_path():
    return Path(os.environ.get("ELUVIAN_HOOKS_LOG") or str(_DEFAULT_LOG))


def hooklog(event, detail=""):
    try:
        ts = datetime.datetime.now().isoformat(timespec="seconds")
        with _log_path().open("a") as f:
            f.write(f"{ts}\t{event}\t{detail}\n")
    except Exception:
        pass


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
        data = json.loads(raw) if raw.strip() else {}
    except Exception:
        print("{}")
        return

    try:
        session_id = str(data["session_id"]) if data.get("session_id") else "unknown"
    except Exception:
        session_id = "unknown"

    prompt = (data.get("prompt") or "").strip()
    if TRIGGER.search(prompt):
        sentinel = _sentinel_path()
        hooklog("UserPromptSubmit-arm", f"ARMED sid={session_id}")
        try:
            sentinel.touch()
            print(json.dumps({
                "hookSpecificOutput": {
                    "hookEventName": "UserPromptSubmit",
                    "additionalContext": (
                        "[wrap-lock ARMED] A session wrap was requested; the "
                        "completion lock is engaged. Follow the /wrap ritual "
                        "(eluvian-session-wrap-ritual memory); you cannot end a "
                        "turn until wrap_check.py verifies all four repos. If this "
                        f"was not a wrap request, remove {sentinel} to disarm."
                    ),
                }
            }))
            return
        except Exception:
            pass
    hooklog("UserPromptSubmit-arm", f"ignored sid={session_id}")
    print("{}")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        print("{}")
