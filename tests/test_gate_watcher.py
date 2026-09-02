"""Tests for tools/gate_watcher.py — session-independent gate watcher."""
import itertools
import json
import os
import sys
import time
from pathlib import Path

import pytest

TOOLS_DIR = Path(__file__).resolve().parent.parent / "tools"
sys.path.insert(0, str(TOOLS_DIR.parent))

import lifecycle
import tools.gate_watcher as gw
from tools.gate_watcher import read_state, judge_transition, main


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


class TestPauseStateSpace:
    # verdict.py:187 — the daemon's writer
    PENDING = ("absent", "present")
    # B1: the two real filename forms plus absence
    VERDICT = ("none", "issued", "processed")
    # B3: SELECT DISTINCT lifecycle_state FROM plans — the REACHABLE set
    STATE = ("in_progress", "awaiting_verdict", "closed", "halted", "abandoned")

    CLASSIFICATION = {
        # pending absent → NO_PAUSE regardless
        ("absent", "none", "in_progress"): "NO_PAUSE",
        ("absent", "none", "closed"): "NO_PAUSE",
        ("absent", "none", "halted"): "NO_PAUSE",
        ("absent", "none", "abandoned"): "NO_PAUSE",
        ("absent", "issued", "in_progress"): "NO_PAUSE",
        ("absent", "issued", "closed"): "NO_PAUSE",
        ("absent", "issued", "halted"): "NO_PAUSE",
        ("absent", "issued", "abandoned"): "NO_PAUSE",
        ("absent", "processed", "in_progress"): "NO_PAUSE",
        ("absent", "processed", "closed"): "NO_PAUSE",
        ("absent", "processed", "halted"): "NO_PAUSE",
        ("absent", "processed", "abandoned"): "NO_PAUSE",
        # terminal state → NO_PAUSE (terminal wins over pending — the stray-file law)
        ("present", "none", "closed"): "NO_PAUSE",
        ("present", "none", "halted"): "NO_PAUSE",
        ("present", "none", "abandoned"): "NO_PAUSE",
        ("present", "issued", "closed"): "NO_PAUSE",
        ("present", "issued", "halted"): "NO_PAUSE",
        ("present", "issued", "abandoned"): "NO_PAUSE",
        ("present", "processed", "closed"): "NO_PAUSE",
        ("present", "processed", "halted"): "NO_PAUSE",
        ("present", "processed", "abandoned"): "NO_PAUSE",
        # pending present + verdict none + non-terminal → REPORT_PAUSE (the cell 572 got wrong)
        ("present", "none", "in_progress"): "REPORT_PAUSE",
        # pending present + verdict issued/processed + non-terminal → NO_PAUSE
        ("present", "issued", "in_progress"): "NO_PAUSE",
        ("present", "processed", "in_progress"): "NO_PAUSE",
        # row state awaiting_verdict → REPORT_PAUSE regardless of the file dimensions (100009's DB corroboration: the state IS the pause; tools/gate_watcher.py returns the awaiting-verdict phase on it after the file checks)
        ("absent", "none", "awaiting_verdict"): "REPORT_PAUSE",
        ("absent", "issued", "awaiting_verdict"): "REPORT_PAUSE",
        ("absent", "processed", "awaiting_verdict"): "REPORT_PAUSE",
        ("present", "none", "awaiting_verdict"): "REPORT_PAUSE",
        ("present", "issued", "awaiting_verdict"): "REPORT_PAUSE",
        ("present", "processed", "awaiting_verdict"): "REPORT_PAUSE",
    }

    _PLAN_ID = 500
    _PLAN_NAME = "state-space-plan.md"

    def test_state_space_is_completely_classified(self):
        assert len(self.CLASSIFICATION) == 2 * 3 * 5
        assert set(self.CLASSIFICATION.keys()) == set(
            itertools.product(self.PENDING, self.VERDICT, self.STATE)
        )

    @pytest.mark.parametrize("cell,expected", list(CLASSIFICATION.items()),
                             ids=[f"{p}-{v}-{s}" for (p, v, s) in CLASSIFICATION])
    def test_every_cell_behaves_as_classified(self, tmp_path, cell, expected):
        pending_dim, verdict_dim, state_dim = cell
        db_path = _init_db(tmp_path)
        _insert_plan(db_path, self._PLAN_ID, self._PLAN_NAME, state=state_dim)

        pend = tmp_path / "pending"
        pend.mkdir()
        resolved = tmp_path / "resolved"
        resolved.mkdir()

        if pending_dim == "present":
            (pend / f"verdict-request-{self._PLAN_ID}-step-1.md").write_text("")
        if verdict_dim == "issued":
            (resolved / f"verdict-{self._PLAN_ID}-step-1.md").write_text("")
        elif verdict_dim == "processed":
            (resolved / f"processed-verdict-{self._PLAN_ID}-step-1.md").write_text("")

        result = read_state(self._PLAN_NAME, db_path=db_path,
                            pending_dir=str(pend), resolved_dir=str(resolved))

        if expected == "REPORT_PAUSE":
            assert result["phase"] == "awaiting-verdict"
        else:
            assert result["phase"] != "awaiting-verdict"

    def test_reachable_states_match_the_classification_dimension(self):
        import sqlite3
        db_path = os.environ.get("GATE_WATCHER_LIVE_DB")
        if db_path is None:
            from tools.gate_watcher import _DB
            db_path = _DB
        if not os.path.exists(db_path):
            pytest.skip(f"no lifecycle.db at {db_path}")
        try:
            conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True, timeout=5)
        except sqlite3.OperationalError:
            pytest.skip(f"lifecycle.db at {db_path} is not a readable SQLite database")
        try:
            rows = conn.execute("SELECT DISTINCT lifecycle_state FROM plans").fetchall()
        except sqlite3.OperationalError:
            conn.close()
            pytest.skip(f"lifecycle.db at {db_path} has no plans table")
        finally:
            conn.close()
        observed = {r[0] for r in rows}
        for s in observed:
            assert s in self.STATE, f"reachable state {s!r} not in STATE dimension"

    def test_no_arming_position_state_survives(self):
        import ast
        src_path = TOOLS_DIR / "gate_watcher.py"
        source = src_path.read_text()
        tree = ast.parse(source)
        names = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Name):
                names.add(node.id)
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                names.add(node.name)
            elif isinstance(node, ast.arg):
                names.add(node.arg)
        for token in ("arm_pending", "armed", "judge_watch_line"):
            assert token not in names, f"{token!r} used as identifier in gate_watcher.py"

    def test_position_cannot_change_the_phase(self):
        cur = {
            "phase": "awaiting-verdict",
            "plan_id": 50,
            "gate_failures": [],
            "pending": ["verdict-request-50-step-1.md"],
        }
        different_prev = {"phase": "in_progress", "plan_id": 50, "gate_failures": []}
        line_from_none = judge_transition(None, cur)
        line_from_prev = judge_transition(different_prev, cur)
        assert line_from_none is not None
        assert line_from_prev is not None
        assert "awaiting-verdict" in line_from_none
        assert "awaiting-verdict" in line_from_prev

    def test_unparseable_request_name_is_reported_live(self, tmp_path):
        db_path = _init_db(tmp_path)
        _insert_plan(db_path, 90, "unparse-plan.md", state="in_progress")
        pend = tmp_path / "pending"
        pend.mkdir()
        resolved = tmp_path / "resolved"
        resolved.mkdir()
        (pend / "verdict-request-90-step-weird.md").write_text("")
        result = read_state("unparse-plan.md", db_path=db_path,
                            pending_dir=str(pend), resolved_dir=str(resolved))
        assert result["phase"] == "awaiting-verdict"

    def test_mixed_steps_report_only_the_unresolved_one(self, tmp_path):
        db_path = _init_db(tmp_path)
        _insert_plan(db_path, 100, "mixed-plan.md", state="in_progress")
        pend = tmp_path / "pending"
        pend.mkdir()
        resolved = tmp_path / "resolved"
        resolved.mkdir()
        (pend / "verdict-request-100-step-1.md").write_text("")
        (pend / "verdict-request-100-step-2.md").write_text("")
        (resolved / "processed-verdict-100-step-1.md").write_text("")
        result = read_state("mixed-plan.md", db_path=db_path,
                            pending_dir=str(pend), resolved_dir=str(resolved))
        assert result["phase"] == "awaiting-verdict"
        assert result["pending"] == ["verdict-request-100-step-2.md"]


