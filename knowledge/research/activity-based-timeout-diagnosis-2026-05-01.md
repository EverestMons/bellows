# Activity-Based Timeout Diagnostic — Findings

**Date:** 2026-05-01
**Plan:** diagnostic-activity-based-timeout-2026-05-01
**Analyst:** Bellows Systems Analyst (SA)

---

## Q1 — Current runner.py Timeout Mechanism

### Critical finding: the inactivity-based timeout is ALREADY IMPLEMENTED

The backlog entry (`2026-04-17: activity-based timeout`) describes runner.py as having "a fixed 1200s timeout." This is **no longer true**. The current `runner.py` already implements a fully inactivity-based design with a hard wall-clock safety cap. The backlog entry is stale.

### (a) Function signature and call surface

```python
def run_step(
    prompt: str,
    project_path: str,
    model: str,
    session_id: Optional[str] = None,
    allowed_tools: str = "Read,Edit,Write,Bash",
    timeout: int = 300,
) -> dict:
```

`bellows.py` calls `run_step()` at two sites (lines 297-299 and 353-357), passing:
- `timeout=config.get("step_inactivity_timeout_seconds", config.get("step_timeout_seconds", 300))`
- Current `config.json` has `step_timeout_seconds: 2400` (no `step_inactivity_timeout_seconds` key).
- **Effective inactivity timeout: 2400s (40 minutes). Effective wall-clock cap: 24,000s (~6.7 hours).**

Return dict shape is consistent across all paths: `{is_error, error, session_id, escalate, receipt_status, ceo_flags, cost_usd, stop_reason, result_text, permission_denials, verdict_requested}`.

### (b) Subprocess invocation pattern

`subprocess.Popen` (line 49) with two daemon `threading.Thread` reader threads for stdout and stderr (lines 82-95). Not `subprocess.run` or `communicate(timeout=)`.

### (c) Inactivity timeout enforcement

- **`last_output_time`** initialized at `time.monotonic()` (line 79).
- **`_read_stream()`** (lines 82-90): reads stdout/stderr line-by-line; updates `last_output_time` under a `threading.Lock` on every line received.
- **Polling loop** (lines 101-127): sleeps 1s per iteration. Checks `age = now - last_output_time` (line 107). If `age >= timeout`, kills the process (lines 115-119). Separate `elapsed >= max_wall_clock` check kills on wall-clock cap (lines 122-127).
- Variable names: `last_output_time` (line 79), `timeout` (parameter), `max_wall_clock` (line 46, `= timeout * 10`), `timed_out` (line 98), `wall_clock_hit` (line 99).
- On timeout, `proc.kill()` is called. Threads are joined with 5s timeout (lines 130-131).

### (d) State captured/lost on timeout

- **Captured:** `timeout_type` ("inactivity" or "wall_clock_cap"), `elapsed_seconds`, `stderr_partial` (first 5000 chars). Written to log via `_write_log()`.
- **Lost:** `cost_usd` set to `None`. `session_id` set to `None`. `result_text` is empty string. No parsed output.
- Return dict on timeout: `{is_error: True, error: "timeout", stop_reason: "timeout", escalate: True, receipt_status: "Blocked"}`.

### (e) Stdout reading: line-by-line (NDJSON-aware)

Yes. `_read_stream()` iterates `for line in stream:` (line 85), reading stdout line-by-line. Each NDJSON event is one line, so the inactivity timer resets on every event emitted by `claude -p`.

### (f) Existing inactivity awareness in runner.py

**Fully present.** `last_output_time` (line 79) is the rolling inactivity timer. The 60s heartbeat is in the polling loop (lines 110-111), printing elapsed time and last-output age. This is a runner.py feature, not a bellows.py feature.

---

## Q2 — Empirical Event-Cadence Analysis

### Method

