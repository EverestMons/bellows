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
"""
from __future__ import annotations

import datetime
import json
import re
import sys
from pathlib import Path

ROOT = Path("/Users/marklehn/Developer/GitHub")
SENTINEL = ROOT / ".wrap-in-progress"
LOG = Path("/Users/marklehn/.claude/eluvian/hooks.log")


def hooklog(event: str, detail: str = "") -> None:
    """Append-only trace proving the HARNESS invoked this hook. Never raises."""
    try:
        ts = datetime.datetime.now().isoformat(timespec="seconds")
        with LOG.open("a") as f:
            f.write(f"{ts}\t{event}\t{detail}\n")
    except Exception:
        pass

# Anchored at message start. Allows a short polite/lead-in prefix only.
TRIGGER = re.compile(
    r"^\s*(please\s+|ok(ay)?\s+|now\s+|let'?s\s+|go\s+ahead\s+and\s+)*"
    r"(/wrap\b|do\s+(the\s+|a\s+)?session\s*wrap|session\s*wrap|"
    r"wrap\s+(up\s+)?(the\s+)?session|wrap\s+up)\b",
    re.IGNORECASE,
)


def main():
    try:
        raw = sys.stdin.read()
        data = json.loads(raw) if raw.strip() else {}
    except Exception:
        print("{}")
        return
    prompt = (data.get("prompt") or "").strip()
    if TRIGGER.search(prompt):
        hooklog("UserPromptSubmit-arm", "ARMED")
        try:
            SENTINEL.touch()
            print(json.dumps({
                "hookSpecificOutput": {
                    "hookEventName": "UserPromptSubmit",
                    "additionalContext": (
                        "[wrap-lock ARMED] A session wrap was requested; the "
                        "completion lock is engaged. Follow the /wrap ritual "
                        "(eluvian-session-wrap-ritual memory); you cannot end a "
                        "turn until wrap_check.py verifies all four repos. If this "
                        f"was not a wrap request, remove {SENTINEL} to disarm."
                    ),
                }
            }))
            return
        except Exception:
            pass
    hooklog("UserPromptSubmit-arm", "ignored")
    print("{}")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        print("{}")