# ---------------------------------------------------------------------------
# TestDbCorroboration: awaiting_verdict DB state recognized without pending file (W2)
# ---------------------------------------------------------------------------

class TestDbCorroboration:
    def test_awaiting_verdict_db_state_without_pending_file(self, tmp_path):
        db_path = _init_db(tmp_path)
        _insert_plan(db_path, 200, "db-corroborate.md", state="awaiting_verdict")
        pend = tmp_path / "pending"
        pend.mkdir()
        result = read_state("db-corroborate.md", db_path=db_path, pending_dir=str(pend))
        assert result["phase"] == "awaiting-verdict", (
            "W2: awaiting_verdict DB state must yield phase 'awaiting-verdict' even with no pending file"
        )


# ---------------------------------------------------------------------------
# TestPushPause: push hook fires on transition, not on repeated poll or --status (W1)
# ---------------------------------------------------------------------------

_AWAITING_STATE = {
    "phase": "awaiting-verdict",
    "plan_id": 1,
    "gate_failures": [],
    "pending": ["verdict-request-1-step-1.md"],
}
_IN_PROGRESS_STATE = {"phase": "in_progress", "plan_id": 1, "gate_failures": []}
_CLOSED_STATE = {"phase": "closed", "plan_id": 1, "gate_failures": []}


