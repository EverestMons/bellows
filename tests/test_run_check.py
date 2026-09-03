"""Tests for tools/run_check.py — pure judge tests + live smokes."""
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
from run_check import judge_cycle, judge_lint, judge_register, judge_propagation


# ---------------------------------------------------------------------------
# Fixtures from real checker output (provenance in comments)
# ---------------------------------------------------------------------------

# cycle_check BAR_MET — from a live cycle_check run on a closed plan
CYCLE_BAR_MET_STDOUT = """\
checking plan…
cycle step 1 — ok
cycle step 2 — ok
BAR_MET
"""

# cycle_check CONTINUE — mid-cycle run where bar is not yet met
CYCLE_CONTINUE_STDOUT = """\
checking plan…
cycle step 1 — ok
CONTINUE
"""

# cycle_check ESCALATE — from a run that hit an escalation condition
CYCLE_ESCALATE_STDOUT = """\
checking plan…
ESCALATE: step 2 exceeded threshold
"""

# walk_register_lint stderr with UNCONFORMANT — from a lint run on a malformed register
REGISTER_UNCONFORMANT_STDERR = (
    "bad-register.md\tUNCONFORMANT\tshapes: missing columns\n"
)

# walk_register_lint stderr with only CONFORMANT — from a clean lint run
# (provenance: walk_register_lint on walk-register-run-check-wrapper-2026-08-26.md)
REGISTER_CONFORMANT_STDERR = (
    "walk-register-run-check-wrapper-2026-08-26.md\tCONFORMANT\t"
    "shapes: | id | walk | lens | sub_question | origin | finding "
    "| pre_fold_text | resolution |\n"
)


# ---------------------------------------------------------------------------
# Pure judge tests (6)
# ---------------------------------------------------------------------------

class TestJudgeCycle:
    def test_bar_met_pass(self):
        verdict, reason = judge_cycle(CYCLE_BAR_MET_STDOUT, "", 0)
        assert verdict == "PASS"
        assert "BAR_MET" in reason

    def test_continue_strict_fail(self):
        verdict, reason = judge_cycle(CYCLE_CONTINUE_STDOUT, "", 0)
        assert verdict == "FAIL"
        assert "CONTINUE" in reason

    def test_continue_accepted_pass(self):
        verdict, reason = judge_cycle(CYCLE_CONTINUE_STDOUT, "", 0,
                                      accept_continue=True)
        assert verdict == "PASS"
        assert "CONTINUE" in reason

    def test_escalate_fail(self):
        verdict, reason = judge_cycle(CYCLE_ESCALATE_STDOUT, "", 0)
        assert verdict == "FAIL"
        assert "ESCALATE" in reason


class TestJudgeRegister:
    def test_unconformant_fail(self):
        verdict, reason = judge_register("", REGISTER_UNCONFORMANT_STDERR, 0)
        assert verdict == "FAIL"
        assert "bad-register.md" in reason
        assert "UNCONFORMANT" in reason

    def test_conformant_pass(self):
        verdict, reason = judge_register("", REGISTER_CONFORMANT_STDERR, 0)
        assert verdict == "PASS"
        assert "CONFORMANT" in reason

    def test_empty_stderr_positive_control_fail(self):
        """The positive control — empty stderr means nothing was scanned."""
        verdict, reason = judge_register("", "", 0)
        assert verdict == "FAIL"
        assert "positive control" in reason

    def test_no_table_is_bad(self):
        """Test 4 — judge_register counts NO_TABLE as bad.
        Commit 45d7aff added this behavior but shipped without a test."""
        stderr = "walk-register-qa-predeclaration.md\tNO_TABLE\tshapes: (none)\n"
        verdict, reason = judge_register("", stderr, 0)
        assert verdict == "FAIL"
        assert "walk-register-qa-predeclaration.md" in reason

    def test_pre_schema_not_bad(self):
        """Test 5 — PRE-SCHEMA is not a defect; judge_register must not count it as bad.
        25 registers in the corpus legitimately predate the schema declaration."""
        stderr = (
            "old-register.md\tPRE-SCHEMA\tshapes: (none)\n"
            "good-register.md\tCONFORMANT\tshapes: | id | walk | ... |\n"
        )
        verdict, reason = judge_register("", stderr, 0)
        assert verdict == "PASS"

    def test_legacy_schema_neither_bad_nor_good(self):
        """Test 5b — LEGACY_SCHEMA is neither bad nor good in judge_register.

        This behavior is EXPLICIT, not by omission. Introducing a status whose judge
        treatment is left to chance creates the defect this plan exists to fix.

        Arm 1: a sweep containing ONLY LEGACY_SCHEMA registers fails the positive
        control (nothing was CONFORMANT-scanned) — the failure reason must reference
        positive control, not a 'bad status' count.

        Arm 2: a LEGACY_SCHEMA line alongside a CONFORMANT line → PASS (legacy
        does not poison a clean sweep).
        """
        # Arm 1: pure legacy sweep fails positive control
        legacy_only = "old.md\tLEGACY_SCHEMA\tshapes: (none)\n"
        verdict1, reason1 = judge_register("", legacy_only, 0)
        assert verdict1 == "FAIL"
        assert "positive control" in reason1

        # Arm 2: legacy + conformant → PASS
        mixed = (
            "old.md\tLEGACY_SCHEMA\tshapes: (none)\n"
            "new.md\tCONFORMANT\tshapes: | id | walk | ... |\n"
        )
        verdict2, _ = judge_register("", mixed, 0)
        assert verdict2 == "PASS"

    def test_failure_message_names_actual_status(self):
        """Test 6 — the failure message names the actual status, not always UNCONFORMANT.
        When only NO_TABLE files are bad, the message must say NO_TABLE, not UNCONFORMANT."""
        no_table_stderr = "register.md\tNO_TABLE\tshapes: (none)\n"
        _, reason = judge_register("", no_table_stderr, 0)
        assert "NO_TABLE" in reason
        # The message must reflect the status actually found, not a hardcoded label
        assert "UNCONFORMANT" not in reason


