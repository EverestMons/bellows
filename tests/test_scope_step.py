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
> - `tests/test_x.py`
> - `knowledge/research/notes.md`

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

BELLOWS_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PLAN_T18_TWO_STEP = """# bellows — scope-step t18 fixture

**Date:** 2026-09-14 | **Project:** bellows | **qa_steps:** none | **Execution:** Step 1 → Step 2

## STEP 1 — DEV

> Build.
>
> **Scope:**
> - `knowledge/qa/evidence/r.md`
> - `tools/x.py`

## STEP 2 — DEV

> Verify.
>
> **Scope:**
> - `bellows/knowledge/qa/evidence/r.md`
> - `bellows/tools/x.py`
"""

PLAN_T19_TWO_STEP = (
    "# bellows — scope-step t19 fixture\n\n"
    "**Date:** 2026-09-14 | **Project:** bellows | **qa_steps:** none | **Execution:** Step 1 → Step 2\n\n"
    "## STEP 1 — DEV\n\n"
    "> Build.\n>\n> **Scope:**\n> - `tools/y.py`\n\n"
    "## STEP 2 — DEV\n\n"
    "> Verify.\n>\n> **Scope:**\n> - `{root}/tools/y.py`\n"
).format(root=BELLOWS_ROOT)


class TestScopeStepArm:
    """t1–t6: gate-level tests for the scope_step arm in gates.check()."""

    def test_t1_step2_own_scope_no_warn(self):
        """t1: step 2 changing its own declared file → passed True, warnings empty."""
        result = gates.check(
            _clean_parsed(), PLAN_TWO_STEP, 2, "/tmp",
            files_changed=["knowledge/qa/evidence/r.md"],
        )
        assert result["passed"] is True
        assert result["warnings"] == []

    def test_t2_step2_earlier_step_file_fails(self):
        """t2: step 2 changing a file declared only in step 1 → passed False, scope_step failure."""
        result = gates.check(
            _clean_parsed(), PLAN_TWO_STEP, 2, "/tmp",
            files_changed=["gates.py"],
        )
        assert result["passed"] is False
        assert result["failures"] == [{"gate": "scope_step", "evidence": "declared by an earlier step only: gates.py"}]
        assert result["warnings"] == []

    def test_t3_step2_undeclared_file_fails_not_warned(self):
        """t3: step 2 changing a completely undeclared file → scope_check FAIL, no warn."""
        result = gates.check(
            _clean_parsed(), PLAN_TWO_STEP, 2, "/tmp",
            files_changed=["totally_unexpected.py"],
        )
        assert result["passed"] is False
        scope_fails = [f for f in result["failures"] if f["gate"] == "scope_check"]
        assert len(scope_fails) == 1
        scope_step_fails = [f for f in result["failures"] if f["gate"] == "scope_step"]
        assert scope_step_fails == []
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
        scope_step_fails = [f for f in result["failures"] if f["gate"] == "scope_step"]
        assert scope_step_fails == []


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
    """t12: STEP 2 with no Scope/Deposits — fails on earlier-step-only files."""

    def test_t12_empty_own_step_set_fails_on_union_files(self):
        """t12: STEP 2 has no Scope/Deposits; changing a step-1-only file → passed False, scope_step failure."""
        result = gates.check(
            _clean_parsed(), PLAN_STEP2_NO_SCOPE, 2, "/tmp",
            files_changed=["gates.py"],
        )
        assert result["passed"] is False
        assert result["failures"] == [{"gate": "scope_step", "evidence": "declared by an earlier step only: gates.py"}]
        assert result["warnings"] == []


