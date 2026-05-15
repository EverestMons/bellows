# Bellows — Rescan Duplicate Runs Race Diagnostic
**Date:** 2026-04-16 | **Status:** Complete

---

## Q1 — `_seen` Set Lifecycle

### (a) When is a path added to `_seen`?

In `_handle` (bellows.py:390–405):

- **Single plans** — line 403: `self._seen.add(path)` called **before** `self.orchestrator.handle_new_plan(path)`
- **Parallel group plans** — lines 398–399: `all_paths = [p for p in siblings if p not in self._seen]` then `[self._seen.add(p) for p in all_paths]` called **before** `self.orchestrator.handle_parallel_group(all_paths)`

Both cases: `_seen` is updated before dispatch, so a second `_handle` call for the same path is always blocked.

### (b) Does `_seen` persist across rescans, or is it reset?

`_seen` is an **instance variable** of `PlanHandler` (line 378: `self._seen = set()`), initialized once in `__init__`. It is **never reset or cleared** in the current code. It persists for the entire Bellows process lifetime. It is cleared only on **Bellows process restart**.

Historical note: commit `c7340a4` ("rescan clears _seen for reset plans") introduced logic to clear `_seen` entries for plans moved back to runnable state. This was later removed (current code has no `_seen` clearing in `_rescan`).

### (c) Does `_consume_verdicts` add the new `in-progress-` path to `_seen`?

**No.** `_consume_verdicts` calls `self.handle_new_plan(inprogress_path, resume_step=step_number + 1)` directly (line 528). `handle_new_plan` (line 447) merely starts a daemon thread — it does **not** add to `_seen`.

However, this gap does **not** create a protection problem because `is_runnable_plan("in-progress-executable-foo.md")` returns `False` (see Q5b). The directory scan in `_rescan` won't pick up the `in-progress-` file regardless.

### (d) Is `Done/` ever scanned?

**No.** `_rescan` iterates over `watched_projects` entries (direct `decisions/` paths) with a flat `os.listdir` — no recursive traversal. The watchdog is scheduled with `recursive=False` (line 552). `Done/` is a subdirectory and is **never scanned** by either mechanism.

---

## Q2 — Rescan vs Verdict-Consumption Race

### (a) Ordering in `_rescan`

```python
def _rescan(self, handler):
    self._consume_verdicts()          # FIRST — process resolved verdicts
    for decisions_path in ...:        # SECOND — scan directories
        for fname in os.listdir(decisions_path):
            if is_runnable_plan(fname):
                handler._handle(full_path)
```
`_consume_verdicts` always runs before the directory scan within the same `_rescan` tick.

### (b) If `_consume_verdicts` moves `verdict-pending-X` → `Done/X`, can the directory scan find it?

**No.** The file is moved to `Done/` which is a subdirectory not in `watched_projects`. The `os.listdir(decisions_path)` call sees only direct children of `decisions_path`. The `Done/X` file is invisible to the scan.

### (c) If `_consume_verdicts` moves `verdict-pending-X` → `in-progress-X` and calls `handle_new_plan`, then the directory scan runs:

Protected by **`is_runnable_plan`**, not by `_seen`. `is_runnable_plan("in-progress-executable-foo.md")` returns `False` (see Q5b) — `_handle` returns immediately at line 392 before even checking `_seen`.

**However**: if the agent never claimed the original plan (i.e., `decisions/original-plan-X.md` still exists because the claim shutil.move used the wrong path), the directory scan would find the unclaimed original. At that point, `_seen` IS the protection:
- If `_seen` contains the original path → filtered, no re-dispatch
- If `_seen` does NOT contain the original path (Bellows restarted) → **duplicate dispatch**

---

## Q3 — Watchdog `on_created`/`on_modified` Path

### (a) Does `shutil.move(verdict-pending → in-progress)` trigger watchdog events?

**Yes.** On the same filesystem, `shutil.move` is a rename. The watchdog fires `on_created` for the new `in-progress-` path and `on_deleted` for the old `verdict-pending-` path.

### (b) Does `_handle` pick up `in-progress-X` as a new plan?

**No.** `_handle` line 392: `if not is_runnable_plan(filename) or path in self._seen: return`. `is_runnable_plan("in-progress-executable-foo.md")` returns `False` (checked first) → immediate return. The watchdog event is a no-op.

