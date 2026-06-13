# Dashboard TUI QA Report

**Date:** 2026-06-12
**Plan:** 33, Step 3
**Agent:** Bellows QA

---

## Verification Table

| # | Check | Section | Present | Content Filled | Evidence |
|---|---|---|---|---|---|
| 1 | Full suite | Full suite run | OK | 582 passed, 0 failures, 19 new tests | `full_suite_tail.txt` |
| 2 | Mock conformance | Render layer vs approved mocks | OK | All 3 mock states structurally match; verdict basename verified | `mock_conformance.txt` |
| 3 | Process safety | Lock, restart, stdout disposition | OK | Dashboard never acquires .bellows.lock; restart waits on lock release; no PIPE | `process_safety.txt` |
| 4 | Read-only + degradation | DB mode=ro, absent-DB/log paths | OK | All DB connects use ?mode=ro via status.py; (no database) and (no log file) render correctly | `safety_check.txt` |
| 5 | PTY smoke | Launch, refresh, quit via PTY | OK | Exit code 0, "Bellows" header in output, 5.15s runtime | `pty_smoke.txt` |
| 6 | CLAUDE.md | Start section documentation | OK | `python dashboard.py` documented as primary; `python bellows.py` as headless alternative | `docs_check.txt` |

---

## Verification Details

### 1. Full Suite

Final 15 lines of `python3 -m pytest tests/ -v`:

```
tests/test_worktree.py::test_landing_noff_when_main_advanced PASSED      [ 98%]
tests/test_worktree.py::test_landing_aborts_on_true_conflict_main_advanced PASSED [ 99%]
tests/test_worktree.py::test_sha_identity_ff_and_noff PASSED             [ 99%]
tests/test_worktree.py::test_legacy_branchless_worktree_raises_descriptive_error PASSED [ 99%]
tests/test_worktree.py::test_auto_stage_preserves_untracked_deposit_on_teardown PASSED [ 99%]
tests/test_worktree.py::test_auto_stage_handles_multiple_deposits PASSED [ 99%]
tests/test_worktree.py::test_auto_stage_noop_when_all_committed PASSED   [100%]

=============================== warnings summary ===============================
-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
======================= 582 passed, 1 warning in 15.45s ========================
```

**New test count:** 19 tests in `tests/test_dashboard.py` (matches dev log).

### 2. Mock Conformance

All three mock variants verified against the approved spec (Step 1 design):

- **Mock 1 (RUNNING):** Header with pid/sha/uptime, IN-FLIGHT with #33 plan row, AWAITING VERDICT (none), EVENT FEED with 8 log lines, footer `r restart  q quit`. 50 rows. PASS.
- **Mock 2 (STOPPED):** Header `○ Bellows STOPPED (exited, code 1)`, IN-FLIGHT shows `stale?`, footer `r relaunch  q quit`. 50 rows. PASS.
- **Mock 3 (CONFIRM RESTART):** Header still RUNNING, confirmation prompt `Restart daemon? (y/n)` replaces footer, normal keybar absent. 50 rows. PASS.
- **Verdict basename:** `/full/path/to/verdict-request-30-step-2.md` rendered as `verdict-request-30-step-2.md` in output. PASS.

### 3. Process Safety

- **Dashboard never acquires `.bellows.lock`:** All `.bellows.lock` references in `dashboard.py` are read-only probes (`probe_daemon()`, `_wait_for_lock_release()`). The dashboard acquires only `.bellows-dashboard.lock` via `_acquire_dashboard_lock()`.
- **Restart path waits on lock release:** `_do_restart()` calls `_terminate_child()` then `_wait_for_lock_release()` (10 retries × 0.5s) before `_spawn_child()`. If lock not released, returns without respawning.
- **No unconsumed PIPE:** Zero `PIPE` references in `dashboard.py`. Child spawned with `stdout=DEVNULL, stderr=DEVNULL, stdin=DEVNULL`.
- **SIGTERM → SIGKILL sequence:** `_terminate_child()` sends SIGTERM, waits 5s, then SIGKILL with 2s timeout.

### 4. Read-Only + Degradation

