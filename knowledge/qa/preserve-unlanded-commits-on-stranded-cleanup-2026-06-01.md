# QA Report — Preserve Un-Landed Commits on Stranded-Worktree Cleanup (Gap 2a)

**Date:** 2026-06-01
**Plan:** `executable-preserve-unlanded-commits-on-stranded-cleanup-2026-06-01`
**Step:** 2 (QA)
**Scope:** Code-level only (no live daemon run)

---

## Deliverable Verification (Rule 17)

| # | Deliverable | Expected | Status | Evidence |
|---|---|---|---|---|
| 1 | Preserve guard at top of stranded-cleanup block | rev-parse HEAD + merge-base --is-ancestor + git branch bellows-preserved/ | ✅ | `evidence/preserve_guard.txt` |
| 2 | Fail-safe bias correct | Skip only on HEAD-unreadable or clean returncode 0 | ✅ | `evidence/failsafe_bias.txt` |
| 3 | Destroy/recreate unchanged | remove --force → rmtree → prune → add HEAD --detach byte-unchanged | ✅ | `evidence/recreate_unchanged.txt` |
| 4 | Out-of-scope code untouched | Diff confined to inside-top of stranded-cleanup block | ✅ | `evidence/diff_scope.txt` |
| 5 | Three regression tests exist | All three test functions present in test_worktree.py | ✅ | `evidence/new_tests_grep.txt` |
| 6 | Dev log complete | All sections filled, Output Receipt Complete | ✅ | `evidence/dev_log_check.txt` |

---

## Test Execution

**Command:** `python3 -m pytest tests/ -v`
**Result:** 5 failed, 440 passed, 1 warning in 8.05s

- All three new tests PASS
- ZERO new failures beyond the carry-over baseline
- Total pass count: 440 (matches DEV's reported post-edit count)
- Carry-over failures (5): 4x test_decisions.py (phrase file not in worktree) + 1x test_run_step_timeout

Evidence: `evidence/pytest_full.txt`

---

## Specificity Check

`test_stranded_cleanup_no_preserve_when_already_landed` (line 426) proves that an already-landed worktree (HEAD == main HEAD) creates NO `bellows-preserved/*` branch. The test asserts `br_list.stdout.strip() == ""` after listing all `bellows-preserved/*` branches.

Evidence: `evidence/no_spurious_branch.txt`

---

## Branch-Leak Check

All three new tests clean up `bellows-preserved/*` branches they create:

- **Test 1** (`test_stranded_cleanup_preserves_unlanded_commits`): `finally` block at lines 413-423 iterates `branches` list and runs `git branch -D` on each.
- **Test 2** (`test_stranded_cleanup_no_preserve_when_already_landed`): No cleanup needed — asserts no branches are created.
- **Test 3** (`test_stranded_cleanup_failsafe_preserves_when_main_unresolvable`): `finally` block at lines 504-514 iterates `branches` list and runs `git branch -D` on each.

Cleanup mechanism: per-test `finally` blocks (matching module's existing pattern). No global fixture dependency. No branch leakage between tests.

---

## Rule 20 Self-Check

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: /Users/marklehn/Developer/GitHub/bellows/.bellows-worktrees/preserve-unlanded-commits-on-stranded-cleanup-2026-06-01/knowledge/qa/evidence/preserve-unlanded-commits-on-stranded-cleanup-2026-06-01/
Files verified: 8
```

---

## Flags for CEO

REMINDER: restart the Bellows daemon to activate the preserve guard. The running daemon executed this plan with pre-edit `_create_worktree`; the guard activates on the next plan dispatched after restart. Also owed: capture this plan's organic Opus baseline (turns/wall) from the step logs for the Opus/Sonnet A/B.

---

## Output Receipt
**Agent:** Bellows QA
**Step:** 2
**Status:** Complete

### What Was Done
Verified all 6 deliverables from DEV Step 1 (preserve guard placement, fail-safe bias, destroy/recreate unchanged, diff scope, regression tests, dev log). Ran full test suite confirming 440 passed with zero new regressions. Verified specificity (no spurious branches on landed path) and branch-leak cleanup. Rule 20 self-check PASSED.

### Files Deposited
- `knowledge/qa/preserve-unlanded-commits-on-stranded-cleanup-2026-06-01.md` — this QA report
- `knowledge/qa/evidence/preserve-unlanded-commits-on-stranded-cleanup-2026-06-01/` — 8 evidence files

### Files Created or Modified (Code)
- `PROJECT_STATUS.md` — prepended 2026-06-01 Gap 2a completion entry

### Decisions Made
- Confirmed all carry-over failures match DEV's pre-edit baseline (no investigation needed)
- Branch-leak check passes via per-test finally blocks (no fixture-level cleanup needed)

### Flags for CEO
- REMINDER: restart the Bellows daemon to activate the preserve guard. The running daemon executed this plan with pre-edit `_create_worktree`; the guard activates on the next plan dispatched after restart. Also owed: capture this plan's organic Opus baseline (turns/wall) from the step logs for the Opus/Sonnet A/B.

### Flags for Next Step
- None
