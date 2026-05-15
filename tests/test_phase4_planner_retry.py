import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from unittest.mock import patch, MagicMock, call
import planner

PARSED_FIXTURE = {
    "receipt_status": "Complete",
    "escalate": False,
    "ceo_flags": [],
    "result_text": "done",
    "cost_usd": 0.1,
    "permission_denials": [],
}

AUTH_ERROR_STDOUT = json.dumps({
    "type": "result",
    "subtype": "success",
    "is_error": True,
    "result": "Failed to authenticate. API Error: 401 {\"type\":\"error\"}",
    "stop_reason": "stop_sequence",
    "session_id": "x",
    "total_cost_usd": 0.0,
    "permission_denials": [],
})

SUCCESS_STDOUT = json.dumps({
    "type": "result",
    "subtype": "success",
    "is_error": False,
    "result": '{"decision": "continue", "reason": "Step looks good", "next_step_prompt": null}',
    "stop_reason": "end_turn",
    "session_id": "y",
    "total_cost_usd": 0.05,
    "permission_denials": [],
})


@patch("planner.time.sleep")
@patch("planner.subprocess.run")
def test_planner_retries_on_auth_failure(mock_run, mock_sleep):
    """First call returns 401 auth error, second call succeeds."""
    mock_run.side_effect = [
        MagicMock(stdout=AUTH_ERROR_STDOUT),
        MagicMock(stdout=SUCCESS_STDOUT),
    ]
    result = planner.consult(PARSED_FIXTURE, "plan text", 1, "claude-sonnet-4-6")
    assert result["decision"] == "continue"
    assert result["reason"] == "Step looks good"
    assert mock_run.call_count == 2
    mock_sleep.assert_called_once_with(5)


@patch("planner.time.sleep")
@patch("planner.subprocess.run")
def test_planner_falls_back_to_continue_on_persistent_failure(mock_run, mock_sleep):
    """Both calls return 401 auth error — should fall back to continue."""
    mock_run.side_effect = [
        MagicMock(stdout=AUTH_ERROR_STDOUT),
        MagicMock(stdout=AUTH_ERROR_STDOUT),
    ]
    result = planner.consult(PARSED_FIXTURE, "plan text", 1, "claude-sonnet-4-6")
    assert result["decision"] == "continue"
    assert "Planner unavailable" in result["reason"]
    assert "401" in result["reason"]
    assert mock_run.call_count == 2
