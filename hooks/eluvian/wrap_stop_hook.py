#!/usr/bin/env python3
"""
Eluvian wrap-completion lock — Claude Code `Stop` hook.

Fires at the end of EVERY turn. It is a deliberate no-op unless a wrap is armed
(a `.wrap-in-progress` sentinel exists at the governance root). Once armed, it
runs wrap_check.py and HARD-BLOCKS the turn from ending until the wrap verifies,
feeding the remaining checklist back to the model so it keeps working. On the
first passing check it removes the sentinel (disarms) and lets the turn end.

This is the enforceable half of "session wrap never skips": you cannot end a turn
mid-ritual once you've started wrapping. (Entire-session skips — closing the
terminal without ever wrapping — are caught next session by wrap_debt_hook.py,
since no turn-end hook can veto a terminal close.)

FAIL-OPEN: any error in this hook or the checker allows the stop. A guard that
can itself trap the operator is worse than the skip it prevents.
"""
from __future__ import annotations

import datetime
import json
import os
import subprocess
import sys
from pathlib import Path

_DEFAULT_ROOT = Path("/Users/marklehn/Developer/GitHub")
CHECK = Path(__file__).with_name("wrap_check.py")
_DEFAULT_LOG = Path("/Users/marklehn/.claude/eluvian/hooks.log")

_BELLOWS_DISPATCH_ALLOW = {"1", "true", "yes"}


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


def allow():
    print("{}")
    sys.exit(0)


def block(reason):
    print(json.dumps({"decision": "block", "reason": reason}))
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
        hooklog("Stop", f"daemon-exempt sid={session_id}")
        allow()

    sentinel = _sentinel_path()

    if not sentinel.exists():
        hooklog("Stop", f"unarmed-allow sid={session_id}")
        allow()

    try:
        res = subprocess.run(
            [sys.executable, str(CHECK)],
            capture_output=True, text=True, timeout=120,
        )
    except Exception as exc:
        block(
            f"[wrap-lock] Could not run wrap_check ({exc}). Wrap is still armed. "
            f"Run `python3 {CHECK}` manually to see remaining steps, or remove "
            f"{sentinel} to disarm."
        )

    if res.returncode == 0:
        try:
            sentinel.unlink()
        except FileNotFoundError:
            pass
        hooklog("Stop", f"armed-pass-disarm sid={session_id}")
        allow()

    hooklog("Stop", f"armed-BLOCK sid={session_id}")
    reason = (res.stdout or "").strip() or "Session wrap is incomplete."
    block(
        reason
        + "\n\n[wrap-lock] This turn is blocked until the wrap verifies. "
        + "Complete the steps above; the lock clears automatically. "
        + f"(To abort a wrap, delete {sentinel}.)"
    )


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(json.dumps({"systemMessage": f"wrap_stop_hook error, allowing: {exc}"}))
        sys.exit(0)
