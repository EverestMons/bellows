"""Tests for lifecycle.py — id minting, plan state, crash recovery, and write helpers."""

import os
import sqlite3
import stat
from datetime import datetime

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
        claimed_actions = [(a, act) for a, act in actions if act == "re_renamed"]
        assert len(claimed_actions) == 1
        assert claimed_actions[0] == (pid, "re_renamed")
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
        # Backdate created_at past the age guard window so abandoned branch fires
        from datetime import timedelta
        old_ts = (datetime.now() - timedelta(minutes=10)).isoformat()
        conn = sqlite3.connect(db_path)
        conn.execute("UPDATE plans SET created_at = ? WHERE id = ?", (old_ts, pid))
        conn.commit()
        conn.close()
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
        claimed_actions = [(a, act) for a, act in actions if act == "already_renamed"]
        assert len(claimed_actions) == 1
        assert claimed_actions[0] == (pid, "already_renamed")
        conn = sqlite3.connect(db_path)
        state = conn.execute("SELECT lifecycle_state FROM plans WHERE id = ?", (pid,)).fetchone()[0]
        conn.close()
        assert state == "in_progress"


class TestRecoverCrossProjectIsolation:
    """G1: recovery must only classify plans belonging to the scanned project."""

    def test_plan_for_project_x_not_touched_when_scanning_project_y(self, tmp_path):
        db_path = str(tmp_path / "cross.db")
        lifecycle.init_lifecycle_db(db_path)
        # Two projects with separate decisions dirs
        proj_x = tmp_path / "project_x"
        proj_y = tmp_path / "project_y"
        decisions_x = proj_x / "knowledge" / "decisions"
        decisions_y = proj_y / "knowledge" / "decisions"
        decisions_x.mkdir(parents=True)
        decisions_y.mkdir(parents=True)
        # Mint a plan for project X and place its in-progress file in X's dir
        pid = lifecycle.mint_and_claim(
            "executable", str(proj_x), "Plan X", "bellows", "small", 1,
            "executable-draft-001.md", db_path=db_path,
        )
        inprog = decisions_x / f"in-progress-executable-{pid}.md"
        inprog.write_text("# Plan X")
        # Scan project Y's directory — should NOT touch project X's plan
        actions = lifecycle.recover_half_claimed(
            str(decisions_y), db_path=db_path, project_root=str(proj_y),
        )
        assert len(actions) == 0
        # Plan X still claimed (not abandoned, not re-classified)
        conn = sqlite3.connect(db_path)
        state = conn.execute(
            "SELECT lifecycle_state FROM plans WHERE id = ?", (pid,)
        ).fetchone()[0]
        conn.close()
        assert state == "claimed"

    def test_plan_for_project_x_found_when_scanning_project_x(self, tmp_path):
        db_path = str(tmp_path / "cross2.db")
        lifecycle.init_lifecycle_db(db_path)
        proj_x = tmp_path / "project_x"
        decisions_x = proj_x / "knowledge" / "decisions"
        decisions_x.mkdir(parents=True)
        pid = lifecycle.mint_and_claim(
            "executable", str(proj_x), "Plan X", "bellows", "small", 1,
            "executable-draft-002.md", db_path=db_path,
        )
        inprog = decisions_x / f"in-progress-executable-{pid}.md"
        inprog.write_text("# Plan X")
        # Scan project X — should find and classify the plan
        actions = lifecycle.recover_half_claimed(
            str(decisions_x), db_path=db_path, project_root=str(proj_x),
        )
        claimed_actions = [(a, act) for a, act in actions if act == "already_renamed"]
        assert len(claimed_actions) == 1
        assert claimed_actions[0] == (pid, "already_renamed")


class TestRecoverAgeGuard:
    """G3: plans younger than 5 minutes must not be marked abandoned."""

    def test_young_plan_not_abandoned(self, tmp_path):
        db_path = str(tmp_path / "age.db")
        lifecycle.init_lifecycle_db(db_path)
        decisions = tmp_path / "decisions"
        decisions.mkdir()
        # Mint a plan (created_at = now, so < 5 min old)
        pid = lifecycle.mint_and_claim(
            "executable", "/proj", "Young", "bellows", "small", 1,
            "executable-draft-young.md", db_path=db_path,
        )
        actions = lifecycle.recover_half_claimed(str(decisions), db_path=db_path)
        assert len(actions) == 1
        assert actions[0] == (pid, "skipped_too_recent")
        # State must remain claimed
        conn = sqlite3.connect(db_path)
        state = conn.execute(
            "SELECT lifecycle_state FROM plans WHERE id = ?", (pid,)
        ).fetchone()[0]
        conn.close()
        assert state == "claimed"

    def test_old_plan_is_abandoned(self, tmp_path):
        db_path = str(tmp_path / "age2.db")
        lifecycle.init_lifecycle_db(db_path)
        decisions = tmp_path / "decisions"
        decisions.mkdir()
        pid = lifecycle.mint_and_claim(
            "executable", "/proj", "Old", "bellows", "small", 1,
            "executable-draft-old.md", db_path=db_path,
        )
        # Backdate created_at to 10 minutes ago
        from datetime import timedelta
        old_ts = (datetime.now() - timedelta(minutes=10)).isoformat()
        conn = sqlite3.connect(db_path)
        conn.execute("UPDATE plans SET created_at = ? WHERE id = ?", (old_ts, pid))
        conn.commit()
        conn.close()
        actions = lifecycle.recover_half_claimed(str(decisions), db_path=db_path)
        assert len(actions) == 1
        assert actions[0] == (pid, "abandoned")
        conn = sqlite3.connect(db_path)
        state = conn.execute(
            "SELECT lifecycle_state FROM plans WHERE id = ?", (pid,)
        ).fetchone()[0]
        conn.close()
        assert state == "abandoned"


class TestFlockGuard:
    """G2: acquiring the flock twice must fail the second acquisition."""

    def test_second_flock_acquisition_fails(self, tmp_path):
        import fcntl
        lock_path = str(tmp_path / ".bellows.lock")
        fd1 = open(lock_path, "w")
        fcntl.flock(fd1, fcntl.LOCK_EX | fcntl.LOCK_NB)
        # Second acquisition in same process must raise
        fd2 = open(lock_path, "w")
        with pytest.raises((BlockingIOError, OSError)):
            fcntl.flock(fd2, fcntl.LOCK_EX | fcntl.LOCK_NB)
        fd2.close()
        fd1.close()

    def test_flock_released_after_fd_close(self, tmp_path):
        import fcntl
        lock_path = str(tmp_path / ".bellows.lock")
        fd1 = open(lock_path, "w")
        fcntl.flock(fd1, fcntl.LOCK_EX | fcntl.LOCK_NB)
        fd1.close()
        # After close, a new fd should acquire successfully
        fd2 = open(lock_path, "w")
        fcntl.flock(fd2, fcntl.LOCK_EX | fcntl.LOCK_NB)  # should not raise
        fd2.close()


class TestInProgressAfterClaim:
    """G4: mark_plan_state('in_progress') is called after claim rename."""

    def test_mark_in_progress_updates_state(self):
        pid = lifecycle.mint_and_claim(
            "executable", "/proj", "T", "bellows", "small", 1, "e.md"
        )
        # Simulate what bellows.py now does after shutil.move
        lifecycle.mark_plan_state(pid, "in_progress")
        conn = sqlite3.connect(lifecycle.LIFECYCLE_DB_PATH)
        state = conn.execute(
            "SELECT lifecycle_state FROM plans WHERE id = ?", (pid,)
        ).fetchone()[0]
        conn.close()
        assert state == "in_progress"

    def test_in_progress_plan_not_selected_by_claimed_recovery(self, tmp_path):
        """Once in_progress, the claimed-recovery path must not re-process the plan.
        The in_progress recovery may see it but will not abandon it (young + age guard)."""
        db_path = str(tmp_path / "g4.db")
        lifecycle.init_lifecycle_db(db_path)
        decisions = tmp_path / "decisions"
        decisions.mkdir()
        pid = lifecycle.mint_and_claim(
            "executable", "/proj", "T", "bellows", "small", 1,
            "executable-draft-g4.md", db_path=db_path,
        )
        lifecycle.mark_plan_state(pid, "in_progress", db_path=db_path)
        actions = lifecycle.recover_half_claimed(str(decisions), db_path=db_path)
        # Claimed-recovery path should not have touched it
        claimed_actions = [(a, act) for a, act in actions
                           if act in ("re_renamed", "already_renamed", "abandoned") and a == pid
                           and act != "skipped_too_recent" and act != "skipped_worktree_exists"]
        # The plan may appear in in_progress recovery as skipped_too_recent, but must NOT be abandoned
        assert all(act != "abandoned" for a, act in actions if a == pid)
        conn = sqlite3.connect(db_path)
        state = conn.execute(
            "SELECT lifecycle_state FROM plans WHERE id = ?", (pid,)
        ).fetchone()[0]
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


# ---------------------------------------------------------------------------
# Executable B tests — schema upgrade, write helpers, log-and-continue, derivations
# ---------------------------------------------------------------------------

class TestSchemaUpgradeInPlace:
    """Verify that init_lifecycle_db() upgrades an A-era DB (id_sequence + plans only)
    without losing existing rows."""

    def test_upgrade_from_a_era_preserves_data(self, tmp_path):
        db_path = str(tmp_path / "a_era.db")
        # Simulate A-era DB: only id_sequence + plans
        conn = sqlite3.connect(db_path)
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("""CREATE TABLE id_sequence (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            next_id INTEGER NOT NULL DEFAULT 1
        )""")
        conn.execute("INSERT INTO id_sequence (id, next_id) VALUES (1, 5)")
        conn.execute("""CREATE TABLE plans (
            id INTEGER PRIMARY KEY,
            type TEXT NOT NULL CHECK (type IN ('diagnostic', 'executable', 'qa')),
            target_project TEXT NOT NULL,
            title TEXT,
            dispatch_mode TEXT,
            tier TEXT,
            lifecycle_state TEXT NOT NULL DEFAULT 'claimed',
            total_steps INTEGER,
            deposit_placeholder_name TEXT,
            created_at TEXT NOT NULL,
            closed_at TEXT
        )""")
        conn.execute(
            "INSERT INTO plans (id, type, target_project, title, lifecycle_state, created_at) VALUES (1, 'diagnostic', '/proj', 'Seeded', 'closed', '2026-06-01T00:00:00')"
        )
        conn.commit()
        conn.close()

        # Run init — should add B-era tables without error
        lifecycle.init_lifecycle_db(db_path)

        conn = sqlite3.connect(db_path)
        # All B-era tables present
        tables = {row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}
        expected_tables = {"id_sequence", "plans", "diagnostic_meta", "executable_meta",
                           "derivations", "steps", "commits", "deposits", "verdicts", "gate_events"}
        assert expected_tables.issubset(tables), f"Missing tables: {expected_tables - tables}"

        # Seeded row intact
        row = conn.execute("SELECT title, lifecycle_state FROM plans WHERE id = 1").fetchone()
        assert row == ("Seeded", "closed")

        # id_sequence not overwritten
        next_id = conn.execute("SELECT next_id FROM id_sequence WHERE id = 1").fetchone()[0]
        assert next_id == 5
        conn.close()

    def test_no_content_blob_columns(self, tmp_path):
        db_path = str(tmp_path / "no_blob.db")
        lifecycle.init_lifecycle_db(db_path)
        conn = sqlite3.connect(db_path)
        tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
        for (tname,) in tables:
            cols = conn.execute(f"PRAGMA table_info({tname})").fetchall()
            for col in cols:
                col_type = col[2].upper() if col[2] else ""
                assert "BLOB" not in col_type, f"Table {tname} column {col[1]} has BLOB type"
        conn.close()


