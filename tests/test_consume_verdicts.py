"""Regression tests for cleanup slug normalization in _consume_verdicts and startup sweep."""
import os
import re
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import bellows
from conftest import clear_plan_for_test


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


def test_cleanup_normalizes_prefixed_verdict_slug():
    """Cleanup must delete verdict-request files even when the verdict filename includes
    a plan-type prefix (e.g. verdict-diagnostic-foo-...) that differs from the
    verdict-request filename (verdict-request-foo-...)."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)

        decisions_dir = tmp_path / "proj" / "knowledge" / "decisions"
        decisions_dir.mkdir(parents=True)
        done_dir = decisions_dir / "Done"
        done_dir.mkdir()

        # Plan file in verdict-pending state
        plan_filename = "diagnostic-foo-2026-05-01.md"
        verdict_pending_name = f"verdict-pending-{plan_filename}"
        verdict_pending_path = decisions_dir / verdict_pending_name
        verdict_pending_path.write_text("## Diagnostic\nSingle-step.\n")

        # Verdict in resolved/ — includes the plan-type prefix (the bug trigger)
        verdicts_resolved = tmp_path / "verdicts" / "resolved"
        verdicts_resolved.mkdir(parents=True)
        verdict_fname = "verdict-diagnostic-foo-2026-05-01-step-1.md"
        (verdicts_resolved / verdict_fname).write_text("continue\nApproved.")

        # Verdict-request file — uses stripped slug (as verdict.py creates it)
        pending_dir = tmp_path / "verdicts" / "pending"
        pending_dir.mkdir(parents=True)
        pending_file = pending_dir / "verdict-request-foo-2026-05-01-step-1.md"
        pending_file.write_text(
            "# Verdict Request\n**Plan:** " + str(verdict_pending_path) +
            '\n**Gate Result JSON:** {"failures": [], "files_changed": []}')

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

        assert not pending_file.exists(), (
            f"Verdict-request file should have been deleted by cleanup with normalized slug: {pending_file}"
        )


def test_cleanup_unprefixed_verdict_slug():
    """Cleanup must still work when the verdict filename does NOT include a plan-type
    prefix — backward compatibility for verdicts like verdict-foo-...-step-1.md."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)

        decisions_dir = tmp_path / "proj" / "knowledge" / "decisions"
        decisions_dir.mkdir(parents=True)
        done_dir = decisions_dir / "Done"
        done_dir.mkdir()

        plan_filename = "executable-qux-2026-05-01.md"
        verdict_pending_name = f"verdict-pending-{plan_filename}"
        verdict_pending_path = decisions_dir / verdict_pending_name
        verdict_pending_path.write_text("## STEP 1\nDo stuff.\n")

        verdicts_resolved = tmp_path / "verdicts" / "resolved"
        verdicts_resolved.mkdir(parents=True)
        # Verdict WITHOUT plan-type prefix (backward-compatible form)
        verdict_fname = "verdict-qux-2026-05-01-step-1.md"
        (verdicts_resolved / verdict_fname).write_text("continue\nApproved.")

        pending_dir = tmp_path / "verdicts" / "pending"
        pending_dir.mkdir(parents=True)
        pending_file = pending_dir / "verdict-request-qux-2026-05-01-step-1.md"
        pending_file.write_text(
            "# Verdict Request\n**Plan:** " + str(verdict_pending_path) +
            '\n**Gate Result JSON:** {"failures": [], "files_changed": []}')

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

        assert not pending_file.exists(), (
            f"Verdict-request file should have been deleted by cleanup with unprefixed slug: {pending_file}"
        )


def test_consume_verdicts_skips_verdict_request_files():
    """S3 Fix B: _consume_verdicts must skip verdict-request-* files in resolved/."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)

        decisions_dir = tmp_path / "proj" / "knowledge" / "decisions"
        decisions_dir.mkdir(parents=True)
        (decisions_dir / "Done").mkdir()

        verdicts_resolved = tmp_path / "verdicts" / "resolved"
        verdicts_resolved.mkdir(parents=True)
        # Drop a verdict-request-* file with valid verdict content
        request_file = verdicts_resolved / "verdict-request-foo-step-1.md"
        request_file.write_text("verdict: continue\nReason text.")

        config = {
            "watched_projects": [str(decisions_dir)],
            "default_model": "claude-sonnet-4-6",
            "pushover": {"app_key": "", "user_key": ""},
            "callback_port": 5999,
        }

        b = bellows.Bellows(config)

        with patch("bellows.BELLOWS_ROOT", tmp_path), \
             patch("bellows.verdict.check_verdict") as mock_check, \
             patch("bellows.verdict.log_to_ledger"), \
             patch("bellows.notifier.push"):
            b._consume_verdicts()

        # check_verdict must NOT have been called — the file should be skipped
        mock_check.assert_not_called()
        # The file must remain in place, not renamed to processed-
        assert request_file.exists(), (
            "verdict-request-* file should remain in place, not processed"
        )
        assert not (verdicts_resolved / "processed-verdict-request-foo-step-1.md").exists(), (
            "verdict-request-* file should NOT be renamed to processed-"
        )


def test_dispatch_starts_fresh_when_db_has_orphan_slug_rows():
    """When a new executable plan is deposited and the DB contains rows for the same slug
    from a prior session (orphan rows from a Done/ or halted plan), Bellows must dispatch
    step 1 fresh — not phantom-resume to a later step. Regression for the 2026-05-01
    phantom-resume bug fixed by F3 removal of Phase 3b/3c DB-resume logic."""
    import sqlite3
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)

        decisions_dir = tmp_path / "proj" / "knowledge" / "decisions"
        decisions_dir.mkdir(parents=True)
        (decisions_dir / "Done").mkdir()

        plan_filename = "executable-regression-slug-collision-2026-05-01.md"
        plan_path = decisions_dir / plan_filename
        plan_content = "## STEP 1\nDo stuff.\n## STEP 2\nDo more stuff.\n"
        plan_path.write_text(plan_content)
        clear_plan_for_test(str(plan_path))

        # Create shadow cache (simulates a prior same-slug plan leaving shadow behind)
        shadow_path = bellows._shadow_path(plan_filename)
        shadow_path.parent.mkdir(parents=True, exist_ok=True)
        shadow_path.write_text(plan_content)

        # Insert orphan DB rows for the same slug (prior session completed steps 1+2)
        db_path = str(tmp_path / "test.db")
        conn = sqlite3.connect(db_path)
        conn.execute(
            "CREATE TABLE IF NOT EXISTS runs "
            "(id INTEGER PRIMARY KEY, plan_path TEXT, project TEXT, session_id TEXT, "
            "step INTEGER, status TEXT, cost_usd REAL, started_at TEXT, completed_at TEXT, "
            "timestamp TEXT, cost REAL, plan_slug TEXT)"
        )
        plan_slug = bellows.verdict.slug_from_path(plan_filename)
        for step in (1, 2):
            conn.execute(
                "INSERT INTO runs (timestamp, plan_path, project, session_id, step, status, cost, plan_slug) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                ("2026-05-01T10:00:00", str(plan_path), "proj", "old-session", step, "Complete", 0.01, plan_slug),
            )
        conn.commit()
        conn.close()

        config = {
            "default_model": "claude-sonnet-4-6",
            "pushover": {"app_key": "", "user_key": ""},
            "callback_port": 5999,
            "step_timeout_seconds": 600,
        }

        with patch("bellows.runner.run_step", return_value=_make_fake_run_step_result()) as mock_run_step, \
             patch("bellows.gates.check", return_value=_clean_gates()), \
             patch("bellows.notifier.push"), \
             patch("bellows.verdict.log_to_ledger"), \
             patch("bellows._capture_git_diff", return_value=""), \
             patch("bellows._create_worktree", return_value="/tmp/wt"), \
             patch("bellows._teardown_worktree"), \
             patch("bellows.record_run"), \
             patch("bellows.DB_PATH", db_path), \
             patch("bellows.validators.validate_at_claim", return_value={"rejected": False, "reject_reason": "", "warnings": []}):
            response_server = MagicMock()
            bellows.run_plan(str(plan_path), config, response_server, resume_step=None)

        # The FIRST call's bootstrap prompt must dispatch Step 1, not phantom-resume to Step 3
        first_prompt = mock_run_step.call_args_list[0][0][0]
        assert "Step 1" in first_prompt, (
            f"Expected first bootstrap prompt to dispatch Step 1, got: {first_prompt}"
        )
        assert "Step 3" not in first_prompt, (
            f"Bootstrap prompt should NOT resume at Step 3 (phantom-resume bug): {first_prompt}"
        )


def test_consume_verdicts_marks_resolved_processed_when_plan_halted():
    """S3 Bug C: a resolved verdict whose plan is halted-* in decisions/ (not in Done/)
    must be moved to processed-*, not left in resolved/ for retry."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)

        decisions_dir = tmp_path / "proj" / "knowledge" / "decisions"
        decisions_dir.mkdir(parents=True)
        (decisions_dir / "Done").mkdir()

        # Halted plan in decisions/ (NOT in Done/)
        halted_plan = decisions_dir / "halted-executable-foo-2026-05-09.md"
        halted_plan.write_text("## STEP 1\nDo stuff.\n## STEP 2\nMore stuff.\n")

        # Verdict in resolved/ referencing the halted plan's slug
        verdicts_resolved = tmp_path / "verdicts" / "resolved"
        verdicts_resolved.mkdir(parents=True)
        verdict_fname = "verdict-executable-foo-2026-05-09-step-2.md"
        (verdicts_resolved / verdict_fname).write_text("verdict: stop\nHalted by Planner.")

        # Empty pending/ (no pending request file — simulating prior cleanup)
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
                 "found": True, "verdict": "stop", "reason": "halted"
             }), \
             patch("bellows.verdict.log_to_ledger"), \
             patch("bellows.notifier.push"):
            b._consume_verdicts()

        # Verdict file must be renamed to processed-*
        processed_path = verdicts_resolved / f"processed-{verdict_fname}"
        assert processed_path.exists(), (
            f"Verdict file should have been moved to processed-: {processed_path}"
        )
        assert not (verdicts_resolved / verdict_fname).exists(), (
            f"Original verdict file should no longer exist in resolved/: {verdict_fname}"
        )
        # Halted plan file must be unchanged
        assert halted_plan.exists(), (
            f"Halted plan file should remain unchanged: {halted_plan}"
        )


