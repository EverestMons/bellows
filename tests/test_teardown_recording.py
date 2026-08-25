"""Tests for teardown failure recording, dirty-tree precheck, Gap-1c retry,
and override refusal (plan 523, A10)."""

import json
import os
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

import bellows
import lifecycle
from bellows import WorktreeTeardownError, _teardown_worktree
from tests.conftest import clear_plan_for_test


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_fake_run_step_result():
    return {
        "session_id": "test-session",
        "is_error": False,
        "stop_reason": "end_turn",
        "result_text": "",
        "cost_usd": 0.01,
        "permission_denials": [],
        "receipt_status": "Complete",
        "ceo_flags": [],
        "escalate": False,
    }


def _clean_gates(auto_close="false"):
    return {
        "passed": True,
        "failures": [],
        "is_qa_step": False,
        "files_changed": [],
        "plan_header": {"auto_close": auto_close, "pause_for_verdict": "always"},
        "verdict_requested": {"requested": False, "body": None},
    }


def _setup_plan(tmp, plan_text, plan_prefix="executable"):
    decisions_dir = os.path.join(tmp, "proj", "knowledge", "decisions")
    os.makedirs(decisions_dir)
    plan_filename = f"{plan_prefix}-teardown-rec.md"
    plan_path = os.path.join(decisions_dir, plan_filename)
    with open(plan_path, "w") as f:
        f.write(plan_text)
    clear_plan_for_test(plan_path)
    return decisions_dir, plan_path


def _run_plan_with_teardown_error(plan_text, error_msg="merge conflict", capture_log=None):
    """Run a plan where _teardown_worktree raises, return (mock_verdict, log_calls)."""
    with tempfile.TemporaryDirectory() as tmp:
        decisions_dir, plan_path = _setup_plan(tmp, plan_text)

        config = {
            "default_model": "claude-sonnet-4-6",
            "pushover": {"app_key": "", "user_key": ""},
            "callback_port": 5999,
            "step_timeout_seconds": 600,
        }

        log_calls = []
        original_log = bellows._log

        def _capture(level, msg, **kwargs):
            log_calls.append((level, msg))
            original_log(level, msg, **kwargs)

        with patch("bellows._create_worktree", return_value="/tmp/wt"), \
             patch("bellows._capture_git_diff", return_value=""), \
             patch("bellows._teardown_worktree",
                   side_effect=WorktreeTeardownError(error_msg)), \
             patch("bellows.runner.run_step", return_value=_make_fake_run_step_result()), \
             patch("bellows.gates.check", return_value=_clean_gates()), \
             patch("bellows.verdict.post_verdict_request", return_value="/tmp/vr.md") as mock_verdict, \
             patch("bellows.notifier.push"), \
             patch("bellows.notifier.notify_verdict_request"), \
             patch("bellows.record_run"), \
             patch("bellows._log", side_effect=_capture), \
             patch("bellows.validators.validate_at_claim",
                   return_value={"rejected": False, "reject_reason": "", "warnings": []}):
            response_server = MagicMock()
            bellows.run_plan(plan_path, config, response_server)

        return mock_verdict, log_calls, decisions_dir


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
        subprocess.run(
            ["git", "worktree", "prune"], cwd=tmp,
            capture_output=True, text=True,
        )
        shutil.rmtree(tmp, ignore_errors=True)


def _create_worktree(git_repo, slug):
    """Create a worktree with the bellows naming convention."""
    from bellows import _create_worktree as bw_create
    return bw_create(git_repo, slug)


# ---------------------------------------------------------------------------
# A10-1: pause-path failure logs ERROR (both sites — parametrize)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("plan_text,label", [
    ("## STEP 1\nDo stuff.\n", "final-step-X2"),
    ("## STEP 1\nDo stuff.\n## STEP 2\nMore stuff.\n", "while-loop-X1"),
])
def test_pause_path_failure_logs_error(plan_text, label):
    """Teardown failure at pause path must emit ERROR log with the failure message."""
    mock_verdict, log_calls, _ = _run_plan_with_teardown_error(plan_text)
    error_msgs = [msg for level, msg in log_calls if level == "ERROR" and "worktree teardown failed" in msg]
    assert len(error_msgs) >= 1, f"[{label}] Expected ERROR log for teardown failure, got: {log_calls}"


