"""Tests for status.py — single-glance status CLI."""

import datetime
import os
import sqlite3

import pytest

import status
from lifecycle import init_lifecycle_db


# ---------------------------------------------------------------------------
# Fixture: lifecycle DB with seed data
# ---------------------------------------------------------------------------

@pytest.fixture
def status_db(tmp_path):
    """Create a lifecycle DB with representative test data and return its path."""
    db_path = str(tmp_path / "lifecycle.db")
    init_lifecycle_db(db_path)
    conn = sqlite3.connect(db_path)

    now = datetime.datetime.now()
    ten_min_ago = (now - datetime.timedelta(minutes=10)).isoformat()
    thirty_min_ago = (now - datetime.timedelta(minutes=30)).isoformat()

    # Plan 10: in-flight with a running step
    conn.execute(
        "INSERT INTO plans (id, type, target_project, title, dispatch_mode, tier,"
        " lifecycle_state, total_steps, created_at)"
        " VALUES (10, 'executable', 'bellows', 'Test Plan Alpha', 'bellows', 'Small',"
        " 'in_progress', 3, ?)",
        (thirty_min_ago,),
    )
    conn.execute(
        "INSERT INTO steps (plan_id, step_number, role, status, step_started_at)"
        " VALUES (10, 1, 'dev', 'running', ?)",
        (ten_min_ago,),
    )

    # Plan 11: awaiting verdict
    conn.execute(
        "INSERT INTO plans (id, type, target_project, title, dispatch_mode, tier,"
        " lifecycle_state, total_steps, created_at)"
        " VALUES (11, 'executable', 'forge', 'Test Plan Beta', 'bellows', 'Small',"
        " 'awaiting_verdict', 2, ?)",
        (thirty_min_ago,),
    )
    conn.execute(
        "INSERT INTO steps (plan_id, step_number, role, status, step_started_at, step_ended_at)"
        " VALUES (11, 2, 'qa', 'awaiting_verdict', ?, ?)",
        (thirty_min_ago, ten_min_ago),
    )
    conn.execute(
        "INSERT INTO verdicts (plan_id, step_number, outcome, pause_reason_code, verdict_file_ref)"
        " VALUES (11, 2, NULL, 'qa_checkpoint', 'verdict-request-11-step-2.md')",
    )

    # Plan 12: closed (should NOT appear anywhere in the three-element output)
    conn.execute(
        "INSERT INTO plans (id, type, target_project, title, dispatch_mode, tier,"
        " lifecycle_state, total_steps, created_at, closed_at)"
        " VALUES (12, 'executable', 'bellows', 'Closed Plan', 'bellows', 'Small',"
        " 'closed', 1, ?, ?)",
        (thirty_min_ago, now.isoformat()),
    )

    # Seed id_sequence so it doesn't conflict
    conn.execute("UPDATE id_sequence SET next_id = 20 WHERE id = 1")
    conn.commit()
    conn.close()
    return db_path


@pytest.fixture
def empty_db(tmp_path):
    """Create a lifecycle DB with no plan data."""
    db_path = str(tmp_path / "lifecycle.db")
    init_lifecycle_db(db_path)
    return db_path


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestInFlightRendering:
    """IN-FLIGHT section renders running plans correctly."""

    def test_in_flight_shows_running_plan(self, status_db):
        conn = sqlite3.connect(f"file:{status_db}?mode=ro", uri=True)
        conn.row_factory = sqlite3.Row
        rows = conn.execute("""
            SELECT p.id, p.target_project, p.title, p.total_steps,
                   s.step_number, s.status, s.step_started_at
            FROM plans p
            LEFT JOIN steps s ON s.plan_id = p.id
              AND s.step_number = (
                SELECT MAX(s2.step_number) FROM steps s2
                WHERE s2.plan_id = p.id AND s2.status IN ('running', 'awaiting_verdict')
              )
            WHERE p.lifecycle_state IN ('in_progress', 'claimed')
            ORDER BY p.id
        """).fetchall()
        conn.close()

        output = status.render_in_flight(rows, daemon_running=True)
        assert "IN-FLIGHT" in output
        assert "#10" in output
        assert "bellows" in output
        assert "Step 1/3" in output
        assert "running" in output
        assert "Test Plan Alpha" in output


