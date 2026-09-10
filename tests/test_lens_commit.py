"""Tests for lens_commit — commits one lens in the correct order.

All fixtures are constructed under tmp_path inside a git init repo.
run_checker is the seam for checker subprocess calls.
"""

import subprocess
import sys
from pathlib import Path

import pytest

BELLOWS_ROOT = Path(__file__).parent.parent.resolve()
SCRIPTS = BELLOWS_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import lens_commit  # noqa: E402 — fails until scripts/lens_commit.py exists

# ---- fixture helpers ----

_DC_BLOCK = (
    "**Tier:** T1\n"
    "**Walk register:** `register.md`\n"
    "- Weak spots: w1 dry.\n"
    "- Destruction: w1 dry.\n"
    "- Vulnerabilities: w1 dry.\n"
    "- Integration-record: w1 dry.\n"
    "- ACID: w1 dry.\n"
)

_MANIFEST_BLOCK = (
    "\n## Cycle Manifest\n"
    "tier: T1\n"
    "target: scripts/lens_commit.py\n"
    "class: shop-infra\n"
    "reads: test\n"
    "writes: test\n"
    "open_forks: none\n"
    "walks: <declare>\n"
    "yields: <declare>\n"
    "validation: <declare>\n"
    "coherence: <declare>\n"
    "fold_baseline: .plan.md.foldcheck.json\n"
)

_INITIAL_PLAN = (
    "# Plan\n"
    "**dispatch_mode:** bellows\n"
    "\n"
    "## Drafting Cycle\n"
    + _DC_BLOCK
    + _MANIFEST_BLOCK
)

_REGISTER = (
    "# Walk Register — test\n\n"
    "**schema_version:** `0.3`\n\n"
    "| id | walk | lens | sub_question | origin | finding | pre_fold_text | resolution |\n"
    "|---|---|---|---|---|---|---|---|\n"
)


def _git(repo, *args):
    return subprocess.run(["git", "-C", str(repo), *args],
                          capture_output=True, text=True)


def _make_lens_fixture(tmp_path):
    """Set up a minimal git repo for lens_commit tests (no prior lens commits)."""
    for cmd in [
        ["git", "-C", str(tmp_path), "init"],
        ["git", "-C", str(tmp_path), "config", "user.name", "Test"],
        ["git", "-C", str(tmp_path), "config", "user.email", "test@test.com"],
    ]:
        subprocess.run(cmd, capture_output=True)

    plan = tmp_path / "plan.md"
    plan.write_text(_INITIAL_PLAN, encoding="utf-8")
    register = tmp_path / "register.md"
    register.write_text(_REGISTER, encoding="utf-8")

    _git(tmp_path, "add", ".")
    _git(tmp_path, "commit", "-m", "initial")

    return plan, register


# ---- l1: subject contains correct lens name from table ----


def test_l1_subject_lens_name(tmp_path):
    """--lens 3 produces subject 'draft(plan): walk 1 lens 3 — Vulnerabilities: <desc>'."""
    plan, register = _make_lens_fixture(tmp_path)

    rc = lens_commit.main([
        str(plan), "--register", str(register),
        "--walk", "1", "--lens", "3", "--desc", "test fixture",
    ])
    assert rc == 0

    log = _git(tmp_path, "log", "--format=%s", "-1").stdout.strip()
    assert log == "draft(plan): walk 1 lens 3 — Vulnerabilities: test fixture", (
        f"unexpected subject: {log!r}"
    )


# ---- l2: wrong name in table detected via commit subject ----


def test_l2_assert_checks_name(tmp_path, monkeypatch):
    """When LENS_NAMES[3] is patched to a wrong name, the assert refuses before any commit."""
    plan, register = _make_lens_fixture(tmp_path)
    monkeypatch.setitem(lens_commit.LENS_NAMES, 3, "WrongName")

    rc = lens_commit.main([
        str(plan), "--register", str(register),
        "--walk", "1", "--lens", "3", "--desc", "test fixture",
    ])
    assert rc == 1, "script must refuse when table entry returns wrong name"

    # No lens commit must have been made
    log = _git(tmp_path, "log", "--format=%s").stdout
    assert "lens 3" not in log


# ---- l3: yield-rising handling ----


def test_l3_yield_rising(tmp_path, monkeypatch):
    """ESCALATE:yield-rising refuses without flag; with --allow-yield-rising --walk 4 appends WARN."""
    plan, register = _make_lens_fixture(tmp_path)

    _real = lens_commit.run_checker

    def fake_run_checker(script, *args):
        if script == "cycle_check.py" and "--emit-manifest" not in args:
            return 1, "ESCALATE:yield-rising\n"
        return _real(script, *args)

    monkeypatch.setattr(lens_commit, "run_checker", fake_run_checker)

    # Without flag: refuses
    rc = lens_commit.main([
        str(plan), "--register", str(register),
        "--walk", "4", "--lens", "1", "--desc", "test",
    ])
    assert rc == 1

    # With --allow-yield-rising: appends WARN and commits
    rc = lens_commit.main([
        str(plan), "--register", str(register),
        "--walk", "4", "--lens", "1", "--desc", "test",
        "--allow-yield-rising",
    ])
    assert rc == 0
    reg_text = register.read_text(encoding="utf-8")
    assert "**WARN (walk 4):**" in reg_text


# ---- l4: --allow-yield-rising --walk 7 refuses ----


def test_l4_yield_rising_walk7_refused(tmp_path, monkeypatch):
    """--allow-yield-rising is refused when --walk >= 7 (CEO ruling)."""
    plan, register = _make_lens_fixture(tmp_path)

    _real = lens_commit.run_checker

    def fake_run_checker(script, *args):
        if script == "cycle_check.py" and "--emit-manifest" not in args:
            return 1, "ESCALATE:yield-rising\n"
        return _real(script, *args)

    monkeypatch.setattr(lens_commit, "run_checker", fake_run_checker)

    rc = lens_commit.main([
        str(plan), "--register", str(register),
        "--walk", "7", "--lens", "1", "--desc", "test",
        "--allow-yield-rising",
    ])
    assert rc == 1


# ---- l5: register lint COVERAGE: INCOMPLETE refuses ----


def test_l5_incomplete_coverage_refuses(tmp_path, monkeypatch):
    """walk_register_lint COVERAGE: INCOMPLETE causes refusal."""
    plan, register = _make_lens_fixture(tmp_path)

    _real = lens_commit.run_checker

    def fake_run_checker(script, *args):
        if script == "walk_register_lint.py":
            return 0, f"{register.name}\tSHAPE-OK\tCOVERAGE: INCOMPLETE — w1 rows=0 declared=2\n"
        return _real(script, *args)

    monkeypatch.setattr(lens_commit, "run_checker", fake_run_checker)

    rc = lens_commit.main([
        str(plan), "--register", str(register),
        "--walk", "1", "--lens", "1", "--desc", "test",
    ])
    assert rc == 1
