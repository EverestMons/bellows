"""Integration tests for the per-plan git worktree mechanism.

These tests exercise REAL git operations against temporary repositories.
No mocking of git itself — only time.sleep and subprocess.run are mocked
where explicitly noted (test 7: retry behavior).
"""

import os
import shutil
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from unittest.mock import MagicMock, patch

import pytest

import bellows
from bellows import (
    WorktreeCreationError,
    WorktreeTeardownError,
    _create_worktree,
    _teardown_worktree,
)


@pytest.fixture
def git_repo():
    """Create a temporary git repository with an initial commit on 'main'."""
    tmp = tempfile.mkdtemp()
    try:
        subprocess.run(
            ["git", "init", "-b", "main"], cwd=tmp,
            capture_output=True, text=True, check=True,
        )
        subprocess.run(
            ["git", "config", "user.email", "test@test.com"], cwd=tmp,
            capture_output=True, text=True,
        )
        subprocess.run(
            ["git", "config", "user.name", "Test"], cwd=tmp,
            capture_output=True, text=True,
        )
        readme_path = os.path.join(tmp, "README.md")
        with open(readme_path, "w") as f:
            f.write("# Test Repo\n")
        subprocess.run(["git", "add", "."], cwd=tmp, capture_output=True, text=True)
        subprocess.run(
            ["git", "commit", "-m", "initial commit"], cwd=tmp,
            capture_output=True, text=True, check=True,
        )
        yield tmp
    finally:
        # Clean up any worktrees before removing temp dir
        subprocess.run(
            ["git", "worktree", "prune"], cwd=tmp,
            capture_output=True, text=True,
        )
        wt_dir = os.path.join(tmp, ".bellows-worktrees")
        if os.path.exists(wt_dir):
            result = subprocess.run(
                ["git", "worktree", "list", "--porcelain"], cwd=tmp,
                capture_output=True, text=True,
            )
            for line in result.stdout.splitlines():
                if line.startswith("worktree ") and ".bellows-worktrees" in line:
                    wt_path = line[len("worktree "):]
                    subprocess.run(
                        ["git", "worktree", "remove", "--force", wt_path], cwd=tmp,
                        capture_output=True, text=True,
                    )
            shutil.rmtree(wt_dir, ignore_errors=True)
        shutil.rmtree(tmp, ignore_errors=True)


def test_create_worktree_returns_valid_path_with_tracked_files(git_repo):
    """Created worktree must exist and contain all tracked files."""
    for name in ["fileA.txt", "fileB.txt"]:
        with open(os.path.join(git_repo, name), "w") as f:
            f.write(f"content of {name}\n")
    subprocess.run(["git", "add", "."], cwd=git_repo, capture_output=True, text=True)
    subprocess.run(
        ["git", "commit", "-m", "add files"], cwd=git_repo,
        capture_output=True, text=True, check=True,
    )

    wt_path = _create_worktree(git_repo, "test-slug")
    try:
        assert os.path.isdir(wt_path), f"Worktree path should exist: {wt_path}"
        for name in ["README.md", "fileA.txt", "fileB.txt"]:
            assert os.path.isfile(os.path.join(wt_path, name)), \
                f"Tracked file {name} missing from worktree"
    finally:
        subprocess.run(
            ["git", "worktree", "remove", "--force", wt_path], cwd=git_repo,
            capture_output=True, text=True,
        )


def test_worktree_isolation_git_diff(git_repo):
    """Modifications in main checkout must not appear in worktree's git diff."""
    wt_path = _create_worktree(git_repo, "isolation-test")
    try:
        # Dirty the file in the MAIN checkout
        with open(os.path.join(git_repo, "README.md"), "a") as f:
            f.write("dirty line in main\n")

        # Check worktree's git diff — should be clean
        result = subprocess.run(
            ["git", "--no-pager", "diff", "--stat"], cwd=wt_path,
            capture_output=True, text=True,
        )
        assert "README.md" not in result.stdout, \
            f"Main checkout's dirty file should NOT appear in worktree diff: {result.stdout}"
    finally:
        subprocess.run(
            ["git", "worktree", "remove", "--force", wt_path], cwd=git_repo,
            capture_output=True, text=True,
        )
        subprocess.run(
            ["git", "checkout", "--", "."], cwd=git_repo,
            capture_output=True, text=True,
        )


def test_teardown_removes_worktree_directory(git_repo):
    """After teardown, the worktree directory must not exist and must not appear in git worktree list."""
    wt_path = _create_worktree(git_repo, "teardown-test")
    assert os.path.isdir(wt_path)

    _teardown_worktree(git_repo, wt_path, "teardown-test")

    assert not os.path.isdir(wt_path), f"Worktree directory should be removed: {wt_path}"
    result = subprocess.run(
        ["git", "worktree", "list"], cwd=git_repo,
        capture_output=True, text=True,
    )
    assert wt_path not in result.stdout, \
        f"Removed worktree should not appear in 'git worktree list': {result.stdout}"


