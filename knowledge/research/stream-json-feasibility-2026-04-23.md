# Stream-JSON Feasibility — Diagnostic Findings
**Date:** 2026-04-23 | **Diagnostic:** stream-json-feasibility | **Agent:** Bellows Systems Analyst

---

## 1. Executive Summary

Stream-json emits fully structured tool-call and tool-result events as NDJSON lines, making tool names, arguments, outputs, and error status visible in real time — none of which the current single-JSON format exposes. Blast radius for a minimal switch (extract `result` event from NDJSON stream, preserve current gate model) is small: 1 file, ~30 lines changed; blast radius for full per-event gating is moderate: 3 files, week-scale. Scope class: **small for minimal switch, medium for full per-event gating**.

---

## 2. Q1 — What Does Stream-JSON Actually Emit?

**Requirement:** `--verbose` flag is mandatory — `stream-json` without `--verbose` errors with "When using --print, --output-format=stream-json requires --verbose".

### Event Type Table

| # | `type` field | `subtype` | When emitted | Top-level keys | Tool calls visible? | Tool results visible? | Final `result` reconstructible? | Session metadata location |
|---|---|---|---|---|---|---|---|---|
| 1 | `system` | `init` | First event | `cwd`, `session_id`, `tools[]`, `mcp_servers[]`, `model`, `permissionMode`, `slash_commands[]`, `apiKeySource`, `claude_code_version`, `agents[]`, `skills[]`, `plugins[]`, `fast_mode_state` | N/A | N/A | N/A | `session_id` present |
| 2 | `assistant` | — | Each model turn | `message{model, id, type, role, content[], stop_reason, usage{input_tokens, cache_*, output_tokens}, context_management}`, `parent_tool_use_id`, `session_id` | **Yes** — `content[]` contains `{type: "tool_use", id, name, input{...}, caller{type}}` with full tool name and structured arguments | No (appears in `user` event) | Yes — last `assistant` event's text content matches `result` field in terminal event | `session_id` in every event; cost per-turn in `usage` |
| 3 | `user` | — | After each tool execution | `message{role: "user", content[{tool_use_id, type: "tool_result", content, is_error}]}`, `tool_use_result{stdout, stderr, interrupted, isImage}` | No (appears in preceding `assistant` event) | **Yes** — full stdout/stderr, error flag, tool_use_id linking back to the call | N/A | `session_id` present |
| 4 | `rate_limit_event` | — | After each API call | `rate_limit_info{status, resetsAt, rateLimitType, overageStatus, isUsingOverage}` | N/A | N/A | N/A | `session_id` present |
| 5 | `result` | `success` | Terminal event | `is_error`, `duration_ms`, `duration_api_ms`, `num_turns`, `result`, `stop_reason`, `session_id`, `total_cost_usd`, `usage{}`, `modelUsage{}`, `permission_denials[]`, `fast_mode_state` | N/A | N/A | **Yes** — `result` field contains final text | All metadata here: `session_id`, `total_cost_usd`, `stop_reason`, `permission_denials[]` |

### Representative Lines (1 per type, truncated)

**system/init:**
```json
{"type":"system","subtype":"init","cwd":"/Users/marklehn/Desktop/GitHub/bellows","session_id":"89becf87-...","tools":["Task","Bash",...],"model":"claude-opus-4-6[1m]",...}
```

**assistant (tool_use):**
```json
{"type":"assistant","message":{"model":"claude-opus-4-6","content":[{"type":"tool_use","id":"toolu_01RRw9Dg4utDXUg4NS2FRbWx","name":"Bash","input":{"command":"echo hello","description":"Print hello"},"caller":{"type":"direct"}}],...},...}
```

**user (tool_result):**
```json
{"type":"user","message":{"role":"user","content":[{"tool_use_id":"toolu_01RRw9Dg4utDXUg4NS2FRbWx","type":"tool_result","content":"hello","is_error":false}]},"tool_use_result":{"stdout":"hello","stderr":"","interrupted":false},...}
```

**result:**
```json
{"type":"result","subtype":"success","is_error":false,"result":"Done — `hello` printed successfully.","stop_reason":"end_turn","total_cost_usd":0.051086,"permission_denials":[],...}
```

### Three-Sentence Summary

Stream-json makes tool calls structurally visible as they happen: each `assistant` event contains typed `tool_use` content blocks with the tool name (e.g., "Bash", "Write", "Edit") and full input arguments as structured JSON, followed by a `user` event with the tool's stdout/stderr and error flag. The current single-JSON format exposes none of this — Bellows sees only the final `result` text and `permission_denials` array after the entire step completes. Under stream-json, Bellows could observe every file write path, every bash command, and every tool error in real time, enabling per-event gating without post-hoc git diff or text parsing.

---

## 3. Q2 — Blast Radius: runner.py and parser.py

### runner.py