def test_startup_sweep_removes_done_plan_orphans():
    """Startup sweep must remove orphaned verdict-request files whose plans are in Done/.
    Previously, Done/ plan slugs were added to active_slugs, protecting these orphans."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)

        decisions_dir = tmp_path / "proj" / "knowledge" / "decisions"
        decisions_dir.mkdir(parents=True)
        done_dir = decisions_dir / "Done"
        done_dir.mkdir()

        # Plan in Done/ (terminal state)
        done_plan = done_dir / "executable-bar-2026-05-01.md"
        done_plan.write_text("## STEP 1\nDone.\n")

        # Orphaned verdict-request for the done plan
        pending_dir = tmp_path / "verdicts" / "pending"
        pending_dir.mkdir(parents=True)
        orphan_file = pending_dir / "verdict-request-bar-2026-05-01-step-1.md"
        orphan_file.write_text("# Verdict Request\nOrphan.")

        config = {
            "watched_projects": [str(decisions_dir)],
            "default_model": "claude-sonnet-4-6",
            "pushover": {"app_key": "", "user_key": ""},
            "callback_port": 5999,
        }

        b = bellows.Bellows(config)

        with patch("bellows.BELLOWS_ROOT", tmp_path):
            orphaned_removed = b._perform_startup_sweep()

        assert not orphan_file.exists(), (
            f"Orphaned verdict-request for Done/ plan should have been removed by startup sweep: {orphan_file}"
        )
        assert "verdict-request-bar-2026-05-01-step-1.md" in orphaned_removed


def _make_verdict_request_content(plan_path, step_number=1, total_steps=2,
                                   pause_reason_code="gate_failure",
                                   precondition_failure=None,
                                   gate_result_json=None):
    """Build verdict-request content with the fields that _consume_verdicts parses."""
    lines = [
        "# Verdict Request",
        f"**Plan:** {plan_path}",
        f"**Step:** {step_number}",
        f"**Total Steps:** {total_steps}",
        f"**Pause Reason Code:** {pause_reason_code}",
    ]
    if precondition_failure is not None:
        lines.append(f"**Precondition Failure:** {'true' if precondition_failure else 'false'}")
    if gate_result_json is not None:
        import json
        lines.append(f"**Gate Result JSON:** {json.dumps(gate_result_json)}")
    return "\n".join(lines)


def test_consume_verdict_continue_advances_step_when_precondition_failure_absent():
    """Backward-compat: verdict-request WITHOUT Precondition Failure field → advance step_number + 1."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)

        decisions_dir = tmp_path / "proj" / "knowledge" / "decisions"
        decisions_dir.mkdir(parents=True)
        (decisions_dir / "Done").mkdir()

        plan_filename = "executable-precond-absent-2026-05-24.md"
        verdict_pending_name = f"verdict-pending-{plan_filename}"
        verdict_pending_path = decisions_dir / verdict_pending_name
        verdict_pending_path.write_text("## STEP 1\nDo stuff.\n## STEP 2\nMore stuff.\n")

        verdicts_resolved = tmp_path / "verdicts" / "resolved"
        verdicts_resolved.mkdir(parents=True)
        verdict_fname = "verdict-precond-absent-2026-05-24-step-1.md"
        (verdicts_resolved / verdict_fname).write_text("continue\nApproved.")

        pending_dir = tmp_path / "verdicts" / "pending"
        pending_dir.mkdir(parents=True)
        pending_file = pending_dir / "verdict-request-precond-absent-2026-05-24-step-1.md"
        # No precondition_failure field — simulates pre-fix verdict-request files
        pending_file.write_text(_make_verdict_request_content(
            str(verdict_pending_path), step_number=1, total_steps=2,
            precondition_failure=None,
            gate_result_json={"failures": [], "files_changed": []}))

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
        call_kwargs = mock_handle.call_args
        assert call_kwargs[1]["resume_step"] == 2, (
            f"Expected resume_step=2 (advance) when Precondition Failure absent, got {call_kwargs[1]['resume_step']}"
        )


def test_consume_verdict_continue_advances_step_when_precondition_failure_false():
    """Explicit false: verdict-request with Precondition Failure: false → advance step_number + 1."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)

        decisions_dir = tmp_path / "proj" / "knowledge" / "decisions"
        decisions_dir.mkdir(parents=True)
        (decisions_dir / "Done").mkdir()

        plan_filename = "executable-precond-false-2026-05-24.md"
        verdict_pending_name = f"verdict-pending-{plan_filename}"
        verdict_pending_path = decisions_dir / verdict_pending_name
        verdict_pending_path.write_text("## STEP 1\nDo stuff.\n## STEP 2\nMore stuff.\n")

        verdicts_resolved = tmp_path / "verdicts" / "resolved"
        verdicts_resolved.mkdir(parents=True)
        verdict_fname = "verdict-precond-false-2026-05-24-step-1.md"
        (verdicts_resolved / verdict_fname).write_text("continue\nApproved.")

        pending_dir = tmp_path / "verdicts" / "pending"
        pending_dir.mkdir(parents=True)
        pending_file = pending_dir / "verdict-request-precond-false-2026-05-24-step-1.md"
        pending_file.write_text(_make_verdict_request_content(
            str(verdict_pending_path), step_number=1, total_steps=2,
            precondition_failure=False,
            gate_result_json={"failures": [], "files_changed": []}))

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
        call_kwargs = mock_handle.call_args
        assert call_kwargs[1]["resume_step"] == 2, (
            f"Expected resume_step=2 (advance) when Precondition Failure is false, got {call_kwargs[1]['resume_step']}"
        )


def test_consume_verdict_continue_retries_step_when_precondition_failure_true():
    """Precondition failure: verdict-request with Precondition Failure: true → retry same step."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)

        decisions_dir = tmp_path / "proj" / "knowledge" / "decisions"
        decisions_dir.mkdir(parents=True)
        (decisions_dir / "Done").mkdir()

        plan_filename = "executable-precond-true-2026-05-24.md"
        verdict_pending_name = f"verdict-pending-{plan_filename}"
        verdict_pending_path = decisions_dir / verdict_pending_name
        verdict_pending_path.write_text("## STEP 1\nDo stuff.\n## STEP 2\nMore stuff.\n")

        verdicts_resolved = tmp_path / "verdicts" / "resolved"
        verdicts_resolved.mkdir(parents=True)
        verdict_fname = "verdict-precond-true-2026-05-24-step-1.md"
        (verdicts_resolved / verdict_fname).write_text("continue\nApproved.")

        pending_dir = tmp_path / "verdicts" / "pending"
        pending_dir.mkdir(parents=True)
        pending_file = pending_dir / "verdict-request-precond-true-2026-05-24-step-1.md"
        pending_file.write_text(_make_verdict_request_content(
            str(verdict_pending_path), step_number=1, total_steps=2,
            precondition_failure=True))

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
        call_kwargs = mock_handle.call_args
        assert call_kwargs[1]["resume_step"] == 1, (
            f"Expected resume_step=1 (retry) when Precondition Failure is true, got {call_kwargs[1]['resume_step']}"
        )


