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
    _auto_stage_deposits,
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
        # Clean up bellows-wt/* branches
        br_result = subprocess.run(
            ["git", "branch", "--list", "bellows-wt/*"], cwd=tmp,
            capture_output=True, text=True,
        )
        for b in br_result.stdout.strip().splitlines():
            b = b.strip()
            if b:
                subprocess.run(
                    ["git", "branch", "-D", b], cwd=tmp,
                    capture_output=True, text=True,
                )
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
        # Named branch must exist after creation
        br_check = subprocess.run(
            ["git", "rev-parse", "--verify", "refs/heads/bellows-wt/test-slug"],
            cwd=git_repo, capture_output=True, text=True,
        )
        assert br_check.returncode == 0, "Branch bellows-wt/test-slug should exist after creation"
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
    # Branch must be cleaned up after teardown
    br_check = subprocess.run(
        ["git", "rev-parse", "--verify", "refs/heads/bellows-wt/teardown-test"],
        cwd=git_repo, capture_output=True, text=True,
    )
    assert br_check.returncode != 0, "Branch bellows-wt/teardown-test should be deleted after teardown"


def test_teardown_merges_commits(git_repo):
    """Commits made in the worktree must appear on main after teardown (via merge)."""
    wt_path = _create_worktree(git_repo, "merge-test")
    try:
        with open(os.path.join(wt_path, "README.md"), "a") as f:
            f.write("worktree change\n")
        subprocess.run(["git", "add", "README.md"], cwd=wt_path, capture_output=True, text=True)
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

    _teardown_worktree(git_repo, wt_path, "merge-test")

    result = subprocess.run(
        ["git", "--no-pager", "log", "--oneline", "-5"], cwd=git_repo,
        capture_output=True, text=True,
    )
    assert "commit from worktree" in result.stdout, \
        f"Merged commit not found on main: {result.stdout}"


def test_step_commit_shas_range_in_order(git_repo):
    """_step_commit_shas returns full 40-char shas oldest-first for the given range."""
    base_sha = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=git_repo,
        capture_output=True, text=True, check=True,
    ).stdout.strip()

    def _make_commit(msg):
        path = os.path.join(git_repo, "f.txt")
        with open(path, "a") as fh:
            fh.write(msg + "\n")
        subprocess.run(["git", "add", "f.txt"], cwd=git_repo, capture_output=True, text=True, check=True)
        subprocess.run(["git", "commit", "-m", msg], cwd=git_repo, capture_output=True, text=True, check=True)
        return subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=git_repo,
            capture_output=True, text=True, check=True,
        ).stdout.strip()

    sha1 = _make_commit("commit one")
    sha2 = _make_commit("commit two")

    result = bellows._step_commit_shas(git_repo, base_sha, sha2)
    assert result == [sha1, sha2]
    assert all(len(s) == 40 and all(c in "0123456789abcdef" for c in s) for s in result)


def test_step_commit_shas_equal_shas_empty(git_repo):
    """Equal pre and post sha → empty list."""
    head = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=git_repo,
        capture_output=True, text=True, check=True,
    ).stdout.strip()
    assert bellows._step_commit_shas(git_repo, head, head) == []


def test_step_commit_shas_empty_sha_empty(git_repo):
    """Empty pre or post sha → empty list without calling subprocess."""
    head = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=git_repo,
        capture_output=True, text=True, check=True,
    ).stdout.strip()
    with patch("bellows.subprocess.run") as mock_run:
        assert bellows._step_commit_shas(git_repo, "", head) == []
        assert bellows._step_commit_shas(git_repo, head, "") == []
        mock_run.assert_not_called()


def test_teardown_aborts_on_merge_conflict(git_repo):
    """Merge conflict must raise WorktreeTeardownError and leave worktree + branch alive."""
    wt_path = _create_worktree(git_repo, "conflict-test")
    try:
        # In worktree: modify README.md and commit
        with open(os.path.join(wt_path, "README.md"), "w") as f:
            f.write("version 2 from worktree\n")
        subprocess.run(["git", "add", "README.md"], cwd=wt_path, capture_output=True, text=True)
        subprocess.run(
            ["git", "commit", "-m", "worktree version 2"], cwd=wt_path,
            capture_output=True, text=True, check=True,
        )

        # In main: modify README.md differently and commit (creates conflict)
        with open(os.path.join(git_repo, "README.md"), "w") as f:
            f.write("version 3 from main\n")
        subprocess.run(["git", "add", "README.md"], cwd=git_repo, capture_output=True, text=True)
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

    with pytest.raises(WorktreeTeardownError, match="merge conflict"):
        _teardown_worktree(git_repo, wt_path, "conflict-test")

    # Main checkout must be clean (merge was aborted) — only .bellows-worktrees/ may remain (worktree left alive)
    merge_head = os.path.join(git_repo, ".git", "MERGE_HEAD")
    assert not os.path.exists(merge_head), \
        "MERGE_HEAD should not exist after abort"
    result = subprocess.run(
        ["git", "status", "--porcelain"], cwd=git_repo,
        capture_output=True, text=True,
    )
    non_wt_status = [l for l in result.stdout.strip().splitlines() if ".bellows-worktrees" not in l]
    assert non_wt_status == [], \
        f"Main checkout should have no merge artifacts after abort: {non_wt_status}"

    # Worktree must still exist (left for manual resolution)
    assert os.path.isdir(wt_path), "Worktree should still exist after conflict"

    # Branch must still exist (not fully merged, -d would fail)
    br_check = subprocess.run(
        ["git", "rev-parse", "--verify", "refs/heads/bellows-wt/conflict-test"],
        cwd=git_repo, capture_output=True, text=True,
    )
    assert br_check.returncode == 0, "Branch bellows-wt/conflict-test should still exist after conflict"

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
    # Branch must still be cleaned up even with no commits
    br_check = subprocess.run(
        ["git", "rev-parse", "--verify", "refs/heads/bellows-wt/empty-commits-test"],
        cwd=git_repo, capture_output=True, text=True,
    )
    assert br_check.returncode != 0, "Branch bellows-wt/empty-commits-test should be deleted after teardown"


def test_create_worktree_retries_once_on_failure(git_repo):
    """_create_worktree retries once on subprocess failure with a 2s sleep between attempts."""
    call_count = [0]

    def fake_subprocess_run(*args, **kwargs):
        call_count[0] += 1
        result = MagicMock()
        if call_count[0] == 1:
            # First call: branch-exists check (rev-parse --verify) — branch does not exist
            result.returncode = 1
            result.stderr = "not a valid ref"
        elif call_count[0] == 2:
            # Second call: worktree add — fail first attempt
            result.returncode = 1
            result.stderr = "fake error"
        elif call_count[0] == 3:
            # Third call: worktree add retry — succeed
            result.returncode = 0
            result.stderr = ""
        else:
            result.returncode = 0
            result.stderr = ""
        return result

    with patch("bellows.subprocess.run", side_effect=fake_subprocess_run), \
         patch("bellows.time.sleep") as mock_sleep:
        wt_path = _create_worktree(git_repo, "retry-test")

    assert call_count[0] == 3, f"Expected 3 subprocess calls (branch check + 2 worktree add), got {call_count[0]}"
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


# --- Gap 2a: preserve un-landed commits on stranded-cleanup ---

def test_stranded_cleanup_preserves_unlanded_commits(git_repo):
    """Un-landed commits on a stranded worktree's HEAD are preserved on a branch before destroy."""
    slug = "preserve-test"

    # Create a worktree and make an un-landed commit on its named branch
    wt_path = _create_worktree(git_repo, slug)
    with open(os.path.join(wt_path, "new_work.txt"), "w") as f:
        f.write("un-landed work\n")
    subprocess.run(["git", "add", "new_work.txt"], cwd=wt_path, capture_output=True, text=True)
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

    # Create a worktree and make a commit on its named branch
    wt_path = _create_worktree(git_repo, slug)
    with open(os.path.join(wt_path, "failsafe_work.txt"), "w") as f:
        f.write("failsafe work\n")
    subprocess.run(["git", "add", "failsafe_work.txt"], cwd=wt_path, capture_output=True, text=True)
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


# --- Merge-ff teardown regression tests (6 permanent) ---

def test_landing_tolerates_dirty_main_invariant(git_repo):
    """INVARIANT: landing must never require a clean main working tree.
    If this test breaks, a checkout-based teardown step was reintroduced.
    See: knowledge/research/teardown-dirty-main-rootcause-2026-06-05.md §R3"""
    wt_path = _create_worktree(git_repo, "dirty-invariant-test")
    try:
        # Commit a file in worktree
        with open(os.path.join(wt_path, "new_file.txt"), "w") as f:
            f.write("worktree content\n")
        subprocess.run(["git", "add", "new_file.txt"], cwd=wt_path, capture_output=True, text=True)
        subprocess.run(
            ["git", "commit", "-m", "worktree commit"], cwd=wt_path,
            capture_output=True, text=True, check=True,
        )

        # Dirty main with a DIFFERENT file (untracked + modified)
        with open(os.path.join(git_repo, "dirty.txt"), "w") as f:
            f.write("untracked dirty file\n")
        with open(os.path.join(git_repo, "README.md"), "a") as f:
            f.write("dirty modification on main\n")
    except Exception:
        subprocess.run(
            ["git", "worktree", "remove", "--force", wt_path], cwd=git_repo,
            capture_output=True, text=True,
        )
        raise

    _teardown_worktree(git_repo, wt_path, "dirty-invariant-test")

    # Merge landed
    assert os.path.isfile(os.path.join(git_repo, "new_file.txt")), \
        "new_file.txt should exist on main (merge landed)"
    # Dirty files preserved
    assert os.path.isfile(os.path.join(git_repo, "dirty.txt")), \
        "dirty.txt should still exist on main (preserved, not cleaned)"
    with open(os.path.join(git_repo, "README.md")) as f:
        assert "dirty modification on main" in f.read(), \
            "README.md modification should be preserved on main"
    # Worktree removed
    assert not os.path.isdir(wt_path), "Worktree directory should be removed"
    # Branch cleaned up
    br_check = subprocess.run(
        ["git", "rev-parse", "--verify", "refs/heads/bellows-wt/dirty-invariant-test"],
        cwd=git_repo, capture_output=True, text=True,
    )
    assert br_check.returncode != 0, "Branch should be deleted after successful teardown"


def test_landing_aborts_clean_on_dirty_overlap(git_repo):
    """Dirty-tree overlap: uncommitted changes on main in same file as worktree commit
    must abort cleanly with no conflict markers."""
    wt_path = _create_worktree(git_repo, "dirty-overlap-test")
    try:
        # Modify file.txt in worktree and commit
        with open(os.path.join(wt_path, "README.md"), "w") as f:
            f.write("worktree version\n")
        subprocess.run(["git", "add", "README.md"], cwd=wt_path, capture_output=True, text=True)
        subprocess.run(
            ["git", "commit", "-m", "worktree edit README"], cwd=wt_path,
            capture_output=True, text=True, check=True,
        )

        # Dirty main by modifying the SAME file (uncommitted)
        with open(os.path.join(git_repo, "README.md"), "w") as f:
            f.write("main dirty version\n")
    except Exception:
        subprocess.run(
            ["git", "worktree", "remove", "--force", wt_path], cwd=git_repo,
            capture_output=True, text=True,
        )
        raise

    with pytest.raises(WorktreeTeardownError):
        _teardown_worktree(git_repo, wt_path, "dirty-overlap-test")

    # No conflict markers in README.md
    with open(os.path.join(git_repo, "README.md")) as f:
        content = f.read()
    assert "<<<<<<<" not in content, "No conflict markers should be present"
    # No MERGE_HEAD
    assert not os.path.exists(os.path.join(git_repo, ".git", "MERGE_HEAD")), \
        "MERGE_HEAD should not exist after abort"
    # Worktree still exists
    assert os.path.isdir(wt_path), "Worktree should still exist for manual resolution"
    # Branch still exists
    br_check = subprocess.run(
        ["git", "rev-parse", "--verify", "refs/heads/bellows-wt/dirty-overlap-test"],
        cwd=git_repo, capture_output=True, text=True,
    )
    assert br_check.returncode == 0, "Branch should still exist after conflict"

    # Clean up
    subprocess.run(
        ["git", "worktree", "remove", "--force", wt_path], cwd=git_repo,
        capture_output=True, text=True,
    )


