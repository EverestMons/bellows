"""Tests for gate→verdict transaction mechanization.

Asserts that the Bellows lifecycle's node-to-node transitions are decided
mechanically — from records — not by prose an agent interprets.
"""

import sqlite3

import lifecycle
import gates
import bellows


STANDARD_GATES = [
    "receipt_status",
    "no_errors",
    "no_permission_denials",
    "deposit_exists",
    "scope_check",
    "rule_20_self_check",
    "rule_22_verification",
]


def _make_db(tmp_path):
    db_path = str(tmp_path / "lifecycle.db")
    lifecycle.init_lifecycle_db(db_path)
    return db_path


def _mint_plan(db_path):
    return lifecycle.mint_and_claim(
        plan_type="executable",
        target_project="bellows",
        title="test plan",
        dispatch_mode="bellows",
        tier="T0",
        total_steps=2,
        deposit_placeholder_name="test-placeholder",
        db_path=db_path,
    )


class TestGateEventsAreMechanicalImage:
    """Invariant 1: gate_events rows are a faithful mirror of gate_result."""

    def test_single_failure_produces_exact_rows(self, tmp_path):
        db_path = _make_db(tmp_path)
        plan_id = _mint_plan(db_path)
        step_id = lifecycle.record_step_start(plan_id, 1, db_path=db_path)

        gate_result = {
            "failures": [{"gate": "scope_check", "evidence": "out-of-scope files: foo.py"}],
            "passed": False,
        }

        lifecycle.record_gate_events(step_id, gate_result, db_path=db_path)

        conn = sqlite3.connect(db_path)
        rows = conn.execute(
            "SELECT gate_name, result FROM gate_events WHERE step_id = ? ORDER BY gate_name",
            (step_id,),
        ).fetchall()
        conn.close()

        assert len(rows) == 7

        row_dict = {name: result for name, result in rows}
        assert row_dict["scope_check"] == "fail"
        for gate in STANDARD_GATES:
            if gate != "scope_check":
                assert row_dict[gate] == "pass", f"{gate} should be pass"

    def test_all_failures_produces_zero_pass_rows(self, tmp_path):
        db_path = _make_db(tmp_path)
        plan_id = _mint_plan(db_path)
        step_id = lifecycle.record_step_start(plan_id, 1, db_path=db_path)

        gate_result = {
            "failures": [
                {"gate": g, "evidence": f"failing {g}"} for g in STANDARD_GATES
            ],
            "passed": False,
        }

        lifecycle.record_gate_events(step_id, gate_result, db_path=db_path)

        conn = sqlite3.connect(db_path)
        pass_count = conn.execute(
            "SELECT COUNT(*) FROM gate_events WHERE step_id = ? AND result = 'pass'",
            (step_id,),
        ).fetchone()[0]
        total = conn.execute(
            "SELECT COUNT(*) FROM gate_events WHERE step_id = ?",
            (step_id,),
        ).fetchone()[0]
        conn.close()

        assert pass_count == 0
        assert total == 7


class TestGatesCheckIsDeterministic:
    """Invariant 2: gates.check is a pure, deterministic function —
    passed == (len(failures) == 0)."""

    def test_identical_inputs_produce_identical_outputs(self, tmp_path):
        parsed = {
            "receipt_status": "Complete",
            "ceo_flags": [],
            "is_error": False,
            "permission_denials": [],
            "result_text": "",
            "verdict_requested": {"requested": False, "reason": None},
        }
        plan_text = "## STEP 1 — DEV\n\nSome task.\n"

        r1 = gates.check(parsed, plan_text, 1, str(tmp_path))
        r2 = gates.check(parsed, plan_text, 1, str(tmp_path))

        assert r1["failures"] == r2["failures"]
        assert r1["passed"] == r2["passed"]
        assert r1["passed"] is (len(r1["failures"]) == 0)

    def test_failing_receipt_status(self, tmp_path):
        parsed = {
            "receipt_status": "Incomplete",
            "ceo_flags": [],
            "is_error": False,
            "permission_denials": [],
            "result_text": "",
            "verdict_requested": {"requested": False, "reason": None},
        }
        plan_text = "## STEP 1 — DEV\n\nSome task.\n"

        result = gates.check(parsed, plan_text, 1, str(tmp_path))

        assert result["passed"] is False
        failure_gates = [f["gate"] for f in result["failures"]]
        assert "receipt_status" in failure_gates


