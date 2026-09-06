"""_resolve_register_ref — ONE resolver, and the shop-root step (thread 153).

The two machine layouts put bellows on opposite sides of the governance root:
    shop : <root>/{COMPANY.md, bellows/, ...}          — bellows UNDER the root
    mini : ~/Developer/{eluvian-governance/, bellows/} — bellows BESIDE it
A ref written `bellows/knowledge/research/<file>` is correct under the shop shape and
unresolvable on the mini. Measured 2026-09-06: 22 plans carry it — 18 Done/, 4 halted —
all failing here while the file sits on disk.
"""
import subprocess
import sys
from pathlib import Path

import pytest

BELLOWS_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BELLOWS_ROOT / "scripts"))
sys.path.insert(0, str(BELLOWS_ROOT))

import cycle_check as cc  # noqa: E402


def _mini(tmp_path):
    """The MINI shape: governance root and bellows as SIBLINGS."""
    gov = tmp_path / "eluvian-governance"
    gov.mkdir()
    (gov / "COMPANY.md").write_text("co\n")
    reg = tmp_path / "bellows" / "knowledge" / "research"
    reg.mkdir(parents=True)
    (reg / "walk-register-x.md").write_text("# reg\n\n## Walk 1 — lenses\n")
    plans = tmp_path / "bellows" / "knowledge" / "decisions" / "Done"
    plans.mkdir(parents=True)
    subprocess.run(["git", "init", "-q", str(tmp_path / "bellows")],
                   capture_output=True, check=True)
    plan = plans / "executable-543.md"
    plan.write_text("x")
    return gov, plan


def test_shop_root_step_resolves_a_bellows_prefixed_ref(monkeypatch, tmp_path):
    """⛔ The 22. Under the mini shape the ref needs the governance root's PARENT."""
    gov, plan = _mini(tmp_path)
    import bellows_root
    monkeypatch.setattr(bellows_root, "resolve_governance_root", lambda: gov)
    got = cc._resolve_register_ref("bellows/knowledge/research/walk-register-x.md", plan)
    assert got is not None, "the shop-root step did not fire"
    assert got.exists() and got.name == "walk-register-x.md"


def test_both_consumers_use_the_same_resolver(monkeypatch, tmp_path):
    """⛔ There were TWO resolvers. Adding the shop-root step to check_assert_2 alone
    left _compute_coherence still reporting 'does not resolve' for the same file —
    the ship-one-copy class. This pins that they agree."""
    gov, plan = _mini(tmp_path)
    import bellows_root
    monkeypatch.setattr(bellows_root, "resolve_governance_root", lambda: gov)
    ref = "bellows/knowledge/research/walk-register-x.md"
    parsed = {"walk_register_ref": ref, "walk_data": {1: {}}, "walk_status": {}}

    assert cc._resolve_register_ref(ref, plan) is not None
    coh = cc._compute_coherence(parsed, plan)
    assert not coh.startswith("N/A"), f"coherence disagrees with the resolver: {coh}"


def test_an_absolute_ref_still_resolves_directly(tmp_path):
    f = tmp_path / "walk-register-abs.md"; f.write_text("# reg\n")
    plan = tmp_path / "p.md"; plan.write_text("x")
    assert cc._resolve_register_ref(str(f), plan) == f


def test_an_absolute_ref_that_does_not_exist_returns_None(tmp_path):
    plan = tmp_path / "p.md"; plan.write_text("x")
    assert cc._resolve_register_ref(str(tmp_path / "nope.md"), plan) is None


def test_a_genuinely_unresolvable_relative_ref_returns_None(monkeypatch, tmp_path):
    gov, plan = _mini(tmp_path)
    import bellows_root
    monkeypatch.setattr(bellows_root, "resolve_governance_root", lambda: gov)
    assert cc._resolve_register_ref("bellows/knowledge/research/absent.md", plan) is None


def test_an_oversized_path_component_does_not_raise(monkeypatch, tmp_path):
    """C-2 (thread 52): an oversized component raises OSError from exists(); the
    resolver must return None, never propagate."""
    gov, plan = _mini(tmp_path)
    import bellows_root
    monkeypatch.setattr(bellows_root, "resolve_governance_root", lambda: gov)
    assert cc._resolve_register_ref("bellows/" + "z" * 500 + "/x.md", plan) is None
