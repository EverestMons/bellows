import importlib
import io
import json
from unittest.mock import patch, MagicMock

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import runner


# --- DISABLE_AUTOUPDATER env-var contract ---

def test_runner_sets_disable_autoupdater_env_var():
    """Importing runner must set DISABLE_AUTOUPDATER=1 in the process environment."""
    assert os.environ.get("DISABLE_AUTOUPDATER") == "1"


def test_runner_respects_explicit_disable_autoupdater_override(monkeypatch):
    """setdefault must not overwrite an explicit operator override."""
    monkeypatch.setenv("DISABLE_AUTOUPDATER", "0")
    importlib.reload(runner)
    assert os.environ.get("DISABLE_AUTOUPDATER") == "0"
    # Restore default so subsequent tests aren't affected
    monkeypatch.setenv("DISABLE_AUTOUPDATER", "1")
    importlib.reload(runner)


# --- NDJSON mock data ---

_SYSTEM_EVENT = json.dumps({
    "type": "system",
    "subtype": "init",
    "session_id": "abc123",
    "tools": [],
    "model": "claude-sonnet-4-20250514",
})

_RESULT_EVENT = json.dumps({
    "type": "result",
    "subtype": "success",
    "is_error": False,
    "result": "Step 1 complete.",
    "stop_reason": "end_turn",
    "session_id": "abc123",
    "total_cost_usd": 0.14,
    "permission_denials": [],
})

CLEAN_NDJSON = _SYSTEM_EVENT + "\n" + _RESULT_EVENT + "\n"


def _make_mock_popen(stdout_data=CLEAN_NDJSON, stderr_data="", returncode=0):
    """Create a mock Popen object compatible with runner.py's threading model."""
    proc = MagicMock()
    proc.stdout = io.StringIO(stdout_data)
    proc.stderr = io.StringIO(stderr_data)
    proc.returncode = returncode
    # poll() returns None once (threads get a chance to read), then returncode
    proc.poll = MagicMock(side_effect=[None, returncode])
    proc.kill = MagicMock()
    return proc


# --- Timeout behavior ---

def test_configurable_timeout_respected():
    """Custom timeout value is used for inactivity detection."""
    proc = MagicMock()
    proc.stdout = io.StringIO("")
    proc.stderr = io.StringIO("")
    proc.returncode = -9
    proc.poll = MagicMock(return_value=None)
    proc.kill = MagicMock()

    with patch("runner.subprocess.Popen", return_value=proc), \
         patch("runner.time.monotonic", side_effect=[0.0, 0.0, 11.0, 11.0]), \
         patch("runner.time.sleep"):
        result = runner.run_step("test", "/tmp", "claude-sonnet-4-6", timeout=10)
    assert result["is_error"] is True
    assert result["error"] == "timeout"


def test_timeout_returns_cost_none():
    proc = MagicMock()
    proc.stdout = io.StringIO("")
    proc.stderr = io.StringIO("")
    proc.returncode = -9
    proc.poll = MagicMock(return_value=None)
    proc.kill = MagicMock()

    with patch("runner.subprocess.Popen", return_value=proc), \
         patch("runner.time.monotonic", side_effect=[0.0, 0.0, 301.0, 301.0]), \
         patch("runner.time.sleep"):
        result = runner.run_step("test", "/tmp", "claude-sonnet-4-6")
    assert result["cost_usd"] is None


def test_timeout_writes_log_file(tmp_path):
    proc = MagicMock()
    proc.stdout = io.StringIO("")
    proc.stderr = io.StringIO("")
    proc.returncode = -9
    proc.poll = MagicMock(return_value=None)
    proc.kill = MagicMock()

    with patch("runner.LOGS_DIR", tmp_path), \
         patch("runner.subprocess.Popen", return_value=proc), \
         patch("runner.time.monotonic", side_effect=[0.0, 0.0, 301.0, 301.0]), \
         patch("runner.time.sleep"):
        runner.run_step("test", "/tmp", "claude-sonnet-4-6")
    log_files = list(tmp_path.glob("*.json"))
    assert len(log_files) == 1
    data = json.loads(log_files[0].read_text())
    assert data["success"] is False
    assert data["error"] == "timeout"