class TestDecidedByDiscrimination:
    """Invariant 3: decided_by distinguishes mechanical auto-continues
    (gate_auto) from verdict-file-parsed continues (verdict_file).
    Gap CLOSED by plan 313."""

    def test_gate_auto_and_verdict_file_are_distinct(self, tmp_path):
        db_path = _make_db(tmp_path)
        plan_id = _mint_plan(db_path)

        lifecycle.record_verdict_request(plan_id, 1, pause_reason_code="auto_close", db_path=db_path)
        lifecycle.record_verdict_outcome(
            plan_id, 1, "continue", decided_by="gate_auto", db_path=db_path
        )

        lifecycle.record_verdict_request(plan_id, 2, db_path=db_path)
        lifecycle.record_verdict_outcome(
            plan_id, 2, "continue", decided_by="verdict_file", db_path=db_path
        )

        conn = sqlite3.connect(db_path)
        rows = conn.execute(
            "SELECT step_number, decided_by FROM verdicts "
            "WHERE plan_id = ? ORDER BY step_number",
            (plan_id,),
        ).fetchall()
        conn.close()

        assert len(rows) == 2
        assert rows[0] == (1, "gate_auto")
        assert rows[1] == (2, "verdict_file")
        assert rows[0][1] != rows[1][1]


class TestAutoCloseProvenance:
    """Invariant 4: the auto-close branch writes a verdicts row with
    decided_by='gate_auto' and outcome='continue', so the mechanical
    transition is queryable in the record.

    Tested at the lifecycle layer (record_verdict_request +
    record_verdict_outcome) rather than via run_plan — the auto-close
    branch in run_plan has extensive mock requirements (worktree, gates,
    notifier, etc.) that are already covered by test_bellows.py's
    test_diagnostic_auto_close_moves_to_done; this test isolates the
    provenance guarantee without duplicating that harness."""

    def test_auto_close_produces_gate_auto_row(self, tmp_path):
        db_path = _make_db(tmp_path)
        plan_id = _mint_plan(db_path)

        lifecycle.record_verdict_request(plan_id, 1, pause_reason_code="auto_close", db_path=db_path)
        lifecycle.record_verdict_outcome(
            plan_id, 1, "continue", decided_by="gate_auto", db_path=db_path
        )

        conn = sqlite3.connect(db_path)
        row = conn.execute(
            "SELECT outcome, decided_by, pause_reason_code FROM verdicts "
            "WHERE plan_id = ? AND step_number = 1",
            (plan_id,),
        ).fetchone()
        conn.close()

        assert row is not None, "auto-close should produce a verdicts row"
        assert row[0] == "continue"
        assert row[1] == "gate_auto"
        assert row[2] == "auto_close"


class TestHeaderSaysPauseModes:
    """Invariant 5: header_says_pause mode branches return correct values
    for all modes including the new qa_and_terminal mode."""

    def test_qa_and_terminal_non_terminal_non_qa_returns_false(self):
        header = {"pause_for_verdict": "qa_and_terminal"}
        assert bellows.header_says_pause(header, 1, 3, False) is False

    def test_qa_and_terminal_qa_step_returns_true(self):
        header = {"pause_for_verdict": "qa_and_terminal"}
        assert bellows.header_says_pause(header, 1, 3, True) is True

    def test_qa_and_terminal_terminal_step_returns_true(self):
        # At the terminal step this mode returns True — the auto-close branch is unreachable
        header = {"pause_for_verdict": "qa_and_terminal"}
        assert bellows.header_says_pause(header, 3, 3, False) is True

    def test_qa_and_terminal_total_steps_zero_returns_true(self):
        header = {"pause_for_verdict": "qa_and_terminal"}
        assert bellows.header_says_pause(header, 1, 0, False) is True

    def test_qa_and_terminal_single_step_plan_returns_true(self):
        header = {"pause_for_verdict": "qa_and_terminal"}
        assert bellows.header_says_pause(header, 1, 1, False) is True

    def test_always_mode_unchanged(self):
        header = {"pause_for_verdict": "always"}
        assert bellows.header_says_pause(header, 1, 3, False) is True
        assert bellows.header_says_pause(header, 2, 3, False) is True
        assert bellows.header_says_pause(header, 3, 3, False) is True

    def test_after_step_1_mode_unchanged(self):
        header = {"pause_for_verdict": "after_step_1"}
        assert bellows.header_says_pause(header, 1, 3, False) is True
        assert bellows.header_says_pause(header, 2, 3, False) is False

    def test_after_qa_step_mode_unchanged(self):
        header = {"pause_for_verdict": "after_qa_step"}
        assert bellows.header_says_pause(header, 1, 3, True) is True
        assert bellows.header_says_pause(header, 1, 3, False) is False

    def test_unrecognized_value_returns_false(self):
        header = {"pause_for_verdict": "bogus_value"}
        assert bellows.header_says_pause(header, 1, 3, False) is False


