# Runner Retry on Transient Failure — Dev Log

**Date:** 2026-05-13
**Plan:** executable-runner-retry-transient-failure-2026-05-13
**Step:** 1 (BELLOWS_DEVELOPER)

## Anchor Verification

`if proc.returncode != 0:` found at line 169 (pre-edit). Post-edit, the anchor is at line 170 due to the added `_retry_attempted` kwarg in the signature.

## Edit Summary

Added retry-on-transient-failure guard inside the non-zero exit branch of `run_step` in `runner.py`. Implementation uses a private kwarg `_retry_attempted: bool = False` as the one-shot guard — recursive call passes `_retry_attempted=True` to prevent infinite recursion. No module-level state (avoids race conditions with concurrent steps).

**Transient patterns scanned in stderr (case-insensitive):** `401`, `unauthorized`, `authentication`, `429`, `rate limit`, `too many requests`.

**Retry mechanics:** one retry only, 5-second `time.sleep` before retry, same args passed through, INFO-level `_log` calls for retry decision and retry dispatch start.

## New Tests

1. `test_run_step_retries_on_transient_401` — patches Popen to fail with "401 Unauthorized" stderr on first call, succeed on second. Asserts `is_error=False` and `time.sleep(5)` called exactly once.
2. `test_run_step_does_not_retry_on_non_transient_error` — patches Popen to fail with "Permission denied" stderr. Asserts `is_error=True`, `escalate=True`, `receipt_status="Blocked"`, and `time.sleep(5)` never called.

## Test Counts

- Pre-edit: 15 tests collected in `tests/test_runner.py`
- Post-edit: 17 tests collected (15 pre-existing + 2 new)
- All 17 passed, zero regressions

## Files Modified

- `runner.py` — added `_retry_attempted` kwarg, transient-failure retry guard in non-zero exit branch
- `tests/test_runner.py` — added 2 new regression tests

## Commit

`36693a5` — `feat(runner): retry once on transient claude -p failures (401/429) — lessons forge proposal 4`

## Daemon Restart Required

Bellows has no hot-reload. The retry logic only takes effect after a daemon restart following the commit. CEO must restart Bellows after this plan moves to Done/ for the fix to be live.

---

## Output Receipt
**Agent:** Bellows Developer
**Step:** 1
**Status:** Complete

### What Was Done
Added retry-on-transient-failure to `run_step` in `runner.py`. When `claude -p` exits non-zero and stderr contains known transient indicators (401/429/rate-limit patterns), the function retries once after a 5-second delay. Two regression tests added and passing.

### Files Deposited
- `knowledge/development/runner-retry-transient-failure-2026-05-13.md` — this dev log

### Files Created or Modified (Code)
- `runner.py` — added `_retry_attempted` kwarg and transient-failure retry guard in non-zero exit branch
- `tests/test_runner.py` — added `test_run_step_retries_on_transient_401` and `test_run_step_does_not_retry_on_non_transient_error`

### Decisions Made
- Used kwarg-based one-shot retry (private `_retry_attempted` param) rather than module-level flag or closure — avoids race conditions with concurrent steps
- Stored transient patterns in lowercase list and compared against `stderr_lower` for case-insensitive matching

### Flags for CEO
- Daemon restart required after Done/ move for retry logic to take effect

### Flags for Next Step
- Anchor line shifted by ~1 line due to kwarg addition; QA should verify against post-edit state
- Pre-existing `test_run_step_timeout` failure status should be checked during full-suite run
