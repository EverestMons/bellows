"""Bellows Dashboard TUI — daemon-owning wrapper with restart key.

Full-screen terminal dashboard that owns the bellows.py daemon process.
Renders daemon header, IN-FLIGHT, AWAITING VERDICT, and a live EVENT FEED
from the session log. Supports `r` to restart the daemon and `q` to quit.

All DB access is read-only (?mode=ro) via status.py query functions.
The dashboard never acquires .bellows.lock — only .bellows-dashboard.lock.
"""

import curses
import fcntl
import os
import re
import signal
import subprocess
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

from bellows_root import resolve_bellows_root
import status

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

MIN_ROWS = 24
MIN_COLS = 80
REFRESH_HALF_DELAY = 20  # curses halfdelay units (tenths of second) = 2s
FLOCK_RETRY_LIMIT = 10
FLOCK_RETRY_INTERVAL = 0.5
SIGTERM_TIMEOUT = 5
SIGKILL_TIMEOUT = 2

# Log line filter: exclude Module fingerprint lines
_MODULE_FINGERPRINT_RE = re.compile(r"Module:.*@ git:")


# ---------------------------------------------------------------------------
# Log tail + feed filter
# ---------------------------------------------------------------------------

def tail_session_log(log_dir, max_lines=20):
    """Read the last max_lines from today's session log.

    Midnight rotation tolerance: if today's file doesn't exist yet,
    fall back to yesterday's file for up to 60 seconds past midnight.
    Returns list of strings (no trailing newlines).
    """
    today = datetime.now()
    today_name = f"bellows-{today.strftime('%Y-%m-%d')}.log"
    today_path = os.path.join(log_dir, today_name)

    if os.path.isfile(today_path):
        return _tail_file(today_path, max_lines)

    # Midnight tolerance: fall back to yesterday's log within 60s of midnight
    if today.hour == 0 and today.minute == 0 and today.second < 60:
        yesterday = today - timedelta(days=1)
        yesterday_name = f"bellows-{yesterday.strftime('%Y-%m-%d')}.log"
        yesterday_path = os.path.join(log_dir, yesterday_name)
        if os.path.isfile(yesterday_path):
            return _tail_file(yesterday_path, max_lines)

    return None  # no log file


def _tail_file(path, max_lines):
    """Read last max_lines from a text file."""
    try:
        with open(path, "r") as f:
            lines = f.readlines()
        return [line.rstrip("\n") for line in lines[-max_lines:]]
    except OSError:
        return None


def filter_feed_lines(lines):
    """Filter log lines: keep all except Module fingerprint lines."""
    if not lines:
        return []
    return [line for line in lines if not _MODULE_FINGERPRINT_RE.search(line)]


# ---------------------------------------------------------------------------
# State assembly (pure data — no rendering)
# ---------------------------------------------------------------------------

def assemble_state(bellows_root, child_proc=None):
    """Gather all dashboard data into a state snapshot dict.

    Args:
        bellows_root: Path to bellows root directory.
        child_proc: subprocess.Popen instance (or None if no child managed).

    Returns dict with keys: daemon_running, pid, sha, uptime,
    in_flight_rows, awaiting_rows, feed_lines, child_alive, child_exit_code,
    db_absent, log_absent.
    """
    lock_path = str(bellows_root / ".bellows.lock")
    db_path = bellows_root / "lifecycle.db"
    log_dir = str(bellows_root / "logs" / "terminal")

    # Child process status
    child_alive = False
    child_exit_code = None
    if child_proc is not None:
        rc = child_proc.poll()
        if rc is None:
            child_alive = True
        else:
            child_exit_code = rc

    # Daemon liveness (via flock probe — works whether we own the child or not)
    daemon_running = status.probe_daemon(lock_path)

    # Header data
    pid = None
    sha = status.get_sha(bellows_root)
    uptime = None
    if daemon_running:
        pid = status.get_daemon_pid(lock_path)
        if pid:
            uptime = status.get_uptime(pid)

    # DB queries
    db_absent = not db_path.exists()
    in_flight_rows = []
    awaiting_rows = []
    if not db_absent:
        try:
            in_flight_rows = status.query_in_flight(str(db_path))
            awaiting_rows = status.query_awaiting_verdict(str(db_path))
        except Exception:
            db_absent = True

    # Log tail
    raw_lines = tail_session_log(log_dir)
    log_absent = raw_lines is None
    feed_lines = filter_feed_lines(raw_lines) if raw_lines else []

    return {
        "daemon_running": daemon_running,
        "pid": pid,
        "sha": sha,
        "uptime": uptime,
        "in_flight_rows": in_flight_rows,
        "awaiting_rows": awaiting_rows,
        "feed_lines": feed_lines,
        "child_alive": child_alive,
        "child_exit_code": child_exit_code,
        "db_absent": db_absent,
        "log_absent": log_absent,
    }