class TestCleanGateAutoProvenance:
    """Invariant 6: the clean_gate_auto request+outcome pair produces a
    queryable row with the correct fields, and the row does NOT match the
    dashboard's awaiting-verdict filter (outcome IS NULL)."""

    def test_clean_gate_auto_produces_queryable_row(self, tmp_path):
        db_path = _make_db(tmp_path)
        plan_id = _mint_plan(db_path)

        lifecycle.record_verdict_request(plan_id, 1, pause_reason_code="clean_gate_auto", db_path=db_path)
        lifecycle.record_verdict_outcome(plan_id, 1, "continue", decided_by="gate_auto", db_path=db_path)

        conn = sqlite3.connect(db_path)
        row = conn.execute(
            "SELECT outcome, decided_by, pause_reason_code FROM verdicts "
            "WHERE plan_id = ? AND step_number = 1",
            (plan_id,),
        ).fetchone()
        conn.close()

        assert row is not None, "clean_gate_auto should produce a verdicts row"
        assert row[0] == "continue"
        assert row[1] == "gate_auto"
        assert row[2] == "clean_gate_auto"

    def test_clean_gate_auto_excluded_from_awaiting_filter(self, tmp_path):
        db_path = _make_db(tmp_path)
        plan_id = _mint_plan(db_path)

        lifecycle.record_verdict_request(plan_id, 1, pause_reason_code="clean_gate_auto", db_path=db_path)
        lifecycle.record_verdict_outcome(plan_id, 1, "continue", decided_by="gate_auto", db_path=db_path)

        conn = sqlite3.connect(db_path)
        awaiting = conn.execute(
            "SELECT * FROM verdicts WHERE plan_id = ? AND outcome IS NULL",
            (plan_id,),
        ).fetchall()
        conn.close()

        assert len(awaiting) == 0, "clean_gate_auto row must not appear in awaiting-verdict filter"

    def test_clean_gate_auto_two_row_case(self, tmp_path):
        """Two pending rows for one plan+step: the outcome call stamps BOTH."""
        db_path = _make_db(tmp_path)
        plan_id = _mint_plan(db_path)

        lifecycle.record_verdict_request(plan_id, 1, pause_reason_code="clean_gate_auto", db_path=db_path)
        lifecycle.record_verdict_request(plan_id, 1, pause_reason_code="clean_gate_auto", db_path=db_path)

        lifecycle.record_verdict_outcome(plan_id, 1, "continue", decided_by="gate_auto", db_path=db_path)

        conn = sqlite3.connect(db_path)
        rows = conn.execute(
            "SELECT outcome, decided_by FROM verdicts WHERE plan_id = ? AND step_number = 1",
            (plan_id,),
        ).fetchall()
        null_rows = conn.execute(
            "SELECT * FROM verdicts WHERE plan_id = ? AND step_number = 1 AND outcome IS NULL",
            (plan_id,),
        ).fetchall()
        conn.close()

        assert len(rows) == 2, "should have two verdicts rows"
        assert all(r[0] == "continue" for r in rows), "both rows should be stamped with outcome=continue"
        assert all(r[1] == "gate_auto" for r in rows), "both rows should have decided_by=gate_auto"
        assert len(null_rows) == 0, "no rows should remain with NULL outcome"


import os
import tempfile
import shutil
from unittest.mock import MagicMock, patch


def _make_fake_parsed():
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


def _advance_gates():
    return {
        "passed": True,
        "failures": [],
        "is_qa_step": False,
        "files_changed": [],
        "plan_header": {"auto_close": "true", "pause_for_verdict": "never", "Total Steps": "2"},
        "verdict_requested": {"requested": False, "body": None},
    }


