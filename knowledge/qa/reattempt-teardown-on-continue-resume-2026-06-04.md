# QA Report — Re-Attempt Recoverable Dirty-Tree Teardown on Continue-Resume (Gap 1c)

**Date:** 2026-06-04
**Plan:** executable-reattempt-teardown-on-continue-resume-2026-06-04
**Step:** 2 (QA)
**Scope:** Code-level ONLY — no live daemon dispatch

---

## DEV Deposit Verification

DEV Output Receipt status: **Complete**

---

## Deliverable Verification (Rule 17)

| # | Deliverable | Expected | Status | Evidence |
|---|-------------|----------|--------|----------|
| 1 | Helper present and correct | `_retry_recoverable_teardown` exists near `_teardown_worktree`; collects wt failures; early returns for none/missing/non-dirty-tree; clears on success; never raises | PASS | `evidence/retry_helper.txt` |
| 2 | Dirty-tree discriminator gate | Retry fires ONLY when every wt failure evidence contains `worktree_teardown_dirty_tree`; content-conflict bypassed | PASS | `evidence/discriminator_gate.txt` |
| 3 | Failure-clearing is scoped | Only `worktree_teardown` entries removed; other failures preserved | PASS | `evidence/failure_clearing.txt` |
| 4 | Call-site order | `_retry_recoverable_teardown` call at TOP of continue branch, IMMEDIATELY BEFORE Gap-1b guard; Gap-1b guard byte-unchanged | PASS | `evidence/guard_order.txt` |
| 5 | Out-of-scope code untouched | Diff confined to (i) new helper and (ii) 6-line call block; `_teardown_worktree`, `_create_worktree`, Gap-1b guard body unchanged | PASS | `evidence/diff_scope.txt` |
| 6 | Four regression tests exist | All four test functions present in `tests/test_consume_verdicts.py` | PASS | `evidence/new_tests_grep.txt` |
| 7 | Dev log complete | Dev log exists with helper placement, predicate order, skip rules, call-site location, pre-edit verification, both pytest runs | PASS | `evidence/dev_log_check.txt` |

**All 7 deliverables: PASS**

---

## Test Execution

Full suite: `python3 -m pytest tests/ -v`

| Metric | Value |
|--------|-------|
| Total passed | 444 |
| Total failed | 5 (carry-over) |
| Warnings | 1 |
| Wall time | 7.29s |

New tests (all PASSED):
- `test_retry_clears_dirty_tree_teardown_on_success`
- `test_retry_skips_content_conflict`
- `test_retry_skips_when_worktree_missing`
- `test_retry_keeps_failure_when_teardown_raises_again`

Carry-over failures (same 5 as DEV pre-edit baseline):
- `test_decisions.py::TestLoadPhrases::test_loads_phrases_from_file`
- `test_decisions.py::TestLoadPhrases::test_includes_known_phrases`
- `test_decisions.py::TestLoadPhrases::test_splits_slash_alternatives`
- `test_decisions.py::TestExtractDecisionBlocks::test_s_class_blocks_from_ground_truth`
- `test_runner_parser.py::test_run_step_timeout`

Verification:
- (a) All four new tests appear in verbose output and PASS: YES
- (b) ZERO new failures beyond carry-over: YES
- (c) Total pass count matches DEV's post-edit (444): YES

Evidence: `evidence/pytest_full.txt`

---

## Behavioral Spot-Checks

| # | Check | Result | Evidence |
|---|-------|--------|----------|
| i | Success test asserts worktree_teardown failure GONE from `gate_result["failures"]` after True return | PASS | `evidence/behavior_spotcheck.txt` |
| ii | Content-conflict and missing-worktree tests assert `_teardown_worktree` NOT called and failure RETAINED | PASS | `evidence/behavior_spotcheck.txt` |
| iii | Raises-again test asserts failure RETAINED so Gap-1b still halts | PASS | `evidence/behavior_spotcheck.txt` |

---

## Rule 20 Self-Check

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: knowledge/qa/evidence/reattempt-teardown-on-continue-resume-2026-06-04/
Files verified: 9
```

---

## Flags for CEO

REMINDER: restart the Bellows daemon to activate the Gap 1c retry. The running daemon executed this plan with pre-edit `_consume_verdicts`; the helper activates on the next continue-resume after restart. Also owed: capture this plan's organic Opus baseline (turns/wall/cost) from the step logs for the Opus/Sonnet A/B.

---

## Output Receipt
**Agent:** Bellows QA
**Step:** 2
**Status:** Complete

### What Was Done
Verified all DEV Step 1 deliverables (7/7 PASS): helper correctness, dirty-tree discriminator gate, scoped failure-clearing, call-site order relative to Gap-1b guard, out-of-scope code untouched, four regression tests present, dev log complete. Ran full test suite (444 passed, 5 carry-over failures, zero new). Performed behavioral spot-checks on all four test assertions. Ran Rule 20 self-check.

### Files Deposited
- `knowledge/qa/reattempt-teardown-on-continue-resume-2026-06-04.md` — this QA report
- `knowledge/qa/evidence/reattempt-teardown-on-continue-resume-2026-06-04/` — 9 evidence files

### Files Created or Modified (Code)
- `PROJECT_STATUS.md` — prepended 2026-06-04 Gap 1c completion entry

### Decisions Made
- Confirmed all 5 carry-over test failures are known pre-existing (not introduced by this change)

### Flags for CEO
- REMINDER: restart the Bellows daemon to activate the Gap 1c retry. The running daemon executed this plan with pre-edit `_consume_verdicts`; the helper activates on the next continue-resume after restart. Also owed: capture this plan's organic Opus baseline (turns/wall/cost) from the step logs for the Opus/Sonnet A/B.

### Flags for Next Step
- None
