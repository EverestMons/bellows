"""Tests for the five gate arms added/changed by plan 100045.

Tests 1-20 (plus 16 interspersed) — all call gate functions directly with a
failures list; no real corpus is read; all I/O uses tmp_path.
"""
import os
import sys
from unittest.mock import patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import gates
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


# PLAN_TEXT from test_gates.py — no Scope block; gates.py / verdict.py authorized by prose.
PLAN_TEXT_NO_SCOPE = """# bellows — executable: fixture

**Date:** 2026-09-06 | **Project:** bellows | **qa_steps:** 2 | **Execution:** Step 1

## STEP 1 — DEV (Developer)

> Build gates.py and verdict.py in the bellows root directory.

## STEP 2 — QA (QA Engineer)

> Run all tests and verify deliverables.
"""


# ---------------------------------------------------------------------------
# Tests 1–4: _gate_scope_check (191)
# ---------------------------------------------------------------------------

def test_1_declared_scope_prose_mention_fails():
    """Declared Scope + file mentioned only in prose → FAIL."""
    plan = """# plan
**Date:** 2026-09-08 | **Project:** bellows | **qa_steps:** none

## STEP 1 — DEV

> **Scope:**
> - `gates.py`
> - `verdict.py`
> - `scripts/cycle_check.py`
> - `scripts/substrate_check.py`
> - `tests/test_cycle_check_battery.py`
> - `tests/test_cycle_check_manifest_provenance.py`
>
> MUST NOT change tests/test_cycle_check.py.
"""
    failures = []
    gates._gate_scope_check(plan, 1, [
        "gates.py",
        "verdict.py",
        "scripts/cycle_check.py",
        "scripts/substrate_check.py",
        "tests/test_cycle_check_battery.py",
        "tests/test_cycle_check_manifest_provenance.py",
        "tests/test_cycle_check.py",
    ], failures)
    assert any("tests/test_cycle_check.py" in f["evidence"] for f in failures), \
        f"Expected failure for tests/test_cycle_check.py, got: {failures}"


def test_2_declared_scope_all_declared_passes():
    """Declared Scope + all changed files declared → passes."""
    plan = """# plan
**Date:** 2026-09-08 | **Project:** bellows | **qa_steps:** none

## STEP 1 — DEV

> **Scope:**
> - `gates.py`
> - `verdict.py`
> - `scripts/cycle_check.py`
> - `scripts/substrate_check.py`
> - `tests/test_cycle_check.py`
> - `tests/test_cycle_check_battery.py`
> - `tests/test_cycle_check_manifest_provenance.py`
"""
    failures = []
    gates._gate_scope_check(plan, 1, [
        "gates.py",
        "verdict.py",
        "scripts/cycle_check.py",
        "scripts/substrate_check.py",
        "tests/test_cycle_check.py",
        "tests/test_cycle_check_battery.py",
        "tests/test_cycle_check_manifest_provenance.py",
    ], failures)
    assert failures == []


def test_3_no_scope_block_prose_authorizes_passes():
    """No Scope block + prose authorizes gates.py / verdict.py → passes.

    A Deposits block alone (no Scope block) must NOT trigger declared-mode (P3, f25).
    """
    # Deposits inside STEP 1 but no Scope block → prose arms still apply
    plan_with_deposits_no_scope = """# plan
**Date:** 2026-09-06 | **Project:** bellows | **qa_steps:** none

## STEP 1 — DEV

> Build gates.py and verdict.py in the bellows root directory.
>
> **Deposits:**
> - `knowledge/qa/evidence/report.md`
"""
    failures = []
    gates._gate_scope_check(plan_with_deposits_no_scope, 1, ["gates.py", "verdict.py"], failures)
    assert failures == [], f"Deposits-only plan must use prose arms, got: {failures}"

    # Ancestor-directory mention also passes (no Scope block)
    plan_dir = """# plan
**Date:** 2026-09-08 | **Project:** bellows | **qa_steps:** none

## STEP 1 — DEV

> Write files into knowledge/qa/evidence/myslug/ directory.
"""
    failures2 = []
    gates._gate_scope_check(plan_dir, 1, ["knowledge/qa/evidence/myslug/report.md"], failures2)
    assert failures2 == []


