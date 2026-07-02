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
