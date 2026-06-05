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
    _is_lifecycle_artifact,
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


def test_teardown_raises_on_git_log_exception(git_repo):
    """A git-log exception during commit enumeration must raise WorktreeTeardownError
    and leave the worktree alive (commits not lost, preserved for recovery)."""
    wt_path = _create_worktree(git_repo, "log-exc-test")
    assert os.path.isdir(wt_path)

    real_run = subprocess.run

    def fake_run(*args, **kwargs):
        cmd = args[0] if args else kwargs.get("args", [])
        if isinstance(cmd, list) and "log" in cmd and "--not" in cmd:
            raise OSError("simulated git-log OS error")
        return real_run(*args, **kwargs)

    with patch("bellows.subprocess.run", side_effect=fake_run):
        with pytest.raises(WorktreeTeardownError, match="git log exception"):
            _teardown_worktree(git_repo, wt_path, "log-exc-test")

    assert os.path.isdir(wt_path), "Worktree must still exist after git-log exception"

    # Clean up
    subprocess.run(
        ["git", "worktree", "remove", "--force", wt_path], cwd=git_repo,
        capture_output=True, text=True,
    )


def test_teardown_raises_on_git_log_nonzero(git_repo):
    """A git-log non-zero returncode must raise WorktreeTeardownError
    and leave the worktree alive."""
    wt_path = _create_worktree(git_repo, "log-rc-test")
    assert os.path.isdir(wt_path)

    real_run = subprocess.run

    def fake_run(*args, **kwargs):
        cmd = args[0] if args else kwargs.get("args", [])
        if isinstance(cmd, list) and "log" in cmd and "--not" in cmd:
            result = MagicMock()
            result.returncode = 1
            result.stdout = ""
            result.stderr = "fatal: bad revision"
            return result
        return real_run(*args, **kwargs)

    with patch("bellows.subprocess.run", side_effect=fake_run):
        with pytest.raises(WorktreeTeardownError, match="git log rc=1"):
            _teardown_worktree(git_repo, wt_path, "log-rc-test")

    assert os.path.isdir(wt_path), "Worktree must still exist after git-log non-zero rc"

    # Clean up
    subprocess.run(
        ["git", "worktree", "remove", "--force", wt_path], cwd=git_repo,
        capture_output=True, text=True,
    )


def test_teardown_proceeds_on_empty_commit_list(git_repo):
    """A worktree with no new commits (HEAD == main) must NOT raise —
    teardown proceeds normally and removes the worktree."""
    wt_path = _create_worktree(git_repo, "empty-commits-test")
    assert os.path.isdir(wt_path)

    # No commits made in the worktree — HEAD is identical to main
    _teardown_worktree(git_repo, wt_path, "empty-commits-test")

    assert not os.path.isdir(wt_path), \
        "Worktree should be removed when no commits were made (legitimate empty case)"


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


# --- Item (a): stranded-worktree cleanup tests ---

def test_create_worktree_cleans_stranded_directory(git_repo, caplog):
    """A bare directory pre-existing at wt_path is cleaned and worktree creation succeeds."""
    slug = "stranded-dir-test"
    wt_path = os.path.join(git_repo, ".bellows-worktrees", slug)
    os.makedirs(wt_path, exist_ok=True)
    # Plant a marker file to prove the directory gets removed
    with open(os.path.join(wt_path, "stale.txt"), "w") as f:
        f.write("stale")

    with patch("bellows._log") as mock_log:
        result_path = _create_worktree(git_repo, slug)

    try:
        assert os.path.isdir(result_path), "Worktree should exist after creation"
        assert os.path.isfile(os.path.join(result_path, "README.md")), \
            "Tracked file should be present in new worktree"
        assert not os.path.isfile(os.path.join(result_path, "stale.txt")), \
            "Stale marker should be gone after cleanup"
        # Verify WARN was logged
        warn_calls = [c for c in mock_log.call_args_list
                      if c[0][0] == "WARN" and "stranded worktree found" in c[0][1]]
        assert len(warn_calls) >= 1, "Expected WARN about stranded worktree"
    finally:
        subprocess.run(
            ["git", "worktree", "remove", "--force", result_path], cwd=git_repo,
            capture_output=True, text=True,
        )


