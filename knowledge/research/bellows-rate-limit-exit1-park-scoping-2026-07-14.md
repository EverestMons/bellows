# Bellows rate-limit exit-1 no-park — scoping for fix

**Date:** 2026-07-14
**Diagnostic:** 184
**Status:** scoping complete — ready for executable

---

## Target 1: Data availability at the park-decision point

**Answer: the stream data IS available in-process. No additional capture is needed.**

### Data flow map

1. `runner.run_step()` spawns `claude -p` via `subprocess.Popen` with `stdout=PIPE, stderr=PIPE` (runner.py:132-138).
2. Two reader threads (`_read_stream`) drain stdout/stderr into `stdout_buf` / `stderr_buf` lists (runner.py:165-173).
3. After the process exits, threads join and the full output is assembled: `result_stdout = "".join(stdout_buf)` (runner.py:216).
4. **On exit-1 (runner.py:246-278):** `result_stdout` holds the complete NDJSON stream. The log file persists `raw_output: result_stdout[:5000]` (truncated), but the in-process variable has the full untruncated content.
5. The NDJSON parsing loop (runner.py:286-305) and session-limit check via `_check_session_limit(raw)` (runner.py:374) are in the **success path only** — they execute after the `proc.returncode == 0` gate at line 246. The exit-1 path returns immediately without parsing the stream.

### Verification from incident data

Both 2026-07-14 incident logs (`20260714-125117-step.json` for plan 181, `20260714-125608-step.json` for plan 182) show `raw_output` truncated to exactly 5000 chars. The full in-process `result_stdout` was longer, confirming the stream data survives to the exit-1 code path but is never parsed.

**The fix can scan `result_stdout` directly within the exit-1 block (runner.py:246-278). No plumbing changes are needed to make stream data available.**

---

## Target 2: The exit-1 code path

### Where it lives

`runner.py:246-278`. Entered when `proc.returncode != 0` after the timeout checks pass.

### What it does today

1. **Transient-retry check (lines 249-256):** Scans `result_stderr` for patterns like `"401"`, `"429"`, `"rate limit"`. If found and no prior retry, sleeps 5s and re-dispatches. This is stderr-only — it catches transport-level 429s but NOT the stdout `rate_limit_event` that signals the 5-hour org cap.
2. **Log write (lines 258-265):** Writes `{success: false, error: "non_zero_exit_1", raw_output: result_stdout[:5000], stderr: result_stderr[:5000]}`.
3. **Return (lines 266-278):** Returns a hardcoded dict:
   - `is_error: True`
   - `error: "claude -p exited with code {returncode}"`
   - `session_id: None`, `cost_usd: None`
   - `receipt_status: "Blocked"`, `ceo_flags: ["claude -p exit code {returncode}"]`
   - `result_text: ""`, `stop_reason: "error"`

### Why parking fails

The returned dict never sets `session_limit`. In `bellows.py`, `_maybe_park_session_limit(parsed, ...)` checks `parsed.get("session_limit")` → always `False` on exit-1 → falls through to gate checking → `gate_failure` → CEO must manually park.

### Is a `rate_limit_event` RELIABLY present before exit-1?

**Evidence from the two 2026-07-14 incidents:**
- Plan 181: `rate_limit_event` with `overageStatus: "rejected"` present as the 2nd NDJSON line, BEFORE the first assistant event.
- Plan 182: `rate_limit_event` with `status: "allowed_warning"`, `utilization: 0.93` present as the 2nd NDJSON line, BEFORE the first assistant event.

The `rate_limit_event` is emitted by Claude Code early in the session — it's a status report, not a response to a specific API call. Both incidents had the event positioned immediately after the `system/init` event.

**Important context:** `rate_limit_event` with `overageStatus: "rejected"` ALSO appears in **success-path** logs (e.g., `20260714-134708-step.json`, `20260714-150846-step.json`). The event reports rate-limit status but does not guarantee the process will crash. A `rate_limit_event` alone is not diagnostic — it must be combined with exit-1 to indicate a cap-caused death.

**Residual risk:** If a 5-hour-cap death occurs before ANY NDJSON is emitted (e.g., the process crashes before writing the init event), no `rate_limit_event` will be in the stream. In this case, the step falls through to `gate_failure` — the existing safe fallback. This is acceptable: `gate_failure` surfaces to the CEO, who can manually park or retry. The auto-park path is a performance optimization, not a correctness requirement.

---

## Target 3: `resetsAt` extraction

### Field shape (confirmed from incident logs)

```json
{
  "type": "rate_limit_event",
  "rate_limit_info": {
    "status": "allowed" | "allowed_warning",
    "resetsAt": 1784053800,
    "rateLimitType": "five_hour",
    "overageStatus": "rejected",
    "overageDisabledReason": "org_level_disabled",
    "isUsingOverage": false,
    "utilization": 0.93,
    "surpassedThreshold": 0.9
  },
  "session_id": "..."
}
```

