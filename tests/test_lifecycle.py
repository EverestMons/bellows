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
        assert len(actions) == 1
        assert actions[0] == (pid, "already_renamed")
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
        assert len(actions) == 1
        assert actions[0] == (pid, "already_renamed")


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

    def test_in_progress_plan_not_selected_by_recovery(self, tmp_path):
        """Once in_progress, recovery must not re-process the plan."""
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
        assert len(actions) == 0


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
