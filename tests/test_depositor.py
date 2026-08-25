"""Tests for depositor.py — in-bellows depositor + dashboard DEPOSITS panel."""

import hashlib
import json
import os
import re
import sqlite3
import sys
import threading
import time
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))

import depositor
import status
from lifecycle import init_lifecycle_db

BELLOWS_ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture(autouse=True)
def _isolate_receipts(monkeypatch, tmp_path):
    """Isolation: every depositor test scans a tmp receipts dir, never the live one."""
    isolated_root = tmp_path / "bellows_root"
    isolated_root.mkdir(exist_ok=True)
    (isolated_root / "receipts").mkdir(exist_ok=True)
    monkeypatch.setattr(depositor, "resolve_bellows_root", lambda: isolated_root)


def _write_receipt_for_plan(tmp_path, plan_path):
    """Write a receipt matching the staged ready-*.md plan into the isolated receipts dir."""
    filename = os.path.basename(plan_path)
    slug = filename
    if slug.startswith("ready-"):
        slug = slug[len("ready-"):]
    if slug.endswith(".md"):
        slug = slug[:-len(".md")]
    content_hash = hashlib.sha256(Path(plan_path).read_bytes()).hexdigest()
    receipts_dir = tmp_path / "bellows_root" / "receipts"
    receipts_dir.mkdir(parents=True, exist_ok=True)
    receipt = {
        "slug": slug,
        "content_hash": content_hash,
        "session_id": "test-session",
        "armed_at": "2026-08-25T00:00:00",
    }
    rpath = receipts_dir / f"receipt-{slug}-test-{content_hash[:12]}.json"
    rpath.write_text(json.dumps(receipt))
    return str(rpath)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _make_plan(*, writes=None, reads=None, plan_class=None, deposits=None):
    """Build minimal plan text with a Deposits block and optional Scope."""
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
    if deposits or writes:
        lines.append("**Deposits:**")
        for p in (deposits or writes or []):
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


@pytest.fixture
def decisions_dir(tmp_path):
    """Create a decisions dir structure: tmp_path/proj/knowledge/decisions/."""
    d = tmp_path / "proj" / "knowledge" / "decisions"
    d.mkdir(parents=True)
    return str(d)


@pytest.fixture
def lifecycle_db(tmp_path):
    db_path = str(tmp_path / "lifecycle.db")
    init_lifecycle_db(db_path)
    return db_path


def _make_depositor(decisions_dir, lifecycle_db, disk_ok=True, shutting_down=False):
    return depositor.Depositor(
        disk_preflight_fn=lambda cfg: disk_ok,
        shutting_down_check=lambda: shutting_down,
        config={"watched_projects": [decisions_dir]},
        lifecycle_db_path=lifecycle_db,
    )


def _stage_plan(decisions_dir, slug, text):
    """Write a ready-prefixed plan file and return its path."""
    fname = f"ready-{slug}.md"
    path = os.path.join(decisions_dir, fname)
    with open(path, "w") as f:
        f.write(text)
    return path


# ---------------------------------------------------------------------------
# Import whitelist assertion (W1)
# ---------------------------------------------------------------------------

class TestImportWhitelist:
    def test_depositor_imports_no_dispatch_functions(self):
        """The depositor module source must NOT import mint_and_claim, run_plan, or handle_new_plan."""
        src = Path(BELLOWS_ROOT / "depositor.py").read_text()
        for forbidden in ("mint_and_claim", "run_plan", "handle_new_plan"):
            assert forbidden not in src, (
                f"depositor.py must not reference '{forbidden}' — "
                f"safety invariant: depositor never mints, never dispatches"
            )


# ---------------------------------------------------------------------------
# Class assignment from writes
# ---------------------------------------------------------------------------

