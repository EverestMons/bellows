"""Tests for the no_receipt admission hold (R-F3) — 19 tests.

D-5's eleven tests + additions 12-14 (A4), 15/15b (A2b), 16-18 (A5).
Isolation: autouse fixture repoints _bellows_root so every depositor test
scans a tmp receipts dir, never the live one.
"""

import hashlib
import json
import os
import shutil
import sqlite3
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

_BELLOWS_ROOT_REAL = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_BELLOWS_ROOT_REAL / "scripts"))
sys.path.insert(0, str(_BELLOWS_ROOT_REAL / "tools"))

import depositor
from lifecycle import init_lifecycle_db


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def _isolate_receipts(monkeypatch, tmp_path):
    """Isolation: every depositor test scans a tmp receipts dir, never the live one."""
    isolated_root = tmp_path / "bellows_root"
    isolated_root.mkdir(exist_ok=True)
    (isolated_root / "receipts").mkdir(exist_ok=True)
    monkeypatch.setattr(depositor, "resolve_bellows_root", lambda: isolated_root)


@pytest.fixture
def decisions_dir(tmp_path):
    d = tmp_path / "proj" / "knowledge" / "decisions"
    d.mkdir(parents=True)
    return str(d)


@pytest.fixture
def lifecycle_db(tmp_path):
    db_path = str(tmp_path / "lifecycle.db")
    init_lifecycle_db(db_path)
    return db_path


def _make_depositor(decisions_dir, lifecycle_db, disk_ok=True):
    return depositor.Depositor(
        disk_preflight_fn=lambda cfg: disk_ok,
        shutting_down_check=lambda: False,
        config={"watched_projects": [decisions_dir]},
        lifecycle_db_path=lifecycle_db,
    )


def _make_plan(*, writes=None, reads=None, plan_class=None):
    lines = [
        "# Test Plan",
        "**Date:** 2026-08-20 | **Tier:** Small | **Dispatch Mode:** bellows",
        "**pause_for_verdict:** after_qa_step",
        "",
        "## Drafting Cycle",
        "**Tier:** T0",
        "**Walk 0 (context pin):**",
        "**Walk 1 STATUS:** instruction 0 / record 0 — **§2 BAR MET.**",
        "**Closing:** 1 warm walk (bar met w1).",
        "**cycle_check:** w1 `BAR_MET`.",
        "",
        "---",
        "",
        "## STEP 1 — DEV",
        "",
    ]
    if writes:
        lines.append("**Deposits:**")
        for p in writes:
            lines.append(f"- `{p}`")
        lines.append("")
    if reads:
        lines.append("**Scope:**")
        for r in reads:
            lines.append(f"- `{r}`")
        lines.append("")
    if plan_class:
        lines.insert(1, f"**class:** {plan_class}")
    lines.append("End with an Output Receipt.")
    return "\n".join(lines)


def _stage_plan(decisions_dir, slug, text):
    fname = f"ready-{slug}.md"
    path = os.path.join(decisions_dir, fname)
    with open(path, "w") as f:
        f.write(text)
    return path


def _write_receipt(tmp_path, slug, content_hash, session_id="test-session"):
    receipts_dir = tmp_path / "bellows_root" / "receipts"
    receipts_dir.mkdir(parents=True, exist_ok=True)
    receipt = {
        "slug": slug,
        "content_hash": content_hash,
        "session_id": session_id,
        "armed_at": "2026-08-25T00:00:00",
    }
    rpath = receipts_dir / f"receipt-{slug}-{session_id}-{content_hash[:12]}.json"
    rpath.write_text(json.dumps(receipt))
    return str(rpath)


def _write_receipt_for_plan(tmp_path, plan_path):
    filename = os.path.basename(plan_path)
    slug = filename
    if slug.startswith("ready-"):
        slug = slug[len("ready-"):]
    elif slug.startswith("hold-"):
        slug = slug[len("hold-"):]
    if slug.endswith(".md"):
        slug = slug[:-len(".md")]
    content_hash = hashlib.sha256(Path(plan_path).read_bytes()).hexdigest()
    return _write_receipt(tmp_path, slug, content_hash)


# ---------------------------------------------------------------------------
# D-5 Tests 1-11
# ---------------------------------------------------------------------------

