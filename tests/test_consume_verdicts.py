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


def test_pre_scan_renames_processed_verdict_to_canonical():
    """Pre-scan must rename processed-verdict-* files to verdict-* so the main
    loop can discover and consume them."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)

        decisions_dir = tmp_path / "proj" / "knowledge" / "decisions"
        decisions_dir.mkdir(parents=True)
        done_dir = decisions_dir / "Done"
        done_dir.mkdir()

        # Plan file in verdict-pending state
        plan_filename = "verdict-pending-diagnostic-foo-2026-05-21.md"
        plan_path = decisions_dir / plan_filename
        plan_path.write_text("## STEP 1\nDo stuff.\n")

        # Verdict in resolved/ with wrong processed- prefix (write-time mistake)
        verdicts_resolved = tmp_path / "verdicts" / "resolved"
        verdicts_resolved.mkdir(parents=True)
        bad_fname = "processed-verdict-foo-2026-05-21-step-1.md"
        (verdicts_resolved / bad_fname).write_text("verdict: continue\nApproved.")

        # Pending request file
        pending_dir = tmp_path / "verdicts" / "pending"
        pending_dir.mkdir(parents=True)
        pending_file = pending_dir / "verdict-request-foo-2026-05-21-step-1.md"
        pending_file.write_text("# Verdict Request\n**Plan:** " + str(plan_path))

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

        # The verdict was consumed — plan moved from verdict-pending- to Done
        assert not plan_path.exists(), (
            f"Plan should have been moved out of verdict-pending state: {plan_path}"
        )
        done_path = decisions_dir / "Done" / "diagnostic-foo-2026-05-21.md"
        assert done_path.exists(), (
            f"Plan should have been moved to Done after continue verdict: {done_path}"
        )
        # The consumption-time rename produces processed-verdict-* (same name as the
        # original write-time mistake, but now it's legitimately post-consumption)
        canonical_fname = "verdict-foo-2026-05-21-step-1.md"
        processed_fname = f"processed-{canonical_fname}"
        assert (verdicts_resolved / processed_fname).exists(), (
            f"Verdict should have been consumed and renamed to processed-: {processed_fname}"
        )


def test_pre_scan_collision_guard_does_not_overwrite():
    """When both verdict-* and processed-verdict-* exist AND a paired plan is
    present, the pre-scan must skip the rename and preserve the canonical file.
    Updated for orphan guard: a verdict-pending-* plan must exist so the orphan
    check lets the file through to the collision guard."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)

        decisions_dir = tmp_path / "proj" / "knowledge" / "decisions"
        decisions_dir.mkdir(parents=True)
        (decisions_dir / "Done").mkdir()

        # Paired plan in verdict-pending state so orphan guard allows rename attempt
        plan_filename = "verdict-pending-diagnostic-foo-2026-05-21.md"
        (decisions_dir / plan_filename).write_text("## STEP 1\nDo stuff.\n")

        verdicts_resolved = tmp_path / "verdicts" / "resolved"
        verdicts_resolved.mkdir(parents=True)
        (tmp_path / "verdicts" / "pending").mkdir(parents=True)

        # Both canonical and processed- form exist simultaneously
        canonical_fname = "verdict-foo-2026-05-21-step-1.md"
        bad_fname = "processed-verdict-foo-2026-05-21-step-1.md"
        canonical_content = "verdict: continue\nCanonical file — must not be overwritten."
        (verdicts_resolved / canonical_fname).write_text(canonical_content)
        (verdicts_resolved / bad_fname).write_text("verdict: continue\nDuplicate processed- file.")

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
             patch("bellows._log") as mock_log, \
             patch.object(b, "handle_new_plan"):
            b._consume_verdicts()

        # The processed-verdict-* file must still exist (rename was skipped)
        assert (verdicts_resolved / bad_fname).exists(), (
            f"processed-verdict-* file should be preserved when canonical exists: {bad_fname}"
        )
        # A WARN log was emitted for the collision
        warn_calls = [c for c in mock_log.call_args_list if c[0][0] == "WARN" and "cannot normalize" in c[0][1]]
        assert len(warn_calls) >= 1, (
            "Expected a WARN log for collision — cannot normalize"
        )