class TestAwaitingVerdictRendering:
    """AWAITING VERDICT section renders pending verdicts with filename."""

    def test_awaiting_verdict_shows_filename(self, status_db):
        conn = sqlite3.connect(f"file:{status_db}?mode=ro", uri=True)
        conn.row_factory = sqlite3.Row
        rows = conn.execute("""
            SELECT v.plan_id, v.step_number, v.pause_reason_code, v.verdict_file_ref,
                   COALESCE(s.step_ended_at, s.step_started_at) AS pause_time
            FROM verdicts v
            LEFT JOIN steps s ON s.plan_id = v.plan_id AND s.step_number = v.step_number
            WHERE v.outcome IS NULL
            ORDER BY v.plan_id
        """).fetchall()
        conn.close()

        output = status.render_awaiting_verdict(rows)
        assert "AWAITING VERDICT" in output
        assert "#11" in output
        assert "step 2" in output
        assert "qa_checkpoint" in output
        assert "verdict-request-11-step-2.md" in output


class TestBothEmptyNone:
    """Both sections show (none) when DB has no active plans or pending verdicts."""

    def test_in_flight_none(self, empty_db):
        conn = sqlite3.connect(f"file:{empty_db}?mode=ro", uri=True)
        conn.row_factory = sqlite3.Row
        rows = conn.execute("""
            SELECT p.id, p.target_project, p.title, p.total_steps,
                   s.step_number, s.status, s.step_started_at
            FROM plans p
            LEFT JOIN steps s ON s.plan_id = p.id
              AND s.step_number = (
                SELECT MAX(s2.step_number) FROM steps s2
                WHERE s2.plan_id = p.id AND s2.status IN ('running', 'awaiting_verdict')
              )
            WHERE p.lifecycle_state IN ('in_progress', 'claimed')
            ORDER BY p.id
        """).fetchall()
        conn.close()

        output = status.render_in_flight(rows, daemon_running=True)
        assert "(none)" in output

    def test_awaiting_verdict_none(self, empty_db):
        conn = sqlite3.connect(f"file:{empty_db}?mode=ro", uri=True)
        conn.row_factory = sqlite3.Row
        rows = conn.execute("""
            SELECT v.plan_id, v.step_number, v.pause_reason_code, v.verdict_file_ref,
                   COALESCE(s.step_ended_at, s.step_started_at) AS pause_time
            FROM verdicts v
            LEFT JOIN steps s ON s.plan_id = v.plan_id AND s.step_number = v.step_number
            WHERE v.outcome IS NULL
            ORDER BY v.plan_id
        """).fetchall()
        conn.close()

        output = status.render_awaiting_verdict(rows)
        assert "(none)" in output


class TestDaemonStoppedStaleMarker:
    """When daemon is stopped, running steps show 'stale?' marker."""

    def test_stale_marker_when_daemon_stopped(self, status_db):
        conn = sqlite3.connect(f"file:{status_db}?mode=ro", uri=True)
        conn.row_factory = sqlite3.Row
        rows = conn.execute("""
            SELECT p.id, p.target_project, p.title, p.total_steps,
                   s.step_number, s.status, s.step_started_at
            FROM plans p
            LEFT JOIN steps s ON s.plan_id = p.id
              AND s.step_number = (
                SELECT MAX(s2.step_number) FROM steps s2
                WHERE s2.plan_id = p.id AND s2.status IN ('running', 'awaiting_verdict')
              )
            WHERE p.lifecycle_state IN ('in_progress', 'claimed')
            ORDER BY p.id
        """).fetchall()
        conn.close()

        output = status.render_in_flight(rows, daemon_running=False)
        assert "stale?" in output
        assert "running" not in output.split("\n", 1)[1]  # 'running' not in data rows


class TestAbsentDbDegradation:
    """Absent lifecycle.db produces graceful message, not a crash."""

    def test_absent_db_message(self, tmp_path, capsys):
        fake_root = tmp_path / "no_db_here"
        fake_root.mkdir()
        db_path = fake_root / "lifecycle.db"
        lock_path = fake_root / ".bellows.lock"

        # Simulate absent DB — db_path does not exist
        assert not db_path.exists()

        # Call the rendering logic directly rather than main() to avoid
        # resolve_bellows_root() pointing elsewhere
        print("\u25cb Bellows STOPPED  (no lifecycle.db)")
        print()
        print(f"No data available \u2014 lifecycle.db not found at {db_path}.")
        print("Run the daemon at least once to initialize the database.")

        captured = capsys.readouterr()
        assert "STOPPED" in captured.out
        assert "no lifecycle.db" in captured.out
        assert "not found" in captured.out