def test_timeout_persists_accumulated_output(tmp_path):
    """Timeout-killed process with accumulated stdout carries output in result_text and log raw_output."""
    accumulated_output = "line1: agent starting work\nline2: reading files\n"
    proc = MagicMock()
    proc.stdout = io.StringIO(accumulated_output)
    proc.stderr = io.StringIO("")
    proc.returncode = -9
    proc.poll = MagicMock(return_value=None)
    proc.kill = MagicMock()

    call_count = [0]
    def fake_monotonic():
        call_count[0] += 1
        return float(call_count[0])

    with patch("runner.LOGS_DIR", tmp_path), \
         patch("runner.subprocess.Popen", return_value=proc), \
         patch("runner.time.monotonic", side_effect=fake_monotonic), \
         patch("runner.time.sleep"):
        result = runner.run_step("test", "/tmp", "claude-sonnet-4-6", timeout=1)

    # result_text carries the accumulated output
    assert "line1: agent starting work" in result["result_text"]
    assert "line2: reading files" in result["result_text"]
    assert result["is_error"] is True
    assert result["error"] == "timeout"

    # Step JSON log carries raw_output
    log_files = list(tmp_path.glob("*.json"))
    assert len(log_files) == 1
    data = json.loads(log_files[0].read_text())
    assert "line1: agent starting work" in data["raw_output"]
    assert "line2: reading files" in data["raw_output"]


def test_timeout_truncates_output_at_5000(tmp_path):
    """Timeout output is capped at 5000 characters in both result_text and raw_output."""
    long_output = "x" * 10000 + "\n"
    proc = MagicMock()
    proc.stdout = io.StringIO(long_output)
    proc.stderr = io.StringIO("")
    proc.returncode = -9
    proc.poll = MagicMock(return_value=None)
    proc.kill = MagicMock()

    call_count = [0]
    def fake_monotonic():
        call_count[0] += 1
        return float(call_count[0])

    with patch("runner.LOGS_DIR", tmp_path), \
         patch("runner.subprocess.Popen", return_value=proc), \
         patch("runner.time.monotonic", side_effect=fake_monotonic), \
         patch("runner.time.sleep"):
        result = runner.run_step("test", "/tmp", "claude-sonnet-4-6", timeout=1)

    assert len(result["result_text"]) == 5000

    log_files = list(tmp_path.glob("*.json"))
    data = json.loads(log_files[0].read_text())
    assert len(data["raw_output"]) == 5000


def test_timeout_silent_stall_empty_strings(tmp_path):
    """Genuinely-silent stall (no output before timeout) yields empty result_text and raw_output, no exception."""
    proc = MagicMock()
    proc.stdout = io.StringIO("")
    proc.stderr = io.StringIO("")
    proc.returncode = -9
    proc.poll = MagicMock(return_value=None)
    proc.kill = MagicMock()

    with patch("runner.LOGS_DIR", tmp_path), \
         patch("runner.subprocess.Popen", return_value=proc), \
         patch("runner.time.monotonic", side_effect=[0.0, 0.0, 301.0, 301.0]), \
         patch("runner.time.sleep"):
        result = runner.run_step("test", "/tmp", "claude-sonnet-4-6")

    assert result["result_text"] == ""
    assert result["is_error"] is True
    assert result["error"] == "timeout"

    log_files = list(tmp_path.glob("*.json"))
    assert len(log_files) == 1
    data = json.loads(log_files[0].read_text())
    assert data["raw_output"] == ""


# --- Generic exception (Popen fails to launch) ---

def test_generic_exception_returns_cost_none():
    with patch("runner.subprocess.Popen", side_effect=OSError("disk full")):
        result = runner.run_step("test", "/tmp", "claude-sonnet-4-6")
    assert result["cost_usd"] is None


