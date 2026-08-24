"""Tests for [2r/receipts] wrap-check step, _retire_receipts, and clear-tool release arm."""
import hashlib
import json
import os
import re
import shutil
import sqlite3
import subprocess
import sys
import textwrap
from datetime import datetime, timedelta
from pathlib import Path

import pytest

BELLOWS_ROOT = Path(__file__).resolve().parent.parent


def _init_lifecycle_db(db_path):
    conn = sqlite3.connect(str(db_path))
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS id_sequence (
            next_id INTEGER NOT NULL DEFAULT 500
        )
    """)
    conn.execute("INSERT OR IGNORE INTO id_sequence (next_id) VALUES (500)")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS plans (
            id INTEGER PRIMARY KEY,
            type TEXT NOT NULL DEFAULT 'executable',
            target_project TEXT NOT NULL DEFAULT '',
            title TEXT,
            dispatch_mode TEXT,
            tier TEXT,
            lifecycle_state TEXT NOT NULL DEFAULT 'claimed',
            total_steps INTEGER DEFAULT 1,
            deposit_placeholder_name TEXT,
            created_at TEXT NOT NULL DEFAULT ''
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS clearances (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            plan_path TEXT NOT NULL,
            content_hash TEXT NOT NULL,
            assigned_class TEXT NOT NULL,
            cleared_by TEXT NOT NULL CHECK (cleared_by IN ('depositor', 'clear_tool')),
            cleared_at TEXT NOT NULL,
            consumed_at TEXT
        )
    """)
    conn.commit()
    conn.close()


def _add_clearance(db_path, plan_path, content_hash, assigned_class="default",
                   cleared_by="depositor", cleared_at=None, consumed_at=None):
    conn = sqlite3.connect(str(db_path))
    if cleared_at is None:
        cleared_at = datetime.now().isoformat()
    conn.execute(
        "INSERT INTO clearances (plan_path, content_hash, assigned_class, cleared_by, cleared_at, consumed_at) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (plan_path, content_hash, assigned_class, cleared_by, cleared_at, consumed_at),
    )
    conn.commit()
    conn.close()


def _write_receipt(receipts_dir, slug, session_id, content_hash, armed_at=None,
                   extra_fields=None):
    receipts_dir.mkdir(parents=True, exist_ok=True)
    if armed_at is None:
        armed_at = datetime.now().isoformat()
    receipt = {
        "slug": slug,
        "content_hash": content_hash,
        "session_id": session_id,
        "armed_at": armed_at,
        "watcher": "gate-watcher armed in depositing session",
        "attestation_boundary": "This receipt proves the watcher was ARMED at write time.",
    }
    if extra_fields:
        receipt.update(extra_fields)
    hash12 = content_hash[:12]
    name = f"receipt-{slug}-{session_id}-{hash12}.json"
    path = receipts_dir / name
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    return path


# ---------------------------------------------------------------------------
# [2r/receipts] wrap-check step tests
# ---------------------------------------------------------------------------

