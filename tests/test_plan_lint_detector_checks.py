"""Tests for plan_lint detector checks (s) and (t)."""

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


def _make_plan(manifest_lines, deposits=None):
    manifest = "\n".join(manifest_lines)
    deposits_block = ""
    if deposits:
        entries = "\n".join(f"> - `{d}`" for d in deposits)
        deposits_block = f">\n> **Deposits:**\n{entries}\n"
    return (
        "# Test Plan\n"
        "**Date:** 2026-07-02 | **Dispatch Mode:** bellows"
        " | **pause_for_verdict:** always\n\n"
        "## STEP 1 — DEV\n\n"
        "> Do the work.\n"
        f"{deposits_block}\n"
        "## Cycle Manifest\n"
        f"{manifest}\n"
    )


def test_s_warns_when_detector_omits_state_space():
    plan = _make_plan([
        "target_class: detector",
        "mutants: knowledge/mutants/gate_watcher.json",
    ])
    result = _run_lint(plan)
    s_lines = [l for l in result.stdout.splitlines() if "(s) WARN" in l]
    assert any("state_space" in l for l in s_lines), (
        f"Expected (s) WARN naming state_space, got:\n{result.stdout}"
    )


def test_s_warns_when_detector_omits_mutants():
    plan = _make_plan([
        "target_class: detector",
        "state_space: x by y",
    ])
    result = _run_lint(plan)
    s_lines = [l for l in result.stdout.splitlines() if "(s) WARN" in l]
    assert any("mutants" in l for l in s_lines), (
        f"Expected (s) WARN naming mutants, got:\n{result.stdout}"
    )


def test_s_silent_when_detector_declares_both():
    plan = _make_plan(
        [
            "target_class: detector",
            "state_space: x by y",
            "mutants: knowledge/mutants/test_manifest.json",
        ],
        deposits=["knowledge/mutants/test_manifest.json"],
    )
    result = _run_lint(plan)
    assert "(s) WARN" not in result.stdout, (
        f"Expected no (s) WARN, got:\n{result.stdout}"
    )


def test_s_does_not_fire_without_the_declaration():
    plan = _make_plan(["target: tools/something.py"])
    result = _run_lint(plan)
    assert "(s)" not in result.stdout, (
        f"Expected no (s) output at all, got:\n{result.stdout}"
    )


def test_s_warns_on_a_declared_but_absent_mutants_path():
    plan_warn = _make_plan([
        "target_class: detector",
        "state_space: x by y",
        "mutants: knowledge/mutants/nope.json",
    ])
    result = _run_lint(plan_warn)
    s_mut_lines = [l for l in result.stdout.splitlines()
                   if "(s) WARN" in l and "mutants" in l]
    assert len(s_mut_lines) > 0, (
        f"Expected (s) WARN for absent mutants path, got:\n{result.stdout}"
    )

    plan_ok = _make_plan(
        [
            "target_class: detector",
            "state_space: x by y",
            "mutants: knowledge/mutants/nope.json",
        ],
        deposits=["knowledge/mutants/nope.json"],
    )
    result2 = _run_lint(plan_ok)
    s_mut_lines2 = [l for l in result2.stdout.splitlines()
                    if "(s) WARN" in l and "mutants" in l]
    assert len(s_mut_lines2) == 0, (
        f"Expected no mutants WARN when path is in Deposits, got:\n{result2.stdout}"
    )


def test_t_warns_on_detectorish_name_without_declaration():
    plan = _make_plan(["target: tools/foo_check.py"])
    result = _run_lint(plan)
    assert "(t) WARN" in result.stdout, (
        f"Expected (t) WARN, got:\n{result.stdout}"
    )


def test_t_silent_when_target_class_declared():
    plan = _make_plan(
        [
            "target: tools/foo_check.py",
            "target_class: detector",
            "state_space: x by y",
            "mutants: knowledge/mutants/test_manifest.json",
        ],
        deposits=["knowledge/mutants/test_manifest.json"],
    )
    result = _run_lint(plan)
    assert "(t) WARN" not in result.stdout, (
        f"Expected no (t) WARN when target_class declared, got:\n{result.stdout}"
    )


def test_t_silent_on_non_detector_name():
    plan = _make_plan(["target: tools/report_builder.py"])
    result = _run_lint(plan)
    assert "(t) WARN" not in result.stdout, (
        f"Expected no (t) WARN for non-detector name, got:\n{result.stdout}"
    )


def test_neither_check_changes_exit_code():
    plan_s = _make_plan([
        "target: tools/foo_check.py",
        "target_class: detector",
    ])
    result_s = _run_lint(plan_s)
    assert "(s) WARN" in result_s.stdout
    assert result_s.returncode == 0, (
        f"(s) WARN changed exit code to {result_s.returncode}\n{result_s.stdout}"
    )

    plan_t = _make_plan(["target: tools/foo_check.py"])
    result_t = _run_lint(plan_t)
    assert "(t) WARN" in result_t.stdout
    assert result_t.returncode == 0, (
        f"(t) WARN changed exit code to {result_t.returncode}\n{result_t.stdout}"
    )
