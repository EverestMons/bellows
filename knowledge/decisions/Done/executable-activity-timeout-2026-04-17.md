# bellows — Activity-Based Timeout (Runner Rewrite)
**Date:** 2026-04-17 | **Type:** Executable | **Priority:** 4 | **Depends on:** `executable-shadow-copy-cache-2026-04-17.md` | **Execution:** Step 1 (DEV) → Step 2 (QA)

## How to Run This Plan

**Bootstrap:** `Read the plan at bellows/knowledge/decisions/executable-activity-timeout-2026-04-17.md. Execute Step 1 ONLY. After completing Step 1, STOP and wait for my confirmation. Do NOT proceed to Step 2 or move the plan to Done.`

## Context

Diagnostic at `knowledge/research/runner-subprocess-2026-04-17.md` confirmed: `runner.py` uses `subprocess.run` (blocking, all-at-once capture, wall-clock timeout). No visibility into agent activity mid-step. Agents get killed at the timeout even when actively working. The fix: replace `subprocess.run` with `subprocess.Popen` + streaming read loop with an inactivity timer. Config field `step_timeout_seconds` becomes the inactivity window (kill after N seconds of silence), not a wall-clock cap.

---
---

## STEP 1 — DEV

---

> **FIRST — claim this plan:** `import shutil; shutil.move("bellows/knowledge/decisions/executable-activity-timeout-2026-04-17.md", "bellows/knowledge/decisions/in-progress-executable-activity-timeout-2026-04-17.md")`. Read `bellows/runner.py` in full. Read the diagnostic at `bellows/knowledge/research/runner-subprocess-2026-04-17.md`. **Single commit. One file: `runner.py`.**
>
> Rewrite `run_step` to use `subprocess.Popen` with activity-based timeout: **(a)** Replace `subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)` with `subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, cwd=project_path)`. **(b)** Create a streaming read loop. Use `select.select` (Unix) or `threading` to read stdout and stderr concurrently without blocking. On each chunk of output received, reset an inactivity timer. Accumulate all output into a buffer for downstream JSON parsing. **(c)** The inactivity timer: initialize to `timeout` seconds (from config `step_timeout_seconds`, default 300). Each time stdout or stderr produces output, reset the timer. If the timer expires (no output for `timeout` seconds), kill the process via `proc.kill()`, capture whatever output was accumulated, and return the timeout error dict. **(d)** Print a heartbeat to Bellows stdout every 60 seconds showing the elapsed time and last-output-age: `Bellows: runner — {elapsed}s elapsed, last output {age}s ago`. This gives the CEO visibility into whether the agent is active. **(e)** On normal completion (process exits with code 0): parse `result_stdout` as JSON same as before. On non-zero exit: capture stderr, return error dict. On inactivity timeout: return the same timeout error dict as today but include `stderr_partial` from the accumulated buffer (the current code leaves this empty). **(f)** The `timeout` parameter semantics change: it was wall-clock max, now it's inactivity window. Rename the config field from `step_timeout_seconds` to `step_inactivity_timeout_seconds` for clarity. Support both field names for backward compat (check new name first, fall back to old). Update `bellows.py` where it reads the config to use the new name. **(g)** Add a hard wall-clock cap as a safety net: `max_wall_clock = timeout * 10` (e.g. 300s inactivity → 3000s max wall clock). This prevents a pathological case where the agent outputs one byte every 299 seconds and runs forever. Print a warning if the wall-clock cap is hit: `Bellows: runner — hard wall-clock cap reached ({max_wall_clock}s), killing process`.
>
> **Important:** the `claude -p` command outputs JSON to stdout ONLY at the end (the final response). During execution, stdout may be empty — all visible "progress" from Claude Code goes to stderr (tool calls, file edits, bash output). So the activity monitoring must watch STDERR, not just stdout. Stdout will be silent until the very end. Verify this by checking the diagnostic's Q2 findings about capture behavior.
>
> Commit: `feat: activity-based inactivity timeout — replace subprocess.run with Popen streaming`. **Deposit dev log** to `bellows/knowledge/development/activity-timeout-2026-04-17.md`. Standard prompt feedback protocol.
>
> **STOP. Do NOT proceed to Step 2. Do NOT move the plan to Done. Wait for CEO confirmation before continuing.**

