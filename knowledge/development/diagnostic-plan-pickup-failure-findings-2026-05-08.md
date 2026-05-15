# Diagnostic: Plan Pickup Failure — Findings

**Date:** 2026-05-08 | **Investigator:** Bellows Developer Agent | **Plan:** diagnostic-plan-pickup-failure-2026-05-08

---

## Q1 — Rescan Code Path Reconstruction

### `is_runnable_plan()` — `bellows.py:706-709`

```python
def is_runnable_plan(filename: str) -> bool:
    if filename.startswith("in-progress-") or filename.startswith("verdict-pending-") or filename.startswith("halted-"):
        return False
    return bool(re.match(r"^(parallel-\d+-)?(executable|diagnostic)-.*\.md$", filename))
```

This is the sole dispatch eligibility filter. A filename must:
1. NOT start with a lifecycle prefix (`in-progress-`, `verdict-pending-`, `halted-`)
2. Match the regex `^(parallel-\d+-)?(executable|diagnostic)-.*\.md$` — only `executable-` and `diagnostic-` prefixes (optionally preceded by `parallel-N-`) are dispatched.

Files that fail either check are silently skipped — no log line is emitted.

### `PlanHandler._handle()` — `bellows.py:734-762`

Called by `on_created`, `on_modified`, `on_moved` filesystem events and by `_rescan`. Checks:
1. `path_parent` must be in `watched_projects` (line 737-738)
2. `is_runnable_plan(filename)` must return True AND `path` must not be in `self._seen` (line 740)
3. If parallel-group prefixed, defers to settle-window logic (lines 743-758)
4. Otherwise, adds to `_seen` and dispatches via `orchestrator.handle_new_plan(path)` (lines 759-762)

### `_rescan()` — `bellows.py:840-861`

Runs every 30 seconds. First consumes verdicts, then dispatches settled parallel groups, then iterates all watched directories calling `handler._handle(full_path, from_rescan=True)` for each file passing `is_runnable_plan()`.

### Startup scan — `bellows.py:1061-1067`

One-time scan at startup. Same logic: iterates watched directories, calls `handler._handle(full_path)` for each file passing `is_runnable_plan()`.

### (a) Filename prefix filter

**Dispatched:** `executable-`, `diagnostic-` (optionally with `parallel-N-` prefix)
**Skipped by lifecycle check:** `in-progress-`, `verdict-pending-`, `halted-`
**Silently rejected by regex:** everything else — `qa-`, `roadmap-`, `_staging-`, or any non-standard prefix. No log line emitted on rejection.

### (b) Deduplication / memoization

`PlanHandler._seen` (line 721) is a `set` keyed on full file paths. Entries are added on dispatch and NEVER removed for the lifetime of the daemon process. This means a plan returned to its original path after halt-and-rename requires a daemon restart to be re-dispatched. (Documented in BACKLOG 2026-05-06 entry.)

### (c) Log lines on pickup vs skip

**Pickup:** `"Bellows: ▶ started {filename}"` at `bellows.py:831` (inside `handle_new_plan`), preceded by `"Bellows: detected plan {filename}"` at line 761 (inside `_handle`).
**Skip:** No log line whatsoever. The `is_runnable_plan()` check at line 740 returns False and execution silently returns.

---

## Q2 — Root Cause Confirmed: `qa-` Prefix Not in Dispatch Whitelist

**Definitive answer: `qa-` is NOT in the dispatched prefix list.**

The regex at `bellows.py:709`:
```
^(parallel-\d+-)?(executable|diagnostic)-.*\.md$
```

Only matches filenames starting with `executable-` or `diagnostic-` (with optional `parallel-N-` prefix). The deposited plan filename `qa-action-queue-limit-and-contract-name-2026-05-08.md` starts with `qa-`, which does not match the regex. `is_runnable_plan("qa-action-queue-limit-and-contract-name-2026-05-08.md")` returns `False`.

**This is the root cause.** The plan was silently rejected at filter time on every rescan tick. Bellows was functioning correctly per its own filter rules — the `qa-` prefix is simply not recognized. The defect has two facets:

1. **Missing prefix:** If the Planner is expected to deposit `qa-` prefixed plans for Bellows dispatch, the prefix must be added to the whitelist.
2. **Silent rejection:** Regardless of whether `qa-` should be dispatched, the complete absence of logging on rejection is a usability defect. A freshly-deposited `.md` file in a watched `decisions/` directory that isn't dispatched should produce a visible "skipped: reason" log line.

**Q3 skipped** — Q2 confirmed the hypothesis; no alternate hypotheses needed.

---

## Q4 — Bellows Log Audit

### Most recent 3 log files by mtime:

| File | Timestamp | Size |
|------|-----------|------|
| `20260508-122328-step.json` | 2026-05-08 12:42 | 1.2 MB |
| `20260508-115159-step.json` | 2026-05-08 12:23 | 1.7 MB |
| `20260508-114222-step.json` | 2026-05-08 11:46 | 1.5 MB |

### Slug search results:

Grepped all 2026-05-08 log files for `action-queue-limit-and-contract-name`:
- **20260508-115159-step.json** — match in `raw_output` field, worktree path: `invoice-pulse/.bellows-worktrees/action-queue-limit-and-contract-name-2026-05-08`. This is the **executable** plan (Step 1).
- **20260508-122328-step.json** — same worktree path. This is the **executable** plan (Step 2).
- **20260508-114222-step.json** — different slug: `action-queue-200-and-contract-code-2026-05-08`. Unrelated plan.

