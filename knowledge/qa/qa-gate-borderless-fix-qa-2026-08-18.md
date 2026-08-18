# QA Report: test-result gate mis-parses borderless pytest summaries

**Plan:** `executable-qa-gate-borderless-fix-2026-08-18`
**Step:** 2 — QA: full suite
**Date:** 2026-08-18
**Agent:** Bellows QA (plan 442)

---

## Summary

Full test suite executed via `python3 -m pytest tests/ -q 2>&1 | cat`. Result: **1105 passed, 1 warning in 32.46s**. Zero failures, zero errors. The Step 1 content-based summary detection fix and borderless regression tests are integrated and green.

## Evidence

| File | Location |
|------|----------|
| `full-suite.txt` | `knowledge/qa/evidence/qa-gate-borderless-fix-2026-08-18/full-suite.txt` |

## Verification Table

| Check | Status | Detail |
|-------|--------|--------|
| Full suite passes | ✅ | 1105 passed, 0 failed, 0 errors |
| Borderless regression tests included | ✅ | 4 new tests from Step 1 present in suite (test_borderless_clean_passes, test_borderless_failed_pauses, test_borderless_zero_failed_with_errors, test_warnings_summary_header_not_matched) |
| No regressions introduced | ✅ | All pre-existing tests continue to pass |
| Evidence deposited | ✅ | Raw pytest output saved to evidence directory |

## Planner Note (expected benign gate failure)

The live daemon still runs the old (buggy) gate until restarted, so this QA step's own `qa_test_result` gate will fail-closed on its borderless evidence exactly as canary 441 did. The Planner overrides with verified-clean reasoning (reads the raw `full-suite.txt`), same as 441. The fix takes effect only after the CEO restarts the daemon; a fresh canary then confirms true clean auto-continue.

## Rule 20 — QA Self-Check Results

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: /Users/marklehn/Developer/GitHub/bellows/.bellows-worktrees/442/knowledge/qa/evidence/qa-gate-borderless-fix-2026-08-18/
Files verified: 1
```
