import json
import os
import shutil
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import bellows
import verdict


def test_load_config():
    with tempfile.TemporaryDirectory() as tmp:
        config_path = os.path.join(tmp, "config.json")
        config_data = {
            "watched_projects": [],
            "default_model": "claude-sonnet-4-6",
            "planner_model": "claude-sonnet-4-6",
            "callback_port": 5000,
        }
        secrets_data = {
            "pushover": {"app_key": "fake-app-key", "user_key": "fake-user-key"},
            "tailscale_ip": "100.0.0.1",
        }
        with open(config_path, "w") as f:
            json.dump(config_data, f)
        with open(os.path.join(tmp, "config.secrets.json"), "w") as f:
            json.dump(secrets_data, f)
        result = bellows.load_config(config_path)
        assert result["default_model"] == "claude-sonnet-4-6"
        assert result["pushover"]["app_key"] == "fake-app-key"
        assert result["tailscale_ip"] == "100.0.0.1"


def test_load_config_merges_secrets():
    with tempfile.TemporaryDirectory() as tmp:
        config_path = os.path.join(tmp, "config.json")
        operational = {
            "watched_projects": ["/tmp/project"],
            "default_model": "claude-sonnet-4-6",
            "planner_model": "claude-sonnet-4-6",
            "callback_port": 5000,
        }
        secrets = {
            "pushover": {"app_key": "test-app", "user_key": "test-user"},
            "tailscale_ip": "100.1.2.3",
        }
        with open(config_path, "w") as f:
            json.dump(operational, f)
        with open(os.path.join(tmp, "config.secrets.json"), "w") as f:
            json.dump(secrets, f)
        result = bellows.load_config(config_path)
        assert result["watched_projects"] == ["/tmp/project"]
        assert result["default_model"] == "claude-sonnet-4-6"
        assert result["pushover"]["app_key"] == "test-app"
        assert result["pushover"]["user_key"] == "test-user"
        assert result["tailscale_ip"] == "100.1.2.3"
        assert result["callback_port"] == 5000


def test_load_config_missing_secrets():
    with tempfile.TemporaryDirectory() as tmp:
        config_path = os.path.join(tmp, "config.json")
        operational = {
            "watched_projects": [],
            "default_model": "claude-sonnet-4-6",
            "callback_port": 5000,
        }
        with open(config_path, "w") as f:
            json.dump(operational, f)
        result = bellows.load_config(config_path)
        assert result["default_model"] == "claude-sonnet-4-6"
        assert result["callback_port"] == 5000
        assert "pushover" not in result


def test_load_config_deep_merge():
    with tempfile.TemporaryDirectory() as tmp:
        config_path = os.path.join(tmp, "config.json")
        operational = {
            "default_model": "claude-sonnet-4-6",
            "pushover": {},
        }
        secrets = {
            "pushover": {"app_key": "merged-key"},
        }
        with open(config_path, "w") as f:
            json.dump(operational, f)
        with open(os.path.join(tmp, "config.secrets.json"), "w") as f:
            json.dump(secrets, f)
        result = bellows.load_config(config_path)
        assert result["pushover"] == {"app_key": "merged-key"}


def test_is_final_step():
    assert bellows.is_final_step(2, 2) is True
    assert bellows.is_final_step(1, 2) is False


def test_is_runnable_plan_diagnostic():
    assert bellows.is_runnable_plan("diagnostic-foo-2026-04-14.md") is True
    assert bellows.is_runnable_plan("in-progress-diagnostic-foo.md") is False


def test_is_runnable_plan_parallel_prefix():
    assert bellows.is_runnable_plan("parallel-1-executable-foo-2026-04-14.md") is True
    assert bellows.is_runnable_plan("parallel-2-diagnostic-bar-2026-04-14.md") is True
    assert bellows.is_runnable_plan("parallel-10-executable-baz.md") is True
    assert bellows.is_runnable_plan("parallel-1-foo.md") is False
    assert bellows.is_runnable_plan("in-progress-parallel-1-executable-foo.md") is False
    assert bellows.is_runnable_plan("executable-foo-2026-04-14.md") is True


def test_extract_parallel_group_match():
    assert bellows.extract_parallel_group("parallel-1-executable-foo-2026-04-14.md") == "parallel-1"
    assert bellows.extract_parallel_group("parallel-2-diagnostic-bar.md") == "parallel-2"


def test_extract_parallel_group_no_match():
    assert bellows.extract_parallel_group("executable-foo.md") is None
    assert bellows.extract_parallel_group("diagnostic-bar.md") is None


def test_is_plan_stranded_returns_true_when_inprogress_exists():
    with tempfile.TemporaryDirectory() as tmp:
        inprogress = os.path.join(tmp, "in-progress-foo.md")
        done = os.path.join(tmp, "Done", "foo.md")
        open(inprogress, "w").close()
        assert bellows._is_plan_stranded(inprogress, done) is True


def test_is_plan_stranded_returns_true_when_done_missing():
    with tempfile.TemporaryDirectory() as tmp:
        inprogress = os.path.join(tmp, "in-progress-foo.md")
        done = os.path.join(tmp, "Done", "foo.md")
        # inprogress does not exist but done also does not exist
        assert bellows._is_plan_stranded(inprogress, done) is True


def test_is_plan_stranded_returns_false_on_happy_path():
    with tempfile.TemporaryDirectory() as tmp:
        inprogress = os.path.join(tmp, "in-progress-foo.md")
        done_dir = os.path.join(tmp, "Done")
        os.makedirs(done_dir)
        done = os.path.join(done_dir, "foo.md")
        open(done, "w").close()
        assert bellows._is_plan_stranded(inprogress, done) is False


def test_rescan_preserves_seen():
    with tempfile.TemporaryDirectory() as tmp:
        fname = "executable-foo-2026-04-14.md"
        plan_path = os.path.join(tmp, fname)
        with open(plan_path, "w") as f:
            f.write("## STEP 1\nfoo\n")

        b = bellows.Bellows({"watched_projects": [tmp], "callback_port": 5999})
        mock_orchestrator = MagicMock()
        mock_orchestrator.config = {"watched_projects": [tmp]}
        slug = verdict.slug_from_path(plan_path)
        mock_orchestrator._seen = {slug}
        handler = bellows.PlanHandler(mock_orchestrator)

        b._rescan(handler)

        assert slug in mock_orchestrator._seen
        mock_orchestrator.handle_new_plan.assert_not_called()


def test_source_sha_returns_string():
    import re
    sha = bellows._source_sha()
    assert isinstance(sha, str)
    assert len(sha) > 0
    assert sha == "unknown" or re.match(r"^[0-9a-f]{7,12}$", sha), f"unexpected SHA format: {sha!r}"


def test_diagnostic_auto_close_moves_to_done():
    with tempfile.TemporaryDirectory() as tmp:
        decisions_dir = os.path.join(tmp, "proj", "knowledge", "decisions")
        os.makedirs(decisions_dir)
        plan_filename = "diagnostic-foo-2026-04-15.md"
        plan_path = os.path.join(decisions_dir, plan_filename)
        with open(plan_path, "w") as f:
            f.write("## Diagnostic\nSingle-step investigation.\n")

        config = {
            "default_model": "claude-sonnet-4-6",
            "pushover": {"app_key": "", "user_key": ""},
            "callback_port": 5999,
            "step_timeout_seconds": 600,
        }

        clean_parsed = {
            "session_id": "test-session",
            "is_error": False,
            "stop_reason": "end_turn",
            "result_text": "",
            "cost_usd": 0.05,
            "permission_denials": [],
            "receipt_status": "Complete",
            "ceo_flags": [],
            "escalate": False,
        }
        clean_gates = {
            "passed": True,
            "failures": [],
            "is_qa_step": False,
            "files_changed": [],
            "plan_header": {"auto_close": "true"},
            "verdict_requested": {"requested": False, "body": None},
        }

        with patch("bellows.runner.run_step", return_value=clean_parsed), \
             patch("bellows.gates.check", return_value=clean_gates), \
             patch("bellows.notifier.notify_plan_complete") as mock_notify, \
             patch("bellows.verdict.log_to_ledger") as mock_ledger, \
             patch("bellows._capture_git_diff", return_value=""), \
             patch("bellows._create_worktree", return_value="/tmp/wt"), \
             patch("bellows._teardown_worktree"), \
             patch("bellows.record_run"), \
             patch("bellows.validators.validate_at_claim", return_value={"rejected": False, "reject_reason": "", "warnings": []}):
            response_server = MagicMock()
            bellows.run_plan(plan_path, config, response_server)

        done_path = os.path.join(decisions_dir, "Done", plan_filename)
        assert os.path.isfile(done_path), f"plan not moved to Done/: {done_path}"
        assert not os.path.exists(plan_path), "original plan file should be moved"
        mock_ledger.assert_called_once()
        assert mock_ledger.call_args[0][3] == "auto-close"
        mock_notify.assert_called()


def test_clean_diagnostic_no_header_posts_verdict():
    """Phase 8.1: clean diagnostic with no plan header should pause for verdict
    instead of stranding. Diagnostic default = auto_close=False."""
    with tempfile.TemporaryDirectory() as tmp:
        decisions_dir = os.path.join(tmp, "proj", "knowledge", "decisions")
        os.makedirs(decisions_dir)
        plan_filename = "diagnostic-no-header-2026-04-16.md"
        plan_path = os.path.join(decisions_dir, plan_filename)
        with open(plan_path, "w") as f:
            f.write("## Diagnostic\nSingle-step investigation, no header.\n")

        config = {
            "default_model": "claude-sonnet-4-6",
            "pushover": {"app_key": "", "user_key": ""},
            "callback_port": 5999,
            "step_timeout_seconds": 600,
        }

        clean_parsed = {
            "session_id": "test-session",
            "is_error": False,
            "stop_reason": "end_turn",
            "result_text": "",
            "cost_usd": 0.05,
            "permission_denials": [],
            "receipt_status": "Complete",
            "ceo_flags": [],
            "escalate": False,
        }
        clean_gates = {
            "passed": True,
            "failures": [],
            "is_qa_step": False,
            "files_changed": [],
            "plan_header": {},  # empty — triggers diagnostic default effective_auto_close=False
            "verdict_requested": {"requested": False, "body": None},
        }

        with patch("bellows.runner.run_step", return_value=clean_parsed), \
             patch("bellows.gates.check", return_value=clean_gates), \
             patch("bellows.notifier.push"), \
             patch("bellows.notifier.notify_verdict_request") as mock_notify_verdict, \
             patch("bellows.verdict.post_verdict_request") as mock_post_verdict, \
             patch("bellows.verdict.log_to_ledger") as mock_ledger, \
             patch("bellows._capture_git_diff", return_value=""), \
             patch("bellows._create_worktree", return_value="/tmp/wt"), \
             patch("bellows._teardown_worktree"), \
             patch("bellows.record_run"), \
             patch("bellows.validators.validate_at_claim", return_value={"rejected": False, "reject_reason": "", "warnings": []}):
            response_server = MagicMock()
            bellows.run_plan(plan_path, config, response_server)

        # Verdict request was posted
        mock_post_verdict.assert_called_once()
        mock_notify_verdict.assert_called()

        # Plan was renamed to verdict-pending-*
        verdict_pending = os.path.join(decisions_dir, f"verdict-pending-{plan_filename}")
        # The original plan path was moved (run_plan's verdict branch only renames
        # inprogress_path if it exists; for diagnostics the plan stays at its original
        # path, so the rename does not happen — but the verdict request itself was
        # posted, which is the primary assertion).
        # Plan must NOT be in Done/
        done_path = os.path.join(decisions_dir, "Done", plan_filename)
        assert not os.path.exists(done_path), "plan should not be auto-closed to Done/"

        # auto-close branch did NOT fire
        for call in mock_ledger.call_args_list:
            assert call[0][3] != "auto-close", "auto-close ledger should not be logged"


def test_clean_diagnostic_auto_close_true_moves_to_done():
    """Phase 8.1 regression: diagnostic with auto_close: true header should still
    move to Done (matches the existing Phase 7-polish test path)."""
    with tempfile.TemporaryDirectory() as tmp:
        decisions_dir = os.path.join(tmp, "proj", "knowledge", "decisions")
        os.makedirs(decisions_dir)
        plan_filename = "diagnostic-auto-close-2026-04-16.md"
        plan_path = os.path.join(decisions_dir, plan_filename)
        with open(plan_path, "w") as f:
            f.write("## Diagnostic\nSingle-step.\n")

        config = {
            "default_model": "claude-sonnet-4-6",
            "pushover": {"app_key": "", "user_key": ""},
            "callback_port": 5999,
            "step_timeout_seconds": 600,
        }

        clean_parsed = {
            "session_id": "test-session",
            "is_error": False,
            "stop_reason": "end_turn",
            "result_text": "",
            "cost_usd": 0.05,
            "permission_denials": [],
            "receipt_status": "Complete",
            "ceo_flags": [],
            "escalate": False,
        }
        clean_gates = {
            "passed": True,
            "failures": [],
            "is_qa_step": False,
            "files_changed": [],
            "plan_header": {"auto_close": "true"},
            "verdict_requested": {"requested": False, "body": None},
        }

        with patch("bellows.runner.run_step", return_value=clean_parsed), \
             patch("bellows.gates.check", return_value=clean_gates), \
             patch("bellows.notifier.notify_plan_complete") as mock_notify, \
             patch("bellows.verdict.log_to_ledger") as mock_ledger, \
             patch("bellows._capture_git_diff", return_value=""), \
             patch("bellows._create_worktree", return_value="/tmp/wt"), \
             patch("bellows._teardown_worktree"), \
             patch("bellows.record_run"), \
             patch("bellows.validators.validate_at_claim", return_value={"rejected": False, "reject_reason": "", "warnings": []}):
            response_server = MagicMock()
            bellows.run_plan(plan_path, config, response_server)

        done_path = os.path.join(decisions_dir, "Done", plan_filename)
        assert os.path.isfile(done_path), f"plan not moved to Done/: {done_path}"
        assert not os.path.exists(plan_path), "original plan file should be moved"
        mock_ledger.assert_called_once()
        assert mock_ledger.call_args[0][3] == "auto-close"
        mock_notify.assert_called()


def test_executable_no_header_defaults_to_verdict():
    """Disable-auto-close: executable plan with no auto_close header key should
    pause for verdict at terminal step, NOT auto-close to Done."""
    with tempfile.TemporaryDirectory() as tmp:
        decisions_dir = os.path.join(tmp, "proj", "knowledge", "decisions")
        os.makedirs(decisions_dir)
        plan_filename = "executable-no-header-2026-04-24.md"
        plan_path = os.path.join(decisions_dir, plan_filename)
        with open(plan_path, "w") as f:
            f.write("## STEP 1\nDo stuff.\n")

        config = {
            "default_model": "claude-sonnet-4-6",
            "pushover": {"app_key": "", "user_key": ""},
            "callback_port": 5999,
            "step_timeout_seconds": 600,
        }

        clean_parsed = _make_fake_run_step_result()
        clean_gates = {
            "passed": True,
            "failures": [],
            "is_qa_step": False,
            "files_changed": [],
            "plan_header": {},  # no auto_close key — new default should be False
            "verdict_requested": {"requested": False, "body": None},
        }

        with patch("bellows.runner.run_step", return_value=clean_parsed), \
             patch("bellows.gates.check", return_value=clean_gates), \
             patch("bellows.notifier.push"), \
             patch("bellows.notifier.notify_verdict_request") as mock_notify_verdict, \
             patch("bellows.verdict.post_verdict_request") as mock_post_verdict, \
             patch("bellows.verdict.log_to_ledger") as mock_ledger, \
             patch("bellows._capture_git_diff", return_value=""), \
             patch("bellows._create_worktree", return_value="/tmp/wt"), \
             patch("bellows._teardown_worktree"), \
             patch("bellows.record_run"), \
             patch("bellows.validators.validate_at_claim", return_value={"rejected": False, "reject_reason": "", "warnings": []}):
            response_server = MagicMock()
            bellows.run_plan(plan_path, config, response_server)

        # Verdict request was posted (pause branch fired)
        mock_post_verdict.assert_called_once()
        mock_notify_verdict.assert_called()

        # Plan must NOT be in Done/ (auto-close did not fire)
        done_path = os.path.join(decisions_dir, "Done", plan_filename)
        assert not os.path.exists(done_path), "executable with no header should not auto-close to Done/"

        # auto-close ledger entry should not exist
        for call in mock_ledger.call_args_list:
            assert call[0][3] != "auto-close", "auto-close ledger should not be logged"


def test_executable_explicit_auto_close_true_still_closes():
    """Disable-auto-close regression guard: executable plan with explicit
    auto_close: true header should still auto-close to Done."""
    with tempfile.TemporaryDirectory() as tmp:
        decisions_dir = os.path.join(tmp, "proj", "knowledge", "decisions")
        os.makedirs(decisions_dir)
        plan_filename = "executable-explicit-close-2026-04-24.md"
        plan_path = os.path.join(decisions_dir, plan_filename)
        with open(plan_path, "w") as f:
            f.write("## STEP 1\nDo stuff.\n")

        config = {
            "default_model": "claude-sonnet-4-6",
            "pushover": {"app_key": "", "user_key": ""},
            "callback_port": 5999,
            "step_timeout_seconds": 600,
        }

        clean_parsed = _make_fake_run_step_result()
        clean_gates = {
            "passed": True,
            "failures": [],
            "is_qa_step": False,
            "files_changed": [],
            "plan_header": {"auto_close": "true"},  # explicit opt-in
            "verdict_requested": {"requested": False, "body": None},
        }

        with patch("bellows.runner.run_step", return_value=clean_parsed), \
             patch("bellows.gates.check", return_value=clean_gates), \
             patch("bellows.notifier.notify_plan_complete") as mock_notify, \
             patch("bellows.verdict.log_to_ledger") as mock_ledger, \
             patch("bellows._capture_git_diff", return_value=""), \
             patch("bellows._create_worktree", return_value="/tmp/wt"), \
             patch("bellows._teardown_worktree"), \
             patch("bellows.record_run"), \
             patch("bellows.validators.validate_at_claim", return_value={"rejected": False, "reject_reason": "", "warnings": []}):
            response_server = MagicMock()
            bellows.run_plan(plan_path, config, response_server)

        done_path = os.path.join(decisions_dir, "Done", plan_filename)
        assert os.path.isfile(done_path), f"explicit auto_close:true plan not moved to Done/: {done_path}"
        assert not os.path.exists(plan_path), "original plan file should be moved"
        mock_ledger.assert_called_once()
        assert mock_ledger.call_args[0][3] == "auto-close"
        mock_notify.assert_called()


def test_handle_parallel_group_stagger():
    b = bellows.Bellows({"watched_projects": [], "callback_port": 5999})
    sleep_calls = []

    def fake_run(path):
        pass

    with patch.object(b, "_run_tracked", side_effect=fake_run), \
         patch("bellows.time.sleep", side_effect=lambda x: sleep_calls.append(x)):
        b.handle_parallel_group(["a", "b", "c"])

    assert sleep_calls.count(2) >= 3


def test_verdict_continue_at_final_step_moves_to_done():
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)

        # Set up decisions dir with verdict-pending diagnostic plan
        decisions_dir = tmp_path / "proj" / "knowledge" / "decisions"
        decisions_dir.mkdir(parents=True)
        done_dir = decisions_dir / "Done"
        done_dir.mkdir()

        plan_filename = "diagnostic-test-2026-04-16.md"
        verdict_pending_name = f"verdict-pending-{plan_filename}"
        verdict_pending_path = decisions_dir / verdict_pending_name
        verdict_pending_path.write_text("## Diagnostic\nSingle-step investigation.\n")

        # Set up resolved verdict directory under tmp bellows root
        verdicts_resolved = tmp_path / "verdicts" / "resolved"
        verdicts_resolved.mkdir(parents=True)
        verdict_fname = f"verdict-diagnostic-test-2026-04-16-step-1.md"
        (verdicts_resolved / verdict_fname).write_text("continue\nApproved.")

        config = {
            "watched_projects": [str(decisions_dir)],
            "default_model": "claude-sonnet-4-6",
            "pushover": {"app_key": "", "user_key": ""},
            "callback_port": 5999,
        }

        b = bellows.Bellows(config)

        with patch("bellows.BELLOWS_ROOT", tmp_path), \
             patch("bellows.verdict.check_verdict", return_value={
                 "found": True, "verdict": "continue", "reason": "approved"
             }), \
             patch("bellows.verdict.log_to_ledger") as mock_ledger, \
             patch("bellows.notifier.push") as mock_push, \
             patch.object(b, "handle_new_plan") as mock_handle:
            b._consume_verdicts()

        # Plan should be in Done/
        done_path = decisions_dir / "Done" / plan_filename
        assert done_path.is_file(), f"Plan not moved to Done/: {done_path}"
        assert not verdict_pending_path.exists(), "verdict-pending file should be moved"

        # log_to_ledger called with "continue-to-done"
        mock_ledger.assert_called_once()
        assert mock_ledger.call_args[0][3] == "continue-to-done"

        # handle_new_plan NOT called — no re-dispatch on final step
        mock_handle.assert_not_called()


