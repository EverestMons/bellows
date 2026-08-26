"""Tests for Strategy 4 (cross-machine re-root) in _resolve_deposit_path."""

import os
import pytest

from gates import _resolve_deposit_path


def _touch(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write("")


class TestCrossMachineReRoot:
    """Strategy 4: re-anchor an absolute path from another machine's layout."""

    def test_560_shape_resolves(self, tmp_path):
        """THE 560 SHAPE — file exists at <tmp>/GitHub/bellows/hooks/eluvian/wrap_check.py,
        declared as /Users/other/Developer/bellows/hooks/eluvian/wrap_check.py
        with project_path=<tmp>/GitHub/bellows → resolves to the local file."""
        project = tmp_path / "GitHub" / "bellows"
        target = project / "hooks" / "eluvian" / "wrap_check.py"
        _touch(str(target))
        declared = "/Users/other/Developer/bellows/hooks/eluvian/wrap_check.py"
        result = _resolve_deposit_path(declared, str(project))
        assert result is not None
        assert os.path.isfile(result)
        assert os.path.samefile(result, str(target))

    def test_560_shape_absent_returns_none(self, tmp_path):
        """Same declared path with the file ABSENT → None (fail-closed)."""
        project = tmp_path / "GitHub" / "bellows"
        os.makedirs(str(project), exist_ok=True)
        declared = "/Users/other/Developer/bellows/hooks/eluvian/wrap_check.py"
        result = _resolve_deposit_path(declared, str(project))
        assert result is None

    def test_foreign_absolute_no_project_basename(self, tmp_path):
        """A foreign absolute path NOT containing the project basename → None."""
        project = tmp_path / "GitHub" / "bellows"
        os.makedirs(str(project), exist_ok=True)
        declared = "/Users/other/Developer/unrelated/hooks/wrap_check.py"
        result = _resolve_deposit_path(declared, str(project))
        assert result is None

    def test_worktree_first(self, tmp_path):
        """Worktree-first: the file in BOTH wt and project → the wt copy returned."""
        project = tmp_path / "project" / "bellows"
        wt = tmp_path / "worktree" / "bellows"
        target_proj = project / "somefile.py"
        target_wt = wt / "somefile.py"
        _touch(str(target_proj))
        _touch(str(target_wt))
        declared = "/Users/other/Developer/bellows/somefile.py"
        result = _resolve_deposit_path(declared, str(project), wt_path=str(wt))
        assert result is not None
        assert os.path.samefile(result, str(target_wt))

    def test_nested_marker_uses_last(self, tmp_path):
        """Nested-marker case /x/bellows/backup/bellows/f.py with f.py at
        the project root → resolves via the LAST marker."""
        project = tmp_path / "GitHub" / "bellows"
        target = project / "f.py"
        _touch(str(target))
        declared = "/x/bellows/backup/bellows/f.py"
        result = _resolve_deposit_path(declared, str(project))
        assert result is not None
        assert os.path.samefile(result, str(target))

    def test_relative_path_unchanged(self, tmp_path):
        """A RELATIVE path still resolves exactly as before
        (Strategy-4 untouched — regression guard)."""
        project = tmp_path / "GitHub" / "bellows"
        target = project / "config.json"
        _touch(str(target))
        result = _resolve_deposit_path("config.json", str(project))
        assert result is not None
        assert os.path.samefile(result, str(target))
