"""Tests for session-limit detection, resets-at parsing, and park+auto-resume (plan 148).

Exit-1 rate-limit park detection tests (plan 185, diag-184 §6 matrix) added below
the original plan-148 tests.
"""

import io
import sys
import os
import json
import sqlite3
import tempfile
import shutil
import time
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
from zoneinfo import ZoneInfo

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import runner


# --- Synthetic result events ---

PLAN_132_RESULT_EVENT = {
    "type": "result",
    "subtype": "success",
    "is_error": True,
    "api_error_status": 429,
    "duration_ms": 416,
    "num_turns": 1,
    "result": "You've hit your session limit · resets 11:50pm (America/Chicago)",
    "stop_reason": "stop_sequence",
    "total_cost_usd": 0,
    "usage": {"input_tokens": 0, "output_tokens": 0},
}


def _session_limit_event(result_text, num_turns=1, total_cost_usd=0, output_tokens=0):
    return {
        "type": "result",
        "subtype": "success",
        "is_error": True,
        "api_error_status": 429,
        "num_turns": num_turns,
        "result": result_text,
        "stop_reason": "stop_sequence",
        "total_cost_usd": total_cost_usd,
        "usage": {"input_tokens": 0, "output_tokens": output_tokens},
    }


# ---- _parse_session_reset tests ----


def test_parse_plan_132_string():
    """The exact plan-132 string parses to a future epoch matching 11:50pm America/Chicago."""
    text = "You've hit your session limit · resets 11:50pm (America/Chicago)"
    epoch = runner._parse_session_reset(text)

    tz = ZoneInfo("America/Chicago")
    reset_dt = datetime.fromtimestamp(epoch, tz=tz)
    assert reset_dt.hour == 23
    assert reset_dt.minute == 50
    assert reset_dt.second == 0
    assert epoch > time.time()


def test_parse_hour_only_pm():
    """'11pm' (no minutes) parses correctly."""
    text = "resets 11pm (America/New_York)"
    epoch = runner._parse_session_reset(text)

    tz = ZoneInfo("America/New_York")
    reset_dt = datetime.fromtimestamp(epoch, tz=tz)
    assert reset_dt.hour == 23
    assert reset_dt.minute == 0
    assert epoch > time.time()


def test_parse_am_with_minutes():
    """'3:30am' parses correctly."""
    text = "resets 3:30am (US/Eastern)"
    epoch = runner._parse_session_reset(text)

    tz = ZoneInfo("US/Eastern")
    reset_dt = datetime.fromtimestamp(epoch, tz=tz)
    assert reset_dt.hour == 3
    assert reset_dt.minute == 30
    assert epoch > time.time()


def test_parse_12pm_noon():
    """'12:00pm' maps to hour 12 (noon), not 24."""
    text = "resets 12:00pm (America/Chicago)"
    epoch = runner._parse_session_reset(text)

    tz = ZoneInfo("America/Chicago")
    reset_dt = datetime.fromtimestamp(epoch, tz=tz)
    assert reset_dt.hour == 12
    assert reset_dt.minute == 0


def test_parse_12am_midnight():
    """'12:00am' maps to hour 0 (midnight)."""
    text = "resets 12:00am (America/Chicago)"
    epoch = runner._parse_session_reset(text)

    tz = ZoneInfo("America/Chicago")
    reset_dt = datetime.fromtimestamp(epoch, tz=tz)
    assert reset_dt.hour == 0
    assert reset_dt.minute == 0


def test_parse_unparseable_falls_back(capsys):
    """Unparseable string falls back to ~now+5h and logs WARN."""
    text = "Something went wrong, no reset info"
    before = time.time()
    epoch = runner._parse_session_reset(text)
    after = time.time()

    assert epoch >= before + 5 * 3600 - 1
    assert epoch <= after + 5 * 3600 + 1

    captured = capsys.readouterr()
    assert "could not parse session-limit reset time" in captured.out


def test_parse_bad_timezone_falls_back(capsys):
    """Valid time format but invalid timezone falls back to ~now+5h."""
    text = "resets 11:50pm (Fake/Timezone)"
    before = time.time()
    epoch = runner._parse_session_reset(text)
    after = time.time()

    assert epoch >= before + 5 * 3600 - 1
    assert epoch <= after + 5 * 3600 + 1

    captured = capsys.readouterr()
    assert "unknown timezone" in captured.out


# ---- _check_session_limit tests ----


