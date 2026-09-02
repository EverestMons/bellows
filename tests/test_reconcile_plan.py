"""Tests for tools/reconcile_plan.py — six cases over a tmp lifecycle.db."""

import os
import shutil
import sqlite3
import subprocess
import sys
import tempfile

import pytest

TOOL = os.path.join(os.path.dirname(__file__), os.pardir, "tools", "reconcile_plan.py")

PLANS_DDL = """
CREATE TABLE plans (
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
);
"""

VERDICTS_DDL = """
CREATE TABLE verdicts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    plan_id INTEGER NOT NULL REFERENCES plans(id),
    step_number INTEGER NOT NULL,
    outcome TEXT,
    pause_reason_code TEXT,
    decided_by TEXT,
    verdict_file_ref TEXT,
    disposition_summary TEXT
);
"""


def _make_env(tmp):
    """Create a tmp subdir with lifecycle.db + verdicts/pending + verdicts/archived."""
    tmp = os.path.join(tmp, "reconcile_env")
    os.makedirs(tmp, exist_ok=True)
    db_path = os.path.join(tmp, "lifecycle.db")
    conn = sqlite3.connect(db_path)
    conn.execute(PLANS_DDL)
    conn.execute(VERDICTS_DDL)
    conn.commit()
    pending = os.path.join(tmp, "verdicts", "pending")
    archived = os.path.join(tmp, "verdicts", "archived")
    os.makedirs(pending, exist_ok=True)
    os.makedirs(archived, exist_ok=True)
    return db_path, conn, pending, archived


def _run(args, db_path):
    return subprocess.run(
        [sys.executable, TOOL] + args + ["--db", db_path],
        capture_output=True, text=True,
    )


def _dump_table(db_path, table):
    conn = sqlite3.connect(db_path)
    rows = conn.execute(f"SELECT * FROM {table}").fetchall()
    conn.close()
    return rows


