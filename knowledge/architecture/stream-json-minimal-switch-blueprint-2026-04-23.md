# Stream-JSON Minimal Switch — Implementation Blueprint
**Date:** 2026-04-23 | **Author:** Bellows Systems Analyst | **Plan:** executable-stream-json-minimal-switch-2026-04-23

---

## 1. Summary

This blueprint specifies the minimal switch from `--output-format json` to `--output-format stream-json --verbose` in runner.py. The change replaces the single-JSON stdout parse with an NDJSON line-by-line parser that extracts the terminal `type: "result"` event, which contains all the same top-level fields (`session_id`, `is_error`, `stop_reason`, `result`, `total_cost_usd`, `permission_denials`) that parser.py already expects. parser.py and gates.py are untouched — the result event schema is field-compatible with the current single-JSON output.

---

## 2. Exact Command-Line Change

**File:** `runner.py` line 35

**Old:**
```python
"--output-format", "json",
```

**New:**
```python
"--output-format", "stream-json",
"--verbose",
```

### `--verbose` is mandatory
The feasibility diagnostic confirms: `stream-json` without `--verbose` errors with *"When using --print, --output-format=stream-json requires --verbose"*. This is a hard requirement from the Claude CLI, not optional.

### `--include-partial-messages` is NOT included
Decision: **Exclude.** Justification:
1. `--include-partial-messages` adds streaming text content events (partial assistant responses at the token level). Bellows only needs the terminal `result` event for the minimal switch.
2. Including it would significantly increase stdout volume (every streamed token becomes an event line) with zero benefit until per-event content analysis is implemented.
3. The NDJSON parser would process many more lines with no gain — unnecessary I/O and CPU cost.
4. This flag can be added later if per-event gating requires partial content visibility.

---

## 3. NDJSON Parse Logic Spec

### Approach: Extract Only the Terminal `type: "result"` Event

**Decision:** Extract only the `result` event, NOT accumulate all events into a list.

**Justification:**
1. Bellows only needs the result event for the minimal switch — no per-event gating in this plan.
2. The full NDJSON stream is preserved verbatim in `raw_output` (Section 4), so no data is lost for future corpus/telemetry work.
3. Accumulating all events would increase memory usage with no benefit until per-event gating is implemented.
4. Simpler logic, fewer failure modes, smaller diff.

### Implementation Spec

Replace the current success path (runner.py lines 188–209) with:

```python
# --- Success path: parse NDJSON stream, extract terminal result event ---
result_event = None
for line in result_stdout.splitlines():
    line = line.strip()
    if not line:
        continue
    try:
        event = json.loads(line)
    except json.JSONDecodeError:
        print(f"[runner] skipping malformed NDJSON line: {line[:200]}", flush=True)
        continue
    if isinstance(event, dict) and event.get("type") == "result":
        result_event = event

if result_event is None:
    _write_log(log_path, {
        "success": False,
        "error": "no_result_event",
        "raw_output": result_stdout[:5000],
        "stderr": result_stderr[:5000],
    })
    return {
        "is_error": True,
        "error": "no_result_event: stream completed without a result event",
        "session_id": None,
        "escalate": True,
        "receipt_status": "Blocked",
        "ceo_flags": ["claude -p stream ended without result event"],
        "cost_usd": None,
        "stop_reason": "error",
        "result_text": "",
        "permission_denials": [],
        "verdict_requested": {"requested": False, "reason": None},
    }

raw = result_event
```

Then continue with the existing `parse(raw)` call (runner.py line 212 onward) — unchanged.

### Edge Case Handling

