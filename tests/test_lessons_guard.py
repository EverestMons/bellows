"""Tests for tools/lessons_guard.py — guard (a) made mechanical (thread 137).

⛔ Every fixture is a SYNTHETIC shop under tmp_path. No test may create a
plan-shaped file under a real knowledge/decisions/ directory — that is the
standing incident mandate, and a stray executable-*.md in a watched lane is a
dispatchable plan.
"""

import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pytest

BELLOWS_ROOT = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(BELLOWS_ROOT / "tools"))

import lessons_guard as lg  # noqa: E402


def _shop(tmp_path, lane_files=(), sidecars=None, lessons_text="# LESSONS\n\n## 2026-01-01: a\n"):
    """A synthetic shop: eleven flat repos plus governance's nested lane."""
    (tmp_path / "eluvian-governance").mkdir()
    gov_lane = tmp_path / "eluvian-governance" / "governance" / "knowledge" / "decisions"
    gov_lane.mkdir(parents=True)
    bell_lane = tmp_path / "bellows" / "knowledge" / "decisions"
    bell_lane.mkdir(parents=True)
    (bell_lane / "Done").mkdir()
    (bell_lane / "drafts").mkdir()
    for name in lane_files:
        (bell_lane / name).write_text("plan body\n")
    if sidecars:
        for name, data in sidecars.items():
            sidecar_name = name[:-3] + ".hold.json"
            content = json.dumps(data) if isinstance(data, dict) else data
            (bell_lane / sidecar_name).write_text(content)
    (tmp_path / "eluvian-governance" / "LESSONS.md").write_text(lessons_text)
    return tmp_path


def _env(monkeypatch, shop):
    monkeypatch.setenv("ELUVIAN_SHOP_ROOT", str(shop))
    monkeypatch.setenv("ELUVIAN_LESSONS", str(shop / "eluvian-governance" / "LESSONS.md"))
    monkeypatch.delenv("ELUVIAN_WRAP_ROOT", raising=False)


def test_lanes_found_at_both_depths(tmp_path, monkeypatch):
    """⛔ The governance lane nests one level deeper than every other repo's.

    A single-depth glob misses it; rooted AT governance (which wrap_check.py is),
    the enumeration sees exactly one lane out of twelve."""
    shop = _shop(tmp_path)
    lanes = lg.decision_lanes(shop)
    names = {str(p.relative_to(shop)) for p in lanes}
    assert "bellows/knowledge/decisions" in names, "flat repo lane missed"
    assert "eluvian-governance/governance/knowledge/decisions" in names, "nested lane missed"
    assert len(lanes) == 2


class TestFreezePredicateTable:
    @pytest.mark.parametrize("name,freezes,sidecar", [
        # deposited-but-un-run: these freeze
        ("executable-100031.md", True, None),
        ("diagnostic-582.md", True, None),
        ("qa-thing.md", True, None),
        pytest.param("hold-executable-100031.md", True, None, id="t-d"),
        ("ready-executable-100031.md", True, None),
        ("parallel-2-executable-x.md", True, None),
        # doctrine names these two explicitly / by the window they span
        ("in-progress-executable-100031.md", True, None),
        ("verdict-pending-executable-100031.md", True, None),
        # PARKED, not pending — doctrine: a halted-* artifact does not freeze
        ("halted-executable-100031.md", False, None),
        ("parked-executable-100031.md", False, None),
        ("obsolete-executable-fuel.md", False, None),
        # share the lane but are not cycle plans
        ("roadmap-codebase-health-2026-04-03.md", False, None),
        ("runbook-floor-only-migration.md", False, None),
        ("sa-blueprint-action-queue.md", False, None),
        ("reporting-phase2-cycle-query.md", False, None),
        # new rows: class sidecar → parked (not frozen)
        pytest.param(
            "hold-executable-100031.md", False,
            {"hold_reason": "class:shop-infra", "held_at": "2026-09-11T00:00:00", "class_assigned": "shop-infra"},
            id="t-a",
        ),
        # stale-checkout sidecar → still freezes
        pytest.param("hold-executable-100031.md", True, {"hold_reason": "stale-checkout"}, id="t-b"),
        # held_pending_ceo_release → still freezes
        pytest.param("hold-executable-100031.md", True, {"hold_reason": "held_pending_ceo_release"}, id="t-c"),
        # sidecar is not JSON → fail-closed, freezes
        pytest.param("hold-executable-100031.md", True, "not-json", id="t-e"),
        # parallel-N-hold- with class sidecar → parked (not frozen)
        pytest.param("parallel-2-hold-executable-x.md", False, {"hold_reason": "class:shop-infra"}, id="t-f"),
    ])
    def test_row(self, tmp_path, name, freezes, sidecar):
        sidecars = {name: sidecar} if sidecar is not None else None
        shop = _shop(tmp_path, lane_files=[name], sidecars=sidecars)
        got = [p.name for p in lg.freezing_plans(shop)]
        assert (name in got) is freezes, f"{name}: expected freezes={freezes}, got {got}"

    def test_parked_class_holds(self, tmp_path):
        """t-g: parked_class_holds returns exactly the class-held paths."""
        sidecar = {"hold_reason": "class:shop-infra", "held_at": "2026-09-11T00:00:00", "class_assigned": "shop-infra"}
        shop = _shop(
            tmp_path,
            lane_files=["hold-executable-100031.md"],
            sidecars={"hold-executable-100031.md": sidecar},
        )
        parked = lg.parked_class_holds(shop)
        assert len(parked) == 1
        assert parked[0].name == "hold-executable-100031.md"
        assert lg.freezing_plans(shop) == []

    def test_pin_class_hold_not_frozen(self, tmp_path):
        """t-h: pin with one class hold prints class-held: 1 and exits 0."""
        sidecar = {"hold_reason": "class:shop-infra", "held_at": "2026-09-11T00:00:00", "class_assigned": "shop-infra"}
        shop = _shop(
            tmp_path,
            lane_files=["hold-executable-100031.md"],
            sidecars={"hold-executable-100031.md": sidecar},
        )
        r = _run(shop, "pin")
        assert r.returncode == 0, r.stderr
        assert "class-held: 1" in r.stdout
        assert "frozen: no" in r.stdout

    def test_pin_frozen_names_only_stale(self, tmp_path):
        """t-i: pin with class hold + stale hold → exit 2, FROZEN names only stale."""
        class_sidecar = {"hold_reason": "class:shop-infra", "held_at": "2026-09-11T00:00:00", "class_assigned": "shop-infra"}
        stale_sidecar = {"hold_reason": "stale-checkout"}
        shop = _shop(
            tmp_path,
            lane_files=["hold-executable-100031.md", "hold-executable-100032.md"],
            sidecars={
                "hold-executable-100031.md": class_sidecar,
                "hold-executable-100032.md": stale_sidecar,
            },
        )
        r = _run(shop, "pin")
        assert r.returncode == 2
        assert "FROZEN" in r.stderr
        assert "hold-executable-100032.md" in r.stderr
        assert "hold-executable-100031.md" not in r.stderr