class TestClassAssignment:
    def _dep(self, tmp_path):
        d = tmp_path / "p" / "knowledge" / "decisions"
        d.mkdir(parents=True)
        db = str(tmp_path / "lifecycle.db")
        init_lifecycle_db(db)
        return _make_depositor(str(d), db)

    def test_read_only_class(self, tmp_path):
        dep = self._dep(tmp_path)
        assert dep._assign_class(["knowledge/research/foo.md"]) == "read-only"
        assert dep._assign_class(["bellows/knowledge/research/bar.md"]) == "read-only"
        assert dep._assign_class(["scratch/tmp.txt"]) == "read-only"

    def test_register_writing_class(self, tmp_path):
        dep = self._dep(tmp_path)
        assert dep._assign_class(["knowledge/decisions/register-cycles.md"]) == "register-writing"
        assert dep._assign_class(["DRAFTING_CYCLE.md"]) == "shop-infra"

    def test_shop_infra_class(self, tmp_path):
        dep = self._dep(tmp_path)
        assert dep._assign_class(["bellows/depositor.py"]) == "shop-infra"
        assert dep._assign_class(["bellows/bellows.py", "bellows/status.py"]) == "shop-infra"

    def test_empty_writes_returns_none(self, tmp_path):
        dep = self._dep(tmp_path)
        assert dep._assign_class([]) is None


# ---------------------------------------------------------------------------
# Class mismatch → HOLD
# ---------------------------------------------------------------------------

class TestClassMismatch:
    @patch("depositor.cycle_check")
    @patch("depositor.subprocess")
    def test_declared_readonly_with_register_write_holds(
        self, mock_subprocess, mock_cc, decisions_dir, lifecycle_db, tmp_path
    ):
        mock_cc.run_check.return_value = ("BAR_MET", 0)
        mock_cc.parse_manifest_stanza.return_value = {
            "class": "read-only",
            "writes": "knowledge/decisions/register-cycles.md",
        }
        mock_subprocess.run.return_value = MagicMock(returncode=0, stdout="PASS: all")

        plan_text = _make_plan(
            writes=["knowledge/decisions/register-cycles.md"],
            plan_class="read-only",
        )
        path = _stage_plan(decisions_dir, "executable-test", plan_text)
        _write_receipt_for_plan(tmp_path, path)
        dep = _make_depositor(decisions_dir, lifecycle_db)
        dep.evaluate(path)

        assert not os.path.exists(path), "ready- file should be renamed"
        hold_path = os.path.join(decisions_dir, "hold-executable-test.md")
        assert os.path.exists(hold_path), "should be HELD"
        hold_json = hold_path.replace(".md", ".hold.json")
        assert os.path.exists(hold_json)
        data = json.loads(Path(hold_json).read_text())
        assert "class_mismatch" in data["hold_reason"]


# ---------------------------------------------------------------------------
# Collision detection
# ---------------------------------------------------------------------------