def test_check_plan_132_event_is_parkable():
    """The exact plan-132 result event is detected as a parkable session limit."""
    result = runner._check_session_limit(PLAN_132_RESULT_EVENT)
    assert result is not None
    assert result["session_limit"] is True
    assert isinstance(result["resets_at_epoch"], float)
    assert result["resets_at_epoch"] > time.time()
    assert "session limit" in result["resets_at_raw"].lower()


def test_check_usage_limit_phrasing():
    """'usage limit' phrasing is also detected."""
    event = _session_limit_event("You've hit your usage limit · resets 3:30am (US/Eastern)")
    result = runner._check_session_limit(event)
    assert result is not None
    assert result["session_limit"] is True


def test_check_transient_rate_limit_not_session_limit():
    """A bare '429 rate limit' / transient result is NOT classified as a session limit."""
    event = {
        "type": "result",
        "is_error": True,
        "api_error_status": 429,
        "num_turns": 1,
        "result": "429 Too Many Requests - rate limit exceeded",
        "total_cost_usd": 0,
        "usage": {"output_tokens": 0},
    }
    result = runner._check_session_limit(event)
    assert result is None


def test_check_non_429_error_not_session_limit():
    """A non-429 error is never a session limit."""
    event = {
        "type": "result",
        "is_error": True,
        "api_error_status": 500,
        "num_turns": 1,
        "result": "You've hit your session limit",
        "total_cost_usd": 0,
        "usage": {"output_tokens": 0},
    }
    result = runner._check_session_limit(event)
    assert result is None


def test_check_no_error_not_session_limit():
    """A non-error result is never a session limit."""
    event = {
        "type": "result",
        "is_error": False,
        "num_turns": 5,
        "result": "session limit mentioned but not an error",
        "total_cost_usd": 0.50,
        "usage": {"output_tokens": 100},
    }
    result = runner._check_session_limit(event)
    assert result is None


def test_check_session_limit_with_progress_not_parkable():
    """A 429 session-limit result WITH num_turns > 1 or nonzero cost is NOT parkable."""
    event_turns = _session_limit_event(
        "You've hit your session limit · resets 11:50pm (America/Chicago)",
        num_turns=3,
    )
    assert runner._check_session_limit(event_turns) is None

    event_cost = _session_limit_event(
        "You've hit your session limit · resets 11:50pm (America/Chicago)",
        total_cost_usd=0.14,
    )
    assert runner._check_session_limit(event_cost) is None

    event_tokens = _session_limit_event(
        "You've hit your session limit · resets 11:50pm (America/Chicago)",
        output_tokens=50,
    )
    assert runner._check_session_limit(event_tokens) is None


# ---- Integration: returned dict fields ----


def test_session_limit_return_dict_fields():
    """When a parkable session limit is detected, the returned dict carries all required fields."""
    sl = runner._check_session_limit(PLAN_132_RESULT_EVENT)
    assert sl is not None
    assert "session_limit" in sl
    assert "resets_at_epoch" in sl
    assert "resets_at_raw" in sl
    assert sl["session_limit"] is True
    assert isinstance(sl["resets_at_epoch"], float)
    assert isinstance(sl["resets_at_raw"], str)


# ==========================================
# Step 2 tests — park + persist + auto-resume
# ==========================================

import bellows


# ---- record_park / clear_park DB round-trip ----


def test_record_park_queryable_at_epoch():
    """record_park persists a row; query with now >= resets_at returns it."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    try:
        resets_at = time.time() - 10  # already past
        bellows.record_park(db_path, "test-slug", "/tmp/parked-test.md", "/tmp/project", 2, resets_at)
        conn = sqlite3.connect(db_path)
        rows = conn.execute(
            "SELECT plan_slug, plan_path, project, resume_step, resets_at_epoch FROM parked_steps WHERE resets_at_epoch <= ?",
            (time.time(),),
        ).fetchall()
        conn.close()
        assert len(rows) == 1
        assert rows[0][0] == "test-slug"
        assert rows[0][3] == 2
    finally:
        os.unlink(db_path)


def test_record_park_not_returned_before_epoch():
    """record_park row is NOT returned when now < resets_at_epoch."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    try:
        resets_at = time.time() + 9999
        bellows.record_park(db_path, "future-slug", "/tmp/parked-future.md", "/tmp/project", 1, resets_at)
        conn = sqlite3.connect(db_path)
        rows = conn.execute(
            "SELECT plan_slug FROM parked_steps WHERE resets_at_epoch <= ?",
            (time.time(),),
        ).fetchall()
        conn.close()
        assert len(rows) == 0
    finally:
        os.unlink(db_path)


