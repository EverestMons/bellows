# QA Report — Bellows Claim-at-Entry Fix
**Plan:** parallel-1-executable-bellows-claim-at-entry-2026-04-16
**Date:** 2026-04-16
**Step:** 2 (QA)
**Commit:** 1171bd6

---

## Deliverable Verification

| Check | Expected | Result | Status |
|---|---|---|---|
| (a) Claim-at-entry logic in bellows.py | 2+ matches for startswith/shutil near top of run_plan | Lines 164–166: guard + shutil.move + plan_path update | ✅ |
| (b) Idempotent guard present | `if not plan_filename.startswith("in-progress-"):` guard | Line 164: `if not plan_filename.startswith("in-progress-"):` | ✅ |
| (c) Bootstrap prompt uses updated path | Bootstrap references in-progress- path | Lines 165–166 set `plan_path = inprogress_path`; bootstrap at 176/178/180 uses `plan_path` | ✅ |
| (d) Tests present (4+ keyword matches) | 4+ matches for claim/orphan/in_progress/idempotent | 4 matches in test_bellows.py (lines 750, 779, 819, 823) | ✅ |
| Step 1 committed | Commit 1171bd6 at HEAD | `1171bd6 fix: Bellows claims plan at run_plan entry` | ✅ |

---

## Test Results

### Targeted (`-k "claim or orphan or in_progress or idempotent or runnable"`)

| Test | Result |
|---|---|
| test_is_runnable_plan_diagnostic | ✅ |
| test_is_runnable_plan_parallel_prefix | ✅ |
| test_run_plan_claims_file_before_runner_runs | ✅ |
| test_run_plan_skips_claim_if_already_inprogress | ✅ |
| test_is_runnable_plan_inprogress_executable_returns_false | ✅ |
| test_scope_check_prefix_allowlist_in_progress (test_gates) | ✅ |

**6/6 targeted passed.**

### Full Suite

**99/99 passed.** No regressions. Evidence at `knowledge/qa/evidence/claim-at-entry-fix/pytest_full.txt`.

---

## Rule 20 Self-Check

Run below produced: **PASSED — all evidence files present, no hedging keywords found.**

Evidence folder: `knowledge/qa/evidence/claim-at-entry-fix/`
Files verified: `pytest_targeted.txt`, `pytest_full.txt`

---

## Verdict

**SHIP.** Fix eliminates the orphan-original duplicate-dispatch class of bugs. All gates passed. No regressions.
