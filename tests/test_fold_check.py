"""Tests for fold_check — the fold post-condition tool (proposals 347/348).

Every scenario below is a MEASURED instance from the 2026-08-14 cycles, replayed
as a constructed failure: the fold that deleted a plan_lint-required literal, the
fold whose explanatory clause tripped the test-scope check, and the line-number
churn that must NOT be reported as drift.
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest

BELLOWS_ROOT = Path(__file__).parent.parent.resolve()
SCRIPTS = BELLOWS_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import fold_check  # noqa: E402


def run_cli(*args):
    p = subprocess.run(
        [sys.executable, str(SCRIPTS / "fold_check.py"), *args],
        capture_output=True, text=True,
    )
    return p.returncode, p.stdout + p.stderr


# ---- unit: normalization ----

def test_normalize_strips_line_numbers():
    a = fold_check.normalize("(q) WARN: line 25 sha256 pin abc123def456 MISMATCH on /x/y.md")
    b = fold_check.normalize("(q) WARN: line 91 sha256 pin abc123def456 MISMATCH on /x/y.md")
    assert a == b, "a line-number shift must not read as drift"


def test_normalize_keeps_hex_identity():
    a = fold_check.normalize("PIN-CHECK: line=3 token=943971f5f909 result=ok")
    b = fold_check.normalize("PIN-CHECK: line=3 token=ea3049ce6fc8 result=ok")
    assert a != b, "a DIFFERENT pin token is a real change"


def test_normalize_ignores_o1_candidate_counts():
    a = fold_check.normalize("(o1) INFO: candidates=11 excluded=6 fired=0")
    b = fold_check.normalize("(o1) INFO: candidates=15 excluded=7 fired=0")
    assert a == b


def test_is_signal_selects_only_actionable_lines():
    assert fold_check.is_signal("(o2) WARN: Deposits entry `x` is not project-prefixed")
    assert fold_check.is_signal("PIN-CHECK: line=1 token=abc result=ok")
    assert not fold_check.is_signal("PASS: (a) header — parsed")
    assert not fold_check.is_signal("")


# ---- integration: the measured instances ----

PLAN_TEMPLATE = """# Executable: fixture plan

**Type:** Executable
**Project:** bellows
**Created:** 2026-08-14
**Author:** Planner
**Slug:** `fixture-2026-08-14`
**dispatch_mode:** bellows
**pause_for_verdict:** always
**cycle_tier:** T1
**qa_steps:** 1

## Why
A fixture.{EXTRA}

## Drafting Cycle

**Tier:** T1 — structure-clone of plan 392.

**Walk 0:** clone origin AND newest same-class = plan 392 (measured by ship date).

## STEP 1 — DEV
> Do the thing.{STEP_EXTRA}
>
> **Deposits:**
> - `bellows/knowledge/development/fixture.md`
>
> **Scope:**
> - `knowledge/development/fixture.md`

