# QA Report — _teardown_worktree (b): raise on git-log failure

**Date:** 2026-06-05
**Plan:** executable-teardown-b-raise-on-log-failure-2026-06-05
**Step:** 2 (QA)
**Scope:** Code-level ONLY (no daemon start, no plan deposit, no live dispatch)

---

## DEV Deposit Verification

DEV Step 1 deposit at `knowledge/development/teardown-b-raise-on-log-failure-2026-06-05.md` — Output Receipt Status: **Complete**.

---

## Deliverable Verification (Rule 17)

| # | Deliverable | Expected | Status | Evidence |
|---|---|---|---|---|
| 1 | Exception path raises | `try/except Exception as e: raise WorktreeTeardownError(...) from e` | PASS | `evidence/teardown-b-raise-on-log-failure-2026-06-05/raise_paths.txt` |
| 2 | Non-zero returncode raises | `if result.returncode != 0: raise WorktreeTeardownError(...)` with stderr | PASS | `evidence/teardown-b-raise-on-log-failure-2026-06-05/raise_paths.txt` |
| 3 | Legitimate-empty preserved | returncode 0, empty stdout does NOT raise; `commit_shas = result.stdout.strip().splitlines()[::-1]` | PASS | `evidence/teardown-b-raise-on-log-failure-2026-06-05/empty_case_preserved.txt` |
| 4 | Rest of function byte-unchanged | Steps (a), index.lock, (b2), (c), (d), (e) unchanged | PASS | `evidence/teardown-b-raise-on-log-failure-2026-06-05/block_body.txt` |
| 5 | Diff scope | Changes confined to step (b) only in bellows.py | PASS | `evidence/teardown-b-raise-on-log-failure-2026-06-05/diff_scope.txt` |
| 6 | Three new tests exist | `test_teardown_raises_on_git_log_exception`, `test_teardown_raises_on_git_log_nonzero`, `test_teardown_proceeds_on_empty_commit_list` | PASS | `evidence/teardown-b-raise-on-log-failure-2026-06-05/new_tests_grep.txt` |
| 7 | Existing teardown tests intact | 4 existing tests present and passing | PASS | `evidence/teardown-b-raise-on-log-failure-2026-06-05/existing_tests.txt` |
| 8 | Dev log complete | Replaced block, byte-unchanged confirmation, fail-vs-empty, pre-edit verification, both pytest runs | PASS | `evidence/teardown-b-raise-on-log-failure-2026-06-05/dev_log_check.txt` |

**Result: 8/8 PASS — no blockers.**

---

## Test Execution

Full suite: `python3 -m pytest tests/ -v`

- **Result:** 5 failed, 455 passed, 1 warning in 9.59s
- (a) All 3 new tests PASS
- (b) All 4 existing teardown tests PASS
- (c) Zero new failures — same 5 carry-over as DEV's pre-edit baseline
- (d) Total pass count 455 == DEV's reported post-edit number

Evidence: `evidence/teardown-b-raise-on-log-failure-2026-06-05/pytest_full.txt`

---

## Rule 20 Self-Check

**Output:**

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: knowledge/qa/evidence/teardown-b-raise-on-log-failure-2026-06-05/
Files verified: 8
```

---

## Flags for CEO

REMINDER: restart the Bellows daemon to activate the teardown-(b) raise. The running daemon executed this plan under the pre-edit `_teardown_worktree`; the fail-safe activates on the next teardown after restart. Also owed: capture this plan's organic Opus baseline (turns/wall/cost) from the step logs for the Opus<->Sonnet A/B.

---

## Output Receipt
**Agent:** Bellows QA
**Step:** 2
**Status:** Complete

### What Was Done
Verified DEV's Step 1 deliverables: both raise paths present, legitimate-empty case preserved, diff confined to step (b), all 3 new tests and 4 existing teardown tests passing, zero new regressions (455 passed matches DEV's post-edit count). Rule 20 self-check executed.

### Files Deposited
- `knowledge/qa/teardown-b-raise-on-log-failure-2026-06-05.md` — this QA report
- `knowledge/qa/evidence/teardown-b-raise-on-log-failure-2026-06-05/` — 8 evidence files

### Files Created or Modified (Code)
- `PROJECT_STATUS.md` — prepended 2026-06-05 Completed entry

### Decisions Made
- Verified all 8 deliverables independently from DEV's report
- Confirmed 5 carry-over failures are identical to DEV's pre-edit baseline (not new regressions)

### Flags for CEO
- REMINDER: restart the Bellows daemon to activate the teardown-(b) raise. The running daemon executed this plan under the pre-edit `_teardown_worktree`; the fail-safe activates on the next teardown after restart. Also owed: capture this plan's organic Opus baseline (turns/wall/cost) from the step logs for the Opus<->Sonnet A/B.

### Flags for Next Step
- None