| Case | How It Reaches Parse Logic | Handling |
|---|---|---|
| **Malformed NDJSON line** | Process exits cleanly but a line isn't valid JSON | `json.JSONDecodeError` caught per-line; line is logged via `print()` and skipped. NOT fatal. Parsing continues to find the result event. |
| **No result event (clean exit)** | Process exits with returncode 0 but stdout contains no event with `type: "result"` | Distinct error path: error type is `no_result_event`, logged as such. Returns Blocked with CEO flag. This is NOT the same as `json_decode_error`. |
| **Result event with `is_error: true`** | Process exits cleanly, result event exists but has `is_error: true` | Handled by existing parser.py logic — `parse()` sets `receipt_status = "Blocked"` when `is_error` is true. No new code needed. |
| **Timeout (process killed)** | Bellows kills the process via `proc.kill()` | Already handled by the `if timed_out:` block (runner.py:137–158) BEFORE the success path. Does not reach NDJSON parse logic. |
| **Crash (non-zero exit)** | Process exits with non-zero return code | Already handled by the `if proc.returncode != 0:` block (runner.py:161–182) BEFORE the success path. Does not reach NDJSON parse logic. |
| **Multiple result events** | Hypothetical edge case — stream contains >1 result event | The `for` loop overwrites `result_event` on each match, so the LAST result event wins. This is the correct behavior (terminal event is always last). |
| **Empty stdout** | Process exits cleanly but produces no output | `result_stdout.splitlines()` yields an empty list, loop body never executes, `result_event` stays `None` → falls into `no_result_event` error path. |

---

## 4. Raw Output Log Spec

**File:** `runner.py` lines 234–239

**Field name:** `raw_output` (unchanged)

**Format:** The full NDJSON stream — all lines joined with newlines, exactly as emitted by claude -p. This is `result_stdout` (which is `"".join(stdout_buf)` — already preserves the complete stream since `_read_stream` reads line-by-line including newline characters).

**No changes needed to the log-writing code.** The existing `_write_log` success path already stores `raw_output: result_stdout`. Under stream-json, `result_stdout` contains the full NDJSON stream instead of a single JSON string. The field name and storage mechanism are identical.

The `parsed` field in the log continues to store the output of `parse(raw)`, which is the parsed result dict. This is also unchanged.

**Verbatim preservation requirement:** `raw_output` MUST NOT be post-processed, filtered, or truncated in the success path. It is the foundation for future corpus/telemetry work. The existing code already meets this requirement — no modification needed.

---

## 5. Resume Compatibility Test Spec

### Why This Test Is Required

Bellows uses `--resume <session_id>` for session continuity across plan steps. The `--verbose` flag is a new constraint added by stream-json. The feasibility diagnostic's follow-up question #3 flagged that `--output-format stream-json --verbose --resume <id>` has not been empirically tested. If resume breaks under stream-json, Bellows cannot execute multi-step plans.

### Test Procedure for DEV

**Step 1 — First call (get session_id):**
```bash
claude -p "Say hello and nothing else." \
  --output-format stream-json \
  --verbose \
  --model claude-sonnet-4-20250514
```
Parse the NDJSON output, find the `type: "result"` event, extract `session_id`.

**Step 2 — Second call (resume with session_id):**
```bash
claude -p "Say goodbye and nothing else." \
  --output-format stream-json \
  --verbose \
  --model claude-sonnet-4-20250514 \
  --resume <session_id_from_step_1>
```
Verify the second call:
- Exits with returncode 0
- Produces a `type: "result"` event in the NDJSON stream
- The result event contains a `session_id` field (may be same or different — both are acceptable)

### Pass/Fail Criteria

- **PASS:** Both calls succeed, both produce result events, second call accepts the `--resume` flag without error.
- **FAIL:** Second call errors, produces no result event, or rejects `--resume` with stream-json flags. **This is a HARD BLOCKER — stop the plan and escalate. Do not ship.**

### Estimated Cost
~$0.05 for both calls combined (trivial prompts, minimal token usage).

---

## 6. Test Enumeration

### Pre-Existing Issue: Mocking Pattern Mismatch

**Critical context for DEV:** All existing tests in `test_runner.py` patch `runner.subprocess.run`, but the current `runner.py` uses `subprocess.Popen` with threading (lines 48–94). This is a pre-existing mismatch from when runner.py was refactored to use Popen for streaming timeout support. DEV must update ALL test mocking to use `subprocess.Popen` (mock the Popen object with stdout/stderr as iterable line sources, mock `proc.poll()`, `proc.returncode`, etc.). This is not stream-json specific but must be done as part of this work since the tests need updating anyway.