# ---------------------------------------------------------------------------
# A10-2: pause-path failure writes worktree_teardown gate_events fail row
# ---------------------------------------------------------------------------

def test_pause_path_failure_writes_gate_event_row():
    """Teardown failure must insert a worktree_teardown fail row via record_single_gate_event."""
    with tempfile.TemporaryDirectory() as tmp:
        decisions_dir, plan_path = _setup_plan(tmp, "## STEP 1\nDo stuff.\n")
        config = {
            "default_model": "claude-sonnet-4-6",
            "pushover": {"app_key": "", "user_key": ""},
            "callback_port": 5999,
            "step_timeout_seconds": 600,
        }

        with patch("bellows._create_worktree", return_value="/tmp/wt"), \
             patch("bellows._capture_git_diff", return_value=""), \
             patch("bellows._teardown_worktree",
                   side_effect=WorktreeTeardownError("test merge conflict")), \
             patch("bellows.runner.run_step", return_value=_make_fake_run_step_result()), \
             patch("bellows.gates.check", return_value=_clean_gates()), \
             patch("bellows.verdict.post_verdict_request", return_value="/tmp/vr.md"), \
             patch("bellows.notifier.push"), \
             patch("bellows.notifier.notify_verdict_request"), \
             patch("bellows.record_run"), \
             patch("bellows.validators.validate_at_claim",
                   return_value={"rejected": False, "reject_reason": "", "warnings": []}):
            response_server = MagicMock()
            bellows.run_plan(plan_path, config, response_server)

        db_path = lifecycle.LIFECYCLE_DB_PATH
        conn = sqlite3.connect(db_path)
        rows = conn.execute(
            "SELECT gate_name, result, reason_code, overridden, override_ref "
            "FROM gate_events WHERE gate_name = 'worktree_teardown'"
        ).fetchall()
        conn.close()
        assert len(rows) >= 1, f"Expected worktree_teardown fail row, got: {rows}"
        row = rows[0]
        assert row[0] == "worktree_teardown"
        assert row[1] == "fail"
        assert "test merge conflict" in row[2]
        assert row[3] == 0
        assert row[4] is None


# ---------------------------------------------------------------------------
# A10-3: pause-path failure flips gate_result["passed"] to False
# ---------------------------------------------------------------------------

def test_pause_path_failure_flips_passed_to_false():
    """Teardown failure must set gate_result['passed'] = False in the posted verdict request."""
    mock_verdict, _, _ = _run_plan_with_teardown_error("## STEP 1\nDo stuff.\n")
    mock_verdict.assert_called_once()
    gate_result_arg = mock_verdict.call_args[0][4]
    assert gate_result_arg["passed"] is False, \
        f"gate_result['passed'] should be False, got: {gate_result_arg}"


# ---------------------------------------------------------------------------
# A10-4: park-path failure routes to halted-
# ---------------------------------------------------------------------------

