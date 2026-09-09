"""coverage_verdict — tests for the new fold-coverage reconciliation (thread 215, plan 100053).

Plans and registers are built as strings under tmp_path. The register lives in a
`governance/knowledge/research/` subtree; the plan lives at the `Draft:` path so the
resolution walks up from the register's directory and finds it under tmp_path.

Run after Item 5's commit and manifest A's run. Tests 1–9 and 11–12 are RED until Item 6;
test 10 is GREEN by construction (the literal is captured before Item 6).
"""
import subprocess
import sys
from pathlib import Path

import pytest

BELLOWS_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BELLOWS_ROOT / "scripts"))
sys.path.insert(0, str(BELLOWS_ROOT / "tools"))

import walk_register_lint as wrl  # noqa: E402

_SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "walk_register_lint.py"

# ---------------------------------------------------------------------------
# Fixtures and helpers
# ---------------------------------------------------------------------------

FOLD_HDR = (
    "| id | walk | lens | sub_question | origin | finding | pre_fold_text | resolution |\n"
    "|---|---|---|---|---|---|---|---|\n"
)

SCHEMA_DECL = "**schema_version:** `0.3`\n\n"


def _row(row_id, walk):
    return (
        f"| {row_id} | {walk} | weak spots | q | o | finding {row_id} | pre | res |\n"
    )


def _plan_text(lens_lines):
    """A minimal plan body with a Drafting Cycle block and the given lens lines."""
    body = "\n".join(f"- {l}" for l in lens_lines)
    return (
        "# test plan\n\n"
        "## Drafting Cycle\n\n"
        f"{body}\n\n"
        "## STEP 1\n"
    )


def _setup(tmp_path, plan_text, reg_text, reg_name="walk-register-test.md"):
    """Create plan + register in the standard layout and return (reg_text, reg_path)."""
    # Plan at tmp_path/knowledge/decisions/drafts/test-plan.md
    plan_dir = tmp_path / "knowledge" / "decisions" / "drafts"
    plan_dir.mkdir(parents=True, exist_ok=True)
    plan_path = plan_dir / "test-plan.md"
    plan_path.write_text(plan_text, encoding="utf-8")

    # Register at tmp_path/governance/knowledge/research/<name>
    reg_dir = tmp_path / "governance" / "knowledge" / "research"
    reg_dir.mkdir(parents=True, exist_ok=True)
    reg_path = reg_dir / reg_name
    reg_path.write_text(reg_text, encoding="utf-8")

    return reg_path, plan_path


def _draft_line(path="knowledge/decisions/drafts/test-plan.md"):
    return f"Draft: `{path}`\n\n"


def _reg(rows_text, *, schema=True, draft_line=True):
    """Minimal register content: optional schema decl, draft line, fold table, rows."""
    parts = []
    if schema:
        parts.append(SCHEMA_DECL)
    if draft_line:
        parts.append(_draft_line())
    parts.append(FOLD_HDR)
    parts.append(rows_text)
    return "".join(parts)


# ---------------------------------------------------------------------------
# Test 1 — COVERED: rows ≥ declared on every completed walk
# ---------------------------------------------------------------------------

def test_covered_basic(tmp_path):
    """w1 3 declared, 3 rows; w2 1 declared, 1 row; w3 (highest) in progress."""
    plan = _plan_text([
        "Weak spots: w1 3 folded — instruction 3 / record 0.",
        "Weak spots: w2 1 folded — instruction 1 / record 0.",
        "Weak spots: w3 dry.",
    ])
    rows = _row("f1", 1) + _row("f2", 1) + _row("f3", 1) + _row("f4", 2)
    reg_path, _ = _setup(tmp_path, plan, _reg(rows))

    token, detail = wrl.coverage_verdict(reg_path.read_text(), reg_path)
    assert token == "COVERED", (token, detail)
    assert "w1 3/3" in detail
    assert "w2 1/1" in detail
    assert "w3 in progress" in detail


# ---------------------------------------------------------------------------
# Test 2 — INCOMPLETE: w1 rows < declared
# ---------------------------------------------------------------------------