# ---------------------------------------------------------------------------
# _capture_git_diff / _parse_diff_stat — commit-aware semantics (BACKLOG 2026-05-21 fix)
# ---------------------------------------------------------------------------

def test_capture_git_diff_returns_head_sha():
    """_capture_git_diff returns the HEAD SHA of the repo at the given path."""
    with tempfile.TemporaryDirectory() as tmpdir:
        subprocess.run(["git", "init"], cwd=tmpdir, capture_output=True, check=True)
        subprocess.run(["git", "config", "user.email", "test@test"], cwd=tmpdir, capture_output=True, check=True)
        subprocess.run(["git", "config", "user.name", "test"], cwd=tmpdir, capture_output=True, check=True)
        # Create initial commit so HEAD exists
        filepath = os.path.join(tmpdir, "init.txt")
        with open(filepath, "w") as f:
            f.write("init")
        subprocess.run(["git", "add", "."], cwd=tmpdir, capture_output=True, check=True)
        subprocess.run(["git", "commit", "-m", "init"], cwd=tmpdir, capture_output=True, check=True)

        result = bellows._capture_git_diff(tmpdir)
        assert result, "Expected non-empty SHA"
        assert all(c in "0123456789abcdef" for c in result), f"Not a hex SHA: {result!r}"

        # Cross-check against independent git rev-parse
        expected = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=tmpdir, capture_output=True, text=True
        ).stdout.strip()
        assert result == expected, f"SHA mismatch: {result!r} vs {expected!r}"


def test_capture_git_diff_returns_empty_on_no_git():
    """_capture_git_diff returns empty string when path is not a git repo."""
    with tempfile.TemporaryDirectory() as tmpdir:
        result = bellows._capture_git_diff(tmpdir)
        assert result == "", f"Expected empty string, got {result!r}"


def test_parse_diff_stat_empty_pre_sha_returns_empty():
    """_parse_diff_stat short-circuits to [] when pre_diff (SHA) is empty."""
    assert bellows._parse_diff_stat("", "", "/any/path") == []
    assert bellows._parse_diff_stat("post_sha", "", "/any/path") == []


def test_parse_diff_stat_detects_committed_changes():
    """Regression test: _parse_diff_stat detects changes that were committed (the actual bug)."""
    with tempfile.TemporaryDirectory() as tmpdir:
        subprocess.run(["git", "init"], cwd=tmpdir, capture_output=True, check=True)
        subprocess.run(["git", "config", "user.email", "test@test"], cwd=tmpdir, capture_output=True, check=True)
        subprocess.run(["git", "config", "user.name", "test"], cwd=tmpdir, capture_output=True, check=True)
        # Initial commit
        filepath = os.path.join(tmpdir, "tracked.txt")
        with open(filepath, "w") as f:
            f.write("original")
        subprocess.run(["git", "add", "."], cwd=tmpdir, capture_output=True, check=True)
        subprocess.run(["git", "commit", "-m", "init"], cwd=tmpdir, capture_output=True, check=True)

        # Capture pre-step SHA
        pre_sha = bellows._capture_git_diff(tmpdir)

        # Simulate agent: edit file and COMMIT (the pattern that caused the false negative)
        with open(filepath, "w") as f:
            f.write("modified by agent")
        subprocess.run(["git", "add", "."], cwd=tmpdir, capture_output=True, check=True)
        subprocess.run(["git", "commit", "-m", "agent edit"], cwd=tmpdir, capture_output=True, check=True)

        result = bellows._parse_diff_stat("", pre_sha, tmpdir)
        assert "tracked.txt" in result, f"Expected 'tracked.txt' in {result!r}"


def test_parse_diff_stat_detects_uncommitted_changes():
    """Edge case: _parse_diff_stat detects changes that are NOT committed."""
    with tempfile.TemporaryDirectory() as tmpdir:
        subprocess.run(["git", "init"], cwd=tmpdir, capture_output=True, check=True)
        subprocess.run(["git", "config", "user.email", "test@test"], cwd=tmpdir, capture_output=True, check=True)
        subprocess.run(["git", "config", "user.name", "test"], cwd=tmpdir, capture_output=True, check=True)
        # Initial commit
        filepath = os.path.join(tmpdir, "tracked.txt")
        with open(filepath, "w") as f:
            f.write("original")
        subprocess.run(["git", "add", "."], cwd=tmpdir, capture_output=True, check=True)
        subprocess.run(["git", "commit", "-m", "init"], cwd=tmpdir, capture_output=True, check=True)

        # Capture pre-step SHA
        pre_sha = bellows._capture_git_diff(tmpdir)

        # Simulate agent: edit file but do NOT commit
        with open(filepath, "w") as f:
            f.write("modified by agent")

        result = bellows._parse_diff_stat("", pre_sha, tmpdir)
        assert "tracked.txt" in result, f"Expected 'tracked.txt' in {result!r}"


def test_parse_diff_stat_filters_dotdot_paths():
    """_parse_diff_stat filters out ../ paths when project_path is provided."""
    mock_result = MagicMock()
    mock_result.returncode = 0
    mock_result.stdout = (
        " src/foo.py          | 3 ++-\n"
        " ../anvil/bar.py     | 5 +++--\n"
        " tests/test_baz.py   | 2 +-\n"
        " 3 files changed\n"
    )
    with patch("bellows.subprocess.run", return_value=mock_result):
        result = bellows._parse_diff_stat("post", "pre", "/some/project")
    assert result == ["src/foo.py", "tests/test_baz.py"]


# ---------------------------------------------------------------------------
# resume_step threading — Bug 1 fix
# ---------------------------------------------------------------------------

def test_run_plan_resume_step_uses_correct_prompt():
    """run_plan with resume_step=2 must build a prompt containing 'Step 2' and not 'Step 1 ONLY'."""
    with tempfile.TemporaryDirectory() as tmp:
        decisions_dir = os.path.join(tmp, "proj", "knowledge", "decisions")
        os.makedirs(decisions_dir)
        plan_filename = "executable-foo-2026-04-16.md"
        plan_path = os.path.join(decisions_dir, plan_filename)
        with open(plan_path, "w") as f:
            f.write("## STEP 1\nDo stuff.\n## STEP 2\nDo more stuff.\n")

        config = {
            "default_model": "claude-sonnet-4-6",
            "pushover": {"app_key": "", "user_key": ""},
            "callback_port": 5999,
            "step_timeout_seconds": 600,
        }

        captured_prompts = []

        def fake_run_step(prompt, *args, **kwargs):
            captured_prompts.append(prompt)
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

        clean_gates = {
            "passed": True,
            "failures": [],
            "is_qa_step": False,
            "files_changed": [],
            "plan_header": {"auto_close": "true"},
            "verdict_requested": {"requested": False, "body": None},
        }

        with patch("bellows.runner.run_step", side_effect=fake_run_step), \
             patch("bellows.gates.check", return_value=clean_gates), \
             patch("bellows.notifier.push"), \
             patch("bellows.verdict.log_to_ledger"), \
             patch("bellows._capture_git_diff", return_value=""), \
             patch("bellows._create_worktree", return_value="/tmp/wt"), \
             patch("bellows._teardown_worktree"), \
             patch("bellows.record_run"):
            response_server = MagicMock()
            # Create in-progress file that run_plan expects on resume (must have STEP headers)
            inprogress_path = os.path.join(decisions_dir, f"in-progress-{plan_filename}")
            with open(inprogress_path, "w") as f:
                f.write("## STEP 1\nDo stuff.\n## STEP 2\nDo more stuff.\n")
            bellows.run_plan(inprogress_path, config, response_server, resume_step=2)

    assert len(captured_prompts) >= 1
    bootstrap = captured_prompts[0]
    assert "Step 2" in bootstrap, f"Expected 'Step 2' in prompt: {bootstrap!r}"
    assert "Step 1 ONLY" not in bootstrap, f"Found 'Step 1 ONLY' in resume prompt: {bootstrap!r}"
    assert ".bellows-cache/" in bootstrap, \
        f"Resume prompt must reference shadow cache path. Got: {bootstrap!r}"
    assert ".pristine" in bootstrap, \
        f"Resume prompt must reference .pristine shadow file. Got: {bootstrap!r}"


def test_consume_verdicts_continue_calls_handle_new_plan_with_resume_step():
    """_consume_verdicts continue verdict on step 1 of a 2-step plan calls handle_new_plan with resume_step=2."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)

        decisions_dir = tmp_path / "proj" / "knowledge" / "decisions"
        decisions_dir.mkdir(parents=True)
        done_dir = decisions_dir / "Done"
        done_dir.mkdir()

        plan_filename = "executable-bar-2026-04-16.md"
        verdict_pending_name = f"verdict-pending-{plan_filename}"
        verdict_pending_path = decisions_dir / verdict_pending_name
        verdict_pending_path.write_text("## STEP 1\nDo stuff.\n## STEP 2\nDo more stuff.\n")

        verdicts_resolved = tmp_path / "verdicts" / "resolved"
        verdicts_resolved.mkdir(parents=True)
        verdict_fname = "verdict-bar-2026-04-16-step-1.md"
        (verdicts_resolved / verdict_fname).write_text("continue\nApproved.")

        config = {
            "watched_projects": [str(decisions_dir)],
            "default_model": "claude-sonnet-4-6",
            "pushover": {"app_key": "", "user_key": ""},
            "callback_port": 5999,
        }

        b = bellows.Bellows(config)

        with patch("bellows.BELLOWS_ROOT", tmp_path), \
             patch("bellows.verdict.check_verdict", return_value={
                 "found": True, "verdict": "continue", "reason": "approved"
             }), \
             patch("bellows.verdict.log_to_ledger"), \
             patch("bellows.notifier.push"), \
             patch.object(b, "handle_new_plan") as mock_handle:
            b._consume_verdicts()

        mock_handle.assert_called_once()
        _, kwargs = mock_handle.call_args
        assert kwargs.get("resume_step") == 2, f"Expected resume_step=2, got: {mock_handle.call_args}"


def test_consume_verdicts_deletes_pending_file():
    """_consume_verdicts must delete the corresponding verdicts/pending/ file after processing."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)

        decisions_dir = tmp_path / "proj" / "knowledge" / "decisions"
        decisions_dir.mkdir(parents=True)
        done_dir = decisions_dir / "Done"
        done_dir.mkdir()

        plan_filename = "diagnostic-baz-2026-04-16.md"
        verdict_pending_name = f"verdict-pending-{plan_filename}"
        verdict_pending_path = decisions_dir / verdict_pending_name
        verdict_pending_path.write_text("## Diagnostic\nSingle-step.\n")

        verdicts_resolved = tmp_path / "verdicts" / "resolved"
        verdicts_resolved.mkdir(parents=True)
        verdict_fname = "verdict-diagnostic-baz-2026-04-16-step-1.md"
        (verdicts_resolved / verdict_fname).write_text("continue\nApproved.")

        # Create the pending file that should be cleaned up
        pending_dir = tmp_path / "verdicts" / "pending"
        pending_dir.mkdir(parents=True)
        pending_file = pending_dir / "verdict-request-baz-2026-04-16-step-1.md"
        pending_file.write_text("# Verdict Request\nPlease review.")

        config = {
            "watched_projects": [str(decisions_dir)],
            "default_model": "claude-sonnet-4-6",
            "pushover": {"app_key": "", "user_key": ""},
            "callback_port": 5999,
        }

        b = bellows.Bellows(config)

        with patch("bellows.BELLOWS_ROOT", tmp_path), \
             patch("bellows.verdict.check_verdict", return_value={
                 "found": True, "verdict": "continue", "reason": "approved"
             }), \
             patch("bellows.verdict.log_to_ledger"), \
             patch("bellows.notifier.push"), \
             patch.object(b, "handle_new_plan"):
            b._consume_verdicts()

        assert not pending_file.exists(), f"Pending file should have been deleted: {pending_file}"


def test_consume_verdicts_pending_cleanup_safe_when_file_missing():
    """_consume_verdicts must not crash when the pending file doesn't exist."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)

        decisions_dir = tmp_path / "proj" / "knowledge" / "decisions"
        decisions_dir.mkdir(parents=True)
        done_dir = decisions_dir / "Done"
        done_dir.mkdir()

        plan_filename = "diagnostic-qux-2026-04-16.md"
        verdict_pending_name = f"verdict-pending-{plan_filename}"
        verdict_pending_path = decisions_dir / verdict_pending_name
        verdict_pending_path.write_text("## Diagnostic\nSingle-step.\n")

        verdicts_resolved = tmp_path / "verdicts" / "resolved"
        verdicts_resolved.mkdir(parents=True)
        verdict_fname = "verdict-diagnostic-qux-2026-04-16-step-1.md"
        (verdicts_resolved / verdict_fname).write_text("continue\nApproved.")

        # No pending file created — cleanup should be a no-op
        pending_dir = tmp_path / "verdicts" / "pending"
        pending_dir.mkdir(parents=True)

        config = {
            "watched_projects": [str(decisions_dir)],
            "default_model": "claude-sonnet-4-6",
            "pushover": {"app_key": "", "user_key": ""},
            "callback_port": 5999,
        }

        b = bellows.Bellows(config)

        with patch("bellows.BELLOWS_ROOT", tmp_path), \
             patch("bellows.verdict.check_verdict", return_value={
                 "found": True, "verdict": "continue", "reason": "approved"
             }), \
             patch("bellows.verdict.log_to_ledger"), \
             patch("bellows.notifier.push"), \
             patch.object(b, "handle_new_plan"):
            # Should not raise
            b._consume_verdicts()


def test_consume_verdicts_scopes_to_project_from_pending_file():
    """_consume_verdicts must search only the project directory named in the
    pending request file's **Plan:** field, not all watched_projects."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)

        # Two project decision directories
        proj_a_decisions = tmp_path / "proj_a" / "knowledge" / "decisions"
        proj_b_decisions = tmp_path / "proj_b" / "knowledge" / "decisions"
        for d in (proj_a_decisions, proj_b_decisions):
            d.mkdir(parents=True)
            (d / "Done").mkdir()

        slug = "foo-2026-04-16"
        plan_filename = f"executable-{slug}.md"
        verdict_pending_name = f"verdict-pending-{plan_filename}"

        # Both projects have a matching verdict-pending file
        plan_content = "## STEP 1\nDo stuff.\n## STEP 2\nDo more stuff.\n"
        (proj_a_decisions / verdict_pending_name).write_text(plan_content)
        (proj_b_decisions / verdict_pending_name).write_text(plan_content)

        # Resolved verdict points to slug at step 1
        verdicts_resolved = tmp_path / "verdicts" / "resolved"
        verdicts_resolved.mkdir(parents=True)
        (verdicts_resolved / f"verdict-{slug}-step-1.md").write_text("continue\nApproved.")

        # Pending request file names proj_a as the owning project
        pending_dir = tmp_path / "verdicts" / "pending"
        pending_dir.mkdir(parents=True)
        pending_req = pending_dir / f"verdict-request-{slug}-step-1.md"
        pending_req.write_text(
            f"**Plan:** {proj_a_decisions / verdict_pending_name}\n"
            "**Step:** 1\n"
        )

        config = {
            "watched_projects": [str(proj_a_decisions), str(proj_b_decisions)],
            "default_model": "claude-sonnet-4-6",
            "pushover": {"app_key": "", "user_key": ""},
            "callback_port": 5999,
        }

        b = bellows.Bellows(config)

        with patch("bellows.BELLOWS_ROOT", tmp_path), \
             patch("bellows.verdict.check_verdict", return_value={
                 "found": True, "verdict": "continue", "reason": "approved"
             }), \
             patch("bellows.verdict.log_to_ledger"), \
             patch("bellows.notifier.push"), \
             patch.object(b, "handle_new_plan"):
            b._consume_verdicts()

        # Only proj_a's plan should have been consumed
        assert not (proj_a_decisions / verdict_pending_name).exists(), \
            "proj_a verdict-pending file should have been moved"
        assert (proj_b_decisions / verdict_pending_name).exists(), \
            "proj_b verdict-pending file must NOT be touched (scoped search)"


def test_consume_verdicts_fallback_to_all_watched_when_pending_missing():
    """_consume_verdicts falls back to searching all watched_projects when the
    pending request file is absent."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)

        decisions_dir = tmp_path / "proj" / "knowledge" / "decisions"
        decisions_dir.mkdir(parents=True)
        (decisions_dir / "Done").mkdir()

        slug = "fallback-2026-04-16"
        plan_filename = f"diagnostic-{slug}.md"
        verdict_pending_name = f"verdict-pending-{plan_filename}"
        (decisions_dir / verdict_pending_name).write_text("## Diagnostic\nSingle-step.\n")

        verdicts_resolved = tmp_path / "verdicts" / "resolved"
        verdicts_resolved.mkdir(parents=True)
        (verdicts_resolved / f"verdict-{slug}-step-1.md").write_text("continue\nApproved.")

        # No pending request file — pending dir exists but file is absent
        pending_dir = tmp_path / "verdicts" / "pending"
        pending_dir.mkdir(parents=True)

        config = {
            "watched_projects": [str(decisions_dir)],
            "default_model": "claude-sonnet-4-6",
            "pushover": {"app_key": "", "user_key": ""},
            "callback_port": 5999,
        }

        b = bellows.Bellows(config)

        with patch("bellows.BELLOWS_ROOT", tmp_path), \
             patch("bellows.verdict.check_verdict", return_value={
                 "found": True, "verdict": "continue", "reason": "approved"
             }), \
             patch("bellows.verdict.log_to_ledger"), \
             patch("bellows.notifier.push"), \
             patch.object(b, "handle_new_plan"):
            b._consume_verdicts()

        # Plan was still consumed via fallback
        assert not (decisions_dir / verdict_pending_name).exists(), \
            "plan should be consumed even without a pending request file (fallback)"


def test_consume_verdicts_break_prevents_double_consumption():
    """_consume_verdicts must consume only one plan per verdict even when multiple
    verdict-pending-* files in the same directory match the slug via substring."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)

        decisions_dir = tmp_path / "proj" / "knowledge" / "decisions"
        decisions_dir.mkdir(parents=True)
        (decisions_dir / "Done").mkdir()

        # Two files whose names both contain slug "overlap-2026-04-16"
        slug = "overlap-2026-04-16"
        file_a = f"verdict-pending-executable-{slug}.md"
        file_b = f"verdict-pending-diagnostic-{slug}.md"
        (decisions_dir / file_a).write_text("## STEP 1\nDo stuff.\n")
        (decisions_dir / file_b).write_text("## Diagnostic\nSingle-step.\n")

        verdicts_resolved = tmp_path / "verdicts" / "resolved"
        verdicts_resolved.mkdir(parents=True)
        (verdicts_resolved / f"verdict-{slug}-step-1.md").write_text("continue\nApproved.")

        # No pending request file → fallback, so both dirs (just one here) are searched
        pending_dir = tmp_path / "verdicts" / "pending"
        pending_dir.mkdir(parents=True)

        config = {
            "watched_projects": [str(decisions_dir)],
            "default_model": "claude-sonnet-4-6",
            "pushover": {"app_key": "", "user_key": ""},
            "callback_port": 5999,
        }

        b = bellows.Bellows(config)

        with patch("bellows.BELLOWS_ROOT", tmp_path), \
             patch("bellows.verdict.check_verdict", return_value={
                 "found": True, "verdict": "continue", "reason": "approved"
             }), \
             patch("bellows.verdict.log_to_ledger"), \
             patch("bellows.notifier.push"), \
             patch.object(b, "handle_new_plan"):
            b._consume_verdicts()

        # Exactly one of the two files should have been moved; the other stays
        a_exists = (decisions_dir / file_a).exists()
        b_exists = (decisions_dir / file_b).exists()
        consumed = [f for f, exists in [(file_a, a_exists), (file_b, b_exists)] if not exists]
        assert len(consumed) == 1, \
            f"Expected exactly 1 plan consumed, got {len(consumed)}: {consumed}"


