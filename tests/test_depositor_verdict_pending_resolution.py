"""An awaiting_verdict plan's file must resolve — thread 93.

Measured 2026-09-02: staging a plan while 100023 sat in awaiting_verdict produced
`hold_reason unresolvable_in_flight`. The paused plan's file is
`verdict-pending-<base>` (bellows.py:1092) and none of the depositor's three
candidates named it, so NO plan could deposit for the whole length of any verdict
pause — and the hold read as a resolution failure rather than as a wait.
"""
import os
import sqlite3
import sys
from pathlib import Path

import pytest

BELLOWS_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BELLOWS_ROOT))

import depositor  # noqa: E402

_PLAN = """# bellows — executable: in flight

**Date:** 2026-09-06 | **Project:** bellows

## Cycle Manifest
class: shop-infra
writes: bellows/tools/paused_thing.py

## STEP 1 — do it
"""


def _db(tmp_path, plan_id, plan_type, state, placeholder):
    """⛔ The REAL schema, via lifecycle.init_lifecycle_db. A hand-rolled `plans`
    table omitted NOT NULL columns the live one has (created_at), and every insert
    failed — a fixture testing an invented database rather than this one."""
    import lifecycle
    db = str(tmp_path / "lifecycle.db")
    lifecycle.init_lifecycle_db(db)
    c = sqlite3.connect(db)
    c.execute("INSERT INTO plans (id, type, target_project, deposit_placeholder_name,"
              " plan_doc_ref, lifecycle_state, created_at) VALUES (?,?,?,?,?,?,?)",
              (plan_id, plan_type, "", placeholder, None, state, "2026-09-06T00:00:00"))
    c.commit(); c.close()
    return db


def _dep(decisions, db):
    return depositor.Depositor(
        disk_preflight_fn=lambda cfg: True,
        shutting_down_check=lambda: False,
        config={"watched_projects": [decisions]},
        lifecycle_db_path=db,
    )


def test_a_paused_plan_resolves_by_its_verdict_pending_name(tmp_path):
    """⛔ The defect. Only the verdict-pending- file exists on disk."""
    d = tmp_path / "decisions"; d.mkdir()
    (d / "verdict-pending-executable-100023.md").write_text(_PLAN)
    db = _db(tmp_path, 100023, "executable", "awaiting_verdict", "executable-100023.md")
    got = _dep(str(d), db)._resolve_in_flight_writes()
    assert got is not None, "the paused plan did not resolve — every deposit would hold"
    # ⚠️ the return is a list of DICTS ({writes, project_root, label}), not of
    # write strings — the first cut of this assertion iterated dicts and failed
    # against correct code.
    assert any("paused_thing.py" in w for e in got for w in e["writes"]), got
    assert got[0]["label"] == "in-flight:#100023", got


def test_a_SLUG_named_paused_plan_also_resolves(tmp_path):
    """⚠️ The thread's own suggested fix — add `verdict-pending-<type>-<id>.md` — would
    MISS this. bellows builds the pause name from the plan's BASE FILENAME, and the two
    forms coincide only for id-named plans."""
    d = tmp_path / "decisions"; d.mkdir()
    (d / "verdict-pending-executable-my-slug.md").write_text(_PLAN)
    db = _db(tmp_path, 555, "executable", "awaiting_verdict", "executable-my-slug.md")
    got = _dep(str(d), db)._resolve_in_flight_writes()
    assert got is not None, "a slug-named paused plan did not resolve"


def test_an_in_progress_plan_still_resolves(tmp_path):
    """The original candidate must keep working."""
    d = tmp_path / "decisions"; d.mkdir()
    (d / "in-progress-executable-100024.md").write_text(_PLAN)
    db = _db(tmp_path, 100024, "executable", "in_progress", "executable-100024.md")
    assert _dep(str(d), db)._resolve_in_flight_writes() is not None


def test_a_genuinely_missing_file_still_fails_SHUT_and_names_the_plan(tmp_path):
    """⛔ Fail-SHUT is kept deliberately: without the file we cannot know the plan's
    writes, so admitting would be a fail-open in the very gate that catches overlaps.
    But the hold must now say WHICH plan and what was tried."""
    d = tmp_path / "decisions"; d.mkdir()
    db = _db(tmp_path, 777, "executable", "awaiting_verdict", "executable-777.md")
    dep = _dep(str(d), db)
    dep._unresolved_in_flight = None
    assert dep._resolve_in_flight_writes() is None
    assert dep._unresolved_in_flight is not None
    assert "777" in dep._unresolved_in_flight
    assert "awaiting_verdict" in dep._unresolved_in_flight
    assert "verdict-pending-" in dep._unresolved_in_flight, dep._unresolved_in_flight


def test_halted_and_parked_are_not_candidates(tmp_path):
    """A halted plan is PARKED, not pending — and the query selects only
    in_progress / claimed / awaiting_verdict, so a halted- file must not resolve one."""
    d = tmp_path / "decisions"; d.mkdir()
    (d / "halted-executable-888.md").write_text(_PLAN)
    db = _db(tmp_path, 888, "executable", "awaiting_verdict", "executable-888.md")
    assert _dep(str(d), db)._resolve_in_flight_writes() is None
