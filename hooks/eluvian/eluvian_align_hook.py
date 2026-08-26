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

# Machine layouts differ (shop machine: ~/Developer/GitHub; Mac mini:
# ~/Developer/eluvian-governance). Same override name as the wrap hooks.
_GOV_ROOT = Path(os.environ.get("ELUVIAN_WRAP_ROOT")
                 or "/Users/marklehn/Developer/GitHub")
_DOCTRINE = _GOV_ROOT / "ELUVIAN_PATH.md"
_BATON = _GOV_ROOT / "shop_next_session.md"
# bellows is a populated submodule on the shop machine, a sibling checkout on
# the mini (the root's submodule dirs sit uninitialized there).
_STATUS_PY = next(
    (p for p in (_GOV_ROOT / "bellows" / "status.py",
                 Path.home() / "Developer" / "bellows" / "status.py")
     if p.exists()),
    _GOV_ROOT / "bellows" / "status.py",
)
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


_SYNC_TIMEOUT = 5


def _sync_repos():
    """Core repos to freshness-check, by existence (machine-portable)."""
    repos = [("root", _GOV_ROOT),
             ("bellows", _STATUS_PY.parent),
             ("lessons-forge", _GOV_ROOT / "lessons-forge")]
    mem = os.environ.get("ELUVIAN_WRAP_MEMORY")
    if mem:
        repos.append(("memory", Path(mem)))
    return [(l, p) for l, p in repos if (p / ".git").exists()]


def _repo_sync(label, path):
    """Bounded fetch + upstream compare. REPORT ONLY — never mutates the tree.
    Returns (label, state); state: current | ahead N (unpushed) | BEHIND N |
    DIVERGED (ahead A, behind B) | no upstream | fetch FAILED[...]."""
    def _git(*args):
        return subprocess.run(
            ["git", "-C", str(path), *args],
            capture_output=True, text=True, timeout=_SYNC_TIMEOUT,
            env={**os.environ, "GIT_TERMINAL_PROMPT": "0"},
        )
    try:
        fetch_failed = _git("fetch", "origin", "--quiet").returncode != 0
        r = _git("rev-list", "--count", "--left-right", "HEAD...@{u}")
        if r.returncode != 0:
            return (label, "fetch FAILED" if fetch_failed else "no upstream")
        ahead, behind = (int(x) for x in r.stdout.split())
        if fetch_failed:
            return (label, f"fetch FAILED (stale view: ahead {ahead}, behind {behind})")
        if ahead and behind:
            return (label, f"DIVERGED (ahead {ahead}, behind {behind})")
        if behind:
            return (label, f"BEHIND {behind}")
        if ahead:
            return (label, f"ahead {ahead} (unpushed)")
        return (label, "current")
    except Exception:
        return (label, "fetch FAILED")


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
    sync = [_repo_sync(l, p) for l, p in _sync_repos()]
    problems = [(l, s) for l, s in sync
                if s != "current" and not s.startswith("ahead")]
    if problems:
        parts.append("⚠️ Sync: " + "; ".join(f"{l} {s}" for l, s in problems)
                     + " — run /eluvian to pull (ff-only) or resolve deliberately")
    else:
        unpushed = [f"{l} {s}" for l, s in sync if s.startswith("ahead")]
        parts.append("Sync: core repos current"
                     + (f" ({'; '.join(unpushed)})" if unpushed else "."))
    parts.append("Type /eluvian for the full alignment pass.")

    hooklog("SessionStart-align", f"parked={parked} sync={sync}")
    emit("\n".join(parts))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        print("⚠️ eluvian_align_hook: internal error (FAIL-OPEN, continuing)")
        print("{}")
        sys.exit(0)