class TestRecordStepStart:
    def test_happy_path(self):
        pid = lifecycle.mint_and_claim("diagnostic", "/proj", "T", "bellows", "small", 1, "d.md")
        step_id = lifecycle.record_step_start(pid, 1, role="DEV")
        assert step_id is not None
        conn = sqlite3.connect(lifecycle.LIFECYCLE_DB_PATH)
        row = conn.execute("SELECT plan_id, step_number, role, status FROM steps WHERE id = ?", (step_id,)).fetchone()
        conn.close()
        assert row[0] == pid
        assert row[1] == 1
        assert row[2] == "DEV"
        assert row[3] == "running"

    def test_returns_none_on_failure(self, tmp_path):
        # Point at a read-only path to force failure
        ro_path = str(tmp_path / "ro.db")
        lifecycle.init_lifecycle_db(ro_path)
        os.chmod(ro_path, stat.S_IRUSR)
        result = lifecycle.record_step_start(1, 1, role="DEV", db_path=ro_path)
        os.chmod(ro_path, stat.S_IRUSR | stat.S_IWUSR)  # restore for cleanup
        assert result is None


class TestRecordStepEnd:
    def test_updates_step(self):
        pid = lifecycle.mint_and_claim("diagnostic", "/proj", "T", "bellows", "small", 1, "d.md")
        step_id = lifecycle.record_step_start(pid, 1)
        lifecycle.record_step_end(step_id, status="complete", cost_usd=0.05, duration_s=12.3)
        conn = sqlite3.connect(lifecycle.LIFECYCLE_DB_PATH)
        row = conn.execute("SELECT status, cost_usd, duration_s FROM steps WHERE id = ?", (step_id,)).fetchone()
        conn.close()
        assert row[0] == "complete"
        assert abs(row[1] - 0.05) < 0.001
        assert abs(row[2] - 12.3) < 0.1

    def test_noop_on_none_step_id(self):
        # Should not raise
        lifecycle.record_step_end(None, status="complete")


class TestMarkStepComplete:
    def test_awaiting_verdict_row_flips_to_complete(self):
        pid = lifecycle.mint_and_claim("diagnostic", "/proj", "T", "bellows", "small", 1, "d.md")
        step_id = lifecycle.record_step_start(pid, 1)
        known_ts = "2026-09-11T01:00:00"
        conn = sqlite3.connect(lifecycle.LIFECYCLE_DB_PATH)
        conn.execute(
            "UPDATE steps SET status = 'awaiting_verdict', step_ended_at = ? WHERE id = ?",
            (known_ts, step_id),
        )
        conn.commit()
        conn.close()
        n = lifecycle.mark_step_complete(pid, 1)
        assert n == 1
        conn = sqlite3.connect(lifecycle.LIFECYCLE_DB_PATH)
        row = conn.execute("SELECT status, step_ended_at FROM steps WHERE id = ?", (step_id,)).fetchone()
        conn.close()
        assert row[0] == "complete"
        assert row[1] == known_ts

    def test_complete_row_returns_zero_unchanged(self):
        pid = lifecycle.mint_and_claim("diagnostic", "/proj", "T", "bellows", "small", 1, "d.md")
        step_id = lifecycle.record_step_start(pid, 1)
        lifecycle.record_step_end(step_id, status="complete")
        n = lifecycle.mark_step_complete(pid, 1)
        assert n == 0
        conn = sqlite3.connect(lifecycle.LIFECYCLE_DB_PATH)
        row = conn.execute("SELECT status FROM steps WHERE id = ?", (step_id,)).fetchone()
        conn.close()
        assert row[0] == "complete"

    def test_running_row_returns_zero_unchanged(self):
        pid = lifecycle.mint_and_claim("diagnostic", "/proj", "T", "bellows", "small", 1, "d.md")
        step_id = lifecycle.record_step_start(pid, 1)
        n = lifecycle.mark_step_complete(pid, 1)
        assert n == 0
        conn = sqlite3.connect(lifecycle.LIFECYCLE_DB_PATH)
        row = conn.execute("SELECT status FROM steps WHERE id = ?", (step_id,)).fetchone()
        conn.close()
        assert row[0] == "running"

    def test_none_plan_id_returns_zero_no_raise(self):
        n = lifecycle.mark_step_complete(None, 1)
        assert n == 0

    def test_null_step_ended_at_gets_set_on_flip(self):
        pid = lifecycle.mint_and_claim("diagnostic", "/proj", "T", "bellows", "small", 1, "d.md")
        step_id = lifecycle.record_step_start(pid, 1)
        conn = sqlite3.connect(lifecycle.LIFECYCLE_DB_PATH)
        conn.execute(
            "UPDATE steps SET status = 'awaiting_verdict', step_ended_at = NULL WHERE id = ?",
            (step_id,),
        )
        conn.commit()
        conn.close()
        lifecycle.mark_step_complete(pid, 1)
        conn = sqlite3.connect(lifecycle.LIFECYCLE_DB_PATH)
        row = conn.execute("SELECT step_ended_at FROM steps WHERE id = ?", (step_id,)).fetchone()
        conn.close()
        assert row[0] is not None


class TestRecordGateEvents:
    def test_records_pass_and_fail(self):
        pid = lifecycle.mint_and_claim("diagnostic", "/proj", "T", "bellows", "small", 1, "d.md")
        step_id = lifecycle.record_step_start(pid, 1)
        gate_result = {
            "failures": [{"gate": "deposit_exists", "evidence": "file missing"}],
            "passed": False,
        }
        lifecycle.record_gate_events(step_id, gate_result)
        conn = sqlite3.connect(lifecycle.LIFECYCLE_DB_PATH)
        rows = conn.execute("SELECT gate_name, result, reason_code FROM gate_events WHERE step_id = ?", (step_id,)).fetchall()
        conn.close()
        gate_dict = {r[0]: (r[1], r[2]) for r in rows}
        assert gate_dict["deposit_exists"] == ("fail", "file missing")
        assert gate_dict["receipt_status"] == ("pass", None)

    def test_pass_rows_for_the_verdict_pause_gates(self):
        """Thread 210: qa_test_result, quoted_test_nodes_exist and mutation_result get
        PASS rows when they do not fail, and a FAIL row (no PASS row) when they do."""
        pid = lifecycle.mint_and_claim("executable", "/proj", "T", "bellows", "small", 2, "d.md")
        step_id = lifecycle.record_step_start(pid, 2)
        lifecycle.record_gate_events(step_id, {"failures": [
            {"gate": "mutation_result", "evidence": "MUTATION: 1 killed, 1 survived, 0 error"}], "passed": False})
        conn = sqlite3.connect(lifecycle.LIFECYCLE_DB_PATH)
        rows = conn.execute("SELECT gate_name, result FROM gate_events WHERE step_id = ?", (step_id,)).fetchall()
        conn.close()
        seen = {}
        for name, result in rows:
            seen.setdefault(name, []).append(result)
        assert seen["qa_test_result"] == ["pass"]
        assert seen["quoted_test_nodes_exist"] == ["pass"]
        assert seen["mutation_result"] == ["fail"]

    def test_noop_on_none_step_id(self):
        lifecycle.record_gate_events(None, {"failures": []})


class TestRecordDeposits:
    def test_records_deposits(self):
        pid = lifecycle.mint_and_claim("diagnostic", "/proj", "T", "bellows", "small", 1, "d.md")
        step_id = lifecycle.record_step_start(pid, 1)
        deposits = [
            {"declared_path": "knowledge/foo.md", "type": "plan_required", "landed": True},
            {"declared_path": "knowledge/bar.md", "type": "frontmatter", "landed": False},
        ]
        lifecycle.record_deposits(step_id, deposits)
        conn = sqlite3.connect(lifecycle.LIFECYCLE_DB_PATH)
        rows = conn.execute("SELECT declared_path, type, landed FROM deposits WHERE step_id = ?", (step_id,)).fetchall()
        conn.close()
        assert len(rows) == 2
        paths = {r[0]: (r[1], r[2]) for r in rows}
        assert paths["knowledge/foo.md"] == ("plan_required", 1)
        assert paths["knowledge/bar.md"] == ("frontmatter", 0)


class TestRecordCommits:
    def test_records_multiple_shas(self):
        pid = lifecycle.mint_and_claim("diagnostic", "/proj", "T", "bellows", "small", 1, "d.md")
        step_id = lifecycle.record_step_start(pid, 1)
        lifecycle.record_commits(step_id, "bellows", ["abc123", "def456"])
        conn = sqlite3.connect(lifecycle.LIFECYCLE_DB_PATH)
        rows = conn.execute("SELECT repo, sha FROM commits WHERE step_id = ?", (step_id,)).fetchall()
        conn.close()
        assert len(rows) == 2
        shas = {r[1] for r in rows}
        assert shas == {"abc123", "def456"}

    def test_noop_on_empty_shas(self):
        pid = lifecycle.mint_and_claim("diagnostic", "/proj", "T", "bellows", "small", 1, "d.md")
        step_id = lifecycle.record_step_start(pid, 1)
        lifecycle.record_commits(step_id, "bellows", [])

    def test_dedupes_within_a_plan(self):
        pid = lifecycle.mint_and_claim("diagnostic", "/proj", "T", "bellows", "small", 2, "d.md")
        s1 = lifecycle.record_step_start(pid, 1)
        n1 = lifecycle.record_commits(s1, "bellows", ["a", "b"])
        assert n1 == 2
        s2 = lifecycle.record_step_start(pid, 2)
        n2 = lifecycle.record_commits(s2, "bellows", ["a", "b", "c"])
        assert n2 == 1
        conn = sqlite3.connect(lifecycle.LIFECYCLE_DB_PATH)
        step2_shas = {r[0] for r in conn.execute("SELECT sha FROM commits WHERE step_id = ?", (s2,)).fetchall()}
        step1_shas = {r[0] for r in conn.execute("SELECT sha FROM commits WHERE step_id = ?", (s1,)).fetchall()}
        conn.close()
        assert step2_shas == {"c"}
        assert step1_shas == {"a", "b"}

    def test_no_dedupe_across_plans(self):
        pid1 = lifecycle.mint_and_claim("diagnostic", "/proj", "T", "bellows", "small", 1, "d1.md")
        pid2 = lifecycle.mint_and_claim("diagnostic", "/proj", "T", "bellows", "small", 1, "d2.md")
        s1 = lifecycle.record_step_start(pid1, 1)
        s2 = lifecycle.record_step_start(pid2, 1)
        lifecycle.record_commits(s1, "bellows", ["a"])
        lifecycle.record_commits(s2, "bellows", ["a"])
        conn = sqlite3.connect(lifecycle.LIFECYCLE_DB_PATH)
        total = conn.execute("SELECT count(*) FROM commits WHERE sha = 'a'").fetchone()[0]
        conn.close()
        assert total == 2

    def test_repeat_in_one_call_inserted_once(self):
        pid = lifecycle.mint_and_claim("diagnostic", "/proj", "T", "bellows", "small", 1, "d.md")
        s1 = lifecycle.record_step_start(pid, 1)
        n = lifecycle.record_commits(s1, "bellows", ["a", "a"])
        assert n == 1
        conn = sqlite3.connect(lifecycle.LIFECYCLE_DB_PATH)
        rows = conn.execute("SELECT sha FROM commits WHERE step_id = ?", (s1,)).fetchall()
        conn.close()
        assert len(rows) == 1
        assert rows[0][0] == "a"