def test_generic_exception_message_contains_actual_error():
    with patch("runner.subprocess.Popen", side_effect=OSError("disk full")):
        result = runner.run_step("test", "/tmp", "claude-sonnet-4-6")
    assert "disk full" in result["ceo_flags"][0]
    assert result["stop_reason"] == "error"


def test_generic_exception_writes_log_file(tmp_path):
    with patch("runner.LOGS_DIR", tmp_path), \
         patch("runner.subprocess.Popen", side_effect=OSError("disk full")):
        runner.run_step("test", "/tmp", "claude-sonnet-4-6")
    log_files = list(tmp_path.glob("*.json"))
    assert len(log_files) == 1
    data = json.loads(log_files[0].read_text())
    assert data["success"] is False
    assert data["exception_type"] == "OSError"


# --- Success path ---

def test_success_writes_log_file(tmp_path):
    proc = _make_mock_popen()
    with patch("runner.LOGS_DIR", tmp_path), \
         patch("runner.subprocess.Popen", return_value=proc), \
         patch("runner.time.sleep"):
        runner.run_step("test", "/tmp", "claude-sonnet-4-6")
    log_files = list(tmp_path.glob("*.json"))
    assert len(log_files) == 1
    data = json.loads(log_files[0].read_text())
    assert data["success"] is True


def test_stderr_printed_on_success(capsys):
    proc = _make_mock_popen(stderr_data="warning: something")
    with patch("runner.subprocess.Popen", return_value=proc), \
         patch("runner.time.sleep"):
        runner.run_step("test", "/tmp", "claude-sonnet-4-6")
    captured = capsys.readouterr()
    assert "warning: something" in captured.out


# --- No result event (replaces json_decode_error tests) ---

def test_no_result_event_returns_blocked():
    proc = _make_mock_popen(stdout_data="NOT JSON\n")
    with patch("runner.subprocess.Popen", return_value=proc), \
         patch("runner.time.sleep"):
        result = runner.run_step("test", "/tmp", "claude-sonnet-4-6")
    assert result["is_error"] is True
    assert result["receipt_status"] == "Blocked"
    assert result["cost_usd"] is None
    assert result["session_id"] is None
    assert "no_result_event" in result["error"]


def test_no_result_event_writes_log_with_raw_output(tmp_path):
    proc = _make_mock_popen(stdout_data="NOT JSON AT ALL\n")
    with patch("runner.LOGS_DIR", tmp_path), \
         patch("runner.subprocess.Popen", return_value=proc), \
         patch("runner.time.sleep"):
        runner.run_step("test", "/tmp", "claude-sonnet-4-6")
    log_files = list(tmp_path.glob("*.json"))
    assert len(log_files) == 1
    data = json.loads(log_files[0].read_text())
    assert data["success"] is False
    assert data["error"] == "no_result_event"
    assert "NOT JSON AT ALL" in data["raw_output"]


# --- New: NDJSON parsing ---

def test_ndjson_parse_valid_stream():
    """Happy path: multi-event NDJSON stream extracts result event correctly."""
    assistant_event = json.dumps({
        "type": "assistant",
        "message": {"role": "assistant", "content": [{"type": "text", "text": "Hello"}]},
        "session_id": "abc123",
    })
    user_event = json.dumps({
        "type": "user",
        "message": {"role": "user", "content": [{"type": "tool_result", "content": "ok"}]},
        "session_id": "abc123",
    })
    ndjson = _SYSTEM_EVENT + "\n" + assistant_event + "\n" + user_event + "\n" + _RESULT_EVENT + "\n"
    proc = _make_mock_popen(stdout_data=ndjson)

    with patch("runner.subprocess.Popen", return_value=proc), \
         patch("runner.time.sleep"):
        result = runner.run_step("test", "/tmp", "claude-sonnet-4-6")

    assert result["is_error"] is False
    assert result["session_id"] == "abc123"
    assert result["result_text"] == "Step 1 complete."
    assert result["cost_usd"] == 0.14
    assert result["stop_reason"] == "end_turn"
    assert result["receipt_status"] == "Complete"


