# QA Report — Runner Retry on Transient Failure

**Date:** 2026-05-13
**Plan:** executable-runner-retry-transient-failure-2026-05-13
**Step:** 2 (BELLOWS_QA)

**DAEMON RESTART REQUIRED.** The retry logic is committed but not loaded. CEO must restart Bellows after Done/ move for the fix to be live.

---

## Deliverable Verification (Rule 17)

| Deliverable | Expected | Status | Evidence |
|---|---|---|---|
| `transient_patterns` in runner.py | 1 match (patterns list) | ✅ | Lines 173, 175 — list defined and used in `next()` comprehension |
| `_retry_attempted` in runner.py | >=2 matches (signature + check + call) | ✅ | Line 38 (signature kwarg), line 176 (guard check), line 180 (recursive call with `=True`) — 3 matches |
| `retry dispatch starting` log line | 1 match | ✅ | Line 179 — `_log("INFO", f"runner: retry dispatch starting (step {step_num})")` |
| `time.sleep(5)` retry sleep | 1 match (distinct from poll-loop `time.sleep(1)`) | ✅ | Line 178 — inside retry guard block, distinct from line 110 poll-loop sleep |
| `test_run_step_retries_on_transient_401` in test file | 1 match | ✅ | tests/test_runner.py line 271 |
| `test_run_step_does_not_retry_on_non_transient_error` in test file | 1 match | ✅ | tests/test_runner.py line 285 |
| Dev log file exists | Present at declared path | ✅ | `knowledge/development/runner-retry-transient-failure-2026-05-13.md` exists |
| Dev log contains commit SHA | SHA cited in body text | ✅ | Line 37: `36693a5` — verified against `git log` |

---

## Test Re-Run (Independent Confirmation)

```
17 passed, 1 warning in 0.12s
```

Both new tests passed on fresh re-run:
- `test_run_step_retries_on_transient_401` PASSED
- `test_run_step_does_not_retry_on_non_transient_error` PASSED

Full output saved to `evidence/executable-runner-retry-transient-failure-2026-05-13/test-runner-rerun.txt`.

---

## Full Suite Test Run

```
308 passed, 1 failed in 5.68s
```

The sole failure is the pre-existing `test_run_step_timeout` in `tests/test_runner_parser.py` (documented in PROJECT_STATUS history since 2026-05-09). No new regressions.

Full output saved to `evidence/executable-runner-retry-transient-failure-2026-05-13/full-suite.txt`.

---

## Rule 20 Self-Check

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: /Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/evidence/executable-runner-retry-transient-failure-2026-05-13/
Files verified: 2
```

---

## Output Receipt

**Agent:** Bellows QA Analyst
**Step:** 2
**Status:** Complete

### What Was Done
Verified all deliverables from DEV Step 1. Re-ran targeted tests (17/17 passed) and full suite (308 passed, 1 pre-existing failure). All 8 verification checks passed. Daemon restart required for retry logic to take effect.

### Files Deposited
- `knowledge/qa/runner-retry-transient-failure-qa-2026-05-13.md` — this QA report
- `knowledge/qa/evidence/executable-runner-retry-transient-failure-2026-05-13/` — test evidence directory

### Flags for CEO
- Daemon restart required after Done/ move for retry logic to take effect