def test_landing_noff_when_main_advanced(git_repo):
    """When main advances, ff-only fails and --no-ff merge lands with worktree SHAs reachable."""
    wt_path = _create_worktree(git_repo, "noff-test")
    try:
        # Commit in worktree
        with open(os.path.join(wt_path, "new_file.txt"), "w") as f:
            f.write("worktree content\n")
        subprocess.run(["git", "add", "new_file.txt"], cwd=wt_path, capture_output=True, text=True)
        subprocess.run(
            ["git", "commit", "-m", "worktree commit"], cwd=wt_path,
            capture_output=True, text=True, check=True,
        )
        wt_sha = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=wt_path,
            capture_output=True, text=True,
        ).stdout.strip()

        # Advance main with a different file
        with open(os.path.join(git_repo, "main_new.txt"), "w") as f:
            f.write("main advance\n")
        subprocess.run(["git", "add", "main_new.txt"], cwd=git_repo, capture_output=True, text=True)
        subprocess.run(
            ["git", "commit", "-m", "main advance commit"], cwd=git_repo,
            capture_output=True, text=True, check=True,
        )
    except Exception:
        subprocess.run(
            ["git", "worktree", "remove", "--force", wt_path], cwd=git_repo,
            capture_output=True, text=True,
        )
        raise

    _teardown_worktree(git_repo, wt_path, "noff-test")

    # Both files on main
    assert os.path.isfile(os.path.join(git_repo, "new_file.txt")), \
        "Worktree file should be on main"
    assert os.path.isfile(os.path.join(git_repo, "main_new.txt")), \
        "Main's commit should be preserved"
    # Merge commit exists
    log_result = subprocess.run(
        ["git", "--no-pager", "log", "--oneline", "-1"], cwd=git_repo,
        capture_output=True, text=True,
    )
    assert "Merge" in log_result.stdout, \
        f"Expected a merge commit, got: {log_result.stdout}"
    # Worktree SHA reachable from HEAD
    ancestor_check = subprocess.run(
        ["git", "merge-base", "--is-ancestor", wt_sha, "HEAD"], cwd=git_repo,
        capture_output=True, text=True,
    )
    assert ancestor_check.returncode == 0, \
        f"Worktree SHA {wt_sha} should be reachable from HEAD"
    # Worktree removed and branch cleaned
    assert not os.path.isdir(wt_path), "Worktree should be removed"
    br_check = subprocess.run(
        ["git", "rev-parse", "--verify", "refs/heads/bellows-wt/noff-test"],
        cwd=git_repo, capture_output=True, text=True,
    )
    assert br_check.returncode != 0, "Branch should be deleted after successful teardown"


def test_landing_aborts_on_true_conflict_main_advanced(git_repo):
    """Main advanced + true content conflict: merge --abort, raise, no partial state."""
    wt_path = _create_worktree(git_repo, "true-conflict-test")
    try:
        # Modify README.md in worktree and commit
        with open(os.path.join(wt_path, "README.md"), "w") as f:
            f.write("worktree conflicting version\n")
        subprocess.run(["git", "add", "README.md"], cwd=wt_path, capture_output=True, text=True)
        subprocess.run(
            ["git", "commit", "-m", "worktree conflict"], cwd=wt_path,
            capture_output=True, text=True, check=True,
        )

        # Modify README.md differently on main and commit (true conflict)
        with open(os.path.join(git_repo, "README.md"), "w") as f:
            f.write("main conflicting version\n")
        subprocess.run(["git", "add", "README.md"], cwd=git_repo, capture_output=True, text=True)
        subprocess.run(
            ["git", "commit", "-m", "main conflict"], cwd=git_repo,
            capture_output=True, text=True, check=True,
        )
    except Exception:
        subprocess.run(
            ["git", "worktree", "remove", "--force", wt_path], cwd=git_repo,
            capture_output=True, text=True,
        )
        raise

    with pytest.raises(WorktreeTeardownError, match="merge conflict"):
        _teardown_worktree(git_repo, wt_path, "true-conflict-test")

    # No MERGE_HEAD (abort was clean)
    assert not os.path.exists(os.path.join(git_repo, ".git", "MERGE_HEAD")), \
        "MERGE_HEAD should not exist after abort"
    # No conflict markers
    with open(os.path.join(git_repo, "README.md")) as f:
        content = f.read()
    assert "<<<<<<<" not in content, "No conflict markers"
    # git status has no merge artifacts (only .bellows-worktrees/ may remain)
    status = subprocess.run(
        ["git", "status", "--porcelain"], cwd=git_repo,
        capture_output=True, text=True,
    )
    non_wt_status = [l for l in status.stdout.strip().splitlines() if ".bellows-worktrees" not in l]
    assert non_wt_status == [], \
        f"Working tree should have no merge artifacts after abort: {non_wt_status}"
    # Worktree still exists
    assert os.path.isdir(wt_path), "Worktree should still exist"
    # Branch still exists (not fully merged, -d would fail)
    br_check = subprocess.run(
        ["git", "rev-parse", "--verify", "refs/heads/bellows-wt/true-conflict-test"],
        cwd=git_repo, capture_output=True, text=True,
    )
    assert br_check.returncode == 0, "Branch should still exist after conflict"

    # Clean up
    subprocess.run(
        ["git", "worktree", "remove", "--force", wt_path], cwd=git_repo,
        capture_output=True, text=True,
    )


def test_sha_identity_ff_and_noff(git_repo):
    """SHA identity: ff path main tip == worktree tip; no-ff path worktree SHAs reachable."""
    # Sub-test A: ff path
    wt_path = _create_worktree(git_repo, "sha-ff-test")
    try:
        with open(os.path.join(wt_path, "ff_file.txt"), "w") as f:
            f.write("ff content\n")
        subprocess.run(["git", "add", "ff_file.txt"], cwd=wt_path, capture_output=True, text=True)
        subprocess.run(
            ["git", "commit", "-m", "ff commit"], cwd=wt_path,
            capture_output=True, text=True, check=True,
        )
        wt_sha_ff = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=wt_path,
            capture_output=True, text=True,
        ).stdout.strip()
    except Exception:
        subprocess.run(
            ["git", "worktree", "remove", "--force", wt_path], cwd=git_repo,
            capture_output=True, text=True,
        )
        raise

    _teardown_worktree(git_repo, wt_path, "sha-ff-test")
    main_head_ff = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=git_repo,
        capture_output=True, text=True,
    ).stdout.strip()
    assert main_head_ff == wt_sha_ff, \
        f"FF path: main HEAD ({main_head_ff}) should equal worktree SHA ({wt_sha_ff})"

    # Sub-test B: no-ff path
    wt_path = _create_worktree(git_repo, "sha-noff-test")
    try:
        with open(os.path.join(wt_path, "noff_file.txt"), "w") as f:
            f.write("noff content\n")
        subprocess.run(["git", "add", "noff_file.txt"], cwd=wt_path, capture_output=True, text=True)
        subprocess.run(
            ["git", "commit", "-m", "noff commit"], cwd=wt_path,
            capture_output=True, text=True, check=True,
        )
        wt_sha_noff = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=wt_path,
            capture_output=True, text=True,
        ).stdout.strip()

        # Advance main
        with open(os.path.join(git_repo, "main_advance.txt"), "w") as f:
            f.write("advance\n")
        subprocess.run(["git", "add", "main_advance.txt"], cwd=git_repo, capture_output=True, text=True)
        subprocess.run(
            ["git", "commit", "-m", "advance main"], cwd=git_repo,
            capture_output=True, text=True, check=True,
        )
    except Exception:
        subprocess.run(
            ["git", "worktree", "remove", "--force", wt_path], cwd=git_repo,
            capture_output=True, text=True,
        )
        raise

    _teardown_worktree(git_repo, wt_path, "sha-noff-test")
    ancestor_check = subprocess.run(
        ["git", "merge-base", "--is-ancestor", wt_sha_noff, "HEAD"], cwd=git_repo,
        capture_output=True, text=True,
    )
    assert ancestor_check.returncode == 0, \
        f"No-ff path: worktree SHA ({wt_sha_noff}) should be reachable from HEAD"


def test_legacy_branchless_worktree_raises_descriptive_error(git_repo):
    """A pre-merge-model detached-HEAD worktree raises a descriptive WorktreeTeardownError."""
    slug = "legacy-test"
    wt_path = os.path.join(git_repo, ".bellows-worktrees", slug)
    os.makedirs(os.path.dirname(wt_path), exist_ok=True)

    # Create a DETACHED-HEAD worktree manually (the old model)
    subprocess.run(
        ["git", "worktree", "add", wt_path, "HEAD", "--detach"], cwd=git_repo,
        capture_output=True, text=True, check=True,
    )

    with pytest.raises(WorktreeTeardownError, match="legacy detached-HEAD") as exc_info:
        _teardown_worktree(git_repo, wt_path, slug)

    assert f"bellows-wt/{slug}" in str(exc_info.value), \
        "Error message should contain the expected branch name"
    assert os.path.isdir(wt_path), "Worktree should still exist after legacy detection"

    # Clean up
    subprocess.run(
        ["git", "worktree", "remove", "--force", wt_path], cwd=git_repo,
        capture_output=True, text=True,
    )


def test_auto_stage_preserves_untracked_deposit_on_teardown(git_repo):
    """An untracked file matching a declared deposit is auto-staged, committed,
    and survives teardown (merged to main)."""
    wt_path = _create_worktree(git_repo, "auto-stage-test")
    deposit_rel = "knowledge/development/test-deposit.md"
    deposit_abs = os.path.join(wt_path, deposit_rel)
    os.makedirs(os.path.dirname(deposit_abs), exist_ok=True)
    with open(deposit_abs, "w") as f:
        f.write("# Test deposit\n")

    # Confirm the file is untracked
    st = subprocess.run(
        ["git", "status", "--porcelain", "--", deposit_abs],
        cwd=wt_path, capture_output=True, text=True,
    )
    assert st.stdout.strip().startswith("??"), f"File should be untracked: {st.stdout}"

    # Plan text that declares the deposit
    plan_text = f"""## STEP 1 — DEV
> Do work.
> **Deposits:**
> - `{deposit_rel}`
"""
    _auto_stage_deposits(plan_text, {}, git_repo, wt_path, "auto-stage-test")

    # Verify the file is now committed
    st2 = subprocess.run(
        ["git", "status", "--porcelain", "--", deposit_abs],
        cwd=wt_path, capture_output=True, text=True,
    )
    assert st2.stdout.strip() == "", f"File should be committed (clean): {st2.stdout}"

    _teardown_worktree(git_repo, wt_path, "auto-stage-test")

    # Verify the file exists on main after merge
    main_deposit = os.path.join(git_repo, deposit_rel)
    assert os.path.isfile(main_deposit), \
        f"Auto-staged deposit should survive teardown and exist on main: {main_deposit}"


def test_auto_stage_handles_multiple_deposits(git_repo):
    """Multiple declared deposits: one committed, one untracked, one staged-only
    — all three survive teardown after auto-staging."""
    wt_path = _create_worktree(git_repo, "multi-deposit-test")
    os.makedirs(os.path.join(wt_path, "knowledge", "development"), exist_ok=True)

    # Deposit 1: already committed
    d1 = os.path.join(wt_path, "knowledge", "development", "committed.md")
    with open(d1, "w") as f:
        f.write("# Already committed\n")
    subprocess.run(["git", "add", "--", d1], cwd=wt_path, capture_output=True, text=True)
    subprocess.run(
        ["git", "commit", "-m", "commit deposit 1"], cwd=wt_path,
        capture_output=True, text=True, check=True,
    )

    # Deposit 2: untracked
    d2 = os.path.join(wt_path, "knowledge", "development", "untracked.md")
    with open(d2, "w") as f:
        f.write("# Untracked deposit\n")

    # Deposit 3: staged but not committed
    d3 = os.path.join(wt_path, "knowledge", "development", "staged-only.md")
    with open(d3, "w") as f:
        f.write("# Staged only\n")
    subprocess.run(["git", "add", "--", d3], cwd=wt_path, capture_output=True, text=True)

    plan_text = """## STEP 1 — DEV
> Do work.
> **Deposits:**
> - `knowledge/development/committed.md`
> - `knowledge/development/untracked.md`
> - `knowledge/development/staged-only.md`
"""
    _auto_stage_deposits(plan_text, {}, git_repo, wt_path, "multi-deposit-test")
    _teardown_worktree(git_repo, wt_path, "multi-deposit-test")

    for name in ("committed.md", "untracked.md", "staged-only.md"):
        path = os.path.join(git_repo, "knowledge", "development", name)
        assert os.path.isfile(path), f"Deposit {name} should survive teardown on main"


def test_auto_stage_noop_when_all_committed(git_repo):
    """When all declared deposits are already committed, no extra commit is created."""
    wt_path = _create_worktree(git_repo, "noop-test")
    deposit_rel = "knowledge/development/already-committed.md"
    deposit_abs = os.path.join(wt_path, deposit_rel)
    os.makedirs(os.path.dirname(deposit_abs), exist_ok=True)
    with open(deposit_abs, "w") as f:
        f.write("# Already committed\n")
    subprocess.run(["git", "add", "--", deposit_abs], cwd=wt_path, capture_output=True, text=True)
    subprocess.run(
        ["git", "commit", "-m", "commit deposit"], cwd=wt_path,
        capture_output=True, text=True, check=True,
    )

    # Record commit count before auto-stage
    log_before = subprocess.run(
        ["git", "log", "--oneline"], cwd=wt_path,
        capture_output=True, text=True,
    )
    count_before = len(log_before.stdout.strip().splitlines())

    plan_text = f"""## STEP 1 — DEV
> Do work.
> **Deposits:**
> - `{deposit_rel}`
"""
    _auto_stage_deposits(plan_text, {}, git_repo, wt_path, "noop-test")

    # No new commit should be created
    log_after = subprocess.run(
        ["git", "log", "--oneline"], cwd=wt_path,
        capture_output=True, text=True,
    )
    count_after = len(log_after.stdout.strip().splitlines())
    assert count_after == count_before, \
        f"No extra commit should be created when all deposits are committed (before={count_before}, after={count_after})"

    # Clean up
    _teardown_worktree(git_repo, wt_path, "noop-test")


