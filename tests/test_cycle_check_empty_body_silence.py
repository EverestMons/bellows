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


def test_claiming_closure_with_an_empty_body_ESCALATES_by_ruling_213(tmp_path):
    """Ruling 213 (thread 213, 2026-09-08): a closure claim with NO walk data ESCALATES.

    Thread 158 measured the asymmetry: the closure check at :633 returns
    ESCALATE:claimed-close-unmet whenever a plan claims closure and verdict is CONTINUE —
    except on the empty-walk path, where the early return answered CONTINUE first. It was
    ratified by eight state-space cells, so changing it needed a ruling. The CEO ruled:
    change it. The Tier-2 table's eight cells and this test move together."""
    repo = tmp_path / "r"
    (repo / "knowledge" / "decisions" / "drafts").mkdir(parents=True)
    import subprocess as _sp
    _sp.run(["git", "init", "-q", str(repo)], capture_output=True, check=True)
    reg = tmp_path / "register.md"
    reg.write_text("# walk register\n")
    p = repo / "knowledge" / "decisions" / "drafts" / "executable-fix.md"
    p.write_text(
        "# bellows — executable: fixture\n\n"
        "**Date:** 2026-09-09 | **Project:** bellows | **cycle_tier:** T1\n\n"
        "## Drafting Cycle\n\n"
        f"**Walk register:** {reg}\n"
        "**Closing:** ✅ BAR MET at walk 1.\n\n"
        "## STEP 1 — do it\n"
    )
    verdict, warns = _run(p)
    assert verdict == "ESCALATE:claimed-close-unmet", verdict


def test_T0_claiming_closure_without_a_result_ESCALATES(tmp_path):
    """Ruling 213, consequence (change 1's ⚠️): the T0 arm fires BEFORE the new closure
    check only when the T0 plan states a lens-4 result. A T0 that claims closure but
    has NO result falls past the T0 arm and hits the new empty-walk check — thread 158's
    asymmetry, now blocked, holds even on the floor tier."""
    def _make(name, cycle_line, closing):
        p = tmp_path / name
        p.write_text(
            "# bellows — executable: a doc edit\n\n"
            "**Date:** 2026-09-09 | **Project:** bellows | **cycle_tier:** T0\n\n"
            "## Drafting Cycle\n\n"
            f"{cycle_line}\n"
            f"**Closing:** {closing}\n\n"
            "## STEP 1 — do it\n"
        )
        return p

    warns = []
    verdict, _ = cc.run_check(
        _make("t0-claim-no-result.md",
              "**cycle_tier:** T0 (no trigger)",
              "✅ BAR MET"),
        warnings=warns,
    )
    assert verdict == "ESCALATE:claimed-close-unmet", verdict

    warns2 = []
    verdict2, _ = cc.run_check(
        _make("t0-claim-with-result.md",
              "**cycle_tier:** T0 (no trigger); integration-vs-record pass: dry.",
              "✅ BAR MET"),
        warnings=warns2,
    )
    assert verdict2 == "BAR_MET", verdict2
