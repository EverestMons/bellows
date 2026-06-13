# Dashboard TUI Design — Daemon-Owning Wrapper with Restart Key

**Date:** 2026-06-12
**Author:** Bellows Systems Analyst
**Plan:** 33
**Layer Impact:** Layer 1 only — new UI surface over existing daemon; no Layer 2/3 changes

---

## 1. Process Model

### Child Spawn

The dashboard launches `bellows.py` as a subprocess via:

```python
subprocess.Popen(
    [sys.executable, "bellows.py"],
    cwd=str(bellows_root),
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL,
    stdin=subprocess.DEVNULL,
)
```

**stdout/stderr → DEVNULL.** The daemon already writes all output to `logs/terminal/bellows-YYYY-MM-DD.log` via `RotatingFileHandler`. Piping stdout would risk pipe-buffer blocking — the daemon's existing file-logging path is the correct event source (Context constraint (b)).

stdin → DEVNULL to prevent the child from competing for terminal input with the curses shell.

### Restart Sequence (`r` key)

1. User presses `r` → confirmation prompt appears in footer: `Restart daemon? (y/n)`
2. User presses `y` →
   a. Send `SIGTERM` to child process (`child.terminate()`).
   b. Wait up to 5 seconds for child to exit (`child.wait(timeout=5)`).
   c. If still alive after 5s, send `SIGKILL` (`child.kill()`), wait 2s.
   d. **Flock-release retry loop:** The child holds `.bellows.lock`. On death the kernel releases the flock. Poll `probe_daemon(lock_path)` up to 10 times at 0.5s intervals (5s max) until the lock is free. If the lock is still held after 10 retries, show `ERROR: lock not released` in the header — do not respawn.
   e. Once the lock is free, spawn a new child (same `Popen` invocation as initial spawn).
   f. Header flips from `RESTARTING...` → `RUNNING`.
3. User presses `n` or any other key → dismiss prompt, return to normal display.

### Quit Sequence (`q` key)

1. User presses `q` → confirmation prompt: `Quit dashboard and stop daemon? (y/n)`
2. User presses `y` →
   a. Send `SIGTERM` to child, wait up to 5s, `SIGKILL` if needed.
   b. Reap child (`child.wait()`).
   c. Exit curses (`curses.endwin()`), `sys.exit(0)`.
3. User presses `n` → dismiss prompt.

### Child-Death Detection

The main refresh loop calls `child.poll()` every refresh cycle (~2s). If `child.poll()` returns a non-`None` return code:

- Header flips to `○ Bellows STOPPED (exited, code {rc})`.
- `r` key now offers `Relaunch daemon? (y/n)` (skips SIGTERM, goes straight to spawn with flock-release retry loop).

### Zombie Reaping

`child.wait()` is called explicitly during restart and quit. If the child dies spontaneously, `child.poll()` reaps the zombie on the next refresh cycle.

### Second-Dashboard Prevention

The child's flock on `.bellows.lock` prevents a second daemon. To prevent a second dashboard, the dashboard itself acquires a **separate advisory lock** on `.bellows-dashboard.lock` (LOCK_EX | LOCK_NB) at startup, before spawning the child. A second dashboard instance will fail to acquire this lock, print `Another dashboard instance is already running`, and exit immediately. The dashboard lock fd is held open for the process lifetime — the kernel releases it on exit/crash.

---

## 2. Screen Layout + Mocks

### Layout Structure (50 rows × 120 cols)

```
Row 0:      [HEADER]     — daemon status line (1 row)
Row 1:      [blank separator]
Row 2-N:    [IN-FLIGHT]  — section label + rows (dynamic height)
Row N+1:    [blank separator]
Row N+2-M:  [AWAITING VERDICT] — section label + rows (dynamic height)
Row M+1:    [blank separator]
Row M+2-48: [EVENT FEED] — fills remaining space, most recent at bottom
Row 49:     [FOOTER]     — keybar, always pinned to last row
```

