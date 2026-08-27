"""Tests for tools/gate_watcher.py — session-independent gate watcher."""
import json
import os
import sys
from pathlib import Path

import pytest

TOOLS_DIR = Path(__file__).resolve().parent.parent / "tools"
sys.path.insert(0, str(TOOLS_DIR.parent))

import lifecycle
from tools.gate_watcher import read_state, judge_transition, judge_watch_line, main


def _init_db(tmp_path):
    db_path = str(tmp_path / "lifecycle.db")
    lifecycle.init_lifecycle_db(db_path)
    return db_path


def _insert_plan(db_path, plan_id, name, state="in_progress"):
    import sqlite3
    conn = sqlite3.connect(db_path)
    conn.execute(
        "INSERT INTO plans (id, type, target_project, lifecycle_state, "
        "deposit_placeholder_name, created_at) VALUES (?, 'executable', 'test', ?, ?, '2026-08-26')",
        (plan_id, state, name),
    )
    conn.commit()
    conn.close()


def _insert_step(db_path, step_id, plan_id, step_number=1):
    import sqlite3
    conn = sqlite3.connect(db_path)
    conn.execute(
        "INSERT INTO steps (id, plan_id, step_number, status) VALUES (?, ?, ?, 'complete')",
        (step_id, plan_id, step_number),
    )
    conn.commit()
    conn.close()


def _insert_gate_event(db_path, step_id, gate_name, result="fail", overridden=0):
    import sqlite3
    conn = sqlite3.connect(db_path)
    conn.execute(
        "INSERT INTO gate_events (step_id, gate_name, result, overridden) VALUES (?, ?, ?, ?)",
        (step_id, gate_name, result, overridden),
    )
    conn.commit()
    conn.close()


# --- Test 1: read_state with no plans row → pre-claim ---
def test_read_state_no_plans(tmp_path):
    db_path = _init_db(tmp_path)
    result = read_state("nonexistent-plan.md", db_path=db_path)
    assert result == {"phase": "pre-claim"}


# --- Test 2: read_state with an in_progress row → phase + plan_id, empty gate_failures ---
def test_read_state_in_progress(tmp_path):
    db_path = _init_db(tmp_path)
    _insert_plan(db_path, 42, "my-plan.md", state="in_progress")
    result = read_state("my-plan.md", db_path=db_path)
    assert result["phase"] == "in_progress"
    assert result["plan_id"] == 42
    assert result["gate_failures"] == []


# --- Test 3: read_state with a fail gate_event (overridden=0) → gate named ---
def test_read_state_gate_failure(tmp_path):
    db_path = _init_db(tmp_path)
    _insert_plan(db_path, 10, "gated-plan.md")
    _insert_step(db_path, 100, 10)
    _insert_gate_event(db_path, 100, "cycle_check", result="fail", overridden=0)
    result = read_state("gated-plan.md", db_path=db_path)
    assert "cycle_check" in result["gate_failures"]


# --- Test 4: read_state with overridden=1 → gate_failures empty ---
def test_read_state_gate_overridden(tmp_path):
    db_path = _init_db(tmp_path)
    _insert_plan(db_path, 11, "overridden-plan.md")
    _insert_step(db_path, 101, 11)
    _insert_gate_event(db_path, 101, "plan_lint", result="fail", overridden=1)
    result = read_state("overridden-plan.md", db_path=db_path)
    assert result["gate_failures"] == []


# --- Test 5: read_state on nonexistent db path → None ---
def test_read_state_bad_db(tmp_path):
    result = read_state("any-plan.md", db_path=str(tmp_path / "no-such.db"))
    assert result is None


# --- Test 6: judge_transition — three asserts ---
def test_judge_transition_variants():
    cur = {"phase": "in_progress", "plan_id": 5, "gate_failures": []}
    cur_with_gates = {"phase": "in_progress", "plan_id": 5, "gate_failures": ["lint"]}

    line = judge_transition(None, cur)
    assert line is not None and "in_progress" in line

    same = judge_transition(cur, cur)
    assert same is None

    changed_line = judge_transition(cur, cur_with_gates)
    assert changed_line is not None and "lint" in changed_line


# --- Test 7: judge_transition with cur=None → db-unreadable ---
def test_judge_transition_db_unreadable():
    prev = {"phase": "in_progress", "plan_id": 1, "gate_failures": []}
    line = judge_transition(prev, None)
    assert "db-unreadable" in line


