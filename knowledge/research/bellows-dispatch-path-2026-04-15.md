# Phase 2 Diagnostic: Bellows Dispatch Path
**Date:** 2026-04-15 | **Type:** Read-only code investigation | **Phase:** 2 of 4

---

## Q1 — bellows.py End-to-End Structure

### File layout (395 lines)

**Module-level state:**
- `BELLOWS_ROOT` (line 16): resolved Path to bellows directory
- `DB_PATH` (line 17): absolute path to `bellows.db`

**Utility functions (lines 29–120):**
| Function | Lines | Purpose |
|----------|-------|---------|
| `load_config()` | 29–32 | Read `config.json` |
| `migrate_db()` | 35–66 | Ensure DB schema current; idempotent column adds |
| `load_file()` | 69–74 | Read file or return `""` |
| `extract_step_number()` | 77–81 | Parse `**Step:** N` from agent output |
| `extract_total_steps()` | 84–85 | Count `## STEP` headers in plan markdown |
| `record_run()` | 88–115 | INSERT one row into `runs` table |
| `is_final_step()` | 118–119 | `step >= total_steps` |
| `_is_plan_stranded()` | 122–123 | Check if in-progress file exists OR Done file missing |

**Core dispatch function (lines 126–229):**
- `run_plan(plan_path, config, response_server)` — the full lifecycle of a single plan:
  1. Load plan text, extract project path
  2. Determine if diagnostic (→ `total_steps = 1`) or executable
  3. Handle 0-step edge case (move to Done immediately)
  4. Build bootstrap prompt (diagnostic vs executable)
  5. Call `runner.run_step()` for step 1
  6. `record_run()` with `parsed["receipt_status"]`
  7. Loop: `while not is_final_step(current_step, total_steps)`: consult planner → run next step → record
  8. Post-loop strand check: if in-progress file exists OR Done file missing → STRANDED
  9. Otherwise → DONE notification

**Source SHA helper (lines 232–245):**
- `_source_sha()` — git log for startup banner

**Plan detection (lines 248–298):**
| Function/Class | Lines | Purpose |
|----------------|-------|---------|
| `is_runnable_plan()` | 248–251 | Regex: `(parallel-N-)?(executable\|diagnostic)-*.md`, excluding `in-progress-` |
| `extract_parallel_group()` | 254–256 | Extract `parallel-N` prefix or None |
| `PlanHandler` (FileSystemEventHandler) | 259–298 | Watchdog handler with `_seen` set, `_handle()` dispatch, `collect_group()` for parallel plans |

**Orchestrator class (lines 301–394):**
| Method | Lines | Purpose |
|--------|-------|---------|
| `__init__()` | 302–306 | Config, response server, `_active_lock` + `_active_count` |
| `_run_tracked()` | 308–316 | Increment count → `run_plan()` → decrement → check drain |
| `_check_queue_drain()` | 318–330 | If `_active_count == 0` and no pending plans → push notification |
| `handle_new_plan()` | 332–336 | Spawn daemon thread → `_run_tracked(path)`, 2s sleep stagger |
| `handle_parallel_group()` | 338–343 | Spawn N daemon threads with 2s stagger |
| `_rescan()` | 345–351 | Walk all watched dirs → `handler._handle()` for runnable plans |
| `start()` | 353–387 | Start server, observer, banner, startup scan, rescan loop (30s) |

### Dispatch path summary

```
Filesystem event / rescan
  → PlanHandler._handle(path)
    → is_runnable_plan(filename) check
    → extract_parallel_group(filename)
      → if parallel: collect_group() → Bellows.handle_parallel_group()
      → else: Bellows.handle_new_plan()
        → daemon Thread → _run_tracked(path) → run_plan(path, ...)
          → runner.run_step() [subprocess: claude -p]
          → record_run() [DB INSERT]
          → while loop (planner consult → next step)
          → strand check
          → DONE or STRANDED
```

### Shared mutable state
| State | Scope | Protection |
|-------|-------|-----------|
| `PlanHandler._seen` (set) | PlanHandler instance | **None** — accessed from main thread (rescan), observer thread (on_created/on_modified), and indirectly from `_rescan()` on main thread. No lock. |
| `Bellows._active_count` (int) | Bellows instance | `_active_lock` (threading.Lock) |
| `bellows.db` | Process-wide | SQLite internal locking (separate connections per call) |

