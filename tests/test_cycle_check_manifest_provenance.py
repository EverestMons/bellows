"""Tests for the manifest-provenance gate in cycle_check.

Gate (plan 100033, DC:253): if BAR_MET is imminent but the stored validation:
line omits any key that MANIFEST_VALIDATION_KEYS declares, the verdict is
downgraded to CONTINUE.  Values may drift — only key presence is checked.
"""

import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

BELLOWS_ROOT = Path(__file__).parent.parent.resolve()
SCRIPTS = BELLOWS_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import importlib
if "cycle_check" in sys.modules and sys.modules["cycle_check"].__file__ != str(SCRIPTS / "cycle_check.py"):
    del sys.modules["cycle_check"]
import cycle_check

# DC block that reaches BAR_MET under a clean run_check (dry final walk,
# all asserts N/A, no register, no git dep).
_BAR_MET_DC = (
    "- Weak spots: w1 2 folded — instruction 2 / record 0; w2 dry.\n"
    "- Destruction: w1 1 folded — instruction 1 / record 0; w2 dry.\n"
    "- Vulnerabilities: w1 dry; w2 dry.\n"
    "- Integration-record: w1 dry; w2 dry.\n"
    "- ACID: w1 dry; w2 dry.\n"
)

# validation: line carrying every key MANIFEST_VALIDATION_KEYS declares.
_FULL_VALIDATION = (
    "cycle_check=BAR_MET, plan_lint=0_FAIL, "
    "fold_check=PASS, propagation_check=DIVERGENT:5"
)


def _make_plan_with_manifest(tmp_path, dc_block, validation_line, filename="plan.md"):
    plan = tmp_path / filename
    content = (
        f"# Plan\n\n## Drafting Cycle\n{dc_block}\n"
        "## Cycle Manifest\n"
        "tier: T1\n"
        "target: scripts/cycle_check.py\n"
        "class: shop-infra\n"
        "reads: scripts/cycle_check.py\n"
        "writes: scripts/cycle_check.py\n"
        "open_forks: none\n"
        "walks: 2\n"
        "yields: 2, 0\n"
        f"validation: {validation_line}\n"
        "coherence: 2/2 walks have register rows\n"
    )
    plan.write_text(content, encoding="utf-8")
    return plan


def _make_plan_no_manifest(tmp_path, dc_block, filename="plan.md"):
    plan = tmp_path / filename
    plan.write_text(
        f"# Plan\n\n## Drafting Cycle\n{dc_block}\n## End\n",
        encoding="utf-8",
    )
    return plan


# ---------- Test 1: missing key → CONTINUE, not BAR_MET ----------

def test_manifest_missing_key_returns_continue(tmp_path):
    """Gate fires when validation: omits a key the emitter writes (regression case)."""
    plan = _make_plan_with_manifest(
        tmp_path, _BAR_MET_DC,
        # propagation_check= is absent — the exact defect in diagnostic-100032
        "cycle_check=BAR_MET, plan_lint=0_FAIL, fold_check=PASS",
    )
    verdict, code = cycle_check.run_check(plan)
    assert verdict == "CONTINUE"
    assert code == 0


# ---------- Test 2: full key set → BAR_MET unaffected ----------

def test_manifest_full_key_set_bar_met(tmp_path):
    """Gate does not fire when all MANIFEST_VALIDATION_KEYS are present."""
    plan = _make_plan_with_manifest(tmp_path, _BAR_MET_DC, _FULL_VALIDATION)
    verdict, code = cycle_check.run_check(plan)
    assert verdict == "BAR_MET"
    assert code == 0


# ---------- Test 3: no stanza → gate does not fire ----------

def test_no_stanza_gate_does_not_fire(tmp_path):
    """No ## Cycle Manifest stanza → gate silent; BAR_MET reachable normally."""
    plan = _make_plan_no_manifest(tmp_path, _BAR_MET_DC)
    verdict, code = cycle_check.run_check(plan)
    assert verdict == "BAR_MET"
    assert code == 0