class TestReceiptAdmission:
    @patch("depositor.cycle_check")
    @patch("depositor.subprocess")
    def test_01_receipt_present_passes(
        self, mock_subprocess, mock_cc, decisions_dir, lifecycle_db, tmp_path
    ):
        """receipt-present passes admission (clears, no hold)."""
        mock_cc.run_check.return_value = ("BAR_MET", 0)
        mock_cc.parse_manifest_stanza.return_value = {}
        mock_subprocess.run.return_value = MagicMock(returncode=0, stdout="PASS: all")

        plan_text = _make_plan(writes=["knowledge/research/result.md"])
        path = _stage_plan(decisions_dir, "diagnostic-pass", plan_text)
        _write_receipt_for_plan(tmp_path, path)

        dep = _make_depositor(decisions_dir, lifecycle_db)
        dep.evaluate(path)

        claimable = os.path.join(decisions_dir, "diagnostic-pass.md")
        assert os.path.exists(claimable), "plan should be cleared"
        assert not os.path.exists(path)

    @patch("depositor.cycle_check")
    @patch("depositor.subprocess")
    def test_02_receipt_absent_holds(
        self, mock_subprocess, mock_cc, decisions_dir, lifecycle_db, tmp_path
    ):
        """receipt-absent → HOLD, sidecar hold_reason == 'no_receipt'."""
        mock_cc.run_check.return_value = ("BAR_MET", 0)
        mock_cc.parse_manifest_stanza.return_value = {}
        mock_subprocess.run.return_value = MagicMock(returncode=0, stdout="PASS: all")

        plan_text = _make_plan(writes=["knowledge/research/result.md"])
        path = _stage_plan(decisions_dir, "diagnostic-noreceipt", plan_text)

        dep = _make_depositor(decisions_dir, lifecycle_db)
        dep.evaluate(path)

        hold_path = os.path.join(decisions_dir, "hold-diagnostic-noreceipt.md")
        assert os.path.exists(hold_path)
        data = json.loads(Path(hold_path.replace(".md", ".hold.json")).read_text())
        assert data["hold_reason"] == "no_receipt"

    @patch("depositor.cycle_check")
    @patch("depositor.subprocess")
    def test_03_hash_mismatch_holds(
        self, mock_subprocess, mock_cc, decisions_dir, lifecycle_db, tmp_path
    ):
        """hash-mismatch → HOLD."""
        mock_cc.run_check.return_value = ("BAR_MET", 0)
        mock_cc.parse_manifest_stanza.return_value = {}
        mock_subprocess.run.return_value = MagicMock(returncode=0, stdout="PASS: all")

        plan_text = _make_plan(writes=["knowledge/research/result.md"])
        path = _stage_plan(decisions_dir, "diagnostic-hashmis", plan_text)
        _write_receipt(tmp_path, "diagnostic-hashmis", "0000deadbeef" * 6)

        dep = _make_depositor(decisions_dir, lifecycle_db)
        dep.evaluate(path)

        hold_path = os.path.join(decisions_dir, "hold-diagnostic-hashmis.md")
        assert os.path.exists(hold_path)
        data = json.loads(Path(hold_path.replace(".md", ".hold.json")).read_text())
        assert data["hold_reason"] == "no_receipt"

    @patch("depositor.cycle_check")
    @patch("depositor.subprocess")
    def test_04_archived_only_receipt_holds(
        self, mock_subprocess, mock_cc, decisions_dir, lifecycle_db, tmp_path
    ):
        """archived-only receipt → HOLD (D-2b)."""
        mock_cc.run_check.return_value = ("BAR_MET", 0)
        mock_cc.parse_manifest_stanza.return_value = {}
        mock_subprocess.run.return_value = MagicMock(returncode=0, stdout="PASS: all")

        plan_text = _make_plan(writes=["knowledge/research/result.md"])
        path = _stage_plan(decisions_dir, "diagnostic-archived", plan_text)

        slug = "diagnostic-archived"
        content_hash = hashlib.sha256(Path(path).read_bytes()).hexdigest()
        archived_dir = tmp_path / "bellows_root" / "receipts" / "archived"
        archived_dir.mkdir(parents=True, exist_ok=True)
        receipt = {
            "slug": slug,
            "content_hash": content_hash,
            "session_id": "old-session",
            "armed_at": "2026-01-01T00:00:00",
        }
        (archived_dir / f"receipt-{slug}-old-{content_hash[:12]}.json").write_text(
            json.dumps(receipt)
        )

        dep = _make_depositor(decisions_dir, lifecycle_db)
        dep.evaluate(path)

        hold_path = os.path.join(decisions_dir, "hold-diagnostic-archived.md")
        assert os.path.exists(hold_path)
        data = json.loads(Path(hold_path.replace(".md", ".hold.json")).read_text())
        assert data["hold_reason"] == "no_receipt"

    @patch("depositor.cycle_check")
    @patch("depositor.subprocess")
    def test_05_grandfather_no_exemption(
        self, mock_subprocess, mock_cc, decisions_dir, lifecycle_db, tmp_path
    ):
        """grandfather posture: legacy artifact, no receipt → HOLD."""
        mock_cc.run_check.return_value = ("BAR_MET", 0)
        mock_cc.parse_manifest_stanza.return_value = {}
        mock_subprocess.run.return_value = MagicMock(returncode=0, stdout="PASS: all")

        plan_text = _make_plan(writes=["knowledge/research/legacy.md"])
        path = _stage_plan(decisions_dir, "diagnostic-legacy", plan_text)

        dep = _make_depositor(decisions_dir, lifecycle_db)
        dep.evaluate(path)

        hold_path = os.path.join(decisions_dir, "hold-diagnostic-legacy.md")
        assert os.path.exists(hold_path)
        data = json.loads(Path(hold_path.replace(".md", ".hold.json")).read_text())
        assert data["hold_reason"] == "no_receipt"

    @patch("depositor.cycle_check")
    @patch("depositor.subprocess")
    def test_06_release_reentry_clears(
        self, mock_subprocess, mock_cc, decisions_dir, lifecycle_db, tmp_path
    ):
        """release-re-entry: hold → write receipt → clear_plan rename → re-eval clears."""
        mock_cc.run_check.return_value = ("BAR_MET", 0)
        mock_cc.parse_manifest_stanza.return_value = {}
        mock_subprocess.run.return_value = MagicMock(returncode=0, stdout="PASS: all")

        plan_text = _make_plan(writes=["knowledge/research/reentry.md"])
        path = _stage_plan(decisions_dir, "diagnostic-reentry", plan_text)

        dep = _make_depositor(decisions_dir, lifecycle_db)
        dep.evaluate(path)

        hold_path = os.path.join(decisions_dir, "hold-diagnostic-reentry.md")
        assert os.path.exists(hold_path), "first eval should hold (no receipt)"

        _write_receipt_for_plan(tmp_path, hold_path)

        ready_path = os.path.join(decisions_dir, "ready-diagnostic-reentry.md")
        hold_json = hold_path.replace(".md", ".hold.json")
        os.rename(hold_path, ready_path)
        if os.path.exists(hold_json):
            os.remove(hold_json)

        original_dedup = depositor._DEDUP_WINDOW
        depositor._DEDUP_WINDOW = 0.0
        try:
            dep.evaluate(ready_path)
        finally:
            depositor._DEDUP_WINDOW = original_dedup

        claimable = os.path.join(decisions_dir, "diagnostic-reentry.md")
        assert os.path.exists(claimable), "re-evaluation should clear after receipt"

    @patch("depositor.cycle_check")
    @patch("depositor.subprocess")
    def test_07_ordering_across_paths(
        self, mock_subprocess, mock_cc, decisions_dir, lifecycle_db, tmp_path
    ):
        """no_receipt fires on ready- files; bare-name checked by bellows.py, not depositor."""
        mock_cc.run_check.return_value = ("BAR_MET", 0)
        mock_cc.parse_manifest_stanza.return_value = {}
        mock_subprocess.run.return_value = MagicMock(returncode=0, stdout="PASS: all")

        plan_text = _make_plan(writes=["knowledge/research/ordering.md"])
        path = _stage_plan(decisions_dir, "diagnostic-ordering", plan_text)

        dep = _make_depositor(decisions_dir, lifecycle_db)
        dep.evaluate(path)

        hold_path = os.path.join(decisions_dir, "hold-diagnostic-ordering.md")
        assert os.path.exists(hold_path)
        data = json.loads(Path(hold_path.replace(".md", ".hold.json")).read_text())
        assert data["hold_reason"] == "no_receipt"

        bare_path = os.path.join(decisions_dir, "diagnostic-ordering.md")
        with open(bare_path, "w") as f:
            f.write(plan_text)
        dep.evaluate(bare_path)
        assert os.path.exists(bare_path), "bare-name file ignored by depositor (no ready- prefix)"

    def test_08_seen_non_refire(self, decisions_dir, lifecycle_db, tmp_path):
        """no_receipt hold does NOT add the slug to _seen; hold-* fails is_runnable_plan."""
        import bellows

        plan_text = _make_plan(writes=["knowledge/research/seen.md"])
        path = _stage_plan(decisions_dir, "diagnostic-seen", plan_text)

        dep = _make_depositor(decisions_dir, lifecycle_db)

        with patch("depositor.cycle_check") as mock_cc, \
             patch("depositor.subprocess") as mock_sub:
            mock_cc.run_check.return_value = ("BAR_MET", 0)
            mock_cc.parse_manifest_stanza.return_value = {}
            mock_sub.run.return_value = MagicMock(returncode=0, stdout="PASS: all")
            dep.evaluate(path)

        hold_path = os.path.join(decisions_dir, "hold-diagnostic-seen.md")
        assert os.path.exists(hold_path)
        assert bellows.is_runnable_plan("hold-diagnostic-seen.md") is False

    def test_09_wrap_check_posture_unchanged(self, tmp_path):
        """[2r] posture unchanged: wrap check's blocking arm catches matchless receipts."""
        import hooks.eluvian.wrap_check as wc

        bellows_dir = tmp_path / "bellows"
        bellows_dir.mkdir()
        receipts = bellows_dir / "receipts"
        receipts.mkdir()
        db_path = bellows_dir / "lifecycle.db"
        init_lifecycle_db(str(db_path))

        content_hash = hashlib.sha256(b"orphan plan").hexdigest()
        old_time = (datetime.now() - timedelta(minutes=15)).isoformat()
        receipt = {
            "slug": "orphan-plan",
            "content_hash": content_hash,
            "session_id": "session-wrap",
            "armed_at": old_time,
        }
        (receipts / f"receipt-orphan-plan-session-wrap-{content_hash[:12]}.json").write_text(
            json.dumps(receipt)
        )

        root = tmp_path / "root"
        root.mkdir()

        orig_root = wc.ROOT
        orig_bellows = wc.BELLOWS
        orig_receipts = wc.RECEIPTS
        orig_db = wc.LIFECYCLE_DB
        try:
            wc.ROOT = root
            wc.BELLOWS = bellows_dir
            wc.RECEIPTS = receipts
            wc.LIFECYCLE_DB = db_path
            fails = wc.check(session_id="session-wrap")
        finally:
            wc.ROOT = orig_root
            wc.BELLOWS = orig_bellows
            wc.RECEIPTS = orig_receipts
            wc.LIFECYCLE_DB = orig_db

        receipt_fails = [f for f in fails if "[2r/receipts]" in f]
        assert len(receipt_fails) == 1
        assert "match no clearance or hold" in receipt_fails[0]

    @patch("depositor.cycle_check")
    @patch("depositor.subprocess")
    def test_10_multiple_receipts_one_matching(
        self, mock_subprocess, mock_cc, decisions_dir, lifecycle_db, tmp_path
    ):
        """multiple active receipts, one matching → passes (D-2c any-match)."""
        mock_cc.run_check.return_value = ("BAR_MET", 0)
        mock_cc.parse_manifest_stanza.return_value = {}
        mock_subprocess.run.return_value = MagicMock(returncode=0, stdout="PASS: all")

        plan_text = _make_plan(writes=["knowledge/research/multi.md"])
        path = _stage_plan(decisions_dir, "diagnostic-multi", plan_text)

        _write_receipt(tmp_path, "other-slug", "0" * 64, session_id="s1")
        _write_receipt(tmp_path, "diagnostic-multi", "1" * 64, session_id="s2")
        _write_receipt_for_plan(tmp_path, path)

        dep = _make_depositor(decisions_dir, lifecycle_db)
        dep.evaluate(path)

        claimable = os.path.join(decisions_dir, "diagnostic-multi.md")
        assert os.path.exists(claimable), "should clear — one receipt matches"

    @patch("depositor.cycle_check")
    @patch("depositor.subprocess")
    def test_11_slug_mismatch_hash_match_holds(
        self, mock_subprocess, mock_cc, decisions_dir, lifecycle_db, tmp_path
    ):
        """slug mismatch with hash match → HOLD (slug+hash predicate)."""
        mock_cc.run_check.return_value = ("BAR_MET", 0)
        mock_cc.parse_manifest_stanza.return_value = {}
        mock_subprocess.run.return_value = MagicMock(returncode=0, stdout="PASS: all")

        plan_text = _make_plan(writes=["knowledge/research/slugmis.md"])
        path = _stage_plan(decisions_dir, "diagnostic-slugmis", plan_text)

        content_hash = hashlib.sha256(Path(path).read_bytes()).hexdigest()
        _write_receipt(tmp_path, "wrong-slug", content_hash)

        dep = _make_depositor(decisions_dir, lifecycle_db)
        dep.evaluate(path)

        hold_path = os.path.join(decisions_dir, "hold-diagnostic-slugmis.md")
        assert os.path.exists(hold_path)
        data = json.loads(Path(hold_path.replace(".md", ".hold.json")).read_text())
        assert data["hold_reason"] == "no_receipt"


