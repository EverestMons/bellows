"""Lifecycle DB — monotonic id minting and plan state tracking.

Implements the lifecycle DB for Reporting Phase 1:
- Executable A: id_sequence + plans tables (shipped)
- Executable B: steps, commits, deposits, verdicts, gate_events,
  diagnostic_meta, executable_meta, derivations tables + write helpers.

DB location: <bellows_root>/lifecycle.db (sibling to bellows.db).
"""

import logging
import os
import re
import sqlite3
from datetime import datetime

from bellows_root import resolve_bellows_root

logger = logging.getLogger("bellows")

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
    # --- Executable B tables (blueprint Section 3.4 DDL, verbatim) ---
    conn.execute("""
        CREATE TABLE IF NOT EXISTS diagnostic_meta (
            plan_id INTEGER PRIMARY KEY REFERENCES plans(id),
            scope TEXT,
            hypothesis TEXT,
            findings_deposit_ref TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS executable_meta (
            plan_id INTEGER PRIMARY KEY REFERENCES plans(id),
            test_scope TEXT,
            files_changed_count INTEGER
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS derivations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            executable_id INTEGER NOT NULL REFERENCES plans(id),
            diagnostic_id INTEGER NOT NULL REFERENCES plans(id),
            UNIQUE(executable_id, diagnostic_id)
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS steps (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            plan_id INTEGER NOT NULL REFERENCES plans(id),
            step_number INTEGER NOT NULL,
            role TEXT,
            status TEXT NOT NULL DEFAULT 'pending'
                CHECK (status IN ('pending','running','awaiting_verdict','complete')),
            step_started_at TEXT,
            step_ended_at TEXT,
            cost_usd REAL,
            turns INTEGER,
            duration_s REAL,
            log_ref TEXT,
            UNIQUE(plan_id, step_number)
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS commits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            step_id INTEGER NOT NULL REFERENCES steps(id),
            repo TEXT NOT NULL,
            sha TEXT NOT NULL,
            message_ref TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS deposits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            step_id INTEGER NOT NULL REFERENCES steps(id),
            declared_path TEXT NOT NULL,
            type TEXT,
            landed INTEGER NOT NULL DEFAULT 0
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS verdicts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            plan_id INTEGER NOT NULL REFERENCES plans(id),
            step_number INTEGER NOT NULL,
            outcome TEXT,
            pause_reason_code TEXT,
            decided_by TEXT,
            verdict_file_ref TEXT,
            disposition_summary TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS gate_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            step_id INTEGER NOT NULL REFERENCES steps(id),
            gate_name TEXT NOT NULL,
            result TEXT NOT NULL CHECK (result IN ('pass', 'fail')),
            reason_code TEXT,
            overridden INTEGER NOT NULL DEFAULT 0,
            override_ref TEXT
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


# ---------------------------------------------------------------------------
# Executable B — write helpers (log-and-continue: lifecycle writes NEVER raise)
# ---------------------------------------------------------------------------

def _warn(msg):
    """Emit a lifecycle WARN. Uses the bellows logger if configured, else print."""
    ts = datetime.now().strftime("%H:%M:%S")
    formatted = f"{ts} [WARN] [lifecycle] {msg}"
    if logger.handlers:
        logger.warning(formatted)
    else:
        print(formatted)


def record_step_start(plan_id, step_number, role=None, db_path=None):
    """Insert a steps row with status='running'. Returns step_id or None."""
    try:
        path = db_path or LIFECYCLE_DB_PATH
        conn = sqlite3.connect(path)
        cur = conn.execute(
            """INSERT INTO steps (plan_id, step_number, role, status, step_started_at)
               VALUES (?, ?, ?, 'running', ?)""",
            (plan_id, step_number, role, datetime.now().isoformat()),
        )
        step_id = cur.lastrowid
        conn.commit()
        conn.close()
        return step_id
    except Exception as e:
        _warn(f"record_step_start failed for plan {plan_id} step {step_number}: {e}")
        return None


def record_step_end(step_id, status="complete", cost_usd=None, turns=None,
                    duration_s=None, log_ref=None, db_path=None):
    """Update a steps row with end-of-step data."""
    if step_id is None:
        return
    try:
        path = db_path or LIFECYCLE_DB_PATH
        conn = sqlite3.connect(path)
        conn.execute(
            """UPDATE steps SET status = ?, step_ended_at = ?, cost_usd = ?,
               turns = ?, duration_s = ?, log_ref = ? WHERE id = ?""",
            (status, datetime.now().isoformat(), cost_usd, turns, duration_s,
             log_ref, step_id),
        )
        conn.commit()
        conn.close()
    except Exception as e:
        _warn(f"record_step_end failed for step_id {step_id}: {e}")


def record_gate_events(step_id, gate_result, db_path=None):
    """Insert gate_events rows from a gate_result dict.

    Generates one row per known gate: failures produce 'fail' rows,
    all other gates that were evaluated produce 'pass' rows.
    """
    if step_id is None:
        return
    try:
        path = db_path or LIFECYCLE_DB_PATH
        conn = sqlite3.connect(path)
        failures = gate_result.get("failures", [])
        failure_gates = set()
        for f in failures:
            gate_name = f.get("gate", "unknown")
            reason = f.get("evidence", "")
            overridden = 1 if f.get("overridden", False) else 0
            override_ref = f.get("override_ref")
            conn.execute(
                """INSERT INTO gate_events (step_id, gate_name, result, reason_code, overridden, override_ref)
                   VALUES (?, ?, 'fail', ?, ?, ?)""",
                (step_id, gate_name, reason, overridden, override_ref),
            )
            failure_gates.add(gate_name)
        # Record pass for standard gates not in the failure set
        standard_gates = [
            "receipt_status", "no_errors", "no_permission_denials",
            "deposit_exists", "scope_check", "rule_20_self_check",
            "rule_22_verification",
        ]
        for gname in standard_gates:
            if gname not in failure_gates:
                conn.execute(
                    """INSERT INTO gate_events (step_id, gate_name, result, reason_code, overridden, override_ref)
                       VALUES (?, ?, 'pass', NULL, 0, NULL)""",
                    (step_id, gname),
                )
        conn.commit()
        conn.close()
    except Exception as e:
        _warn(f"record_gate_events failed for step_id {step_id}: {e}")


def record_deposits(step_id, deposits_list, db_path=None):
    """Insert deposits rows. deposits_list: list of dicts with declared_path, type, landed."""
    if step_id is None or not deposits_list:
        return
    try:
        path = db_path or LIFECYCLE_DB_PATH
        conn = sqlite3.connect(path)
        for d in deposits_list:
            conn.execute(
                """INSERT INTO deposits (step_id, declared_path, type, landed)
                   VALUES (?, ?, ?, ?)""",
                (step_id, d["declared_path"], d.get("type"), 1 if d.get("landed") else 0),
            )
        conn.commit()
        conn.close()
    except Exception as e:
        _warn(f"record_deposits failed for step_id {step_id}: {e}")


def record_commits(step_id, repo, shas, db_path=None):
    """Insert commits rows — one per SHA."""
    if step_id is None or not shas:
        return
    try:
        path = db_path or LIFECYCLE_DB_PATH
        conn = sqlite3.connect(path)
        for sha in shas:
            conn.execute(
                "INSERT INTO commits (step_id, repo, sha, message_ref) VALUES (?, ?, ?, NULL)",
                (step_id, repo, sha),
            )
        conn.commit()
        conn.close()
    except Exception as e:
        _warn(f"record_commits failed for step_id {step_id}: {e}")


def record_verdict_request(plan_id, step_number, pause_reason_code=None,
                           verdict_file_ref=None, db_path=None):
    """Insert a verdicts row with outcome=NULL (pending)."""
    if plan_id is None:
        return
    try:
        path = db_path or LIFECYCLE_DB_PATH
        conn = sqlite3.connect(path)
        conn.execute(
            """INSERT INTO verdicts (plan_id, step_number, outcome, pause_reason_code, verdict_file_ref)
               VALUES (?, ?, NULL, ?, ?)""",
            (plan_id, step_number, pause_reason_code, verdict_file_ref),
        )
        conn.commit()
        conn.close()
    except Exception as e:
        _warn(f"record_verdict_request failed for plan {plan_id} step {step_number}: {e}")


def record_verdict_outcome(plan_id, step_number, outcome, decided_by=None,
                           disposition_summary=None, db_path=None):
    """Update the most recent pending verdict row for this plan+step with the outcome."""
    if plan_id is None:
        return
    try:
        path = db_path or LIFECYCLE_DB_PATH
        conn = sqlite3.connect(path)
        conn.execute(
            """UPDATE verdicts SET outcome = ?, decided_by = ?, disposition_summary = ?
               WHERE plan_id = ? AND step_number = ? AND outcome IS NULL""",
            (outcome, decided_by, disposition_summary, plan_id, step_number),
        )
        conn.commit()
        conn.close()
    except Exception as e:
        _warn(f"record_verdict_outcome failed for plan {plan_id} step {step_number}: {e}")


def record_meta(plan_id, plan_type, header=None, db_path=None):
    """Insert a diagnostic_meta or executable_meta row from parsed header fields."""
    if plan_id is None:
        return
    try:
        path = db_path or LIFECYCLE_DB_PATH
        conn = sqlite3.connect(path)
        header = header or {}
        if plan_type == "diagnostic":
            conn.execute(
                """INSERT OR IGNORE INTO diagnostic_meta (plan_id, scope, hypothesis, findings_deposit_ref)
                   VALUES (?, ?, ?, ?)""",
                (plan_id,
                 header.get("scope", header.get("Scope")),
                 header.get("hypothesis", header.get("Hypothesis")),
                 header.get("findings_deposit_ref")),
            )
        elif plan_type == "executable":
            conn.execute(
                """INSERT OR IGNORE INTO executable_meta (plan_id, test_scope, files_changed_count)
                   VALUES (?, ?, ?)""",
                (plan_id,
                 header.get("test_scope", header.get("Test Scope")),
                 header.get("files_changed_count")),
            )
        conn.commit()
        conn.close()
    except Exception as e:
        _warn(f"record_meta failed for plan {plan_id}: {e}")


def parse_derivations(plan_text):
    """Parse 'implements diagnostic <id-or-slug>' citations from plan text.

    Returns a list of integer diagnostic ids found, or empty list if none.
    Tolerates both numeric ids (e.g., 'implements diagnostic 42') and
    legacy slug citations (e.g., 'implements diagnostic foo-bar-2026-06-10').
    Only numeric ids are returned (slug citations are not resolvable to an id
    without a DB lookup, so they are skipped).
    """
    ids = []
    for m in re.finditer(r'implements\s+diagnostic\s+(\d+)', plan_text, re.IGNORECASE):
        ids.append(int(m.group(1)))
    return ids


def record_derivations(executable_id, diagnostic_ids, db_path=None):
    """Insert derivations rows linking an executable to its source diagnostics."""
    if executable_id is None or not diagnostic_ids:
        return
    try:
        path = db_path or LIFECYCLE_DB_PATH
        conn = sqlite3.connect(path)
        for diag_id in diagnostic_ids:
            conn.execute(
                "INSERT OR IGNORE INTO derivations (executable_id, diagnostic_id) VALUES (?, ?)",
                (executable_id, diag_id),
            )
        conn.commit()
        conn.close()
    except Exception as e:
        _warn(f"record_derivations failed for executable {executable_id}: {e}")


def get_step_id(plan_id, step_number, db_path=None):
    """Look up the step_id for a given plan_id and step_number. Returns int or None."""
    if plan_id is None:
        return None
    try:
        path = db_path or LIFECYCLE_DB_PATH
        conn = sqlite3.connect(path)
        row = conn.execute(
            "SELECT id FROM steps WHERE plan_id = ? AND step_number = ?",
            (plan_id, step_number),
        ).fetchone()
        conn.close()
        return row[0] if row else None
    except Exception as e:
        _warn(f"get_step_id failed for plan {plan_id} step {step_number}: {e}")
        return None