### (c) Does `_seen` protect against watchdog re-dispatch?

`_seen` protection is **not needed** here — `is_runnable_plan` is the gating check and it runs first. The watchdog cannot cause a duplicate dispatch for `in-progress-` or `verdict-pending-` prefixed files.

---

## Q4 — Concrete Cases

### Approach A viability diagnostic (`diagnostic-forge-approach-a-viability-2026-04-16.md`)

**DB query result:**
```
forge/knowledge/decisions/diagnostic-forge-approach-a-viability-2026-04-16.md | 1 | Complete     | 2026-04-16T12:42:48.556002
forge/knowledge/decisions/diagnostic-forge-approach-a-viability-2026-04-16.md | 1 | VerdictPending | 2026-04-16T12:42:48.894751
```

The DB shows **exactly one run** (step 1 Complete immediately followed by VerdictPending — normal for a diagnostic with `auto_close` defaulting to false). The `Done/` folder contains `diagnostic-forge-approach-a-viability-2026-04-16.md`, confirming successful verdict resolution. **No duplicate run appears in the DB.**

Possible explanations for the observed duplicate:
1. **Bellows restart with orphan original**: The original file stayed in `decisions/` (agent claim instruction used a wrong path). After the verdict moved `verdict-pending-` to Done, the orphan remained. On a Bellows restart, `_seen` cleared and the orphan was re-dispatched. The second run was killed or aborted before the DB write completed — leaving no trace in the DB.
2. **Multi-chunk write race**: The Planner's write process deposited a second copy of the plan file mid-session (the "orphan files" described in the plan context). The original was in `_seen`, but the second copy at the same path string was also blocked by `_seen`... unless a restart occurred in between.

The DB evidence is insufficient to confirm which mechanism triggered the specific duplicate. The most likely root cause is **Bellows restart clearing `_seen` while an unclaimed orphan original remained in `decisions/`**.

### Notifier timeout plan (`executable-bellows-notifier-timeout-2026-04-16.md`)

**DB query result:**
```
bellows/knowledge/decisions/executable-bellows-notifier-timeout-2026-04-16.md | 1 | Complete     | 2026-04-16T14:12:43.011735
bellows/knowledge/decisions/executable-bellows-notifier-timeout-2026-04-16.md | 2 | Complete     | 2026-04-16T14:14:03.523497
bellows/knowledge/decisions/executable-bellows-notifier-timeout-2026-04-16.md | 2 | VerdictPending | 2026-04-16T14:14:03.841314
```

