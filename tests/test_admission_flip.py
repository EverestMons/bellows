"""Tests for the admission flip (Steps 1+2 / DEV-A + DEV-B).

All tests use tmp dirs and tmp DBs — no real watched path is ever named.
"""

import hashlib
import json
import os
import sqlite3
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

_BELLOWS_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_BELLOWS_ROOT, "scripts"))
sys.path.insert(0, os.path.join(_BELLOWS_ROOT, "tools"))

import bellows
import depositor
import lifecycle
from lifecycle import init_lifecycle_db
from clear_plan import clear_plan


@pytest.fixture(autouse=True)
def _isolate_receipts(monkeypatch, tmp_path):
    """Isolation: every depositor test scans a tmp receipts dir, never the live one."""
    isolated_root = tmp_path / "bellows_root"
    isolated_root.mkdir(exist_ok=True)
    (isolated_root / "receipts").mkdir(exist_ok=True)
    monkeypatch.setattr(depositor, "resolve_bellows_root", lambda: isolated_root)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def tmp_db(tmp_path):
    db_path = str(tmp_path / "lifecycle.db")
    init_lifecycle_db(db_path)
    return db_path


@pytest.fixture
def decisions_dir(tmp_path):
    d = tmp_path / "proj" / "knowledge" / "decisions"
    d.mkdir(parents=True)
    return str(d)


def _make_depositor(decisions_dir, db_path, disk_ok=True):
    return depositor.Depositor(
        disk_preflight_fn=lambda cfg: disk_ok,
        shutting_down_check=lambda: False,
        config={"watched_projects": [decisions_dir]},
        lifecycle_db_path=db_path,
    )


# ---------------------------------------------------------------------------
# Clearance round-trip
# ---------------------------------------------------------------------------

class TestClearanceRoundTrip:
    def test_write_then_has(self, tmp_db):
        lifecycle.write_clearance(
            "executable-100.md", "abc123hash", "read-only", "depositor",
            tmp_db,
        )
        assert lifecycle.has_clearance("abc123hash", "executable-100.md", tmp_db)

    def test_same_hash_idempotent(self, tmp_db):
        lifecycle.write_clearance(
            "executable-100.md", "abc123hash", "read-only", "depositor",
            tmp_db,
        )
        lifecycle.write_clearance(
            "executable-100.md", "abc123hash", "read-only", "depositor",
            tmp_db,
        )
        conn = sqlite3.connect(tmp_db)
        count = conn.execute(
            "SELECT count(*) FROM clearances WHERE content_hash = ?",
            ("abc123hash",),
        ).fetchone()[0]
        conn.close()
        assert count == 1

    def test_path_mismatch_refuses(self, tmp_db):
        lifecycle.write_clearance(
            "executable-100.md", "abc123hash", "read-only", "depositor",
            tmp_db,
        )
        assert not lifecycle.has_clearance(
            "abc123hash", "executable-999.md", tmp_db
        )

    def test_consumed_refuses(self, tmp_db):
        lifecycle.write_clearance(
            "executable-100.md", "abc123hash", "read-only", "depositor",
            tmp_db,
        )
        lifecycle.consume_clearance("abc123hash", "executable-100.md", tmp_db)
        assert not lifecycle.has_clearance(
            "abc123hash", "executable-100.md", tmp_db
        )


# ---------------------------------------------------------------------------
# Correction-25 end-to-end: _clear() → has_clearance on claimable path
# ---------------------------------------------------------------------------

