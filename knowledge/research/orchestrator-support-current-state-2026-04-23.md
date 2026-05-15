# Orchestrator Support — Current State Findings

**Date:** 2026-04-23 | **Plan:** diagnostic-orchestrator-support-current-state-2026-04-23

---

## Q1 — Dispatch State Machine

### (a) Plan-file states

| State | Filename Pattern | Setter (file:line) | Reader (file:line) | Exit Transitions |
|---|---|---|---|---|
| Runnable (executable) | `executable-*.md` | Planner (external — deposits file to `knowledge/decisions/`) | `bellows.py:452-455` (`is_runnable_plan`) | Claimed → `in-progress-*` via `shutil.move` at `bellows.py:222` |
| Runnable (diagnostic) | `diagnostic-*.md` | Planner (external) | `bellows.py:452-455` (`is_runnable_plan`) | Claimed → `in-progress-*` via `shutil.move` at `bellows.py:222` |
| Runnable (parallel) | `parallel-N-executable-*.md` or `parallel-N-diagnostic-*.md` | Planner (external) | `bellows.py:452-455` (`is_runnable_plan`), `bellows.py:458-459` (`extract_parallel_group`) | Claimed → `in-progress-*` via `shutil.move` at `bellows.py:222` (inside `run_plan`, same path as non-parallel) |
| In-progress | `in-progress-*.md` | `bellows.py:222` (`shutil.move` inside `run_plan`) | `bellows.py:453` (`is_runnable_plan` rejects), `bellows.py:734` (startup active-slug scan) | → `verdict-pending-*` at `bellows.py:296` or `bellows.py:354`; → `Done/` at `bellows.py:376`; → `Done/` at `bellows.py:233` (0-step skip) |
| Verdict-pending | `verdict-pending-*.md` | `bellows.py:294-296` (mid-plan pause), `bellows.py:352-354` (final-step pause) | `bellows.py:453` (`is_runnable_plan` rejects), `bellows.py:649` (`_consume_verdicts` scan), `bellows.py:734` (startup active-slug scan) | → `in-progress-*` at `bellows.py:687` (continue verdict, not final step); → `Done/` at `bellows.py:678` (continue verdict, final step); → `halted-*` at `bellows.py:696` (stop verdict) |
| Halted | `halted-*.md` | `bellows.py:693-696` (`_consume_verdicts`, stop verdict) | `bellows.py:453` (`is_runnable_plan` rejects) | No automated exit — manual CEO intervention only |
| Done | Files in `Done/` subdirectory | `bellows.py:233` (0-step skip), `bellows.py:376` (auto-close), `bellows.py:678` (continue-to-done verdict) | `bellows.py:743-747` (startup active-slug scan for orphan cleanup) | Terminal state — no automated exit |

### (b) State transition ownership

| State | Owner | Documented or Inferred |
|---|---|---|
| Runnable → In-progress | Bellows daemon (`run_plan` at `bellows.py:222`) | Inferred from code |
| In-progress → Verdict-pending | Bellows daemon (`run_plan` at `bellows.py:294-296`, `bellows.py:352-354`) | Inferred from code |
| In-progress → Done (auto-close) | Bellows daemon (`run_plan` at `bellows.py:370-377`) | Inferred from code |
| In-progress → Done (0-step skip) | Bellows daemon (`run_plan` at `bellows.py:233`) | Inferred from code |
| Verdict-pending → In-progress (resume) | Bellows daemon (`_consume_verdicts` at `bellows.py:687`) | Inferred from code |
| Verdict-pending → Done (continue-to-done) | Bellows daemon (`_consume_verdicts` at `bellows.py:678`) | Inferred from code |
| Verdict-pending → Halted | Bellows daemon (`_consume_verdicts` at `bellows.py:693-696`) | Inferred from code |
| Halted → (any) | CEO via manual filesystem operation | Inferred (no code path transitions out of halted) |
| New plan deposited (Runnable) | Planner via filesystem (external to Bellows) | Documented in CLAUDE.md ("Plans deposited by the Planner") |
| Verdict deposited (triggers transitions out of verdict-pending) | Planner/CEO via filesystem — writes `verdicts/resolved/verdict-{slug}-step-{N}.md` | Inferred from `_consume_verdicts` at `bellows.py:597-710` |

