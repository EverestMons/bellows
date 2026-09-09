"""Tests for step_files recording and replay_scope_check tool (plan 100049, thread 209)."""

import os
import sqlite3
import subprocess
import sys

import pytest

import lifecycle

_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOL = os.path.join(_REPO_ROOT, "tools", "replay_scope_check.py")
PYTHON = sys.executable


def _make_db(tmp_path, name="lifecycle.db"):
    db_path = str(tmp_path / name)
    lifecycle.init_lifecycle_db(db_path)
    return db_path


def _mint_step(db_path, step_number=1, placeholder="placeholder.md"):
    plan_id = lifecycle.mint_and_claim(
        "executable", "/proj", "test plan", "bellows", "T0", 1,
        placeholder, db_path=db_path,
    )
    step_id = lifecycle.record_step_start(plan_id, step_number, db_path=db_path)
    return plan_id, step_id


def _insert_step_files(db_path, step_id, paths):
    conn = sqlite3.connect(db_path)
    conn.execute("DELETE FROM step_files WHERE step_id = ?", (step_id,))
    conn.executemany(
        "INSERT OR IGNORE INTO step_files (step_id, path) VALUES (?, ?)",
        [(step_id, p) for p in paths],
    )
    conn.commit()
    conn.close()


def _insert_gate_event(db_path, step_id, gate_name, result):
    conn = sqlite3.connect(db_path)
    conn.execute(
        "INSERT INTO gate_events (step_id, gate_name, result, reason_code, overridden, override_ref)"
        " VALUES (?, ?, ?, NULL, 0, NULL)",
        (step_id, gate_name, result),
    )
    conn.commit()
    conn.close()


def _set_plan_doc_ref(db_path, plan_id, ref):
    conn = sqlite3.connect(db_path)
    conn.execute("UPDATE plans SET plan_doc_ref = ? WHERE id = ?", (ref, plan_id))
    conn.commit()
    conn.close()


# ── Test 1 ──────────────────────────────────────────────────────────────────

def test_1_init_twice_table_exists_row_survives(tmp_path):
    db_path = _make_db(tmp_path)
    plan_id = lifecycle.mint_and_claim(
        "executable", "/proj", "Survivor", "bellows", "T0", 1, "ph.md", db_path=db_path,
    )
    lifecycle.init_lifecycle_db(db_path)
    conn = sqlite3.connect(db_path)
    cols = conn.execute("PRAGMA table_info(step_files)").fetchall()
    assert cols, "step_files table missing after second init"
    col_names = {c[1] for c in cols}
    assert {"id", "step_id", "path"}.issubset(col_names)
    row = conn.execute("SELECT title FROM plans WHERE id = ?", (plan_id,)).fetchone()
    assert row is not None and row[0] == "Survivor"
    conn.close()


# ── Test 2 ──────────────────────────────────────────────────────────────────

def test_2_files_recorded_with_gate_rows(tmp_path):
    db_path = _make_db(tmp_path)

    # Case A: passed=True, two files → two step_files rows + ten PASS rows
    plan_id_a, step_id_a = _mint_step(db_path, placeholder="ph-a.md")
    lifecycle.record_gate_events(
        step_id_a,
        {"passed": True, "failures": [], "files_changed": ["a.py", "b/c.md"]},
        db_path=db_path,
    )
    conn = sqlite3.connect(db_path)
    paths_a = {r[0] for r in conn.execute(
        "SELECT path FROM step_files WHERE step_id = ?", (step_id_a,)
    ).fetchall()}
    pass_count_a = conn.execute(
        "SELECT COUNT(*) FROM gate_events WHERE step_id = ? AND result = 'pass'",
        (step_id_a,),
    ).fetchone()[0]
    conn.close()
    assert paths_a == {"a.py", "b/c.md"}, f"case A paths: {paths_a}"
    assert pass_count_a == 10, f"case A pass rows: {pass_count_a}"

    # Case B: one FAIL, same files → two step_files rows + one FAIL row
    plan_id_b, step_id_b = _mint_step(db_path, step_number=1, placeholder="ph-b.md")
    lifecycle.record_gate_events(
        step_id_b,
        {
            "passed": False,
            "failures": [{"gate": "scope_check", "evidence": "out of scope: x.py"}],
            "files_changed": ["a.py", "b/c.md"],
        },
        db_path=db_path,
    )
    conn = sqlite3.connect(db_path)
    paths_b = {r[0] for r in conn.execute(
        "SELECT path FROM step_files WHERE step_id = ?", (step_id_b,)
    ).fetchall()}
    fail_count_b = conn.execute(
        "SELECT COUNT(*) FROM gate_events WHERE step_id = ? AND result = 'fail'",
        (step_id_b,),
    ).fetchone()[0]
    conn.close()
    assert paths_b == {"a.py", "b/c.md"}, f"case B paths: {paths_b}"
    assert fail_count_b == 1, f"case B fail rows: {fail_count_b}"


