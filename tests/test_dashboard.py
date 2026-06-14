"""Tests for dashboard.py — headless render layer + PTY smoke."""

import curses
import datetime
import os
import sqlite3
import sys
import textwrap

import pytest

import dashboard
import status
from lifecycle import init_lifecycle_db


def _texts(rows):
    """Extract text strings from (text, attr) rows."""
    return [t for t, _ in rows]


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _make_state(**overrides):
    """Build a default state dict, with overrides."""
    base = {
        "daemon_running": True,
        "pid": 17920,
        "sha": "6274d1a",
        "uptime": "6m",
        "in_flight_rows": [],
        "awaiting_rows": [],
        "feed_lines": [],
        "child_alive": True,
        "child_exit_code": None,
        "db_absent": False,
        "log_absent": False,
    }
    base.update(overrides)
    return base


@pytest.fixture
def running_db(tmp_path):
    """Create a lifecycle DB with an in-flight plan and an awaiting verdict."""
    db_path = str(tmp_path / "lifecycle.db")
    init_lifecycle_db(db_path)
    conn = sqlite3.connect(db_path)

    now = datetime.datetime.now()
    ten_min_ago = (now - datetime.timedelta(minutes=10)).isoformat()
    thirty_min_ago = (now - datetime.timedelta(minutes=30)).isoformat()

    conn.execute(
        "INSERT INTO plans (id, type, target_project, title, dispatch_mode, tier,"
        " lifecycle_state, total_steps, created_at)"
        " VALUES (33, 'executable', 'bellows', 'Bellows — Live Dashboard TUI', 'bellows', 'Medium',"
        " 'in_progress', 3, ?)",
        (thirty_min_ago,),
    )
    conn.execute(
        "INSERT INTO steps (plan_id, step_number, role, status, step_started_at)"
        " VALUES (33, 1, 'sa', 'running', ?)",
        (ten_min_ago,),
    )
    conn.execute(
        "INSERT INTO plans (id, type, target_project, title, dispatch_mode, tier,"
        " lifecycle_state, total_steps, created_at)"
        " VALUES (30, 'executable', 'forge', 'Some Other Plan', 'bellows', 'Small',"
        " 'awaiting_verdict', 2, ?)",
        (thirty_min_ago,),
    )
    conn.execute(
        "INSERT INTO steps (plan_id, step_number, role, status, step_started_at, step_ended_at)"
        " VALUES (30, 2, 'qa', 'awaiting_verdict', ?, ?)",
        (thirty_min_ago, ten_min_ago),
    )
    conn.execute(
        "INSERT INTO verdicts (plan_id, step_number, outcome, pause_reason_code, verdict_file_ref)"
        " VALUES (30, 2, NULL, 'qa_checkpoint', '/full/path/to/verdict-request-30-step-2.md')",
    )

    conn.execute("UPDATE id_sequence SET next_id = 40 WHERE id = 1")
    conn.commit()
    conn.close()
    return db_path


def _query_state(db_path, daemon_running=True):
    """Query the DB and return in_flight_rows and awaiting_rows."""
    in_flight = status.query_in_flight(db_path)
    awaiting = status.query_awaiting_verdict(db_path)
    return in_flight, awaiting


# ---------------------------------------------------------------------------
# Test 1: RUNNING state
# ---------------------------------------------------------------------------

class TestRenderRunningState:
    def test_running_header_and_panes(self, running_db):
        in_flight, awaiting = _query_state(running_db)
        state = _make_state(
            in_flight_rows=in_flight,
            awaiting_rows=awaiting,
            feed_lines=[
                "20:06:00 [EVENT] [executable-33] \u25b6 started",
                "20:06:59 [INFO] [executable-33] runner: 60s elapsed",
            ],
        )
        rows = dashboard.render_screen(state, 50, 120)
        lines = _texts(rows)

        assert len(rows) == 50
        assert "\u25cf Bellows RUNNING" in lines[0]
        assert "pid 17920" in lines[0]
        assert "sha 6274d1a" in lines[0]
        assert "up 6m" in lines[0]

        joined = "\n".join(lines)
        assert "IN-FLIGHT" in joined
        assert "#33" in joined
        assert "AWAITING VERDICT" in joined
        assert "EVENT FEED" in joined
        assert "r restart  q quit" in lines[-1]