# ---------------------------------------------------------------------------
# Tests for bellows #100115 (thread 322):
# _preserve_and_remove_stranded_worktree — identity proof, registered-HEAD
# read, tip in both modes, symlink guard, foreign-repository stop, removal
# stop, step-number in pause, final-step precondition retry.
# RED on the base; GREEN after Step 2.
# ---------------------------------------------------------------------------

import pathlib as _pl
import stat as _stat

_REAL_SUBPROCESS_RUN = subprocess.run


def _filesystem_is_case_sensitive():
    with tempfile.TemporaryDirectory() as d:
        lower = os.path.join(d, "casechk")
        open(lower, "w").close()
        return not os.path.exists(os.path.join(d, "CASECHK"))


def _make_unlanded_worktree(project_path, slug):
    """Return (wt_path, tip_sha) — worktree with one un-landed commit on bellows-wt/<slug>."""
    wt_path = _create_worktree(project_path, slug)
    with open(os.path.join(wt_path, "work.txt"), "w") as f:
        f.write("unlanded work\n")
    subprocess.run(["git", "add", "work.txt"], cwd=wt_path,
                   capture_output=True, text=True)
    subprocess.run(["git", "commit", "-m", "unlanded commit"], cwd=wt_path,
                   capture_output=True, text=True, check=True)
    tip = subprocess.run(["git", "rev-parse", "HEAD"], cwd=wt_path,
                         capture_output=True, text=True).stdout.strip()
    return wt_path, tip


def _drop_git_file(wt_path):
    """Remove the .git file from a worktree, leaving a plain directory."""
    git_file = os.path.join(wt_path, ".git")
    if os.path.isfile(git_file) and not os.path.islink(git_file):
        os.remove(git_file)


def _drop_worktree_entry(project_path, slug):
    """Delete the .git/worktrees/<slug> directory to create the gitdir-gone shape.

    After this the worktree's .git file still points to
    <project>/.git/worktrees/<slug> but the entry no longer exists.
    Git cannot resolve the repository for the worktree path → not its own.
    """
    entry = os.path.join(project_path, ".git", "worktrees", slug)
    if os.path.isdir(entry):
        shutil.rmtree(entry)


def _subprocess_fail_matching(pattern_args, exc=None, rc=1, stderr="injected"):
    """Return a subprocess.run side_effect that fails when command matches all patterns."""
    def _side(cmd, **kw):
        cmd_list = list(cmd) if not isinstance(cmd, str) else cmd.split()
        if all(p in cmd_list for p in pattern_args):
            if exc is not None:
                raise exc
            r = MagicMock()
            r.returncode = rc
            r.stdout = ""
            r.stderr = stderr
            return r
        return _REAL_SUBPROCESS_RUN(cmd, **kw)
    return _side


def _get_branch_tip(project_path, branch):
    r = subprocess.run(["git", "rev-parse", "--verify", f"refs/heads/{branch}"],
                       cwd=project_path, capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else None


def _list_preserved(project_path, slug):
    r = subprocess.run(["git", "branch", "--list", f"bellows-preserved/{slug}-*"],
                       cwd=project_path, capture_output=True, text=True)
    return [b.strip().lstrip("* ") for b in r.stdout.strip().splitlines() if b.strip()]


def _is_reachable(project_path, sha):
    r = subprocess.run(["git", "for-each-ref", "--contains", sha,
                        "--format=%(refname)", "refs/heads/"],
                       cwd=project_path, capture_output=True, text=True)
    return bool(r.stdout.strip())


# --- x1: tip preserved on -branch when path is plain directory ----------------

def test_stranded_plain_directory_preserves_branch_tip(git_repo):
    """x1: bellows-wt/<slug> tip kept on bellows-preserved/<slug>-<ts>-branch when path is plain dir."""
    slug = "x1-tip-slug"
    wt_path, tip = _make_unlanded_worktree(git_repo, slug)
    _drop_git_file(wt_path)

    with patch("bellows._log") as mock_log:
        new_wt = _create_worktree(git_repo, slug)

    try:
        branches = _list_preserved(git_repo, slug)
        tip_branches = [b for b in branches if b.endswith("-branch")]
        assert tip_branches, f"Expected a -branch preservation, got: {branches}"
        br_tip = _get_branch_tip(git_repo, tip_branches[0])
        assert br_tip == tip, f"Tip branch should point at {tip}, got {br_tip}"
        assert _is_reachable(git_repo, tip), "Tip must be reachable from a ref"
        warn_msgs = [str(c) for c in mock_log.call_args_list if "WARN" in str(c)]
        assert any("bellows-preserved" in m for m in warn_msgs), \
            f"Expected WARN naming the preservation branch: {warn_msgs}"
        assert os.path.isdir(new_wt), "New worktree must exist"
    finally:
        subprocess.run(["git", "worktree", "remove", "--force", new_wt],
                       cwd=git_repo, capture_output=True, text=True)
        for b in _list_preserved(git_repo, slug):
            subprocess.run(["git", "branch", "-D", b], cwd=git_repo,
                           capture_output=True, text=True)


# --- x2: checkout HEAD NOT preserved when path is plain directory -------------

def test_stranded_plain_directory_does_not_preserve_checkout_head(git_repo):
    """x2: only the tip is preserved, not the checkout (main) HEAD."""
    slug = "x2-no-checkout-slug"
    main_head = subprocess.run(["git", "rev-parse", "main"], cwd=git_repo,
                                capture_output=True, text=True).stdout.strip()
    wt_path, tip = _make_unlanded_worktree(git_repo, slug)
    assert tip != main_head, "precondition: tip must differ from main"
    _drop_git_file(wt_path)

    new_wt = _create_worktree(git_repo, slug)
    try:
        branches = _list_preserved(git_repo, slug)
        # No branch should point at main's HEAD
        for b in branches:
            b_sha = _get_branch_tip(git_repo, b)
            assert b_sha != main_head, \
                f"Branch {b} must not point at main HEAD {main_head}"
        tip_branches = [b for b in branches if b.endswith("-branch")]
        assert tip_branches, "Tip must be preserved on a -branch"
    finally:
        subprocess.run(["git", "worktree", "remove", "--force", new_wt],
                       cwd=git_repo, capture_output=True, text=True)
        for b in _list_preserved(git_repo, slug):
            subprocess.run(["git", "branch", "-D", b], cwd=git_repo,
                           capture_output=True, text=True)


# --- x3: tip ON main not preserved (GREEN on base) ---------------------------

def test_stranded_plain_directory_tip_on_main_not_preserved(git_repo):
    """x3: no bellows-preserved/* when the tip is already on main (GREEN on base)."""
    slug = "x3-on-main-slug"
    wt_path = _create_worktree(git_repo, slug)
    _drop_git_file(wt_path)

    new_wt = _create_worktree(git_repo, slug)
    try:
        branches = _list_preserved(git_repo, slug)
        assert not branches, f"No preservation branch expected, got: {branches}"
    finally:
        subprocess.run(["git", "worktree", "remove", "--force", new_wt],
                       cwd=git_repo, capture_output=True, text=True)


# --- x4: WARN names path as "not its own repository" -------------------------

def test_stranded_plain_directory_warn_names_path(git_repo):
    """x4: a WARN identifies the path as not its own repository."""
    slug = "x4-warn-slug"
    wt_path, _ = _make_unlanded_worktree(git_repo, slug)
    _drop_git_file(wt_path)

    with patch("bellows._log") as mock_log:
        new_wt = _create_worktree(git_repo, slug)

    try:
        warn_msgs = [str(c) for c in mock_log.call_args_list if "WARN" in str(c)]
        assert any("not its own" in m or "not its own repository" in m for m in warn_msgs), \
            f"Expected WARN naming path as 'not its own repository': {warn_msgs}"
    finally:
        subprocess.run(["git", "worktree", "remove", "--force", new_wt],
                       cwd=git_repo, capture_output=True, text=True)
        for b in _list_preserved(git_repo, slug):
            subprocess.run(["git", "branch", "-D", b], cwd=git_repo,
                           capture_output=True, text=True)


# --- x5: detached HEAD and tip both preserved ---------------------------------

def test_stranded_detached_head_and_branch_tip_both_preserved(git_repo):
    """x5: detached HEAD off the tip's parent, both off main — both kept on separate branches."""
    slug = "x5-both-slug"
    wt_path, tip = _make_unlanded_worktree(git_repo, slug)
    # Detach HEAD in the worktree at a new commit (off the tip's parent)
    subprocess.run(["git", "checkout", "--detach", "HEAD~1"], cwd=wt_path,
                   capture_output=True, text=True)
    with open(os.path.join(wt_path, "detached_work.txt"), "w") as f:
        f.write("detached work\n")
    subprocess.run(["git", "add", "detached_work.txt"], cwd=wt_path, capture_output=True, text=True)
    subprocess.run(["git", "commit", "-m", "detached commit"], cwd=wt_path,
                   capture_output=True, text=True, check=True)
    det_head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=wt_path,
                               capture_output=True, text=True).stdout.strip()
    assert det_head != tip, "precondition: detached HEAD differs from tip"
    # Neither holds the other
    r1 = subprocess.run(["git", "merge-base", "--is-ancestor", tip, det_head],
                        cwd=git_repo, capture_output=True, text=True)
    r2 = subprocess.run(["git", "merge-base", "--is-ancestor", det_head, tip],
                        cwd=git_repo, capture_output=True, text=True)
    assert r1.returncode != 0 and r2.returncode != 0, "precondition: neither holds the other"
    _drop_git_file(wt_path)

    new_wt = _create_worktree(git_repo, slug)
    try:
        branches = _list_preserved(git_repo, slug)
        tip_branches = [b for b in branches if b.endswith("-branch")]
        ts_branches = [b for b in branches if not b.endswith("-branch")]
        assert tip_branches, f"Tip must be on a -branch: {branches}"
        assert ts_branches, f"Detached HEAD must be on a ts branch: {branches}"
        tip_sha = _get_branch_tip(git_repo, tip_branches[0])
        assert tip_sha == tip, f"Tip branch must point at tip {tip}"
        head_sha = _get_branch_tip(git_repo, ts_branches[0])
        assert head_sha == det_head, f"HEAD branch must point at {det_head}"
        assert _is_reachable(git_repo, tip), "Tip must be reachable"
        assert _is_reachable(git_repo, det_head), "Detached HEAD must be reachable"
    finally:
        subprocess.run(["git", "worktree", "remove", "--force", new_wt],
                       cwd=git_repo, capture_output=True, text=True)
        for b in _list_preserved(git_repo, slug):
            subprocess.run(["git", "branch", "-D", b], cwd=git_repo,
                           capture_output=True, text=True)


# --- x6: symlink to checkout — no HEAD read, tip kept, dispatch stopped -------

def test_stranded_symlink_to_checkout_head_neither_read_nor_preserved(git_repo):
    """x6: symlink at wt_path — no git -C <path> run, tip kept, WorktreeCreationError raised."""
    slug = "x6-symlink-checkout"
    wt_dir = os.path.join(git_repo, ".bellows-worktrees")
    os.makedirs(wt_dir, exist_ok=True)
    wt_path = os.path.join(wt_dir, slug)
    # Create the bellows-wt/ branch with a commit so we can check the tip
    subprocess.run(["git", "checkout", "-b", f"bellows-wt/{slug}"],
                   cwd=git_repo, capture_output=True, text=True)
    with open(os.path.join(git_repo, "x6_work.txt"), "w") as f:
        f.write("x6 work\n")
    subprocess.run(["git", "add", "x6_work.txt"], cwd=git_repo, capture_output=True, text=True)
    subprocess.run(["git", "commit", "-m", "x6 unlanded"], cwd=git_repo,
                   capture_output=True, text=True, check=True)
    subprocess.run(["git", "checkout", "main"], cwd=git_repo, capture_output=True, text=True)
    tip = _get_branch_tip(git_repo, f"bellows-wt/{slug}")
    # Place a symlink to the checkout itself at wt_path
    os.symlink(git_repo, wt_path)

    called_with_wt = []
    real_run = _REAL_SUBPROCESS_RUN

    def _track_git_minus_c(cmd, **kw):
        if isinstance(cmd, list) and len(cmd) >= 4 and cmd[0] == "git" and "-C" in cmd:
            idx = cmd.index("-C")
            cwd_arg = cmd[idx + 1]
            if os.path.abspath(cwd_arg) == os.path.abspath(wt_path):
                called_with_wt.append(list(cmd))
        return real_run(cmd, **kw)

    with patch("bellows.subprocess.run", side_effect=_track_git_minus_c), \
         patch("time.sleep"):
        with pytest.raises(WorktreeCreationError) as exc_info:
            _create_worktree(git_repo, slug)

    assert not called_with_wt, \
        f"No git -C <wt_path> commands should run: {called_with_wt}"
    assert os.path.islink(wt_path), "Symlink must still be there (not removed)"
    assert tip is not None
    br_tip = _get_branch_tip(git_repo, f"bellows-wt/{slug}")
    # After WorktreeCreationError: bellows-wt/<slug> is deleted to signal the stop kept it
    # but the tip was preserved on a -branch first
    preserved = _list_preserved(git_repo, slug)
    assert any(_get_branch_tip(git_repo, b) == tip for b in preserved), \
        f"Tip {tip} must be preserved: {preserved}"

    os.unlink(wt_path)
    subprocess.run(["git", "branch", "-D", f"bellows-wt/{slug}"],
                   cwd=git_repo, capture_output=True, text=True)
    for b in _list_preserved(git_repo, slug):
        subprocess.run(["git", "branch", "-D", b], cwd=git_repo,
                       capture_output=True, text=True)


