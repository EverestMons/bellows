"""Tests for _check_bare_constants (the (r) WARN-FIRST check)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from plan_lint import _check_bare_constants


def test_bare_constant_in_step_fires():
    text = "## STEP 1 — DEV\n> probe: count == 3 found\n"
    assert _check_bare_constants(text) == 1


def test_supersede_clause_suppresses():
    text = (
        "## STEP 1 — DEV\n"
        "> measured supersedes the old value\n"
        "> probe: count == 3 found\n"
    )
    assert _check_bare_constants(text) == 0


def test_outside_step_block_no_fire():
    text = "## Overview\nprobe: count == 3 found\n"
    assert _check_bare_constants(text) == 0


def test_recorded_nearby_case_insensitive():
    text = (
        "## STEP 1 — DEV\n"
        "> RECORDED in the dev log\n"
        "> probe: count >= 2 expected\n"
    )
    assert _check_bare_constants(text) == 0


def test_multiple_bare_constants():
    text = (
        "## STEP 1 — DEV\n"
        "> first == 1\n"
        "> second >= 2\n"
        "> third <= 3\n"
    )
    assert _check_bare_constants(text) == 3


def test_fence_excludes_structural_constants():
    # 563 fixture: structural constants in fenced code fire zero warns.
    # Provenance: blob 155110df5d23a61ce4ebe95ffbac25f557561b89
    # (68b5288:knowledge/decisions/ready-executable-run-check-wrapper.md)
    text = (
        "## STEP 1 — DEV\n"
        "> Task A — the wrapper.\n"
        ">\n"
        "> ```python\n"
        "> def judge_lint(stdout, stderr, code):\n"
        ">     if code == 0:\n"
        ">         return 'PASS'\n"
        ">     x == 3\n"
        "> ```\n"
    )
    assert _check_bare_constants(text) == 0


def test_fence_toggle_reopens():
    text = (
        "## STEP 1 — DEV\n"
        "> ```python\n"
        "> if code == 0:\n"
        "> ```\n"
        "> prose: count == 5 found\n"
    )
    assert _check_bare_constants(text) == 1