**All three log files predate the daemon restart at ~13:51.** No log files exist after 12:42 on 2026-05-08. Bellows never logged seeing the `qa-action-queue-limit-and-contract-name-2026-05-08.md` plan filename — confirming silent-skip at filter time, not a downstream failure.

---

## Q5 — Frequency Check

### Bellows step executions per day (step log files):

| Date | Steps |
|------|-------|
| 2026-04-14 | 64 |
| 2026-04-15 | 15 |
| 2026-04-16 | 87 |
| 2026-04-17 | 54 |
| 2026-04-18 | 56 |
| 2026-04-19 | 98 |
| 2026-04-20 | 3 |
| 2026-04-21 | 10 |
| 2026-04-22 | 6 |
| 2026-04-23 | 35 |
| 2026-04-24 | 13 |
| 2026-04-28 | 23 |
| 2026-04-30 | 14 |
| 2026-05-01 | 52 |
| 2026-05-02 | 2 |
| 2026-05-03 | 21 |
| 2026-05-04 | 9 |
| 2026-05-05 | 24 |
| 2026-05-06 | 33 |
| 2026-05-07 | 13 |
| 2026-05-08 | 3 |
| **Total** | **~635** |

### Done plans per project:

| Project | Done Plans |
|---------|-----------|
| invoice-pulse | 593 |
| bellows | 173 |
| forge | 104 |
| study | 84 |
| BrewBuddy | 43 |
| anvil | 29 |
| SimpleScreen | 22 |
| freight-kb | 9 |
| ai-career-digest | 8 |
| **Total** | **~1,065** |

### Interpretation:

The disparity (1,065 Done plans vs ~635 step log files) is NOT evidence of systematic skipping. Many Done plans predate Bellows (the system was not running from day 1), multi-step plans generate multiple log files per plan, some Done plans were manually executed and moved, and diagnostic plans often have a single step. The `qa-` prefix issue is **the first known occurrence** of a plan deposited with an unrecognized prefix. Prior to today, all Planner-deposited plans used `executable-` or `diagnostic-` prefixes. The `qa-` prefix appears to be a novel Planner convention for QA-only re-verification plans. This is a one-off attributable to a new prefix convention, not a systemic silent-skip pattern — but it will recur every time the Planner uses `qa-` (or any other non-whitelisted prefix).

---

## Q6 — Fix Shape

**Recommended: both (a) and (b).**

### (a) Add `qa-` to dispatch prefix whitelist — 1-line fix

At `bellows.py:709`, change the regex from:
```python
return bool(re.match(r"^(parallel-\d+-)?(executable|diagnostic)-.*\.md$", filename))
```
to:
```python
return bool(re.match(r"^(parallel-\d+-)?(executable|diagnostic|qa)-.*\.md$", filename))
```

**LOC: 1.** Also consider whether `roadmap-` should be added — the diagnostic prompt mentioned it as a "typically dispatched" prefix, but it is also NOT in the current whitelist.

### (b) Add rejection logging for silent skips — ~5-8 LOC

In `PlanHandler._handle()` around line 740, after the `is_runnable_plan()` check, add a log line for `.md` files in watched directories that fail the filter but aren't lifecycle-prefixed (to avoid spamming on `in-progress-`, `verdict-pending-`, `halted-` files which are expected to fail):

```python
if not is_runnable_plan(filename):
    if (filename.endswith(".md")
        and not filename.startswith(("in-progress-", "verdict-pending-", "halted-"))
        and path not in self._seen):
        print(f"Bellows: ⚠️  skipped {filename} — prefix not in dispatch whitelist")
    return
```

**LOC: ~5-8.** This ensures any future prefix mismatch produces a visible log line rather than silent non-action.

### Total recommended fix: ~6-9 LOC + unit tests

---

## Secondary Observations

### S1 — Plan filename remained `in-progress-qa-...md` after agent paused

**Consistent with non-pickup.** The `in-progress-` rename is performed by `run_plan()` at `bellows.py:252-253`:
```python
if not plan_filename.startswith("in-progress-"):
    shutil.move(plan_path, inprogress_path)
```
Since `is_runnable_plan()` rejected the file at line 709, `run_plan()` was never invoked. The file was never claimed by Bellows. The `in-progress-` prefix observed by the CEO was likely added by the manually-launched Claude Code agent (which would have been told to "claim" the plan per standard bootstrap prompt conventions), not by Bellows.

### S2 — Step 2 auto-advance without verdict pause

Relevant code: the while-loop at `bellows.py:343-375`. After Step 1 completes, Bellows checks `gate_result["is_qa_step"]` (line 346) to decide whether to pause. If `gates.check()` does not flag the **current** step's output as containing a QA checkpoint signal, Bellows auto-advances to the next step. The `is_qa_step` detection logic lives in `gates.py` — if Step 2 was the QA step but the Step 1 gate check didn't detect a QA signal in Step 1's output, Bellows would proceed. This is a separate investigation target.

### S3 — Verdict-resolved retry loop targeting plan in Done/

Relevant code: `bellows.py:1011-1012`:
```python
print(f"Bellows: ⚠️  no verdict-pending plan found for {plan_slug} step {step_number} — leaving in resolved/ for retry")
```
This fires when: (1) a verdict file exists in `resolved/`, (2) no matching `verdict-pending-` plan is found in any watched directory, AND (3) the stale-verdict check at lines 997-1010 (`plan_slug in dname` scan of Done/ directories) fails to match. If the plan was manually moved to Done/ but the slug-substring match at line 925/1002 doesn't hit (e.g., naming variation), the verdict stays in `resolved/` and the message repeats every 30-second rescan. The ~12 minutes of retry corresponds to ~24 rescan cycles.

---

## Output Receipt: Complete
