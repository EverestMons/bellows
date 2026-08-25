#!/usr/bin/env python3
"""
Eluvian wrap-completion lock — Claude Code `Stop` hook.

Fires at the end of EVERY turn. It is a deliberate no-op unless a wrap is armed
(any `.wrap-in-progress*` sentinel exists at the governance root). Once armed, it
runs wrap_check.py and HARD-BLOCKS the turn from ending until the wrap verifies,
feeding the remaining checklist back to the model so it keeps working.

Ownership model (plan 497):
  ARM-IF-ANY: block whenever ANY sentinel is present — bare, own, or foreign.
  UNLINK-ONLY-MINE: on a passing check, remove only this session's sentinel.
  Bare sentinels (legacy): clear on pass, never claimed by a session.
  Stale-foreign reaper: foreign per-session sentinels older than _STALE_SECONDS
  are reaped BEFORE the check so an abandoned wrap cannot wedge the machine
  indefinitely (P2). Each reap is logged. No session's Stop hook may clear
  another's ACTIVE sentinel — the reaper is a deliberate, declared, logged
  exception bounded by age.

FAIL-OPEN: any error in this hook or the checker allows the stop. A guard that
can itself trap the operator is worse than the skip it prevents.
"""
from __future__ import annotations

import datetime
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

_DEFAULT_ROOT = Path("/Users/marklehn/Developer/GitHub")
CHECK = Path(__file__).with_name("wrap_check.py")
_DEFAULT_LOG = Path("/Users/marklehn/.claude/eluvian/hooks.log")

_BELLOWS_DISPATCH_ALLOW = {"1", "true", "yes"}
_VALID_SESSION_ID = re.compile(r"^[A-Za-z0-9-]+$")
_STALE_SECONDS = 14400  # 4 hours — generous; a wrap takes minutes


def _wrap_root():
    return Path(os.environ.get("ELUVIAN_WRAP_ROOT") or str(_DEFAULT_ROOT))


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


def _validate_session_id(raw_id):
    """Return raw_id if non-empty and [A-Za-z0-9-] only, else None."""
    if not raw_id or not isinstance(raw_id, str):
        return None
    raw_id = raw_id.strip()
    if not raw_id or not _VALID_SESSION_ID.match(raw_id):
        return None
    return raw_id


def _extract_session_id(raw_stdin):
    """Extract session_id string from stdin JSON payload, or None."""
    try:
        if raw_stdin and raw_stdin.strip():
            data = json.loads(raw_stdin)
            if isinstance(data, dict):
                sid = data.get("session_id")
                if sid is not None:
                    return str(sid)
    except Exception:
        pass
    return None


def _own_sentinel(root, session_id):
    """This session's sentinel: per-session if valid id, bare if not."""
    if session_id:
        return root / f".wrap-in-progress-{session_id}"
    return root / ".wrap-in-progress"


def _all_sentinels(root):
    """All sentinel files at the root — bare + per-session."""
    result = []
    bare = root / ".wrap-in-progress"
    if bare.exists():
        result.append(bare)
    for p in sorted(root.glob(".wrap-in-progress-*")):
        if p.is_file():
            result.append(p)
    return result


def _sentinel_age_seconds(path):
    try:
        return time.time() - path.stat().st_mtime
    except Exception:
        return 0


def _format_age(seconds):
    if seconds < 60:
        return f"{int(seconds)}s"
    elif seconds < 3600:
        return f"{int(seconds // 60)}m"
    else:
        return f"{seconds / 3600:.1f}h"


def _reap_stale_foreign(root, own, log_sid):
    """Remove foreign per-session sentinels older than _STALE_SECONDS.

    Runs BEFORE wrap_check so abandoned sentinels cannot wedge the machine
    even when wrap_check is in its ordinary failing state (P2).
    Bare sentinels are never reaped — they clear on pass (legacy compat).
    """
    for s in _all_sentinels(root):
        if s == own:
            continue
        if s.name == ".wrap-in-progress":
            continue
        age = _sentinel_age_seconds(s)
        if age >= _STALE_SECONDS:
            try:
                s.unlink()
                hooklog("Stop", f"reaped-stale sentinel={s.name} age={_format_age(age)} sid={log_sid}")
            except FileNotFoundError:
                pass


def _foreign_sentinel_info(root, own):
    """Return (filename, age_seconds) for each foreign per-session sentinel."""
    foreign = []
    for s in _all_sentinels(root):
        if s == own:
            continue
        if s.name == ".wrap-in-progress":
            continue
        age = _sentinel_age_seconds(s)
        foreign.append((s.name, age))
    return foreign


def _anti_hijack_message(foreign):
    if not foreign:
        return ""
    lines = ["\n\n⚠️ OTHER SESSION(S) ARE ALSO WRAPPING:"]
    for name, age in foreign:
        lines.append(f"  • {name} (age: {_format_age(age)})")
    lines.append(
        "\nSome or all of the listed items above may belong to another session. "
        "Do NOT commit, push, add, or otherwise resolve work you did not do — "
        "wait for the other session to finish. "
        "A fresh sentinel means the session is likely still active; "
        "a stale one (hours old) may indicate an abandoned wrap. "
        "Clearing a FOREIGN sentinel is the CEO's decision alone and never the model's."
    )
    return "\n".join(lines)


def main():
    try:
        raw = sys.stdin.read()
    except Exception:
        raw = ""

    raw_sid = _extract_session_id(raw)
    session_id = _validate_session_id(raw_sid)
    log_sid = session_id or "unknown"

    if os.environ.get("BELLOWS_DISPATCH", "").strip().lower() in _BELLOWS_DISPATCH_ALLOW:
        hooklog("Stop", f"daemon-exempt sid={log_sid}")
        allow()

    root = _wrap_root()
    own = _own_sentinel(root, session_id)

    # P2: reap stale foreign sentinels BEFORE check so abandoned wraps
    # cannot wedge the machine when wrap_check is in its ordinary failing state.
    _reap_stale_foreign(root, own, log_sid)

    all_sents = _all_sentinels(root)
    if not all_sents:
        hooklog("Stop", f"unarmed-allow sid={log_sid}")
        allow()

    try:
        res = subprocess.run(
            [sys.executable, str(CHECK), session_id or "", "stop"],
            capture_output=True, text=True, timeout=120,
        )
    except Exception as exc:
        block(
            f"[wrap-lock] Could not run wrap_check ({exc}). Wrap is still armed. "
            f"Run `python3 {CHECK}` manually to see remaining steps, or remove "
            f"{own} to disarm."
        )

    if res.returncode == 0:
        # UNLINK-ONLY-MINE
        try:
            own.unlink()
        except FileNotFoundError:
            pass
        # Backward compat: bare sentinel also clears on pass
        bare = root / ".wrap-in-progress"
        if bare != own and bare.exists():
            try:
                bare.unlink()
            except FileNotFoundError:
                pass
        hooklog("Stop", f"armed-pass-disarm sid={log_sid}")
        allow()

    hooklog("Stop", f"armed-BLOCK sid={log_sid}")
    reason = (res.stdout or "").strip() or "Session wrap is incomplete."

    foreign = _foreign_sentinel_info(root, own)
    hijack_msg = _anti_hijack_message(foreign)

    block(
        reason
        + "\n\n[wrap-lock] This turn is blocked until the wrap verifies. "
        + "Complete the steps above; the lock clears automatically. "
        + f"(To abort YOUR wrap, delete {own}.)"
        + hijack_msg
    )


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(json.dumps({"systemMessage": f"wrap_stop_hook error, allowing: {exc}"}))
        sys.exit(0)
