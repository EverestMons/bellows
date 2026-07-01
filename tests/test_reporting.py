"""Tests for reporting.py — cycle query module (Reporting Phase 2)."""

import sqlite3

import pytest
import lifecycle
import reporting


def _seed_db(tmp_path):
    """Initialize lifecycle.db at tmp_path and return the path string."""
    db_path = str(tmp_path / "reporting_test.db")
    lifecycle.init_lifecycle_db(db_path)
    return db_path


def _insert_plan(conn, plan_id, plan_type, project, closed_at):
    conn.execute(
        "INSERT INTO plans (id, type, target_project, created_at, closed_at, lifecycle_state) "
        "VALUES (?, ?, ?, '2026-06-01T00:00:00', ?, 'closed')",
        (plan_id, plan_type, project, closed_at),
    )


def _insert_step(conn, plan_id, step_number, cost_usd, turns):
    conn.execute(
        "INSERT INTO steps (plan_id, step_number, status, cost_usd, turns) "
        "VALUES (?, ?, 'complete', ?, ?)",
        (plan_id, step_number, cost_usd, turns),
    )


class TestMultiStepPlanCount:
    """Test 1: multi-step executable — plan count not inflated by step rows."""

    def test_single_plan_with_three_steps_counts_as_one(self, tmp_path):
        db_path = _seed_db(tmp_path)
        conn = sqlite3.connect(db_path)
        _insert_plan(conn, 1, "executable", "/proj/alpha", "2026-06-15T12:00:00")
        _insert_step(conn, 1, 1, 0.50, 10)
        _insert_step(conn, 1, 2, 0.75, 15)
        _insert_step(conn, 1, 3, 0.25, 5)
        conn.commit()
        conn.close()

        result = reporting.query_cycle_report(db_path, "2026-06-01", "2026-07-01")
        assert len(result) == 1
        assert result[0]["plan_count"] == 1
        assert result[0]["plan_count"] != 3


class TestCostTurnSums:
    """Test 2: cost/turn SUMs match hand-computed values."""

    def test_sums_match_expected(self, tmp_path):
        db_path = _seed_db(tmp_path)
        conn = sqlite3.connect(db_path)
        # diagnostic plan with 1 step
        _insert_plan(conn, 1, "diagnostic", "/proj/alpha", "2026-06-10T10:00:00")
        _insert_step(conn, 1, 1, 1.25, 20)
        # executable plan with 2 steps
        _insert_plan(conn, 2, "executable", "/proj/alpha", "2026-06-12T14:00:00")
        _insert_step(conn, 2, 1, 0.80, 12)
        _insert_step(conn, 2, 2, 0.45, 8)
        conn.commit()
        conn.close()

        result = reporting.query_cycle_report(db_path, "2026-06-01", "2026-07-01")
        by_type = {r["type"]: r for r in result}

        # diagnostic: 1 plan, cost=1.25, turns=20
        assert by_type["diagnostic"]["plan_count"] == 1
        assert by_type["diagnostic"]["total_cost_usd"] == pytest.approx(1.25)
        assert by_type["diagnostic"]["total_turns"] == 20

        # executable: 1 plan, cost=0.80+0.45=1.25, turns=12+8=20
        assert by_type["executable"]["plan_count"] == 1
        assert by_type["executable"]["total_cost_usd"] == pytest.approx(1.25)
        assert by_type["executable"]["total_turns"] == 20


class TestEmptyRange:
    """Test 3: empty range returns empty list, not an error."""

    def test_no_plans_returns_empty_list(self, tmp_path):
        db_path = _seed_db(tmp_path)
        conn = sqlite3.connect(db_path)
        _insert_plan(conn, 1, "diagnostic", "/proj", "2026-06-15T12:00:00")
        _insert_step(conn, 1, 1, 0.50, 10)
        conn.commit()
        conn.close()

        result = reporting.query_cycle_report(db_path, "2026-01-01", "2026-02-01")
        assert result == []

    def test_empty_db_returns_empty_list(self, tmp_path):
        db_path = _seed_db(tmp_path)
        result = reporting.query_cycle_report(db_path, "2026-06-01", "2026-07-01")
        assert result == []


class TestHalfOpenBoundary:
    """Test 4: [start, end) — plan at end is excluded, plan at start is included."""

    def test_plan_at_end_excluded(self, tmp_path):
        db_path = _seed_db(tmp_path)
        conn = sqlite3.connect(db_path)
        _insert_plan(conn, 1, "diagnostic", "/proj", "2026-07-01T00:00:00")
        _insert_step(conn, 1, 1, 0.50, 10)
        conn.commit()
        conn.close()

        result = reporting.query_cycle_report(db_path, "2026-06-01", "2026-07-01T00:00:00")
        assert result == []

    def test_plan_at_start_included(self, tmp_path):
        db_path = _seed_db(tmp_path)
        conn = sqlite3.connect(db_path)
        _insert_plan(conn, 1, "diagnostic", "/proj", "2026-06-01T00:00:00")
        _insert_step(conn, 1, 1, 0.50, 10)
        conn.commit()
        conn.close()

        result = reporting.query_cycle_report(db_path, "2026-06-01T00:00:00", "2026-07-01")
        assert len(result) == 1
        assert result[0]["plan_count"] == 1


class TestGrouping:
    """Test 5: groups by target_project and type."""

    def test_multiple_projects_and_types(self, tmp_path):
        db_path = _seed_db(tmp_path)
        conn = sqlite3.connect(db_path)
        _insert_plan(conn, 1, "diagnostic", "/proj/alpha", "2026-06-10T10:00:00")
        _insert_step(conn, 1, 1, 0.50, 5)
        _insert_plan(conn, 2, "executable", "/proj/alpha", "2026-06-11T10:00:00")
        _insert_step(conn, 2, 1, 1.00, 10)
        _insert_plan(conn, 3, "diagnostic", "/proj/beta", "2026-06-12T10:00:00")
        _insert_step(conn, 3, 1, 0.75, 8)
        _insert_plan(conn, 4, "executable", "/proj/beta", "2026-06-13T10:00:00")
        _insert_step(conn, 4, 1, 2.00, 20)
        conn.commit()
        conn.close()

        result = reporting.query_cycle_report(db_path, "2026-06-01", "2026-07-01")
        assert len(result) == 4
        # Verify ordering: alpha/diagnostic, alpha/executable, beta/diagnostic, beta/executable
        assert result[0]["target_project"] == "/proj/alpha"
        assert result[0]["type"] == "diagnostic"
        assert result[1]["target_project"] == "/proj/alpha"
        assert result[1]["type"] == "executable"
        assert result[2]["target_project"] == "/proj/beta"
        assert result[2]["type"] == "diagnostic"
        assert result[3]["target_project"] == "/proj/beta"
        assert result[3]["type"] == "executable"


class TestReadOnlyAccess:
    """Test 6: reporting.py does not import daemon internals."""

    def test_no_daemon_imports(self):
        import ast
        import inspect

        source = inspect.getsource(reporting)
        tree = ast.parse(source)
        imported_names = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imported_names.add(alias.name.split(".")[0])
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported_names.add(node.module.split(".")[0])
        daemon_modules = {"bellows", "runner", "parser", "gates", "verdict", "planner", "server", "notifier"}
        violations = imported_names & daemon_modules
        assert not violations, f"reporting.py imports daemon modules: {violations}"
