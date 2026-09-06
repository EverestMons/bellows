"""The acceptance seam consumes §2.7's observer (2026-09-06).

CEO architecture: the drafting cycle is separate from bellows, and DC's pass/fail is
what bellows reads to accept a plan. lens_order_check is the observer §2.7 appointed;
depositor._rerun_validation is where bellows consumes its verdict.

⛔ ONLY A PROVEN BREACH HOLDS. NO-RECORD (exit 2) is absence of evidence, not a
refusal: of the 19 plans passing cycle_check and plan_lint on 2026-09-06, 18 were
NO-RECORD and ZERO were clean, so holding on absence would stop every deposit.
"""
import pathlib
import subprocess
import sys
from types import SimpleNamespace

import pytest

BELLOWS_ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BELLOWS_ROOT))
sys.path.insert(0, str(BELLOWS_ROOT / "scripts"))

import depositor as depositor_mod  # noqa: E402


def _dep():
    d = depositor_mod.Depositor.__new__(depositor_mod.Depositor)
    d._bellows_root = BELLOWS_ROOT
    return d


def _stub_run(returncode, stdout=""):
    def _run(cmd, **kw):
        script = str(cmd[1])
        if script.endswith("lens_order_check.py"):
            return SimpleNamespace(returncode=returncode, stdout=stdout, stderr="")
        return SimpleNamespace(returncode=0, stdout="", stderr="")
    return _run


@pytest.fixture
def passing_plan(monkeypatch):
    """cycle_check BAR_MET and plan_lint clean, so the lens_order step is REACHED."""
    monkeypatch.setattr(depositor_mod.cycle_check, "run_check",
                        lambda p: ("BAR_MET", 0))
    monkeypatch.setattr(depositor_mod.cycle_check, "parse_manifest_stanza",
                        lambda t: {})
    return pathlib.Path("plan.md")


def test_proven_breach_HOLDS(monkeypatch, passing_plan):
    out = ("BASIS: tier=T1\n"
           "BATCHED: walk 2 — a419bbd names lenses [2, 3] in ONE commit\n"
           "INCOMPLETE: walk 1 — closed walk proves lenses [1]\n")
    monkeypatch.setattr(depositor_mod.subprocess, "run", _stub_run(1, out))
    r = _dep()._rerun_validation(passing_plan, "text")
    assert r["hold"] is True
    assert r["reason"] == "lens_order:2_breach", r
    assert r["lens_order"] == "breach_2"


def test_NO_RECORD_does_not_hold(monkeypatch, passing_plan):
    """⛔ Absence of evidence is recorded, never converted into a refusal."""
    monkeypatch.setattr(depositor_mod.subprocess, "run", _stub_run(2, ""))
    r = _dep()._rerun_validation(passing_plan, "text")
    assert r["hold"] is False, r
    assert r["lens_order"] == "no_record"
    assert r["reason"] == ""


def test_clean_record_passes(monkeypatch, passing_plan):
    monkeypatch.setattr(depositor_mod.subprocess, "run",
                        _stub_run(0, "LENS-ORDER OK — 5 lens commit(s)\n"))
    r = _dep()._rerun_validation(passing_plan, "text")
    assert r["hold"] is False
    assert r["lens_order"] == "exit_0"


def test_a_broken_observer_neither_accepts_nor_blocks(monkeypatch, passing_plan):
    """⛔ A gate that fails open is a fail-open; a gate that blocks on its own crash
    stops the lane. Record the exception and let the other gates decide."""
    def _boom(cmd, **kw):
        if str(cmd[1]).endswith("lens_order_check.py"):
            raise OSError("no git")
        return SimpleNamespace(returncode=0, stdout="", stderr="")
    monkeypatch.setattr(depositor_mod.subprocess, "run", _boom)
    r = _dep()._rerun_validation(passing_plan, "text")
    assert r["hold"] is False
    assert r["lens_order"].startswith("exception:"), r


def test_earlier_gates_short_circuit_before_lens_order(monkeypatch):
    """cycle_check runs FIRST; a plan it holds must never reach the observer."""
    monkeypatch.setattr(depositor_mod.cycle_check, "run_check",
                        lambda p: ("CONTINUE", 1))
    called = {"n": 0}

    def _count(cmd, **kw):
        called["n"] += 1
        return SimpleNamespace(returncode=0, stdout="", stderr="")
    monkeypatch.setattr(depositor_mod.subprocess, "run", _count)
    r = _dep()._rerun_validation(pathlib.Path("plan.md"), "text")
    assert r["hold"] is True
    assert r["reason"] == "cycle_check:CONTINUE"
    assert r["lens_order"] is None, "the observer ran despite an earlier hold"
    assert called["n"] == 0
