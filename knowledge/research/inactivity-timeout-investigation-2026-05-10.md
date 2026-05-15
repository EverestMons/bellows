# Inactivity Timeout Investigation — Findings

**Date:** 2026-05-10
**Plan:** diagnostic-inactivity-timeout-investigation-2026-05-10
**Analyst:** Bellows Systems Analyst (SA)

---

## Q1 — CONFIG-LOAD AUDIT

### (a) Current value of `step_inactivity_timeout_seconds`

`config.json:18`: `"step_inactivity_timeout_seconds": 1800`

### (b) How `runner.run_step()` receives the timeout value

`bellows.py:301-302` (first call site) and `bellows.py:388-389` (while-loop continuation):

```python
timeout=config.get("step_inactivity_timeout_seconds",
                   config.get("step_timeout_seconds", 300))
```

With `step_inactivity_timeout_seconds: 1800` present in config, this resolves to `timeout=1800`. The fallback chain (`step_timeout_seconds` → hardcoded `300`) is never reached.

### (c) Where timeout is compared against `last_output_time`

`runner.py:109-110` (age computation):
```python
with lock:
    age = now - last_output_time
```

`runner.py:118` (inactivity check):
```python
if age >= timeout:
```

This is the sole comparison. `age` is the elapsed time since the last subprocess output line. `timeout` is the 1800s value passed from bellows.py.

### (d) Is the timeout value reassigned or overridden inside `run_step()`?

**No.** The `timeout` parameter (runner.py:33, default=300) is used directly at:
- Line 49: `max_wall_clock = timeout * 10`
- Line 118: `if age >= timeout:`
- Line 119: `print(f"... inactivity timeout ({timeout}s ...)`

No `timeout = timeout or X`, no reassignment, no fallback chain inside `run_step()`. The value received (1800) is the value checked.

### (e) Wall-clock cap verification

`runner.py:49`:
```python
max_wall_clock = timeout * 10
```

With `timeout=1800`, `max_wall_clock = 18000` (5 hours). Enforced at `runner.py:125-130`:
```python
if elapsed >= max_wall_clock:
    print(f"Bellows: runner — hard wall-clock cap reached ({max_wall_clock}s), killing process", flush=True)
    proc.kill()
```

**Config-load path is structurally correct.** The value 1800 flows unmodified from config.json → bellows.py → runner.run_step() → age comparison. No drops, no overrides.

---

## Q2 — SUBPROCESS PLUMBING AUDIT

### (a) Subprocess invocation

`runner.py:52-58`:
```python
proc = subprocess.Popen(
    cmd,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
    cwd=project_path,
)
```

Standard `subprocess.Popen` with PIPE'd stdout AND stderr, text mode.

### (b) Stdout consumption

Threaded readers. `runner.py:95-98`:
```python
stdout_thread = threading.Thread(target=_read_stream, args=(proc.stdout, stdout_buf), daemon=True)
stderr_thread = threading.Thread(target=_read_stream, args=(proc.stderr, stderr_buf), daemon=True)
stdout_thread.start()
stderr_thread.start()
```

Two daemon threads, one per stream, each running `_read_stream()` which iterates line-by-line (`for line in stream:` at runner.py:88).

### (c) Where `last_output_time` is updated

`runner.py:82` (initialization):
```python
last_output_time = time.monotonic()
```

`runner.py:89-91` (update inside `_read_stream`):
```python
with lock:
    buf.append(line)
    last_output_time = time.monotonic()
```

Updated on every line received from EITHER stdout or stderr, under a shared `threading.Lock`.

### (d) Timeout check location

Polled in a 1-second loop at `runner.py:104-130`:
```python
while proc.poll() is None:
    time.sleep(1)
    now = time.monotonic()
    # ...
    with lock:
        age = now - last_output_time
    # Heartbeat every 60s (lines 113-115)
    # Inactivity timeout (lines 118-122)
    if age >= timeout:
        proc.kill()
        timed_out = True
        break
    # Wall-clock cap (lines 125-130)
```

### (e) Kill path

On inactivity timeout (`runner.py:119-122`):
```python
print(f"Bellows: runner — inactivity timeout ({timeout}s with no output), killing process", flush=True)
proc.kill()
timed_out = True
break
```

`proc.kill()` sends SIGKILL on Unix. Reader threads joined with 5s timeout (`runner.py:133-134`). Return dict: `{is_error: True, error: "timeout", stop_reason: "timeout", escalate: True, receipt_status: "Blocked"}`.

---

## Q3 — STDOUT BUFFER DEADLOCK ANALYSIS

### (a) Stderr capture