class TestScopeStepFail:
    """t13–t22: scope_step FAIL arm — every kind fails; one failure per step; helpers shared."""

    def test_t13_test_file_declared_earlier_fails(self):
        """t13: step 2 changing a test file declared only in step 1 → passed False, scope_step failure."""
        result = gates.check(
            _clean_parsed(), PLAN_TWO_STEP, 2, "/tmp",
            files_changed=["tests/test_x.py"],
        )
        assert result["passed"] is False
        assert result["failures"] == [{"gate": "scope_step", "evidence": "declared by an earlier step only: tests/test_x.py"}]
        assert result["warnings"] == []

    def test_t14_knowledge_file_declared_earlier_fails(self):
        """t14: step 2 changing a knowledge file declared only in step 1 → passed False, scope_step failure."""
        result = gates.check(
            _clean_parsed(), PLAN_TWO_STEP, 2, "/tmp",
            files_changed=["knowledge/research/notes.md"],
        )
        assert result["passed"] is False
        assert result["failures"] == [{"gate": "scope_step", "evidence": "declared by an earlier step only: knowledge/research/notes.md"}]
        assert result["warnings"] == []

    def test_t15_multiple_earlier_step_files_one_failure(self):
        """t15: step 2 changing all three earlier-step files → ONE scope_step failure naming all."""
        result = gates.check(
            _clean_parsed(), PLAN_TWO_STEP, 2, "/tmp",
            files_changed=["gates.py", "tests/test_x.py", "knowledge/research/notes.md"],
        )
        assert result["passed"] is False
        assert result["failures"] == [{"gate": "scope_step", "evidence": "declared by an earlier step only: gates.py, tests/test_x.py, knowledge/research/notes.md"}]
        assert result["warnings"] == []

    def test_t16_table_scope_step_fail_row(self):
        """t16: verdict table with scope_step failure → FAIL row, scope_check still PASS."""
        gate_result = {
            "failures": [{"gate": "scope_step", "evidence": "declared by an earlier step only: gates.py"}],
            "passed": False,
            "is_qa_step": False,
            "files_changed": ["gates.py"],
            "warnings": [],
        }
        table = verdict._build_verification_results_table(gate_result, {}, 2, 2)
        assert "| scope_step | FAIL | declared by an earlier step only: gates.py |" in table
        assert "| scope_check | PASS |" in table

    def test_t17_ledger_scope_step_fail_row(self):
        """t17: record_gate_events with scope_step failure → exactly one scope_step row, fail."""
        pid = lifecycle.mint_and_claim("executable", "/proj", "T", "bellows", "small", 1, "d.md")
        step_id = lifecycle.record_step_start(pid, 1)
        gate_result = {
            "failures": [{"gate": "scope_step", "evidence": "declared by an earlier step only: gates.py"}],
            "passed": False,
            "warnings": [],
        }
        lifecycle.record_gate_events(step_id, gate_result)
        conn = sqlite3.connect(lifecycle.LIFECYCLE_DB_PATH)
        rows = conn.execute(
            "SELECT result, reason_code FROM gate_events WHERE step_id = ? AND gate_name = 'scope_step'",
            (step_id,),
        ).fetchall()
        conn.close()
        assert rows == [("fail", "declared by an earlier step only: gates.py")]

    def test_t18_leading_segment_own_step_passes(self):
        """t18: step 2 declares files with one extra leading segment; changing them is own: passed True."""
        result = gates.check(
            _clean_parsed(), PLAN_T18_TWO_STEP, 2, "/tmp",
            files_changed=["knowledge/qa/evidence/r.md", "tools/x.py"],
        )
        assert result["passed"] is True
        assert result["failures"] == []

    def test_t19_absolute_path_own_step_passes(self):
        """t19: step 2 declares tools/y.py by absolute path; after normalization it matches: passed True."""
        result = gates.check(
            _clean_parsed(), PLAN_T19_TWO_STEP, 2, BELLOWS_ROOT,
            files_changed=["tools/y.py"],
        )
        assert result["passed"] is True
        assert result["failures"] == []

    def test_t20_direct_caller_no_warnings_reads_union_only(self):
        """t20: _gate_scope_check without warnings → union-only, no scope_step failure."""
        failures = []
        gates._gate_scope_check(PLAN_TWO_STEP, 2, ["gates.py"], failures)
        assert failures == []

    def test_t21_recorded_100061_step2_scope_step_fails(self):
        """t21: recorded step 100061 step 2 changes scripts/close_cycle.py declared only by step 1."""
        plan_path = os.path.join(BELLOWS_ROOT, "knowledge/decisions/Done/executable-100061.md")
        with open(plan_path, encoding="utf-8") as f:
            plan_text = f.read()
        files = [
            "knowledge/qa/evidence/close-cycle-tool-qa-evidence-2026-09-09.md",
            "knowledge/qa/evidence/close-cycle-tool-suite-2026-09-09.txt",
            "scripts/close_cycle.py",
        ]
        failures = []
        gates._gate_scope_check(plan_text, 2, files, failures, project_path=BELLOWS_ROOT, warnings=[])
        assert failures == [{"gate": "scope_step", "evidence": "declared by an earlier step only: scripts/close_cycle.py"}]

    def test_t22_recorded_100037_step2_scope_check_and_scope_step(self):
        """t22: recorded step 100037 step 2 has undeclared tests + manifest declared only by step 1."""
        plan_path = os.path.join(BELLOWS_ROOT, "knowledge/decisions/Done/executable-100037.md")
        with open(plan_path, encoding="utf-8") as f:
            plan_text = f.read()
        files = [
            "knowledge/mutants/close-failopen-defaults.json",
            "knowledge/qa/evidence/close-failopen-defaults-2026-09-04/probes-raw.txt",
            "knowledge/qa/evidence/close-failopen-defaults-2026-09-04/pytest_full.txt",
            "knowledge/qa/evidence/close-failopen-defaults-2026-09-04/qa-receipt.md",
            "tests/test_depositor_receipts.py",
            "tests/test_wrap_receipts.py",
        ]
        failures = []
        gates._gate_scope_check(plan_text, 2, files, failures, project_path=BELLOWS_ROOT, warnings=[])
        assert len(failures) == 2
        assert failures[0]["gate"] == "scope_check"
        assert failures[0]["evidence"].startswith("out-of-scope files: tests/test_depositor_receipts.py, tests/test_wrap_receipts.py")
        assert failures[1] == {"gate": "scope_step", "evidence": "declared by an earlier step only: knowledge/mutants/close-failopen-defaults.json"}