---
---

## STEP 2 — QA

---

> Before starting, read `bellows/knowledge/development/activity-timeout-2026-04-17.md` and check Output Receipt. If not Complete, stop. **Verification.** (a) `runner.py` — grep for `Popen` (replaces `subprocess.run`). Grep for `select` or `threading` (concurrent read). Grep for `inactivity` or `last_output` (timer reset logic). Grep for `proc.kill` (timeout kill). Grep for `stderr_partial` (partial capture on timeout). (b) `bellows.py` — grep for `step_inactivity_timeout_seconds` (new config field name). (c) Verify backward compat: confirm code checks both `step_inactivity_timeout_seconds` and `step_timeout_seconds` from config. (d) Verify hard wall-clock cap exists. Pipe evidence to `bellows/knowledge/qa/evidence/executable-activity-timeout-2026-04-17/grep_deliverables.txt`. **Deposit QA report** to `bellows/knowledge/qa/activity-timeout-qa-2026-04-17.md`.
>
> **Rule 20 Self-Check:**
> ```python
> import os, sys
> plan_slug = "executable-activity-timeout-2026-04-17"
> qa_report_path = "bellows/knowledge/qa/activity-timeout-qa-2026-04-17.md"
> evidence_dir = f"bellows/knowledge/qa/evidence/{plan_slug}/"
> required_evidence_files = ["grep_deliverables.txt"]
> hedging_keywords = ["pending", "inferred", "extrapolated", "estimated", "approximate", "skipped", "assumed", "close enough", "should pass", "would pass", "not run"]
> POSITIVE_STATUS_TOKENS = ["✅", "OK", "PASS", "[x]", "done", "complete", "verified"]
> def is_positive_row(line):
>     if "|" not in line: return False
>     cells = [c.strip() for c in line.split("|")]
>     for cell in cells:
>         for token in POSITIVE_STATUS_TOKENS:
>             if token == "✅":
>                 if "✅" in cell: return True
>             else:
>                 if cell.lower() == token.lower(): return True
>     return False
> failures = []
> if not os.path.isdir(evidence_dir):
>     failures.append(f"CRITICAL: evidence folder missing: {evidence_dir}")
> else:
>     for fname in required_evidence_files:
>         fpath = os.path.join(evidence_dir, fname)
>         if not os.path.isfile(fpath): failures.append(f"CRITICAL: evidence file missing: {fpath}")
>         elif os.path.getsize(fpath) == 0: failures.append(f"CRITICAL: evidence file empty: {fpath}")
> if os.path.isfile(qa_report_path):
>     with open(qa_report_path, "r") as f: report = f.read()
>     for line in report.splitlines():
>         if is_positive_row(line):
>             lower = line.lower()
>             for kw in hedging_keywords:
>                 if kw in lower: failures.append(f"CRITICAL: hedging keyword '{kw}' in positive-status row: {line.strip()[:120]}"); break
> else:
>     failures.append(f"CRITICAL: QA report not found at {qa_report_path}")
> print("=" * 60)
> if failures:
>     print(f"FAILED — {len(failures)} issue(s):")
>     for f in failures: print(f"  - {f}")
>     sys.exit(1)
> else:
>     print("PASSED — all evidence present, no hedging.")
> ```
>
> If FAILS, STOP. If PASSES: move to Done. Commit: `chore: move activity-timeout to Done`. Standard prompt feedback protocol.
>
> **STOP. Do NOT proceed further. Wait for CEO confirmation.**
