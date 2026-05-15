# QA Report: _handle Subdirectory Guard

**Plan:** executable-handle-subdirectory-guard-2026-04-19
**Date:** 2026-04-19
**Dev Log:** `bellows/knowledge/development/handle-subdirectory-guard-2026-04-19.md`
**Commit:** fb1d5f3

## Flags

**BELLOWS RESTART REQUIRED BEFORE MOVE-TO-DONE. The plan is intentionally left in `in-progress-executable-handle-subdirectory-guard-2026-04-19.md` state. After CEO restarts Bellows to load the guard fix, CEO manually moves the plan to Done via `shutil.move('bellows/knowledge/decisions/in-progress-executable-handle-subdirectory-guard-2026-04-19.md', 'bellows/knowledge/decisions/Done/executable-handle-subdirectory-guard-2026-04-19.md')` then commits. Five verdict-pending-* plans currently in decisions/ will remain safe from re-run only after the restart.**

## Deliverable Verification (Rule 17)

| Deliverable | Expected | Status | Evidence |
|---|---|---|---|
| Guard in `_handle()` | `path_parent = str(Path(path).parent)` at L453 | ✅ | `knowledge/qa/evidence/executable-handle-subdirectory-guard-2026-04-19/grep_guard.txt` |
| New test: `test_on_moved_dispatches_for_top_level_dest` | Function exists in `tests/test_bellows.py` | ✅ | `knowledge/qa/evidence/executable-handle-subdirectory-guard-2026-04-19/grep_new_tests.txt` |
| New test: `test_on_moved_rejects_subdirectory_dest` | Function exists in `tests/test_bellows.py` | ✅ | `knowledge/qa/evidence/executable-handle-subdirectory-guard-2026-04-19/grep_new_tests.txt` |
| New test: `test_on_moved_dispatches_same_directory_rename` | Function exists in `tests/test_bellows.py` | ✅ | `knowledge/qa/evidence/executable-handle-subdirectory-guard-2026-04-19/grep_new_tests.txt` |
| Commit SHA fb1d5f3 | Exists in git history | ✅ | `knowledge/qa/evidence/executable-handle-subdirectory-guard-2026-04-19/git_log.txt` |

## Test Results

- **42 passed, 0 failed**
- Evidence: `knowledge/qa/evidence/executable-handle-subdirectory-guard-2026-04-19/pytest_targeted.txt`

## Rule 20 Self-Check

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — all evidence files present, no hedging keywords found.
Evidence folder: bellows/knowledge/qa/evidence/executable-handle-subdirectory-guard-2026-04-19/
Files verified: 4
```