---

## Q2 — Threading Model (f86f1a2)

### Literal diff

```diff
+import threading

# In Bellows class:
-    def handle_new_plan(self, path: str):
-        run_plan(path, self.config, self.response_server)
+    def handle_new_plan(self, path: str):
+        t = threading.Thread(target=run_plan, args=(path, self.config, self.response_server), daemon=True)
+        t.start()
+        print(f"Bellows: ▶ started {os.path.basename(path)}")

# Added _rescan method:
+    def _rescan(self, handler):
+        for decisions_path in self.config.get("watched_projects", []):
+            if os.path.isdir(decisions_path):
+                for fname in os.listdir(decisions_path):
+                    if is_runnable_plan(fname):
+                        full_path = os.path.join(decisions_path, fname)
+                        handler._handle(full_path)

# Added rescan loop in start():
+        rescan_interval = 30
+        last_rescan = time.time()
         try:
             while True:
                 time.sleep(1)
+                if time.time() - last_rescan >= rescan_interval:
+                    self._rescan(handler)
+                    last_rescan = time.time()

# Also added: diagnostic detection, print statements, _active_plans set (later replaced)
```

### Prose analysis

**Before f86f1a2:** `handle_new_plan()` called `run_plan()` synchronously, blocking the main loop. Only one plan could run at a time. No rescan existed.

**After f86f1a2:** Each plan gets its own **daemon thread**. `run_plan()` runs inside the thread. The main loop continues immediately and can dispatch more plans. A periodic rescan (30s) was added on the main thread.

**Thread model:** One thread per plan (not per step). All steps of a plan run sequentially within the same thread via the `while not is_final_step` loop.

**Shared state touched by threads:**
- `PlanHandler._seen` (set): read/written by `_handle()`, which is called from observer threads (watchdog), the main thread (rescan and startup scan), and indirectly from `handle_new_plan` threads. **No lock protects this set.** Python's GIL makes individual set operations atomic, but the read-then-write pattern in `_handle()` (check `path in self._seen` → `self._seen.add(path)`) is not atomic as a unit.
- `response_server`: accessed by all threads calling `wait_for_response()`. Only relevant during escalation.
- `bellows.db`: each `record_run()` call opens its own connection — thread-safe.

**Thread lifecycle:** Daemon threads are fire-and-forget. The main loop has no way to know when a thread completes except via `_active_count` (added later in c16e1d3). No join, no future, no callback.

---

## Q3 — Parallel Group Code (c16e1d3)

### Literal diff

```diff
+from typing import Optional

+def extract_parallel_group(filename: str) -> Optional[str]:
+    match = re.match(r"^(parallel-\d+)-", filename)
+    return match.group(1) if match else None

# PlanHandler additions:
+    def collect_group(self, decisions_path: str, group: str) -> list:
+        files = os.listdir(decisions_path)
+        result = []
+        for fname in files:
+            if fname.startswith(group + "-") and is_runnable_plan(fname):
+                full_path = os.path.join(decisions_path, fname)
+                if full_path not in self._seen:
+                    result.append(full_path)
+        return result

# _handle rewritten from if-block to early-return:
     def _handle(self, path: str):
         filename = os.path.basename(path)
-        if is_runnable_plan(filename) and path not in self._seen:
+        if not is_runnable_plan(filename) or path in self._seen:
+            return
+        group = extract_parallel_group(filename)
+        if group:
+            decisions_path = str(pathlib.Path(path).parent)
+            siblings = self.collect_group(decisions_path, group)
+            all_paths = [p for p in siblings if p not in self._seen]
+            [self._seen.add(p) for p in all_paths]
+            self.orchestrator.handle_parallel_group(all_paths)
+        else:
             self._seen.add(path)
             self.orchestrator.handle_new_plan(path)

# Bellows class additions:
-        self._active_plans: set = set()
+        self._active_lock = threading.Lock()
+        self._active_count = 0

+    def _run_tracked(self, path: str):
+        with self._active_lock:
+            self._active_count += 1
+        try:
+            run_plan(path, self.config, self.response_server)
+        finally:
+            with self._active_lock:
+                self._active_count -= 1
+            self._check_queue_drain()

+    def _check_queue_drain(self):
+        ...  # if _active_count == 0 and no pending → push notification

     def handle_new_plan(self, path: str):
-        t = threading.Thread(target=run_plan, args=(...))
+        t = threading.Thread(target=self._run_tracked, args=(path,), daemon=True)

+    def handle_parallel_group(self, paths: list):
+        threads = [threading.Thread(target=self._run_tracked, args=(p,), daemon=True) for p in paths]
+        [t.start() for t in threads]
```

