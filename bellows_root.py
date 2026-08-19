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