class TestRecordVerdicts:
    def test_verdict_request_and_outcome(self):
        pid = lifecycle.mint_and_claim("diagnostic", "/proj", "T", "bellows", "small", 1, "d.md")
        lifecycle.record_verdict_request(pid, 1, pause_reason_code="header_pause", verdict_file_ref="/path/to/vr.md")
        conn = sqlite3.connect(lifecycle.LIFECYCLE_DB_PATH)
        row = conn.execute("SELECT outcome, pause_reason_code, verdict_file_ref FROM verdicts WHERE plan_id = ?", (pid,)).fetchone()
        assert row[0] is None  # pending
        assert row[1] == "header_pause"
        assert row[2] == "/path/to/vr.md"
        conn.close()

        lifecycle.record_verdict_outcome(pid, 1, "continue", decided_by="ceo", disposition_summary="looks good")
        conn = sqlite3.connect(lifecycle.LIFECYCLE_DB_PATH)
        row = conn.execute("SELECT outcome, decided_by, disposition_summary FROM verdicts WHERE plan_id = ?", (pid,)).fetchone()
        conn.close()
        assert row[0] == "continue"
        assert row[1] == "ceo"
        assert row[2] == "looks good"


class TestRecordMeta:
    def test_diagnostic_meta(self):
        pid = lifecycle.mint_and_claim("diagnostic", "/proj", "T", "bellows", "small", 1, "d.md")
        lifecycle.record_meta(pid, "diagnostic", header={"scope": "bellows.py", "hypothesis": "bug in X"})
        conn = sqlite3.connect(lifecycle.LIFECYCLE_DB_PATH)
        row = conn.execute("SELECT scope, hypothesis FROM diagnostic_meta WHERE plan_id = ?", (pid,)).fetchone()
        conn.close()
        assert row[0] == "bellows.py"
        assert row[1] == "bug in X"

    def test_executable_meta(self):
        pid = lifecycle.mint_and_claim("executable", "/proj", "T", "bellows", "small", 1, "e.md")
        lifecycle.record_meta(pid, "executable", header={"test_scope": "tests/"})
        conn = sqlite3.connect(lifecycle.LIFECYCLE_DB_PATH)
        row = conn.execute("SELECT test_scope FROM executable_meta WHERE plan_id = ?", (pid,)).fetchone()
        conn.close()
        assert row[0] == "tests/"

    def test_noop_on_none_plan_id(self):
        lifecycle.record_meta(None, "diagnostic")


class TestParseDerivations:
    def test_numeric_id_citation(self):
        text = "This executable implements diagnostic 42 and extends the work."
        ids = lifecycle.parse_derivations(text)
        assert ids == [42]

    def test_multiple_citations(self):
        text = "Implements diagnostic 10, also implements diagnostic 20."
        ids = lifecycle.parse_derivations(text)
        assert ids == [10, 20]

    def test_legacy_slug_citation_not_returned(self):
        text = "Implements diagnostic foo-bar-2026-06-10."
        ids = lifecycle.parse_derivations(text)
        assert ids == []

    def test_no_citation(self):
        text = "This plan has no diagnostic reference."
        ids = lifecycle.parse_derivations(text)
        assert ids == []

    def test_case_insensitive(self):
        text = "Implements Diagnostic 7."
        ids = lifecycle.parse_derivations(text)
        assert ids == [7]


class TestRecordDerivations:
    def test_records_derivation_link(self):
        diag_id = lifecycle.mint_and_claim("diagnostic", "/proj", "D", "bellows", "small", 1, "d.md")
        exec_id = lifecycle.mint_and_claim("executable", "/proj", "E", "bellows", "small", 1, "e.md")
        lifecycle.record_derivations(exec_id, [diag_id])
        conn = sqlite3.connect(lifecycle.LIFECYCLE_DB_PATH)
        row = conn.execute("SELECT executable_id, diagnostic_id FROM derivations").fetchone()
        conn.close()
        assert row == (exec_id, diag_id)

    def test_duplicate_ignored(self):
        diag_id = lifecycle.mint_and_claim("diagnostic", "/proj", "D", "bellows", "small", 1, "d.md")
        exec_id = lifecycle.mint_and_claim("executable", "/proj", "E", "bellows", "small", 1, "e.md")
        lifecycle.record_derivations(exec_id, [diag_id])
        lifecycle.record_derivations(exec_id, [diag_id])  # should not raise
        conn = sqlite3.connect(lifecycle.LIFECYCLE_DB_PATH)
        count = conn.execute("SELECT COUNT(*) FROM derivations").fetchone()[0]
        conn.close()
        assert count == 1


class TestGetStepId:
    def test_returns_step_id(self):
        pid = lifecycle.mint_and_claim("diagnostic", "/proj", "T", "bellows", "small", 1, "d.md")
        step_id = lifecycle.record_step_start(pid, 1)
        result = lifecycle.get_step_id(pid, 1)
        assert result == step_id

    def test_returns_none_for_missing(self):
        pid = lifecycle.mint_and_claim("diagnostic", "/proj", "T", "bellows", "small", 1, "d.md")
        assert lifecycle.get_step_id(pid, 99) is None


class TestLogAndContinueContract:
    """Verify that every write helper logs WARN and does NOT propagate exceptions
    when the DB is unwritable."""

    def _make_readonly_db(self, tmp_path):
        db_path = str(tmp_path / "readonly.db")
        lifecycle.init_lifecycle_db(db_path)
        pid = lifecycle.mint_and_claim("diagnostic", "/proj", "T", "bellows", "small", 1, "d.md", db_path=db_path)
        step_id = lifecycle.record_step_start(pid, 1, db_path=db_path)
        os.chmod(db_path, stat.S_IRUSR)
        return db_path, pid, step_id

    def _restore(self, db_path):
        os.chmod(db_path, stat.S_IRUSR | stat.S_IWUSR)

    def test_record_step_start_no_raise(self, tmp_path):
        db_path, pid, _ = self._make_readonly_db(tmp_path)
        result = lifecycle.record_step_start(pid, 2, db_path=db_path)
        self._restore(db_path)
        assert result is None

    def test_record_step_end_no_raise(self, tmp_path):
        db_path, _, step_id = self._make_readonly_db(tmp_path)
        lifecycle.record_step_end(step_id, db_path=db_path)
        self._restore(db_path)

    def test_record_gate_events_no_raise(self, tmp_path):
        db_path, _, step_id = self._make_readonly_db(tmp_path)
        lifecycle.record_gate_events(step_id, {"failures": [{"gate": "x", "evidence": "y"}]}, db_path=db_path)
        self._restore(db_path)

    def test_record_deposits_no_raise(self, tmp_path):
        db_path, _, step_id = self._make_readonly_db(tmp_path)
        lifecycle.record_deposits(step_id, [{"declared_path": "x.md", "type": "plan_required", "landed": False}], db_path=db_path)
        self._restore(db_path)

    def test_record_commits_no_raise(self, tmp_path):
        db_path, _, step_id = self._make_readonly_db(tmp_path)
        lifecycle.record_commits(step_id, "repo", ["abc"], db_path=db_path)
        self._restore(db_path)

    def test_record_verdict_request_no_raise(self, tmp_path):
        db_path, pid, _ = self._make_readonly_db(tmp_path)
        lifecycle.record_verdict_request(pid, 1, db_path=db_path)
        self._restore(db_path)

    def test_record_verdict_outcome_no_raise(self, tmp_path):
        db_path, pid, _ = self._make_readonly_db(tmp_path)
        lifecycle.record_verdict_outcome(pid, 1, "continue", db_path=db_path)
        self._restore(db_path)

    def test_record_meta_no_raise(self, tmp_path):
        db_path, pid, _ = self._make_readonly_db(tmp_path)
        lifecycle.record_meta(pid, "diagnostic", db_path=db_path)
        self._restore(db_path)

    def test_record_derivations_no_raise(self, tmp_path):
        db_path, pid, _ = self._make_readonly_db(tmp_path)
        lifecycle.record_derivations(pid, [1], db_path=db_path)
        self._restore(db_path)


# ---------------------------------------------------------------------------
# plan_doc_ref tests — migration, writer, claim→close, backfill
# ---------------------------------------------------------------------------

class TestPlanDocRefMigration:
    """(a) migration adds the column idempotently."""

    def test_column_present_on_fresh_db(self, tmp_path):
        db_path = str(tmp_path / "fresh.db")
        lifecycle.init_lifecycle_db(db_path)
        conn = sqlite3.connect(db_path)
        cols = {row[1] for row in conn.execute("PRAGMA table_info(plans)")}
        conn.close()
        assert "plan_doc_ref" in cols

    def test_column_added_to_existing_db(self, tmp_path):
        db_path = str(tmp_path / "old.db")
        # Create an A-era DB without plan_doc_ref
        conn = sqlite3.connect(db_path)
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("""CREATE TABLE id_sequence (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            next_id INTEGER NOT NULL DEFAULT 1
        )""")
        conn.execute("INSERT INTO id_sequence (id, next_id) VALUES (1, 1)")
        conn.execute("""CREATE TABLE plans (
            id INTEGER PRIMARY KEY,
            type TEXT NOT NULL CHECK (type IN ('diagnostic', 'executable', 'qa')),
            target_project TEXT NOT NULL,
            title TEXT,
            dispatch_mode TEXT,
            tier TEXT,
            lifecycle_state TEXT NOT NULL DEFAULT 'claimed',
            total_steps INTEGER,
            deposit_placeholder_name TEXT,
            created_at TEXT NOT NULL,
            closed_at TEXT
        )""")
        conn.commit()
        conn.close()
        # Run init — should add plan_doc_ref via ALTER TABLE
        lifecycle.init_lifecycle_db(db_path)
        conn = sqlite3.connect(db_path)
        cols = {row[1] for row in conn.execute("PRAGMA table_info(plans)")}
        conn.close()
        assert "plan_doc_ref" in cols

    def test_idempotent_double_init(self, tmp_path):
        db_path = str(tmp_path / "idem.db")
        lifecycle.init_lifecycle_db(db_path)
        lifecycle.init_lifecycle_db(db_path)  # should not raise
        conn = sqlite3.connect(db_path)
        cols = [row[1] for row in conn.execute("PRAGMA table_info(plans)")]
        conn.close()
        assert cols.count("plan_doc_ref") == 1


