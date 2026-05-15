import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from unittest.mock import patch, MagicMock
import subprocess
import planner

PARSED_FIXTURE = {
    "receipt_status": "Complete",
    "escalate": False,
    "ceo_flags": [],
    "result_text": "done",
    "cost_usd": 0.1,
    "permission_denials": [],
}


def test_build_consult_file():
    path = planner.build_consult_file(PARSED_FIXTURE, "plan text", 1)
    assert os.path.exists(path)
    content = open(path).read()
    assert "Eluvian Project Planner" in content
    assert "continue" in content
    os.unlink(path)


@patch("planner.subprocess.run")
def test_consult_bad_json(mock_run):
    mock_run.return_value = MagicMock(
        stdout='{"type":"result","subtype":"success","is_error":false,"result":"not json","stop_reason":"end_turn","session_id":"x","total_cost_usd":0.0,"permission_denials":[]}'
    )
    result = planner.consult(PARSED_FIXTURE, "plan text", 1, "claude-sonnet-4-6")
    assert result["decision"] == "continue"
    assert "not valid JSON" in result["reason"]


@patch("planner.subprocess.run")
def test_consult_timeout(mock_run):
    mock_run.side_effect = subprocess.TimeoutExpired("claude", 120)
    result = planner.consult(PARSED_FIXTURE, "plan text", 1, "claude-sonnet-4-6")
    assert result["decision"] == "escalate"
    assert "timed out" in result["reason"]
