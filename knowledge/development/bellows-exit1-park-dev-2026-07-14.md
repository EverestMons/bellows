# Exit-1 rate-limit park detection — dev log

**Plan:** 185
**Diagnostic:** 184
**Date:** 2026-07-14

## Changes

### runner.py

1. **`_reset_epoch_from_rate_limit_event(rate_limit_info, plan_slug)`** — extracts `resetsAt` epoch integer from a `rate_limit_event`'s `rate_limit_info` dict. Falls back to `now + 5h` if missing/invalid.

2. **`_check_exit1_rate_limit(result_stdout, plan_slug)`** — scans NDJSON stream for a `rate_limit_event` with `rateLimitType == "five_hour"`. Computes stream progress metrics (num_turns, total_output_tokens, has_mutating_tool_use). Returns `{session_limit, resets_at_epoch, resets_at_raw}` only when five_hour event found AND zero committable progress (`num_turns <= 1 AND total_output_tokens < 500 AND NOT has_mutating_tool_use`). Returns None otherwise.

3. **Exit-1 block** — after the transient-retry check and before the hardcoded gate_failure return, calls `_check_exit1_rate_limit`. On parkable result, returns a dict with `session_limit=True` and `stop_reason="session_limit"` so `bellows._maybe_park_session_limit` parks it. On None, preserves all existing exit-1 behavior unchanged.

### bellows.py

4. **`_maybe_park_session_limit`** — added optional `plan_baseline_sha` parameter. When provided, compares current worktree HEAD against baseline; if they differ (agent committed work), returns False (does not park). Threaded from both call sites (`pre_diff` variable).

### tests/test_session_limit_park.py

5. **4-case test matrix (diag-184 §6):**
   - (i) exit-1 + five_hour + zero progress → parkable, `resets_at_epoch == 1784053800`
   - (ii) exit-1, no rate_limit_event → not parkable (gate_failure)
   - (iii) exit-1 + five_hour + Write tool_use + output_tokens >= 500 → not parkable
   - (iv) graceful 429 "session limit" (exit 0) → still parkable via existing path (no regression)

   Plus integration tests via `run_step()` with mocked Popen, and backup guard test.

## Hard constraints verified

- Existing `_check_session_limit` path (lines 74-101) unchanged — test (iv) confirms
- No changes to `_resume_parked`, `record_park`, `clear_park`, or `parked_steps` schema
- All 57 tests pass (26 session_limit_park + 31 runner)