class TestCleanGateAutoRunPlanIntegration:
    """run_plan integration: the clean_gate_auto row lands on mechanical advance
    and does NOT land on a paused run — placement discrimination."""

    def test_clean_gate_auto_row_lands_on_mechanical_advance(self):
        """Multi-step plan whose non-terminal step advances mechanically:
        a clean_gate_auto row must be written for that step."""
        with tempfile.TemporaryDirectory() as tmp:
            decisions_dir = os.path.join(tmp, "proj", "knowledge", "decisions")
            os.makedirs(decisions_dir)
            plan_filename = "executable-clean-gate-auto-test-2026-08-08.md"
            plan_path = os.path.join(decisions_dir, plan_filename)
            with open(plan_path, "w") as f:
                f.write("## STEP 1\nDo stuff.\n## STEP 2\nDo more stuff.\n")

            config = {
                "default_model": "claude-sonnet-4-6",
                "pushover": {"app_key": "", "user_key": ""},
                "callback_port": 5999,
                "step_timeout_seconds": 600,
            }

            with patch("bellows.runner.run_step", return_value=_make_fake_parsed()), \
                 patch("bellows.gates.check", return_value=_advance_gates()), \
                 patch("bellows.notifier.push"), \
                 patch("bellows.verdict.log_to_ledger"), \
                 patch("bellows._capture_git_diff", return_value=""), \
                 patch("bellows._create_worktree", return_value="/tmp/wt"), \
                 patch("bellows._teardown_worktree"), \
                 patch("bellows.record_run"), \
                 patch("bellows.validators.validate_at_claim", return_value={"rejected": False, "reject_reason": "", "warnings": []}):
                response_server = MagicMock()
                bellows.run_plan(plan_path, config, response_server)

            # Query the lifecycle DB for the clean_gate_auto row at step 1
            import lifecycle as lc
            conn = sqlite3.connect(lc.LIFECYCLE_DB_PATH)
            rows = conn.execute(
                "SELECT pause_reason_code, outcome, decided_by FROM verdicts "
                "WHERE step_number = 1 AND pause_reason_code = 'clean_gate_auto'"
            ).fetchall()
            conn.close()

            assert len(rows) >= 1, "clean_gate_auto row must land for the mechanically advanced step"
            assert rows[0][1] == "continue"
            assert rows[0][2] == "gate_auto"

    def test_no_clean_gate_auto_row_on_paused_run(self):
        """A plan that pauses at step 1 must NOT write a clean_gate_auto row."""
        with tempfile.TemporaryDirectory() as tmp:
            decisions_dir = os.path.join(tmp, "proj", "knowledge", "decisions")
            os.makedirs(decisions_dir)
            plan_filename = "executable-paused-no-auto-2026-08-08.md"
            plan_path = os.path.join(decisions_dir, plan_filename)
            with open(plan_path, "w") as f:
                f.write("## STEP 1\nDo stuff.\n## STEP 2\nDo more stuff.\n")

            config = {
                "default_model": "claude-sonnet-4-6",
                "pushover": {"app_key": "", "user_key": ""},
                "callback_port": 5999,
                "step_timeout_seconds": 600,
            }

            paused_gates = {
                "passed": True,
                "failures": [],
                "is_qa_step": False,
                "files_changed": [],
                "plan_header": {"pause_for_verdict": "always", "Total Steps": "2", "dummy": "x"},
                "verdict_requested": {"requested": False, "body": None},
            }

            original_header_says_pause = bellows.header_says_pause

            def spy_header_says_pause(header, *args, **kwargs):
                return original_header_says_pause(header, *args, **kwargs)

            with patch("bellows.runner.run_step", return_value=_make_fake_parsed()), \
                 patch("bellows.gates.check", return_value=paused_gates), \
                 patch("bellows.notifier.push"), \
                 patch("bellows.notifier.notify_verdict_request"), \
                 patch("bellows.verdict.post_verdict_request"), \
                 patch("bellows._capture_git_diff", return_value=""), \
                 patch("bellows._create_worktree", return_value="/tmp/wt"), \
                 patch("bellows._teardown_worktree"), \
                 patch("bellows.record_run"), \
                 patch("bellows.validators.validate_at_claim", return_value={"rejected": False, "reject_reason": "", "warnings": []}), \
                 patch("bellows.header_says_pause", side_effect=spy_header_says_pause):
                response_server = MagicMock()
                bellows.run_plan(plan_path, config, response_server)

            # Query the lifecycle DB: no clean_gate_auto row should exist
            import lifecycle as lc
            conn = sqlite3.connect(lc.LIFECYCLE_DB_PATH)
            rows = conn.execute(
                "SELECT pause_reason_code FROM verdicts "
                "WHERE pause_reason_code = 'clean_gate_auto'"
            ).fetchall()
            conn.close()

            assert len(rows) == 0, "paused run must NOT write a clean_gate_auto row"
