#!/usr/bin/env python3
"""gate_watcher — session-independent watcher for one deposited plan.

Spawned detached by tools/deposit_receipt.py at deposit time (or run by
hand). Polls lifecycle.db READ-ONLY; appends state transitions and
un-overridden gate failures to logs/watch/<name>.log; exits on a terminal
lifecycle state or timeout. The watcher is a REPORTER, never an actor —
it writes no DB row and touches no plan file.

The deposit receipt attests ARMING; this process is the armed thing. Its
log is the watcher's own output file: every line records a direct DB read
(the async-notifications-are-claims law, mechanized — the log IS the
stable state query).

usage: gate_watcher.py <claimable-name.md> [--timeout-min N] [--interval-sec N]
       gate_watcher.py --status <claimable-name.md>

exit: 0 terminal state reached (or --status printed); 2 usage; 3 timeout.
"""
import argparse
import os
import sqlite3
import sys
import time
from datetime import datetime

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
_DB = os.path.join(_ROOT, "lifecycle.db")
_WATCH_DIR = os.path.join(_ROOT, "logs", "watch")

TERMINAL = {"closed", "halted", "abandoned"}


def read_state(name, db_path=None):
    """One read-only DB query -> state dict, or None if the DB is unreadable."""
    path = db_path or _DB
    try:
        conn = sqlite3.connect(f"file:{path}?mode=ro", uri=True, timeout=5)
    except sqlite3.Error:
        return None
    try:
        row = conn.execute(
            "SELECT id, lifecycle_state FROM plans "
            "WHERE deposit_placeholder_name = ? ORDER BY id DESC LIMIT 1",
            (name,),
        ).fetchone()
        if row is None:
            return {"phase": "pre-claim"}
        plan_id, state = row
        fails = conn.execute(
            "SELECT g.gate_name FROM gate_events g "
            "JOIN steps s ON g.step_id = s.id "
            "WHERE s.plan_id = ? AND g.result = 'fail' AND g.overridden = 0",
            (plan_id,),
        ).fetchall()
        return {
            "phase": state,
            "plan_id": plan_id,
            "gate_failures": sorted(f[0] for f in fails),
        }
    except sqlite3.Error:
        return None
    finally:
        conn.close()


def judge_transition(prev, cur):
    """(prev_state, cur_state) -> log line, or None when nothing changed.

    A db-unreadable poll is REPORTED (transient or not, silence would be
    indistinguishable from 'no change' — silence is not success).
    """
    if cur is None:
        return "WATCH: db-unreadable (will retry)"
    if prev is not None and prev == cur:
        return None
    gf = cur.get("gate_failures") or []
    tail = " gate_failures=" + ",".join(gf) if gf else ""
    pid_part = f" id={cur['plan_id']}" if "plan_id" in cur else ""
    return f"WATCH: {cur['phase']}{pid_part}{tail}"


def _log_line(log_path, line):
    stamped = f"{datetime.now().isoformat()} {line}\n"
    with open(log_path, "a") as f:
        f.write(stamped)


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("name")
    ap.add_argument("--timeout-min", type=int, default=120)
    ap.add_argument("--interval-sec", type=int, default=15)
    ap.add_argument("--status", action="store_true")
    ap.add_argument("--db-path", default=None,
                    help="lifecycle.db path (default: beside this tool's bellows root; "
                         "worktrees have no lifecycle.db — pass the live checkout's)")
    try:
        args = ap.parse_args(argv[1:])
    except SystemExit:
        return 2

    if args.status:
        cur = read_state(args.name, db_path=args.db_path)
        line = judge_transition(None, cur) or "WATCH: (no state)"
        print(line)
        return 0

    os.makedirs(_WATCH_DIR, exist_ok=True)
    log_path = os.path.join(_WATCH_DIR, args.name + ".log")
    _log_line(log_path, f"WATCH: armed for {args.name} "
                        f"(timeout {args.timeout_min}m, interval {args.interval_sec}s)")
    deadline = time.monotonic() + args.timeout_min * 60
    prev = "UNSET"
    while time.monotonic() < deadline:
        cur = read_state(args.name, db_path=args.db_path)
        line = judge_transition(None if prev == "UNSET" else prev, cur)
        if line:
            _log_line(log_path, line)
        if cur is not None:
            prev = cur
            if cur.get("phase") in TERMINAL:
                _log_line(log_path, f"WATCH: terminal — {cur['phase']}; exiting")
                return 0
        time.sleep(args.interval_sec)
    _log_line(log_path, "WATCH: timeout; exiting")
    return 3


if __name__ == "__main__":
    sys.exit(main(sys.argv))