def test_incomplete(tmp_path):
    """Same plan; only 2 w1 rows against declared 3 → INCOMPLETE for w1."""
    plan = _plan_text([
        "Weak spots: w1 3 folded — instruction 3 / record 0.",
        "Weak spots: w2 1 folded — instruction 1 / record 0.",
        "Weak spots: w3 dry.",
    ])
    rows = _row("f1", 1) + _row("f2", 1) + _row("f4", 2)
    reg_path, _ = _setup(tmp_path, plan, _reg(rows))

    token, detail = wrl.coverage_verdict(reg_path.read_text(), reg_path)
    assert token == "INCOMPLETE", (token, detail)
    assert "w1 rows=2 declared=3" in detail
    # w2 is covered (1/1) — must not appear in the INCOMPLETE message
    assert "w2" not in detail


# ---------------------------------------------------------------------------
# Test 3 — rows exceed declared is still COVERED
# ---------------------------------------------------------------------------

def test_rows_exceed_declared_is_covered(tmp_path):
    """4 rows for w1 against declared 3 → COVERED, detail shows 4/3."""
    plan = _plan_text([
        "Weak spots: w1 3 folded — instruction 3 / record 0.",
        "Weak spots: w2 dry.",
    ])
    rows = _row("f1", 1) + _row("f2", 1) + _row("f3", 1) + _row("f4", 1)
    reg_path, _ = _setup(tmp_path, plan, _reg(rows))

    token, detail = wrl.coverage_verdict(reg_path.read_text(), reg_path)
    assert token == "COVERED", (token, detail)
    assert "w1 4/3" in detail


# ---------------------------------------------------------------------------
# Test 4 — panel and walk-0 rows counted, not reconciled
# ---------------------------------------------------------------------------

def test_panel_and_walk0_rows_counted_not_reconciled(tmp_path):
    """panel-1, panel-2, and walk-0 rows are tallied in the detail, never judged."""
    plan = _plan_text([
        "Weak spots: w1 3 folded — instruction 3 / record 0.",
        "Weak spots: w2 dry.",
    ])
    walk_rows = _row("f1", 1) + _row("f2", 1) + _row("f3", 1)
    panel_rows = (
        "| p1 | panel-1 | weak spots | q | o | panel finding 1 | pre | res |\n"
        "| p2 | panel-2 | weak spots | q | o | panel finding 2 | pre | res |\n"
        "| w0 | 0 | weak spots | q | o | walk-0 finding | pre | res |\n"
    )
    reg_path, _ = _setup(tmp_path, plan, _reg(walk_rows + panel_rows))

    token, detail = wrl.coverage_verdict(reg_path.read_text(), reg_path)
    assert token == "COVERED", (token, detail)
    assert "panel rows 2" in detail
    assert "walk-0 rows 1" in detail


# ---------------------------------------------------------------------------
# Test 5 — --plan overrides the Draft: line
# ---------------------------------------------------------------------------

def test_plan_arg_overrides_draft_line(tmp_path):
    """A register whose Draft: is unresolvable — but --plan points to a valid plan."""
    plan_text = _plan_text([
        "Weak spots: w1 3 folded — instruction 3 / record 0.",
        "Weak spots: w2 dry.",
    ])
    plan_dir = tmp_path / "plans"
    plan_dir.mkdir()
    explicit_plan = plan_dir / "my-plan.md"
    explicit_plan.write_text(plan_text, encoding="utf-8")

    rows = _row("f1", 1) + _row("f2", 1) + _row("f3", 1)
    reg_dir = tmp_path / "regs"
    reg_dir.mkdir()
    reg_path = reg_dir / "walk-register-test.md"
    reg_path.write_text(
        SCHEMA_DECL
        + "Draft: `nonexistent/path/plan.md`\n\n"
        + FOLD_HDR
        + rows,
        encoding="utf-8",
    )

    token, detail = wrl.coverage_verdict(
        reg_path.read_text(), reg_path, plan_path=explicit_plan
    )
    assert token == "COVERED", (token, detail)
    assert "w1 3/3" in detail


