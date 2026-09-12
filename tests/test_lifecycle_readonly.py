"""Tests for lifecycle.connect_readonly — WAL fallback helper."""

import importlib.util
import os
import sqlite3
import sys

import pytest

import lifecycle  # always the worktree's: bellows.py imports lifecycle before depositor pollutes path

# When the full suite runs, test_bellows.py → bellows.py → depositor.py adds the main repo to
# sys.path and caches the main repo's status.py in sys.modules (before this file is collected).
# Force the worktree's status.py so t1/t5 test the correct code path.
_WORKTREE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_spec = importlib.util.spec_from_file_location("status", os.path.join(_WORKTREE, "status.py"))
_wt_status = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_wt_status)
sys.modules["status"] = _wt_status
import status


class _DeferredRefusal:
    """Stand-in connection whose first execute raises, simulating SQLite 3.43.2's deferred CANTOPEN."""

    def __init__(self, message="unable to open database file"):
        self.message = message
        self.closed = False

    def execute(self, *a, **kw):
        raise sqlite3.OperationalError(self.message)

    def close(self):
        self.closed = True


class TestConnectReadonly:

    # t1 — monkeypatched: mode=ro raises, fallback succeeds; status.query_in_flight returns rows
    def test_fallback_on_file_uri_error(self, tmp_path, monkeypatch):
        db_path = str(tmp_path / "lifecycle.db")
        lifecycle.init_lifecycle_db(db_path)

        real_connect = sqlite3.connect
        calls = []

        def wrapper(*a, **kw):
            calls.append(a[0])
            if isinstance(a[0], str) and a[0].startswith("file:"):
                raise sqlite3.OperationalError("unable to open database file")
            return real_connect(*a, **kw)

        monkeypatch.setattr(sqlite3, "connect", wrapper)

        rows = status.query_in_flight(db_path)
        assert isinstance(rows, list)
        assert len(calls) == 2
        assert calls[0].startswith("file:")
        assert not calls[1].startswith("file:")

        calls.clear()
        conn = lifecycle.connect_readonly(db_path)
        conn.execute("SELECT count(*) FROM plans").fetchone()
        assert os.path.exists(db_path + "-shm")
        conn.close()

    # t1b — live reproduction; skipped when SQLite creates the WAL index for mode=ro
    @pytest.mark.skipif(
        sqlite3.sqlite_version_info >= (3, 44),
        reason="this SQLite creates the WAL index for a read-only reader",
    )
    def test_fallback_live_wal_window(self, tmp_path):
        db_path = str(tmp_path / "lifecycle.db")
        lifecycle.init_lifecycle_db(db_path)
        rows = status.query_in_flight(db_path)
        assert isinstance(rows, list)

    # t2 — real connect with a writer open; mode=ro succeeds; exactly one file: call recorded
    def test_uri_reads_when_writer_open(self, tmp_path, monkeypatch):
        db_path = str(tmp_path / "lifecycle.db")
        lifecycle.init_lifecycle_db(db_path)

        writer = sqlite3.connect(db_path)

        real_connect = sqlite3.connect
        calls = []

        def wrapper(*a, **kw):
            calls.append(a[0])
            return real_connect(*a, **kw)

        monkeypatch.setattr(sqlite3, "connect", wrapper)

        conn = lifecycle.connect_readonly(db_path)
        rows = conn.execute("SELECT count(*) FROM plans").fetchone()
        conn.close()
        writer.close()

        assert rows is not None
        file_calls = [c for c in calls if isinstance(c, str) and c.startswith("file:")]
        assert len(file_calls) == 1

    # t3 — missing file propagates OperationalError unchanged
    def test_missing_file_propagates(self, tmp_path):
        db_path = str(tmp_path / "nonexistent.db")
        with pytest.raises(sqlite3.OperationalError):
            lifecycle.connect_readonly(db_path)

    # t4 — fallback connection refuses INSERT
    def test_fallback_connection_is_readonly(self, tmp_path, monkeypatch):
        db_path = str(tmp_path / "lifecycle.db")
        lifecycle.init_lifecycle_db(db_path)

        real_connect = sqlite3.connect

        def wrapper(*a, **kw):
            if isinstance(a[0], str) and a[0].startswith("file:"):
                raise sqlite3.OperationalError("unable to open database file")
            return real_connect(*a, **kw)

        monkeypatch.setattr(sqlite3, "connect", wrapper)

        conn = lifecycle.connect_readonly(db_path)
        with pytest.raises(sqlite3.OperationalError, match="readonly"):
            conn.execute(
                "INSERT INTO plans (id, type, target_project, title, dispatch_mode, tier,"
                " lifecycle_state, total_steps, created_at)"
                " VALUES (999, 'executable', 'p', 't', 'bellows', 'Small', 'in_progress', 1, 'now')"
            )
        conn.close()

    # t5 — _resolve_in_flight_writes returns a list (not None) under the t1 wrapper
    def test_resolve_in_flight_writes_returns_list(self, tmp_path, monkeypatch):
        db_path = str(tmp_path / "lifecycle.db")
        lifecycle.init_lifecycle_db(db_path)

        real_connect = sqlite3.connect

        def wrapper(*a, **kw):
            if isinstance(a[0], str) and a[0].startswith("file:"):
                raise sqlite3.OperationalError("unable to open database file")
            return real_connect(*a, **kw)

        monkeypatch.setattr(sqlite3, "connect", wrapper)

        import depositor as dep_mod
        dep = dep_mod.Depositor(
            disk_preflight_fn=lambda cfg: True,
            shutting_down_check=lambda: False,
            config={},
            lifecycle_db_path=db_path,
        )
        result = dep._resolve_in_flight_writes()
        assert isinstance(result, list)

    # t6 — source assertion: the four changed call-site files no longer open ?mode=ro directly
    def test_no_mode_ro_outside_lifecycle(self):
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        # Only the files that were changed to use connect_readonly
        targets = [
            os.path.join(root, "status.py"),
            os.path.join(root, "dashboard.py"),
            os.path.join(root, "depositor.py"),
            os.path.join(root, "tools", "gate_watcher.py"),
        ]
        violations = []
        for fpath in targets:
            with open(fpath, encoding="utf-8") as f:
                for lineno, line in enumerate(f, 1):
                    if 'mode=ro"' in line:
                        violations.append(f"{fpath}:{lineno}: {line.rstrip()}")
        assert violations == [], "mode=ro literal found in changed call-site files:\n" + "\n".join(violations)

    def test_no_python3_status_in_hooks(self):
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        hooks_dir = os.path.join(root, "hooks", "commands")
        violations = []
        for fn in ["wrap.md", "eluvian.md"]:
            fpath = os.path.join(hooks_dir, fn)
            if not os.path.exists(fpath):
                continue
            with open(fpath, encoding="utf-8") as f:
                for lineno, line in enumerate(f, 1):
                    # Match lines where python3 status.py is an instruction, not a
                    # parenthetical attribution like "(from `python3 <bellows>/status.py`)".
                    if "python3" in line and "status.py" in line and "(from `python3" not in line:
                        violations.append(f"{fpath}:{lineno}: {line.rstrip()}")
        assert violations == [], "python3 status.py found in hook files:\n" + "\n".join(violations)

    # t7 — deferred refusal: mode=ro returns a stand-in that raises on first execute
    def test_fallback_on_deferred_refusal(self, tmp_path, monkeypatch):
        db_path = str(tmp_path / "lifecycle.db")
        lifecycle.init_lifecycle_db(db_path)

        real_connect = sqlite3.connect
        calls = []
        deferred = None

        def wrapper(*a, **kw):
            nonlocal deferred
            calls.append(a[0])
            if isinstance(a[0], str) and a[0].startswith("file:"):
                deferred = _DeferredRefusal()
                return deferred
            return real_connect(*a, **kw)

        monkeypatch.setattr(sqlite3, "connect", wrapper)

        conn = lifecycle.connect_readonly(db_path)
        assert deferred is not None
        assert deferred.closed is True
        assert len(calls) == 2
        assert calls[0].startswith("file:")
        assert not calls[1].startswith("file:")
        assert conn.execute("SELECT count(*) FROM plans").fetchone() == (0,)
        assert conn.execute("PRAGMA query_only").fetchone() == (1,)
        conn.close()

    # t8 — deferred non-refusal error propagates and the stand-in is closed
    def test_deferred_other_error_propagates(self, tmp_path, monkeypatch):
        db_path = str(tmp_path / "lifecycle.db")
        lifecycle.init_lifecycle_db(db_path)

        real_connect = sqlite3.connect
        calls = []
        deferred = None

        def wrapper(*a, **kw):
            nonlocal deferred
            calls.append(a[0])
            if isinstance(a[0], str) and a[0].startswith("file:"):
                deferred = _DeferredRefusal("database is locked")
                return deferred
            return real_connect(*a, **kw)

        monkeypatch.setattr(sqlite3, "connect", wrapper)

        with pytest.raises(sqlite3.OperationalError, match="locked"):
            lifecycle.connect_readonly(db_path)
        assert deferred is not None
        assert deferred.closed is True
        assert len(calls) == 1

    # t9 — status.query_in_flight reads through a deferred refusal
    def test_status_reads_through_deferred_refusal(self, tmp_path, monkeypatch):
        db_path = str(tmp_path / "lifecycle.db")
        lifecycle.init_lifecycle_db(db_path)

        real_connect = sqlite3.connect
        calls = []

        def wrapper(*a, **kw):
            calls.append(a[0])
            if isinstance(a[0], str) and a[0].startswith("file:"):
                return _DeferredRefusal()
            return real_connect(*a, **kw)

        monkeypatch.setattr(sqlite3, "connect", wrapper)

        result = status.query_in_flight(db_path)
        assert isinstance(result, list)
