# Runner Subprocess Management — Diagnostic Findings
**Date:** 2026-04-17 | **Source:** `runner.py` (full read)

---

## Q1 — Subprocess launch pattern

`run_step` uses **`subprocess.run`** (blocking). The exact call:

```python
result = subprocess.run(
    cmd,
    cwd=project_path,
    capture_output=True,
    text=True,
    timeout=timeout,
)
```

- `capture_output=True` — pipes both stdout and stderr (equivalent to `stdout=PIPE, stderr=PIPE`)
- `text=True` — decodes output as UTF-8 strings
- `timeout=timeout` — default 600 seconds, passed as parameter
- `cwd=project_path` — runs in the target project directory

The command itself is `claude -p <prompt> --output-format json --model <model> --allowedTools <tools>`, optionally with `--resume <session_id>`.

**Implication:** `subprocess.run` is fully blocking. The calling thread is parked until the subprocess exits or the timeout fires. There is no opportunity to inspect partial output, monitor activity, or implement an activity-based timeout while the call is in progress.

## Q2 — Output capture

Output is captured **all-at-once after completion**. `capture_output=True` buffers the entire stdout and stderr in memory. The caller sees `result.stdout` and `result.stderr` only after the subprocess exits.

- No streaming / line-by-line reading exists.
- No partial-output hook exists.
- stderr is printed (first 500 chars) on the success path but only after the process finishes.
- stdout is parsed as JSON via `json.loads(result.stdout)` then passed to `parse()`.

**Implication:** There is zero visibility into what the agent is doing mid-step. If the agent is active but slow, or idle/hung, the runner cannot distinguish these states — it only knows "still waiting" vs "done" vs "timed out."

## Q3 — Timeout mechanism

The timeout is **`subprocess.run(timeout=N)`**, which raises `subprocess.TimeoutExpired` after N seconds of wall-clock time (default 600s).

When the timeout fires:
- Python sends SIGKILL to the child process (on Unix, `subprocess.run` kills the child on `TimeoutExpired`).
- The `except subprocess.TimeoutExpired` block logs the failure and returns a structured error dict with `"error": "timeout"`, `escalate: True`, and a CEO flag `"Step timed out after {timeout}s"`.
- **Note:** `stderr_partial` is logged as empty string `""` — the partial stderr from the timed-out process is not captured (the `TimeoutExpired` exception object has a `.stderr` attribute that could be used here but isn't).

**Implication:** The timeout is purely wall-clock. A step that is actively producing output at 599s gets killed just the same as one that hung at 10s. An activity-based timeout (reset-on-output) would require switching from `subprocess.run` to `subprocess.Popen` with a streaming read loop.

---

## Summary for activity-based timeout design

To implement a timeout that resets when the agent produces output, the runner would need to:

1. **Replace `subprocess.run` with `subprocess.Popen`** — non-blocking, gives access to stdout/stderr pipes.
2. **Stream stdout/stderr line-by-line** (or chunk-by-chunk) in a read loop.
3. **Track last-output timestamp** — reset a timer each time data arrives.
4. **Kill the process if the inactivity window exceeds the threshold** (`proc.kill()` or `proc.terminate()`).
5. **Accumulate the full output** in a buffer so downstream JSON parsing still works.
6. **Capture partial output on timeout** — unlike the current approach, partial stderr/stdout would be available for diagnostics.
