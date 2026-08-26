"""Tests for tools/run_check.py — six pure judge tests + two live smokes."""
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
from run_check import judge_cycle, judge_lint, judge_register


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
