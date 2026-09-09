"""Tests for the four new gate arms added by plan 100052.

204: _select_qa_report (content-based QA report selection)
211: _gate_quoted_test_nodes_exist widened to DEV steps
203: _gate_qa_nodes_match_suite (quoted node verdict vs suite output)
196: _gate_dev_log_declared_text (declared headings and verbatim cells)
204b: _select_summary_txt (content-based suite selection with Rule-21 tie-breaks)

Test 5 is expected GREEN before implementation; tests 1-4 and 6-17 are expected red.
All tests use plans-as-strings and deposits under tmp_path.
"""
import os
import re
import sqlite3
import sys
from unittest.mock import patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import gates
import verdict
import lifecycle


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


_PLAN_NO_SCOPE = """\
# bellows — executable: fixture

**Date:** 2026-09-09 | **Project:** bellows | **qa_steps:** 2 | **Execution:** Step 1 (DEV) → Step 2 (QA)

## STEP 1 — DEV

> Build something.

## STEP 2 — QA

> Run all tests.
"""


def _qa_plan(md_paths=None, txt_paths=None):
    """QA plan: STEP 1 DEV, STEP 2 QA with given deposits."""
    md_paths = md_paths or []
    txt_paths = txt_paths or []
    all_paths = md_paths + txt_paths
    deposit_lines = "\n".join(f"> - `{p}`" for p in all_paths)
    return (
        "# bellows — executable: fixture\n\n"
        "**Date:** 2026-09-09 | **Project:** bellows | **qa_steps:** 2"
        " | **Execution:** Step 1 (DEV) → Step 2 (QA)\n\n"
        "## STEP 1 — DEV\n\n> Nothing here.\n\n"
        "## STEP 2 — QA\n\n> **Deposits:**\n" + deposit_lines + "\n"
    )


def _dev_plan(md_paths=None, extra_text=""):
    """DEV plan: pin table in head, STEP 1 DEV with deposits and optional extra text."""
    md_paths = md_paths or []
    if md_paths:
        deposit_lines = "\n".join(f"> - `{p}`" for p in md_paths)
        deposits_block = "\n> **Deposits:**\n" + deposit_lines + "\n"
    else:
        deposits_block = ""
    return (
        "# bellows — executable: fixture\n\n"
        "| # | pin | value | how to re-derive |\n"
        "|---|---|---|---|\n"
        "| P10 | blast radius |"
        " population: every `.md` under **the trees** = 2080 files | script |\n"
        "| P99 | other | other value | - |\n\n"
        "**Date:** 2026-09-09 | **Project:** bellows | **qa_steps:** 2"
        " | **Execution:** Step 1 (DEV) → Step 2 (QA)\n\n"
        "## STEP 1 — DEV\n\n> Some DEV work.\n"
        + extra_text
        + deposits_block
        + "\n## STEP 2 — QA\n\n> Nothing here.\n"
    )


# ---------------------------------------------------------------------------
# Tests 1-3: _select_qa_report (204)
# ---------------------------------------------------------------------------

def test_1_banner_wins(tmp_path):
    """notes.md (no banner) listed first, receipt.md (banner+PASSED+table) second → receipt chosen."""
    notes = tmp_path / "notes.md"
    notes.write_text("Some notes without banner.\n")

    receipt = tmp_path / "receipt.md"
    receipt.write_text(
        "## Verification\n"
        "| Check | Result | Detail |\n"
        "|---|---|---|\n"
        "| suite | ✅ | 10 passed |\n\n"
        "============================================================\n"
        "Rule 20 — QA Self-Check Results\n"
        "============================================================\n"
        "PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.\n"
    )

    # _select_qa_report returns receipt.md
    path, _ = gates._select_qa_report(["notes.md", "receipt.md"], str(tmp_path))
    assert path == "receipt.md"

    # rule_20 and rule_22 add nothing
    plan = _qa_plan(["notes.md", "receipt.md"], [])
    parsed = _clean_parsed()
    failures = []
    gates._gate_rule_20_self_check(True, plan, 2, str(tmp_path), parsed, failures, wt_path=str(tmp_path))
    gates._gate_rule_22_verification(True, plan, 2, str(tmp_path), parsed, failures, wt_path=str(tmp_path))
    assert failures == [], f"Expected no failures, got: {failures}"

    # With PASSED line removed, rule_20 fails naming receipt.md (NOT notes.md)
    receipt.write_text(
        "## Verification\n"
        "| Check | Result |\n"
        "|---|---|\n"
        "| suite | ✅ |\n\n"
        "============================================================\n"
        "Rule 20 — QA Self-Check Results\n"
        "============================================================\n"
        "Checking...\n"
    )
    failures2 = []
    gates._gate_rule_20_self_check(True, plan, 2, str(tmp_path), parsed, failures2, wt_path=str(tmp_path))
    assert len(failures2) == 1
    assert "receipt.md" in failures2[0]["evidence"]
    assert "notes.md" not in failures2[0]["evidence"]