class TestWrapCheckReceipts:
    @pytest.fixture(autouse=True)
    def _setup(self, tmp_path, monkeypatch):
        self.root = tmp_path / "root"
        self.root.mkdir()
        self.bellows = self.root / "bellows"
        self.bellows.mkdir()
        self.receipts = self.bellows / "receipts"
        self.db_path = self.bellows / "lifecycle.db"
        _init_lifecycle_db(self.db_path)

        monkeypatch.setenv("ELUVIAN_WRAP_ROOT", str(self.root))
        monkeypatch.setenv("ELUVIAN_WRAP_MEMORY", str(tmp_path / "memory"))
        (tmp_path / "memory").mkdir()

        import hooks.eluvian.wrap_check as wc
        monkeypatch.setattr(wc, "ROOT", self.root)
        monkeypatch.setattr(wc, "BELLOWS", self.bellows)
        monkeypatch.setattr(wc, "RECEIPTS", self.receipts)
        monkeypatch.setattr(wc, "LIFECYCLE_DB", self.db_path)
        monkeypatch.setattr(wc, "MEMORY", tmp_path / "memory")
        monkeypatch.setattr(wc, "BATON", self.root / "shop_next_session.md")
        self.wc = wc

    def test_pass_own_receipts_all_matched(self):
        content_hash = hashlib.sha256(b"plan bytes").hexdigest()
        _write_receipt(self.receipts, "my-plan", "session-A", content_hash)
        _add_clearance(self.db_path, "my-plan.md", content_hash)

        fails = self.wc.check(session_id="session-A")
        receipt_fails = [f for f in fails if "[2r/receipts]" in f]
        assert len(receipt_fails) == 0

    def test_blocking_arm_fires_on_matchless_own_receipt(self):
        old_time = (datetime.now() - timedelta(minutes=15)).isoformat()
        _write_receipt(self.receipts, "orphan-plan", "session-A",
                       hashlib.sha256(b"orphan").hexdigest(), armed_at=old_time)

        fails = self.wc.check(session_id="session-A")
        receipt_fails = [f for f in fails if "[2r/receipts]" in f]
        assert len(receipt_fails) == 1
        assert "match no clearance or hold" in receipt_fails[0]

    def test_pending_evaluation_grace(self, capsys):
        fresh_time = datetime.now().isoformat()
        _write_receipt(self.receipts, "fresh-plan", "session-A",
                       hashlib.sha256(b"fresh").hexdigest(), armed_at=fresh_time)

        fails = self.wc.check(session_id="session-A")
        receipt_fails = [f for f in fails if "[2r/receipts]" in f]
        assert len(receipt_fails) == 0
        captured = capsys.readouterr()
        assert "pending evaluation" in captured.out

    def test_warning_arm_on_receiptless_clearance(self, capsys):
        self.receipts.mkdir(parents=True, exist_ok=True)
        content_hash = hashlib.sha256(b"no receipt for this").hexdigest()
        _add_clearance(self.db_path, "some-plan.md", content_hash)

        fails = self.wc.check(session_id="session-A")
        receipt_fails = [f for f in fails if "[2r/receipts]" in f]
        assert len(receipt_fails) == 0

        captured = capsys.readouterr()
        assert "WARNING" in captured.out
        assert "without a receipt" in captured.out

    def test_skip_no_session_id(self, capsys):
        self.receipts.mkdir(parents=True, exist_ok=True)
        fails = self.wc.check(session_id=None)
        receipt_fails = [f for f in fails if "[2r/receipts]" in f]
        assert len(receipt_fails) == 0
        captured = capsys.readouterr()
        assert "SKIPPED" in captured.out and "blocking arm" in captured.out

    def test_skip_no_receipts_dir(self, capsys):
        fails = self.wc.check(session_id="session-A")
        receipt_fails = [f for f in fails if "[2r/receipts]" in f]
        assert len(receipt_fails) == 0
        captured = capsys.readouterr()
        assert "SKIPPED" in captured.out and "absent" in captured.out

    def test_skip_unreadable_db(self, capsys, monkeypatch):
        self.receipts.mkdir(parents=True, exist_ok=True)
        monkeypatch.setattr(self.wc, "LIFECYCLE_DB", self.bellows / "nonexistent.db")

        fails = self.wc.check(session_id="session-A")
        receipt_fails = [f for f in fails if "[2r/receipts]" in f]
        assert len(receipt_fails) == 0
        captured = capsys.readouterr()
        assert "lifecycle.db not readable" in captured.out

    def test_malformed_receipt_warning(self, capsys):
        self.receipts.mkdir(parents=True, exist_ok=True)
        bad = self.receipts / "receipt-bad-session-A-000000000000.json"
        bad.write_text("not valid json")

        fails = self.wc.check(session_id="session-A")
        receipt_fails = [f for f in fails if "[2r/receipts]" in f]
        assert len(receipt_fails) == 0
        captured = capsys.readouterr()
        assert "WARNING" in captured.out and "malformed" in captured.out

    def test_anti_foreign_block(self):
        old_time = (datetime.now() - timedelta(minutes=15)).isoformat()
        foreign_hash = hashlib.sha256(b"foreign plan").hexdigest()
        _write_receipt(self.receipts, "foreign-plan", "other-session",
                       foreign_hash, armed_at=old_time)

        fails = self.wc.check(session_id="session-A")
        receipt_fails = [f for f in fails if "[2r/receipts]" in f]
        assert len(receipt_fails) == 0

    def test_blast_radius_clearances_present_receipts_empty(self, capsys):
        self.receipts.mkdir(parents=True, exist_ok=True)
        content_hash = hashlib.sha256(b"existing deposit").hexdigest()
        _add_clearance(self.db_path, "old-plan.md", content_hash)

        fails = self.wc.check(session_id="session-A")
        receipt_fails = [f for f in fails if "[2r/receipts]" in f]
        assert len(receipt_fails) == 0

        captured = capsys.readouterr()
        assert "WARNING" in captured.out or "OK" in captured.out

    def test_hold_sidecar_match(self):
        content_hash = hashlib.sha256(b"held plan").hexdigest()
        _write_receipt(self.receipts, "my-held-plan", "session-A", content_hash)

        proj = self.root / "some-project" / "knowledge" / "decisions"
        proj.mkdir(parents=True)
        sidecar = proj / "hold-my-held-plan.hold.json"
        sidecar.write_text(json.dumps({"hold_reason": "class:shop-infra"}))

        fails = self.wc.check(session_id="session-A")
        receipt_fails = [f for f in fails if "[2r/receipts]" in f]
        assert len(receipt_fails) == 0

    def test_consumed_clearance_still_matches(self):
        content_hash = hashlib.sha256(b"claimed plan").hexdigest()
        _write_receipt(self.receipts, "claimed-plan", "session-A", content_hash)
        _add_clearance(self.db_path, "claimed-plan.md", content_hash,
                       consumed_at=datetime.now().isoformat())

        fails = self.wc.check(session_id="session-A")
        receipt_fails = [f for f in fails if "[2r/receipts]" in f]
        assert len(receipt_fails) == 0

    def test_warning_arm_checks_archived_receipts(self, capsys):
        content_hash = hashlib.sha256(b"archived deposit").hexdigest()
        _add_clearance(self.db_path, "archived-plan.md", content_hash)
        archived = self.receipts / "archived"
        archived.mkdir(parents=True)
        _write_receipt(archived, "archived-plan", "old-session", content_hash)
        self.receipts.mkdir(exist_ok=True)

        fails = self.wc.check(session_id="session-A")
        captured = capsys.readouterr()
        assert "WARNING" not in captured.out or "without a receipt" not in captured.out

    def test_warning_arm_runs_without_session_id(self, capsys):
        self.receipts.mkdir(parents=True, exist_ok=True)
        content_hash = hashlib.sha256(b"no receipt deposit").hexdigest()
        _add_clearance(self.db_path, "plan-x.md", content_hash)

        fails = self.wc.check(session_id=None)
        captured = capsys.readouterr()
        assert "WARNING" in captured.out
        assert "without a receipt" in captured.out

    def test_malformed_receipt_missing_fields(self, capsys):
        self.receipts.mkdir(parents=True, exist_ok=True)
        bad = self.receipts / "receipt-incomplete-session-A-000000000000.json"
        bad.write_text(json.dumps({"slug": "incomplete"}))

        fails = self.wc.check(session_id="session-A")
        receipt_fails = [f for f in fails if "[2r/receipts]" in f]
        assert len(receipt_fails) == 0
        captured = capsys.readouterr()
        assert "malformed" in captured.out