def test_consume_verdicts_rejects_continue_with_unoverridden_failures_final_step():
    """E4: continue verdict on final step with unoverridden gate failures is rejected."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)

        decisions_dir = tmp_path / "proj" / "knowledge" / "decisions"
        decisions_dir.mkdir(parents=True)
        (decisions_dir / "Done").mkdir()

        plan_filename = "executable-gate-json-done-2026-05-26.md"
        verdict_pending_name = f"verdict-pending-{plan_filename}"
        verdict_pending_path = decisions_dir / verdict_pending_name
        verdict_pending_path.write_text("## STEP 1\nDo stuff.\n")

        verdicts_resolved = tmp_path / "verdicts" / "resolved"
        verdicts_resolved.mkdir(parents=True)
        verdict_fname = "verdict-gate-json-done-2026-05-26-step-1.md"
        (verdicts_resolved / verdict_fname).write_text("continue\nApproved.")

        pending_dir = tmp_path / "verdicts" / "pending"
        pending_dir.mkdir(parents=True)
        pending_file = pending_dir / "verdict-request-gate-json-done-2026-05-26-step-1.md"
        gate_data = {
            "failures": [{"gate": "scope_check", "evidence": "out-of-scope"}],
            "files_changed": ["a.py", "b.py"],
        }
        pending_file.write_text(_make_verdict_request_content(
            str(verdict_pending_path), step_number=1, total_steps=1,
            gate_result_json=gate_data))

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
             patch("bellows.notifier.push"), \
             patch("bellows.lifecycle.record_verdict_outcome") as mock_record, \
             patch("bellows.lifecycle.record_verdict_request"):
            b._consume_verdicts()

        assert verdict_pending_path.exists(), "Plan must stay verdict-pending after rejection"
        rejected_verdict = verdicts_resolved / f"processed-rejected-{verdict_fname}"
        assert rejected_verdict.exists(), f"Verdict must be renamed to processed-rejected-: {rejected_verdict}"
        assert pending_file.exists(), "Request file must be preserved on rejection"
        mock_ledger.assert_called_once()
        assert mock_ledger.call_args[0][3] == "continue-rejected"
        mock_record.assert_called_once()
        assert mock_record.call_args[1]["decided_by"] == "gate_recheck"


def test_consume_verdicts_advances_continue_to_done_with_clean_gates():
    """E4: continue verdict on final step with clean gates advances to Done."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)

        decisions_dir = tmp_path / "proj" / "knowledge" / "decisions"
        decisions_dir.mkdir(parents=True)
        (decisions_dir / "Done").mkdir()

        plan_filename = "executable-gate-json-done-clean-2026-05-26.md"
        verdict_pending_name = f"verdict-pending-{plan_filename}"
        verdict_pending_path = decisions_dir / verdict_pending_name
        verdict_pending_path.write_text("## STEP 1\nDo stuff.\n")

        verdicts_resolved = tmp_path / "verdicts" / "resolved"
        verdicts_resolved.mkdir(parents=True)
        verdict_fname = "verdict-gate-json-done-clean-2026-05-26-step-1.md"
        (verdicts_resolved / verdict_fname).write_text("continue\nApproved.")

        pending_dir = tmp_path / "verdicts" / "pending"
        pending_dir.mkdir(parents=True)
        pending_file = pending_dir / "verdict-request-gate-json-done-clean-2026-05-26-step-1.md"
        gate_data = {"failures": [], "files_changed": ["a.py", "b.py"]}
        pending_file.write_text(_make_verdict_request_content(
            str(verdict_pending_path), step_number=1, total_steps=1,
            gate_result_json=gate_data))

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
             patch("bellows.notifier.push"):
            b._consume_verdicts()

        done_path = decisions_dir / "Done" / plan_filename
        assert done_path.is_file(), f"Plan should move to Done with clean gates: {done_path}"
        mock_ledger.assert_called_once()
        assert mock_ledger.call_args[0][3] == "continue-to-done"


def test_consume_verdicts_rejects_continue_with_unoverridden_failures_resume():
    """E4: continue verdict on non-final step with unoverridden gate failures is rejected."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)

        decisions_dir = tmp_path / "proj" / "knowledge" / "decisions"
        decisions_dir.mkdir(parents=True)
        (decisions_dir / "Done").mkdir()

        plan_filename = "executable-gate-json-resume-2026-05-26.md"
        verdict_pending_name = f"verdict-pending-{plan_filename}"
        verdict_pending_path = decisions_dir / verdict_pending_name
        verdict_pending_path.write_text("## STEP 1\nDo stuff.\n## STEP 2\nMore stuff.\n")

        verdicts_resolved = tmp_path / "verdicts" / "resolved"
        verdicts_resolved.mkdir(parents=True)
        verdict_fname = "verdict-gate-json-resume-2026-05-26-step-1.md"
        (verdicts_resolved / verdict_fname).write_text("continue\nApproved.")

        pending_dir = tmp_path / "verdicts" / "pending"
        pending_dir.mkdir(parents=True)
        pending_file = pending_dir / "verdict-request-gate-json-resume-2026-05-26-step-1.md"
        gate_data = {
            "failures": [{"gate": "deposit_exists", "evidence": "missing deposit"}],
            "files_changed": ["src/main.py"],
        }
        pending_file.write_text(_make_verdict_request_content(
            str(verdict_pending_path), step_number=1, total_steps=2,
            gate_result_json=gate_data))

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
             patch("bellows.notifier.push"), \
             patch("bellows.lifecycle.record_verdict_outcome") as mock_record, \
             patch("bellows.lifecycle.record_verdict_request"), \
             patch.object(b, "handle_new_plan") as mock_handle:
            b._consume_verdicts()

        mock_handle.assert_not_called()
        assert verdict_pending_path.exists(), "Plan must stay verdict-pending after rejection"
        rejected_verdict = verdicts_resolved / f"processed-rejected-{verdict_fname}"
        assert rejected_verdict.exists(), f"Verdict must be renamed to processed-rejected-"
        assert pending_file.exists(), "Request file must be preserved on rejection"
        mock_ledger.assert_called_once()
        assert mock_ledger.call_args[0][3] == "continue-rejected"
        mock_record.assert_called_once()
        assert mock_record.call_args[1]["decided_by"] == "gate_recheck"


def test_consume_verdicts_advances_continue_resume_with_clean_gates():
    """E4: continue verdict on non-final step with clean gates advances normally."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)

        decisions_dir = tmp_path / "proj" / "knowledge" / "decisions"
        decisions_dir.mkdir(parents=True)
        (decisions_dir / "Done").mkdir()

        plan_filename = "executable-gate-json-resume-clean-2026-05-26.md"
        verdict_pending_name = f"verdict-pending-{plan_filename}"
        verdict_pending_path = decisions_dir / verdict_pending_name
        verdict_pending_path.write_text("## STEP 1\nDo stuff.\n## STEP 2\nMore stuff.\n")

        verdicts_resolved = tmp_path / "verdicts" / "resolved"
        verdicts_resolved.mkdir(parents=True)
        verdict_fname = "verdict-gate-json-resume-clean-2026-05-26-step-1.md"
        (verdicts_resolved / verdict_fname).write_text("continue\nApproved.")

        pending_dir = tmp_path / "verdicts" / "pending"
        pending_dir.mkdir(parents=True)
        pending_file = pending_dir / "verdict-request-gate-json-resume-clean-2026-05-26-step-1.md"
        gate_data = {"failures": [], "files_changed": ["src/main.py"]}
        pending_file.write_text(_make_verdict_request_content(
            str(verdict_pending_path), step_number=1, total_steps=2,
            gate_result_json=gate_data))

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
             patch("bellows.notifier.push"), \
             patch.object(b, "handle_new_plan") as mock_handle:
            b._consume_verdicts()

        mock_handle.assert_called_once()
        _, kwargs = mock_handle.call_args
        assert kwargs.get("resume_step") == 2, f"Expected resume_step=2, got: {mock_handle.call_args}"