### Prose analysis

**Detection:** When `_handle()` detects a `parallel-N-` prefix, it calls `collect_group()` to find all files with the same group prefix. All are added to `_seen` and dispatched together via `handle_parallel_group()`.

**Execution:** Each parallel plan gets its own daemon thread (same as solo plans). All threads start simultaneously (no stagger in original — stagger added later in d3daeec/fd75e76). Each thread runs `_run_tracked()` → `run_plan()` independently.

**Synchronization:**
- `_active_lock` + `_active_count`: tracks how many threads are running. When count hits 0, `_check_queue_drain()` fires.
- **No synchronization between parallel sibling plans.** Each runs independently. One sibling's completion doesn't affect another's detection or execution.
- `_seen` set: all parallel siblings are added to `_seen` atomically (list comprehension in `_handle`), so rescan won't re-dispatch them.

**Potential issue:** `collect_group()` reads `_seen` without holding a lock. If a rescan thread and an observer thread both call `_handle()` for different siblings of the same group near-simultaneously, `collect_group()` could return overlapping lists, causing double-dispatch. However, the `_seen.add()` before `handle_parallel_group()` mitigates this partially.

---

## Q4 — Six Bug-Fix Commits (Grouped)

### Individual summaries

| SHA | Date | What it tried to fix |
|-----|------|---------------------|
| **c7340a4** | Apr 14 11:53 | Rescan clears `_seen` for plans that exist on disk (so manually-reset plans get re-picked up). Added `handler._seen.discard(full_path)` in `_rescan()` when file exists on disk. |
| **be72e9e** | Apr 14 11:44 | Plans with 0 `## STEP` headers caused a crash (or infinite loop). Added early-exit: move to Done with Pushover notice. |
| **d3daeec** | Apr 14 13:11 | Double-execution race: rescan was clearing `_seen` during the 5-15s agent bootup window (file exists, no in-progress version yet), causing re-dispatch. Added: only clear from `_seen` if no in-progress version exists. Also added 2s stagger to `handle_new_plan`. |
| **5ac6ae2** | Apr 14 13:40 | `plan_dir` was referenced in the 0-step guard but assigned AFTER it, causing `NameError`. Moved `plan_dir`/`plan_filename`/`inprogress_path` assignment before the 0-step check. |
| **1cd47ab** | Apr 14 14:31 | `is_runnable_plan()` rejected `parallel-N-executable-*.md` filenames because it only accepted `executable-` or `diagnostic-` prefixes. Rewrote with regex: `^(parallel-\d+-)?(executable\|diagnostic)-.*\.md$`. |
| **fd75e76** | Apr 14 15:54 | Three fixes: (A) Added post-loop strand detection (`_is_plan_stranded()` helper). (B) Removed `_seen.discard` from `_rescan` entirely — the anti-race check from d3daeec still had a window during agent bootup. (C) Added 2s stagger to `handle_parallel_group()`. |

### Synthesis

These six patches address **three distinct failure regions:**

1. **`_seen` / rescan race** (c7340a4 → d3daeec → fd75e76 Bug B): Three successive attempts to get the rescan-vs-dispatch interaction right. c7340a4 added `_seen.discard()` to re-enable reset plans; d3daeec narrowed the condition to avoid the bootup window race; fd75e76 removed the discard entirely. This is one root cause (shared mutable `_seen` set accessed from multiple threads without locking) that took three tries to stabilize.

2. **Edge cases in `run_plan()`** (be72e9e, 5ac6ae2): 0-step plans and variable assignment ordering. These are independent bugs unrelated to the strand pattern — they cause crashes, not strands.

3. **Missing detection/filtering** (1cd47ab, fd75e76 Bug A): `is_runnable_plan` didn't accept parallel prefixes (invisible plans); no strand detection existed until fd75e76. These are detection-gap fixes, not root cause fixes.