# ---------------------------------------------------------------------------
# Addition tests 12-14 (A4)
# ---------------------------------------------------------------------------

class TestReceiptEdgeCases:
    @patch("depositor.cycle_check")
    @patch("depositor.subprocess")
    def test_12_malformed_receipt_skipped(
        self, mock_subprocess, mock_cc, decisions_dir, lifecycle_db, tmp_path
    ):
        """malformed receipt JSON → skipped; a matching receipt elsewhere still found."""
        mock_cc.run_check.return_value = ("BAR_MET", 0)
        mock_cc.parse_manifest_stanza.return_value = {}
        mock_subprocess.run.return_value = MagicMock(returncode=0, stdout="PASS: all")

        plan_text = _make_plan(writes=["knowledge/research/malformed.md"])
        path = _stage_plan(decisions_dir, "diagnostic-malformed", plan_text)

        receipts_dir = tmp_path / "bellows_root" / "receipts"
        (receipts_dir / "receipt-bad-parse.json").write_text("NOT VALID JSON {{{")
        _write_receipt_for_plan(tmp_path, path)

        dep = _make_depositor(decisions_dir, lifecycle_db)
        dep.evaluate(path)

        claimable = os.path.join(decisions_dir, "diagnostic-malformed.md")
        assert os.path.exists(claimable), "should clear — malformed receipt skipped, valid one found"

    @patch("depositor.cycle_check")
    @patch("depositor.subprocess")
    def test_13_missing_receipts_dir_holds(
        self, mock_subprocess, mock_cc, decisions_dir, lifecycle_db, tmp_path
    ):
        """missing receipts directory → HOLD with hold_reason == 'no_receipt'."""
        mock_cc.run_check.return_value = ("BAR_MET", 0)
        mock_cc.parse_manifest_stanza.return_value = {}
        mock_subprocess.run.return_value = MagicMock(returncode=0, stdout="PASS: all")

        plan_text = _make_plan(writes=["knowledge/research/nodir.md"])
        path = _stage_plan(decisions_dir, "diagnostic-nodir", plan_text)

        receipts_dir = tmp_path / "bellows_root" / "receipts"
        shutil.rmtree(receipts_dir)

        dep = _make_depositor(decisions_dir, lifecycle_db)
        dep.evaluate(path)

        hold_path = os.path.join(decisions_dir, "hold-diagnostic-nodir.md")
        assert os.path.exists(hold_path)
        data = json.loads(Path(hold_path.replace(".md", ".hold.json")).read_text())
        assert data["hold_reason"] == "no_receipt"

    @patch("depositor.cycle_check")
    @patch("depositor.subprocess")
    def test_14_one_sidecar_invariant(
        self, mock_subprocess, mock_cc, decisions_dir, lifecycle_db, tmp_path
    ):
        """re-hold on the same slug overwrites sidecar, never duplicates."""
        mock_cc.run_check.return_value = ("BAR_MET", 0)
        mock_cc.parse_manifest_stanza.return_value = {}
        mock_subprocess.run.return_value = MagicMock(returncode=0, stdout="PASS: all")

        plan_text = _make_plan(writes=["knowledge/research/dup.md"])
        path = _stage_plan(decisions_dir, "diagnostic-dup", plan_text)

        dep = _make_depositor(decisions_dir, lifecycle_db)
        dep.evaluate(path)

        hold_path = os.path.join(decisions_dir, "hold-diagnostic-dup.md")
        assert os.path.exists(hold_path)

        ready_path2 = os.path.join(decisions_dir, "ready-diagnostic-dup.md")
        os.rename(hold_path, ready_path2)
        hold_json = hold_path.replace(".md", ".hold.json")
        if os.path.exists(hold_json):
            os.remove(hold_json)

        original_dedup = depositor._DEDUP_WINDOW
        depositor._DEDUP_WINDOW = 0.0
        try:
            dep.evaluate(ready_path2)
        finally:
            depositor._DEDUP_WINDOW = original_dedup

        assert os.path.exists(hold_path)
        sidecars = [f for f in os.listdir(decisions_dir) if f.endswith(".hold.json")]
        assert len(sidecars) == 1


