"""Source-text tests for verdict-signal-2026-09-01.

Guards the structural invariants written by the plan:
  - bellows.py carries exactly 4 mark_plan_state(plan_id, "awaiting_verdict") writes
  - bellows.py carries exactly 1 mark_plan_state(_lc_plan_id, "awaiting_verdict") write
  - the resume restore (in_progress) precedes handle_new_plan in text order
  - depositor.py's _resolve_in_flight_writes SQL includes 'awaiting_verdict'
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _bellows_src():
    return (ROOT / "bellows.py").read_text()


def _depositor_src():
    return (ROOT / "depositor.py").read_text()


class TestBellowsMarkPlanStateWrites:
    def test_plan_id_awaiting_verdict_count(self):
        src = _bellows_src()
        assert src.count('mark_plan_state(plan_id, "awaiting_verdict")') == 4

    def test_lc_plan_id_awaiting_verdict_count(self):
        src = _bellows_src()
        assert src.count('mark_plan_state(_lc_plan_id, "awaiting_verdict")') == 1

    def test_resume_restore_precedes_handle_new_plan(self):
        src = _bellows_src()
        restore_idx = src.index('mark_plan_state(_lc_plan_id, "in_progress")')
        resume_idx = src.index("handle_new_plan(inprogress_path, resume_step=next_step)")
        assert restore_idx < resume_idx, (
            "resume mark_plan_state(in_progress) must appear before handle_new_plan in text order"
        )


class TestDepositorInFlightGuard:
    def test_depositor_in_flight_sql_includes_awaiting_verdict(self):
        src = _depositor_src()
        assert "'awaiting_verdict'" in src, (
            "D1: depositor._resolve_in_flight_writes must include 'awaiting_verdict' in its SQL"
        )
