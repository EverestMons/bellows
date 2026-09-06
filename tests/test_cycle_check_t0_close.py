"""T0 can reach BAR_MET — thread 156, CEO decision (a), 2026-09-06.

DRAFTING_CYCLE §1 sanctions a floor tier whose terminal instruction is "then DEPOSIT",
and §3 collapses its Cycle Log to one line carrying an integration-vs-record RESULT.
There was no BAR_MET arm reachable without walk data, so the tier's own instruction was
unreachable by construction: measured 2026-09-06, 13 plans declare T0 and ZERO reached
BAR_MET. §6's coordinate-doctrine-and-gate clause, violated and declared nowhere.
"""
import sys
from pathlib import Path

import pytest

BELLOWS_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BELLOWS_ROOT / "scripts"))

import cycle_check as cc  # noqa: E402


def _t0(tmp_path, cycle_line, name="executable-t0.md"):
    p = tmp_path / name
    p.write_text(
        "# bellows — executable: a doc edit\n\n"
        "**Date:** 2026-09-06 | **Project:** bellows | **cycle_tier:** T0\n\n"
        "## Drafting Cycle\n\n"
        f"{cycle_line}\n\n"
        "## STEP 1 — do it\n"
    )
    return p


def _run(p):
    warns = []
    verdict, _ = cc.run_check(p, warnings=warns)
    return verdict, warns


def test_a_well_formed_T0_reaches_BAR_MET(tmp_path):
    """§3's collapsed form, verbatim."""
    p = _t0(tmp_path, "**cycle_tier:** T0 (no trigger); integration-vs-record pass: dry.")
    verdict, _ = _run(p)
    assert verdict == "BAR_MET", verdict


def test_the_corpus_variant_paren_form_also_closes(tmp_path):
    """executable-431 writes the semicolon INSIDE the parenthesis where §3's example
    puts it outside. It is the only genuine collapsed declaration in the corpus, and
    refusing it on punctuation would be a parser deciding doctrine."""
    p = _t0(tmp_path, "**cycle_tier:** T0 (no trigger; integration-vs-record pass: run — see below)")
    verdict, _ = _run(p)
    assert verdict == "BAR_MET", verdict


def test_T0_with_NO_result_refuses_on_silence(tmp_path):
    """⛔ RULING 119: a gate reading a DECLARATION is defeated by silence. The
    discriminator is the POSITIVE lens-4 result, never 'T0 and no walk data' — which
    any plan could satisfy by writing nothing."""
    p = _t0(tmp_path, "**cycle_tier:** T0 (no trigger)")
    verdict, warns = _run(p)
    assert verdict == "CONTINUE", verdict
    assert any("states no integration-vs-record result" in w for w in warns), warns


def test_T0_with_a_PLACEHOLDER_result_refuses(tmp_path):
    """Same shape as the unemitted Cycle Manifest: a heading with a placeholder body
    passed every gate until the placeholder itself was refused."""
    p = _t0(tmp_path, "**cycle_tier:** T0 (no trigger); integration-vs-record pass: <result>")
    verdict, warns = _run(p)
    assert verdict == "CONTINUE", verdict
    assert any("leaves the integration-vs-record result empty" in w for w in warns), warns


def test_a_NON_T0_plan_with_no_walks_is_unaffected(tmp_path):
    """⛔ The ratified precedence survives. The state-space table force-classifies
    'none walk -> CONTINUE, no walk data DOMINATES close and register', and this arm
    fires ONLY on a declared T0 carrying a result — never on the absence of walks."""
    p = tmp_path / "executable-t1.md"
    p.write_text("# t\n\n**Date:** 2026-09-06 | **cycle_tier:** T1\n\n"
                 "## Drafting Cycle\n\nintegration-vs-record pass: dry.\n\n## STEP 1\n")
    verdict, _ = _run(p)
    assert verdict == "CONTINUE", "a T1 plan closed on a T0 arm"


def test_an_undeclared_tier_with_a_result_does_not_close(tmp_path):
    """The tier must be DECLARED. A stray lens-4 line is not a tier."""
    p = tmp_path / "executable-none.md"
    p.write_text("# t\n\n**Date:** 2026-09-06\n\n## Drafting Cycle\n\n"
                 "integration-vs-record pass: dry.\n\n## STEP 1\n")
    verdict, _ = _run(p)
    assert verdict == "CONTINUE", verdict