class TestCollision:
    @patch("depositor.cycle_check")
    @patch("depositor.subprocess")
    def test_writes_intersect_writes_with_in_flight_holds(
        self, mock_subprocess, mock_cc, decisions_dir, lifecycle_db
    ):
        """Collision: writes∩writes with an in-flight plan → HOLD."""
        mock_cc.run_check.return_value = ("BAR_MET", 0)
        mock_cc.parse_manifest_stanza.return_value = {}
        mock_subprocess.run.return_value = MagicMock(returncode=0, stdout="PASS: all")

        conn = sqlite3.connect(lifecycle_db)
        conn.execute(
            "INSERT INTO plans (id, type, target_project, title, dispatch_mode, tier,"
            " lifecycle_state, total_steps, deposit_placeholder_name, created_at)"
            " VALUES (99, 'executable', ?, 'Collider', 'bellows', 'Small',"
            " 'in_progress', 1, 'executable-collider.md', ?)",
            (str(Path(decisions_dir).parent.parent), "2026-08-20T00:00:00"),
        )
        conn.commit()
        conn.close()

        in_progress_text = _make_plan(writes=["knowledge/research/shared.md"])
        ip_path = os.path.join(decisions_dir, "in-progress-executable-99.md")
        with open(ip_path, "w") as f:
            f.write(in_progress_text)

        staged_text = _make_plan(writes=["knowledge/research/shared.md"])
        path = _stage_plan(decisions_dir, "executable-staged", staged_text)

        dep = _make_depositor(decisions_dir, lifecycle_db)
        dep.evaluate(path)

        hold_path = os.path.join(decisions_dir, "hold-executable-staged.md")
        assert os.path.exists(hold_path)
        data = json.loads(Path(hold_path.replace(".md", ".hold.json")).read_text())
        assert "writes∩writes" in data["hold_reason"]

    @patch("depositor.cycle_check")
    @patch("depositor.subprocess")
    def test_writes_intersect_writes_with_sibling_holds(
        self, mock_subprocess, mock_cc, decisions_dir, lifecycle_db
    ):
        """Collision: writes∩writes with another ready- sibling → HOLD."""
        mock_cc.run_check.return_value = ("BAR_MET", 0)
        mock_cc.parse_manifest_stanza.return_value = {}
        mock_subprocess.run.return_value = MagicMock(returncode=0, stdout="PASS: all")

        sibling_text = _make_plan(writes=["knowledge/research/conflict.md"])
        _stage_plan(decisions_dir, "diagnostic-sibling", sibling_text)

        staged_text = _make_plan(writes=["knowledge/research/conflict.md"])
        path = _stage_plan(decisions_dir, "executable-target", staged_text)

        dep = _make_depositor(decisions_dir, lifecycle_db)
        dep.evaluate(path)

        hold_path = os.path.join(decisions_dir, "hold-executable-target.md")
        assert os.path.exists(hold_path)

    def test_file_vs_file_collision(self, tmp_path):
        d = tmp_path / "p" / "knowledge" / "decisions"
        d.mkdir(parents=True)
        db = str(tmp_path / "lifecycle.db")
        init_lifecycle_db(db)
        dep = _make_depositor(str(d), db)
        result = dep._check_collisions(
            ["knowledge/research/a.md"], [],
            [{"writes": ["knowledge/research/a.md"], "project_root": str(d.parent.parent), "label": "test"}],
            str(d.parent.parent),
        )
        assert result is not None
        assert "writes∩writes" in result["reason"]

    def test_prefix_vs_file_collision(self, tmp_path):
        d = tmp_path / "p" / "knowledge" / "decisions"
        d.mkdir(parents=True)
        db = str(tmp_path / "lifecycle.db")
        init_lifecycle_db(db)
        dep = _make_depositor(str(d), db)
        result = dep._check_collisions(
            ["knowledge/research/"], [],
            [{"writes": ["knowledge/research/a.md"], "project_root": str(d.parent.parent), "label": "test"}],
            str(d.parent.parent),
        )
        assert result is not None

    def test_prefix_vs_prefix_collision(self, tmp_path):
        d = tmp_path / "p" / "knowledge" / "decisions"
        d.mkdir(parents=True)
        db = str(tmp_path / "lifecycle.db")
        init_lifecycle_db(db)
        dep = _make_depositor(str(d), db)
        result = dep._check_collisions(
            ["knowledge/research/"], [],
            [{"writes": ["knowledge/"], "project_root": str(d.parent.parent), "label": "test"}],
            str(d.parent.parent),
        )
        assert result is not None


# ---------------------------------------------------------------------------
# Fail-safe: unparseable / missing class → HOLD
# ---------------------------------------------------------------------------

class TestFailSafe:
    @patch("depositor.cycle_check")
    @patch("depositor.subprocess")
    def test_empty_writes_holds(self, mock_subprocess, mock_cc, decisions_dir, lifecycle_db):
        mock_cc.run_check.return_value = ("BAR_MET", 0)
        mock_cc.parse_manifest_stanza.return_value = {}
        mock_subprocess.run.return_value = MagicMock(returncode=0, stdout="")

        plan_text = "# Empty plan\nNo deposits block.\n"
        path = _stage_plan(decisions_dir, "executable-empty", plan_text)

        dep = _make_depositor(decisions_dir, lifecycle_db)
        dep.evaluate(path)

        hold_path = os.path.join(decisions_dir, "hold-executable-empty.md")
        assert os.path.exists(hold_path)
        data = json.loads(Path(hold_path.replace(".md", ".hold.json")).read_text())
        assert "empty_writes" in data["hold_reason"]


# ---------------------------------------------------------------------------
# Read-only plan with no collision → CLEAR
# ---------------------------------------------------------------------------