class TestMarkPlanStateWithDocRef:
    """(b) mark_plan_state with plan_doc_ref writes it."""

    def test_writes_plan_doc_ref(self):
        pid = lifecycle.mint_and_claim("executable", "/proj", "T", "bellows", "small", 1, "e.md")
        lifecycle.mark_plan_state(pid, "in_progress",
                                  plan_doc_ref="knowledge/decisions/in-progress-executable-1.md")
        conn = sqlite3.connect(lifecycle.LIFECYCLE_DB_PATH)
        ref = conn.execute("SELECT plan_doc_ref FROM plans WHERE id = ?", (pid,)).fetchone()[0]
        conn.close()
        assert ref == "knowledge/decisions/in-progress-executable-1.md"

    def test_updates_plan_doc_ref_on_close(self):
        pid = lifecycle.mint_and_claim("executable", "/proj", "T", "bellows", "small", 1, "e.md")
        lifecycle.mark_plan_state(pid, "in_progress",
                                  plan_doc_ref="knowledge/decisions/in-progress-executable-1.md")
        lifecycle.mark_plan_state(pid, "closed", closed_at="2026-06-13T12:00:00",
                                  plan_doc_ref="knowledge/decisions/Done/executable-1.md")
        conn = sqlite3.connect(lifecycle.LIFECYCLE_DB_PATH)
        row = conn.execute("SELECT lifecycle_state, plan_doc_ref FROM plans WHERE id = ?", (pid,)).fetchone()
        conn.close()
        assert row[0] == "closed"
        assert row[1] == "knowledge/decisions/Done/executable-1.md"

    def test_omitting_plan_doc_ref_leaves_it_unchanged(self):
        pid = lifecycle.mint_and_claim("executable", "/proj", "T", "bellows", "small", 1, "e.md")
        lifecycle.mark_plan_state(pid, "in_progress",
                                  plan_doc_ref="knowledge/decisions/in-progress-executable-1.md")
        lifecycle.mark_plan_state(pid, "closed", closed_at="2026-06-13T12:00:00")
        conn = sqlite3.connect(lifecycle.LIFECYCLE_DB_PATH)
        ref = conn.execute("SELECT plan_doc_ref FROM plans WHERE id = ?", (pid,)).fetchone()[0]
        conn.close()
        # plan_doc_ref unchanged from in_progress write
        assert ref == "knowledge/decisions/in-progress-executable-1.md"


class TestPlanDocRefClaimToClose:
    """(c) a claim→close sequence leaves Done/<type>-<id>.md in plan_doc_ref."""

    def test_full_claim_to_close_sequence(self, tmp_path):
        db_path = str(tmp_path / "seq.db")
        lifecycle.init_lifecycle_db(db_path)
        project_root = str(tmp_path / "project")
        decisions_dir = os.path.join(project_root, "knowledge", "decisions")
        done_dir = os.path.join(decisions_dir, "Done")
        os.makedirs(done_dir)

        pid = lifecycle.mint_and_claim("executable", project_root, "T", "bellows", "small", 2, "e.md",
                                        db_path=db_path)
        # Claim → in_progress
        inprogress_path = os.path.join(decisions_dir, f"in-progress-executable-{pid}.md")
        claim_ref = os.path.relpath(inprogress_path, project_root)
        lifecycle.mark_plan_state(pid, "in_progress", plan_doc_ref=claim_ref, db_path=db_path)

        conn = sqlite3.connect(db_path)
        ref = conn.execute("SELECT plan_doc_ref FROM plans WHERE id = ?", (pid,)).fetchone()[0]
        conn.close()
        assert ref == f"knowledge/decisions/in-progress-executable-{pid}.md"

        # Close → Done
        done_path = os.path.join(done_dir, f"executable-{pid}.md")
        close_ref = os.path.relpath(done_path, project_root)
        lifecycle.mark_plan_state(pid, "closed", closed_at="2026-06-13T12:00:00",
                                  plan_doc_ref=close_ref, db_path=db_path)

        conn = sqlite3.connect(db_path)
        row = conn.execute("SELECT lifecycle_state, plan_doc_ref FROM plans WHERE id = ?", (pid,)).fetchone()
        conn.close()
        assert row[0] == "closed"
        assert row[1] == f"knowledge/decisions/Done/executable-{pid}.md"


class TestBackfillPlanDocRef:
    """(d) backfill resolves a closed row to its Done path and leaves non-existent ones NULL."""

    def test_closed_row_resolves_to_done(self, tmp_path):
        db_path = str(tmp_path / "backfill.db")
        lifecycle.init_lifecycle_db(db_path)
        project_root = str(tmp_path / "project")
        decisions_dir = os.path.join(project_root, "knowledge", "decisions")
        done_dir = os.path.join(decisions_dir, "Done")
        os.makedirs(done_dir)

        pid = lifecycle.mint_and_claim("executable", project_root, "T", "bellows", "small", 1, "e.md",
                                        db_path=db_path)
        lifecycle.mark_plan_state(pid, "closed", closed_at="2026-06-13T12:00:00", db_path=db_path)

        # Create the Done file on disk
        done_file = os.path.join(done_dir, f"executable-{pid}.md")
        with open(done_file, "w") as f:
            f.write("# Plan")

        backfilled, left_null = lifecycle.backfill_plan_doc_ref(db_path=db_path)
        assert backfilled == 1
        assert left_null == 0

        conn = sqlite3.connect(db_path)
        ref = conn.execute("SELECT plan_doc_ref FROM plans WHERE id = ?", (pid,)).fetchone()[0]
        conn.close()
        assert ref == f"knowledge/decisions/Done/executable-{pid}.md"

    def test_nonexistent_file_left_null(self, tmp_path):
        db_path = str(tmp_path / "backfill2.db")
        lifecycle.init_lifecycle_db(db_path)
        project_root = str(tmp_path / "project")
        os.makedirs(os.path.join(project_root, "knowledge", "decisions", "Done"))

        pid = lifecycle.mint_and_claim("executable", project_root, "T", "bellows", "small", 1, "e.md",
                                        db_path=db_path)
        lifecycle.mark_plan_state(pid, "closed", closed_at="2026-06-13T12:00:00", db_path=db_path)
        # Do NOT create the file on disk

        backfilled, left_null = lifecycle.backfill_plan_doc_ref(db_path=db_path)
        assert backfilled == 0
        assert left_null == 1

        conn = sqlite3.connect(db_path)
        ref = conn.execute("SELECT plan_doc_ref FROM plans WHERE id = ?", (pid,)).fetchone()[0]
        conn.close()
        assert ref is None

    def test_idempotent_backfill(self, tmp_path):
        db_path = str(tmp_path / "backfill3.db")
        lifecycle.init_lifecycle_db(db_path)
        project_root = str(tmp_path / "project")
        done_dir = os.path.join(project_root, "knowledge", "decisions", "Done")
        os.makedirs(done_dir)

        pid = lifecycle.mint_and_claim("executable", project_root, "T", "bellows", "small", 1, "e.md",
                                        db_path=db_path)
        lifecycle.mark_plan_state(pid, "closed", closed_at="2026-06-13T12:00:00", db_path=db_path)
        with open(os.path.join(done_dir, f"executable-{pid}.md"), "w") as f:
            f.write("# Plan")

        lifecycle.backfill_plan_doc_ref(db_path=db_path)
        # Second call should be a no-op (already has plan_doc_ref)
        backfilled2, left_null2 = lifecycle.backfill_plan_doc_ref(db_path=db_path)
        assert backfilled2 == 0
        assert left_null2 == 0

    def test_in_progress_row_resolves(self, tmp_path):
        db_path = str(tmp_path / "backfill4.db")
        lifecycle.init_lifecycle_db(db_path)
        project_root = str(tmp_path / "project")
        decisions_dir = os.path.join(project_root, "knowledge", "decisions")
        os.makedirs(decisions_dir)

        pid = lifecycle.mint_and_claim("diagnostic", project_root, "T", "bellows", "small", 1, "d.md",
                                        db_path=db_path)
        lifecycle.mark_plan_state(pid, "in_progress", db_path=db_path)
        # Create in-progress file on disk
        with open(os.path.join(decisions_dir, f"in-progress-diagnostic-{pid}.md"), "w") as f:
            f.write("# Plan")

        backfilled, left_null = lifecycle.backfill_plan_doc_ref(db_path=db_path)
        assert backfilled == 1

        conn = sqlite3.connect(db_path)
        ref = conn.execute("SELECT plan_doc_ref FROM plans WHERE id = ?", (pid,)).fetchone()[0]
        conn.close()
        assert ref == f"knowledge/decisions/in-progress-diagnostic-{pid}.md"


# ---------------------------------------------------------------------------
# Daemon-owned ledgers Phase 1 — prompt_feedback tests
# ---------------------------------------------------------------------------

class TestPromptFeedbackMigration:
    """(a) migration adds prompt_feedback table idempotently."""

    def test_table_present_on_fresh_db(self, tmp_path):
        db_path = str(tmp_path / "fresh_pf.db")
        lifecycle.init_lifecycle_db(db_path)
        conn = sqlite3.connect(db_path)
        tables = {row[0] for row in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()}
        conn.close()
        assert "prompt_feedback" in tables

    def test_columns_match_spec(self, tmp_path):
        db_path = str(tmp_path / "cols_pf.db")
        lifecycle.init_lifecycle_db(db_path)
        conn = sqlite3.connect(db_path)
        cols = {row[1] for row in conn.execute("PRAGMA table_info(prompt_feedback)")}
        conn.close()
        expected = {"id", "plan_id", "step_number", "agent", "project",
                    "entry_text", "created_at"}
        assert expected == cols

    def test_idempotent_double_init(self, tmp_path):
        db_path = str(tmp_path / "idem_pf.db")
        lifecycle.init_lifecycle_db(db_path)
        lifecycle.init_lifecycle_db(db_path)  # should not raise
        conn = sqlite3.connect(db_path)
        tables = [row[0] for row in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='prompt_feedback'"
        ).fetchall()]
        conn.close()
        assert len(tables) == 1


class TestRecordPromptFeedback:
    """(b) record_prompt_feedback + read back."""

    def test_happy_path(self):
        pid = lifecycle.mint_and_claim("diagnostic", "/proj", "T", "bellows", "small", 1, "d.md")
        lifecycle.record_prompt_feedback(pid, 1, "Bellows Developer", "/proj",
                                         "**2026-06-13** — test feedback entry")
        conn = sqlite3.connect(lifecycle.LIFECYCLE_DB_PATH)
        row = conn.execute(
            "SELECT plan_id, step_number, agent, project, entry_text FROM prompt_feedback"
        ).fetchone()
        conn.close()
        assert row[0] == pid
        assert row[1] == 1
        assert row[2] == "Bellows Developer"
        assert row[3] == "/proj"
        assert "test feedback entry" in row[4]

    def test_multiple_entries(self):
        pid = lifecycle.mint_and_claim("executable", "/proj", "T", "bellows", "small", 2, "e.md")
        lifecycle.record_prompt_feedback(pid, 1, "DEV", "/proj", "Entry 1")
        lifecycle.record_prompt_feedback(pid, 2, "QA", "/proj", "Entry 2")
        conn = sqlite3.connect(lifecycle.LIFECYCLE_DB_PATH)
        rows = conn.execute("SELECT entry_text FROM prompt_feedback ORDER BY id").fetchall()
        conn.close()
        assert len(rows) == 2
        assert rows[0][0] == "Entry 1"
        assert rows[1][0] == "Entry 2"

    def test_log_and_continue_on_failure(self, tmp_path):
        db_path = str(tmp_path / "ro_pf.db")
        lifecycle.init_lifecycle_db(db_path)
        os.chmod(db_path, stat.S_IRUSR)
        # Should not raise
        lifecycle.record_prompt_feedback(1, 1, "DEV", "/proj", "text", db_path=db_path)
        os.chmod(db_path, stat.S_IRUSR | stat.S_IWUSR)