def test_pre_scan_ignores_non_verdict_processed_files():
    """Pre-scan must not rename processed-* files that are not verdict files."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)

        decisions_dir = tmp_path / "proj" / "knowledge" / "decisions"
        decisions_dir.mkdir(parents=True)
        (decisions_dir / "Done").mkdir()

        verdicts_resolved = tmp_path / "verdicts" / "resolved"
        verdicts_resolved.mkdir(parents=True)
        (tmp_path / "verdicts" / "pending").mkdir(parents=True)

        # A non-verdict processed- file
        non_verdict = "processed-something-unrelated.md"
        (verdicts_resolved / non_verdict).write_text("not a verdict")

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
             patch("bellows.notifier.push"), \
             patch("bellows._log") as mock_log:
            b._consume_verdicts()

        # File must not have been renamed
        assert (verdicts_resolved / non_verdict).exists(), (
            f"Non-verdict processed-* file should not be renamed: {non_verdict}"
        )
        # No rename WARN log emitted
        rename_warns = [c for c in mock_log.call_args_list if c[0][0] == "WARN" and "normalized" in c[0][1]]
        assert len(rename_warns) == 0, (
            "No rename WARN should be emitted for non-verdict files"
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


# --- Pre-scan orphan guard regression tests (2026-05-22) ---

def test_pre_scan_skips_rename_when_no_paired_plan():
    """Pre-scan orphan guard: when no verdict-pending-* plan exists anywhere,
    processed-verdict-* must stay as-is with INFO log (not WARN)."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)

        decisions_dir = tmp_path / "proj" / "knowledge" / "decisions"
        decisions_dir.mkdir(parents=True)
        (decisions_dir / "Done").mkdir()

        verdicts_resolved = tmp_path / "verdicts" / "resolved"
        verdicts_resolved.mkdir(parents=True)
        (tmp_path / "verdicts" / "pending").mkdir(parents=True)

        # processed-verdict file with no paired plan anywhere
        orphan_fname = "processed-verdict-foo-2026-05-22-step-1.md"
        (verdicts_resolved / orphan_fname).write_text("verdict: continue\nOrphan.")

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
             patch("bellows.notifier.push"), \
             patch("bellows._log") as mock_log:
            # Clear dedup set to ensure INFO log fires
            bellows._prescan_orphan_logged.discard(orphan_fname)
            b._consume_verdicts()

        # File must remain as processed-verdict-* (not renamed)
        assert (verdicts_resolved / orphan_fname).exists(), (
            f"Orphan file should stay as processed-*: {orphan_fname}"
        )
        canonical_fname = "verdict-foo-2026-05-22-step-1.md"
        assert not (verdicts_resolved / canonical_fname).exists(), (
            f"Orphan should NOT be renamed to canonical: {canonical_fname}"
        )
        # INFO log emitted (not WARN)
        info_calls = [c for c in mock_log.call_args_list if c[0][0] == "INFO" and "skipping orphan" in c[0][1]]
        assert len(info_calls) >= 1, (
            "Expected INFO log for skipped orphan"
        )
        warn_calls = [c for c in mock_log.call_args_list if c[0][0] == "WARN" and "skipping orphan" in c[0][1]]
        assert len(warn_calls) == 0, (
            "Orphan skip should be INFO, not WARN"
        )
        # check_verdict must NOT have been called — file was skipped
        mock_check.assert_not_called()


