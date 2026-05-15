# Development Log — Bellows Phase 4 Reliability Fixes
**Date:** 2026-04-15 | **Plan:** executable-bellows-phase4-reliability-fixes-2026-04-15.md | **Step:** 1 (DEV)

## Changes

### Fix 2c — Planner consultation logging (`bellows.py`)

Added 1 line after `planner.consult()` returns in `run_plan()`:
```python
print(f"Bellows: Planner decision for {plan_name} step {current_step}: {decision} — {reason}")
```
This makes every planner consultation visible in the Bellows terminal output. Previously, planner decisions were silent — if the planner escalated due to a transient auth failure, there was no terminal output indicating what happened.

### Fix 1 — Parser stop_reason inference (`parser.py`)

Replaced the text-scan loop at lines 14-19 with stop_reason-based inference:
```python
if is_error:
    receipt_status = "Blocked"
elif stop_reason == "end_turn":
    receipt_status = "Complete"
elif stop_reason == "max_tokens":
    receipt_status = "Partial"
else:
    receipt_status = "Unknown"
```

**Rationale (Phase 2 Q5, Phase 3 Q1):** The old parser searched `result_text` for `**Status:** Complete`, but 28/30 production logs never contained this string in the agent's conversational output — the Output Receipt was only written to deposited files. `stop_reason` is set by the `claude -p` runtime and is reliably `"end_turn"` for all normal completions across 30 inspected log files.

**Test update:** `test_parse_blocked_output` was updated to set `is_error=True` instead of relying on text content. The old test set `**Status:** Blocked` in the result text with `is_error=False` and `stop_reason="end_turn"`, which the new parser correctly identifies as "Complete" (the subprocess completed normally regardless of what the agent wrote).

### Fix 2a — Escalation strand check (`bellows.py`)

Changed the escalation-timeout early `return` to `break`:
```python
# Before (line 195):
return  # ← bypassed strand check

# After:
break   # ← exits while loop, falls through to strand check
```

**Rationale (Phase 2 Q6, Phase 3 Q6):** When the planner escalated and the CEO didn't respond within 1 hour, `run_plan()` returned early, bypassing the strand check at lines 218-223. The plan file stayed as `in-progress-*` with no STRANDED notification — a silent failure. With `break`, the while loop exits and the strand check runs, firing the STRANDED notification and Pushover alert.

### Fix 2b — Planner retry and fallback (`planner.py`)

Rewrote `consult()` with three additions:

1. **Retry on auth failure:** If the `claude -p` subprocess returns a 401 auth error, sleep 5 seconds and retry once. Added `_is_auth_error()` helper.

2. **Fallback to "continue" on transient failures:** If the retry also fails (auth error or invalid JSON stdout), return `decision="continue"` with a descriptive reason instead of `decision="escalate"`. This prevents transient API issues from triggering the 1-hour escalation wait. Genuine planner judgments (valid JSON with "escalate") are still honored. Timeouts still escalate (they may indicate a real problem).

3. **Consultation logging:** Every consultation result (success or failure) is appended to `logs/planner-consultation.jsonl` via `_log_consultation()`. Each entry includes timestamp, model, decision, reason, duration_ms, and error string. Added `BELLOWS_ROOT`, `time`, and `datetime` imports.

**Test update:** `test_consult_bad_json` was updated to expect `decision="continue"` instead of `"escalate"`, matching the new fallback behavior for invalid JSON responses.

## Tests

- **21/21 pass** after updating 2 tests (`test_parse_blocked_output`, `test_consult_bad_json`)
- No new test failures introduced
- Test evidence captured to `knowledge/qa/evidence/executable-bellows-phase4-reliability-fixes-2026-04-15/pytest_targeted.txt`

## Output Receipt

- **Status:** Complete
- **Files Created or Modified (Code):**
  - `parser.py` — replaced text-scan with stop_reason-based status inference
  - `bellows.py` — added planner logging (1 line), changed escalation `return` to `break`
  - `planner.py` — added retry-on-auth, fallback-to-continue, consultation JSONL logging
  - `tests/test_runner_parser.py` — updated `test_parse_blocked_output` for new parser behavior
  - `tests/test_planner.py` — updated `test_consult_bad_json` for new fallback behavior
- **Decisions Made:** Used `break` for Fix 2a (1-word change, minimal diff) instead of a flag variable. Changed planner JSON parse error from "escalate" to "continue" fallback (matching auth failure behavior). Kept timeout as "escalate" since it may indicate a real problem.
- **Flags for CEO:** None — all changes are straightforward, no unexpected interactions.
- **Flags for Next Step:** QA should verify (1) parser returns "Complete" for normal runs, (2) the escalation path now reaches the strand check, (3) planner retry logic handles auth failure correctly, (4) full regression passes.