def test_2_legacy_position(tmp_path):
    """No banner/Verification anywhere → md_paths[0] chosen; unreadable first; Shape 7A."""
    first = tmp_path / "first.md"
    first.write_text("No banner. No verification section.\n")
    second = tmp_path / "second.md"
    second.write_text("Also no banner here.\n")

    # _select_qa_report returns first (md_paths[0]) — both score 0
    path, _ = gates._select_qa_report(["first.md", "second.md"], str(tmp_path))
    assert path == "first.md"

    # rule_20 fails with byte-exact today's text
    plan = _qa_plan(["first.md", "second.md"], [])
    parsed = _clean_parsed()
    failures = []
    gates._gate_rule_20_self_check(True, plan, 2, str(tmp_path), parsed, failures, wt_path=str(tmp_path))
    assert len(failures) == 1
    assert failures[0]["evidence"] == "no QA deposit contains Rule 20 self-check banner"

    # Unreadable first file → today's "deposit file unreadable: … (file not found)" text
    plan2 = _qa_plan(["nonexistent.md", "second.md"], [])
    failures2 = []
    gates._gate_rule_20_self_check(True, plan2, 2, str(tmp_path), parsed, failures2, wt_path=str(tmp_path))
    assert len(failures2) == 1
    assert "deposit file unreadable" in failures2[0]["evidence"]
    assert "nonexistent.md" in failures2[0]["evidence"]
    assert "file not found" in failures2[0]["evidence"]

    # Shape 7A: banner text appears inside a prose sentence on second file (not as whole line)
    s7a_first = tmp_path / "s7a_first.md"
    s7a_first.write_text("No banner.\n")
    s7a_second = tmp_path / "s7a_second.md"
    s7a_second.write_text(
        "See Rule 20 — QA Self-Check Results for more context. Not a whole line.\n"
    )
    path7a, _ = gates._select_qa_report(["s7a_first.md", "s7a_second.md"], str(tmp_path))
    assert path7a == "s7a_first.md"  # both score 0, first wins

    # rule_20 still fails with today's text (s7a_first chosen, no banner)
    plan3 = _qa_plan(["s7a_first.md", "s7a_second.md"], [])
    failures3 = []
    gates._gate_rule_20_self_check(True, plan3, 2, str(tmp_path), parsed, failures3, wt_path=str(tmp_path))
    assert failures3[0]["evidence"] == "no QA deposit contains Rule 20 self-check banner"


def test_3_scoring(tmp_path):
    """notes.md: banner only (score 2); receipt.md: banner+## Verification (score 3) → receipt wins."""
    notes = tmp_path / "notes.md"
    notes.write_text("Rule 20 — QA Self-Check Results\n")  # banner as whole line → +2

    receipt = tmp_path / "receipt.md"
    receipt.write_text(
        "## Verification\n"  # +1
        "Rule 20 — QA Self-Check Results\n"  # +2 (banner as whole line)
    )

    path, _ = gates._select_qa_report(["notes.md", "receipt.md"], str(tmp_path))
    assert path == "receipt.md"  # score 3 beats score 2

    # A lone ## Verification file (score 1) beats a bannerless first file (score 0)
    ver = tmp_path / "ver.md"
    ver.write_text(
        "## Verification\n"
        "| Check | Result |\n"
        "|---|---|\n"
        "| suite | ❌ |\n"
    )
    no_ver = tmp_path / "no_ver.md"
    no_ver.write_text("No verification here.\n")

    path2, _ = gates._select_qa_report(["no_ver.md", "ver.md"], str(tmp_path))
    assert path2 == "ver.md"  # score 1 beats score 0

    # rule_22's (c) evidence names ver.md (the ❌ row triggers a failure citing ver.md)
    plan = _qa_plan(["no_ver.md", "ver.md"], [])
    parsed = _clean_parsed()
    failures = []
    gates._gate_rule_22_verification(True, plan, 2, str(tmp_path), parsed, failures, wt_path=str(tmp_path))
    assert any("ver.md" in f["evidence"] for f in failures), (
        f"Expected ver.md in rule_22 evidence: {failures}"
    )


