# Resume Path + Pending Cleanup Diagnostic Findings
**Date:** 2026-04-16 | **Source plan:** diagnostic-resume-path-pending-cleanup-2026-04-16.md

## Summary

**Bug 1 (Resume):** CONFIRMED. `_consume_verdicts` calls `handle_new_plan(inprogress_path)` which re-enters `run_plan` from scratch. `run_plan` receives no step-number information and always builds a hardcoded "Execute Step 1 ONLY" bootstrap prompt for executable plans. Step N+1 never executes. Option B (add `resume_step` parameter to `run_plan`) is viable — `runner.run_step` already accepts a custom prompt; only 3 function signatures in the chain need optional parameters.

**Bug 2 (Pending cleanup):** CONFIRMED. `_consume_verdicts` never deletes or moves `verdicts/pending/verdict-request-{slug}-step-N.md`. The pending filename is reliably reconstructable from `plan_slug` + `step_number` already present in `_consume_verdicts`. No dangerous edge cases for cleanup at option (a). One important ancillary finding: `gates.py` reads from `verdicts/pending/` but for a DIFFERENTLY named file pattern — the agent self-request mechanism has two latent bugs (filename prefix mismatch + slug mismatch).

---

## Q1 — Resume Code Path Trace

**Call chain: `_consume_verdicts` → `handle_new_plan` → `_run_tracked` → `run_plan`**

### Step 1: `_consume_verdicts` (bellows.py lines 528–535)

For `continue` verdict on non-final step:

```python
# bellows.py lines 529–535
else:
    verdict.log_to_ledger(full_plan_path, step_number, gate_result, v, reason)
    inprogress_name = f"in-progress-{original_name}"
    inprogress_path = os.path.join(decisions_path, inprogress_name)
    shutil.move(full_plan_path, inprogress_path)
    print(f"Bellows: verdict continue — resuming {original_name}")
    # Dispatch next step
    self.handle_new_plan(inprogress_path)
```

`handle_new_plan` receives only `inprogress_path` — no step number, no custom prompt.

### Step 2: `handle_new_plan` (bellows.py lines 454–458)

```python
def handle_new_plan(self, path: str):
    t = threading.Thread(target=self._run_tracked, args=(path,), daemon=True)
    t.start()
    ...
```

Passes only `path` to `_run_tracked`.

### Step 3: `_run_tracked` (bellows.py lines 430–437)

```python
def _run_tracked(self, path: str):
    with self._active_lock:
        self._active_count += 1
    try:
        run_plan(path, self.config, self.response_server)
```

Calls `run_plan` with path only — no step context.

### Step 4: `run_plan` bootstrap prompt construction (bellows.py lines 153–172)

```python
is_diagnostic = os.path.basename(plan_path).startswith("diagnostic-")
...
if is_diagnostic:
    bootstrap_prompt = f"Read the diagnostic at {plan_path}. Execute it fully..."
else:
    bootstrap_prompt = f"Read the plan at {plan_path}. Execute Step 1 ONLY. After completing Step 1, STOP and wait for my confirmation before proceeding to Step 2."
```

When called with `inprogress_path` (e.g., `in-progress-executable-foo-2026-04-16.md`):
- `os.path.basename(plan_path).startswith("diagnostic-")` → **False** (basename starts with `in-progress-`)
- The `else` branch fires unconditionally
- **Bootstrap prompt is always: "Execute Step 1 ONLY"**

**CONFIRMED.** `run_plan` receives no information about which step to resume from. Step N+1 never executes on resume. The plan re-runs from Step 1.

---

## Q2 — What Happens to Step 1 Code Changes on Re-Run

When the plan resumes and re-runs Step 1:

1. `run_plan` builds the bootstrap prompt with no `session_id` (first call in `run_plan`, line 177–178):
   ```python
   parsed = runner.run_step(bootstrap_prompt, project_path, config["default_model"],
                             timeout=config.get("step_timeout_seconds", 600))
   ```
   `session_id` defaults to `None` — the agent starts a completely fresh Claude session with no memory of the original Step 1.