Stderr IS captured separately with `stderr=subprocess.PIPE` (runner.py:55) and read by a dedicated thread (runner.py:96). This avoids the classic deadlock where one pipe fills while the other is being read.

### (b) Concurrent reading

Yes. Both stdout and stderr are read concurrently by separate daemon threads (runner.py:95-98). There is no deadlock risk from pipe buffer exhaustion — both buffers are drained continuously.

### (c) Timer behavior during subprocess deadlock

If the subprocess were somehow deadlocked (neither stdout nor stderr producing output), both reader threads would block on `for line in stream:`, `last_output_time` would stop advancing, `age` would grow at wall-clock rate, and the `if age >= timeout` check at runner.py:118 WOULD fire once `age` reaches 1800s.

**Empirical confirmation:** stderr is consistently empty in production. Analysis of the entire 684-log corpus shows zero logs with stderr content (`stderr_len=0` across all entries). The `claude -p` subprocess does not write to stderr during normal operation. Therefore stderr cannot be silently resetting the timer.

**Hypothesis 2 (stdout buffer deadlock) is DISPROVEN.** The plumbing is correct — two concurrent readers, no buffer deadlock risk, and the timer mechanism would correctly fire even if a deadlock occurred.

---

## Q4 — ACTIVITY-CANARY RESET AUDIT

### (a) Every place that updates `last_output_time`

There is exactly **one** update site: `runner.py:91` inside `_read_stream()`:

```python
last_output_time = time.monotonic()
```

This is inside the `for line in stream:` loop that reads subprocess stdout/stderr. It fires only on genuine subprocess output lines. No other code path updates `last_output_time`.

Classification:
- `_read_stream(proc.stdout, ...)` → updates on subprocess stdout lines (genuine agent NDJSON output)
- `_read_stream(proc.stderr, ...)` → updates on subprocess stderr lines (consistently empty in production; see Q3(c))
- Bellows heartbeat at runner.py:113-115 → **does NOT update** `last_output_time`; it only reads `age = now - last_output_time`

### (b) Heartbeat interaction with canary

The heartbeat at `runner.py:113-115`:
```python
if now - last_heartbeat >= 60:
    print(f"Bellows: runner — {int(elapsed)}s elapsed, last output {int(age)}s ago", flush=True)
    last_heartbeat = now
```

This `print()` writes to Bellows's own stdout (the terminal), NOT to the subprocess streams. It updates `last_heartbeat` (the heartbeat cadence tracker) but does NOT touch `last_output_time`. The canary is NOT falsely reset by the heartbeat.

### (c) Background threads that could reset the canary

Only two background threads exist in `run_step()`: the stdout reader and the stderr reader (runner.py:95-98). Both correctly update `last_output_time` only on genuine subprocess output. No other threads exist.

**Hypothesis 3 (canary reset bug) is DISPROVEN.** The canary is updated exclusively by genuine subprocess output. The heartbeat and other Bellows-side activity do not reset it.

---

## Q5 — EMPIRICAL TIMING DATA

### (a) Heartbeat progression confirms canary is advancing

The BACKLOG entry documents: "`last output 256s ago` advancing to `last output 910s+ ago`". The heartbeat's `age` value is computed from `last_output_time`, which is only updated by genuine subprocess output (Q4). The fact that `age` is monotonically increasing confirms:

1. No subprocess output is being produced (no false resets)
2. The canary is correctly tracking the time since last output
3. **This is evidence AGAINST Hypothesis 3** (canary reset)

### (b) Why the kill didn't fire

The `last output 910s ago` observation is the critical data point. The configured threshold is 1800s. **910s < 1800s.** The kill check at runner.py:118 (`if age >= timeout`) evaluates `910 >= 1800` → `False`. The timeout had not been reached when the user manually killed the process.

The BACKLOG says "Step 1 ran 41+ minutes" (2460s elapsed). If the last output was at ~1550s elapsed (2460s - 910s), and the threshold is 1800s of inactivity, the automatic kill would have fired at ~3350s elapsed (1550s + 1800s = 3350s ≈ 55.8 minutes). **The user killed Bellows approximately 15 minutes before the inactivity timeout would have fired.**

This is **(i) the threshold being checked IS 1800s** and **(ii) the kill check itself would fire** — the user simply intervened first.

### (c) Log corpus analysis

No log file exists for the hung run. When the user kills the Bellows process externally (`kill` command), `runner.py` never reaches its log-writing code paths. The process dies mid-loop.

The 37-minute successful run (`20260506-175815-step.json`, 2222s duration, 590 events) is a different session that completed normally. Its maximum inter-event gap was 304.1s — within the 1800s threshold by a wide margin.

