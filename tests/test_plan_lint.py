import os
import subprocess
import sys
import tempfile

BELLOWS_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LINT_SCRIPT = os.path.join(BELLOWS_ROOT, "scripts", "plan_lint.py")


def _run_lint(plan_text):
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(plan_text)
        f.flush()
        try:
            result = subprocess.run(
                [sys.executable, LINT_SCRIPT, f.name],
                capture_output=True, text=True, timeout=30,
            )
            return result
        finally:
            os.unlink(f.name)


GOOD_PLAN = """\
# Test Plan
**Date:** 2026-07-02 | **Dispatch Mode:** bellows | **qa_steps:** 2 | **pause_for_verdict:** always

## STEP 1 — DEV

> Do the work.
>
> **Deposits:**
> - `knowledge/development/dev-log.md`

## STEP 2 — QA

> Verify deliverables.
>
> Your QA report MUST include the byte-exact banner `Rule 20 — QA Self-Check Results` and a `PASSED — SELF-CHECK PASSED` line.
>
> **Deposits:**
> - `knowledge/qa/qa-report.md`
"""


def test_lint_well_formed_plan_passes():
    """(i) Well-formed fixture plan passes all checks exit 0."""
    result = _run_lint(GOOD_PLAN)
    assert result.returncode == 0, f"Expected exit 0, got {result.returncode}\nstdout: {result.stdout}\nstderr: {result.stderr}"
    assert "FAIL" not in result.stdout


def test_lint_missing_deposits_block_fails():
    """(ii) Missing Deposits block in a deposit-mentioning step -> exit 1 naming check (b)."""
    plan = """\
# Test Plan
**Date:** 2026-07-02 | **Dispatch Mode:** bellows | **pause_for_verdict:** always

## STEP 1 — DEV

> Do the work. Deposit the dev log as inline prose.

"""
    result = _run_lint(plan)
    assert result.returncode == 1, f"Expected exit 1, got {result.returncode}\nstdout: {result.stdout}"
    assert "(b)" in result.stdout


def test_lint_qa_missing_banner_pair_fails():
    """(iii) QA plan missing the banner pair -> exit 1 naming check (c)."""
    plan = """\
# Test Plan
**Date:** 2026-07-02 | **Dispatch Mode:** bellows | **qa_steps:** 2 | **pause_for_verdict:** always

## STEP 1 — DEV

> Do the work.
>
> **Deposits:**
> - `knowledge/development/dev-log.md`

## STEP 2 — QA

> Verify deliverables.
>
> **Deposits:**
> - `knowledge/qa/qa-report.md`
"""
    result = _run_lint(plan)
    assert result.returncode == 1, f"Expected exit 1, got {result.returncode}\nstdout: {result.stdout}"
    assert "(c)" in result.stdout


def test_lint_empty_scope_block_fails():
    """(vi) Present-but-empty Scope block → exit 1 naming check (d)."""
    plan = """\
# Test Plan
**Date:** 2026-07-02 | **Dispatch Mode:** bellows | **pause_for_verdict:** always

## STEP 1 — DEV

> Do the work.
>
> **Scope:**
>
> **Deposits:**
> - `knowledge/development/dev-log.md`

"""
    result = _run_lint(plan)
    assert result.returncode == 1, f"Expected exit 1, got {result.returncode}\nstdout: {result.stdout}"
    assert "(d)" in result.stdout


def test_lint_test_mentioned_no_test_scope_warns():
    """(vii) Step mentions tests but declares no test scope -> WARN fires, exit code unaffected."""
    plan = """\
# Test Plan
**Date:** 2026-07-02 | **Dispatch Mode:** bellows | **pause_for_verdict:** always

## STEP 1 — DEV

> Do the work and run the test suite.
>
> **Scope:**
> - `gates.py`
>
> **Deposits:**
> - `knowledge/development/dev-log.md`

"""
    result = _run_lint(plan)
    assert result.returncode == 0, f"Expected exit 0 (WARN only), got {result.returncode}\nstdout: {result.stdout}"
    assert "WARN" in result.stdout
    assert "test scope" in result.stdout.lower() or "test scope" in result.stdout