- **Field name:** `resetsAt` (camelCase), nested under `rate_limit_info`
- **Type:** integer (Unix epoch seconds)
- **Always present:** yes, in both the `rejected` and `allowed_warning` variants

### Recommended helper: `_reset_epoch_from_rate_limit_event(event_info: dict) -> float`

```python
def _reset_epoch_from_rate_limit_event(rate_limit_info: dict, plan_slug: str = None) -> float:
    """Extract reset epoch from a rate_limit_event's rate_limit_info dict.

    Returns the resetsAt epoch directly (integer, simpler than wall-clock parsing).
    Falls back to now + 5h if resetsAt is missing or non-numeric.
    """
    resets_at = rate_limit_info.get("resetsAt")
    if isinstance(resets_at, (int, float)) and resets_at > 0:
        return float(resets_at)
    _log("WARN", f"runner: rate_limit_event missing/invalid resetsAt, using 5h fallback",
         slug=plan_slug)
    return time.time() + 5 * 3600
```

This is much simpler than `_parse_session_reset()`, which regex-parses a wall-clock string with timezone. The epoch integer requires no parsing.

---

## Target 4: Park hook + false-positive guard

### Detection logic

**Location:** Inside the exit-1 block in `runner.py:246-278`, AFTER the transient-retry check but BEFORE the return statement.

**Scan algorithm:**
1. Parse each line of `result_stdout` as JSON.
2. Find events where `event["type"] == "rate_limit_event"`.
3. Check `event["rate_limit_info"]["rateLimitType"] == "five_hour"`.
4. If found, extract `resets_at_epoch` via `_reset_epoch_from_rate_limit_event()`.

**Cap-hit status detection:** Any `five_hour` rate_limit_event in an exit-1 stream is treated as cap-caused. Rationale: the event appears in success-path runs too (benignly), so the event alone is not diagnostic — but combined with exit-1, it's the only explanation. No need to distinguish `overageStatus: "rejected"` from `status: "allowed_warning"` — both indicate the cap is active and the exit-1 is cap-related.

### Guard (a): No committable progress

**Stream-level progress check (runner.py):** Scan the stream for progress indicators. Count:
- `num_turns`: number of distinct request-response cycles (count `user` events with `tool_result` content — each one represents a completed turn)
- `total_output_tokens`: sum of `usage.output_tokens` across all `assistant` events
- `has_mutating_tool_use`: whether any `tool_use` block has `name` in `{"Write", "Edit", "Bash", "NotebookEdit"}` (Read-only tool_use is not progress)

**Parkable when:** `num_turns <= 1 AND total_output_tokens < 500 AND NOT has_mutating_tool_use`.

**Rationale for thresholds vs. the existing `> 0` guard:**
The existing 429 guard uses `output_tokens > 0` because the result event's output_tokens is a session aggregate — 0 means literally no response. In the exit-1 stream, every session produces SOME output tokens (the initial assistant response). Both 2026-07-14 incidents had output_tokens of 4 and 110 respectively — both were zero-progress sessions that just read the plan file. The 500-token threshold catches this while still blocking parking for sessions with real work (which typically produce 1000+ tokens across multiple turns).

**Bellows-level backup guard:** In `_maybe_park_session_limit` (bellows.py), add a worktree commit check as a secondary guard. If `_capture_git_diff(wt_path)` differs from `plan_baseline_sha`, the agent committed work → NOT parkable, even if the stream metrics say otherwise. This requires passing `plan_baseline_sha` into `_maybe_park_session_limit` (new parameter).

### Guard (b): Rate-limit event must be present

**Already enforced by the detection logic:** the park path ONLY activates when a `rate_limit_event` with `rateLimitType == "five_hour"` is found in the stream. If no such event exists, the exit-1 is a genuine crash (e.g., OOM, segfault, auth failure) and must NOT be parked — parking it would strand the plan waiting for a reset that resolves nothing. The step falls through to the existing `gate_failure` path.

---

## Target 5: Idempotency + resume correctness

### `record_park` row shape

`record_park(db_path, plan_slug, plan_path, project, resume_step, resets_at_epoch)` writes to `parked_steps`:

| Column | Type | Source for exit-1 path |
|---|---|---|
| plan_slug | TEXT (PK) | Already available in `run_plan` scope |
| plan_path | TEXT | `parked_path` (after rename) |
| project | TEXT | `project_path` |
| resume_step | INTEGER | `current_step` |
| resets_at_epoch | REAL | From `_reset_epoch_from_rate_limit_event()` |
| parked_at | TEXT | `datetime.now().isoformat()` |

The new exit-1 park path writes the identical row shape. No schema changes needed.

### Resume flow verification

`_resume_parked` (bellows.py:1888-1924):
1. Queries `parked_steps WHERE resets_at_epoch <= now`.
2. Renames `parked-{name}` → `in-progress-{name}`.
3. Clears DB row via `clear_park`.
4. Dispatches via `handle_new_plan(inprogress_path, resume_step=N)`.