# ---------------------------------------------------------------------------
# Parallel group deferred dispatch — settle window fix
# ---------------------------------------------------------------------------

def test_handle_parallel_from_watchdog_adds_pending_not_dispatched():
    """Parallel plan via on_created (from_rescan=False) must add to _pending_groups,
    not dispatch, and not add to _seen."""
    mock_orch = MagicMock()
    mock_orch._seen = set()
    handler = bellows.PlanHandler(mock_orch)

    with tempfile.TemporaryDirectory() as tmp:
        mock_orch.config = {"watched_projects": [tmp]}
        fname = "parallel-1-executable-foo-2026-04-16.md"
        path = os.path.join(tmp, fname)
        open(path, "w").close()

        handler._handle(path)  # default from_rescan=False

    assert "parallel-1" in handler._pending_groups
    assert verdict.slug_from_path(path) not in mock_orch._seen
    mock_orch.handle_parallel_group.assert_not_called()
    mock_orch.handle_new_plan.assert_not_called()


def test_rescan_dispatches_pending_group_after_settle():
    """_rescan must dispatch pending groups whose first-seen timestamp is > 5s ago."""
    with tempfile.TemporaryDirectory() as tmp:
        fname_a = "parallel-1-executable-foo-2026-04-16.md"
        fname_b = "parallel-1-executable-bar-2026-04-16.md"
        for fname in [fname_a, fname_b]:
            open(os.path.join(tmp, fname), "w").close()

        config = {"watched_projects": [tmp], "callback_port": 5999}
        b = bellows.Bellows(config)
        mock_orch = MagicMock()
        mock_orch.config = {"watched_projects": [tmp]}
        mock_orch._seen = set()
        handler = bellows.PlanHandler(mock_orch)
        # Simulate group first seen 10s ago (well past 5s settle window)
        handler._pending_groups["parallel-1"] = time.time() - 10

        with patch.object(b, "handle_parallel_group") as mock_dispatch, \
             patch.object(b, "_consume_verdicts"):
            b._rescan(handler)

        mock_dispatch.assert_called_once()
        dispatched_paths = mock_dispatch.call_args[0][0]
        assert len(dispatched_paths) == 2
        assert "parallel-1" not in handler._pending_groups


def test_rescan_does_not_dispatch_pending_group_within_settle():
    """_rescan must NOT dispatch pending groups whose first-seen timestamp is < 5s ago."""
    with tempfile.TemporaryDirectory() as tmp:
        fname = "parallel-1-executable-foo-2026-04-16.md"
        open(os.path.join(tmp, fname), "w").close()

        config = {"watched_projects": [tmp], "callback_port": 5999}
        b = bellows.Bellows(config)
        mock_orch = MagicMock()
        mock_orch.config = {"watched_projects": [tmp]}
        mock_orch._seen = set()
        handler = bellows.PlanHandler(mock_orch)
        # Simulate group first seen 1s ago (within 5s settle window)
        handler._pending_groups["parallel-1"] = time.time() - 1

        with patch.object(b, "handle_parallel_group") as mock_dispatch, \
             patch.object(b, "_consume_verdicts"):
            b._rescan(handler)

        mock_dispatch.assert_not_called()
        assert "parallel-1" in handler._pending_groups


def test_nonparallel_plan_dispatches_immediately_from_handle():
    """Non-parallel plan via _handle (from_rescan=False) must dispatch immediately."""
    mock_orch = MagicMock()
    mock_orch._seen = set()
    handler = bellows.PlanHandler(mock_orch)

    with tempfile.TemporaryDirectory() as tmp:
        mock_orch.config = {"watched_projects": [tmp]}
        fname = "executable-foo-2026-04-16.md"
        path = os.path.join(tmp, fname)
        open(path, "w").close()

        handler._handle(path)  # default from_rescan=False

    mock_orch.handle_new_plan.assert_called_once_with(path)
    assert verdict.slug_from_path(path) in mock_orch._seen
    assert handler._pending_groups == {}


def test_two_parallel_siblings_collected_as_one_group():
    """Two parallel siblings deferred to _pending_groups are dispatched together
    as one group after the settle window expires."""
    with tempfile.TemporaryDirectory() as tmp:
        fname_a = "parallel-1-executable-forge-annotation-2026-04-16.md"
        fname_b = "parallel-1-executable-forge-budget-2026-04-16.md"
        path_a = os.path.join(tmp, fname_a)
        path_b = os.path.join(tmp, fname_b)
        open(path_a, "w").close()
        open(path_b, "w").close()

        config = {"watched_projects": [tmp], "callback_port": 5999}
        b = bellows.Bellows(config)
        mock_orch = MagicMock()
        mock_orch.config = {"watched_projects": [tmp]}
        mock_orch._seen = set()
        handler = bellows.PlanHandler(mock_orch)

        # Simulate watchdog events: both files deferred
        handler._handle(path_a)  # adds group to _pending_groups
        handler._handle(path_b)  # group already present, returns immediately

        assert "parallel-1" in handler._pending_groups
        mock_orch.handle_parallel_group.assert_not_called()

        # Fast-forward: settle window expired
        handler._pending_groups["parallel-1"] = time.time() - 10

        dispatched_paths = []

        def capture_dispatch(paths):
            dispatched_paths.extend(paths)

        with patch.object(b, "handle_parallel_group", side_effect=capture_dispatch), \
             patch.object(b, "_consume_verdicts"):
            b._rescan(handler)

        assert len(dispatched_paths) == 2
        assert path_a in dispatched_paths
        assert path_b in dispatched_paths
        assert "parallel-1" not in handler._pending_groups


# ---------------------------------------------------------------------------
# Claim-at-entry — orphan original duplicate-dispatch fix
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


def _clean_gates(auto_close="true"):
    return {
        "passed": True,
        "failures": [],
        "is_qa_step": False,
        "files_changed": [],
        "plan_header": {"auto_close": auto_close},
        "verdict_requested": {"requested": False, "body": None},
    }


def test_run_plan_claims_file_before_runner_runs():
    """run_plan must move the original plan to in-progress- before calling runner.run_step."""
    with tempfile.TemporaryDirectory() as tmp:
        decisions_dir = os.path.join(tmp, "proj", "knowledge", "decisions")
        os.makedirs(decisions_dir)
        plan_filename = "executable-claim-test-2026-04-16.md"
        plan_path = os.path.join(decisions_dir, plan_filename)
        inprogress_path = os.path.join(decisions_dir, f"in-progress-{plan_filename}")
        with open(plan_path, "w") as f:
            f.write("## STEP 1\nDo stuff.\n")

        config = {
            "default_model": "claude-sonnet-4-6",
            "pushover": {"app_key": "", "user_key": ""},
            "callback_port": 5999,
            "step_timeout_seconds": 600,
        }

        claim_state = {}

        def fake_run_step(prompt, *args, **kwargs):
            claim_state["original_exists"] = os.path.exists(plan_path)
            claim_state["inprogress_exists"] = os.path.exists(inprogress_path)
            return _make_fake_run_step_result()

        with patch("bellows.runner.run_step", side_effect=fake_run_step), \
             patch("bellows.gates.check", return_value=_clean_gates()), \
             patch("bellows.notifier.push"), \
             patch("bellows.verdict.log_to_ledger"), \
             patch("bellows._capture_git_diff", return_value=""), \
             patch("bellows._create_worktree", return_value="/tmp/wt"), \
             patch("bellows._teardown_worktree"), \
             patch("bellows.record_run"), \
             patch("bellows.validators.validate_at_claim", return_value={"rejected": False, "reject_reason": "", "warnings": []}):
            response_server = MagicMock()
            bellows.run_plan(plan_path, config, response_server)

        assert not claim_state.get("original_exists", True), \
            "Original plan file must not exist when runner.run_step is called"
        assert claim_state.get("inprogress_exists", False), \
            "in-progress- file must exist when runner.run_step is called"


def test_run_plan_skips_claim_if_already_inprogress():
    """run_plan with an already-in-progress- plan skips the move (idempotent claim)."""
    with tempfile.TemporaryDirectory() as tmp:
        decisions_dir = os.path.join(tmp, "proj", "knowledge", "decisions")
        os.makedirs(decisions_dir)
        inprogress_filename = "in-progress-executable-idempotent-2026-04-16.md"
        inprogress_path = os.path.join(decisions_dir, inprogress_filename)
        double_prefix_path = os.path.join(decisions_dir, f"in-progress-{inprogress_filename}")
        with open(inprogress_path, "w") as f:
            f.write("## STEP 1\nDo stuff.\n")

        config = {
            "default_model": "claude-sonnet-4-6",
            "pushover": {"app_key": "", "user_key": ""},
            "callback_port": 5999,
            "step_timeout_seconds": 600,
        }

        with patch("bellows.runner.run_step", return_value=_make_fake_run_step_result()), \
             patch("bellows.gates.check", return_value=_clean_gates()), \
             patch("bellows.notifier.push"), \
             patch("bellows.verdict.log_to_ledger"), \
             patch("bellows._capture_git_diff", return_value=""), \
             patch("bellows._create_worktree", return_value="/tmp/wt"), \
             patch("bellows._teardown_worktree"), \
             patch("bellows.record_run"):
            response_server = MagicMock()
            bellows.run_plan(inprogress_path, config, response_server)

        assert not os.path.exists(double_prefix_path), \
            f"Must not create double in-progress- file: {double_prefix_path}"


def test_run_plan_bootstrap_prompt_uses_shadow_path():
    """Bootstrap prompt passed to runner must reference the shadow cache path, not the in-progress path."""
    with tempfile.TemporaryDirectory() as tmp:
        decisions_dir = os.path.join(tmp, "proj", "knowledge", "decisions")
        os.makedirs(decisions_dir)
        plan_filename = "executable-bootstrap-prompt-2026-04-16.md"
        plan_path = os.path.join(decisions_dir, plan_filename)
        with open(plan_path, "w") as f:
            f.write("## STEP 1\nDo stuff.\n")

        config = {
            "default_model": "claude-sonnet-4-6",
            "pushover": {"app_key": "", "user_key": ""},
            "callback_port": 5999,
            "step_timeout_seconds": 600,
        }

        captured_prompts = []

        def fake_run_step(prompt, *args, **kwargs):
            captured_prompts.append(prompt)
            return _make_fake_run_step_result()

        with patch("bellows.runner.run_step", side_effect=fake_run_step), \
             patch("bellows.gates.check", return_value=_clean_gates()), \
             patch("bellows.notifier.push"), \
             patch("bellows.verdict.log_to_ledger"), \
             patch("bellows._capture_git_diff", return_value=""), \
             patch("bellows._create_worktree", return_value="/tmp/wt"), \
             patch("bellows._teardown_worktree"), \
             patch("bellows.record_run"), \
             patch("bellows.validators.validate_at_claim", return_value={"rejected": False, "reject_reason": "", "warnings": []}):
            response_server = MagicMock()
            bellows.run_plan(plan_path, config, response_server)

        assert len(captured_prompts) >= 1
        bootstrap = captured_prompts[0]
        assert ".bellows-cache/" in bootstrap, \
            f"Bootstrap must reference shadow cache path. Got: {bootstrap!r}"
        assert ".pristine" in bootstrap, \
            f"Bootstrap must reference .pristine shadow file. Got: {bootstrap!r}"
        assert "in-progress-" not in bootstrap, \
            f"Bootstrap must NOT reference in-progress- path. Got: {bootstrap!r}"


def test_run_plan_continuation_prompt_uses_shadow_path():
    """Mid-loop continuation prompt must reference the shadow cache path, not in-progress path."""
    with tempfile.TemporaryDirectory() as tmp:
        decisions_dir = os.path.join(tmp, "proj", "knowledge", "decisions")
        os.makedirs(decisions_dir)
        plan_filename = "executable-cont-shadow-2026-04-19.md"
        plan_path = os.path.join(decisions_dir, plan_filename)
        with open(plan_path, "w") as f:
            f.write("## STEP 1\nDo stuff.\n## STEP 2\nDo more stuff.\n")

        config = {
            "default_model": "claude-sonnet-4-6",
            "pushover": {"app_key": "", "user_key": ""},
            "callback_port": 5999,
            "step_timeout_seconds": 600,
        }

        captured_prompts = []

        def fake_run_step(prompt, *args, **kwargs):
            captured_prompts.append(prompt)
            return _make_fake_run_step_result()

        # Use a non-sparse plan_header (>= 3 keys) so _apply_defensive_header_defaults
        # doesn't inject pause_for_verdict — this test is about shadow path, not pause behavior.
        advance_gates = _clean_gates()
        advance_gates["plan_header"] = {"auto_close": "true", "pause_for_verdict": "never", "Total Steps": "2"}

        with patch("bellows.runner.run_step", side_effect=fake_run_step), \
             patch("bellows.gates.check", return_value=advance_gates), \
             patch("bellows.notifier.push"), \
             patch("bellows.verdict.log_to_ledger"), \
             patch("bellows._capture_git_diff", return_value=""), \
             patch("bellows._create_worktree", return_value="/tmp/wt"), \
             patch("bellows._teardown_worktree"), \
             patch("bellows.record_run"), \
             patch("bellows.validators.validate_at_claim", return_value={"rejected": False, "reject_reason": "", "warnings": []}):
            response_server = MagicMock()
            bellows.run_plan(plan_path, config, response_server)

        assert len(captured_prompts) >= 2, \
            f"Expected at least 2 prompts (bootstrap + continuation). Got {len(captured_prompts)}"
        continuation = captured_prompts[1]
        assert ".bellows-cache/" in continuation, \
            f"Continuation prompt must reference shadow cache path. Got: {continuation!r}"
        assert ".pristine" in continuation, \
            f"Continuation prompt must reference .pristine shadow file. Got: {continuation!r}"
        assert "in-progress-" not in continuation, \
            f"Continuation prompt must NOT reference in-progress- path. Got: {continuation!r}"
        assert "Step 2" in continuation, \
            f"Continuation prompt must reference Step 2. Got: {continuation!r}"


def test_run_plan_diagnostic_prompt_uses_shadow_path():
    """Diagnostic bootstrap prompt must reference the shadow cache path."""
    with tempfile.TemporaryDirectory() as tmp:
        decisions_dir = os.path.join(tmp, "proj", "knowledge", "decisions")
        os.makedirs(decisions_dir)
        plan_filename = "diagnostic-shadow-test-2026-04-19.md"
        plan_path = os.path.join(decisions_dir, plan_filename)
        with open(plan_path, "w") as f:
            f.write("## STEP 1\nInvestigate stuff.\n")

        config = {
            "default_model": "claude-sonnet-4-6",
            "pushover": {"app_key": "", "user_key": ""},
            "callback_port": 5999,
            "step_timeout_seconds": 600,
        }

        captured_prompts = []

        def fake_run_step(prompt, *args, **kwargs):
            captured_prompts.append(prompt)
            return _make_fake_run_step_result()

        with patch("bellows.runner.run_step", side_effect=fake_run_step), \
             patch("bellows.gates.check", return_value=_clean_gates(auto_close="false")), \
             patch("bellows.notifier.push"), \
             patch("bellows.notifier.notify_verdict_request"), \
             patch("bellows.verdict.log_to_ledger"), \
             patch("bellows.verdict.post_verdict_request"), \
             patch("bellows._capture_git_diff", return_value=""), \
             patch("bellows._create_worktree", return_value="/tmp/wt"), \
             patch("bellows._teardown_worktree"), \
             patch("bellows.record_run"), \
             patch("bellows.validators.validate_at_claim", return_value={"rejected": False, "reject_reason": "", "warnings": []}):
            response_server = MagicMock()
            bellows.run_plan(plan_path, config, response_server)

        assert len(captured_prompts) >= 1
        bootstrap = captured_prompts[0]
        assert "Read the diagnostic at" in bootstrap, \
            f"Diagnostic prompt must start with 'Read the diagnostic at'. Got: {bootstrap!r}"
        assert ".bellows-cache/" in bootstrap, \
            f"Diagnostic prompt must reference shadow cache path. Got: {bootstrap!r}"
        assert ".pristine" in bootstrap, \
            f"Diagnostic prompt must reference .pristine shadow file. Got: {bootstrap!r}"


def test_run_plan_resume_prompt_uses_shadow_path():
    """Resume bootstrap prompt (verdict-continue path) must reference the shadow cache path."""
    with tempfile.TemporaryDirectory() as tmp:
        decisions_dir = os.path.join(tmp, "proj", "knowledge", "decisions")
        os.makedirs(decisions_dir)
        plan_filename = "executable-resume-shadow-2026-04-19.md"
        inprogress_filename = f"in-progress-{plan_filename}"
        inprogress_path = os.path.join(decisions_dir, inprogress_filename)
        with open(inprogress_path, "w") as f:
            f.write("## STEP 1\nDo stuff.\n## STEP 2\nDo more stuff.\n")

        config = {
            "default_model": "claude-sonnet-4-6",
            "pushover": {"app_key": "", "user_key": ""},
            "callback_port": 5999,
            "step_timeout_seconds": 600,
        }

        captured_prompts = []

        def fake_run_step(prompt, *args, **kwargs):
            captured_prompts.append(prompt)
            return _make_fake_run_step_result()

        with patch("bellows.runner.run_step", side_effect=fake_run_step), \
             patch("bellows.gates.check", return_value=_clean_gates()), \
             patch("bellows.notifier.push"), \
             patch("bellows.verdict.log_to_ledger"), \
             patch("bellows._capture_git_diff", return_value=""), \
             patch("bellows._create_worktree", return_value="/tmp/wt"), \
             patch("bellows._teardown_worktree"), \
             patch("bellows.record_run"):
            response_server = MagicMock()
            bellows.run_plan(inprogress_path, config, response_server, resume_step=2)

        assert len(captured_prompts) >= 1
        bootstrap = captured_prompts[0]
        assert ".bellows-cache/" in bootstrap, \
            f"Resume prompt must reference shadow cache path. Got: {bootstrap!r}"
        assert ".pristine" in bootstrap, \
            f"Resume prompt must reference .pristine shadow file. Got: {bootstrap!r}"
        assert "Step 2" in bootstrap, \
            f"Resume prompt must reference Step 2. Got: {bootstrap!r}"


def test_shadow_path_resolves_after_claim():
    """After run_plan claims a plan, the shadow file must exist with pristine content."""
    with tempfile.TemporaryDirectory() as tmp:
        decisions_dir = os.path.join(tmp, "proj", "knowledge", "decisions")
        os.makedirs(decisions_dir)
        plan_filename = "executable-shadow-resolve-2026-04-19.md"
        plan_path = os.path.join(decisions_dir, plan_filename)
        plan_content = "## STEP 1\nDo stuff.\n"
        with open(plan_path, "w") as f:
            f.write(plan_content)

        config = {
            "default_model": "claude-sonnet-4-6",
            "pushover": {"app_key": "", "user_key": ""},
            "callback_port": 5999,
            "step_timeout_seconds": 600,
        }

        shadow_state = {}

        def fake_run_step(prompt, *args, **kwargs):
            # Capture shadow file state during execution (before auto-close deletes it)
            shadow_file = bellows._shadow_path(plan_filename)
            shadow_state["exists"] = shadow_file.exists()
            if shadow_file.exists():
                shadow_state["content"] = shadow_file.read_text()
            return _make_fake_run_step_result()

        with patch("bellows.runner.run_step", side_effect=fake_run_step), \
             patch("bellows.gates.check", return_value=_clean_gates()), \
             patch("bellows.notifier.push"), \
             patch("bellows.verdict.log_to_ledger"), \
             patch("bellows._capture_git_diff", return_value=""), \
             patch("bellows._create_worktree", return_value="/tmp/wt"), \
             patch("bellows._teardown_worktree"), \
             patch("bellows.record_run"), \
             patch("bellows.validators.validate_at_claim", return_value={"rejected": False, "reject_reason": "", "warnings": []}):
            response_server = MagicMock()
            bellows.run_plan(plan_path, config, response_server)

        assert shadow_state.get("exists", False), \
            "Shadow file must exist after claim, during runner execution"
        assert shadow_state.get("content") == plan_content, \
            f"Shadow content must match original plan. Got: {shadow_state.get('content')!r}"