class TestClear:
    @patch("depositor.cycle_check")
    @patch("depositor.subprocess")
    def test_readonly_no_collision_clears(
        self, mock_subprocess, mock_cc, decisions_dir, lifecycle_db, tmp_path
    ):
        mock_cc.run_check.return_value = ("BAR_MET", 0)
        mock_cc.parse_manifest_stanza.return_value = {}
        mock_subprocess.run.return_value = MagicMock(returncode=0, stdout="PASS: all")

        plan_text = _make_plan(writes=["knowledge/research/result.md"])
        path = _stage_plan(decisions_dir, "diagnostic-clear", plan_text)
        _write_receipt_for_plan(tmp_path, path)

        dep = _make_depositor(decisions_dir, lifecycle_db)
        dep.evaluate(path)

        claimable_path = os.path.join(decisions_dir, "diagnostic-clear.md")
        assert os.path.exists(claimable_path), "plan should be cleared to claimable name"
        assert not os.path.exists(path), "ready- file should no longer exist"

        import bellows
        assert bellows.is_runnable_plan("diagnostic-clear.md") is True


# ---------------------------------------------------------------------------
# HOLD writes hold-X.md + .hold.json; is_runnable_plan("hold-…") is False
# ---------------------------------------------------------------------------

class TestHoldMechanics:
    @patch("depositor.cycle_check")
    @patch("depositor.subprocess")
    def test_hold_creates_holdfile_and_json(
        self, mock_subprocess, mock_cc, decisions_dir, lifecycle_db, tmp_path
    ):
        mock_cc.run_check.return_value = ("BAR_MET", 0)
        mock_cc.parse_manifest_stanza.return_value = {}
        mock_subprocess.run.return_value = MagicMock(returncode=0, stdout="PASS: all")

        plan_text = _make_plan(writes=["bellows/depositor.py"])
        path = _stage_plan(decisions_dir, "executable-hold", plan_text)
        _write_receipt_for_plan(tmp_path, path)

        dep = _make_depositor(decisions_dir, lifecycle_db)
        dep.evaluate(path)

        hold_path = os.path.join(decisions_dir, "hold-executable-hold.md")
        assert os.path.exists(hold_path)

        hold_json = hold_path.replace(".md", ".hold.json")
        assert os.path.exists(hold_json)
        data = json.loads(Path(hold_json).read_text())
        assert data["hold_reason"] == "class:shop-infra"

        import bellows
        assert bellows.is_runnable_plan("hold-executable-hold.md") is False


# ---------------------------------------------------------------------------
# _handle branch additive: roadmap- still skipped, no depositor call (D1)
# ---------------------------------------------------------------------------

class TestHandleAdditive:
    def test_roadmap_file_still_skipped(self, tmp_path):
        """A roadmap- file is not routed to the depositor — D1 purely additive."""
        import bellows

        decisions_dir = str(tmp_path / "decisions")
        os.makedirs(decisions_dir, exist_ok=True)

        config = {"watched_projects": [decisions_dir], "callback_port": 19999}

        mock_orchestrator = MagicMock()
        mock_orchestrator.config = config
        mock_orchestrator._seen = set()
        mock_orchestrator._shutting_down = False
        mock_orchestrator.depositor = MagicMock()

        handler = bellows.PlanHandler(mock_orchestrator)

        roadmap_path = os.path.join(decisions_dir, "roadmap-2026.md")
        with open(roadmap_path, "w") as f:
            f.write("# Roadmap\n")

        handler._handle(roadmap_path)

        mock_orchestrator.depositor.evaluate.assert_not_called()


# ---------------------------------------------------------------------------
# Positive wiring test: _handle on ready- CALLS depositor.evaluate (DISC-5)
# ---------------------------------------------------------------------------

class TestHandleWiring:
    def test_handle_routes_ready_to_depositor(self, tmp_path):
        """_handle on a ready- file dispatches to depositor.evaluate."""
        import bellows

        decisions_dir = str(tmp_path / "decisions")
        os.makedirs(decisions_dir, exist_ok=True)

        config = {"watched_projects": [decisions_dir], "callback_port": 19999}

        mock_depositor = MagicMock()
        mock_orchestrator = MagicMock()
        mock_orchestrator.config = config
        mock_orchestrator._seen = set()
        mock_orchestrator._shutting_down = False
        mock_orchestrator.depositor = mock_depositor

        handler = bellows.PlanHandler(mock_orchestrator)

        ready_path = os.path.join(decisions_dir, "ready-executable-test.md")
        with open(ready_path, "w") as f:
            f.write("# Test\n")

        handler._handle(ready_path)
        time.sleep(0.3)

        mock_depositor.evaluate.assert_called_once_with(ready_path)