# --- Test 8: --status one-shot via main() ---
def test_status_oneshot(tmp_path, capsys):
    db_path = _init_db(tmp_path)
    _insert_plan(db_path, 99, "status-plan.md", state="in_progress")
    rc = main(["gate_watcher.py", "status-plan.md", "--status", "--db-path", db_path])
    assert rc == 0
    captured = capsys.readouterr()
    assert "WATCH:" in captured.out


# --- Test 9: deposit_receipt.write_receipt with spawn_watcher toggling ---
def test_receipt_watcher_wording(tmp_path, monkeypatch):
    import tools.deposit_receipt as dr

    monkeypatch.setattr(dr, "_BELLOWS_ROOT", str(tmp_path))
    monkeypatch.setattr(dr, "_RECEIPTS_DIR", str(tmp_path / "receipts"))

    plan_path = tmp_path / "ready-watcher-test.md"
    plan_path.write_text("# test\n")

    monkeypatch.setattr(dr, "_spawn_watcher", lambda name: None)
    result = dr.write_receipt(str(plan_path), "sess-no-spawn", spawn_watcher=False)
    assert result is True
    files = list((tmp_path / "receipts").glob("receipt-*.json"))
    data = json.loads(files[0].read_text())
    assert data["watcher"] == "gate-watcher armed in depositing session"

    Path(plan_path).write_bytes(b"# test v2\n")
    monkeypatch.setattr(dr, "_spawn_watcher", lambda name: 4242)
    result = dr.write_receipt(str(plan_path), "sess-spawned", spawn_watcher=True)
    assert result is True
    files = sorted((tmp_path / "receipts").glob("receipt-*.json"))
    data2 = json.loads(files[-1].read_text())
    assert "pid 4242" in data2["watcher"]


# --- TestPauseDetection — constructed-state tests for the verdict-request pause branch ---

class TestPauseDetection:
    def test_paused_plan_reports_awaiting_verdict(self, tmp_path):
        db_path = _init_db(tmp_path)
        _insert_plan(db_path, 50, "paused-plan.md", state="in_progress")
        pend = tmp_path / "pending"
        pend.mkdir()
        (pend / "verdict-request-50-step-2.md").write_text("")
        result = read_state("paused-plan.md", db_path=db_path, pending_dir=str(pend))
        assert result["phase"] == "awaiting-verdict"
        assert result["pending"] == ["verdict-request-50-step-2.md"]

    def test_foreign_plan_request_is_invisible(self, tmp_path):
        db_path = _init_db(tmp_path)
        _insert_plan(db_path, 50, "my-plan.md", state="in_progress")
        pend = tmp_path / "pending"
        pend.mkdir()
        (pend / "verdict-request-51-step-1.md").write_text("")
        result = read_state("my-plan.md", db_path=db_path, pending_dir=str(pend))
        assert result["phase"] == "in_progress"
        assert "pending" not in result

    def test_terminal_state_ignores_stray_request(self, tmp_path):
        db_path = _init_db(tmp_path)
        _insert_plan(db_path, 60, "done-plan.md", state="closed")
        pend = tmp_path / "pending"
        pend.mkdir()
        (pend / "verdict-request-60-step-1.md").write_text("")
        result = read_state("done-plan.md", db_path=db_path, pending_dir=str(pend))
        assert result["phase"] == "closed"
        assert "pending" not in result

    def test_empty_pending_dir_reports_in_progress(self, tmp_path):
        db_path = _init_db(tmp_path)
        _insert_plan(db_path, 50, "running-plan.md", state="in_progress")
        pend = tmp_path / "pending"
        pend.mkdir()
        result = read_state("running-plan.md", db_path=db_path, pending_dir=str(pend))
        assert result["phase"] == "in_progress"
        assert "pending" not in result

    def test_pending_dir_derived_from_db_path(self, tmp_path):
        sub = tmp_path / "x"
        sub.mkdir()
        db_path = str(sub / "lifecycle.db")
        lifecycle.init_lifecycle_db(db_path)
        _insert_plan(db_path, 70, "derived-plan.md", state="in_progress")
        pend = sub / "verdicts" / "pending"
        pend.mkdir(parents=True)
        (pend / "verdict-request-70-step-1.md").write_text("")
        result = read_state("derived-plan.md", db_path=db_path)
        assert result["phase"] == "awaiting-verdict"
        assert "verdict-request-70-step-1.md" in result["pending"]

    def test_transition_line_carries_pending_names(self):
        state = {
            "phase": "awaiting-verdict",
            "plan_id": 50,
            "gate_failures": [],
            "pending": ["verdict-request-50-step-2.md"],
        }
        line = judge_transition(None, state)
        assert "awaiting-verdict" in line
        assert "pending=verdict-request-50-step-2.md" in line

    def test_resume_transition_logged(self):
        prev = {
            "phase": "awaiting-verdict",
            "plan_id": 50,
            "gate_failures": [],
            "pending": ["verdict-request-50-step-1.md"],
        }
        cur = {"phase": "in_progress", "plan_id": 50, "gate_failures": []}
        line = judge_transition(prev, cur)
        assert line is not None


