"""Tests for the R2 registry information line in wrap_check (plan 560)."""
import datetime
import importlib
import os
import sqlite3
import stat
import subprocess
import sys
from pathlib import Path

import pytest

BELLOWS_ROOT = Path(__file__).resolve().parent.parent


def _init_lifecycle_db(db_path):
    conn = sqlite3.connect(str(db_path))
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS clearances (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            plan_filename TEXT NOT NULL,
            content_hash TEXT NOT NULL UNIQUE,
            cleared_by TEXT NOT NULL,
            cleared_at TEXT NOT NULL,
            consumed_at TEXT,
            source TEXT
        )
    """)
    conn.commit()
    conn.close()


@pytest.fixture(autouse=True)
def wc_env(monkeypatch, tmp_path):
    root = tmp_path / "root"
    root.mkdir()
    bellows = root / "bellows"
    bellows.mkdir()
    receipts = bellows / "receipts"
    db_path = bellows / "lifecycle.db"
    _init_lifecycle_db(db_path)
    memory = tmp_path / "memory"
    memory.mkdir()

    monkeypatch.setenv("ELUVIAN_WRAP_ROOT", str(root))
    monkeypatch.setenv("ELUVIAN_WRAP_MEMORY", str(memory))

    import hooks.eluvian.wrap_check as wc
    monkeypatch.setattr(wc, "ROOT", root)
    monkeypatch.setattr(wc, "BELLOWS", bellows)
    monkeypatch.setattr(wc, "RECEIPTS", receipts)
    monkeypatch.setattr(wc, "LIFECYCLE_DB", db_path)
    monkeypatch.setattr(wc, "MEMORY", memory)
    monkeypatch.setattr(wc, "BATON", root / "shop_next_session.md")
    return wc


TODAY = datetime.date.today().isoformat()
YESTERDAY = (datetime.date.today() - datetime.timedelta(days=1)).isoformat()


def _make_fake_tuyere(tmp_path, script_output, exit_code=0, hang=False):
    """Create a fake tuyere checkout with a canned .venv/bin/python script."""
    tuyere_dir = tmp_path / "tuyere_fake"
    tuyere_dir.mkdir(exist_ok=True)
    venv_bin = tuyere_dir / ".venv" / "bin"
    venv_bin.mkdir(parents=True, exist_ok=True)

    fake_python = venv_bin / "python"
    if hang:
        script = "#!/usr/bin/env python3\nimport time\ntime.sleep(30)\n"
    else:
        script = (
            "#!/usr/bin/env python3\n"
            "import sys\n"
            f"print({script_output!r})\n"
            f"sys.exit({exit_code})\n"
        )
    fake_python.write_text(script)
    fake_python.chmod(fake_python.stat().st_mode | stat.S_IEXEC)
    return tuyere_dir


class TestSessionWrapsToday:

    def test_today_rows_returned_yesterday_filtered(self, wc_env, monkeypatch, tmp_path):
        output = (
            f"[1] shop — session-abc wrapped at {TODAY} 14:30:00\n"
            f"[2] mini — session-xyz wrapped at {YESTERDAY} 10:00:00"
        )
        tuyere = _make_fake_tuyere(tmp_path, output)
        monkeypatch.setattr(wc_env, "_tuyere_checkout", lambda: tuyere)

        result = wc_env._session_wraps_today()
        assert result is not None
        assert len(result) == 1
        assert TODAY in result[0]
        assert YESTERDAY not in str(result)

    def test_empty_output_returns_empty_list(self, wc_env, monkeypatch, tmp_path):
        tuyere = _make_fake_tuyere(tmp_path, "")
        monkeypatch.setattr(wc_env, "_tuyere_checkout", lambda: tuyere)

        result = wc_env._session_wraps_today()
        assert result == []

    def test_no_wraps_message_returns_empty_list(self, wc_env, monkeypatch, tmp_path):
        tuyere = _make_fake_tuyere(tmp_path, "no session wraps recorded")
        monkeypatch.setattr(wc_env, "_tuyere_checkout", lambda: tuyere)

        result = wc_env._session_wraps_today()
        assert result == []

    def test_nonzero_exit_returns_none(self, wc_env, monkeypatch, tmp_path):
        output = f"[1] shop — session-abc wrapped at {TODAY} 14:30:00"
        tuyere = _make_fake_tuyere(tmp_path, output, exit_code=1)
        monkeypatch.setattr(wc_env, "_tuyere_checkout", lambda: tuyere)

        result = wc_env._session_wraps_today()
        assert result is None

    def test_timeout_returns_none(self, wc_env, monkeypatch, tmp_path):
        tuyere = _make_fake_tuyere(tmp_path, "", hang=True)
        monkeypatch.setattr(wc_env, "_tuyere_checkout", lambda: tuyere)

        result = wc_env._session_wraps_today(timeout_seconds=1)
        assert result is None

    def test_missing_checkout_returns_none(self, wc_env, monkeypatch):
        monkeypatch.setattr(wc_env, "_tuyere_checkout", lambda: None)

        result = wc_env._session_wraps_today()
        assert result is None


class TestNeverSuppressPositivePrint:
    """The registry line is informational only — fails lists must be identical
    whether the registry returns rows or None. The registry line appears in
    stdout only when rows are present."""

    def test_fails_equal_and_registry_line_presence(self, monkeypatch, tmp_path, capsys):
        root = tmp_path / "root2"
        root.mkdir()
        bellows = root / "bellows"
        bellows.mkdir()
        receipts = bellows / "receipts"
        db_path = bellows / "lifecycle.db"
        _init_lifecycle_db(db_path)
        memory = tmp_path / "memory2"
        memory.mkdir()

        baton = root / "shop_next_session.md"
        baton.write_text("no swept line here\n")

        monkeypatch.setenv("ELUVIAN_WRAP_ROOT", str(root))
        monkeypatch.setenv("ELUVIAN_WRAP_MEMORY", str(memory))

        import hooks.eluvian.wrap_check as wc
        importlib.reload(wc)

        monkeypatch.setattr(wc, "ROOT", root)
        monkeypatch.setattr(wc, "BELLOWS", bellows)
        monkeypatch.setattr(wc, "RECEIPTS", receipts)
        monkeypatch.setattr(wc, "LIFECYCLE_DB", db_path)
        monkeypatch.setattr(wc, "MEMORY", memory)
        monkeypatch.setattr(wc, "BATON", baton)

        today = datetime.date.today().isoformat()
        registry_rows = [f"[1] shop — session-abc wrapped at {today} 14:30:00"]

        monkeypatch.setattr(wc, "_session_wraps_today", lambda: registry_rows)
        fails_with = wc.check(session_id=None, caller="debt")
        cap_with = capsys.readouterr()

        monkeypatch.setattr(wc, "_session_wraps_today", lambda: None)
        fails_without = wc.check(session_id=None, caller="debt")
        cap_without = capsys.readouterr()

        assert fails_with == fails_without
        assert len(fails_with) > 0

        assert "[R2/registry]" in cap_with.out
        assert registry_rows[0] in cap_with.out
        assert "[R2/registry]" not in cap_without.out