class TestReconcilePlan:
    def test_full_reconcile_halted(self, tmp_path):
        """Test 1: full reconcile of a halted target."""
        db_path, conn, pending, archived = _make_env(str(tmp_path))
        conn.execute(
            "INSERT INTO plans (id, type, target_project, lifecycle_state, created_at) "
            "VALUES (42, 'executable', 'bellows', 'awaiting_verdict', '2026-01-01T00:00:00Z')")
        conn.execute(
            "INSERT INTO verdicts (plan_id, step_number, outcome, decided_by, disposition_summary) "
            "VALUES (42, 1, NULL, NULL, NULL)")
        conn.commit()

        req_file = os.path.join(pending, "verdict-request-42-step-1.md")
        with open(req_file, "w") as f:
            f.write("request content\n")

        conn.close()

        result = _run(["42", "halted", "--outcome", "stop", "--summary", "orphan recovery",
                        "--killed-verified"], db_path)
        assert result.returncode == 0

        check_conn = sqlite3.connect(db_path)
        plan = check_conn.execute("SELECT lifecycle_state, closed_at FROM plans WHERE id = 42").fetchone()
        assert plan[0] == "halted"
        assert plan[1] is not None

        verdict = check_conn.execute("SELECT outcome, decided_by, disposition_summary FROM verdicts WHERE plan_id = 42").fetchone()
        assert verdict[0] == "stop"
        assert verdict[1] == "planner"
        assert verdict[2] == "orphan recovery"
        check_conn.close()

        assert os.path.exists(os.path.join(archived, "verdict-request-42-step-1.md"))
        assert not os.path.exists(req_file)

    def test_in_progress_refused_without_flag(self, tmp_path):
        """Test 2: in_progress WITHOUT --killed-verified -> exit 3, DB unchanged."""
        db_path, conn, pending, archived = _make_env(str(tmp_path))
        conn.execute(
            "INSERT INTO plans (id, type, target_project, lifecycle_state, created_at) "
            "VALUES (10, 'executable', 'bellows', 'in_progress', '2026-01-01T00:00:00Z')")
        conn.execute(
            "INSERT INTO verdicts (plan_id, step_number, outcome) VALUES (10, 1, NULL)")
        conn.commit()
        conn.close()

        plans_before = _dump_table(db_path, "plans")
        verdicts_before = _dump_table(db_path, "verdicts")

        result = _run(["10", "closed", "--outcome", "stop", "--summary", "test"], db_path)
        assert result.returncode == 3

        plans_after = _dump_table(db_path, "plans")
        verdicts_after = _dump_table(db_path, "verdicts")
        assert plans_before == plans_after
        assert verdicts_before == verdicts_after

    def test_in_progress_with_killed_verified(self, tmp_path):
        """Test 3: in_progress WITH --killed-verified -> proceeds."""
        db_path, conn, pending, archived = _make_env(str(tmp_path))
        conn.execute(
            "INSERT INTO plans (id, type, target_project, lifecycle_state, created_at) "
            "VALUES (11, 'executable', 'bellows', 'in_progress', '2026-01-01T00:00:00Z')")
        conn.execute(
            "INSERT INTO verdicts (plan_id, step_number, outcome) VALUES (11, 1, NULL)")
        conn.commit()
        conn.close()

        result = _run(["11", "abandoned", "--outcome", "stop", "--summary", "killed",
                        "--killed-verified"], db_path)
        assert result.returncode == 0

        check_conn = sqlite3.connect(db_path)
        plan = check_conn.execute("SELECT lifecycle_state FROM plans WHERE id = 11").fetchone()
        assert plan[0] == "abandoned"
        check_conn.close()

    def test_zero_null_outcome_verdicts(self, tmp_path):
        """Test 4: plan with ZERO null-outcome verdicts -> rowcount 0, exit 0."""
        db_path, conn, pending, archived = _make_env(str(tmp_path))
        conn.execute(
            "INSERT INTO plans (id, type, target_project, lifecycle_state, created_at) "
            "VALUES (20, 'executable', 'bellows', 'awaiting_verdict', '2026-01-01T00:00:00Z')")
        conn.commit()
        conn.close()

        result = _run(["20", "closed", "--outcome", "continue", "--summary", "clean",
                        "--killed-verified"], db_path)
        assert result.returncode == 0
        assert "verdicts rows updated (NULL-outcome): 0" in result.stdout

    def test_terminal_verdict_untouched(self, tmp_path):
        """Test 5: a TERMINAL-outcome verdict row is NEVER touched."""
        db_path, conn, pending, archived = _make_env(str(tmp_path))
        conn.execute(
            "INSERT INTO plans (id, type, target_project, lifecycle_state, created_at) "
            "VALUES (30, 'executable', 'bellows', 'awaiting_verdict', '2026-01-01T00:00:00Z')")
        conn.execute(
            "INSERT INTO verdicts (plan_id, step_number, outcome, decided_by, disposition_summary) "
            "VALUES (30, 1, 'continue', 'ceo', 'original summary')")
        conn.execute(
            "INSERT INTO verdicts (plan_id, step_number, outcome) VALUES (30, 2, NULL)")
        conn.commit()
        conn.close()

        result = _run(["30", "closed", "--outcome", "stop", "--summary", "reconcile",
                        "--killed-verified"], db_path)
        assert result.returncode == 0

        check_conn = sqlite3.connect(db_path)
        terminal = check_conn.execute(
            "SELECT outcome, decided_by, disposition_summary FROM verdicts "
            "WHERE plan_id = 30 AND step_number = 1").fetchone()
        assert terminal[0] == "continue"
        assert terminal[1] == "ceo"
        assert terminal[2] == "original summary"

        reconciled = check_conn.execute(
            "SELECT outcome, decided_by, disposition_summary FROM verdicts "
            "WHERE plan_id = 30 AND step_number = 2").fetchone()
        assert reconciled[0] == "stop"
        assert reconciled[1] == "planner"
        check_conn.close()

    def test_bad_state_vocab(self, tmp_path):
        """Test 6: bad state vocab -> exit 2 usage."""
        db_path, conn, pending, archived = _make_env(str(tmp_path))
        conn.close()

        result = _run(["99", "bogus", "--outcome", "stop", "--summary", "x"], db_path)
        assert result.returncode == 2

    def test_awaiting_verdict_refused_without_flag(self, tmp_path):
        """R1: awaiting_verdict WITHOUT --killed-verified -> exit 3, DB unchanged."""
        db_path, conn, pending, archived = _make_env(str(tmp_path))
        conn.execute(
            "INSERT INTO plans (id, type, target_project, lifecycle_state, created_at) "
            "VALUES (50, 'executable', 'bellows', 'awaiting_verdict', '2026-09-01T00:00:00Z')")
        conn.execute(
            "INSERT INTO verdicts (plan_id, step_number, outcome) VALUES (50, 1, NULL)")
        conn.commit()
        conn.close()

        plans_before = _dump_table(db_path, "plans")
        result = _run(["50", "closed", "--outcome", "stop", "--summary", "test"], db_path)
        assert result.returncode == 3
        plans_after = _dump_table(db_path, "plans")
        assert plans_before == plans_after

    def test_awaiting_verdict_with_killed_verified(self, tmp_path):
        """R1: awaiting_verdict WITH --killed-verified -> proceeds."""
        db_path, conn, pending, archived = _make_env(str(tmp_path))
        conn.execute(
            "INSERT INTO plans (id, type, target_project, lifecycle_state, created_at) "
            "VALUES (51, 'executable', 'bellows', 'awaiting_verdict', '2026-09-01T00:00:00Z')")
        conn.execute(
            "INSERT INTO verdicts (plan_id, step_number, outcome) VALUES (51, 1, NULL)")
        conn.commit()
        conn.close()

        result = _run(["51", "abandoned", "--outcome", "stop", "--summary", "killed",
                        "--killed-verified"], db_path)
        assert result.returncode == 0

        check_conn = sqlite3.connect(db_path)
        plan = check_conn.execute("SELECT lifecycle_state FROM plans WHERE id = 51").fetchone()
        assert plan[0] == "abandoned"
        check_conn.close()