# ---------------------------------------------------------------------------
# Tests 4-5: _gate_quoted_test_nodes_exist widened to DEV steps (211)
# ---------------------------------------------------------------------------

def test_4_211_dev_step_missing_nodes(tmp_path):
    """DEV step: dev-log quoting two missing nodes → one failure naming both."""
    test_file = tmp_path / "tests" / "test_foo.py"
    test_file.parent.mkdir(parents=True)
    test_file.write_text("def test_real():\n    pass\n")

    dev_log = tmp_path / "dev-log.md"
    dev_log.write_text(
        "## Section\n\n"
        "See `tests/test_foo.py::test_missing_one` and"
        " `tests/test_foo.py::test_missing_two`.\n"
    )

    plan = _dev_plan(["dev-log.md"])
    parsed = _clean_parsed()
    failures = []
    gates._gate_quoted_test_nodes_exist(
        False, plan, 1, str(tmp_path), parsed, failures, wt_path=str(tmp_path)
    )
    assert len(failures) == 1
    assert failures[0]["gate"] == "quoted_test_nodes_exist"
    assert "test_missing_one" in failures[0]["evidence"]
    assert "test_missing_two" in failures[0]["evidence"]


def test_5_211_dev_step_nodes_exist(tmp_path):
    """DEV step: dev-log quoting existing nodes → adds nothing (green before implementation)."""
    test_file = tmp_path / "tests" / "test_foo.py"
    test_file.parent.mkdir(parents=True)
    test_file.write_text("def test_real():\n    pass\n")

    dev_log = tmp_path / "dev-log.md"
    dev_log.write_text("See `tests/test_foo.py::test_real` — it exists.\n")

    plan = _dev_plan(["dev-log.md"])
    parsed = _clean_parsed()
    failures = []
    gates._gate_quoted_test_nodes_exist(
        False, plan, 1, str(tmp_path), parsed, failures, wt_path=str(tmp_path)
    )
    assert failures == []


# ---------------------------------------------------------------------------
# Tests 6-11: _gate_qa_nodes_match_suite (203)
# ---------------------------------------------------------------------------

def test_6_203_failed_marked_present(tmp_path):
    """Receipt FAILED node, suite has FAILED for that node → adds nothing."""
    receipt = tmp_path / "receipt.md"
    receipt.write_text(
        "FAILED tests/t.py::test_a\n"
        "Rule 20 — QA Self-Check Results\n"
        "PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.\n"
    )
    suite = tmp_path / "suite.txt"
    suite.write_text("FAILED tests/t.py::test_a - AssertionError\n3 passed in 0.5s\n")

    plan = _qa_plan(["receipt.md"], ["suite.txt"])
    parsed = _clean_parsed()
    failures = []
    gates._gate_qa_nodes_match_suite(
        True, plan, 2, str(tmp_path), parsed, failures, wt_path=str(tmp_path)
    )
    assert failures == []


def test_7_203_failed_marked_absent(tmp_path):
    """Receipt FAILED node absent from suite → FAIL: quoted FAILED, absent from suite."""
    receipt = tmp_path / "receipt.md"
    receipt.write_text(
        "FAILED tests/t.py::test_a\n"
        "Rule 20 — QA Self-Check Results\n"
        "PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.\n"
    )
    suite = tmp_path / "suite.txt"
    suite.write_text("3 passed in 0.5s\n")

    plan = _qa_plan(["receipt.md"], ["suite.txt"])
    parsed = _clean_parsed()
    failures = []
    gates._gate_qa_nodes_match_suite(
        True, plan, 2, str(tmp_path), parsed, failures, wt_path=str(tmp_path)
    )
    assert len(failures) == 1
    assert "quoted FAILED, absent from suite" in failures[0]["evidence"]
    assert "tests/t.py::test_a" in failures[0]["evidence"]


