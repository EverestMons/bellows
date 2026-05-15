# Notification Coalescing + Dead-Code Cleanup — Dev Log

**Date**: 2026-05-12
**Plan**: `executable-notification-coalescing-2026-05-12`
**Commit**: `07a87ad`

---

## HEAD Refresh Result

Compared HEAD against Plan 1 commit `b11ecc4`. No unexpected drift. `notifier.py` had 4 functions: `push()`, `notify_escalation()` (dead), `notify_complete()` (dead), `notify_failure()`, `notify_verdict_request()`. `bellows.py` had 5 direct `notifier.push()` calls at lines 370, 614, 1009, 1147, 1169. Both `notify_failure` (line 621) and `notify_verdict_request` (lines 478, 566) were called correctly.

---

## Per-Stage Completion Checklist

| Stage | Description | Status |
|-------|-------------|--------|
| 1 | Dead-code deletion (`notify_escalation`, `notify_complete`) | Done |
| 2 | 4 new named functions + update `push()` with priority/sound params | Done |
| 3 | Coalescing buffer + timer thread (`_buffer`, `_enqueue_deferred`, `_flush_buffer`, `_flush_buffer_immediate`) | Done |
| 4 | Config schema — `notifications` block in `config.json` and `config.example.json` + `init_notifications()` call | Done |
| 5 | Migrate 5 direct `notifier.push()` calls in `bellows.py` to named functions | Done |
| 6 | Final wiring — `notify_failure` and `notify_verdict_request` flush buffer before urgent push | Done |

---

## Design Choices

### Python 3.9 compatibility
Used `Optional[X]` from `typing` instead of `X | None` union syntax (PEP 604), since the test environment runs Python 3.9.

### Module-level config initialization
Added `init_notifications(config)` function called once at startup in `__main__`. Named functions read config via module-level `_config`, `_app_key`, `_user_key` set by this init. Defaults to all-enabled with 30s window when `notifications` block is missing (backward compat).

### Coalescing window=0 bypass
When `coalesce_window_seconds` is 0, `_enqueue_deferred()` calls `_flush_buffer()` immediately (no timer), reverting to one-push-per-event for testing or rollback.

### Verdict continue-to-done cost
The `notify_plan_complete(original_name, 0.0)` call at the continue-to-done site passes `total_cost=0.0` because the cost data is not available in the verdict consumption path. The plan notes this is acceptable since the CEO doesn't need to distinguish continue-to-done from regular auto-close in digests.

---

## Verification

### Direct `notifier.push()` calls remaining in `bellows.py`: 0

```
grep -n "notifier.push(" bellows.py → 0 matches
```

### Named function call sites in `bellows.py`

- `notifier.notify_plan_skipped(plan_name)` — line 370 (skip path)
- `notifier.notify_plan_complete(plan_name, total_cost)` — line 614 (auto-close)
- `notifier.notify_queue_empty()` — line 1007 (queue drain)
- `notifier.notify_plan_complete(original_name, 0.0)` — line 1145 (continue-to-done)
- `notifier.notify_plan_halted(original_name)` — line 1167 (stop verdict)
- `notifier.notify_verdict_request(...)` — lines 478, 566 (verdict pause sites)
- `notifier.notify_failure(...)` — line 620 (exception handler)

---

## Test Results

- **Total**: 269 tests
- **Passed**: 268
- **Failed**: 1 (pre-existing: `test_run_step_timeout` — same as Plan 1 baseline)
- **Tests modified**: 3
  - `test_diagnostic_auto_close_moves_to_done`: mock `notifier.notify_plan_complete` instead of `notifier.push`
  - `test_clean_diagnostic_auto_close_true_moves_to_done`: same
  - `test_executable_explicit_auto_close_true_still_closes`: same

---

## Output Receipt

```
Step 1 complete.
Files modified: notifier.py, bellows.py, config.json, config.example.json, tests/test_bellows.py
Commit: 07a87ad
Tests: 268/269 passed (1 pre-existing failure)
Dead-code functions deleted: 2 (notify_escalation, notify_complete)
Named functions added: 4 (notify_plan_complete, notify_plan_halted, notify_plan_skipped, notify_queue_empty)
Direct notifier.push() calls remaining in bellows.py: 0
Coalescing buffer: _buffer + _buffer_lock + _timer + _timer_lock (thread-safe)
Config: notifications block with enabled, 6 event toggles, coalesce_window_seconds (default 30)
```