def test_4_scope_matching_rules():
    """Verify exact match, one-segment tolerance, basename arm gone, Deposits, prefixes, lifecycle."""
    # (a) basename arm gone: declared tests/test_x.py does NOT authorize other/test_x.py
    plan_a = """# plan
**Date:** 2026-09-08 | **Project:** bellows | **qa_steps:** none

## STEP 1 — DEV

> **Scope:**
> - `tests/test_x.py`
"""
    failures = []
    gates._gate_scope_check(plan_a, 1, ["other/test_x.py"], failures)
    assert any("other/test_x.py" in f["evidence"] for f in failures)

    # (b) basename arm gone: scratch/old/tests/test_x.py also fails
    failures2 = []
    gates._gate_scope_check(plan_a, 1, ["scratch/old/tests/test_x.py"], failures2)
    assert any("scratch/old/tests/test_x.py" in f["evidence"] for f in failures2)

    # (c) one-segment declared: bellows/tests/test_x.py DOES authorize tests/test_x.py
    plan_c = """# plan
**Date:** 2026-09-08 | **Project:** bellows | **qa_steps:** none

## STEP 1 — DEV

> **Scope:**
> - `bellows/tests/test_x.py`
"""
    failures3 = []
    gates._gate_scope_check(plan_c, 1, ["tests/test_x.py"], failures3)
    assert failures3 == []

    # (d) declared tests/fixtures/x.py does NOT authorize x.py (no float on changed side)
    plan_d = """# plan
**Date:** 2026-09-08 | **Project:** bellows | **qa_steps:** none

## STEP 1 — DEV

> **Scope:**
> - `tests/fixtures/x.py`
"""
    failures4 = []
    gates._gate_scope_check(plan_d, 1, ["x.py"], failures4)
    assert any("x.py" in f["evidence"] for f in failures4)

    # (e) declared root gates.py does NOT authorize tests/fixtures/gates.py
    plan_e = """# plan
**Date:** 2026-09-08 | **Project:** bellows | **qa_steps:** none

## STEP 1 — DEV

> **Scope:**
> - `gates.py`
"""
    failures5 = []
    gates._gate_scope_check(plan_e, 1, ["tests/fixtures/gates.py"], failures5)
    assert any("tests/fixtures/gates.py" in f["evidence"] for f in failures5)

    # (f) path listed only in Deposits block is authorized
    plan_f = """# plan
**Date:** 2026-09-08 | **Project:** bellows | **qa_steps:** none

## STEP 1 — DEV

> **Scope:**
> - `gates.py`
>
> **Deposits:**
> - `knowledge/qa/evidence/report.md`
"""
    failures6 = []
    gates._gate_scope_check(plan_f, 1, ["gates.py", "knowledge/qa/evidence/report.md"], failures6)
    assert failures6 == []

    # (g) Deposits entry ending / authorizes its children
    plan_g = """# plan
**Date:** 2026-09-08 | **Project:** bellows | **qa_steps:** none

## STEP 1 — DEV

> **Scope:**
> - `gates.py`
>
> **Deposits:**
> - `knowledge/qa/evidence/myslug/`
"""
    failures7 = []
    gates._gate_scope_check(plan_g, 1, [
        "gates.py",
        "knowledge/qa/evidence/myslug/suite.txt",
        "knowledge/qa/evidence/myslug/report.md",
    ], failures7)
    assert failures7 == []

    # (h) declared prefix bellows/knowledge/qa/evidence/s/ authorizes knowledge/qa/evidence/s/full-suite.txt
    plan_h = """# plan
**Date:** 2026-09-08 | **Project:** bellows | **qa_steps:** none

## STEP 1 — DEV

> **Scope:**
> - `bellows/knowledge/qa/evidence/s/`
"""
    failures8 = []
    gates._gate_scope_check(plan_h, 1, ["knowledge/qa/evidence/s/full-suite.txt"], failures8)
    assert failures8 == []

    # (i) lifecycle-file prefixes stay allowlisted
    plan_i = """# plan
**Date:** 2026-09-08 | **Project:** bellows | **qa_steps:** none

## STEP 1 — DEV

> **Scope:**
> - `gates.py`
"""
    failures9 = []
    gates._gate_scope_check(plan_i, 1, [
        "gates.py",
        "in-progress-bellows-100045.md",
        "hold-bellows-100045.md",
    ], failures9)
    assert failures9 == []