## STEP 2 — QA
> **Rule 20 — QA Self-Check Results** / `PASSED — SELF-CHECK PASSED`
>
> **Deposits:**
> - `bellows/knowledge/qa/fixture-qa.md`
>
> **Scope:**
> - `knowledge/qa/fixture-qa.md`
"""


def write_plan(tmp_path, extra="", step_extra="", name="executable-999.md"):
    p = tmp_path / name
    p.write_text(PLAN_TEMPLATE.format(EXTRA=extra, STEP_EXTRA=step_extra), encoding="utf-8")
    return p


def test_clean_when_nothing_changed(tmp_path):
    plan = write_plan(tmp_path)
    code, out = run_cli("--save-baseline", str(plan))
    assert code == 0 and "BASELINE SAVED" in out
    code, out = run_cli(str(plan))
    assert code == 0, out
    assert "FOLD-CHECK CLEAN" in out


def test_detects_deleted_required_literal(tmp_path):
    """The X-2 instance: a fold rewrote `newest same-class` away and plan_lint (k) fired."""
    plan = write_plan(tmp_path)
    code, _ = run_cli("--save-baseline", str(plan))
    assert code == 0
    # the fold: a clarity rewrite that drops the literal the (k) check requires
    text = plan.read_text(encoding="utf-8").replace(
        "clone origin AND newest same-class = plan 392",
        "the comparison plan is 392",
    )
    plan.write_text(text, encoding="utf-8")
    code, out = run_cli(str(plan))
    assert code == 1, out
    assert "FOLD-CHECK DRIFT" in out
    assert "APPEARED" in out


def test_detects_bare_token_tripping_a_check(tmp_path):
    """The f7/CP-5 instance: a bare `test` token in an explanatory clause."""
    plan = write_plan(tmp_path)
    code, _ = run_cli("--save-baseline", str(plan))
    assert code == 0
    text = plan.read_text(encoding="utf-8").replace(
        "> Do the thing.",
        "> Do the thing. A count-only test is not sufficient here.",
    )
    plan.write_text(text, encoding="utf-8")
    code, out = run_cli(str(plan))
    assert code == 1, out
    assert "APPEARED" in out


def test_line_shift_alone_is_not_drift(tmp_path):
    """A fold that adds prose shifts every line below it — that must stay silent."""
    plan = write_plan(tmp_path)
    code, _ = run_cli("--save-baseline", str(plan))
    assert code == 0
    text = plan.read_text(encoding="utf-8").replace(
        "## Why",
        "## Context\n\nSeveral\nadded\nlines\nof\nharmless\nprose.\n\n## Why",
    )
    plan.write_text(text, encoding="utf-8")
    code, out = run_cli(str(plan))
    assert code == 0, out
    assert "FOLD-CHECK CLEAN" in out


def test_missing_baseline_is_exit_2_not_a_pass(tmp_path):
    plan = write_plan(tmp_path)
    code, out = run_cli(str(plan))
    assert code == 2, out
    assert "no baseline" in out


def test_missing_artifact_is_exit_2(tmp_path):
    code, out = run_cli(str(tmp_path / "nope.md"))
    assert code == 2
    assert "not found" in out


def test_baseline_file_is_json_and_round_trips(tmp_path):
    plan = write_plan(tmp_path)
    run_cli("--save-baseline", str(plan))
    bpath = plan.parent / f".{plan.name}.foldcheck.json"
    data = json.loads(bpath.read_text(encoding="utf-8"))
    assert "plan_lint" in data
    assert "signals" in data["plan_lint"] and "exit" in data["plan_lint"]


def test_explicit_baseline_path_is_honoured(tmp_path):
    plan = write_plan(tmp_path)
    b = tmp_path / "custom-baseline.json"
    code, _ = run_cli("--save-baseline", str(plan), "--baseline", str(b))
    assert code == 0 and b.is_file()
    code, out = run_cli(str(plan), "--baseline", str(b))
    assert code == 0, out


def test_walk_register_artifact_routes_to_its_own_reader(tmp_path):
    reg = tmp_path / "walk-register-fixture-2026-08-14.md"
    reg.write_text(
        "**schema_version:** `0.3`\n\n"
        "| id | walk | lens | sub_question | origin | finding | pre_fold_text | resolution |\n"
        "|---|---|---|---|---|---|---|---|\n"
        "| f1 | 1 | ACID | 5.1 | pre-existing | a | ADDITION | kept |\n",
        encoding="utf-8",
    )
    code, out = run_cli("--save-baseline", str(reg))
    assert code == 0, out
    assert "walk_register_lint" in out


def test_crashed_reader_is_exit_2_never_a_clean_pass(tmp_path, monkeypatch):
    """A reader that cannot run must HALT the check — a silent reader is
    otherwise indistinguishable from a clean artifact (the defect this test
    caught in fold_check's own first form)."""
    plan = write_plan(tmp_path)
    fake = tmp_path / "scripts"
    fake.mkdir()
    (fake / "plan_lint.py").write_text("raise SystemExit(__import__('sys').stderr.write('Traceback (most recent call last)\\nBoom\\n'))", encoding="utf-8")
    monkeypatch.setattr(fold_check, "SCRIPTS_DIR", fake)
    with pytest.raises(fold_check.ReaderCrashed):
        fold_check.collect(plan)


def test_reader_with_no_output_is_not_clean(tmp_path, monkeypatch):
    plan = write_plan(tmp_path)
    fake = tmp_path / "scripts2"
    fake.mkdir()
    (fake / "plan_lint.py").write_text("pass\n", encoding="utf-8")
    monkeypatch.setattr(fold_check, "SCRIPTS_DIR", fake)
    with pytest.raises(fold_check.ReaderCrashed):
        fold_check.collect(plan)