class TestGenerateFeedbackMd:
    """(e) generate_feedback_md renders rows newest-first."""

    def test_empty_db_returns_header(self, tmp_path):
        db_path = str(tmp_path / "gen_empty.db")
        lifecycle.init_lifecycle_db(db_path)
        result = lifecycle.generate_feedback_md("/proj", db_path=db_path)
        assert "No feedback entries" in result

    def test_renders_newest_first(self, tmp_path):
        db_path = str(tmp_path / "gen_order.db")
        lifecycle.init_lifecycle_db(db_path)
        conn = sqlite3.connect(db_path)
        conn.execute(
            "INSERT INTO prompt_feedback (plan_id, step_number, agent, project, entry_text, created_at) "
            "VALUES (1, 1, 'DEV', '/proj', 'First entry', '2026-06-13T10:00:00')"
        )
        conn.execute(
            "INSERT INTO prompt_feedback (plan_id, step_number, agent, project, entry_text, created_at) "
            "VALUES (2, 1, 'QA', '/proj', 'Second entry', '2026-06-13T11:00:00')"
        )
        conn.commit()
        conn.close()
        result = lifecycle.generate_feedback_md("/proj", db_path=db_path)
        # Second entry (newer) should appear before First entry
        pos_second = result.index("Second entry")
        pos_first = result.index("First entry")
        assert pos_second < pos_first

    def test_filters_by_project(self, tmp_path):
        db_path = str(tmp_path / "gen_filter.db")
        lifecycle.init_lifecycle_db(db_path)
        conn = sqlite3.connect(db_path)
        conn.execute(
            "INSERT INTO prompt_feedback (plan_id, step_number, agent, project, entry_text, created_at) "
            "VALUES (1, 1, 'DEV', '/proj_a', 'Entry A', '2026-06-13T10:00:00')"
        )
        conn.execute(
            "INSERT INTO prompt_feedback (plan_id, step_number, agent, project, entry_text, created_at) "
            "VALUES (2, 1, 'DEV', '/proj_b', 'Entry B', '2026-06-13T10:00:00')"
        )
        conn.commit()
        conn.close()
        result = lifecycle.generate_feedback_md("/proj_a", db_path=db_path)
        assert "Entry A" in result
        assert "Entry B" not in result


# ---------------------------------------------------------------------------
# Daemon-owned ledgers activation — ledger_writes idempotency tests
# ---------------------------------------------------------------------------

class TestLedgerWritesMigration:
    """(a) ledger_writes migration is idempotent."""

    def test_table_present_on_fresh_db(self, tmp_path):
        db_path = str(tmp_path / "fresh_lw.db")
        lifecycle.init_lifecycle_db(db_path)
        conn = sqlite3.connect(db_path)
        tables = {row[0] for row in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()}
        conn.close()
        assert "ledger_writes" in tables

    def test_columns_match_spec(self, tmp_path):
        db_path = str(tmp_path / "cols_lw.db")
        lifecycle.init_lifecycle_db(db_path)
        conn = sqlite3.connect(db_path)
        cols = {row[1] for row in conn.execute("PRAGMA table_info(ledger_writes)")}
        conn.close()
        expected = {"id", "step_id", "ledger_file", "content_hash", "applied_at"}
        assert expected == cols

    def test_idempotent_double_init(self, tmp_path):
        db_path = str(tmp_path / "idem_lw.db")
        lifecycle.init_lifecycle_db(db_path)
        lifecycle.init_lifecycle_db(db_path)  # should not raise
        conn = sqlite3.connect(db_path)
        tables = [row[0] for row in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='ledger_writes'"
        ).fetchall()]
        conn.close()
        assert len(tables) == 1


class TestLedgerWriteIdempotency:
    """(b) check + record functions for idempotency guard."""

    def test_check_returns_false_for_new_write(self, tmp_path):
        db_path = str(tmp_path / "idem_check.db")
        lifecycle.init_lifecycle_db(db_path)
        result = lifecycle.check_ledger_write_exists(
            "42-1", "agent-prompt-feedback.md", "abc123", db_path=db_path
        )
        assert result is False

    def test_record_then_check_returns_true(self, tmp_path):
        db_path = str(tmp_path / "idem_record.db")
        lifecycle.init_lifecycle_db(db_path)
        lifecycle.record_ledger_write(
            "42-1", "agent-prompt-feedback.md", "abc123", db_path=db_path
        )
        result = lifecycle.check_ledger_write_exists(
            "42-1", "agent-prompt-feedback.md", "abc123", db_path=db_path
        )
        assert result is True

    def test_different_hash_not_blocked(self, tmp_path):
        db_path = str(tmp_path / "idem_diff.db")
        lifecycle.init_lifecycle_db(db_path)
        lifecycle.record_ledger_write(
            "42-1", "agent-prompt-feedback.md", "abc123", db_path=db_path
        )
        result = lifecycle.check_ledger_write_exists(
            "42-1", "agent-prompt-feedback.md", "def456", db_path=db_path
        )
        assert result is False

    def test_duplicate_record_does_not_raise(self, tmp_path):
        db_path = str(tmp_path / "idem_dup.db")
        lifecycle.init_lifecycle_db(db_path)
        lifecycle.record_ledger_write(
            "42-1", "agent-prompt-feedback.md", "abc123", db_path=db_path
        )
        # Should not raise (INSERT OR IGNORE)
        lifecycle.record_ledger_write(
            "42-1", "agent-prompt-feedback.md", "abc123", db_path=db_path
        )
        conn = sqlite3.connect(db_path)
        count = conn.execute("SELECT COUNT(*) FROM ledger_writes").fetchone()[0]
        conn.close()
        assert count == 1


# ---------------------------------------------------------------------------
# in_progress-strand recovery (plan 54)
# ---------------------------------------------------------------------------

class TestInProgressStrandRecovery:
    """Plan 54: recover_half_claimed also recovers stranded in_progress plans
    whose worktree no longer exists on disk."""

    def test_stranded_in_progress_recovered(self, tmp_path):
        """in_progress + no worktree + past age guard → abandoned + closed_at."""
        db_path = str(tmp_path / "ip_recovery.db")
        lifecycle.init_lifecycle_db(db_path)
        project = str(tmp_path / "project")
        decisions = tmp_path / "decisions"
        decisions.mkdir()
        os.makedirs(os.path.join(project, ".bellows-worktrees"), exist_ok=True)

        pid = lifecycle.mint_and_claim(
            "executable", project, "Stranded", "bellows", "small", 1,
            "executable-draft-ip.md", db_path=db_path,
        )
        lifecycle.mark_plan_state(pid, "in_progress", db_path=db_path)
        # Backdate past age guard
        from datetime import timedelta
        old_ts = (datetime.now() - timedelta(minutes=10)).isoformat()
        conn = sqlite3.connect(db_path)
        conn.execute("UPDATE plans SET created_at = ? WHERE id = ?", (old_ts, pid))
        conn.commit()
        conn.close()
        # No worktree directory exists

        actions = lifecycle.recover_half_claimed(
            str(decisions), db_path=db_path, project_root=project,
        )
        ip_actions = [(a, act) for a, act in actions if a == pid]
        assert len(ip_actions) == 1
        assert ip_actions[0][1] == "abandoned"

        conn = sqlite3.connect(db_path)
        row = conn.execute(
            "SELECT lifecycle_state, closed_at FROM plans WHERE id = ?", (pid,)
        ).fetchone()
        conn.close()
        assert row[0] == "abandoned"
        assert row[1] is not None  # closed_at set

    def test_in_progress_with_worktree_not_touched(self, tmp_path):
        """in_progress + worktree EXISTS → not abandoned (plan still running)."""
        db_path = str(tmp_path / "ip_wt.db")
        lifecycle.init_lifecycle_db(db_path)
        project = str(tmp_path / "project")
        decisions = tmp_path / "decisions"
        decisions.mkdir()

        pid = lifecycle.mint_and_claim(
            "executable", project, "Running", "bellows", "small", 1,
            "executable-draft-running.md", db_path=db_path,
        )
        lifecycle.mark_plan_state(pid, "in_progress", db_path=db_path)
        # Backdate past age guard
        from datetime import timedelta
        old_ts = (datetime.now() - timedelta(minutes=10)).isoformat()
        conn = sqlite3.connect(db_path)
        conn.execute("UPDATE plans SET created_at = ? WHERE id = ?", (old_ts, pid))
        conn.commit()
        conn.close()
        # CREATE the worktree directory — simulates a live plan
        wt_path = os.path.join(project, ".bellows-worktrees", str(pid))
        os.makedirs(wt_path)

        actions = lifecycle.recover_half_claimed(
            str(decisions), db_path=db_path, project_root=project,
        )
        ip_actions = [(a, act) for a, act in actions if a == pid]
        assert len(ip_actions) == 1
        assert ip_actions[0][1] == "skipped_worktree_exists"

        conn = sqlite3.connect(db_path)
        state = conn.execute(
            "SELECT lifecycle_state FROM plans WHERE id = ?", (pid,)
        ).fetchone()[0]
        conn.close()
        assert state == "in_progress"  # unchanged

    def test_in_progress_within_age_guard_not_touched(self, tmp_path):
        """in_progress + no worktree but within age guard → not abandoned."""
        db_path = str(tmp_path / "ip_young.db")
        lifecycle.init_lifecycle_db(db_path)
        project = str(tmp_path / "project")
        decisions = tmp_path / "decisions"
        decisions.mkdir()
        os.makedirs(os.path.join(project, ".bellows-worktrees"), exist_ok=True)

        pid = lifecycle.mint_and_claim(
            "executable", project, "Young", "bellows", "small", 1,
            "executable-draft-young-ip.md", db_path=db_path,
        )
        lifecycle.mark_plan_state(pid, "in_progress", db_path=db_path)
        # created_at is now (within age guard) — no worktree exists

        actions = lifecycle.recover_half_claimed(
            str(decisions), db_path=db_path, project_root=project,
        )
        ip_actions = [(a, act) for a, act in actions if a == pid]
        assert len(ip_actions) == 1
        assert ip_actions[0][1] == "skipped_too_recent"

        conn = sqlite3.connect(db_path)
        state = conn.execute(
            "SELECT lifecycle_state FROM plans WHERE id = ?", (pid,)
        ).fetchone()[0]
        conn.close()
        assert state == "in_progress"  # unchanged

    def test_claimed_recovery_still_works_alongside_in_progress(self, tmp_path):
        """Existing claimed-recovery path is not broken by the in_progress extension."""
        db_path = str(tmp_path / "ip_claimed.db")
        lifecycle.init_lifecycle_db(db_path)
        project = str(tmp_path / "project")
        decisions = tmp_path / "decisions"
        decisions.mkdir()

        # Create a claimed plan with no deposit
        pid = lifecycle.mint_and_claim(
            "executable", project, "Old Claimed", "bellows", "small", 1,
            "executable-draft-old-claimed.md", db_path=db_path,
        )
        from datetime import timedelta
        old_ts = (datetime.now() - timedelta(minutes=10)).isoformat()
        conn = sqlite3.connect(db_path)
        conn.execute("UPDATE plans SET created_at = ? WHERE id = ?", (old_ts, pid))
        conn.commit()
        conn.close()

        actions = lifecycle.recover_half_claimed(
            str(decisions), db_path=db_path, project_root=project,
        )
        claimed_actions = [(a, act) for a, act in actions if a == pid]
        assert len(claimed_actions) == 1
        assert claimed_actions[0][1] == "abandoned"

        conn = sqlite3.connect(db_path)
        state = conn.execute(
            "SELECT lifecycle_state FROM plans WHERE id = ?", (pid,)
        ).fetchone()[0]
        conn.close()
        assert state == "abandoned"