- **mode=ro:** Both `query_in_flight()` and `query_awaiting_verdict()` in `status.py` use `f"file:{db_path}?mode=ro"`. Dashboard has zero direct `sqlite3.connect` calls — all DB access delegates to `status.py`.
- **DB absent:** Render shows `(no database)` in both IN-FLIGHT and AWAITING VERDICT panes. Verified via headless render.
- **Log absent:** Render shows `(no log file)` in EVENT FEED pane. `tail_session_log()` returns `None` when file doesn't exist. Verified via headless render.

### 5. PTY Smoke

```
tests/test_dashboard.py::TestPTYSmoke::test_pty_launch_refresh_quit PASSED [100%]
========================= 1 passed, 1 warning in 5.15s =========================
```

The test launches `dashboard.py` on a real PTY (50x120), waits for render, sends `q` → `y` quit sequence, and verifies exit code 0 with "Bellows" in output. 5.15s runtime (expected — aligns with halfdelay refresh cycle).

### 6. CLAUDE.md

Start section now reads:
```
## Start
python dashboard.py          # primary — full-screen TUI that owns the daemon
python bellows.py             # headless daemon (no TUI)
```

Dashboard documented as primary, headless daemon preserved as alternative.

---

## Rule 20 Self-Check

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: /Users/marklehn/Developer/GitHub/bellows/.bellows-worktrees/33/knowledge/qa/evidence/dashboard-tui-2026-06-12/
Files verified: 6
```

---

## Receipt Flags for CEO

1. **Live interactive acceptance is the CEO's first `python dashboard.py` run** — the dispatched agent session cannot fully exercise the interactive TUI loop (curses keyboard handling, live refresh, restart/quit flows). The PTY smoke test confirms launch-render-quit works, but the full interactive experience requires a human at the terminal.
2. **The dashboard becomes the primary run mode** — the CEO's current terminal workflow changes: start `python dashboard.py` instead of `python bellows.py`. The headless daemon remains available for non-interactive use.
3. **Restart via `r` supersedes manual kill/restart** — for routine daemon-code activation (after code changes), press `r` in the dashboard instead of Ctrl+C → re-run. The dashboard handles SIGTERM, flock-release waiting, and respawn automatically.

---

## Output Receipt
**Agent:** Bellows QA
**Step:** 3
**Status:** Complete

### What Was Done
Executed six verification checks for the dashboard TUI (plan 33): full suite (582 passed, 19 new tests), mock conformance (all 3 states match approved spec), process safety (lock isolation, restart sequence, no PIPE), read-only + degradation (mode=ro, graceful absent-DB/log), PTY smoke (launch-render-quit exit 0), and CLAUDE.md documentation. All checks pass. Rule 20 self-check executed and included.

### Files Deposited
- `knowledge/qa/dashboard-tui-qa-report-2026-06-12.md` — this QA report
- `knowledge/qa/evidence/dashboard-tui-2026-06-12/full_suite_tail.txt` — final 15 lines of test suite
- `knowledge/qa/evidence/dashboard-tui-2026-06-12/mock_conformance.txt` — render layer vs 3 mock states
- `knowledge/qa/evidence/dashboard-tui-2026-06-12/process_safety.txt` — lock/restart/stdout grep evidence
- `knowledge/qa/evidence/dashboard-tui-2026-06-12/safety_check.txt` — mode=ro and degradation checks
- `knowledge/qa/evidence/dashboard-tui-2026-06-12/pty_smoke.txt` — PTY smoke test output
- `knowledge/qa/evidence/dashboard-tui-2026-06-12/docs_check.txt` — CLAUDE.md verification

### Files Created or Modified (Code)
- None (QA step only)

### Decisions Made
- Verified `.bellows.lock` references in dashboard.py are read-only probes only (not acquisitions) — consistent with spec constraint
- PTY smoke 5.15s runtime accepted as normal (halfdelay cycle timing)

### Flags for CEO
- Live interactive acceptance required: CEO's first `python dashboard.py` run
- Dashboard is now the primary run mode — workflow change from `python bellows.py`
- `r` key restart supersedes manual kill/restart for routine daemon reloads

### Flags for Next Step
- None
