# Session-Limit Detection — Runner (Plan 148, Step 1)
**Date:** 2026-07-09 | **Plan:** 148 | **Step:** 1

## Detection Design

Added two helpers to `runner.py`:

### `_check_session_limit(result_event) -> Optional[dict]`
Identifies parkable session-limit events on the stdout result event (NOT stderr). Criteria:
- `is_error == True` AND `api_error_status == 429`
- Result text contains `"session limit"` or `"usage limit"` (case-insensitive substring)
- Safety guard: `num_turns <= 1` AND `total_cost_usd == 0` AND `output_tokens == 0` — step must not have progressed

If all criteria met, returns `{"session_limit": True, "resets_at_epoch": <float>, "resets_at_raw": <str>}`.
If the 429 session-limit has progress indicators (turns/cost/tokens > 0), returns None — the step falls through to the existing Blocked/escalate path (not safe to re-dispatch).

### `_parse_session_reset(result_text) -> float`
Extracts reset wall-clock time + IANA timezone from strings like:
- `"resets 11:50pm (America/Chicago)"`
- `"resets 11pm (America/New_York)"`
- `"resets 3:30am (US/Eastern)"`

Supported formats: `h[:mm]am/pm` with `(Area/City)` zone in parens. Uses `zoneinfo.ZoneInfo` for timezone resolution. Computes the next-future epoch for that wall-clock time in that zone (rolls to tomorrow if the time today has already passed).

**Fallback:** If the time or zone cannot be parsed, returns `now + 5*3600` (conservative 5-hour cap) and logs WARN. The step still parks on this fallback — it never crashes or loses the step.

## Transient/Session Split

The transient stderr retry guard (`runner.py:244-254`) and session-limit detection (`runner.py:372+`) are mutually exclusive by construction:
- **Transient retry:** non-zero exit path, greps stderr for `["401", "429", "rate limit", ...]`
- **Session limit:** success path (exit code 0), checks stdout result event fields

Comments added at both sites to prevent future merging.

## Return Shape (Step-1-only safety)

When a parkable session limit is detected, `run_step` returns the normal `parsed` dict augmented with:
- `session_limit=True`
- `resets_at_epoch=<float>`
- `resets_at_raw=<str>`
- `stop_reason="session_limit"`

Existing fallback fields preserved (`is_error=True`, `receipt_status="Blocked"`, `escalate=True`) so behavior without Step 2 is no worse than today — still escalates as Blocked.

## Tests

14 tests in `tests/test_session_limit_park.py`:
- Parser: plan-132 exact string, 11pm form, 3:30am form, 12pm noon, 12am midnight, unparseable fallback (~now+5h + WARN), bad timezone fallback
- Detection: plan-132 event parkable, usage-limit phrasing, transient rate-limit NOT classified, non-429 NOT classified, non-error NOT classified, progress guards (turns/cost/tokens), return dict field assertions

## Full Suite

```
781 passed, 1 warning in 19.61s
```

0 regressions. Commit: `f8d701b`.

### Ledger Updates

#### Prompt Feedback

None.

---
## Output Receipt
**Agent:** Bellows Developer
**Step:** 1
**Status:** Complete

### What Was Done
Added session-limit detection to `runner.py` with `_check_session_limit` and `_parse_session_reset` helpers. The runner now identifies parkable session-limit 429 events on the stdout result event, parses the resets-at wall-clock time with timezone support, and augments the return dict with session_limit fields while preserving existing Blocked/escalate fallback behavior. 14 unit tests cover all detection and parsing paths.

### Files Deposited
- `knowledge/development/session-limit-detection-runner-2026-07-09.md` — this dev log

### Files Created or Modified (Code)
- `runner.py` — added `_parse_session_reset`, `_check_session_limit`, session-limit detection block after parse(), comment at transient retry guard
- `tests/test_session_limit_park.py` — 14 new tests for detection + parsing

### Decisions Made
- Extracted detection into `_check_session_limit` and parsing into `_parse_session_reset` as module-level helpers for testability
- 5-hour fallback on parse failure (conservative cap, matches plan spec)

### Flags for CEO
- None

### Flags for Next Step
- Step 2 should branch on `parsed.get("session_limit")` in `run_plan` before the gate/escalate handling — the new fields are already in the return dict
