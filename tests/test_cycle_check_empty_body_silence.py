"""The empty-body path no longer returns in silence (thread 151).

Both register warns are built inside `if resolved_path is not None`, so a ref that
resolved to NOTHING left register_warn None and this path emitted nothing — while the
SAME ref is a blocking ESCALATE:assert-fail:2 once the body has walks. Total silence in
exactly the state where the register is the only place the record could be.
"""
import subprocess
import sys
from pathlib import Path

import pytest

BELLOWS_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BELLOWS_ROOT / "scripts"))
sys.path.insert(0, str(BELLOWS_ROOT))

import cycle_check as cc  # noqa: E402


def _plan(tmp_path, *, ref, walks=False, closing="in progress."):
    """A REAL git repo, and the LIVE Cycle Log shape (lens-keyed lines with wN tokens)."""
    repo = tmp_path / "r"
    (repo / "knowledge" / "decisions" / "drafts").mkdir(parents=True)
    subprocess.run(["git", "init", "-q", str(repo)], capture_output=True, check=True)
    lens = "\n".join(
        f"- {n}: w1 1 folded — instruction 1 / record 0."
        for n in ("Weak spots", "Destruction", "Vulnerabilities",
                  "Integration-record", "ACID")) if walks else ""
    body = f"""# bellows — executable: fixture

**Date:** 2026-09-06 | **Project:** bellows | **cycle_tier:** T1

## Drafting Cycle

**Walk register:** `{ref}`
{lens}
**Closing:** {closing}

## STEP 1 — do it
"""
    p = repo / "knowledge" / "decisions" / "drafts" / "executable-fix.md"
    p.write_text(body)
    return p


def _run(plan):
    warns = []
    verdict, _ = cc.run_check(plan, warnings=warns)
    return verdict, warns


def test_unresolvable_ref_with_an_empty_body_no_longer_returns_in_silence(tmp_path):
    plan = _plan(tmp_path, ref="knowledge/research/walk-register-absent.md")
    verdict, warns = _run(plan)
    assert verdict == "CONTINUE", verdict
    assert any("UNRESOLVABLE" in w for w in warns), f"silent CONTINUE: {warns}"


def test_it_WARNS_and_does_not_block(tmp_path):
    """⛔ Measured: all 6 plans in this window are legitimately PRE-WALK — they declare
    a register not yet created, and none claims closure. Escalating would block every
    one of them, so the signal is a WARN."""
    plan = _plan(tmp_path, ref="knowledge/research/walk-register-absent.md")
    verdict, _ = _run(plan)
    assert verdict == "CONTINUE", f"a pre-walk plan must not be blocked: {verdict}"


def test_no_ref_declared_emits_no_new_warn(tmp_path):
    """Nothing was promised, so there is nothing absent. The warn must be specific —
    a checker that speaks on every run trains the reader to skim it (thread 117)."""
    repo = tmp_path / "r"
    (repo / "knowledge" / "decisions" / "drafts").mkdir(parents=True)
    subprocess.run(["git", "init", "-q", str(repo)], capture_output=True, check=True)
    p = repo / "knowledge" / "decisions" / "drafts" / "executable-fix.md"
    p.write_text("# t\n\n**cycle_tier:** T1\n\n## Drafting Cycle\n\n"
                 "**Closing:** in progress.\n\n## STEP 1 — do it\n")
    _, warns = _run(p)
    assert not any("UNRESOLVABLE" in w for w in warns), warns


def test_claiming_closure_with_an_empty_body_stays_CONTINUE_by_RATIFIED_precedence(tmp_path):
    """⛔ CHARACTERISATION, not endorsement — and it pins a decision, not an accident.

    Thread 151's second asymmetry is real: the closure check sits BELOW the empty-body
    early return, so a plan claiming closure with no walks is told CONTINUE, bypassing
    a condition that blocks on every other path. It LOOKS like the same defect as the
    silent register.

    It is RATIFIED. The Tier-2 state-space table in test_cycle_check.py force-classifies
    rule 2 as "none walk -> CONTINUE, no walk data DOMINATES close/reg" (_WALK_DIM: "no
    walk lines -> CONTINUE regardless"), and EIGHT cells assert it. Closing the bypass
    flipped all eight. Changing a ratified precedence is a design decision for the CEO,
    not a bug fix.

    This test exists so the next reader who spots the asymmetry finds the ruling instead
    of re-fixing it. If the precedence is ever changed, this test and those eight cells
    move together."""
    plan = _plan(tmp_path, ref="knowledge/research/walk-register-absent.md",
                 closing="BAR MET at walk 1.")
    verdict, warns = _run(plan)
    assert verdict == "CONTINUE", verdict
    # ...but it is no longer SILENT, which is the half thread 151 actually closes.
    assert any("UNRESOLVABLE" in w for w in warns), warns