Pane height allocation: IN-FLIGHT and AWAITING VERDICT take their natural height (label + rows, or label + `(none)`). EVENT FEED expands to fill all remaining rows between AWAITING VERDICT and the footer.

### Mock 1 — RUNNING state (real current data)

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ ● Bellows RUNNING  pid 17920  sha 6274d1a  up 6m                                                                      │
│                                                                                                                        │
│ IN-FLIGHT                                                                                                              │
│  #33  bellows    Step 1/3  running   1m    Bellows — Live Dashboard TUI (Daemon-…                                       │
│                                                                                                                        │
│ AWAITING VERDICT                                                                                                       │
│  (none)                                                                                                                │
│                                                                                                                        │
│ EVENT FEED                                                                                                             │
│  20:01:12 [INFO] ── session restart ──────────────────────────────                                                      │
│  20:01:12 [INFO] session log: /Users/…/bellows-2026-06-12.log                                                          │
│  20:05:58 [EVENT] [executable-draft-200504] ⏳ detected plan                                                           │
│  20:05:58 [EVENT] [executable-draft-200504] ⏳ RUNNING                                                                 │
│  20:05:58 [INFO] [executable-33] minted id 33 — renamed to in-progress-executable-33.md                                │
│  20:05:58 [INFO] [executable-draft-200504] plan has 3 steps                                                            │
│  20:06:00 [EVENT] [executable-draft-200504] ▶ started                                                                  │
│  20:06:59 [INFO] [executable-draft-200504] runner: 60s elapsed, last output 5s ago (step 1)                            │
│                                                                                                                        │
│                                                                                                                        │
│                                                                                                                        │
│                                                    (remaining rows empty)                                              │
│                                                                                                                        │
│                                                                                                                        │
│                                                                                                                        │
│ r restart  q quit                                                                                                      │
└──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

### Mock 2 — STOPPED state (child died or was killed)

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ ○ Bellows STOPPED (exited, code 1)                                                                                     │
│                                                                                                                        │
│ IN-FLIGHT                                                                                                              │
│  #33  bellows    Step 1/3  stale?    1h 04m Bellows — Live Dashboard TUI (Daemon-…                                     │
│                                                                                                                        │
│ AWAITING VERDICT                                                                                                       │
│  (none)                                                                                                                │
│                                                                                                                        │
│ EVENT FEED                                                                                                             │
│  20:05:58 [EVENT] [executable-draft-200504] ▶ started                                                                  │
│  20:06:59 [INFO] [executable-draft-200504] runner: 60s elapsed, last output 5s ago (step 1)                            │
│                                                                                                                        │
│                                                    (remaining rows empty)                                              │
│                                                                                                                        │
│ r relaunch  q quit                                                                                                     │
└──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