# ---------------------------------------------------------------------------
# Tests 15/15b (A2b) — original_reason preservation
# ---------------------------------------------------------------------------

class TestOriginalReasonPreservation:
    def test_15_two_restarts_preserve_original_reason(
        self, decisions_dir, lifecycle_db, tmp_path
    ):
        """TWO consecutive _reevaluate_hold passes preserve original_reason == 'no_receipt'."""
        plan_text = _make_plan(writes=["knowledge/research/restart.md"])
        hold_path = os.path.join(decisions_dir, "hold-diagnostic-restart.md")
        with open(hold_path, "w") as f:
            f.write(plan_text)
        hold_json = hold_path.replace(".md", ".hold.json")
        with open(hold_json, "w") as f:
            json.dump({"hold_reason": "no_receipt", "held_at": "2026-08-25T00:00:00"}, f)

        dep = _make_depositor(decisions_dir, lifecycle_db)

        with patch("depositor.cycle_check") as mock_cc, \
             patch("depositor.subprocess") as mock_sub:
            mock_cc.run_check.return_value = ("BAR_MET", 0)
            mock_cc.parse_manifest_stanza.return_value = {}
            mock_sub.run.return_value = MagicMock(returncode=0, stdout="PASS: all")

            dep._reevaluate_hold(hold_path)

            data = json.loads(Path(hold_json).read_text())
            assert data["hold_reason"] == "held_pending_ceo_release"
            assert data["original_reason"] == "no_receipt"

            dep._reevaluate_hold(hold_path)

            data = json.loads(Path(hold_json).read_text())
            assert data["hold_reason"] == "held_pending_ceo_release"
            assert data["original_reason"] == "no_receipt"

    def test_15_differing_reason_restart_preserves(
        self, decisions_dir, lifecycle_db, tmp_path
    ):
        """Differing-reason rewrite at restart 2 still preserves original_reason."""
        plan_text = _make_plan(writes=["knowledge/research/diff.md"])
        hold_path = os.path.join(decisions_dir, "hold-diagnostic-diff.md")
        with open(hold_path, "w") as f:
            f.write(plan_text)
        hold_json = hold_path.replace(".md", ".hold.json")
        with open(hold_json, "w") as f:
            json.dump({"hold_reason": "no_receipt", "held_at": "2026-08-25T00:00:00"}, f)

        dep = _make_depositor(decisions_dir, lifecycle_db)

        with patch("depositor.cycle_check") as mock_cc, \
             patch("depositor.subprocess") as mock_sub:
            mock_cc.run_check.return_value = ("BAR_MET", 0)
            mock_cc.parse_manifest_stanza.return_value = {}
            mock_sub.run.return_value = MagicMock(returncode=0, stdout="PASS: all")

            dep._reevaluate_hold(hold_path)
            data = json.loads(Path(hold_json).read_text())
            assert data["original_reason"] == "no_receipt"

            sibling_text = _make_plan(writes=["knowledge/research/diff.md"])
            sibling_path = os.path.join(decisions_dir, "ready-diagnostic-collider.md")
            with open(sibling_path, "w") as f:
                f.write(sibling_text)

            dep._reevaluate_hold(hold_path)
            data = json.loads(Path(hold_json).read_text())
            assert "collision" in data["hold_reason"]
            assert data["original_reason"] == "no_receipt"

    def test_15b_vanished_sidecar_no_raise(
        self, decisions_dir, lifecycle_db, tmp_path
    ):
        """Clause (iv): sidecar vanished between read and write → no raise, fresh write."""
        plan_text = _make_plan(writes=["knowledge/research/vanish.md"])
        hold_path = os.path.join(decisions_dir, "hold-diagnostic-vanish.md")
        with open(hold_path, "w") as f:
            f.write(plan_text)
        hold_json = hold_path.replace(".md", ".hold.json")

        dep = _make_depositor(decisions_dir, lifecycle_db)

        with patch("depositor.cycle_check") as mock_cc, \
             patch("depositor.subprocess") as mock_sub:
            mock_cc.run_check.return_value = ("BAR_MET", 0)
            mock_cc.parse_manifest_stanza.return_value = {}
            mock_sub.run.return_value = MagicMock(returncode=0, stdout="PASS: all")

            dep._reevaluate_hold(hold_path)

            assert os.path.exists(hold_json)
            data = json.loads(Path(hold_json).read_text())
            assert data["hold_reason"] == "held_pending_ceo_release"