# ---------------------------------------------------------------------------
# Test 6 — the highest walk is never judged (in progress)
# ---------------------------------------------------------------------------

def test_highest_walk_never_judged(tmp_path):
    """w2 is the highest; 0 w2 rows is fine — w2 is in progress."""
    plan = _plan_text([
        "Weak spots: w1 3 folded — instruction 3 / record 0.",
        "Weak spots: w2 4 folded — instruction 4 / record 0.",
    ])
    rows = _row("f1", 1) + _row("f2", 1) + _row("f3", 1)
    reg_path, _ = _setup(tmp_path, plan, _reg(rows))

    token, detail = wrl.coverage_verdict(reg_path.read_text(), reg_path)
    assert token == "COVERED", (token, detail)
    assert "w2 in progress" in detail


# ---------------------------------------------------------------------------
# Test 7 — single-walk plan, walk 1 is in progress
# ---------------------------------------------------------------------------

def test_single_walk_plan_is_covered(tmp_path):
    """Only w1 declared (5 folded); 0 w1 rows → COVERED (w1 is the only walk, in progress)."""
    plan = _plan_text([
        "Weak spots: w1 5 folded — instruction 5 / record 0.",
    ])
    reg_path, _ = _setup(tmp_path, plan, _reg(""))

    token, detail = wrl.coverage_verdict(reg_path.read_text(), reg_path)
    assert token == "COVERED", (token, detail)
    assert "w1 in progress" in detail


# ---------------------------------------------------------------------------
# Test 8 — UNDECLARED: three arms, none is INCOMPLETE
# ---------------------------------------------------------------------------

def test_undeclared_no_draft_line(tmp_path):
    """(a) No Draft: line and no --plan → UNDECLARED 'plan not resolvable'."""
    rows = _row("f1", 1)
    reg_dir = tmp_path / "regs"
    reg_dir.mkdir()
    reg_path = reg_dir / "walk-register-test.md"
    reg_path.write_text(SCHEMA_DECL + FOLD_HDR + rows, encoding="utf-8")

    token, detail = wrl.coverage_verdict(reg_path.read_text(), reg_path)
    assert token == "UNDECLARED", (token, detail)
    assert "plan not resolvable" in detail


def test_undeclared_plan_no_lens_lines(tmp_path):
    """(b) Plan resolves but declares no lens lines → UNDECLARED 'plan declares no lens walks'."""
    plan = "# test plan\n\n## Drafting Cycle\n\nNo lens lines here.\n\n## STEP 1\n"
    rows = _row("f1", 1)
    reg_path, _ = _setup(tmp_path, plan, _reg(rows))

    token, detail = wrl.coverage_verdict(reg_path.read_text(), reg_path)
    assert token == "UNDECLARED", (token, detail)
    assert "plan declares no lens walks" in detail


def test_undeclared_no_fold_table(tmp_path):
    """(c) Register with no fold table → UNDECLARED 'no fold table'."""
    plan = _plan_text(["Weak spots: w1 3 folded — instruction 3 / record 0."])
    reg_path, _ = _setup(tmp_path, plan, SCHEMA_DECL + _draft_line() + "Just prose.\n")

    token, detail = wrl.coverage_verdict(reg_path.read_text(), reg_path)
    assert token == "UNDECLARED", (token, detail)
    assert "no fold table" in detail


# ---------------------------------------------------------------------------
# Test 9 — stderr line format: SHAPE-OK, COVERAGE field, split("\t")[1]
# ---------------------------------------------------------------------------

