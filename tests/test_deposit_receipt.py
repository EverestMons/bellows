"""Tests for tools/deposit_receipt.py — receipt writer tool."""
import hashlib
import json
import os
import sys
from pathlib import Path

import pytest

TOOLS_DIR = Path(__file__).resolve().parent.parent / "tools"
sys.path.insert(0, str(TOOLS_DIR.parent))


@pytest.fixture(autouse=True)
def _patch_bellows_root(monkeypatch, tmp_path):
    """Redirect the receipt tool's root resolution to tmp_path."""
    import tools.deposit_receipt as dr
    monkeypatch.setattr(dr, "_BELLOWS_ROOT", str(tmp_path))
    monkeypatch.setattr(dr, "_RECEIPTS_DIR", str(tmp_path / "receipts"))
    yield


def _write_plan(tmp_path, name="ready-executable-foo.md", content=b"# test plan\n"):
    plan = tmp_path / name
    plan.write_bytes(content)
    return str(plan)


class TestWriteReceipt:
    def test_round_trip(self, tmp_path):
        import tools.deposit_receipt as dr
        plan_path = _write_plan(tmp_path)
        content = Path(plan_path).read_bytes()
        expected_hash = hashlib.sha256(content).hexdigest()

        result = dr.write_receipt(plan_path, "test-session-1")
        assert result is True

        receipts_dir = tmp_path / "receipts"
        files = list(receipts_dir.glob("receipt-*.json"))
        assert len(files) == 1

        data = json.loads(files[0].read_text())
        assert data["slug"] == "executable-foo"
        assert data["content_hash"] == expected_hash
        assert data["session_id"] == "test-session-1"
        assert data["armed_at"]
        assert data["watcher"] == "gate-watcher armed in depositing session"
        assert "ARMED" in data["attestation_boundary"]
        assert "alive" not in data["watcher"].lower()

        assert expected_hash[:12] in files[0].name

    def test_refusal_missing_plan(self, tmp_path):
        import tools.deposit_receipt as dr
        result = dr.write_receipt("/nonexistent/plan.md", "session-1")
        assert result is False

    def test_refusal_invalid_session_id(self, tmp_path):
        import tools.deposit_receipt as dr
        plan_path = _write_plan(tmp_path)
        assert dr.write_receipt(plan_path, "") is False
        assert dr.write_receipt(plan_path, None) is False
        assert dr.write_receipt(plan_path, "bad id with spaces") is False
        assert dr.write_receipt(plan_path, "has@special") is False

    def test_refusal_missing_session_id(self, tmp_path):
        import tools.deposit_receipt as dr
        plan_path = _write_plan(tmp_path)
        assert dr.write_receipt(plan_path, None) is False

    def test_refusal_duplicate_slug_hash(self, tmp_path):
        import tools.deposit_receipt as dr
        plan_path = _write_plan(tmp_path)

        assert dr.write_receipt(plan_path, "session-1") is True
        assert dr.write_receipt(plan_path, "session-2") is False

    def test_new_hash_new_receipt(self, tmp_path):
        import tools.deposit_receipt as dr
        plan_path = _write_plan(tmp_path, content=b"version 1\n")
        assert dr.write_receipt(plan_path, "session-1") is True

        Path(plan_path).write_bytes(b"version 2\n")
        assert dr.write_receipt(plan_path, "session-1") is True

        receipts_dir = tmp_path / "receipts"
        files = list(receipts_dir.glob("receipt-*.json"))
        assert len(files) == 2

    def test_receipts_dir_auto_created(self, tmp_path):
        import tools.deposit_receipt as dr
        receipts = tmp_path / "receipts"
        assert not receipts.exists()
        plan_path = _write_plan(tmp_path)
        dr.write_receipt(plan_path, "session-1")
        assert receipts.is_dir()

    def test_slug_strips_ready_prefix(self, tmp_path):
        import tools.deposit_receipt as dr
        plan_path = _write_plan(tmp_path, name="ready-my-plan.md")
        dr.write_receipt(plan_path, "session-1")
        files = list((tmp_path / "receipts").glob("receipt-*.json"))
        data = json.loads(files[0].read_text())
        assert data["slug"] == "my-plan"

    def test_slug_no_ready_prefix(self, tmp_path):
        import tools.deposit_receipt as dr
        plan_path = _write_plan(tmp_path, name="executable-bar.md")
        dr.write_receipt(plan_path, "session-1")
        files = list((tmp_path / "receipts").glob("receipt-*.json"))
        data = json.loads(files[0].read_text())
        assert data["slug"] == "executable-bar"

    def test_draft_path_outside_watched_dir(self, tmp_path, capsys):
        import tools.deposit_receipt as dr
        cfg = tmp_path / "config.json"
        cfg.write_text(json.dumps({"watched_projects": [str(tmp_path / "decisions")]}))
        monkeypatch_root = str(tmp_path)
        dr._BELLOWS_ROOT = monkeypatch_root

        draft_dir = tmp_path / "drafts"
        draft_dir.mkdir()
        plan_path = _write_plan(draft_dir, name="executable-test.md")
        result = dr.write_receipt(plan_path, "session-1")
        assert result is True

        captured = capsys.readouterr()
        assert "outside watched project trees" in captured.out

    def test_duplicate_check_excludes_archived(self, tmp_path):
        import tools.deposit_receipt as dr
        plan_path = _write_plan(tmp_path, content=b"plan content\n")
        content_hash = hashlib.sha256(b"plan content\n").hexdigest()

        archived = tmp_path / "receipts" / "archived"
        archived.mkdir(parents=True)
        archived_receipt = archived / f"receipt-executable-foo-old-session-{content_hash[:12]}.json"
        archived_receipt.write_text(json.dumps({
            "slug": "executable-foo",
            "content_hash": content_hash,
            "session_id": "old-session",
            "armed_at": "2026-01-01T00:00:00",
        }))

        result = dr.write_receipt(plan_path, "new-session")
        assert result is True