def test_done_and_drafts_do_not_freeze(tmp_path):
    """Only files sitting DIRECTLY in the lane count: Done/ is complete,
    drafts/ is not deposited."""
    shop = _shop(tmp_path)
    lane = shop / "bellows" / "knowledge" / "decisions"
    (lane / "Done" / "executable-999.md").write_text("done\n")
    (lane / "drafts" / "executable-888.md").write_text("draft\n")
    assert lg.freezing_plans(shop) == []


def _run(shop, *args):
    env = {"ELUVIAN_SHOP_ROOT": str(shop),
           "ELUVIAN_LESSONS": str(shop / "eluvian-governance" / "LESSONS.md"),
           "PATH": "/usr/bin:/bin"}
    return subprocess.run([sys.executable, str(BELLOWS_ROOT / "tools" / "lessons_guard.py"), *args],
                          capture_output=True, text=True, env=env)


def test_pin_refuses_when_frozen(tmp_path):
    shop = _shop(tmp_path, lane_files=["executable-100031.md"])
    r = _run(shop, "pin")
    assert r.returncode == 2, r.stdout
    assert "FROZEN" in r.stderr
    assert "executable-100031.md" in r.stderr


def test_verify_refuses_when_sha_moved(tmp_path):
    """⛔ The defect thread 137 reports: the guard is taken once and never re-taken,
    so a writer arriving in the window is invisible. Two live incidents on
    2026-09-04 were exactly this."""
    shop = _shop(tmp_path)
    lessons = shop / "eluvian-governance" / "LESSONS.md"
    pin = _run(shop, "pin")
    assert pin.returncode == 0
    sha = pin.stdout.strip().split("\n")[-1]

    # another writer appends between the pin and the write
    with open(lessons, "a") as f:
        f.write("\n## 2026-01-02: appended by another session\n")

    r = _run(shop, "verify", "--sha", sha)
    assert r.returncode == 2, r.stdout
    assert "moved since the pin" in r.stderr


def test_verify_refuses_when_a_plan_lands_in_the_window(tmp_path):
    """The other half: the corpus can FREEZE between the pin and the write."""
    shop = _shop(tmp_path)
    pin = _run(shop, "pin")
    sha = pin.stdout.strip().split("\n")[-1]
    lane = shop / "bellows" / "knowledge" / "decisions"
    (lane / "executable-100031.md").write_text("deposited in the window\n")
    r = _run(shop, "verify", "--sha", sha)
    assert r.returncode == 2
    assert "FROZEN" in r.stderr


def test_verify_passes_when_nothing_moved(tmp_path):
    shop = _shop(tmp_path)
    pin = _run(shop, "pin")
    sha = pin.stdout.strip().split("\n")[-1]
    r = _run(shop, "verify", "--sha", sha)
    assert r.returncode == 0, r.stderr
    assert "safe to write NOW" in r.stdout