# ---------------------------------------------------------------------------
# Tests 5–7: _gate_qa_test_result (43)
# ---------------------------------------------------------------------------

def _qa_plan_with_txt_deposits(paths):
    """Plan fixture: QA step with given .txt deposits."""
    deposits = "\n".join(f"> - `{p}`" for p in paths)
    return f"""# plan
**Date:** 2026-09-08 | **Project:** bellows | **qa_steps:** 2 | **Execution:** Step 2

## STEP 1 — DEV

> Nothing here.

## STEP 2 — QA

> **Deposits:**
{deposits}
"""


def test_5_qa_test_result_probe_first_suite_second_reads_suite(tmp_path):
    """Two .txt deposits (probe first, suite second), neither named full-suite → gate reads SUITE."""
    # probe has no pytest summary; suite does
    probe = tmp_path / "probes-raw.txt"
    probe.write_text("Some probe output\nno summary line here\n")
    suite = tmp_path / "pytest-results.txt"
    suite.write_text("==== test session ====\n10 passed in 1.23s\n")

    plan = _qa_plan_with_txt_deposits(["probes-raw.txt", "pytest-results.txt"])
    parsed = _clean_parsed()
    failures = []
    gates._gate_qa_test_result(True, plan, 2, str(tmp_path), parsed, failures, wt_path=str(tmp_path))
    assert failures == [], f"Expected PASS, got: {failures}"


def test_6_qa_test_result_suite_basename_wins(tmp_path):
    """Multiple summary-bearing .txt files → the one with 'suite' in basename wins.

    other-results.txt has a failure; full-suite-results.txt is clean.
    The 'suite' tie-break must pick the suite file or the gate fires on the failure.
    """
    other = tmp_path / "other-results.txt"
    other.write_text("1 failed, 4 passed in 0.5s\n")  # has a failure
    suite = tmp_path / "full-suite-results.txt"
    suite.write_text("100 passed in 5.0s\n")

    plan = _qa_plan_with_txt_deposits(["other-results.txt", "full-suite-results.txt"])
    parsed = _clean_parsed()
    failures = []
    gates._gate_qa_test_result(True, plan, 2, str(tmp_path), parsed, failures, wt_path=str(tmp_path))
    assert failures == [], f"Expected PASS reading suite file, got: {failures}"


def test_7_qa_test_result_no_summary_fails(tmp_path):
    """No .txt carries a pytest summary → FAIL naming every .txt inspected."""
    f1 = tmp_path / "probes-raw.txt"
    f1.write_text("Some random output, no summary line.\n")
    f2 = tmp_path / "doc-integrity.txt"
    f2.write_text("Another file, no passed line.\n")

    plan = _qa_plan_with_txt_deposits(["probes-raw.txt", "doc-integrity.txt"])
    parsed = _clean_parsed()
    failures = []
    gates._gate_qa_test_result(True, plan, 2, str(tmp_path), parsed, failures, wt_path=str(tmp_path))
    assert len(failures) == 1
    assert failures[0]["gate"] == "qa_test_result"
    assert "probes-raw.txt" in failures[0]["evidence"]
    assert "doc-integrity.txt" in failures[0]["evidence"]


# ---------------------------------------------------------------------------
# Tests 8–10: _gate_quoted_test_nodes_exist (65)
# ---------------------------------------------------------------------------