# ---------------------------------------------------------------------------
# Test 2: STOPPED state
# ---------------------------------------------------------------------------

class TestRenderStoppedState:
    def test_stopped_header_and_stale(self, running_db):
        in_flight, awaiting = _query_state(running_db)
        state = _make_state(
            daemon_running=False,
            pid=None,
            uptime=None,
            child_alive=False,
            child_exit_code=1,
            in_flight_rows=in_flight,
            awaiting_rows=awaiting,
            feed_lines=["20:06:00 [EVENT] started"],
        )
        rows = dashboard.render_screen(state, 50, 120)
        lines = _texts(rows)

        assert "\u25cb Bellows STOPPED (exited, code 1)" in lines[0]
        joined = "\n".join(lines)
        assert "stale?" in joined
        assert "r relaunch  q quit" in lines[-1]


# ---------------------------------------------------------------------------
# Test 3: Confirm restart prompt
# ---------------------------------------------------------------------------

class TestRenderConfirmRestart:
    def test_confirm_restart_replaces_footer(self):
        state = _make_state(feed_lines=["20:06:00 [EVENT] started"])
        rows = dashboard.render_screen(state, 50, 120, mode="confirm_restart")
        lines = _texts(rows)

        assert "Restart daemon? (y/n)" in lines[-1]
        # Normal keybar should not appear
        assert "r restart" not in lines[-1]


# ---------------------------------------------------------------------------
# Test 4: Confirm quit prompt
# ---------------------------------------------------------------------------

class TestRenderConfirmQuit:
    def test_confirm_quit_replaces_footer(self):
        state = _make_state(feed_lines=["20:06:00 [EVENT] started"])
        rows = dashboard.render_screen(state, 50, 120, mode="confirm_quit")
        lines = _texts(rows)

        assert "Quit dashboard and stop daemon? (y/n)" in lines[-1]


# ---------------------------------------------------------------------------
# Test 5: Empty panes — all (none)
# ---------------------------------------------------------------------------

class TestRenderEmptyPanes:
    def test_all_none(self):
        state = _make_state(
            in_flight_rows=[],
            awaiting_rows=[],
            feed_lines=[],
        )
        rows = dashboard.render_screen(state, 50, 120)
        lines = _texts(rows)
        joined = "\n".join(lines)

        assert "(none)" in joined
        # IN-FLIGHT (none), AWAITING VERDICT (none), EVENT FEED (none)
        assert joined.count("(none)") == 3


# ---------------------------------------------------------------------------
# Test 6: DB absent
# ---------------------------------------------------------------------------

class TestRenderDbAbsent:
    def test_db_absent_shows_no_database(self):
        state = _make_state(db_absent=True)
        rows = dashboard.render_screen(state, 50, 120)
        lines = _texts(rows)
        joined = "\n".join(lines)

        assert "(no database)" in joined
        # Should appear in both IN-FLIGHT and AWAITING VERDICT
        assert joined.count("(no database)") == 2


# ---------------------------------------------------------------------------
# Test 7: Log absent
# ---------------------------------------------------------------------------

class TestRenderLogAbsent:
    def test_log_absent_shows_no_log_file(self):
        state = _make_state(log_absent=True, feed_lines=[])
        rows = dashboard.render_screen(state, 50, 120)
        lines = _texts(rows)
        joined = "\n".join(lines)

        assert "(no log file)" in joined


# ---------------------------------------------------------------------------
# Test 8: Minimum size check
# ---------------------------------------------------------------------------