def test_8_203_passed_marked_contradicted(tmp_path):
    """Receipt PASSED node, suite says FAILED → FAIL: quoted PASSED, suite says FAILED."""
    receipt = tmp_path / "receipt.md"
    receipt.write_text(
        "tests/t.py::test_b PASSED ✅\n"
        "Rule 20 — QA Self-Check Results\n"
        "PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.\n"
    )
    suite = tmp_path / "suite.txt"
    suite.write_text("FAILED tests/t.py::test_b - some error\n3 passed in 0.5s\n")

    plan = _qa_plan(["receipt.md"], ["suite.txt"])
    parsed = _clean_parsed()
    failures = []
    gates._gate_qa_nodes_match_suite(
        True, plan, 2, str(tmp_path), parsed, failures, wt_path=str(tmp_path)
    )
    assert len(failures) == 1
    assert "quoted PASSED, suite says FAILED" in failures[0]["evidence"]
    assert "tests/t.py::test_b" in failures[0]["evidence"]


def test_9_203_quiet_suite_adds_nothing(tmp_path):
    """Quiet (-q) suite: no node lines; receipt quotes PASSED nodes → adds nothing."""
    receipt = tmp_path / "receipt.md"
    receipt.write_text(
        "tests/t.py::test_c PASSED ✅\n"
        "tests/t.py::test_d PASSED ✅\n"
        "tests/t.py::test_e PASSED ✅\n"
        "Rule 20 — QA Self-Check Results\n"
        "PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.\n"
    )
    suite = tmp_path / "suite.txt"
    suite.write_text("10 passed in 1.0s\n")

    plan = _qa_plan(["receipt.md"], ["suite.txt"])
    parsed = _clean_parsed()
    failures = []
    gates._gate_qa_nodes_match_suite(
        True, plan, 2, str(tmp_path), parsed, failures, wt_path=str(tmp_path)
    )
    assert failures == []


def test_10_203_verbose_suite(tmp_path):
    """Verbose suite: absent PASSED node → FAIL; present → nothing; test_c ≠ test_cd."""
    receipt = tmp_path / "receipt.md"
    receipt.write_text(
        "tests/t.py::test_c PASSED ✅\n"
        "tests/t.py::test_cd PASSED ✅\n"
        "Rule 20 — QA Self-Check Results\n"
        "PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.\n"
    )

    # (-v) shape: test_c present, test_cd absent → one failure for test_cd only
    suite_v = tmp_path / "suite_v.txt"
    suite_v.write_text("tests/t.py::test_c PASSED\n10 passed in 1.0s\n")

    plan_v = _qa_plan(["receipt.md"], ["suite_v.txt"])
    parsed = _clean_parsed()
    failures_v = []
    gates._gate_qa_nodes_match_suite(
        True, plan_v, 2, str(tmp_path), parsed, failures_v, wt_path=str(tmp_path)
    )
    assert len(failures_v) == 1
    assert "quoted PASSED, absent from verbose suite" in failures_v[0]["evidence"]
    assert "tests/t.py::test_cd" in failures_v[0]["evidence"]
    # test_c is present in the suite — must NOT appear in evidence
    assert "test_c;" not in failures_v[0]["evidence"]
    assert "test_c," not in failures_v[0]["evidence"]

    # (-rA) shape: test_c present via PASSED prefix; test_cd absent → one failure
    suite_ra = tmp_path / "suite_ra.txt"
    suite_ra.write_text("PASSED tests/t.py::test_c\n10 passed in 1.0s\n")

    plan_ra = _qa_plan(["receipt.md"], ["suite_ra.txt"])
    failures_ra = []
    gates._gate_qa_nodes_match_suite(
        True, plan_ra, 2, str(tmp_path), parsed, failures_ra, wt_path=str(tmp_path)
    )
    assert len(failures_ra) == 1
    assert "quoted PASSED, absent from verbose suite" in failures_ra[0]["evidence"]
    assert "tests/t.py::test_cd" in failures_ra[0]["evidence"]


