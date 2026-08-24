#!/usr/bin/env python3
"""
Eluvian session-wrap verifier — the single source of truth for "is the wrap done?"

Used by two hooks:
  - Stop hook (wrap_stop_hook.sh): while a wrap is in progress, HARD-BLOCKS the
    turn from ending until every check below passes.
  - SessionStart hook (wrap_debt_hook.sh): at the start of a new session, reports
    leftover wrap debt from a prior (un-wrapped) session.

Design principles (mirroring the memory lessons this is meant to enforce):
  - FAIL-OPEN on checker error: a bug in THIS script must never trap a session.
    Any unexpected exception -> exit 0 with a printed warning.
  - FAIL-CLOSED on genuine incompleteness: if the ritual is verifiably not done,
    exit 1 with a precise, actionable checklist.
  - Checks assert the ritual's DELTAS, not full repo cleanliness (the root carries
    unrelated untracked files by design — see the wrap ritual memory).

Exit codes:
  0  = wrap complete (or fail-open on internal error)
  1  = wrap incomplete; stdout lists exactly what remains

Ritual reference: eluvian-session-wrap-ritual memory. Four repos:
  1. project repos  — untracked knowledge/decisions/Done/ plan files committed
  2. bellows        — verdicts/resolved/ committed AND pushed
  3. governance root— baton refreshed+committed, bellows gitlink bumped, 3b done
  4. memory repo    — committed AND pushed (if touched)
"""
from __future__ import annotations

import datetime
import os
import subprocess
import sys
from pathlib import Path

# Machine layouts differ (shop machine: ~/Developer/GitHub; Mac mini:
# ~/Developer/eluvian-governance). Same override names as the arm/stop hooks.
ROOT = Path(os.environ.get("ELUVIAN_WRAP_ROOT")
            or "/Users/marklehn/Developer/GitHub")
BELLOWS = ROOT / "bellows"
MEMORY = Path(os.environ.get("ELUVIAN_WRAP_MEMORY")
              or "/Users/marklehn/.claude/projects/-Users-marklehn-Developer-GitHub/memory")
BATON = ROOT / "shop_next_session.md"


def git(repo: Path, *args) -> str:
    """Run a git command in `repo`, return stdout stripped. '' on any failure."""
    try:
        out = subprocess.run(
            ["git", "-C", str(repo), *args],
            capture_output=True, text=True, timeout=30,
        )
        return out.stdout.strip()
    except Exception:
        return ""


def porcelain(repo: Path, pathspec: str | None = None) -> list[str]:
    """Lines of `git status --porcelain` (optionally scoped to a pathspec)."""
    args = ["status", "--porcelain"]
    if pathspec:
        args += ["--", pathspec]
    out = git(repo, *args)
    return [ln for ln in out.splitlines() if ln.strip()]


def unpushed_count(repo: Path) -> int | None:
    """Commits ahead of upstream. None if no upstream configured (can't tell)."""
    up = git(repo, "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}")
    if not up:
        return None
    n = git(repo, "rev-list", "--count", "@{u}..HEAD")
    try:
        return int(n)
    except ValueError:
        return None


def project_done_dirs() -> list[Path]:
    """Every <repo>/knowledge/decisions/Done directory under the root."""
    return sorted(ROOT.glob("*/knowledge/decisions/Done"))


def check() -> list[str]:
    """Return a list of failure messages. Empty list == wrap complete."""
    fails: list[str] = []
    today = datetime.date.today().isoformat()

    # --- Step 1: project repos — no UNTRACKED completed plans in Done/ ----------
    for done in project_done_dirs():
        repo = done.parents[2]  # <repo>/knowledge/decisions/Done -> <repo>
        # untracked (??) or modified files scoped to the Done/ dir
        rel = "knowledge/decisions/Done"
        dirty = porcelain(repo, rel)
        if dirty:
            fails.append(
                f"[1/project] {repo.name}: {len(dirty)} uncommitted file(s) in "
                f"{rel}/ — commit completed plan files."
            )

    # --- Step 2: bellows — verdicts committed AND pushed -----------------------
    v_dirty = porcelain(BELLOWS, "verdicts/resolved")
    if v_dirty:
        fails.append(
            f"[2/bellows] {len(v_dirty)} uncommitted file(s) under "
            f"verdicts/resolved/ — commit consumed verdicts."
        )
    b_ahead = unpushed_count(BELLOWS)
    if b_ahead:
        fails.append(f"[2/bellows] {b_ahead} commit(s) not pushed — push bellows.")

    # --- Step 3: governance root — baton + gitlink + 3b lessons sweep ----------
    # baton must be committed (not sitting modified/untracked)
    baton_dirty = porcelain(ROOT, "shop_next_session.md")
    if baton_dirty:
        fails.append("[3/root] shop_next_session.md is uncommitted — commit the refreshed baton.")
    # bellows gitlink must be committed (not a dangling submodule bump)
    gitlink_dirty = porcelain(ROOT, "bellows")
    if gitlink_dirty:
        fails.append("[3/root] bellows gitlink is uncommitted — `git add bellows` and commit the bump.")
    r_ahead = unpushed_count(ROOT)
    if r_ahead:
        fails.append(f"[3/root] {r_ahead} commit(s) not pushed — push governance root.")
    # 3b: the MOST-SKIPPED step. Force an explicit affirmation in today's baton.
    try:
        baton_text = BATON.read_text(errors="replace") if BATON.exists() else ""
    except Exception:
        baton_text = ""
    swept_ok = any(
        line.strip().lower().startswith("lessons-swept:") and today in line
        for line in baton_text.splitlines()
    )
    if not swept_ok:
        fails.append(
            f"[3b/lessons] No `Lessons-swept: {today}` line in the baton. Do the 3b "
            f"transferable-lessons sweep AS ITS OWN ACT (distinct from the arc note), "
            f"then add a `Lessons-swept: {today} — <delta, or 'none'>` line to "
            f"shop_next_session.md and commit."
        )

    # --- Step 4: memory repo — committed AND pushed (if touched) ---------------
    m_dirty = porcelain(MEMORY)
    if m_dirty:
        fails.append(
            f"[4/memory] {len(m_dirty)} uncommitted change(s) in the memory repo — "
            f"commit memories + MEMORY.md."
        )
    m_ahead = unpushed_count(MEMORY)
    if m_ahead:
        fails.append(f"[4/memory] {m_ahead} commit(s) not pushed — push the memory repo.")

    return fails


def main() -> int:
    try:
        fails = check()
    except Exception as exc:  # FAIL-OPEN — a broken checker must never trap
        print(f"wrap_check: internal error, failing open (allowing): {exc}")
        return 0
    if not fails:
        print("wrap_check: OK — all four repos wrapped.")
        return 0
    print("SESSION WRAP INCOMPLETE — the following steps are not verifiably done:\n")
    for f in fails:
        print(f"  ✗ {f}")
    print("\nComplete these, then this lock clears automatically.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
