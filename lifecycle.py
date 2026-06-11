"""Lifecycle DB — monotonic id minting and plan state tracking.

Implements the MINIMAL lifecycle-DB subset for Reporting Phase 1 Executable A:
id_sequence + plans tables only. Other tables (steps, commits, deposits,
verdicts, gate_events) are deferred to Executable B.

DB location: <bellows_root>/lifecycle.db (sibling to bellows.db).
"""

import os
import sqlite3
from datetime import datetime

from bellows_root import resolve_bellows_root

LIFECYCLE_DB_PATH = str(resolve_bellows_root() / "lifecycle.db")


def init_lifecycle_db(db_path=None):
    """Create lifecycle.db schema (idempotent). Safe to call on every startup."""
    path = db_path or LIFECYCLE_DB_PATH
    conn = sqlite3.connect(path)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS id_sequence (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            next_id INTEGER NOT NULL DEFAULT 1
        )
    """)
    # Seed the single-row counter if absent
    conn.execute("INSERT OR IGNORE INTO id_sequence (id, next_id) VALUES (1, 1)")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS plans (
            id INTEGER PRIMARY KEY,
            type TEXT NOT NULL CHECK (type IN ('diagnostic', 'executable', 'qa')),
            target_project TEXT NOT NULL,
            title TEXT,
            dispatch_mode TEXT,
            tier TEXT,
            lifecycle_state TEXT NOT NULL DEFAULT 'claimed'
                CHECK (lifecycle_state IN ('claimed','in_progress','awaiting_verdict','closed','halted','abandoned')),
            total_steps INTEGER,
            deposit_placeholder_name TEXT,
            created_at TEXT NOT NULL,
            closed_at TEXT
        )
    """)
    conn.commit()
    conn.close()


def mint_and_claim(plan_type, target_project, title, dispatch_mode, tier,
                   total_steps, deposit_placeholder_name, db_path=None):
    """Mint a global-monotonic id and write the initial plans row atomically.

    Returns the minted integer id.
    Executes UPDATE+INSERT in a single BEGIN IMMEDIATE transaction so no id
    is burned without a corresponding plans row.
    """
    path = db_path or LIFECYCLE_DB_PATH
    conn = sqlite3.connect(path)
    try:
        conn.execute("BEGIN IMMEDIATE")
        row = conn.execute(
            "UPDATE id_sequence SET next_id = next_id + 1 RETURNING next_id - 1"
        ).fetchone()
        plan_id = row[0]
        conn.execute(
            """INSERT INTO plans
               (id, type, target_project, title, dispatch_mode, tier,
                lifecycle_state, total_steps, deposit_placeholder_name, created_at)
               VALUES (?, ?, ?, ?, ?, ?, 'claimed', ?, ?, ?)""",
            (plan_id, plan_type, target_project, title, dispatch_mode, tier,
             total_steps, deposit_placeholder_name, datetime.now().isoformat()),
        )
        conn.execute("COMMIT")
        return plan_id
    except Exception:
        conn.execute("ROLLBACK")
        raise
    finally:
        conn.close()


def mark_plan_state(plan_id, state, closed_at=None, db_path=None):
    """Update a plan's lifecycle_state (and optionally closed_at)."""
    path = db_path or LIFECYCLE_DB_PATH
    conn = sqlite3.connect(path)
    if closed_at is not None:
        conn.execute(
            "UPDATE plans SET lifecycle_state = ?, closed_at = ? WHERE id = ?",
            (state, closed_at, plan_id),
        )
    else:
        conn.execute(
            "UPDATE plans SET lifecycle_state = ? WHERE id = ?",
            (state, plan_id),
        )
    conn.commit()
    conn.close()


def recover_half_claimed(decisions_dir, db_path=None):
    """Startup recovery for half-claimed plans (blueprint 2.4a).

    For each plans row with lifecycle_state='claimed' whose
    in-progress-<type>-<id>.md is absent:
      - If deposit_placeholder_name still exists on disk, re-execute the rename.
      - Otherwise mark the row 'abandoned'.

    Returns list of (plan_id, action) tuples describing what was done.
    """
    path = db_path or LIFECYCLE_DB_PATH
    conn = sqlite3.connect(path)
    rows = conn.execute(
        "SELECT id, type, deposit_placeholder_name FROM plans WHERE lifecycle_state = 'claimed'"
    ).fetchall()
    actions = []
    for plan_id, plan_type, deposit_name in rows:
        expected_name = f"in-progress-{plan_type}-{plan_id}.md"
        expected_path = os.path.join(decisions_dir, expected_name)
        if os.path.exists(expected_path):
            # Already renamed — just needs state update
            conn.execute(
                "UPDATE plans SET lifecycle_state = 'in_progress' WHERE id = ?",
                (plan_id,),
            )
            actions.append((plan_id, "already_renamed"))
            continue
        # Check if deposit placeholder still on disk
        if deposit_name:
            deposit_path = os.path.join(decisions_dir, deposit_name)
            if os.path.exists(deposit_path):
                os.rename(deposit_path, expected_path)
                conn.execute(
                    "UPDATE plans SET lifecycle_state = 'in_progress' WHERE id = ?",
                    (plan_id,),
                )
                actions.append((plan_id, "re_renamed"))
                continue
        # Neither the in-progress file nor the deposit exists — abandon
        conn.execute(
            "UPDATE plans SET lifecycle_state = 'abandoned', closed_at = ? WHERE id = ?",
            (datetime.now().isoformat(), plan_id),
        )
        actions.append((plan_id, "abandoned"))
    conn.commit()
    conn.close()
    return actions
