# Dev Log — Dashboard Event Feed Log-Rotation Fix

**Plan:** 87 | **Step:** 1 (DEV) | **Date:** 2026-06-17

## Change Summary

### Before (`dashboard.py:67-89`)
`tail_session_log()` built the log filename from **today's date** (`bellows-<today>.log`) and returned `None` if that file didn't exist — with a narrow 60-second post-midnight fallback to yesterday's file. This broke the EVENT FEED whenever the daemon had been running across a midnight boundary, since the daemon writes to a single session log named for its **start** date.

### After (`dashboard.py:67-80`)
`tail_session_log()` now globs `bellows-*.log` in the log directory and selects the file with the **greatest mtime** (most recently written). This matches the daemon's one-log-per-session behavior and is robust across midnight and multi-day runs.

- Removed `datetime`/`timedelta` imports (no longer needed).
- Added `glob` import (as `glob_mod` to avoid shadowing).
- Preserved the return contract: `list[str]` on success, `None` when no log available.
- `_tail_file()`, `filter_feed_lines()`, and `assemble_state()` are **unchanged**.

## Files Changed

| File | Change |
|---|---|
| `dashboard.py` | Rewrote `tail_session_log` (mtime selection); updated imports |
| `tests/test_dashboard.py` | Replaced old date-based tests; added mtime, regression, edge-case tests |

## Tests Added/Updated (`tests/test_dashboard.py`)

| Test | Description |
|---|---|
| `test_reads_newest_log_by_mtime` | Multiple bellows-*.log files → returns tail of newest by mtime |
| `test_regression_cross_midnight_daemon` | Yesterday-dated log found when no today-dated file exists (the exact bug) |
| `test_returns_none_when_no_log` | Empty dir → `None` |
| `test_returns_none_for_absent_dir` | Nonexistent dir → `None` |
| `test_max_lines_honored` | `max_lines` parameter correctly limits output |
| `test_ignores_non_bellows_files` | Non-matching files (e.g. `nohup-restart-*.out`) are excluded |

## Scope Confirmation

No changes to `bellows.py`, `runner.py`, `status.py`, or any daemon/lifecycle code.

## Output Receipt

```
$ python3 -m pytest tests/test_dashboard.py --tb=short -q
37 passed in 5.46s
```
