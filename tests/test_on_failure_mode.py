"""Tests for on_failure pause mode (plan 439, step 2).

Covers: header_says_pause branch, three-site is_qa_step guard,
effective_auto_close under on_failure, plan_lint FAIL for missing qa_steps,
and backward-compat with existing modes (Q7).
"""

import textwrap

import pytest

import bellows
from scripts import plan_lint


# ---------------------------------------------------------------------------
# header_says_pause
# ---------------------------------------------------------------------------

class TestHeaderSaysPause:
    def test_on_failure_returns_false(self):
        header = {"pause_for_verdict": "on_failure"}
        assert bellows.header_says_pause(header, 1, 3, is_qa_step=False) is False

    def test_on_failure_returns_false_on_qa_step(self):
        header = {"pause_for_verdict": "on_failure"}
        assert bellows.header_says_pause(header, 2, 3, is_qa_step=True) is False

    def test_on_failure_returns_false_on_final_step(self):
        header = {"pause_for_verdict": "on_failure"}
        assert bellows.header_says_pause(header, 3, 3, is_qa_step=False) is False

    # Q7 backward-compat: existing modes unchanged
    def test_always_still_pauses(self):
        header = {"pause_for_verdict": "always"}
        assert bellows.header_says_pause(header, 1, 3, is_qa_step=False) is True

    def test_after_step_1_still_pauses_step1(self):
        header = {"pause_for_verdict": "after_step_1"}
        assert bellows.header_says_pause(header, 1, 3, is_qa_step=False) is True

    def test_after_step_1_no_pause_step2(self):
        header = {"pause_for_verdict": "after_step_1"}
        assert bellows.header_says_pause(header, 2, 3, is_qa_step=False) is False

    def test_after_qa_step_pauses_qa(self):
        header = {"pause_for_verdict": "after_qa_step"}
        assert bellows.header_says_pause(header, 2, 3, is_qa_step=True) is True

    def test_after_qa_step_no_pause_non_qa(self):
        header = {"pause_for_verdict": "after_qa_step"}
        assert bellows.header_says_pause(header, 2, 3, is_qa_step=False) is False

    def test_qa_and_terminal_pauses_qa(self):
        header = {"pause_for_verdict": "qa_and_terminal"}
        assert bellows.header_says_pause(header, 1, 3, is_qa_step=True) is True

    def test_qa_and_terminal_pauses_final(self):
        header = {"pause_for_verdict": "qa_and_terminal"}
        assert bellows.header_says_pause(header, 3, 3, is_qa_step=False) is True


# ---------------------------------------------------------------------------
# Three-site is_qa_step guard (unit harness on the pause conditions)
# ---------------------------------------------------------------------------

def _site1_would_pause(gate_result, header):
    """Non-final while-loop pause condition (bellows.py ~:993-996)."""
    return (not gate_result["passed"]
            or (gate_result["is_qa_step"] and header.get("pause_for_verdict") != "on_failure")
            or gate_result.get("verdict_requested", {}).get("requested", False)
            or bellows.header_says_pause(header, 1, 3, gate_result["is_qa_step"]))


def _site2_would_pause(gate_result, header, effective_auto_close):
    """Final-step pause condition (bellows.py ~:1117-1121)."""
    return (not gate_result["passed"]
            or (gate_result["is_qa_step"] and header.get("pause_for_verdict") != "on_failure")
            or gate_result.get("verdict_requested", {}).get("requested", False)
            or bellows.header_says_pause(header, 3, 3, gate_result["is_qa_step"])
            or not effective_auto_close)


def _site3_would_auto_close(gate_result, header, effective_auto_close):
    """Auto-close condition (bellows.py ~:1162-1166)."""
    return (gate_result["passed"]
            and (not gate_result["is_qa_step"] or header.get("pause_for_verdict") == "on_failure")
            and not bellows.header_says_pause(header, 3, 3, gate_result["is_qa_step"])
            and not gate_result.get("verdict_requested", {}).get("requested", False)
            and effective_auto_close)


class TestThreeSiteGuard:
    def _clean_qa_gate_result(self):
        return {"passed": True, "is_qa_step": True, "failures": []}

    def _clean_non_qa_gate_result(self):
        return {"passed": True, "is_qa_step": False, "failures": []}

    def _failed_qa_gate_result(self):
        return {"passed": False, "is_qa_step": True, "failures": [{"gate": "qa_test_result"}]}

    # on_failure: clean QA step does NOT pause (auto-continues)
    def test_site1_on_failure_clean_qa_no_pause(self):
        header = {"pause_for_verdict": "on_failure"}
        assert _site1_would_pause(self._clean_qa_gate_result(), header) is False

    def test_site2_on_failure_clean_qa_no_pause(self):
        header = {"pause_for_verdict": "on_failure"}
        assert _site2_would_pause(self._clean_qa_gate_result(), header, effective_auto_close=True) is False

    def test_site3_on_failure_clean_qa_auto_closes(self):
        header = {"pause_for_verdict": "on_failure"}
        assert _site3_would_auto_close(self._clean_qa_gate_result(), header, effective_auto_close=True) is True

    # on_failure: failed QA step DOES pause (gate failure always pauses)
    def test_site1_on_failure_failed_qa_pauses(self):
        header = {"pause_for_verdict": "on_failure"}
        assert _site1_would_pause(self._failed_qa_gate_result(), header) is True

    def test_site2_on_failure_failed_qa_pauses(self):
        header = {"pause_for_verdict": "on_failure"}
        assert _site2_would_pause(self._failed_qa_gate_result(), header, effective_auto_close=True) is True

    # Q7: existing modes still pause on QA step
    def test_site1_always_qa_pauses(self):
        header = {"pause_for_verdict": "always"}
        assert _site1_would_pause(self._clean_qa_gate_result(), header) is True

    def test_site1_after_qa_step_qa_pauses(self):
        header = {"pause_for_verdict": "after_qa_step"}
        assert _site1_would_pause(self._clean_qa_gate_result(), header) is True

    def test_site1_qa_and_terminal_qa_pauses(self):
        header = {"pause_for_verdict": "qa_and_terminal"}
        assert _site1_would_pause(self._clean_qa_gate_result(), header) is True

    # on_failure: clean non-QA step also auto-continues
    def test_site1_on_failure_clean_non_qa_no_pause(self):
        header = {"pause_for_verdict": "on_failure"}
        assert _site1_would_pause(self._clean_non_qa_gate_result(), header) is False