class TestRenderMinimumSize:
    def test_too_small_shows_message(self):
        rows = dashboard.render_screen(_make_state(), 20, 60)
        lines = _texts(rows)

        joined = "\n".join(lines)
        assert "Terminal too small" in joined
        assert "need 80x24" in joined
        assert len(rows) == 20

    def test_exactly_minimum_renders_normal(self):
        rows = dashboard.render_screen(_make_state(), MIN_ROWS, MIN_COLS)
        lines = _texts(rows)
        joined = "\n".join(lines)
        assert "Terminal too small" not in joined
        assert "RUNNING" in joined


MIN_ROWS = dashboard.MIN_ROWS
MIN_COLS = dashboard.MIN_COLS


# ---------------------------------------------------------------------------
# Test 9: Feed filter
# ---------------------------------------------------------------------------

class TestFeedFilter:
    def test_passes_event_pause_error_warn_info(self):
        lines = [
            "20:01:12 [INFO] session restart",
            "20:05:58 [EVENT] detected plan",
            "20:06:00 [PAUSE] awaiting verdict",
            "20:06:01 [ERROR] something broke",
            "20:06:02 [WARN] low disk",
        ]
        result = dashboard.filter_feed_lines(lines)
        assert len(result) == 5
        assert result == lines

    def test_excludes_module_fingerprint(self):
        lines = [
            "20:01:12 [INFO] session restart",
            "20:01:13 [INFO] Module: bellows @ git: abc1234",
            "20:05:58 [EVENT] detected plan",
        ]
        result = dashboard.filter_feed_lines(lines)
        assert len(result) == 2
        assert "Module:" not in "\n".join(result)

    def test_empty_input(self):
        assert dashboard.filter_feed_lines([]) == []
        assert dashboard.filter_feed_lines(None) == []


# ---------------------------------------------------------------------------
# Test 10: Feed line truncation
# ---------------------------------------------------------------------------

class TestFeedLineTruncation:
    def test_long_lines_truncated_to_width(self):
        long_line = "20:06:00 [EVENT] " + "x" * 200
        state = _make_state(feed_lines=[long_line])
        rows = dashboard.render_screen(state, 50, 80)
        lines = _texts(rows)

        # Find the feed line (it'll have the event marker)
        feed_lines = [l for l in lines if "EVENT" in l and "FEED" not in l]
        assert len(feed_lines) == 1
        assert len(feed_lines[0]) <= 80


# ---------------------------------------------------------------------------
# Test 11: Verdict file ref shown as basename
# ---------------------------------------------------------------------------

class TestVerdictFileBasename:
    def test_verdict_ref_as_basename(self, running_db):
        _, awaiting = _query_state(running_db)
        state = _make_state(awaiting_rows=awaiting)
        rows = dashboard.render_screen(state, 50, 120)
        lines = _texts(rows)
        joined = "\n".join(lines)

        # The verdict_file_ref is stored as full path; render_awaiting_verdict
        # from status.py renders whatever is in the row. The spec says basename.
        # Check the basename appears in the output.
        assert "verdict-request-30-step-2.md" in joined


# ---------------------------------------------------------------------------
# Test 12: Event feed height fills remaining space
# ---------------------------------------------------------------------------

class TestEventFeedHeightFillsRemaining:
    def test_feed_expands_with_few_panes(self):
        """With minimal in-flight/awaiting, feed gets more rows."""
        state = _make_state(
            in_flight_rows=[],
            awaiting_rows=[],
            feed_lines=["line " + str(i) for i in range(30)],
        )
        lines_50 = _texts(dashboard.render_screen(state, 50, 120))
        lines_30 = _texts(dashboard.render_screen(state, 30, 120))

        # Count visible feed content lines (non-empty, containing "line ")
        feed_50 = [l for l in lines_50 if "line " in l]
        feed_30 = [l for l in lines_30 if "line " in l]
        assert len(feed_50) > len(feed_30)

    def test_feed_contracts_with_many_panes(self, running_db):
        """With many in-flight/awaiting rows, feed gets fewer rows than empty panes."""
        in_flight, awaiting = _query_state(running_db)
        # Duplicate in-flight rows to consume more vertical space
        many_in_flight = list(in_flight) * 4
        many_awaiting = list(awaiting) * 3
        feed = ["line " + str(i) for i in range(30)]
        state_with = _make_state(
            in_flight_rows=many_in_flight,
            awaiting_rows=many_awaiting,
            feed_lines=feed,
        )
        state_without = _make_state(
            in_flight_rows=[],
            awaiting_rows=[],
            feed_lines=feed,
        )
        # Use 30 rows so feed actually gets constrained
        lines_with = _texts(dashboard.render_screen(state_with, 30, 120))
        lines_without = _texts(dashboard.render_screen(state_without, 30, 120))

        feed_with = [l for l in lines_with if "line " in l]
        feed_without = [l for l in lines_without if "line " in l]
        assert len(feed_without) > len(feed_with)