def test_clear_park_removes_row():
    """clear_park deletes the row for the given plan_slug."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    try:
        bellows.record_park(db_path, "clear-me", "/tmp/parked.md", "/tmp/project", 1, time.time())
        bellows.clear_park(db_path, "clear-me")
        conn = sqlite3.connect(db_path)
        rows = conn.execute("SELECT plan_slug FROM parked_steps").fetchall()
        conn.close()
        assert len(rows) == 0
    finally:
        os.unlink(db_path)


# ---- is_runnable_plan excludes parked- ----


def test_is_runnable_plan_excludes_parked():
    """is_runnable_plan returns False for parked- prefixed files."""
    assert bellows.is_runnable_plan("parked-executable-9.md") is False
    assert bellows.is_runnable_plan("parked-executable-foo-2026-07-09.md") is False


# ---- Park helper simulation ----


def test_maybe_park_session_limit_renames_and_persists(tmp_path):
    """Simulate _maybe_park_session_limit: plan renamed to parked-*, DB row exists, record_run status is Parked."""
    decisions_dir = tmp_path / "decisions"
    decisions_dir.mkdir()
    base_filename = "executable-999.md"
    inprogress_path = str(decisions_dir / f"in-progress-{base_filename}")
    with open(inprogress_path, "w") as f:
        f.write("# Test plan")
    db_path = str(tmp_path / "test.db")
    parsed = {
        "session_limit": True,
        "resets_at_epoch": time.time() + 3600,
        "resets_at_raw": "resets 11:50pm (America/Chicago)",
        "session_id": "test-session",
        "cost_usd": 0.0,
    }
    with patch("bellows._teardown_worktree"), \
         patch("bellows.notifier") as mock_notifier:
        mock_notifier.push = lambda *a, **kw: True
        result = bellows._maybe_park_session_limit(
            parsed, inprogress_path, 2, "999", "executable-999.md",
            base_filename, str(decisions_dir), None, db_path, "/tmp/project",
            "/tmp/wt", "app_key", "user_key", 999,
        )
    assert result is True
    parked_path = str(decisions_dir / f"parked-{base_filename}")
    assert os.path.exists(parked_path)
    assert not os.path.exists(inprogress_path)
    # Check DB row
    conn = sqlite3.connect(db_path)
    rows = conn.execute("SELECT plan_slug, resume_step FROM parked_steps").fetchall()
    conn.close()
    assert len(rows) == 1
    assert rows[0][0] == "999"
    assert rows[0][1] == 2
    # Check record_run status
    conn = sqlite3.connect(db_path)
    runs = conn.execute("SELECT status FROM runs WHERE plan_slug = '999'").fetchall()
    conn.close()
    assert any(r[0] == "Parked" for r in runs)


def test_maybe_park_returns_false_for_non_session_limit():
    """_maybe_park_session_limit returns False when parsed has no session_limit."""
    parsed = {"receipt_status": "Complete", "cost_usd": 0.5}
    result = bellows._maybe_park_session_limit(
        parsed, "/tmp/in-progress.md", 1, "slug", "plan.md",
        "plan.md", "/tmp", None, "/tmp/db", "/tmp/project",
        "/tmp/wt", "", "", None,
    )
    assert result is False


# ---- Resume: un-park rename produces in-progress-* ----


def test_resume_unpark_rename(tmp_path):
    """Resume at/after epoch: un-park produces in-progress-* and clears the DB row."""
    decisions_dir = tmp_path / "decisions"
    decisions_dir.mkdir()
    base_filename = "executable-50.md"
    parked_path = str(decisions_dir / f"parked-{base_filename}")
    with open(parked_path, "w") as f:
        f.write("# Test plan")
    db_path = str(tmp_path / "test.db")
    resets_at = time.time() - 10  # already past
    bellows.record_park(db_path, "50", parked_path, str(tmp_path), 3, resets_at)
    # Simulate what _resume_parked does
    parked_dir = os.path.dirname(parked_path)
    parked_name = os.path.basename(parked_path)
    in_base = parked_name[len("parked-"):]
    inprogress_path = os.path.join(parked_dir, f"in-progress-{in_base}")
    shutil.move(parked_path, inprogress_path)
    bellows.clear_park(db_path, "50")
    assert os.path.exists(inprogress_path)
    assert not os.path.exists(parked_path)
    conn = sqlite3.connect(db_path)
    rows = conn.execute("SELECT plan_slug FROM parked_steps").fetchall()
    conn.close()
    assert len(rows) == 0


# ==========================================
# Exit-1 rate-limit park detection (plan 185, diag-184 §6 matrix)
# ==========================================


# --- _reset_epoch_from_rate_limit_event tests ---


def test_reset_epoch_valid_resets_at():
    """Valid resetsAt integer is returned as float."""
    info = {"resetsAt": 1784053800, "rateLimitType": "five_hour"}
    assert runner._reset_epoch_from_rate_limit_event(info) == 1784053800.0


def test_reset_epoch_missing_resets_at_falls_back(capsys):
    """Missing resetsAt falls back to ~now+5h."""
    before = time.time()
    result = runner._reset_epoch_from_rate_limit_event({})
    after = time.time()
    assert result >= before + 5 * 3600 - 1
    assert result <= after + 5 * 3600 + 1
    captured = capsys.readouterr()
    assert "missing/invalid resetsAt" in captured.out


# --- _check_exit1_rate_limit helper tests ---


def test_exit1_five_hour_zero_progress_parkable():
    """(i) exit-1 + five_hour rate_limit_event + zero progress → parkable, correct resets_at_epoch."""
    stream = "\n".join([
        json.dumps({"type": "system", "subtype": "init", "session_id": "test-sess"}),
        json.dumps({"type": "rate_limit_event", "rate_limit_info": {
            "rateLimitType": "five_hour", "resetsAt": 1784053800,
            "overageStatus": "rejected", "status": "allowed"
        }}),
        json.dumps({"type": "assistant", "message": {
            "content": [{"type": "tool_use", "name": "Read", "input": {"file_path": "/tmp/plan.md"}}],
            "usage": {"output_tokens": 4}
        }}),
    ])
    result = runner._check_exit1_rate_limit(stream)
    assert result is not None
    assert result["session_limit"] is True
    assert result["resets_at_epoch"] == 1784053800.0


def test_exit1_no_rate_limit_event_not_parkable():
    """(ii) exit-1, NO rate_limit_event → NOT parkable (gate_failure)."""
    stream = "\n".join([
        json.dumps({"type": "system", "subtype": "init", "session_id": "test-sess"}),
        json.dumps({"type": "assistant", "message": {
            "content": [{"type": "text", "text": "Reading..."}],
            "usage": {"output_tokens": 10}
        }}),
    ])
    result = runner._check_exit1_rate_limit(stream)
    assert result is None


def test_exit1_five_hour_with_progress_not_parkable():
    """(iii) exit-1 + five_hour + Write tool_use + output_tokens >= 500 → NOT parkable."""
    stream = "\n".join([
        json.dumps({"type": "system", "subtype": "init", "session_id": "test-sess"}),
        json.dumps({"type": "rate_limit_event", "rate_limit_info": {
            "rateLimitType": "five_hour", "resetsAt": 1784053800,
            "overageStatus": "rejected"
        }}),
        json.dumps({"type": "assistant", "message": {
            "content": [{"type": "tool_use", "name": "Write", "input": {"file_path": "/tmp/out.md", "content": "findings..."}}],
            "usage": {"output_tokens": 2000}
        }}),
    ])
    result = runner._check_exit1_rate_limit(stream)
    assert result is None


def test_graceful_429_session_limit_still_parkable():
    """(iv) Graceful 429 'session limit' result (exit 0) → still parkable via existing _check_session_limit path (no regression)."""
    event = {
        "type": "result",
        "subtype": "success",
        "is_error": True,
        "api_error_status": 429,
        "num_turns": 1,
        "result": "You've hit your session limit · resets 11:50pm (America/Chicago)",
        "stop_reason": "stop_sequence",
        "total_cost_usd": 0,
        "usage": {"input_tokens": 0, "output_tokens": 0},
    }
    result = runner._check_session_limit(event)
    assert result is not None
    assert result["session_limit"] is True
    assert isinstance(result["resets_at_epoch"], float)
    assert result["resets_at_epoch"] > time.time()


# --- Integration tests: run_step end-to-end with mocked Popen ---


def _make_exit1_popen(stdout_data, stderr_data=""):
    """Create a mock Popen for exit-1 scenarios."""
    proc = MagicMock()
    proc.stdout = io.StringIO(stdout_data)
    proc.stderr = io.StringIO(stderr_data)
    proc.returncode = 1
    proc.poll = MagicMock(side_effect=[None, 1])
    proc.kill = MagicMock()
    return proc


def test_exit1_rate_limit_integration_parkable(tmp_path):
    """Integration: run_step with exit-1 + five_hour event + zero progress returns session_limit dict."""
    stream = "\n".join([
        json.dumps({"type": "system", "subtype": "init", "session_id": "test-sess"}),
        json.dumps({"type": "rate_limit_event", "rate_limit_info": {
            "rateLimitType": "five_hour", "resetsAt": 1784053800,
            "overageStatus": "rejected", "status": "allowed"
        }}),
        json.dumps({"type": "assistant", "message": {
            "content": [{"type": "tool_use", "name": "Read", "input": {"file_path": "/tmp/plan.md"}}],
            "usage": {"output_tokens": 4}
        }}),
    ])
    proc = _make_exit1_popen(stream)

    with patch("runner.LOGS_DIR", tmp_path), \
         patch("runner.subprocess.Popen", return_value=proc), \
         patch("runner.time.sleep"):
        result = runner.run_step("test", "/tmp", "claude-sonnet-4-6")

    assert result["session_limit"] is True
    assert result["resets_at_epoch"] == 1784053800.0
    assert result["stop_reason"] == "session_limit"
    assert result["is_error"] is True


def test_exit1_no_rate_limit_integration_gate_failure(tmp_path):
    """Integration: run_step with exit-1 but NO rate_limit_event → gate_failure (stop_reason='error')."""
    stream = "\n".join([
        json.dumps({"type": "system", "subtype": "init", "session_id": "test-sess"}),
        json.dumps({"type": "assistant", "message": {
            "content": [{"type": "text", "text": "Starting..."}],
            "usage": {"output_tokens": 10}
        }}),
    ])
    proc = _make_exit1_popen(stream)

    with patch("runner.LOGS_DIR", tmp_path), \
         patch("runner.subprocess.Popen", return_value=proc), \
         patch("runner.time.sleep"):
        result = runner.run_step("test", "/tmp", "claude-sonnet-4-6")

    assert result.get("session_limit") is not True
    assert result["stop_reason"] == "error"
    assert result["is_error"] is True


def test_exit1_five_hour_with_progress_integration_gate_failure(tmp_path):
    """Integration: run_step with exit-1 + five_hour + Write progress → gate_failure."""
    stream = "\n".join([
        json.dumps({"type": "system", "subtype": "init", "session_id": "test-sess"}),
        json.dumps({"type": "rate_limit_event", "rate_limit_info": {
            "rateLimitType": "five_hour", "resetsAt": 1784053800,
            "overageStatus": "rejected"
        }}),
        json.dumps({"type": "assistant", "message": {
            "content": [{"type": "tool_use", "name": "Write", "input": {"file_path": "/tmp/out.md", "content": "done"}}],
            "usage": {"output_tokens": 2000}
        }}),
    ])
    proc = _make_exit1_popen(stream)

    with patch("runner.LOGS_DIR", tmp_path), \
         patch("runner.subprocess.Popen", return_value=proc), \
         patch("runner.time.sleep"):
        result = runner.run_step("test", "/tmp", "claude-sonnet-4-6")

    assert result.get("session_limit") is not True
    assert result["stop_reason"] == "error"


# --- bellows.py backup guard test ---


def test_maybe_park_backup_guard_blocks_when_head_differs(tmp_path):
    """Backup guard: _maybe_park_session_limit returns False when worktree HEAD differs from baseline."""
    decisions_dir = tmp_path / "decisions"
    decisions_dir.mkdir()
    base_filename = "executable-888.md"
    inprogress_path = str(decisions_dir / f"in-progress-{base_filename}")
    with open(inprogress_path, "w") as f:
        f.write("# Test plan")

    parsed = {
        "session_limit": True,
        "resets_at_epoch": time.time() + 3600,
        "resets_at_raw": "",
        "session_id": "test-session",
        "cost_usd": 0.0,
    }

    with patch("bellows._capture_git_diff", return_value="abc123def"), \
         patch("bellows._teardown_worktree"), \
         patch("bellows.notifier"):
        result = bellows._maybe_park_session_limit(
            parsed, inprogress_path, 1, "888", "executable-888.md",
            base_filename, str(decisions_dir), None, str(tmp_path / "test.db"),
            "/tmp/project", "/tmp/wt", "", "", None,
            plan_baseline_sha="000000baseline",
        )
    assert result is False
    assert os.path.exists(inprogress_path)