def test_consume_verdicts_refuses_when_gate_result_json_absent():
    """E4 fail-closed: pending file without Gate Result JSON → continue refused as unverifiable."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)

        decisions_dir = tmp_path / "proj" / "knowledge" / "decisions"
        decisions_dir.mkdir(parents=True)
        (decisions_dir / "Done").mkdir()

        plan_filename = "executable-gate-json-absent-2026-05-26.md"
        verdict_pending_name = f"verdict-pending-{plan_filename}"
        verdict_pending_path = decisions_dir / verdict_pending_name
        verdict_pending_path.write_text("## STEP 1\nDo stuff.\n")

        verdicts_resolved = tmp_path / "verdicts" / "resolved"
        verdicts_resolved.mkdir(parents=True)
        verdict_fname = "verdict-gate-json-absent-2026-05-26-step-1.md"
        (verdicts_resolved / verdict_fname).write_text("continue\nApproved.")

        pending_dir = tmp_path / "verdicts" / "pending"
        pending_dir.mkdir(parents=True)
        pending_file = pending_dir / "verdict-request-gate-json-absent-2026-05-26-step-1.md"
        pending_file.write_text(_make_verdict_request_content(
            str(verdict_pending_path), step_number=1, total_steps=1))

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
             patch("bellows.notifier.push"), \
             patch("bellows.lifecycle.record_verdict_outcome"), \
             patch("bellows.lifecycle.record_verdict_request"):
            b._consume_verdicts()

        assert verdict_pending_path.exists(), "Plan must stay verdict-pending (refusal)"
        rejected_verdict = verdicts_resolved / f"processed-rejected-{verdict_fname}"
        assert rejected_verdict.exists(), "Verdict must be renamed to processed-rejected-"
        assert pending_file.exists(), "Request file must be preserved on refusal"
        mock_ledger.assert_called_once()
        assert mock_ledger.call_args[0][3] == "continue-rejected"


def test_no_match_warning_logged_once():
    """Dedup guard: the no-match WARN fires exactly once across two rescan ticks for the same file."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)

        decisions_dir = tmp_path / "proj" / "knowledge" / "decisions"
        decisions_dir.mkdir(parents=True)
        (decisions_dir / "Done").mkdir()

        # Verdict in resolved/ with no paired verdict-pending-* plan and no Done/ or halted-* entry
        verdicts_resolved = tmp_path / "verdicts" / "resolved"
        verdicts_resolved.mkdir(parents=True)
        verdict_fname = "verdict-no-match-dedup-2026-05-31-step-1.md"
        (verdicts_resolved / verdict_fname).write_text("continue\nApproved.")

        config = {
            "watched_projects": [str(decisions_dir)],
            "default_model": "claude-sonnet-4-6",
            "pushover": {"app_key": "", "user_key": ""},
            "callback_port": 5999,
        }

        b = bellows.Bellows(config)

        # Reset module-level dedup set to prevent state leak from prior tests
        bellows._warned_no_match.clear()

        warn_messages = []

        def capture_log(level, msg, slug=None, suppress_timer_update=False):
            if level == "WARN":
                warn_messages.append(msg)

        with patch("bellows.BELLOWS_ROOT", tmp_path), \
             patch("bellows.verdict.check_verdict", return_value={
                 "found": True, "verdict": "continue", "reason": "approved"
             }), \
             patch("bellows._log", side_effect=capture_log):
            # Two rescan ticks — verdict is found but no matching verdict-pending plan exists
            b._consume_verdicts()
            b._consume_verdicts()

        no_match_warns = [m for m in warn_messages if "no verdict-pending plan found" in m]
        assert len(no_match_warns) == 1, (
            f"Expected exactly 1 no-match WARN across two ticks, got {len(no_match_warns)}: {no_match_warns}"
        )
        # File must remain in resolved/ (not consumed or moved)
        assert (verdicts_resolved / verdict_fname).exists(), (
            "Verdict file should remain in resolved/ when no match found"
        )


def test_no_match_warning_cleared_when_file_leaves_resolved():
    """Clear-on-leave: after a no-match WARN fires, making the slug stale causes the file to be
    moved to processed-* AND fname is removed from _warned_no_match."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)

        decisions_dir = tmp_path / "proj" / "knowledge" / "decisions"
        decisions_dir.mkdir(parents=True)
        done_dir = decisions_dir / "Done"
        done_dir.mkdir()

        # Verdict in resolved/ — no match initially
        verdicts_resolved = tmp_path / "verdicts" / "resolved"
        verdicts_resolved.mkdir(parents=True)
        verdict_fname = "verdict-no-match-clear-2026-05-31-step-1.md"
        (verdicts_resolved / verdict_fname).write_text("continue\nApproved.")

        config = {
            "watched_projects": [str(decisions_dir)],
            "default_model": "claude-sonnet-4-6",
            "pushover": {"app_key": "", "user_key": ""},
            "callback_port": 5999,
        }

        b = bellows.Bellows(config)

        # Reset module-level dedup set
        bellows._warned_no_match.clear()

        # Tick 1: verdict found but no matching verdict-pending plan — WARN fires, fname added to _warned_no_match
        with patch("bellows.BELLOWS_ROOT", tmp_path), \
             patch("bellows.verdict.check_verdict", return_value={
                 "found": True, "verdict": "continue", "reason": "approved"
             }), \
             patch("bellows.verdict.log_to_ledger"), \
             patch("bellows.notifier.push"):
            b._consume_verdicts()

        assert verdict_fname in bellows._warned_no_match, (
            "fname should be in _warned_no_match after first no-match WARN"
        )

        # Now make the slug stale: place a Done/ entry matching the slug
        done_plan = done_dir / "executable-no-match-clear-2026-05-31.md"
        done_plan.write_text("## STEP 1\nDone.\n")

        # Tick 2: stale branch fires — file moved to processed-*, fname cleared from set
        with patch("bellows.BELLOWS_ROOT", tmp_path), \
             patch("bellows.verdict.check_verdict", return_value={
                 "found": True, "verdict": "continue", "reason": "approved"
             }), \
             patch("bellows.verdict.log_to_ledger"), \
             patch("bellows.notifier.push"):
            b._consume_verdicts()

        processed_path = verdicts_resolved / f"processed-{verdict_fname}"
        assert processed_path.exists(), (
            f"Verdict file should have been moved to processed- on stale detection: {processed_path}"
        )
        assert not (verdicts_resolved / verdict_fname).exists(), (
            "Original verdict file should no longer exist in resolved/ after stale move"
        )
        assert verdict_fname not in bellows._warned_no_match, (
            "fname should be cleared from _warned_no_match after file leaves resolved/"
        )


def test_continue_blocked_on_worktree_teardown_failure_interstep():
    """Guard: a continue verdict on a non-final step is REJECTED when the prior step's
    gate result carries an uncleared worktree_teardown failure. Plan routes to halted-."""
    import json
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)

        decisions_dir = tmp_path / "proj" / "knowledge" / "decisions"
        decisions_dir.mkdir(parents=True)
        (decisions_dir / "Done").mkdir()

        plan_filename = "executable-wt-block-interstep-2026-06-01.md"
        verdict_pending_name = f"verdict-pending-{plan_filename}"
        verdict_pending_path = decisions_dir / verdict_pending_name
        verdict_pending_path.write_text("## STEP 1\nDo stuff.\n## STEP 2\nMore stuff.\n")

        verdicts_resolved = tmp_path / "verdicts" / "resolved"
        verdicts_resolved.mkdir(parents=True)
        verdict_fname = "verdict-wt-block-interstep-2026-06-01-step-1.md"
        (verdicts_resolved / verdict_fname).write_text("continue\nApproved.")

        pending_dir = tmp_path / "verdicts" / "pending"
        pending_dir.mkdir(parents=True)
        pending_file = pending_dir / "verdict-request-wt-block-interstep-2026-06-01-step-1.md"
        gate_data = {
            "failures": [{"gate": "worktree_teardown", "evidence": "merge conflict on bellows-wt/wt-block-interstep-2026-06-01"}],
            "files_changed": ["bellows.py"],
        }
        pending_file.write_text(_make_verdict_request_content(
            str(verdict_pending_path), step_number=1, total_steps=2,
            gate_result_json=gate_data))

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
             patch("bellows.notifier.push"), \
             patch.object(b, "handle_new_plan") as mock_handle:
            b._consume_verdicts()

        # (a) Plan is halted, NOT in-progress or Done
        halted_path = decisions_dir / f"halted-{plan_filename}"
        assert halted_path.exists(), f"Plan should be routed to halted-: {halted_path}"
        assert not verdict_pending_path.exists(), "verdict-pending plan should no longer exist"
        assert not (decisions_dir / f"in-progress-{plan_filename}").exists(), "Plan must NOT advance to in-progress"
        done_path = decisions_dir / "Done" / plan_filename
        assert not done_path.exists(), "Plan must NOT be moved to Done/"

        # (b) Next step NOT dispatched
        mock_handle.assert_not_called()

        # (c) Ledger entry with correct action
        mock_ledger.assert_called_once()
        ledger_call = mock_ledger.call_args
        assert ledger_call[0][3] == "continue-blocked-worktree-teardown", (
            f"Expected ledger action 'continue-blocked-worktree-teardown', got: {ledger_call[0][3]}"
        )

        # (d) Verdict file moved to processed
        processed_path = verdicts_resolved / f"processed-{verdict_fname}"
        assert processed_path.exists(), f"Verdict file should be moved to processed-: {processed_path}"
        assert not (verdicts_resolved / verdict_fname).exists(), "Original verdict file should not remain"


def test_continue_to_done_blocked_on_worktree_teardown_failure_final_step():
    """Guard on final step: continue verdict on the FINAL step is REJECTED when the prior
    step's gate result carries a worktree_teardown failure. Plan routes to halted-, NOT Done/."""
    import json
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)

        decisions_dir = tmp_path / "proj" / "knowledge" / "decisions"
        decisions_dir.mkdir(parents=True)
        (decisions_dir / "Done").mkdir()

        plan_filename = "executable-wt-block-final-2026-06-01.md"
        verdict_pending_name = f"verdict-pending-{plan_filename}"
        verdict_pending_path = decisions_dir / verdict_pending_name
        verdict_pending_path.write_text("## STEP 1\nDo stuff.\n")

        verdicts_resolved = tmp_path / "verdicts" / "resolved"
        verdicts_resolved.mkdir(parents=True)
        verdict_fname = "verdict-wt-block-final-2026-06-01-step-1.md"
        (verdicts_resolved / verdict_fname).write_text("continue\nApproved.")

        pending_dir = tmp_path / "verdicts" / "pending"
        pending_dir.mkdir(parents=True)
        pending_file = pending_dir / "verdict-request-wt-block-final-2026-06-01-step-1.md"
        gate_data = {
            "failures": [{"gate": "worktree_teardown", "evidence": "merge conflict on bellows-wt/wt-block-final-2026-06-01"}],
            "files_changed": [],
        }
        pending_file.write_text(_make_verdict_request_content(
            str(verdict_pending_path), step_number=1, total_steps=1,
            gate_result_json=gate_data))

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
             patch("bellows.notifier.push"):
            b._consume_verdicts()

        # Plan is halted, NOT in Done/
        halted_path = decisions_dir / f"halted-{plan_filename}"
        assert halted_path.exists(), f"Plan should be routed to halted-: {halted_path}"
        done_path = decisions_dir / "Done" / plan_filename
        assert not done_path.exists(), "Plan must NOT be moved to Done/ when teardown failed"
        assert not verdict_pending_path.exists(), "verdict-pending plan should no longer exist"

        # Ledger entry
        mock_ledger.assert_called_once()
        ledger_call = mock_ledger.call_args
        assert ledger_call[0][3] == "continue-blocked-worktree-teardown", (
            f"Expected ledger action 'continue-blocked-worktree-teardown', got: {ledger_call[0][3]}"
        )

        # Verdict file moved to processed
        processed_path = verdicts_resolved / f"processed-{verdict_fname}"
        assert processed_path.exists(), f"Verdict file should be moved to processed-: {processed_path}"


