# no_permission_denials Read-Class Fix — QA Report

**Date:** 2026-04-28
**Plan:** executable-no-permission-denials-read-class-fix-2026-04-28
**Step:** 2 (Bellows QA)

---

## 1. Rule 17 — Deliverable Verification

| # | Check | Result | Evidence |
|---|---|---|---|
| a | `grep -n READ_CLASS_TOOLS gates.py` returns 2+ matches (constant + use) | ✅ 2 matches: L20 (constant), L112 (use in function) | `evidence/.../grep_deliverables.txt` |
| b | `grep -n blocking gates.py` shows new variable in modified function | ✅ 7 matches: L108, L114, L116, L117, L118, L119, L122 | `evidence/.../grep_deliverables.txt` |
| c | `grep -c test_permission_denials_ tests/test_gates.py` returns 8+ | ✅ 8 (1 existing + 7 new) | `evidence/.../grep_deliverables.txt` |

All three deliverable checks confirmed. Changes landed as declared in Step 1 Output Receipt.

---

## 2. Test Execution Summary

**Full suite:** 164 collected, 163 passed, 1 failed (pre-existing `test_run_step_timeout`).

| Metric | Before (Step 1 baseline) | After |
|---|---|---|
| test_gates.py tests | 22 | 29 (+7 new) |
| Total suite | 157 passed / 1 failed | 163 passed / 1 failed |
| Regressions | — | 0 |

The sole failure (`test_run_step_timeout` in test_runner_parser.py) is a pre-existing issue unrelated to this change. Zero regressions introduced.

Full output: `evidence/executable-no-permission-denials-read-class-fix-2026-04-28/pytest_full.txt`

---

## 3. Behavioral Verification

Simulated the exact BACKLOG #2 production pattern (Grep denial against governance root) and a write-class denial (Edit):

| Scenario | Gate Fired | Expected | Result |
|---|---|---|---|
| Grep denial (read-class, cross-project path) | False | False | ✅ Correctly filtered |
| Edit denial (write-class) | True | True | ✅ Correctly blocks |

Both results match expectations. The read-class taxonomy fix correctly filters Grep/Glob/Read denials while preserving write-class blocking behavior.

Full output: `evidence/executable-no-permission-denials-read-class-fix-2026-04-28/behavioral_check.txt`

---

## 4. BACKLOG #2 Closure Verdict

**BACKLOG #2 is ready for closure.** The fix addresses the root cause identified in the diagnostic: 100% of observed `no_permission_denials` gate failures were caused by read-class tools (Grep, Glob) hitting cross-project paths. The `READ_CLASS_TOOLS` allowlist correctly exempts these tools while maintaining blocking behavior for write-class tools and defensive handling of unknown/missing tool names. 7 new edge-case tests provide comprehensive coverage per the diagnostic's Q5 table.

**Bellows daemon restart required** to load the new gate code.

---

## 5. Rule 20 — QA Self-Check

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: /Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/evidence/executable-no-permission-denials-read-class-fix-2026-04-28/
Files verified: 3
```

---

## Output Receipt
**Agent:** Bellows QA
**Step:** 2
**Status:** Complete

### What Was Done
Verified Step 1 deliverables (Rule 17), ran full pytest suite (163/164 pass, 0 regressions), performed behavioral verification (read-class filtered, write-class blocks), wrote QA report, ran Rule 20 self-check.

### Files Deposited
- `bellows/knowledge/qa/no-permission-denials-read-class-fix-qa-2026-04-28.md`
- `bellows/knowledge/qa/evidence/executable-no-permission-denials-read-class-fix-2026-04-28/grep_deliverables.txt`
- `bellows/knowledge/qa/evidence/executable-no-permission-denials-read-class-fix-2026-04-28/pytest_full.txt`
- `bellows/knowledge/qa/evidence/executable-no-permission-denials-read-class-fix-2026-04-28/behavioral_check.txt`

### Files Created or Modified (Code)
- None (QA verification only)

### Decisions Made
- Pre-existing `test_run_step_timeout` failure acknowledged as unrelated
- BACKLOG #2 closure recommended

### Flags for CEO
- None

### Flags for Next Step
- None (terminal step)