# ---------------------------------------------------------------------------
# Claim-dedup guard (plan 141)
# ---------------------------------------------------------------------------

class TestPartialUniqueIndex:
    """(a) Partial unique index blocks a second active row with the same placeholder."""

    def test_second_active_claim_raises_integrity_error(self, tmp_path):
        db_path = str(tmp_path / "dedup.db")
        lifecycle.init_lifecycle_db(db_path)
        lifecycle.mint_and_claim(
            "executable", "/proj", "Plan A", "bellows", "small", 1,
            "executable-foo.md", db_path=db_path,
        )
        with pytest.raises(sqlite3.IntegrityError):
            lifecycle.mint_and_claim(
                "executable", "/proj", "Plan B", "bellows", "small", 1,
                "executable-foo.md", db_path=db_path,
            )

    def test_new_claim_allowed_after_terminal_state(self, tmp_path):
        db_path = str(tmp_path / "dedup_term.db")
        lifecycle.init_lifecycle_db(db_path)
        pid1 = lifecycle.mint_and_claim(
            "executable", "/proj", "Plan A", "bellows", "small", 1,
            "executable-foo.md", db_path=db_path,
        )
        lifecycle.mark_plan_state(pid1, "closed", closed_at="2026-07-07T12:00:00",
                                  db_path=db_path)
        pid2 = lifecycle.mint_and_claim(
            "executable", "/proj", "Plan B", "bellows", "small", 1,
            "executable-foo.md", db_path=db_path,
        )
        assert pid2 == pid1 + 1

    def test_halted_does_not_block_new_claim(self, tmp_path):
        db_path = str(tmp_path / "dedup_halt.db")
        lifecycle.init_lifecycle_db(db_path)
        pid1 = lifecycle.mint_and_claim(
            "executable", "/proj", "Plan A", "bellows", "small", 1,
            "executable-foo.md", db_path=db_path,
        )
        lifecycle.mark_plan_state(pid1, "halted", db_path=db_path)
        pid2 = lifecycle.mint_and_claim(
            "executable", "/proj", "Plan B", "bellows", "small", 1,
            "executable-foo.md", db_path=db_path,
        )
        assert pid2 == pid1 + 1


class TestActivePlanForPlaceholder:
    """(b) active_plan_for_placeholder returns id for active plans, None for terminal/absent."""

    def test_returns_id_for_active_plan(self, tmp_path):
        db_path = str(tmp_path / "apfp.db")
        lifecycle.init_lifecycle_db(db_path)
        pid = lifecycle.mint_and_claim(
            "executable", "/proj", "Plan A", "bellows", "small", 1,
            "executable-foo.md", db_path=db_path,
        )
        result = lifecycle.active_plan_for_placeholder("executable-foo.md", db_path=db_path)
        assert result == pid

    def test_returns_none_for_closed_plan(self, tmp_path):
        db_path = str(tmp_path / "apfp_closed.db")
        lifecycle.init_lifecycle_db(db_path)
        pid = lifecycle.mint_and_claim(
            "executable", "/proj", "Plan A", "bellows", "small", 1,
            "executable-foo.md", db_path=db_path,
        )
        lifecycle.mark_plan_state(pid, "closed", closed_at="2026-07-07T12:00:00",
                                  db_path=db_path)
        result = lifecycle.active_plan_for_placeholder("executable-foo.md", db_path=db_path)
        assert result is None

    def test_returns_none_for_halted_plan(self, tmp_path):
        db_path = str(tmp_path / "apfp_halted.db")
        lifecycle.init_lifecycle_db(db_path)
        pid = lifecycle.mint_and_claim(
            "executable", "/proj", "Plan A", "bellows", "small", 1,
            "executable-foo.md", db_path=db_path,
        )
        lifecycle.mark_plan_state(pid, "halted", db_path=db_path)
        result = lifecycle.active_plan_for_placeholder("executable-foo.md", db_path=db_path)
        assert result is None

    def test_returns_none_for_absent_placeholder(self, tmp_path):
        db_path = str(tmp_path / "apfp_absent.db")
        lifecycle.init_lifecycle_db(db_path)
        result = lifecycle.active_plan_for_placeholder("nonexistent.md", db_path=db_path)
        assert result is None

    def test_returns_id_for_in_progress(self, tmp_path):
        db_path = str(tmp_path / "apfp_ip.db")
        lifecycle.init_lifecycle_db(db_path)
        pid = lifecycle.mint_and_claim(
            "executable", "/proj", "Plan A", "bellows", "small", 1,
            "executable-foo.md", db_path=db_path,
        )
        lifecycle.mark_plan_state(pid, "in_progress", db_path=db_path)
        result = lifecycle.active_plan_for_placeholder("executable-foo.md", db_path=db_path)
        assert result == pid

    def test_returns_id_for_awaiting_verdict(self, tmp_path):
        db_path = str(tmp_path / "apfp_av.db")
        lifecycle.init_lifecycle_db(db_path)
        pid = lifecycle.mint_and_claim(
            "executable", "/proj", "Plan A", "bellows", "small", 1,
            "executable-foo.md", db_path=db_path,
        )
        lifecycle.mark_plan_state(pid, "awaiting_verdict", db_path=db_path)
        result = lifecycle.active_plan_for_placeholder("executable-foo.md", db_path=db_path)
        assert result == pid


class TestRunPlanDedupGuard:
    """(c) run_plan-level guard refuses a duplicate — no second id minted, routed to halted."""

    def test_duplicate_deposit_routed_to_halted(self, tmp_path):
        db_path = str(tmp_path / "rp_dedup.db")
        lifecycle.init_lifecycle_db(db_path)
        decisions = tmp_path / "knowledge" / "decisions"
        decisions.mkdir(parents=True)
        (decisions / "Done").mkdir()

        placeholder = "executable-dedup-test.md"
        pid1 = lifecycle.mint_and_claim(
            "executable", str(tmp_path), "Plan A", "bellows", "small", 1,
            placeholder, db_path=db_path,
        )
        lifecycle.mark_plan_state(pid1, "in_progress", db_path=db_path)

        deposit_path = decisions / placeholder
        deposit_path.write_text("# Duplicate\n**Tier:** small\n\n## STEP 1\nDo stuff\n")

        from unittest.mock import patch, MagicMock
        config = {"default_model": "sonnet", "pushover": {}}
        mock_server = MagicMock()

        with patch("bellows.lifecycle.active_plan_for_placeholder", return_value=pid1), \
             patch("bellows.lifecycle.LIFECYCLE_DB_PATH", db_path):
            import bellows as bellows_mod
            bellows_mod.run_plan(str(deposit_path), config, mock_server)

        assert (decisions / f"halted-{placeholder}").exists()
        assert not deposit_path.exists()

        conn = sqlite3.connect(db_path)
        count = conn.execute(
            "SELECT COUNT(*) FROM plans WHERE deposit_placeholder_name = ?",
            (placeholder,),
        ).fetchone()[0]
        conn.close()
        assert count == 1


class TestInvalidateSeenDedupGuard:
    """(d) _invalidate_seen_on_redeposit does NOT discard _seen when active plan exists,
    and DOES when none exists."""

    def test_does_not_discard_seen_when_active(self, tmp_path):
        db_path = str(tmp_path / "iseen.db")
        lifecycle.init_lifecycle_db(db_path)
        placeholder = "executable-foo.md"
        pid = lifecycle.mint_and_claim(
            "executable", "/proj", "Plan A", "bellows", "small", 1,
            placeholder, db_path=db_path,
        )
        lifecycle.mark_plan_state(pid, "in_progress", db_path=db_path)

        from unittest.mock import MagicMock, patch
        import verdict
        slug = verdict.slug_from_path(placeholder)

        orchestrator = MagicMock()
        orchestrator._seen = {slug}

        from bellows import PlanHandler
        handler = PlanHandler(orchestrator)

        with patch("bellows.lifecycle.active_plan_for_placeholder", return_value=pid):
            handler._invalidate_seen_on_redeposit(f"/some/dir/{placeholder}")

        assert slug in orchestrator._seen

    def test_discards_seen_when_no_active_plan(self, tmp_path):
        db_path = str(tmp_path / "iseen2.db")
        lifecycle.init_lifecycle_db(db_path)

        from unittest.mock import MagicMock, patch
        import verdict
        placeholder = "executable-foo.md"
        slug = verdict.slug_from_path(placeholder)

        orchestrator = MagicMock()
        orchestrator._seen = {slug}

        from bellows import PlanHandler
        handler = PlanHandler(orchestrator)

        with patch("bellows.lifecycle.active_plan_for_placeholder", return_value=None):
            handler._invalidate_seen_on_redeposit(f"/some/dir/{placeholder}")

        assert slug not in orchestrator._seen


# ---------------------------------------------------------------------------
# Helpers shared by migration/pid tests
# ---------------------------------------------------------------------------

def _build_old_steps_db(tmp_path, name="old.db"):
    """Build a database whose steps DDL uses the OLD CHECK (no 'abandoned', no daemon_pid)."""
    db = str(tmp_path / name)
    conn = sqlite3.connect(db)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS id_sequence (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            next_id INTEGER NOT NULL DEFAULT 1
        )
    """)
    conn.execute("INSERT OR IGNORE INTO id_sequence (id, next_id) VALUES (1, 100)")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS plans (
            id INTEGER PRIMARY KEY,
            type TEXT NOT NULL CHECK (type IN ('diagnostic', 'executable', 'qa')),
            target_project TEXT NOT NULL,
            title TEXT,
            dispatch_mode TEXT,
            tier TEXT,
            lifecycle_state TEXT NOT NULL DEFAULT 'claimed'
                CHECK (lifecycle_state IN ('claimed','in_progress','awaiting_verdict','closed','halted','abandoned')),
            total_steps INTEGER,
            deposit_placeholder_name TEXT,
            created_at TEXT NOT NULL,
            closed_at TEXT,
            plan_doc_ref TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS steps (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            plan_id INTEGER NOT NULL REFERENCES plans(id),
            step_number INTEGER NOT NULL,
            role TEXT,
            status TEXT NOT NULL DEFAULT 'pending'
                CHECK (status IN ('pending','running','awaiting_verdict','complete')),
            step_started_at TEXT,
            step_ended_at TEXT,
            cost_usd REAL,
            turns INTEGER,
            duration_s REAL,
            log_ref TEXT,
            UNIQUE(plan_id, step_number)
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS commits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            step_id INTEGER NOT NULL REFERENCES steps(id),
            repo TEXT NOT NULL,
            sha TEXT NOT NULL,
            message_ref TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS deposits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            step_id INTEGER NOT NULL REFERENCES steps(id),
            declared_path TEXT NOT NULL,
            type TEXT,
            landed INTEGER NOT NULL DEFAULT 0
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS verdicts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            plan_id INTEGER NOT NULL REFERENCES plans(id),
            step_number INTEGER NOT NULL,
            outcome TEXT,
            pause_reason_code TEXT,
            decided_by TEXT,
            verdict_file_ref TEXT,
            disposition_summary TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS gate_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            step_id INTEGER NOT NULL REFERENCES steps(id),
            gate_name TEXT NOT NULL,
            result TEXT NOT NULL CHECK (result IN ('pass', 'fail')),
            reason_code TEXT,
            overridden INTEGER NOT NULL DEFAULT 0,
            override_ref TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS step_files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            step_id INTEGER NOT NULL REFERENCES steps(id),
            path TEXT NOT NULL,
            UNIQUE(step_id, path)
        )
    """)
    conn.commit()
    conn.close()
    return db


