import subprocess
from unittest.mock import patch

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import parser
import runner


CLEAN_FIXTURE = {
    "type": "result",
    "subtype": "success",
    "is_error": False,
    "result": (
        "Step 1 complete.\n\n---\n"
        "## Output Receipt\n"
        "**Agent:** Test\n"
        "**Step:** 1\n"
        "**Status:** Complete\n\n"
        "### Flags for CEO\n"
        "- None"
    ),
    "stop_reason": "end_turn",
    "session_id": "abc123",
    "total_cost_usd": 0.14,
    "permission_denials": [],
}


def test_parse_clean_output():
    result = parser.parse(CLEAN_FIXTURE)
    assert result["receipt_status"] == "Complete"
    assert result["ceo_flags"] == []
    assert result["escalate"] is False
    assert parser.is_clean(result) is True


def test_parse_blocked_output():
    fixture = dict(CLEAN_FIXTURE)
    fixture["is_error"] = True
    fixture["result"] = (
        "Step 1 failed.\n\n---\n"
        "### Flags for CEO\n"
        "- Schema drift detected"
    )
    result = parser.parse(fixture)
    assert result["receipt_status"] == "Blocked"
    assert result["ceo_flags"] == ["Schema drift detected"]
    assert result["escalate"] is True


def test_run_step_timeout():
    class FakeProcess:
        """Simulates a process that produces no output and never exits on its own."""
        def __init__(self, *args, **kwargs):
            self.stdout = iter([])  # empty iterator — reader thread finishes instantly
            self.stderr = iter([])

        def poll(self):
            return None  # process appears to still be running

        def kill(self):
            pass  # accept the kill silently

    with patch("runner.subprocess.Popen", return_value=FakeProcess()), \
         patch("runner.time.sleep"):
        result = runner.run_step("test prompt", "/tmp", "claude-sonnet-4-6", timeout=0)
    assert result["is_error"] is True
    assert result["stop_reason"] == "timeout"
    assert result["escalate"] is True


def _flag_raw(result_text):
    return {
        "result": result_text,
        "stop_reason": "end_turn",
        "is_error": False,
        "session_id": "test",
        "total_cost_usd": 0.0,
        "permission_denials": [],
    }


def test_parse_paragraph_form_no_longer_extracted():
    # H3 with mismatched heading ("CEO Flag" vs "Flags for CEO") — not recognized
    text = (
        "Done.\n\n"
        "### CEO Flag\n\n"
        "Some paragraph text\n"
    )
    result = parser.parse(_flag_raw(text))
    assert result["ceo_flags"] == []


def test_parse_h3_flags_for_ceo_bulleted_regression():
    text = (
        "Done.\n\n"
        "### Flags for CEO\n"
        "- Bulleted flag one\n"
        "- Bulleted flag two\n"
    )
    result = parser.parse(_flag_raw(text))
    assert result["ceo_flags"] == ["Bulleted flag one", "Bulleted flag two"]


def test_parse_h3_flags_for_ceo_none_regression():
    text = (
        "Done.\n\n"
        "### Flags for CEO\n"
        "- None\n"
    )
    result = parser.parse(_flag_raw(text))
    assert result["ceo_flags"] == []
    assert result["escalate"] is False


def test_parse_verdict_requested_present():
    text = "Step done.\nVERDICT_REQUESTED: agent found inconsistency\nMore text."
    result = parser.parse(_flag_raw(text))
    assert result["verdict_requested"] == {"requested": True, "reason": "agent found inconsistency"}


def test_parse_verdict_requested_absent():
    text = "Step done. No issues."
    result = parser.parse(_flag_raw(text))
    assert result["verdict_requested"] == {"requested": False, "reason": None}


def test_parse_verdict_requested_mid_text():
    text = (
        "I completed the analysis.\n"
        "Results look inconsistent with the plan.\n"
        "VERDICT_REQUESTED: schema drift detected in step output\n"
        "I will stop here and wait for CEO review.\n"
        "Further notes below."
    )
    result = parser.parse(_flag_raw(text))
    assert result["verdict_requested"]["requested"] is True
    assert result["verdict_requested"]["reason"] == "schema drift detected in step output"