# ---------------------------------------------------------------------------
# on_moved handler — BACKLOG #4 watcher reliability fix
# ---------------------------------------------------------------------------

def test_on_moved_dispatches_for_non_directory_event():
    """on_moved must call _handle with event.dest_path for non-directory events."""
    mock_orch = MagicMock()
    mock_orch.config = {"watched_projects": ["/some/decisions"]}
    handler = bellows.PlanHandler(mock_orch)

    event = MagicMock()
    event.is_directory = False
    event.src_path = "/some/decisions/verdict-pending-foo.md"
    event.dest_path = "/some/decisions/executable-foo.md"

    with patch.object(handler, "_handle") as mock_handle:
        handler.on_moved(event)

    mock_handle.assert_called_once_with("/some/decisions/executable-foo.md")


def test_on_moved_ignores_directory_events():
    """on_moved must NOT call _handle for directory events."""
    mock_orch = MagicMock()
    handler = bellows.PlanHandler(mock_orch)

    event = MagicMock()
    event.is_directory = True
    event.src_path = "/some/decisions/old_dir"
    event.dest_path = "/some/decisions/new_dir"

    with patch.object(handler, "_handle") as mock_handle:
        handler.on_moved(event)

    mock_handle.assert_not_called()


def test_on_moved_dispatches_for_top_level_dest():
    """on_moved with dest_path in a watched directory must call _handle."""
    mock_orch = MagicMock()
    mock_orch.config = {"watched_projects": ["/proj/knowledge/decisions"]}
    handler = bellows.PlanHandler(mock_orch)

    event = MagicMock()
    event.is_directory = False
    event.src_path = "/proj/knowledge/decisions/verdict-pending-foo.md"
    event.dest_path = "/proj/knowledge/decisions/executable-foo.md"

    with patch.object(handler, "_handle") as mock_handle:
        handler.on_moved(event)

    mock_handle.assert_called_once_with("/proj/knowledge/decisions/executable-foo.md")


def test_on_moved_rejects_subdirectory_dest():
    """on_moved with dest_path in a subdirectory (e.g. Done/) must be rejected by _handle guard."""
    mock_orch = MagicMock()
    mock_orch.config = {"watched_projects": ["/proj/knowledge/decisions"]}
    handler = bellows.PlanHandler(mock_orch)

    event = MagicMock()
    event.is_directory = False
    event.src_path = "/proj/knowledge/decisions/executable-foo.md"
    event.dest_path = "/proj/knowledge/decisions/Done/executable-foo.md"

    handler.on_moved(event)

    # Guard in _handle rejects Done/ subdirectory — no dispatch
    mock_orch.handle_new_plan.assert_not_called()
    mock_orch.handle_parallel_group.assert_not_called()


def test_on_moved_dispatches_same_directory_rename():
    """on_moved with src and dest both in watched dir (rename) must call _handle."""
    mock_orch = MagicMock()
    mock_orch.config = {"watched_projects": ["/proj/knowledge/decisions"]}
    handler = bellows.PlanHandler(mock_orch)

    event = MagicMock()
    event.is_directory = False
    event.src_path = "/proj/knowledge/decisions/executable-old.md"
    event.dest_path = "/proj/knowledge/decisions/executable-new.md"

    with patch.object(handler, "_handle") as mock_handle:
        handler.on_moved(event)

    mock_handle.assert_called_once_with("/proj/knowledge/decisions/executable-new.md")


def test_is_runnable_plan_inprogress_executable_returns_false():
    """Regression guard: is_runnable_plan must return False for in-progress-executable-* files."""
    assert bellows.is_runnable_plan("in-progress-executable-foo-2026-04-16.md") is False
    assert bellows.is_runnable_plan("in-progress-diagnostic-bar-2026-04-16.md") is False
    assert bellows.is_runnable_plan("in-progress-parallel-1-executable-baz-2026-04-16.md") is False


# ---------------------------------------------------------------------------
# qa- prefix dispatch + silent-skip logging
# ---------------------------------------------------------------------------

def test_is_runnable_plan_qa_prefix():
    """is_runnable_plan accepts qa- prefixed plans."""
    assert bellows.is_runnable_plan("qa-foo-2026-05-08.md") is True


def test_is_runnable_plan_parallel_qa_prefix():
    """is_runnable_plan accepts parallel-N-qa- prefixed plans."""
    assert bellows.is_runnable_plan("parallel-1-qa-foo-2026-05-08.md") is True


def test_is_runnable_plan_rejects_roadmap():
    """is_runnable_plan rejects roadmap- prefixed files (not dispatchable)."""
    assert bellows.is_runnable_plan("roadmap-foo-2026-05-08.md") is False


def test_is_runnable_plan_rejects_staging():
    """is_runnable_plan rejects _staging- prefixed files."""
    assert bellows.is_runnable_plan("_staging-foo-2026-05-08.md") is False


def test_skip_logging_fires_once(capsys):
    """PlanHandler._handle logs a warning for unrecognized .md prefix, once only."""
    mock_orch = MagicMock()
    mock_orch._seen = set()

    with tempfile.TemporaryDirectory() as tmp:
        mock_orch.config = {"watched_projects": [tmp]}
        handler = bellows.PlanHandler(mock_orch)

        fname = "unknown-foo.md"
        path = os.path.join(tmp, fname)
        open(path, "w").close()

        handler._handle(path)
        captured = capsys.readouterr()
        assert "skipped" in captured.out and "[unknown-foo]" in captured.out
        assert "prefix not in dispatch whitelist" in captured.out


def test_skip_logging_deduplication(capsys):
    """PlanHandler._handle does NOT repeat the skip warning on the same file."""
    mock_orch = MagicMock()
    mock_orch._seen = set()

    with tempfile.TemporaryDirectory() as tmp:
        mock_orch.config = {"watched_projects": [tmp]}
        handler = bellows.PlanHandler(mock_orch)

        fname = "unknown-foo.md"
        path = os.path.join(tmp, fname)
        open(path, "w").close()

        handler._handle(path)
        capsys.readouterr()  # clear first invocation output

        handler._handle(path)
        captured = capsys.readouterr()
        assert "skipped" not in captured.out, "Skip warning must not repeat for the same file"


# ---------------------------------------------------------------------------
# Bug 1 — _consume_verdicts plan_matched gate
# ---------------------------------------------------------------------------

def test_consume_verdicts_no_match_leaves_in_resolved():
    """Bug 1: verdict whose slug matches no verdict-pending plan stays in resolved/."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)

        decisions_dir = tmp_path / "proj" / "knowledge" / "decisions"
        decisions_dir.mkdir(parents=True)
        (decisions_dir / "Done").mkdir()
        # No verdict-pending-* file exists

        verdicts_resolved = tmp_path / "verdicts" / "resolved"
        verdicts_resolved.mkdir(parents=True)
        verdict_fname = "verdict-orphan-slug-2026-04-24-step-1.md"
        (verdicts_resolved / verdict_fname).write_text("continue\nApproved.")

        config = {
            "watched_projects": [str(decisions_dir)],
            "default_model": "claude-sonnet-4-6",
            "pushover": {"app_key": "", "user_key": ""},
            "callback_port": 5999,
        }

        b = bellows.Bellows(config)

        with patch("bellows.BELLOWS_ROOT", tmp_path), \
             patch("bellows.verdict.check_verdict", return_value={
                 "found": True, "verdict": "continue", "reason": "approved"
             }):
            b._consume_verdicts()

        # Verdict must remain in resolved/ — NOT moved to processed-*
        assert (verdicts_resolved / verdict_fname).exists(), \
            "Verdict with no matching plan should stay in resolved/"
        assert not (verdicts_resolved / f"processed-{verdict_fname}").exists(), \
            "Verdict should NOT be moved to processed when no plan matched"


def test_consume_verdicts_stale_verdict_plan_in_done_moves_to_processed():
    """Bug 1: verdict whose slug matches a plan in Done/ is moved to processed (stale verdict)."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)

        decisions_dir = tmp_path / "proj" / "knowledge" / "decisions"
        decisions_dir.mkdir(parents=True)
        done_dir = decisions_dir / "Done"
        done_dir.mkdir()
        # Plan is already in Done/ — no verdict-pending-* exists
        (done_dir / "executable-stale-plan-2026-04-24.md").write_text("## STEP 1\nDone.\n")

        verdicts_resolved = tmp_path / "verdicts" / "resolved"
        verdicts_resolved.mkdir(parents=True)
        verdict_fname = "verdict-stale-plan-2026-04-24-step-1.md"
        (verdicts_resolved / verdict_fname).write_text("continue\nApproved.")

        config = {
            "watched_projects": [str(decisions_dir)],
            "default_model": "claude-sonnet-4-6",
            "pushover": {"app_key": "", "user_key": ""},
            "callback_port": 5999,
        }

        b = bellows.Bellows(config)

        with patch("bellows.BELLOWS_ROOT", tmp_path), \
             patch("bellows.verdict.check_verdict", return_value={
                 "found": True, "verdict": "continue", "reason": "approved"
             }):
            b._consume_verdicts()

        # Stale verdict should be moved to processed (plan is in Done/)
        assert not (verdicts_resolved / verdict_fname).exists(), \
            "Stale verdict should be removed from resolved/"
        assert (verdicts_resolved / f"processed-{verdict_fname}").exists(), \
            "Stale verdict should be moved to processed-*"


def test_consume_verdicts_match_still_moves_to_processed():
    """Bug 1 regression guard: verdict with matching verdict-pending plan still moves to processed."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)

        decisions_dir = tmp_path / "proj" / "knowledge" / "decisions"
        decisions_dir.mkdir(parents=True)
        done_dir = decisions_dir / "Done"
        done_dir.mkdir()

        plan_filename = "diagnostic-matched-2026-04-24.md"
        verdict_pending_path = decisions_dir / f"verdict-pending-{plan_filename}"
        verdict_pending_path.write_text("## Diagnostic\nSingle-step.\n")

        verdicts_resolved = tmp_path / "verdicts" / "resolved"
        verdicts_resolved.mkdir(parents=True)
        verdict_fname = "verdict-matched-2026-04-24-step-1.md"
        (verdicts_resolved / verdict_fname).write_text("continue\nApproved.")

        config = {
            "watched_projects": [str(decisions_dir)],
            "default_model": "claude-sonnet-4-6",
            "pushover": {"app_key": "", "user_key": ""},
            "callback_port": 5999,
        }

        b = bellows.Bellows(config)

        with patch("bellows.BELLOWS_ROOT", tmp_path), \
             patch("bellows.verdict.check_verdict", return_value={
                 "found": True, "verdict": "continue", "reason": "approved"
             }), \
             patch("bellows.verdict.log_to_ledger"), \
             patch("bellows.notifier.push"):
            b._consume_verdicts()

        # Verdict should be moved to processed (match found)
        assert not (verdicts_resolved / verdict_fname).exists(), \
            "Matched verdict should be removed from resolved/"
        assert (verdicts_resolved / f"processed-{verdict_fname}").exists(), \
            "Matched verdict should be moved to processed-*"


# ---------------------------------------------------------------------------
# Bug 2 — pause-rename canonical path (base_filename)
# ---------------------------------------------------------------------------

def test_run_plan_inprogress_entry_renames_to_verdict_pending():
    """Bug 2: plan entering run_plan with in-progress- prefix renames to
    verdict-pending-{base_name}, NOT verdict-pending-in-progress-{name}."""
    with tempfile.TemporaryDirectory() as tmp:
        decisions_dir = os.path.join(tmp, "proj", "knowledge", "decisions")
        os.makedirs(decisions_dir)
        base_name = "executable-bug2-test-2026-04-24.md"
        inprogress_name = f"in-progress-{base_name}"
        plan_path = os.path.join(decisions_dir, inprogress_name)
        with open(plan_path, "w") as f:
            f.write("## STEP 1\nDo stuff.\n## STEP 2\nMore stuff.\n")

        config = {
            "default_model": "claude-sonnet-4-6",
            "pushover": {"app_key": "", "user_key": ""},
            "callback_port": 5999,
            "step_timeout_seconds": 600,
        }

        # Gates fail to trigger the pause branch
        failing_gates = {
            "passed": False,
            "failures": [{"gate": "scope_check", "evidence": "test fixture for scope_check failure"}],
            "is_qa_step": False,
            "files_changed": [],
            "plan_header": {},
            "verdict_requested": {"requested": False, "body": None},
        }

        with patch("bellows.runner.run_step", return_value=_make_fake_run_step_result()), \
             patch("bellows.gates.check", return_value=failing_gates), \
             patch("bellows.notifier.push"), \
             patch("bellows.notifier.notify_verdict_request"), \
             patch("bellows.verdict.post_verdict_request"), \
             patch("bellows._capture_git_diff", return_value=""), \
             patch("bellows._create_worktree", return_value="/tmp/wt"), \
             patch("bellows._teardown_worktree"), \
             patch("bellows.record_run"):
            response_server = MagicMock()
            bellows.run_plan(plan_path, config, response_server)

        # Correct: verdict-pending-executable-bug2-test-2026-04-24.md
        expected = os.path.join(decisions_dir, f"verdict-pending-{base_name}")
        assert os.path.exists(expected), \
            f"Expected {expected} to exist after pause"

        # Wrong: verdict-pending-in-progress-executable-bug2-test-2026-04-24.md
        wrong = os.path.join(decisions_dir, f"verdict-pending-{inprogress_name}")
        assert not os.path.exists(wrong), \
            f"Double-prefix file should NOT exist: {wrong}"


def test_run_plan_inprogress_entry_no_double_prefix():
    """Bug 2: inprogress_path must NOT have double in-progress-in-progress- prefix."""
    with tempfile.TemporaryDirectory() as tmp:
        decisions_dir = os.path.join(tmp, "proj", "knowledge", "decisions")
        os.makedirs(decisions_dir)
        base_name = "executable-prefix-test-2026-04-24.md"
        inprogress_name = f"in-progress-{base_name}"
        plan_path = os.path.join(decisions_dir, inprogress_name)
        with open(plan_path, "w") as f:
            f.write("## STEP 1\nDo stuff.\n")

        config = {
            "default_model": "claude-sonnet-4-6",
            "pushover": {"app_key": "", "user_key": ""},
            "callback_port": 5999,
            "step_timeout_seconds": 600,
        }

        captured_inprogress_path = {}

        original_run_step = None
        def capture_inprogress(prompt, proj, model, **kwargs):
            # After run_plan constructs inprogress_path, check the file exists
            # The in-progress file should be the single-prefix version
            single = os.path.join(decisions_dir, inprogress_name)
            double = os.path.join(decisions_dir, f"in-progress-{inprogress_name}")
            captured_inprogress_path["single_exists"] = os.path.exists(single)
            captured_inprogress_path["double_exists"] = os.path.exists(double)
            return _make_fake_run_step_result()

        clean_gates = {
            "passed": True,
            "failures": [],
            "is_qa_step": False,
            "files_changed": [],
            "plan_header": {},
            "verdict_requested": {"requested": False, "body": None},
        }

        with patch("bellows.runner.run_step", side_effect=capture_inprogress), \
             patch("bellows.gates.check", return_value=clean_gates), \
             patch("bellows.notifier.push"), \
             patch("bellows.notifier.notify_verdict_request"), \
             patch("bellows.verdict.post_verdict_request"), \
             patch("bellows._capture_git_diff", return_value=""), \
             patch("bellows._create_worktree", return_value="/tmp/wt"), \
             patch("bellows._teardown_worktree"), \
             patch("bellows.record_run"):
            response_server = MagicMock()
            bellows.run_plan(plan_path, config, response_server)

        assert captured_inprogress_path.get("single_exists") is True, \
            "Single-prefix in-progress file should exist"
        assert captured_inprogress_path.get("double_exists") is False, \
            "Double-prefix in-progress-in-progress file should NOT exist"


# ---------------------------------------------------------------------------
# Bug 3 — case-insensitive extract_total_steps
# ---------------------------------------------------------------------------

def test_extract_total_steps_mixed_case():
    """Bug 3: ## Step 1 — X should be counted."""
    assert bellows.extract_total_steps("## Step 1 — Foo\nContent.\n## Step 2 — Bar\n") == 2


def test_extract_total_steps_lowercase():
    """Bug 3: ## step 1 — X should be counted."""
    assert bellows.extract_total_steps("## step 1 — Foo\n") == 1


def test_extract_total_steps_uppercase_unchanged():
    """Bug 3 regression guard: ## STEP 1 — X still works."""
    assert bellows.extract_total_steps("## STEP 1 — Foo\n## STEP 2 — Bar\n## STEP 3 — Baz\n") == 3


def test_extract_total_steps_requires_number():
    """Bug 3: ## Step-by-step approach should NOT count as a step."""
    assert bellows.extract_total_steps("## Step-by-step approach\nContent.\n") == 0


def test_extract_total_steps_case_mismatch_warning(capsys):
    """Bug 3: warning fires when mixed case is used instead of uppercase."""
    bellows.extract_total_steps("## Step 1 — Mixed\n")
    captured = capsys.readouterr()
    assert "[WARN]" in captured.out
    assert "case does not match" in captured.out


def test_strip_fenced_code_blocks_basic():
    """Utility unit test: fenced content stripped, non-fence content preserved."""
    text = (
        "Before fence.\n"
        "\n"
        "```python\n"
        "code = True\n"
        "more_code = False\n"
        "```\n"
        "\n"
        "After fence.\n"
    )
    result = bellows.strip_fenced_code_blocks(text)
    assert "code = True" not in result
    assert "more_code = False" not in result
    assert "Before fence." in result
    assert "After fence." in result


def test_extract_total_steps_ignores_in_fence_headers():
    """Regression: in-fence ## STEP N patterns must not be counted."""
    fixture = (
        "## STEP 1 — Real Step One\n"
        "\n"
        "Do something real.\n"
        "\n"
        "```python\n"
        'FIXTURE = """\n'
        "## STEP 1 — Example Fixture Step\n"
        "Do example stuff.\n"
        "\n"
        "## STEP 2 — Example Fixture Step\n"
        'More example.\n'
        '"""\n'
        "```\n"
        "\n"
        "## STEP 2 — Real Step Two\n"
        "\n"
        "Do something else.\n"
    )
    assert bellows.extract_total_steps(fixture) == 2


# ---------------------------------------------------------------------------
# Phase 3b — DB-based step state recovery + plan_slug column (BACKLOG #6)
# ---------------------------------------------------------------------------

import sqlite3


def _create_test_db(db_path: str):
    """Create a runs table matching the current schema for testing."""
    conn = sqlite3.connect(db_path)
    conn.execute(
        """CREATE TABLE IF NOT EXISTS runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            plan_path TEXT,
            project TEXT,
            session_id TEXT,
            step INTEGER,
            status TEXT,
            cost REAL,
            plan_slug TEXT
        )"""
    )
    conn.commit()
    conn.close()


def test_record_run_stores_plan_slug():
    """Phase 3b: record_run stores plan_slug in the DB."""
    with tempfile.TemporaryDirectory() as tmp:
        db_path = os.path.join(tmp, "test.db")
        bellows.record_run(
            db_path, "/path/plan.md", "proj", "sess1", 1, "Complete", 0.05, "my-plan-slug"
        )
        conn = sqlite3.connect(db_path)
        row = conn.execute("SELECT plan_slug FROM runs WHERE step = 1").fetchone()
        conn.close()
        assert row is not None
        assert row[0] == "my-plan-slug"


# ---------------------------------------------------------------------------
# Per-plan worktree — unit tests (Plan 2)
# ---------------------------------------------------------------------------


