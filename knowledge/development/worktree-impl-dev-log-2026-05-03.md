# Worktree Implementation Dev Log

**Date:** 2026-05-03 | **Plan:** executable-bellows-worktree-impl-2026-05-03 | **Step:** 1

---

## Summary

Implemented per-plan git worktree isolation in `bellows.py` to fix the BACKLOG #1 parallel-plan `scope_check` collision bug. Every `run_plan` invocation now creates a detached-HEAD worktree at `<project>/.bellows-worktrees/<slug>/`, routes all `_capture_git_diff` and `runner.run_step` calls through the worktree path, then tears down the worktree on plan pause or auto-close (cherry-picking commits back to main, copying dirty files, removing the worktree).

## Files Modified

| File | Lines | What Changed |
|---|---|---|
| `bellows.py` | 21-29 | Added `WorktreeCreationError` and `WorktreeTeardownError` exception classes |
| `bellows.py` | 518-545 | Added `_create_worktree(project_path, slug)` helper |
| `bellows.py` | 547-631 | Added `_teardown_worktree(project_path, wt_path, slug)` helper |
| `bellows.py` | 282-293 | Wired worktree creation with strict-pause-on-failure in `run_plan` |
| `bellows.py` | 296, 298, 312, 352, 354, 370 | 6 cwd swaps: `project_path` → `wt_path` for `_capture_git_diff` (4) and `runner.run_step` (2) |
| `bellows.py` | 335-340 | Teardown at mid-plan pause exit (while loop) |
| `bellows.py` | 400-405 | Teardown at final-step pause exit |
| `bellows.py` | 426-438 | Teardown at auto-close exit with cherry-pick conflict → gate_failure conversion |
| `bellows.py` | 730-737 | Startup `git worktree prune` hook in `Bellows.__init__` |
| `.gitignore` | 12 | Added `.bellows-worktrees/` |
| `tests/test_bellows.py` | multiple | Added `_create_worktree` and `_teardown_worktree` mocks to all `run_plan`-calling tests |
| `tests/test_consume_verdicts.py` | 196-197 | Added worktree mocks |

## Helper Function Signatures

- **`_create_worktree(project_path: str, slug: str) -> str`** — Line 518. Creates detached-HEAD worktree. Returns `wt_path`. Retry-once on failure with 2s delay. Raises `WorktreeCreationError` after second failure or on timeout/OS error.
- **`_teardown_worktree(project_path: str, wt_path: str, slug: str) -> None`** — Line 547. Cherry-picks worktree commits back to main, copies dirty files, removes worktree. Raises `WorktreeTeardownError` on cherry-pick conflict (worktree left alive for manual resolution).
- **`WorktreeCreationError`** — Line 21. Subclass of `Exception`.
- **`WorktreeTeardownError`** — Line 26. Subclass of `Exception`.

## Retry Behavior

`_create_worktree` attempts `git worktree add` once. On non-zero return code, prints warning, sleeps 2 seconds, retries once. On second failure, raises `WorktreeCreationError`. The `subprocess.TimeoutExpired` and `OSError` exceptions are caught and converted to `WorktreeCreationError`. In `run_plan`, the caught `WorktreeCreationError` triggers a `gate_failure` verdict request and renames the plan to `verdict-pending-*`.

## Cherry-Pick Conflict Handling

`_teardown_worktree` sub-operation (c) cherry-picks each worktree commit onto the main checkout in chronological order. On any non-zero cherry-pick return code: runs `git cherry-pick --abort` to reset state, then raises `WorktreeTeardownError`. The worktree is NOT removed — left alive at `.bellows-worktrees/<slug>/` for manual resolution. In `run_plan`, the three teardown call sites catch `WorktreeTeardownError` and either:
- (mid-plan pause, final-step pause): append error to `gate_result["failures"]`, override `_pause_reason` to `"gate_failure"`, then proceed with normal verdict post + rename
- (auto-close): convert to gate_failure pause with verdict request + rename to `verdict-pending-*`

## Test Results

| Metric | Before | After |
|---|---|---|
| Total tests | 177 | 177 |
| Passed | 176 | 176 |
| Failed | 1 (`test_run_step_timeout`) | 1 (`test_run_step_timeout`) |
| New failures | — | 0 |

Pre-existing `test_run_step_timeout` failure is unrelated (runner timeout mock issue). Baseline matches.

## Commit SHAs

- `36b2bba` — `fix(bellows): per-plan git worktree for parallel-collision isolation`
- `9ce69d5` — `docs: dev log for worktree implementation`

## Call Sites NOT Changed (by design)

- `_parse_diff_stat(post_diff, pre_diff, project_path)` — `project_path` stays as project root for relative-path filtering
- `gates.check(parsed, plan_text, current_step, project_path, ...)` — gates use `project_path` for deposit-existence resolution
- `record_run(db_path, plan_path, project_path, ...)` — DB writes use absolute project paths

---

## Output Receipt
**Agent:** Bellows Developer
**Step:** 1
**Status:** Complete

### What Was Done
Implemented per-plan git worktree isolation in `bellows.py`: two exception classes, two helper functions (`_create_worktree`, `_teardown_worktree`), startup prune hook, worktree creation with strict-pause-on-failure, 6 cwd swaps, teardown at all 3 exit points. Updated `.gitignore`. Updated existing test mocks. Targeted test regression matches baseline (176 pass, 1 pre-existing fail).

### Files Deposited
- `bellows/knowledge/development/worktree-impl-dev-log-2026-05-03.md` — this dev log

### Files Created or Modified (Code)
- `bellows/bellows.py` — worktree helpers, exception classes, startup prune, creation/teardown wiring in run_plan, 6 cwd swaps
- `bellows/.gitignore` — added `.bellows-worktrees/`
- `bellows/tests/test_bellows.py` — added worktree mocks to existing run_plan tests
- `bellows/tests/test_consume_verdicts.py` — added worktree mocks

### Decisions Made
- Test files updated with worktree mocks (necessary for existing tests to pass with new run_plan code — not "new tests")

### Flags for CEO
- None

### Flags for Next Step
- Plan 2 reads helper function signatures and line numbers from this dev log
- Behavioral verification (live worktree isolation) deferred to Plan 2 post-restart
- `test_run_step_timeout` pre-existing failure unrelated to this change