def test_create_worktree_cleans_stranded_registered_worktree(git_repo):
    """A registered worktree pre-existing at wt_path is cleaned via worktree remove --force."""
    slug = "stranded-registered-test"
    # Create a real worktree first, then try to create again at the same path
    wt_path = _create_worktree(git_repo, slug)
    assert os.path.isdir(wt_path)

    # Now call _create_worktree again — should clean up and succeed
    with patch("bellows._log") as mock_log:
        result_path = _create_worktree(git_repo, slug)

    try:
        assert os.path.isdir(result_path), "Worktree should exist after re-creation"
        assert os.path.isfile(os.path.join(result_path, "README.md")), \
            "Tracked file should be present in re-created worktree"
        # Verify WARN was logged
        warn_calls = [c for c in mock_log.call_args_list
                      if c[0][0] == "WARN" and "stranded worktree found" in c[0][1]]
        assert len(warn_calls) >= 1, "Expected WARN about stranded worktree"
    finally:
        subprocess.run(
            ["git", "worktree", "remove", "--force", result_path], cwd=git_repo,
            capture_output=True, text=True,
        )


# --- Item (f): rstrip + leading-space tolerance tests ---

def test_pre_check_recognizes_space_prefixed_lifecycle_line():
    """A space-prefixed lifecycle artifact on the first porcelain line must be recognized."""
    # " D" status — deleted lifecycle artifact
    assert _is_lifecycle_artifact(" D knowledge/decisions/verdict-pending-foo.md") is True
    # " M" status — modified lifecycle artifact
    assert _is_lifecycle_artifact(" M verdicts/pending/some-verdict.md") is True
    # Negative control: space-prefixed REAL dirty file must NOT be treated as lifecycle
    assert _is_lifecycle_artifact(" M README.md") is False
    assert _is_lifecycle_artifact(" D src/app.py") is False


# --- Item (g): .bellows-worktrees/ lifecycle-ignore tests ---

def test_pre_check_ignores_bellows_worktrees_dir():
    """Porcelain entries under .bellows-worktrees/ must be treated as lifecycle artifacts."""
    # Bare directory entry
    assert _is_lifecycle_artifact("?? .bellows-worktrees/") is True
    # Child path
    assert _is_lifecycle_artifact("?? .bellows-worktrees/some-slug/file.py") is True
    # Negative control: real untracked file outside .bellows-worktrees/
    assert _is_lifecycle_artifact("?? src/untracked.py") is False
    assert _is_lifecycle_artifact("?? bellows-worktrees-imposter/foo.py") is False


# --- Gap 2a: preserve un-landed commits on stranded-cleanup ---

def test_stranded_cleanup_preserves_unlanded_commits(git_repo):
    """Un-landed commits on a stranded worktree's HEAD are preserved on a branch before destroy."""
    slug = "preserve-test"

    # Create a worktree and make an un-landed commit on its detached HEAD
    wt_path = _create_worktree(git_repo, slug)
    with open(os.path.join(wt_path, "new_work.txt"), "w") as f:
        f.write("un-landed work\n")
    subprocess.run(["git", "add", "."], cwd=wt_path, capture_output=True, text=True)
    subprocess.run(
        ["git", "commit", "-m", "un-landed commit"], cwd=wt_path,
        capture_output=True, text=True, check=True,
    )
    wt_head = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=wt_path,
        capture_output=True, text=True,
    ).stdout.strip()

    main_head = subprocess.run(
        ["git", "rev-parse", "main"], cwd=git_repo,
        capture_output=True, text=True,
    ).stdout.strip()
    assert wt_head != main_head, "Precondition: worktree HEAD must differ from main"

    # Now call _create_worktree again — triggers stranded-cleanup with preserve
    result_path = _create_worktree(git_repo, slug)
    try:
        # (a) A bellows-preserved/<slug>-* branch exists
        br_list = subprocess.run(
            ["git", "branch", "--list", f"bellows-preserved/{slug}-*"], cwd=git_repo,
            capture_output=True, text=True,
        )
        branches = [b.strip() for b in br_list.stdout.strip().splitlines() if b.strip()]
        assert len(branches) >= 1, f"Expected a bellows-preserved branch, got: {br_list.stdout}"

        # (b) The branch points at the captured wt_head
        br_sha = subprocess.run(
            ["git", "rev-parse", branches[0]], cwd=git_repo,
            capture_output=True, text=True,
        ).stdout.strip()
        assert br_sha == wt_head, f"Preserved branch should point at {wt_head}, got {br_sha}"

        # (c) wt_head is still reachable
        cat_result = subprocess.run(
            ["git", "cat-file", "-e", wt_head], cwd=git_repo,
            capture_output=True, text=True,
        )
        assert cat_result.returncode == 0, f"wt_head {wt_head} should be reachable"

        # (d) Worktree was removed and recreated (fresh HEAD == main HEAD)
        assert os.path.isdir(result_path), "Worktree should exist after re-creation"
        new_head = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=result_path,
            capture_output=True, text=True,
        ).stdout.strip()
        assert new_head == main_head, f"Recreated worktree HEAD should be main HEAD {main_head}, got {new_head}"
    finally:
        subprocess.run(
            ["git", "worktree", "remove", "--force", result_path], cwd=git_repo,
            capture_output=True, text=True,
        )
        # Clean up preservation branches
        for b in branches:
            subprocess.run(
                ["git", "branch", "-D", b], cwd=git_repo,
                capture_output=True, text=True,
            )


