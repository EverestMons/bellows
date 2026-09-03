"""Tests for plan_lint check (v): no-pytest QA step must pre-declare its qa_test_result override."""

import os
import subprocess
import sys
import tempfile

BELLOWS_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LINT_SCRIPT = os.path.join(BELLOWS_ROOT, "scripts", "plan_lint.py")

# Rule 20 banner strings required by check (c) — included in test 4's plan so that
# (c) passes and the plan exits 0 with only the (v) WARN firing.
_RULE20_BANNER = (
    "Rule 20 — QA Self-Check Results\n"
    "PASSED — SELF-CHECK PASSED\n"
)


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


def _make_plan(test_scope="none", qa_step_content="", dev_step_content="",
               qa_steps="2", with_banner=False):
    """Build a two-step DEV+QA plan for (v) testing.

    qa_steps: the qa_steps header value ('2' → step 2 is QA by the gate's predicate).
    qa_step_content: text inserted into the QA step body.
    dev_step_content: text inserted into the DEV step body.
    with_banner: if True, appends the Rule 20 banner to the QA step so check (c) passes.
    """
    header = (
        "**Date:** 2026-07-02 | **Dispatch Mode:** bellows | **pause_for_verdict:** always"
    )
    if test_scope:
        header += f" | **Test Scope:** {test_scope}"
    if qa_steps:
        header += f" | **qa_steps:** {qa_steps}"
    banner_block = _RULE20_BANNER if with_banner else ""
    return (
        f"# Test Plan\n"
        f"{header}\n\n"
        f"## STEP 1 — DEV\n\n"
        f"> Do the work.\n"
        f"{dev_step_content}\n"
        f"## STEP 2 — QA\n\n"
        f"> Run the tests.\n"
        f"{qa_step_content}"
        f"{banner_block}\n"
        f"## Cycle Manifest\n"
        f"tier: T1\n"
    )


# Test 1: no-pytest QA step, no clause → WARN appears
def test_v_warns_when_qa_step_has_none_scope_and_no_clause():
    plan = _make_plan(test_scope="none")
    result = _run_lint(plan)
    v_lines = [l for l in result.stdout.splitlines() if "(v) WARN" in l]
    assert v_lines, f"Expected (v) WARN, got:\n{result.stdout}"
    assert any("step 2" in l for l in v_lines), (
        f"Expected WARN naming step 2, got:\n{v_lines}"
    )


# Test 2: clause present → no WARN
def test_v_silent_when_qa_step_has_clause():
    clause = "> **Gate note:** This QA step pre-declares that qa_test_result will fail benign.\n"
    plan = _make_plan(test_scope="none", qa_step_content=clause)
    result = _run_lint(plan)
    assert "(v) WARN" not in result.stdout, (
        f"Expected no (v) WARN, got:\n{result.stdout}"
    )


# Test 3: targeted scope, no clause → silent
def test_v_silent_when_test_scope_is_targeted():
    plan = _make_plan(test_scope="targeted (the new check)")
    result = _run_lint(plan)
    assert "(v) WARN" not in result.stdout, (
        f"Expected no (v) WARN for targeted scope, got:\n{result.stdout}"
    )


# Test 4: (v) fires but no FAILs → exit 0 (guards the exit-code invariant)
def test_v_does_not_alter_exit_code():
    # with_banner makes check (c) pass so the only lint output is WARNs.
    plan = _make_plan(test_scope="none", with_banner=True)
    result = _run_lint(plan)
    v_lines = [l for l in result.stdout.splitlines() if "(v) WARN" in l]
    assert v_lines, f"Expected (v) WARN to fire, got:\n{result.stdout}"
    assert result.returncode == 0, (
        f"Expected exit 0, got {result.returncode}:\n{result.stdout}"
    )


# Test 5: 555 case — clause present without the gate-name token → suppressed
def test_v_silent_when_clause_uses_pre_declar_and_gate_note_without_gate_name():
    # pre-declar and gate note present; qa_test_result absent — mirrors executable-555.
    clause = "> **Gate note:** pre-declaration: no pytest scope, Planner overrides at verdict.\n"
    plan = _make_plan(test_scope="none", qa_step_content=clause)
    result = _run_lint(plan)
    assert "(v) WARN" not in result.stdout, (
        f"Expected no (v) WARN (555 case), got:\n{result.stdout}"
    )


