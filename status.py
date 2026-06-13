"""Single-glance status CLI — read-only observer of Bellows lifecycle state.

Renders exactly three elements: daemon header, IN-FLIGHT, AWAITING VERDICT.
All DB access is read-only (?mode=ro). Never imports daemon internals.
"""

import datetime
import fcntl
import os
import sqlite3
import subprocess
import sys
from pathlib import Path

from bellows_root import resolve_bellows_root


# ---------------------------------------------------------------------------
# Daemon liveness helpers
# ---------------------------------------------------------------------------

def probe_daemon(lock_path):
    """Returns True if daemon is running (lock held), False if stopped."""
    if not os.path.exists(lock_path):
        return False
    fd = os.open(lock_path, os.O_RDONLY)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        fcntl.flock(fd, fcntl.LOCK_UN)
        return False
    except (BlockingIOError, OSError):
        return True
    finally:
        os.close(fd)


def get_daemon_pid(lock_path):
    """Best-effort PID from lsof. Returns int or None."""
    try:
        result = subprocess.run(
            ["lsof", "-t", lock_path],
            capture_output=True, text=True, timeout=5
        )
        pids = result.stdout.strip().splitlines()
        return int(pids[0]) if pids else None
    except Exception:
        return None


def get_uptime(pid):
    """Process start time -> uptime string. Returns str or None."""
    try:
        result = subprocess.run(
            ["ps", "-o", "lstart=", "-p", str(pid)],
            capture_output=True, text=True, timeout=5
        )
        start_str = result.stdout.strip()
        if not start_str:
            return None
        start = datetime.datetime.strptime(start_str, "%c")
        delta = datetime.datetime.now() - start
        hours, remainder = divmod(int(delta.total_seconds()), 3600)
        minutes = remainder // 60
        if hours > 0:
            return f"{hours}h {minutes:02d}m"
        return f"{minutes}m"
    except Exception:
        return None


def get_sha(bellows_root):
    """Git short SHA of most recent bellows.py commit."""
    try:
        result = subprocess.run(
            ["git", "log", "-1", "--format=%h", "--", "bellows.py"],
            capture_output=True, text=True, timeout=5,
            cwd=str(bellows_root)
        )
        return result.stdout.strip() or None
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Formatting helpers
# ---------------------------------------------------------------------------

def format_elapsed(iso_str):
    """ISO timestamp -> elapsed string like '4m' or '2h 16m'."""
    if not iso_str:
        return "\u2014"
    try:
        start = datetime.datetime.fromisoformat(iso_str)
        delta = datetime.datetime.now() - start
        total_seconds = max(0, int(delta.total_seconds()))
        hours, remainder = divmod(total_seconds, 3600)
        minutes = remainder // 60
        if hours > 0:
            return f"{hours}h {minutes:02d}m"
        return f"{minutes}m"
    except (ValueError, TypeError):
        return "\u2014"


def truncate(text, max_len):
    """Truncate text with ellipsis if too long."""
    if not text:
        return ""
    if len(text) <= max_len:
        return text
    return text[: max_len - 1] + "\u2026"


# ---------------------------------------------------------------------------
# Section renderers
# ---------------------------------------------------------------------------

def render_daemon_header(running, pid, sha, uptime):
    """Render the daemon status header line."""
    if not running:
        return "\u25cb Bellows STOPPED"
    parts = ["\u25cf Bellows RUNNING"]
    parts.append(f"pid {pid}" if pid else "pid \u2014")
    parts.append(f"sha {sha}" if sha else "sha \u2014")
    parts.append(f"up {uptime}" if uptime else "up \u2014")
    return "  ".join(parts)


def _project_name(target_project):
    """Extract short project name from a target_project value (may be a path)."""
    if not target_project:
        return "\u2014"
    # Strip trailing slashes and take the last path component
    name = target_project.rstrip("/").rsplit("/", 1)[-1]
    return name or target_project