class TestClearEndToEnd:
    @patch("depositor.cycle_check")
    @patch("depositor.subprocess")
    def test_clear_writes_clearance_for_claimable_path(
        self, mock_subprocess, mock_cc, decisions_dir, tmp_db
    ):
        mock_cc.run_check.return_value = ("BAR_MET", 0)
        mock_cc.parse_manifest_stanza.return_value = {}
        mock_subprocess.run.return_value = MagicMock(returncode=0, stdout="PASS: all")

        plan_content = (
            "# Test Plan\n"
            "**Date:** 2026-08-20 | **Tier:** Small | **Dispatch Mode:** bellows\n"
            "**pause_for_verdict:** after_qa_step\n\n"
            "## Drafting Cycle\n"
            "**Tier:** T0\n"
            "**Walk 0 (context pin):**\n"
            "**Walk 1 STATUS:** instruction 0 / record 0 — **§2 BAR MET.**\n"
            "**Closing:** 1 warm walk (bar met w1).\n"
            "**cycle_check:** w1 `BAR_MET`.\n\n---\n\n"
            "## STEP 1 — DEV\n\n"
            "**Deposits:**\n"
            "- `knowledge/research/e2e-test.md`\n\n"
            "End with an Output Receipt.\n"
        )
        ready_name = "ready-diagnostic-e2e.md"
        ready_path = os.path.join(decisions_dir, ready_name)
        Path(ready_path).write_bytes(plan_content.encode("utf-8"))

        dep = _make_depositor(decisions_dir, tmp_db)
        dep._clear(ready_path, "read-only")

        claimable_name = "diagnostic-e2e.md"
        claimable_path = os.path.join(decisions_dir, claimable_name)
        assert os.path.exists(claimable_path)
        assert not os.path.exists(ready_path)

        raw_bytes = Path(claimable_path).read_bytes()
        content_hash = hashlib.sha256(raw_bytes).hexdigest()
        assert lifecycle.has_clearance(content_hash, claimable_name, tmp_db)


# ---------------------------------------------------------------------------
# Correction-19: raw bytes hash vs text-mode hash diverge on CRLF
# ---------------------------------------------------------------------------

class TestRawBytesHash:
    def test_crlf_hash_divergence(self, tmp_path, tmp_db):
        crlf_content = b"line one\r\nline two\r\n"
        plan_file = tmp_path / "test-crlf.md"
        plan_file.write_bytes(crlf_content)

        raw_hash = hashlib.sha256(plan_file.read_bytes()).hexdigest()
        text_hash = hashlib.sha256(
            plan_file.read_text(encoding="utf-8").encode("utf-8")
        ).hexdigest()

        assert raw_hash != text_hash, (
            "raw bytes and text-mode hashes must diverge on CRLF — "
            "the clearance system uses raw bytes (correction 19)"
        )

        lifecycle.write_clearance(
            "test-crlf.md", raw_hash, "read-only", "depositor", tmp_db,
        )
        assert lifecycle.has_clearance(raw_hash, "test-crlf.md", tmp_db)
        assert not lifecycle.has_clearance(text_hash, "test-crlf.md", tmp_db)


# ---------------------------------------------------------------------------
# Class matrix — the design's 20 rows with project identity
# ---------------------------------------------------------------------------