# ---------------------------------------------------------------------------
# judge_propagation — four cases from real checker output (M3 kill target)
# ---------------------------------------------------------------------------

# propagation_check exit 0 — CLEAN run (after F1 the tool parses the plan)
PROP_CLEAN_STDOUT = (
    "declared symbols: 3 (values: 5)\n"
    "  SUITE: ['1782']\n"
    "  POPULATION: ['51', '34', '17']\n"
    "  CORPUS: ['15']\n"
    "instruction region: 45 lines of 120\n\n"
    "(1) RESTATED VALUE — a declared value written as a bare numeral in prose\n"
    "  none\n\n"
    "(2) ORDERING — distinct task sequences (>1 distinct = a claim stated two ways)\n"
    "  0 distinct sequence — consistent\n\n"
    "(3) ARITHMETIC — same operands, different constants\n"
    "  none\n\n"
    "CLEAN — no divergence found\n"
)

# propagation_check exit 1 — divergences reported
PROP_DIVERGENT_STDOUT = (
    "declared symbols: 2 (values: 3)\n"
    "instruction region: 30 lines of 80\n\n"
    "(1) RESTATED VALUE\n"
    "  L12: `SUITE` = 1782 restated unqualified\n"
    "      Run all 1782 tests.\n"
    "  L25: `POPULATION` = 51 restated unqualified\n"
    "      Covers all 51 rows.\n\n"
    "DIVERGENCES: 2\n"
)

# propagation_check exit 2 — no declarations parsed
PROP_NOTRUN_STDOUT = (
    "declared symbols: 0 (values: 0)\n\n"
    "ERROR: no symbol declarations parsed — detector (1) cannot run.\n"
    "  Expected a Numbers-discipline row of the form: ...\n"
    "  This is EXIT 2 (could not run), never a clean result.\n"
)


class TestJudgePropagation:
    def test_clean_pass(self):
        verdict, reason = judge_propagation(PROP_CLEAN_STDOUT, "", 0)
        assert verdict == "PASS"
        assert "CLEAN" in reason
        assert "3" in reason  # N symbols

    def test_divergent_fail(self):
        verdict, reason = judge_propagation(PROP_DIVERGENT_STDOUT, "", 1)
        assert verdict == "FAIL"
        assert "2" in reason  # N divergences

    def test_not_run_fail(self):
        """M3 kill: rc 2 must be FAIL, never PASS."""
        verdict, reason = judge_propagation(PROP_NOTRUN_STDOUT, "", 2)
        assert verdict == "FAIL"
        assert "NOT RUN" in reason

    def test_crash_fail(self):
        verdict, reason = judge_propagation("", "", 99)
        assert verdict == "FAIL"
        assert "crashed" in reason.lower() or "99" in reason


# ---------------------------------------------------------------------------
# Live smoke tests (2)
# ---------------------------------------------------------------------------

class TestLiveSmokes:
    def test_lint_on_done_plan(self):
        """Lint mode on executable-561.md (Done/) should exit 0 with VERDICT=PASS."""
        target = ROOT / "knowledge" / "decisions" / "Done" / "executable-561.md"
        result = subprocess.run(
            [sys.executable, str(ROOT / "tools" / "run_check.py"),
             "lint", str(target)],
            capture_output=True, text=True, timeout=30,
        )
        assert result.returncode == 0, f"exit {result.returncode}\n{result.stdout}\n{result.stderr}"
        last_line = result.stdout.strip().splitlines()[-1]
        assert "VERDICT=PASS" in last_line

    def test_register_on_walk_register(self):
        """Register mode on the plan's own walk register — proves the pipeline runs.

        Derivation: the walk register is CONFORMANT (verified at deposit);
        the smoke proves the wrapper→checker→judge pipeline, the fixtures
        prove the judgments. Verdict recorded: PASS (1 file CONFORMANT).
        """
        target = ROOT / "knowledge" / "research" / "walk-register-run-check-wrapper-2026-08-26.md"
        result = subprocess.run(
            [sys.executable, str(ROOT / "tools" / "run_check.py"),
             "register", str(target)],
            capture_output=True, text=True, timeout=30,
        )
        last_line = result.stdout.strip().splitlines()[-1]
        assert "RUN_CHECK:" in last_line
        # Record: this register is CONFORMANT → VERDICT=PASS, exit 0
        assert result.returncode == 0, f"exit {result.returncode}\n{result.stdout}\n{result.stderr}"
        assert "VERDICT=PASS" in last_line