def test_run_plan_creates_worktree_before_pre_diff():
    """Worktree creation must happen before the first _capture_git_diff call."""
    with tempfile.TemporaryDirectory() as tmp:
        decisions_dir = os.path.join(tmp, "proj", "knowledge", "decisions")
        os.makedirs(decisions_dir)
        plan_filename = "executable-wt-order-2026-05-03.md"
        plan_path = os.path.join(decisions_dir, plan_filename)
        with open(plan_path, "w") as f:
            f.write("## STEP 1\nDo stuff.\n")

        config = {
            "default_model": "claude-sonnet-4-6",
            "pushover": {"app_key": "", "user_key": ""},
            "callback_port": 5999,
            "step_timeout_seconds": 600,
        }

        call_order = []

        def track_create_worktree(project_path, slug):
            call_order.append("create_worktree")
            return "/tmp/wt-sentinel"

        def track_capture_diff(path):
            call_order.append("capture_git_diff")
            return ""

        with patch("bellows._create_worktree", side_effect=track_create_worktree), \
             patch("bellows._capture_git_diff", side_effect=track_capture_diff), \
             patch("bellows._teardown_worktree"), \
             patch("bellows.runner.run_step", return_value=_make_fake_run_step_result()), \
             patch("bellows.gates.check", return_value=_clean_gates()), \
             patch("bellows.notifier.push"), \
             patch("bellows.verdict.log_to_ledger"), \
             patch("bellows.record_run"), \
             patch("bellows.validators.validate_at_claim", return_value={"rejected": False, "reject_reason": "", "warnings": []}):
            response_server = MagicMock()
            bellows.run_plan(plan_path, config, response_server)

        assert "create_worktree" in call_order
        assert "capture_git_diff" in call_order
        wt_idx = call_order.index("create_worktree")
        diff_idx = call_order.index("capture_git_diff")
        assert wt_idx < diff_idx, \
            f"_create_worktree (index {wt_idx}) must precede _capture_git_diff (index {diff_idx})"


def test_run_plan_passes_wt_path_to_capture_and_runner():
    """run_plan must route _capture_git_diff and runner.run_step through the worktree path."""
    with tempfile.TemporaryDirectory() as tmp:
        decisions_dir = os.path.join(tmp, "proj", "knowledge", "decisions")
        os.makedirs(decisions_dir)
        plan_filename = "executable-wt-path-2026-05-03.md"
        plan_path = os.path.join(decisions_dir, plan_filename)
        with open(plan_path, "w") as f:
            f.write("## STEP 1\nDo stuff.\n")

        config = {
            "default_model": "claude-sonnet-4-6",
            "pushover": {"app_key": "", "user_key": ""},
            "callback_port": 5999,
            "step_timeout_seconds": 600,
        }

        with patch("bellows._create_worktree", return_value="WT_PATH_SENTINEL"), \
             patch("bellows._capture_git_diff", return_value="") as mock_capture, \
             patch("bellows._teardown_worktree"), \
             patch("bellows.runner.run_step", return_value=_make_fake_run_step_result()) as mock_runner, \
             patch("bellows.gates.check", return_value=_clean_gates()), \
             patch("bellows.notifier.push"), \
             patch("bellows.verdict.log_to_ledger"), \
             patch("bellows.record_run"), \
             patch("bellows.validators.validate_at_claim", return_value={"rejected": False, "reject_reason": "", "warnings": []}):
            response_server = MagicMock()
            bellows.run_plan(plan_path, config, response_server)

        # _capture_git_diff must receive the worktree path, not the project path
        for call in mock_capture.call_args_list:
            assert call[0][0] == "WT_PATH_SENTINEL", \
                f"_capture_git_diff called with {call[0][0]!r}, expected 'WT_PATH_SENTINEL'"

        # runner.run_step second positional arg must be the worktree path
        assert mock_runner.call_count >= 1
        for call in mock_runner.call_args_list:
            assert call[0][1] == "WT_PATH_SENTINEL", \
                f"runner.run_step project_path={call[0][1]!r}, expected 'WT_PATH_SENTINEL'"


def test_run_plan_tears_down_worktree_after_final_gate():
    """Teardown must happen after gates.check and before Done move on auto-close."""
    with tempfile.TemporaryDirectory() as tmp:
        decisions_dir = os.path.join(tmp, "proj", "knowledge", "decisions")
        os.makedirs(decisions_dir)
        plan_filename = "executable-wt-teardown-order-2026-05-03.md"
        plan_path = os.path.join(decisions_dir, plan_filename)
        with open(plan_path, "w") as f:
            f.write("## STEP 1\nDo stuff.\n")

        config = {
            "default_model": "claude-sonnet-4-6",
            "pushover": {"app_key": "", "user_key": ""},
            "callback_port": 5999,
            "step_timeout_seconds": 600,
        }

        call_order = []

        def track_gates_check(*args, **kwargs):
            call_order.append("gates_check")
            return _clean_gates()

        def track_teardown(*args, **kwargs):
            call_order.append("teardown")

        with patch("bellows._create_worktree", return_value="/tmp/wt"), \
             patch("bellows._capture_git_diff", return_value=""), \
             patch("bellows._teardown_worktree", side_effect=track_teardown), \
             patch("bellows.runner.run_step", return_value=_make_fake_run_step_result()), \
             patch("bellows.gates.check", side_effect=track_gates_check), \
             patch("bellows.notifier.push"), \
             patch("bellows.verdict.log_to_ledger"), \
             patch("bellows.record_run"), \
             patch("bellows.validators.validate_at_claim", return_value={"rejected": False, "reject_reason": "", "warnings": []}):
            response_server = MagicMock()
            bellows.run_plan(plan_path, config, response_server)

        assert "gates_check" in call_order
        assert "teardown" in call_order
        gates_idx = call_order.index("gates_check")
        teardown_idx = call_order.index("teardown")
        assert gates_idx < teardown_idx, \
            f"gates.check ({gates_idx}) must precede _teardown_worktree ({teardown_idx})"
        # Verify plan reached Done (teardown happened before move)
        done_path = os.path.join(decisions_dir, "Done", plan_filename)
        assert os.path.isfile(done_path), f"plan not moved to Done/: {done_path}"


def test_run_plan_strict_pause_on_creation_failure():
    """WorktreeCreationError triggers gate_failure verdict and blocks runner dispatch."""
    with tempfile.TemporaryDirectory() as tmp:
        decisions_dir = os.path.join(tmp, "proj", "knowledge", "decisions")
        os.makedirs(decisions_dir)
        plan_filename = "executable-wt-fail-2026-05-03.md"
        plan_path = os.path.join(decisions_dir, plan_filename)
        with open(plan_path, "w") as f:
            f.write("## STEP 1\nDo stuff.\n")

        config = {
            "default_model": "claude-sonnet-4-6",
            "pushover": {"app_key": "", "user_key": ""},
            "callback_port": 5999,
            "step_timeout_seconds": 600,
        }

        with patch("bellows._create_worktree", side_effect=bellows.WorktreeCreationError("test failure")), \
             patch("bellows.verdict.post_verdict_request") as mock_verdict, \
             patch("bellows.runner.run_step") as mock_runner, \
             patch("bellows.notifier.push"), \
             patch("bellows.record_run"), \
             patch("bellows.validators.validate_at_claim", return_value={"rejected": False, "reject_reason": "", "warnings": []}):
            response_server = MagicMock()
            bellows.run_plan(plan_path, config, response_server)

        # Verdict posted with gate_failure
        mock_verdict.assert_called_once()
        assert mock_verdict.call_args[1].get("pause_reason") == "gate_failure"

        # Runner was never called
        mock_runner.assert_not_called()

        # Plan renamed to verdict-pending-
        verdict_pending = os.path.join(decisions_dir, f"verdict-pending-{plan_filename}")
        assert os.path.exists(verdict_pending), "Plan should be renamed to verdict-pending-"
        assert not os.path.exists(os.path.join(decisions_dir, "Done", plan_filename)), \
            "Plan must not be in Done/"


def test_run_plan_pauses_on_merge_conflict():
    """WorktreeTeardownError on auto-close triggers gate_failure verdict."""
    with tempfile.TemporaryDirectory() as tmp:
        decisions_dir = os.path.join(tmp, "proj", "knowledge", "decisions")
        os.makedirs(decisions_dir)
        plan_filename = "executable-wt-cp-conflict-2026-05-03.md"
        plan_path = os.path.join(decisions_dir, plan_filename)
        with open(plan_path, "w") as f:
            f.write("## STEP 1\nDo stuff.\n")

        config = {
            "default_model": "claude-sonnet-4-6",
            "pushover": {"app_key": "", "user_key": ""},
            "callback_port": 5999,
            "step_timeout_seconds": 600,
        }

        with patch("bellows._create_worktree", return_value="/tmp/wt"), \
             patch("bellows._capture_git_diff", return_value=""), \
             patch("bellows._teardown_worktree",
                   side_effect=bellows.WorktreeTeardownError("merge conflict")), \
             patch("bellows.runner.run_step", return_value=_make_fake_run_step_result()), \
             patch("bellows.gates.check", return_value=_clean_gates()), \
             patch("bellows.verdict.post_verdict_request") as mock_verdict, \
             patch("bellows.notifier.push"), \
             patch("bellows.record_run"), \
             patch("bellows.validators.validate_at_claim", return_value={"rejected": False, "reject_reason": "", "warnings": []}):
            response_server = MagicMock()
            bellows.run_plan(plan_path, config, response_server)

        # Verdict posted with gate_failure
        mock_verdict.assert_called_once()
        assert mock_verdict.call_args[1].get("pause_reason") == "gate_failure"

        # Gate failures should reference teardown (dict format per verdict.py contract)
        gate_result_arg = mock_verdict.call_args[0][4]
        failures = gate_result_arg.get("failures", [])
        assert any(f["gate"] == "worktree_teardown" for f in failures), \
            f"Failures should reference teardown: {failures}"

        # Plan renamed to verdict-pending-
        verdict_pending = os.path.join(decisions_dir, f"verdict-pending-{plan_filename}")
        assert os.path.exists(verdict_pending), "Plan should be renamed to verdict-pending-"
        assert not os.path.exists(os.path.join(decisions_dir, "Done", plan_filename)), \
            "Plan must not be in Done/"


def test_bellows_init_runs_worktree_prune():
    """Bellows.__init__ must run git worktree prune for each watched project."""
    with tempfile.TemporaryDirectory() as tmp:
        wp = os.path.join(tmp, "proj", "knowledge", "decisions")
        os.makedirs(wp)

        with patch("bellows.subprocess.run") as mock_subprocess, \
             patch("bellows.server.ResponseServer"):
            bellows.Bellows({"watched_projects": [wp], "callback_port": 5999})

        prune_calls = [
            c for c in mock_subprocess.call_args_list
            if c[0][0] == ["git", "--no-pager", "worktree", "prune"]
        ]
        assert len(prune_calls) == 1, \
            f"Expected 1 worktree prune call, got {len(prune_calls)}"
        expected_cwd = os.path.join(tmp, "proj")
        assert prune_calls[0][1].get("cwd") == expected_cwd, \
            f"Expected cwd={expected_cwd}, got: {prune_calls[0][1].get('cwd')}"


# ---------------------------------------------------------------------------
# Monorepo worktree skip — unit tests (detect-and-skip when no .git)
# ---------------------------------------------------------------------------


def test_create_worktree_returns_project_path_when_no_git():
    """_create_worktree returns project_path unchanged when .git is absent."""
    with tempfile.TemporaryDirectory() as tmp:
        project_path = os.path.join(tmp, "bellows")
        os.makedirs(project_path)
        # No .git created — simulates the monorepo-child case

        result = bellows._create_worktree(project_path, "test-slug")

        assert result == project_path, \
            f"Expected project_path returned as-is, got: {result}"


def test_teardown_worktree_noop_when_wt_equals_project():
    """_teardown_worktree is a no-op when wt_path == project_path (in-place execution)."""
    with tempfile.TemporaryDirectory() as tmp:
        project_path = os.path.join(tmp, "bellows")
        os.makedirs(project_path)

        with patch("bellows.subprocess.run") as mock_subprocess:
            bellows._teardown_worktree(project_path, project_path, "test-slug")

        assert mock_subprocess.call_count == 0, \
            f"Expected zero subprocess calls for in-place teardown, got {mock_subprocess.call_count}"


# ---------------------------------------------------------------------------
# Mode A detection and recovery (B2) — Failure 3 closure 2026-05-06
# ---------------------------------------------------------------------------


def test_mode_a_detected_and_recovered():
    """B2: agent moves plan to Done/ during execution — file recovered, synthetic gate failure injected."""
    with tempfile.TemporaryDirectory() as tmp:
        decisions_dir = os.path.join(tmp, "proj", "knowledge", "decisions")
        done_dir = os.path.join(decisions_dir, "Done")
        os.makedirs(decisions_dir)
        os.makedirs(done_dir)
        plan_filename = "executable-mode-a-test-2026-05-06.md"
        plan_path = os.path.join(decisions_dir, plan_filename)
        inprogress_path = os.path.join(decisions_dir, f"in-progress-{plan_filename}")
        with open(plan_path, "w") as f:
            f.write("## STEP 1\nDo stuff.\n")

        config = {
            "default_model": "claude-sonnet-4-6",
            "pushover": {"app_key": "", "user_key": ""},
            "callback_port": 5999,
            "step_timeout_seconds": 600,
        }

        def agent_moves_to_done(*args, **kwargs):
            """Simulate agent moving in-progress file to Done/ during execution."""
            if os.path.exists(inprogress_path):
                os.rename(inprogress_path, os.path.join(done_dir, plan_filename))
            return _make_fake_run_step_result()

        with patch("bellows._create_worktree", return_value="/tmp/wt"), \
             patch("bellows._capture_git_diff", return_value=""), \
             patch("bellows._teardown_worktree"), \
             patch("bellows.runner.run_step", side_effect=agent_moves_to_done), \
             patch("bellows.gates.check", return_value=_clean_gates(auto_close="false")), \
             patch("bellows.verdict.post_verdict_request") as mock_verdict, \
             patch("bellows.notifier.notify_verdict_request"), \
             patch("bellows.notifier.push"), \
             patch("bellows.record_run"), \
             patch("bellows.validators.validate_at_claim", return_value={"rejected": False, "reject_reason": "", "warnings": []}):
            response_server = MagicMock()
            bellows.run_plan(plan_path, config, response_server)

        # File should be recovered to verdict-pending- (via normal pause flow after gate failure)
        verdict_pending = os.path.join(decisions_dir, f"verdict-pending-{plan_filename}")
        assert os.path.exists(inprogress_path) or os.path.exists(verdict_pending), \
            "Plan should be recovered from Done/ (at in-progress or verdict-pending)"
        assert not os.path.exists(os.path.join(done_dir, plan_filename)), \
            "Plan must not remain in Done/"

        # Verdict posted with gate_failure containing unauthorized_done_move
        mock_verdict.assert_called_once()
        gate_result_arg = mock_verdict.call_args[0][4]
        failures = gate_result_arg.get("failures", [])
        assert any(f["gate"] == "unauthorized_done_move" for f in failures), \
            f"Expected unauthorized_done_move failure, got: {failures}"
        assert gate_result_arg["passed"] is False


def test_mode_a_no_detection_normal_flow():
    """B2: normal flow — in-progress file exists, no Mode A detection, no synthetic failure."""
    with tempfile.TemporaryDirectory() as tmp:
        decisions_dir = os.path.join(tmp, "proj", "knowledge", "decisions")
        os.makedirs(decisions_dir)
        plan_filename = "executable-mode-a-normal-2026-05-06.md"
        plan_path = os.path.join(decisions_dir, plan_filename)
        with open(plan_path, "w") as f:
            f.write("## STEP 1\nDo stuff.\n")

        config = {
            "default_model": "claude-sonnet-4-6",
            "pushover": {"app_key": "", "user_key": ""},
            "callback_port": 5999,
            "step_timeout_seconds": 600,
        }

        clean_gate = _clean_gates(auto_close="false")

        with patch("bellows._create_worktree", return_value="/tmp/wt"), \
             patch("bellows._capture_git_diff", return_value=""), \
             patch("bellows._teardown_worktree"), \
             patch("bellows.runner.run_step", return_value=_make_fake_run_step_result()), \
             patch("bellows.gates.check", return_value=clean_gate), \
             patch("bellows.verdict.post_verdict_request") as mock_verdict, \
             patch("bellows.notifier.notify_verdict_request"), \
             patch("bellows.notifier.push"), \
             patch("bellows.record_run"), \
             patch("bellows.validators.validate_at_claim", return_value={"rejected": False, "reject_reason": "", "warnings": []}):
            response_server = MagicMock()
            bellows.run_plan(plan_path, config, response_server)

        # Verdict posted (auto_close=false, single-step plan pauses) but no Mode A failure
        mock_verdict.assert_called_once()
        gate_result_arg = mock_verdict.call_args[0][4]
        failures = gate_result_arg.get("failures", [])
        assert not any(f.get("gate") == "unauthorized_done_move" for f in failures), \
            f"Should have no unauthorized_done_move failure, got: {failures}"


def test_mode_a_missing_file_not_in_done():
    """B2: in-progress file deleted (not moved to Done/) — warning logged, no Mode A classification."""
    with tempfile.TemporaryDirectory() as tmp:
        decisions_dir = os.path.join(tmp, "proj", "knowledge", "decisions")
        os.makedirs(decisions_dir)
        plan_filename = "executable-mode-a-deleted-2026-05-06.md"
        plan_path = os.path.join(decisions_dir, plan_filename)
        inprogress_path = os.path.join(decisions_dir, f"in-progress-{plan_filename}")
        with open(plan_path, "w") as f:
            f.write("## STEP 1\nDo stuff.\n")

        config = {
            "default_model": "claude-sonnet-4-6",
            "pushover": {"app_key": "", "user_key": ""},
            "callback_port": 5999,
            "step_timeout_seconds": 600,
        }

        def agent_deletes_file(*args, **kwargs):
            """Simulate agent deleting the in-progress file without moving to Done/."""
            if os.path.exists(inprogress_path):
                os.remove(inprogress_path)
            return _make_fake_run_step_result()

        clean_gate = _clean_gates(auto_close="false")

        with patch("bellows._create_worktree", return_value="/tmp/wt"), \
             patch("bellows._capture_git_diff", return_value=""), \
             patch("bellows._teardown_worktree"), \
             patch("bellows.runner.run_step", side_effect=agent_deletes_file), \
             patch("bellows.gates.check", return_value=clean_gate), \
             patch("bellows.verdict.post_verdict_request") as mock_verdict, \
             patch("bellows.notifier.notify_verdict_request"), \
             patch("bellows.notifier.push"), \
             patch("bellows.record_run"), \
             patch("bellows.validators.validate_at_claim", return_value={"rejected": False, "reject_reason": "", "warnings": []}):
            response_server = MagicMock()
            bellows.run_plan(plan_path, config, response_server)

        # Verdict posted but no unauthorized_done_move failure
        mock_verdict.assert_called_once()
        gate_result_arg = mock_verdict.call_args[0][4]
        failures = gate_result_arg.get("failures", [])
        assert not any(f.get("gate") == "unauthorized_done_move" for f in failures), \
            f"Should not classify as Mode A when file is not in Done/, got: {failures}"


