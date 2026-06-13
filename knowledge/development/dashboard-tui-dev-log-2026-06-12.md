# Dashboard TUI Dev Log

**Date:** 2026-06-12
**Plan:** 33, Step 2
**Agent:** Bellows Developer

---

## Implementation Summary

Built the full-screen dashboard TUI per the approved Step 1 design spec. Three files created/modified:

### 1. `status.py` — DB query extraction (refactor)

Extracted the two inline SQL queries from `main()` into importable functions:
- `query_in_flight(db_path)` — returns in-flight plan rows
- `query_awaiting_verdict(db_path)` — returns awaiting-verdict rows

Both open their own `?mode=ro` connections and close them immediately. `main()` now calls these instead of embedding the SQL. Existing tests pass unchanged.

### 2. `dashboard.py` — New file (main deliverable)

**Pure functions (headless-testable):**
- `tail_session_log(log_dir, max_lines)` — reads today's session log with midnight rotation tolerance (falls back to yesterday's file within 60s of midnight)
- `filter_feed_lines(lines)` — keeps all log lines except Module fingerprint noise
- `assemble_state(bellows_root, child_proc)` — gathers all data into a state snapshot dict (daemon liveness, header data, DB queries, log tail, child process status)
- `render_screen(state, height, width, mode)` — pure render: state + dimensions + mode → list of strings. Handles all three modes (normal, confirm_restart, confirm_quit), minimum-size check, dynamic feed-pane height

**Curses shell (thin):**
- `CursesShell` class wraps `curses.wrapper`. Owns the daemon child process via `subprocess.Popen(stdout=DEVNULL, stderr=DEVNULL, stdin=DEVNULL)`. Handles `r`/`q` keypress dispatch, restart with flock-release retry loop (10 attempts × 0.5s), quit with SIGTERM→SIGKILL sequence, child-death detection via `poll()`, resize via `KEY_RESIZE`.
- Separate `.bellows-dashboard.lock` prevents second dashboard instance. Dashboard never touches `.bellows.lock`.
- Refresh every ~2s via `curses.halfdelay(20)`.

### 3. `CLAUDE.md` — Start section updated

Added `python dashboard.py` as the primary run mode, kept `python bellows.py` as the headless alternative.

### 4. `tests/test_dashboard.py` — New file (19 tests)

**12 headless render tests per spec:**
1. `test_render_running_state` — RUNNING header, panes, footer
2. `test_render_stopped_state` — STOPPED header with exit code, `stale?` marker, `r relaunch` footer
3. `test_render_confirm_restart` — confirmation prompt replaces footer
4. `test_render_confirm_quit` — quit confirmation replaces footer
5. `test_render_empty_panes` — all three panes show `(none)`
6. `test_render_db_absent` — both DB panes show `(no database)`
7. `test_render_log_absent` — feed shows `(no log file)`
8. `test_render_minimum_size` — below 80×24 shows "Terminal too small" message
9. `test_feed_filter` — passes EVENT/PAUSE/ERROR/WARN/INFO, excludes Module fingerprint
10. `test_feed_line_truncation` — long lines truncated to terminal width
11. `test_verdict_file_basename` — verdict ref shown as basename in output
12. `test_event_feed_height_fills_remaining` — two sub-tests proving feed expands/contracts

**PTY smoke test (SA confirmed feasible):**
13. `test_pty_launch_refresh_quit` — launches dashboard on a real PTY (50×120), waits for render, sends `q`→`y`, asserts exit code 0 and "Bellows" in output

**Additional unit tests:**
14-15. `tail_session_log` — reads today's log, returns None when absent

---

## Render Layer Output vs Mock

**Fixture-data render (24×120):**
```
● Bellows RUNNING  pid 17920  sha 6274d1a  up 6m

IN-FLIGHT
 #33  bellows   Step 1/3  running   10m   Bellows — Live Dashboard TUI (Daemon-…

AWAITING VERDICT
 (none)

EVENT FEED
 20:01:12 [INFO] ── session restart ──────────────────────────────
 20:01:12 [INFO] session log: /Users/…/bellows-2026-06-12.log
 20:05:58 [EVENT] [executable-33] ⏳ detected plan
 20:05:58 [EVENT] [executable-33] ⏳ RUNNING
 20:05:58 [INFO] [executable-33] minted id 33 — renamed to in-progress-executable-33.md
 20:05:58 [INFO] [executable-33] plan has 3 steps
 20:06:00 [EVENT] [executable-33] ▶ started
 20:06:59 [INFO] [executable-33] runner: 60s elapsed, last output 5s ago (step 1)




r restart  q quit
```

Structurally matches Mock 1 from the approved spec. All elements present: header with pid/sha/uptime, IN-FLIGHT with plan row, AWAITING VERDICT `(none)`, EVENT FEED with log lines, footer keybar.

---

## Test Suite Results

```
======================= 582 passed, 1 warning in 15.41s ========================
```

All 582 tests pass. 19 new tests in `test_dashboard.py`. Zero failures, zero errors.

---

## Output Receipt
**Agent:** Bellows Developer
**Step:** 2
**Status:** Complete

### What Was Done
Implemented the dashboard TUI per the approved design spec: `dashboard.py` (new) with pure render functions and thin curses shell, `tests/test_dashboard.py` (new) with 19 tests including PTY smoke, `status.py` refactored to export DB query functions, `CLAUDE.md` updated.

### Files Deposited
- `knowledge/development/dashboard-tui-dev-log-2026-06-12.md` — this dev log

### Files Created or Modified (Code)
- `dashboard.py` — new: full-screen TUI with daemon-owning wrapper, pure render layer, process management
- `tests/test_dashboard.py` — new: 19 tests (12 headless render + PTY smoke + unit tests)
- `status.py` — refactored: extracted `query_in_flight()` and `query_awaiting_verdict()` from `main()`
- `CLAUDE.md` — updated Start section: dashboard as primary run mode

### Decisions Made
- Used `list(in_flight) * 4` trick in test 12b to actually exercise feed contraction (single rows = same height as `(none)`)
- PTY smoke test uses 2.5s delays between keystrokes to align with halfdelay(20) refresh cycle
- `_fit()` helper truncates with `…` rather than hard-clip — consistent with status.py's `truncate()`

### Flags for CEO
- The interactive TUI loop cannot be fully exercised in a dispatched session — CEO's first `python dashboard.py` run is the live acceptance

### Flags for Next Step
- 19 new tests in `test_dashboard.py` — QA should verify count matches
- PTY smoke test takes ~5s due to halfdelay timing — normal, not a hang
- The `status.py` refactor is backward-compatible — `main()` behavior unchanged