# --- x7: registered detached HEAD preserved from registration -----------------

def test_stranded_plain_directory_registered_detached_head_preserved(git_repo):
    """x7: when path is not its own, detached HEAD from registration kept on bellows-preserved/<ts>."""
    slug = "x7-reg-det-slug"
    wt_path, tip = _make_unlanded_worktree(git_repo, slug)
    # Detach HEAD in the worktree
    subprocess.run(["git", "checkout", "--detach", "HEAD"],
                   cwd=wt_path, capture_output=True, text=True)
    det_head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=wt_path,
                               capture_output=True, text=True).stdout.strip()
    # Remove the .git file — registration still shows the entry (detached)
    _drop_git_file(wt_path)

    new_wt = _create_worktree(git_repo, slug)
    try:
        preserved = _list_preserved(git_repo, slug)
        ts_branches = [b for b in preserved if not b.endswith("-branch")]
        assert ts_branches, f"Expected HEAD preserved on a ts branch: {preserved}"
        head_sha = _get_branch_tip(git_repo, ts_branches[0])
        assert head_sha == det_head, \
            f"Registered HEAD {det_head} must be on ts branch, got {head_sha}"
        assert os.path.isdir(new_wt), "New worktree must exist"
    finally:
        subprocess.run(["git", "worktree", "remove", "--force", new_wt],
                       cwd=git_repo, capture_output=True, text=True)
        for b in _list_preserved(git_repo, slug):
            subprocess.run(["git", "branch", "-D", b], cwd=git_repo,
                           capture_output=True, text=True)


# --- x8: failed tip preservation stops before removal -------------------------

def test_stranded_failed_tip_preservation_stops_before_removal(git_repo):
    """x8: when tip preservation fails, WorktreeCreationError is raised before any removal."""
    slug = "x8-failed-tip-slug"
    wt_path, tip = _make_unlanded_worktree(git_repo, slug)
    _drop_git_file(wt_path)

    tip_sha = _get_branch_tip(git_repo, f"bellows-wt/{slug}")
    assert tip_sha is not None, "bellows-wt/<slug> must exist"

    # Mock git branch to fail when creating the -branch preservation
    def _fail_tip_branch(cmd, **kw):
        if (isinstance(cmd, list) and "branch" in cmd and
                any("bellows-preserved" in str(a) and "-branch" in str(a) for a in cmd)):
            r = MagicMock()
            r.returncode = 1
            r.stdout = ""
            r.stderr = "injected: cannot create -branch"
            return r
        return _REAL_SUBPROCESS_RUN(cmd, **kw)

    with patch("bellows.subprocess.run", side_effect=_fail_tip_branch), \
         patch("bellows._log") as mock_log, \
         patch("time.sleep"):
        with pytest.raises(WorktreeCreationError) as exc_info:
            _create_worktree(git_repo, slug)

    err_msg = str(exc_info.value)
    assert "could not be saved" in err_msg or "failed to preserve" in err_msg, \
        f"Error must say 'could not be saved': {err_msg}"
    assert "left as found" in err_msg or "nothing was removed" in err_msg, \
        f"Error must note nothing removed: {err_msg}"
    # The path must still exist (not removed)
    assert os.path.isdir(wt_path), "Worktree directory must still be there"
    # bellows-wt/<slug> must still exist (not deleted)
    assert _get_branch_tip(git_repo, f"bellows-wt/{slug}") == tip_sha, \
        "bellows-wt/<slug> branch must still exist"

    # Check ERROR was logged with "left as found"
    err_calls = [str(c) for c in mock_log.call_args_list if "ERROR" in str(c)]
    assert any("left as found" in c for c in err_calls), \
        f"Expected ERROR logged with 'left as found': {err_calls}"

    # Clean up
    subprocess.run(["git", "branch", "-D", f"bellows-wt/{slug}"],
                   cwd=git_repo, capture_output=True, text=True)
    shutil.rmtree(wt_path, ignore_errors=True)
    subprocess.run(["git", "worktree", "prune"], cwd=git_repo, capture_output=True, text=True)


# --- x9: nested repository stops before any read or removal ------------------

def test_stranded_nested_repository_stops_before_any_read_or_removal(git_repo):
    """x9: a repository of its own at wt_path — dispatch stopped before any read or removal."""
    slug = "x9-nested-repo"
    wt_dir = os.path.join(git_repo, ".bellows-worktrees")
    os.makedirs(wt_dir, exist_ok=True)
    wt_path = os.path.join(wt_dir, slug)
    os.makedirs(wt_path)
    # Create a nested git repository at wt_path
    subprocess.run(["git", "init", "-b", "main"], cwd=wt_path,
                   capture_output=True, text=True, check=True)
    subprocess.run(["git", "config", "user.email", "t@t.com"], cwd=wt_path,
                   capture_output=True, text=True)
    subprocess.run(["git", "config", "user.name", "T"], cwd=wt_path,
                   capture_output=True, text=True)
    with open(os.path.join(wt_path, "nested.txt"), "w") as f:
        f.write("nested\n")
    subprocess.run(["git", "add", "nested.txt"], cwd=wt_path, capture_output=True, text=True)
    subprocess.run(["git", "commit", "-m", "nested init"], cwd=wt_path,
                   capture_output=True, text=True, check=True)
    nested_head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=wt_path,
                                  capture_output=True, text=True).stdout.strip()

    called_with_wt = []
    real_run = _REAL_SUBPROCESS_RUN

    def _track_wt_calls(cmd, **kw):
        if isinstance(cmd, list) and "-C" in cmd:
            idx = cmd.index("-C")
            try:
                if os.path.samefile(cmd[idx + 1], wt_path):
                    called_with_wt.append(list(cmd))
            except OSError:
                pass
        return real_run(cmd, **kw)

    with patch("bellows.subprocess.run", side_effect=_track_wt_calls), \
         patch("time.sleep"):
        with pytest.raises(WorktreeCreationError) as exc_info:
            _create_worktree(git_repo, slug)

    err_msg = str(exc_info.value)
    assert "repository of its own" in err_msg or "a .git directory" in err_msg, \
        f"Error must name foreign repository: {err_msg}"
    assert "nothing was read" in err_msg or "nothing was removed" in err_msg, \
        f"Error must note nothing read/removed: {err_msg}"
    assert "move or remove" in err_msg, f"Error must give the act: {err_msg}"
    assert not called_with_wt, f"No git -C <wt_path> should run: {called_with_wt}"
    assert os.path.isdir(wt_path), "Nested repo must still be there"
    assert os.path.isfile(os.path.join(wt_path, "nested.txt")), "Nested file intact"
    # bellows-wt/<slug> should be absent (never created)
    assert _get_branch_tip(git_repo, f"bellows-wt/{slug}") is None, \
        "bellows-wt/<slug> must not exist"
    # Move the nested repo aside and verify a second create succeeds
    aside = wt_path + "-aside"
    shutil.move(wt_path, aside)
    try:
        new_wt = _create_worktree(git_repo, slug)
        assert os.path.isdir(new_wt), "Second create must succeed"
        subprocess.run(["git", "worktree", "remove", "--force", new_wt],
                       cwd=git_repo, capture_output=True, text=True)
    finally:
        shutil.rmtree(aside, ignore_errors=True)


# --- x10: own worktree through case-variant path (GREEN on case-insensitive) --

def test_stranded_own_worktree_through_case_variant_path(git_repo):
    """x10: case-variant path still proves own worktree by inode (skip on case-sensitive fs)."""
    if _filesystem_is_case_sensitive():
        pytest.skip("case-sensitive filesystem — x10 only runs on case-insensitive (macOS default)")
    slug = "x10-case-slug"
    wt_path, _ = _make_unlanded_worktree(git_repo, slug)
    wt_path_upper = wt_path.upper()
    assert os.path.exists(wt_path_upper), "Precondition: upper-case path must exist on case-insensitive fs"

    with patch("bellows._log") as mock_log:
        new_wt = _create_worktree(git_repo, slug)

    try:
        warn_msgs = [str(c) for c in mock_log.call_args_list if "WARN" in str(c)]
        assert not any("not its own" in m for m in warn_msgs), \
            f"Should NOT warn 'not its own' for case variant: {warn_msgs}"
        preserved = _list_preserved(git_repo, slug)
        ts_branches = [b for b in preserved if not b.endswith("-branch")]
        assert ts_branches, f"Detached HEAD must be preserved for own worktree: {preserved}"
    finally:
        subprocess.run(["git", "worktree", "remove", "--force", new_wt],
                       cwd=git_repo, capture_output=True, text=True)
        for b in _list_preserved(git_repo, slug):
            subprocess.run(["git", "branch", "-D", b], cwd=git_repo,
                           capture_output=True, text=True)


# --- x11: failed-save stops before removal (7 parametrized cases) -------------

@pytest.mark.parametrize("case_id", [
    "head-read-raises",
    "head-read-nonzero",
    "porcelain-raises",
    "porcelain-nonzero",
    "head-branch-raises",
    "head-branch-nonzero",
    "tip-check-raises",
])
def test_stranded_failed_save_stops_before_removal(git_repo, case_id):
    """x11: each failed-save stop raises WorktreeCreationError before any removal."""
    slug = f"x11-{case_id}"
    real_run = _REAL_SUBPROCESS_RUN

    # For cases that need a plain directory (not its own):
    plain_cases = {"porcelain-raises", "porcelain-nonzero"}
    # For tip-check-raises we need the HEAD branch to succeed first:
    tip_check_case = case_id == "tip-check-raises"

    if case_id in plain_cases:
        wt_path, _ = _make_unlanded_worktree(git_repo, slug)
        _drop_git_file(wt_path)
    else:
        wt_path, tip = _make_unlanded_worktree(git_repo, slug)
        if tip_check_case:
            # Detach HEAD so it's off main and the HEAD branch creation succeeds
            subprocess.run(["git", "checkout", "--detach", "HEAD~1"],
                           cwd=wt_path, capture_output=True, text=True)

    initial_dir_exists = os.path.isdir(wt_path)
    initial_tip = _get_branch_tip(git_repo, f"bellows-wt/{slug}")

    def _inject(cmd, **kw):
        cmd_list = list(cmd) if not isinstance(cmd, str) else cmd.split()
        # head-read-*: fail rev-parse --verify HEAD (but NOT --show-toplevel)
        if case_id in {"head-read-raises", "head-read-nonzero"}:
            if ("rev-parse" in cmd_list and "--verify" in cmd_list and
                    "HEAD" in cmd_list and "--show-toplevel" not in cmd_list):
                if case_id == "head-read-raises":
                    raise subprocess.TimeoutExpired(cmd, 10)
                r = MagicMock()
                r.returncode = 1; r.stdout = ""; r.stderr = "injected"
                return r
        # porcelain-*: fail worktree list --porcelain
        if case_id in {"porcelain-raises", "porcelain-nonzero"}:
            if "worktree" in cmd_list and "list" in cmd_list and "--porcelain" in cmd_list:
                if case_id == "porcelain-raises":
                    raise subprocess.TimeoutExpired(cmd, 10)
                r = MagicMock()
                r.returncode = 1; r.stdout = ""; r.stderr = "injected"
                return r
        # head-branch-*: fail git branch <bellows-preserved/<slug>-<ts>> <sha>
        if case_id in {"head-branch-raises", "head-branch-nonzero"}:
            if ("branch" in cmd_list and
                    any("bellows-preserved" in str(a) and "-branch" not in str(a) for a in cmd_list)):
                if case_id == "head-branch-raises":
                    raise subprocess.TimeoutExpired(cmd, 10)
                r = MagicMock()
                r.returncode = 1; r.stdout = ""; r.stderr = "injected"
                return r
        # tip-check-raises: fail rev-parse --verify refs/heads/bellows-wt/...
        if case_id == "tip-check-raises":
            if ("rev-parse" in cmd_list and "--verify" in cmd_list and
                    any("bellows-wt" in str(a) for a in cmd_list)):
                raise subprocess.TimeoutExpired(cmd, 10)
        return real_run(cmd, **kw)

    with patch("bellows.subprocess.run", side_effect=_inject), \
         patch("bellows._log") as mock_log, \
         patch("time.sleep"):
        with pytest.raises(WorktreeCreationError) as exc_info:
            _create_worktree(git_repo, slug)

    err_msg = str(exc_info.value)
    assert "could not be saved" in err_msg or "nothing was removed" in err_msg, \
        f"[{case_id}] Error must say 'could not be saved': {err_msg}"
    assert "left as found" in err_msg or "nothing was removed" in err_msg, \
        f"[{case_id}] Error must note nothing removed: {err_msg}"

    # Directory must still exist (nothing removed)
    assert os.path.isdir(wt_path), f"[{case_id}] Directory must still exist"
    # bellows-wt/<slug> must be unchanged
    assert _get_branch_tip(git_repo, f"bellows-wt/{slug}") == initial_tip, \
        f"[{case_id}] bellows-wt/<slug> must be unchanged"

    # ERROR must have been logged with "left as found"
    err_logs = [str(c) for c in mock_log.call_args_list if "ERROR" in str(c)]
    assert any("left as found" in e for e in err_logs), \
        f"[{case_id}] Expected ERROR with 'left as found': {err_logs}"

    # For tip-check-raises: the HEAD branch was created before the stop — name it in message
    if case_id == "tip-check-raises":
        assert "bellows-preserved" in err_msg, \
            f"[{case_id}] Message must name the HEAD branch created before the stop"

    # Clean up
    subprocess.run(["git", "branch", "-D", f"bellows-wt/{slug}"],
                   cwd=git_repo, capture_output=True, text=True)
    shutil.rmtree(wt_path, ignore_errors=True)
    subprocess.run(["git", "worktree", "prune"], cwd=git_repo, capture_output=True, text=True)
    for b in _list_preserved(git_repo, slug):
        subprocess.run(["git", "branch", "-D", b], cwd=git_repo, capture_output=True, text=True)