### Existing Tests That Will Break Under Stream-JSON

| # | Test Function | Line | Why It Breaks | How to Fix |
|---|---|---|---|---|
| 1 | `test_configurable_timeout_passed_to_subprocess` | 34 | Uses `CLEAN_STDOUT` (single JSON string); patches `subprocess.run` | Update `CLEAN_STDOUT` to NDJSON format (system init line + result line). Update mock to use Popen pattern. Timeout is now inactivity-based (no `kwargs["timeout"]`), so redesign assertion to verify timeout behavior via the inactivity mechanism. |
| 2 | `test_default_timeout_is_600` | 41 | Same as #1 | Same fix as #1. Default timeout is 300 (runner.py line 31), not 600. |
| 3 | `test_timeout_returns_cost_none` | 50 | Patches `subprocess.run` with `TimeoutExpired`; runner uses Popen with inactivity timeout | Update mock to simulate Popen inactivity timeout (mock `proc.poll()` to never return, let `last_output_time` age exceed timeout). Verify `cost_usd is None` in result. |
| 4 | `test_generic_exception_returns_cost_none` | 56 | Patches `subprocess.run` with `OSError` | Update to patch `subprocess.Popen` with `OSError`. Assertion unchanged. |
| 5 | `test_generic_exception_message_contains_actual_error` | 62 | Same as #4 | Update to patch `subprocess.Popen`. Assertions unchanged. |
| 6 | `test_timeout_writes_log_file` | 71 | Patches `subprocess.run` with `TimeoutExpired` | Update to simulate Popen inactivity timeout. Verify log file written with `error: "timeout"`. |
| 7 | `test_success_writes_log_file` | 82 | Uses `CLEAN_STDOUT` (single JSON); patches `subprocess.run` | Update `CLEAN_STDOUT` to NDJSON. Update mock to Popen pattern. |
| 8 | `test_generic_exception_writes_log_file` | 92 | Patches `subprocess.run` with `OSError` | Update to patch `subprocess.Popen`. Assertions unchanged. |
| 9 | `test_stderr_printed_on_success` | 105 | Uses `CLEAN_STDOUT` (single JSON); patches `subprocess.run` | Update `CLEAN_STDOUT` to NDJSON. Update mock to Popen pattern. |
| 10 | `test_json_decode_error_returns_blocked` | 115 | Uses `stdout="NOT JSON"`; error type changes from `json_decode_error` to `no_result_event` | Update mock to Popen pattern. Update assertion: error should contain `no_result_event` instead of `json_decode_error`. |
| 11 | `test_json_decode_error_writes_log_with_raw_output` | 125 | Same as #10; log error field changes | Update mock to Popen pattern. Update assertion: `data["error"]` should be `"no_result_event"` instead of `"json_decode_error"`. Rename test to `test_no_result_event_writes_log_with_raw_output`. |

### CLEAN_STDOUT Constant Update

The module-level `CLEAN_STDOUT` constant (line 12) must change from a single JSON string to NDJSON format:

```python
# NDJSON stream: system init event + result event (one per line)
_SYSTEM_EVENT = json.dumps({
    "type": "system",
    "subtype": "init",
    "session_id": "abc123",
    "tools": [],
    "model": "claude-sonnet-4-20250514",
})

_RESULT_EVENT = json.dumps({
    "type": "result",
    "subtype": "success",
    "is_error": False,
    "result": "Step 1 complete.",
    "stop_reason": "end_turn",
    "session_id": "abc123",
    "total_cost_usd": 0.14,
    "permission_denials": [],
})

CLEAN_NDJSON = _SYSTEM_EVENT + "\n" + _RESULT_EVENT + "\n"
```

### New Tests to Add