_CLASS_MATRIX = [
    pytest.param(
        ["ELUVIAN_PATH.md", "~/.claude/commands/eluvian.md",
         "bellows/hooks/eluvian/eluvian_align_hook.py"],
        "governance", "shop-infra", id="510-governance-root+cross-project"
    ),
    pytest.param(
        ["knowledge/research/eluvian-path-audit-2026-08-24.md"],
        "governance", "read-only", id="509-governance-research"
    ),
    pytest.param(
        ["knowledge/research/eluvian-path-audit-2026-08-24.md",
         "knowledge/research/eluvian-path-draft-2026-08-24.md"],
        "governance", "read-only", id="508-governance-research-pair"
    ),
    pytest.param(
        ["knowledge/research/bare-entry-ruling-2026-08-23.tsv"],
        "lessons-forge", "read-only", id="507-lf-research"
    ),
    pytest.param(
        ["knowledge/research/bare-entry-ruling-2026-08-23.md",
         "knowledge/research/bare-entry-ruling-2026-08-23.tsv"],
        "lessons-forge", "read-only", id="506-lf-research-pair"
    ),
    pytest.param(
        ["LESSONS.md", "knowledge/tools/apply_annotation.py",
         "knowledge/research/annotation-fix.md"],
        "governance", "shop-infra", id="505-governance-root+tools"
    ),
    pytest.param(
        ["knowledge/research/promotion-corrected-2026-08-23.md",
         "knowledge/research/promotion-corrected-2026-08-23.tsv"],
        "lessons-forge", "read-only", id="504-lf-research"
    ),
    pytest.param(
        ["knowledge/research/learned-promotion-2026-08-23.md",
         "knowledge/research/learned-promotion-2026-08-23.tsv"],
        "lessons-forge", "read-only", id="503-lf-research"
    ),
    pytest.param(
        ["LESSONS.md", "knowledge/tools/apply_annotation.py",
         "knowledge/research/annotation-fix.md"],
        "governance", "shop-infra", id="502-governance-root+tools"
    ),
    pytest.param(
        ["knowledge/research/annotation-detector-2026-08-22.md",
         "knowledge/research/annotation-detector-2026-08-22.tsv",
         "scripts/detect_learned.py"],
        "lessons-forge", "shop-infra", id="501-lf-research+script"
    ),
    pytest.param(
        ["src/lessons_forge.py", "src/test_lessons_forge.py"],
        "lessons-forge", "shop-infra", id="500-lf-src-correction22"
    ),
    pytest.param(
        ["src/lessons_forge.py", "src/test_lessons_forge.py"],
        "lessons-forge", "shop-infra", id="499-lf-src-correction22"
    ),
    pytest.param(
        ["knowledge/research/lessons-reconcile-learned-2026-08-21.md"],
        "lessons-forge", "read-only", id="498-lf-research"
    ),
    pytest.param(
        ["hooks/eluvian/wrap_stop_hook.py", "hooks/eluvian/wrap_arm_hook.py",
         "tests/test_wrap_sentinel.py"],
        "bellows", "shop-infra", id="497-bellows-hooks+tests"
    ),
    pytest.param(
        ["hooks/eluvian/foo.py", "hooks/commands/wrap.md",
         "hooks/settings-hooks-snapshot.json", "hooks/README.md",
         "knowledge/qa/qa-result.md"],
        "bellows", "shop-infra", id="496-bellows-hooks+qa"
    ),
    pytest.param(
        ["knowledge/research/wrap-hook-daemon-exemption-2026-08-21.md"],
        "bellows", "read-only", id="495-bellows-research"
    ),
    pytest.param(
        ["web/reporting.py", "web/templates/report.html",
         "tests/test_reporting.py"],
        "invoice-pulse", "app-feature", id="494-ip-web+tests"
    ),
    pytest.param(
        ["scripts/reconcile_dispute_outcomes.py", "tests/test_reconcile.py"],
        "invoice-pulse", "app-feature", id="493-ip-scripts+tests"
    ),
    pytest.param(
        ["scripts/plan_lint.py", "tests/test_plan_lint.py"],
        "bellows", "shop-infra", id="492-bellows-scripts+tests"
    ),
]


class TestClassMatrix:
    @pytest.mark.parametrize("writes,project,expected", _CLASS_MATRIX)
    def test_20_row_matrix(self, writes, project, expected, tmp_path):
        d = tmp_path / project / "knowledge" / "decisions"
        d.mkdir(parents=True)
        db = str(tmp_path / "lifecycle.db")
        init_lifecycle_db(db)
        dep = _make_depositor(str(d), db)
        project_root = str(tmp_path / project)
        assert dep._assign_class(writes, project_root) == expected


# ---------------------------------------------------------------------------
# Adversarial rows (correction 13)
# ---------------------------------------------------------------------------