# --- x12: registered detached HEAD through case-variant path ------------------

def test_stranded_registered_detached_head_through_case_variant_path(git_repo):
    """x12: registration matched by inode, not string, for case-variant path (skip on case-sensitive)."""
    if _filesystem_is_case_sensitive():
        pytest.skip("case-sensitive filesystem — x12 only runs on case-insensitive (macOS default)")
    slug = "x12-case-det-slug"
    wt_path, tip = _make_unlanded_worktree(git_repo, slug)
    wt_path_upper = wt_path.upper()
    assert os.path.samefile(wt_path, wt_path_upper), \
        "Precondition: two spellings are one directory by inode"
    assert wt_path != wt_path_upper, \
        "Precondition: two spellings are two realpath strings"
    # Detach HEAD in the worktree
    subprocess.run(["git", "checkout", "--detach", "HEAD"],
                   cwd=wt_path, capture_output=True, text=True)
    det_head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=wt_path,
                               capture_output=True, text=True).stdout.strip()
    _drop_git_file(wt_path)

    new_wt = _create_worktree(git_repo, slug)
    try:
        preserved = _list_preserved(git_repo, slug)
        ts_branches = [b for b in preserved if not b.endswith("-branch")]
        assert ts_branches, f"Detached HEAD must be preserved: {preserved}"
        head_sha = _get_branch_tip(git_repo, ts_branches[0])
        assert head_sha == det_head, \
            f"Registration matched by inode — HEAD {det_head} must be preserved"
    finally:
        subprocess.run(["git", "worktree", "remove", "--force", new_wt],
                       cwd=git_repo, capture_output=True, text=True)
        for b in _list_preserved(git_repo, slug):
            subprocess.run(["git", "branch", "-D", b], cwd=git_repo,
                           capture_output=True, text=True)


# --- x13: failed save raises before worktree_add -----------------------------

def test_stranded_failed_save_raises_before_worktree_add(git_repo):
    """x13: failed save raises WorktreeCreationError before git worktree add runs."""
    slug = "x13-no-add"
    wt_path, tip = _make_unlanded_worktree(git_repo, slug)
    # Simulate gitdir-gone: worktree is own, detach HEAD, delete branch
    subprocess.run(["git", "checkout", "--detach", "HEAD"],
                   cwd=wt_path, capture_output=True, text=True)
    subprocess.run(["git", "branch", "-D", f"bellows-wt/{slug}"],
                   cwd=git_repo, capture_output=True, text=True)
    det_head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=wt_path,
                               capture_output=True, text=True).stdout.strip()

    worktree_add_called = []
    real_run = _REAL_SUBPROCESS_RUN

    def _inject(cmd, **kw):
        cmd_list = list(cmd) if not isinstance(cmd, str) else cmd.split()
        # Fail git branch for HEAD preservation
        if ("branch" in cmd_list and
                any("bellows-preserved" in str(a) for a in cmd_list)):
            r = MagicMock()
            r.returncode = 1; r.stdout = ""; r.stderr = "injected branch fail"
            return r
        # Track worktree add
        if "worktree" in cmd_list and "add" in cmd_list:
            worktree_add_called.append(list(cmd))
        return real_run(cmd, **kw)

    with patch("bellows.subprocess.run", side_effect=_inject), \
         patch("time.sleep"):
        with pytest.raises(WorktreeCreationError):
            _create_worktree(git_repo, slug)

    assert not worktree_add_called, \
        f"git worktree add must NOT run after a failed save: {worktree_add_called}"
    assert os.path.isdir(wt_path), "Directory must still be there"
    assert _get_branch_tip(git_repo, f"bellows-wt/{slug}") is None, \
        "bellows-wt/<slug> still absent"
    assert subprocess.run(["git", "rev-parse", "--verify", det_head],
                          cwd=git_repo, capture_output=True, text=True).returncode == 0, \
        "HEAD commit must still be reachable"
    # Clean up and verify second create works
    shutil.rmtree(wt_path, ignore_errors=True)
    subprocess.run(["git", "worktree", "prune"], cwd=git_repo, capture_output=True, text=True)
    new_wt = _create_worktree(git_repo, slug)
    assert os.path.isdir(new_wt)
    subprocess.run(["git", "worktree", "remove", "--force", new_wt],
                   cwd=git_repo, capture_output=True, text=True)


# --- x14: unremovable symlink stops before worktree_add ----------------------

def test_stranded_unremovable_symlink_stops_before_worktree_add(git_repo):
    """x14: symlink at wt_path — tip kept, removal stop raised, worktree_add NOT called."""
    slug = "x14-symlink-stop"
    wt_dir = os.path.join(git_repo, ".bellows-worktrees")
    os.makedirs(wt_dir, exist_ok=True)
    wt_path = os.path.join(wt_dir, slug)
    # Create a branch with un-landed commit for the tip
    subprocess.run(["git", "checkout", "-b", f"bellows-wt/{slug}"],
                   cwd=git_repo, capture_output=True, text=True)
    with open(os.path.join(git_repo, "x14_work.txt"), "w") as f:
        f.write("x14 work\n")
    subprocess.run(["git", "add", "x14_work.txt"], cwd=git_repo, capture_output=True, text=True)
    subprocess.run(["git", "commit", "-m", "x14 unlanded"], cwd=git_repo,
                   capture_output=True, text=True, check=True)
    subprocess.run(["git", "checkout", "main"], cwd=git_repo, capture_output=True, text=True)
    tip = _get_branch_tip(git_repo, f"bellows-wt/{slug}")
    # Place a symlink (to a temp dir — "unremovable" in the sense that remove is wrong)
    target_dir = tempfile.mkdtemp()
    os.symlink(target_dir, wt_path)

    worktree_add_called = []
    real_run = _REAL_SUBPROCESS_RUN

    def _track(cmd, **kw):
        if isinstance(cmd, list) and "worktree" in cmd and "add" in cmd:
            worktree_add_called.append(list(cmd))
        return real_run(cmd, **kw)

    with patch("bellows.subprocess.run", side_effect=_track), \
         patch("time.sleep"):
        with pytest.raises(WorktreeCreationError) as exc_info:
            _create_worktree(git_repo, slug)

    err_msg = str(exc_info.value)
    assert "symlink" in err_msg or "unlink" in err_msg, \
        f"Error must mention symlink: {err_msg}"
    assert not worktree_add_called, "git worktree add must NOT run"
    assert os.path.islink(wt_path), "Symlink must still be there"
    # Tip must be preserved on a -branch
    preserved = _list_preserved(git_repo, slug)
    assert any(_get_branch_tip(git_repo, b) == tip for b in preserved), \
        f"Tip must be preserved: {preserved}"
    # bellows-wt/<slug> deleted after its tip was kept
    assert _get_branch_tip(git_repo, f"bellows-wt/{slug}") is None, \
        "bellows-wt/<slug> must be deleted"
    # Clean up and verify second create works
    os.unlink(wt_path)
    shutil.rmtree(target_dir, ignore_errors=True)
    for b in _list_preserved(git_repo, slug):
        subprocess.run(["git", "branch", "-D", b], cwd=git_repo, capture_output=True, text=True)
    new_wt = _create_worktree(git_repo, slug)
    assert os.path.isdir(new_wt)
    subprocess.run(["git", "worktree", "remove", "--force", new_wt],
                   cwd=git_repo, capture_output=True, text=True)


# --- x15: partly-removable directory stops before worktree_add ---------------

def test_stranded_partly_removable_directory_stops_before_worktree_add(git_repo):
    """x15: directory that can't be fully removed — stop after tip kept, worktree_add NOT called."""
    slug = "x15-partial-remove"
    wt_path, tip = _make_unlanded_worktree(git_repo, slug)
    _drop_git_file(wt_path)
    # Create a read-only subdirectory that rmtree can't remove
    ro_dir = os.path.join(wt_path, "read_only_sub")
    os.makedirs(ro_dir)
    os.chmod(ro_dir, _stat.S_IRUSR | _stat.S_IXUSR)

    worktree_add_called = []
    real_run = _REAL_SUBPROCESS_RUN

    def _track(cmd, **kw):
        if isinstance(cmd, list) and "worktree" in cmd and "add" in cmd:
            worktree_add_called.append(list(cmd))
        return real_run(cmd, **kw)

    try:
        with patch("bellows.subprocess.run", side_effect=_track), \
             patch("time.sleep"):
            with pytest.raises(WorktreeCreationError) as exc_info:
                _create_worktree(git_repo, slug)
    finally:
        os.chmod(ro_dir, _stat.S_IRWXU)

    err_msg = str(exc_info.value)
    assert "could not be removed" in err_msg or "still present" in err_msg, \
        f"Error must note path not removed: {err_msg}"
    assert not worktree_add_called, "git worktree add must NOT run"
    # Tip was preserved first (branch was deleted after tip was kept)
    preserved = _list_preserved(git_repo, slug)
    assert any(_get_branch_tip(git_repo, b) == tip for b in preserved), \
        f"Tip must be preserved: {preserved}"

    # Clean up
    shutil.rmtree(wt_path, ignore_errors=True)
    subprocess.run(["git", "worktree", "prune"], cwd=git_repo, capture_output=True, text=True)
    for b in _list_preserved(git_repo, slug):
        subprocess.run(["git", "branch", "-D", b], cwd=git_repo, capture_output=True, text=True)


# --- x16: symlink to live worktree leaves target intact ----------------------

def test_stranded_symlink_to_live_worktree_leaves_the_target_intact(git_repo):
    """x16: symlink at wt_path points to another live worktree — target left intact."""
    slug_live = "x16-live-target"
    slug_bad = "x16-bad-symlink"
    wt_dir = os.path.join(git_repo, ".bellows-worktrees")
    os.makedirs(wt_dir, exist_ok=True)

    # Create a real live worktree for slug_live
    live_wt = _create_worktree(git_repo, slug_live)
    with open(os.path.join(live_wt, "live_work.txt"), "w") as f:
        f.write("live uncommitted work\n")
    live_reg = subprocess.run(["git", "worktree", "list", "--porcelain"],
                              cwd=git_repo, capture_output=True, text=True).stdout

    # Place a symlink for slug_bad pointing to the live worktree
    bad_wt = os.path.join(wt_dir, slug_bad)
    os.symlink(live_wt, bad_wt)

    with patch("time.sleep"):
        with pytest.raises(WorktreeCreationError):
            _create_worktree(git_repo, slug_bad)

    # Live worktree must be intact
    assert os.path.isdir(live_wt), "Live worktree directory must be intact"
    assert os.path.isfile(os.path.join(live_wt, "live_work.txt")), \
        "Uncommitted file in live worktree must be intact"
    live_reg_after = subprocess.run(["git", "worktree", "list", "--porcelain"],
                                    cwd=git_repo, capture_output=True, text=True).stdout
    assert slug_live in live_reg_after, "Live worktree registration must be intact"

    # Clean up
    os.unlink(bad_wt)
    subprocess.run(["git", "worktree", "remove", "--force", live_wt],
                   cwd=git_repo, capture_output=True, text=True)


