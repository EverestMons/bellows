# Partial-Output Loss on Inactivity-Timeout Kill — Design Diagnostic

**Date:** 2026-06-12
**Agent:** Bellows Systems Analyst
**Plan:** diagnostic-partial-output-timeout-loss
**FORWARD ref:** Row 18

---

## Section 1 — Stream Lifecycle Anatomy

### Subprocess launch and stream plumbing

The subprocess is created at `runner.py:62` via `subprocess.Popen` with `stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True`. Both pipes are consumed by reader threads, not the main thread.

### Reader threads and buffer accumulation

Two shared buffers are initialized at `runner.py:90-91`:

```python
stdout_buf = []    # runner.py:90
stderr_buf = []    # runner.py:91
```

A `last_output_time` timestamp (`runner.py:92`) and a `threading.Lock` (`runner.py:93`) protect shared state.

The `_read_stream` closure (`runner.py:95-103`) runs in daemon threads (`runner.py:105-108`). It iterates `for line in stream` and on each line: acquires the lock, appends to the buffer, and bumps `last_output_time`:

```python
def _read_stream(stream, buf):                  # :95
    nonlocal last_output_time
    try:
        for line in stream:
            with lock:
                buf.append(line)                 # :100 — data enters memory
                last_output_time = time.monotonic()  # :101 — feeds inactivity timer
    except Exception:
        pass
```

### Inactivity timer

The main thread polls in a `while proc.poll() is None` loop (`runner.py:114`), sleeping 1s per tick (`runner.py:115`). Each tick reads `last_output_time` under lock (`runner.py:119-120`) and computes `age = now - last_output_time`.

- **Heartbeat logging** every 60s (`runner.py:122-125`): `runner: {elapsed}s elapsed, last output {age}s ago (step {step_num})` — this proves the reader thread is feeding timestamps into memory.
- **Inactivity check** at `runner.py:128`: `if age >= timeout`.
- **Wall-clock cap** at `runner.py:135`: `if elapsed >= max_wall_clock` (where `max_wall_clock = timeout * 10`, `runner.py:59`).

### The kill path on timeout

When `age >= timeout` at `runner.py:128`:

1. **`proc.kill()`** at `runner.py:130` — sends SIGKILL to the subprocess.
2. **`timed_out = True`** at `runner.py:131`.
3. **`break`** at `runner.py:132` — exits the polling loop.

After the break:

4. **Reader thread join** at `runner.py:143-144` with 5s timeout — allows threads to drain remaining pipe data after SIGKILL.
5. **Buffer join** at `runner.py:146-147`:
   ```python
   result_stdout = "".join(stdout_buf)   # :146 — output IS available here
   result_stderr = "".join(stderr_buf)   # :147
   ```

**The accumulated stdout buffer IS joined into `result_stdout` at line 146.** The data exists in memory at this point.

### The timeout log write — where output is LOST

At `runner.py:151-159`, the timeout branch writes the step JSON:

```python
if timed_out:                                                 # :151
    timeout_type = "wall_clock_cap" if wall_clock_hit else "inactivity"
    _write_log(log_path, {                                    # :153
        "success": False,
        "error": "timeout",
        "timeout_type": timeout_type,
        "elapsed_seconds": round(elapsed, 1),
        "stderr_partial": result_stderr[:5000],               # :158 — stderr IS written
    })                                                        # :159
```

**`raw_output` is NOT included in this dict.** The variable `result_stdout` exists and contains the accumulated buffer, but is simply never referenced on this path.

### The timeout return dict — output also absent

At `runner.py:160-172`, the return dict has:

```python
"result_text": "",    # :169 — hardcoded empty string
```

All downstream consumers (bellows.py gates, verdict posting, lifecycle DB) receive an empty string.

### `raw_output` write-site census (all paths)

| Path | File:Line | `raw_output` written? | Truncation |
|---|---|---|---|
| **Timeout (inactivity or wall-clock)** | runner.py:153-159 | **NO — OMITTED** | N/A |
| Non-zero exit | runner.py:189-194 | Yes: `result_stdout[:5000]` | **5000 chars** |
| No result event | runner.py:228-233 | Yes: `result_stdout[:5000]` | **5000 chars** |
| Parse error | runner.py:253-258 | Yes: `result_stdout[:5000]` | **5000 chars** |
| Success | runner.py:278-283 | Yes: `result_stdout` (full) | **No cap** |

### Precise loss point