### (c) Filesystem watcher setup — `is_runnable_plan` verbatim

From `bellows.py:452-455`:

```python
def is_runnable_plan(filename: str) -> bool:
    if filename.startswith("in-progress-") or filename.startswith("verdict-pending-") or filename.startswith("halted-"):
        return False
    return bool(re.match(r"^(parallel-\d+-)?(executable|diagnostic)-.*\.md$", filename))
```

**Allowlist regex:** `^(parallel-\d+-)?(executable|diagnostic)-.*\.md$`

**Dispatch-dedup logic:** `PlanHandler._seen` set at `bellows.py:467`. Each dispatched path is added to `_seen` at `bellows.py:502` (parallel group) or `bellows.py:506` (single plan). The `_handle` method checks `path in self._seen` at `bellows.py:486` and returns early if already seen. Additionally, `_handle` at `bellows.py:481-484` checks that `path_parent` is in `watched_projects` to prevent subdirectory dispatch (e.g., `Done/`).

**Watcher setup** at `bellows.py:714-717`:
```python
observer = Observer()
handler = PlanHandler(self)
for decisions_path in self.config.get("watched_projects", []):
    observer.schedule(handler, decisions_path, recursive=False)
```

**Parallel group deferred dispatch:** `_pending_groups` dict at `bellows.py:468` tracks `group prefix → first-seen timestamp`. On initial detection (`from_rescan=False`), parallel plans are deferred (`bellows.py:491-493`). The `_rescan` method at `bellows.py:574-589` dispatches groups that have passed a 5-second settle window.

---

## Q2 — Gate Evaluation Boundary

### (a) Gate names and signatures

All gates are in `gates.py`. There are 8 gates total:

| # | Gate Name | Signature (verbatim) | Location |
|---|---|---|---|
| 1 | `_gate_receipt_status` | `def _gate_receipt_status(parsed, failures):` | `gates.py:81` |
| 2 | `_gate_ceo_flags` | `def _gate_ceo_flags(parsed, failures):` | `gates.py:87` |
| 3 | `_gate_no_errors` | `def _gate_no_errors(parsed, failures):` | `gates.py:93` |
| 4 | `_gate_no_permission_denials` | `def _gate_no_permission_denials(parsed, failures):` | `gates.py:101` |
| 5 | `_gate_deposit_exists` | `def _gate_deposit_exists(parsed, failures, project_path, plan_text=None, step_number=None):` | `gates.py:128` |
| 6 | `_gate_is_qa_step` | `def _gate_is_qa_step(plan_text, step_number):` | `gates.py:202` |
| 7 | `_gate_file_change_audit` | `def _gate_file_change_audit(files_changed):` | `gates.py:210` |
| 8 | `_gate_scope_check` | `def _gate_scope_check(plan_text, step_number, files_changed, failures):` | `gates.py:216` |

Public entry point: `def check(parsed, plan_text, step_number, project_path, files_changed=None):` at `gates.py:31`

### (b) When gates run relative to step execution lifecycle

Gates run **after agent completion**, once per step. The call site is in `bellows.py`. Two invocation points:

**First step** — `bellows.py:268`:
```python
gate_result = gates.check(parsed, plan_text, current_step, project_path, files_changed=files_changed)
```
This runs after the initial `runner.run_step()` returns at `bellows.py:252-254`.

**Subsequent steps** — `bellows.py:326`:
```python
gate_result = gates.check(parsed, plan_text, current_step, project_path, files_changed=files_changed)
```
This runs after each subsequent `runner.run_step()` returns at `bellows.py:308-313`.

**Lifecycle position:** Per-step, after agent completion, before the continue/pause decision. Gates never run before agent dispatch. Gates run once per step (not per-plan).

### (c) Gate result data model

The return type is a plain `dict`, defined in the docstring at `gates.py:31-42`:

```python
def check(parsed, plan_text, step_number, project_path, files_changed=None):
    """Run all gates and return a result dict.

    Returns:
        {
            "passed": bool,       # True only if zero failures from gates 1-5, 8
            "failures": [{"gate": str, "evidence": str}, ...],
            "is_qa_step": bool,
            "files_changed": list,
            "plan_header": dict,
            "verdict_requested": {"requested": bool, "body": str|None},
        }
    """
```

Constructed at `gates.py:71-78`:
```python
return {
    "passed": len(failures) == 0,
    "failures": failures,
    "is_qa_step": is_qa_step,
    "files_changed": files_changed,
    "plan_header": header,
    "verdict_requested": {"requested": requested, "body": request_body},
}
```

### (d) Where gate failures persist

1. **Verdict request files** — `verdicts/pending/verdict-request-{slug}-step-{N}.md`. Posted by `verdict.post_verdict_request()` at `verdict.py:78-139`. Contains `Gate Result Passed` field and a `## Gate Failures` section listing each failure's gate name and evidence.

2. **Ledger** — `verdicts/ledger.jsonl`. Written by `verdict.log_to_ledger()` at `verdict.py:166-183`. Each JSON line contains `gate_failures` and `files_changed` arrays.

3. **DB** — `bellows.db` `runs` table. Records `status` (receipt status, not gate results directly) at `bellows.py:259-263` and `bellows.py:297-298`. Gate results are NOT stored in the DB — only receipt status.

4. **Log files** — `logs/{timestamp}-step.json`. Written by `runner._write_log()` at `runner.py:234-239`. Contains full parsed output but not gate results directly. Gate results are not written to log files.

### (e) Gate independence / sequentiality

Gates are **independent and all run unconditionally**. From `gates.py:49-64`:

```python
# Gate 1: receipt status
_gate_receipt_status(parsed, failures)
# Gate 2: CEO flags
_gate_ceo_flags(parsed, failures)
# Gate 3: no errors
_gate_no_errors(parsed, failures)
# Gate 4: no permission denials
_gate_no_permission_denials(parsed, failures)
# Gate 5: deposit exists
_gate_deposit_exists(parsed, failures, project_path, plan_text=plan_text, step_number=step_number)
# Gate 6: QA step detection (informational)
is_qa_step = _gate_is_qa_step(plan_text, step_number)
# Gate 7: file change audit (informational)
_gate_file_change_audit(files_changed)
# Gate 8: scope check
_gate_scope_check(plan_text, step_number, files_changed, failures)
```

All 8 gates run sequentially in code order. If gate N fails (appends to `failures`), all subsequent gates still run. There is no short-circuit. The `passed` field is computed at the end: `len(failures) == 0`. Gates 6 and 7 are informational — they do not append to `failures`.

---

## Q3 — Agent Dispatch Mechanics

### (a) `claude -p` invocation site

From `runner.py:25-38`:

```python
def run_step(
    prompt: str,
    project_path: str,
    model: str,
    session_id: Optional[str] = None,
    allowed_tools: str = "Read,Edit,Write,Bash",
    timeout: int = 300,
) -> dict:
    cmd = [
        "claude", "-p", prompt,
        "--output-format", "json",
        "--model", model,
        "--allowedTools", allowed_tools,
    ]
    if session_id is not None:
        cmd += ["--resume", session_id]
```

**Arguments passed:** prompt text, `--output-format json`, `--model` (from plan header or config default), `--allowedTools` (default: `Read,Edit,Write,Bash`), optionally `--resume` with a session ID for multi-step continuation.

**Working directory:** `project_path` — set via `cwd=project_path` at `runner.py:54`:
```python
proc = subprocess.Popen(
    cmd,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
    cwd=project_path,
)
```

**Environment:** Inherited from Bellows's process environment (no explicit `env` parameter passed to `Popen`).

### (b) Agent completion detection

**Process exit detection.** Bellows polls `proc.poll()` in a 1-second loop at `runner.py:100`:

```python
while proc.poll() is None:
    time.sleep(1)
```

Completion is detected when `proc.poll()` returns non-None (process exited). Additionally, two timeout mechanisms kill the process:

1. **Inactivity timeout** — `runner.py:114-117`: kills process after `timeout` seconds with no stdout/stderr output.
2. **Wall-clock cap** — `runner.py:121-125`: kills process after `timeout * 10` seconds regardless of activity.

**Streaming reader threads** (`runner.py:81-93`) monitor stdout and stderr in background threads, updating `last_output_time` on each line received.

### (c) Data flow from agent to Bellows

1. **Stdout capture** — `runner.py:132`: `result_stdout = "".join(stdout_buf)`. The entire stdout is captured.

2. **JSON parsing** — `runner.py:188-189`: stdout is parsed as JSON (`json.loads(result_stdout)`).

3. **Structured output parsing** — `runner.py:211-212`: the JSON is passed to `parser.parse(raw)` which extracts:
   - `session_id` — for session resumption
   - `receipt_status` — inferred from `stop_reason` (`parser.py:15-22`)
   - `cost_usd` — from `total_cost_usd` field
   - `result_text` — the agent's text output
   - `ceo_flags` — extracted from `### Flags for CEO` section in result text (`parser.py:29-36`)
   - `verdict_requested` — extracted from `VERDICT_REQUESTED:` marker in result text (`parser.py:39-42`)
   - `permission_denials` — from raw JSON
   - `is_error`, `stop_reason`, `escalate`

4. **Files on disk** — Bellows reads `git diff --stat` before and after each step (`bellows.py:250-251`, `bellows.py:266-267`) to detect files changed by the agent. No other disk-based output is read from the agent.

5. **Stderr capture** — `runner.py:133`: `result_stderr = "".join(stderr_buf)`. Logged but not parsed for structured data.

### (d) Step progress communication

There is **no real-time notion of "I finished step 1, waiting for verdict"** communicated by the agent during execution. Step progress is entirely **inferred by Bellows after agent exit**:

- `bellows.py:256`: `current_step = resume_step if resume_step is not None else 1` — Bellows tracks the step number internally.
- `bellows.py:314`: `current_step += 1` — Bellows increments after each `runner.run_step()` call.
- The agent's output receipt may contain a step number (`parser.py` checks for `**Step:** N` in `bellows.py:80-83` via `extract_step_number`), but this is not used for progression logic — only for DB recording.

The "finished step 1, waiting for verdict" state is created by Bellows renaming the file to `verdict-pending-*` at `bellows.py:294-296`. The "finished all steps, moved to Done" state is created by Bellows moving the file to `Done/` at `bellows.py:370-376`. Both are filesystem state transitions made by Bellows after the agent returns, not by the agent itself.

The agent is dispatched for one step at a time. Bellows's while-loop (`bellows.py:274-327`) decides whether to dispatch the next step based on gate results, not on any agent signal.

---

## Q4 — Extension Points for Orchestrator Plans

### (a) Plan-to-plan references

**`**Depends on:**` field parsing:** No match found. Searched all `.py` files for `Depends on`, `depends_on`, `depends on` — no code parses this field. The field exists in some plan files (found in `knowledge/decisions/Done/executable-activity-timeout-2026-04-17.md` and `knowledge/decisions/Done/executable-verdict-request-pause-reason-2026-04-16.md`) but is **not read by any Bellows code**. It is documentation-only with no dispatch behavior.

**`parallel-N-` group coordination:** Plans in the same parallel group share **only the group prefix string** for dispatch coordination. They share no runtime state — each runs in its own thread (`bellows.py:567-572`), each gets its own `run_plan` call, each has independent gate evaluation. There is no shared dispatch state, no inter-plan communication, no barrier synchronization, and no dependency ordering within a group.

**`before-*`/`after-*` relationships:** No match found. Searched all `.py` files — no code references `before-` or `after-` prefixed plans. No such mechanism exists.

**Summary:** No plan-to-plan reference mechanism is currently parsed or acted upon by Bellows.

### (b) Parallel-group dispatch code path

**`extract_parallel_group`** at `bellows.py:458-460`:
```python
def extract_parallel_group(filename: str) -> Optional[str]:
    match = re.match(r"^(parallel-\d+)-", filename)
    return match.group(1) if match else None
```

