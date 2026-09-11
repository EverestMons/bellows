import os
import sqlite3
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import gates
import lifecycle
import verdict


def _clean_parsed():
    return {
        "receipt_status": "Complete",
        "ceo_flags": [],
        "is_error": False,
        "permission_denials": [],
        "result_text": "All done.",
        "cost_usd": 0.05,
        "verdict_requested": {"requested": False, "reason": None},
    }


PLAN_TWO_STEP = """# bellows — scope-step test fixture

**Date:** 2026-09-11 | **Project:** bellows | **qa_steps:** none | **Execution:** Step 1 → Step 2

## STEP 1 — DEV

> Build the arm.
>
> **Scope:**
> - `gates.py`
> - `verdict.py`

## STEP 2 — DEV

> Verify the arm.
>
> **Scope:**
> - `knowledge/qa/evidence/r.md`
"""

# t12 fixture: STEP 2 has no Scope and no Deposits block
PLAN_STEP2_NO_SCOPE = """# bellows — scope-step t12 fixture

**Date:** 2026-09-11 | **Project:** bellows | **qa_steps:** none | **Execution:** Step 1 → Step 2

## STEP 1 — DEV

> Build the arm.
>
> **Scope:**
> - `gates.py`

## STEP 2 — DEV

> Verify the arm.
"""

# t6 fixture: legacy plan text from test_gates.py (no Scope block)
PLAN_TEXT_LEGACY = """# bellows — executable: fixture

**Date:** 2026-09-06 | **Project:** bellows | **qa_steps:** 2 | **Execution:** Step 1

## STEP 1 — DEV (Developer)

> Build gates.py and verdict.py in the bellows root directory.

## STEP 2 — QA (QA Engineer)

> Run all tests and verify deliverables.
"""


class TestScopeStepArm:
    """t1–t6: gate-level tests for the scope_step WARN arm in gates.check()."""

    def test_t1_step2_own_scope_no_warn(self):
        """t1: step 2 changing its own declared file → passed True, warnings empty."""
        result = gates.check(
            _clean_parsed(), PLAN_TWO_STEP, 2, "/tmp",
            files_changed=["knowledge/qa/evidence/r.md"],
        )
        assert result["passed"] is True
        assert result["warnings"] == []

    def test_t2_step2_earlier_step_file_warns(self):
        """t2: step 2 changing a file declared only in step 1 → WARN, passed still True."""
        result = gates.check(
            _clean_parsed(), PLAN_TWO_STEP, 2, "/tmp",
            files_changed=["gates.py"],
        )
        assert result["passed"] is True
        scope_fails = [f for f in result["failures"] if f["gate"] == "scope_check"]
        assert scope_fails == []
        assert result["warnings"] == [{"gate": "scope_step", "evidence": "gates.py"}]

    def test_t3_step2_undeclared_file_fails_not_warned(self):
        """t3: step 2 changing a completely undeclared file → scope_check FAIL, no warn."""
        result = gates.check(
            _clean_parsed(), PLAN_TWO_STEP, 2, "/tmp",
            files_changed=["totally_unexpected.py"],
        )
        assert result["passed"] is False
        scope_fails = [f for f in result["failures"] if f["gate"] == "scope_check"]
        assert len(scope_fails) == 1
        assert result["warnings"] == []

    def test_t4_step1_no_warn(self):
        """t4: step 1 changing its own declared file → warnings empty (own == union)."""
        result = gates.check(
            _clean_parsed(), PLAN_TWO_STEP, 1, "/tmp",
            files_changed=["gates.py"],
        )
        assert result["passed"] is True
        assert result["warnings"] == []

    def test_t5_allowlisted_file_neither(self):
        """t5: step 2 changing .gitkeep → neither fail nor warn."""
        result = gates.check(
            _clean_parsed(), PLAN_TWO_STEP, 2, "/tmp",
            files_changed=[".gitkeep"],
        )
        assert result["passed"] is True
        assert result["warnings"] == []

    def test_t6_legacy_plan_no_warn(self):
        """t6: legacy plan (no Scope block) at step 2 → warnings empty (undeclared plan)."""
        result = gates.check(
            _clean_parsed(), PLAN_TEXT_LEGACY, 2, "/tmp",
            files_changed=["gates.py"],
        )
        assert result["warnings"] == []