`run_plan` with `resume_step=N`:
- Skips mint-and-claim (file already named `in-progress-*`).
- Recovers `plan_id` from filename via `recover_plan_id_from_filename()`.
- Creates a fresh worktree — prior DEV commits are on main (landed during the original dispatch's worktree teardown, or preserved if teardown was skipped for exit-1 park).
- Bootstrap prompt: `"Execute Step {N}..."`.

**Exit-1 park teardown subtlety:** On exit-1 park, `_maybe_park_session_limit` calls `_teardown_worktree(project_path, wt_path, ...)`. Since the agent made no progress (guard a), the worktree has no new commits → teardown is a no-op merge. This is safe. The comment in `_maybe_park_session_limit` says "step made no progress — safe no-op merge."

**Manual verification:** 2026-07-14 plan 181 was manually parked + resumed. After manual `parked_steps` DB insert, `_resume_parked` correctly re-dispatched step 2 with prior step-1 commits on main. Confirmed working.

---

## Target 6: Test strategy

### Synthetic step result matrix

| # | Scenario | Stream content | Expected | Validates |
|---|---|---|---|---|
| (i) | exit-1 + five_hour/rejected event + zero progress | `rate_limit_event` with `rateLimitType: "five_hour"`, no Write/Edit/Bash tool_use, output_tokens < 500 | **Parkable** — `session_limit: True`, correct `resets_at_epoch` from `resetsAt` field | Detection + resetsAt extraction + progress guard passes |
| (ii) | exit-1, NO rate_limit_event | Standard NDJSON with system/assistant events but no `rate_limit_event` line | **NOT parkable** — falls through to gate_failure | Guard (b): no event → no park |
| (iii) | exit-1 + five_hour rate_limit_event + WITH progress | `rate_limit_event` present + Write tool_use blocks + output_tokens > 500 | **NOT parkable** — gate_failure for CEO continue-with-reasoning | Guard (a): has progress → no park |
| (iv) | Graceful 429 "session limit" result (exit 0) | Standard success-path result event with `is_error: True`, `api_error_status: 429`, "session limit" in result text | **Still parkable** via existing `_check_session_limit` path | No regression to existing park path |

### Test case (i) detail — the primary fix path

```python
# Synthetic stream: init → rate_limit_event → assistant (Read only) → no result event
stream = "\n".join([
    json.dumps({"type": "system", "subtype": "init", "session_id": "test-sess"}),
    json.dumps({"type": "rate_limit_event", "rate_limit_info": {
        "rateLimitType": "five_hour", "resetsAt": 1784053800,
        "overageStatus": "rejected", "status": "allowed"
    }}),
    json.dumps({"type": "assistant", "message": {
        "content": [{"type": "tool_use", "name": "Read", "input": {"file_path": "/tmp/plan.md"}}],
        "usage": {"output_tokens": 4}
    }}),
])
# Process exits with returncode 1 after this stream
# Expected: parsed dict includes session_limit=True, resets_at_epoch=1784053800
```

### Test case (iii) detail — progress blocks parking

```python
# Synthetic stream with a Write tool_use indicating the agent did work
stream = "\n".join([
    json.dumps({"type": "system", "subtype": "init", "session_id": "test-sess"}),
    json.dumps({"type": "rate_limit_event", "rate_limit_info": {
        "rateLimitType": "five_hour", "resetsAt": 1784053800,
        "overageStatus": "rejected"
    }}),
    json.dumps({"type": "assistant", "message": {
        "content": [{"type": "tool_use", "name": "Write", "input": {"file_path": "/tmp/out.md", "content": "findings..."}}],
        "usage": {"output_tokens": 2000}
    }}),
])
# Expected: NOT parkable — has_mutating_tool_use=True and output_tokens >= 500
```

### Implementation notes for tests

- Mock `subprocess.Popen` to return the synthetic stream on stdout and exit with code 1.
- Call `runner.run_step()` directly and assert the returned dict's `session_limit`, `resets_at_epoch`, and `stop_reason` fields.
- For test (iv), verify the existing `_check_session_limit` path still works by passing a result event with `is_error: True`, `api_error_status: 429`.

---

## Summary of recommended fix scope

**Small executable — 3 changes:**

1. **`runner.py` — new helper `_check_exit1_rate_limit(result_stdout)`:** Scans NDJSON lines for `rate_limit_event` with `rateLimitType == "five_hour"`. Returns `{session_limit: True, resets_at_epoch, ...}` or `None`. Includes the stream-level progress guard (output_tokens, mutating tool_use, turn count).

2. **`runner.py` — exit-1 block (line 246-278):** After the transient-retry check, call `_check_exit1_rate_limit(result_stdout)`. If it returns a parkable result, merge the session_limit fields into the return dict instead of the hardcoded gate_failure return.

3. **`bellows.py` — `_maybe_park_session_limit` (optional backup):** Add a worktree commit check as a secondary progress guard. Pass `plan_baseline_sha` as a new parameter; compare against current worktree HEAD. If they differ, the agent committed → don't park.

No changes needed to: `_resume_parked`, `record_park`, `clear_park`, or the `parked_steps` DB schema.
