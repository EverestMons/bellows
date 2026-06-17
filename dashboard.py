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
import glob as glob_mod
import re
import signal
import subprocess
import sys
import time
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

# Color pair IDs (only valid after init_colors())
COLOR_HEADER_RUN = 1
COLOR_HEADER_STOP = 2
COLOR_INFLIGHT = 3
COLOR_AWAITING = 4

# Separator character
SEPARATOR_CHAR = "\u2500"  # ─ box-drawing horizontal

# Log line filter: exclude Module fingerprint lines
_MODULE_FINGERPRINT_RE = re.compile(r"Module:.*@ git:")


def init_colors():
    """Initialize curses color pairs. Returns True if colors available."""
    if not curses.has_colors():
        return False
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(COLOR_HEADER_RUN, curses.COLOR_GREEN, -1)
    curses.init_pair(COLOR_HEADER_STOP, curses.COLOR_RED, -1)
    curses.init_pair(COLOR_INFLIGHT, curses.COLOR_CYAN, -1)
    curses.init_pair(COLOR_AWAITING, curses.COLOR_YELLOW, -1)
    return True


# ---------------------------------------------------------------------------
# Log tail + feed filter
# ---------------------------------------------------------------------------

def tail_session_log(log_dir, max_lines=20):
    """Read the last max_lines from the most recently modified session log.

    Selects the bellows-*.log file with the greatest mtime in log_dir.
    Returns list of strings (no trailing newlines), or None if no log exists.
    """
    try:
        candidates = glob_mod.glob(os.path.join(log_dir, "bellows-*.log"))
    except OSError:
        return None
    if not candidates:
        return None
    newest = max(candidates, key=os.path.getmtime)
    return _tail_file(newest, max_lines)


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

def render_screen(state, height, width, mode="normal", has_colors=False):
    """Pure function: state → list of (text, attr) tuples (one per terminal row).

    Args:
        state: dict from assemble_state().
        height: terminal rows.
        width: terminal columns.
        mode: "normal", "confirm_restart", or "confirm_quit".
        has_colors: True if curses color pairs are initialized.

    Returns list of (text, attr) tuples, len == height.
    Each text is <= width chars; attr is a curses attribute bitmask.
    """
    # Minimum size check
    if height < MIN_ROWS or width < MIN_COLS:
        lines = [("", 0)] * height
        msg = f"Terminal too small (need {MIN_COLS}x{MIN_ROWS})"
        mid = height // 2
        pad = max(0, (width - len(msg)) // 2)
        lines[mid] = (" " * pad + msg, 0)
        return lines

    # Build attribute palette based on color availability.
    # color_pair(n) == n << 8; computed directly so render_screen stays pure
    # (curses.color_pair() requires initscr()).
    if has_colors:
        attr_header_run = curses.A_BOLD | (COLOR_HEADER_RUN << 8)
        attr_header_stop = curses.A_BOLD | (COLOR_HEADER_STOP << 8)
        attr_inflight = curses.A_BOLD | (COLOR_INFLIGHT << 8)
        attr_awaiting = curses.A_BOLD | (COLOR_AWAITING << 8)
        attr_awaiting_row = COLOR_AWAITING << 8
        attr_feed_header = curses.A_DIM
        attr_separator = curses.A_DIM
        attr_footer = curses.A_REVERSE
    else:
        attr_header_run = curses.A_BOLD
        attr_header_stop = curses.A_BOLD
        attr_inflight = curses.A_BOLD
        attr_awaiting = curses.A_BOLD | curses.A_REVERSE
        attr_awaiting_row = curses.A_REVERSE
        attr_feed_header = curses.A_DIM
        attr_separator = curses.A_DIM
        attr_footer = curses.A_BOLD

    rows = []

    # --- Header (row 0) ---
    if state["child_alive"] or state["daemon_running"]:
        header = status.render_daemon_header(
            True, state["pid"], state["sha"], state["uptime"]
        )
        rows.append((_fit(header, width), attr_header_run))
    else:
        if state["child_exit_code"] is not None:
            header = f"\u25cb Bellows STOPPED (exited, code {state['child_exit_code']})"
        else:
            header = status.render_daemon_header(False, None, state["sha"], None)
        rows.append((_fit(header, width), attr_header_stop))

    # --- Separator ---
    rows.append((SEPARATOR_CHAR * width, attr_separator))

    # --- IN-FLIGHT ---
    if state["db_absent"]:
        in_flight_text = "IN-FLIGHT\n (no database)"
    else:
        in_flight_text = status.render_in_flight(
            state["in_flight_rows"], state["daemon_running"]
        )
    in_flight_lines = in_flight_text.split("\n")
    rows.append((_fit(in_flight_lines[0], width), attr_inflight))
    for line in in_flight_lines[1:]:
        rows.append((_fit(line, width), 0))

    # --- Separator ---
    rows.append((SEPARATOR_CHAR * width, attr_separator))

    # --- AWAITING VERDICT ---
    if state["db_absent"]:
        awaiting_text = "AWAITING VERDICT\n (no database)"
    else:
        awaiting_text = status.render_awaiting_verdict(state["awaiting_rows"])
    awaiting_lines = awaiting_text.split("\n")
    has_awaiting = bool(state["awaiting_rows"]) and not state["db_absent"]
    rows.append((_fit(awaiting_lines[0], width), attr_awaiting))
    for line in awaiting_lines[1:]:
        rows.append((_fit(line, width), attr_awaiting_row if has_awaiting else 0))

    # --- Separator ---
    rows.append((SEPARATOR_CHAR * width, attr_separator))

    # --- EVENT FEED (fills remaining space above footer) ---
    feed_start = len(rows)
    feed_available = height - feed_start - 1  # -1 for footer

    rows.append((_fit("EVENT FEED", width), attr_feed_header))
    feed_available -= 1  # label row consumed

    if state["log_absent"]:
        rows.append((_fit(" (no log file)", width), 0))
        feed_available -= 1
    elif not state["feed_lines"]:
        rows.append((_fit(" (none)", width), 0))
        feed_available -= 1
    else:
        # Show as many feed lines as fit, most recent at bottom
        visible = state["feed_lines"][-feed_available:] if feed_available > 0 else []
        for line in visible:
            rows.append((_fit(" " + line, width), 0))
            feed_available -= 1

    # Fill remaining space with empty rows
    while feed_available > 0:
        rows.append(("", 0))
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
    rows.append((_fit(footer, width), attr_footer))

    # Ensure exactly `height` rows
    while len(rows) < height:
        rows.insert(-1, ("", 0))  # insert empties before footer
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
        self._has_colors = init_colors()
        stdscr.clear()

        self._spawn_child()

        while True:
            # Get terminal size
            height, width = stdscr.getmaxyx()

            # Assemble state and render
            state = assemble_state(self.bellows_root, self.child)
            lines = render_screen(state, height, width, self.mode, self._has_colors)

            # Draw
            stdscr.erase()
            for i, (text, attr) in enumerate(lines):
                try:
                    stdscr.addnstr(i, 0, text, width, attr)
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
