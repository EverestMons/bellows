"""Thread 162 — an in-flight plan that declares NO writes must not block every deposit.

A read-only diagnostic in flight has no writes by design. _resolve_in_flight_writes
returned None for it, and the caller holds EVERY new deposit as
unresolvable_in_flight — a fail-shut on the whole lane, not a collision.
"""
import os, sqlite3, sys
from pathlib import Path
import pytest
BELLOWS_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BELLOWS_ROOT))
import depositor  # noqa: E402

_DIAG_NO_WRITES = """# bellows — diagnostic: read-only census
**Date:** 2026-09-07 | **Project:** bellows

## Cycle Manifest
tier: T0
target: bellows/scripts/x.py
class: read-only
reads: bellows/scripts/x.py
writes:
open_forks: none

## STEP 1 — count things

> Read the corpus and report.
"""

def _db(tmp_path, plan_id, plan_type, state, placeholder):
    import lifecycle
    db = str(tmp_path / "lifecycle.db")
    lifecycle.init_lifecycle_db(db)
    c = sqlite3.connect(db)
    c.execute("INSERT INTO plans (id, type, target_project, deposit_placeholder_name,"
              " plan_doc_ref, lifecycle_state, created_at) VALUES (?,?,?,?,?,?,?)",
              (plan_id, plan_type, "", placeholder, None, state, "2026-09-07T00:00:00"))
    c.commit(); c.close()
    return db

def _dep(tmp_path, db, watched):
    d = depositor.Depositor.__new__(depositor.Depositor)
    d._db_path = db
    d._watched_dirs = lambda: [str(watched)]
    d._unresolved_in_flight = None
    d._bellows_root = BELLOWS_ROOT
    return d

def test_in_flight_diagnostic_with_no_writes_is_an_empty_set_not_a_hold(tmp_path):
    watched = tmp_path / "decisions"; watched.mkdir()
    (watched / "in-progress-diagnostic-7.md").write_text(_DIAG_NO_WRITES)
    db = _db(tmp_path, 7, "diagnostic", "in_progress", "diagnostic-7.md")
    d = _dep(tmp_path, db, watched)
    result = d._resolve_in_flight_writes()
    assert result is not None, f"lane blocked by a read-only plan: {d._unresolved_in_flight!r}"
    assert result == [] or all(r["writes"] == [] for r in result)

def test_in_flight_file_with_no_plan_structure_still_holds_and_names_the_plan(tmp_path):
    watched = tmp_path / "decisions"; watched.mkdir()
    (watched / "in-progress-executable-9.md").write_text("garbage — no manifest, no steps\n")
    db = _db(tmp_path, 9, "executable", "in_progress", "executable-9.md")
    d = _dep(tmp_path, db, watched)
    assert d._resolve_in_flight_writes() is None
    assert d._unresolved_in_flight and "9" in d._unresolved_in_flight