# ---------------------------------------------------------------------------
# _retire_receipts tests
# ---------------------------------------------------------------------------

class TestRetireReceipts:
    @pytest.fixture(autouse=True)
    def _setup(self, tmp_path, monkeypatch):
        self.tmp = tmp_path
        self.receipts = tmp_path / "receipts"
        self.receipts.mkdir()
        self.db_path = tmp_path / "lifecycle.db"

        sys.path.insert(0, str(BELLOWS_ROOT))
        import lifecycle
        lifecycle.init_lifecycle_db(str(self.db_path))
        import bellows as bm
        monkeypatch.setattr(bm, "BELLOWS_ROOT", tmp_path)
        self.bm = bm

    def _insert_plan(self, plan_id, placeholder_name):
        conn = sqlite3.connect(str(self.db_path))
        conn.execute(
            "INSERT INTO plans (id, type, target_project, deposit_placeholder_name, "
            "lifecycle_state, created_at) "
            "VALUES (?, 'executable', '/tmp/test', ?, 'closed', '2026-01-01T00:00:00')",
            (plan_id, placeholder_name),
        )
        conn.commit()
        conn.close()

    def test_retires_matching_receipts(self):
        self._insert_plan(100, "executable-foo.md")

        content_hash = hashlib.sha256(b"foo bytes").hexdigest()
        receipt = _write_receipt(self.receipts, "executable-foo", "session-1", content_hash)
        assert receipt.exists()

        self.bm._retire_receipts(100)

        assert not receipt.exists()
        archived = self.receipts / "archived" / receipt.name
        assert archived.exists()

    def test_prefix_extending_slug_not_archived(self):
        self._insert_plan(200, "executable-foo.md")

        hash_foo = hashlib.sha256(b"foo").hexdigest()
        hash_foo2 = hashlib.sha256(b"foo2").hexdigest()
        receipt_foo = _write_receipt(self.receipts, "executable-foo", "s1", hash_foo)
        receipt_foo2 = _write_receipt(self.receipts, "executable-foo-2", "s1", hash_foo2)

        self.bm._retire_receipts(200)

        assert not receipt_foo.exists()
        assert receipt_foo2.exists()

    def test_ignores_missing_receipts_dir(self):
        shutil.rmtree(self.receipts)
        self._insert_plan(300, "test.md")
        self.bm._retire_receipts(300)

    def test_none_plan_id_no_op(self):
        self.bm._retire_receipts(None)


# ---------------------------------------------------------------------------
# clear_plan.py --release-class-hold tests
# ---------------------------------------------------------------------------