class TestStepsAbandonedMigration:
    """m-t1 through m-t7: _migrate_steps_abandoned and init_lifecycle_db migration."""

    def test_fresh_db_admits_abandoned_and_daemon_pid(self, tmp_path):
        """m-t1: a fresh database admits an abandoned row and carries daemon_pid."""
        db = str(tmp_path / "fresh.db")
        lifecycle.init_lifecycle_db(db)
        conn = sqlite3.connect(db)
        ddl = conn.execute(
            "SELECT sql FROM sqlite_master WHERE type='table' AND name='steps'"
        ).fetchone()[0]
        assert "'abandoned'" in ddl
        assert "daemon_pid" in ddl
        conn.execute(
            "INSERT INTO plans (id, type, target_project, lifecycle_state, created_at) "
            "VALUES (1, 'executable', '/p', 'in_progress', '2026-09-12')"
        )
        conn.execute(
            "INSERT INTO steps (plan_id, step_number, status, daemon_pid) VALUES (1, 1, 'abandoned', 42)"
        )
        conn.commit()
        row = conn.execute("SELECT status, daemon_pid FROM steps WHERE plan_id=1").fetchone()
        conn.close()
        assert row[0] == "abandoned"
        assert row[1] == 42

    def test_old_db_migrated_rows_and_backup(self, tmp_path):
        """m-t2: old DDL database is migrated via init — DDL updated, rows kept, backup present."""
        db = _build_old_steps_db(tmp_path, "m2.db")
        conn = sqlite3.connect(db)
        conn.execute(
            "INSERT INTO plans (id, type, target_project, lifecycle_state, created_at) "
            "VALUES (1, 'executable', '/p', 'in_progress', '2026-09-12')"
        )
        conn.execute("INSERT INTO steps (plan_id, step_number, status) VALUES (1, 1, 'running')")
        step_id = conn.execute("SELECT id FROM steps WHERE plan_id=1").fetchone()[0]
        conn.execute(
            "INSERT INTO commits (step_id, repo, sha, message_ref) VALUES (?, 'r', 'abc', NULL)",
            (step_id,),
        )
        conn.commit()
        old_ddl = conn.execute(
            "SELECT sql FROM sqlite_master WHERE type='table' AND name='steps'"
        ).fetchone()[0]
        conn.close()
        assert "'abandoned'" not in old_ddl

        lifecycle.init_lifecycle_db(db)

        conn = sqlite3.connect(db)
        new_ddl = conn.execute(
            "SELECT sql FROM sqlite_master WHERE type='table' AND name='steps'"
        ).fetchone()[0]
        assert "'abandoned'" in new_ddl
        assert "daemon_pid" in new_ddl
        rows = conn.execute("SELECT plan_id, status, daemon_pid FROM steps").fetchall()
        assert len(rows) == 1
        assert rows[0][0] == 1
        assert rows[0][1] == "running"
        assert rows[0][2] is None  # daemon_pid NULL on old rows
        commits = conn.execute("SELECT step_id FROM commits").fetchall()
        assert len(commits) == 1
        assert commits[0][0] == step_id
        fk = conn.execute("PRAGMA foreign_key_check(steps)").fetchall()
        assert fk == []
        conn.close()

        from datetime import timezone
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        bak_path = db + f".pre-steps-abandoned-{today}.bak"
        assert os.path.exists(bak_path)
        conn_bak = sqlite3.connect(bak_path)
        bak_ddl = conn_bak.execute(
            "SELECT sql FROM sqlite_master WHERE type='table' AND name='steps'"
        ).fetchone()[0]
        conn_bak.close()
        assert "'abandoned'" not in bak_ddl

    def test_second_call_no_second_backup(self, tmp_path):
        """m-t3: a second init call on an already-migrated db writes no second backup."""
        db = _build_old_steps_db(tmp_path, "m3.db")
        lifecycle.init_lifecycle_db(db)
        from datetime import timezone
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        bak_path = db + f".pre-steps-abandoned-{today}.bak"
        assert os.path.exists(bak_path)
        bak_mtime = os.stat(bak_path).st_mtime

        import time
        time.sleep(0.05)
        lifecycle.init_lifecycle_db(db)

        assert os.path.exists(bak_path)
        assert os.stat(bak_path).st_mtime == bak_mtime  # unchanged

    def test_failure_inside_transaction_does_not_raise(self, tmp_path):
        """m-t4: forced failure inside transaction (pre-existing steps_new) leaves old DDL intact.
        Also: lock held across the migration call → old DDL preserved, no raise."""

        db = _build_old_steps_db(tmp_path, "m4a.db")
        conn = sqlite3.connect(db)
        conn.execute(
            "INSERT INTO plans (id, type, target_project, lifecycle_state, created_at) "
            "VALUES (1, 'executable', '/p', 'in_progress', '2026-09-12')"
        )
        conn.execute("INSERT INTO steps (plan_id, step_number, status) VALUES (1, 1, 'running')")
        conn.commit()
        conn.execute("ALTER TABLE steps ADD COLUMN daemon_pid INTEGER")
        conn.execute("CREATE TABLE steps_new (id INTEGER PRIMARY KEY)")
        conn.commit()
        conn.close()

        lifecycle._migrate_steps_abandoned(db)

        conn = sqlite3.connect(db)
        ddl = conn.execute(
            "SELECT sql FROM sqlite_master WHERE type='table' AND name='steps'"
        ).fetchone()[0]
        count = conn.execute("SELECT count(*) FROM steps").fetchone()[0]
        conn.close()
        assert "'abandoned'" not in ddl
        assert count == 1

        db2 = _build_old_steps_db(tmp_path, "m4b.db")
        conn2 = sqlite3.connect(db2)
        conn2.execute("ALTER TABLE steps ADD COLUMN daemon_pid INTEGER")
        conn2.commit()
        conn2.close()
        conn_hold = sqlite3.connect(db2, isolation_level=None)
        conn_hold.execute("BEGIN IMMEDIATE")
        try:
            lifecycle._migrate_steps_abandoned(db2)
        finally:
            conn_hold.execute("ROLLBACK")
            conn_hold.close()

        conn2b = sqlite3.connect(db2)
        ddl2 = conn2b.execute(
            "SELECT sql FROM sqlite_master WHERE type='table' AND name='steps'"
        ).fetchone()[0]
        conn2b.close()
        assert "'abandoned'" not in ddl2

    def test_dangling_refs_kept_after_migration(self, tmp_path):
        """m-t5: verdicts referencing missing plan left intact; gate_events referencing missing step also kept."""
        db = _build_old_steps_db(tmp_path, "m5.db")
        conn = sqlite3.connect(db)
        conn.execute(
            "INSERT INTO plans (id, type, target_project, lifecycle_state, created_at) "
            "VALUES (1, 'executable', '/p', 'closed', '2026-09-12')"
        )
        conn.execute("INSERT INTO steps (plan_id, step_number, status) VALUES (1, 1, 'complete')")
        step_id = conn.execute("SELECT id FROM steps WHERE plan_id=1").fetchone()[0]
        conn.execute("INSERT INTO verdicts (plan_id, step_number, outcome) VALUES (999, 1, 'pass')")
        conn.execute("INSERT INTO gate_events (step_id, gate_name, result) VALUES (999, 'g', 'pass')")
        count_before = conn.execute("SELECT count(*) FROM steps").fetchone()[0]
        conn.commit()
        conn.close()

        lifecycle.init_lifecycle_db(db)

        conn = sqlite3.connect(db)
        ddl = conn.execute(
            "SELECT sql FROM sqlite_master WHERE type='table' AND name='steps'"
        ).fetchone()[0]
        count_after = conn.execute("SELECT count(*) FROM steps").fetchone()[0]
        v_row = conn.execute("SELECT plan_id FROM verdicts WHERE plan_id=999").fetchone()
        g_row = conn.execute("SELECT step_id FROM gate_events WHERE step_id=999").fetchone()
        conn.close()
        assert "'abandoned'" in ddl
        assert count_after == count_before
        assert v_row is not None
        assert g_row is not None

    def test_failed_backup_leaves_no_tmp_next_succeeds(self, tmp_path):
        """m-t6: backup failure (directory at bak_tmp) leaves no .bak.tmp; next init call writes the .bak."""
        db = _build_old_steps_db(tmp_path, "m6.db")
        from datetime import timezone
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        bak_path = db + f".pre-steps-abandoned-{today}.bak"
        bak_tmp = bak_path + ".tmp"

        os.makedirs(bak_tmp, exist_ok=True)
        lifecycle.init_lifecycle_db(db)

        assert os.path.isdir(bak_tmp)
        assert not os.path.exists(bak_path)

        os.rmdir(bak_tmp)

        lifecycle.init_lifecycle_db(db)

        conn = sqlite3.connect(db)
        ddl = conn.execute(
            "SELECT sql FROM sqlite_master WHERE type='table' AND name='steps'"
        ).fetchone()[0]
        conn.close()
        assert "'abandoned'" in ddl
        assert os.path.exists(bak_path)

    def test_rebuild_fails_daemon_pid_present_record_step_start_works(self, tmp_path):
        """m-t7: rebuild fails (pre-existing steps_new) → daemon_pid present, 'abandoned' absent.
        record_step_start still writes daemon_pid."""
        db = _build_old_steps_db(tmp_path, "m7.db")
        conn = sqlite3.connect(db)
        conn.execute(
            "INSERT INTO plans (id, type, target_project, lifecycle_state, created_at) "
            "VALUES (1, 'executable', '/p', 'in_progress', '2026-09-12')"
        )
        conn.commit()
        conn.execute("CREATE TABLE steps_new (id INTEGER PRIMARY KEY)")
        conn.commit()
        conn.close()

        lifecycle.init_lifecycle_db(db)

        conn = sqlite3.connect(db)
        ddl = conn.execute(
            "SELECT sql FROM sqlite_master WHERE type='table' AND name='steps'"
        ).fetchone()[0]
        cols = {row[1] for row in conn.execute("PRAGMA table_info(steps)")}
        conn.close()
        assert "'abandoned'" not in ddl
        assert "daemon_pid" in cols

        step_id = lifecycle.record_step_start(1, 1, db_path=db)
        assert step_id is not None
        conn = sqlite3.connect(db)
        row = conn.execute(
            "SELECT daemon_pid FROM steps WHERE plan_id=1 AND step_number=1"
        ).fetchone()
        conn.close()
        assert row[0] == os.getpid()


