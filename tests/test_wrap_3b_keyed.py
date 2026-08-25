"""Tests for the session-id-keyed 3b Lessons-swept check (E5)."""
import datetime
import hashlib
import json
import os
import sqlite3
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
SID = "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
SID_PREFIX = SID[:8]
FOREIGN_SID = "ff00ff00-dead-beef-cafe-000000000000"
FOREIGN_PREFIX = FOREIGN_SID[:8]


def _3b_fails(fails):
    return [f for f in fails if "[3b/lessons]" in f]


def _write_baton(wc, text):
    wc.BATON.write_text(text)


# --- Arm 1: keyed pass ---

def test_keyed_pass(wc_env):
    _write_baton(wc_env, f"Lessons-swept: {TODAY} [sid: {SID_PREFIX}] — none\n")
    fails = wc_env.check(session_id=SID, caller="stop")
    assert _3b_fails(fails) == []


# --- Arm 2: foreign-sid fail ---

def test_foreign_sid_fail(wc_env):
    _write_baton(wc_env, f"Lessons-swept: {TODAY} [sid: {FOREIGN_PREFIX}] — none\n")
    fails = wc_env.check(session_id=SID, caller="stop")
    found = _3b_fails(fails)
    assert len(found) == 1
    assert FOREIGN_PREFIX in found[0]
    assert SID_PREFIX in found[0]


# --- Arm 3: historical-format fail (no sid token) ---

def test_historical_format_fail(wc_env):
    _write_baton(wc_env, f"Lessons-swept: {TODAY} — none\n")
    fails = wc_env.check(session_id=SID, caller="stop")
    found = _3b_fails(fails)
    assert len(found) == 1
    assert "no session-id key" in found[0]


# --- Arm 4: no-sid date-fallback (hit and miss) ---

def test_no_sid_date_fallback_hit(wc_env):
    _write_baton(wc_env, f"Lessons-swept: {TODAY} — none\n")
    fails = wc_env.check(session_id=None, caller="stop")
    assert _3b_fails(fails) == []


def test_no_sid_date_fallback_miss(wc_env):
    _write_baton(wc_env, "Lessons-swept: 2020-01-01 — none\n")
    fails = wc_env.check(session_id=None, caller="stop")
    found = _3b_fails(fails)
    assert len(found) == 1
    assert TODAY in found[0]


# --- Arm 5: debt-caller date-fallback (hit and miss) ---

def test_debt_caller_date_fallback_hit(wc_env):
    _write_baton(wc_env, f"Lessons-swept: {TODAY} [sid: {FOREIGN_PREFIX}] — none\n")
    fails = wc_env.check(session_id=SID, caller="debt")
    assert _3b_fails(fails) == []


def test_debt_caller_date_fallback_miss(wc_env):
    _write_baton(wc_env, "Lessons-swept: 2020-01-01 — none\n")
    fails = wc_env.check(session_id=SID, caller="debt")
    found = _3b_fails(fails)
    assert len(found) == 1


# --- Blockquote-prefix fix (SESSION 63 fixture) ---

def test_blockquote_prefix_found(wc_env):
    _write_baton(wc_env, f"> Lessons-swept: {TODAY} [sid: {SID_PREFIX}] — none\n")
    fails = wc_env.check(session_id=SID, caller="stop")
    assert _3b_fails(fails) == []


def test_blockquote_prefix_date_fallback(wc_env):
    _write_baton(wc_env, f"> Lessons-swept: {TODAY} (SESSION 63) — carried\n")
    fails = wc_env.check(session_id=None, caller="stop")
    assert _3b_fails(fails) == []


# --- Re-dated twin: old predicate missed blockquoted stale-date lines,
#     new predicate finds them but correctly fails on stale date ---

def test_redated_blockquote_stale_date_fails(wc_env):
    _write_baton(wc_env, "> Lessons-swept: 2020-01-01 (SESSION 63) — carried\n")
    fails = wc_env.check(session_id=None, caller="stop")
    found = _3b_fails(fails)
    assert len(found) == 1


# --- Prose-line non-match (G4 false-count fixture) ---

def test_prose_line_not_a_sweep(wc_env):
    baton = (
        f"Lessons-swept: {TODAY} [sid: {SID_PREFIX}] — none\n"
        "The format is `Lessons-swept: <date>` which the lock checks.\n"
    )
    _write_baton(wc_env, baton)
    fails = wc_env.check(session_id=SID, caller="stop")
    assert _3b_fails(fails) == []


