"""Tests for bellows_root.resolve_bellows_root()."""
from bellows_root import resolve_bellows_root


def test_resolves_to_dir_with_config(tmp_path):
    """_start dir itself contains config.json — returns that dir."""
    (tmp_path / "config.json").write_text("{}")
    assert resolve_bellows_root(_start=tmp_path) == tmp_path


def test_walks_up_to_config(tmp_path):
    """Negative worktree-resolution test.

    Builds a simulated worktree layout:
        <tmp>/canonical/config.json
        <tmp>/canonical/.bellows-worktrees/wt1/

    The helper should walk up from wt1 and return <tmp>/canonical (the dir
    containing config.json).  The legacy `Path(__file__).parent` approach would
    return the wt1 dir itself — this test FAILS under that legacy behavior and
    PASSES only under the walk-up helper.
    """
    canonical = tmp_path / "canonical"
    canonical.mkdir()
    (canonical / "config.json").write_text("{}")
    wt_dir = canonical / ".bellows-worktrees" / "wt1"
    wt_dir.mkdir(parents=True)

    result = resolve_bellows_root(_start=wt_dir)
    assert result == canonical, f"Expected walk-up to canonical {canonical}, got {result}"


def test_falls_back_when_no_config(tmp_path):
    """No config.json anywhere in the tmp tree — falls back to _start dir."""
    deep = tmp_path / "a" / "b" / "c"
    deep.mkdir(parents=True)
    result = resolve_bellows_root(_start=deep)
    assert result == deep
