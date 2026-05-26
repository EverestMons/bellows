# QA Report — Bellows Hardening Batch Items 1, 3, 4
**Plan:** executable-bellows-hardening-batch-items-1-3-4-2026-05-26
**Date:** 2026-05-26
**Agent:** Bellows QA
**Step:** 2 (QA)

---

## DEV Output Receipt Verification

DEV deposit at `knowledge/development/bellows-hardening-batch-items-1-3-4-2026-05-26.md` — Output Receipt status: **Complete**. All sections present including pre-edit verification, three change blocks with before/after snippets, regression tests, pytest output, and anchor verification.

DEV flag for next step: `test_run_plan_continuation_prompt_uses_shadow_path` was updated to use a non-sparse `plan_header` (3 keys including `pause_for_verdict: "never"`) to avoid interference from Item 4's defensive default propagation. Verified: this is a correct behavioral change — the test's purpose is shadow-path verification, not pause behavior. The test continues to PASS.

---

## Deliverable Verification (Rule 17)

| # | Deliverable | Expected | Status | Evidence |
|---|-------------|----------|--------|----------|
| 1 | Item 1 evidence string at gates.py:441 | New disambiguated string `"deposits block declares no .md paths..."` | OK | `evidence/gates_441_grep.txt` — 1 hit at line 441 |
| 2 | Item 1 line 464 preserved | Original `"no QA deposit contains Rule 20 self-check banner"` | OK | `evidence/gates_464_grep.txt` — 1 hit at line 464 |
| 3 | Item 3 on_modified invalidation logic | Lifecycle-prefix guard + `_seen.discard(slug)` + `_handle(path)` at end | OK | `evidence/on_modified_handler.txt` — all 3 structural requirements verified |
| 4 | Item 4 defensive default re-application | 3 occurrences of `_apply_defensive_header_defaults` (def + 2 calls) | OK | `evidence/defensive_default_callsites.txt` — 3 hits: lines 318, 382, 499 |
| 5 | Item 1 regression test | `test_rule_20_self_check_distinguishes_no_md_paths_from_missing_banner` exists | OK | `evidence/test_item_1_grep.txt` — 1 hit at test_gates.py:1589 |
| 6 | Item 3 regression tests | `test_on_modified_invalidates_seen_for_runnable_plan` + `test_on_modified_preserves_seen_for_lifecycle_renames` | OK | `evidence/test_item_3_grep.txt` — 2 hits at test_bellows.py:2944, 2972 |
| 7 | Item 4 regression test | `test_apply_defensive_header_defaults_propagates_to_reparsed_header` exists | OK | `evidence/test_item_4_grep.txt` — 1 hit at test_bellows.py:3001 |
| 8 | Dev log exists with required sections | 3 change blocks, pre-edit verification, pytest output, anchor verification | OK | `evidence/dev_log_check.txt` — 170 lines, all sections present |

**Result: 8/8 deliverables verified.**

---

## Test Execution

```
=================== 5 failed, 411 passed, 1 warning in 7.63s ===================
```

| Metric | Expected | Actual | Status |
|--------|----------|--------|--------|
| Total passed | 410 (407 + 3 new) | 411 (407 + 3 new + 1 existing fix) | OK |
| Total failed | 5 known carry-overs | 5 known carry-overs | OK |
| New regressions | 0 | 0 | OK |
| New tests pass | 4 (3 new + 1 fix) | 4 all PASSED | OK |

DEV reported 411 passed (407 baseline + 3 new + 1 existing test fix). QA independently confirms 411 passed, 5 failed (all carry-overs).

New regression tests confirmed PASSED:
- `test_rule_20_self_check_distinguishes_no_md_paths_from_missing_banner`
- `test_on_modified_invalidates_seen_for_runnable_plan`
- `test_on_modified_preserves_seen_for_lifecycle_renames`
- `test_apply_defensive_header_defaults_propagates_to_reparsed_header`

