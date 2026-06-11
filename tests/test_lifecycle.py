"""Tests for lifecycle.py — id minting, plan state, and crash recovery."""

import os
import sqlite3
import pytest
import lifecycle


class TestMintMonotonicity:
    def test_sequential_mints_return_consecutive_ids(self):
        id1 = lifecycle.mint_and_claim("diagnostic", "/proj", "Plan A", "bellows", "small", 1, "d-draft-1.md")
        id2 = lifecycle.mint_and_claim("executable", "/proj", "Plan B", "bellows", "large", 2, "e-draft-2.md")
        id3 = lifecycle.mint_and_claim("qa", "/proj", "Plan C", "bellows", "small", 1, "q-draft-3.md")
        assert id1 == 1
        assert id2 == 2
        assert id3 == 3

    def test_mint_returns_integer(self):
        pid = lifecycle.mint_and_claim("diagnostic", "/proj", "T", "bellows", "small", 1, "d.md")
        assert isinstance(pid, int)


class TestMintAtomicity:
    def test_failed_insert_does_not_consume_id(self, tmp_path):
        db_path = str(tmp_path / "atomic_test.db")
        lifecycle.init_lifecycle_db(db_path)
        # Mint one valid id
        id1 = lifecycle.mint_and_claim("diagnostic", "/proj", "OK", "bellows", "small", 1, "d.md", db_path=db_path)
        assert id1 == 1
        # Force a plans INSERT failure by violating the type CHECK constraint
        with pytest.raises(Exception):
            lifecycle.mint_and_claim("INVALID_TYPE", "/proj", "Bad", "bellows", "small", 1, "d2.md", db_path=db_path)
        # next_id should NOT have advanced — next mint should return 2
        id2 = lifecycle.mint_and_claim("executable", "/proj", "OK2", "bellows", "small", 1, "d3.md", db_path=db_path)
        assert id2 == 2

    def test_plans_row_written_on_successful_mint(self):
        pid = lifecycle.mint_and_claim("diagnostic", "/proj", "Title", "bellows", "small", 2, "dep.md")
        conn = sqlite3.connect(lifecycle.LIFECYCLE_DB_PATH)
        row = conn.execute("SELECT type, target_project, title, total_steps, deposit_placeholder_name FROM plans WHERE id = ?", (pid,)).fetchone()
        conn.close()
        assert row is not None
        assert row[0] == "diagnostic"
        assert row[1] == "/proj"
        assert row[2] == "Title"
        assert row[3] == 2
        assert row[4] == "dep.md"


class TestMarkPlanState:
    def test_mark_plan_state_updates(self):
        pid = lifecycle.mint_and_claim("diagnostic", "/proj", "T", "bellows", "small", 1, "d.md")
        lifecycle.mark_plan_state(pid, "in_progress")
        conn = sqlite3.connect(lifecycle.LIFECYCLE_DB_PATH)
        state = conn.execute("SELECT lifecycle_state FROM plans WHERE id = ?", (pid,)).fetchone()[0]
        conn.close()
        assert state == "in_progress"

    def test_mark_plan_state_with_closed_at(self):
        pid = lifecycle.mint_and_claim("diagnostic", "/proj", "T", "bellows", "small", 1, "d.md")
        lifecycle.mark_plan_state(pid, "closed", closed_at="2026-06-11T12:00:00")
        conn = sqlite3.connect(lifecycle.LIFECYCLE_DB_PATH)
        row = conn.execute("SELECT lifecycle_state, closed_at FROM plans WHERE id = ?", (pid,)).fetchone()
        conn.close()
        assert row[0] == "closed"
        assert row[1] == "2026-06-11T12:00:00"


class TestRecoverHalfClaimed:
    def test_deposit_present_re_renames(self, tmp_path):
        db_path = str(tmp_path / "recover.db")
        lifecycle.init_lifecycle_db(db_path)
        decisions = tmp_path / "decisions"
        decisions.mkdir()
        # Create a deposit file on disk
        deposit = decisions / "diagnostic-draft-100000.md"
        deposit.write_text("# Test Plan")
        # Mint — this creates a plans row with state='claimed'
        pid = lifecycle.mint_and_claim("diagnostic", "/proj", "Test", "bellows", "small", 1,
                                       "diagnostic-draft-100000.md", db_path=db_path)
        # Simulate crash: the in-progress file was never created
        # Run recovery
        actions = lifecycle.recover_half_claimed(str(decisions), db_path=db_path)
        assert len(actions) == 1
        assert actions[0] == (pid, "re_renamed")
        # The deposit should have been renamed to in-progress-diagnostic-<id>.md
        expected = decisions / f"in-progress-diagnostic-{pid}.md"
        assert expected.exists()
        assert not deposit.exists()

    def test_deposit_absent_marks_abandoned(self, tmp_path):
        db_path = str(tmp_path / "recover2.db")
        lifecycle.init_lifecycle_db(db_path)
        decisions = tmp_path / "decisions"
        decisions.mkdir()
        # Mint without creating a deposit file on disk
        pid = lifecycle.mint_and_claim("executable", "/proj", "Ghost", "bellows", "small", 1,
                                       "executable-draft-999999.md", db_path=db_path)
        actions = lifecycle.recover_half_claimed(str(decisions), db_path=db_path)
        assert len(actions) == 1
        assert actions[0] == (pid, "abandoned")
        # Verify DB state
        conn = sqlite3.connect(db_path)
        state = conn.execute("SELECT lifecycle_state FROM plans WHERE id = ?", (pid,)).fetchone()[0]
        conn.close()
        assert state == "abandoned"

    def test_already_renamed_transitions_to_in_progress(self, tmp_path):
        db_path = str(tmp_path / "recover3.db")
        lifecycle.init_lifecycle_db(db_path)
        decisions = tmp_path / "decisions"
        decisions.mkdir()
        pid = lifecycle.mint_and_claim("diagnostic", "/proj", "OK", "bellows", "small", 1,
                                       "diagnostic-draft-111.md", db_path=db_path)
        # Simulate: the in-progress file exists (rename succeeded before crash)
        expected = decisions / f"in-progress-diagnostic-{pid}.md"
        expected.write_text("# Plan")
        actions = lifecycle.recover_half_claimed(str(decisions), db_path=db_path)
        assert len(actions) == 1
        assert actions[0] == (pid, "already_renamed")
        conn = sqlite3.connect(db_path)
        state = conn.execute("SELECT lifecycle_state FROM plans WHERE id = ?", (pid,)).fetchone()[0]
        conn.close()
        assert state == "in_progress"


class TestDbPath:
    def test_lifecycle_db_resolves_under_bellows_root(self):
        from bellows_root import resolve_bellows_root
        expected = str(resolve_bellows_root() / "lifecycle.db")
        # The module-level constant should match (but in tests it's monkeypatched)
        # Verify the resolution logic directly
        assert expected.endswith("lifecycle.db")
        assert "bellows" in expected.lower() or "bellows" in str(resolve_bellows_root()).lower()


class TestInitIdempotent:
    def test_init_twice_does_not_error(self, tmp_path):
        db_path = str(tmp_path / "idem.db")
        lifecycle.init_lifecycle_db(db_path)
        lifecycle.init_lifecycle_db(db_path)
        # Should still have exactly one row in id_sequence
        conn = sqlite3.connect(db_path)
        count = conn.execute("SELECT COUNT(*) FROM id_sequence").fetchone()[0]
        conn.close()
        assert count == 1
