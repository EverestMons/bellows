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
import datetime
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path("/Users/marklehn/Developer/GitHub")
SENTINEL = ROOT / ".wrap-in-progress"
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


def allow():
    print("{}")
    sys.exit(0)


def block(reason: str):
    print(json.dumps({"decision": "block", "reason": reason}))
    sys.exit(0)


def main():
    # Drain stdin (hook receives JSON; we don't need its contents).
    try:
        sys.stdin.read()
    except Exception:
        pass

    if not SENTINEL.exists():
        hooklog("Stop", "unarmed-allow")
        allow()  # wrap not armed -> nothing to enforce

    try:
        res = subprocess.run(
            [sys.executable, str(CHECK)],
            capture_output=True, text=True, timeout=120,
        )
    except Exception as exc:
        # Checker won't run -> fail open, but leave the sentinel so the next
        # turn re-attempts enforcement rather than silently disarming.
        block(
            f"[wrap-lock] Could not run wrap_check ({exc}). Wrap is still armed. "
            f"Run `python3 {CHECK}` manually to see remaining steps, or remove "
            f"{SENTINEL} to disarm."
        )

    if res.returncode == 0:
        try:
            SENTINEL.unlink()
        except FileNotFoundError:
            pass
        hooklog("Stop", "armed-pass-disarm")
        allow()  # wrap complete -> disarm and let the turn end

    hooklog("Stop", "armed-BLOCK")
    reason = (res.stdout or "").strip() or "Session wrap is incomplete."
    block(
        reason
        + "\n\n[wrap-lock] This turn is blocked until the wrap verifies. "
        + "Complete the steps above; the lock clears automatically. "
        + f"(To abort a wrap, delete {SENTINEL}.)"
    )


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        # Absolute last-resort fail-open.
        print(json.dumps({"systemMessage": f"wrap_stop_hook error, allowing: {exc}"}))
        sys.exit(0)