| # | Test Function Name | What It Tests |
|---|---|---|
| a | `test_ndjson_parse_valid_stream` | Happy path: NDJSON stream with system init + assistant + user + result events. Verify `result_event` is extracted correctly and `parse()` output matches expected schema. |
| b | `test_ndjson_parse_malformed_line_skipped` | NDJSON stream with one malformed line (not valid JSON) interspersed among valid events. Verify the malformed line is skipped (not fatal), result event is still extracted, and a warning is printed to stdout. |
| c | `test_ndjson_parse_missing_result_event` | NDJSON stream with valid events but NO `type: "result"` event. Verify distinct error path: `error` contains `no_result_event`, `receipt_status` is `Blocked`, `is_error` is `True`. This is NOT the same as `json_decode_error`. |
| d | `test_resume_session_flag_in_command` | Verify that when `session_id` is passed to `run_step()`, the command includes `--resume <session_id>` alongside `--output-format stream-json --verbose`. This is a unit test for command construction, not a live resume test (the live test is in Section 5). |

---

## 7. Acceptance Criteria

DEV must self-check all 8 criteria before declaring Step 2 Complete:

1. `--output-format stream-json --verbose` is passed on every `claude -p` invocation in runner.py (replacing `--output-format json`).
2. `run_step`'s success path extracts the `type: "result"` event from the NDJSON stream and returns a dict with identical schema to the current implementation (same keys, same types).
3. Malformed NDJSON lines are logged (printed to stdout) and skipped, not fatal.
4. Missing result event (process exits cleanly but no `type: "result"` event in stream) produces a distinct error path logged as `no_result_event` — NOT `json_decode_error`.
5. Resume test passes: `session_id` from first `claude -p --output-format stream-json --verbose` call is accepted by second call with `--resume <session_id>`.
6. All existing `test_runner.py` tests updated to use Popen mocking and NDJSON mock data, and passing.
7. New tests (a)–(d) added and passing.
8. Full test suite passes (`pytest tests/ -v` — targeted run + full suite both clean).

---

## 8. Explicit Scope Confirmation

### parser.py — UNTOUCHED
The `result` event in stream-json contains all the same top-level fields that `parse()` expects: `session_id`, `is_error`, `stop_reason`, `result`, `total_cost_usd`, `permission_denials`. The field names and types are identical. `parse()` receives the extracted `result` event dict and processes it with zero code changes.

### gates.py — UNTOUCHED
All 8 gates remain post-hoc under the minimal switch. Gates operate on the output of `parse()`, which is unchanged. Per-event gating is explicitly out of scope for this plan.

### Out of Scope
- No per-event gating design
- No parser.py changes
- No gates.py changes
- No corpus/telemetry layer
- No documentation changes to PLANNER_TEMPLATE or specialist files
- No `--include-partial-messages` flag

---

## Output Receipt
**Agent:** Bellows Systems Analyst
**Step:** 1
**Status:** Complete

### What Was Done
Produced an implementation blueprint for the minimal stream-json switch. Analyzed runner.py's success path parsing, enumerated all 11 existing tests that will break (with fix descriptions), specified 4 new tests, defined the NDJSON parse logic with 7 edge cases, and documented the resume compatibility test procedure.

### Files Deposited
- `bellows/knowledge/architecture/stream-json-minimal-switch-blueprint-2026-04-23.md` — full implementation blueprint for DEV

### Files Created or Modified (Code)
- None (blueprint only)

### Decisions Made
- Extract only the terminal `type: "result"` event (not accumulate all events) — simpler, lower memory, full stream preserved in raw_output
- Exclude `--include-partial-messages` — no benefit for minimal switch, adds noise
- Error type for missing result event is `no_result_event` (distinct from `json_decode_error`)
- Last result event wins if multiple appear (overwrite on each match)
- All 11 existing tests require updating (Popen mocking + NDJSON format), not just the stream-json specific ones

### Flags for CEO
- None

### Flags for Next Step
- ALL existing tests have a pre-existing mocking mismatch (patch `subprocess.run` but code uses `subprocess.Popen`). DEV must fix this as part of the test update — it's not optional.
- The `test_configurable_timeout_passed_to_subprocess` and `test_default_timeout_is_600` tests assert against `kwargs["timeout"]` from `subprocess.run`, but the current runner uses inactivity-based timeout via Popen polling. These tests need conceptual redesign, not just mechanical NDJSON updates.