def test_mode_a_recovery_failure():
    """B2: agent moves to Done/, recovery shutil.move raises — synthetic failure still injected."""
    with tempfile.TemporaryDirectory() as tmp:
        decisions_dir = os.path.join(tmp, "proj", "knowledge", "decisions")
        done_dir = os.path.join(decisions_dir, "Done")
        os.makedirs(decisions_dir)
        os.makedirs(done_dir)
        plan_filename = "executable-mode-a-recovery-fail-2026-05-06.md"
        plan_path = os.path.join(decisions_dir, plan_filename)
        inprogress_path = os.path.join(decisions_dir, f"in-progress-{plan_filename}")
        with open(plan_path, "w") as f:
            f.write("## STEP 1\nDo stuff.\n")

        config = {
            "default_model": "claude-sonnet-4-6",
            "pushover": {"app_key": "", "user_key": ""},
            "callback_port": 5999,
            "step_timeout_seconds": 600,
        }

        def agent_moves_to_done(*args, **kwargs):
            if os.path.exists(inprogress_path):
                os.rename(inprogress_path, os.path.join(done_dir, plan_filename))
            return _make_fake_run_step_result()

        original_shutil_move = shutil.move

        def patched_shutil_move(src, dst):
            # Block the recovery move (Done/ → in-progress), allow all others
            if "Done" in str(src) and "in-progress-" in str(dst):
                raise PermissionError("simulated recovery failure")
            return original_shutil_move(src, dst)

        with patch("bellows._create_worktree", return_value="/tmp/wt"), \
             patch("bellows._capture_git_diff", return_value=""), \
             patch("bellows._teardown_worktree"), \
             patch("bellows.runner.run_step", side_effect=agent_moves_to_done), \
             patch("bellows.shutil.move", side_effect=patched_shutil_move), \
             patch("bellows.gates.check", return_value=_clean_gates(auto_close="false")), \
             patch("bellows.verdict.post_verdict_request") as mock_verdict, \
             patch("bellows.notifier.notify_verdict_request"), \
             patch("bellows.notifier.push"), \
             patch("bellows.record_run"), \
             patch("bellows.validators.validate_at_claim", return_value={"rejected": False, "reject_reason": "", "warnings": []}):
            response_server = MagicMock()
            bellows.run_plan(plan_path, config, response_server)

        # Synthetic failure should still be injected even though recovery failed
        mock_verdict.assert_called_once()
        gate_result_arg = mock_verdict.call_args[0][4]
        failures = gate_result_arg.get("failures", [])
        assert any(f["gate"] == "unauthorized_done_move" for f in failures), \
            f"Expected unauthorized_done_move failure even on recovery failure, got: {failures}"
        assert gate_result_arg["passed"] is False


def test_mode_a_synthetic_failure_in_verdict_request():
    """B2 end-to-end: Mode A triggers verdict request with unauthorized_done_move gate."""
    with tempfile.TemporaryDirectory() as tmp:
        decisions_dir = os.path.join(tmp, "proj", "knowledge", "decisions")
        done_dir = os.path.join(decisions_dir, "Done")
        os.makedirs(decisions_dir)
        os.makedirs(done_dir)
        plan_filename = "executable-mode-a-e2e-2026-05-06.md"
        plan_path = os.path.join(decisions_dir, plan_filename)
        inprogress_path = os.path.join(decisions_dir, f"in-progress-{plan_filename}")
        with open(plan_path, "w") as f:
            f.write("## STEP 1\nDo stuff.\n")

        config = {
            "default_model": "claude-sonnet-4-6",
            "pushover": {"app_key": "", "user_key": ""},
            "callback_port": 5999,
            "step_timeout_seconds": 600,
        }

        def agent_moves_to_done(*args, **kwargs):
            if os.path.exists(inprogress_path):
                os.rename(inprogress_path, os.path.join(done_dir, plan_filename))
            return _make_fake_run_step_result()

        # Use real gates.check but mock runner — allows end-to-end gate flow
        # We need to also capture what verdict.post_verdict_request receives
        verdict_calls = []

        def capture_verdict(*args, **kwargs):
            verdict_calls.append({"args": args, "kwargs": kwargs})

        with patch("bellows._create_worktree", return_value="/tmp/wt"), \
             patch("bellows._capture_git_diff", return_value=""), \
             patch("bellows._teardown_worktree"), \
             patch("bellows.runner.run_step", side_effect=agent_moves_to_done), \
             patch("bellows.gates.check", return_value=_clean_gates(auto_close="false")), \
             patch("bellows.verdict.post_verdict_request", side_effect=capture_verdict), \
             patch("bellows.notifier.notify_verdict_request"), \
             patch("bellows.notifier.push"), \
             patch("bellows.record_run"), \
             patch("bellows.validators.validate_at_claim", return_value={"rejected": False, "reject_reason": "", "warnings": []}):
            response_server = MagicMock()
            bellows.run_plan(plan_path, config, response_server)

        assert len(verdict_calls) == 1, f"Expected 1 verdict call, got {len(verdict_calls)}"
        gate_result_arg = verdict_calls[0]["args"][4]
        assert any(f["gate"] == "unauthorized_done_move" for f in gate_result_arg["failures"]), \
            f"Verdict request should contain unauthorized_done_move gate failure"
        assert gate_result_arg["passed"] is False
        # Verify pause_reason is gate_failure
        assert verdict_calls[0]["kwargs"].get("pause_reason") == "gate_failure"


def test_create_worktree_proceeds_when_git_exists():
    """_create_worktree creates a real worktree when project has its own .git."""
    with tempfile.TemporaryDirectory() as tmp:
        project_path = os.path.join(tmp, "proj")
        os.makedirs(os.path.join(project_path, ".git"))  # simulate standalone repo

        def fake_run(cmd, **kwargs):
            mock_result = MagicMock(returncode=0, stdout="", stderr="")
            # Branch-exists check must return non-zero (branch does not exist)
            if isinstance(cmd, list) and "rev-parse" in cmd and "refs/heads/" in " ".join(cmd):
                mock_result.returncode = 1
            return mock_result

        with patch("bellows.subprocess.run", side_effect=fake_run) as mock_subprocess:
            result = bellows._create_worktree(project_path, "test-slug")

        expected_wt = os.path.join(project_path, ".bellows-worktrees", "test-slug")
        assert result == expected_wt, \
            f"Expected worktree path {expected_wt}, got: {result}"
        # Verify git worktree add was invoked
        assert mock_subprocess.call_count >= 1
        wt_add_calls = [c for c in mock_subprocess.call_args_list if isinstance(c[0][0], list) and "worktree" in c[0][0]]
        assert len(wt_add_calls) >= 1, \
            f"Expected git worktree add command, got calls: {mock_subprocess.call_args_list}"


def test_warning_multi_step_plan_without_pause_for_verdict(capsys):
    """Multi-step plan without pause_for_verdict header emits a sparse-header warning.
    The narrowed pause_for_verdict warning does NOT fire because the defensive default
    already inserted the key before the check runs (Case 3 from shape-choice diagnostic)."""
    with tempfile.TemporaryDirectory() as tmp:
        decisions_dir = os.path.join(tmp, "proj", "knowledge", "decisions")
        os.makedirs(decisions_dir)
        plan_filename = "executable-test-warning-2026-05-08.md"
        plan_path = os.path.join(decisions_dir, plan_filename)
        with open(plan_path, "w") as f:
            f.write("# Test Plan\n**Date:** 2026-05-08\n\n## STEP 1 — DEV\n\n> Do step 1.\n\n## STEP 2 — QA\n\n> Do step 2.\n")

        config = {
            "default_model": "claude-sonnet-4-6",
            "pushover": {"app_key": "", "user_key": ""},
            "callback_port": 5999,
            "step_timeout_seconds": 600,
        }

        clean_parsed = {
            "session_id": "test-session",
            "is_error": False,
            "stop_reason": "end_turn",
            "result_text": "",
            "cost_usd": 0.05,
            "permission_denials": [],
            "receipt_status": "Complete",
            "ceo_flags": [],
            "escalate": False,
        }
        clean_gates = {
            "passed": True,
            "failures": [],
            "is_qa_step": True,
            "files_changed": [],
            "plan_header": {},
            "verdict_requested": {"requested": False, "body": None},
        }

        with patch("bellows.runner.run_step", return_value=clean_parsed), \
             patch("bellows.gates.check", return_value=clean_gates), \
             patch("bellows.notifier.push"), \
             patch("bellows.notifier.notify_verdict_request"), \
             patch("bellows.verdict.post_verdict_request"), \
             patch("bellows._capture_git_diff", return_value=""), \
             patch("bellows._create_worktree", return_value="/tmp/wt"), \
             patch("bellows._teardown_worktree"), \
             patch("bellows._read_shadow", return_value=None), \
             patch("bellows._write_shadow"), \
             patch("bellows._delete_shadow"), \
             patch("bellows.record_run"), \
             patch("bellows.validators.validate_at_claim", return_value={"rejected": False, "reject_reason": "", "warnings": []}):
            response_server = MagicMock()
            bellows.run_plan(plan_path, config, response_server)

        captured = capsys.readouterr()
        # Defensive default fires (sparse header)
        assert "sparse header" in captured.out and "safe-pause" in captured.out, \
            f"Expected sparse-header defensive default warning. stdout:\n{captured.out}"
        # Narrowed pause_for_verdict warning does NOT fire — defensive default already inserted key
        assert "will auto-advance without pausing at intermediate steps" not in captured.out, \
            f"Narrowed warning should NOT fire when defensive default inserted pause_for_verdict. stdout:\n{captured.out}"


def test_no_warning_multi_step_plan_with_pause_for_verdict(capsys):
    """Multi-step plan WITH pause_for_verdict header does NOT emit the warning."""
    with tempfile.TemporaryDirectory() as tmp:
        decisions_dir = os.path.join(tmp, "proj", "knowledge", "decisions")
        os.makedirs(decisions_dir)
        plan_filename = "executable-test-no-warning-2026-05-08.md"
        plan_path = os.path.join(decisions_dir, plan_filename)
        with open(plan_path, "w") as f:
            f.write("---\npause_for_verdict: after_step_1\n---\n\n## STEP 1 — DEV\n\n> Do step 1.\n\n## STEP 2 — QA\n\n> Do step 2.\n")

        config = {
            "default_model": "claude-sonnet-4-6",
            "pushover": {"app_key": "", "user_key": ""},
            "callback_port": 5999,
            "step_timeout_seconds": 600,
        }

        clean_parsed = {
            "session_id": "test-session",
            "is_error": False,
            "stop_reason": "end_turn",
            "result_text": "",
            "cost_usd": 0.05,
            "permission_denials": [],
            "receipt_status": "Complete",
            "ceo_flags": [],
            "escalate": False,
        }
        clean_gates = {
            "passed": True,
            "failures": [],
            "is_qa_step": False,
            "files_changed": [],
            "plan_header": {"pause_for_verdict": "after_step_1"},
            "verdict_requested": {"requested": False, "body": None},
        }

        with patch("bellows.runner.run_step", return_value=clean_parsed), \
             patch("bellows.gates.check", return_value=clean_gates), \
             patch("bellows.notifier.push"), \
             patch("bellows.notifier.notify_verdict_request"), \
             patch("bellows.verdict.post_verdict_request"), \
             patch("bellows._capture_git_diff", return_value=""), \
             patch("bellows._create_worktree", return_value="/tmp/wt"), \
             patch("bellows._teardown_worktree"), \
             patch("bellows._read_shadow", return_value=None), \
             patch("bellows._write_shadow"), \
             patch("bellows._delete_shadow"), \
             patch("bellows.record_run"):
            response_server = MagicMock()
            bellows.run_plan(plan_path, config, response_server)

        captured = capsys.readouterr()
        assert "pause_for_verdict header — Bellows will auto-advance" not in captured.out, \
            f"Warning should NOT appear when pause_for_verdict is declared. stdout:\n{captured.out}"


def test_no_warning_single_step_plan_without_pause_for_verdict(capsys):
    """Single-step plan without pause_for_verdict header does NOT emit the warning."""
    with tempfile.TemporaryDirectory() as tmp:
        decisions_dir = os.path.join(tmp, "proj", "knowledge", "decisions")
        os.makedirs(decisions_dir)
        plan_filename = "executable-test-single-step-2026-05-08.md"
        plan_path = os.path.join(decisions_dir, plan_filename)
        with open(plan_path, "w") as f:
            f.write("# Test Plan\n**Date:** 2026-05-08\n\n## STEP 1 — DEV\n\n> Do step 1.\n")

        config = {
            "default_model": "claude-sonnet-4-6",
            "pushover": {"app_key": "", "user_key": ""},
            "callback_port": 5999,
            "step_timeout_seconds": 600,
        }

        clean_parsed = {
            "session_id": "test-session",
            "is_error": False,
            "stop_reason": "end_turn",
            "result_text": "",
            "cost_usd": 0.05,
            "permission_denials": [],
            "receipt_status": "Complete",
            "ceo_flags": [],
            "escalate": False,
        }
        clean_gates = {
            "passed": True,
            "failures": [],
            "is_qa_step": False,
            "files_changed": [],
            "plan_header": {},
            "verdict_requested": {"requested": False, "body": None},
        }

        with patch("bellows.runner.run_step", return_value=clean_parsed), \
             patch("bellows.gates.check", return_value=clean_gates), \
             patch("bellows.notifier.push"), \
             patch("bellows.notifier.notify_verdict_request"), \
             patch("bellows.verdict.post_verdict_request"), \
             patch("bellows._capture_git_diff", return_value=""), \
             patch("bellows._create_worktree", return_value="/tmp/wt"), \
             patch("bellows._teardown_worktree"), \
             patch("bellows._read_shadow", return_value=None), \
             patch("bellows._write_shadow"), \
             patch("bellows._delete_shadow"), \
             patch("bellows.record_run"):
            response_server = MagicMock()
            bellows.run_plan(plan_path, config, response_server)

        captured = capsys.readouterr()
        assert "pause_for_verdict header — Bellows will auto-advance" not in captured.out, \
            f"Warning should NOT appear for single-step plans. stdout:\n{captured.out}"


def test_no_warning_multi_step_plan_with_pause_always(capsys):
    """Multi-step plan with pause_for_verdict: always does NOT emit the warning."""
    with tempfile.TemporaryDirectory() as tmp:
        decisions_dir = os.path.join(tmp, "proj", "knowledge", "decisions")
        os.makedirs(decisions_dir)
        plan_filename = "executable-test-always-2026-05-08.md"
        plan_path = os.path.join(decisions_dir, plan_filename)
        with open(plan_path, "w") as f:
            f.write("---\npause_for_verdict: always\n---\n\n## STEP 1 — DEV\n\n> Do step 1.\n\n## STEP 2 — QA\n\n> Do step 2.\n")

        config = {
            "default_model": "claude-sonnet-4-6",
            "pushover": {"app_key": "", "user_key": ""},
            "callback_port": 5999,
            "step_timeout_seconds": 600,
        }

        clean_parsed = {
            "session_id": "test-session",
            "is_error": False,
            "stop_reason": "end_turn",
            "result_text": "",
            "cost_usd": 0.05,
            "permission_denials": [],
            "receipt_status": "Complete",
            "ceo_flags": [],
            "escalate": False,
        }
        clean_gates = {
            "passed": True,
            "failures": [],
            "is_qa_step": False,
            "files_changed": [],
            "plan_header": {"pause_for_verdict": "always"},
            "verdict_requested": {"requested": False, "body": None},
        }

        with patch("bellows.runner.run_step", return_value=clean_parsed), \
             patch("bellows.gates.check", return_value=clean_gates), \
             patch("bellows.notifier.push"), \
             patch("bellows.notifier.notify_verdict_request"), \
             patch("bellows.verdict.post_verdict_request"), \
             patch("bellows._capture_git_diff", return_value=""), \
             patch("bellows._create_worktree", return_value="/tmp/wt"), \
             patch("bellows._teardown_worktree"), \
             patch("bellows._read_shadow", return_value=None), \
             patch("bellows._write_shadow"), \
             patch("bellows._delete_shadow"), \
             patch("bellows.record_run"):
            response_server = MagicMock()
            bellows.run_plan(plan_path, config, response_server)

        captured = capsys.readouterr()
        assert "pause_for_verdict header — Bellows will auto-advance" not in captured.out, \
            f"Warning should NOT appear when pause_for_verdict is 'always'. stdout:\n{captured.out}"


# ---------------------------------------------------------------------------
# _teardown_worktree lock detection + orphan cleanup (BACKLOG 2026-05-07)
# ---------------------------------------------------------------------------


def test_teardown_worktree_removes_stale_index_lock():
    """Stale .git/index.lock (>5s old) is removed before merge."""
    with tempfile.TemporaryDirectory() as tmp:
        project_path = os.path.join(tmp, "project")
        wt_path = os.path.join(tmp, "worktree")
        os.makedirs(os.path.join(project_path, ".git"))
        os.makedirs(wt_path)

        # Create a stale lock file (mtime 30s ago)
        lock_path = os.path.join(project_path, ".git", "index.lock")
        with open(lock_path, "w") as f:
            f.write("")
        os.utime(lock_path, (time.time() - 30, time.time() - 30))

        def fake_subprocess_run(cmd, **kwargs):
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = ""
            mock_result.stderr = ""
            return mock_result

        with patch("bellows.subprocess.run", side_effect=fake_subprocess_run):
            bellows._teardown_worktree(project_path, wt_path, "test-slug")

        assert not os.path.exists(lock_path), \
            f"Stale .git/index.lock should have been removed, but still exists"


def test_teardown_worktree_waits_for_fresh_index_lock():
    """Fresh .git/index.lock triggers a wait then removal."""
    with tempfile.TemporaryDirectory() as tmp:
        project_path = os.path.join(tmp, "project")
        wt_path = os.path.join(tmp, "worktree")
        os.makedirs(os.path.join(project_path, ".git"))
        os.makedirs(wt_path)

        # Create a fresh lock file (current mtime)
        lock_path = os.path.join(project_path, ".git", "index.lock")
        with open(lock_path, "w") as f:
            f.write("")

        def fake_subprocess_run(cmd, **kwargs):
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = ""
            mock_result.stderr = ""
            return mock_result

        with patch("bellows.subprocess.run", side_effect=fake_subprocess_run), \
             patch("bellows.time.sleep"):
            bellows._teardown_worktree(project_path, wt_path, "test-slug")

        assert not os.path.exists(lock_path), \
            f"Fresh .git/index.lock should have been removed after wait, but still exists"


def test_teardown_worktree_force_removes_orphaned_directory():
    """Orphaned worktree directory is force-removed when git worktree remove fails."""
    with tempfile.TemporaryDirectory() as tmp:
        project_path = os.path.join(tmp, "project")
        wt_path = os.path.join(tmp, "worktree")
        os.makedirs(os.path.join(project_path, ".git"))
        os.makedirs(wt_path)
        # Put a file in wt_path so it's non-empty
        with open(os.path.join(wt_path, "dummy.txt"), "w") as f:
            f.write("test")

        call_count = [0]

        def fake_subprocess_run(cmd, **kwargs):
            call_count[0] += 1
            mock_result = MagicMock()
            # Make git worktree remove fail
            if "worktree" in cmd and "remove" in cmd:
                mock_result.returncode = 1
                mock_result.stdout = ""
                mock_result.stderr = "fatal: worktree remove failed"
            else:
                mock_result.returncode = 0
                mock_result.stdout = ""
                mock_result.stderr = ""
            return mock_result

        with patch("bellows.subprocess.run", side_effect=fake_subprocess_run):
            bellows._teardown_worktree(project_path, wt_path, "test-slug")

        assert not os.path.exists(wt_path), \
            f"Orphaned worktree directory should have been force-removed, but still exists"


def test_defensive_default_sets_pause_for_verdict_when_header_sparse():
    """Shape g safety net: when header parse returns < 3 keys for a multi-step plan,
    pause_for_verdict defaults to after_step_1 to prevent silent auto-advance.
    Regression for BACKLOG 2026-05-10."""
    sparse_header = {"project": "bellows"}
    result = bellows._apply_defensive_header_defaults(sparse_header, total_steps=2)
    assert result["pause_for_verdict"] == "after_step_1"


def test_defensive_default_does_not_override_explicit_pause_for_verdict():
    """The defensive default must NOT override an explicit pause_for_verdict value."""
    sparse_header = {"project": "bellows", "pause_for_verdict": "always"}
    result = bellows._apply_defensive_header_defaults(sparse_header, total_steps=3)
    assert result["pause_for_verdict"] == "always"


# ---------------------------------------------------------------------------
# _seen slug-keying and lifecycle discard regression tests
# ---------------------------------------------------------------------------

def test_seen_uses_slug_not_path():
    """After dispatch, bellows._seen must contain the slug (not the full path)."""
    mock_orch = MagicMock()
    mock_orch._seen = set()
    handler = bellows.PlanHandler(mock_orch)

    with tempfile.TemporaryDirectory() as tmp:
        mock_orch.config = {"watched_projects": [tmp]}
        fname = "executable-widget-2026-05-11.md"
        path = os.path.join(tmp, fname)
        open(path, "w").close()

        handler._handle(path)

    slug = verdict.slug_from_path(path)
    assert slug in mock_orch._seen, f"slug {slug!r} should be in _seen"
    assert path not in mock_orch._seen, "full path should NOT be in _seen"


