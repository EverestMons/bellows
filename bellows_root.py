"""Worktree-safe resolution of the canonical bellows root.

Under worktree execution, __file__ resolves inside .bellows-worktrees/<wt>/,
so the legacy `Path(__file__).parent` yields the worktree dir, not canonical
bellows. Two-sentinel walk: first for config.json (gitignored, canonical-only),
then for bellows.py (tracked, present in worktrees and fresh clones). Raises
ValueError if neither sentinel is found in any ancestor — a loud failure beats
a stray lifecycle.db in the wrong repo.
Standalone (pathlib only) to avoid the bellows<->runner import cycle.
"""
from pathlib import Path


def resolve_bellows_root(_start=None) -> Path:
    """Return the canonical bellows root via two-sentinel walk.

    Walk 1: ancestor containing config.json (canonical operational config).
    Walk 2: ancestor containing bellows.py (tracked sentinel for CI/fresh-clone
    where the gitignored config.json is absent).
    Raises ValueError if neither sentinel is found.

    `_start` is for testing only; production calls resolve from this file.
    """
    start = (_start or Path(__file__).resolve().parent).resolve()
    current = start
    while True:
        if (current / "config.json").exists():
            return current
        parent = current.parent
        if parent == current:
            break
        current = parent
    current = start
    while True:
        if (current / "bellows.py").exists():
            return current
        parent = current.parent
        if parent == current:
            break
        current = parent
    raise ValueError(
        f"resolve_bellows_root: no bellows sentinel (config.json or bellows.py) "
        f"found in any ancestor of {start}"
    )


GOVERNANCE_MARKER = "COMPANY.md"


def resolve_governance_root(_start=None, _env=None):
    """Return the governance root — the directory holding COMPANY.md,
    PLANNER_TEMPLATE.md, RULE_20_SELF_CHECK_BLOCK.md, LESSONS.md.

    Two layouts exist (2026-09-01) and a third may come:
      shop : <root>/{COMPANY.md, bellows/, lessons-forge/, ...}     — bellows UNDER the root
      mini : ~/Developer/{eluvian-governance/COMPANY.md, bellows/}  — bellows BESIDE the root

    Resolution order, first hit wins, every hit verified by the marker:
      1. $ELUVIAN_WRAP_ROOT (an override, never a requirement — the daemon's
         environment does not carry it; measured 2026-09-01 on the mini)
      2. an ancestor of the bellows root that holds the marker (shop shape)
      3. siblings of the bellows root: <parent>/eluvian-governance, <parent>
         (mini shape, and any layout where governance is a sibling checkout)
      4. ~/Developer/eluvian-governance, ~/Developer/GitHub (the two known
         homes, tried LAST and only by marker — never assumed)
    Raises ValueError when no candidate holds the marker: a loud failure beats
    a QA agent told to read a file that does not exist.

    `_start` / `_env` are for testing only.
    """
    import os
    env = _env if _env is not None else os.environ.get("ELUVIAN_WRAP_ROOT")
    if env:
        p = Path(env).expanduser()
        if (p / GOVERNANCE_MARKER).is_file():
            return p.resolve()
    try:
        broot = resolve_bellows_root(_start)
    except ValueError:
        broot = (_start or Path(__file__).resolve().parent).resolve()
    current = broot
    while True:
        if (current / GOVERNANCE_MARKER).is_file():
            return current
        parent = current.parent
        if parent == current:
            break
        current = parent
    for cand in (broot.parent / "eluvian-governance", broot.parent,
                 Path.home() / "Developer" / "eluvian-governance",
                 Path.home() / "Developer" / "GitHub"):
        if (cand / GOVERNANCE_MARKER).is_file():
            return cand.resolve()
    raise ValueError(
        f"resolve_governance_root: no {GOVERNANCE_MARKER} found via $ELUVIAN_WRAP_ROOT, "
        f"the ancestors of {broot}, its siblings, or the two known homes"
    )


def resolve_projects_parent(_start=None):
    """The directory that holds the project checkouts (bellows, forge, tuyere, ...):
    the bellows root's parent on every layout — <root> on the shop (projects live
    under the governance root), ~/Developer on the mini."""
    return resolve_bellows_root(_start).parent