# --- Prepend-ordering: newest wins over older same-day keyed line ---

def test_prepend_ordering_newest_wins(wc_env):
    baton = (
        f"Lessons-swept: {TODAY} [sid: {SID_PREFIX}] — latest\n"
        f"Lessons-swept: {TODAY} [sid: {FOREIGN_PREFIX}] — older\n"
    )
    _write_baton(wc_env, baton)
    fails = wc_env.check(session_id=SID, caller="stop")
    assert _3b_fails(fails) == []


def test_prepend_ordering_foreign_on_top_fails(wc_env):
    baton = (
        f"Lessons-swept: {TODAY} [sid: {FOREIGN_PREFIX}] — latest\n"
        f"Lessons-swept: {TODAY} [sid: {SID_PREFIX}] — older\n"
    )
    _write_baton(wc_env, baton)
    fails = wc_env.check(session_id=SID, caller="stop")
    found = _3b_fails(fails)
    assert len(found) == 1
    assert FOREIGN_PREFIX in found[0]


# --- Newest-None fail (no sweep line at all) ---

def test_newest_none_fail(wc_env):
    _write_baton(wc_env, "Some baton content with no sweep lines.\n")
    fails = wc_env.check(session_id=SID, caller="stop")
    found = _3b_fails(fails)
    assert len(found) == 1
    assert "No Lessons-swept: line found" in found[0]


# --- Empty baton ---

def test_empty_baton(wc_env):
    _write_baton(wc_env, "")
    fails = wc_env.check(session_id=SID, caller="stop")
    found = _3b_fails(fails)
    assert len(found) == 1


# --- Missing baton file ---

def test_missing_baton_file(wc_env):
    fails = wc_env.check(session_id=SID, caller="stop")
    found = _3b_fails(fails)
    assert len(found) == 1


# --- Prefix-semantics probe (C-5): prefix-8 and full UUID both match ---

def test_prefix_8_matches(wc_env):
    _write_baton(wc_env, f"Lessons-swept: {TODAY} [sid: {SID_PREFIX}] — none\n")
    fails = wc_env.check(session_id=SID, caller="stop")
    assert _3b_fails(fails) == []


def test_full_uuid_token_matches(wc_env):
    _write_baton(wc_env, f"Lessons-swept: {TODAY} [sid: {SID}] — none\n")
    fails = wc_env.check(session_id=SID, caller="stop")
    assert _3b_fails(fails) == []


def test_short_token_rejected(wc_env):
    _write_baton(wc_env, f"Lessons-swept: {TODAY} [sid: a1b2] — none\n")
    fails = wc_env.check(session_id=SID, caller="stop")
    found = _3b_fails(fails)
    assert len(found) == 1


# --- C-6 line-initial-quote pair ---

def test_backticked_example_inert(wc_env):
    baton = (
        f"Lessons-swept: {TODAY} [sid: {SID_PREFIX}] — none\n"
        "The format is `Lessons-swept: {today} [sid: ...]` etc.\n"
    )
    _write_baton(wc_env, baton)
    fails = wc_env.check(session_id=SID, caller="stop")
    assert _3b_fails(fails) == []


def test_unbackticked_line_initial_matches(wc_env):
    baton = (
        f"Lessons-swept: {TODAY} [sid: {FOREIGN_PREFIX}] — from another session\n"
        f"Lessons-swept: {TODAY} [sid: {SID_PREFIX}] — mine but second\n"
    )
    _write_baton(wc_env, baton)
    fails = wc_env.check(session_id=SID, caller="stop")
    found = _3b_fails(fails)
    assert len(found) == 1
    assert FOREIGN_PREFIX in found[0]


# --- Helper unit tests ---

def test_find_newest_sweep_line_strips_blockquote(wc_env):
    text = "> Lessons-swept: 2026-08-24 (SESSION 63) — carried\nOther line\n"
    result = wc_env._find_newest_sweep_line(text)
    assert result is not None
    assert result.startswith("Lessons-swept:")
    assert ">" not in result


def test_extract_sid_returns_prefix(wc_env):
    line = f"Lessons-swept: {TODAY} [sid: {SID_PREFIX}] — none"
    assert wc_env._extract_sid(line) == SID_PREFIX


def test_extract_sid_returns_none_for_historical(wc_env):
    line = f"Lessons-swept: {TODAY} — none"
    assert wc_env._extract_sid(line) is None
