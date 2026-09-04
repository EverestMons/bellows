"""Tests for plan_lint check (c): qa_steps: none normalization (plan 100037).

FO-3 bug: header.get("qa_steps") is truthy for the string "none", causing the
linter to demand a Rule 20 banner even when qa_steps: none means no QA steps.

P4b normalization: "none" and empty are absent-equivalent and must not trigger
the banner demand.  n/a and 0 are NOT normalized (they don't appear in the corpus).
The template placeholder "[comma-separated step numbers]" must emit a WARN but
NOT trigger the banner demand.
"""

import os
import subprocess
import sys
import tempfile

BELLOWS_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LINT_SCRIPT = os.path.join(BELLOWS_ROOT, "scripts", "plan_lint.py")

_RULE20_BANNER = (
    "Rule 20 — QA Self-Check Results\n"
    "PASSED — SELF-CHECK PASSED\n"
)

_QA_STEPS_PLACEHOLDER = "[comma-separated step numbers]"


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


def _make_plan(qa_steps_value, step_headers=None, banner=False):
    """Build a minimal plan with the given qa_steps: header value.

    step_headers: list of step heading suffixes, e.g. ["DEV", "QA"].
                  Defaults to ["DEV"] (no QA step heading) when None.
    banner: if True, include the Rule 20 banner in the last step.
    """
    if step_headers is None:
        step_headers = ["DEV"]
    header = (
        "**Date:** 2026-09-04 | **Dispatch Mode:** bellows "
        "| **pause_for_verdict:** always"
    )
    if qa_steps_value is not None:
        header += f" | **qa_steps:** {qa_steps_value}"
    steps = ""
    for i, suffix in enumerate(step_headers, 1):
        steps += f"## STEP {i} — {suffix}\n\n> Do the work.\n\n"
        if banner and i == len(step_headers):
            steps += _RULE20_BANNER + "\n"
    return (
        f"# Test Plan\n{header}\n\n"
        f"{steps}"
        f"## Cycle Manifest\ntier: T1\n"
    )


# Test 6 (100037): qa_steps: none → no banner demanded, exit 0.
def test_qa_steps_none_no_banner_demanded():
    """qa_steps: none is absent-equivalent — check (c) must not demand a Rule 20 banner."""
    plan = _make_plan(qa_steps_value="none")
    result = _run_lint(plan)
    c_fails = [l for l in result.stdout.splitlines() if "(c)" in l and "FAIL" in l]
    assert not c_fails, f"Unexpected (c) FAIL for qa_steps: none:\n{result.stdout}"
    assert result.returncode == 0, f"Expected exit 0, got {result.returncode}:\n{result.stdout}"


# Test 7 (100037): qa_steps: 2 → banner demanded when absent.
def test_qa_steps_numeric_demands_banner():
    """qa_steps: 2 is a real step number — check (c) must demand a Rule 20 banner."""
    plan = _make_plan(qa_steps_value="2", step_headers=["DEV", "QA"])
    result = _run_lint(plan)
    c_fails = [l for l in result.stdout.splitlines() if "(c)" in l and "FAIL" in l]
    assert c_fails, f"Expected (c) FAIL for qa_steps: 2 without banner:\n{result.stdout}"


# Test 8 (100037): absent qa_steps + step heading containing "qa" → banner demanded.
def test_absent_qa_steps_with_qa_heading_demands_banner():
    """No qa_steps header but a step heading contains 'qa' → check (c) must fire."""
    plan = _make_plan(qa_steps_value=None, step_headers=["DEV", "QA"])
    result = _run_lint(plan)
    c_fails = [l for l in result.stdout.splitlines() if "(c)" in l and "FAIL" in l]
    assert c_fails, f"Expected (c) FAIL for QA heading without banner:\n{result.stdout}"


# Test 9 (100037): empty qa_steps → no banner demanded (P4b normalization).
def test_qa_steps_empty_no_banner_demanded():
    """qa_steps: (empty) is absent-equivalent — check (c) must not demand a banner."""
    plan = _make_plan(qa_steps_value="")
    result = _run_lint(plan)
    c_fails = [l for l in result.stdout.splitlines() if "(c)" in l and "FAIL" in l]
    assert not c_fails, f"Unexpected (c) FAIL for empty qa_steps:\n{result.stdout}"


# Test 9b (100037): placeholder qa_steps → WARN (not FAIL), no banner demanded.
def test_qa_steps_placeholder_warns_no_fail():
    """qa_steps: [comma-separated step numbers] → WARN printed, no (c) FAIL."""
    plan = _make_plan(qa_steps_value=_QA_STEPS_PLACEHOLDER)
    result = _run_lint(plan)
    # Must emit a WARN about the unfilled placeholder
    warn_lines = [l for l in result.stdout.splitlines() if "(c) WARN" in l and "placeholder" in l.lower()]
    assert warn_lines, f"Expected (c) WARN about placeholder, got:\n{result.stdout}"
    # Must NOT emit a FAIL demanding a banner
    c_fails = [l for l in result.stdout.splitlines() if "(c)" in l and "FAIL" in l]
    assert not c_fails, f"Unexpected (c) FAIL for placeholder qa_steps:\n{result.stdout}"
    # Exit code unaffected (WARNs don't raise exit code)
    assert result.returncode == 0, f"Expected exit 0, got {result.returncode}:\n{result.stdout}"


# Test 9c (100037): qa_steps: n/a is NOT normalized — treated as non-none value → banner demanded.
# n/a does not appear in the corpus; we do not special-case it.
def test_qa_steps_na_not_normalized():
    """qa_steps: n/a is NOT in the normalization set — (c) must demand a banner."""
    plan = _make_plan(qa_steps_value="n/a", step_headers=["DEV"])
    result = _run_lint(plan)
    # n/a is truthy and non-special — has_qa becomes True, banner demanded
    c_fails = [l for l in result.stdout.splitlines() if "(c)" in l and "FAIL" in l]
    assert c_fails, f"Expected (c) FAIL for qa_steps: n/a:\n{result.stdout}"


# Test 10 (100037): advisory path unchanged — qa_steps: none + banner present → exit 0.
def test_qa_steps_none_with_banner_exit_zero():
    """qa_steps: none with a banner present — check (c) silent, plan still exits 0."""
    plan = _make_plan(qa_steps_value="none", step_headers=["DEV"], banner=True)
    result = _run_lint(plan)
    c_fails = [l for l in result.stdout.splitlines() if "(c)" in l and "FAIL" in l]
    assert not c_fails, f"Unexpected (c) FAIL:\n{result.stdout}"
    assert result.returncode == 0, f"Expected exit 0, got {result.returncode}:\n{result.stdout}"