# ---------------------------------------------------------------------------
# Test 13: PTY smoke test
# ---------------------------------------------------------------------------

class TestPTYSmoke:
    """Launch dashboard.py in a PTY with a mock bellows.py, verify clean exit."""

    def test_pty_launch_refresh_quit(self, tmp_path):
        import fcntl as fcntl_mod
        import pty
        import select
        import struct
        import subprocess as sp
        import termios
        import time as time_mod

        bellows_src = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        # Write a mock bellows.py that acquires the lock and sleeps
        mock_bellows = tmp_path / "bellows.py"
        mock_bellows.write_text(textwrap.dedent("""\
            import fcntl, os, time
            lock_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".bellows.lock")
            fd = open(lock_path, "w")
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            time.sleep(30)
        """))

        # Create minimal structure
        (tmp_path / "logs" / "terminal").mkdir(parents=True)
        log_file = tmp_path / "logs" / "terminal" / f"bellows-{datetime.datetime.now():%Y-%m-%d}.log"
        log_file.write_text("20:01:00 [INFO] test log line\n")
        (tmp_path / "config.json").write_text("{}")

        # Open PTY
        master_fd, slave_fd = pty.openpty()

        # Set terminal size to 50x120
        winsize = struct.pack("HHHH", 50, 120, 0, 0)
        fcntl_mod.ioctl(slave_fd, termios.TIOCSWINSZ, winsize)

        # Launch dashboard in subprocess on the slave PTY
        script = textwrap.dedent(f"""\
            import sys, os
            from pathlib import Path
            sys.path.insert(0, {bellows_src!r})
            os.chdir({str(tmp_path)!r})
            from dashboard import CursesShell
            shell = CursesShell(bellows_root=Path({str(tmp_path)!r}))
            shell.run()
        """)
        env = os.environ.copy()
        env["TERM"] = "xterm"
        proc = sp.Popen(
            [sys.executable, "-c", script],
            stdin=slave_fd,
            stdout=slave_fd,
            stderr=slave_fd,
            close_fds=True,
            env=env,
        )
        os.close(slave_fd)

        # Read PTY output — wait for dashboard to render
        deadline = time_mod.time() + 8
        output = b""
        while time_mod.time() < deadline:
            ready, _, _ = select.select([master_fd], [], [], 0.5)
            if ready:
                try:
                    chunk = os.read(master_fd, 4096)
                    if not chunk:
                        break
                    output += chunk
                    if b"Bellows" in output:
                        break
                except OSError:
                    break

        # Send 'q' then 'y' to quit — allow time for halfdelay refresh cycles
        try:
            time_mod.sleep(2.5)
            os.write(master_fd, b"q")
            time_mod.sleep(2.5)
            os.write(master_fd, b"y")
        except OSError:
            pass  # child may have exited already

        # Drain remaining PTY output
        while True:
            ready, _, _ = select.select([master_fd], [], [], 1.0)
            if ready:
                try:
                    chunk = os.read(master_fd, 4096)
                    if not chunk:
                        break
                except OSError:
                    break
            else:
                break

        # Wait for exit
        try:
            rc = proc.wait(timeout=10)
        except sp.TimeoutExpired:
            proc.kill()
            proc.wait()
            rc = -1
        finally:
            try:
                os.close(master_fd)
            except OSError:
                pass

        assert rc == 0, f"Dashboard exited with code {rc}, output: {output[:500]}"
        assert b"Bellows" in output, f"Dashboard header not found in PTY output: {output[:500]}"