# ---------------------------------------------------------------------------
# Tests 16 (A5 — deposit_receipt hold- slug fix)
# ---------------------------------------------------------------------------

class TestHoldSlugFix:
    def test_16_hold_prefix_receipt_satisfies_check(
        self, decisions_dir, lifecycle_db, tmp_path
    ):
        """Receipt written against hold-*.md path derives the bare slug and satisfies admission."""
        import tools.deposit_receipt as dr

        plan_text = _make_plan(writes=["knowledge/research/holdfix.md"])
        ready_path = _stage_plan(decisions_dir, "diagnostic-holdfix", plan_text)

        dep = _make_depositor(decisions_dir, lifecycle_db)

        with patch("depositor.cycle_check") as mock_cc, \
             patch("depositor.subprocess") as mock_sub:
            mock_cc.run_check.return_value = ("BAR_MET", 0)
            mock_cc.parse_manifest_stanza.return_value = {}
            mock_sub.run.return_value = MagicMock(returncode=0, stdout="PASS: all")

            dep.evaluate(ready_path)

        hold_path = os.path.join(decisions_dir, "hold-diagnostic-holdfix.md")
        assert os.path.exists(hold_path)

        receipts_dir = tmp_path / "bellows_root" / "receipts"
        orig_receipts_dir = dr._RECEIPTS_DIR
        dr._RECEIPTS_DIR = str(receipts_dir)
        try:
            result = dr.write_receipt(hold_path, "test-session-16")
        finally:
            dr._RECEIPTS_DIR = orig_receipts_dir

        assert result is True

        receipt_files = list(receipts_dir.glob("receipt-*.json"))
        assert len(receipt_files) >= 1
        receipt_data = json.loads(receipt_files[-1].read_text())
        assert receipt_data["slug"] == "diagnostic-holdfix"

        ready_path2 = os.path.join(decisions_dir, "ready-diagnostic-holdfix.md")
        hold_json = hold_path.replace(".md", ".hold.json")
        os.rename(hold_path, ready_path2)
        if os.path.exists(hold_json):
            os.remove(hold_json)

        original_dedup = depositor._DEDUP_WINDOW
        depositor._DEDUP_WINDOW = 0.0
        try:
            with patch("depositor.cycle_check") as mock_cc, \
                 patch("depositor.subprocess") as mock_sub:
                mock_cc.run_check.return_value = ("BAR_MET", 0)
                mock_cc.parse_manifest_stanza.return_value = {}
                mock_sub.run.return_value = MagicMock(returncode=0, stdout="PASS: all")
                dep.evaluate(ready_path2)
        finally:
            depositor._DEDUP_WINDOW = original_dedup

        claimable = os.path.join(decisions_dir, "diagnostic-holdfix.md")
        assert os.path.exists(claimable), "re-eval should clear after hold-path receipt"


