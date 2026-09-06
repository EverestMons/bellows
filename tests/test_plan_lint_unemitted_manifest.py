"""(f) manifest — an UNEMITTED Cycle Manifest must FAIL at close (plan #2, thread 107/112).

A '## Cycle Manifest' heading whose stanza parses to ZERO fields is not "ten missing
fields" — it is a manifest no consumer can read. cycle_check.parse_manifest_stanza
returns {}, depositor._parse_plan falls back to prose deposits, and the write set and
class narrow silently. That is the 2026-09-03 failed-open deposit (LESSONS 413): four
writes became two, all under knowledge/, so the infra rule never fired and the plan
AUTO-CLEARED past the shop-infra human release act — while plan_lint printed ten WARNs
and exited 0.
"""
import os
import subprocess
import sys
import tempfile
from pathlib import Path

BELLOWS_ROOT = Path(__file__).resolve().parent.parent
LINT_SCRIPT = str(BELLOWS_ROOT / "scripts" / "plan_lint.py")


def _run_lint(plan_text):
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(plan_text)
        f.flush()
        try:
            return subprocess.run([sys.executable, LINT_SCRIPT, f.name],
                                  capture_output=True, text=True, timeout=30)
        finally:
            os.unlink(f.name)


def _plan(*, manifest_body, closing):
    return f"""# bellows — executable: a plan

**Date:** 2026-09-05 | **Project:** bellows | **Tier:** Small | **cycle_tier:** T1

## Drafting Cycle

**Walk 1** — Weak spots · Destruction · Vulnerabilities · Integration-record · ACID
- Lens 1 (weak spots): 0 findings
**Closing:** {closing}

## Cycle Manifest

{manifest_body}

## STEP 1 — Do the thing
"""


_EMITTED = """tier: T1
target: tools/x.py
class: shop-infra
reads: a.py
writes: tools/x.py
open_forks: none
walks: 1
yields: 0
validation: cycle_check=BAR_MET, plan_lint=0, fold_check=CLEAN, propagation_check=0
coherence: 1.0"""


def test_unemitted_manifest_at_close_FAILS():
    r = _run_lint(_plan(manifest_body="*(emitted at BAR_MET)*", closing="BAR MET at walk 1."))
    assert "FAIL: (f) manifest" in r.stdout, r.stdout
    assert r.returncode == 1, (
        f"printed a FAIL but exited {r.returncode} — results.append does not set "
        f"all_passed, and depositor.py only reads FAIL: lines when returncode != 0"
    )


def test_unemitted_manifest_MID_CYCLE_does_not_fail():
    """⛔ The condition is load-bearing. A plan mid-cycle carries the placeholder
    legitimately; FAILing every walk of every cycle trains the FAIL into noise.
    Measured 2026-09-05: of 8 corpus plans with a zero-field stanza, 7 are mid-cycle."""
    r = _run_lint(_plan(manifest_body="*(emitted at BAR_MET)*",
                        closing="walk 1 complete, continuing."))
    assert "FAIL: (f) manifest" not in r.stdout, r.stdout
    assert "(f) WARN: Cycle Manifest stanza missing or empty field" in r.stdout, \
        "the per-field WARNs must survive for mid-cycle plans"


def test_negated_closure_claim_is_not_a_claim():
    """`_NEGATION_RE` strips 'bar NOT met' before the claim search — a plan saying it
    has NOT met the bar is mid-cycle, not closing."""
    r = _run_lint(_plan(manifest_body="*(emitted at BAR_MET)*",
                        closing="BAR NOT MET — one finding open."))
    assert "FAIL: (f) manifest" not in r.stdout, r.stdout


def test_emitted_manifest_at_close_passes_the_check():
    r = _run_lint(_plan(manifest_body=_EMITTED, closing="BAR MET at walk 1."))
    assert "FAIL: (f) manifest" not in r.stdout, r.stdout


def test_no_manifest_heading_at_all_is_not_this_check():
    """Arm A (no heading) is cycle_check's to block at BAR_MET; this check is arm B
    only — a heading that lies. It must not fire when there is no heading."""
    t = _plan(manifest_body=_EMITTED, closing="BAR MET at walk 1.")
    t = t.replace("## Cycle Manifest\n\n" + _EMITTED + "\n\n", "")
    r = _run_lint(t)
    assert "FAIL: (f) manifest" not in r.stdout, r.stdout