class TestClassAdversarial:
    def _dep(self, tmp_path):
        d = tmp_path / "p" / "knowledge" / "decisions"
        d.mkdir(parents=True)
        db = str(tmp_path / "lifecycle.db")
        init_lifecycle_db(db)
        return _make_depositor(str(d), db)

    def test_shop_infra_knowledge_exempt_is_readonly(self, tmp_path):
        dep = self._dep(tmp_path)
        assert dep._assign_class(
            ["bellows/knowledge/research/bar.md"]
        ) == "read-only"

    def test_mixed_infra_and_app_is_shop_infra(self, tmp_path):
        dep = self._dep(tmp_path)
        assert dep._assign_class(
            ["bellows/runner.py", "src/app.py"]
        ) == "shop-infra"

    def test_register_plus_infra_is_shop_infra(self, tmp_path):
        dep = self._dep(tmp_path)
        assert dep._assign_class(
            ["knowledge/decisions/register-cycles.md", "bellows/depositor.py"]
        ) == "shop-infra"

    def test_governance_root_file_is_shop_infra(self, tmp_path):
        dep = self._dep(tmp_path)
        assert dep._assign_class(["ELUVIAN_PATH.md"]) == "shop-infra"
        assert dep._assign_class(["LESSONS.md"]) == "shop-infra"

    def test_knowledge_subdir_not_research_in_infra_project(self, tmp_path):
        d = tmp_path / "bellows" / "knowledge" / "decisions"
        d.mkdir(parents=True)
        db = str(tmp_path / "lifecycle.db")
        init_lifecycle_db(db)
        dep = _make_depositor(str(d), db)
        assert dep._assign_class(
            ["knowledge/qa/result.md"],
            str(tmp_path / "bellows"),
        ) == "app-feature"
        assert dep._assign_class(
            ["knowledge/qa/result.md", "hooks/foo.py"],
            str(tmp_path / "bellows"),
        ) == "shop-infra"


# ---------------------------------------------------------------------------
# Correction 12: out-of-tree-only → None (HOLD via caller)
# ---------------------------------------------------------------------------

class TestOutOfTreeHold:
    def _dep(self, tmp_path):
        d = tmp_path / "p" / "knowledge" / "decisions"
        d.mkdir(parents=True)
        db = str(tmp_path / "lifecycle.db")
        init_lifecycle_db(db)
        return _make_depositor(str(d), db)

    def test_all_external_writes_returns_none(self, tmp_path):
        dep = self._dep(tmp_path)
        result = dep._assign_class(
            ["~/.claude/commands/eluvian.md", "../other/file.py"],
            str(tmp_path / "invoice-pulse"),
        )
        assert result is None

    def test_mixed_external_and_internal_resolves(self, tmp_path):
        dep = self._dep(tmp_path)
        result = dep._assign_class(
            ["~/.claude/commands/eluvian.md", "src/app.py"],
            str(tmp_path / "invoice-pulse"),
        )
        assert result == "app-feature"


# ---------------------------------------------------------------------------
# DDL verification
# ---------------------------------------------------------------------------

class TestClearancesDDL:
    def test_table_exists_after_init(self, tmp_db):
        conn = sqlite3.connect(tmp_db)
        cols = conn.execute("pragma table_info('clearances')").fetchall()
        conn.close()
        col_names = [c[1] for c in cols]
        assert "plan_path" in col_names
        assert "content_hash" in col_names
        assert "assigned_class" in col_names
        assert "cleared_by" in col_names
        assert "cleared_at" in col_names
        assert "consumed_at" in col_names

    def test_partial_unique_index_exists(self, tmp_db):
        conn = sqlite3.connect(tmp_db)
        indexes = conn.execute(
            "SELECT name, sql FROM sqlite_master WHERE type='index' "
            "AND tbl_name='clearances'"
        ).fetchall()
        conn.close()
        idx_names = [i[0] for i in indexes]
        assert "idx_clearances_active" in idx_names
        idx_sql = [i[1] for i in indexes if i[0] == "idx_clearances_active"][0]
        assert "consumed_at IS NULL" in idx_sql


# ===========================================================================
# STEP 2 / DEV-B — Claim path tests
# ===========================================================================


# ---------------------------------------------------------------------------
# Gate truth table: is_claimable
# ---------------------------------------------------------------------------