class TestScopeStepVerdict:
    """t7–t8: verdict table row for scope_step."""

    def test_t7_warn_row_when_warnings_present(self):
        """t7: scope_step warning → WARN row with file, scope_check still PASS."""
        gate_result = {
            "failures": [],
            "passed": True,
            "is_qa_step": False,
            "files_changed": [],
            "warnings": [{"gate": "scope_step", "evidence": "gates.py"}],
        }
        table = verdict._build_verification_results_table(gate_result, {}, 2, 2)
        assert "| scope_step | WARN | " in table
        assert "gates.py" in table
        assert "| scope_check | PASS |" in table

    def test_t8_pass_row_when_no_warnings(self):
        """t8: no scope_step warnings → PASS row."""
        gate_result = {
            "failures": [],
            "passed": True,
            "is_qa_step": False,
            "files_changed": [],
            "warnings": [],
        }
        table = verdict._build_verification_results_table(gate_result, {}, 2, 2)
        assert "| scope_step | PASS |" in table
        assert "Every changed file is in this step's own Scope or Deposits" in table


class TestScopeStepLedger:
    """t9–t11: lifecycle.record_gate_events rows for scope_step."""

    def test_t9_scope_step_row_with_warning(self):
        """t9: warning present → scope_step row with reason_code."""
        pid = lifecycle.mint_and_claim("executable", "/proj", "T", "bellows", "small", 1, "d.md")
        step_id = lifecycle.record_step_start(pid, 1)
        gate_result = {
            "failures": [],
            "passed": True,
            "warnings": [{"gate": "scope_step", "evidence": "gates.py"}],
        }
        lifecycle.record_gate_events(step_id, gate_result)
        conn = sqlite3.connect(lifecycle.LIFECYCLE_DB_PATH)
        row = conn.execute(
            "SELECT result, reason_code FROM gate_events WHERE step_id = ? AND gate_name = 'scope_step'",
            (step_id,),
        ).fetchone()
        conn.close()
        assert row == ("pass", "earlier-step-only: gates.py")

    def test_t10_scope_step_row_without_warning(self):
        """t10: no warnings → scope_step row with NULL reason_code."""
        pid = lifecycle.mint_and_claim("executable", "/proj", "T", "bellows", "small", 1, "d.md")
        step_id = lifecycle.record_step_start(pid, 1)
        gate_result = {
            "failures": [],
            "passed": True,
            "warnings": [],
        }
        lifecycle.record_gate_events(step_id, gate_result)
        conn = sqlite3.connect(lifecycle.LIFECYCLE_DB_PATH)
        row = conn.execute(
            "SELECT result, reason_code FROM gate_events WHERE step_id = ? AND gate_name = 'scope_step'",
            (step_id,),
        ).fetchone()
        conn.close()
        assert row == ("pass", None)

    def test_t11_no_warnings_key_no_raise(self):
        """t11: gate_result has no 'warnings' key → scope_step row ('pass', None), no raise."""
        pid = lifecycle.mint_and_claim("executable", "/proj", "T", "bellows", "small", 1, "d.md")
        step_id = lifecycle.record_step_start(pid, 1)
        gate_result = {
            "failures": [],
            "passed": True,
            # no 'warnings' key at all
        }
        lifecycle.record_gate_events(step_id, gate_result)
        conn = sqlite3.connect(lifecycle.LIFECYCLE_DB_PATH)
        row = conn.execute(
            "SELECT result, reason_code FROM gate_events WHERE step_id = ? AND gate_name = 'scope_step'",
            (step_id,),
        ).fetchone()
        conn.close()
        assert row == ("pass", None)


class TestScopeStepT12:
    """t12: STEP 2 with no Scope/Deposits — warns on all earlier-step-only files."""

    def test_t12_empty_own_step_set_warns_all_union_files(self):
        """t12: step 2 has no Scope/Deposits; changing a step-1-only file → WARN, passed True."""
        result = gates.check(
            _clean_parsed(), PLAN_STEP2_NO_SCOPE, 2, "/tmp",
            files_changed=["gates.py"],
        )
        assert result["passed"] is True
        assert result["warnings"] == [{"gate": "scope_step", "evidence": "gates.py"}]