# Test 6: step-scoped suppression — tokens only OUTSIDE the QA step → WARN fires
def test_v_not_suppressed_when_clause_outside_qa_step():
    # Clause tokens appear only in the DEV step, not in the QA step.
    dev_content = "> Discusses pre-declar, gate note, and qa_test_result for reference.\n"
    plan = _make_plan(test_scope="none", dev_step_content=dev_content, qa_step_content="")
    result = _run_lint(plan)
    v_lines = [l for l in result.stdout.splitlines() if "(v) WARN" in l]
    assert v_lines, (
        f"Expected (v) WARN (tokens only in DEV step, not QA step), got:\n{result.stdout}"
    )


# Test 7: headerless plan → lint completes, check (a) FAIL reported, no traceback
def test_v_headerless_plan_does_not_crash():
    plan = (
        "# Untitled Plan\n\n"
        "No header line here.\n\n"
        "## STEP 1 — QA\n\n"
        "> Do stuff.\n"
    )
    result = _run_lint(plan)
    assert "Traceback" not in result.stderr, f"Traceback in stderr:\n{result.stderr}"
    assert "Traceback" not in result.stdout, f"Traceback in stdout:\n{result.stdout}"
    assert "(a) header" in result.stdout, (
        f"Expected (a) header FAIL, got:\n{result.stdout}"
    )


# Test 8: loop-placement discriminator (cold scout S1-1)
def test_v_loop_placement():
    # (a) QA step NOT last: a once-only check at the anchor's indent would read the
    # leaked sn from (u)'s loop (sn=2, which is NOT the QA step) and stay silent.
    # The correct per-step loop fires for sn=1 (the QA step).
    plan_qa_first = (
        "# Test Plan\n"
        "**Date:** 2026-07-02 | **Dispatch Mode:** bellows | **pause_for_verdict:** always"
        " | **Test Scope:** none | **qa_steps:** 1\n\n"
        "## STEP 1 — QA\n\n"
        "> Run tests here. No clause.\n\n"
        "## STEP 2 — cleanup\n\n"
        "> Wrap up.\n\n"
        "## Cycle Manifest\ntier: T1\n"
    )
    result_a = _run_lint(plan_qa_first)
    v_lines_a = [l for l in result_a.stdout.splitlines() if "(v) WARN" in l]
    assert v_lines_a, f"Expected (v) WARN for step 1, got:\n{result_a.stdout}"
    assert any("step 1" in l for l in v_lines_a), (
        f"WARN should name step 1, got:\n{v_lines_a}"
    )

    # (b) No ## STEP headings at all → no traceback (unbound sn would raise NameError
    # if the check were mis-indented at function-body level instead of its own loop).
    plan_no_steps = (
        "# No Steps Plan\n"
        "**Date:** 2026-07-02 | **Dispatch Mode:** bellows | **pause_for_verdict:** always"
        " | **Test Scope:** none | **qa_steps:** 1\n\n"
        "This plan has no step headings.\n\n"
        "## Cycle Manifest\ntier: T1\n"
    )
    result_b = _run_lint(plan_no_steps)
    assert "Traceback" not in result_b.stderr, f"Traceback in stderr:\n{result_b.stderr}"
    assert "Traceback" not in result_b.stdout, f"Traceback in stdout:\n{result_b.stdout}"


# Test 9: predicate regression — non-QA step mentioning "Rule 20" does not trigger WARN
def test_v_predicate_does_not_fire_on_non_qa_step_mentioning_rule_20():
    # Step 1 is QA (qa_steps: 1), no clause → (v) fires for step 1.
    # Step 2 is NOT QA but body mentions "Rule 20" — (u)'s heuristic would treat it as
    # QA, but (v) must use gates._gate_is_qa_step and stay silent for step 2.
    plan = (
        "# Test Plan\n"
        "**Date:** 2026-07-02 | **Dispatch Mode:** bellows | **pause_for_verdict:** always"
        " | **Test Scope:** none | **qa_steps:** 1\n\n"
        "## STEP 1 — QA\n\n"
        "> Run the tests here. Omits the required clause entirely.\n\n"
        "## STEP 2 — cleanup\n\n"
        "> See Rule 20 for reference on self-check formatting.\n\n"
        "## Cycle Manifest\ntier: T1\n"
    )
    result = _run_lint(plan)
    v_lines = [l for l in result.stdout.splitlines() if "(v) WARN" in l]
    # Step 1 has no clause → (v) fires for step 1
    assert any("step 1" in l for l in v_lines), (
        f"Expected (v) WARN for step 1, got:\n{result.stdout}"
    )
    # Step 2 mentions Rule 20 but is not a QA step → (v) must not fire for step 2
    assert not any("step 2" in l for l in v_lines), (
        f"(v) WARN fired incorrectly on step 2 (Rule 20 false positive):\n{result.stdout}"
    )