**`runner.py:153-159`** — the `_write_log` call on the timeout path omits `raw_output` despite `result_stdout` being available at `runner.py:146`. Secondary loss: **`runner.py:169`** — the return dict hardcodes `result_text: ""`, discarding the buffer for all downstream consumers.

---

## Section 2 — Evidence Reconciliation

### Step JSON from the incident

File: `logs/20260611-143027-step.json`

```json
{
  "success": false,
  "error": "timeout",
  "timeout_type": "inactivity",
  "elapsed_seconds": 703.9,
  "stderr_partial": ""
}
```

Confirmed: **no `raw_output` field present.** The step JSON contains only the five fields written by the timeout path at `runner.py:153-159`. Zero forensic data about what the agent produced before stalling.

### Daemon terminal log reconstruction

Source: `logs/terminal/bellows-2026-06-11.log`, slug `executable-draft-143021`.

| Timestamp | Log line | Interpretation |
|---|---|---|
| 14:30:26 | `detected plan` | Plan pickup |
| 14:30:28 | `started` | Subprocess launched |
| 14:31:27 | `60s elapsed, last output 22s ago` | Output at ~38s into execution |
| 14:32:28 | `120s elapsed, last output 16s ago` | Output at ~104s into execution |
| 14:33:28 | `180s elapsed, last output 77s ago` | Last output at ~103s — **stall began here** |
| 14:34:28 | `241s elapsed, last output 137s ago` | Age growing monotonically — confirmed stall |
| 14:35:28–14:41:31 | `301s–663s elapsed, last output 197s–560s ago` | Continued stall |
| 14:42:11 | `inactivity timeout (600s with no output), killing process` | **Kill at 703s elapsed** |

### Loss quantification

- **Output produced:** ~103 seconds of agent output (from launch at 14:30:28 to stall at ~14:32:11).
- **Output lost:** 100% — the step JSON contains no `raw_output`, and the return dict's `result_text` is `""`.
- **Output type:** NDJSON stream (since `--output-format stream-json` is always passed at `runner.py:48`). The ~103s of output would contain tool calls, assistant text blocks, and possibly partial result events — the exact forensic trail needed to diagnose what caused the stall.
- **Effective timeout:** 600s (the `timeout` parameter value logged in the kill message). The config key `step_inactivity_timeout_seconds` was reportedly raised to 1800s on 2026-05-01 (`PROJECT_STATUS.md:108`), but this plan executed with 600s — either the config was not reloaded or this project's config did not include the override.

---

## Section 3 — Fix Shapes

### Shape (a): Persist accumulated buffer on kill path

**What:** Add `raw_output` to the timeout path's log dict and populate `result_text` in the return dict, using the already-available `result_stdout` variable at `runner.py:146`.

**Changes (2 sites):**

1. `runner.py:153-159` — add `"raw_output": result_stdout[:5000]` to the `_write_log` dict.
2. `runner.py:169` — change `"result_text": ""` to `"result_text": result_stdout[:5000]`.

**Crash-safety:** Same as all other paths. If the daemon crashes (SIGKILL, OOM) between `proc.kill()` and `_write_log()`, data is lost. This is a ~0.1s window (join threads + dict construction). Acceptable — this failure class has not been observed.

**Disk behavior:** No new files. The existing step JSON grows by up to 5000 chars.

**Truncation:** Consistent with the non-zero-exit, no-result-event, and parse-error paths (all cap at 5000).

**Blast radius:** 2 lines in `runner.py`. No behavioral change to any other code path. Downstream consumers (gates, verdict posting) will see non-empty `result_text` on timeout for the first time, but all gate checks on `result_text` are safe with non-empty strings (they check for presence of patterns, not absence).

### Shape (b): Incremental spill — reader writes to `.partial` file

**What:** Modify `_read_stream` at `runner.py:95-103` to open a per-step file (e.g., `logs/{timestamp}-step.partial`) and append each line as it arrives. On clean completion, delete the `.partial` file after writing the full log. On kill or daemon crash, the `.partial` file survives.

**Changes (~4 sites):**

1. `runner.py:57` area — construct `.partial` path alongside `log_path`.
2. `runner.py:95-103` — open file handle, append per line, handle I/O errors.
3. `runner.py:278` area — delete `.partial` on success path.
4. `runner.py:153` area — reference `.partial` path in timeout log for cross-reference.

**Crash-safety:** YES — survives daemon crash, OOM, power loss. The `.partial` file is written incrementally. This is the key advantage over shape (a).