# ---------------------------------------------------------------------------
# Two concurrent evaluate() calls → exactly one clear (W2/R4)
# ---------------------------------------------------------------------------

class TestConcurrentEvaluate:
    @patch("depositor.cycle_check")
    @patch("depositor.subprocess")
    def test_two_concurrent_evals_one_clear(
        self, mock_subprocess, mock_cc, decisions_dir, lifecycle_db, tmp_path
    ):
        mock_cc.run_check.return_value = ("BAR_MET", 0)
        mock_cc.parse_manifest_stanza.return_value = {}
        mock_subprocess.run.return_value = MagicMock(returncode=0, stdout="PASS: all")

        plan_text = _make_plan(writes=["knowledge/research/concurrent.md"])
        path = _stage_plan(decisions_dir, "diagnostic-concurrent", plan_text)
        _write_receipt_for_plan(tmp_path, path)

        dep = _make_depositor(decisions_dir, lifecycle_db)
        # Override dedup window so both threads CAN try
        dep._recent_evals = {}
        original_dedup = depositor._DEDUP_WINDOW
        depositor._DEDUP_WINDOW = 0.0

        results = {"cleared": 0, "errors": []}

        original_clear = dep._clear

        def counting_clear(*args):
            results["cleared"] += 1
            original_clear(*args)

        dep._clear = counting_clear

        t1 = threading.Thread(target=dep.evaluate, args=(path,))
        t2 = threading.Thread(target=dep.evaluate, args=(path,))
        t1.start()
        t2.start()
        t1.join(timeout=10)
        t2.join(timeout=10)

        depositor._DEDUP_WINDOW = original_dedup

        claimable = os.path.join(decisions_dir, "diagnostic-concurrent.md")
        assert results["cleared"] == 1


# ---------------------------------------------------------------------------
# Restart re-eval does NOT release a hold (A2)
# ---------------------------------------------------------------------------

class TestRestartReeval:
    @patch("depositor.cycle_check")
    @patch("depositor.subprocess")
    def test_hold_stays_held_on_restart(
        self, mock_subprocess, mock_cc, decisions_dir, lifecycle_db
    ):
        mock_cc.run_check.return_value = ("BAR_MET", 0)
        mock_cc.parse_manifest_stanza.return_value = {}
        mock_subprocess.run.return_value = MagicMock(returncode=0, stdout="PASS: all")

        plan_text = _make_plan(writes=["bellows/some_code.py"])
        hold_path = os.path.join(decisions_dir, "hold-executable-restart.md")
        with open(hold_path, "w") as f:
            f.write(plan_text)
        hold_json = hold_path.replace(".md", ".hold.json")
        with open(hold_json, "w") as f:
            json.dump({"hold_reason": "class:governed-tooling", "held_at": "2026-08-20T00:00:00"}, f)

        dep = _make_depositor(decisions_dir, lifecycle_db)
        dep.reevaluate_on_startup()

        # hold- file must still exist — never auto-cleared
        assert os.path.exists(hold_path), "hold- file must persist across restart"
        # Must NOT be cleared to claimable
        claimable = os.path.join(decisions_dir, "executable-restart.md")
        assert not os.path.exists(claimable)


# ---------------------------------------------------------------------------
# Path B: legacy extraction weighted (EXEC-2)
# ---------------------------------------------------------------------------