class TestArmTimeSnapshot:

    def test_pre_existing_pause_reported_as_armed_over(self):
        cur = {
            "phase": "awaiting-verdict",
            "plan_id": 50,
            "gate_failures": [],
            "pending": ["verdict-request-50-step-1.md"],
        }
        line, new_snap = judge_watch_line(None, cur, {"verdict-request-50-step-1.md"})
        assert "armed over pre-existing" in line
        assert "awaiting-verdict" not in line

    def test_pre_existing_pause_silent_on_later_polls(self):
        cur = {
            "phase": "awaiting-verdict",
            "plan_id": 50,
            "gate_failures": [],
            "pending": ["verdict-request-50-step-1.md"],
        }
        line, new_snap = judge_watch_line(cur, cur, {"verdict-request-50-step-1.md"})
        assert line is None

    def test_new_pause_after_snapshot_cleared_reports_normally(self):
        cur = {
            "phase": "awaiting-verdict",
            "plan_id": 50,
            "gate_failures": [],
            "pending": ["verdict-request-50-step-2.md"],
        }
        line, new_snap = judge_watch_line(None, cur, None)
        assert "awaiting-verdict" in line
        assert "pending=verdict-request-50-step-2.md" in line

    def test_snapshot_cleared_when_pending_empties(self):
        cur = {"phase": "in_progress", "plan_id": 50, "gate_failures": []}
        line, new_snap = judge_watch_line(None, cur, {"verdict-request-50-step-1.md"})
        assert new_snap is None

    def test_different_pending_set_is_a_new_pause(self):
        cur = {
            "phase": "awaiting-verdict",
            "plan_id": 50,
            "gate_failures": [],
            "pending": ["verdict-request-50-step-2.md"],
        }
        line, new_snap = judge_watch_line(None, cur, {"verdict-request-50-step-1.md"})
        assert "awaiting-verdict" in line
        assert "pending=verdict-request-50-step-2.md" in line

    def test_arm_pending_none_is_transparent(self):
        cur_running = {"phase": "in_progress", "plan_id": 50, "gate_failures": []}
        cur_terminal = {"phase": "closed", "plan_id": 50, "gate_failures": []}
        for cur in (cur_running, cur_terminal):
            line, new_snap = judge_watch_line(None, cur, None)
            expected = judge_transition(None, cur)
            assert line == expected

    def test_db_unreadable_preserves_snapshot(self):
        snap = {"verdict-request-50-step-1.md"}
        line, new_snap = judge_watch_line(None, None, snap)
        assert "db-unreadable" in line
        assert new_snap == snap
        next_cur = {
            "phase": "awaiting-verdict",
            "plan_id": 50,
            "gate_failures": [],
            "pending": ["verdict-request-50-step-1.md"],
        }
        line2, new_snap2 = judge_watch_line(None, next_cur, new_snap)
        assert "armed over pre-existing" in line2

    def test_status_mode_unchanged_for_pause(self, tmp_path, capsys):
        db_path = _init_db(tmp_path)
        _insert_plan(db_path, 80, "status-pause.md", state="in_progress")
        pend = tmp_path / "pending"
        pend.mkdir()
        (pend / "verdict-request-80-step-1.md").write_text("")
        rc = main(["gate_watcher.py", "status-pause.md", "--status",
                    "--db-path", db_path, "--pending-dir", str(pend)])
        assert rc == 0
        captured = capsys.readouterr()
        assert "WATCH: awaiting-verdict id=80 pending=verdict-request-80-step-1.md" in captured.out