class TestIsClaimableGate:
    def _write_plan(self, d, name, content=b"# Test plan\n"):
        p = Path(d) / name
        p.write_bytes(content)
        return str(p)

    def test_no_clearance_row(self, tmp_path, tmp_db):
        path = self._write_plan(tmp_path, "executable-gate-1.md")
        assert not bellows.is_claimable(path, tmp_db)

    def test_cleared(self, tmp_path, tmp_db):
        content = b"# Cleared plan\n"
        path = self._write_plan(tmp_path, "executable-gate-2.md", content)
        h = hashlib.sha256(content).hexdigest()
        lifecycle.write_clearance("executable-gate-2.md", h, "read-only",
                                  "depositor", tmp_db)
        assert bellows.is_claimable(path, tmp_db)

    def test_drift(self, tmp_path, tmp_db):
        original = b"# Original content\n"
        h = hashlib.sha256(original).hexdigest()
        lifecycle.write_clearance("executable-gate-3.md", h, "read-only",
                                  "depositor", tmp_db)
        path = self._write_plan(tmp_path, "executable-gate-3.md",
                                b"# Modified content\n")
        assert not bellows.is_claimable(path, tmp_db)

    def test_consumed(self, tmp_path, tmp_db):
        content = b"# Consumed plan\n"
        path = self._write_plan(tmp_path, "executable-gate-4.md", content)
        h = hashlib.sha256(content).hexdigest()
        lifecycle.write_clearance("executable-gate-4.md", h, "read-only",
                                  "depositor", tmp_db)
        lifecycle.consume_clearance(h, "executable-gate-4.md", tmp_db)
        assert not bellows.is_claimable(path, tmp_db)

    def test_unreadable_db_missing(self, tmp_path):
        content = b"# Plan\n"
        path = self._write_plan(tmp_path, "executable-gate-5.md", content)
        missing_db = str(tmp_path / "nonexistent" / "lifecycle.db")
        assert not bellows.is_claimable(path, missing_db)

    def test_unreadable_db_corrupt(self, tmp_path):
        content = b"# Plan\n"
        path = self._write_plan(tmp_path, "executable-gate-6.md", content)
        bad_db = str(tmp_path / "corrupt.db")
        Path(bad_db).write_bytes(b"not a database")
        assert not bellows.is_claimable(path, bad_db)

    def test_unreadable_db_no_clearances_table(self, tmp_path):
        content = b"# Plan\n"
        path = self._write_plan(tmp_path, "executable-gate-7.md", content)
        bare_db = str(tmp_path / "bare.db")
        conn = sqlite3.connect(bare_db)
        conn.execute("CREATE TABLE dummy (id INTEGER)")
        conn.commit()
        conn.close()
        assert not bellows.is_claimable(path, bare_db)


# ---------------------------------------------------------------------------
# Replay pair
# ---------------------------------------------------------------------------

class TestReplayPair:
    def test_other_path_copy_refuses(self, tmp_path, tmp_db):
        content = b"# Same content\n"
        h = hashlib.sha256(content).hexdigest()
        lifecycle.write_clearance("executable-original.md", h, "read-only",
                                  "depositor", tmp_db)
        copy_path = tmp_path / "executable-copy.md"
        copy_path.write_bytes(content)
        assert not bellows.is_claimable(str(copy_path), tmp_db)

    def test_post_consumption_refuses(self, tmp_path, tmp_db):
        content = b"# Consume me\n"
        h = hashlib.sha256(content).hexdigest()
        name = "executable-replay-consume.md"
        plan_path = tmp_path / name
        plan_path.write_bytes(content)
        lifecycle.write_clearance(name, h, "read-only", "depositor", tmp_db)
        lifecycle.consume_clearance(h, name, tmp_db)
        assert not bellows.is_claimable(str(plan_path), tmp_db)

    def test_fresh_reclear_after_transient_death(self, tmp_path, tmp_db):
        content = b"# Transient death recovery\n"
        h = hashlib.sha256(content).hexdigest()
        name = "executable-replay-reclear.md"
        plan_path = tmp_path / name
        plan_path.write_bytes(content)
        lifecycle.write_clearance(name, h, "read-only", "depositor", tmp_db)
        lifecycle.consume_clearance(h, name, tmp_db)
        assert not bellows.is_claimable(str(plan_path), tmp_db)
        lifecycle.write_clearance(name, h, "read-only", "depositor", tmp_db)
        assert bellows.is_claimable(str(plan_path), tmp_db)


