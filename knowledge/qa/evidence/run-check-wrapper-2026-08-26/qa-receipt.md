# QA Receipt — run-check-wrapper (563)

**Date:** 2026-08-26
**Plan:** executable-563
**Commit:** 01aa74e

## Hygiene

**Numstat (3 files):**
| File | Added | Removed |
|---|---|---|
| tools/run_check.py | 91 | 0 |
| tests/test_run_check.py | 132 | 0 |
| knowledge/dev-logs/run-check-wrapper-dev-2026-08-26.md | 95 | 0 |

**Toplevel:** `/Users/marklehn/Developer/GitHub/bellows/.bellows-worktrees/563`

**Reflog -n 4:** 2 entries, 0 amends (reset to HEAD + the commit itself)

## Verification

| Item | Check | Status | Evidence |
|---|---|---|---|
| 1 | Full pytest suite: 0 failed | ✅ | 1503 passed in 52.24s; predicted 1494+8=1502, actual 1503 (1 extra from adjacent arc); see pytest_full.txt |
| 2a | lint on Done/executable-561.md: VERDICT=PASS, exit 0 | ✅ | RUN_CHECK: lint VERDICT=PASS — exit 0; EXIT=0; see probes-raw.txt |
| 2b | cycle STRICT on Done/executable-561.md: honest verdict recorded | ✅ | RUN_CHECK: cycle VERDICT=PASS — BAR_MET; EXIT=0; see probes-raw.txt |
| 2c | register on walk-register-plan-lint-bare-constants-2026-08-26.md: exit 0 iff PASS | ✅ | RUN_CHECK: register VERDICT=PASS — 1 file(s) CONFORMANT, 0 UNCONFORMANT; EXIT=0; 0-iff-PASS confirmed; see probes-raw.txt |
| 2d | cmp tools/run_check.py committed vs live | ✅ | cmp exit 0; see probes-raw.txt |
| 2e | cmp tests/test_run_check.py committed vs live | ✅ | cmp exit 0; see probes-raw.txt |
| 3a | numstat 3 files | ✅ | 3 files, all additions; see probes-raw.txt |
| 3b | toplevel correct | ✅ | matches worktree path |
| 3c | reflog -n 4: 0 amends | ✅ | 2 entries, no amend; see probes-raw.txt |

============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: knowledge/qa/evidence/run-check-wrapper-2026-08-26/
Files verified: 3