def test_plan_id_derivation_from_slug():
    """The regex-based _lc_plan_id derivation extracts correct integer ids from
    type-prefixed slugs, bare integers, and returns None for legacy slug+date names."""
    import re

    def _extract(slug):
        m = re.fullmatch(r"(?:(?:diagnostic|executable|qa)-)?(\d+)", slug)
        return int(m.group(1)) if m else None

    assert _extract("qa-149") == 149
    assert _extract("executable-148") == 148
    assert _extract("diagnostic-5") == 5
    assert _extract("148") == 148
    assert _extract("executable-foo-bar-2026-05-28") is None
    assert _extract("diagnostic-foo-2026-05-01") is None
    assert _extract("some-legacy-slug") is None


def test_consume_verdict_continue_to_done_calls_mark_plan_state_for_qa_plan():
    """A continue-to-done verdict for a qa-type plan (slug 'qa-149') must call
    lifecycle.mark_plan_state with the correct integer id (149), not skip it."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)

        decisions_dir = tmp_path / "proj" / "knowledge" / "decisions"
        decisions_dir.mkdir(parents=True)
        (decisions_dir / "Done").mkdir()

        plan_filename = "qa-149.md"
        verdict_pending_name = f"verdict-pending-{plan_filename}"
        verdict_pending_path = decisions_dir / verdict_pending_name
        verdict_pending_path.write_text("## STEP 1\nVerify stuff.\n")

        verdicts_resolved = tmp_path / "verdicts" / "resolved"
        verdicts_resolved.mkdir(parents=True)
        verdict_fname = "verdict-qa-149-step-1.md"
        (verdicts_resolved / verdict_fname).write_text("continue\nApproved.")

        pending_dir = tmp_path / "verdicts" / "pending"
        pending_dir.mkdir(parents=True)
        pending_file = pending_dir / "verdict-request-qa-149-step-1.md"
        pending_file.write_text(_make_verdict_request_content(
            str(verdict_pending_path), step_number=1, total_steps=1,
            gate_result_json={"failures": [], "files_changed": []}))

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
             patch("bellows.lifecycle.mark_plan_state") as mock_mark, \
             patch("bellows.lifecycle.record_verdict_outcome"), \
             patch("bellows.lifecycle.get_overridden_gates_for_step", return_value=set()):
            b._consume_verdicts()

        # mark_plan_state must be called with plan_id=149 and state="closed"
        mock_mark.assert_called_once()
        call_args = mock_mark.call_args
        assert call_args[0][0] == 149, (
            f"Expected plan_id=149, got: {call_args[0][0]}"
        )
        assert call_args[0][1] == "closed", (
            f"Expected state='closed', got: {call_args[0][1]}"
        )


def test_consume_verdict_stop_calls_mark_plan_state_for_qa_plan():
    """A stop verdict for a qa-type plan must call lifecycle.mark_plan_state with
    the correct integer id, not skip it due to type-prefix parse failure."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)

        decisions_dir = tmp_path / "proj" / "knowledge" / "decisions"
        decisions_dir.mkdir(parents=True)
        (decisions_dir / "Done").mkdir()

        plan_filename = "qa-200.md"
        verdict_pending_name = f"verdict-pending-{plan_filename}"
        verdict_pending_path = decisions_dir / verdict_pending_name
        verdict_pending_path.write_text("## STEP 1\nVerify stuff.\n## STEP 2\nMore.\n")

        verdicts_resolved = tmp_path / "verdicts" / "resolved"
        verdicts_resolved.mkdir(parents=True)
        verdict_fname = "verdict-qa-200-step-1.md"
        (verdicts_resolved / verdict_fname).write_text("stop\nBlocked.")

        pending_dir = tmp_path / "verdicts" / "pending"
        pending_dir.mkdir(parents=True)
        pending_file = pending_dir / "verdict-request-qa-200-step-1.md"
        pending_file.write_text(_make_verdict_request_content(
            str(verdict_pending_path), step_number=1, total_steps=2))

        config = {
            "watched_projects": [str(decisions_dir)],
            "default_model": "claude-sonnet-4-6",
            "pushover": {"app_key": "", "user_key": ""},
            "callback_port": 5999,
        }

        b = bellows.Bellows(config)

        with patch("bellows.BELLOWS_ROOT", tmp_path), \
             patch("bellows.verdict.check_verdict", return_value={
                 "found": True, "verdict": "stop", "reason": "blocked"
             }), \
             patch("bellows.verdict.log_to_ledger"), \
             patch("bellows.notifier.push"), \
             patch("bellows.lifecycle.mark_plan_state") as mock_mark, \
             patch("bellows.lifecycle.record_verdict_outcome"):
            b._consume_verdicts()

        mock_mark.assert_called_once()
        call_args = mock_mark.call_args
        assert call_args[0][0] == 200, (
            f"Expected plan_id=200, got: {call_args[0][0]}"
        )
        assert call_args[0][1] == "halted", (
            f"Expected state='halted', got: {call_args[0][1]}"
        )