Note: When stopped, footer shows `r relaunch` instead of `r restart`. The IN-FLIGHT section marks `running` entries as `stale?` (reuses `render_in_flight`'s existing `daemon_running=False` behavior from `status.py`).

### Mock 3 — Restart Confirmation Prompt

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ ● Bellows RUNNING  pid 17920  sha 6274d1a  up 6m                                                                      │
│                                                                                                                        │
│ IN-FLIGHT                                                                                                              │
│  #33  bellows    Step 1/3  running   1m    Bellows — Live Dashboard TUI (Daemon-…                                       │
│                                                                                                                        │
│ AWAITING VERDICT                                                                                                       │
│  (none)                                                                                                                │
│                                                                                                                        │
│ EVENT FEED                                                                                                             │
│  20:06:00 [EVENT] [executable-draft-200504] ▶ started                                                                  │
│  20:06:59 [INFO] [executable-draft-200504] runner: 60s elapsed, last output 5s ago (step 1)                            │
│                                                                                                                        │
│ Restart daemon? (y/n)                                                                                                  │
└──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

The confirmation prompt replaces the footer keybar. The quit confirmation follows the same pattern: `Quit dashboard and stop daemon? (y/n)`.

### Minimum Terminal Size

**Minimum: 24 rows × 80 columns.** If the terminal is smaller, display a centered message:

```
Terminal too small (need 80×24)
```

No curses content is rendered until the terminal meets the minimum. On `SIGWINCH` (resize), re-check dimensions. If the terminal grows back above the minimum, resume normal rendering immediately.

### Resize Handling

The curses loop catches `curses.KEY_RESIZE` (triggered by `SIGWINCH`). On resize:
1. Call `stdscr.clear()`.
2. Re-read `stdscr.getmaxyx()`.
3. If below minimum → show "too small" message.
4. Otherwise → re-render all panes at new dimensions. EVENT FEED height adjusts dynamically since it fills remaining space.

---

## 3. Data Contract

### Imported from `status.py` (no duplication)

| Function | Purpose |
|---|---|
| `probe_daemon(lock_path)` | Daemon liveness via flock probe |
| `get_daemon_pid(lock_path)` | PID via lsof |
| `get_uptime(pid)` | Process uptime string |
| `get_sha(bellows_root)` | Git short SHA of bellows.py |
| `render_daemon_header(running, pid, sha, uptime)` | Header line formatting |
| `render_in_flight(rows, daemon_running)` | IN-FLIGHT section formatting |
| `render_awaiting_verdict(rows)` | AWAITING VERDICT section formatting |
| `format_elapsed(iso_str)` | ISO → elapsed string |
| `truncate(text, max_len)` | Text truncation |

The DB query logic (IN-FLIGHT and AWAITING VERDICT SQL) will be extracted into importable functions in `status.py` — currently embedded in `main()`. The dashboard imports these query functions and the render functions, satisfying Context constraint (c): all lifecycle.db reads remain `?mode=ro`.

### New in `dashboard.py`

| Component | Purpose |
|---|---|
| `tail_session_log(log_dir, max_lines)` | Reads the current day's session log file (`bellows-YYYY-MM-DD.log`), returns the last `max_lines` lines. **Midnight rotation tolerance:** on each call, compute today's filename. If the file doesn't exist yet (just past midnight), fall back to yesterday's file for up to 60 seconds, then show `(no log file for today)`. |
| `filter_feed_lines(lines)` | Filters log lines to EVENT, PAUSE, ERROR, WARN, and INFO classes. All levels are shown since INFO lines carry operational context (heartbeats, runner progress). The filter excludes only Module fingerprint lines (`Module:.*@ git:`) to reduce noise. |
| `assemble_state(bellows_root)` | Gathers all data into a state snapshot dict: `{daemon_running, pid, sha, uptime, in_flight_rows, awaiting_rows, feed_lines, child_alive, child_exit_code}`. Pure-data function; no rendering. |
| `render_screen(state, height, width, mode)` | Pure function: state snapshot + terminal dimensions + mode (`normal`, `confirm_restart`, `confirm_quit`) → list of strings (one per row). This is the **testable render layer** (Context constraint (d)). |
| `CursesShell` | Thin class wrapping `curses.wrapper`. Calls `assemble_state` + `render_screen` every ~2s, handles keypress dispatch. The shell itself is minimal — all logic lives in the pure functions. |

### Refresh Cadence

- **Screen refresh:** every 2 seconds (via `curses.halfdelay(20)` — 2000ms timeout on `getch()`).
- **DB queries:** every refresh cycle (read-only, fast — two indexed queries).
- **Log tail:** every refresh cycle (single `open` + seek to end, read backwards — no full file scan).
- **Daemon liveness probe:** every refresh cycle (single flock attempt, sub-ms).

### Degradation

| Condition | Behavior |
|---|---|
| `lifecycle.db` absent | IN-FLIGHT and AWAITING VERDICT show `(no database)` |
| Session log absent | EVENT FEED shows `(no log file)` |
| PID lookup fails | Header shows `pid —` |
| Uptime lookup fails | Header shows `up —` |
| Git SHA lookup fails | Header shows `sha —` |
| Child dead | Header shows STOPPED, `r` offers relaunch |

---

## 4. Test Strategy

### Pure Render Layer Tests (`tests/test_dashboard.py`)

These test `render_screen()` — the pure function that converts state → list of strings.

| # | Test | What it verifies |
|---|---|---|
| 1 | `test_render_running_state` | RUNNING header, IN-FLIGHT with active plan, AWAITING VERDICT `(none)`, feed lines present, footer shows `r restart  q quit` |
| 2 | `test_render_stopped_state` | STOPPED header with exit code, `stale?` status on in-flight rows, footer shows `r relaunch  q quit` |
| 3 | `test_render_confirm_restart` | Normal content with confirmation prompt replacing footer |
| 4 | `test_render_confirm_quit` | Normal content with quit confirmation replacing footer |
| 5 | `test_render_empty_panes` | All panes show `(none)` when no in-flight, no awaiting, no feed |
| 6 | `test_render_db_absent` | IN-FLIGHT and AWAITING show `(no database)` |
| 7 | `test_render_log_absent` | EVENT FEED shows `(no log file)` |
| 8 | `test_render_minimum_size` | Below 80×24 → "Terminal too small" message only |
| 9 | `test_feed_filter` | `filter_feed_lines` passes EVENT/PAUSE/ERROR/WARN/INFO, excludes Module fingerprint lines |
| 10 | `test_feed_line_truncation` | Long log lines are truncated to terminal width |
| 11 | `test_verdict_file_basename` | Verdict file ref shown as basename, not full path |
| 12 | `test_event_feed_height_fills_remaining` | Feed pane expands/contracts based on in-flight/awaiting row counts |

### PTY Smoke Test

**Feasibility: CONFIRMED.** Proof executed in this session:

```
PTY_FEASIBLE: yes — child output captured via pty
CURSES_PTY_SMOKE: PASS — curses app ran, exit code 0
```

The test will:
1. Open a PTY pair, set `TIOCSWINSZ` to 50×120.
2. Launch `dashboard.py` as a subprocess on the slave fd (with a mock `bellows.py` that just sleeps).
3. Wait 2.5 seconds (one full refresh cycle).
4. Send `q` keystroke, then `y` to confirm quit.
5. Assert exit code 0 and that stdout contained the `Bellows` header marker.

The mock `bellows.py` for the smoke test will be a minimal script that acquires `.bellows.lock` and sleeps, exercising the real flock path without running the full daemon.

---

## Output Receipt
**Agent:** Bellows Systems Analyst
**Step:** 1
**Status:** Complete

### What Was Done
Designed the dashboard TUI architecture: process model (child spawn, restart with flock-release retry, quit, crash detection, second-instance prevention), screen layout with three full mocks from real live data, data contract (imports from status.py, new log-tail and render functions), and test strategy (12 headless render tests + PTY smoke, feasibility confirmed).

### Files Deposited
- `knowledge/architecture/dashboard-tui-design-2026-06-12.md` — Full TUI design spec with process model, screen mocks, data contract, and test strategy

### Files Created or Modified (Code)
- None (design step only)

### Decisions Made
- Dashboard uses a separate `.bellows-dashboard.lock` to prevent second dashboard instances (the daemon's `.bellows.lock` only prevents second daemons)
- Child stdout/stderr → DEVNULL (not piped) — daemon's file logging is the event source
- All log levels shown in feed except Module fingerprint lines (INFO carries operational value)
- Minimum terminal: 80×24; resize via KEY_RESIZE with dynamic feed-pane height
- DB queries extracted from status.py main() into importable functions (small refactor)
- PTY smoke test confirmed feasible — will be implemented in Step 2

### Flags for CEO
- None

### Flags for Next Step
- The Developer must extract the DB query logic from `status.py:main()` into importable functions (e.g., `query_in_flight(db_path)`, `query_awaiting_verdict(db_path)`) — currently inline in `main()`
- PTY smoke test is feasible and should be implemented per the proof-of-concept approach documented in Section 4