# ---------------------------------------------------------------------------
# Test 14: Attributed rows — render_screen returns (text, attr) tuples
# ---------------------------------------------------------------------------

class TestAttributedRows:
    def test_returns_tuples(self):
        state = _make_state(feed_lines=["20:06:00 [EVENT] started"])
        rows = dashboard.render_screen(state, 50, 120)

        assert isinstance(rows, list)
        for row in rows:
            assert isinstance(row, tuple), f"Expected tuple, got {type(row)}: {row!r}"
            assert len(row) == 2
            text, attr = row
            assert isinstance(text, str)
            assert isinstance(attr, int)


# ---------------------------------------------------------------------------
# Test 15: Section headers carry bold attr
# ---------------------------------------------------------------------------

class TestSectionHeadersBold:
    def test_section_headers_bold(self):
        state = _make_state(feed_lines=["20:06:00 [EVENT] started"])
        rows = dashboard.render_screen(state, 50, 120)

        header_rows = {text: attr for text, attr in rows}
        # Find section header rows by text content
        for text, attr in rows:
            if text.startswith("IN-FLIGHT"):
                assert attr & curses.A_BOLD, "IN-FLIGHT header should be bold"
            elif text.startswith("AWAITING VERDICT"):
                assert attr & curses.A_BOLD, "AWAITING VERDICT header should be bold"

    def test_daemon_header_bold(self):
        state = _make_state()
        rows = dashboard.render_screen(state, 50, 120)
        _, attr = rows[0]
        assert attr & curses.A_BOLD, "Daemon header should be bold"


# ---------------------------------------------------------------------------
# Test 16: AWAITING VERDICT emphasis when rows exist
# ---------------------------------------------------------------------------

class TestAwaitingEmphasis:
    def test_awaiting_rows_emphasized(self, running_db):
        _, awaiting = _query_state(running_db)
        state = _make_state(awaiting_rows=awaiting)
        rows = dashboard.render_screen(state, 50, 120)

        # Find content rows after the AWAITING VERDICT header
        in_awaiting_section = False
        content_attrs = []
        for text, attr in rows:
            if text.startswith("AWAITING VERDICT"):
                in_awaiting_section = True
                continue
            if in_awaiting_section:
                if dashboard.SEPARATOR_CHAR in text or text.startswith("EVENT FEED"):
                    break
                if text.strip():
                    content_attrs.append(attr)

        assert content_attrs, "Should have awaiting content rows"
        for attr in content_attrs:
            assert attr != 0, "Awaiting content rows should have emphasis attr"

    def test_no_emphasis_when_no_awaiting(self):
        state = _make_state(awaiting_rows=[])
        rows = dashboard.render_screen(state, 50, 120)

        # Content rows after AWAITING VERDICT header should have attr=0
        in_awaiting_section = False
        for text, attr in rows:
            if text.startswith("AWAITING VERDICT"):
                in_awaiting_section = True
                continue
            if in_awaiting_section:
                if dashboard.SEPARATOR_CHAR in text or text.startswith("EVENT FEED"):
                    break
                if text.strip():
                    assert attr == 0, "No emphasis when no awaiting rows"


# ---------------------------------------------------------------------------
# Test 17: Separator rules between sections
# ---------------------------------------------------------------------------

