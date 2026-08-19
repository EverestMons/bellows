"""Tests for bellows_root.resolve_bellows_root()."""
import pytest

from bellows_root import resolve_bellows_root


def test_resolves_to_dir_with_config(tmp_path):
    """_start dir itself contains config.json — returns that dir."""
    (tmp_path / "config.json").write_text("{}")
    assert resolve_bellows_root(_start=tmp_path) == tmp_path


def test_walks_up_to_config(tmp_path):
    """config.json walk must win even when bellows.py exists in a worktree.

    Builds a simulated worktree layout:
        <tmp>/canonical/config.json
        <tmp>/canonical/bellows.py          (tracked sentinel)
        <tmp>/canonical/.bellows-worktrees/wt1/bellows.py   (also tracked)

    The helper should walk up from wt1 and return <tmp>/canonical (the dir
    containing config.json), NOT wt1 (which contains bellows.py).  A wrong
    combined-check implementation would stop at wt1.
    """
    canonical = tmp_path / "canonical"
    canonical.mkdir()
    (canonical / "config.json").write_text("{}")
    (canonical / "bellows.py").write_text("# sentinel")
    wt_dir = canonical / ".bellows-worktrees" / "wt1"
    wt_dir.mkdir(parents=True)
    (wt_dir / "bellows.py").write_text("# sentinel")

    result = resolve_bellows_root(_start=wt_dir)
    assert result == canonical, f"Expected walk-up to canonical {canonical}, got {result}"


def test_non_bellows_tree_raises(tmp_path):
    """Non-bellows tree (no sentinel anywhere) must raise, not return a path."""
    deep = tmp_path / "a" / "b" / "c"
    deep.mkdir(parents=True)
    with pytest.raises(ValueError, match="no bellows sentinel"):
        resolve_bellows_root(_start=deep)


def test_fresh_clone_resolves_via_bellows_py(tmp_path):
    """Fresh clone: bellows.py present, config.json absent — resolves to root."""
    clone_root = tmp_path / "bellows-fresh"
    clone_root.mkdir()
    (clone_root / "bellows.py").write_text("# sentinel")
    sub = clone_root / "subdir"
    sub.mkdir()
    assert resolve_bellows_root(_start=sub) == clone_root