# ---------------------------------------------------------------------------
# Tests 17-18 (A5 — clear_plan positive routing guard)
# ---------------------------------------------------------------------------

class TestPositiveRoutingGuard:
    def _make_held_plan(self, decisions_dir, slug, hold_reason, original_reason=None,
                        plan_text=None):
        if plan_text is None:
            plan_text = _make_plan(writes=["knowledge/research/routing.md"])
        hold_path = os.path.join(decisions_dir, f"hold-{slug}.md")
        with open(hold_path, "w") as f:
            f.write(plan_text)
        sidecar = {"hold_reason": hold_reason, "held_at": "2026-08-25T00:00:00"}
        if original_reason is not None:
            sidecar["original_reason"] = original_reason
        hold_json = hold_path.replace(".md", ".hold.json")
        with open(hold_json, "w") as f:
            json.dump(sidecar, f)
        return hold_path

    def test_17_refusal_no_receipt_direct(self, decisions_dir, lifecycle_db, tmp_path):
        """release_class_hold refuses on no_receipt direct hold."""
        from clear_plan import release_class_hold
        hold_path = self._make_held_plan(decisions_dir, "diagnostic-r17a", "no_receipt")
        result = release_class_hold(hold_path)
        assert result is False
        assert os.path.exists(hold_path), "file should remain held"

    def test_17_refusal_no_receipt_via_original(self, decisions_dir, lifecycle_db, tmp_path):
        """release_class_hold refuses when original_reason is no_receipt."""
        from clear_plan import release_class_hold
        hold_path = self._make_held_plan(
            decisions_dir, "diagnostic-r17b",
            "held_pending_ceo_release", original_reason="no_receipt"
        )
        result = release_class_hold(hold_path)
        assert result is False
        assert os.path.exists(hold_path)

    def test_17_refusal_collision(self, decisions_dir, lifecycle_db, tmp_path):
        """release_class_hold refuses on collision:* hold (S3-1 demo case)."""
        from clear_plan import release_class_hold
        hold_path = self._make_held_plan(
            decisions_dir, "diagnostic-r17c", "collision:writes∩writes with #99"
        )
        result = release_class_hold(hold_path)
        assert result is False
        assert os.path.exists(hold_path)

    def test_18_class_hold_releases(self, decisions_dir, lifecycle_db, tmp_path, monkeypatch):
        """A genuine class:* hold releases through release_class_hold."""
        import tools.clear_plan as cp
        import lifecycle as lc

        monkeypatch.setattr(lc, "LIFECYCLE_DB_PATH", lifecycle_db)

        plan_text = (
            "# Test Plan\n\n"
            "**Date:** 2026-08-20 | **Tier:** Small | **Dispatch Mode:** bellows\n\n"
            "## STEP 1 — DEV\n\n"
            "Do the work.\n\n"
            "## Drafting Cycle\n"
            "- Weak spots: w1 dry\n"
            "- Destruction: w1 dry\n"
            "- Vulnerabilities: w1 dry\n"
            "- Integration-record: w1 dry\n"
            "- ACID: w1 dry\n\n"
            "## Cycle Manifest\n"
            "tier: T2\n"
            "target: hooks/eluvian/wrap_check.py\n"
            "class: shop-infra\n"
            "validation: cycle_check=BAR_MET, plan_lint=0_FAIL, fold_check=N/A, propagation_check=N/A\n"
        )
        hold_path = self._make_held_plan(
            decisions_dir, "executable-r18a", "class:shop-infra",
            plan_text=plan_text,
        )

        result = cp.release_class_hold(hold_path)
        assert result is True
        assert not os.path.exists(hold_path)

    def test_18_legacy_no_original_reason_releases(
        self, decisions_dir, lifecycle_db, tmp_path, monkeypatch
    ):
        """Legacy rewritten sidecar (no original_reason) with held_pending_ceo_release
        still releases — keeps pre-A2b behavior."""
        import tools.clear_plan as cp
        import lifecycle as lc

        monkeypatch.setattr(lc, "LIFECYCLE_DB_PATH", lifecycle_db)

        plan_text = (
            "# Test Plan\n\n"
            "**Date:** 2026-08-20 | **Tier:** Small | **Dispatch Mode:** bellows\n\n"
            "## STEP 1 — DEV\n\n"
            "Do the work.\n\n"
            "## Drafting Cycle\n"
            "- Weak spots: w1 dry\n"
            "- Destruction: w1 dry\n"
            "- Vulnerabilities: w1 dry\n"
            "- Integration-record: w1 dry\n"
            "- ACID: w1 dry\n\n"
            "## Cycle Manifest\n"
            "tier: T2\n"
            "target: hooks/eluvian/wrap_check.py\n"
            "class: shop-infra\n"
            "validation: cycle_check=BAR_MET, plan_lint=0_FAIL, fold_check=N/A, propagation_check=N/A\n"
        )
        hold_path = self._make_held_plan(
            decisions_dir, "executable-r18b", "held_pending_ceo_release",
            plan_text=plan_text,
        )

        result = cp.release_class_hold(hold_path)
        assert result is True
        assert not os.path.exists(hold_path)
