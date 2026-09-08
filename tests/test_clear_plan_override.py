"""Thread 123 — `--override-gate --ref` validates the ref and can correct an override."""
import os, sqlite3, sys
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "tools"))
import lifecycle  # noqa: E402
import clear_plan  # noqa: E402


def _db_with_failed_gate(tmp_path, plan_id=7, step=1, gate="rule_22_verification"):
    db = tmp_path / "lifecycle.db"; lifecycle.init_lifecycle_db(str(db))
    c = sqlite3.connect(str(db))
    c.execute("INSERT INTO plans (id, type, target_project, created_at) VALUES (?, 'executable', 'bellows', '2026-09-08T00:00:00')", (plan_id,))
    c.execute("INSERT INTO steps (id, plan_id, step_number) VALUES (1, ?, ?)", (plan_id, step))
    c.execute("INSERT INTO gate_events (step_id, gate_name, result, overridden) VALUES (1, ?, 'fail', 0)", (gate,))
    c.commit(); c.close(); return db


def _rows(db):
    c = sqlite3.connect(str(db)); r = c.execute("SELECT overridden, override_ref FROM gate_events").fetchall(); c.close(); return r


def test_ref_must_exist(tmp_path):
    db = _db_with_failed_gate(tmp_path)
    assert clear_plan.override_gate("7", 1, "rule_22_verification", str(tmp_path / "missing.md"), db_path=str(db)) is False
    assert _rows(db) == [(0, None)]


def test_ref_under_a_temp_dir_is_refused(tmp_path, monkeypatch):
    db = _db_with_failed_gate(tmp_path)
    scratch = Path("/private/tmp") / f"override-ref-test-{os.getpid()}.md"; scratch.write_text("why\n")
    try:
        assert clear_plan.override_gate("7", 1, "rule_22_verification", str(scratch), db_path=str(db)) is False
    finally:
        scratch.unlink()
    assert _rows(db) == [(0, None)]


def test_durable_ref_overrides_then_a_second_ref_corrects(tmp_path, monkeypatch, capsys):
    db = _db_with_failed_gate(tmp_path)
    durable = ROOT / "receipts" / f"_test-override-ref-{os.getpid()}.md"; durable.write_text("justification\n")
    durable2 = ROOT / "receipts" / f"_test-override-ref2-{os.getpid()}.md"; durable2.write_text("better justification\n")
    try:
        assert clear_plan.override_gate("7", 1, "rule_22_verification", str(durable), db_path=str(db))
        assert _rows(db) == [(1, str(durable))]
        # write-once used to refuse here; now the pointer is corrected and the act is printed
        assert clear_plan.override_gate("7", 1, "rule_22_verification", str(durable2), db_path=str(db))
        assert _rows(db) == [(1, str(durable2))]
        assert "CORRECTED" in capsys.readouterr().out
    finally:
        durable.unlink(); durable2.unlink()


def test_nothing_to_override_or_correct_fails(tmp_path):
    db = _db_with_failed_gate(tmp_path)
    durable = ROOT / "receipts" / f"_test-override-ref3-{os.getpid()}.md"; durable.write_text("x\n")
    try:
        assert clear_plan.override_gate("7", 1, "scope_check", str(durable), db_path=str(db)) is False  # a gate with no fail row
    finally:
        durable.unlink()