def test_11_203_adds_nothing(tmp_path):
    """Non-QA step → nothing; no-marker line → skip; both-marker line → skip."""
    receipt = tmp_path / "receipt.md"
    receipt.write_text(
        "A line with no markers but tests/t.py::test_a mentioned.\n"
        "FAILED and PASSED tests/t.py::test_b — both markers, unclassifiable.\n"
        "Rule 20 — QA Self-Check Results\n"
        "PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.\n"
    )
    suite = tmp_path / "suite.txt"
    suite.write_text("5 passed in 0.5s\n")

    plan = _qa_plan(["receipt.md"], ["suite.txt"])
    parsed = _clean_parsed()

    # Non-QA step → nothing
    failures = []
    gates._gate_qa_nodes_match_suite(
        False, plan, 1, str(tmp_path), parsed, failures, wt_path=str(tmp_path)
    )
    assert failures == []

    # QA step: no-marker line and both-marker line are both skipped → nothing
    failures2 = []
    gates._gate_qa_nodes_match_suite(
        True, plan, 2, str(tmp_path), parsed, failures2, wt_path=str(tmp_path)
    )
    assert failures2 == []


# ---------------------------------------------------------------------------
# Tests 12-14: _gate_dev_log_declared_text (196)
# ---------------------------------------------------------------------------

def test_12_196_arm_a(tmp_path):
    """Arm (a): declared headings must appear as full stripped lines; paraphrase fails."""
    dev_log = tmp_path / "dev-log.md"
    dev_log.write_text(
        "## Pins re-derived (P1, P2)\nSome content\n"
        "## Cost\nTiming data\n"
    )

    extra_text = "> **Headings:** `## Pins re-derived (P1, P2)`; `## Cost`\n"
    plan = _dev_plan(["dev-log.md"], extra_text)
    parsed = _clean_parsed()

    # Both headings present as full lines → nothing
    failures = []
    gates._gate_dev_log_declared_text(plan, 1, str(tmp_path), parsed, failures, wt_path=str(tmp_path))
    assert failures == [], f"Expected no failures, got: {failures}"

    # ## Cost rewritten to ## Cost (revised) — does NOT satisfy declared ## Cost
    dev_log.write_text(
        "## Pins re-derived (P1, P2)\nSome content\n"
        "## Cost (revised)\nTiming data\n"
    )
    failures2 = []
    gates._gate_dev_log_declared_text(plan, 1, str(tmp_path), parsed, failures2, wt_path=str(tmp_path))
    assert len(failures2) == 1
    assert "## Cost" in failures2[0]["evidence"]