**What the pattern reveals:** The `_seen` race is the only bug that was iterated on three times, suggesting it was the hardest to reason about. But none of these six commits fix the UNDERLYING cause of stranding — they either fix secondary bugs (crashes, detection gaps) or fix the rescan race (which caused double-dispatch, a different symptom). The strand itself — agent completing without moving to Done — is left unaddressed.

---

## Q5 — Status-Recording Code Path

### Where status is written

`record_run()` at lines 88–115:

```python
def record_run(
    db_path: str,
    plan_path: str,
    project: str,
    session_id: str,
    step: int,
    status: str,            # ← this becomes runs.status
    cost: float,
):
    conn = sqlite3.connect(db_path)
    # ... CREATE TABLE IF NOT EXISTS ...
    conn.execute(
        "INSERT INTO runs (timestamp, plan_path, project, session_id, step, status, cost) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (datetime.now().isoformat(), plan_path, project, session_id, step, status, cost),
    )
```

### Where status value comes from

Called at lines 169–173 and 212–216:

```python
record_run(
    db_path, plan_path, project_path,
    parsed.get("session_id", ""), current_step,
    parsed["receipt_status"], parsed["cost_usd"],    # ← receipt_status
)
```

`parsed["receipt_status"]` comes from `runner.run_step()` → `parser.parse()`.

### The bug: parser.py lines 14–19

```python
# parser.py:14-19
receipt_status = "Unknown"
for status in ("Complete", "Partial", "Blocked"):
    if f"**Status:** {status}" in result_text:
        receipt_status = status
        break
```

Where `result_text = raw.get("result", "")` — the agent's **final conversational text response** from `claude -p --output-format json`.

**Why it's always "Unknown":** The Output Receipt containing `**Status:** Complete` is written into a **deposited markdown file** (e.g., `bellows-strand-timeline-2026-04-15.md`), NOT into the agent's spoken conversational output. The `result` field in the JSON output captures the agent's last text message to the user, which is typically a summary like "I've completed Step 1 and committed the changes" — it does NOT contain the formatted `**Status:** Complete` string.

The parser is looking for the receipt in the wrong data source. Every run defaults to `"Unknown"` because the pattern is never matched in `result_text`.

**Note:** The timeout and exception paths in `runner.py:40-65` correctly return `receipt_status = "Blocked"`, but those paths are never reached in normal operation (all runs show "Unknown", not "Blocked", confirming the subprocess completes normally).

---

## Q6 — Strand-Detection Logic

### Code (bellows.py lines 122–123, 218–223)

```python
# Line 122-123: helper function
def _is_plan_stranded(inprogress_path: str, expected_done_path: str) -> bool:
    return os.path.exists(inprogress_path) or not os.path.exists(expected_done_path)
```

```python
# Lines 218-223: invoked after the step loop exits
expected_done_path = os.path.join(plan_dir, "Done", plan_filename)
if _is_plan_stranded(inprogress_path, expected_done_path):
    stranded_msg = f"{plan_name} reported step complete but plan file not in Done/"
    print(f"Bellows: ⚠️  STRANDED — {stranded_msg}")
    notifier.push(app_key, user_key, "Bellows — STRANDED Plan", stranded_msg)
    return
```

### When it runs

The strand check executes **once per plan, after the step loop completes** (after `while not is_final_step(...)` exits). It runs at the very end of `run_plan()`, before the DONE notification. It is:
- **Not polled** — runs exactly once
- **Not event-driven** — runs inline in the dispatch thread
- **Only on the final step** — the `while` loop must have exited (meaning all steps have been dispatched and returned)

### Trigger chain

```
run_plan() → runner.run_step() returns for final step
  → while loop condition False → exits loop
  → lines 218-223: strand check
  → if stranded: STRANDED notification + early return
  → else: DONE notification
```

### Variables involved

- `inprogress_path` = `{plan_dir}/in-progress-{plan_filename}` (line 150)
- `plan_filename` = `os.path.basename(plan_path)` = original filename WITHOUT `in-progress-` prefix (line 149)
- `expected_done_path` = `{plan_dir}/Done/{plan_filename}` (line 218)

### Timing relationship with threading