def test_teardown_cherry_picks_commits(git_repo):
    """Commits made in the worktree must appear on main after teardown."""
    wt_path = _create_worktree(git_repo, "cherry-pick-test")
    try:
        with open(os.path.join(wt_path, "README.md"), "a") as f:
            f.write("worktree change\n")
        subprocess.run(["git", "add", "."], cwd=wt_path, capture_output=True, text=True)
        subprocess.run(
            ["git", "commit", "-m", "commit from worktree"], cwd=wt_path,
            capture_output=True, text=True, check=True,
        )
    except Exception:
        subprocess.run(
            ["git", "worktree", "remove", "--force", wt_path], cwd=git_repo,
            capture_output=True, text=True,
        )
        raise

    _teardown_worktree(git_repo, wt_path, "cherry-pick-test")

    result = subprocess.run(
        ["git", "--no-pager", "log", "--oneline", "-5"], cwd=git_repo,
        capture_output=True, text=True,
    )
    assert "commit from worktree" in result.stdout, \
        f"Cherry-picked commit not found on main: {result.stdout}"


def test_teardown_copies_uncommitted_files(git_repo):
    """Uncommitted new files in the worktree must be copied back to main on teardown."""
    wt_path = _create_worktree(git_repo, "dirty-copy-test")
    try:
        new_file = os.path.join(wt_path, "new_file.txt")
        with open(new_file, "w") as f:
            f.write("uncommitted content\n")
    except Exception:
        subprocess.run(
            ["git", "worktree", "remove", "--force", wt_path], cwd=git_repo,
            capture_output=True, text=True,
        )
        raise

    _teardown_worktree(git_repo, wt_path, "dirty-copy-test")

    main_copy = os.path.join(git_repo, "new_file.txt")
    assert os.path.isfile(main_copy), f"Uncommitted file should be copied to main: {main_copy}"
    with open(main_copy) as f:
        assert f.read() == "uncommitted content\n"


def test_teardown_aborts_on_cherry_pick_conflict(git_repo):
    """Cherry-pick conflict must raise WorktreeTeardownError and leave worktree alive."""
    wt_path = _create_worktree(git_repo, "conflict-test")
    try:
        # In worktree: modify README.md and commit
        with open(os.path.join(wt_path, "README.md"), "w") as f:
            f.write("version 2 from worktree\n")
        subprocess.run(["git", "add", "."], cwd=wt_path, capture_output=True, text=True)
        subprocess.run(
            ["git", "commit", "-m", "worktree version 2"], cwd=wt_path,
            capture_output=True, text=True, check=True,
        )

        # In main: modify README.md differently and commit (creates conflict)
        with open(os.path.join(git_repo, "README.md"), "w") as f:
            f.write("version 3 from main\n")
        subprocess.run(["git", "add", "."], cwd=git_repo, capture_output=True, text=True)
        subprocess.run(
            ["git", "commit", "-m", "main version 3"], cwd=git_repo,
            capture_output=True, text=True, check=True,
        )
    except Exception:
        subprocess.run(
            ["git", "worktree", "remove", "--force", wt_path], cwd=git_repo,
            capture_output=True, text=True,
        )
        raise

    with pytest.raises(WorktreeTeardownError):
        _teardown_worktree(git_repo, wt_path, "conflict-test")

    # Main checkout must be clean (cherry-pick was aborted)
    cherry_pick_head = os.path.join(git_repo, ".git", "CHERRY_PICK_HEAD")
    assert not os.path.exists(cherry_pick_head), \
        "CHERRY_PICK_HEAD should not exist after abort"
    result = subprocess.run(
        ["git", "status", "--porcelain"], cwd=git_repo,
        capture_output=True, text=True,
    )
    assert result.stdout.strip() == "", \
        f"Main checkout should be clean after abort: {result.stdout}"

    # Worktree must still exist (left for manual resolution)
    assert os.path.isdir(wt_path), "Worktree should still exist after conflict"

    # Clean up
    subprocess.run(
        ["git", "worktree", "remove", "--force", wt_path], cwd=git_repo,
        capture_output=True, text=True,
    )


def test_create_worktree_retries_once_on_failure(git_repo):
    """_create_worktree retries once on subprocess failure with a 2s sleep between attempts."""
    call_count = [0]

    def fake_subprocess_run(*args, **kwargs):
        call_count[0] += 1
        result = MagicMock()
        if call_count[0] == 1:
            result.returncode = 1
            result.stderr = "fake error"
        else:
            result.returncode = 0
            result.stderr = ""
        return result

    with patch("bellows.subprocess.run", side_effect=fake_subprocess_run), \
         patch("bellows.time.sleep") as mock_sleep:
        wt_path = _create_worktree(git_repo, "retry-test")

    assert call_count[0] == 2, f"Expected 2 subprocess calls, got {call_count[0]}"
    mock_sleep.assert_called_once_with(2)
    expected_path = os.path.join(git_repo, ".bellows-worktrees", "retry-test")
    assert wt_path == expected_path, f"Expected {expected_path}, got {wt_path}"