def _qa_plan_with_md_deposit(path):
    return f"""# plan
**Date:** 2026-09-08 | **Project:** bellows | **qa_steps:** 2 | **Execution:** Step 2

## STEP 1 — DEV

> Nothing here.

## STEP 2 — QA

> **Deposits:**
> - `{path}`
"""


def test_8_quoted_node_missing_fails(tmp_path):
    """QA receipt quoting a node not in the test file → FAIL listing the node."""
    test_file = tmp_path / "tests" / "test_decisions.py"
    test_file.parent.mkdir(parents=True)
    test_file.write_text("class TestLoadPhrases:\n    def test_other(self):\n        pass\n")

    receipt = tmp_path / "qa-report.md"
    receipt.write_text(
        "## QA Report\n\n"
        "Verified `tests/test_decisions.py::TestLoadPhrases::test_loads_slash_alternatives`.\n"
    )

    plan = _qa_plan_with_md_deposit("qa-report.md")
    parsed = _clean_parsed()
    failures = []
    gates._gate_quoted_test_nodes_exist(
        True, plan, 2, str(tmp_path), parsed, failures, wt_path=str(tmp_path)
    )
    assert len(failures) == 1
    assert failures[0]["gate"] == "quoted_test_nodes_exist"
    assert "test_loads_slash_alternatives" in failures[0]["evidence"]


def test_9_quoted_nodes_all_exist_passes(tmp_path):
    """Quoted nodes (function, class, class::method, parametrised) all exist → passes."""
    test_file = tmp_path / "tests" / "test_example.py"
    test_file.parent.mkdir(parents=True)
    test_file.write_text(
        "def test_simple():\n    pass\n\n"
        "class TestGroup:\n"
        "    def test_method(self):\n        pass\n"
    )

    receipt = tmp_path / "qa-report.md"
    receipt.write_text(
        "## QA Report\n\n"
        "Verified:\n"
        "- `tests/test_example.py::test_simple`\n"
        "- `tests/test_example.py::TestGroup::test_method`\n"
        "- `tests/test_example.py::test_simple[param1]`\n"
    )

    plan = _qa_plan_with_md_deposit("qa-report.md")
    parsed = _clean_parsed()
    failures = []
    gates._gate_quoted_test_nodes_exist(
        True, plan, 2, str(tmp_path), parsed, failures, wt_path=str(tmp_path)
    )
    assert failures == []


def test_10_no_test_node_quoted_passes(tmp_path):
    """Receipt with no test node quotations → passes."""
    receipt = tmp_path / "qa-report.md"
    receipt.write_text(
        "## QA Report\n\n"
        "All checks passed. No specific test nodes quoted.\n"
    )

    plan = _qa_plan_with_md_deposit("qa-report.md")
    parsed = _clean_parsed()
    failures = []
    gates._gate_quoted_test_nodes_exist(
        True, plan, 2, str(tmp_path), parsed, failures, wt_path=str(tmp_path)
    )
    assert failures == []


# ---------------------------------------------------------------------------
# Tests 11–12: _gate_rule_22_verification (d) — LESSONS marker not a hedge (136)
# ---------------------------------------------------------------------------

def _qa_plan_with_qa_md(qa_path):
    return f"""# plan
**Date:** 2026-09-08 | **Project:** bellows | **qa_steps:** 2 | **Execution:** Step 2

## STEP 1 — DEV

> Nothing here.

## STEP 2 — QA

> **Deposits:**
> - `{qa_path}`
"""


def _write_verification_table(path, rows):
    """Write a QA report with a Verification section containing the given table rows."""
    header = "| Step | Status | Detail |\n|---|---|---|\n"
    content = "## Verification\n\n" + header + "\n".join(rows) + "\n"
    path.write_text(content)