def test_seen_dispatch_window_guard_holds():
    """With a slug already in _seen, _handle must return without dispatching (race-window guard)."""
    mock_orch = MagicMock()
    mock_orch._seen = set()
    handler = bellows.PlanHandler(mock_orch)

    with tempfile.TemporaryDirectory() as tmp:
        mock_orch.config = {"watched_projects": [tmp]}
        fname = "executable-widget-2026-05-11.md"
        path = os.path.join(tmp, fname)
        open(path, "w").close()

        slug = verdict.slug_from_path(path)
        mock_orch._seen.add(slug)  # simulate post-dispatch state

        handler._handle(path)

    mock_orch.handle_new_plan.assert_not_called()


def test_on_modified_invalidates_seen_for_runnable_plan():
    """Item 3 regression: on_modified must discard the slug from _seen when the modified file
    is a runnable plan without a lifecycle prefix, allowing corrected re-deposits to dispatch."""
    mock_orch = MagicMock()
    mock_orch._seen = set()
    handler = bellows.PlanHandler(mock_orch)

    with tempfile.TemporaryDirectory() as tmp:
        mock_orch.config = {"watched_projects": [tmp]}
        fname = "executable-widget-2026-05-11.md"
        path = os.path.join(tmp, fname)
        open(path, "w").close()

        slug = verdict.slug_from_path(path)
        mock_orch._seen.add(slug)

        event = MagicMock()
        event.is_directory = False
        event.src_path = path

        with patch.object(handler, "_handle") as mock_handle:
            handler.on_modified(event)

        # Slug should have been invalidated before _handle was called
        assert slug not in mock_orch._seen, "slug should be discarded from _seen on non-lifecycle on_modified"
        mock_handle.assert_called_once_with(path)


def test_on_modified_preserves_seen_for_lifecycle_renames():
    """Item 3 regression: on_modified must NOT invalidate _seen when the file has a Bellows-managed
    lifecycle prefix (in-progress-, verdict-pending-, halted-). This prevents re-dispatch loops."""
    mock_orch = MagicMock()
    mock_orch._seen = set()
    handler = bellows.PlanHandler(mock_orch)

    lifecycle_filenames = [
        "in-progress-executable-widget-2026-05-11.md",
        "verdict-pending-executable-widget-2026-05-11.md",
        "halted-executable-widget-2026-05-11.md",
    ]

    for lf in lifecycle_filenames:
        path = f"/proj/knowledge/decisions/{lf}"
        slug = verdict.slug_from_path(path)
        mock_orch._seen.add(slug)

        event = MagicMock()
        event.is_directory = False
        event.src_path = path

        with patch.object(handler, "_handle") as mock_handle:
            handler.on_modified(event)

        assert slug in mock_orch._seen, f"slug should remain in _seen for lifecycle prefix file {lf}"
        mock_handle.assert_called_once_with(path)


def test_on_created_invalidates_seen_for_runnable_plan():
    """on_created must discard the slug from _seen when the created file is a runnable plan
    without a lifecycle prefix, allowing re-deposits (e.g. follow-on executables after a
    Planner-direct close) to dispatch."""
    mock_orch = MagicMock()
    mock_orch._seen = set()
    handler = bellows.PlanHandler(mock_orch)

    with tempfile.TemporaryDirectory() as tmp:
        mock_orch.config = {"watched_projects": [tmp]}
        fname = "executable-widget-2026-05-11.md"
        path = os.path.join(tmp, fname)
        open(path, "w").close()

        slug = verdict.slug_from_path(path)
        mock_orch._seen.add(slug)

        event = MagicMock()
        event.is_directory = False
        event.src_path = path

        with patch.object(handler, "_handle") as mock_handle:
            handler.on_created(event)

        assert slug not in mock_orch._seen, "slug should be discarded from _seen on non-lifecycle on_created"
        mock_handle.assert_called_once_with(path)


def test_on_created_preserves_seen_for_lifecycle_renames():
    """on_created must NOT invalidate _seen when the file has a Bellows-managed lifecycle
    prefix (in-progress-, verdict-pending-, halted-). This prevents re-dispatch loops."""
    mock_orch = MagicMock()
    mock_orch._seen = set()
    handler = bellows.PlanHandler(mock_orch)

    lifecycle_filenames = [
        "in-progress-executable-widget-2026-05-11.md",
        "verdict-pending-executable-widget-2026-05-11.md",
        "halted-executable-widget-2026-05-11.md",
    ]

    for lf in lifecycle_filenames:
        path = f"/proj/knowledge/decisions/{lf}"
        slug = verdict.slug_from_path(path)
        mock_orch._seen.add(slug)

        event = MagicMock()
        event.is_directory = False
        event.src_path = path

        with patch.object(handler, "_handle") as mock_handle:
            handler.on_created(event)

        assert slug in mock_orch._seen, f"slug should remain in _seen for lifecycle prefix file {lf}"
        mock_handle.assert_called_once_with(path)


def test_on_moved_invalidates_seen_for_runnable_plan():
    """on_moved must discard the slug from _seen when the dest file is a runnable plan
    without a lifecycle prefix, allowing re-deposits via cross-directory moves to dispatch."""
    mock_orch = MagicMock()
    mock_orch._seen = set()
    handler = bellows.PlanHandler(mock_orch)

    with tempfile.TemporaryDirectory() as tmp:
        mock_orch.config = {"watched_projects": [tmp]}
        fname = "executable-widget-2026-05-11.md"
        dest_path = os.path.join(tmp, fname)
        open(dest_path, "w").close()

        slug = verdict.slug_from_path(dest_path)
        mock_orch._seen.add(slug)

        event = MagicMock()
        event.is_directory = False
        event.dest_path = dest_path

        with patch.object(handler, "_handle") as mock_handle:
            handler.on_moved(event)

        assert slug not in mock_orch._seen, "slug should be discarded from _seen on non-lifecycle on_moved"
        mock_handle.assert_called_once_with(dest_path)


def test_on_moved_preserves_seen_for_lifecycle_renames():
    """on_moved must NOT invalidate _seen when the dest file has a Bellows-managed lifecycle
    prefix (in-progress-, verdict-pending-, halted-). This prevents re-dispatch loops."""
    mock_orch = MagicMock()
    mock_orch._seen = set()
    handler = bellows.PlanHandler(mock_orch)

    lifecycle_filenames = [
        "in-progress-executable-widget-2026-05-11.md",
        "verdict-pending-executable-widget-2026-05-11.md",
        "halted-executable-widget-2026-05-11.md",
    ]

    for lf in lifecycle_filenames:
        dest_path = f"/proj/knowledge/decisions/{lf}"
        slug = verdict.slug_from_path(dest_path)
        mock_orch._seen.add(slug)

        event = MagicMock()
        event.is_directory = False
        event.dest_path = dest_path

        with patch.object(handler, "_handle") as mock_handle:
            handler.on_moved(event)

        assert slug in mock_orch._seen, f"slug should remain in _seen for lifecycle prefix file {lf}"
        mock_handle.assert_called_once_with(dest_path)


def test_apply_defensive_header_defaults_propagates_to_reparsed_header():
    """Item 4 regression: after gates.check() re-parses the header at line ~498, run_plan must
    call _apply_defensive_header_defaults again so header_says_pause() consumers see the default."""
    with tempfile.TemporaryDirectory() as tmp:
        decisions_dir = os.path.join(tmp, "proj", "knowledge", "decisions")
        os.makedirs(decisions_dir)
        plan_filename = "executable-item4-test-2026-05-26.md"
        plan_path = os.path.join(decisions_dir, plan_filename)
        plan_text = "## STEP 1\nDo stuff.\n## STEP 2\nDo more stuff.\n"
        with open(plan_path, "w") as f:
            f.write(plan_text)

        config = {
            "default_model": "claude-sonnet-4-6",
            "pushover": {"app_key": "", "user_key": ""},
            "callback_port": 5999,
            "step_timeout_seconds": 600,
        }

        # gates.check returns a sparse plan_header (missing pause_for_verdict)
        # simulating the re-parse that drops the defensive default
        sparse_gate_result = {
            "passed": True,
            "failures": [],
            "is_qa_step": False,
            "files_changed": [],
            "plan_header": {"project": "bellows"},
            "verdict_requested": {"requested": False, "body": None},
        }

        captured_headers = []
        original_header_says_pause = bellows.header_says_pause

        def spy_header_says_pause(header, *args, **kwargs):
            captured_headers.append(dict(header))
            return original_header_says_pause(header, *args, **kwargs)

        with patch("bellows.runner.run_step", return_value=_make_fake_run_step_result()), \
             patch("bellows.gates.check", return_value=sparse_gate_result), \
             patch("bellows.notifier.push"), \
             patch("bellows.verdict.log_to_ledger"), \
             patch("bellows._capture_git_diff", return_value=""), \
             patch("bellows._create_worktree", return_value="/tmp/wt"), \
             patch("bellows._teardown_worktree"), \
             patch("bellows.record_run"), \
             patch("bellows.validators.validate_at_claim", return_value={"rejected": False, "reject_reason": "", "warnings": []}), \
             patch("bellows.header_says_pause", side_effect=spy_header_says_pause):
            response_server = MagicMock()
            bellows.run_plan(plan_path, config, response_server)

        # The header passed to header_says_pause must contain the defensive default
        assert len(captured_headers) >= 1, "header_says_pause should have been called"
        assert captured_headers[0].get("pause_for_verdict") == "after_step_1", \
            "re-parsed header should have defensive default pause_for_verdict=after_step_1"


def test_seen_cleared_on_continue_to_done():
    """_consume_verdicts continue-to-done must discard the slug from _seen."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)

        decisions_dir = tmp_path / "proj" / "knowledge" / "decisions"
        decisions_dir.mkdir(parents=True)
        done_dir = decisions_dir / "Done"
        done_dir.mkdir()

        plan_filename = "diagnostic-seen-clear-test-2026-05-11.md"
        verdict_pending_name = f"verdict-pending-{plan_filename}"
        verdict_pending_path = decisions_dir / verdict_pending_name
        verdict_pending_path.write_text("## Diagnostic\nSingle-step.\n")

        verdicts_resolved = tmp_path / "verdicts" / "resolved"
        verdicts_resolved.mkdir(parents=True)
        verdict_fname = "verdict-seen-clear-test-2026-05-11-step-1.md"
        (verdicts_resolved / verdict_fname).write_text("continue\nApproved.")

        config = {
            "watched_projects": [str(decisions_dir)],
            "default_model": "claude-sonnet-4-6",
            "pushover": {"app_key": "", "user_key": ""},
            "callback_port": 5999,
        }

        b = bellows.Bellows(config)
        slug = verdict.slug_from_path(plan_filename)
        b._seen.add(slug)

        with patch("bellows.BELLOWS_ROOT", tmp_path), \
             patch("bellows.verdict.check_verdict", return_value={
                 "found": True, "verdict": "continue", "reason": "approved"
             }), \
             patch("bellows.verdict.log_to_ledger"), \
             patch("bellows.notifier.push"), \
             patch.object(b, "handle_new_plan"):
            b._consume_verdicts()

        assert slug not in b._seen, f"slug {slug!r} should be discarded from _seen after continue-to-done"


def test_seen_cleared_on_halt():
    """_consume_verdicts halt must discard the slug from _seen."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)

        decisions_dir = tmp_path / "proj" / "knowledge" / "decisions"
        decisions_dir.mkdir(parents=True)

        plan_filename = "executable-halt-test-2026-05-11.md"
        verdict_pending_name = f"verdict-pending-{plan_filename}"
        verdict_pending_path = decisions_dir / verdict_pending_name
        verdict_pending_path.write_text("## STEP 1\nDo something.\n## STEP 2\nDo more.\n")

        verdicts_resolved = tmp_path / "verdicts" / "resolved"
        verdicts_resolved.mkdir(parents=True)
        verdict_fname = "verdict-halt-test-2026-05-11-step-1.md"
        (verdicts_resolved / verdict_fname).write_text("stop\nHalted by planner.")

        config = {
            "watched_projects": [str(decisions_dir)],
            "default_model": "claude-sonnet-4-6",
            "pushover": {"app_key": "", "user_key": ""},
            "callback_port": 5999,
        }

        b = bellows.Bellows(config)
        slug = verdict.slug_from_path(plan_filename)
        b._seen.add(slug)

        with patch("bellows.BELLOWS_ROOT", tmp_path), \
             patch("bellows.verdict.check_verdict", return_value={
                 "found": True, "verdict": "stop", "reason": "halted"
             }), \
             patch("bellows.verdict.log_to_ledger"), \
             patch("bellows.notifier.push"):
            b._consume_verdicts()

        assert slug not in b._seen, f"slug {slug!r} should be discarded from _seen after halt"


def test_module_fingerprints_returns_all_six_modules():
    fps = bellows._module_fingerprints()
    expected_keys = {"bellows.py", "gates.py", "verdict.py", "parser.py", "runner.py", "decisions.py"}
    assert set(fps.keys()) == expected_keys


def test_module_fingerprints_handles_git_failure():
    def failing_run(*args, **kwargs):
        result = MagicMock()
        result.returncode = 1
        result.stdout = ""
        return result

    with patch("bellows.subprocess.run", side_effect=failing_run):
        fps = bellows._module_fingerprints()
    for mod, fp in fps.items():
        assert fp.startswith("mtime:"), f"{mod} should have mtime prefix, got {fp}"


def test_module_fingerprints_fallback_to_unknown_on_unexpected_error():
    with patch("bellows.subprocess.run", side_effect=Exception("boom")), \
         patch("bellows.os.path.getmtime", side_effect=Exception("no mtime")):
        fps = bellows._module_fingerprints()
    for mod, fp in fps.items():
        assert fp == "unknown", f"{mod} should be 'unknown', got {fp}"


def test_auto_close_yaml_bool_does_not_crash():
    """YAML frontmatter can return auto_close as Python bool True.
    Verify str() coercion prevents AttributeError on .lower()."""
    with tempfile.TemporaryDirectory() as tmp:
        decisions_dir = os.path.join(tmp, "proj", "knowledge", "decisions")
        os.makedirs(decisions_dir)
        plan_filename = "executable-yaml-bool-true-2026-05-17.md"
        plan_path = os.path.join(decisions_dir, plan_filename)
        with open(plan_path, "w") as f:
            f.write("## STEP 1\nDo stuff.\n")

        config = {
            "default_model": "claude-sonnet-4-6",
            "pushover": {"app_key": "", "user_key": ""},
            "callback_port": 5999,
            "step_timeout_seconds": 600,
        }

        clean_parsed = _make_fake_run_step_result()
        # Simulate YAML-parsed bool True (not string "true")
        clean_gates = {
            "passed": True,
            "failures": [],
            "is_qa_step": False,
            "files_changed": [],
            "plan_header": {"auto_close": True},  # Python bool from pyyaml
            "verdict_requested": {"requested": False, "body": None},
        }

        with patch("bellows.runner.run_step", return_value=clean_parsed), \
             patch("bellows.gates.check", return_value=clean_gates), \
             patch("bellows.notifier.notify_plan_complete") as mock_notify, \
             patch("bellows.verdict.log_to_ledger") as mock_ledger, \
             patch("bellows._capture_git_diff", return_value=""), \
             patch("bellows._create_worktree", return_value="/tmp/wt"), \
             patch("bellows._teardown_worktree"), \
             patch("bellows.record_run"), \
             patch("bellows.validators.validate_at_claim", return_value={"rejected": False, "reject_reason": "", "warnings": []}):
            response_server = MagicMock()
            # This must NOT raise AttributeError
            bellows.run_plan(plan_path, config, response_server)

        # effective_auto_close should be True — plan moves to Done
        done_path = os.path.join(decisions_dir, "Done", plan_filename)
        assert os.path.isfile(done_path), f"plan not moved to Done/ with bool True: {done_path}"
        mock_ledger.assert_called_once()
        assert mock_ledger.call_args[0][3] == "auto-close"


def test_auto_close_yaml_bool_false():
    """YAML frontmatter can return auto_close as Python bool False.
    Verify str() coercion prevents AttributeError and resolves to False."""
    with tempfile.TemporaryDirectory() as tmp:
        decisions_dir = os.path.join(tmp, "proj", "knowledge", "decisions")
        os.makedirs(decisions_dir)
        plan_filename = "executable-yaml-bool-false-2026-05-17.md"
        plan_path = os.path.join(decisions_dir, plan_filename)
        with open(plan_path, "w") as f:
            f.write("## STEP 1\nDo stuff.\n")

        config = {
            "default_model": "claude-sonnet-4-6",
            "pushover": {"app_key": "", "user_key": ""},
            "callback_port": 5999,
            "step_timeout_seconds": 600,
        }

        clean_parsed = _make_fake_run_step_result()
        # Simulate YAML-parsed bool False (not string "false")
        clean_gates = {
            "passed": True,
            "failures": [],
            "is_qa_step": False,
            "files_changed": [],
            "plan_header": {"auto_close": False},  # Python bool from pyyaml
            "verdict_requested": {"requested": False, "body": None},
        }

        with patch("bellows.runner.run_step", return_value=clean_parsed), \
             patch("bellows.gates.check", return_value=clean_gates), \
             patch("bellows.notifier.push"), \
             patch("bellows.notifier.notify_verdict_request") as mock_notify_verdict, \
             patch("bellows.verdict.post_verdict_request") as mock_post_verdict, \
             patch("bellows.verdict.log_to_ledger") as mock_ledger, \
             patch("bellows._capture_git_diff", return_value=""), \
             patch("bellows._create_worktree", return_value="/tmp/wt"), \
             patch("bellows._teardown_worktree"), \
             patch("bellows.record_run"), \
             patch("bellows.validators.validate_at_claim", return_value={"rejected": False, "reject_reason": "", "warnings": []}):
            response_server = MagicMock()
            # This must NOT raise AttributeError
            bellows.run_plan(plan_path, config, response_server)

        # effective_auto_close should be False — plan pauses for verdict
        done_path = os.path.join(decisions_dir, "Done", plan_filename)
        assert not os.path.exists(done_path), "plan should NOT auto-close with bool False"
        mock_post_verdict.assert_called_once()
        for call in mock_ledger.call_args_list:
            assert call[0][3] != "auto-close", "auto-close should not fire"


def test_migrate_config_idempotent():
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))
    import migrate_config

    with tempfile.TemporaryDirectory() as tmp:
        config_path = Path(tmp) / "config.json"
        original = {
            "callback_port": 5000,
            "default_model": "claude-sonnet-4-6",
            "planner_model": "claude-sonnet-4-6",
            "pushover": {"app_key": "fake-key", "user_key": "fake-user"},
            "tailscale_ip": "100.0.0.1",
            "watched_projects": [],
        }
        with open(config_path, "w") as f:
            json.dump(original, f, indent=2, sort_keys=True)
            f.write("\n")

        # Patch paths to point at temp dir
        old_config = migrate_config.CONFIG_PATH
        old_secrets = migrate_config.SECRETS_PATH
        try:
            migrate_config.CONFIG_PATH = config_path
            migrate_config.SECRETS_PATH = Path(tmp) / "config.secrets.json"

            migrate_config.migrate()
            first_config = config_path.read_text()
            first_secrets = migrate_config.SECRETS_PATH.read_text()

            migrate_config.migrate()
            second_config = config_path.read_text()
            second_secrets = migrate_config.SECRETS_PATH.read_text()

            assert first_config == second_config, "config.json changed on second run"
            assert first_secrets == second_secrets, "config.secrets.json changed on second run"
        finally:
            migrate_config.CONFIG_PATH = old_config
            migrate_config.SECRETS_PATH = old_secrets