# ---------------------------------------------------------------------------
# Pure render layer: state + dimensions + mode → list of strings
# ---------------------------------------------------------------------------

def render_screen(state, height, width, mode="normal"):
    """Pure function: state → list of strings (one per terminal row).

    Args:
        state: dict from assemble_state().
        height: terminal rows.
        width: terminal columns.
        mode: "normal", "confirm_restart", or "confirm_quit".

    Returns list of strings, len == height. Each string is <= width chars.
    """
    # Minimum size check
    if height < MIN_ROWS or width < MIN_COLS:
        lines = [""] * height
        msg = f"Terminal too small (need {MIN_COLS}x{MIN_ROWS})"
        mid = height // 2
        pad = max(0, (width - len(msg)) // 2)
        lines[mid] = " " * pad + msg
        return lines

    rows = []

    # --- Header (row 0) ---
    if state["child_alive"] or state["daemon_running"]:
        header = status.render_daemon_header(
            True, state["pid"], state["sha"], state["uptime"]
        )
    else:
        if state["child_exit_code"] is not None:
            header = f"\u25cb Bellows STOPPED (exited, code {state['child_exit_code']})"
        else:
            header = status.render_daemon_header(False, None, state["sha"], None)
    rows.append(_fit(header, width))

    # --- Blank separator ---
    rows.append("")

    # --- IN-FLIGHT ---
    if state["db_absent"]:
        in_flight_text = "IN-FLIGHT\n (no database)"
    else:
        in_flight_text = status.render_in_flight(
            state["in_flight_rows"], state["daemon_running"]
        )
    for line in in_flight_text.split("\n"):
        rows.append(_fit(line, width))

    # --- Blank separator ---
    rows.append("")

    # --- AWAITING VERDICT ---
    if state["db_absent"]:
        awaiting_text = "AWAITING VERDICT\n (no database)"
    else:
        awaiting_text = status.render_awaiting_verdict(state["awaiting_rows"])
    for line in awaiting_text.split("\n"):
        rows.append(_fit(line, width))

    # --- Blank separator ---
    rows.append("")

    # --- EVENT FEED (fills remaining space above footer) ---
    # Reserve 1 row for footer (last row)
    feed_start = len(rows)
    feed_available = height - feed_start - 1  # -1 for footer

    rows.append(_fit("EVENT FEED", width))
    feed_available -= 1  # label row consumed

    if state["log_absent"]:
        rows.append(_fit(" (no log file)", width))
        feed_available -= 1
    elif not state["feed_lines"]:
        rows.append(_fit(" (none)", width))
        feed_available -= 1
    else:
        # Show as many feed lines as fit, most recent at bottom
        visible = state["feed_lines"][-feed_available:] if feed_available > 0 else []
        for line in visible:
            rows.append(_fit(" " + line, width))
            feed_available -= 1

    # Fill remaining space with empty rows
    while feed_available > 0:
        rows.append("")
        feed_available -= 1

    # --- Footer (pinned to last row) ---
    if mode == "confirm_restart":
        footer = "Restart daemon? (y/n)"
    elif mode == "confirm_quit":
        footer = "Quit dashboard and stop daemon? (y/n)"
    else:
        daemon_up = state["child_alive"] or state["daemon_running"]
        if daemon_up:
            footer = "r restart  q quit"
        else:
            footer = "r relaunch  q quit"
    rows.append(_fit(footer, width))

    # Ensure exactly `height` rows
    while len(rows) < height:
        rows.insert(-1, "")  # insert empties before footer
    rows = rows[:height]

    return rows


def _fit(text, width):
    """Truncate a string to fit within width."""
    if len(text) <= width:
        return text
    return text[: width - 1] + "\u2026"


# ---------------------------------------------------------------------------
# Curses shell — thin wrapper, all logic in pure functions
# ---------------------------------------------------------------------------

class CursesShell:
    """Thin curses wrapper that owns the daemon child process."""

    def __init__(self, bellows_root=None):
        self.bellows_root = bellows_root or resolve_bellows_root()
        self.child = None
        self.mode = "normal"  # normal | confirm_restart | confirm_quit
        self.dashboard_lock_fd = None

    def run(self):
        """Entry point — acquire dashboard lock, then enter curses."""
        self._acquire_dashboard_lock()
        try:
            curses.wrapper(self._main_loop)
        finally:
            self._release_dashboard_lock()

    def _acquire_dashboard_lock(self):
        lock_path = str(self.bellows_root / ".bellows-dashboard.lock")
        self.dashboard_lock_fd = open(lock_path, "w")
        try:
            fcntl.flock(self.dashboard_lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except (BlockingIOError, OSError):
            self.dashboard_lock_fd.close()
            self.dashboard_lock_fd = None
            print("Another dashboard instance is already running")
            sys.exit(1)

    def _release_dashboard_lock(self):
        if self.dashboard_lock_fd:
            try:
                fcntl.flock(self.dashboard_lock_fd, fcntl.LOCK_UN)
                self.dashboard_lock_fd.close()
            except OSError:
                pass

    def _spawn_child(self):
        """Spawn bellows.py as a subprocess."""
        self.child = subprocess.Popen(
            [sys.executable, "bellows.py"],
            cwd=str(self.bellows_root),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL,
        )

    def _terminate_child(self):
        """SIGTERM → wait → SIGKILL if needed. Returns True if child is dead."""
        if self.child is None:
            return True
        if self.child.poll() is not None:
            return True
        self.child.terminate()
        try:
            self.child.wait(timeout=SIGTERM_TIMEOUT)
            return True
        except subprocess.TimeoutExpired:
            self.child.kill()
            try:
                self.child.wait(timeout=SIGKILL_TIMEOUT)
                return True
            except subprocess.TimeoutExpired:
                return False

    def _wait_for_lock_release(self):
        """Poll until .bellows.lock is free. Returns True if released."""
        lock_path = str(self.bellows_root / ".bellows.lock")
        for _ in range(FLOCK_RETRY_LIMIT):
            if not status.probe_daemon(lock_path):
                return True
            time.sleep(FLOCK_RETRY_INTERVAL)
        return False

    def _do_restart(self, stdscr):
        """Restart sequence: terminate → wait for lock → respawn."""
        self._terminate_child()
        if not self._wait_for_lock_release():
            # Lock not released — don't respawn
            self.mode = "normal"
            return
        self._spawn_child()
        self.mode = "normal"

    def _do_quit(self):
        """Quit sequence: terminate child, exit."""
        self._terminate_child()
        if self.child:
            try:
                self.child.wait(timeout=2)
            except subprocess.TimeoutExpired:
                pass

    def _main_loop(self, stdscr):
        """Curses main loop: refresh every ~2s, handle keys."""
        curses.curs_set(0)  # hide cursor
        curses.halfdelay(REFRESH_HALF_DELAY)
        stdscr.clear()

        self._spawn_child()

        while True:
            # Get terminal size
            height, width = stdscr.getmaxyx()

            # Assemble state and render
            state = assemble_state(self.bellows_root, self.child)
            lines = render_screen(state, height, width, self.mode)

            # Draw
            stdscr.erase()
            for i, line in enumerate(lines):
                try:
                    stdscr.addnstr(i, 0, line, width)
                except curses.error:
                    pass  # last-cell write can raise on some terminals
            stdscr.refresh()

            # Wait for key (or timeout after ~2s)
            try:
                key = stdscr.getch()
            except curses.error:
                key = -1

            if key == curses.KEY_RESIZE:
                stdscr.clear()
                continue

            if key == -1:
                # Timeout — just refresh
                continue

            # Handle key based on mode
            if self.mode == "normal":
                if key in (ord("r"), ord("R")):
                    self.mode = "confirm_restart"
                elif key in (ord("q"), ord("Q")):
                    self.mode = "confirm_quit"
            elif self.mode == "confirm_restart":
                if key in (ord("y"), ord("Y")):
                    self._do_restart(stdscr)
                else:
                    self.mode = "normal"
            elif self.mode == "confirm_quit":
                if key in (ord("y"), ord("Y")):
                    self._do_quit()
                    return  # exit curses
                else:
                    self.mode = "normal"


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    shell = CursesShell()
    shell.run()


if __name__ == "__main__":
    main()