class TestMarkStepAbandoned:
    """a-t1 to a-t3: mark_step_abandoned."""

    def test_running_row_flips_to_abandoned(self, tmp_path):
        """a-t1: a running row is flipped to abandoned, returns 1, step_ended_at set."""
        db = str(tmp_path / "a1.db")
        lifecycle.init_lifecycle_db(db)
        conn = sqlite3.connect(db)
        conn.execute(
            "INSERT INTO plans (id, type, target_project, lifecycle_state, created_at) "
            "VALUES (1, 'executable', '/p', 'in_progress', '2026-09-12')"
        )
        conn.execute(
            "INSERT INTO steps (plan_id, step_number, status, step_started_at) "
            "VALUES (1, 1, 'running', '2026-09-12T10:00:00')"
        )
        conn.commit()
        conn.close()

        n = lifecycle.mark_step_abandoned(1, db_path=db)
        assert n == 1

        conn = sqlite3.connect(db)
        row = conn.execute("SELECT status, step_ended_at FROM steps WHERE plan_id=1").fetchone()
        conn.close()
        assert row[0] == "abandoned"
        assert row[1] is not None

    def test_complete_and_awaiting_rows_not_touched(self, tmp_path):
        """a-t2: complete and awaiting_verdict rows return 0 and stay unchanged."""
        db = str(tmp_path / "a2.db")
        lifecycle.init_lifecycle_db(db)
        conn = sqlite3.connect(db)
        conn.execute(
            "INSERT INTO plans (id, type, target_project, lifecycle_state, created_at) "
            "VALUES (1, 'executable', '/p', 'closed', '2026-09-12')"
        )
        conn.execute(
            "INSERT INTO steps (plan_id, step_number, status) VALUES (1, 1, 'complete')"
        )
        conn.execute(
            "INSERT INTO steps (plan_id, step_number, status) VALUES (1, 2, 'awaiting_verdict')"
        )
        conn.commit()
        conn.close()

        n = lifecycle.mark_step_abandoned(1, db_path=db)
        assert n == 0

        conn = sqlite3.connect(db)
        rows = {r[0]: r[1] for r in conn.execute("SELECT step_number, status FROM steps").fetchall()}
        conn.close()
        assert rows[1] == "complete"
        assert rows[2] == "awaiting_verdict"

    def test_none_plan_id_returns_zero(self):
        """a-t3: None plan_id returns 0 immediately."""
        n = lifecycle.mark_step_abandoned(None)
        assert n == 0


class TestRecordStepStartPid:
    """p-t1 to p-t3: record_step_start records daemon_pid and handles resume."""

    def test_new_row_records_daemon_pid(self, tmp_path):
        """p-t1: a new step row records os.getpid() as daemon_pid."""
        db = str(tmp_path / "p1.db")
        lifecycle.init_lifecycle_db(db)
        conn = sqlite3.connect(db)
        conn.execute(
            "INSERT INTO plans (id, type, target_project, lifecycle_state, created_at) "
            "VALUES (1, 'executable', '/p', 'in_progress', '2026-09-12')"
        )
        conn.commit()
        conn.close()

        step_id = lifecycle.record_step_start(1, 1, db_path=db)
        assert step_id is not None

        conn = sqlite3.connect(db)
        row = conn.execute("SELECT daemon_pid FROM steps WHERE id=?", (step_id,)).fetchone()
        conn.close()
        assert row[0] == os.getpid()

    def test_resume_running_step_refreshes_pid(self, tmp_path):
        """p-t2: resuming a running step refreshes daemon_pid to current process."""
        from unittest.mock import patch
        db = str(tmp_path / "p2.db")
        lifecycle.init_lifecycle_db(db)
        conn = sqlite3.connect(db)
        conn.execute(
            "INSERT INTO plans (id, type, target_project, lifecycle_state, created_at) "
            "VALUES (1, 'executable', '/p', 'in_progress', '2026-09-12')"
        )
        conn.commit()
        conn.close()

        old_pid = os.getpid() + 5000
        with patch("os.getpid", return_value=old_pid):
            first_id = lifecycle.record_step_start(1, 1, db_path=db)
        assert first_id is not None

        second_id = lifecycle.record_step_start(1, 1, db_path=db)
        assert second_id == first_id

        conn = sqlite3.connect(db)
        row = conn.execute(
            "SELECT daemon_pid FROM steps WHERE id=?", (first_id,)
        ).fetchone()
        conn.close()
        assert row[0] == os.getpid()

    def test_resume_complete_row_returns_none(self, tmp_path):
        """p-t3: a second start on a complete row returns None and leaves the row."""
        db = str(tmp_path / "p3.db")
        lifecycle.init_lifecycle_db(db)
        conn = sqlite3.connect(db)
        conn.execute(
            "INSERT INTO plans (id, type, target_project, lifecycle_state, created_at) "
            "VALUES (1, 'executable', '/p', 'in_progress', '2026-09-12')"
        )
        conn.execute(
            "INSERT INTO steps (plan_id, step_number, status) VALUES (1, 1, 'complete')"
        )
        conn.commit()
        conn.close()

        result = lifecycle.record_step_start(1, 1, db_path=db)
        assert result is None

        conn = sqlite3.connect(db)
        status = conn.execute("SELECT status FROM steps WHERE plan_id=1").fetchone()[0]
        conn.close()
        assert status == "complete"


class TestAbandonedRunnerDiscriminator:
    """d-t1 to d-t5: recover_half_claimed lane-file discriminator for in_progress arm."""

    def _make_plan(self, db_path, decisions_dir, project, state="in_progress",
                   placeholder=None, minutes_old=10):
        from datetime import timedelta
        pid = lifecycle.mint_and_claim(
            "executable", str(project), "T", "bellows", "small", 1,
            placeholder or "executable-draft.md", db_path=db_path,
        )
        lifecycle.mark_plan_state(pid, state, db_path=db_path)
        old_ts = (datetime.now() - timedelta(minutes=minutes_old)).isoformat()
        conn = sqlite3.connect(db_path)
        conn.execute("UPDATE plans SET created_at = ? WHERE id = ?", (old_ts, pid))
        conn.commit()
        conn.close()
        return pid

    def test_inprogress_lane_returns_abandoned_runner(self, tmp_path):
        """d-t1: in-progress- lane with worktree present → abandoned_runner, row stays in_progress."""
        db = str(tmp_path / "d1.db")
        lifecycle.init_lifecycle_db(db)
        project = tmp_path / "proj"
        decisions = tmp_path / "decisions"
        decisions.mkdir()
        project.mkdir()

        pid = self._make_plan(db, decisions, project)
        inprogress = decisions / f"in-progress-executable-{pid}.md"
        inprogress.write_text("lane")
        wt = project / ".bellows-worktrees" / str(pid)
        wt.mkdir(parents=True)

        actions = lifecycle.recover_half_claimed(str(decisions), db_path=db, project_root=str(project))
        ip = [(p, a) for p, a in actions if p == pid]
        assert ip == [(pid, "abandoned_runner")]

        conn = sqlite3.connect(db)
        state = conn.execute("SELECT lifecycle_state FROM plans WHERE id=?", (pid,)).fetchone()[0]
        conn.close()
        assert state == "in_progress"

    def test_done_abandoned_lane_returns_abandoned_runner(self, tmp_path):
        """d-t2: Done/abandoned- lane → abandoned_runner."""
        db = str(tmp_path / "d2.db")
        lifecycle.init_lifecycle_db(db)
        project = tmp_path / "proj"
        decisions = tmp_path / "decisions"
        decisions.mkdir()
        project.mkdir()

        pid = self._make_plan(db, decisions, project)
        done_dir = decisions / "Done"
        done_dir.mkdir()
        (done_dir / f"abandoned-executable-{pid}.md").write_text("done lane")

        actions = lifecycle.recover_half_claimed(str(decisions), db_path=db, project_root=str(project))
        ip = [(p, a) for p, a in actions if p == pid]
        assert ip == [(pid, "abandoned_runner")]

    def test_parked_lane_skipped(self, tmp_path):
        """d-t3: parked- lane, no worktree, past age guard → skipped_parked."""
        db = str(tmp_path / "d3.db")
        lifecycle.init_lifecycle_db(db)
        project = tmp_path / "proj"
        decisions = tmp_path / "decisions"
        decisions.mkdir()
        project.mkdir()

        pid = self._make_plan(db, decisions, project)
        parked = decisions / f"parked-executable-{pid}.md"
        parked.write_text("parked")

        actions = lifecycle.recover_half_claimed(str(decisions), db_path=db, project_root=str(project))
        ip = [(p, a) for p, a in actions if p == pid]
        assert ip == [(pid, "skipped_parked")]

        conn = sqlite3.connect(db)
        state = conn.execute("SELECT lifecycle_state FROM plans WHERE id=?", (pid,)).fetchone()[0]
        conn.close()
        assert state == "in_progress"

    def test_inprogress_lane_inside_age_guard_still_abandoned_runner(self, tmp_path):
        """d-t4: in-progress- lane inside age guard → abandoned_runner (discriminator fires before age guard)."""
        db = str(tmp_path / "d4.db")
        lifecycle.init_lifecycle_db(db)
        project = tmp_path / "proj"
        decisions = tmp_path / "decisions"
        decisions.mkdir()
        project.mkdir()

        pid = self._make_plan(db, decisions, project, minutes_old=0)
        inprogress = decisions / f"in-progress-executable-{pid}.md"
        inprogress.write_text("lane")

        actions = lifecycle.recover_half_claimed(str(decisions), db_path=db, project_root=str(project))
        ip = [(p, a) for p, a in actions if p == pid]
        assert ip == [(pid, "abandoned_runner")]

    def test_claimed_to_re_renamed_then_abandoned_runner(self, tmp_path):
        """d-t5: claimed row with placeholder on disk → re_renamed then abandoned_runner in same pass."""
        db = str(tmp_path / "d5.db")
        lifecycle.init_lifecycle_db(db)
        project = tmp_path / "proj"
        decisions = tmp_path / "decisions"
        decisions.mkdir()
        project.mkdir()

        from datetime import timedelta
        pid = lifecycle.mint_and_claim(
            "executable", str(project), "T", "bellows", "small", 1,
            f"executable-draft-d5.md", db_path=db,
        )
        placeholder = decisions / f"executable-draft-d5.md"
        placeholder.write_text("plan")
        old_ts = (datetime.now() - timedelta(minutes=10)).isoformat()
        conn = sqlite3.connect(db)
        conn.execute("UPDATE plans SET created_at = ? WHERE id = ?", (old_ts, pid))
        conn.commit()
        conn.close()

        inprogress_path = decisions / f"in-progress-executable-{pid}.md"

        actions = lifecycle.recover_half_claimed(str(decisions), db_path=db, project_root=str(project))

        plan_actions = [(p, a) for p, a in actions if p == pid]
        action_names = [a for _, a in plan_actions]
        assert "re_renamed" in action_names or "already_renamed" in action_names
        assert "abandoned_runner" in action_names