def test_park_path_failure_routes_to_halted(monkeypatch, tmp_path):
    """Teardown failure during park must route to halted-, not parked-."""
    decisions_dir = tmp_path / "proj" / "knowledge" / "decisions"
    decisions_dir.mkdir(parents=True)
    base_filename = "executable-park-halt.md"
    inprogress_path = str(decisions_dir / f"in-progress-{base_filename}")
    with open(inprogress_path, "w") as f:
        f.write("# Test plan")

    db_path = str(tmp_path / "test.db")
    conn = sqlite3.connect(db_path)
    conn.execute(
        """CREATE TABLE IF NOT EXISTS runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT, plan_path TEXT, project TEXT,
            session_id TEXT, step INTEGER, status TEXT,
            cost REAL, plan_slug TEXT
        )""")
    conn.execute(
        """CREATE TABLE IF NOT EXISTS parked_steps (
            plan_slug TEXT PRIMARY KEY,
            plan_path TEXT, project TEXT,
            resume_step INTEGER, resets_at_epoch REAL,
            parked_at TEXT
        )""")
    conn.commit()
    conn.close()

    parsed = {
        "session_limit": True,
        "resets_at_epoch": time.time() + 3600,
        "resets_at_raw": "resets 11:50pm",
        "session_id": "test-session",
        "cost_usd": 0.0,
    }

    # Register the plan in lifecycle DB so mark_plan_state works
    plan_id = 999
    conn = sqlite3.connect(lifecycle.LIFECYCLE_DB_PATH)
    conn.execute(
        "INSERT INTO plans (id, type, target_project, title, lifecycle_state, created_at) "
        "VALUES (?, 'executable', 'bellows', 'park-halt-test', 'in_progress', '2026-01-01')",
        (plan_id,))
    conn.commit()
    conn.close()

    monkeypatch.setattr(bellows, "BELLOWS_ROOT", tmp_path)

    with patch("bellows._teardown_worktree",
               side_effect=WorktreeTeardownError("dirty tree conflict")), \
         patch("bellows.notifier.notify_plan_halted") as mock_halted, \
         patch("bellows._retire_receipts") as mock_retire:
        result = bellows._maybe_park_session_limit(
            parsed, inprogress_path, 2, "executable-park-halt", base_filename,
            base_filename, str(decisions_dir), None, db_path,
            str(tmp_path / "proj"), "/tmp/wt", "app_key", "user_key", plan_id,
        )

    assert result is True
    halted_path = str(decisions_dir / f"halted-{base_filename}")
    parked_path = str(decisions_dir / f"parked-{base_filename}")
    assert os.path.exists(halted_path), "Plan should be renamed to halted-"
    assert not os.path.exists(parked_path), "Plan must NOT be renamed to parked-"
    assert not os.path.exists(inprogress_path), "in-progress file should be gone"

    # No record_park row
    conn = sqlite3.connect(db_path)
    park_rows = conn.execute("SELECT * FROM parked_steps WHERE plan_slug = 'executable-park-halt'").fetchall()
    conn.close()
    assert len(park_rows) == 0, "No park row should be written for halted route"

    # plans row marked halted
    conn = sqlite3.connect(lifecycle.LIFECYCLE_DB_PATH)
    plan_row = conn.execute("SELECT lifecycle_state FROM plans WHERE id = ?", (plan_id,)).fetchone()
    conn.close()
    assert plan_row is not None and plan_row[0] == "halted", \
        f"Plan state should be 'halted', got: {plan_row}"

    mock_halted.assert_called_once()
    mock_retire.assert_called_once_with(plan_id)


# ---------------------------------------------------------------------------
# A10-5: dirty file INTERSECTING branch changes → precheck raises
# ---------------------------------------------------------------------------

def test_precheck_raises_on_intersecting_dirty_file(git_repo):
    """Dirty file on main that intersects branch changes triggers precheck before merge."""
    wt_path = _create_worktree(git_repo, "precheck-intersect")
    try:
        # Commit a change to README.md in worktree
        with open(os.path.join(wt_path, "README.md"), "w") as f:
            f.write("worktree version\n")
        subprocess.run(["git", "add", "README.md"], cwd=wt_path, capture_output=True, text=True)
        subprocess.run(
            ["git", "commit", "-m", "wt edit"], cwd=wt_path,
            capture_output=True, text=True, check=True,
        )
        # Dirty main with the SAME file
        with open(os.path.join(git_repo, "README.md"), "w") as f:
            f.write("main dirty version\n")

        with pytest.raises(WorktreeTeardownError) as exc_info:
            _teardown_worktree(git_repo, wt_path, "precheck-intersect")

        assert "worktree_teardown_dirty_tree" in str(exc_info.value)
        assert "README.md" in str(exc_info.value)
        # No merge was attempted — no MERGE_HEAD
        assert not os.path.exists(os.path.join(git_repo, ".git", "MERGE_HEAD"))
    finally:
        subprocess.run(
            ["git", "worktree", "remove", "--force", wt_path], cwd=git_repo,
            capture_output=True, text=True,
        )


# ---------------------------------------------------------------------------
# A10-5b: dirty NON-intersecting file → precheck passes, merge proceeds
# ---------------------------------------------------------------------------