# ── Test 3 ──────────────────────────────────────────────────────────────────

def test_3_empty_files_no_rows_no_exception(tmp_path):
    db_path = _make_db(tmp_path)

    # Empty list
    _, step_id_empty = _mint_step(db_path, placeholder="ph-empty.md")
    lifecycle.record_gate_events(
        step_id_empty, {"passed": True, "failures": [], "files_changed": []}, db_path=db_path,
    )
    conn = sqlite3.connect(db_path)
    assert conn.execute(
        "SELECT COUNT(*) FROM step_files WHERE step_id = ?", (step_id_empty,)
    ).fetchone()[0] == 0

    # Missing key
    plan_id_b = lifecycle.mint_and_claim(
        "executable", "/proj", "t2", "bellows", "T0", 1, "ph-missing.md", db_path=db_path,
    )
    step_id_missing = lifecycle.record_step_start(plan_id_b, 1, db_path=db_path)
    conn.close()

    lifecycle.record_gate_events(
        step_id_missing, {"passed": True, "failures": []}, db_path=db_path,
    )
    conn = sqlite3.connect(db_path)
    assert conn.execute(
        "SELECT COUNT(*) FROM step_files WHERE step_id = ?", (step_id_missing,)
    ).fetchone()[0] == 0
    conn.close()


# ── Test 4 ──────────────────────────────────────────────────────────────────

def test_4_replace_on_re_evaluation(tmp_path):
    db_path = _make_db(tmp_path)
    _, step_id = _mint_step(db_path)
    lifecycle.record_gate_events(
        step_id,
        {"passed": True, "failures": [], "files_changed": ["a.py", "b/c.md"]},
        db_path=db_path,
    )
    lifecycle.record_gate_events(
        step_id,
        {"passed": True, "failures": [], "files_changed": ["a.py"]},
        db_path=db_path,
    )
    conn = sqlite3.connect(db_path)
    paths = {r[0] for r in conn.execute(
        "SELECT path FROM step_files WHERE step_id = ?", (step_id,)
    ).fetchall()}
    count = conn.execute(
        "SELECT COUNT(*) FROM step_files WHERE step_id = ?", (step_id,)
    ).fetchone()[0]
    conn.close()
    assert count == 1, f"expected 1 row after replace, got {count}"
    assert paths == {"a.py"}, f"expected {{a.py}}, got {paths}"


# ── Test 5 ──────────────────────────────────────────────────────────────────

_PLAN_FLIP = """\
# flip plan

## Cycle Manifest
tier: T1
target: lifecycle.py

---

## STEP 1 — DEV

> **Scope:**
> - a.py
"""

_PLAN_SAME = """\
# same plan

## Cycle Manifest
tier: T1
target: lifecycle.py

---

## STEP 1 — DEV

> **Scope:**
> - c.py
"""


def test_5_tool_flip_and_read_only(tmp_path):
    db_path = _make_db(tmp_path)

    # Plan 1: FLIP — files a.py+b.py, scope only a.py → recorded=pass, now=fail
    flip_plan_file = tmp_path / "flip_plan.md"
    flip_plan_file.write_text(_PLAN_FLIP)
    flip_id = lifecycle.mint_and_claim(
        "executable", "/proj", "flip", "bellows", "T0", 1, "flip-ph.md", db_path=db_path,
    )
    _set_plan_doc_ref(db_path, flip_id, str(flip_plan_file))
    flip_step_id = lifecycle.record_step_start(flip_id, 1, db_path=db_path)
    _insert_step_files(db_path, flip_step_id, ["a.py", "b.py"])
    _insert_gate_event(db_path, flip_step_id, "scope_check", "pass")

    # Plan 2: SAME — files c.py, scope c.py → recorded=pass, now=pass
    same_plan_file = tmp_path / "same_plan.md"
    same_plan_file.write_text(_PLAN_SAME)
    same_id = lifecycle.mint_and_claim(
        "executable", "/proj", "same", "bellows", "T0", 1, "same-ph.md", db_path=db_path,
    )
    _set_plan_doc_ref(db_path, same_id, str(same_plan_file))
    same_step_id = lifecycle.record_step_start(same_id, 1, db_path=db_path)
    _insert_step_files(db_path, same_step_id, ["c.py"])
    _insert_gate_event(db_path, same_step_id, "scope_check", "pass")

    mtime_before = os.stat(db_path).st_mtime
    conn = sqlite3.connect(db_path)
    counts_before = {
        tname: conn.execute(f"SELECT COUNT(*) FROM [{tname}]").fetchone()[0]
        for (tname,) in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
    }
    conn.close()

    result = subprocess.run(
        [PYTHON, TOOL, db_path, "--plan-root", str(tmp_path)],
        capture_output=True, text=True,
    )
    out = result.stdout

    assert f"{flip_id}/1" in out, f"flip step line missing: {out}"
    assert f"{same_id}/1" in out, f"same step line missing: {out}"
    assert "FLIPS: 1" in out, f"expected FLIPS: 1 in: {out}"
    assert str(flip_id) in out.split("FLIPS:")[1], f"flip id not in FLIPS section: {out}"

    mtime_after = os.stat(db_path).st_mtime
    assert mtime_before == mtime_after, "db mtime changed — tool wrote to db"

    conn = sqlite3.connect(db_path)
    counts_after = {
        tname: conn.execute(f"SELECT COUNT(*) FROM [{tname}]").fetchone()[0]
        for (tname,) in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
    }
    conn.close()
    assert counts_before == counts_after, f"table counts changed: {counts_before} → {counts_after}"


