# QA Report — Revert File-Checksum Snapshot Fix + Re-Open BACKLOG Entry

**Date:** 2026-05-01
**Plan:** `executable-revert-snapshot-fix-and-reopen-backlog-2026-05-01`
**Test Scope:** targeted

## Prior Step Verification

- Step 1 Output Receipt Status: **Complete** (confirmed in `knowledge/development/revert-snapshot-fix-2026-05-01.md`)
- Step 2 BACKLOG edit: **Landed** — `(REOPENED 2026-05-01 after failed close attempt)` annotation present at line 11 of `knowledge/BACKLOG.md`

## Deliverable Verification

| Deliverable | Expected | Status | Evidence |
|-------------|----------|--------|----------|
| Revert commit in git log | `7e1d157` visible in `git log --oneline -5` | ✅ | `evidence/executable-revert-snapshot-fix-and-reopen-backlog-2026-05-01/git_log_after_revert.txt` |
| `_snapshot_file_state` removed from bellows.py | `grep -c` returns 0 | ✅ | `evidence/executable-revert-snapshot-fix-and-reopen-backlog-2026-05-01/grep_snapshot_function_gone.txt` |
| `_capture_git_diff` restored in bellows.py | `grep -c` returns >= 3 | ✅ | `evidence/executable-revert-snapshot-fix-and-reopen-backlog-2026-05-01/grep_capture_function_restored.txt` — 5 matches (1 definition + 4 call sites) |
| `test_snapshot_file_state.py` removed | `ls` returns "No such file or directory" | ✅ | `evidence/executable-revert-snapshot-fix-and-reopen-backlog-2026-05-01/ls_test_file_gone.txt` |
| BACKLOG REOPENED annotation in Open section | Exactly 1 match at line 11 | ✅ | `evidence/executable-revert-snapshot-fix-and-reopen-backlog-2026-05-01/grep_backlog_reopen_annotation.txt` |
| Test suite returns to pre-snapshot-fix baseline | 177 passed, 1 failed (pre-existing `test_run_step_timeout`) | ✅ | `evidence/executable-revert-snapshot-fix-and-reopen-backlog-2026-05-01/pytest_targeted.txt` |

**Note on test count:** The plan expected 183 passed + 1 failed, but the actual pre-snapshot-fix baseline is 177 passed + 1 failed = 178 total. The snapshot fix added 6 tests (bringing total to 184); reverting removes those 6, returning to 178. The 177+1 result is correct — it matches the pre-snapshot-fix baseline from the Step 1 dev log.

## Rule 20 Self-Check

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: knowledge/qa/evidence/executable-revert-snapshot-fix-and-reopen-backlog-2026-05-01/
Files verified: 6
```
