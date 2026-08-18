# QA Report: Auto-continue-unless-errors (plan 439, step 4)

**Plan:** `executable-bellows-autocontinue-2026-08-18`
**Date:** 2026-08-18
**Suite:** `python3 -m pytest tests/ -q`
**Result:** 1098 passed, 0 failed, 0 errors, 1 warning

## Full suite summary

All 1098 tests pass. No failures, no errors. The single warning is an unrelated urllib3/LibreSSL version notice.

Evidence: `knowledge/qa/evidence/bellows-autocontinue-2026-08-18/full-suite.txt`

## Verification table

| # | Check | Status | Evidence |
|---|-------|--------|----------|
| 1 | Backward compat (Q7): `always` mode unchanged | ✅ | `test_always_still_pauses` PASSED; `test_site1_always_qa_pauses` PASSED |
| 2 | Backward compat (Q7): `after_step_1` mode unchanged | ✅ | `test_after_step_1_still_pauses_step1` + `test_after_step_1_no_pause_step2` PASSED |
| 3 | Backward compat (Q7): `after_qa_step` mode unchanged | ✅ | `test_after_qa_step_pauses_qa` + `test_after_qa_step_no_pause_non_qa` PASSED |
| 4 | Backward compat (Q7): `qa_and_terminal` mode unchanged | ✅ | `test_qa_and_terminal_pauses_qa` + `test_qa_and_terminal_pauses_final` PASSED; `test_site1_qa_and_terminal_qa_pauses` PASSED |
| 5 | QA-result gate: clean summary passes | ✅ | `TestCleanSummaryPasses` (3 tests) all PASSED |
| 6 | QA-result gate: `failed > known_failures` fails | ✅ | `TestFailedExceedsKnownFailures` (2 tests) PASSED |
| 7 | QA-result gate: `failed == known_failures` passes | ✅ | `test_exact_match_passes` PASSED |
| 8 | QA-result gate: no summary line fails-closed (Fork B) | ✅ | `TestNoSummaryLineFailsClosed` (3 tests) PASSED — empty, no-equals, no-tests-ran all fail-close |
| 9 | QA-result gate: `errors` counted (F-Cold2 keystone) | ✅ | `TestErrorFormFailsClosed` (3 tests) PASSED — errors-only, failed+errors, 0-failed-with-errors all caught |
| 10 | QA-result gate: non-QA step no-ops | ✅ | `test_dev_step_skips` PASSED |
| 11 | QA-result gate: malformed `known_failures` fails-closed (F-Cold3) | ✅ | `test_non_int_fails_closed` PASSED |
| 12 | QA-result gate: no .txt deposit fails-closed | ✅ | `test_no_txt_fails_closed` PASSED |
| 13 | Three-site guard: site 1 (non-final) on_failure clean QA no-pause | ✅ | `test_site1_on_failure_clean_qa_no_pause` PASSED |
| 14 | Three-site guard: site 2 (final) on_failure clean QA no-pause | ✅ | `test_site2_on_failure_clean_qa_no_pause` PASSED |
| 15 | Three-site guard: site 3 (auto-close) on_failure clean QA auto-closes | ✅ | `test_site3_on_failure_clean_qa_auto_closes` PASSED |
| 16 | Three-site guard fires ONLY under `on_failure` | ✅ | `test_site1_always_qa_pauses`, `test_site1_after_qa_step_qa_pauses`, `test_site1_qa_and_terminal_qa_pauses` all PASSED — existing modes still pause on QA |
| 17 | Canary dry-run: clean QA auto-continues to Done | ✅ | Sites 1+2 no-pause + site 3 auto-close verified — synthetic clean QA under `on_failure` auto-continues |
| 18 | Canary dry-run: injected regression pauses | ✅ | `test_site1_on_failure_failed_qa_pauses` + `test_site2_on_failure_failed_qa_pauses` PASSED — gate failure forces pause |
| 19 | `effective_auto_close` true under `on_failure` | ✅ | `TestEffectiveAutoClose` (5 tests) all PASSED |
| 20 | `header_says_pause` returns False for `on_failure` | ✅ | `test_on_failure_returns_false` + qa_step + final_step variants all PASSED |
| 21 | `plan_lint`: `on_failure` recognized as valid token | ✅ | `test_on_failure_recognized` PASSED |
| 22 | `plan_lint`: `on_failure` without `qa_steps` is FAIL | ✅ | `test_on_failure_without_qa_steps_fails` PASSED (exit_code == 1) |
| 23 | `plan_lint`: existing `qa_and_terminal` without `qa_steps` stays WARN | ✅ | `test_qa_and_terminal_without_qa_steps_warns_not_fails` PASSED (Q7 compat) |
| 24 | Last summary line used (multiple summaries) | ✅ | `test_multiple_summaries_uses_last` PASSED |
| 25 | Full suite green (1098 passed, 0 failed) | ✅ | `full-suite.txt`: `1098 passed, 1 warning` |

## Rule 20 — QA Self-Check Results

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: /Users/marklehn/Developer/GitHub/bellows/.bellows-worktrees/439/knowledge/qa/evidence/bellows-autocontinue-2026-08-18/
Files verified: 1
```