**Disk behavior:** Creates one new file per running step. File grows unbounded during execution (successful steps may produce 100KB+). Requires cleanup — either on success or via a periodic sweep of stale `.partial` files.

**Truncation:** No inherent cap. The `.partial` file contains the full stream. A post-hoc truncation policy would need to be applied when reading it for forensics. Inconsistent with the 5000-char convention unless a rotation/cap mechanism is added.

**Blast radius:** 4+ sites across `runner.py`. The reader thread gains disk I/O on every line, adding latency to the hot path. File handle lifecycle (open/close/error) must be managed across thread boundaries.

### Shape (c): Both (a) and (b)

Combines (a) for the common case and (b) for the daemon-crash case. Belt and suspenders. Additive complexity of both shapes.

### Recommendation: Shape (a)

Shape (a) is the minimal fix that addresses the observed failure. The data is already in memory; the bug is a pure omission in two dict literals. Shape (b) addresses a different failure class (daemon crash mid-step) that has never been observed and adds significant complexity to the reader hot path. If daemon crashes during step execution become a concern, shape (b) can be layered on later without any interaction with shape (a).

---

## Section 4 — Gap Assessment + Verification Blocks

### Gap Assessment

| Gap | Current State (file:line) | Proposed State | Change Required |
|---|---|---|---|
| G1: Timeout log omits `raw_output` | `runner.py:153-159` — `_write_log` dict has no `raw_output` key | Add `"raw_output": result_stdout[:5000]` | Add 1 key to dict literal |
| G2: Timeout return dict has empty `result_text` | `runner.py:169` — `"result_text": ""` | Change to `"result_text": result_stdout[:5000]` | Edit 1 value in dict literal |
| G3: Truncation policy for timeout partial output | N/A (no output written) | 5000 chars (consistent with error paths) or raised cap | CEO decision fork |

### Verification Blocks

```
V1: (claim: "The buffer-loss line is runner.py:153-159",
     query: "Read runner.py:153-159 and confirm _write_log dict has no raw_output key",
     expected_output: "Dict contains success, error, timeout_type, elapsed_seconds, stderr_partial — no raw_output")

V2: (claim: "The timeout-path return dict has empty result_text at runner.py:169",
     query: "Read runner.py:169 and confirm result_text value",
     expected_output: '"result_text": ""')

V3: (claim: "Truncation census: non-zero-exit at :192, no-result-event at :231, parse-error at :256 all cap at 5000; success at :280 is uncapped; timeout omits entirely",
     query: "Grep runner.py for 'raw_output' and verify each occurrence's truncation",
     expected_output: "4 occurrences: 3x [:5000], 1x full, 0x on timeout path")
```

### CEO Decision Forks

**Fork 1 — Fix shape:**
- **(a) Persist buffer on kill path** — 2-line change, consistent with existing patterns. **Recommended.**
- **(b) Incremental spill** — crash-safe but complex; addresses unobserved failure class.
- **(c) Both** — maximum coverage, maximum complexity.

**Fork 2 — Truncation cap for timeout partial output:**
- **5000 chars** — consistent with other error paths. Conservative. **Recommended** for initial ship; can be raised later if forensics prove insufficient.
- **10000 chars** — timeout output is inherently shorter than successful output; a larger cap costs little.
- **Uncapped** — matches success path. Timeout output is the primary forensic artifact and is bounded by the stall point (typically < 50KB). Risk: unbounded log file growth on pathological cases.

---

## Output Receipt
**Agent:** Bellows Systems Analyst
**Step:** 1
**Status:** Complete

### What Was Done
Investigated the partial-output loss on inactivity-timeout kill (FORWARD row 18). Traced the stream lifecycle through runner.py, identified the precise loss point (runner.py:153-159 omits `raw_output`; runner.py:169 hardcodes empty `result_text`), confirmed the incident evidence from 2026-06-11 (plan `executable-draft-143021`, ~103s of output lost), and designed three fix shapes with a recommendation for shape (a).

### Files Deposited
- `knowledge/research/partial-output-timeout-loss-2026-06-12.md` — full diagnostic with stream lifecycle anatomy, evidence reconciliation, fix shapes, gap assessment, and verification blocks

### Files Created or Modified (Code)
- None (investigation only)

### Decisions Made
- Recommended shape (a) (persist buffer on kill path) as the fix — minimal change, addresses observed failure, consistent with existing patterns

### Flags for CEO
- Fork 1: Fix shape selection — (a)/(b)/(c)
- Fork 2: Truncation cap — 5000/10000/uncapped

### Flags for Next Step
- None
