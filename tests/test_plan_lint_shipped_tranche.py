"""(x) — a plan whose OWN slug names a shipped doctrine changelog row (thread 157).

Nothing in the admission path asks whether a plan's work has ALREADY BEEN DONE.
cycle_check BAR_MET attests the plan's own cycle converged; it says nothing about the
world the plan would act on. Measured 2026-09-06: of 7 gate-clean drafts, FOUR had
shipped — two of them doctrine tranches that would have re-applied proposals already
codified into PT v4.98 and DC v2.24.
"""
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

BELLOWS_ROOT = Path(__file__).resolve().parent.parent
LINT = str(BELLOWS_ROOT / "scripts" / "plan_lint.py")


def _gov(tmp_path, changelog_slug):
    gov = tmp_path / "eluvian-governance"
    gov.mkdir()
    (gov / "COMPANY.md").write_text("co\n")
    (gov / "DRAFTING_CYCLE.md").write_text(
        "# DC\n\n## History\n"
        f"- **2.24 (2026-09-02):** slug {changelog_slug}; a shipped tranche.\n")
    (gov / "PLANNER_TEMPLATE.md").write_text("# PT\n")
    return gov


def _run(plan_path, gov):
    env = dict(os.environ, ELUVIAN_WRAP_ROOT=str(gov))
    return subprocess.run([sys.executable, LINT, str(plan_path)],
                          capture_output=True, text=True, timeout=60, env=env)


def _plan(tmp_path, name):
    d = tmp_path / "d"; d.mkdir(exist_ok=True)
    p = d / name
    p.write_text("# bellows — executable: fixture\n\n"
                 "**Date:** 2026-09-06 | **Project:** bellows\n\n## STEP 1 — do it\n")
    return p


def test_warns_when_the_plans_own_slug_is_a_shipped_changelog_row(tmp_path):
    gov = _gov(tmp_path, "dc-manifest-sentence-2026-09-02")
    p = _plan(tmp_path, "executable-dc-manifest-sentence.md")
    r = _run(p, gov)
    assert "(x) WARN" in r.stdout, r.stdout
    assert "SHIPPED doctrine changelog row" in r.stdout


def test_it_is_a_WARN_and_never_fails_the_lint(tmp_path):
    """The remedy for the general class is the retirement ritual, not a gate — and a
    plan may legitimately be re-run. Advisory only."""
    gov = _gov(tmp_path, "dc-manifest-sentence-2026-09-02")
    p = _plan(tmp_path, "executable-dc-manifest-sentence.md")
    r = _run(p, gov)
    assert "FAIL: (x)" not in r.stdout


def test_merely_CITING_a_shipped_slug_does_not_warn(tmp_path):
    """⛔ Keyed on the FILENAME, never on prose. 27 of 35 real drafts MENTION some
    changelog slug — citing a shipped tranche is normal — so a text match is
    degenerate. An earlier cut of this measurement keyed on the first `slug X` in the
    body and got the right answer only by luck."""
    gov = _gov(tmp_path, "dc-manifest-sentence-2026-09-02")
    p = _plan(tmp_path, "executable-something-else.md")
    p.write_text(p.read_text() + "\nThis plan builds on `slug dc-manifest-sentence-2026-09-02`.\n")
    r = _run(p, gov)
    assert "(x) WARN" not in r.stdout, r.stdout


def test_an_unrelated_plan_does_not_warn(tmp_path):
    gov = _gov(tmp_path, "some-other-tranche-2026-08-01")
    p = _plan(tmp_path, "executable-brand-new-subject.md")
    r = _run(p, gov)
    assert "(x) WARN" not in r.stdout, r.stdout


def test_a_missing_governance_root_is_silent_not_a_crash(tmp_path):
    """Advisory checks never decide a verdict, and never take the lint down with them."""
    p = _plan(tmp_path, "executable-dc-manifest-sentence.md")
    r = _run(p, tmp_path / "nonexistent")
    assert r.returncode in (0, 1), r.stderr[:400]
    assert "Traceback" not in r.stderr