def test_stderr_line_format(tmp_path):
    """main's stderr gains COVERAGE field at position 3; split('\\t')[1] == 'SHAPE-OK'."""
    plan = _plan_text([
        "Weak spots: w1 3 folded — instruction 3 / record 0.",
        "Weak spots: w2 dry.",
    ])
    rows = _row("f1", 1) + _row("f2", 1) + _row("f3", 1)
    reg_path, _ = _setup(tmp_path, plan, _reg(rows))

    result = subprocess.run(
        [sys.executable, str(_SCRIPT), str(reg_path)],
        capture_output=True, text=True, timeout=30,
    )
    lines = [l for l in result.stderr.splitlines() if reg_path.name in l]
    assert lines, f"no stderr line for register: {result.stderr!r}"
    parts = lines[0].split("\t")
    assert parts[1] == "SHAPE-OK", f"expected SHAPE-OK, got {parts[1]!r}: {lines[0]!r}"
    assert parts[2].startswith("COVERAGE:"), (
        f"expected COVERAGE field at [2], got {parts[2]!r}: {lines[0]!r}"
    )

    # A shape-bad register (UNCONFORMANT → SHAPE-FAIL)
    bad_rows = (
        "| f1 | 1 | ACID | 5.1 | pre-existing | elided | the guard ... elided | kept |\n"
    )
    bad_reg = reg_path.parent / "walk-register-bad.md"
    bad_reg.write_text(SCHEMA_DECL + _draft_line() + FOLD_HDR + bad_rows, encoding="utf-8")
    r2 = subprocess.run(
        [sys.executable, str(_SCRIPT), str(bad_reg)],
        capture_output=True, text=True, timeout=30,
    )
    lines2 = [l for l in r2.stderr.splitlines() if bad_reg.name in l]
    assert lines2, r2.stderr
    assert lines2[0].split("\t")[1] == "SHAPE-FAIL", lines2[0]


# ---------------------------------------------------------------------------
# Test 10 — stdout rows byte-identical (PRE-SCHEMA fixture, column-4 contract)
# ---------------------------------------------------------------------------

_T10_FIXTURE_TEXT = (
    "Draft: `knowledge/decisions/drafts/test-plan.md`\n\n"
    "| id | walk | lens | sub_question | origin | finding | pre_fold_text | resolution |\n"
    "|---|---|---|---|---|---|---|---|\n"
    "| f1 | 1 | weak spots | q1 | origin1 | the finding | pre text | resolved |\n"
    "| f2 | 1 | weak spots | q2 | origin2 | the finding 2 | pre text 2 | resolved 2 |\n"
)

_T10_EXPECTED_STDOUT = (
    "file\tline\ttable\trow_status\tfile_status\tcolumns\tmissing\tnote\n"
    "walk-register-fixture.md\t5\t1\tOK\tPRE-SCHEMA\t"
    "| id | walk | lens | sub_question | origin | finding | pre_fold_text | resolution |\t-\t-\n"
    "walk-register-fixture.md\t6\t1\tOK\tPRE-SCHEMA\t"
    "| id | walk | lens | sub_question | origin | finding | pre_fold_text | resolution |\t-\t-\n"
)


def test_stdout_rows_byte_identical(tmp_path):
    """Stdout TSV rows are unchanged — coverage moves to stderr only. Column 4 = row_status."""
    reg_path = tmp_path / "walk-register-fixture.md"
    reg_path.write_text(_T10_FIXTURE_TEXT, encoding="utf-8")

    result = subprocess.run(
        [sys.executable, str(_SCRIPT), str(reg_path)],
        capture_output=True, text=True, timeout=30,
    )
    assert result.stdout == _T10_EXPECTED_STDOUT, (
        f"stdout changed:\nexpected: {_T10_EXPECTED_STDOUT!r}\ngot:      {result.stdout!r}"
    )


# ---------------------------------------------------------------------------
# Test 11 — run_check.judge_register with new token logic
# ---------------------------------------------------------------------------