def test_13_196_arm_b(tmp_path):
    """Arm (b): section body must contain normalized pin value; heading/pin errors named."""
    dev_log = tmp_path / "dev-log.md"
    dev_log.write_text(
        "## P10\npopulation: every .md under the trees = 2080 files\n"
        "## Next\nother content\n"
    )

    extra_text = "> **Verbatim:** `## P10` ← P10\n"
    plan = _dev_plan(["dev-log.md"], extra_text)
    parsed = _clean_parsed()

    # Section content matches normalized pin value → nothing
    failures = []
    gates._gate_dev_log_declared_text(plan, 1, str(tmp_path), parsed, failures, wt_path=str(tmp_path))
    assert failures == [], f"Expected nothing, got: {failures}"

    # Paraphrase → FAIL (cell absent)
    dev_log.write_text("## P10\nscans the active plan queue\n## Next\nother\n")
    failures2 = []
    gates._gate_dev_log_declared_text(plan, 1, str(tmp_path), parsed, failures2, wt_path=str(tmp_path))
    assert len(failures2) == 1, f"Expected 1 failure, got: {failures2}"
    assert "cell absent" in failures2[0]["evidence"]

    # Heading missing → FAIL (heading missing)
    dev_log.write_text("## Other\nsome content\n")
    failures3 = []
    gates._gate_dev_log_declared_text(plan, 1, str(tmp_path), parsed, failures3, wt_path=str(tmp_path))
    assert len(failures3) == 1
    assert "heading missing" in failures3[0]["evidence"]

    # Pin row missing (← P999, not in plan) → FAIL (pin row missing)
    plan_p99 = _dev_plan(["dev-log.md"], "> **Verbatim:** `## P10` ← P999\n")
    dev_log.write_text("## P10\npopulation: every .md under the trees = 2080 files\n")
    failures4 = []
    gates._gate_dev_log_declared_text(plan_p99, 1, str(tmp_path), parsed, failures4, wt_path=str(tmp_path))
    assert len(failures4) == 1
    assert "pin row missing" in failures4[0]["evidence"]

    # Escaped \| in pin row value cell — split preserves \| inside the cell
    plan_esc = (
        "# fixture\n\n"
        "| # | pin | value | how |\n"
        "|---|---|---|---|\n"
        + "| P10 | x | pop\\|ulation | - |\n\n"
        + "**Date:** 2026-09-09 | **qa_steps:** 2\n\n"
        "## STEP 1 — DEV\n\n"
        "> **Verbatim:** `## P10` ← P10\n"
        "\n> **Deposits:**\n> - `dev-log.md`\n\n"
        "## STEP 2 — QA\n\n> Nothing.\n"
    )
    dev_log.write_text("## P10\npop\\|ulation\n")
    failures5 = []
    gates._gate_dev_log_declared_text(
        plan_esc, 1, str(tmp_path), parsed, failures5, wt_path=str(tmp_path)
    )
    assert failures5 == [], f"Escaped pipe should match whole: {failures5}"


def test_14_196_adds_nothing(tmp_path):
    """No .md deposit + no declarations → nothing; heading satisfied by any of two deposits."""
    # No deposits, no declarations → nothing
    plan_empty = _dev_plan([])
    parsed = _clean_parsed()
    failures = []
    gates._gate_dev_log_declared_text(plan_empty, 1, str(tmp_path), parsed, failures, wt_path=str(tmp_path))
    assert failures == []

    # Declared heading ## Cost satisfied by dep1, ## Pins by dep2 → both found → nothing
    dep1 = tmp_path / "dep1.md"
    dep1.write_text("## Cost\nContent\n")
    dep2 = tmp_path / "dep2.md"
    dep2.write_text("## Pins\nContent\n")

    extra_text = "> **Headings:** `## Cost`; `## Pins`\n"
    plan = _dev_plan(["dep1.md", "dep2.md"], extra_text)
    failures2 = []
    gates._gate_dev_log_declared_text(plan, 1, str(tmp_path), parsed, failures2, wt_path=str(tmp_path))
    assert failures2 == []


# ---------------------------------------------------------------------------
# Test 15: dispatch order + verdict rows
# ---------------------------------------------------------------------------