# ---------- Test 4: stale values do not trigger the gate (P7) ----------

def test_stale_values_do_not_fire(tmp_path):
    """Keys present but values deliberately wrong: gate must NOT fire (P7 — values drift)."""
    plan = _make_plan_with_manifest(
        tmp_path, _BAR_MET_DC,
        "cycle_check=CONTINUE, plan_lint=3_FAIL, fold_check=N/A, propagation_check=DIVERGENT:999",
    )
    verdict, code = cycle_check.run_check(plan)
    assert verdict == "BAR_MET"
    assert code == 0


# ---------- Test 5: key set derived from MANIFEST_VALIDATION_KEYS, not hardcoded ----------

def test_key_set_derived_from_emitter_constant(tmp_path):
    """Patch MANIFEST_VALIDATION_KEYS to add a fifth key; gate fires without editing this test."""
    augmented = cycle_check.MANIFEST_VALIDATION_KEYS | {"extra_key"}
    # Plan carries the original four keys — missing the patched-in fifth
    plan = _make_plan_with_manifest(tmp_path, _BAR_MET_DC, _FULL_VALIDATION)
    with patch.object(cycle_check, "MANIFEST_VALIDATION_KEYS", augmented):
        verdict, code = cycle_check.run_check(plan)
    assert verdict == "CONTINUE"
    assert code == 0


# ---------- Test 6: validation: N/A → gate does not fire ----------

def test_validation_na_does_not_fire(tmp_path):
    """validation: N/A is the emitter's no-walk-data fallback; gate must not fire."""
    plan = _make_plan_with_manifest(tmp_path, _BAR_MET_DC, "N/A")
    verdict, code = cycle_check.run_check(plan)
    assert verdict == "BAR_MET"
    assert code == 0


# ---------- Test 6b: validation: <declare> → gate does not fire ----------

def test_validation_declare_does_not_fire(tmp_path):
    """validation: <declare> is written mid-emission; gate must not block it."""
    plan = _make_plan_with_manifest(tmp_path, _BAR_MET_DC, "<declare>")
    verdict, code = cycle_check.run_check(plan)
    assert verdict == "BAR_MET"
    assert code == 0


# ---------- Test 6c: empty validation: → gate does not fire ----------

def test_validation_empty_does_not_fire(tmp_path):
    """Empty validation: does not trigger the gate."""
    plan = _make_plan_with_manifest(tmp_path, _BAR_MET_DC, "")
    verdict, code = cycle_check.run_check(plan)
    assert verdict == "BAR_MET"
    assert code == 0


# ---------- Test 7: no subprocess added on the normal path ----------

def test_no_subprocess_spawned(tmp_path):
    """The manifest key-set gate adds zero subprocess launches (cycle_check runs constantly)."""
    # Baseline: same DC block, no manifest stanza
    plan_no_stanza = _make_plan_no_manifest(tmp_path, _BAR_MET_DC, "baseline.md")
    # Gate-firing plan: manifest with missing key
    plan_missing_key = _make_plan_with_manifest(
        tmp_path, _BAR_MET_DC,
        "cycle_check=BAR_MET, plan_lint=0_FAIL, fold_check=PASS",
        "gate.md",
    )

    original_run = subprocess.run
    calls = {"baseline": 0, "gate": 0}

    def counter_baseline(*args, **kwargs):
        calls["baseline"] += 1
        return original_run(*args, **kwargs)

    def counter_gate(*args, **kwargs):
        calls["gate"] += 1
        return original_run(*args, **kwargs)

    with patch.object(subprocess, "run", side_effect=counter_baseline):
        cycle_check.run_check(plan_no_stanza)

    with patch.object(subprocess, "run", side_effect=counter_gate):
        cycle_check.run_check(plan_missing_key)

    # The gate must not add any subprocess calls beyond the baseline
    assert calls["gate"] == calls["baseline"]
