# Deposit-Loss Fix — QA Report

**Date:** 2026-06-10 | **Plan:** bellows-deposit-loss-fix-2026-06-10 | **Step:** 2 (QA)

## Deliverable Verification (Rule 17)

| Deliverable | Expected | Status | Evidence |
|---|---|---|---|
| `_auto_stage_deposits` defined in `bellows.py` | Function exists at line ~886 | ✅ | `grep -n "def _auto_stage_deposits" bellows.py` -> `886:def _auto_stage_deposits(...)` |
| `_auto_stage_deposits` called before `gates.check()` (site 1) | Line 495 precedes line 500 | ✅ | `grep -n` confirms `_auto_stage_deposits` at 495, `gates.check` at 500 |
| `_auto_stage_deposits` called before `gates.check()` (site 2) | Line 591 precedes line 596 | ✅ | `grep -n` confirms `_auto_stage_deposits` at 591, `gates.check` at 596 |
| `_gate_deposit_exists` has `git status --porcelain` check | `_check_deposit_uncommitted` at line 351 | ✅ | `grep -n "status.*porcelain" gates.py` -> line 361 |
| `test_auto_stage_preserves_untracked_deposit_on_teardown` | Exists in `tests/test_worktree.py` | ✅ | Line 907 |
| `test_auto_stage_handles_multiple_deposits` | Exists in `tests/test_worktree.py` | ✅ | Line 947 |
| `test_auto_stage_noop_when_all_committed` | Exists in `tests/test_worktree.py` | ✅ | Line 989 |
| `test_gate_fails_on_uncommitted_deposit` | Exists in `tests/test_gates.py` | ✅ | Line 1977 |
| `test_gate_deposit_uncommitted_evidence_message` | Exists in `tests/test_gates.py` | ✅ | Line 2017 |
| `test_gate_passes_when_deposit_committed` | Exists in `tests/test_gates.py` | ✅ | Line 2061 |

All deliverables verified. Full grep evidence in `deliverable_grep.txt`.

## QA Checks

### Check 1: Preserve (load-bearing)

`test_auto_stage_preserves_untracked_deposit_on_teardown` and `test_auto_stage_handles_multiple_deposits` both **PASSED**. An untracked declared deposit is now auto-staged, committed, and survives teardown merge to main.

Evidence: `preserve.txt` (2 passed, 0 failed)

### Check 2: Fail-loud residue

`test_gate_fails_on_uncommitted_deposit` and `test_gate_deposit_uncommitted_evidence_message` both **PASSED**. The gate correctly fails with `deposit_uncommitted` when a declared deposit exists on disk but is not committed, and the evidence message contains the path and clear description.

Evidence: `fail_loud.txt` (2 passed, 0 failed)

### Check 3: No-op + ordering

`test_auto_stage_noop_when_all_committed` **PASSED** (no extra commit when all deposits already committed). Grep confirms `_auto_stage_deposits` precedes `gates.check()` at both call sites (lines 495<500, 591<596), so (b) evaluates post-commit state per the ordering correction.

Evidence: `ordering_noop.txt`

### Check 4: Hardened-teardown regression (CRITICAL)

All 4 existing tests **PASSED** unchanged:
- `test_teardown_merges_commits` — PASSED
- `test_teardown_proceeds_on_empty_commit_list` — PASSED
- `test_landing_tolerates_dirty_main_invariant` — PASSED
- `test_teardown_raises_on_git_log_exception` — PASSED

Evidence: `teardown_regression.txt` (4 passed, 0 failed)

### Check 5: Full suite

`pytest tests/` — **461 passed**, 1 warning, in 6.59s. Full green (455 prior baseline + 6 new).

Evidence: `pytest_full.txt`

## Rule 20 Self-Check

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: /Users/marklehn/Developer/GitHub/bellows/.bellows-worktrees/bellows-deposit-loss-fix-2026-06-10/knowledge/qa/evidence/bellows-deposit-loss-fix-2026-06-10/
Files verified: 6
```

### Output Receipt

| Field | Value |
|---|---|
| Status | Complete |
| Deposit | `knowledge/qa/deposit-loss-fix-2026-06-10-qa.md` |
| Evidence | `knowledge/qa/evidence/bellows-deposit-loss-fix-2026-06-10/` |
