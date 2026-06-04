# QA Report — Invalidate _seen on Re-Deposit via on_created / on_moved (#7)

**Date:** 2026-06-04
**Plan:** executable-seen-invalidate-on-created-moved-2026-06-04
**Step:** 2 (QA)

---

## DEV Output Receipt Status

DEV Step 1 deposit at `knowledge/development/seen-invalidate-on-created-moved-2026-06-04.md` — **Status: Complete**. No blockers.

---

## Deliverable Verification (Rule 17)

| # | Deliverable | Expected | Status | Evidence |
|---|-------------|----------|--------|----------|
| 1 | Helper present and correct | `_invalidate_seen_on_redeposit(self, path)` with filename computation, LIFECYCLE_PREFIXES guard, conditional discard | PASS | `evidence/seen-invalidate-on-created-moved-2026-06-04/helper_body.txt` — method at L1190, all elements verified |
| 2 | All three callbacks call helper before `_handle` | `on_created` (src_path), `on_modified` (src_path), `on_moved` (dest_path) each call helper then `_handle` | PASS | `evidence/seen-invalidate-on-created-moved-2026-06-04/callbacks.txt` — L1205-1218, order confirmed |
| 3 | Lifecycle guard preserved verbatim | Three-prefix tuple matches original, early-return on any match | PASS | `evidence/seen-invalidate-on-created-moved-2026-06-04/guard_check.txt` — L1197-1199, byte-match |
| 4 | `_handle` and rescan path byte-unchanged | `_seen` guard at L1166, `from_rescan=True` at L1306, no invalidation added | PASS | `evidence/seen-invalidate-on-created-moved-2026-06-04/handle_unchanged.txt` — confirmed untouched |
| 5 | Diff scope | Changes confined to new helper + three callback bodies only | PASS | `evidence/seen-invalidate-on-created-moved-2026-06-04/diff_scope.txt` — git diff verified |
| 6 | Four new tests exist | All four test function names present in test_bellows.py | PASS | `evidence/seen-invalidate-on-created-moved-2026-06-04/new_tests_grep.txt` — L3324, L3352, L3381, L3408 |
| 7 | Parity tests intact | Two existing on_modified tests still present and passing | PASS | `evidence/seen-invalidate-on-created-moved-2026-06-04/parity_tests.txt` — L3267, L3295, both PASSED |
| 8 | Dev log complete | All required sections present with content | PASS | `evidence/seen-invalidate-on-created-moved-2026-06-04/dev_log_check.txt` — 122 lines, all sections verified |

**Result: 8/8 PASS — no blockers.**

---

## Test Execution

Full suite: `python3 -m pytest tests/ -v`

**Result: 448 passed, 5 failed, 1 warning in 7.65s**

### Four new tests — all PASS:
- `test_on_created_invalidates_seen_for_runnable_plan` — PASSED
- `test_on_created_preserves_seen_for_lifecycle_renames` — PASSED
- `test_on_moved_invalidates_seen_for_runnable_plan` — PASSED
- `test_on_moved_preserves_seen_for_lifecycle_renames` — PASSED

### Two existing on_modified tests — still PASS:
- `test_on_modified_invalidates_seen_for_runnable_plan` — PASSED
- `test_on_modified_preserves_seen_for_lifecycle_renames` — PASSED

### Zero new failures:
Same 5 carry-over failures as DEV's pre-edit baseline:
- 4x `test_decisions.py` (missing `INTERMEDIATE_DECISION_PHRASES.md` in worktree)
- 1x `test_runner_parser.py::test_run_step_timeout`

### Total pass count: 448 — matches DEV's reported post-edit count.

Evidence: `evidence/seen-invalidate-on-created-moved-2026-06-04/pytest_full.txt`

---

## Behavioral Spot-Checks

Read from test assertions (no live runs invented):

**(i) Create/move invalidate tests** assert slug is GONE from `_seen` before `_handle` is called, and `_handle` is called once with the correct path (`src_path` for create, `dest_path` for move).

**(ii) Create/move lifecycle tests** assert slug is RETAINED for each of the three lifecycle prefixes (`in-progress-`, `verdict-pending-`, `halted-`), and `_handle` is still called once.

Evidence: `evidence/seen-invalidate-on-created-moved-2026-06-04/behavior_spotcheck.txt`

---

## Rule 20 Self-Check

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: knowledge/qa/evidence/seen-invalidate-on-created-moved-2026-06-04/
Files verified: 10
```

---

## Flags for CEO

- REMINDER: restart the Bellows daemon to activate the create/move `_seen` invalidation. The running daemon executed this plan with the pre-edit watcher; the fix activates on the next watcher event after restart. Also owed: capture this plan's organic Opus baseline (turns/wall/cost) from the step logs for the Opus/Sonnet A/B.

---

## Output Receipt
**Agent:** Bellows QA
**Step:** 2
**Status:** Complete

### What Was Done
Verified all 8 deliverables from DEV Step 1. Ran full test suite confirming 448 passed with zero new regressions. Confirmed behavioral correctness of all 6 _seen tests via assertion spot-checks. Rule 20 self-check executed.

### Files Deposited
- `knowledge/qa/seen-invalidate-on-created-moved-2026-06-04.md` — this QA report
- `knowledge/qa/evidence/seen-invalidate-on-created-moved-2026-06-04/` — 10 evidence files

### Files Created or Modified (Code)
- `PROJECT_STATUS.md` — prepended 2026-06-04 completion entry

### Decisions Made
- All 8 deliverable checks PASS — no escalation needed

### Flags for CEO
- REMINDER: restart the Bellows daemon to activate the create/move `_seen` invalidation. The running daemon executed this plan with the pre-edit watcher; the fix activates on the next watcher event after restart. Also owed: capture this plan's organic Opus baseline (turns/wall/cost) from the step logs for the Opus/Sonnet A/B.

### Flags for Next Step
- None