def test_continue_advances_normally_without_teardown_failure():
    """Negative: a continue verdict with NO worktree_teardown failure advances normally
    (the guard does not false-trip). Plan moves to in-progress and next step is dispatched."""
    import json
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)

        decisions_dir = tmp_path / "proj" / "knowledge" / "decisions"
        decisions_dir.mkdir(parents=True)
        (decisions_dir / "Done").mkdir()

        plan_filename = "executable-wt-clean-advance-2026-06-01.md"
        verdict_pending_name = f"verdict-pending-{plan_filename}"
        verdict_pending_path = decisions_dir / verdict_pending_name
        verdict_pending_path.write_text("## STEP 1\nDo stuff.\n## STEP 2\nMore stuff.\n")

        verdicts_resolved = tmp_path / "verdicts" / "resolved"
        verdicts_resolved.mkdir(parents=True)
        verdict_fname = "verdict-wt-clean-advance-2026-06-01-step-1.md"
        (verdicts_resolved / verdict_fname).write_text("continue\nApproved.")

        pending_dir = tmp_path / "verdicts" / "pending"
        pending_dir.mkdir(parents=True)
        pending_file = pending_dir / "verdict-request-wt-clean-advance-2026-06-01-step-1.md"
        # Clean gate result — no worktree_teardown failure
        gate_data = {
            "failures": [],
            "files_changed": ["bellows.py"],
        }
        pending_file.write_text(_make_verdict_request_content(
            str(verdict_pending_path), step_number=1, total_steps=2,
            gate_result_json=gate_data))

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
             patch("bellows.notifier.push"), \
             patch.object(b, "handle_new_plan") as mock_handle:
            b._consume_verdicts()

        # Plan advances to in-progress, NOT halted
        inprogress_path = decisions_dir / f"in-progress-{plan_filename}"
        assert inprogress_path.exists(), f"Plan should advance to in-progress-: {inprogress_path}"
        halted_path = decisions_dir / f"halted-{plan_filename}"
        assert not halted_path.exists(), "Plan must NOT be routed to halted- on clean continue"

        # Next step dispatched
        mock_handle.assert_called_once()
        call_kwargs = mock_handle.call_args
        assert call_kwargs[1]["resume_step"] == 2, (
            f"Expected resume_step=2 (advance), got: {call_kwargs[1]['resume_step']}"
        )

        # Ledger action is regular continue, not blocked
        ledger_call = mock_ledger.call_args
        assert ledger_call[0][3] == "continue", (
            f"Expected ledger action 'continue', got: {ledger_call[0][3]}"
        )


# ---------------------------------------------------------------------------
# E4 gate re-check — new behavior tests
# ---------------------------------------------------------------------------


def test_continue_clean_advances_regression():
    """E4 regression: continue + clean gates (no failures) still advances."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        decisions_dir = tmp_path / "proj" / "knowledge" / "decisions"
        decisions_dir.mkdir(parents=True)
        (decisions_dir / "Done").mkdir()

        plan_filename = "executable-e4-clean-2026-08-24.md"
        verdict_pending_path = decisions_dir / f"verdict-pending-{plan_filename}"
        verdict_pending_path.write_text("## STEP 1\nDo stuff.\n## STEP 2\nMore.\n")

        verdicts_resolved = tmp_path / "verdicts" / "resolved"
        verdicts_resolved.mkdir(parents=True)
        verdict_fname = "verdict-e4-clean-2026-08-24-step-1.md"
        (verdicts_resolved / verdict_fname).write_text("continue\nApproved.")

        pending_dir = tmp_path / "verdicts" / "pending"
        pending_dir.mkdir(parents=True)
        pending_file = pending_dir / "verdict-request-e4-clean-2026-08-24-step-1.md"
        pending_file.write_text(_make_verdict_request_content(
            str(verdict_pending_path), step_number=1, total_steps=2,
            gate_result_json={"failures": [], "files_changed": []}))

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
        assert mock_handle.call_args[1]["resume_step"] == 2


def test_continue_failed_unoverridden_rejects():
    """E4: continue with unoverridden gate failures → rejected, plan stays verdict-pending,
    NULL row resolved continue-rejected PLUS fresh pending row, request file preserved,
    verdict file renamed, second scan is no-op (idempotency)."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        decisions_dir = tmp_path / "proj" / "knowledge" / "decisions"
        decisions_dir.mkdir(parents=True)
        (decisions_dir / "Done").mkdir()

        plan_filename = "executable-e4-reject-2026-08-24.md"
        verdict_pending_path = decisions_dir / f"verdict-pending-{plan_filename}"
        verdict_pending_path.write_text("## STEP 1\nDo stuff.\n## STEP 2\nMore.\n")

        verdicts_resolved = tmp_path / "verdicts" / "resolved"
        verdicts_resolved.mkdir(parents=True)
        verdict_fname = "verdict-e4-reject-2026-08-24-step-1.md"
        (verdicts_resolved / verdict_fname).write_text("continue\nApproved.")

        pending_dir = tmp_path / "verdicts" / "pending"
        pending_dir.mkdir(parents=True)
        pending_file = pending_dir / "verdict-request-e4-reject-2026-08-24-step-1.md"
        gate_data = {"failures": [{"gate": "no_errors", "evidence": "errors found"}], "files_changed": []}
        pending_file.write_text(_make_verdict_request_content(
            str(verdict_pending_path), step_number=1, total_steps=2,
            gate_result_json=gate_data))

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
             patch("bellows.notifier.push"), \
             patch("bellows.lifecycle.record_verdict_outcome") as mock_outcome, \
             patch("bellows.lifecycle.record_verdict_request") as mock_req, \
             patch.object(b, "handle_new_plan") as mock_handle:
            b._consume_verdicts()

        assert verdict_pending_path.exists(), "Plan must stay verdict-pending"
        assert pending_file.exists(), "Request file must be preserved (C-2)"
        rejected_verdict = verdicts_resolved / f"processed-rejected-{verdict_fname}"
        assert rejected_verdict.exists(), "Verdict must be renamed to processed-rejected-"
        mock_handle.assert_not_called()
        mock_outcome.assert_called_once()
        assert mock_outcome.call_args[0][2] == "continue-rejected"
        assert mock_outcome.call_args[1]["decided_by"] == "gate_recheck"
        mock_req.assert_called_once()

        # Idempotency: second scan is a no-op (verdict already renamed)
        with patch("bellows.BELLOWS_ROOT", tmp_path), \
             patch("bellows.verdict.check_verdict", return_value={"found": False}), \
             patch("bellows.notifier.push"):
            b._consume_verdicts()
        assert verdict_pending_path.exists(), "Plan must still be verdict-pending after re-scan"