# ---------------------------------------------------------------------------
# Auto-HOLD arm
# ---------------------------------------------------------------------------

class TestAutoHoldArm:
    def _make_handler(self, decisions_dir, db_path):
        orch = MagicMock()
        orch.config = {"watched_projects": [decisions_dir]}
        orch._seen = set()
        orch.depositor = MagicMock()
        orch.depositor._db_path = db_path
        handler = bellows.PlanHandler(orch)
        return handler, orch

    def test_one_effective_hold_per_slug(self, tmp_path, tmp_db):
        d = str(tmp_path / "decisions")
        os.makedirs(d)
        plan = Path(d) / "executable-arm-test.md"
        plan.write_bytes(b"# No clearance\n")
        handler, orch = self._make_handler(d, tmp_db)

        handler._handle(str(plan))

        assert os.path.exists(os.path.join(d, "hold-executable-arm-test.md"))
        assert not os.path.exists(str(plan))
        hold_json = os.path.join(d, "hold-executable-arm-test.hold.json")
        assert os.path.exists(hold_json)
        with open(hold_json) as f:
            data = json.load(f)
        assert data["hold_reason"] == "no_clearance"

    def test_repeat_attempt_safe_noop(self, tmp_path, tmp_db):
        d = str(tmp_path / "decisions")
        os.makedirs(d)
        plan = Path(d) / "executable-arm-repeat.md"
        plan.write_bytes(b"# No clearance\n")
        handler, orch = self._make_handler(d, tmp_db)

        handler._handle(str(plan))
        assert os.path.exists(os.path.join(d, "hold-executable-arm-repeat.md"))

        plan.write_bytes(b"# No clearance again\n")
        handler._handle(str(plan))

    def test_never_adds_to_seen(self, tmp_path, tmp_db):
        d = str(tmp_path / "decisions")
        os.makedirs(d)
        plan = Path(d) / "executable-arm-seen.md"
        plan.write_bytes(b"# No clearance\n")
        handler, orch = self._make_handler(d, tmp_db)
        assert len(orch._seen) == 0
        handler._handle(str(plan))
        assert len(orch._seen) == 0

    def test_vanished_source_exception_safe(self, tmp_path, tmp_db):
        d = str(tmp_path / "decisions")
        os.makedirs(d)
        vanished = os.path.join(d, "executable-arm-vanished.md")
        handler, orch = self._make_handler(d, tmp_db)
        handler._handle(vanished)

    def test_mid_claim_skip(self, tmp_path, tmp_db):
        d = str(tmp_path / "decisions")
        os.makedirs(d)
        plan = Path(d) / "executable-arm-midclaim.md"
        plan.write_bytes(b"# No clearance\n")
        handler, orch = self._make_handler(d, tmp_db)
        import verdict as verdict_mod
        slug = verdict_mod.slug_from_path(str(plan))
        orch._seen.add(slug)

        handler._handle(str(plan))
        assert os.path.exists(str(plan)), "plan should NOT be held — slug in _seen"
        assert not os.path.exists(
            os.path.join(d, "hold-executable-arm-midclaim.md")
        )


# ---------------------------------------------------------------------------
# collect_group
# ---------------------------------------------------------------------------