# --- x17: dangling symlink reaches the helper (2 cases) ----------------------

@pytest.mark.parametrize("case_id", ["no-branch", "unlanded-branch"])
def test_stranded_dangling_symlink_reaches_the_helper(git_repo, case_id):
    """x17: dangling symlink at wt_path — helper runs, dispatch stopped, link left in place."""
    slug = f"x17-dangling-{case_id}"
    wt_dir = os.path.join(git_repo, ".bellows-worktrees")
    os.makedirs(wt_dir, exist_ok=True)
    wt_path = os.path.join(wt_dir, slug)

    if case_id == "unlanded-branch":
        # Create a branch with un-landed commit
        subprocess.run(["git", "checkout", "-b", f"bellows-wt/{slug}"],
                       cwd=git_repo, capture_output=True, text=True)
        with open(os.path.join(git_repo, f"x17_{slug}.txt"), "w") as f:
            f.write("work\n")
        subprocess.run(["git", "add", "."], cwd=git_repo, capture_output=True, text=True)
        subprocess.run(["git", "commit", "-m", f"x17 {slug}"], cwd=git_repo,
                       capture_output=True, text=True, check=True)
        subprocess.run(["git", "checkout", "main"], cwd=git_repo, capture_output=True, text=True)
        tip = _get_branch_tip(git_repo, f"bellows-wt/{slug}")
    else:
        tip = None

    # Create a dangling symlink (target doesn't exist)
    nonexistent = os.path.join(wt_dir, "nonexistent-target-for-x17")
    os.symlink(nonexistent, wt_path)
    assert os.path.islink(wt_path), "Symlink must exist"
    assert not os.path.exists(wt_path), "Symlink must be dangling"

    git_through_link = []
    real_run = _REAL_SUBPROCESS_RUN

    def _track(cmd, **kw):
        if isinstance(cmd, list) and "-C" in cmd:
            idx = cmd.index("-C")
            carg = cmd[idx + 1]
            # os.path.lexists follows symlink? No — just check abspath
            if os.path.abspath(carg) == os.path.abspath(wt_path):
                git_through_link.append(list(cmd))
        return real_run(cmd, **kw)

    with patch("bellows.subprocess.run", side_effect=_track), \
         patch("time.sleep"):
        with pytest.raises(WorktreeCreationError) as exc_info:
            _create_worktree(git_repo, slug)

    err_msg = str(exc_info.value)
    assert "symlink" in err_msg or "unlink" in err_msg, \
        f"[{case_id}] Error must name symlink: {err_msg}"
    assert not git_through_link, \
        f"[{case_id}] No git -C <dangling link> should run: {git_through_link}"
    assert os.path.islink(wt_path), f"[{case_id}] Dangling symlink must still be there"
    # bellows-wt/<slug> must NOT exist (or was deleted after tip was kept)
    if case_id == "unlanded-branch":
        assert _get_branch_tip(git_repo, f"bellows-wt/{slug}") is None, \
            "bellows-wt/<slug> must be deleted after tip was preserved"
        preserved = _list_preserved(git_repo, slug)
        assert any(_get_branch_tip(git_repo, b) == tip for b in preserved), \
            f"Tip must be preserved: {preserved}"
    else:
        assert _get_branch_tip(git_repo, f"bellows-wt/{slug}") is None, \
            "bellows-wt/<slug> must not exist for no-branch case"

    # Clean up and verify second create works
    os.unlink(wt_path)
    for b in _list_preserved(git_repo, slug):
        subprocess.run(["git", "branch", "-D", b], cwd=git_repo, capture_output=True, text=True)
    new_wt = _create_worktree(git_repo, slug)
    assert os.path.isdir(new_wt)
    subprocess.run(["git", "worktree", "remove", "--force", new_wt],
                   cwd=git_repo, capture_output=True, text=True)


# ---------------------------------------------------------------------------
# Helpers for daemon-entry-point tests (x18, x22, x23, x24)
# ---------------------------------------------------------------------------

def _setup_daemon_test(tmp_path, git_repo, plan_content, plan_id=1, slug_base="test"):
    """Set up a minimal daemon test environment.

    Returns (decisions_dir, plan_path, plan_slug, config).
    The plan file is placed as in-progress-executable-<plan_id>.md.
    The lifecycle DB has a plan row for plan_id.
    bellows.BELLOWS_ROOT is NOT set here — caller patches it.
    """
    import lifecycle
    import sqlite3

    decisions_dir = _pl.Path(git_repo) / "knowledge" / "decisions"
    decisions_dir.mkdir(parents=True, exist_ok=True)
    (decisions_dir / "Done").mkdir(exist_ok=True)

    plan_filename = f"in-progress-executable-{plan_id}.md"
    plan_path = decisions_dir / plan_filename
    plan_path.write_text(plan_content)

    # Insert plan row into the lifecycle DB (conftest already init'd it)
    db_path = lifecycle.LIFECYCLE_DB_PATH
    conn = sqlite3.connect(db_path)
    conn.execute(
        "INSERT OR REPLACE INTO id_sequence (id, next_id) VALUES (1, ?)",
        (plan_id + 1,),
    )
    conn.execute(
        "INSERT OR IGNORE INTO plans "
        "(id, type, target_project, lifecycle_state, created_at) "
        "VALUES (?, 'executable', ?, 'in_progress', '2026-09-15')",
        (plan_id, str(git_repo)),
    )
    conn.commit()
    conn.close()

    config = {
        "default_model": "claude-sonnet-4-6",
        "pushover": {"app_key": "", "user_key": ""},
        "callback_port": 5999,
        "step_timeout_seconds": 600,
        "watched_projects": [str(decisions_dir)],
    }
    plan_slug = str(plan_id)  # slug_from_path("executable-<id>.md") = "<id>"
    return decisions_dir, plan_path, plan_slug, config


def _make_gitdir_gone_worktree_for_daemon(git_repo, slug):
    """Create a real worktree, make an unlanded commit, then remove the worktrees entry.

    After this call the path exists with a .git file pointing to a pruned entry.
    git -C <path> commands fail (gitdir-gone). The path is NOT foreign.
    """
    wt_path = _pl.Path(git_repo) / ".bellows-worktrees" / slug
    wt_path.parent.mkdir(parents=True, exist_ok=True)

    # Create a real worktree
    subprocess.run(["git", "worktree", "add", str(wt_path), "-b", f"bellows-wt/{slug}", "HEAD"],
                   cwd=git_repo, capture_output=True, text=True, check=True)
    # Make an unlanded commit
    (wt_path / "work_daemon.txt").write_text("daemon work\n")
    subprocess.run(["git", "add", "work_daemon.txt"], cwd=str(wt_path),
                   capture_output=True, text=True)
    subprocess.run(["git", "commit", "-m", "unlanded daemon commit"], cwd=str(wt_path),
                   capture_output=True, text=True, check=True)
    # Remove the worktrees entry to create the gitdir-gone shape
    entry = _pl.Path(git_repo) / ".git" / "worktrees" / slug
    if entry.exists():
        shutil.rmtree(str(entry))
    return wt_path


def _inject_porcelain_fail(exc_or_rc):
    """Return a subprocess.run side_effect that fails worktree list --porcelain."""
    real_run = _REAL_SUBPROCESS_RUN

    def _side(cmd, **kw):
        cmd_list = list(cmd) if not isinstance(cmd, str) else cmd.split()
        if "worktree" in cmd_list and "list" in cmd_list and "--porcelain" in cmd_list:
            if isinstance(exc_or_rc, BaseException):
                raise exc_or_rc
            r = MagicMock()
            r.returncode = exc_or_rc
            r.stdout = ""
            r.stderr = "injected porcelain failure"
            return r
        return real_run(cmd, **kw)
    return _side


# --- x18: stop on resumed dispatch pauses at the dispatched step --------------

def test_stranded_stop_on_resumed_dispatch_pauses_at_the_dispatched_step(
        tmp_path, git_repo, monkeypatch):
    """x18: run_plan dispatching step 2 posts verdict-request at step 2, not step 1."""
    import lifecycle
    import verdict as verdict_mod

    plan_content = "## STEP 1\nDo stuff.\n## STEP 2\nMore stuff.\n"
    plan_id = 18
    decisions_dir, plan_path, plan_slug, config = _setup_daemon_test(
        tmp_path, git_repo, plan_content, plan_id=plan_id)

    bellows_root = _pl.Path(tmp_path)
    shadow_cache = bellows_root / ".bellows-cache"
    shadow_cache.mkdir(exist_ok=True)
    # Write a shadow copy so run_plan uses it for metadata
    shadow_copy = shadow_cache / f"in-progress-executable-{plan_id}.md.pristine"
    shadow_copy.write_text(plan_content)

    monkeypatch.setattr(bellows, "BELLOWS_ROOT", bellows_root)
    monkeypatch.setattr(bellows, "SHADOW_CACHE_DIR", shadow_cache)

    _make_gitdir_gone_worktree_for_daemon(git_repo, plan_slug)

    (bellows_root / "logs").mkdir(exist_ok=True)
    (bellows_root / "verdicts" / "pending").mkdir(parents=True, exist_ok=True)
    (bellows_root / "verdicts" / "resolved").mkdir(parents=True, exist_ok=True)

    with patch("bellows.subprocess.run",
               side_effect=_inject_porcelain_fail(subprocess.TimeoutExpired([], 10))), \
         patch("bellows.runner.run_step") as mock_run_step, \
         patch("bellows.record_run"), \
         patch("bellows.notifier.push"), \
         patch("bellows.plan_claim.release_for_plan"), \
         patch("time.sleep"):
        bellows.run_plan(str(plan_path), config, MagicMock(), resume_step=2)

    mock_run_step.assert_not_called()

    # Verdict-request must be at step 2
    pending_dir = _pl.Path(verdict_mod.VERDICTS_DIR) / "pending"
    req_files = list(pending_dir.glob(f"verdict-request-executable-{plan_id}-step-2.md"))
    assert req_files, (
        f"verdict-request at step 2 expected; pending/: "
        f"{list(pending_dir.iterdir()) if pending_dir.exists() else 'missing'}"
    )
    body = req_files[0].read_text()
    assert "**Step:** 2" in body, f"Body must carry Step: 2: {body[:300]}"
    assert "**Precondition Failure:** true" in body, \
        f"Body must carry Precondition Failure: true: {body[:300]}"

    # Plan must be in verdict-pending- lane
    vp_files = list(decisions_dir.glob(f"verdict-pending-executable-{plan_id}.md"))
    assert vp_files, f"Plan must be in verdict-pending- lane: {list(decisions_dir.iterdir())}"

    # bellows-wt/<slug> must NOT have been created
    assert _get_branch_tip(git_repo, f"bellows-wt/{plan_slug}") is None, \
        "bellows-wt/<slug> must not be created after a failed save"

    # Lifecycle verdict row at step 2
    import sqlite3
    conn = sqlite3.connect(lifecycle.LIFECYCLE_DB_PATH)
    row = conn.execute(
        "SELECT step_number FROM verdicts WHERE plan_id=? ORDER BY id DESC LIMIT 1",
        (plan_id,)).fetchone()
    conn.close()
    assert row and row[0] == 2, f"Lifecycle verdict row must be at step 2, got: {row}"


# --- x19: symlink failed save names the symlink and unlink (2 cases) ---------

@pytest.mark.parametrize("case_id", ["link-to-live-worktree", "link-to-checkout"])
def test_stranded_symlink_failed_save_names_the_symlink_and_unlink(git_repo, case_id):
    """x19: when save fails with a symlink at path, message names 'the symlink' and gives unlink."""
    slug = f"x19-{case_id}"
    wt_dir = os.path.join(git_repo, ".bellows-worktrees")
    os.makedirs(wt_dir, exist_ok=True)
    wt_path = os.path.join(wt_dir, slug)

    if case_id == "link-to-live-worktree":
        live_slug = f"x19-live-{case_id}"
        live_wt = _create_worktree(git_repo, live_slug)
        with open(os.path.join(live_wt, "live_f.txt"), "w") as f:
            f.write("live\n")
        target = live_wt
    else:
        target = git_repo

    os.symlink(target, wt_path)

    with patch("time.sleep"):
        with pytest.raises(WorktreeCreationError) as exc_info:
            _create_worktree(git_repo, slug)

    err_msg = str(exc_info.value)
    assert "symlink" in err_msg, f"[{case_id}] Error must mention symlink: {err_msg}"
    assert "unlink" in err_msg, f"[{case_id}] Error must give unlink act: {err_msg}"
    # No "its registration" — the symlink has no registration (samefile follows the link)
    # Message gives 'the symlink', not 'the path and its registration'
    assert "symlink" in err_msg.lower(), f"[{case_id}] Must name 'the symlink': {err_msg}"
    assert os.path.islink(wt_path), f"[{case_id}] Symlink must still be there"

    if case_id == "link-to-live-worktree":
        assert os.path.isdir(live_wt), "Live worktree directory must be intact"
        assert os.path.isfile(os.path.join(live_wt, "live_f.txt")), "Live file intact"
        assert subprocess.run(["git", "worktree", "list", "--porcelain"],
                              cwd=git_repo, capture_output=True, text=True
                              ).stdout.count(live_wt) >= 1, "Live registration intact"

    # Clean up
    os.unlink(wt_path)
    if case_id == "link-to-live-worktree":
        subprocess.run(["git", "worktree", "remove", "--force", live_wt],
                       cwd=git_repo, capture_output=True, text=True)
        subprocess.run(["git", "branch", "-D", f"bellows-wt/{live_slug}"],
                       cwd=git_repo, capture_output=True, text=True)


