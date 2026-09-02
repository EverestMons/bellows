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

def _default_root() -> Path:
    """The governance root when $ELUVIAN_WRAP_ROOT is unset: the two known homes,
    admitted only by their COMPANY.md marker; the first if neither holds it — a
    hook must never crash a session. Duplicated verbatim in the four hooks by
    design: they are standalone files copied into ~/.claude/eluvian/, and a
    shared module would be one more file to install (test_hook_default_root
    asserts the four bodies stay identical). Plan hooks-de-hardcode, 2026-09-02."""
    for cand in (Path.home() / "Developer" / "eluvian-governance",
                 Path.home() / "Developer" / "GitHub"):
        if (cand / "COMPANY.md").is_file():
            return cand
    return Path.home() / "Developer" / "eluvian-governance"


_DEFAULT_ROOT = _default_root()
_DEFAULT_LOG = Path("/Users/marklehn/.claude/eluvian/hooks.log")

# Anchored at message start. Allows a short polite/lead-in prefix only.
TRIGGER = re.compile(
    r"^\s*(please\s+|ok(ay)?\s+|now\s+|let'?s\s+|go\s+ahead\s+and\s+)*"
    r"(/wrap\b|do\s+(the\s+|a\s+)?session\s*wrap|session\s*wrap|"
    r"wrap\s+(up\s+)?(the\s+)?session|wrap\s+up)\b",
    re.IGNORECASE,
)

_VALID_SESSION_ID = re.compile(r"^[A-Za-z0-9-]+$")


def _wrap_root():
    return Path(os.environ.get("ELUVIAN_WRAP_ROOT") or str(_DEFAULT_ROOT))


def _log_path():
    return Path(os.environ.get("ELUVIAN_HOOKS_LOG") or str(_DEFAULT_LOG))


def _validate_session_id(raw_id):
    """Return raw_id if non-empty and [A-Za-z0-9-] only, else None."""
    if not raw_id or not isinstance(raw_id, str):
        return None
    raw_id = raw_id.strip()
    if not raw_id or not _VALID_SESSION_ID.match(raw_id):
        return None
    return raw_id


def _sentinel_for(session_id):
    """Per-session sentinel if valid id, bare sentinel otherwise."""
    root = _wrap_root()
    if session_id:
        return root / f".wrap-in-progress-{session_id}"
    return root / ".wrap-in-progress"


def hooklog(event, detail=""):
    try:
        ts = datetime.datetime.now().isoformat(timespec="seconds")
        with _log_path().open("a") as f:
            f.write(f"{ts}\t{event}\t{detail}\n")
    except Exception:
        pass


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