| File:Line | Function/Block | Current Assumption | Change Class | Justification |
|---|---|---|---|---|
| runner.py:35 | `run_step` cmd build | `--output-format` is `json` | (a) MECHANICAL | Swap string literal to `stream-json`, add `--verbose` |
| runner.py:76-89 | `_read_stream` threads + `stdout_buf` | stdout is a single JSON blob accumulated line-by-line | (a) MECHANICAL | NDJSON is also line-delimited; line-by-line reading already works |
| runner.py:78 | `last_output_time` tracking | Updated per-line for inactivity timeout | (a) MECHANICAL | Per-line tracking works identically for NDJSON lines |
| runner.py:132 | `result_stdout = "".join(stdout_buf)` | Concatenation produces a single parseable JSON string | (b) LOGIC | Must change to iterate lines, `json.loads()` each, collect events |
| runner.py:188-189 | `json.loads(result_stdout)` | Entire stdout is one JSON object | (b) LOGIC | Must parse NDJSON line-by-line and extract the `type: "result"` event |
| runner.py:212 | `parse(raw)` | `raw` is the single JSON object from claude -p | (b) LOGIC | Must pass the extracted `result` event dict; `result` event has compatible fields |
| runner.py:234-239 | `_write_log` success path | Logs `raw_output` (single JSON string) and `parsed` | (a) MECHANICAL | Log full NDJSON stream as `raw_output`; `parsed` unchanged |
| runner.py:139-145 | `_write_log` timeout path | Logs `stderr_partial` | (a) MECHANICAL | No change — stderr handling is independent of output format |
| runner.py:165-169 | `_write_log` non-zero exit path | Logs `raw_output` as string | (a) MECHANICAL | NDJSON stream stored as-is |
| runner.py:191-196 | `_write_log` JSON decode error | Catches single `json.JSONDecodeError` | (b) LOGIC | Error handling must account for per-line parse failures vs. missing result event |

### parser.py

| File:Line | Function/Block | Current Assumption | Change Class | Justification |
|---|---|---|---|---|
| parser.py:7 | `parse()` — `session_id` | `raw.get("session_id")` from single JSON | (a) MECHANICAL | `result` event has `session_id` at top level — same key |
| parser.py:8 | `parse()` — `is_error` | `raw.get("is_error")` | (a) MECHANICAL | `result` event has `is_error` at top level — same key |
| parser.py:9 | `parse()` — `stop_reason` | `raw.get("stop_reason")` | (a) MECHANICAL | `result` event has `stop_reason` — same key |
| parser.py:10 | `parse()` — `result_text` | `raw.get("result", "")` | (a) MECHANICAL | `result` event has `result` — same key |
| parser.py:11 | `parse()` — `cost_usd` | `raw.get("total_cost_usd")` | (a) MECHANICAL | `result` event has `total_cost_usd` — same key |
| parser.py:12 | `parse()` — `permission_denials` | `raw.get("permission_denials", [])` | (a) MECHANICAL | `result` event has `permission_denials` — same key |
| parser.py:29-36 | `parse()` — ceo_flags regex | Scans `result_text` for `### Flags for CEO` | (a) MECHANICAL | `result_text` is identical — same text, same regex |
| parser.py:39-42 | `parse()` — VERDICT_REQUESTED regex | Scans `result_text` for `VERDICT_REQUESTED:` marker | (a) MECHANICAL | `result_text` is identical |
| parser.py:60-65 | `is_clean()` | Checks `escalate`, `stop_reason`, `receipt_status` | (a) MECHANICAL | All fields preserved in parsed dict |

### Summary

