"""Tests for close_cycle — runs the close sequence in the correct order.

All fixtures are constructed under tmp_path inside a git init repo; the real
checkers are subprocess-run (no mocking of the battery). Seam patch points:
run_checker (every checker call) and after_step (step boundary hook).
"""

import re
import subprocess
import sys
from pathlib import Path

import pytest

BELLOWS_ROOT = Path(__file__).parent.parent.resolve()
SCRIPTS = BELLOWS_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import close_cycle  # noqa: E402 — fails until scripts/close_cycle.py exists

# ---- fixture helpers ----

_LENS_NAMES = {
    1: "Weak spots",
    2: "Destruction",
    3: "Vulnerabilities",
    4: "Integration-record",
    5: "ACID",
}

_DC_BLOCK = (
    "**Tier:** T1\n"
    "**Walk register:** `register.md`\n"
    "- Weak spots: w1 dry.\n"
    "- Destruction: w1 dry.\n"
    "- Vulnerabilities: w1 dry.\n"
    "- Integration-record: w1 dry.\n"
    "- ACID: w1 dry.\n"
    "\n"
    "**Closing:** not reached.\n"
)

_MANIFEST_BLOCK = (
    "\n## Cycle Manifest\n"
    "tier: T1\n"
    "target: scripts/close_cycle.py\n"
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


def _make_fixture(tmp_path):
    """Set up a git repo with plan + register + 5 lens commits (one per lens)."""
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

    for n, name in sorted(_LENS_NAMES.items()):
        register.write_text(register.read_text(encoding="utf-8") + f"<!-- walk1 lens{n} -->\n",
                             encoding="utf-8")
        _git(tmp_path, "add", str(register))
        _git(tmp_path, "commit", "-m", f"draft(plan): walk 1 lens {n} — {name}: test fixture")

    return plan, register


def _closing_file(tmp_path, text="**Closing:** WARM close after walk 1 — BAR MET (T1)."):
    p = tmp_path / "closing.txt"
    p.write_text(text, encoding="utf-8")
    return p


# ---- c1: happy path ----


def test_c1_happy_path(tmp_path, capsys):
    plan, register = _make_fixture(tmp_path)
    closing = _closing_file(tmp_path)

    rc = close_cycle.main([
        str(plan), "--closing-file", str(closing), "--register", str(register),
    ])

    out = capsys.readouterr().out
    steps = [l.split()[1] for l in out.splitlines() if l.startswith("CLOSE:")]
    assert steps == [
        "closing", "baseline", "emit", "splice", "baseline",
        "stored==live", "battery", "commit(skipped)",
    ], f"unexpected step sequence: {steps}"
    assert rc == 0
    plan_text = plan.read_text(encoding="utf-8")
    assert "yields: <declare>" not in plan_text
    assert "validation: <declare>" not in plan_text
    assert "coherence: <declare>" not in plan_text


# ---- c2: emitter output carries ## Cycle Manifest header ----


def test_c2_emit_header_ignored(tmp_path, monkeypatch, capsys):
    """An emitter stdout carrying ## Cycle Manifest still splices only the three keys."""
    plan, register = _make_fixture(tmp_path)
    closing = _closing_file(tmp_path)

    real_run_checker = close_cycle.run_checker

    def patched_run_checker(script, *args):
        rc, out = real_run_checker(script, *args)
        # For the emit step, prepend the Cycle Manifest header to test c2
        if script == "cycle_check.py" and "--emit-manifest" in args:
            out = "## Cycle Manifest\n" + out
        return rc, out

    monkeypatch.setattr(close_cycle, "run_checker", patched_run_checker)

    rc = close_cycle.main([
        str(plan), "--closing-file", str(closing), "--register", str(register),
    ])
    assert rc == 0
    plan_text = plan.read_text(encoding="utf-8")
    assert "yields: <declare>" not in plan_text
    assert "validation: <declare>" not in plan_text
    assert "coherence: <declare>" not in plan_text


# ---- c3: --dry-run step sequence ----


def test_c3_dry_run_order(tmp_path, capsys):
    plan, register = _make_fixture(tmp_path)
    closing = _closing_file(tmp_path)
    plan_before = plan.read_text(encoding="utf-8")

    rc = close_cycle.main([
        str(plan), "--closing-file", str(closing), "--register", str(register),
        "--dry-run",
    ])

    out = capsys.readouterr().out
    steps = [l.split()[1] for l in out.splitlines() if l.startswith("CLOSE:")]
    assert steps == [
        "closing", "baseline", "emit", "splice", "baseline",
        "stored==live", "battery", "commit(skipped)",
    ]
    assert rc == 0
    # dry-run must not modify the real plan
    assert plan.read_text(encoding="utf-8") == plan_before


# ---- c4: stored != live → exit 1 ----


def test_c4_stored_live_mismatch(tmp_path, monkeypatch, capsys):
    """After step 5, tampering with the stored validation: line causes stored==live to fail."""
    plan, register = _make_fixture(tmp_path)
    closing = _closing_file(tmp_path)

    baseline_calls = []

    def tamper_after_step(name):
        if name == "baseline":
            baseline_calls.append(1)
            if len(baseline_calls) == 2:
                # Corrupt the stored validation line in the draft
                text = plan.read_text(encoding="utf-8")
                text = re.sub(
                    r"^validation: .*$",
                    "validation: cycle_check=CONTINUE, plan_lint=0_FAIL, fold_check=VACUOUS, propagation_check=N/A",
                    text, flags=re.MULTILINE,
                )
                plan.write_text(text, encoding="utf-8")

    monkeypatch.setattr(close_cycle, "after_step", tamper_after_step)

    rc = close_cycle.main([
        str(plan), "--closing-file", str(closing), "--register", str(register),
    ])

    out = capsys.readouterr().out
    steps = [l.split()[1] for l in out.splitlines() if l.startswith("CLOSE:")]
    assert "stored==live" in steps[-1]
    assert rc == 1
    # no commit was made
    log = _git(tmp_path, "log", "--oneline").stdout
    assert "close" not in log


# ---- c5: no **Closing:** line → exit 1 at step 1, file untouched ----


def test_c5_no_closing_line(tmp_path, capsys):
    plan, register = _make_fixture(tmp_path)
    # Remove the **Closing:** line from the plan
    text = plan.read_text(encoding="utf-8")
    text = re.sub(r"\*\*Closing:\*\*.*\n", "", text)
    plan.write_text(text, encoding="utf-8")
    original_text = plan.read_text(encoding="utf-8")

    closing = _closing_file(tmp_path)

    rc = close_cycle.main([
        str(plan), "--closing-file", str(closing), "--register", str(register),
    ])

    out = capsys.readouterr().out
    steps = [l.split()[1] for l in out.splitlines() if l.startswith("CLOSE:")]
    assert steps == ["closing"]
    assert rc == 1
    # file must be untouched
    assert plan.read_text(encoding="utf-8") == original_text


# ---- c6: --commit produces one commit with correct subject ----


def test_c6_commit(tmp_path, capsys):
    plan, register = _make_fixture(tmp_path)
    closing = _closing_file(tmp_path)

    rc = close_cycle.main([
        str(plan), "--closing-file", str(closing), "--register", str(register),
        "--commit",
    ])
    assert rc == 0

    log = _git(tmp_path, "log", "--format=%s", "-1").stdout.strip()
    assert log.startswith("draft(plan): close —"), f"unexpected subject: {log!r}"
    # tree must contain draft, register and baseline
    tree = _git(tmp_path, "diff-tree", "--no-commit-id", "-r", "--name-only", "HEAD").stdout
    assert "plan.md" in tree
    assert "register.md" in tree
    assert ".plan.md.foldcheck.json" in tree