class TestCollectGroup:
    def test_mixed_group_dispatches_claimable_holds_unclearable(
        self, tmp_path, tmp_db
    ):
        d = str(tmp_path / "decisions")
        os.makedirs(d)

        cleared_content = b"# Cleared member\n"
        cleared_hash = hashlib.sha256(cleared_content).hexdigest()
        cleared_name = "parallel-1-executable-cleared.md"
        (Path(d) / cleared_name).write_bytes(cleared_content)
        lifecycle.write_clearance(cleared_name, cleared_hash, "app-feature",
                                  "depositor", tmp_db)

        unclearable_name = "parallel-1-executable-unclearable.md"
        (Path(d) / unclearable_name).write_bytes(b"# No clearance\n")

        orch = MagicMock()
        orch.config = {"watched_projects": [d]}
        orch._seen = set()
        orch.depositor = MagicMock()
        orch.depositor._db_path = tmp_db
        handler = bellows.PlanHandler(orch)

        result = handler.collect_group(d, "parallel-1")

        assert len(result) == 1
        assert os.path.basename(result[0]) == cleared_name
        assert os.path.exists(
            os.path.join(d, "hold-" + unclearable_name)
        )

    def test_full_path_resolves(self, tmp_path, tmp_db):
        d = str(tmp_path / "decisions")
        os.makedirs(d)
        content = b"# Full path test\n"
        h = hashlib.sha256(content).hexdigest()
        name = "parallel-2-executable-fp.md"
        (Path(d) / name).write_bytes(content)
        lifecycle.write_clearance(name, h, "app-feature", "depositor", tmp_db)

        orch = MagicMock()
        orch.config = {"watched_projects": [d]}
        orch._seen = set()
        orch.depositor = MagicMock()
        orch.depositor._db_path = tmp_db
        handler = bellows.PlanHandler(orch)

        result = handler.collect_group(d, "parallel-2")
        assert len(result) == 1
        assert os.path.isabs(result[0])
        assert os.path.exists(result[0])


# ---------------------------------------------------------------------------
# Consumed-at inside mint_and_claim transaction (correction 24)
# ---------------------------------------------------------------------------

class TestConsumeInTransaction:
    def test_mint_and_claim_stamps_consumed_at(self, tmp_db):
        h = "deadbeef" * 8
        name = "executable-consume-tx.md"
        lifecycle.write_clearance(name, h, "app-feature", "depositor", tmp_db)
        assert lifecycle.has_clearance(h, name, tmp_db)

        lifecycle.mint_and_claim(
            plan_type="executable",
            target_project="/tmp/proj",
            title="test",
            dispatch_mode="bellows",
            tier="T0",
            total_steps=1,
            deposit_placeholder_name=name,
            db_path=tmp_db,
            content_hash=h,
            clearance_plan_path=name,
        )
        assert not lifecycle.has_clearance(h, name, tmp_db)


# ---------------------------------------------------------------------------
# Clear tool preconditions + rename target
# ---------------------------------------------------------------------------

class TestClearTool:
    def test_rejects_non_hold(self, tmp_path):
        p = tmp_path / "executable-test.md"
        p.write_bytes(b"# plan\n")
        assert not clear_plan(str(p))

    def test_rejects_missing_sidecar(self, tmp_path):
        p = tmp_path / "hold-executable-test.md"
        p.write_bytes(b"# plan\n")
        assert not clear_plan(str(p))

    def test_rejects_nonexistent(self, tmp_path):
        p = tmp_path / "hold-executable-missing.md"
        assert not clear_plan(str(p))

    def test_rejects_non_md(self, tmp_path):
        p = tmp_path / "hold-executable-test.txt"
        p.write_bytes(b"# plan\n")
        sidecar = tmp_path / "hold-executable-test.hold.json"
        sidecar.write_text('{"hold_reason": "test"}')
        assert not clear_plan(str(p))

    def test_rename_hold_to_ready(self, tmp_path):
        p = tmp_path / "hold-executable-clear-test.md"
        p.write_bytes(b"# plan\n")
        sidecar = tmp_path / "hold-executable-clear-test.hold.json"
        sidecar.write_text('{"hold_reason": "no_clearance"}')

        assert clear_plan(str(p))
        assert not os.path.exists(str(p))
        assert not os.path.exists(str(sidecar))
        assert os.path.exists(
            str(tmp_path / "ready-executable-clear-test.md")
        )
