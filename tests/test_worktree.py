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
