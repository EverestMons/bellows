import fcntl
import os
import signal
import sqlite3
import subprocess
import sys
import time

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from unittest.mock import patch, MagicMock
from bellows import (
    acquire_instance_lock,
    LockAcquireError,
    stop_daemon,
    _discover_holder,
    _verify_identity,
    _check_idle,
)


def _make_lifecycle_db(db_path, rows):
    """Create a minimal lifecycle.db matching the production schema's required columns."""
    conn = sqlite3.connect(db_path)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS plans (
            id INTEGER PRIMARY KEY,
            type TEXT NOT NULL,
            target_project TEXT NOT NULL,
            title TEXT,
            total_steps INTEGER,
            lifecycle_state TEXT NOT NULL DEFAULT 'in_progress',
            created_at TEXT NOT NULL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS steps (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            plan_id INTEGER NOT NULL REFERENCES plans(id),
            step_number INTEGER NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending',
            step_started_at TEXT,
            UNIQUE(plan_id, step_number)
        )
    """)
    for r in rows:
        conn.execute(
            "INSERT INTO plans (id, type, target_project, title, total_steps, "
            "lifecycle_state, created_at) VALUES (?, ?, ?, ?, ?, 'in_progress', '2026-08-15T00:00:00')",
            (r["id"], r.get("type", "executable"), r.get("target_project", "/proj"),
             r.get("title"), r.get("total_steps")),
        )
        if r.get("status") is not None or r.get("step_number") is not None:
            conn.execute(
                "INSERT INTO steps (plan_id, step_number, status, step_started_at) "
                "VALUES (?, ?, ?, ?)",
                (r["id"], r.get("step_number", 1), r.get("status", "pending"),
                 r.get("step_started_at")),
            )
    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------
# Test 1: acquire-succeeds → reports no-incumbent, no kill attempted
# ---------------------------------------------------------------------------

def test_acquire_succeeds_no_incumbent(tmp_path):
    lock_path = str(tmp_path / ".bellows.lock")
    db_path = str(tmp_path / "lifecycle.db")
    _make_lifecycle_db(db_path, [])

    with patch("bellows.os.kill") as mock_kill:
        success, msg = stop_daemon(lock_path, db_path, {})
    assert success
    assert "no running daemon" in msg
    mock_kill.assert_not_called()


# ---------------------------------------------------------------------------
# Test 2: identity mismatch → REFUSE, no signal sent
# ---------------------------------------------------------------------------

def test_identity_mismatch_refuses(tmp_path):
    lock_path = str(tmp_path / ".bellows.lock")
    db_path = str(tmp_path / "lifecycle.db")
    _make_lifecycle_db(db_path, [])

    holder = acquire_instance_lock(lock_path)
    try:
        holder_pid = os.getpid()
        with patch("bellows._discover_holder", return_value=(holder_pid, None)):
            with patch("bellows._verify_identity", return_value=False):
                with patch("bellows.os.kill") as mock_kill:
                    success, msg = stop_daemon(lock_path, db_path, {})
        assert not success
        assert "REFUSE" in msg
        assert "identity" in msg.lower()
        mock_kill.assert_not_called()
    finally:
        holder.close()


# ---------------------------------------------------------------------------
# Test 3: idle guard trips on status='running' → REFUSE
# ---------------------------------------------------------------------------

def test_idle_guard_running_refuses(tmp_path):
    lock_path = str(tmp_path / ".bellows.lock")
    db_path = str(tmp_path / "lifecycle.db")
    _make_lifecycle_db(db_path, [
        {"id": 42, "status": "running", "step_number": 1,
         "type": "executable", "target_project": "/proj", "title": "test", "total_steps": 3},
    ])

    holder = acquire_instance_lock(lock_path)
    try:
        holder_pid = os.getpid()
        with patch("bellows._discover_holder", return_value=(holder_pid, None)):
            with patch("bellows._verify_identity", return_value=True):
                with patch("bellows.os.kill") as mock_kill:
                    success, msg = stop_daemon(lock_path, db_path, {})
        assert not success
        assert "REFUSE" in msg
        assert "running" in msg
        mock_kill.assert_not_called()
    finally:
        holder.close()


# ---------------------------------------------------------------------------
# Test 4: both guards pass → SIGTERM then SIGKILL, re-acquire as arbiter
# ---------------------------------------------------------------------------

def test_both_guards_pass_sigterm_then_sigkill(tmp_path):
    lock_path = str(tmp_path / ".bellows.lock")
    db_path = str(tmp_path / "lifecycle.db")
    _make_lifecycle_db(db_path, [])

    # Spawn a dummy that ignores SIGTERM to force the SIGKILL escalation
    dummy = subprocess.Popen([
        sys.executable, "-c",
        "import signal, time; signal.signal(signal.SIGTERM, signal.SIG_IGN); time.sleep(60)",
    ])
    dummy_pid = dummy.pid

    kill_calls = []
    original_kill = os.kill

    def tracking_kill(pid, sig):
        kill_calls.append((pid, sig))
        original_kill(pid, sig)

    mock_lock = MagicMock()
    acquire_count = [0]

    def mock_acquire(path):
        acquire_count[0] += 1
        if acquire_count[0] == 1:
            raise LockAcquireError("locked")
        return mock_lock

    try:
        with patch("bellows._discover_holder", return_value=(dummy_pid, None)):
            with patch("bellows._verify_identity", return_value=True):
                with patch("bellows.os.kill", side_effect=tracking_kill):
                    with patch("bellows.acquire_instance_lock", side_effect=mock_acquire):
                        with patch("bellows._STOP_SIGTERM_TIMEOUT", 1):
                            with patch("bellows._STOP_SIGKILL_TIMEOUT", 1):
                                success, msg = stop_daemon(lock_path, db_path, {})
    finally:
        try:
            dummy.kill()
        except Exception:
            pass
        dummy.wait(timeout=5)

    assert success
    assert str(dummy_pid) in msg

    sigterm_sent = any(sig == signal.SIGTERM for _, sig in kill_calls)
    assert sigterm_sent, f"SIGTERM not found in kill calls: {kill_calls}"
    sigkill_sent = any(sig == signal.SIGKILL for _, sig in kill_calls)
    assert sigkill_sent, f"SIGKILL not found (process ignored SIGTERM): {kill_calls}"


# ---------------------------------------------------------------------------
# Test 5: re-acquire race lost → REFUSE
# ---------------------------------------------------------------------------

def test_reacquire_race_lost_refuses(tmp_path):
    lock_path = str(tmp_path / ".bellows.lock")
    db_path = str(tmp_path / "lifecycle.db")
    _make_lifecycle_db(db_path, [])

    acquire_count = [0]

    def mock_acquire(path):
        acquire_count[0] += 1
        if acquire_count[0] == 1:
            raise LockAcquireError("locked")
        raise LockAcquireError("race lost — another holder")

    with patch("bellows._discover_holder", return_value=(99999, None)):
        with patch("bellows._verify_identity", return_value=True):
            with patch("bellows.os.kill"):
                with patch("bellows.acquire_instance_lock", side_effect=mock_acquire):
                    with patch("bellows._STOP_SIGTERM_TIMEOUT", 0.1):
                        success, msg = stop_daemon(lock_path, db_path, {})
    assert not success
    assert "REFUSE" in msg
    assert "re-acquire" in msg.lower()


# ---------------------------------------------------------------------------
# Test 6: lsof returns >1 PID → REFUSE (ambiguous), no signal sent
# ---------------------------------------------------------------------------

def test_ambiguous_lsof_refuses(tmp_path):
    lock_path = str(tmp_path / ".bellows.lock")
    db_path = str(tmp_path / "lifecycle.db")
    _make_lifecycle_db(db_path, [])

    holder = acquire_instance_lock(lock_path)
    try:
        lsof_output = f"{os.getpid()}\n{os.getpid() + 1}\n"
        mock_result = MagicMock()
        mock_result.stdout = lsof_output
        with patch("bellows.subprocess.run", return_value=mock_result):
            pid, err = _discover_holder(lock_path)
        assert pid is None
        assert "ambiguous" in err.lower()

        with patch("bellows._discover_holder", return_value=(None, "ambiguous: 2 PIDs")):
            with patch("bellows.os.kill") as mock_kill:
                success, msg = stop_daemon(lock_path, db_path, {})
        assert not success
        assert "REFUSE" in msg
        mock_kill.assert_not_called()
    finally:
        holder.close()


# ---------------------------------------------------------------------------
# Test 7: awaiting_verdict-only DB + orphaned in-progress file → guard PASSES
# ---------------------------------------------------------------------------

def test_idle_guard_passes_awaiting_verdict_with_orphan(tmp_path):
    lock_path = str(tmp_path / ".bellows.lock")
    db_path = str(tmp_path / "lifecycle.db")
    _make_lifecycle_db(db_path, [
        {"id": 50, "status": "awaiting_verdict", "step_number": 2,
         "type": "executable", "target_project": "/proj", "title": "paused plan",
         "total_steps": 3},
    ])

    decisions_dir = tmp_path / "knowledge" / "decisions"
    decisions_dir.mkdir(parents=True)
    (decisions_dir / "in-progress-executable-50.md").write_text("orphaned")

    config = {"watched_projects": [str(decisions_dir)]}

    is_idle, reason = _check_idle(db_path, config)
    assert is_idle, f"idle guard should pass but got: {reason}"
    assert reason is None