def test_continue_failed_overridden_advances():
    """E4: continue with failures overridden in gate_events → advances."""
    import sqlite3
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        decisions_dir = tmp_path / "proj" / "knowledge" / "decisions"
        decisions_dir.mkdir(parents=True)
        (decisions_dir / "Done").mkdir()

        plan_filename = "executable-501.md"
        verdict_pending_path = decisions_dir / f"verdict-pending-{plan_filename}"
        verdict_pending_path.write_text("## STEP 1\nDo stuff.\n## STEP 2\nMore.\n")

        verdicts_resolved = tmp_path / "verdicts" / "resolved"
        verdicts_resolved.mkdir(parents=True)
        verdict_fname = "verdict-executable-501-step-1.md"
        (verdicts_resolved / verdict_fname).write_text("continue\nApproved.")

        pending_dir = tmp_path / "verdicts" / "pending"
        pending_dir.mkdir(parents=True)
        pending_file = pending_dir / "verdict-request-501-step-1.md"
        gate_data = {"failures": [{"gate": "scope_check", "evidence": "out-of-scope"}], "files_changed": []}
        pending_file.write_text(_make_verdict_request_content(
            str(verdict_pending_path), step_number=1, total_steps=2,
            gate_result_json=gate_data))

        # Set up tmp lifecycle DB with overridden gate_events row
        import lifecycle
        db_path = str(tmp_path / "lifecycle.db")
        lifecycle.init_lifecycle_db(db_path)
        conn = sqlite3.connect(db_path)
        conn.execute("INSERT INTO id_sequence (id, next_id) VALUES (1, 502) ON CONFLICT DO UPDATE SET next_id=502")
        conn.execute("INSERT INTO plans (id, type, target_project, lifecycle_state, created_at) VALUES (501, 'executable', 'proj', 'awaiting_verdict', '2026-08-24')")
        conn.execute("INSERT INTO steps (plan_id, step_number, status) VALUES (501, 1, 'awaiting_verdict')")
        step_id = conn.execute("SELECT id FROM steps WHERE plan_id=501 AND step_number=1").fetchone()[0]
        conn.execute("INSERT INTO gate_events (step_id, gate_name, result, overridden, override_ref) VALUES (?, 'scope_check', 'fail', 1, 'CEO approved')", (step_id,))
        conn.commit()
        conn.close()

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
             patch("bellows.lifecycle.LIFECYCLE_DB_PATH", db_path), \
             patch("bellows.lifecycle.record_verdict_outcome"), \
             patch.object(b, "handle_new_plan") as mock_handle:
            b._consume_verdicts()

        mock_handle.assert_called_once()
        assert mock_handle.call_args[1]["resume_step"] == 2


def test_request_file_absent_refuses():
    """E4 C-1: absent request file → refused as unverifiable (id-native WITH gate_events pass rows)."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        decisions_dir = tmp_path / "proj" / "knowledge" / "decisions"
        decisions_dir.mkdir(parents=True)
        (decisions_dir / "Done").mkdir()

        plan_filename = "executable-e4-absent-req-2026-08-24.md"
        verdict_pending_path = decisions_dir / f"verdict-pending-{plan_filename}"
        verdict_pending_path.write_text("## STEP 1\nDo stuff.\n")

        verdicts_resolved = tmp_path / "verdicts" / "resolved"
        verdicts_resolved.mkdir(parents=True)
        verdict_fname = "verdict-e4-absent-req-2026-08-24-step-1.md"
        (verdicts_resolved / verdict_fname).write_text("continue\nApproved.")

        pending_dir = tmp_path / "verdicts" / "pending"
        pending_dir.mkdir(parents=True)
        # No request file created

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
             patch("bellows.notifier.push"), \
             patch("bellows.lifecycle.record_verdict_outcome"), \
             patch("bellows.lifecycle.record_verdict_request"):
            b._consume_verdicts()

        assert verdict_pending_path.exists(), "Plan must stay verdict-pending (refusal)"
        rejected_verdict = verdicts_resolved / f"processed-rejected-{verdict_fname}"
        assert rejected_verdict.exists(), "Verdict must be renamed to processed-rejected-"
        mock_ledger.assert_called_once()
        assert mock_ledger.call_args[0][3] == "continue-rejected"


def test_legacy_slug_with_clean_request_advances():
    """E4: legacy slug-only plan + clean request file → advances."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        decisions_dir = tmp_path / "proj" / "knowledge" / "decisions"
        decisions_dir.mkdir(parents=True)
        (decisions_dir / "Done").mkdir()

        plan_filename = "diagnostic-legacy-test-2026-08-24.md"
        verdict_pending_path = decisions_dir / f"verdict-pending-{plan_filename}"
        verdict_pending_path.write_text("## Diagnostic\nSingle step.\n")

        verdicts_resolved = tmp_path / "verdicts" / "resolved"
        verdicts_resolved.mkdir(parents=True)
        verdict_fname = "verdict-legacy-test-2026-08-24-step-1.md"
        (verdicts_resolved / verdict_fname).write_text("continue\nApproved.")

        pending_dir = tmp_path / "verdicts" / "pending"
        pending_dir.mkdir(parents=True)
        pending_file = pending_dir / "verdict-request-legacy-test-2026-08-24-step-1.md"
        pending_file.write_text(_make_verdict_request_content(
            str(verdict_pending_path), step_number=1, total_steps=1,
            gate_result_json={"failures": [], "files_changed": []}))

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
             patch("bellows.notifier.push"):
            b._consume_verdicts()

        done_path = decisions_dir / "Done" / plan_filename
        assert done_path.is_file(), "Legacy plan should advance to Done with clean gates"


def test_teardown_in_fallback_routes_to_halted():
    """E4 C-3: worktree_teardown failure → the :2581 guard's halted routing, NOT rejection."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        decisions_dir = tmp_path / "proj" / "knowledge" / "decisions"
        decisions_dir.mkdir(parents=True)
        (decisions_dir / "Done").mkdir()

        plan_filename = "executable-e4-teardown-2026-08-24.md"
        verdict_pending_path = decisions_dir / f"verdict-pending-{plan_filename}"
        verdict_pending_path.write_text("## STEP 1\nDo stuff.\n## STEP 2\nMore.\n")

        verdicts_resolved = tmp_path / "verdicts" / "resolved"
        verdicts_resolved.mkdir(parents=True)
        verdict_fname = "verdict-e4-teardown-2026-08-24-step-1.md"
        (verdicts_resolved / verdict_fname).write_text("continue\nApproved.")

        pending_dir = tmp_path / "verdicts" / "pending"
        pending_dir.mkdir(parents=True)
        pending_file = pending_dir / "verdict-request-e4-teardown-2026-08-24-step-1.md"
        gate_data = {"failures": [{"gate": "worktree_teardown", "evidence": "merge conflict"}], "files_changed": []}
        pending_file.write_text(_make_verdict_request_content(
            str(verdict_pending_path), step_number=1, total_steps=2,
            gate_result_json=gate_data))

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
             patch("bellows.notifier.push"), \
             patch("bellows.lifecycle.record_verdict_outcome"), \
             patch("bellows.lifecycle.mark_plan_state"):
            b._consume_verdicts()

        halted_path = decisions_dir / f"halted-{plan_filename}"
        assert halted_path.exists(), "Teardown failure must route to halted- (not rejection)"
        assert not verdict_pending_path.exists(), "Plan must be moved out of verdict-pending-"
        mock_ledger.assert_called_once()
        assert mock_ledger.call_args[0][3] == "continue-blocked-worktree-teardown"


def test_stop_verdict_byte_identical():
    """E4: stop verdicts are byte-identical — NOT routed through the re-check."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        decisions_dir = tmp_path / "proj" / "knowledge" / "decisions"
        decisions_dir.mkdir(parents=True)
        (decisions_dir / "Done").mkdir()

        plan_filename = "executable-e4-stop-2026-08-24.md"
        verdict_pending_path = decisions_dir / f"verdict-pending-{plan_filename}"
        verdict_pending_path.write_text("## STEP 1\nDo stuff.\n## STEP 2\nMore.\n")

        verdicts_resolved = tmp_path / "verdicts" / "resolved"
        verdicts_resolved.mkdir(parents=True)
        verdict_fname = "verdict-e4-stop-2026-08-24-step-1.md"
        (verdicts_resolved / verdict_fname).write_text("stop\nBlocked.")

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
                 "found": True, "verdict": "stop", "reason": "blocked"
             }), \
             patch("bellows.verdict.log_to_ledger") as mock_ledger, \
             patch("bellows.notifier.push"), \
             patch("bellows.lifecycle.record_verdict_outcome") as mock_outcome, \
             patch("bellows.lifecycle.mark_plan_state"):
            b._consume_verdicts()

        halted_path = decisions_dir / f"halted-{plan_filename}"
        assert halted_path.exists(), "Stop verdict must halt plan"
        mock_outcome.assert_called_once()
        assert mock_outcome.call_args[0][2] == "stop"


