# QA Report — Bellows Phase 6: Runner Timeout + Observability
**Date:** 2026-04-16 | **QA Agent:** Claude Code

## Deliverable Verification

| Deliverable | Expected | Status | Evidence |
|---|---|---|---|
| Fix 1: configurable timeout in runner.py | `timeout=` param with default 600 | PASS | `timeout: int = 600` on line 31, `timeout=timeout` on line 48 |
| Fix 1b: step_timeout_seconds in config.example.json | Key present with value 600 | PASS | `"step_timeout_seconds": 600` in config.example.json |
| Fix 2: cost_usd None on error paths | `None` instead of `0.0` in error handlers | PASS | Lines 63, 78, 97, 113: `"cost_usd": None` |
| Fix 3: log writing on all code paths | `_write_log`/`log_path` referenced 4+ times | PASS | 14 references (helper def + 4 call sites + path construction) |
| Fix 4: result.stderr captured | `result.stderr` referenced in runner.py | PASS | Lines 85, 93, 94, 117, 118 |
| Fix 5: JSONDecodeError handled | `JSONDecodeError`/`json_decode_error` present | PASS | Lines 88, 91, 92 (handler + log + return) |

All 6 checks PASS. No blockers.

## Test Results

**Targeted suite:** `tests/test_runner.py` — **11 passed in 0.02s**

Dev log reported 11 tests. Fresh QA re-run confirms 11/11 pass. Test list:
1. test_configurable_timeout_passed_to_subprocess
2. test_default_timeout_is_600
3. test_timeout_returns_cost_none
4. test_generic_exception_returns_cost_none
5. test_generic_exception_message_contains_actual_error
6. test_timeout_writes_log_file
7. test_success_writes_log_file
8. test_generic_exception_writes_log_file
9. test_stderr_printed_on_success
10. test_json_decode_error_returns_blocked
11. test_json_decode_error_writes_log_with_raw_output

## Summary

All five Phase 6 fixes verified in runner.py via grep evidence. Both bellows.py call sites pass the configurable timeout. config.example.json updated. 11/11 targeted tests pass on fresh run matching dev log count. No regressions in existing test_runner_parser.py (3/3 pass, verified in Step 1).

## Output Receipt

- **Status:** Complete
- **Evidence Files:**
  - `grep_deliverables.txt` — 6 deliverable checks, all PASS
  - `pytest_targeted.txt` — 11/11 tests pass
- **Flags for CEO:** None

## Rule 20 Self-Check

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: /Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/evidence/executable-bellows-phase6-runner-observability-2026-04-16/
Files verified: 2
```