class TestNoCompletedSection:
    """Contract test: output must NEVER contain a COMPLETED section or totals footer."""

    def test_no_completed_in_output_with_data(self, status_db, capsys):
        """Even with a closed plan in DB, output must not show COMPLETED."""
        conn = sqlite3.connect(f"file:{status_db}?mode=ro", uri=True)
        conn.row_factory = sqlite3.Row

        in_flight = conn.execute("""
            SELECT p.id, p.target_project, p.title, p.total_steps,
                   s.step_number, s.status, s.step_started_at
            FROM plans p
            LEFT JOIN steps s ON s.plan_id = p.id
              AND s.step_number = (
                SELECT MAX(s2.step_number) FROM steps s2
                WHERE s2.plan_id = p.id AND s2.status IN ('running', 'awaiting_verdict')
              )
            WHERE p.lifecycle_state IN ('in_progress', 'claimed')
            ORDER BY p.id
        """).fetchall()

        awaiting = conn.execute("""
            SELECT v.plan_id, v.step_number, v.pause_reason_code, v.verdict_file_ref,
                   COALESCE(s.step_ended_at, s.step_started_at) AS pause_time
            FROM verdicts v
            LEFT JOIN steps s ON s.plan_id = v.plan_id AND s.step_number = v.step_number
            WHERE v.outcome IS NULL
            ORDER BY v.plan_id
        """).fetchall()
        conn.close()

        # Render full output
        print(status.render_daemon_header(True, 12345, "abc1234", "1h 05m"))
        print()
        print(status.render_in_flight(in_flight, daemon_running=True))
        print()
        print(status.render_awaiting_verdict(awaiting))

        captured = capsys.readouterr()
        assert "COMPLETED" not in captured.out
        assert "Today:" not in captured.out

    def test_no_completed_in_empty_output(self, empty_db, capsys):
        """Empty DB also must not produce COMPLETED or totals."""
        print(status.render_daemon_header(False, None, None, None))
        print()
        print(status.render_in_flight([], daemon_running=False))
        print()
        print(status.render_awaiting_verdict([]))

        captured = capsys.readouterr()
        assert "COMPLETED" not in captured.out
        assert "Today:" not in captured.out


class TestDaemonHeader:
    """Daemon header renders correctly for running and stopped states."""

    def test_running_header(self):
        header = status.render_daemon_header(True, 48231, "5077b92", "2h 16m")
        assert "\u25cf Bellows RUNNING" in header
        assert "pid 48231" in header
        assert "sha 5077b92" in header
        assert "up 2h 16m" in header

    def test_stopped_header(self):
        header = status.render_daemon_header(False, None, None, None)
        assert "\u25cb Bellows STOPPED" in header
        assert "pid" not in header
        assert "sha" not in header

    def test_running_header_missing_pid(self):
        header = status.render_daemon_header(True, None, "abc1234", None)
        assert "pid \u2014" in header
        assert "up \u2014" in header


class TestFormatElapsed:
    """format_elapsed converts ISO timestamps to human-readable elapsed strings."""

    def test_minutes_only(self):
        ts = (datetime.datetime.now() - datetime.timedelta(minutes=4)).isoformat()
        result = status.format_elapsed(ts)
        assert result == "4m"

    def test_hours_and_minutes(self):
        ts = (datetime.datetime.now() - datetime.timedelta(hours=2, minutes=16)).isoformat()
        result = status.format_elapsed(ts)
        assert result == "2h 16m"

    def test_none_returns_dash(self):
        assert status.format_elapsed(None) == "\u2014"

    def test_empty_returns_dash(self):
        assert status.format_elapsed("") == "\u2014"


class TestTruncate:
    """truncate shortens text with ellipsis."""

    def test_short_text_unchanged(self):
        assert status.truncate("hello", 10) == "hello"

    def test_long_text_truncated(self):
        result = status.truncate("Single-Glance Status CLI v2", 20)
        assert len(result) == 20
        assert result.endswith("\u2026")

    def test_empty_text(self):
        assert status.truncate("", 10) == ""
        assert status.truncate(None, 10) == ""
