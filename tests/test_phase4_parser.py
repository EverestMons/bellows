import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import parser


BASE_FIXTURE = {
    "type": "result",
    "subtype": "success",
    "is_error": False,
    "result": "Step 1 complete.",
    "stop_reason": "end_turn",
    "session_id": "abc123",
    "total_cost_usd": 0.10,
    "permission_denials": [],
}


def test_parser_returns_complete_for_end_turn():
    fixture = dict(BASE_FIXTURE)
    fixture["stop_reason"] = "end_turn"
    fixture["is_error"] = False
    result = parser.parse(fixture)
    assert result["receipt_status"] == "Complete"


def test_parser_returns_blocked_for_error():
    fixture = dict(BASE_FIXTURE)
    fixture["is_error"] = True
    result = parser.parse(fixture)
    assert result["receipt_status"] == "Blocked"


def test_parser_returns_partial_for_max_tokens():
    fixture = dict(BASE_FIXTURE)
    fixture["stop_reason"] = "max_tokens"
    fixture["is_error"] = False
    result = parser.parse(fixture)
    assert result["receipt_status"] == "Partial"