def test_11_marker_form_pending_not_a_hedge(tmp_path):
    """✅ row whose status cell reads '[status: pending] written' → (d) does NOT fire."""
    qa = tmp_path / "qa-report.md"
    _write_verification_table(qa, [
        "| write marker | ✅ marker `[status: pending]` written | detail |",
    ])

    plan = _qa_plan_with_qa_md("qa-report.md")
    parsed = _clean_parsed()
    failures = []
    gates._gate_rule_22_verification(
        True, plan, 2, str(tmp_path), parsed, failures, wt_path=str(tmp_path)
    )
    rule22_d = [f for f in failures if f.get("gate") == "rule_22_verification" and "(d)" in f.get("evidence", "")]
    assert rule22_d == [], f"(d) should NOT fire on marker form, got: {rule22_d}"


def test_12_bare_word_pending_fires_and_detail_cell_is_silent(tmp_path):
    """✅ row whose status cell has bare 'pending' → (d) fires;
    same two rows with token in Detail cell → (d) silent both times."""
    # Case 1: bare word in status-bearing cell → fires
    qa_fires = tmp_path / "qa-fires.md"
    _write_verification_table(qa_fires, [
        "| tests | ✅ tests pending | detail |",
    ])
    plan1 = _qa_plan_with_qa_md("qa-fires.md")
    parsed = _clean_parsed()
    failures1 = []
    gates._gate_rule_22_verification(
        True, plan1, 2, str(tmp_path), parsed, failures1, wt_path=str(tmp_path)
    )
    d_failures = [f for f in failures1 if "(d)" in f.get("evidence", "")]
    assert d_failures, f"(d) should fire on bare 'pending' in status cell, got: {failures1}"

    # Case 2: marker form in Detail cell → silent
    qa_detail_marker = tmp_path / "qa-detail-marker.md"
    _write_verification_table(qa_detail_marker, [
        "| write marker | ✅ | marker [status: pending] written |",
    ])
    plan2 = _qa_plan_with_qa_md("qa-detail-marker.md")
    failures2 = []
    gates._gate_rule_22_verification(
        True, plan2, 2, str(tmp_path), parsed, failures2, wt_path=str(tmp_path)
    )
    d2 = [f for f in failures2 if "(d)" in f.get("evidence", "")]
    assert d2 == [], f"(d) should be silent when token is in Detail cell (marker form), got: {d2}"

    # Case 3: bare word in Detail cell → silent
    qa_detail_bare = tmp_path / "qa-detail-bare.md"
    _write_verification_table(qa_detail_bare, [
        "| tests | ✅ | tests pending |",
    ])
    plan3 = _qa_plan_with_qa_md("qa-detail-bare.md")
    failures3 = []
    gates._gate_rule_22_verification(
        True, plan3, 2, str(tmp_path), parsed, failures3, wt_path=str(tmp_path)
    )
    d3 = [f for f in failures3 if "(d)" in f.get("evidence", "")]
    assert d3 == [], f"(d) should be silent when token is in Detail cell (bare), got: {d3}"


# ---------------------------------------------------------------------------
# Tests 13–15: _gate_mutation_result (192)
# ---------------------------------------------------------------------------

def _plan_with_run_deposit(run_path, json_path=None, use_scope_json=False):
    """Plan with a .run.txt deposit; optionally also declares a .json."""
    scope = ""
    if use_scope_json and json_path:
        scope = f"\n> **Scope:**\n> - `{json_path}`\n"
    dep_json = f"\n> - `{json_path}`" if json_path and not use_scope_json else ""
    return f"""# plan
**Date:** 2026-09-08 | **Project:** bellows | **qa_steps:** none

## STEP 1 — DEV

>{scope}
> **Deposits:**
> - `{run_path}`{dep_json}
"""


