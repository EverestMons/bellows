"""Tests for the cycle-nudge trigger (plans-closed-since-ingestion threshold)."""

import sqlite3
import time
from unittest.mock import patch, MagicMock

import bellows
import lifecycle
import notifier


def _create_lessons_db(path):
    conn = sqlite3.connect(str(path))
    conn.execute("""
        CREATE TABLE lesson_entries (
            id INTEGER PRIMARY KEY,
            source_file TEXT NOT NULL,
            source_heading TEXT NOT NULL,
            entry_date TEXT,
            raw_content TEXT NOT NULL,
            content_hash TEXT NOT NULL,
            tags TEXT,
            ingested_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def _insert_lesson(path, ingested_at):
    conn = sqlite3.connect(str(path))
    conn.execute(
        "INSERT INTO lesson_entries (source_file, source_heading, raw_content, content_hash, ingested_at) "
        "VALUES (?, ?, ?, ?, ?)",
        ("f.md", "heading", "content", "hash123", ingested_at),
    )
    conn.commit()
    conn.close()


def _insert_closed_plan(db_path, closed_at):
    conn = sqlite3.connect(db_path)
    conn.execute(
        "INSERT INTO plans (type, target_project, lifecycle_state, created_at, closed_at) "
        "VALUES ('executable', 'test-project', 'closed', '2026-01-01T00:00:00', ?)",
        (closed_at,),
    )
    conn.commit()
    conn.close()


# (a) count-since query correctness including NULL-ingestion branch
def test_count_plans_closed_since_with_timestamp(tmp_path):
    db_path = str(tmp_path / "lifecycle.db")
    lifecycle.init_lifecycle_db(db_path)
    _insert_closed_plan(db_path, "2026-06-01T00:00:00")
    _insert_closed_plan(db_path, "2026-06-15T00:00:00")
    _insert_closed_plan(db_path, "2026-07-01T00:00:00")
    count = bellows._count_plans_closed_since("2026-06-10T00:00:00", lifecycle_db_path=db_path)
    assert count == 2


def test_count_plans_closed_since_null_ingestion(tmp_path):
    db_path = str(tmp_path / "lifecycle.db")
    lifecycle.init_lifecycle_db(db_path)
    _insert_closed_plan(db_path, "2026-06-01T00:00:00")
    _insert_closed_plan(db_path, "2026-07-01T00:00:00")
    count = bellows._count_plans_closed_since(None, lifecycle_db_path=db_path)
    assert count == 2


# (b) threshold boundary
def test_threshold_boundary_fires_at_threshold(tmp_path):
    db_path = str(tmp_path / "lifecycle.db")
    lifecycle.init_lifecycle_db(db_path)
    lessons_db = tmp_path / "lessons-forge.db"
    _create_lessons_db(lessons_db)
    _insert_lesson(lessons_db, "2026-01-01T00:00:00")
    for i in range(10):
        _insert_closed_plan(db_path, f"2026-07-0{i+1 if i < 9 else 1}T00:00:00")

    config = {
        "cycle_nudge": {"enabled": True, "plans_closed_threshold": 10, "interval_hours": 24},
        "notifications": {"enabled": True, "events": {"cycle_nudge": True}},
        "callback_port": 19999,
        "watched_projects": [],
        "pushover": {"app_key": "test", "user_key": "test"},
    }
    b = bellows.Bellows(config)
    b._cycle_nudge_last_eval = 0.0

    with patch.object(bellows, "LESSONS_FORGE_DB", str(lessons_db)), \
         patch.object(lifecycle, "LIFECYCLE_DB_PATH", db_path), \
         patch.object(notifier, "_enqueue_deferred") as mock_enqueue:
        b._evaluate_cycle_nudge()

    mock_enqueue.assert_called_once()
    assert mock_enqueue.call_args[0][0] == "cycle_nudge"


def test_threshold_boundary_no_fire_below(tmp_path):
    db_path = str(tmp_path / "lifecycle.db")
    lifecycle.init_lifecycle_db(db_path)
    lessons_db = tmp_path / "lessons-forge.db"
    _create_lessons_db(lessons_db)
    _insert_lesson(lessons_db, "2026-01-01T00:00:00")
    for i in range(9):
        _insert_closed_plan(db_path, f"2026-07-0{i+1}T00:00:00")

    config = {
        "cycle_nudge": {"enabled": True, "plans_closed_threshold": 10, "interval_hours": 24},
        "notifications": {"enabled": True, "events": {"cycle_nudge": True}},
        "callback_port": 19998,
        "watched_projects": [],
        "pushover": {"app_key": "test", "user_key": "test"},
    }
    b = bellows.Bellows(config)
    b._cycle_nudge_last_eval = 0.0

    with patch.object(bellows, "LESSONS_FORGE_DB", str(lessons_db)), \
         patch.object(lifecycle, "LIFECYCLE_DB_PATH", db_path), \
         patch.object(notifier, "_enqueue_deferred") as mock_enqueue:
        b._evaluate_cycle_nudge()

    mock_enqueue.assert_not_called()


# (c) missing lessons-forge.db → logged no-op, no exception
def test_missing_lessons_db_no_exception(tmp_path):
    db_path = str(tmp_path / "lifecycle.db")
    lifecycle.init_lifecycle_db(db_path)
    nonexistent = str(tmp_path / "nonexistent.db")

    config = {
        "cycle_nudge": {"enabled": True, "plans_closed_threshold": 1, "interval_hours": 24},
        "notifications": {"enabled": True, "events": {"cycle_nudge": True}},
        "callback_port": 19997,
        "watched_projects": [],
        "pushover": {"app_key": "test", "user_key": "test"},
    }
    b = bellows.Bellows(config)
    b._cycle_nudge_last_eval = 0.0

    with patch.object(bellows, "LESSONS_FORGE_DB", nonexistent), \
         patch.object(lifecycle, "LIFECYCLE_DB_PATH", db_path), \
         patch.object(notifier, "_enqueue_deferred") as mock_enqueue:
        b._evaluate_cycle_nudge()

    mock_enqueue.assert_not_called()


# (d) interval gating — second evaluation inside the window is a no-op
def test_interval_gating(tmp_path):
    db_path = str(tmp_path / "lifecycle.db")
    lifecycle.init_lifecycle_db(db_path)
    lessons_db = tmp_path / "lessons-forge.db"
    _create_lessons_db(lessons_db)
    _insert_lesson(lessons_db, "2026-01-01T00:00:00")
    for i in range(10):
        _insert_closed_plan(db_path, f"2026-07-0{i+1 if i < 9 else 1}T00:00:00")

    config = {
        "cycle_nudge": {"enabled": True, "plans_closed_threshold": 10, "interval_hours": 24},
        "notifications": {"enabled": True, "events": {"cycle_nudge": True}},
        "callback_port": 19996,
        "watched_projects": [],
        "pushover": {"app_key": "test", "user_key": "test"},
    }
    b = bellows.Bellows(config)
    b._cycle_nudge_last_eval = 0.0

    with patch.object(bellows, "LESSONS_FORGE_DB", str(lessons_db)), \
         patch.object(lifecycle, "LIFECYCLE_DB_PATH", db_path), \
         patch.object(notifier, "_enqueue_deferred") as mock_enqueue:
        b._evaluate_cycle_nudge()
        assert mock_enqueue.call_count == 1
        b._evaluate_cycle_nudge()
        assert mock_enqueue.call_count == 1


# (e) post-fire suppression until ingested_at advances
def test_post_fire_suppression(tmp_path):
    db_path = str(tmp_path / "lifecycle.db")
    lifecycle.init_lifecycle_db(db_path)
    lessons_db = tmp_path / "lessons-forge.db"
    _create_lessons_db(lessons_db)
    _insert_lesson(lessons_db, "2026-01-01T00:00:00")
    for i in range(10):
        _insert_closed_plan(db_path, f"2026-07-0{i+1 if i < 9 else 1}T00:00:00")

    config = {
        "cycle_nudge": {"enabled": True, "plans_closed_threshold": 10, "interval_hours": 0},
        "notifications": {"enabled": True, "events": {"cycle_nudge": True}},
        "callback_port": 19995,
        "watched_projects": [],
        "pushover": {"app_key": "test", "user_key": "test"},
    }
    b = bellows.Bellows(config)
    b._cycle_nudge_last_eval = 0.0

    with patch.object(bellows, "LESSONS_FORGE_DB", str(lessons_db)), \
         patch.object(lifecycle, "LIFECYCLE_DB_PATH", db_path), \
         patch.object(notifier, "_enqueue_deferred") as mock_enqueue:
        b._evaluate_cycle_nudge()
        assert mock_enqueue.call_count == 1

        b._cycle_nudge_last_eval = 0.0
        b._evaluate_cycle_nudge()
        assert mock_enqueue.call_count == 1

        _insert_lesson(lessons_db, "2026-01-02T00:00:00")
        b._cycle_nudge_last_eval = 0.0
        b._evaluate_cycle_nudge()
        assert mock_enqueue.call_count == 2


# (f) absent cycle_nudge config block → disabled, no exception
def test_absent_config_disabled(tmp_path):
    config = {
        "notifications": {"enabled": True, "events": {}},
        "callback_port": 19994,
        "watched_projects": [],
        "pushover": {"app_key": "test", "user_key": "test"},
    }
    b = bellows.Bellows(config)
    b._cycle_nudge_last_eval = 0.0
    b._evaluate_cycle_nudge()