class TestSeparatorRules:
    def test_separator_present_between_sections(self):
        state = _make_state(feed_lines=["20:06:00 [EVENT] started"])
        rows = dashboard.render_screen(state, 50, 120)
        lines = _texts(rows)

        separator_count = sum(
            1 for text in lines if text and all(c == dashboard.SEPARATOR_CHAR for c in text)
        )
        # 3 separators: after header, after IN-FLIGHT, after AWAITING VERDICT
        assert separator_count == 3, f"Expected 3 separators, got {separator_count}"

    def test_separator_full_width(self):
        width = 100
        state = _make_state(feed_lines=["20:06:00 [EVENT] started"])
        rows = dashboard.render_screen(state, 50, width)

        for text, attr in rows:
            if text and all(c == dashboard.SEPARATOR_CHAR for c in text):
                assert len(text) == width, f"Separator should be {width} chars, got {len(text)}"

    def test_separator_dim(self):
        state = _make_state(feed_lines=["20:06:00 [EVENT] started"])
        rows = dashboard.render_screen(state, 50, 120)

        for text, attr in rows:
            if text and all(c == dashboard.SEPARATOR_CHAR for c in text):
                assert attr & curses.A_DIM, "Separator should have DIM attr"


# ---------------------------------------------------------------------------
# Test 18: Monochrome fallback (no color)
# ---------------------------------------------------------------------------

class TestMonochromeFallback:
    def test_no_color_returns_valid_rows(self):
        state = _make_state(feed_lines=["20:06:00 [EVENT] started"])
        rows = dashboard.render_screen(state, 50, 120, has_colors=False)

        assert len(rows) == 50
        for row in rows:
            assert isinstance(row, tuple)
            text, attr = row
            assert isinstance(text, str)
            assert isinstance(attr, int)

    def test_no_color_uses_monochrome_attrs(self):
        state = _make_state(feed_lines=["20:06:00 [EVENT] started"])
        rows = dashboard.render_screen(state, 50, 120, has_colors=False)

        # No color_pair bits should be set (color pairs occupy bits 8-15)
        for text, attr in rows:
            # In monochrome mode, no color pair should be used
            color_pair_bits = (attr >> 8) & 0xFF
            assert color_pair_bits == 0, f"Monochrome should not use color pairs: {text!r} attr={attr}"

    def test_color_mode_uses_color_pairs(self):
        state = _make_state(feed_lines=["20:06:00 [EVENT] started"])
        rows = dashboard.render_screen(state, 50, 120, has_colors=True)

        # At least some rows should have color pair bits set
        color_rows = [
            text for text, attr in rows
            if (attr >> 8) & 0xFF != 0
        ]
        assert color_rows, "Color mode should use color pairs for some rows"


# ---------------------------------------------------------------------------
# Test 19: Single-screen line-budget contract
# ---------------------------------------------------------------------------

class TestLineBudget:
    def test_budget_exact_height(self):
        """render_screen always returns exactly height rows."""
        for h in [24, 30, 50, 80]:
            state = _make_state(feed_lines=["line " + str(i) for i in range(20)])
            rows = dashboard.render_screen(state, h, 120)
            assert len(rows) == h, f"Expected {h} rows, got {len(rows)}"

    def test_budget_with_separators(self, running_db):
        """Separators don't break the height contract."""
        in_flight, awaiting = _query_state(running_db)
        state = _make_state(
            in_flight_rows=in_flight,
            awaiting_rows=awaiting,
            feed_lines=["line " + str(i) for i in range(20)],
        )
        rows = dashboard.render_screen(state, 30, 120)
        assert len(rows) == 30

    def test_footer_always_last(self):
        """Footer is always the last row."""
        state = _make_state(feed_lines=["line " + str(i) for i in range(20)])
        rows = dashboard.render_screen(state, 50, 120)
        footer_text, _ = rows[-1]
        assert "q quit" in footer_text


# ---------------------------------------------------------------------------
# Tail / filter unit tests
# ---------------------------------------------------------------------------

class TestTailSessionLog:
    def test_reads_today_log(self, tmp_path):
        log_dir = str(tmp_path)
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        log_file = tmp_path / f"bellows-{today}.log"
        log_file.write_text("line1\nline2\nline3\n")

        result = dashboard.tail_session_log(log_dir, max_lines=2)
        assert result == ["line2", "line3"]

    def test_returns_none_when_no_log(self, tmp_path):
        result = dashboard.tail_session_log(str(tmp_path))
        assert result is None