def test_13_mutation_result_pass_and_fail(tmp_path):
    """Run .txt variations: clean passes; survivor or error fails; no MUTATION: fails."""
    run = tmp_path / "knowledge" / "mutants" / "x.run.txt"
    run.parent.mkdir(parents=True)

    # Clean (12 killed, 0 survived, 0 error) → passes
    run.write_text("MUTATION: 12 killed, 0 survived, 0 error\n")
    plan = _plan_with_run_deposit("knowledge/mutants/x.run.txt")
    failures = []
    gates._gate_mutation_result(plan, 1, str(tmp_path), _clean_parsed(), failures, wt_path=str(tmp_path))
    assert failures == []

    # Survivor → FAIL
    run.write_text("MUTATION: 12 killed, 1 survived, 0 error\n")
    failures2 = []
    gates._gate_mutation_result(plan, 1, str(tmp_path), _clean_parsed(), failures2, wt_path=str(tmp_path))
    assert any("survived" in f["evidence"] for f in failures2)

    # Error → FAIL
    run.write_text("MUTATION: 0 killed, 0 survived, 9 error\n")
    failures3 = []
    gates._gate_mutation_result(plan, 1, str(tmp_path), _clean_parsed(), failures3, wt_path=str(tmp_path))
    assert any("9 error" in f["evidence"] for f in failures3)

    # No MUTATION: line → FAIL
    run.write_text("Some output but no mutation line.\n")
    failures4 = []
    gates._gate_mutation_result(plan, 1, str(tmp_path), _clean_parsed(), failures4, wt_path=str(tmp_path))
    assert any("no MUTATION" in f["evidence"].lower() or "MUTATION:" in f["evidence"] for f in failures4)


def test_14_manifest_without_run_fails(tmp_path):
    """Scope (or Deposits) names .json but no .run.txt deposit → FAIL."""
    run_dir = tmp_path / "knowledge" / "mutants"
    run_dir.mkdir(parents=True)
    json_file = run_dir / "x.json"
    json_file.write_text('{"target": "gates.py", "mutants": []}')

    # Case 1: .json in Scope, no .run.txt in deposits
    plan_scope = f"""# plan
**Date:** 2026-09-08 | **Project:** bellows | **qa_steps:** none

## STEP 1 — DEV

> **Scope:**
> - `knowledge/mutants/x.json`
>
> **Deposits:**
> - `knowledge/development/dev-log.md`
"""
    dev_log = tmp_path / "knowledge" / "development" / "dev-log.md"
    dev_log.parent.mkdir(parents=True)
    dev_log.write_text("# dev log\n")
    failures = []
    gates._gate_mutation_result(
        plan_scope, 1, str(tmp_path), _clean_parsed(), failures, wt_path=str(tmp_path)
    )
    assert any("manifest" in f["evidence"].lower() or "run" in f["evidence"].lower() for f in failures), \
        f"Expected manifest-without-run failure, got: {failures}"

    # Case 2: .json in Deposits block only (C15), no .run.txt
    plan_dep = f"""# plan
**Date:** 2026-09-08 | **Project:** bellows | **qa_steps:** none

## STEP 1 — DEV

> **Deposits:**
> - `knowledge/mutants/x.json`
> - `knowledge/development/dev-log.md`
"""
    failures2 = []
    gates._gate_mutation_result(
        plan_dep, 1, str(tmp_path), _clean_parsed(), failures2, wt_path=str(tmp_path)
    )
    assert any("manifest" in f["evidence"].lower() or "run" in f["evidence"].lower() for f in failures2), \
        f"Expected manifest-without-run failure (Deposits-only case), got: {failures2}"


def test_15_no_mutant_files_gate_adds_nothing(tmp_path):
    """Step declaring no mutant files → 192 gate adds nothing."""
    plan = """# plan
**Date:** 2026-09-08 | **Project:** bellows | **qa_steps:** none

## STEP 1 — DEV

> **Deposits:**
> - `knowledge/development/dev-log.md`
"""
    dev_log = tmp_path / "knowledge" / "development" / "dev-log.md"
    dev_log.parent.mkdir(parents=True)
    dev_log.write_text("# dev log\n")
    failures = []
    gates._gate_mutation_result(
        plan, 1, str(tmp_path), _clean_parsed(), failures, wt_path=str(tmp_path)
    )
    assert failures == []


# ---------------------------------------------------------------------------
# Test 16: dispatch order + verdict table
# ---------------------------------------------------------------------------