Again, **exactly one run** in the DB (steps 1 and 2, with VerdictPending on step 2). The file is in `Done/`. Git status shows `D knowledge/decisions/in-progress-executable-bellows-notifier-timeout-2026-04-16.md` — this `in-progress-` file was previously committed to git (an operational file that shouldn't be tracked), and was subsequently deleted as part of the `8cca078` resume-path-pending-cleanup fix. **No duplicate run in DB.**

Same diagnosis as approach-a: the duplicate was likely triggered by a Bellows restart while an orphan file existed, with the second run aborted before DB recording.

### Historical pattern — `in-progress-` files in DB (before `8cca078`)

The DB contains entries like:
```
in-progress-parallel-1-executable-verdict-readme-2026-04-16.md | 1 | Complete | 11:14:40
in-progress-parallel-1-executable-parse-diff-stat-fix-2026-04-16.md | 1 | Complete | 11:15:44
```

These occurred at 11:14–11:15, BEFORE the `8cca078` ("resume from correct step") fix was applied at ~11:38. In the pre-fix code, `_consume_verdicts` called `handle_new_plan(inprogress_path)` WITHOUT a `resume_step` argument. `run_plan` therefore used `current_step = 1` and the bootstrap prompt said "Execute Step 1." This explains why these runs recorded step=1 instead of step=2.

After `8cca078`, `_consume_verdicts` correctly passes `resume_step=step_number+1`, confirmed by:
```
in-progress-parallel-1-executable-forge-evaluation-annotation-2026-04-16.md | 2 | Complete | 12:23:28
```

---

## Q5 — Proposed Fixes

### (a) Should `_consume_verdicts` add `in-progress-` path to `_seen`?

**Low value.** The `in-progress-` path is already blocked from re-dispatch by `is_runnable_plan` returning `False`. Adding it to `_seen` would provide redundant protection for the watchdog path, but the watchdog is also already blocked. Not recommended — adds complexity without fixing the real problem.

### (b) `is_runnable_plan` return values (current code, line 363–366)

```python
def is_runnable_plan(filename: str) -> bool:
    if filename.startswith("in-progress-") or filename.startswith("verdict-pending-") or filename.startswith("halted-"):
        return False
    return bool(re.match(r"^(parallel-\d+-)?(executable|diagnostic)-.*\.md$", filename))
```

- `is_runnable_plan("in-progress-executable-foo.md")` → **False** (startswith check)
- `is_runnable_plan("verdict-pending-executable-foo.md")` → **False** (startswith check)
- `is_runnable_plan("in-progress-parallel-1-executable-foo.md")` → **False** (startswith check)

The current code correctly guards all three prefixes. These filters are the primary protection against watchdog/rescan re-dispatch of already-active plans.

### (c) Should the watchdog be paused during `_consume_verdicts` file moves?

**Not needed.** `is_runnable_plan` already blocks `in-progress-` and `verdict-pending-` prefixed files from all dispatch paths (watchdog and rescan). Pausing the watchdog would add complexity for zero benefit.

### (d) Root cause and fix recommendation

**Root cause:**
The duplicate dispatch requires two conditions simultaneously:
1. **Orphan unclaimed original** — the original plan file stays in `decisions/` because the agent's claim instruction used a wrong path (e.g., `diagnostic-foo.md` instead of `parallel-1-diagnostic-foo.md` for plans with the `parallel-1-` prefix, or any path mismatch). Bellows's `run_plan` never explicitly moves the original — it only moves `inprogress_path` (which the agent was supposed to create).
2. **Bellows restart** — clears `_seen`, so the orphan original is no longer filtered.

**Fix options (ranked by reliability):**

**Fix 1 (RECOMMENDED — most robust):** Move the original plan to `in-progress-` in Bellows BEFORE calling the runner.

At the start of `run_plan`, add:
```python
shutil.move(plan_path, inprogress_path)
plan_path = inprogress_path  # update all downstream references
```

This eliminates the orphan completely. The original disappears from `decisions/` before the agent runs. If Bellows restarts, the startup scan finds `in-progress-*` which `is_runnable_plan` returns `False` for — no re-dispatch. The agent's claim instruction becomes a no-op (file already claimed), which is harmless.

**Fix 2:** Persist `_seen` across restarts in bellows.db. On startup, reload from DB. Moderate complexity — needs schema change and care around stale entries.

**Fix 3:** At startup, skip plans where a corresponding `Done/` or `verdict-pending-` version exists. Handles orphans after restart without schema changes. Lower complexity than Fix 2. Doesn't handle the case where both `Done/` version and orphan original exist with the same name.

**Fix 4:** Fix plan templates to use the correct filename in claim instructions. Purely operational — unreliable, depends on every plan being correct.

**Verdict on Fix 1:** Bellows claiming the plan at `run_plan` entry is the architecturally correct design. The agent should never need to claim the plan file — that's a Bellows orchestration responsibility. Fix 1 eliminates the entire class of orphan-original duplicate-dispatch bugs.

---

## Summary

| Question | Finding |
|---|---|
| Q1a | `_seen` populated in `_handle` before dispatch (line 399/403) |
| Q1b | `_seen` persists for process lifetime; cleared on restart only |
| Q1c | `in-progress-` path NOT added to `_seen` by `_consume_verdicts`; harmless because `is_runnable_plan` blocks it |
| Q1d | `Done/` never scanned (not in `watched_projects`, watchdog non-recursive) |
| Q2a | `_consume_verdicts` runs FIRST in `_rescan`, then directory scan |
| Q2b | `Done/` unreachable by directory scan |
| Q2c | `is_runnable_plan` (not `_seen`) blocks `in-progress-` re-dispatch; orphan original blocked by `_seen` while Bellows runs |
| Q3a | `shutil.move` triggers `on_created` for `in-progress-` via watchdog |
| Q3b | `is_runnable_plan` returns False → `_handle` no-ops immediately |
| Q3c | `_seen` not needed; `is_runnable_plan` is the guard |
| Q4 | DB shows only one run for each case; duplicate likely triggered by restart + orphan; root cause is Bellows not claiming files |
| Q5 | Best fix: Bellows moves original to `in-progress-` at `run_plan` entry before calling runner |