def test_recheck_exception_skips_without_consuming():
    """E4 C-5: exception in re-check → WARN, skip verdict file, retried next poll."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        decisions_dir = tmp_path / "proj" / "knowledge" / "decisions"
        decisions_dir.mkdir(parents=True)
        (decisions_dir / "Done").mkdir()

        plan_filename = "executable-e4-exc-2026-08-24.md"
        verdict_pending_path = decisions_dir / f"verdict-pending-{plan_filename}"
        verdict_pending_path.write_text("## STEP 1\nDo stuff.\n## STEP 2\nMore.\n")

        verdicts_resolved = tmp_path / "verdicts" / "resolved"
        verdicts_resolved.mkdir(parents=True)
        verdict_fname = "verdict-e4-exc-2026-08-24-step-1.md"
        (verdicts_resolved / verdict_fname).write_text("continue\nApproved.")

        pending_dir = tmp_path / "verdicts" / "pending"
        pending_dir.mkdir(parents=True)
        pending_file = pending_dir / "verdict-request-e4-exc-2026-08-24-step-1.md"
        pending_file.write_text(_make_verdict_request_content(
            str(verdict_pending_path), step_number=1, total_steps=2,
            gate_result_json={"failures": [], "files_changed": []}))

        config = {
            "watched_projects": [str(decisions_dir)],
            "default_model": "claude-sonnet-4-6",
            "pushover": {"app_key": "", "user_key": ""},
            "callback_port": 5999,
        }
        b = bellows.Bellows(config)

        def _boom(*a, **kw):
            raise RuntimeError("simulated explosion")

        with patch("bellows.BELLOWS_ROOT", tmp_path), \
             patch("bellows.verdict.check_verdict", return_value={
                 "found": True, "verdict": "continue", "reason": "approved"
             }), \
             patch("bellows.verdict.log_to_ledger"), \
             patch("bellows.notifier.push"), \
             patch("bellows.lifecycle.record_verdict_outcome", side_effect=_boom):
            b._consume_verdicts()

        assert verdict_pending_path.exists(), "Plan must stay verdict-pending"
        assert (verdicts_resolved / verdict_fname).exists(), "Verdict file must stay in resolved/"
        assert pending_file.exists(), "Request file must stay"


def test_stale_gate_events_with_clean_retry_advances():
    """E4 C-9: first-pass fail rows in gate_events + clean retry request → advances."""
    import sqlite3
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        decisions_dir = tmp_path / "proj" / "knowledge" / "decisions"
        decisions_dir.mkdir(parents=True)
        (decisions_dir / "Done").mkdir()

        plan_filename = "executable-502.md"
        verdict_pending_path = decisions_dir / f"verdict-pending-{plan_filename}"
        verdict_pending_path.write_text("## STEP 1\nDo stuff.\n## STEP 2\nMore.\n")

        verdicts_resolved = tmp_path / "verdicts" / "resolved"
        verdicts_resolved.mkdir(parents=True)
        verdict_fname = "verdict-executable-502-step-1.md"
        (verdicts_resolved / verdict_fname).write_text("continue\nApproved.")

        pending_dir = tmp_path / "verdicts" / "pending"
        pending_dir.mkdir(parents=True)
        pending_file = pending_dir / "verdict-request-502-step-1.md"
        pending_file.write_text(_make_verdict_request_content(
            str(verdict_pending_path), step_number=1, total_steps=2,
            gate_result_json={"failures": [], "files_changed": []}))

        # Stale fail rows in gate_events (from a prior failed attempt)
        import lifecycle
        db_path = str(tmp_path / "lifecycle.db")
        lifecycle.init_lifecycle_db(db_path)
        conn = sqlite3.connect(db_path)
        conn.execute("INSERT INTO id_sequence (id, next_id) VALUES (1, 503) ON CONFLICT DO UPDATE SET next_id=503")
        conn.execute("INSERT INTO plans (id, type, target_project, lifecycle_state, created_at) VALUES (502, 'executable', 'proj', 'awaiting_verdict', '2026-08-24')")
        conn.execute("INSERT INTO steps (plan_id, step_number, status) VALUES (502, 1, 'awaiting_verdict')")
        step_id = conn.execute("SELECT id FROM steps WHERE plan_id=502 AND step_number=1").fetchone()[0]
        conn.execute("INSERT INTO gate_events (step_id, gate_name, result, overridden, override_ref) VALUES (?, 'no_errors', 'fail', 0, NULL)", (step_id,))
        conn.commit()
        conn.close()

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
             patch("bellows.lifecycle.LIFECYCLE_DB_PATH", db_path), \
             patch("bellows.lifecycle.record_verdict_outcome"), \
             patch.object(b, "handle_new_plan") as mock_handle:
            b._consume_verdicts()

        mock_handle.assert_called_once()
        assert mock_handle.call_args[1]["resume_step"] == 2


def test_precondition_retry_routes_before_c1():
    """E4 C-12: precondition-failure retry's request routes to retry arm before C-1."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        decisions_dir = tmp_path / "proj" / "knowledge" / "decisions"
        decisions_dir.mkdir(parents=True)
        (decisions_dir / "Done").mkdir()

        plan_filename = "executable-e4-precond-2026-08-24.md"
        verdict_pending_path = decisions_dir / f"verdict-pending-{plan_filename}"
        verdict_pending_path.write_text("## STEP 1\nDo stuff.\n## STEP 2\nMore.\n")

        verdicts_resolved = tmp_path / "verdicts" / "resolved"
        verdicts_resolved.mkdir(parents=True)
        verdict_fname = "verdict-e4-precond-2026-08-24-step-1.md"
        (verdicts_resolved / verdict_fname).write_text("continue\nApproved.")

        pending_dir = tmp_path / "verdicts" / "pending"
        pending_dir.mkdir(parents=True)
        pending_file = pending_dir / "verdict-request-e4-precond-2026-08-24-step-1.md"
        # Precondition failure with no gate JSON — C-12 skips C-1
        pending_file.write_text(_make_verdict_request_content(
            str(verdict_pending_path), step_number=1, total_steps=2,
            precondition_failure=True))

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
        assert mock_handle.call_args[1]["resume_step"] == 1, \
            "Precondition failure must retry same step"


def test_override_gate_tool_writes_all_matching_rows():
    """E4: --override-gate writes ALL matching unoverridden fail rows via --db-path."""
    import sqlite3
    import lifecycle
    with tempfile.TemporaryDirectory() as tmp:
        db_path = os.path.join(tmp, "lifecycle.db")
        lifecycle.init_lifecycle_db(db_path)
        conn = sqlite3.connect(db_path)
        conn.execute("INSERT INTO id_sequence (id, next_id) VALUES (1, 100) ON CONFLICT DO UPDATE SET next_id=100")
        conn.execute("INSERT INTO plans (id, type, target_project, lifecycle_state, created_at) VALUES (99, 'executable', 'proj', 'awaiting_verdict', '2026-08-24')")
        conn.execute("INSERT INTO steps (plan_id, step_number, status) VALUES (99, 1, 'awaiting_verdict')")
        step_id = conn.execute("SELECT id FROM steps WHERE plan_id=99 AND step_number=1").fetchone()[0]
        conn.execute("INSERT INTO gate_events (step_id, gate_name, result, overridden, override_ref) VALUES (?, 'scope_check', 'fail', 0, NULL)", (step_id,))
        conn.execute("INSERT INTO gate_events (step_id, gate_name, result, overridden, override_ref) VALUES (?, 'scope_check', 'fail', 0, NULL)", (step_id,))
        conn.commit()
        conn.close()

        sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tools"))
        from clear_plan import override_gate
        result = override_gate("executable-99", "1", "scope_check", "CEO approved", db_path=db_path)
        assert result is True

        conn = sqlite3.connect(db_path)
        rows = conn.execute("SELECT overridden, override_ref FROM gate_events WHERE gate_name='scope_check' AND result='fail'").fetchall()
        conn.close()
        assert all(r[0] == 1 for r in rows), "All matching rows must be overridden"
        assert all(r[1] == "CEO approved" for r in rows), "All matching rows must have override_ref"


def test_override_gate_tool_refuses_no_match():
    """E4: --override-gate refuses when no matching unoverridden fail rows exist."""
    import sqlite3
    import lifecycle
    with tempfile.TemporaryDirectory() as tmp:
        db_path = os.path.join(tmp, "lifecycle.db")
        lifecycle.init_lifecycle_db(db_path)
        conn = sqlite3.connect(db_path)
        conn.execute("INSERT INTO id_sequence (id, next_id) VALUES (1, 100) ON CONFLICT DO UPDATE SET next_id=100")
        conn.execute("INSERT INTO plans (id, type, target_project, lifecycle_state, created_at) VALUES (99, 'executable', 'proj', 'awaiting_verdict', '2026-08-24')")
        conn.execute("INSERT INTO steps (plan_id, step_number, status) VALUES (99, 1, 'awaiting_verdict')")
        conn.commit()
        conn.close()

        sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tools"))
        from clear_plan import override_gate
        result = override_gate("99", "1", "nonexistent_gate", "ref", db_path=db_path)
        assert result is False