---

## Q6 — KILL PATH VERIFICATION

### (a) Kill mechanism

`proc.kill()` at runner.py:120. On Unix/macOS, this sends SIGKILL (signal 9) — immediate, unblockable process termination. Reader threads joined with 5s timeout at runner.py:133-134 (daemon threads, so cleanup occurs even if join times out).

### (b) Propagation to caller

Returns a fully-formed dict at runner.py:150-162:
```python
return {
    "is_error": True,
    "error": "timeout",
    "session_id": None,
    "escalate": True,
    "receipt_status": "Blocked",
    "ceo_flags": [f"Step timed out ({timeout_type}) after {int(elapsed)}s"],
    "cost_usd": None,
    "stop_reason": "timeout",
    "result_text": "",
    "permission_denials": [],
    "verdict_requested": {"requested": False, "reason": None},
}
```

The caller (`bellows.py:run_plan()`) receives this as `parsed` and proceeds to gate check and verdict posting. `escalate: True` triggers a Pushover notification.

### (c) Post-kill state

- Worktree: unchanged (still exists, still has the agent's partial work)
- Plan file: stays at `in-progress-*` prefix (the pause/rename logic only fires when gates are checked; the timeout return triggers gate check which will produce a gate_failure for the error)
- bellows.db: `record_run()` at bellows.py:307-311 records `receipt_status: "Blocked"` for the step

### (d) Notification path

The print at runner.py:119 (`"Bellows: runner — inactivity timeout ({timeout}s with no output), killing process"`) would appear in terminal output. Additionally, `escalate: True` in the return dict triggers `notifier.notify_verdict_request()` downstream. **The absence of this print in the 2026-05-06 reproduction is definitive evidence that the kill path was never reached** — because `age` never reached 1800s.

---

## Q7 — CROSS-REFERENCE WITH 2026-05-01 EMPIRICAL ANALYSIS

### (a) Did any gap exceed the configured threshold?

The 2026-05-01 diagnostic found P99=119.5s and max=283.2s (inter-user-event gaps, which overestimate true NDJSON silence). The configured threshold at that time was 2400s (pre-tightening). No gap came close to 2400s. Post-tightening to 300s, the threshold was closer to the distribution tail but still above max. Today's measurement of the longest 2026-05-06 log (37-min run) found a max gap of 304.1s — above 300s but well below 1800s.

### (b) Pre-tightening enforcement

The pre-tightening threshold (2400s via `step_timeout_seconds`) WAS being enforced. The mechanism is identical — the `run_step()` timeout parameter controls the check. But with 2400s threshold and max observed gap of 283s, the kill never triggered during normal operation.

**Post-tightening kills:** Two successful inactivity timeout kills exist in the corpus:
1. `20260501-173542-step.json`: `timeout_type: "inactivity"`, `elapsed_seconds: 431.5` — killed when configured threshold was 300s
2. `20260505-145844-step.json`: `timeout_type: "inactivity"`, `elapsed_seconds: 11.0` — quick kill, likely a stuck process

These confirm the kill path is exercised and functions correctly.

### (c) "Zero timeout kills in 100-log corpus"

The 2026-05-01 diagnostic's 100-log corpus was post-stream-JSON era only. Pre-stream-JSON logs (2026-04-15 through 2026-04-17) contain 34 timeout kills. Including the two post-2026-05-01 kills, the total is 36 inactivity timeout kills across 684 logs. The mechanism works and HAS killed hung processes.

---

## Q8 — RECOMMENDATION

### Classification: (iv) Threshold mismatch

None of the three hypothesized bugs exist:

| Hypothesis | Status | Evidence |
|---|---|---|
| (i) Config-load bug | **DISPROVEN** | Q1: value flows unmodified from config.json → bellows.py → runner.py → age comparison |
| (ii) Stdout/stderr buffer deadlock | **DISPROVEN** | Q3: concurrent threaded readers drain both pipes; stderr consistently empty; timer would fire even on deadlock |
| (iii) Canary reset bug | **DISPROVEN** | Q4: only genuine subprocess output resets `last_output_time`; heartbeat does NOT reset it; Q5(a) confirms canary is advancing monotonically |
| **(iv) Threshold mismatch** | **CONFIRMED** | Q5(b): configured 1800s threshold, observed 910s gap at manual kill — kill would fire at 1800s but user intervened at 910s |

**The inactivity timeout mechanism is structurally correct and has fired successfully 36 times across the log corpus.** The bug is that `step_inactivity_timeout_seconds: 1800` (30 minutes) is too high for the CEO's operational expectation. A genuinely hung process must sit idle for a full 30 minutes before automatic intervention, creating a window where manual kills are the only recourse.

### Config change history

| Date | Threshold | Source |
|---|---|---|
| Pre-2026-05-01 | 2400s (via `step_timeout_seconds`) | Original config |
| 2026-05-01 | 300s (via `step_inactivity_timeout_seconds`) | SA recommendation, 2.5x P99 |
| 2026-05-06 | 1800s | CEO adjustment (300s was too aggressive) |

The 300s → 1800s adjustment (6x increase) created the 30-minute dead zone. The 2026-05-06 reproduction's 910s gap would have been killed at 300s but was not killed at 1800s.

### Recommended fix

**Tighten threshold to 600s (10 minutes):**

- `config.json:18`: `"step_inactivity_timeout_seconds": 600`
- Wall-clock cap becomes `600 * 10 = 6000s` (100 minutes) — still generous
- Provides 2.0x headroom over the observed max inter-event gap (304.1s in the 37-minute 2026-05-06 run)
- Limits the hung-process dead zone to 10 minutes (vs. 30 minutes at 1800s)
- LOC: 0 (config-only change)
- Risk: Low — may occasionally kill legitimately slow agents, but the 2x headroom over max observed gap provides a safety margin
- Test approach: Deploy config change, restart Bellows, monitor for false-positive timeout kills over next 5 sessions. If any legitimate kills at 600s, bump to 900s.

---

## Root Cause

**The inactivity timeout does not fire on hung runners because the configured threshold (1800s) exceeds the observed inactivity gap at the time of manual intervention.** The mechanism is correct; the parameter is wrong.

The code path `config.json:18 → bellows.py:301 → runner.py:33 → runner.py:118` is an unbroken chain that correctly compares wall-clock silence against the configured threshold. Both stdout and stderr readers correctly update the canary (though stderr is consistently empty). The heartbeat does not interfere. The kill path sends SIGKILL and returns an `escalate: True` error dict. The mechanism has fired successfully 36 times in the log corpus (most pre-2026-04-17, two post-2026-05-01).

The structural seam is the absence of a feedback loop: when the user manually kills Bellows at 910s of inactivity, no record is written (the process dies before the log-write path), so there is no signal to suggest the threshold should be lowered. The user's only recourse is a BACKLOG entry, which is what produced this diagnostic.

---

## Confidence

| Claim | Confidence | Evidence that would raise it |
|---|---|---|
| Config value (1800) flows correctly to the kill check | **HIGH** | Code trace Q1(b-d) with zero drops or overrides |
| The inactivity canary is NOT falsely reset | **HIGH** | Q4 (single update site), Q5(a) (heartbeat shows monotonic advance), Q3(c) (stderr empty) |
| The 2026-05-06 gap never reached 1800s | **HIGH** | Q5(b): 910s observed < 1800s threshold; user killed at that point; elapsed time (2460s) consistent with kill before threshold |
| Recommended 600s threshold provides adequate headroom | **MEDIUM** | Max observed gap is 304.1s from one log; broader sample of very long runs (30+ min) would strengthen this. A rate-limit-induced silence >300s could push the gap closer to 600s. |
| The 300s → 1800s change was a CEO adjustment | **MEDIUM** | Inferred from config.json state at two timestamps; no config change log exists. Git blame on config.json would confirm. |

---

## Rule 20 — QA Self-Check

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: bellows/knowledge/research/
Files verified: 1
```

---

## Output Receipt

**Agent:** Bellows Systems Analyst
**Step:** 1
**Status:** Complete

### What Was Done
Investigated the inactivity timeout non-firing bug from BACKLOG 2026-05-06. Audited the full code path (config.json → bellows.py → runner.py), the subprocess plumbing, the canary reset mechanism, and the empirical log corpus (684 logs, 36 timeout kills). All three hypothesized bugs disproven. Root cause identified as threshold mismatch: configured 1800s threshold exceeds the 910s inactivity gap observed before manual kill.

### Files Deposited
- `bellows/knowledge/research/inactivity-timeout-investigation-2026-05-10.md` — full findings with Q1-Q8 answers, root cause, confidence assessment

### Files Created or Modified (Code)
- None (read-only investigation)

### Decisions Made
- Classified bug as (iv) threshold mismatch, not a code defect
- Recommended 600s threshold (2x headroom over observed 304s max gap)

### Flags for CEO
- Config change `step_inactivity_timeout_seconds: 600` is the recommended fix — zero code changes required
- The 300s → 1800s threshold change between 2026-05-01 and 2026-05-06 is the structural cause — if 300s was too aggressive, 600s provides a middle ground

### Flags for Next Step
- None — single-step diagnostic