Known carry-over failures (unchanged):
- 4 x `test_decisions.py` — worktree-context `INTERMEDIATE_DECISION_PHRASES.md` not found
- 1 x `test_runner_parser.py::test_run_step_timeout` — long-standing assertion mismatch

Evidence: `evidence/pytest_full.txt`

---

## Structural-Compliance Checks

### (a) Single-file scope for Item 1

`git diff HEAD~2 HEAD -- gates.py` confirms Item 1's change is bounded to `gates.py` — single string replacement at line 441. No incidental edits to bellows.py, verdict.py, or elsewhere.

Evidence: `evidence/item_1_scope.txt`

### (b) Lifecycle-prefix list completeness for Item 3

Guard in `on_modified` (bellows.py:1039): `LIFECYCLE_PREFIXES = ("in-progress-", "verdict-pending-", "halted-")`

Cross-referenced against all project documentation:
- `agents/BELLOWS_DEVELOPER.md:64` — "three lifecycle prefixes (`in-progress-`, `verdict-pending-`, `halted-`)"
- `agents/BELLOWS_QA.md:40` — "three plan lifecycle prefixes (`in-progress-`, `verdict-pending-`, `halted-`)"
- `gates.py:30` — `SCOPE_ALLOWLIST_PREFIXES = ("in-progress-", "verdict-pending-", "halted-")`
- `PROJECT_STATUS.md` — same three prefixes documented

No fourth prefix exists in any project documentation. The guard is complete.

Evidence: `evidence/lifecycle_prefix_audit.txt`

### (c) Defensive default call symmetry for Item 4

Pre-gate call (bellows.py:382): `_apply_defensive_header_defaults(header, total_steps)`
Post-gate call (bellows.py:499): `_apply_defensive_header_defaults(header, total_steps)`

Both call sites pass identical arguments `(header, total_steps)`. Symmetric.

Evidence: `evidence/defensive_default_symmetry.txt`

---

## Rule 20 Self-Check

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: knowledge/qa/evidence/executable-bellows-hardening-batch-items-1-3-4-2026-05-26/
Files verified: 12
```

---

## Flags for CEO

- REMINDER: restart Bellows daemon to load (a) the new Item 1 evidence string for verdict-read disambiguation, (b) the new Item 3 `_seen` invalidation logic for corrected-redeposit recovery, and (c) the new Item 4 defensive-default propagation. The running daemon executed this plan with pre-edit code; the three fixes activate on next plan dispatched after restart.

---

## Output Receipt
**Agent:** Bellows QA
**Step:** 2
**Status:** Complete

### What Was Done
Verified all 8 deliverables from DEV Step 1, ran full test suite (411 passed, 5 known carry-overs, 0 regressions), confirmed 3 structural-compliance checks (Item 1 single-file scope, Item 3 lifecycle-prefix completeness, Item 4 call symmetry), executed Rule 20 self-check, and updated PROJECT_STATUS.md.

### Files Deposited
- `bellows/knowledge/qa/executable-bellows-hardening-batch-items-1-3-4-2026-05-26.md` — this QA report
- `bellows/knowledge/qa/evidence/executable-bellows-hardening-batch-items-1-3-4-2026-05-26/` — 12 evidence files

### Files Created or Modified (Code)
- `bellows/PROJECT_STATUS.md` — prepended 2026-05-26 completion entry for hardening batch items 1, 3, 4

### Decisions Made
- Accepted DEV's update to `test_run_plan_continuation_prompt_uses_shadow_path` as a correct behavioral change (not a regression) — the test was previously passing due to the Item 4 bug (defensive default not propagating to re-parsed header)

### Flags for CEO
- REMINDER: restart Bellows daemon to load (a) the new Item 1 evidence string for verdict-read disambiguation, (b) the new Item 3 `_seen` invalidation logic for corrected-redeposit recovery, and (c) the new Item 4 defensive-default propagation. The running daemon executed this plan with pre-edit code; the three fixes activate on next plan dispatched after restart.

### Flags for Next Step
- None
