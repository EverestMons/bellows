"""Tests for the admission flip substrate (Step 1 / DEV-A).

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

sys.path.insert(
    0,
    os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"
    ),
)

import depositor
import lifecycle
from lifecycle import init_lifecycle_db


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
