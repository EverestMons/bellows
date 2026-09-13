"""Tests for tools/reconcile_steps.py — LIST, --apply, and in-flight guard."""
import os
import shutil
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
    """t9: --apply flips closed/awaiting row and abandoned/running row; halted unchanged."""
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
    assert statuses[4] == "abandoned"


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


def test_apply_moves_running_step_on_abandoned_plan(tmp_path):
    """r-t1: --apply moves a running step on an abandoned plan; running on halted stays."""
    db = _make_db(tmp_path)
    result = _run(["--apply"], db)
    assert result.returncode == 0
    conn = sqlite3.connect(db)
    rows = conn.execute("SELECT plan_id, status FROM steps ORDER BY plan_id").fetchall()
    conn.close()
    statuses = {r[0]: r[1] for r in rows}
    assert statuses[4] == "abandoned"
    assert statuses[1] == "complete"


def _make_old_steps_db(tmp_path):
    """Build a database with today's steps DDL (no 'abandoned' in CHECK) for migration tests."""
    db = str(tmp_path / "old.db")
    conn = sqlite3.connect(db)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS id_sequence (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            next_id INTEGER NOT NULL DEFAULT 1
        )
    """)
    conn.execute("INSERT OR IGNORE INTO id_sequence (id, next_id) VALUES (1, 200)")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS plans (
            id INTEGER PRIMARY KEY,
            type TEXT NOT NULL CHECK (type IN ('diagnostic', 'executable', 'qa')),
            target_project TEXT NOT NULL,
            title TEXT,
            dispatch_mode TEXT,
            tier TEXT,
            lifecycle_state TEXT NOT NULL DEFAULT 'claimed'
                CHECK (lifecycle_state IN ('claimed','in_progress','awaiting_verdict','closed','halted','abandoned')),
            total_steps INTEGER,
            deposit_placeholder_name TEXT,
            created_at TEXT NOT NULL,
            closed_at TEXT,
            plan_doc_ref TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS steps (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            plan_id INTEGER NOT NULL REFERENCES plans(id),
            step_number INTEGER NOT NULL,
            role TEXT,
            status TEXT NOT NULL DEFAULT 'pending'
                CHECK (status IN ('pending','running','awaiting_verdict','complete')),
            step_started_at TEXT,
            step_ended_at TEXT,
            cost_usd REAL,
            turns INTEGER,
            duration_s REAL,
            log_ref TEXT,
            UNIQUE(plan_id, step_number)
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS commits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            step_id INTEGER NOT NULL REFERENCES steps(id),
            repo TEXT NOT NULL,
            sha TEXT NOT NULL,
            message_ref TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS deposits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            step_id INTEGER NOT NULL REFERENCES steps(id),
            declared_path TEXT NOT NULL,
            type TEXT,
            landed INTEGER NOT NULL DEFAULT 0
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS verdicts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            plan_id INTEGER NOT NULL REFERENCES plans(id),
            step_number INTEGER NOT NULL,
            outcome TEXT,
            pause_reason_code TEXT,
            decided_by TEXT,
            verdict_file_ref TEXT,
            disposition_summary TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS gate_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            step_id INTEGER NOT NULL REFERENCES steps(id),
            gate_name TEXT NOT NULL,
            result TEXT NOT NULL CHECK (result IN ('pass', 'fail')),
            reason_code TEXT,
            overridden INTEGER NOT NULL DEFAULT 0,
            override_ref TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS step_files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            step_id INTEGER NOT NULL REFERENCES steps(id),
            path TEXT NOT NULL,
            UNIQUE(step_id, path)
        )
    """)
    conn.execute(
        "INSERT INTO plans (id, type, target_project, lifecycle_state, total_steps, created_at) "
        "VALUES (10, 'executable', '/proj', 'closed', 1, '2026-09-11')"
    )
    conn.execute("INSERT INTO steps (plan_id, step_number, status) VALUES (10, 1, 'awaiting_verdict')")
    conn.commit()
    conn.close()
    return db


def test_apply_migrates_old_db_before_writing(tmp_path):
    """r-t2: --apply migrates a database with today's DDL before flipping rows."""
    db = _make_old_steps_db(tmp_path)
    result = _run(["--apply"], db)
    assert result.returncode == 0
    conn = sqlite3.connect(db)
    ddl = conn.execute(
        "SELECT sql FROM sqlite_master WHERE type='table' AND name='steps'"
    ).fetchone()[0]
    status = conn.execute("SELECT status FROM steps WHERE plan_id=10").fetchone()[0]
    conn.close()
    assert "'abandoned'" in ddl
    assert status == "complete"


def test_apply_with_named_db_does_not_write_default(tmp_path):
    """r-t3: --db <test-db> --apply writes only the named db; the default db (with old DDL) unchanged."""
    import sys as _sys
    from unittest.mock import patch as _patch

    (tmp_path / "d1").mkdir()
    (tmp_path / "d2").mkdir()
    test_db = _make_old_steps_db(tmp_path / "d1")
    src_db = _make_old_steps_db(tmp_path / "d2")
    default_db = str(tmp_path / "default.db")
    shutil.copy(src_db, default_db)

    with _patch.object(_sys, "argv", ["reconcile_steps.py", "--db", test_db, "--apply"]):
        with _patch("lifecycle.LIFECYCLE_DB_PATH", default_db):
            import tools.reconcile_steps as rs
            import importlib
            importlib.reload(rs)
            rs.main()

    conn = sqlite3.connect(default_db)
    ddl = conn.execute(
        "SELECT sql FROM sqlite_master WHERE type='table' AND name='steps'"
    ).fetchone()[0]
    conn.close()
    assert "'abandoned'" not in ddl, "default db must not be migrated"


def test_apply_abandoned_pass_no_awaiting_rows(tmp_path):
    """r-t4: database with no closed/awaiting row and one running on abandoned → abandoned moved."""
    db = str(tmp_path / "r4.db")
    import lifecycle as lc
    lc.init_lifecycle_db(db)
    conn = sqlite3.connect(db)
    conn.execute("INSERT OR REPLACE INTO id_sequence (id, next_id) VALUES (1, 300)")
    conn.execute(
        "INSERT INTO plans (id, type, target_project, lifecycle_state, total_steps, created_at) "
        "VALUES (20, 'executable', '/proj', 'abandoned', 1, '2026-09-11')"
    )
    conn.execute("INSERT INTO steps (plan_id, step_number, status) VALUES (20, 1, 'running')")
    conn.commit()
    conn.close()
    result = _run(["--apply"], db)
    assert result.returncode == 0
    conn = sqlite3.connect(db)
    status = conn.execute("SELECT status FROM steps WHERE plan_id=20").fetchone()[0]
    conn.close()
    assert status == "abandoned"
