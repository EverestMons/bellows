# QA Receipt — close-failopen-defaults-2026-09-04

**Plan:** executable-100037.md (close-failopen-defaults)
**Step:** 2 (QA)
**Date:** 2026-09-04
**Worktree:** `/Users/marklehn/Developer/bellows/.bellows-worktrees/100037`
**DEV commit:** `0383b6c` (FO-1 and FO-3 closed — manifest gate and qa_steps normalization)
**QA commit:** `6f9faea` (fixture and mutant manifest corrections)

---

## Summary

Step 2 QA was executed from the dispatch worktree. The full suite is green (1870 passed, 1 skipped, 0 failed). Both fail-open paths (FO-1 and FO-3) are shown discriminating: the pre-fix behavior accepted the demonstration inputs; the post-fix behavior refuses them. The legacy corpus is untouched by construction. The advisory stays advisory. All 6 mutants killed, 0 survived, 0 error. Both changed checkers pass on this plan itself (self-application).

Three DEV-step deficiencies were discovered and corrected in the QA commit:
1. `test_wrap_receipts.py::TestClearToolRelease._create_held_plan` — fixture manifest lacked `validation:` line; new FO-1 gate correctly rejected it.
2. `test_depositor_receipts.py::test_18_class_hold_releases` and `test_18_legacy_no_original_reason_releases` — same fixture deficiency.
3. `knowledge/mutants/close-failopen-defaults.json` — missing top-level `"target"` field required by `mutation_check.py`; added `"scripts/cycle_check.py"` (each mutant already carried its own override).

The DEV commit also changed `tests/test_cycle_check.py` (updating BAR_MET fixture helpers to include complete manifests), making the effective file count 7 rather than the declared 6. Documented below.

---

## Verification

| Item | Check | Status |
|------|-------|--------|
| 1 | Full suite from worktree — 1870 passed, 1 xfail, 0 failed | ✅ |
| 2a | FO-1 BEFORE: `_manifest_validation_keys` returned `None` on halted-100031 → gate inactive → BAR_MET | ✅ |
| 2b | FO-1 AFTER: returns `frozenset()` → gate fires → ESCALATE:claimed-close-unmet | ✅ |
| 2c | FO-3 BEFORE: `qa_steps: none` truthy → demanded banner → FAIL (c) | ✅ |
| 2d | FO-3 AFTER: normalized to absent → no FAIL (c) → exit 0 | ✅ |
| 3 | cycle_check call sites: `depositor.py`, `tools/clear_plan.py`, `scripts/cycle_check.py` only — none scan `Done/` | ✅ |
| 4 | Advisory stays advisory: plan with `qa_steps: 2` + missing banner still exits 1 with FAIL (c) | ✅ |
| 5 | mutation_check: 6 killed, 0 survived, 0 error | ✅ |
| 6 | Self-application: `cycle_check` → BAR_MET; `plan_lint` → exit 0 | ✅ |
| 7a | numstat: DEV commit changed 7 files (test_cycle_check.py updated as side-effect); QA commit changed 3 fixture files | ✅ |
| 7b | reflog: 0 amends in last 6 entries | ✅ |
| 7c | DEV deficiencies: 3 fixture/manifest issues found and corrected in QA commit | ✅ |

---

## Verification (Rule 20 Self-Check)

The canonical Rule 20 self-check block was run after all evidence files were deposited. Stdout appended verbatim below.

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: /Users/marklehn/Developer/bellows/.bellows-worktrees/100037/knowledge/qa/evidence/close-failopen-defaults-2026-09-04/
Files verified: 2
```