def test_stranded_cleanup_no_preserve_when_already_landed(git_repo):
    """When stranded worktree HEAD is already on main, no bellows-preserved branch is created."""
    slug = "landed-test"

    # Create a worktree — its HEAD == main HEAD (already landed, no new commits)
    wt_path = _create_worktree(git_repo, slug)
    assert os.path.isdir(wt_path)

    # Call _create_worktree again — triggers stranded-cleanup
    result_path = _create_worktree(git_repo, slug)
    try:
        # No bellows-preserved/* branch should exist
        br_list = subprocess.run(
            ["git", "branch", "--list", "bellows-preserved/*"], cwd=git_repo,
            capture_output=True, text=True,
        )
        assert br_list.stdout.strip() == "", \
            f"No preservation branch expected for already-landed HEAD, got: {br_list.stdout}"

        # Worktree recreated normally
        assert os.path.isdir(result_path), "Worktree should exist after re-creation"
    finally:
        subprocess.run(
            ["git", "worktree", "remove", "--force", result_path], cwd=git_repo,
            capture_output=True, text=True,
        )


def test_stranded_cleanup_failsafe_preserves_when_main_unresolvable(git_repo):
    """When main ref is unresolvable, fail-safe bias preserves the worktree commits."""
    slug = "failsafe-test"

    # Create a worktree and make a commit on its detached HEAD
    wt_path = _create_worktree(git_repo, slug)
    with open(os.path.join(wt_path, "failsafe_work.txt"), "w") as f:
        f.write("failsafe work\n")
    subprocess.run(["git", "add", "."], cwd=wt_path, capture_output=True, text=True)
    subprocess.run(
        ["git", "commit", "-m", "failsafe commit"], cwd=wt_path,
        capture_output=True, text=True, check=True,
    )
    wt_head = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=wt_path,
        capture_output=True, text=True,
    ).stdout.strip()

    # Delete the 'main' branch ref so merge-base --is-ancestor ... main will fail
    # First detach the main repo HEAD so we can delete the branch
    subprocess.run(
        ["git", "checkout", "--detach"], cwd=git_repo,
        capture_output=True, text=True,
    )
    subprocess.run(
        ["git", "branch", "-D", "main"], cwd=git_repo,
        capture_output=True, text=True,
    )

    # Now call _create_worktree — should fail-safe and preserve
    result_path = _create_worktree(git_repo, slug)
    try:
        # A bellows-preserved branch should exist (fail-safe bias)
        br_list = subprocess.run(
            ["git", "branch", "--list", f"bellows-preserved/{slug}-*"], cwd=git_repo,
            capture_output=True, text=True,
        )
        branches = [b.strip() for b in br_list.stdout.strip().splitlines() if b.strip()]
        assert len(branches) >= 1, \
            f"Fail-safe should create preservation branch when main unresolvable, got: {br_list.stdout}"

        # The branch points at the captured wt_head
        br_sha = subprocess.run(
            ["git", "rev-parse", branches[0]], cwd=git_repo,
            capture_output=True, text=True,
        ).stdout.strip()
        assert br_sha == wt_head, f"Preserved branch should point at {wt_head}, got {br_sha}"

        # _create_worktree returned a valid path without raising
        assert os.path.isdir(result_path), "Worktree should exist after re-creation"
    finally:
        subprocess.run(
            ["git", "worktree", "remove", "--force", result_path], cwd=git_repo,
            capture_output=True, text=True,
        )
        # Clean up preservation branches
        for b in branches:
            subprocess.run(
                ["git", "branch", "-D", b], cwd=git_repo,
                capture_output=True, text=True,
            )