**`PlanHandler._handle`** at `bellows.py:488-504` (parallel branch):
```python
group = extract_parallel_group(filename)
if group:
    if not from_rescan:
        if group not in self._pending_groups:
            self._pending_groups[group] = time.time()
        return
    if group in self._pending_groups:
        return
    decisions_path = str(pathlib.Path(path).parent)
    siblings = self.collect_group(decisions_path, group)
    all_paths = [p for p in siblings if p not in self._seen]
    [self._seen.add(p) for p in all_paths]
    print(f"Bellows: parallel group {group} — {len(all_paths)} plans")
    self.orchestrator.handle_parallel_group(all_paths)
```

**`_rescan` parallel dispatch** at `bellows.py:579-589` (settle window):
```python
for group in list(handler._pending_groups.keys()):
    if now - handler._pending_groups[group] > 5:
        for decisions_path in self.config.get("watched_projects", []):
            if os.path.isdir(decisions_path):
                siblings = handler.collect_group(decisions_path, group)
                if siblings:
                    all_paths = [p for p in siblings if p not in handler._seen]
                    [handler._seen.add(p) for p in all_paths]
                    print(f"Bellows: parallel group {group} — {len(all_paths)} plans (deferred dispatch)")
                    self.handle_parallel_group(all_paths)
        del handler._pending_groups[group]
```

**`handle_parallel_group`** at `bellows.py:567-572`:
```python
def handle_parallel_group(self, paths: list):
    threads = [threading.Thread(target=self._run_tracked, args=(p,), daemon=True) for p in paths]
    for t in threads:
        t.start()
        time.sleep(2)
    print(f"Bellows: ▶ started {len(threads)} parallel threads")
```

**Dispatch model:** Bellows runs parallel-group plans **concurrently** (one thread per plan, staggered by 2 seconds). The Planner deposits all plans with the same `parallel-N-` prefix, and Bellows collects them after a 5-second settle window, then spawns threads for all. No sequencing within a group.

### (c) Structural support for parent-spawns-child primitive

**What would work:** A plan step could invoke `shutil.move` (or any filesystem operation) to place a child plan file into a watched `decisions/` directory with an `executable-*` or `diagnostic-*` filename. Bellows's `_rescan` loop (`bellows.py:590-595`) runs every 30 seconds and calls `_handle` on any new runnable plan found in the watched directories. The child plan would be picked up on the next rescan cycle.

**What would fail:**
1. **No parent-child lifecycle coupling.** The parent plan has no way to wait for the child to complete. The parent's step would finish, gates would evaluate, and the parent would advance to its next step (or close) independently of the child. There is no "block until child completes" primitive.
2. **No return-value channel.** Child plan results (findings, gate results, verdict outcomes) have no mechanism to flow back to the parent. The parent would need to poll the filesystem for the child's `Done/` or `verdict-pending-*` state, which is not supported in any current step execution model.
3. **Dedup risk.** If the parent deposits the child plan during a step, and the step is retried (e.g., after a verdict-pending → resume cycle), the child plan may already exist (in `in-progress-*`, `Done/`, etc.), causing a `shutil.move` failure or duplicate dispatch.
4. **`_seen` set is in-memory only.** If Bellows restarts, the parent's `_seen` entry is lost, but the child's lifecycle state persists on disk — no structural conflict, but the parent cannot track whether it already spawned the child.

**Net assessment:** Spawning works mechanically. Coordination (waiting, result collection, lifecycle coupling) does not exist.

### (d) Where an orchestrator-plan abstraction would land

**Smallest change surface options:**

1. **New module (e.g., `orchestrator.py`):** Would own parent-child plan relationships, dependency tracking, and barrier synchronization. The `_rescan` loop in `bellows.py` would delegate to this module for plans with an orchestrator marker (e.g., `orchestrator-*` prefix or a plan header field like `type: orchestrator`). Estimated touch points: `bellows.py` (dispatch routing in `_rescan` and `_handle`), new `orchestrator.py` module, possibly `gates.py` (orchestrator-specific gates or gate exemptions).