def test_precheck_passes_on_non_intersecting_dirty_file(git_repo):
    """Dirty file on main that does NOT intersect branch changes → precheck passes."""
    wt_path = _create_worktree(git_repo, "precheck-nonintersect")
    try:
        # Commit a NEW file in worktree
        with open(os.path.join(wt_path, "new_file.txt"), "w") as f:
            f.write("worktree content\n")
        subprocess.run(["git", "add", "new_file.txt"], cwd=wt_path, capture_output=True, text=True)
        subprocess.run(
            ["git", "commit", "-m", "wt add new_file"], cwd=wt_path,
            capture_output=True, text=True, check=True,
        )
        # Dirty main with a DIFFERENT file (untracked)
        with open(os.path.join(git_repo, "dirty.txt"), "w") as f:
            f.write("untracked dirty file\n")
    except Exception:
        subprocess.run(
            ["git", "worktree", "remove", "--force", wt_path], cwd=git_repo,
            capture_output=True, text=True,
        )
        raise

    _teardown_worktree(git_repo, wt_path, "precheck-nonintersect")

    # Merge landed
    assert os.path.isfile(os.path.join(git_repo, "new_file.txt")), \
        "new_file.txt should exist on main (merge landed)"
    # Dirty file preserved
    assert os.path.isfile(os.path.join(git_repo, "dirty.txt")), \
        "dirty.txt should still exist on main"


# ---------------------------------------------------------------------------
# A10-5c: commit-less teardown with dirty tree → precheck skipped
# ---------------------------------------------------------------------------

def test_precheck_skipped_when_no_commits(git_repo):
    """Commit-less teardown with a dirty tree → precheck not triggered."""
    wt_path = _create_worktree(git_repo, "precheck-nocommit")
    try:
        # Do NOT commit anything in the worktree — zero commits to land
        # Dirty main
        with open(os.path.join(git_repo, "dirty.txt"), "w") as f:
            f.write("dirty content\n")
    except Exception:
        subprocess.run(
            ["git", "worktree", "remove", "--force", wt_path], cwd=git_repo,
            capture_output=True, text=True,
        )
        raise

    # Should NOT raise even though main is dirty — no commits to land
    _teardown_worktree(git_repo, wt_path, "precheck-nocommit")

    # Worktree removed
    assert not os.path.isdir(wt_path), "Worktree should be removed"


# ---------------------------------------------------------------------------
# A10-6: clean live tree → merge proceeds, commits land
# ---------------------------------------------------------------------------

def test_clean_tree_merge_proceeds(git_repo):
    """Clean main tree with worktree commits → merge proceeds normally."""
    wt_path = _create_worktree(git_repo, "clean-merge")
    try:
        with open(os.path.join(wt_path, "new_file.txt"), "w") as f:
            f.write("content\n")
        subprocess.run(["git", "add", "new_file.txt"], cwd=wt_path, capture_output=True, text=True)
        subprocess.run(
            ["git", "commit", "-m", "wt commit"], cwd=wt_path,
            capture_output=True, text=True, check=True,
        )
    except Exception:
        subprocess.run(
            ["git", "worktree", "remove", "--force", wt_path], cwd=git_repo,
            capture_output=True, text=True,
        )
        raise

    shas = _teardown_worktree(git_repo, wt_path, "clean-merge")

    assert len(shas) >= 1, "Should return landed SHAs"
    assert os.path.isfile(os.path.join(git_repo, "new_file.txt"))
    assert not os.path.isdir(wt_path)


# ---------------------------------------------------------------------------
# A10-7: precheck evidence contains recovery commands with git stash push
# ---------------------------------------------------------------------------

def test_precheck_evidence_contains_stash_recovery(git_repo):
    """Precheck evidence must contain 'git stash push' recovery command."""
    wt_path = _create_worktree(git_repo, "precheck-stash")
    try:
        with open(os.path.join(wt_path, "README.md"), "w") as f:
            f.write("worktree version\n")
        subprocess.run(["git", "add", "README.md"], cwd=wt_path, capture_output=True, text=True)
        subprocess.run(
            ["git", "commit", "-m", "wt edit"], cwd=wt_path,
            capture_output=True, text=True, check=True,
        )
        with open(os.path.join(git_repo, "README.md"), "w") as f:
            f.write("main dirty\n")

        with pytest.raises(WorktreeTeardownError) as exc_info:
            _teardown_worktree(git_repo, wt_path, "precheck-stash")

        evidence = str(exc_info.value)
        assert "git stash push" in evidence, \
            f"Evidence should contain 'git stash push', got: {evidence}"
        assert "README.md" in evidence
    finally:
        subprocess.run(
            ["git", "worktree", "remove", "--force", wt_path], cwd=git_repo,
            capture_output=True, text=True,
        )


