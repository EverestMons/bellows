"""_compute_coherence — every non-answer names itself, and the empty body is a FINDING.

Thread 152 (session 5f165f0d, 2026-09-06): coherence is the system's ONLY body-vs-
register reconciliation, and it was disabled by the state it exists to detect. Measured
over the plan corpus: 118 N/A, 51 scored, 51 perfect, ZERO disagreeing — a measure that
has never once disagreed is reporting on its own construction.
"""
import subprocess
import sys
from pathlib import Path

import pytest

BELLOWS_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BELLOWS_ROOT / "scripts"))

import cycle_check as cc  # noqa: E402


def _init_repo(tmp_path):
    """⛔ A REAL git repo. _find_git_root shells out to `git rev-parse --show-toplevel`,
    so a bare .git directory is not a repo — and without one the fixture exits at the
    no-git-root arm and tests nothing."""
    if not (tmp_path / ".git" / "HEAD").exists():
        subprocess.run(["git", "init", "-q", str(tmp_path)], capture_output=True, check=True)
    return tmp_path


def _reg(tmp_path, rows):
    _init_repo(tmp_path)
    d = tmp_path / "regs"
    d.mkdir(exist_ok=True)
    body = "\n".join(
        f"| f{i} | {i} | Weak spots | 1.1 | pre-existing | a finding | bytes | fixed |"
        for i in range(1, rows + 1))
    # ⚠️ Real registers carry `## Walk N` SECTION HEADINGS, and that literal text is
    # what the matcher looks for — a walk number sitting only in a table cell is not
    # matched. The first cut of this fixture omitted them and scored 0/2, which is the
    # function behaving correctly against a register unlike any real one.
    heads = "\n".join(f"## Walk {i} — lenses 1-5\n" for i in range(1, rows + 1))
    (d / "walk-register-t.md").write_text(
        "# Walk Register — t\n\n**schema_version:** `0.3`\n\n" + heads + "\n"
        "| id | walk | lens | sub_question | origin | finding | pre_fold_text | resolution |\n"
        "|---|---|---|---|---|---|---|---|\n" + body + "\n")
    return "regs/walk-register-t.md"


def test_empty_body_against_a_populated_register_is_SUSPECT(tmp_path):
    """⛔ The arm that mattered. A body declaring no walks beside a register full of
    rows is EXACTLY the drift coherence exists to detect, and it returned N/A."""
    ref = _reg(tmp_path, 4)
    plan = tmp_path / "p.md"; plan.write_text("x")
    v = cc._compute_coherence({"walk_register_ref": ref, "walk_data": {}}, plan)
    assert v.startswith("SUSPECT"), v
    assert "carries 4 rows" in v


def test_empty_body_and_empty_register_is_an_EXPLAINED_na(tmp_path):
    ref = _reg(tmp_path, 0)
    plan = tmp_path / "p.md"; plan.write_text("x")
    v = cc._compute_coherence({"walk_register_ref": ref, "walk_data": {}}, plan)
    assert v.startswith("N/A"), v
    assert "no walks" in v


def test_every_na_arm_states_its_reason(tmp_path):
    """A bare 'N/A' is indistinguishable from three different situations. Measured:
    the 118 N/A split 62 unresolvable-ref / 53 no-ref-declared / 1 genuinely empty."""
    _init_repo(tmp_path)
    plan = tmp_path / "p.md"; plan.write_text("x")
    no_ref = cc._compute_coherence({"walk_register_ref": None, "walk_data": {}}, plan)
    assert no_ref == "N/A (no register declared)"
    unresolved = cc._compute_coherence(
        {"walk_register_ref": "regs/missing.md", "walk_data": {1: {}}}, plan)
    assert unresolved.startswith("N/A ("), unresolved
    assert "resolve" in unresolved
    assert unresolved != "N/A", "a bare N/A hides which arm was taken"


def test_scored_value_states_its_basis_and_disclaims_coverage(tmp_path):
    """It counts body walks whose NUMBER appears in the register text — it says nothing
    about whether those walks' findings have rows. N/N must not read as coverage."""
    ref = _reg(tmp_path, 4)
    plan = tmp_path / "p.md"; plan.write_text("x")
    v = cc._compute_coherence({"walk_register_ref": ref, "walk_data": {1: {}, 2: {}}}, plan)
    assert v.startswith("2/2"), v
    assert "register rows" in v
    assert "NOT row coverage" in v


def test_the_walk_matcher_cannot_reach_a_gate2_week_token(tmp_path):
    """⛔ Thread 152's defect (2) does NOT reproduce, and the matcher is deliberately
    unchanged. The loop is bounded by total_walks (17 at corpus max) and `\\bw2\\b`
    cannot match `w28` — the trailing \\b fails against `8`."""
    _init_repo(tmp_path)
    d = tmp_path / "regs"; d.mkdir()
    (d / "walk-register-t.md").write_text(
        "# reg\n\nthe gate2-dc-w28 commit and forge-cycle-w29-2026-09-02\n")
    plan = tmp_path / "p.md"; plan.write_text("x")
    v = cc._compute_coherence(
        {"walk_register_ref": "regs/walk-register-t.md", "walk_data": {1: {}, 2: {}}}, plan)
    assert v.startswith("0/2"), f"a w28/w29 token was scored as a walk: {v}"