class TestPathB:
    @patch("depositor.cycle_check")
    @patch("depositor.subprocess")
    def test_legacy_deposits_block_extraction(
        self, mock_subprocess, mock_cc, decisions_dir, lifecycle_db, tmp_path
    ):
        """Path B: plans with no manifest stanza use **Deposits:** block."""
        mock_cc.run_check.return_value = ("BAR_MET", 0)
        mock_cc.parse_manifest_stanza.return_value = {}
        mock_subprocess.run.return_value = MagicMock(returncode=0, stdout="PASS: all")

        plan_text = _make_plan(writes=["knowledge/research/legacy-result.md"])
        path = _stage_plan(decisions_dir, "diagnostic-legacy", plan_text)
        _write_receipt_for_plan(tmp_path, path)

        dep = _make_depositor(decisions_dir, lifecycle_db)
        dep.evaluate(path)

        claimable = os.path.join(decisions_dir, "diagnostic-legacy.md")
        assert os.path.exists(claimable), "Path B extraction should work for read-only plans"


# ---------------------------------------------------------------------------
# Dashboard render: DEPOSITS panel
# ---------------------------------------------------------------------------

class TestDashboardDeposits:
    def test_deposits_panel_renders(self):
        deposit_rows = [
            {"file": "hold-executable-476.md", "status": "HOLD",
             "reason": "collision:writes∩writes with #475", "dir": "/tmp"},
            {"file": "ready-diagnostic-479.md", "status": "READY",
             "reason": "", "dir": "/tmp"},
        ]
        output = status.render_depositor_status(deposit_rows)
        assert "DEPOSITS" in output
        assert "hold-executable-476.md" in output
        assert "HOLD" in output
        assert "READY" in output

    def test_deposits_panel_empty(self):
        output = status.render_depositor_status([])
        assert "DEPOSITS" in output
        assert "(none)" in output

    def test_deposits_panel_caps_rows(self):
        rows = [
            {"file": f"hold-executable-{i}.md", "status": "HOLD",
             "reason": f"reason-{i}", "dir": "/tmp"}
            for i in range(15)
        ]
        output = status.render_depositor_status(rows, max_rows=8)
        assert "…(7 more)" in output


# ---------------------------------------------------------------------------
# Disk low → HOLD
# ---------------------------------------------------------------------------

class TestDiskLow:
    @patch("depositor.cycle_check")
    @patch("depositor.subprocess")
    def test_disk_low_holds(self, mock_subprocess, mock_cc, decisions_dir, lifecycle_db, tmp_path):
        mock_cc.run_check.return_value = ("BAR_MET", 0)
        mock_cc.parse_manifest_stanza.return_value = {}
        mock_subprocess.run.return_value = MagicMock(returncode=0, stdout="PASS: all")

        plan_text = _make_plan(writes=["knowledge/research/disk.md"])
        path = _stage_plan(decisions_dir, "diagnostic-disk", plan_text)
        _write_receipt_for_plan(tmp_path, path)

        dep = _make_depositor(decisions_dir, lifecycle_db, disk_ok=False)
        dep.evaluate(path)

        hold_path = os.path.join(decisions_dir, "hold-diagnostic-disk.md")
        assert os.path.exists(hold_path)
        data = json.loads(Path(hold_path.replace(".md", ".hold.json")).read_text())
        assert "disk_low" in data["hold_reason"]


# ---------------------------------------------------------------------------
# Clear deletes stale .hold.json (DISC-6)
# ---------------------------------------------------------------------------

class TestClearDeletesHoldJson:
    @patch("depositor.cycle_check")
    @patch("depositor.subprocess")
    def test_clear_removes_stale_hold_json(
        self, mock_subprocess, mock_cc, decisions_dir, lifecycle_db, tmp_path
    ):
        mock_cc.run_check.return_value = ("BAR_MET", 0)
        mock_cc.parse_manifest_stanza.return_value = {}
        mock_subprocess.run.return_value = MagicMock(returncode=0, stdout="PASS: all")

        hold_json_path = os.path.join(
            decisions_dir, "hold-diagnostic-stale.hold.json"
        )
        with open(hold_json_path, "w") as f:
            json.dump({"hold_reason": "old"}, f)

        plan_text = _make_plan(writes=["knowledge/research/stale.md"])
        path = _stage_plan(decisions_dir, "diagnostic-stale", plan_text)
        _write_receipt_for_plan(tmp_path, path)

        dep = _make_depositor(decisions_dir, lifecycle_db)
        dep.evaluate(path)

        assert not os.path.exists(hold_json_path), "stale .hold.json should be deleted"
