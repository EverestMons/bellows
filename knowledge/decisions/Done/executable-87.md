# Bellows — Dashboard Event Feed Log-Rotation Fix

**Date:** 2026-06-17 | **Tier:** small | **Dispatch Mode:** bellows | **Total Steps:** 2 | **Execution:** Step 1 (DEV) → Step 2 (QA) | **qa_steps:** 2 | **pause_for_verdict:** always

## How to Run This Plan

Fixes a display-only bug in the dashboard TUI: the EVENT FEED renders empty whenever the daemon has been running across a midnight boundary.

**Root cause (diagnosed 2026-06-17):** `dashboard.tail_session_log()` builds the log filename from **today's** date (`bellows-<today>.log`) and returns `None` if that exact file doesn't exist (except a 60-second post-midnight fallback). But the daemon opens ONE session log named for its **start** date and writes to it for its entire lifetime — it never rotates at midnight. So a daemon started 2026-06-16 keeps writing to `bellows-2026-06-16.log` while the dashboard looks for `bellows-2026-06-17.log` (which won't exist until a restart) → `log_absent` → blank feed. Verified: the actively-written log is `logs/terminal/bellows-2026-06-16.log` (mtime today) and no `bellows-2026-06-17.log` exists. The IN-FLIGHT / AWAITING-VERDICT panels are unaffected because they read `lifecycle.db`, not the log.

**Fix:** select the session log by **most-recent mtime** among `bellows-*.log` in the log dir, instead of by today's date. This matches the daemon's actual one-log-per-session behavior and is robust across midnight and multi-day runs.

**Scope note — display only, no daemon impact:** `dashboard.py` is the TUI wrapper, separate from the headless daemon (`bellows.py`). Editing it does NOT require restarting the running daemon; the fix takes effect the next time the dashboard is launched. Do NOT touch `bellows.py`, `runner.py`, the daemon loop, or `lifecycle.db` logic.

```
Read the plan at bellows/knowledge/decisions/executable-dashboard-event-feed-log-rotation-fix-2026-06-17.md. Execute Step 1 ONLY, then STOP and wait for CEO verdict.
```

**Deposits:**
- Step 1: `bellows/knowledge/development/dashboard-event-feed-fix-dev-2026-06-17.md`
- Step 2: `bellows/knowledge/qa/dashboard-event-feed-fix-qa-2026-06-17.md`

---

## STEP 1 — DEV (newest-log selection in tail_session_log)

You are the Bellows Developer. Read your specialist file at `bellows/agents/BELLOWS_DEVELOPER.md` first. Verify the current code before editing.

**File in scope this step:** `dashboard.py` (and `tests/test_dashboard.py` for test updates). Touch nothing else — NOT `bellows.py`, `runner.py`, `status.py`, or any daemon/lifecycle code.

1. **Rewrite `tail_session_log(log_dir, max_lines=20)`** (currently dashboard.py:67-89) to select the session log by most-recent modification time rather than today's date:
   - Glob `bellows-*.log` within `log_dir` (this pattern correctly excludes `nohup-restart-*.out` and other files).
   - If no matching files exist (or `log_dir` is absent/unreadable), return `None` (preserving the existing `log_absent` contract).
   - Otherwise pick the file with the greatest mtime and return `_tail_file(path, max_lines)` on it.
   - Remove the now-redundant today's-date construction and the 60-second midnight-tolerance branch — newest-mtime selection subsumes both. Keep `_tail_file()` unchanged.
   - Preserve the return contract exactly: `list[str]` (no trailing newlines) on success, `None` when no log is available.
2. Confirm `filter_feed_lines()` and `assemble_state()` are unchanged — `assemble_state` already derives `log_absent = raw_lines is None`, which still holds.

**Targeted tests:** `python3 -m pytest tests/test_dashboard.py --tb=short -q 2>&1 | cat`. Add/update tests:
- Given multiple `bellows-*.log` files with different mtimes, `tail_session_log` returns the tail of the **newest** one regardless of the date string in its name.
- **Regression case:** an actively-written start-dated log (e.g. `bellows-2026-06-16.log`) is still found when no today-dated file exists — this is the exact bug being fixed.
- Preserve existing behavior: empty/absent log dir → `None`; `max_lines` honored.

Deposit a dev log to `bellows/knowledge/development/dashboard-event-feed-fix-dev-2026-06-17.md`: the before/after of `tail_session_log`, the tests added/updated, and confirmation no daemon/lifecycle file was touched. Include an Output Receipt. Commit: `fix(dashboard): event feed selects newest bellows-*.log by mtime (cross-midnight rotation fix)`.

---

## STEP 2 — QA (full suite + behavior verification)

You are the Bellows QA analyst. Read your specialist file at `bellows/agents/BELLOWS_QA.md` first, then the Step 1 dev log. Verify with per-item PASS/FAIL; run the actual tests.

1. **Newest-log selection:** with multiple `bellows-*.log` files of differing mtimes in a temp dir, `tail_session_log` returns the newest file's tail — including the regression case where the newest file's date-name is NOT today (the daemon-across-midnight scenario).
2. **No-log contract preserved:** empty dir / absent dir → `None` → `assemble_state` reports `log_absent = True`.
3. **`max_lines` honored** and trailing newlines stripped (unchanged `_tail_file` behavior).
4. **Scope:** only `dashboard.py` + `tests/test_dashboard.py` changed; no diff to `bellows.py`, `runner.py`, `status.py`, or daemon/lifecycle code.
5. **Full suite:** `python3 -m pytest tests/ --tb=short -q 2>&1 | cat`. Report pass/fail counts; zero regressions.

Deposit a QA report to `bellows/knowledge/qa/dashboard-event-feed-fix-qa-2026-06-17.md` with the per-item PASS/FAIL table and suite counts.

Then closeout: (1) note the fix in the Bellows BACKLOG / status doc if one tracks dashboard issues; (2) move the in-progress plan file to `bellows/knowledge/decisions/Done/`. Commit: `test: dashboard event-feed log-rotation fix verified — full suite green`.