# ── Test 6 ──────────────────────────────────────────────────────────────────

def test_6_step_files_failure_no_raise_gate_rows_present(tmp_path, monkeypatch):
    db_path = _make_db(tmp_path)
    _, step_id = _mint_step(db_path)

    real_connect = sqlite3.connect

    class _FaultyConn:
        def __init__(self, real):
            self._real = real

        def execute(self, sql, *args):
            if "step_files" in sql.lower():
                raise RuntimeError("injected step_files failure")
            return self._real.execute(sql, *args)

        def executemany(self, sql, *args):
            if "step_files" in sql.lower():
                raise RuntimeError("injected step_files failure")
            return self._real.executemany(sql, *args)

        def commit(self):
            return self._real.commit()

        def close(self):
            return self._real.close()

    def fake_connect(path, **kwargs):
        return _FaultyConn(real_connect(path, **kwargs))

    warned = []
    monkeypatch.setattr(sqlite3, "connect", fake_connect)
    monkeypatch.setattr(lifecycle, "_warn", lambda msg: warned.append(msg))

    lifecycle.record_gate_events(
        step_id,
        {"passed": True, "failures": [], "files_changed": ["a.py"]},
        db_path=db_path,
    )

    assert warned, "expected _warn to be called on step_files failure"

    conn = real_connect(db_path)
    gate_count = conn.execute(
        "SELECT COUNT(*) FROM gate_events WHERE step_id = ?", (step_id,)
    ).fetchone()[0]
    step_files_count = conn.execute(
        "SELECT COUNT(*) FROM step_files WHERE step_id = ?", (step_id,)
    ).fetchone()[0]
    conn.close()
    assert gate_count == 10, f"gate rows missing after step_files failure: {gate_count}"
    assert step_files_count == 0, f"step_files rows present after failure: {step_files_count}"


# ── Test 7 ──────────────────────────────────────────────────────────────────

def test_7_tool_no_plan_text_not_found(tmp_path):
    db_path = _make_db(tmp_path)
    plan_id = lifecycle.mint_and_claim(
        "executable", "/proj", "orphan", "bellows", "T0", 1, "orphan-ph.md", db_path=db_path,
    )
    step_id = lifecycle.record_step_start(plan_id, 1, db_path=db_path)
    _insert_step_files(db_path, step_id, ["x.py"])
    _insert_gate_event(db_path, step_id, "scope_check", "pass")

    result = subprocess.run(
        [PYTHON, TOOL, db_path, "--plan-root", str(tmp_path)],
        capture_output=True, text=True,
    )
    assert "plan text not found" in result.stdout, result.stdout
    assert "FLIPS: 0" in result.stdout, result.stdout
    assert result.returncode == 0


# ── Test 8 ──────────────────────────────────────────────────────────────────

def test_8_tool_table_absent(tmp_path):
    db_path = str(tmp_path / "old.db")
    conn = sqlite3.connect(db_path)
    conn.execute("CREATE TABLE plans (id INTEGER PRIMARY KEY)")
    conn.execute("CREATE TABLE steps (id INTEGER PRIMARY KEY)")
    conn.commit()
    conn.close()

    result = subprocess.run(
        [PYTHON, TOOL, db_path],
        capture_output=True, text=True,
    )
    assert "table absent" in result.stdout, result.stdout
    assert result.returncode == 0
