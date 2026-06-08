"""Worktree-safe resolution of the canonical bellows root.

Under worktree execution, __file__ resolves inside .bellows-worktrees/<wt>/,
so the legacy `Path(__file__).parent` yields the worktree dir, not canonical
bellows. This walks up to the nearest ancestor containing config.json (the
gitignored, canonical-only operational config), which is absent from worktrees.
Standalone (pathlib only) to avoid the bellows<->runner import cycle.
"""
from pathlib import Path


def resolve_bellows_root(_start=None) -> Path:
    """Return the canonical bellows root (ancestor containing config.json).

    Falls back to the start dir (legacy `Path(__file__).parent` behavior) when
    no config.json is found in any ancestor -- preserves current behavior in
    CI / fresh-clone environments without a config.json.

    `_start` is for testing only; production calls resolve from this file.
    """
    start = (_start or Path(__file__).resolve().parent).resolve()
    current = start
    while True:
        if (current / "config.json").exists():
            return current
        parent = current.parent
        if parent == current:  # filesystem root reached
            return start
        current = parent