def test_migrate_config_preserves_values():
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))
    import migrate_config

    with tempfile.TemporaryDirectory() as tmp:
        config_path = Path(tmp) / "config.json"
        secrets_path = Path(tmp) / "config.secrets.json"
        original = {
            "callback_port": 5000,
            "default_model": "claude-sonnet-4-6",
            "notifications": {"enabled": True, "events": {"failure": True}},
            "planner_model": "claude-sonnet-4-6",
            "pushover": {"app_key": "fake-key", "user_key": "fake-user"},
            "tailscale_ip": "100.0.0.1",
            "watched_projects": ["/tmp/proj"],
        }
        with open(config_path, "w") as f:
            json.dump(original, f, indent=2, sort_keys=True)
            f.write("\n")

        old_config = migrate_config.CONFIG_PATH
        old_secrets = migrate_config.SECRETS_PATH
        try:
            migrate_config.CONFIG_PATH = config_path
            migrate_config.SECRETS_PATH = secrets_path

            migrate_config.migrate()

            with open(config_path) as f:
                operational = json.load(f)
            with open(secrets_path) as f:
                secrets = json.load(f)

            # Merge and compare to original
            merged = dict(operational)
            for key, value in secrets.items():
                if isinstance(value, dict) and isinstance(merged.get(key), dict):
                    merged[key].update(value)
                else:
                    merged[key] = value
            assert merged == original, f"Merged config differs from original: {merged} != {original}"
        finally:
            migrate_config.CONFIG_PATH = old_config
            migrate_config.SECRETS_PATH = old_secrets


def test_migrate_config_already_split():
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))
    import migrate_config

    with tempfile.TemporaryDirectory() as tmp:
        config_path = Path(tmp) / "config.json"
        secrets_path = Path(tmp) / "config.secrets.json"
        operational = {
            "callback_port": 5000,
            "default_model": "claude-sonnet-4-6",
            "watched_projects": [],
        }
        secrets = {
            "pushover": {"app_key": "fake-key", "user_key": "fake-user"},
            "tailscale_ip": "100.0.0.1",
        }
        with open(config_path, "w") as f:
            json.dump(operational, f, indent=2, sort_keys=True)
            f.write("\n")
        with open(secrets_path, "w") as f:
            json.dump(secrets, f, indent=2, sort_keys=True)
            f.write("\n")

        config_before = config_path.read_text()
        secrets_before = secrets_path.read_text()

        old_config = migrate_config.CONFIG_PATH
        old_secrets = migrate_config.SECRETS_PATH
        try:
            migrate_config.CONFIG_PATH = config_path
            migrate_config.SECRETS_PATH = secrets_path

            migrate_config.migrate()

            assert config_path.read_text() == config_before, "config.json should not change"
            assert secrets_path.read_text() == secrets_before, "config.secrets.json should not change"
        finally:
            migrate_config.CONFIG_PATH = old_config
            migrate_config.SECRETS_PATH = old_secrets


# ===================================================================
# V1 — Verdict filename format validator
# ===================================================================

def test_consume_verdicts_malformed_filename_logs_warn_and_notifies():
    """_consume_verdicts emits WARN + notification for verdict file with malformed filename."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)

        decisions_dir = tmp_path / "proj" / "knowledge" / "decisions"
        decisions_dir.mkdir(parents=True)

        verdicts_resolved = tmp_path / "verdicts" / "resolved"
        verdicts_resolved.mkdir(parents=True)
        # Malformed filename: starts with verdict- and ends with .md but doesn't match slug-step pattern
        malformed_fname = "verdict-continue-my-plan.md"
        (verdicts_resolved / malformed_fname).write_text("continue\nApproved.")

        config = {
            "watched_projects": [str(decisions_dir)],
            "default_model": "claude-sonnet-4-6",
            "pushover": {"app_key": "test-app", "user_key": "test-user"},
            "callback_port": 5999,
        }

        b = bellows.Bellows(config)

        log_calls = []
        original_log = bellows._log

        def capture_log(level, msg, **kwargs):
            log_calls.append((level, msg))
            original_log(level, msg, **kwargs)

        with patch("bellows.BELLOWS_ROOT", tmp_path), \
             patch("bellows._log", side_effect=capture_log), \
             patch("bellows.verdict._notify_malformed_verdict") as mock_notify:
            b._consume_verdicts()

        # Assert WARN was logged with the filename
        warn_logs = [(lvl, msg) for lvl, msg in log_calls if lvl == "WARN" and "verdict-continue-my-plan.md" in msg]
        assert len(warn_logs) >= 1, f"Expected WARN log for malformed filename, got: {log_calls}"

        # Assert notification helper was called
        mock_notify.assert_called_once()
        call_args = mock_notify.call_args
        assert malformed_fname in str(call_args[0][0])


def test_consume_verdicts_malformed_filename_still_skipped():
    """_consume_verdicts still skips (does not process) a malformed-filename verdict file."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)

        decisions_dir = tmp_path / "proj" / "knowledge" / "decisions"
        decisions_dir.mkdir(parents=True)

        verdicts_resolved = tmp_path / "verdicts" / "resolved"
        verdicts_resolved.mkdir(parents=True)
        malformed_fname = "verdict-no-step-number.md"
        (verdicts_resolved / malformed_fname).write_text("continue\nApproved.")

        config = {
            "watched_projects": [str(decisions_dir)],
            "default_model": "claude-sonnet-4-6",
            "pushover": {"app_key": "", "user_key": ""},
            "callback_port": 5999,
        }

        b = bellows.Bellows(config)

        with patch("bellows.BELLOWS_ROOT", tmp_path), \
             patch("bellows.verdict._notify_malformed_verdict"), \
             patch("bellows.verdict.check_verdict") as mock_check:
            b._consume_verdicts()

        # check_verdict should NOT be called — malformed filename is skipped before verdict check
        mock_check.assert_not_called()


def test_consume_verdicts_valid_filename_not_flagged():
    """_consume_verdicts does NOT warn for a correctly-formatted verdict filename."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)

        decisions_dir = tmp_path / "proj" / "knowledge" / "decisions"
        decisions_dir.mkdir(parents=True)

        plan_filename = "executable-test-2026-05-20.md"
        verdict_pending_name = f"verdict-pending-{plan_filename}"
        verdict_pending_path = decisions_dir / verdict_pending_name
        verdict_pending_path.write_text("## STEP 1\nDo stuff.\n")

        verdicts_resolved = tmp_path / "verdicts" / "resolved"
        verdicts_resolved.mkdir(parents=True)
        valid_fname = "verdict-test-2026-05-20-step-1.md"
        (verdicts_resolved / valid_fname).write_text("continue\nApproved.")

        config = {
            "watched_projects": [str(decisions_dir)],
            "default_model": "claude-sonnet-4-6",
            "pushover": {"app_key": "", "user_key": ""},
            "callback_port": 5999,
        }

        b = bellows.Bellows(config)

        log_calls = []
        original_log = bellows._log

        def capture_log(level, msg, **kwargs):
            log_calls.append((level, msg))
            original_log(level, msg, **kwargs)

        with patch("bellows.BELLOWS_ROOT", tmp_path), \
             patch("bellows._log", side_effect=capture_log), \
             patch("bellows.verdict.check_verdict", return_value={
                 "found": True, "verdict": "continue", "reason": "approved"
             }), \
             patch("bellows.verdict.log_to_ledger"), \
             patch("bellows.notifier.push"), \
             patch.object(b, "handle_new_plan"), \
             patch("bellows.verdict._notify_malformed_verdict") as mock_notify:
            b._consume_verdicts()

        # No WARN about filename format
        filename_warns = [(lvl, msg) for lvl, msg in log_calls if lvl == "WARN" and "filename format mismatch" in msg]
        assert len(filename_warns) == 0, f"Unexpected filename format warning: {filename_warns}"
        mock_notify.assert_not_called()


def test_consume_verdicts_verdict_request_not_flagged_as_malformed():
    """verdict-request-* files are excluded before the filename format check."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)

        verdicts_resolved = tmp_path / "verdicts" / "resolved"
        verdicts_resolved.mkdir(parents=True)
        # verdict-request files don't match slug-step pattern but should be silently skipped
        (verdicts_resolved / "verdict-request-my-plan-step-1.md").write_text("# Request")

        config = {
            "watched_projects": [],
            "default_model": "claude-sonnet-4-6",
            "pushover": {"app_key": "", "user_key": ""},
            "callback_port": 5999,
        }

        b = bellows.Bellows(config)

        with patch("bellows.BELLOWS_ROOT", tmp_path), \
             patch("bellows.verdict._notify_malformed_verdict") as mock_notify:
            b._consume_verdicts()

        mock_notify.assert_not_called()


# ---------------------------------------------------------------------------
# Rename-first ordering regression tests (RV-1 closure, 2026-05-24)
# Each test verifies that shutil.move (to verdict-pending-*) happens BEFORE
# verdict.post_verdict_request at the corresponding pause site.
# ---------------------------------------------------------------------------

def _make_ordering_tracker():
    """Return (call_order list, shutil.move wrapper, verdict.post wrapper)."""
    call_order = []
    _real_move = shutil.move

    def tracking_move(src, dst, *args, **kwargs):
        if "verdict-pending-" in str(dst):
            call_order.append("rename")
        return _real_move(src, dst, *args, **kwargs)

    def tracking_post(*args, **kwargs):
        call_order.append("verdict_post")

    return call_order, tracking_move, tracking_post


def test_pause_site_1_worktree_creation_failure_renames_before_post():
    """Site 1: WorktreeCreationError — rename to verdict-pending-* must precede verdict.post_verdict_request."""
    with tempfile.TemporaryDirectory() as tmp:
        decisions_dir = os.path.join(tmp, "proj", "knowledge", "decisions")
        os.makedirs(decisions_dir)
        plan_filename = "executable-rv1-site1-2026-05-24.md"
        plan_path = os.path.join(decisions_dir, plan_filename)
        with open(plan_path, "w") as f:
            f.write("## STEP 1\nDo stuff.\n")

        config = {
            "default_model": "claude-sonnet-4-6",
            "pushover": {"app_key": "", "user_key": ""},
            "callback_port": 5999,
            "step_timeout_seconds": 600,
        }

        call_order, tracking_move, tracking_post = _make_ordering_tracker()

        with patch("bellows._create_worktree", side_effect=bellows.WorktreeCreationError("test failure")), \
             patch("shutil.move", side_effect=tracking_move), \
             patch("bellows.verdict.post_verdict_request", side_effect=tracking_post), \
             patch("bellows.runner.run_step") as mock_runner, \
             patch("bellows.notifier.push"), \
             patch("bellows.record_run"), \
             patch("bellows.validators.validate_at_claim", return_value={"rejected": False, "reject_reason": "", "warnings": []}):
            response_server = MagicMock()
            bellows.run_plan(plan_path, config, response_server)

        assert "rename" in call_order, f"shutil.move to verdict-pending-* was not called: {call_order}"
        assert "verdict_post" in call_order, f"verdict.post_verdict_request was not called: {call_order}"
        rename_idx = call_order.index("rename")
        post_idx = call_order.index("verdict_post")
        assert rename_idx < post_idx, \
            f"Site 1: rename ({rename_idx}) must precede verdict_post ({post_idx}): {call_order}"


def test_pause_site_2_intermediate_step_gate_failure_renames_before_post():
    """Site 2: Intermediate-step gate failure — rename to verdict-pending-* must precede verdict.post_verdict_request."""
    with tempfile.TemporaryDirectory() as tmp:
        decisions_dir = os.path.join(tmp, "proj", "knowledge", "decisions")
        os.makedirs(decisions_dir)
        plan_filename = "executable-rv1-site2-2026-05-24.md"
        plan_path = os.path.join(decisions_dir, plan_filename)
        with open(plan_path, "w") as f:
            f.write("## STEP 1\nDo stuff.\n## STEP 2\nMore stuff.\n")

        config = {
            "default_model": "claude-sonnet-4-6",
            "pushover": {"app_key": "", "user_key": ""},
            "callback_port": 5999,
            "step_timeout_seconds": 600,
        }

        call_order, tracking_move, tracking_post = _make_ordering_tracker()

        def failing_gates(*args, **kwargs):
            return {
                "passed": False,
                "failures": [{"gate": "test_gate", "evidence": "forced failure"}],
                "is_qa_step": False,
                "files_changed": [],
                "plan_header": {"auto_close": "false"},
                "verdict_requested": {"requested": False, "body": None},
            }

        with patch("bellows._create_worktree", return_value="/tmp/wt"), \
             patch("bellows._capture_git_diff", return_value=""), \
             patch("bellows._teardown_worktree"), \
             patch("bellows.runner.run_step", return_value=_make_fake_run_step_result()), \
             patch("bellows.gates.check", side_effect=failing_gates), \
             patch("shutil.move", side_effect=tracking_move), \
             patch("bellows.verdict.post_verdict_request", side_effect=tracking_post), \
             patch("bellows.notifier.notify_verdict_request"), \
             patch("bellows.notifier.push"), \
             patch("bellows.record_run"), \
             patch("bellows.validators.validate_at_claim", return_value={"rejected": False, "reject_reason": "", "warnings": []}):
            response_server = MagicMock()
            bellows.run_plan(plan_path, config, response_server)

        assert "rename" in call_order, f"shutil.move to verdict-pending-* was not called: {call_order}"
        assert "verdict_post" in call_order, f"verdict.post_verdict_request was not called: {call_order}"
        rename_idx = call_order.index("rename")
        post_idx = call_order.index("verdict_post")
        assert rename_idx < post_idx, \
            f"Site 2: rename ({rename_idx}) must precede verdict_post ({post_idx}): {call_order}"


def test_pause_site_3_final_step_gate_failure_renames_before_post():
    """Site 3: Final-step gate failure — rename to verdict-pending-* must precede verdict.post_verdict_request."""
    with tempfile.TemporaryDirectory() as tmp:
        decisions_dir = os.path.join(tmp, "proj", "knowledge", "decisions")
        os.makedirs(decisions_dir)
        plan_filename = "executable-rv1-site3-2026-05-24.md"
        plan_path = os.path.join(decisions_dir, plan_filename)
        with open(plan_path, "w") as f:
            f.write("## STEP 1\nDo stuff.\n")

        config = {
            "default_model": "claude-sonnet-4-6",
            "pushover": {"app_key": "", "user_key": ""},
            "callback_port": 5999,
            "step_timeout_seconds": 600,
        }

        call_order, tracking_move, tracking_post = _make_ordering_tracker()

        def failing_gates(*args, **kwargs):
            return {
                "passed": False,
                "failures": [{"gate": "test_gate", "evidence": "forced failure"}],
                "is_qa_step": False,
                "files_changed": [],
                "plan_header": {"auto_close": "false"},
                "verdict_requested": {"requested": False, "body": None},
            }

        with patch("bellows._create_worktree", return_value="/tmp/wt"), \
             patch("bellows._capture_git_diff", return_value=""), \
             patch("bellows._teardown_worktree"), \
             patch("bellows.runner.run_step", return_value=_make_fake_run_step_result()), \
             patch("bellows.gates.check", side_effect=failing_gates), \
             patch("shutil.move", side_effect=tracking_move), \
             patch("bellows.verdict.post_verdict_request", side_effect=tracking_post), \
             patch("bellows.notifier.notify_verdict_request"), \
             patch("bellows.notifier.push"), \
             patch("bellows.record_run"), \
             patch("bellows.validators.validate_at_claim", return_value={"rejected": False, "reject_reason": "", "warnings": []}):
            response_server = MagicMock()
            bellows.run_plan(plan_path, config, response_server)

        assert "rename" in call_order, f"shutil.move to verdict-pending-* was not called: {call_order}"
        assert "verdict_post" in call_order, f"verdict.post_verdict_request was not called: {call_order}"
        rename_idx = call_order.index("rename")
        post_idx = call_order.index("verdict_post")
        assert rename_idx < post_idx, \
            f"Site 3: rename ({rename_idx}) must precede verdict_post ({post_idx}): {call_order}"


def test_pause_site_4_auto_close_teardown_failure_renames_before_post():
    """Site 4: Auto-close teardown failure — rename to verdict-pending-* must precede verdict.post_verdict_request."""
    with tempfile.TemporaryDirectory() as tmp:
        decisions_dir = os.path.join(tmp, "proj", "knowledge", "decisions")
        os.makedirs(decisions_dir)
        plan_filename = "executable-rv1-site4-2026-05-24.md"
        plan_path = os.path.join(decisions_dir, plan_filename)
        with open(plan_path, "w") as f:
            f.write("## STEP 1\nDo stuff.\n")

        config = {
            "default_model": "claude-sonnet-4-6",
            "pushover": {"app_key": "", "user_key": ""},
            "callback_port": 5999,
            "step_timeout_seconds": 600,
        }

        call_order, tracking_move, tracking_post = _make_ordering_tracker()

        with patch("bellows._create_worktree", return_value="/tmp/wt"), \
             patch("bellows._capture_git_diff", return_value=""), \
             patch("bellows._teardown_worktree",
                   side_effect=bellows.WorktreeTeardownError("merge conflict")), \
             patch("bellows.runner.run_step", return_value=_make_fake_run_step_result()), \
             patch("bellows.gates.check", return_value=_clean_gates()), \
             patch("shutil.move", side_effect=tracking_move), \
             patch("bellows.verdict.post_verdict_request", side_effect=tracking_post), \
             patch("bellows.notifier.push"), \
             patch("bellows.record_run"), \
             patch("bellows.validators.validate_at_claim", return_value={"rejected": False, "reject_reason": "", "warnings": []}):
            response_server = MagicMock()
            bellows.run_plan(plan_path, config, response_server)

        assert "rename" in call_order, f"shutil.move to verdict-pending-* was not called: {call_order}"
        assert "verdict_post" in call_order, f"verdict.post_verdict_request was not called: {call_order}"
        rename_idx = call_order.index("rename")
        post_idx = call_order.index("verdict_post")
        assert rename_idx < post_idx, \
            f"Site 4: rename ({rename_idx}) must precede verdict_post ({post_idx}): {call_order}"


def test_gates_log_includes_failure_gates_and_files_changed_count():
    """Fix F: gate log message must include failure gate names and files_changed count."""
    with tempfile.TemporaryDirectory() as tmp:
        decisions_dir = os.path.join(tmp, "proj", "knowledge", "decisions")
        os.makedirs(decisions_dir)
        plan_filename = "executable-gate-log-expand-2026-05-26.md"
        plan_path = os.path.join(decisions_dir, plan_filename)
        with open(plan_path, "w") as f:
            f.write("## STEP 1\nDo stuff.\n")

        config = {
            "default_model": "claude-sonnet-4-6",
            "pushover": {"app_key": "", "user_key": ""},
            "callback_port": 5999,
            "step_timeout_seconds": 600,
        }

        def failing_gates_with_files(*args, **kwargs):
            return {
                "passed": False,
                "failures": [
                    {"gate": "scope_check", "evidence": "out-of-scope"},
                    {"gate": "deposit_exists", "evidence": "missing deposit"},
                ],
                "is_qa_step": False,
                "files_changed": ["a.py", "b.py", "c.py"],
                "plan_header": {"auto_close": "false"},
                "verdict_requested": {"requested": False, "body": None},
            }

        log_calls = []
        original_log = bellows._log

        def capture_log(level, msg, **kwargs):
            log_calls.append((level, msg))
            original_log(level, msg, **kwargs)

        with patch("bellows._create_worktree", return_value="/tmp/wt"), \
             patch("bellows._capture_git_diff", return_value=""), \
             patch("bellows._teardown_worktree"), \
             patch("bellows.runner.run_step", return_value=_make_fake_run_step_result()), \
             patch("bellows.gates.check", side_effect=failing_gates_with_files), \
             patch("bellows._log", side_effect=capture_log), \
             patch("shutil.move"), \
             patch("bellows.verdict.post_verdict_request", return_value="/tmp/verdict.md"), \
             patch("bellows.notifier.notify_verdict_request"), \
             patch("bellows.notifier.push"), \
             patch("bellows.record_run"), \
             patch("bellows.validators.validate_at_claim", return_value={"rejected": False, "reject_reason": "", "warnings": []}):
            response_server = MagicMock()
            bellows.run_plan(plan_path, config, response_server)

        gate_log_msgs = [msg for level, msg in log_calls if "gates step" in msg]
        assert len(gate_log_msgs) >= 1, f"Expected at least one 'gates step' log, got: {log_calls}"
        msg = gate_log_msgs[0]
        assert "scope_check" in msg, f"Expected 'scope_check' in gate log, got: {msg}"
        assert "deposit_exists" in msg, f"Expected 'deposit_exists' in gate log, got: {msg}"
        assert "files_changed=3" in msg, f"Expected 'files_changed=3' in gate log, got: {msg}"
