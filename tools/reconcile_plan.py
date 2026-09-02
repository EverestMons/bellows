#!/usr/bin/env python3
"""reconcile_plan — three-surface orphan recovery in one transaction.

Reconciles a plan that has become orphaned: updates the plans row,
closes NULL-outcome verdicts, and archives pending verdict-request files.
One transaction for the two DB updates; the pending-file archive is a
filesystem rename.

WAL law: writes are live-correct in the -wal; NEVER checkpoint or commit
the DBs from a Planner session. See exec-454/458.

Usage:
    reconcile_plan.py <plan-id> {closed|halted|abandoned}
        --outcome {continue|stop} --summary "<text>"
        [--doc-ref <path>] [--killed-verified] [--db <path>]
"""

import argparse
import glob
import os
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_BELLOWS_ROOT = _HERE.parent

VALID_STATES = ("closed", "halted", "abandoned")
VALID_OUTCOMES = ("continue", "stop")


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Three-surface orphan recovery for a plan")
    parser.add_argument("plan_id", type=int, help="plan id (integer)")
    parser.add_argument("state", choices=VALID_STATES,
                        help="target lifecycle state")
    parser.add_argument("--outcome", required=True, choices=VALID_OUTCOMES,
                        help="verdict outcome for NULL-outcome rows")
    parser.add_argument("--summary", required=True,
                        help="disposition summary for NULL-outcome verdict rows")
    parser.add_argument("--doc-ref",
                        help="plan_doc_ref to set (keeps existing if omitted)")
    parser.add_argument("--killed-verified", action="store_true",
                        help="acknowledge that an in_progress worker was verified killed")
    parser.add_argument("--db",
                        help="path to lifecycle.db (default: repo-root lifecycle.db)")
    args = parser.parse_args(argv)

    db_path = Path(args.db) if args.db else _BELLOWS_ROOT / "lifecycle.db"
    if not db_path.exists():
        print(f"ERROR: database not found: {db_path}", file=sys.stderr)
        sys.exit(2)

    root = db_path.resolve().parent if args.db else _BELLOWS_ROOT
    pending_dir = root / "verdicts" / "pending"
    archived_dir = root / "verdicts" / "archived"

    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row

    plan_row = conn.execute("SELECT * FROM plans WHERE id = ?",
                            (args.plan_id,)).fetchone()
    if plan_row is None:
        print(f"ERROR: no plan with id={args.plan_id}", file=sys.stderr)
        conn.close()
        sys.exit(2)

    print("=== Plan row ===")
    for key in plan_row.keys():
        print(f"  {key}: {plan_row[key]}")

    verdict_rows = conn.execute(
        "SELECT * FROM verdicts WHERE plan_id = ? AND outcome IS NULL",
        (args.plan_id,)).fetchall()
    print(f"\n=== NULL-outcome verdict rows ({len(verdict_rows)}) ===")
    for row in verdict_rows:
        print("  ---")
        for key in row.keys():
            print(f"  {key}: {row[key]}")

    pattern = f"verdict-request-{args.plan_id}-step-*.md"
    pending_files = sorted(glob.glob(str(pending_dir / pattern))) if pending_dir.is_dir() else []
    print(f"\n=== Pending verdict-request files ({len(pending_files)}) ===")
    for f in pending_files:
        print(f"  {f}")

    if plan_row["lifecycle_state"] in ("in_progress", "awaiting_verdict") and not args.killed_verified:
        print("\nREFUSED (exit 3): lifecycle_state is 'in_progress' or 'awaiting_verdict' and "
              "--killed-verified was not passed.", file=sys.stderr)
        print("A worker can survive ENOSPC and wedge (~70 min measured) — "
              "verify with `ps -o etime,%cpu -p <pid>`, kill it, then "
              "re-run with --killed-verified.", file=sys.stderr)
        conn.close()
        sys.exit(3)

    now_utc = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    try:
        conn.execute("BEGIN")
        conn.execute(
            "UPDATE plans SET lifecycle_state = ?, closed_at = ?, "
            "plan_doc_ref = COALESCE(?, plan_doc_ref) WHERE id = ?",
            (args.state, now_utc, args.doc_ref, args.plan_id))
        cursor = conn.execute(
            "UPDATE verdicts SET outcome = ?, decided_by = 'planner', "
            "disposition_summary = ? WHERE plan_id = ? AND outcome IS NULL",
            (args.outcome, args.summary, args.plan_id))
        verdict_update_count = cursor.rowcount
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"ERROR: transaction failed: {e}", file=sys.stderr)
        conn.close()
        sys.exit(1)

    print(f"\n=== Transaction complete ===")
    print(f"  plans row updated: lifecycle_state={args.state}, closed_at={now_utc}")
    print(f"  verdicts rows updated (NULL-outcome): {verdict_update_count}")

    if pending_files:
        archived_dir.mkdir(parents=True, exist_ok=True)
        print(f"\n=== Archiving pending files ===")
        for src in pending_files:
            dst = archived_dir / Path(src).name
            os.rename(src, str(dst))
            print(f"  {src} -> {dst}")

    conn.close()

    plan_type = plan_row["type"]
    if args.state == "halted":
        dest_name = f"halted-{plan_type}-{args.plan_id}.md"
    else:
        dest_name = f"{plan_type}-{args.plan_id}.md"

    print(f"\n=== Remaining human acts (NOT performed by this tool) ===")
    print(f"  git mv knowledge/decisions/{plan_type}-{args.plan_id}.md "
          f"knowledge/decisions/Done/{dest_name}")
    print(f"  git commit -m \"chore: {args.plan_id} {args.state}\"")


if __name__ == "__main__":
    main()
