"""Tests for tools/reconcile_steps.py — LIST, --apply, and in-flight guard."""
import os
import sqlite3
import subprocess
import sys

import pytest
import lifecycle

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RECONCILE = os.path.join(REPO_ROOT, "tools", "reconcile_steps.py")
PYTHON = sys.executable


def _make_db(tmp_path):
    db = str(tmp_path / "test.db")
    lifecycle.init_lifecycle_db(db)
    conn = sqlite3.connect(db)
    conn.execute("INSERT INTO id_sequence (id, next_id) VALUES (1, 200) ON CONFLICT DO UPDATE SET next_id=200")
    # closed plan with awaiting_verdict step (the target for --apply)
    conn.execute(
        "INSERT INTO plans (id, type, target_project, lifecycle_state, total_steps, created_at) "
        "VALUES (1, 'executable', '/proj', 'closed', 1, '2026-09-11')"
    )
    conn.execute("INSERT INTO steps (plan_id, step_number, status) VALUES (1, 1, 'awaiting_verdict')")
    # halted plan with awaiting_verdict step (must NOT be flipped by --apply)
    conn.execute(
        "INSERT INTO plans (id, type, target_project, lifecycle_state, total_steps, created_at) "
        "VALUES (2, 'executable', '/proj', 'halted', 1, '2026-09-11')"
    )
    conn.execute("INSERT INTO steps (plan_id, step_number, status) VALUES (2, 1, 'awaiting_verdict')")
    # closed plan with complete step (should appear in LIST, untouched)
    conn.execute(
        "INSERT INTO plans (id, type, target_project, lifecycle_state, total_steps, created_at) "
        "VALUES (3, 'executable', '/proj', 'closed', 1, '2026-09-11')"
    )
    conn.execute("INSERT INTO steps (plan_id, step_number, status) VALUES (3, 1, 'complete')")
    # abandoned plan with running step (phantom — listed, never touched)
    conn.execute(
        "INSERT INTO plans (id, type, target_project, lifecycle_state, total_steps, created_at) "
        "VALUES (4, 'executable', '/proj', 'abandoned', 1, '2026-09-11')"
    )
    conn.execute("INSERT INTO steps (plan_id, step_number, status) VALUES (4, 1, 'running')")
    conn.commit()
    conn.close()
    return db


def _run(args, db):
    return subprocess.run(
        [PYTHON, RECONCILE, "--db", db] + args,
        capture_output=True, text=True,
    )


def test_list_prints_groups_writes_nothing(tmp_path):
    """t8: LIST (no flag) prints awaiting_verdict rows by group; statuses unchanged."""
    db = _make_db(tmp_path)
    result = _run([], db)
    assert result.returncode == 0
    out = result.stdout
    # closed awaiting row
    assert "closed" in out
    # halted awaiting row
    assert "halted" in out
    conn = sqlite3.connect(db)
    rows = conn.execute("SELECT plan_id, status FROM steps ORDER BY plan_id").fetchall()
    conn.close()
    statuses = {r[0]: r[1] for r in rows}
    assert statuses[1] == "awaiting_verdict"
    assert statuses[2] == "awaiting_verdict"
    assert statuses[3] == "complete"
    assert statuses[4] == "running"


def test_apply_flips_only_closed_awaiting(tmp_path):
    """t9: --apply flips only the closed/awaiting row; halted and running rows unchanged."""
    db = _make_db(tmp_path)
    result = _run(["--apply"], db)
    assert result.returncode == 0
    conn = sqlite3.connect(db)
    rows = conn.execute("SELECT plan_id, status FROM steps ORDER BY plan_id").fetchall()
    conn.close()
    statuses = {r[0]: r[1] for r in rows}
    assert statuses[1] == "complete"
    assert statuses[2] == "awaiting_verdict"
    assert statuses[3] == "complete"
    assert statuses[4] == "running"


def test_apply_refuses_when_in_progress(tmp_path):
    """t10: --apply exits non-zero and writes nothing when a plan is in_progress."""
    db = _make_db(tmp_path)
    conn = sqlite3.connect(db)
    conn.execute(
        "INSERT INTO plans (id, type, target_project, lifecycle_state, total_steps, created_at) "
        "VALUES (5, 'executable', '/proj', 'in_progress', 1, '2026-09-11')"
    )
    conn.commit()
    conn.close()
    result = _run(["--apply"], db)
    assert result.returncode != 0
    out = result.stdout + result.stderr
    assert "5" in out
    conn = sqlite3.connect(db)
    status = conn.execute("SELECT status FROM steps WHERE plan_id=1").fetchone()[0]
    conn.close()
    assert status == "awaiting_verdict"
