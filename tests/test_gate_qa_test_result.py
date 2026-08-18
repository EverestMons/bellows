"""Tests for _gate_qa_test_result — the QA-result gate (plan 439, step 1)."""

import os
import textwrap

import pytest

import gates


PLAN_TEMPLATE = textwrap.dedent("""\
    # Test Plan
    **Type:** Executable
    **pause_for_verdict:** always
    **qa_steps:** 2
    {extra_header}

    ## STEP 1 — DEV: implementation

    Do stuff.

    **Deposits:**
    - `some_file.py`

    ## STEP 2 — QA: full suite

    Run tests.

    **Deposits:**
    - `knowledge/qa/report.md`
    - `knowledge/qa/evidence/{evidence_filename}`
""")


def _make_plan(evidence_filename="full-suite.txt", extra_header=""):
    return PLAN_TEMPLATE.format(evidence_filename=evidence_filename, extra_header=extra_header)


def _make_evidence(summary_line):
    return f"collected 100 items\n\n{summary_line}\n"


def _run_gate(tmp_path, plan_text, step_number, evidence_content, evidence_filename="full-suite.txt"):
    evidence_dir = tmp_path / "knowledge" / "qa" / "evidence"
    evidence_dir.mkdir(parents=True, exist_ok=True)
    evidence_file = evidence_dir / evidence_filename
    if evidence_content is not None:
        evidence_file.write_text(evidence_content, encoding="utf-8")

    report_dir = tmp_path / "knowledge" / "qa"
    report_dir.mkdir(parents=True, exist_ok=True)
    (report_dir / "report.md").write_text("# QA Report\n", encoding="utf-8")

    header = gates._parse_plan_header(plan_text)
    is_qa_step = gates._gate_is_qa_step(plan_text, step_number, plan_header=header)
    failures = []
    parsed = {"receipt_status": "Complete", "result_text": ""}
    gates._gate_qa_test_result(
        is_qa_step, plan_text, step_number, str(tmp_path), parsed, failures,
        wt_path=str(tmp_path), plan_header=header,
    )
    return failures


class TestCleanSummaryPasses:
    def test_all_passed(self, tmp_path):
        plan = _make_plan()
        evidence = _make_evidence("========================= 100 passed in 12.34s =========================")
        failures = _run_gate(tmp_path, plan, 2, evidence)
        assert failures == []

    def test_passed_with_warnings(self, tmp_path):
        plan = _make_plan()
        evidence = _make_evidence("=============== 100 passed, 3 warnings in 5.67s ===============")
        failures = _run_gate(tmp_path, plan, 2, evidence)
        assert failures == []

    def test_passed_with_skipped(self, tmp_path):
        plan = _make_plan()
        evidence = _make_evidence("============ 98 passed, 2 skipped in 8.90s ============")
        failures = _run_gate(tmp_path, plan, 2, evidence)
        assert failures == []


class TestFailedExceedsKnownFailures:
    def test_failures_above_zero_known(self, tmp_path):
        plan = _make_plan()
        evidence = _make_evidence("============ 2 failed, 98 passed in 12.34s ============")
        failures = _run_gate(tmp_path, plan, 2, evidence)
        assert len(failures) == 1
        assert failures[0]["gate"] == "qa_test_result"
        assert "bad=2" in failures[0]["evidence"]

    def test_failures_above_known(self, tmp_path):
        plan = _make_plan(extra_header="**known_failures:** 1")
        evidence = _make_evidence("============ 3 failed, 97 passed in 12.34s ============")
        failures = _run_gate(tmp_path, plan, 2, evidence)
        assert len(failures) == 1
        assert "delta=2" in failures[0]["evidence"]


class TestFailedEqualsKnownFailures:
    def test_exact_match_passes(self, tmp_path):
        plan = _make_plan(extra_header="**known_failures:** 2")
        evidence = _make_evidence("============ 2 failed, 98 passed in 12.34s ============")
        failures = _run_gate(tmp_path, plan, 2, evidence)
        assert failures == []