# ---------------------------------------------------------------------------
# effective_auto_close
# ---------------------------------------------------------------------------

class TestEffectiveAutoClose:
    def _compute_effective_auto_close(self, header):
        return (
            str(header.get("auto_close", "false")).lower() == "true"
            or header.get("pause_for_verdict") == "on_failure"
        )

    def test_on_failure_implies_auto_close(self):
        header = {"pause_for_verdict": "on_failure"}
        assert self._compute_effective_auto_close(header) is True

    def test_on_failure_with_auto_close_false(self):
        header = {"pause_for_verdict": "on_failure", "auto_close": "false"}
        assert self._compute_effective_auto_close(header) is True

    def test_explicit_auto_close_true(self):
        header = {"auto_close": "true"}
        assert self._compute_effective_auto_close(header) is True

    def test_always_no_auto_close(self):
        header = {"pause_for_verdict": "always"}
        assert self._compute_effective_auto_close(header) is False

    def test_default_no_auto_close(self):
        header = {}
        assert self._compute_effective_auto_close(header) is False


# ---------------------------------------------------------------------------
# plan_lint: on_failure requires qa_steps
# ---------------------------------------------------------------------------

PLAN_WITH_ON_FAILURE = textwrap.dedent("""\
    # Test Plan
    **Type:** Executable
    **pause_for_verdict:** on_failure
    **dispatch_mode:** bellows
    **qa_steps:** 2

    ## STEP 1 — DEV: implementation

    Do stuff.

    **Deposits:**
    - `some_file.py`

    ## STEP 2 — QA: full suite

    Run tests.

    ## Rule 20 — QA Self-Check Results
    **PASSED — SELF-CHECK PASSED**

    **Deposits:**
    - `knowledge/qa/report.md`
""")

PLAN_ON_FAILURE_NO_QA_STEPS = textwrap.dedent("""\
    # Test Plan
    **Type:** Executable
    **pause_for_verdict:** on_failure
    **dispatch_mode:** bellows

    ## STEP 1 — DEV: implementation

    Do stuff.

    **Deposits:**
    - `some_file.py`
""")

PLAN_QA_AND_TERMINAL_NO_QA_STEPS = textwrap.dedent("""\
    # Test Plan
    **Type:** Executable
    **pause_for_verdict:** qa_and_terminal
    **dispatch_mode:** bellows

    ## STEP 1 — DEV: implementation

    Do stuff.

    **Deposits:**
    - `some_file.py`
""")


class TestPlanLintOnFailure:
    def test_on_failure_with_qa_steps_passes(self, tmp_path):
        plan_file = tmp_path / "plan.md"
        plan_file.write_text(PLAN_WITH_ON_FAILURE, encoding="utf-8")
        exit_code = plan_lint.lint(str(plan_file))
        assert exit_code == 0

    def test_on_failure_without_qa_steps_fails(self, tmp_path):
        plan_file = tmp_path / "plan.md"
        plan_file.write_text(PLAN_ON_FAILURE_NO_QA_STEPS, encoding="utf-8")
        exit_code = plan_lint.lint(str(plan_file))
        assert exit_code == 1

    def test_qa_and_terminal_without_qa_steps_warns_not_fails(self, tmp_path):
        """Q7 compat: qa_and_terminal missing qa_steps is WARN, not FAIL."""
        plan_file = tmp_path / "plan.md"
        plan_file.write_text(PLAN_QA_AND_TERMINAL_NO_QA_STEPS, encoding="utf-8")
        exit_code = plan_lint.lint(str(plan_file))
        assert exit_code == 0


# ---------------------------------------------------------------------------
# RECOGNIZED_PAUSE_TOKENS includes on_failure
# ---------------------------------------------------------------------------

class TestRecognizedPauseTokens:
    def test_on_failure_recognized(self):
        assert "on_failure" in plan_lint.RECOGNIZED_PAUSE_TOKENS

    def test_existing_tokens_still_recognized(self):
        for token in ("always", "after_step_1", "after_qa_step", "qa_and_terminal"):
            assert token in plan_lint.RECOGNIZED_PAUSE_TOKENS
