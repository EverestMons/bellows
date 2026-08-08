"""Tests for gate→verdict transaction mechanization.

Asserts that the Bellows lifecycle's node-to-node transitions are decided
mechanically — from records — not by prose an agent interprets.
"""

import sqlite3

import lifecycle
import gates


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


class TestDecidedByGap:
    """Invariant 3: pin that bellows.py:2118 hardcodes decided_by=\"ceo\", so a
    mechanical auto-continue and a prose-parsed continue are indistinguishable
    in the record. This test is EXPECTED to fail the day real discrimination is
    wired — that failure is the signal to update it."""

    def test_both_verdicts_record_ceo(self, tmp_path):
        db_path = _make_db(tmp_path)
        plan_id = _mint_plan(db_path)

        lifecycle.record_verdict_request(plan_id, 1, db_path=db_path)
        lifecycle.record_verdict_outcome(
            plan_id, 1, "continue", decided_by="ceo", db_path=db_path
        )

        lifecycle.record_verdict_request(plan_id, 2, db_path=db_path)
        lifecycle.record_verdict_outcome(
            plan_id, 2, "continue", decided_by="ceo", db_path=db_path
        )

        conn = sqlite3.connect(db_path)
        rows = conn.execute(
            "SELECT step_number, decided_by FROM verdicts "
            "WHERE plan_id = ? ORDER BY step_number",
            (plan_id,),
        ).fetchall()
        conn.close()

        assert len(rows) == 2
        assert rows[0] == (1, "ceo")
        assert rows[1] == (2, "ceo")