def test_lint_unrecognized_dispatch_mode_fails():
    """(iv) Unrecognized dispatch_mode -> exit 1 naming check (a)."""
    plan = """\
# Test Plan
**Date:** 2026-07-02 | **Dispatch Mode:** auto_magical | **pause_for_verdict:** always

## STEP 1 — DEV

> Do the work.

"""
    result = _run_lint(plan)
    assert result.returncode == 1, f"Expected exit 1, got {result.returncode}\nstdout: {result.stdout}"
    assert "(a)" in result.stdout


def test_lint_qa_steps_cross_check_good():
    """(a) Good DEV→QA plan (qa_steps: 2, STEP 2 QA-labeled) emits NO qa_steps WARN, exit 0."""
    plan = """\
# Test Plan
**Date:** 2026-07-02 | **Dispatch Mode:** bellows | **qa_steps:** 2 | **pause_for_verdict:** always

## STEP 1 — DEV

> Do the work.
>
> **Deposits:**
> - `knowledge/development/dev-log.md`

## STEP 2 — QA

> Verify deliverables.
>
> Your QA report MUST include the byte-exact banner `Rule 20 — QA Self-Check Results` and a `PASSED — SELF-CHECK PASSED` line.
>
> **Deposits:**
> - `knowledge/qa/qa-report.md`
"""
    result = _run_lint(plan)
    assert result.returncode == 0, f"Expected exit 0, got {result.returncode}\nstdout: {result.stdout}"
    assert "qa_steps lists step" not in result.stdout
    assert "QA-labeled but absent from qa_steps" not in result.stdout


def test_lint_qa_steps_plan133_trap():
    """(b) Plan-133 shape: qa_steps: 1, STEP 1 DEV / STEP 2 QA → 'gated as QA' WARN, exit 0."""
    plan = """\
# Test Plan
**Date:** 2026-07-02 | **Dispatch Mode:** bellows | **qa_steps:** 1 | **pause_for_verdict:** always

## STEP 1 — DEV

> Do the work.
>
> **Deposits:**
> - `knowledge/development/dev-log.md`

## STEP 2 — QA

> Verify deliverables.
>
> Your QA report MUST include the byte-exact banner `Rule 20 — QA Self-Check Results` and a `PASSED — SELF-CHECK PASSED` line.
>
> **Deposits:**
> - `knowledge/qa/qa-report.md`
"""
    result = _run_lint(plan)
    assert result.returncode == 0, f"Expected exit 0 (WARN only), got {result.returncode}\nstdout: {result.stdout}"
    assert "gated as QA (plan-133 trap)" in result.stdout
    assert "QA-labeled but absent from qa_steps" in result.stdout


def test_lint_qa_steps_qa_labeled_absent():
    """(c) QA-labeled step absent from qa_steps → 'will not be gated' WARN, exit 0."""
    plan = """\
# Test Plan
**Date:** 2026-07-02 | **Dispatch Mode:** bellows | **qa_steps:** 3 | **pause_for_verdict:** always

## STEP 1 — DEV

> Do the work.
>
> **Deposits:**
> - `knowledge/development/dev-log.md`

## STEP 2 — QA

> Verify deliverables.
>
> Your QA report MUST include the byte-exact banner `Rule 20 — QA Self-Check Results` and a `PASSED — SELF-CHECK PASSED` line.
>
> **Deposits:**
> - `knowledge/qa/qa-report.md`
"""
    result = _run_lint(plan)
    assert result.returncode == 0, f"Expected exit 0 (WARN only), got {result.returncode}\nstdout: {result.stdout}"
    assert "will not be Rule 20/22 gated" in result.stdout


def test_lint_qa_steps_list_form():
    """(d) List-form qa_steps: [2] parses identically — no false WARN."""
    plan = """\
# Test Plan
**Date:** 2026-07-02 | **Dispatch Mode:** bellows | **qa_steps:** [2] | **pause_for_verdict:** always

## STEP 1 — DEV

> Do the work.
>
> **Deposits:**
> - `knowledge/development/dev-log.md`

## STEP 2 — QA

> Verify deliverables.
>
> Your QA report MUST include the byte-exact banner `Rule 20 — QA Self-Check Results` and a `PASSED — SELF-CHECK PASSED` line.
>
> **Deposits:**
> - `knowledge/qa/qa-report.md`
"""
    result = _run_lint(plan)
    assert result.returncode == 0, f"Expected exit 0, got {result.returncode}\nstdout: {result.stdout}"
    assert "qa_steps lists step" not in result.stdout
    assert "QA-labeled but absent from qa_steps" not in result.stdout


