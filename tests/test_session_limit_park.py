"""Tests for session-limit detection and resets-at parsing (plan 148, Step 1)."""

import sys
import os
import time
from datetime import datetime, timedelta
from unittest.mock import patch
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
