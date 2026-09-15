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

STEPS_DDL = """
CREATE TABLE steps (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    plan_id INTEGER NOT NULL REFERENCES plans(id),
    step_number INTEGER NOT NULL,
    role TEXT,
    status TEXT NOT NULL DEFAULT 'pending'
        CHECK (status IN ('pending','running','awaiting_verdict','complete','abandoned')),
    step_started_at TEXT,
    step_ended_at TEXT,
    cost_usd REAL,
    turns INTEGER,
    duration_s REAL,
    log_ref TEXT,
    daemon_pid INTEGER,
    UNIQUE(plan_id, step_number)
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
    conn.execute(STEPS_DDL)
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


def _insert_plan(conn, plan_id, state, placeholder=None, project="bellows",
                 plan_type="executable"):
    conn.execute(
        "INSERT INTO plans (id, type, target_project, lifecycle_state, created_at,"
        " deposit_placeholder_name) VALUES (?, ?, ?, ?, '2026-01-01T00:00:00Z', ?)",
        (plan_id, plan_type, project, state, placeholder),
    )
    conn.commit()


def _insert_step(conn, plan_id, step_number, status):
    conn.execute(
        "INSERT INTO steps (plan_id, step_number, status) VALUES (?, ?, ?)",
        (plan_id, step_number, status),
    )
    conn.commit()


def _steps(db_path, plan_id):
    conn = sqlite3.connect(db_path)
    rows = conn.execute(
        "SELECT step_number, status, step_ended_at FROM steps"
        " WHERE plan_id = ? ORDER BY step_number",
        (plan_id,),
    ).fetchall()
    conn.close()
    return rows


def _lane(root, *filenames):
    for fn in filenames:
        path = os.path.join(root, "knowledge", "decisions", fn)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            f.write("")
    return root


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


class TestReconcileStepsClaimLane:
    @pytest.mark.parametrize("state", ["closed", "halted", "abandoned"])
    def test_running_step_abandoned_on_every_target(self, tmp_path, state):
        db_path, conn, _, _ = _make_env(str(tmp_path))
        _insert_plan(conn, 1, "claimed")
        _insert_step(conn, 1, 1, "running")
        _insert_step(conn, 1, 2, "complete")
        conn.close()

        result = _run(["1", state, "--outcome", "continue", "--summary", "test"], db_path)
        assert result.returncode == 0

        rows = _steps(db_path, 1)
        row1 = next(r for r in rows if r[0] == 1)
        row2 = next(r for r in rows if r[0] == 2)
        assert row1[1] == "abandoned"
        assert row1[2] is not None
        assert row2[1] == "complete"
        assert "running→abandoned 1" in result.stdout

    def test_awaiting_verdict_step_completed_when_closed(self, tmp_path):
        db_path, conn, _, _ = _make_env(str(tmp_path))
        _insert_plan(conn, 1, "claimed")
        _insert_step(conn, 1, 1, "awaiting_verdict")
        conn.close()

        result = _run(["1", "closed", "--outcome", "continue", "--summary", "test"], db_path)
        assert result.returncode == 0

        rows = _steps(db_path, 1)
        assert rows[0][1] == "complete"
        assert "awaiting_verdict→complete 1" in result.stdout

    @pytest.mark.parametrize("state", ["halted", "abandoned"])
    def test_awaiting_verdict_step_kept_when_halted_or_abandoned(self, tmp_path, state):
        db_path, conn, _, _ = _make_env(str(tmp_path))
        _insert_plan(conn, 1, "claimed")
        _insert_step(conn, 1, 1, "awaiting_verdict")
        conn.close()

        result = _run(["1", state, "--outcome", "stop", "--summary", "test"], db_path)
        assert result.returncode == 0

        rows = _steps(db_path, 1)
        assert rows[0][1] == "awaiting_verdict"

    def test_other_plans_steps_untouched(self, tmp_path):
        db_path, conn, _, _ = _make_env(str(tmp_path))
        _insert_plan(conn, 1, "claimed")
        _insert_plan(conn, 2, "claimed")
        _insert_step(conn, 1, 1, "running")
        _insert_step(conn, 2, 1, "running")
        conn.close()

        result = _run(["1", "closed", "--outcome", "continue", "--summary", "test"], db_path)
        assert result.returncode == 0

        rows2 = _steps(db_path, 2)
        assert rows2[0][1] == "running"

    @pytest.mark.parametrize("state", ["closed", "halted", "abandoned"])
    def test_step_marks_mirror_lifecycle_writers(self, tmp_path, state):
        import lifecycle as _lc

        db1 = str(tmp_path / "db1.db")
        db2 = str(tmp_path / "db2.db")
        _lc.init_lifecycle_db(db1)
        _lc.init_lifecycle_db(db2)

        for db in (db1, db2):
            c = sqlite3.connect(db)
            c.execute(
                "INSERT INTO plans (id, type, target_project, lifecycle_state, created_at)"
                " VALUES (1, 'executable', 'bellows', 'claimed', '2026-01-01T00:00:00Z')"
            )
            c.execute(
                "INSERT INTO steps (plan_id, step_number, status) VALUES (1, 1, 'running')"
            )
            if state == "closed":
                c.execute(
                    "INSERT INTO steps (plan_id, step_number, status)"
                    " VALUES (1, 2, 'awaiting_verdict')"
                )
            c.commit()
            c.close()

        result = _run(["1", state, "--outcome", "continue", "--summary", "test"], db1)
        assert result.returncode == 0

        _lc.mark_step_abandoned(1, db_path=db2)
        if state == "closed":
            _lc.mark_step_complete(1, 2, db_path=db2)

        rows1 = [(r[0], r[1]) for r in _steps(db1, 1)]
        rows2 = [(r[0], r[1]) for r in _steps(db2, 1)]
        assert rows1 == rows2

    def test_prints_the_claim_release_for_the_placeholder(self, tmp_path):
        db_path, conn, _, _ = _make_env(str(tmp_path))
        _insert_plan(conn, 99, "claimed", placeholder="executable-99.md")
        conn.close()

        result = _run(["99", "abandoned", "--outcome", "stop", "--summary", "test"], db_path)
        assert result.returncode == 0
        assert 'tuyere.claims release executable-99 --reason "reconcile: abandoned"' in result.stdout

    def test_no_placeholder_no_release_command(self, tmp_path):
        db_path, conn, _, _ = _make_env(str(tmp_path))
        _insert_plan(conn, 99, "claimed", placeholder=None)
        conn.close()

        result = _run(["99", "abandoned", "--outcome", "stop", "--summary", "test"], db_path)
        assert result.returncode == 0
        assert "no deposit placeholder recorded" in result.stdout

    @pytest.mark.parametrize("state,destination", [
        ("closed", "knowledge/decisions/Done/executable-99.md"),
        ("halted", "knowledge/decisions/halted-executable-99.md"),
        ("abandoned", "knowledge/decisions/Done/abandoned-executable-99.md"),
    ])
    def test_lane_move_names_the_real_source_and_the_convention(
            self, tmp_path, state, destination):
        db_path, conn, _, _ = _make_env(str(tmp_path))
        root = os.path.realpath(os.path.dirname(db_path))
        _insert_plan(conn, 99, "claimed")
        conn.close()
        _lane(root, "in-progress-executable-99.md")

        result = _run(["99", state, "--outcome", "continue", "--summary", "test"], db_path)
        assert result.returncode == 0

        source = "knowledge/decisions/in-progress-executable-99.md"
        assert f"git -C {root} mv {source} {destination}" in result.stdout
        assert f"-- {source} {destination}" in result.stdout
        assert f"git -C {root} mv knowledge/decisions/executable-99.md " not in result.stdout

    def test_verdict_pending_source_located(self, tmp_path):
        db_path, conn, _, _ = _make_env(str(tmp_path))
        root = os.path.realpath(os.path.dirname(db_path))
        _insert_plan(conn, 99, "claimed")
        conn.close()
        _lane(root, "verdict-pending-executable-99.md")

        result = _run(["99", "closed", "--outcome", "continue", "--summary", "test"], db_path)
        assert result.returncode == 0

        source = "knowledge/decisions/verdict-pending-executable-99.md"
        destination = "knowledge/decisions/Done/executable-99.md"
        assert f"git -C {root} mv {source} {destination}" in result.stdout

    def test_missing_lane_file_is_reported_not_moved(self, tmp_path):
        db_path, conn, _, _ = _make_env(str(tmp_path))
        _insert_plan(conn, 99, "claimed")
        conn.close()

        result = _run(["99", "closed", "--outcome", "continue", "--summary", "test"], db_path)
        assert result.returncode == 0
        assert "lane file NOT FOUND" in result.stdout
        assert " mv " not in result.stdout
        assert "commit" not in result.stdout

    def test_file_already_at_the_destination(self, tmp_path):
        db_path, conn, _, _ = _make_env(str(tmp_path))
        root = os.path.realpath(os.path.dirname(db_path))
        _insert_plan(conn, 99, "claimed")
        conn.close()
        _lane(root, "Done/executable-99.md")

        result = _run(["99", "closed", "--outcome", "continue", "--summary", "test"], db_path)
        assert result.returncode == 0
        assert "already at" in result.stdout
        assert " mv " not in result.stdout
        assert "commit" not in result.stdout

    def test_steps_rows_printed_before_any_write(self, tmp_path):
        db_path, conn, _, _ = _make_env(str(tmp_path))
        _insert_plan(conn, 1, "in_progress")
        _insert_step(conn, 1, 1, "complete")
        _insert_step(conn, 1, 2, "running")
        conn.close()

        result = _run(["1", "closed", "--outcome", "continue", "--summary", "test"], db_path)
        assert result.returncode == 3
        assert "=== Steps rows (2) ===" in result.stdout
        assert "step 2: running" in result.stdout

        rows = _steps(db_path, 1)
        row2 = next(r for r in rows if r[0] == 2)
        assert row2[1] == "running"

        result2 = _run(["1", "closed", "--outcome", "continue", "--summary", "test",
                        "--killed-verified"], db_path)
        assert result2.returncode == 0
        idx_steps = result2.stdout.index("=== Steps rows")
        idx_tx = result2.stdout.index("=== Transaction complete")
        assert idx_steps < idx_tx