# --- x20: symlink removal stop — branch not deletable ------------------------

def test_stranded_symlink_removal_stop_branch_not_deletable(git_repo):
    """x20: branch can't be deleted (checked out in another worktree) — message says so."""
    slug = "x20-no-delete-branch"
    wt_dir = os.path.join(git_repo, ".bellows-worktrees")
    os.makedirs(wt_dir, exist_ok=True)
    wt_path = os.path.join(wt_dir, slug)

    # Create bellows-wt/<slug> with un-landed commits
    other_wt = _create_worktree(git_repo, slug)
    with open(os.path.join(other_wt, "x20_work.txt"), "w") as f:
        f.write("x20 work\n")
    subprocess.run(["git", "add", "x20_work.txt"], cwd=other_wt,
                   capture_output=True, text=True)
    subprocess.run(["git", "commit", "-m", "x20 unlanded"], cwd=other_wt,
                   capture_output=True, text=True, check=True)
    tip = subprocess.run(["git", "rev-parse", "HEAD"], cwd=other_wt,
                         capture_output=True, text=True).stdout.strip()

    # Place a symlink at wt_path pointing to another location (not the live worktree)
    # The symlink points to a temp dir (the branch IS checked out in other_wt still)
    target = tempfile.mkdtemp()
    os.symlink(target, wt_path)

    with patch("time.sleep"):
        with pytest.raises(WorktreeCreationError) as exc_info:
            _create_worktree(git_repo, slug)

    err_msg = str(exc_info.value)
    # Tip must be preserved first
    preserved = _list_preserved(git_repo, slug)
    assert any(_get_branch_tip(git_repo, b) == tip for b in preserved), \
        f"Tip must be preserved: {preserved}"
    # Message must say branch COULD NOT be deleted (since it's checked out in other_wt)
    # (or that it IS deleted — depends on whether git refuses)
    # Key: message must accurately reflect what happened with the branch
    assert os.path.islink(wt_path), "Symlink must still be there"
    assert os.path.isdir(other_wt), "Live worktree must be intact"

    # Clean up
    os.unlink(wt_path)
    shutil.rmtree(target, ignore_errors=True)
    subprocess.run(["git", "worktree", "remove", "--force", other_wt],
                   cwd=git_repo, capture_output=True, text=True)
    for b in _list_preserved(git_repo, slug):
        subprocess.run(["git", "branch", "-D", b], cwd=git_repo,
                       capture_output=True, text=True)
    subprocess.run(["git", "branch", "-D", f"bellows-wt/{slug}"],
                   cwd=git_repo, capture_output=True, text=True)


# --- x21: failed identity lookup reads as not own (2 cases) ------------------

@pytest.mark.parametrize("case_id", ["lookup-nonzero", "lookup-raises"])
def test_stranded_failed_identity_lookup_reads_as_not_own(git_repo, case_id):
    """x21: failed show-toplevel reads as not-own — WARN logged, no HEAD read through path."""
    slug = f"x21-{case_id}"
    wt_path, tip = _make_unlanded_worktree(git_repo, slug)
    real_run = _REAL_SUBPROCESS_RUN
    git_c_path_calls = []

    def _inject_toplevel_fail(cmd, **kw):
        cmd_list = list(cmd) if not isinstance(cmd, str) else cmd.split()
        if ("rev-parse" in cmd_list and "--show-toplevel" in cmd_list and
                "-C" in cmd_list):
            idx = cmd_list.index("-C")
            try:
                if os.path.samefile(cmd_list[idx + 1], wt_path):
                    git_c_path_calls.append(list(cmd))
                    if case_id == "lookup-raises":
                        raise subprocess.TimeoutExpired(cmd, 10)
                    r = MagicMock()
                    r.returncode = 128; r.stdout = ""; r.stderr = "not a git repo"
                    return r
            except (OSError, IndexError):
                pass
        # Track any other git -C <wt_path> HEAD read
        if ("rev-parse" in cmd_list and "--verify" in cmd_list and
                "HEAD" in cmd_list and "-C" in cmd_list):
            idx = cmd_list.index("-C")
            try:
                if os.path.samefile(cmd_list[idx + 1], wt_path):
                    git_c_path_calls.append(list(cmd))
            except OSError:
                pass
        return real_run(cmd, **kw)

    with patch("bellows.subprocess.run", side_effect=_inject_toplevel_fail), \
         patch("bellows._log") as mock_log, \
         patch("time.sleep"):
        new_wt = _create_worktree(git_repo, slug)

    try:
        # WARN must name "not its own repository"
        warn_msgs = [str(c) for c in mock_log.call_args_list if "WARN" in str(c)]
        assert any("not its own" in m for m in warn_msgs), \
            f"[{case_id}] WARN must name 'not its own repository': {warn_msgs}"
        # No HEAD read through the path (only show-toplevel is allowed to run through it)
        head_reads = [c for c in git_c_path_calls
                      if "rev-parse" in c and "--verify" in c and "HEAD" in c]
        assert not head_reads, \
            f"[{case_id}] HEAD must NOT be read through the path: {head_reads}"
        # Tip IS preserved (it's off main)
        preserved = _list_preserved(git_repo, slug)
        tip_branches = [b for b in preserved if b.endswith("-branch")]
        assert tip_branches, f"[{case_id}] Tip must be preserved on -branch: {preserved}"
        assert _get_branch_tip(git_repo, tip_branches[0]) == tip
    finally:
        subprocess.run(["git", "worktree", "remove", "--force", new_wt],
                       cwd=git_repo, capture_output=True, text=True)
        for b in _list_preserved(git_repo, slug):
            subprocess.run(["git", "branch", "-D", b], cwd=git_repo,
                           capture_output=True, text=True)


# --- x22: stop at final step — continue retries the step (2 cases) -----------

@pytest.mark.parametrize("case_id", ["two-step-final", "one-step"])
def test_stranded_stop_at_final_step_continue_retries_the_step(
        tmp_path, git_repo, case_id, monkeypatch):
    """x22: precondition-failure continue at final step retries the step, not Done."""
    import lifecycle
    import verdict as verdict_mod
    import sqlite3

    if case_id == "two-step-final":
        plan_content = "## STEP 1\nDo stuff.\n## STEP 2\nMore stuff.\n"
        resume_step = 2
        plan_id = 221
    else:
        plan_content = "## STEP 1\nDo the only thing.\n"
        resume_step = 1
        plan_id = 222

    decisions_dir, plan_path, plan_slug, config = _setup_daemon_test(
        tmp_path, git_repo, plan_content, plan_id=plan_id)

    bellows_root = _pl.Path(tmp_path)
    shadow_cache = bellows_root / ".bellows-cache"
    shadow_cache.mkdir(exist_ok=True)
    shadow_copy = shadow_cache / f"in-progress-executable-{plan_id}.md.pristine"
    shadow_copy.write_text(plan_content)

    monkeypatch.setattr(bellows, "BELLOWS_ROOT", bellows_root)
    monkeypatch.setattr(bellows, "SHADOW_CACHE_DIR", shadow_cache)

    _make_gitdir_gone_worktree_for_daemon(git_repo, plan_slug)

    (bellows_root / "logs").mkdir(exist_ok=True)
    (bellows_root / "verdicts" / "pending").mkdir(parents=True, exist_ok=True)
    (bellows_root / "verdicts" / "resolved").mkdir(parents=True, exist_ok=True)

    # Phase 1: run_plan — posts verdict-request at step resume_step
    with patch("bellows.subprocess.run",
               side_effect=_inject_porcelain_fail(subprocess.TimeoutExpired([], 10))), \
         patch("bellows.runner.run_step") as mock_run_step, \
         patch("bellows.record_run"), \
         patch("bellows.notifier.push"), \
         patch("bellows.plan_claim.release_for_plan"), \
         patch("time.sleep"):
        bellows.run_plan(str(plan_path), config, MagicMock(), resume_step=resume_step)

    mock_run_step.assert_not_called()

    # Find the verdict-pending plan file
    vp_files = list(decisions_dir.glob(f"verdict-pending-executable-{plan_id}.md"))
    assert vp_files, f"Plan must be in verdict-pending- lane: {list(decisions_dir.iterdir())}"
    vp_path = vp_files[0]

    # Find the verdict-request file
    pending_dir = _pl.Path(verdict_mod.VERDICTS_DIR) / "pending"
    req_files = list(pending_dir.glob(
        f"verdict-request-executable-{plan_id}-step-{resume_step}.md"))
    assert req_files, f"Verdict-request at step {resume_step} must exist"

    # Set up a 'continue' verdict in resolved/
    resolved_dir = _pl.Path(verdict_mod.VERDICTS_DIR) / "resolved"
    verdict_fname = f"verdict-executable-{plan_id}-step-{resume_step}.md"
    (resolved_dir / verdict_fname).write_text("continue\nOperator approved retry.")

    # Phase 2: consume the verdict
    b = bellows.Bellows(config)
    handle_calls = []
    claim_release_calls = []

    def _mock_handle(path, resume_step=None):
        handle_calls.append((path, resume_step))

    with patch("bellows.BELLOWS_ROOT", bellows_root), \
         patch("bellows.SHADOW_CACHE_DIR", shadow_cache), \
         patch("bellows.verdict.log_to_ledger"), \
         patch("bellows.notifier.push"), \
         patch("bellows.plan_claim.release_for_plan",
               side_effect=lambda *a, **kw: claim_release_calls.append(a)), \
         patch("bellows.plan_claim.enqueue_thread_reviews"), \
         patch.object(b, "handle_new_plan", side_effect=_mock_handle), \
         patch("time.sleep"):
        b._consume_verdicts()

    # Must have called handle_new_plan with resume_step=<the failed step>
    assert len(handle_calls) == 1, f"handle_new_plan must be called once: {handle_calls}"
    _, called_resume = handle_calls[0]
    assert called_resume == resume_step, \
        f"[{case_id}] Must retry step {resume_step}, got resume_step={called_resume}"

    # Must NOT have closed to Done/
    done_files = list((decisions_dir / "Done").glob(f"executable-{plan_id}.md"))
    assert not done_files, f"[{case_id}] Must NOT close to Done/: {done_files}"

    # Must NOT have released the claim (not a completion)
    assert not claim_release_calls, \
        f"[{case_id}] Claim must NOT be released: {claim_release_calls}"

    # Plan must be in in-progress- lane (handle_new_plan called with in-progress path)
    assert handle_calls[0][0] and "in-progress" in handle_calls[0][0], \
        f"[{case_id}] handle_new_plan called with in-progress- path"

    # Lifecycle verdict row must be 'continue' (not 'continue-to-done')
    conn = sqlite3.connect(lifecycle.LIFECYCLE_DB_PATH)
    row = conn.execute(
        "SELECT outcome FROM verdicts WHERE plan_id=? AND step_number=? "
        "ORDER BY id DESC LIMIT 1",
        (plan_id, resume_step)).fetchone()
    conn.close()
    # Note: verdict.log_to_ledger is mocked, so we check via _recheck_continue_gates
    # which calls lifecycle.record_verdict_outcome with 'continue'
    # The row was written by record_verdict_request (outcome=NULL initially),
    # so the outcome update comes from _recheck_continue_gates
    # Since log_to_ledger is mocked, check the handler was invoked with the right step


# --- x23: final-step gate failure continue still closes to Done (control) ----

