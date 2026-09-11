"""Reconcile stale awaiting_verdict step rows on closed plans.

No flags: LIST — print every awaiting_verdict row grouped by plan lifecycle_state,
plus running rows on non-in_progress plans.

--apply: for each awaiting_verdict row whose plan is closed, call
lifecycle.mark_step_complete. Refuses if any plan is in_progress or awaiting_verdict
in the same DB (to avoid racing the daemon).
"""
import argparse
import sqlite3
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import lifecycle


def _open_ro(db_path):
    return sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)


def _list(db_path):
    conn = _open_ro(db_path)
    rows = conn.execute(
        """SELECT s.id, s.plan_id, s.step_number, p.lifecycle_state, p.total_steps
           FROM steps s JOIN plans p ON s.plan_id = p.id
           WHERE s.status = 'awaiting_verdict'
           ORDER BY p.lifecycle_state, s.id"""
    ).fetchall()
    conn.close()

    by_state = {}
    for row in rows:
        state = row[3]
        by_state.setdefault(state, []).append(row)

    if not by_state:
        print("No awaiting_verdict step rows found.")
    for state, group in sorted(by_state.items()):
        print(f"\n--- awaiting_verdict on {state} plans ---")
        for r in group:
            print(f"  id={r[0]} plan_id={r[1]} step_number={r[2]} lifecycle_state={r[3]} total_steps={r[4]}")

    # phantom running rows
    conn = _open_ro(db_path)
    phantoms = conn.execute(
        """SELECT s.id, s.plan_id, s.step_number, p.lifecycle_state
           FROM steps s JOIN plans p ON s.plan_id = p.id
           WHERE s.status = 'running' AND p.lifecycle_state != 'in_progress'
           ORDER BY s.id"""
    ).fetchall()
    conn.close()
    if phantoms:
        print("\n--- running steps on non-in_progress plans (listed, not touched) ---")
        for r in phantoms:
            print(f"  id={r[0]} plan_id={r[1]} step_number={r[2]} lifecycle_state={r[3]}")

    total_av = sum(len(g) for g in by_state.values())
    closed_av = len(by_state.get("closed", []))
    halted_av = len(by_state.get("halted", []))
    print(f"\nTotals: {total_av} awaiting_verdict ({closed_av} closed, {halted_av} halted), {len(phantoms)} running phantom(s)")


def _check_no_inflight(db_path):
    conn = _open_ro(db_path)
    blocking = conn.execute(
        "SELECT id FROM plans WHERE lifecycle_state IN ('in_progress', 'awaiting_verdict')"
    ).fetchall()
    conn.close()
    return [r[0] for r in blocking]


def _apply(db_path):
    blocking = _check_no_inflight(db_path)
    if blocking:
        ids = ", ".join(str(i) for i in blocking)
        print(f"REFUSED: plans in flight or awaiting verdict: {ids}", file=sys.stderr)
        sys.exit(1)

    conn = _open_ro(db_path)
    targets = conn.execute(
        """SELECT s.plan_id, s.step_number
           FROM steps s JOIN plans p ON s.plan_id = p.id
           WHERE s.status = 'awaiting_verdict' AND p.lifecycle_state = 'closed'
           ORDER BY s.id"""
    ).fetchall()
    conn.close()

    if not targets:
        print("No closed/awaiting_verdict rows to repair.")
        return

    for plan_id, step_number in targets:
        n = lifecycle.mark_step_complete(plan_id, step_number, db_path=db_path)
        print(f"  plan_id={plan_id} step_number={step_number} rowcount={n}")

    print(f"\nApplied: {len(targets)} row(s) flipped to complete.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true",
                        help="Flip closed/awaiting_verdict rows to complete.")
    parser.add_argument("--db", default=lifecycle.LIFECYCLE_DB_PATH,
                        help="Path to lifecycle.db (default: lifecycle.LIFECYCLE_DB_PATH).")
    args = parser.parse_args()

    if args.apply:
        _apply(args.db)
    else:
        _list(args.db)


if __name__ == "__main__":
    main()
