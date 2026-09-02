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


_GOV_ROOT = Path(os.environ.get("ELUVIAN_WRAP_ROOT") or _default_root())
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


def _resolve_sibling(env_var, *candidates):
    """First candidate that is a real checkout (has .git). None if none is.

    A repo is not in the same place, or under the same NAME, on every machine:
    lessons-forge is `<root>/lessons-forge` (populated submodule) on the shop
    machine and `~/Developer/forge_lessons` on the mini. And an UNINITIALIZED
    submodule dir is present-but-empty, so an existence test on the root-
    relative path passes while the real checkout goes unexamined.
    """
    env = os.environ.get(env_var)
    if env:
        # An explicit override is AUTHORITATIVE — never fall back past it.
        # Falling through on a typo'd override would silently resolve to a
        # different repo than the operator named, which is the same
        # wrong-target failure this resolver exists to prevent. Matches
        # wrap_check._resolve_bellows.
        return Path(env) if (Path(env) / ".git").exists() else None
    for c in candidates:
        if (Path(c) / ".git").exists():
            return Path(c)
    return None


def _sync_repos():
    """Core repos to freshness-check.

    Returns (resolved, unresolved): resolved is [(label, path)]; unresolved is
    [label] for repos that could not be located on this machine.

    ⚠️ Unresolved repos are RETURNED, not dropped. The previous form filtered
    on `(p / ".git").exists()` and silently omitted anything whose path was
    wrong for this layout — which made "this repo is not checked here" look
    identical to "this repo is current". Measured on the mini: lessons-forge
    resolved to an empty uninitialized submodule dir, was dropped, and sat
    101 commits behind while the report named only root and bellows.
    """
    home_dev = Path.home() / "Developer"
    repos = [
        ("root", _GOV_ROOT),
        ("bellows", _STATUS_PY.parent),
        ("lessons-forge", _resolve_sibling(
            "ELUVIAN_WRAP_LESSONS_FORGE",
            _GOV_ROOT / "lessons-forge",
            home_dev / "lessons-forge",
            home_dev / "forge_lessons")),
    ]
    mem = os.environ.get("ELUVIAN_WRAP_MEMORY")
    if mem:
        # The mini deliberately points this at a NON-git auto-memory dir;
        # absent .git there is by design, not a resolution failure.
        mem_p = Path(mem)
        if (mem_p / ".git").exists():
            repos.append(("memory", mem_p))
    resolved = [(l, p) for l, p in repos if p and (Path(p) / ".git").exists()]
    unresolved = [l for l, p in repos if not (p and (Path(p) / ".git").exists())]
    return resolved, unresolved


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


# The baton is append-only with newest blocks at the top; counting the whole
# file counts every parked marker ever written (measured inflating 44→47 in
# two days — tuyere thread 3). "The head" = the newest two session blocks:
# scan up to the third top-level block header, capped at 200 lines.
_BLOCK_RE = re.compile(r"^> ## ")


def _parked_count():
    try:
        lines = _BATON.read_text(encoding="utf-8").splitlines()
        blocks = 0
        count = 0
        for i, line in enumerate(lines):
            if _BLOCK_RE.match(line):
                blocks += 1
                if blocks >= 3:
                    break
            if i >= 200:
                break
            if _PARKED_RE.search(line):
                count += 1
        return count
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
    _resolved, _unresolved = _sync_repos()
    sync = [_repo_sync(l, p) for l, p in _resolved]
    problems = [(l, s) for l, s in sync
                if s != "current" and not s.startswith("ahead")]
    problems += [(l, "NOT RESOLVED on this machine — not freshness-checked")
                 for l in _unresolved]
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