def render_in_flight(rows, daemon_running):
    """Render IN-FLIGHT section."""
    lines = ["IN-FLIGHT"]
    if not rows:
        lines.append(" (none)")
        return "\n".join(lines)
    for row in rows:
        plan_id = row["id"]
        ptype = row["type"] if row["type"] else None
        project = truncate(_project_name(row["target_project"]), 8)
        step_num = row["step_number"] if row["step_number"] is not None else "\u2014"
        total = row["total_steps"] if row["total_steps"] is not None else "?"
        status = row["status"] or "pending"
        if not daemon_running and status == "running":
            status = "stale?"
        elapsed = format_elapsed(row["step_started_at"])
        title = truncate(row["title"] or "", 38)
        id_label = f"{ptype} #{plan_id}" if ptype else f"#{plan_id}"
        lines.append(
            f" {id_label}  {project:<8s}  Step {step_num}/{total}"
            f"  {status:<8s}  {elapsed:<5s} {title}"
        )
    return "\n".join(lines)


def render_awaiting_verdict(rows):
    """Render AWAITING VERDICT section."""
    lines = ["AWAITING VERDICT"]
    if not rows:
        lines.append(" (none)")
        return "\n".join(lines)
    for row in rows:
        plan_id = row["plan_id"]
        ptype = row["type"] if row["type"] else None
        step = row["step_number"]
        reason = row["pause_reason_code"] or "\u2014"
        filename = row["verdict_file_ref"] or "\u2014"
        pause_time = row["pause_time"]
        elapsed = format_elapsed(pause_time)
        id_label = f"{ptype} #{plan_id}" if ptype else f"#{plan_id}"
        lines.append(
            f" {id_label}  step {step}  {reason}  {filename}  {elapsed}"
        )
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# DB query helpers (importable — all read-only, ?mode=ro)
# ---------------------------------------------------------------------------

def query_in_flight(db_path):
    """Return in-flight plan rows from lifecycle.db. Returns list of Row dicts."""
    db_uri = f"file:{db_path}?mode=ro"
    conn = sqlite3.connect(db_uri, uri=True)
    conn.row_factory = sqlite3.Row
    rows = conn.execute("""
        SELECT p.id, p.type, p.target_project, p.title, p.total_steps,
               s.step_number, s.status, s.step_started_at
        FROM plans p
        LEFT JOIN steps s ON s.plan_id = p.id
          AND s.step_number = (
            SELECT MAX(s2.step_number) FROM steps s2
            WHERE s2.plan_id = p.id AND s2.status IN ('running', 'awaiting_verdict')
          )
        WHERE p.lifecycle_state IN ('in_progress', 'claimed')
        ORDER BY p.id
    """).fetchall()
    conn.close()
    return rows


def query_awaiting_verdict(db_path):
    """Return awaiting-verdict rows from lifecycle.db. Returns list of Row dicts."""
    db_uri = f"file:{db_path}?mode=ro"
    conn = sqlite3.connect(db_uri, uri=True)
    conn.row_factory = sqlite3.Row
    rows = conn.execute("""
        SELECT v.plan_id, p.type, v.step_number, v.pause_reason_code, v.verdict_file_ref,
               COALESCE(s.step_ended_at, s.step_started_at) AS pause_time
        FROM verdicts v
        LEFT JOIN plans p ON p.id = v.plan_id
        LEFT JOIN steps s ON s.plan_id = v.plan_id AND s.step_number = v.step_number
        WHERE v.outcome IS NULL
        ORDER BY v.plan_id
    """).fetchall()
    conn.close()
    return rows


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    bellows_root = resolve_bellows_root()
    db_path = bellows_root / "lifecycle.db"
    lock_path = bellows_root / ".bellows.lock"

    # Absent-DB degradation
    if not db_path.exists():
        print("\u25cb Bellows STOPPED  (no lifecycle.db)")
        print()
        print(f"No data available \u2014 lifecycle.db not found at {db_path}.")
        print("Run the daemon at least once to initialize the database.")
        return

    daemon_running = probe_daemon(str(lock_path))

    # Daemon header
    pid = None
    sha = get_sha(bellows_root)
    uptime = None
    if daemon_running:
        pid = get_daemon_pid(str(lock_path))
        if pid:
            uptime = get_uptime(pid)
    print(render_daemon_header(daemon_running, pid, sha, uptime))
    print()

    in_flight = query_in_flight(str(db_path))
    print(render_in_flight(in_flight, daemon_running))
    print()

    awaiting = query_awaiting_verdict(str(db_path))
    print(render_awaiting_verdict(awaiting))

    conn = None  # no longer held open


if __name__ == "__main__":
    main()