# ---------------------------------------------------------------------------
# A10-8: Gap-1c retry tests
# ---------------------------------------------------------------------------

def test_gap1c_dirty_tree_retry_succeeds():
    """Gap-1c: dirty-tree-marked failure retries and clears on success, SHAs recorded."""
    with tempfile.TemporaryDirectory() as tmp:
        wt_path = os.path.join(tmp, "wt")
        os.makedirs(wt_path)
        gate_result = {
            "failures": [
                {"gate": "worktree_teardown",
                 "evidence": "worktree_teardown_dirty_tree: local main has uncommitted changes"},
            ],
            "files_changed": ["bellows.py"],
        }
        mock_shas = ["abc123", "def456"]
        with patch("bellows._teardown_worktree", return_value=mock_shas) as mock_teardown:
            result = bellows._retry_recoverable_teardown(
                gate_result, tmp, wt_path, "test-slug", plan_id=42)

        assert result == mock_shas
        assert not any(f.get("gate") == "worktree_teardown" for f in gate_result["failures"])
        mock_teardown.assert_called_once_with(tmp, wt_path, "test-slug", plan_id=42)


def test_gap1c_content_conflict_does_not_retry():
    """Gap-1c: content-conflict teardown failure (no dirty_tree token) → skip retry."""
    with tempfile.TemporaryDirectory() as tmp:
        wt_path = os.path.join(tmp, "wt")
        os.makedirs(wt_path)
        gate_result = {
            "failures": [
                {"gate": "worktree_teardown",
                 "evidence": "cherry-pick conflict on bellows.py"},
            ],
            "files_changed": [],
        }
        with patch("bellows._teardown_worktree") as mock_teardown:
            result = bellows._retry_recoverable_teardown(
                gate_result, tmp, wt_path, "test-slug")

        assert result == []
        assert any(f.get("gate") == "worktree_teardown" for f in gate_result["failures"])
        mock_teardown.assert_not_called()


def test_gap1c_mixed_failure_does_not_retry():
    """Gap-1c: mixed-failure continue (worktree_teardown + another gate) → skip retry."""
    with tempfile.TemporaryDirectory() as tmp:
        wt_path = os.path.join(tmp, "wt")
        os.makedirs(wt_path)
        gate_result = {
            "failures": [
                {"gate": "worktree_teardown",
                 "evidence": "worktree_teardown_dirty_tree: dirty"},
                {"gate": "scope_check",
                 "evidence": "out of scope"},
            ],
            "files_changed": [],
        }
        with patch("bellows._teardown_worktree") as mock_teardown:
            result = bellows._retry_recoverable_teardown(
                gate_result, tmp, wt_path, "test-slug")

        assert result == []
        assert any(f.get("gate") == "worktree_teardown" for f in gate_result["failures"])
        mock_teardown.assert_not_called()


def test_gap1c_retry_fails_leaves_failure():
    """Gap-1c: dirty-tree retry still fails → failure retained for Gap-1b halt."""
    with tempfile.TemporaryDirectory() as tmp:
        wt_path = os.path.join(tmp, "wt")
        os.makedirs(wt_path)
        gate_result = {
            "failures": [
                {"gate": "worktree_teardown",
                 "evidence": "worktree_teardown_dirty_tree: still dirty"},
            ],
            "files_changed": [],
        }
        with patch("bellows._teardown_worktree",
                    side_effect=WorktreeTeardownError("worktree_teardown_dirty_tree: still dirty")):
            result = bellows._retry_recoverable_teardown(
                gate_result, tmp, wt_path, "test-slug")

        assert result == []
        assert any(f.get("gate") == "worktree_teardown" for f in gate_result["failures"])


def test_gap1c_worktree_gone_skips_retry():
    """Gap-1c: worktree directory missing → skip retry."""
    gate_result = {
        "failures": [
            {"gate": "worktree_teardown",
             "evidence": "worktree_teardown_dirty_tree: dirty"},
        ],
        "files_changed": [],
    }
    with patch("bellows._teardown_worktree") as mock_teardown:
        result = bellows._retry_recoverable_teardown(
            gate_result, "/nonexistent", "/nonexistent/wt", "test-slug")

    assert result == []
    assert any(f.get("gate") == "worktree_teardown" for f in gate_result["failures"])
    mock_teardown.assert_not_called()


