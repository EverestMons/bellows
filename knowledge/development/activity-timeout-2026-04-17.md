# Activity-Based Inactivity Timeout — Dev Log
**Date:** 2026-04-17 | **Plan:** `executable-activity-timeout-2026-04-17`

## Output Receipt
- **Status:** Complete
- **File changed:** `runner.py` (full rewrite of `run_step`), `bellows.py` (config field update)
- **Commit:** `feat: activity-based inactivity timeout — replace subprocess.run with Popen streaming`

## What Changed

### runner.py — `run_step` rewrite
1. **`subprocess.run` → `subprocess.Popen`** — non-blocking launch with `stdout=PIPE, stderr=PIPE, text=True, cwd=project_path`.
2. **Threaded streaming read** — two daemon threads read stdout and stderr concurrently via `for line in stream`. Each line resets `last_output_time` under a lock.
3. **Inactivity timer** — main loop polls every 1s. If `now - last_output_time >= timeout`, calls `proc.kill()` and returns timeout error dict with `stderr_partial` populated from accumulated buffer.
4. **Heartbeat** — every 60s prints `Bellows: runner — {elapsed}s elapsed, last output {age}s ago` to give CEO visibility into agent activity.
5. **Hard wall-clock cap** — `timeout * 10` (e.g. 300s inactivity → 3000s max). Prevents pathological drip-feed from running forever. Prints warning on hit.
6. **Non-zero exit handling** — explicit branch for `proc.returncode != 0` with stderr capture.
7. **Timeout error dict** — now includes `stderr_partial` (first 5000 chars) and `timeout_type` (inactivity vs wall_clock_cap) in both logs and CEO flags.

### bellows.py — config field
- Both `runner.run_step` call sites updated: `config.get("step_inactivity_timeout_seconds", config.get("step_timeout_seconds", 300))`.
- New field name: `step_inactivity_timeout_seconds`. Falls back to old `step_timeout_seconds` for backward compat.
- Default changed from 600 (wall-clock) to 300 (inactivity window).

## Design Notes
- **Why stderr matters:** `claude -p` outputs JSON to stdout only at the end. All tool calls, file edits, and bash output go to stderr. Activity monitoring watches both streams but stderr is where all mid-execution output appears.
- **Threading vs select:** Used `threading` for cross-platform compatibility. `select.select` on pipes has edge cases on macOS. Two daemon threads iterating `for line in stream` is clean and reliable.
- **`proc.kill()` not `proc.terminate()`:** SIGKILL ensures the child dies immediately. SIGTERM could be caught/ignored.

## Prompt Feedback
- Plan was clear and complete. The emphasis on stderr being the activity signal was critical context — without it the inactivity timer would fire immediately since stdout is silent until completion.