def test_16_dispatch_order_and_verdict_table():
    """gates.check dispatch order unchanged; verdict table has the three new rows."""
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
        result = gates.check(_clean_parsed(), PLAN_TEXT_NO_SCOPE, 1, "/tmp")

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
    ]
    assert order == expected_order, f"Dispatch order mismatch:\n  got: {order}\n  want: {expected_order}"

    # Verdict table — PASS rows for the three new gates
    table_clean = verdict._build_verification_results_table(result, None, 1, 2)

    # Pre-existing rows byte-identical to pre-change capture
    pre_existing_rows = [
        "| receipt_status | PASS | Status: Complete |",
        "| ceo_flags | PASS | No flags raised by agent |",
        "| errors | PASS | No errors reported in step output |",
        "| permission_denials | PASS | No blocking permission denials |",
        "| deposit_exists | PASS | All agent-declared deposits present on disk |",
        "| qa_step_detection | PASS | Not a QA step |",
        "| file_change_audit | PASS | 0 files modified |",
        "| scope_check | PASS | All changes within plan scope |",
        "| rule_20_self_check | PASS | N/A (not a QA step) |",
        "| rule_22_verification | PASS | Plan-declared deposits present on disk |",
    ]
    for row in pre_existing_rows:
        assert row in table_clean, f"Pre-existing row missing: {row!r}"

    # New PASS rows
    assert "| qa_test_result | PASS | pytest summary clean, or not a QA step |" in table_clean
    assert "| quoted_test_nodes_exist | PASS | Every quoted test node exists in the worktree |" in table_clean
    assert "| mutation_result | PASS | Mutation run clean, or none declared |" in table_clean

    # FAIL rows when failures present
    result_with_fails = dict(result)
    result_with_fails["failures"] = [
        {"gate": "qa_test_result", "evidence": "no summary in any .txt"},
        {"gate": "quoted_test_nodes_exist", "evidence": "test_foo not found"},
        {"gate": "mutation_result", "evidence": "1 survived"},
    ]
    table_fail = verdict._build_verification_results_table(result_with_fails, None, 1, 2)
    assert "| qa_test_result | FAIL | no summary in any .txt |" in table_fail
    assert "| quoted_test_nodes_exist | FAIL | test_foo not found |" in table_fail
    assert "| mutation_result | FAIL | 1 survived |" in table_fail


# ---------------------------------------------------------------------------
# Test 17: 65 on DEV step / two missing nodes
# ---------------------------------------------------------------------------

def test_17_dev_step_adds_nothing_and_two_missing_nodes_one_failure(tmp_path):
    """65 on DEV step → adds nothing; QA receipt quoting TWO missing nodes → one failure listing both."""
    test_file = tmp_path / "tests" / "test_foo.py"
    test_file.parent.mkdir(parents=True)
    test_file.write_text("def test_real():\n    pass\n")

    receipt = tmp_path / "qa-report.md"
    receipt.write_text(
        "## QA Report\n\n"
        "- `tests/test_foo.py::test_missing_one`\n"
        "- `tests/test_foo.py::test_missing_two`\n"
    )

    plan = _qa_plan_with_md_deposit("qa-report.md")

    # DEV step: adds nothing
    parsed = _clean_parsed()
    failures_dev = []
    gates._gate_quoted_test_nodes_exist(
        False, plan, 2, str(tmp_path), parsed, failures_dev, wt_path=str(tmp_path)
    )
    assert failures_dev == []

    # QA step: one failure listing both missing nodes
    failures_qa = []
    gates._gate_quoted_test_nodes_exist(
        True, plan, 2, str(tmp_path), parsed, failures_qa, wt_path=str(tmp_path)
    )
    assert len(failures_qa) == 1
    assert failures_qa[0]["gate"] == "quoted_test_nodes_exist"
    assert "test_missing_one" in failures_qa[0]["evidence"]
    assert "test_missing_two" in failures_qa[0]["evidence"]


# ---------------------------------------------------------------------------
# Test 18: mutation result — N≥1 and last MUTATION: line
# ---------------------------------------------------------------------------

