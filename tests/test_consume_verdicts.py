"""Regression tests for cleanup slug normalization in _consume_verdicts and startup sweep."""
import os
import re
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import bellows


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
        pending_file.write_text("# Verdict Request\n**Plan:** " + str(verdict_pending_path))

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
        pending_file.write_text("# Verdict Request\n**Plan:** " + str(verdict_pending_path))

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