# ---------------------------------------------------------------------------
# A10-8b: precheck intersection arms
# ---------------------------------------------------------------------------

def test_precheck_untracked_dir_collapse(git_repo):
    """Untracked directory on main containing a branch-added file must intersect.
    Without -uall, git collapses the untracked dir, escaping the intersection."""
    wt_path = _create_worktree(git_repo, "precheck-uall")
    try:
        # In worktree: add a file inside a new directory
        newdir = os.path.join(wt_path, "newdir")
        os.makedirs(newdir)
        with open(os.path.join(newdir, "file.py"), "w") as f:
            f.write("content\n")
        subprocess.run(["git", "add", "newdir/file.py"], cwd=wt_path, capture_output=True, text=True)
        subprocess.run(
            ["git", "commit", "-m", "add newdir/file.py"], cwd=wt_path,
            capture_output=True, text=True, check=True,
        )
        # On main: create the same directory with an untracked file
        main_newdir = os.path.join(git_repo, "newdir")
        os.makedirs(main_newdir)
        with open(os.path.join(main_newdir, "file.py"), "w") as f:
            f.write("conflicting content\n")

        with pytest.raises(WorktreeTeardownError) as exc_info:
            _teardown_worktree(git_repo, wt_path, "precheck-uall")

        assert "worktree_teardown_dirty_tree" in str(exc_info.value)
        assert "newdir/file.py" in str(exc_info.value)
    finally:
        subprocess.run(
            ["git", "worktree", "remove", "--force", wt_path], cwd=git_repo,
            capture_output=True, text=True,
        )


def test_precheck_spaced_path(git_repo):
    """Dirty file with spaces in path must be correctly intersected."""
    wt_path = _create_worktree(git_repo, "precheck-spaced")
    try:
        spaced = os.path.join(wt_path, "my file.txt")
        with open(spaced, "w") as f:
            f.write("content\n")
        subprocess.run(["git", "add", "my file.txt"], cwd=wt_path, capture_output=True, text=True)
        subprocess.run(
            ["git", "commit", "-m", "add spaced file"], cwd=wt_path,
            capture_output=True, text=True, check=True,
        )
        with open(os.path.join(git_repo, "my file.txt"), "w") as f:
            f.write("dirty\n")

        with pytest.raises(WorktreeTeardownError) as exc_info:
            _teardown_worktree(git_repo, wt_path, "precheck-spaced")

        assert "worktree_teardown_dirty_tree" in str(exc_info.value)
        assert "my file.txt" in str(exc_info.value)
    finally:
        subprocess.run(
            ["git", "worktree", "remove", "--force", wt_path], cwd=git_repo,
            capture_output=True, text=True,
        )


def test_precheck_rename_entry_both_sides(git_repo):
    """Rename entry: both old and new paths must be in the dirty set for intersection."""
    wt_path = _create_worktree(git_repo, "precheck-rename")
    try:
        # In worktree: modify README.md
        with open(os.path.join(wt_path, "README.md"), "w") as f:
            f.write("modified in worktree\n")
        subprocess.run(["git", "add", "README.md"], cwd=wt_path, capture_output=True, text=True)
        subprocess.run(
            ["git", "commit", "-m", "edit README"], cwd=wt_path,
            capture_output=True, text=True, check=True,
        )
        # On main: rename README.md → old_readme.md (staged rename)
        subprocess.run(["git", "mv", "README.md", "old_readme.md"], cwd=git_repo,
                       capture_output=True, text=True, check=True)

        with pytest.raises(WorktreeTeardownError) as exc_info:
            _teardown_worktree(git_repo, wt_path, "precheck-rename")

        evidence = str(exc_info.value)
        assert "worktree_teardown_dirty_tree" in evidence
        # At least the original README.md (which is in branch diff) should intersect
        assert "README.md" in evidence
    finally:
        # Unstage the rename to clean up
        subprocess.run(["git", "reset", "HEAD", "."], cwd=git_repo,
                       capture_output=True, text=True)
        # Restore README.md
        subprocess.run(["git", "checkout", "--", "README.md"], cwd=git_repo,
                       capture_output=True, text=True)
        if os.path.exists(os.path.join(git_repo, "old_readme.md")):
            os.remove(os.path.join(git_repo, "old_readme.md"))
        subprocess.run(
            ["git", "worktree", "remove", "--force", wt_path], cwd=git_repo,
            capture_output=True, text=True,
        )