def test_judge_register_new_token_logic():
    """judge_register: SHAPE-OK → PASS; COVERAGE: INCOMPLETE → FAIL; SHAPE-FAIL → FAIL."""
    sys.path.insert(0, str(BELLOWS_ROOT / "tools"))
    from run_check import judge_register

    # SHAPE-OK + COVERED → PASS
    stderr_ok = (
        "walk-register-test.md\tSHAPE-OK\tCOVERAGE: COVERED — w1 3/3 (rows ≥ declared; "
        "w2 in progress)\tBASIS: rows=3 shape-only; coverage: see COVERAGE\t"
        "shapes: | id | walk | lens | sub_question | origin | finding | pre_fold_text | resolution |\n"
    )
    verdict, reason = judge_register("", stderr_ok, 0)
    assert verdict == "PASS", (verdict, reason)

    # SHAPE-OK + COVERAGE: INCOMPLETE → FAIL naming INCOMPLETE
    stderr_incomplete = (
        "walk-register-test.md\tSHAPE-OK\tCOVERAGE: INCOMPLETE — w1 rows=2 declared=3\t"
        "BASIS: rows=2 shape-only; coverage: see COVERAGE\t"
        "shapes: | id | walk | lens | sub_question | origin | finding | pre_fold_text | resolution |\n"
    )
    verdict2, reason2 = judge_register("", stderr_incomplete, 0)
    assert verdict2 == "FAIL", (verdict2, reason2)
    assert "INCOMPLETE" in reason2, reason2

    # SHAPE-FAIL → FAIL
    stderr_fail = (
        "bad-register.md\tSHAPE-FAIL\tCOVERAGE: UNDECLARED — plan not resolvable\t"
        "BASIS: rows=1 shape-only; coverage: see COVERAGE\tshapes: | ... |\n"
    )
    verdict3, reason3 = judge_register("", stderr_fail, 0)
    assert verdict3 == "FAIL", (verdict3, reason3)

    # Positive control: no SHAPE-OK line → FAIL
    verdict4, reason4 = judge_register("", "", 0)
    assert verdict4 == "FAIL", (verdict4, reason4)


# ---------------------------------------------------------------------------
# Test 12 — substrate_check uses the constant, not the literal "CONFORMANT"
# ---------------------------------------------------------------------------

def test_substrate_check_uses_constant_not_literal(monkeypatch, tmp_path):
    """substrate_check:80 must compare to walk_register_lint.STATUS_CONFORMANT (the
    constant), not the literal 'CONFORMANT'. Monkeypatching the constant to a sentinel
    and asserting the register is accepted proves the literal is gone."""
    import importlib
    _scripts = BELLOWS_ROOT / "scripts"
    sys.path.insert(0, str(_scripts))
    import walk_register_lint as wrl_mod
    # Force the worktree's substrate_check — depositor.py (imported via runner→bellows)
    # adds the canonical bellows scripts to sys.path[0] before this test runs, so
    # sys.modules may hold the main-branch copy which still has the old literal.
    _sc_wt = str(_scripts / "substrate_check.py")
    if "substrate_check" in sys.modules and sys.modules["substrate_check"].__file__ != _sc_wt:
        del sys.modules["substrate_check"]
    import substrate_check as sc

    # Create a plan that declares T1 and has a register ref
    reg = tmp_path / "walk-register-test.md"
    reg.write_text("# register\n", encoding="utf-8")
    plan = tmp_path / "test-plan.md"
    plan.write_text(
        "# test\n\n"
        "**Date:** 2026-09-09 | **cycle_tier:** T1\n\n"
        "## Drafting Cycle\n\n"
        f"**Walk register:** {reg}\n\n"
        "## STEP 1\n",
        encoding="utf-8",
    )

    sentinel = "SENTINEL_STATUS"
    monkeypatch.setattr(wrl_mod, "STATUS_CONFORMANT", sentinel)
    monkeypatch.setattr(wrl_mod, "validate_file", lambda p: (sentinel, [], []))
    monkeypatch.setattr(sc, "_committed_and_clean", lambda p: (True, ""))

    # Bypass legs 2 and 3 so the register leg is isolated
    import lens_order_check
    import cycle_check
    monkeypatch.setattr(lens_order_check, "declared_walks", lambda text: set())
    baseline_file = tmp_path / "baseline.json"
    baseline_file.write_text("{}", encoding="utf-8")
    monkeypatch.setattr(
        cycle_check, "resolve_fold_baseline",
        lambda plan_path, manifest=None: (baseline_file, True),
    )

    _, detail = sc.substrate_status(plan)
    assert "register: walk_register_lint says" not in (detail or ""), detail
