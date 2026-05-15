# QA Report — Notifier Timeout + Heartbeat + Dead Code Cleanup
**Date:** 2026-04-16 | **Plan:** executable-bellows-notifier-timeout-2026-04-16 | **Step:** 2 (QA) | **Status:** PASS

---

## Deliverable Verification

| Check | Expected | Observed | Status |
|---|---|---|---|
| (a) Timeout in notifier.py | `timeout=(5, 10)` in `requests.post` call | `notifier.py:22` — `requests.post(PUSHOVER_API_URL, data=payload, timeout=(5, 10))` | ✅ |
| (b) Heartbeat variable in bellows.py | `last_heartbeat = time.time()` before loop | `bellows.py:573` — `last_heartbeat = time.time()` | ✅ |
| (c) Heartbeat print in bellows.py | `if time.time() - last_heartbeat >= 60: print(...)` | `bellows.py:580-582` — condition + print + reset | ✅ |
| (d) Dead code removed (call site) | `STRANDED Plan` push call absent from `run_plan` | `grep "STRANDED Plan" bellows.py` → 0 matches | ✅ |
| (e) `_is_plan_stranded` function preserved | Function definition still present (used in tests) | `bellows.py:135` — function still exists, only call site removed | ✅ |
| (f) Test: timeout kwarg asserted | `test_push_passes_timeout` passes | PASSED | ✅ |
| (g) Test: Timeout exception handled | `test_push_timeout_exception_handled_gracefully` passes | PASSED | ✅ |
| (h) Test: dead code absent | `test_no_stranded_check_in_run_plan` passes | PASSED | ✅ |

---

## Test Results

### Targeted (12 selected)
```
tests/test_notifier_server.py::test_push_success PASSED
tests/test_notifier_server.py::test_push_passes_timeout PASSED
tests/test_notifier_server.py::test_push_timeout_exception_handled_gracefully PASSED
tests/test_notifier_server.py::test_no_stranded_check_in_run_plan PASSED
tests/test_notifier_server.py::test_push_failure PASSED
tests/test_notifier_server.py::test_server_respond PASSED
tests/test_planner.py::test_consult_timeout PASSED
tests/test_runner.py::test_configurable_timeout_passed_to_subprocess PASSED
tests/test_runner.py::test_default_timeout_is_600 PASSED
tests/test_runner.py::test_timeout_returns_cost_none PASSED
tests/test_runner.py::test_timeout_writes_log_file PASSED
tests/test_runner_parser.py::test_run_step_timeout PASSED
12 passed, 76 deselected
```

### Full Suite
```
88 passed, 1 warning in 0.68s
```

Evidence: `knowledge/qa/evidence/notifier-timeout-fix/`

---

## Summary

All three fixes verified in code and confirmed by passing tests:

1. **Fix 1 (CRITICAL):** `notifier.py:22` — `requests.post` now uses `timeout=(5, 10)`. Eliminates indefinite blocks on stalled Pushover TCP connections. `requests.Timeout` caught by existing `requests.RequestException` handler — no extra error handling needed.
2. **Fix 2:** `bellows.py:573,580-582` — `last_heartbeat` tracker and 60-second heartbeat print added to main loop. Serves as canary: if heartbeat stops, main thread is hung.
3. **Fix 3:** `bellows.py:306-313` (old numbering) removed — stranded-check block was unreachable (logical complement conditions guarantee `return` at line 304 is always reached first). `_is_plan_stranded` function definition retained at line 135 (used by existing tests).

No regressions. 88/88 tests pass.
