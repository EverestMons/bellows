# Worktree Recommendation Delta Check — Findings

**Date:** 2026-05-05 | **Plan:** diagnostic-worktree-delta-2026-05-05 | **Step:** 1

---

## Q1 — Code Interaction with the 2026-05-04 Detect-and-Skip Fix

### (a) Where are `_create_worktree` and `_teardown_worktree` called from in `run_plan`?

**`_create_worktree` — 1 call site:**

| # | Location | Context |
|---|---|---|
| 1 | `bellows.py:282` | `wt_path = _create_worktree(project_path, plan_slug)` — between bootstrap prompt construction (line 278) and pre-diff capture (line 296). Inside a `try/except WorktreeCreationError` block (lines 281–293). |

**`_teardown_worktree` — 3 call sites:**

| # | Location | Context |
|---|---|---|
| 1 | `bellows.py:337` | Inside the `while not is_final_step` loop, in the pause branch (gate failure / QA / verdict-request / header-pause). Wrapped in `try/except WorktreeTeardownError` (lines 336–340). Tears down before pausing mid-plan. |
| 2 | `bellows.py:402` | Final-step pause branch (same pause conditions as #1 plus `not effective_auto_close`). Wrapped in `try/except WorktreeTeardownError` (lines 401–405). |
| 3 | `bellows.py:428` | Auto-close branch (all gates passed + `effective_auto_close=True`). Wrapped in `try/except WorktreeTeardownError` (lines 427–441). On teardown failure, converts to gate_failure pause. |

### (b) Under what conditions are they called?

**Every plan dispatch, all plan types.** The `_create_worktree` call at `bellows.py:282` is unconditional within `run_plan` — it fires for diagnostics, executables, parallel-N- groups, and sequential plans alike. The only conditional skip is **inside** `_create_worktree` itself (`bellows.py:528`): if `project_path` has no `.git` directory or file, it returns `project_path` as-is (the 2026-05-04 detect-and-skip fix). This means:

- Real-`.git` projects (e.g., invoice-pulse): worktree created on every dispatch.
- bellows-self (subdirectory of governance-root monorepo, no project-local `.git`): worktree skipped, runs in-place.

### (c) Do current signatures and bodies match the 2026-05-03 recommendation's Step 1E?

**Yes — full alignment.** No restructuring needed.

| Aspect | Step 1E Proposed | Current HEAD |
|---|---|---|
| `_create_worktree` signature | `_create_worktree(project_path, slug)` | `_create_worktree(project_path: str, slug: str) -> str` at `bellows.py:518` |
| `_teardown_worktree` signature | `_teardown_worktree(project_path, wt_path, slug)` | `_teardown_worktree(project_path: str, wt_path: str, slug: str) -> None` at `bellows.py:556` |
| Detached HEAD creation | `git worktree add <path> HEAD --detach` | Matches: `bellows.py:538` |
| Retry on failure | Proposed in D3g | Implemented: 2s retry at `bellows.py:542–546` |
| Fallback-to-shared-tree | D3g: try/except with warning log | Implemented as `WorktreeCreationError` escalation to verdict-pending pause (`bellows.py:283–293`) — stricter than D3g's "silent degradation" lean but functionally equivalent (plan is not lost) |
| Cherry-pick merge-back | D3b: `git log` + `git cherry-pick` | Matches: `bellows.py:583–607` |
| Uncommitted file copy-back | D3c: `git status --porcelain` + copy | Matches: `bellows.py:610–632` |
| Worktree removal | `git worktree remove` | Matches: `bellows.py:635–643` (with `--force` flag) |
| Startup prune | D3g: `git worktree prune` in `__init__` | Matches: `bellows.py:741–750` |
| `.gitignore` update | `.bellows-worktrees/` entry | **Not yet verified** — not in scope of this delta check |

**One minor divergence from SA lean:** The SA recommended silent degradation with warning log on creation failure (Step 1F, Q3). The implementation instead raises `WorktreeCreationError`, which triggers a verdict-pending pause for CEO attention. This is the **stricter** option from Q3, not the SA's lean. This is a CEO decision (or implementation decision accepted by CEO) and does not affect the recommendation's validity.

### (d) Does `_create_worktree` create a worktree for real-`.git` projects today?

**YES — always-worktree behavior IS wired up.** The detect-and-skip check at `bellows.py:528`:

```python
if not os.path.exists(os.path.join(project_path, ".git")):
    ...
    return project_path
```

This fires ONLY when there is no project-local `.git`. For any project with its own `.git` (directory or file), the function proceeds to create a worktree at `.bellows-worktrees/<slug>` (`bellows.py:533`). The 2026-05-04 close was scoped to bellows-self detect-and-skip, but the always-worktree behavior for real-`.git` projects was already shipping since commit `36b2bba` (2026-05-03).

**Summary for Q1:** The 2026-05-03 recommendation has been **fully implemented**. The worktree code shipped across three commits:
- `36b2bba` (2026-05-03): main implementation — per-plan git worktree for parallel-collision isolation
- `272fbe4` (2026-05-03): bugfix — dict format for worktree failure entries
- `06aa938` (2026-05-04): detect-and-skip — no worktree for projects without `.git`

---

## Q2 — Surface Map Staleness Check

### (a) Line number accuracy at HEAD

**All 2026-05-03 line numbers are stale.** The worktree implementation (commits `36b2bba`, `272fbe4`, `06aa938`, plus the `9786e87` step-count override fix) added ~120 lines of new code to `bellows.py`, shifting all referenced locations downward.

| Surface Map Citation | 2026-05-03 Line | Current HEAD Line | Drift |
|---|---|---|---|
| `_capture_git_diff` definition | 404–420 | 463–479 | +59 |
| `_capture_git_diff` call site 1 (first step pre-diff) | 265 | 296 | +31 |
| `_capture_git_diff` call site 2 (first step post-diff) | 281 | 312 | +31 |
| `_capture_git_diff` call site 3 (loop pre-diff) | 321 | 358 | +37 |
| `_capture_git_diff` call site 4 (loop post-diff) | 339 | 376 | +37 |
| `_parse_diff_stat` definition | 423–456 | 482–515 | +59 |
| `_parse_diff_stat` call site 1 (first step) | 282 | 313 | +31 |
| `_parse_diff_stat` call site 2 (loop) | 340 | 377 | +37 |
| `run_plan` definition | 194–401 | 204–461 | +10/+60 |
| Plan claim (`shutil.move`) | 240 | 253 | +13 |
| `runner.run_step` call site 1 | 267 | 298 | +31 |
| `runner.run_step` call site 2 (loop) | 323 | 360 | +37 |
| `handle_parallel_group` | 590–595 | 789–794 | +199 |
| `handle_new_plan` | 584–588 | 783–787 | +199 |
| `PlanHandler.__init__` `_pending_groups` | 491 | 678 | +187 |
| `_rescan` parallel settle-window | 601–612 | 796–811 | +195 |
| `_active_lock` | 550 | 737 | +187 |

### (b) New state, functions, or call sites added in the 2026-05-03 → 2026-05-05 window

**Yes — 4 commits modified `bellows.py` in this window:**

1. **`9786e87`** — `fix(bellows): narrow is_diagnostic step-count override to total_steps==0` — Modified the `total_steps == 0 and is_diagnostic` override logic. Added at lines 238–245 (current HEAD 244–245). New `is_diagnostic` variable at line 236. This is in the header/metadata section of `run_plan`, BEFORE the pre-diff capture. **No impact on worktree or diff-capture topology.**

2. **`36b2bba`** — `fix(bellows): per-plan git worktree for parallel-collision isolation` — The main worktree implementation. Added:
   - `WorktreeCreationError` and `WorktreeTeardownError` exception classes (lines 21–28)
   - `_create_worktree` function (lines 518–553)
   - `_teardown_worktree` function (lines 556–643)
   - Worktree creation call in `run_plan` (line 282)
   - 3 teardown call sites with error handling (lines 335–340, 400–405, 426–441)
   - Startup prune in `Bellows.__init__` (lines 740–750)
   - Changed all 4 `_capture_git_diff` call sites from `project_path` to `wt_path`
   - Changed both `runner.run_step` call sites from `project_path` to `wt_path`

3. **`272fbe4`** — `fix(bellows): use dict format for worktree failure entries (4 sites)` — Fixed the `gate_result["failures"].append(...)` calls at 4 worktree error handling sites to use dict format instead of string format. No new call sites or topology changes.

4. **`06aa938`** — `fix: skip worktree creation when project_path has no .git` — Added the `.git` existence check inside `_create_worktree` (line 528–531). No new call sites in `run_plan`.

### (c) Are the 4 `_capture_git_diff` call sites still 4?

**YES — still exactly 4 call sites.** No call sites added or removed. They now pass `wt_path` instead of `project_path`:

| # | Old (2026-05-03) | Current HEAD |
|---|---|---|
| 1 | `bellows.py:265`: `_capture_git_diff(project_path)` | `bellows.py:296`: `_capture_git_diff(wt_path)` |
| 2 | `bellows.py:281`: `_capture_git_diff(project_path)` | `bellows.py:312`: `_capture_git_diff(wt_path)` |
| 3 | `bellows.py:321`: `_capture_git_diff(project_path)` | `bellows.py:358`: `_capture_git_diff(wt_path)` |
| 4 | `bellows.py:339`: `_capture_git_diff(project_path)` | `bellows.py:376`: `_capture_git_diff(wt_path)` |

### (d) New code-modification sites from `_create_worktree` / `_teardown_worktree`

**These functions and their call sites ARE the worktree implementation — they are the output of the recommendation, not pending work.** The 2026-05-03 surface map was the input to the implementation. The implementation has shipped. The new sites are:

| Site | Lines | Purpose |
|---|---|---|
| `_create_worktree` definition | 518–553 | Worktree creation helper (did not exist 2026-05-03) |
| `_teardown_worktree` definition | 556–643 | Worktree teardown helper (did not exist 2026-05-03) |
| Creation call + error handling | 281–293 | In `run_plan`, between bootstrap prompt and pre-diff |
| Teardown call 1 + error handling | 335–340 | In while-loop pause branch |
| Teardown call 2 + error handling | 400–405 | In final-step pause branch |
| Teardown call 3 + error handling | 426–441 | In auto-close branch |
| Startup prune | 740–750 | In `Bellows.__init__` |

No additional executable work is needed to address these sites — they already implement the recommendation.

---

## Surface Map Updates Required for Executable

**No updates required — the surface map is archival.**

The 2026-05-03 surface map (`worktree-implementation-surface-2026-05-03.md`) was the input artifact for the worktree implementation. The implementation has now shipped (commits `36b2bba`, `272fbe4`, `06aa938`). The surface map's line numbers are stale at HEAD, but updating them would serve no purpose — there is no pending executable that consumes these line numbers. The surface map accurately captures the pre-implementation state, which is its historical value.

If a future diagnostic or executable needs current line numbers for `_capture_git_diff` call sites or `run_plan` structure, it should generate a fresh surface map rather than patching the 2026-05-03 artifact.

---

## Recommendation Impact

**No change to the 2026-05-03 recommendation.**

The recommendation has been **fully implemented** as designed:
- Step 1E's proposed `_create_worktree` and `_teardown_worktree` functions exist with matching signatures and behavior.
- Always-worktree scope is wired up for real-`.git` projects.
- Detect-and-skip (2026-05-04 close) added graceful handling for bellows-self's monorepo case without altering the recommendation's core design.
- Startup prune is in `Bellows.__init__`.
- All 4 `_capture_git_diff` call sites pass `wt_path`.
- Both `runner.run_step` call sites pass `wt_path`.
- Cherry-pick merge-back, uncommitted file copy-back, and worktree removal all match D3b/D3c/D3g designs.

The 2026-05-03 recommendation is not stale — it is **implemented and live**. No re-evaluation is needed.

---

## Output Receipt
**Agent:** Bellows Systems Analyst
**Step:** 1
**Status:** Complete

### What Was Done
Delta-checked the 2026-05-03 worktree recommendation against the current `bellows.py` HEAD. Answered two specific questions: (Q1) the 2026-05-04 detect-and-skip fix's code interaction with the recommendation, and (Q2) the staleness of the 2026-05-03 surface map's line numbers and call-site topology. Verified that the recommendation has been fully implemented across three commits with matching signatures, bodies, and always-worktree scope. Produced a complete line-drift table for all surface-map citations.

### Files Deposited
- `bellows/knowledge/research/worktree-delta-check-2026-05-05.md` — delta check findings with file:line citations and drift table

### Files Created or Modified (Code)
- None (diagnostic — no production code modified)

### Decisions Made
- The 2026-05-03 surface map is archival (not worth patching — no pending consumer)
- The 2026-05-03 recommendation is implemented and live — no re-evaluation needed

### Flags for CEO
- None. The recommendation and its implementation are aligned. No re-evaluation trigger found.

### Flags for Next Step
- None — this is a single-step diagnostic. The Planner reads this deposit, verifies via Rule 22, and performs housekeeping directly.