class TestClearToolRelease:
    @pytest.fixture(autouse=True)
    def _setup(self, tmp_path, monkeypatch):
        self.tmp = tmp_path
        self.decisions = tmp_path / "knowledge" / "decisions"
        self.decisions.mkdir(parents=True)
        self.db_path = tmp_path / "lifecycle.db"
        _init_lifecycle_db(self.db_path)

        sys.path.insert(0, str(BELLOWS_ROOT))
        sys.path.insert(0, str(BELLOWS_ROOT / "tools"))
        sys.path.insert(0, str(BELLOWS_ROOT / "scripts"))

        monkeypatch.setenv("PYTHONPATH", str(BELLOWS_ROOT))

        import lifecycle
        monkeypatch.setattr(lifecycle, "LIFECYCLE_DB_PATH", str(self.db_path))
        self.lifecycle = lifecycle

    def _create_held_plan(self, slug="executable-test-plan", plan_class="shop-infra",
                          cycle_content=None, hold_reason="class:shop-infra"):
        if cycle_content is None:
            cycle_content = textwrap.dedent(f"""\
                # test plan

                **Date:** 2026-08-24 | **Tier:** Medium | **Dispatch Mode:** bellows | **Test Scope:** full suite (bellows)

                ## STEP 1 — DEV

                Do the work.

                ## Drafting Cycle
                - Weak spots: w1 dry
                - Destruction: w1 dry
                - Vulnerabilities: w1 dry
                - Integration-record: w1 dry
                - ACID: w1 dry

                ## Cycle Manifest
                tier: T2
                target: hooks/eluvian/wrap_check.py
                class: {plan_class}
            """)
        hold_name = f"hold-{slug}.md"
        hold_path = self.decisions / hold_name
        hold_path.write_text(cycle_content)

        sidecar = self.decisions / f"hold-{slug}.hold.json"
        sidecar.write_text(json.dumps({"hold_reason": hold_reason, "held_at": datetime.now().isoformat()}))

        return str(hold_path)

    def test_release_class_hold_success(self):
        import tools.clear_plan as cp
        hold_path = self._create_held_plan()

        result = cp.release_class_hold(hold_path)
        assert result is True

        claimable = self.decisions / "executable-test-plan.md"
        assert claimable.exists()
        assert not Path(hold_path).exists()
        sidecar = self.decisions / "hold-executable-test-plan.hold.json"
        assert not sidecar.exists()

        conn = sqlite3.connect(str(self.db_path))
        row = conn.execute(
            "SELECT plan_path, cleared_by, assigned_class FROM clearances"
        ).fetchone()
        conn.close()
        assert row is not None
        assert row[0] == "executable-test-plan.md"
        assert row[1] == "clear_tool"
        assert row[2] == "shop-infra"

    def test_release_works_with_restart_rewritten_sidecar(self):
        import tools.clear_plan as cp
        hold_path = self._create_held_plan(hold_reason="held_pending_ceo_release")
        result = cp.release_class_hold(hold_path)
        assert result is True

    def test_failing_gate_refuses(self):
        import tools.clear_plan as cp
        hold_path = self._create_held_plan(cycle_content=textwrap.dedent("""\
            # test plan — no cycle manifest
            No Drafting Cycle section at all.
        """))
        result = cp.release_class_hold(hold_path)
        assert result is False
        assert Path(hold_path).exists()
        sidecar = self.decisions / "hold-executable-test-plan.hold.json"
        assert sidecar.exists()

    def test_no_flag_old_rename_path(self):
        import tools.clear_plan as cp
        hold_path = self._create_held_plan()
        result = cp.clear_plan(hold_path)
        assert result is True
        ready = self.decisions / "ready-executable-test-plan.md"
        assert ready.exists()
        sidecar = self.decisions / "hold-executable-test-plan.hold.json"
        assert not sidecar.exists()

    def test_benign_only_fail_passes(self):
        import tools.clear_plan as cp
        hold_path = self._create_held_plan()
        result = cp.release_class_hold(hold_path)
        assert result is True

    def test_stores_basename_not_absolute(self):
        import tools.clear_plan as cp
        hold_path = self._create_held_plan()
        cp.release_class_hold(hold_path)

        conn = sqlite3.connect(str(self.db_path))
        row = conn.execute("SELECT plan_path FROM clearances").fetchone()
        conn.close()
        assert row[0] == "executable-test-plan.md"
        assert "/" not in row[0]


# ---------------------------------------------------------------------------
# Porcelain receipts check in [2/bellows]
# ---------------------------------------------------------------------------

class TestPorcelainReceipts:
    def test_porcelain_import(self):
        import hooks.eluvian.wrap_check as wc
        source = Path(wc.__file__).read_text()
        assert 'porcelain(BELLOWS, "receipts")' in source