The strand check runs **inside the plan's daemon thread**, after the final `runner.run_step()` subprocess completes. It's not affected by other threads. However, it runs IMMEDIATELY after the subprocess returns — there's no delay to allow for filesystem propagation. Since the subprocess IS the agent, and the agent's `shutil.move` would have completed before the subprocess exits, this should not be a timing issue IF the agent actually executes the move.

### Assessment

The strand detection is **correctly catching real failures** — the agent subprocess has exited but the plan file was not moved to Done. This behavior should be preserved in Phase 4.

---

## Q7 — Root Cause Hypothesis

### Bug 1: "All runs Unknown status"

**Root cause: Parsing mismatch in `parser.py:14-19`.** The parser looks for `**Status:** Complete` in the agent's conversational output (`result_text` from the `result` field of `claude -p --output-format json`), but the Output Receipt containing this string is written into a deposited file, not into the agent's spoken response. The pattern is never matched, so all runs default to `"Unknown"`. This is independent of the stranding bug — it's a straightforward parsing error where the parser is searching the wrong data source.

**Fix direction (Phase 4):** Either (a) change the plan template to instruct agents to include `**Status:** Complete` in their final spoken message, or (b) have `run_plan()` read the deposited findings file after the subprocess returns and parse the status from there, or (c) infer status from `stop_reason` and the presence/absence of errors rather than relying on the agent to emit a specific string.

### Bug 2: Plan stranding

**Root cause: The agent subprocess (`claude -p`) completes without executing the move-to-Done instruction.** The strand check is correctly detecting a real condition. The question is why the agent doesn't complete all instructions.

**Most likely cause (ranked):**

1. **Agent early termination on single-step plans.** For diagnostic plans, `total_steps = 1` and the bootstrap prompt is: _"Execute it fully — this is a single-step investigation. Deposit your findings and report Complete when done."_ The plan itself contains substeps A through D (deposit → feedback → commit → move-to-Done). The agent may interpret "deposit your findings and report Complete" as its completion condition, stopping after substep A (findings deposit) without continuing to B, C, D. For multi-step executable plans, the final step similarly contains substeps ending with move-to-Done, and the agent may stop after the first deposit-like action. This matches the Phase 1 observation: _"the agent appears to be terminating after the first deposit-style action regardless of plan length."_

2. **No Bellows-side fallback for the move-to-Done.** Bellows delegates the ENTIRE plan lifecycle (including the move-to-Done) to the agent. If the agent fails to execute the move, Bellows has no mechanism to complete it. The strand check detects the failure but doesn't remediate it. A Bellows-side fallback that moves the plan to Done after verifying step completion would eliminate the strand entirely, regardless of agent behavior.

3. **Threading changed failure visibility, not failure rate.** Before f86f1a2, `run_plan()` ran synchronously and there was no strand check. Plans may have stranded in the synchronous model too, but it was invisible. The threading commit (f86f1a2) didn't introduce the strand — it just made the system capable of running more plans (and thus hitting the failure more often), while fd75e76 added the detection that made strands visible. The correlation between threading and strand visibility is coincidental timing, not causation.

**These two bugs are independent.** The "Unknown" status bug is a parsing error. The stranding bug is an agent-behavior issue compounded by Bellows having no fallback for the move-to-Done. Fixing the status parsing alone won't fix stranding, and vice versa.

---

## Output Receipt

- **Status:** Complete
- **Files Deposited:** `knowledge/research/bellows-dispatch-path-2026-04-15.md`
- **Files Created or Modified (Code):** `[]` (read-only investigation)
- **Decisions Made:** Root cause hypothesis in Q7 — stranding caused by agent early termination (not completing move-to-Done), compounded by no Bellows-side fallback. "Unknown" status caused by parser looking in wrong data source. Both bugs are independent.
- **Flags for CEO:** Phase 3 should reproduce both bugs independently:
  - For stranding: run a minimal diagnostic plan via `claude -p` and verify whether the agent completes the move-to-Done. If it doesn't, check the agent's output for where it stopped.
  - For "Unknown" status: inspect a recent log file in `logs/` to see what the `result` field actually contains, confirming the Output Receipt text is absent.
  - Phase 4 fix candidates: (a) Bellows-side move-to-Done fallback after strand detection, (b) parser fix to infer status from `stop_reason` or other signals, (c) bootstrap prompt rewording to emphasize move-to-Done as a hard requirement.
