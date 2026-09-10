#!/usr/bin/env python3
"""
Eluvian wrap-arm — Claude Code `UserPromptSubmit` hook.

Makes the PHRASE the trigger, not the model's memory. When the user's message is a
wrap command ("/wrap", "session wrap", "wrap the session", "wrap up"), this drops
a per-session `.wrap-in-progress-{session_id}` sentinel so the Stop-hook completion
lock engages — WITHOUT relying on the model to remember to arm it.

Match policy (deliberate bias toward arming):
  - A false ARM is cheap: the next turn gets blocked with the checklist; abort with
    `rm .wrap-in-progress-*`.
  - A false MISS is the failure we're eliminating (a silent skip).
  So we match liberally BUT anchor to the message start, so command-style messages
  ("session wrap") arm while questions/discussion ("when I say session wrap...",
  "can you explain the wrap") do not.

Per-session sentinel: each session arms `.wrap-in-progress-{session_id}` so
ownership is scoped. Missing or invalid session_id falls back to the bare
`.wrap-in-progress` (legacy behavior) — do NOT invent an id.

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

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _common import _default_root, _log_path, hooklog, _validate_session_id

_DEFAULT_ROOT = _default_root()

# Anchored at message start. Allows a short polite/lead-in prefix only.
TRIGGER = re.compile(
    r"^\s*(please\s+|ok(ay)?\s+|now\s+|let'?s\s+|go\s+ahead\s+and\s+)*"
    r"(/wrap\b|do\s+(the\s+|a\s+)?session\s*wrap|session\s*wrap|"
    r"wrap\s+(up\s+)?(the\s+)?session|wrap\s+up)\b",
    re.IGNORECASE,
)


def _wrap_root():
    return Path(os.environ.get("ELUVIAN_WRAP_ROOT") or str(_DEFAULT_ROOT))


def _sentinel_for(session_id):
    """Per-session sentinel if valid id, bare sentinel otherwise."""
    root = _wrap_root()
    if session_id:
        return root / f".wrap-in-progress-{session_id}"
    return root / ".wrap-in-progress"


def main():
    try:
        raw = sys.stdin.read()
        data = json.loads(raw) if raw.strip() else {}
    except Exception:
        print("{}")
        return

    raw_sid = data.get("session_id")
    session_id = _validate_session_id(str(raw_sid) if raw_sid is not None else None)
    log_sid = session_id or "unknown"

    prompt = (data.get("prompt") or "").strip()
    if TRIGGER.search(prompt):
        sentinel = _sentinel_for(session_id)
        hooklog("UserPromptSubmit-arm", f"ARMED sid={log_sid}")
        try:
            sentinel.touch()
            print(json.dumps({
                "hookSpecificOutput": {
                    "hookEventName": "UserPromptSubmit",
                    "additionalContext": (
                        "[wrap-lock ARMED] A session wrap was requested; the "
                        "completion lock is engaged. FIRST invoke the /wrap "
                        "skill (Skill tool, skill \"wrap\") — it loads the "
                        "canonical ritual; a phrase-triggered wrap follows "
                        "the SAME ritual as /wrap, never memory. You cannot "
                        "end a turn until wrap_check.py verifies all four "
                        "repos. If this was not a wrap request, remove "
                        f"{sentinel} to disarm."
                    ),
                }
            }))
            return
        except Exception:
            pass
    hooklog("UserPromptSubmit-arm", f"ignored sid={log_sid}")
    print("{}")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        print("{}")