class TestNoSummaryLineFailsClosed:
    def test_empty_file(self, tmp_path):
        plan = _make_plan()
        failures = _run_gate(tmp_path, plan, 2, "")
        assert len(failures) == 1
        assert "no parseable pytest summary" in failures[0]["evidence"]

    def test_no_equals_line(self, tmp_path):
        plan = _make_plan()
        evidence = "some random output\ncollected 10 items\nall done\n"
        failures = _run_gate(tmp_path, plan, 2, evidence)
        assert len(failures) == 1
        assert "no parseable pytest summary" in failures[0]["evidence"]

    def test_summary_without_passed(self, tmp_path):
        plan = _make_plan()
        evidence = _make_evidence("========================= no tests ran =========================")
        failures = _run_gate(tmp_path, plan, 2, evidence)
        assert len(failures) == 1
        assert "no parseable pytest summary" in failures[0]["evidence"]


class TestErrorFormFailsClosed:
    def test_errors_only(self, tmp_path):
        plan = _make_plan()
        evidence = _make_evidence("============ 5 passed, 3 errors in 4.56s ============")
        failures = _run_gate(tmp_path, plan, 2, evidence)
        assert len(failures) == 1
        assert "3 errors" in failures[0]["evidence"]
        assert "bad=3" in failures[0]["evidence"]

    def test_failed_plus_errors(self, tmp_path):
        plan = _make_plan()
        evidence = _make_evidence("============ 1 failed, 5 passed, 2 errors in 4.56s ============")
        failures = _run_gate(tmp_path, plan, 2, evidence)
        assert len(failures) == 1
        assert "bad=3" in failures[0]["evidence"]

    def test_zero_failed_with_errors(self, tmp_path):
        """The F-Cold2 keystone: '0 failed, 5 passed, 3 errors' must NOT pass."""
        plan = _make_plan()
        evidence = _make_evidence("============ 0 failed, 5 passed, 3 errors in 4.56s ============")
        failures = _run_gate(tmp_path, plan, 2, evidence)
        assert len(failures) == 1
        assert "3 errors" in failures[0]["evidence"]


class TestNonQaStepNoOps:
    def test_dev_step_skips(self, tmp_path):
        plan = _make_plan()
        failures = _run_gate(tmp_path, plan, 1, None)
        assert failures == []


class TestKnownFailuresMalformed:
    def test_non_int_fails_closed(self, tmp_path):
        plan = _make_plan(extra_header="**known_failures:** abc")
        evidence = _make_evidence("========================= 100 passed in 12.34s =========================")
        failures = _run_gate(tmp_path, plan, 2, evidence)
        assert len(failures) == 1
        assert "known_failures header malformed" in failures[0]["evidence"]


class TestNoTxtDeposit:
    def test_no_txt_fails_closed(self, tmp_path):
        plan_text = textwrap.dedent("""\
            # Test Plan
            **Type:** Executable
            **pause_for_verdict:** always
            **qa_steps:** 2

            ## STEP 1 — DEV: implementation

            Do stuff.

            ## STEP 2 — QA: full suite

            Run tests.

            **Deposits:**
            - `knowledge/qa/report.md`
        """)
        header = gates._parse_plan_header(plan_text)
        is_qa_step = gates._gate_is_qa_step(plan_text, 2, plan_header=header)
        failures = []
        parsed = {"receipt_status": "Complete", "result_text": ""}
        gates._gate_qa_test_result(
            is_qa_step, plan_text, 2, str(tmp_path), parsed, failures,
            wt_path=str(tmp_path), plan_header=header,
        )
        assert len(failures) == 1
        assert "no .txt evidence deposit" in failures[0]["evidence"]


class TestLastSummaryLineUsed:
    def test_multiple_summaries_uses_last(self, tmp_path):
        plan = _make_plan()
        evidence = (
            "========================= 2 failed, 98 passed in 5.00s =========================\n"
            "some intervening output\n"
            "========================= 100 passed in 12.34s =========================\n"
        )
        failures = _run_gate(tmp_path, plan, 2, evidence)
        assert failures == []
