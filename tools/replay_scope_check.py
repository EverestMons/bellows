#!/usr/bin/env python3
"""Replay today's scope_check gate over every step that has recorded step_files rows.

Usage: replay_scope_check.py <lifecycle.db> [--plan-root <path>]

Read-only: opens the db with mode=ro, writes nothing.
Prints one line per step and a FLIPS summary.
"""

import argparse
import os
import sqlite3
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import gates
from bellows_root import resolve_bellows_root


def _resolve_plan_text(plan_id, plan_doc_ref, plan_root):
    candidates = []
    if plan_doc_ref:
        if os.path.isabs(plan_doc_ref):
            candidates.append(plan_doc_ref)
        else:
            candidates.append(os.path.join(plan_root, plan_doc_ref))
    candidates.append(
        os.path.join(plan_root, "knowledge", "decisions", "Done", f"executable-{plan_id}.md")
    )
    for c in candidates:
        if os.path.isfile(c):
            try:
                with open(c, errors="replace") as fh:
                    return fh.read()
            except OSError:
                pass
    return None


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Replay today's scope_check over recorded step_files rows."
    )
    parser.add_argument("db", help="Path to lifecycle.db")
    parser.add_argument(
        "--plan-root",
        default=str(resolve_bellows_root()),
        help="Project root for resolving plan paths and the scope_check (default: bellows root)",
    )
    args = parser.parse_args(argv)

    db_uri = f"file:{args.db}?mode=ro"
    conn = sqlite3.connect(db_uri, uri=True)

    tables = {
        row[0]
        for row in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
    }
    if "step_files" not in tables:
        print(
            "step_files: table absent — the daemon has not restarted since the plan"
            " that added it; nothing to replay"
        )
        conn.close()
        return 0

    rows = conn.execute(
        "SELECT s.id, s.plan_id, s.step_number, p.plan_doc_ref"
        " FROM steps s JOIN plans p ON p.id = s.plan_id"
        " WHERE s.id IN (SELECT DISTINCT step_id FROM step_files)"
        " ORDER BY s.plan_id, s.step_number"
    ).fetchall()

    flips = []
    for step_id, plan_id, step_number, plan_doc_ref in rows:
        files = [
            r[0]
            for r in conn.execute(
                "SELECT path FROM step_files WHERE step_id = ? ORDER BY path", (step_id,)
            ).fetchall()
        ]

        recorded_rows = conn.execute(
            "SELECT result FROM gate_events WHERE step_id = ? AND gate_name = 'scope_check'",
            (step_id,),
        ).fetchall()
        if not recorded_rows:
            recorded = "none"
        elif any(r[0] == "fail" for r in recorded_rows):
            recorded = "fail"
        else:
            recorded = "pass"

        plan_text = _resolve_plan_text(plan_id, plan_doc_ref, args.plan_root)
        if plan_text is None:
            print(f"{plan_id}/{step_number}: plan text not found")
            continue

        now_failures = []
        gates._gate_scope_check(
            plan_text, step_number, files, now_failures, project_path=args.plan_root
        )
        now = "fail" if now_failures else "pass"

        print(f"{plan_id}/{step_number}: recorded={recorded} now={now}")

        if recorded != "none" and recorded != now:
            flips.append((plan_id, step_number))

    print(f"FLIPS: {len(flips)}")
    for plan_id, step_number in flips:
        print(f"  {plan_id}/{step_number}")

    conn.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