def test_ndjson_parse_malformed_line_skipped(capsys):
    """Malformed line is skipped (not fatal), result event still extracted."""
    ndjson = _SYSTEM_EVENT + "\n" + "THIS IS NOT JSON\n" + _RESULT_EVENT + "\n"
    proc = _make_mock_popen(stdout_data=ndjson)

    with patch("runner.subprocess.Popen", return_value=proc), \
         patch("runner.time.sleep"):
        result = runner.run_step("test", "/tmp", "claude-sonnet-4-6")

    assert result["is_error"] is False
    assert result["session_id"] == "abc123"
    captured = capsys.readouterr()
    assert "skipping malformed NDJSON line" in captured.out


def test_ndjson_parse_missing_result_event():
    """Stream with valid JSON events but no result event produces distinct error path."""
    ndjson = _SYSTEM_EVENT + "\n"
    proc = _make_mock_popen(stdout_data=ndjson)

    with patch("runner.subprocess.Popen", return_value=proc), \
         patch("runner.time.sleep"):
        result = runner.run_step("test", "/tmp", "claude-sonnet-4-6")

    assert result["is_error"] is True
    assert "no_result_event" in result["error"]
    assert result["receipt_status"] == "Blocked"
    assert result["cost_usd"] is None


def test_resume_session_flag_in_command():
    """When session_id is passed, command includes --resume alongside stream-json flags."""
    proc = _make_mock_popen()

    with patch("runner.subprocess.Popen", return_value=proc) as mock_popen, \
         patch("runner.time.sleep"):
        runner.run_step("test", "/tmp", "claude-sonnet-4-6", session_id="sess-xyz")

    cmd = mock_popen.call_args[0][0]
    assert "--output-format" in cmd
    idx = cmd.index("--output-format")
    assert cmd[idx + 1] == "stream-json"
    assert "--verbose" in cmd
    assert "--resume" in cmd
    assert "sess-xyz" in cmd


def test_append_system_prompt_flag_in_command():
    """A1 verification: --append-system-prompt with BELLOWS_AGENT_SYSTEM_PROMPT is in cmd."""
    proc = _make_mock_popen()

    with patch("runner.subprocess.Popen", return_value=proc) as mock_popen, \
         patch("runner.time.sleep"):
        runner.run_step("test", "/tmp", "claude-sonnet-4-6")

    cmd = mock_popen.call_args[0][0]
    assert "--append-system-prompt" in cmd
    idx = cmd.index("--append-system-prompt")
    assert cmd[idx + 1] == runner.BELLOWS_AGENT_SYSTEM_PROMPT


# --- Transient-failure retry ---

def test_run_step_retries_on_transient_401():
    """Transient 401 stderr triggers a single retry; success on retry returns is_error=False."""
    fail_proc = _make_mock_popen(stdout_data="", stderr_data="401 Unauthorized", returncode=1)
    success_proc = _make_mock_popen(stdout_data=CLEAN_NDJSON, stderr_data="", returncode=0)

    with patch("runner.subprocess.Popen", side_effect=[fail_proc, success_proc]), \
         patch("runner.time.sleep") as mock_sleep:
        result = runner.run_step("test", "/tmp", "claude-sonnet-4-6")

    assert result["is_error"] is False
    mock_sleep.assert_any_call(5)
    assert sum(1 for c in mock_sleep.call_args_list if c == ((5,),)) == 1


def test_run_step_does_not_retry_on_non_transient_error():
    """Non-transient stderr (no 401/429 indicators) goes straight to Blocked, no retry."""
    proc = _make_mock_popen(stdout_data="", stderr_data="Permission denied", returncode=1)

    with patch("runner.subprocess.Popen", return_value=proc), \
         patch("runner.time.sleep") as mock_sleep:
        result = runner.run_step("test", "/tmp", "claude-sonnet-4-6")

    assert result["is_error"] is True
    assert result["escalate"] is True
    assert result["receipt_status"] == "Blocked"
    # time.sleep(5) should NOT have been called (only time.sleep(1) from poll loop)
    for call in mock_sleep.call_args_list:
        assert call != ((5,),)