# ---------------------------------------------------------------------------
# A10-9: override refusal for worktree_teardown
# ---------------------------------------------------------------------------

def test_override_gate_refuses_worktree_teardown():
    """clear_plan.py --override-gate <x> <y> worktree_teardown --ref <dummy> exits 1."""
    result = subprocess.run(
        [sys.executable, "tools/clear_plan.py",
         "--override-gate", "executable-999", "1", "worktree_teardown",
         "--ref", "test-ref"],
        capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 1, f"Expected exit 1, got {result.returncode}: {result.stderr}"
    assert "cannot be overridden" in result.stdout, \
        f"Expected refusal text in stdout, got: {result.stdout}"


def test_override_gate_refuses_worktree_teardown_no_db_write(tmp_path):
    """Override refusal must not write to DB."""
    db_path = str(tmp_path / "lifecycle.db")
    lifecycle.init_lifecycle_db(db_path)
    # Register a plan and step so a non-refused override WOULD find rows
    conn = sqlite3.connect(db_path)
    conn.execute(
        "INSERT INTO plans (id, type, target_project, title, lifecycle_state, created_at) "
        "VALUES (999, 'executable', 'bellows', 'test', 'in_progress', '2026-01-01')")
    conn.execute("INSERT INTO steps (id, plan_id, step_number) VALUES (1, 999, 1)")
    conn.execute(
        "INSERT INTO gate_events (step_id, gate_name, result, reason_code, overridden, override_ref) "
        "VALUES (1, 'worktree_teardown', 'fail', 'test', 0, NULL)")
    conn.commit()
    conn.close()

    sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tools"))
    import importlib
    import clear_plan
    importlib.reload(clear_plan)

    with pytest.raises(SystemExit) as exc_info:
        clear_plan.override_gate("999", "1", "worktree_teardown", "test-ref", db_path=db_path)

    assert exc_info.value.code == 1

    # Verify no override was applied
    conn = sqlite3.connect(db_path)
    row = conn.execute(
        "SELECT overridden FROM gate_events WHERE gate_name = 'worktree_teardown'"
    ).fetchone()
    conn.close()
    assert row[0] == 0, "worktree_teardown row must NOT be overridden"


# ---------------------------------------------------------------------------
# A10-10: record_single_gate_event
# ---------------------------------------------------------------------------

def test_record_single_gate_event_inserts_one_row():
    """record_single_gate_event inserts exactly one row."""
    db_path = lifecycle.LIFECYCLE_DB_PATH
    conn = sqlite3.connect(db_path)
    conn.execute(
        "INSERT INTO plans (id, type, target_project, title, lifecycle_state, created_at) "
        "VALUES (888, 'executable', 'bellows', 'test', 'in_progress', '2026-01-01')")
    conn.execute("INSERT INTO steps (id, plan_id, step_number) VALUES (1, 888, 1)")
    conn.commit()
    conn.close()

    lifecycle.record_single_gate_event(1, "worktree_teardown", "fail", "test reason")

    conn = sqlite3.connect(db_path)
    rows = conn.execute(
        "SELECT gate_name, result, reason_code, overridden, override_ref "
        "FROM gate_events WHERE step_id = 1 AND gate_name = 'worktree_teardown'"
    ).fetchall()
    conn.close()
    assert len(rows) == 1
    assert rows[0] == ("worktree_teardown", "fail", "test reason", 0, None)


def test_record_single_gate_event_noop_on_none_step_id():
    """record_single_gate_event is a no-op when step_id is None."""
    db_path = lifecycle.LIFECYCLE_DB_PATH
    conn = sqlite3.connect(db_path)
    count_before = conn.execute("SELECT COUNT(*) FROM gate_events").fetchone()[0]
    conn.close()

    lifecycle.record_single_gate_event(None, "worktree_teardown", "fail", "test")

    conn = sqlite3.connect(db_path)
    count_after = conn.execute("SELECT COUNT(*) FROM gate_events").fetchone()[0]
    conn.close()
    assert count_after == count_before, "No row should be inserted for None step_id"
