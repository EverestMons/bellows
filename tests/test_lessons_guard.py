"""Tests for tools/lessons_guard.py — guard (a) made mechanical (thread 137).

⛔ Every fixture is a SYNTHETIC shop under tmp_path. No test may create a
plan-shaped file under a real knowledge/decisions/ directory — that is the
standing incident mandate, and a stray executable-*.md in a watched lane is a
dispatchable plan.
"""

import hashlib
import subprocess
import sys
from pathlib import Path

import pytest

BELLOWS_ROOT = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(BELLOWS_ROOT / "tools"))

import lessons_guard as lg  # noqa: E402


def _shop(tmp_path, lane_files=(), lessons_text="# LESSONS\n\n## 2026-01-01: a\n"):
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


@pytest.mark.parametrize("name,freezes", [
    # deposited-but-un-run: these freeze
    ("executable-100031.md", True),
    ("diagnostic-582.md", True),
    ("qa-thing.md", True),
    ("hold-executable-100031.md", True),
    ("ready-executable-100031.md", True),
    ("parallel-2-executable-x.md", True),
    # doctrine names these two explicitly / by the window they span
    ("in-progress-executable-100031.md", True),
    ("verdict-pending-executable-100031.md", True),
    # PARKED, not pending — doctrine: a halted-* artifact does not freeze
    ("halted-executable-100031.md", False),
    ("parked-executable-100031.md", False),
    ("obsolete-executable-fuel.md", False),
    # share the lane but are not cycle plans
    ("roadmap-codebase-health-2026-04-03.md", False),
    ("runbook-floor-only-migration.md", False),
    ("sa-blueprint-action-queue.md", False),
    ("reporting-phase2-cycle-query.md", False),
])
def test_freeze_predicate_table(tmp_path, name, freezes):
    shop = _shop(tmp_path, lane_files=[name])
    got = [p.name for p in lg.freezing_plans(shop)]
    assert (name in got) is freezes, f"{name}: expected freezes={freezes}, got {got}"


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
