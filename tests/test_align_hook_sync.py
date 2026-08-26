"""Tests for _repo_sync — real temp git repos, no mocks."""
import subprocess
import sys
from pathlib import Path

import pytest

HOOKS_DIR = Path(__file__).resolve().parent.parent / "hooks" / "eluvian"
sys.path.insert(0, str(HOOKS_DIR))

from eluvian_align_hook import _repo_sync  # noqa: E402


def _git(cwd, *args):
    subprocess.run(
        ["git", "-C", str(cwd)] + list(args),
        capture_output=True, text=True, check=True,
    )


def _commit(cwd, msg="c"):
    (cwd / "f.txt").write_text(msg)
    _git(cwd, "add", "f.txt")
    _git(cwd, "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-m", msg)


@pytest.fixture()
def repo_pair(tmp_path):
    """Bare origin + working clone, one initial commit."""
    origin = tmp_path / "origin.git"
    clone = tmp_path / "clone"
    subprocess.run(["git", "init", "--bare", str(origin)],
                    capture_output=True, check=True)
    subprocess.run(["git", "clone", str(origin), str(clone)],
                    capture_output=True, check=True)
    _commit(clone, "init")
    _git(clone, "push")
    return origin, clone


def test_current(repo_pair):
    _, clone = repo_pair
    label, state = _repo_sync("test", clone)
    assert label == "test"
    assert state == "current"


def test_behind(repo_pair, tmp_path):
    origin, clone = repo_pair
    pusher = tmp_path / "pusher"
    subprocess.run(["git", "clone", str(origin), str(pusher)],
                    capture_output=True, check=True)
    _commit(pusher, "remote-only")
    _git(pusher, "push")
    _, state = _repo_sync("x", clone)
    assert state == "BEHIND 1"


def test_ahead(repo_pair):
    _, clone = repo_pair
    _commit(clone, "local-only")
    _, state = _repo_sync("x", clone)
    assert state == "ahead 1 (unpushed)"


def test_diverged(repo_pair, tmp_path):
    origin, clone = repo_pair
    pusher = tmp_path / "pusher"
    subprocess.run(["git", "clone", str(origin), str(pusher)],
                    capture_output=True, check=True)
    _commit(pusher, "remote-side")
    _git(pusher, "push")
    _commit(clone, "local-side")
    _, state = _repo_sync("x", clone)
    assert state == "DIVERGED (ahead 1, behind 1)"


def test_no_upstream(repo_pair):
    _, clone = repo_pair
    _git(clone, "branch", "--unset-upstream")
    _, state = _repo_sync("x", clone)
    assert state == "no upstream"


def test_fetch_failed(repo_pair):
    _, clone = repo_pair
    _git(clone, "remote", "set-url", "origin", "/nonexistent/path")
    _, state = _repo_sync("x", clone)
    assert state.startswith("fetch FAILED")