2. **Extension to `bellows.py`:** Add orchestrator state to the `Bellows` class — a registry of active orchestrator plans, their child plan slugs, and completion barriers. The `_consume_verdicts` and `_check_queue_drain` methods would check orchestrator state before transitioning parents. Heavier change surface in `bellows.py` but avoids a new module.

3. **New gate type:** A gate that checks "all child plans are in Done/" before allowing the parent to advance. Would require `gates.py` to accept a plan dependency manifest and perform filesystem checks. Smallest code change but limited — only handles the "wait for children" case, not spawning or result collection.

4. **Cross-cutting changes:** All three of the above, plus changes to `verdict.py` (orchestrator-aware verdict requests), `parser.py` (child-plan output aggregation), and the plan file format (dependency declarations).

**Recommendation for smallest viable surface:** Option 1 (new module) + minimal routing changes in `bellows.py:_handle` and `bellows.py:_rescan`. The existing `parallel-N-` group mechanism in `PlanHandler` is the closest structural analogue but lacks lifecycle coupling, making it insufficient as a base.

### (e) Backlog items related to orchestrator concepts

Scanned `knowledge/BACKLOG.md` for: `orchestrator`, `parent plan`, `child plan`, `cross-plan`, `plan-to-plan`, `depends on`, `dependency`, `spawn`, `multi-plan`, `coordination`.

| Search Term | Match? | Details |
|---|---|---|
| `orchestrator` | No match | — |
| `parent plan` | No match | — |
| `child plan` | No match | — |
| `cross-plan` | No match | (Note: `cross-project-verdict-queue` exists in research but not in BACKLOG) |
| `plan-to-plan` | No match | — |
| `depends on` | No match | — |
| `dependency` | No match | — |
| `spawn` | No match | — |
| `multi-plan` | No match | — |
| `coordination` | No match | — |

**Related items (indirect):**

1. BACKLOG open item "Planner↔Bellows integration protocol underdefined" (2026-04-18) — touches on the need to define how plans interact with Bellows's state machine, which is prerequisite to orchestrator support. Quote: *"Do NOT document the Bellows integration protocol in PLANNER_TEMPLATE.md until the step-persistence and watcher-reliability items above are resolved."*

2. BACKLOG open item "verdict mechanization" (2026-04-18) — proposes Bellows running Rule 22 checks mechanically. Quote: *"Target: Bellows runs these checks mechanically and auto-transitions on clean pass; Planner is summoned only when validation can't decide."* This is Layer 1 self-sufficiency infrastructure that an orchestrator would build on.

3. BACKLOG open item "step state lost across re-claim" (2026-04-18) — step persistence is a prerequisite for reliable orchestrator-plan lifecycle management. Without it, orchestrator plans cannot track which child steps have completed across Bellows restarts.

**Net assessment:** No backlog items directly address orchestrator or plan-to-plan coordination. Three items are structural prerequisites.

---

## Output Receipt

- **Agent:** Bellows Developer (Claude Code)
- **Step:** 1
- **Status:** Complete
- **What Was Done:** Read-only audit of Bellows dispatch architecture across `bellows.py`, `gates.py`, `runner.py`, `verdict.py`, `parser.py`, and `knowledge/BACKLOG.md`. Answered Q1 (dispatch state machine — 7 states, 10 transitions, ownership table, `is_runnable_plan` verbatim), Q2 (8 gates, all independent, post-completion per-step, dict return type, persistence locations), Q3 (agent dispatch via `claude -p` subprocess, process-exit detection with inactivity/wall-clock timeout, JSON+parser structured output, no real-time step progress), Q4 (no plan-to-plan references exist, parallel groups run concurrently with no lifecycle coupling, child-spawn mechanically works but coordination does not, new module is smallest viable surface, no direct backlog items but three prerequisites identified).
- **Files Deposited:** `bellows/knowledge/research/orchestrator-support-current-state-2026-04-23.md`
- **Files Created or Modified (Code):** None
- **Decisions Made:** None
- **Flags for CEO:** None
- **Flags for Next Step:** N/A (single-step diagnostic)