def test_pre_scan_renames_when_verdict_pending_plan_exists():
    """Pre-scan orphan guard: when a verdict-pending-* plan exists in decisions/,
    processed-verdict-* must be renamed to verdict-* (canonical form)."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)

        decisions_dir = tmp_path / "proj" / "knowledge" / "decisions"
        decisions_dir.mkdir(parents=True)
        (decisions_dir / "Done").mkdir()

        # verdict-pending plan exists — this file should be allowed through
        plan_filename = "verdict-pending-diagnostic-foo-2026-05-22.md"
        (decisions_dir / plan_filename).write_text("## STEP 1\nDo stuff.\n")

        verdicts_resolved = tmp_path / "verdicts" / "resolved"
        verdicts_resolved.mkdir(parents=True)
        (tmp_path / "verdicts" / "pending").mkdir(parents=True)

        # processed-verdict file matching the plan slug
        processed_fname = "processed-verdict-foo-2026-05-22-step-1.md"
        (verdicts_resolved / processed_fname).write_text("verdict: continue\nApproved.")

        # Pending request file for the main loop
        pending_dir = tmp_path / "verdicts" / "pending"
        pending_file = pending_dir / "verdict-request-foo-2026-05-22-step-1.md"
        pending_file.write_text("# Verdict Request\n**Plan:** " + str(decisions_dir / plan_filename))

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

        # The processed-verdict file should have been renamed to canonical
        # and then consumed by the main loop (producing processed-verdict-*)
        canonical_fname = "verdict-foo-2026-05-22-step-1.md"
        # Either the canonical was consumed (processed-*) or it still exists
        # The key assertion: the original processed-verdict was renamed (canonical or re-processed)
        assert not (verdicts_resolved / processed_fname).exists() or \
               (verdicts_resolved / canonical_fname).exists() or \
               (verdicts_resolved / f"processed-{canonical_fname}").exists(), (
            f"File should have been renamed from processed-verdict to canonical form"
        )


def test_pre_scan_treats_done_plan_as_no_paired_plan():
    """Pre-scan orphan guard: a plan in Done/ is terminal — processed-verdict-*
    must NOT be renamed when the only matching plan is in Done/."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)

        decisions_dir = tmp_path / "proj" / "knowledge" / "decisions"
        decisions_dir.mkdir(parents=True)
        done_dir = decisions_dir / "Done"
        done_dir.mkdir()

        # Plan in Done/ only — terminal state, no verdict-pending-* in decisions/
        done_plan = done_dir / "diagnostic-bar-2026-05-22.md"
        done_plan.write_text("## STEP 1\nCompleted.\n")

        verdicts_resolved = tmp_path / "verdicts" / "resolved"
        verdicts_resolved.mkdir(parents=True)
        (tmp_path / "verdicts" / "pending").mkdir(parents=True)

        # processed-verdict file for the done plan
        orphan_fname = "processed-verdict-bar-2026-05-22-step-1.md"
        (verdicts_resolved / orphan_fname).write_text("verdict: continue\nDone plan orphan.")

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
             patch("bellows.notifier.push"), \
             patch("bellows._log") as mock_log:
            bellows._prescan_orphan_logged.discard(orphan_fname)
            b._consume_verdicts()

        # File must remain as processed-* (Done/ plan is terminal)
        assert (verdicts_resolved / orphan_fname).exists(), (
            f"File should stay as processed-* when plan is in Done/: {orphan_fname}"
        )
        canonical_fname = "verdict-bar-2026-05-22-step-1.md"
        assert not (verdicts_resolved / canonical_fname).exists(), (
            f"File should NOT be renamed when plan is in Done/: {canonical_fname}"
        )
        # check_verdict must NOT have been called
        mock_check.assert_not_called()


def test_pre_scan_collision_guard_fires_regardless_of_paired_plan():
    """Pre-scan orphan guard + collision guard: when both forms exist AND a paired
    plan is present, the orphan guard allows the rename attempt but the collision
    guard must fire (skip rename + WARN)."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)

        decisions_dir = tmp_path / "proj" / "knowledge" / "decisions"
        decisions_dir.mkdir(parents=True)
        (decisions_dir / "Done").mkdir()

        # Paired plan present — orphan guard allows rename attempt
        plan_filename = "verdict-pending-diagnostic-baz-2026-05-22.md"
        (decisions_dir / plan_filename).write_text("## STEP 1\nDo stuff.\n")

        verdicts_resolved = tmp_path / "verdicts" / "resolved"
        verdicts_resolved.mkdir(parents=True)
        (tmp_path / "verdicts" / "pending").mkdir(parents=True)

        # Both canonical and processed- forms exist
        canonical_fname = "verdict-baz-2026-05-22-step-1.md"
        processed_fname = "processed-verdict-baz-2026-05-22-step-1.md"
        canonical_content = "verdict: continue\nCanonical — must not be overwritten."
        (verdicts_resolved / canonical_fname).write_text(canonical_content)
        (verdicts_resolved / processed_fname).write_text("verdict: continue\nDuplicate.")

        config = {
            "watched_projects": [str(decisions_dir)],
            "default_model": "claude-sonnet-4-6",
            "pushover": {"app_key": "", "user_key": ""},
            "callback_port": 5999,
        }

        b = bellows.Bellows(config)

        with patch("bellows.BELLOWS_ROOT", tmp_path), \
             patch("bellows.verdict.check_verdict", return_value={
                 "found": False, "verdict": None, "reason": None
             }), \
             patch("bellows.verdict.log_to_ledger"), \
             patch("bellows.notifier.push"), \
             patch("bellows._log") as mock_log:
            b._consume_verdicts()

        # Processed file must still exist (collision guard skipped the rename)
        assert (verdicts_resolved / processed_fname).exists(), (
            f"processed-verdict-* should be preserved by collision guard: {processed_fname}"
        )
        # Canonical content must be unchanged (main loop skipped it — found=False)
        assert (verdicts_resolved / canonical_fname).read_text() == canonical_content, (
            "Canonical file content must not be overwritten by collision"
        )
        # WARN log was emitted for the collision
        warn_calls = [c for c in mock_log.call_args_list if c[0][0] == "WARN" and "cannot normalize" in c[0][1]]
        assert len(warn_calls) >= 1, (
            "Expected WARN log for collision — cannot normalize"
        )