def test_15_dispatch_and_rows():
    """gates.check dispatch ends with two new gates; verdict table has two new rows."""
    order = []
    gate_funcs = [
        "_gate_receipt_status",
        "_gate_ceo_flags",
        "_gate_no_errors",
        "_gate_no_permission_denials",
        "_gate_deposit_exists",
        "_gate_is_qa_step",
        "_gate_rule_20_self_check",
        "_gate_rule_22_verification",
        "_gate_qa_test_result",
        "_gate_file_change_audit",
        "_gate_scope_check",
        "_gate_quoted_test_nodes_exist",
        "_gate_mutation_result",
        "_gate_qa_nodes_match_suite",
        "_gate_dev_log_declared_text",
    ]

    wrappers = {}
    for name in gate_funcs:
        orig = getattr(gates, name)

        def _make_wrapper(n, f):
            def wrapper(*args, **kwargs):
                order.append(n)
                return f(*args, **kwargs)
            return wrapper

        wrappers[name] = _make_wrapper(name, orig)

    with patch.multiple("gates", **wrappers):
        result = gates.check(_clean_parsed(), _PLAN_NO_SCOPE, 1, "/tmp")

    expected_order = [
        "_gate_receipt_status",
        "_gate_ceo_flags",
        "_gate_no_errors",
        "_gate_no_permission_denials",
        "_gate_deposit_exists",
        "_gate_is_qa_step",
        "_gate_rule_20_self_check",
        "_gate_rule_22_verification",
        "_gate_qa_test_result",
        "_gate_file_change_audit",
        "_gate_scope_check",
        "_gate_quoted_test_nodes_exist",
        "_gate_mutation_result",
        "_gate_qa_nodes_match_suite",
        "_gate_dev_log_declared_text",
    ]
    assert order == expected_order, (
        f"Dispatch order mismatch:\n  got: {order}\n  want: {expected_order}"
    )

    # Verdict table: PASS rows for the two new gates (immediately after mutation_result)
    table = verdict._build_verification_results_table(result, None, 1, 2)
    assert (
        "| qa_nodes_match_suite | PASS |"
        " Quoted nodes agree with the suite output, or not a QA step |"
    ) in table
    assert (
        "| dev_log_declared_text | PASS |"
        " Declared headings and verbatim cells present, or none declared |"
    ) in table

    # FAIL rows when failures present
    result_fail = dict(result)
    result_fail["failures"] = [
        {"gate": "qa_nodes_match_suite", "evidence": "some mismatch"},
        {"gate": "dev_log_declared_text", "evidence": "heading missing: ## Foo"},
    ]
    table_fail = verdict._build_verification_results_table(result_fail, None, 1, 2)
    assert "| qa_nodes_match_suite | FAIL | some mismatch |" in table_fail
    assert "| dev_log_declared_text | FAIL | heading missing: ## Foo |" in table_fail


# ---------------------------------------------------------------------------
# Test 16: lifecycle rows (file must live under tests/ for conftest autouse redirect)
# ---------------------------------------------------------------------------

def test_16_lifecycle_rows():
    """record_gate_events with no failures writes pass rows for both new gates."""
    pid = lifecycle.mint_and_claim("executable", "/proj", "T", "bellows", "small", 2, "d.md")
    step_id = lifecycle.record_step_start(pid, 2)
    lifecycle.record_gate_events(step_id, {"failures": [], "passed": True})

    conn = sqlite3.connect(lifecycle.LIFECYCLE_DB_PATH)
    rows = conn.execute(
        "SELECT gate_name, result FROM gate_events WHERE step_id = ?", (step_id,)
    ).fetchall()
    conn.close()

    seen = {name: result for name, result in rows}
    assert seen.get("qa_nodes_match_suite") == "pass", (
        f"Expected pass for qa_nodes_match_suite, got: {seen}"
    )
    assert seen.get("dev_log_declared_text") == "pass", (
        f"Expected pass for dev_log_declared_text, got: {seen}"
    )


# ---------------------------------------------------------------------------
# Test 17: _select_summary_txt (Rule 21 tie-breaks)
# ---------------------------------------------------------------------------

def test_17_suite_selection_rule_21(tmp_path):
    """'full' in basename wins; without suite/full, largest passed count wins."""
    targeted = tmp_path / "pytest_targeted.txt"
    targeted.write_text("5 passed in 0.3s\n")
    full = tmp_path / "pytest_full.txt"
    full.write_text("2000 passed in 30.0s\n")

    # 'full' in basename → wins even though targeted is listed first
    path, _, _ = gates._select_summary_txt(
        ["pytest_targeted.txt", "pytest_full.txt"], str(tmp_path)
    )
    assert path == "pytest_full.txt"

    # Neither 'suite' nor 'full': larger passed count wins
    run1 = tmp_path / "run1.txt"
    run1.write_text("5 passed\n")
    run2 = tmp_path / "run2.txt"
    run2.write_text("200 passed\n")
    path2, _, _ = gates._select_summary_txt(["run1.txt", "run2.txt"], str(tmp_path))
    assert path2 == "run2.txt"

    # 'suite' in basename wins over largest count
    suite = tmp_path / "full-suite-results.txt"
    suite.write_text("50 passed\n")
    path3, _, _ = gates._select_summary_txt(
        ["run1.txt", "run2.txt", "full-suite-results.txt"], str(tmp_path)
    )
    assert path3 == "full-suite-results.txt"