def test_lint_qa_steps_malformed():
    """(e) Malformed qa_steps: abc — no crash, no traceback, exits without error."""
    plan = """\
# Test Plan
**Date:** 2026-07-02 | **Dispatch Mode:** bellows | **qa_steps:** abc | **pause_for_verdict:** always

## STEP 1 — DEV

> Do the work.
>
> **Deposits:**
> - `knowledge/development/dev-log.md`
"""
    result = _run_lint(plan)
    assert "Traceback" not in result.stderr
    assert "Traceback" not in result.stdout
    assert "qa_steps lists step" not in result.stdout


def test_lint_qa_steps_absent_no_warn():
    """(f) No qa_steps field → no qa_steps WARN."""
    plan = """\
# Test Plan
**Date:** 2026-07-02 | **Dispatch Mode:** bellows | **pause_for_verdict:** always

## STEP 1 — DEV

> Do the work.
>
> **Deposits:**
> - `knowledge/development/dev-log.md`
"""
    result = _run_lint(plan)
    assert "qa_steps lists step" not in result.stdout
    assert "QA-labeled but absent from qa_steps" not in result.stdout


def test_lint_titlecase_step_headings_with_qa_steps_fails():
    """(e-a) qa_steps: 2 with title-case '## Step N' headings → (e) FAIL, exit 1."""
    plan = """\
# Test Plan
**Date:** 2026-07-13 | **Dispatch Mode:** bellows | **qa_steps:** 2 | **pause_for_verdict:** always

## Step 1 — DEV

> Do the work.
>
> **Deposits:**
> - `knowledge/development/dev-log.md`

## Step 2 — QA

> Verify deliverables.
>
> Your QA report MUST include the byte-exact banner `Rule 20 — QA Self-Check Results` and a `PASSED — SELF-CHECK PASSED` line.
>
> **Deposits:**
> - `knowledge/qa/qa-report.md`
"""
    result = _run_lint(plan)
    assert result.returncode == 1, f"Expected exit 1, got {result.returncode}\nstdout: {result.stdout}"
    assert "(e)" in result.stdout
    assert "vacuous pass" in result.stdout
    assert "uppercase" in result.stdout.lower()


def test_lint_uppercase_step_headings_no_e_fail():
    """(e-b) Correct uppercase '## STEP N' → NO (e) row."""
    result = _run_lint(GOOD_PLAN)
    assert "(e)" not in result.stdout


def test_lint_single_step_diagnostic_no_e_fail():
    """(e-c) Single-step diagnostic (no qa_steps, no step headings) → NO (e) FAIL, NO case WARN, exit 0."""
    plan = """\
# Diagnostic
**Date:** 2026-07-13 | **Dispatch Mode:** bellows | **pause_for_verdict:** always

## Context

Some analysis goes here.
"""
    result = _run_lint(plan)
    assert result.returncode == 0, f"Expected exit 0, got {result.returncode}\nstdout: {result.stdout}"
    assert "(e)" not in result.stdout
    assert "WARN" not in result.stdout


def test_lint_titlecase_step_no_qa_steps_warns_only():
    """(e-d) No qa_steps, '## Step 1' prose → WARN printed but exit 0."""
    plan = """\
# Diagnostic
**Date:** 2026-07-13 | **Dispatch Mode:** bellows | **pause_for_verdict:** always

## Step 1 — Analysis

> Investigate the issue.
"""
    result = _run_lint(plan)
    assert result.returncode == 0, f"Expected exit 0 (WARN only), got {result.returncode}\nstdout: {result.stdout}"
    assert "WARN" in result.stdout
    assert "uppercase" in result.stdout.lower()
    assert "(e)" not in result.stdout