The `result` event in stream-json contains **all the same top-level fields** that the current single-JSON output provides (`session_id`, `is_error`, `stop_reason`, `result`, `total_cost_usd`, `permission_denials`). This means `parser.py` requires **zero logic changes** — only `runner.py` needs to change its stdout parsing from single-JSON to NDJSON-extract-result. The blast radius is concentrated in one function (`run_step`'s success path, ~15 lines of parse logic).

---

## 4. Q3 — Gate Reclassification Under Stream-JSON

| Gate # | Gate Name | Function | Blocking? | Classification | Chain Notes |
|---|---|---|---|---|---|
| 1 | receipt_status | `_gate_receipt_status` | Blocking | **(b) STAYS POST-HOC** | `stop_reason` only in terminal `result` event. No mid-stream signal for completion status. |
| 2 | ceo_flags | `_gate_ceo_flags` | Blocking | **(b) STAYS POST-HOC** | Flags are embedded in agent-authored `result_text`, not structured events. Would require agent-side changes to emit flags as events. |
| 3 | no_errors | `_gate_no_errors` | Blocking | **(b) STAYS POST-HOC** | `is_error` only in terminal `result` event. Tool-level errors visible per-event via `user` event's `is_error` field, but step-level error status is terminal. |
| 4 | no_permission_denials | `_gate_no_permission_denials` | Blocking | **(b) STAYS POST-HOC** | `permission_denials[]` array only in terminal `result` event. **BACKLOG known issue:** Grep-denial false positive — stream-json does NOT fix this since the false positive is about what counts as a denial, not when it's detected. |
| 5 | deposit_exists | `_gate_deposit_exists` | Blocking | **(b) STAYS POST-HOC** | Checks filesystem state (file existence). Inherently end-state even if Write events are observed mid-stream, because agent could delete/overwrite files later. **BACKLOG known issue:** prose-directory false positive — NOT fixed by stream-json (issue is regex matching, not timing). |
| 6 | is_qa_step | `_gate_is_qa_step` | Informational | **(b) STAYS POST-HOC** | Derived from plan text, not agent output. Stream-json irrelevant. |
| 7 | file_change_audit | `_gate_file_change_audit` | Informational | **(a) BECOMES PER-EVENT** | Write/Edit tool_use events in the stream contain file paths as structured arguments. Could track file changes in real time without post-hoc git diff. |
| 8 | scope_check | `_gate_scope_check` | Blocking | **(a) BECOMES PER-EVENT** | If file changes are observed per-event (from Write/Edit tool_use events), scope violations could be detected the moment they occur. Could theoretically kill the subprocess on first out-of-scope write. **BACKLOG known issue:** scope_check git-range false positive — **INCIDENTALLY FIXED** by stream-json since Write/Edit events provide exact file paths, eliminating reliance on git diff range. Depends on Gate 7 per-event tracking. |

### Chain Dependencies

- Gate 8 (scope_check) per-event mode depends on Gate 7 (file_change_audit) being converted to per-event tracking first — they share the `files_changed` data source.
- No gate's reclassification depends on Q2's INVARIANT-class changes (there are none — all Q2 changes are MECHANICAL or LOGIC class).

### Classification (c) — BECOMES UNNECESSARY

No gates qualify as (c). All gates check conditions that remain necessary even under stream-json. The closest candidate is Gate 4 (permission_denials), where stream events could theoretically provide the same signal — but permission denials are not emitted as separate structured events in the stream; they are only aggregated in the terminal `result` event.

---

## 5. Scope Estimate

**Minimal switch** (stream-json output, extract `result` event, preserve current post-hoc gate model):
- **1 file touched** (runner.py)
- **1 function to modify** (`run_step` success-path parsing, ~15 lines replaced)
- **0 parser.py changes** (result event has identical field schema)
- **0 gates.py changes** (all gates remain post-hoc)
- **1–2 existing tests to update** (any that mock `json.loads` on runner stdout)
- **2–3 new tests to add** (NDJSON parsing, missing result event handling, multi-event stream)
- **Class: day of work**

**Full per-event gating** (minimal switch + real-time gate evaluation during stream):
- **3 files touched** (runner.py, gates.py, parser.py or new stream_parser.py)
- **3–4 functions to rewrite** (`run_step` main loop becomes event-processing loop; `_gate_file_change_audit` and `_gate_scope_check` need per-event variants; `check()` needs incremental call path)
- **4–6 existing tests to update**
- **8–12 new tests to add** (per-event gate triggers, scope kill scenarios, partial stream handling, error mid-stream)
- **Class: week of work**

**Riskiest unknown:** Whether permission denial events, context management events, and error-during-tool-execution events appear as distinct mid-stream events or are only aggregated in the terminal `result` — the two test runs exercised only the happy path and cannot confirm the failure-path event vocabulary.

---

## 6. Follow-Up Questions

1. **Permission denial event shape.** A test that deliberately triggers a permission denial under stream-json would confirm whether denials appear as mid-stream events (enabling per-event Gate 4) or only in the terminal `permission_denials[]` array. This would determine whether Gate 4 can ever become per-event.
2. **Error/crash event shape.** What does the stream emit when claude -p crashes mid-execution or hits max_tokens? Is there a `result` event with `subtype: "error"`, or does the stream simply terminate? This affects the robustness of the NDJSON parser's "find result event" logic.
3. **`--verbose` flag interaction with `--resume`.** Bellows uses `--resume` for session continuity. Confirm that `--output-format stream-json --verbose --resume <id>` works correctly — the `--verbose` requirement is a new constraint.

---

## Output Receipt
**Agent:** Bellows Systems Analyst
**Step:** 1 (single-step diagnostic)
**Status:** Complete

### What Was Done
Investigated stream-json output format via two live `claude -p` invocations (trivial prompt and tool-use prompt). Catalogued 5 event types with full structural analysis. Classified every assumption site in runner.py (10 sites) and parser.py (9 sites) by change class. Classified all 8 gates by per-event/post-hoc/unnecessary taxonomy.

### Files Deposited
- `bellows/knowledge/research/stream-json-feasibility-2026-04-23.md` — full diagnostic findings with event catalog, blast radius table, gate reclassification, and scope estimate

### Files Created or Modified (Code)
- None (investigation only)

### Decisions Made
- Classified blast radius as MECHANICAL/LOGIC only (no INVARIANT-class changes) — the `result` event schema is field-compatible with current single-JSON output
- Classified 6 of 8 gates as STAYS POST-HOC and 2 as BECOMES PER-EVENT
- Identified scope_check git-range BACKLOG issue as incidentally fixable by stream-json

### Flags for CEO
- None

### Flags for Next Step
- None (single-step diagnostic — Planner verifies and handles housekeeping)
