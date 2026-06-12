"""Tests for diagnostic 6 fixes: resume-path plan_id recovery (G1),
num_turns parser passthrough (G2), and the record_step_end turns callsite (G3).

See knowledge/research/steps-table-coverage-forensics-2026-06-12.md.
"""

import os
import sqlite3
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import bellows
import lifecycle
import parser


# ---------------------------------------------------------------------------
# G1 — resume-path plan_id recovery from the id-canonical in-progress filename
# ---------------------------------------------------------------------------

class TestRecoverPlanIdFromFilename:
    def test_recovers_executable_id(self):
        assert bellows.recover_plan_id_from_filename("in-progress-executable-4.md") == 4

    def test_recovers_diagnostic_id(self):
        assert bellows.recover_plan_id_from_filename("in-progress-diagnostic-12.md") == 12

    def test_recovers_qa_id(self):
        assert bellows.recover_plan_id_from_filename("in-progress-qa-7.md") == 7

    def test_legacy_slug_date_name_returns_none_no_exception(self):
        # Legacy slug+date in-progress name must be tolerated indefinitely:
        # no integer id parses, so recovery returns None (lifecycle writes then
        # degrade silently) — and it must not raise.
        result = bellows.recover_plan_id_from_filename(
            "in-progress-executable-foo-bar-2026-05-28.md"
        )
        assert result is None

    def test_multidigit_id(self):
        assert bellows.recover_plan_id_from_filename("in-progress-diagnostic-1234.md") == 1234


# ---------------------------------------------------------------------------
# G2 — parser extracts num_turns from the result event into "turns"
# ---------------------------------------------------------------------------

class TestParserTurnsPassthrough:
    def _raw(self, **overrides):
        raw = {
            "result": "Done.",
            "stop_reason": "end_turn",
            "is_error": False,
            "session_id": "abc",
            "total_cost_usd": 0.5,
            "permission_denials": [],
        }
        raw.update(overrides)
        return raw

    def test_num_turns_mapped_to_turns(self):
        parsed = parser.parse(self._raw(num_turns=100))
        assert parsed["turns"] == 100

    def test_turns_none_when_field_absent(self):
        parsed = parser.parse(self._raw())
        assert parsed["turns"] is None


# ---------------------------------------------------------------------------
# G3 — record_step_end receives the turns value end-to-end
# ---------------------------------------------------------------------------

class TestTurnsReachesDb:
    def test_parsed_turns_lands_in_steps_row(self):
        # Mirror the bellows.py callsite: parse a raw result event carrying
        # num_turns, then pass turns=parsed.get("turns") into record_step_end.
        raw = {
            "result": "Step done.",
            "stop_reason": "end_turn",
            "is_error": False,
            "session_id": "s1",
            "total_cost_usd": 1.25,
            "num_turns": 42,
            "permission_denials": [],
        }
        parsed = parser.parse(raw)

        pid = lifecycle.mint_and_claim("executable", "/proj", "T", "bellows", "small", 1, "e.md")
        step_id = lifecycle.record_step_start(pid, 1)
        lifecycle.record_step_end(
            step_id,
            status="complete",
            cost_usd=parsed.get("cost_usd"),
            turns=parsed.get("turns"),
            duration_s=3.0,
        )

        conn = sqlite3.connect(lifecycle.LIFECYCLE_DB_PATH)
        row = conn.execute("SELECT turns, cost_usd FROM steps WHERE id = ?", (step_id,)).fetchone()
        conn.close()
        assert row[0] == 42
        assert abs(row[1] - 1.25) < 0.001