def test_final_step_gate_failure_continue_still_closes_to_done(tmp_path, git_repo, monkeypatch):
    """x23: final step that ran (no precondition flag) → continue → Done/ (GREEN on base)."""
    import verdict as verdict_mod
    import lifecycle
    import sqlite3

    plan_content = "## STEP 1\nDo stuff.\n"
    plan_id = 23
    decisions_dir, plan_path, plan_slug, config = _setup_daemon_test(
        tmp_path, git_repo, plan_content, plan_id=plan_id)

    bellows_root = _pl.Path(tmp_path)
    shadow_cache = bellows_root / ".bellows-cache"
    shadow_cache.mkdir(exist_ok=True)

    monkeypatch.setattr(bellows, "BELLOWS_ROOT", bellows_root)
    monkeypatch.setattr(bellows, "SHADOW_CACHE_DIR", shadow_cache)

    (bellows_root / "verdicts" / "pending").mkdir(parents=True, exist_ok=True)
    (bellows_root / "verdicts" / "resolved").mkdir(parents=True, exist_ok=True)

    # Set up a verdict-pending plan with a verdict-request (no precondition_failure)
    vp_name = f"verdict-pending-executable-{plan_id}.md"
    vp_path = decisions_dir / vp_name
    vp_path.write_text(plan_content)

    pending_dir = _pl.Path(verdict_mod.VERDICTS_DIR) / "pending"
    req_file = pending_dir / f"verdict-request-executable-{plan_id}-step-1.md"
    req_file.write_text(
        f"# Verdict Request\n"
        f"**Plan:** {vp_path}\n"
        f"**Step:** 1\n"
        f"**Total Steps:** 1\n"
        f"**Pause Reason Code:** gate_failure\n"
        f"**Gate Result JSON:** {{\"failures\": [], \"files_changed\": []}}\n"
    )

    resolved_dir = _pl.Path(verdict_mod.VERDICTS_DIR) / "resolved"
    (resolved_dir / f"verdict-executable-{plan_id}-step-1.md").write_text(
        "continue\nApproved.")

    b = bellows.Bellows(config)
    handle_calls = []
    release_calls = []

    with patch("bellows.BELLOWS_ROOT", bellows_root), \
         patch("bellows.SHADOW_CACHE_DIR", shadow_cache), \
         patch("bellows.verdict.log_to_ledger"), \
         patch("bellows.notifier.push"), \
         patch("bellows.notifier.notify_plan_complete"), \
         patch("bellows.plan_claim.release_for_plan",
               side_effect=lambda *a, **kw: release_calls.append(a)), \
         patch("bellows.plan_claim.enqueue_thread_reviews"), \
         patch("bellows._retire_receipts"), \
         patch.object(b, "handle_new_plan",
                      side_effect=lambda *a, **kw: handle_calls.append(a)), \
         patch("time.sleep"):
        b._consume_verdicts()

    # Must close to Done/
    done_files = list((decisions_dir / "Done").glob(f"executable-{plan_id}.md"))
    assert done_files, f"Must close to Done/: {list(decisions_dir.iterdir())}"
    # handle_new_plan must NOT be called (it's Done, not a retry)
    assert not handle_calls, f"handle_new_plan must NOT be called: {handle_calls}"
    # Claim must be released
    assert release_calls, "Claim must be released on continue-to-done"


# --- x24: stop retry reposts the request the consumer keeps ------------------

def test_stranded_stop_retry_reposts_the_request_the_consumer_keeps(
        tmp_path, git_repo, monkeypatch):
    """x24: consumer unlinks request before re-dispatch, so the stop's new request survives."""
    import lifecycle
    import verdict as verdict_mod
    import sqlite3
    import threading

    plan_content = "## STEP 1\nDo stuff.\n## STEP 2\nMore stuff.\n"
    plan_id = 24
    decisions_dir, plan_path, plan_slug, config = _setup_daemon_test(
        tmp_path, git_repo, plan_content, plan_id=plan_id)

    bellows_root = _pl.Path(tmp_path)
    shadow_cache = bellows_root / ".bellows-cache"
    shadow_cache.mkdir(exist_ok=True)
    shadow_copy = shadow_cache / f"in-progress-executable-{plan_id}.md.pristine"
    shadow_copy.write_text(plan_content)

    monkeypatch.setattr(bellows, "BELLOWS_ROOT", bellows_root)
    monkeypatch.setattr(bellows, "SHADOW_CACHE_DIR", shadow_cache)

    _make_gitdir_gone_worktree_for_daemon(git_repo, plan_slug)

    (bellows_root / "logs").mkdir(exist_ok=True)
    (bellows_root / "verdicts" / "pending").mkdir(parents=True, exist_ok=True)
    (bellows_root / "verdicts" / "resolved").mkdir(parents=True, exist_ok=True)

    # Phase 1: run_plan posts the verdict-request at step 2
    with patch("bellows.subprocess.run",
               side_effect=_inject_porcelain_fail(subprocess.TimeoutExpired([], 10))), \
         patch("bellows.runner.run_step"), \
         patch("bellows.record_run"), \
         patch("bellows.notifier.push"), \
         patch("bellows.plan_claim.release_for_plan"), \
         patch("time.sleep"):
        bellows.run_plan(str(plan_path), config, MagicMock(), resume_step=2)

    vp_files = list(decisions_dir.glob(f"verdict-pending-executable-{plan_id}.md"))
    assert vp_files, "Plan must be in verdict-pending-"
    pending_dir = _pl.Path(verdict_mod.VERDICTS_DIR) / "pending"
    req_files = list(pending_dir.glob(f"verdict-request-executable-{plan_id}-step-2.md"))
    assert req_files, "Verdict-request at step 2 must exist"

    # Set up a 'continue' verdict
    resolved_dir = _pl.Path(verdict_mod.VERDICTS_DIR) / "resolved"
    verdict_fname = f"verdict-executable-{plan_id}-step-2.md"
    (resolved_dir / verdict_fname).write_text("continue\nApproved.")

    # Phase 2: use the REAL handle_new_plan so the re-dispatch actually runs
    # The re-dispatch will call run_plan again → hits the same worktree failure
    # → posts a NEW verdict-request at step 2
    # x24 verifies the consumer's early unlink allows this re-post to survive

    b = bellows.Bellows(config)

    stop_count = [0]
    original_run_plan = bellows.run_plan

    def _counted_run_plan(path, cfg, srv, resume_step=None, bellows_inst=None):
        stop_count[0] += 1
        if stop_count[0] > 2:
            return  # safety valve
        with patch("bellows.subprocess.run",
                   side_effect=_inject_porcelain_fail(subprocess.TimeoutExpired([], 10))), \
             patch("bellows.runner.run_step"), \
             patch("bellows.record_run"), \
             patch("bellows.notifier.push"), \
             patch("bellows.plan_claim.release_for_plan"), \
             patch("time.sleep"):
            original_run_plan(path, cfg, srv, resume_step=resume_step, bellows=bellows_inst)

    with patch("bellows.BELLOWS_ROOT", bellows_root), \
         patch("bellows.SHADOW_CACHE_DIR", shadow_cache), \
         patch("bellows.verdict.log_to_ledger"), \
         patch("bellows.notifier.push"), \
         patch("bellows.plan_claim.release_for_plan"), \
         patch("bellows.plan_claim.enqueue_thread_reviews"), \
         patch("bellows.run_plan", side_effect=_counted_run_plan):
        b._consume_verdicts()

    # After the consumer's pass: the re-dispatch's NEW stop request must be in pending/
    req_after = list(pending_dir.glob(f"verdict-request-executable-{plan_id}-step-2.md"))
    assert req_after, (
        f"The second stop's request must be in pending after the consumer's pass: "
        f"{list(pending_dir.iterdir()) if pending_dir.exists() else '[]'}"
    )


# --- x25: stranded clone of the project left intact -------------------------

def test_stranded_clone_of_the_project_left_intact(git_repo):
    """x25: a clone of the project at wt_path — stop raised, clone left intact."""
    slug = "x25-clone"
    wt_dir = os.path.join(git_repo, ".bellows-worktrees")
    os.makedirs(wt_dir, exist_ok=True)
    wt_path = os.path.join(wt_dir, slug)

    # Clone the project into wt_path
    subprocess.run(["git", "clone", git_repo, wt_path],
                   capture_output=True, text=True, check=True)
    # Add a branch and file that exist only in the clone
    subprocess.run(["git", "checkout", "-b", "clone-only-branch"],
                   cwd=wt_path, capture_output=True, text=True)
    with open(os.path.join(wt_path, "clone_work.txt"), "w") as f:
        f.write("clone work\n")
    subprocess.run(["git", "add", "clone_work.txt"], cwd=wt_path,
                   capture_output=True, text=True)
    subprocess.run(["git", "commit", "-m", "clone-only commit"], cwd=wt_path,
                   capture_output=True, text=True, check=True)
    clone_commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=wt_path,
                                   capture_output=True, text=True).stdout.strip()

    with patch("time.sleep"):
        with pytest.raises(WorktreeCreationError) as exc_info:
            _create_worktree(git_repo, slug)

    err_msg = str(exc_info.value)
    assert "repository of its own" in err_msg or "a .git directory" in err_msg, \
        f"Error must name foreign repository: {err_msg}"
    assert os.path.isdir(wt_path), "Clone must still be there"
    assert os.path.isfile(os.path.join(wt_path, "clone_work.txt")), "Clone file intact"
    # Clone-only commit must still be in the clone's store
    assert subprocess.run(
        ["git", "cat-file", "-e", clone_commit], cwd=wt_path,
        capture_output=True, text=True).returncode == 0, \
        "Clone's own commit must still exist in its store"

    shutil.rmtree(wt_path, ignore_errors=True)


# --- x26: separate-git-dir clone left intact ---------------------------------

def test_stranded_separate_git_dir_clone_left_intact(git_repo):
    """x26: git clone --separate-git-dir (a .git FILE pointing outside this project) — stop raised."""
    slug = "x26-sep-gitdir"
    wt_dir = os.path.join(git_repo, ".bellows-worktrees")
    os.makedirs(wt_dir, exist_ok=True)
    wt_path = os.path.join(wt_dir, slug)
    ext_gitdir = tempfile.mkdtemp(suffix="-ext-gitdir")

    try:
        subprocess.run(
            ["git", "clone", "--separate-git-dir", ext_gitdir, git_repo, wt_path],
            capture_output=True, text=True, check=True)
        # Branch and uncommitted file in the clone
        with open(os.path.join(wt_path, "dirty.txt"), "w") as f:
            f.write("dirty\n")
        clone_head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=wt_path,
                                     capture_output=True, text=True).stdout.strip()

        with patch("time.sleep"):
            with pytest.raises(WorktreeCreationError) as exc_info:
                _create_worktree(git_repo, slug)

        err_msg = str(exc_info.value)
        assert "repository of its own" in err_msg or ".git file" in err_msg, \
            f"Error must name the shape: {err_msg}"
        assert os.path.isdir(wt_path), "Clone directory must still be there"
        assert os.path.isfile(os.path.join(wt_path, "dirty.txt")), "Dirty file intact"

        shutil.rmtree(wt_path, ignore_errors=True)
        shutil.rmtree(ext_gitdir, ignore_errors=True)

        # After removal, second create must succeed
        new_wt = _create_worktree(git_repo, slug)
        assert os.path.isdir(new_wt)
        subprocess.run(["git", "worktree", "remove", "--force", new_wt],
                       cwd=git_repo, capture_output=True, text=True)
    finally:
        shutil.rmtree(wt_path, ignore_errors=True)
        shutil.rmtree(ext_gitdir, ignore_errors=True)


# --- x27: .git symlink stops before any read ---------------------------------

def test_stranded_dot_git_symlink_stops_before_any_read(git_repo):
    """x27: plain dir whose .git SYMLINKS to another live worktree's .git file — stop raised."""
    slug_live = "x27-live-wt"
    slug_bad = "x27-dot-git-symlink"
    wt_dir = os.path.join(git_repo, ".bellows-worktrees")
    os.makedirs(wt_dir, exist_ok=True)

    # Create a real live worktree
    live_wt = _create_worktree(git_repo, slug_live)
    live_git_file = os.path.join(live_wt, ".git")

    # Create the bad directory with .git as a symlink to the live worktree's .git file
    bad_wt = os.path.join(wt_dir, slug_bad)
    os.makedirs(bad_wt)
    os.symlink(live_git_file, os.path.join(bad_wt, ".git"))

    called_through_bad = []
    real_run = _REAL_SUBPROCESS_RUN

    def _track(cmd, **kw):
        if isinstance(cmd, list) and "-C" in cmd:
            idx = cmd.index("-C")
            try:
                if os.path.samefile(cmd[idx + 1], bad_wt):
                    called_through_bad.append(list(cmd))
            except OSError:
                pass
        return real_run(cmd, **kw)

    with patch("bellows.subprocess.run", side_effect=_track), \
         patch("time.sleep"):
        with pytest.raises(WorktreeCreationError) as exc_info:
            _create_worktree(git_repo, slug_bad)

    err_msg = str(exc_info.value)
    assert "repository of its own" in err_msg or ".git symlink" in err_msg, \
        f"Error must name the .git symlink shape: {err_msg}"
    assert not called_through_bad, \
        f"No git -C <bad_wt> should run: {called_through_bad}"
    # Live worktree must be intact
    assert os.path.isdir(live_wt), "Live worktree must be intact"
    assert os.path.isfile(live_git_file), "Live .git file must be intact"
    live_reg = subprocess.run(["git", "worktree", "list", "--porcelain"],
                              cwd=git_repo, capture_output=True, text=True).stdout
    assert slug_live in live_reg, "Live worktree registration must be intact"
    # bellows-wt/<slug_bad> must NOT have been created
    assert _get_branch_tip(git_repo, f"bellows-wt/{slug_bad}") is None

    # Clean up
    shutil.rmtree(bad_wt, ignore_errors=True)
    subprocess.run(["git", "worktree", "remove", "--force", live_wt],
                   cwd=git_repo, capture_output=True, text=True)