def test_18_mutation_n_ge_1_and_last_line_read(tmp_path):
    """0/0/0 kills → FAIL (N≥1); two MUTATION: lines with trailing \\r → LAST one is read."""
    run = tmp_path / "knowledge" / "mutants" / "x.run.txt"
    run.parent.mkdir(parents=True)

    # 0 killed → FAIL
    run.write_text("MUTATION: 0 killed, 0 survived, 0 error\n")
    plan = _plan_with_run_deposit("knowledge/mutants/x.run.txt")
    failures = []
    gates._gate_mutation_result(plan, 1, str(tmp_path), _clean_parsed(), failures, wt_path=str(tmp_path))
    assert any(f["gate"] == "mutation_result" for f in failures), \
        f"Expected FAIL for 0 killed: {failures}"

    # Two MUTATION: lines, trailing \r, LAST one is read (5 killed → passes)
    run.write_bytes(
        b"MUTATION: 0 killed, 0 survived, 9 error\r\n"
        b"MUTATION: 5 killed, 0 survived, 0 error\r\n"
    )
    failures2 = []
    gates._gate_mutation_result(plan, 1, str(tmp_path), _clean_parsed(), failures2, wt_path=str(tmp_path))
    assert failures2 == [], f"Expected PASS reading last line: {failures2}"


# ---------------------------------------------------------------------------
# Test 19: absolute-entry normalization (P14)
# ---------------------------------------------------------------------------

def test_19_absolute_entry_normalization(tmp_path):
    """/<project_path>/tuyere/claims.py authorizes tuyere/claims.py (normalized);
    absolute entry outside project_path authorizes nothing."""
    project_path = str(tmp_path)

    plan_absolute = f"""# plan
**Date:** 2026-09-08 | **Project:** bellows | **qa_steps:** none

## STEP 1 — DEV

> **Scope:**
> - `{project_path}/tuyere/claims.py`
"""
    # Absolute entry under project_path → normalizes to tuyere/claims.py → passes
    failures = []
    gates._gate_scope_check(plan_absolute, 1, ["tuyere/claims.py"], failures, project_path=project_path)
    assert failures == [], f"Expected PASS after normalization, got: {failures}"

    # Absolute entry outside project_path → authorizes nothing
    plan_outside = f"""# plan
**Date:** 2026-09-08 | **Project:** bellows | **qa_steps:** none

## STEP 1 — DEV

> **Scope:**
> - `/some/other/repo/claims.py`
"""
    failures2 = []
    gates._gate_scope_check(plan_outside, 1, ["claims.py"], failures2, project_path=project_path)
    assert any("claims.py" in f["evidence"] for f in failures2), \
        f"Expected FAIL for outside-project absolute entry, got: {failures2}"


# ---------------------------------------------------------------------------
# Test 20: prefix tolerance on declared side only (C1)
# ---------------------------------------------------------------------------

def test_20_prefix_tolerance_declared_side_only():
    """Declared prefix bellows/knowledge/qa/evidence/s/ authorizes knowledge/qa/evidence/s/full-suite.txt;
    declared prefix knowledge/ does NOT authorize docs/knowledge/x."""
    plan_ok = """# plan
**Date:** 2026-09-08 | **Project:** bellows | **qa_steps:** none

## STEP 1 — DEV

> **Scope:**
> - `bellows/knowledge/qa/evidence/s/`
"""
    failures = []
    gates._gate_scope_check(plan_ok, 1, ["knowledge/qa/evidence/s/full-suite.txt"], failures)
    assert failures == [], f"Expected PASS with one-segment prefix tolerance: {failures}"

    # knowledge/ prefix does NOT authorize docs/knowledge/x (prefix tolerance on declared side only)
    plan_no = """# plan
**Date:** 2026-09-08 | **Project:** bellows | **qa_steps:** none

## STEP 1 — DEV

> **Scope:**
> - `knowledge/`
"""
    failures2 = []
    gates._gate_scope_check(plan_no, 1, ["docs/knowledge/x"], failures2)
    assert any("docs/knowledge/x" in f["evidence"] for f in failures2), \
        f"Expected FAIL: prefix tolerance is declared-side only, got: {failures2}"