Sampled the 20 largest (by file size) post-stream-JSON log files (`>= 20260423`) where `is_error=false` and `stop_reason=end_turn`. Duration sourced from `result.duration_ms`. Inter-event timestamps are only available on `user`-type events (tool-use results); assistant/system events lack timestamps, so measured gaps are **tool-result-to-tool-result** intervals that OVERESTIMATE true NDJSON silence (assistant events interleave within measured gaps and would reset the runner's inactivity timer).

### Summary Table

| log_filename | total_events | duration_estimate | max_inter_event_gap_s | rate_limit_event_count | rate_limit_max_pause_s | notes |
|---|---|---|---|---|---|---|
| 20260424-112023-step.json | 93 | 216s (3.6m) | 34.7s | 1 | n/a | largest log |
| 20260430-140957-step.json | 103 | 440s (7.3m) | 119.5s | 2 | 24.9s | |
| 20260428-223040-step.json | 99 | 334s (5.6m) | 99.5s | 2 | 26.2s | |
| 20260428-212308-step.json | 69 | 171s (2.8m) | 27.4s | 2 | 4.6s | |
| 20260424-221718-step.json | 172 | 255s (4.2m) | 92.7s | 1 | n/a | most events |
| 20260430-161231-step.json | 109 | 239s (4.0m) | 27.4s | 2 | 14.5s | |
| 20260430-154720-step.json | 66 | 163s (2.7m) | 26.0s | 1 | 0.5s | |
| 20260430-154422-step.json | 47 | 121s (2.0m) | 25.0s | 2 | 5.4s | |
| 20260424-102559-step.json | 73 | 378s (6.3m) | 137.3s | 1 | 10.5s | |
| 20260424-104158-step.json | 62 | 131s (2.2m) | 15.0s | 3 | 15.0s | 3 rate limits |
| 20260501-101808-step.json | 99 | 283s (4.7m) | 30.6s | 1 | 10.0s | |
| 20260501-094651-step.json | 81 | 246s (4.1m) | 96.3s | 1 | 8.4s | |
| 20260430-145615-step.json | 69 | 743s (12.4m) | 283.2s | 2 | 21.5s | longest run |
| 20260428-191956-step.json | 86 | 334s (5.6m) | 103.5s | 2 | 5.1s | |
| 20260424-082650-step.json | 100 | 506s (8.4m) | 133.3s | 2 | 7.9s | |
| 20260428-193440-step.json | 162 | 229s (3.8m) | 24.0s | 2 | 8.2s | |
| 20260430-154448-step.json | 60 | 150s (2.5m) | 34.1s | 2 | 8.7s | |
| 20260430-131629-step.json | 67 | 185s (3.1m) | 23.1s | 1 | 11.4s | |
| 20260501-100714-step.json | 46 | 253s (4.2m) | 139.0s | 1 | 2.4s | |
| 20260501-104929-step.json | 52 | 144s (2.4m) | 38.3s | 1 | 13.4s | |

### Inter-Event Gap Histogram (user-event timestamps, all 20 logs, N=587)

```
    0-1s: ███████████████████████████ 145 (24.7%)
    1-5s: ████████████████████████████████████████ 208 (35.4%)
   5-10s: ██████████████████████████ 137 (23.3%)
  10-30s: ██████████████ 73 (12.4%)
  30-60s: █ 7 (1.2%)
 60-120s: ██ 12 (2.0%)
   120s+: █ 5 (0.9%)
```

**Percentiles:** P50=4.0s | P90=16.8s | P95=26.0s | P99=119.5s | Max=283.2s

**Important caveat:** These gaps are measured between `user`-type events (tool results) only. Assistant events (thinking, text output, tool_use requests) interleave within these gaps but lack timestamps. The runner's `_read_stream()` resets `last_output_time` on every NDJSON line including assistant events, so actual NDJSON silence is **shorter** than the gaps above. The 283s max gap, for example, contained 3 assistant events (thinking, text, tool_use) between the two timestamped user events.

### Rate Limit Event Behavior

- Every sampled log has 1-3 `rate_limit_event` occurrences. These appear at API rate-limit boundaries (5-hour window checks).
- Rate limit events carry `rate_limit_info.resetsAt` (epoch timestamp) but no `retry_after` field.
- **Agent is silent during rate limits:** 31 of 32 rate-limit events were followed directly by a substantive event (assistant or user), with zero interleaving non-rate-limit events. The agent pauses output entirely during the rate-limit wait.
- Max observed rate-limit pause (measured between surrounding timestamped events): 26.2s. Most are <15s.

---

## Q3 — Wall-Clock Data Points

### Longest legitimate run

**743s (12.4 minutes)** — `20260430-145615-step.json`. This was a successful run with 69 events, end_turn stop_reason.

Top 5 by duration:
1. 743s (12.4m) — 20260430-145615
2. 506s (8.4m) — 20260424-082650
3. 440s (7.3m) — 20260430-140957
4. 378s (6.3m) — 20260424-102559
5. 334s (5.6m) — 20260428-223040

### Timeout-killed runs

**None.** Zero timeout-killed runs found in the entire post-stream-JSON corpus (100 successful logs, all 100 completed naturally with `stop_reason=end_turn`). No log file contains `error: "timeout"` or a `timeout_type` field.

### Current config setting

`config.json` has `step_timeout_seconds: 2400` (40 minutes). With the current runner.py's `max_wall_clock = timeout * 10`, the wall-clock cap is 24,000s (6.7 hours). Given the longest run is 12.4 minutes, the current settings are extremely permissive.

---

## Q4 — Design Recommendation

### (a) Inactivity threshold — ALREADY IMPLEMENTED; recommend tightening

The inactivity-based timeout is already shipped in `runner.py`. The CEO's deferred design decision is answered by existing code.

**Current effective threshold: 2400s (via `step_timeout_seconds`).**

The data strongly supports tightening. Since timestamps only exist on user events and the actual NDJSON cadence is faster than what we can measure, the P99 gap of 119.5s is an overestimate of true silence. Even so:
- **Recommended inactivity threshold: 300s (5 minutes).** Justification: P99 inter-event gap is 119.5s (measured between user events; true NDJSON gap is shorter). A 300s threshold provides 2.5x headroom over the measured P99 and accommodates long LLM thinking sequences. The default `timeout=300` in `run_step()` already reflects this.
- **Action: add `step_inactivity_timeout_seconds: 300` to config.json** and remove reliance on `step_timeout_seconds` for this purpose.

### (b) Hard wall-clock ceiling — YES, keep it; tighten from 24,000s

The current `max_wall_clock = timeout * 10` formula ties the ceiling to the inactivity threshold. With inactivity at 300s, ceiling = 3000s (50 minutes). This is reasonable given:
- Longest legitimate run: 743s (12.4 minutes).
- 50 minutes provides 4x headroom over the observed max.
- A pure inactivity-based system with no ceiling risks unbounded runtime if an agent enters a slow but steady output loop (e.g., infinite retry with periodic status messages).

**Recommendation: keep `max_wall_clock = timeout * 10`. With inactivity=300s, ceiling=3000s (50 min). Alternatively, make it configurable: `step_wall_clock_cap_seconds` in config.json with default `inactivity * 10`.**

### (c) rate_limit_event and inactivity timer — ALREADY HANDLED; no change needed

The existing design resets `last_output_time` on every NDJSON line, including `rate_limit_event`. This is correct. Data confirms:
- Agents go silent during rate limits (31/32 events showed silence).
- Max rate-limit pause observed: 26.2s — well within any reasonable inactivity threshold.
- The `rate_limit_event` IS a signal of "still alive but throttled" and correctly resets the timer under the current line-by-line reader design.

**No code change needed.** The current `_read_stream` approach of resetting on ANY stdout line naturally handles rate_limit_event.

### (d) Code changes needed — CONFIG ONLY

No structural code changes are required. The implementation is complete. The only action items are config and backlog hygiene:

```
# config.json — add explicit inactivity key
"step_inactivity_timeout_seconds": 300

# Optionally add explicit wall-clock cap override
# (defaults to inactivity * 10 if absent)
"step_wall_clock_cap_seconds": 3000
```

**What stays the same:** Log file path generation, return dict shape, cost reporting on terminate, `_write_log()` behavior, thread cleanup, all Popen/stream-reader machinery.

**If adding a separate wall-clock config key**, a small change in `runner.py` line 46:
```python
# Current:
max_wall_clock = timeout * 10

# Proposed (pseudocode):
# Accept an optional wall_clock_cap parameter, default to timeout * 10
max_wall_clock = wall_clock_cap if wall_clock_cap else timeout * 10
```

---

## Q5 — Risks and Edge Cases

### (a) Agent stuck in a tool call producing no NDJSON output

**Can this happen?** Yes, in theory. If a tool call (e.g., `Bash` running a long compilation or download) blocks for more than the inactivity threshold, the agent produces no NDJSON output during that time. However:
- In the current Bellows operational profile (writing/reading files, running tests), tool calls rarely exceed 60s. The data shows no legitimate gap approaching 300s in actual NDJSON output (the 283s gap measured between user-event timestamps contained 3 assistant events).
- `claude -p` writes the `user` event (tool result) when the tool completes, resetting the timer.
- **Mitigation:** If a use case emerges where tool calls routinely exceed 5 minutes, increase the inactivity threshold via config. No code change needed.

### (b) Network hang vs agent hang

- A network hang (API unreachable) would cause `claude -p` to either retry with backoff (emitting rate_limit_event or error output) or exit with a non-zero code. In either case, the runner would detect it — either through output resetting the timer, or through process exit.
- An agent hang (infinite loop within Claude Code itself) would produce no NDJSON output and would be correctly killed by the inactivity timeout.
- **Distinction doesn't matter operationally:** both cases are handled by the existing mechanism. The `ceo_flags` in the timeout return dict includes the timeout type for post-mortem analysis.

### (c) Interaction with existing call sites

The `timeout` parameter is passed in by `bellows.py` via config lookup (lines 298, 356). The new design doesn't add a parameter — it tightens the config value. Both call sites use the same config lookup chain: `config.get("step_inactivity_timeout_seconds", config.get("step_timeout_seconds", 300))`. Adding `step_inactivity_timeout_seconds` to config.json takes precedence cleanly.

### (d) Other failure modes

- **Thread join timeout on kill:** After `proc.kill()`, reader threads are joined with `timeout=5` (lines 130-131). If a thread hangs (e.g., blocked on a pipe read), it's a daemon thread and will be cleaned up on process exit. Not a risk in practice.
- **Config migration:** Existing `step_timeout_seconds: 2400` should be left in place for backward compatibility until `step_inactivity_timeout_seconds` is added. Once added, `step_timeout_seconds` becomes a dead key (referenced only as fallback). Document this in config.json.
- **Log corpus bias:** All 100 post-stream-JSON logs completed successfully. No timeout kills means we have no data on what a legitimate timeout looks like. The 300s threshold is conservative, but the first real timeout should be investigated to validate the threshold choice.

---

## Summary for CEO Decisions

| Decision | Answer | Justification |
|---|---|---|
| Inactivity-based timeout needed? | **Already implemented.** Shipped in current runner.py. | `last_output_time` + line-by-line stream readers + polling loop. |
| Recommended inactivity threshold? | **300s** (tighten from current 2400s) | P99 gap=119.5s (overestimate); 300s = 2.5x P99. |
| Hard wall-clock ceiling? | **Yes, keep it.** 3000s (50 min) with inactivity=300s. | Longest run=743s (12.4m); 3000s = 4x longest. Prevents unbounded slow-output loops. |
| Does `rate_limit_event` reset timer? | **Yes, already does.** No change needed. | Agent goes silent during rate limits; the event is the only "alive" signal. Max pause=26s, well within threshold. |
| Backlog item status? | **Resolved.** Close the backlog entry. | Implementation shipped; only config tightening recommended. |