def _run_main_with_states(states, plan_name, tmp_path, monkeypatch):
    """Drive main() through a fixed state sequence, return (push_calls, log_lines)."""
    push_calls = []

    def mock_push(name, cur, db_path=None):
        push_calls.append((name, dict(cur)))
        return "WATCH: push sent"

    monkeypatch.setattr(gw, "_push_pause", mock_push)

    state_iter = iter(states)

    def mock_read_state(*args, **kwargs):
        return next(state_iter, _CLOSED_STATE)

    monkeypatch.setattr(gw, "read_state", mock_read_state)
    monkeypatch.setattr(gw.time, "sleep", lambda n: None)

    log_lines = []

    def mock_log_line(path, line):
        log_lines.append(line)

    monkeypatch.setattr(gw, "_log_line", mock_log_line)

    db_path = str(tmp_path / "lifecycle.db")
    lifecycle.init_lifecycle_db(db_path)

    rc = gw.main([
        "gate_watcher.py", plan_name,
        "--timeout-min", "60",
        "--db-path", db_path,
    ])
    return push_calls, log_lines, rc


class TestPushPause:
    def test_push_fires_once_on_transition(self, tmp_path, monkeypatch):
        states = [
            _IN_PROGRESS_STATE,
            _AWAITING_STATE,
            _CLOSED_STATE,
        ]
        push_calls, log_lines, rc = _run_main_with_states(
            states, "test-plan.md", tmp_path, monkeypatch
        )
        assert len(push_calls) == 1
        assert push_calls[0][0] == "test-plan.md"
        assert rc == 0

    def test_push_does_not_fire_on_repeated_poll(self, tmp_path, monkeypatch):
        states = [
            _IN_PROGRESS_STATE,
            _AWAITING_STATE,
            _AWAITING_STATE,
            _CLOSED_STATE,
        ]
        push_calls, log_lines, rc = _run_main_with_states(
            states, "test-plan.md", tmp_path, monkeypatch
        )
        assert len(push_calls) == 1

    def test_push_not_called_for_status(self, tmp_path, monkeypatch):
        push_calls = []

        def mock_push(name, cur, db_path=None):
            push_calls.append(name)
            return "WATCH: push sent"

        monkeypatch.setattr(gw, "_push_pause", mock_push)

        db_path = _init_db(tmp_path)
        _insert_plan(db_path, 300, "status-check.md", state="awaiting_verdict")
        pend = tmp_path / "pending"
        pend.mkdir()
        (pend / "verdict-request-300-step-1.md").write_text("")

        rc = gw.main([
            "gate_watcher.py", "status-check.md",
            "--status",
            "--db-path", db_path,
            "--pending-dir", str(pend),
        ])
        assert rc == 0
        assert len(push_calls) == 0

    def test_raising_push_logged_loop_continues(self, tmp_path, monkeypatch):
        states = [
            _IN_PROGRESS_STATE,
            _AWAITING_STATE,
            _CLOSED_STATE,
        ]

        def raising_push(name, cur, db_path=None):
            raise RuntimeError("network failure")

        monkeypatch.setattr(gw, "_push_pause", raising_push)
        monkeypatch.setattr(gw.time, "sleep", lambda n: None)

        state_iter = iter(states)
        monkeypatch.setattr(gw, "read_state", lambda *a, **kw: next(state_iter, _CLOSED_STATE))

        log_lines = []

        def mock_log_line(path, line):
            log_lines.append(line)

        monkeypatch.setattr(gw, "_log_line", mock_log_line)

        db_path = str(tmp_path / "lifecycle.db")
        lifecycle.init_lifecycle_db(db_path)

        rc = gw.main([
            "gate_watcher.py", "test-plan.md",
            "--timeout-min", "60",
            "--db-path", db_path,
        ])
        assert rc == 0
        skip_lines = [l for l in log_lines if "push skipped" in l]
        assert len(skip_lines) >= 1
        assert any("RuntimeError" in l for l in skip_lines)