2. The agent re-reads the plan and re-executes Step 1. If Step 1 originally wrote or modified code that was already committed:
   - **No-op outcome (likely):** Agent finds files already match the intended state, makes no edits, commits nothing. This is the most common outcome for well-specified steps.
   - **Duplicate commit (possible):** Agent re-writes files (possibly identical content) and creates a new commit — producing a duplicate history entry.
   - **Conflict (unlikely):** Agent tries to create a file that already exists with different content (e.g., from a prior agent's partial work), triggering a merge conflict. No automatic protection against this — `run_plan` captures no pre-existing state before the re-run.

There is no guard in `run_plan` or `_consume_verdicts` to detect "this step was already completed." The `bellows.db` records each run but nothing reads it to prevent re-execution.

---

## Q3 — Viability of Option B

### (a) Does `run_plan` accept a custom bootstrap prompt?

**No.** The bootstrap prompt is constructed internally at lines 169–172. Signature:
```python
def run_plan(plan_path: str, config: dict, response_server: server.ResponseServer):
```
No prompt parameter exists.

### (b) Does `runner.run_step` accept a custom prompt?

**Yes.** Signature (runner.py lines 24–31):
```python
def run_step(
    prompt: str,
    project_path: str,
    model: str,
    session_id: Optional[str] = None,
    allowed_tools: str = "Read,Edit,Write,Bash",
    timeout: int = 600,
) -> dict:
```
`prompt` is the first positional parameter and is fully caller-controlled. The prompt is passed directly to `claude -p {prompt}`.

### (c) Minimal signature change to thread a resume prompt through

The full dispatch chain: `_consume_verdicts` → `handle_new_plan` → `_run_tracked` → `run_plan` → `runner.run_step`.

`runner.run_step` needs **no change**.

The Planner's proposed `handle_resume(path, prompt)` approach is viable. Minimum changes required:

1. **`run_plan`**: add `resume_step: Optional[int] = None`
   - If `resume_step` is set, build `bootstrap_prompt = f"Read the plan at {plan_path}. Execute Step {resume_step}."`
   - Existing Step 1 default behavior unchanged when `resume_step=None`

2. **`_run_tracked`**: add `resume_step: Optional[int] = None`, pass through to `run_plan`

3. **`handle_new_plan`** (or a new `handle_resume`): accept and pass `resume_step`

4. **`_consume_verdicts`**: call `self.handle_new_plan(inprogress_path, resume_step=step_number + 1)` instead of the bare call

**Option B is viable and recommended.** Adding `resume_step: Optional[int] = None` to `run_plan` and threading it down is the minimal, non-breaking change. `runner.run_step` already accepts a fully custom prompt — the only wiring needed is through 3 calling functions. No new method is strictly required, though a `handle_resume` alias is reasonable for clarity.

---

## Q4 — Pending File Accumulation Confirmation

**CONFIRMED.** `_consume_verdicts` does NOT delete or move the pending request file.

Full accounting of file operations in `_consume_verdicts`:

**`continue` to Done (lines 518–527):**
```python
done_path = os.path.join(done_dir, original_name)
shutil.move(full_plan_path, done_path)      # moves verdict-pending-plan → Done/plan
```

**`continue` to next step (lines 529–535):**
```python
shutil.move(full_plan_path, inprogress_path)  # moves verdict-pending-plan → in-progress-plan
self.handle_new_plan(inprogress_path)
```

**`stop` (lines 537–543):**
```python
shutil.move(full_plan_path, halted_path)      # moves verdict-pending-plan → halted-plan
```

**After all branches (lines 545–547):**
```python
processed_path = resolved_dir / f"processed-{fname}"
shutil.move(str(resolved_dir / fname), str(processed_path))   # moves resolved verdict → processed-
```

In ALL branches: only the plan file and the resolved verdict file are moved. `verdicts/pending/verdict-request-{slug}-step-{N}.md` is **never touched**.

---

## Q5 — Cleanest Cleanup Location and Filename Reliability

**Filename pattern:** `verdict-request-{slug}-step-{step_number}.md`

This is reliably reconstructable from the values already present in `_consume_verdicts`:
- `plan_slug` = parsed from verdict filename via `re.match(r"^verdict-(.+)-step-(\d+)\.md$", fname).group(1)` (line 489–492)
- `step_number` = `int(match.group(2))` (line 493)

**Consistency verification:**

`post_verdict_request` builds the slug via `_slug_from_path(plan_path)` (verdict.py lines 13–23), which strips all of `("in-progress-", "verdict-pending-", "executable-", "diagnostic-")` from the basename in sequence.

Example: `plan_path` = `.../in-progress-executable-foo-2026-04-16.md`
- Strip `in-progress-` → `executable-foo-2026-04-16.md`
- Strip `executable-` → `foo-2026-04-16.md`
- Strip `.md` → `foo-2026-04-16`
- Pending file written: `verdict-request-foo-2026-04-16-step-N.md`

The Planner files a verdict named `verdict-foo-2026-04-16-step-N.md`. `_consume_verdicts` parses `plan_slug = "foo-2026-04-16"`. Reconstructed pending filename: `verdict-request-foo-2026-04-16-step-N.md` ✓

**The naming is consistent and reliable.** Cleanup code in `_consume_verdicts`:

```python
pending_file = BELLOWS_ROOT / "verdicts" / "pending" / f"verdict-request-{plan_slug}-step-{step_number}.md"
if pending_file.exists():
    pending_file.unlink()
```

This should be placed after the per-verdict branching logic (continue-to-done / continue-to-step / stop) and before or after the `processed_path` shutil.move. Either order is safe.

---

## Q6 — Edge Cases for Pending File Deletion

### Who reads `verdicts/pending/`?

**`_consume_verdicts` itself:** No — it only scans `verdicts/resolved/`.

**`check_verdict` (verdict.py lines 79–100):** No — reads only from `verdicts/resolved/`.

**`notifier.py`:** No — takes arguments directly, makes no file reads.

**`gates.py` (`_verdict_requested`, lines 30–48): YES — but for a DIFFERENT filename pattern.**

`gates.py` reads from `verdicts/pending/` to detect agent-deposited verdict requests:
```python
# gates.py line 44
request_file = os.path.join(VERDICT_REQUEST_DIR, f"request-{slug}-step-{step_number}.md")
```

This looks for `request-{slug}-step-N.md` (no `verdict-` prefix).

`verdict.post_verdict_request()` writes `verdict-request-{slug}-step-N.md` (with `verdict-` prefix).

**These filenames do NOT match.** The two file types are distinct:
- `verdicts/pending/verdict-request-{slug}-step-N.md` — written by Bellows for the Planner's review (what we want to clean up)
- `verdicts/pending/request-{slug}-step-N.md` — what gates.py looks for (intended to be written by the executing agent to signal a self-requested pause)

Additionally, `gates.py`'s slug derivation differs from `verdict.py`'s: `_verdict_requested` strips `("in-progress-", "verdict-pending-", "halted-")` but NOT `("executable-", "diagnostic-")`, so for `in-progress-executable-foo.md` it produces slug `executable-foo` instead of `foo`. **The agent self-request mechanism is currently non-functional due to two bugs: filename prefix mismatch (`request-` vs `verdict-request-`) and slug mismatch (`executable-` prefix retained by gates.py but stripped by verdict.py).**

This does NOT affect the cleanup of `verdict-request-*` files. Deleting `verdict-request-{slug}-step-N.md` files in `_consume_verdicts` is safe and will not interfere with `gates.py`.

### Timing safety

The cleanup runs only after `_consume_verdicts` has found a resolved verdict and acted on it. By definition, the Planner already read the pending file before writing the resolved verdict. The pending file's purpose is exhausted.

### Crash/partial-processing edge case

If Bellows crashes after acting on the verdict but before deleting the pending file, the pending file survives as an orphan. On the next rescan, the resolved verdict has already been moved to `processed-`, so `_consume_verdicts` won't find it again and won't retry the cleanup. The orphan pending file is harmless — the Planner ignores files whose corresponding resolved verdicts have been consumed.

### Step-number uniqueness

Each `verdict-request-{slug}-step-N.md` is unique per slug + step number. Cleanup of step N's pending file cannot affect a pending file for step N+1 or a different plan. No collision risk.

**Conclusion: no dangerous edge cases. Option (a) is safe.**

---

## Ancillary Finding: Agent Self-Request Mechanism is Non-Functional

The `gates.py` `_verdict_requested` check (lines 30–48) is intended to allow the executing agent to deposit a verdict-request file during a step, triggering a pause. Two bugs make this non-functional:

1. **Filename mismatch:** `gates.py` looks for `request-{slug}-step-N.md`; there is no code path that creates this file. `verdict.py` creates `verdict-request-{slug}-step-N.md` — different prefix.

2. **Slug mismatch:** `gates.py` builds the slug without stripping `executable-`/`diagnostic-` prefixes, while `verdict.py` does strip them. For any `executable-` plan, the slugs differ.

The gate result key `verdict_requested.requested` in `gates.check()` is always `False` in production (no file ever matches the pattern). The `agent_verdict_request` pause_reason code path in `run_plan` is unreachable.

This is a separate fix from the two bugs in scope for this diagnostic — flagged here as context.

---

## Output Receipt

| Field | Value |
|---|---|
| Status | Complete |
| Questions answered | Q1, Q2, Q3, Q4, Q5, Q6 |
| Findings file | knowledge/research/resume-path-pending-cleanup-diagnostic-2026-04-16.md |
| Fixes implemented | No — diagnostic only, per plan instructions |
| Bug 1 (resume) confirmed | Yes — always Step 1 bootstrap, step_number never threaded through call chain |
| Bug 2 (pending cleanup) confirmed | Yes — no deletion in any branch of `_consume_verdicts` |
| Option B viability | Yes — `runner.run_step` already accepts custom prompt; 3 calling-function signatures need optional `resume_step` parameter |
| Ancillary finding | Agent self-request verdict mechanism non-functional (filename + slug mismatch in gates.py vs verdict.py) |
