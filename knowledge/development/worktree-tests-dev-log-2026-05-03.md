# Worktree Tests Dev Log

**Date:** 2026-05-03 | **Plan:** executable-bellows-worktree-tests-2026-05-03 | **Step:** 1

---

## Summary

Added 6 unit tests to `tests/test_bellows.py` and created `tests/test_worktree.py` with 7 integration tests covering the per-plan git worktree mechanism implemented in Plan 1. All 13 new tests pass. The integration tests exercise real git worktree operations against temporary repositories — no mocking of git itself.

## Files Modified

| File | What Changed |
|---|---|
| `tests/test_bellows.py` | Appended 6 new unit tests for run_plan worktree call points |
| `tests/test_worktree.py` | Created with 7 integration tests for _create_worktree and _teardown_worktree |

## New Tests Added

### Unit tests in test_bellows.py (6)

1. **`test_run_plan_creates_worktree_before_pre_diff`** — Verifies `_create_worktree` is called before the first `_capture_git_diff` using call-order tracking.
2. **`test_run_plan_passes_wt_path_to_capture_and_runner`** — Verifies `_capture_git_diff` and `runner.run_step` receive the worktree path (sentinel string), not the project path.
3. **`test_run_plan_tears_down_worktree_after_final_gate`** — Verifies `_teardown_worktree` is called after `gates.check` returns and the plan reaches Done/ on auto-close.
4. **`test_run_plan_strict_pause_on_creation_failure`** — Verifies `WorktreeCreationError` triggers `gate_failure` verdict, blocks runner dispatch, and renames plan to `verdict-pending-`.
5. **`test_run_plan_pauses_on_cherry_pick_conflict`** — Verifies `WorktreeTeardownError` on auto-close triggers `gate_failure` verdict with teardown failure in gate_result, renames to `verdict-pending-`.
6. **`test_bellows_init_runs_worktree_prune`** — Verifies `Bellows.__init__` calls `git worktree prune` with correct `cwd` for each watched project.

### Integration tests in test_worktree.py (7)

1. **`test_create_worktree_returns_valid_path_with_tracked_files`** — Real git init + 3 committed files. Worktree created, path verified, all tracked files present.
2. **`test_worktree_isolation_git_diff`** — Dirty file in main checkout does NOT appear in worktree's `git diff`. Core BACKLOG #1 regression guard.
3. **`test_teardown_removes_worktree_directory`** — After `_teardown_worktree`, directory is gone and not in `git worktree list`.
4. **`test_teardown_cherry_picks_commits`** — Commit in worktree appears on main's HEAD after teardown.
5. **`test_teardown_copies_uncommitted_files`** — Uncommitted new file in worktree is copied to main after teardown.
6. **`test_teardown_aborts_on_cherry_pick_conflict`** — Conflicting commits raise `WorktreeTeardownError`. Main checkout is clean (no CHERRY_PICK_HEAD). Worktree left alive.
7. **`test_create_worktree_retries_once_on_failure`** — Mocked subprocess: fails once, succeeds on retry. Verifies 2 calls, 1 sleep(2), correct return path.

## Test Results

| Metric | Before | After |
|---|---|---|
| Total tests | 177 | 190 |
| Passed | 176 | 189 |
| Failed | 1 (`test_run_step_timeout`) | 1 (`test_run_step_timeout`) |
| New tests added | — | 13 |
| New failures | — | 0 |

Pre-existing `test_run_step_timeout` failure is unrelated (runner timeout mock issue). Baseline matches Plan 1.

## Spec Deviations from SA Design (Plan 1 implementation)

The following deviations exist between the SA design spec (`worktree-candidate-designs-2026-05-03.md` Section D2, Candidate 1) and the actual Plan 1 implementation. These are neutral observations — the implementation choices may be entirely correct.

1. **Function consolidation:** SA spec defined three separate functions (`_create_worktree`, `_merge_worktree_commits`, `_remove_worktree`). Implementation combines merge + copy-dirty + remove into a single `_teardown_worktree(project_path, wt_path, slug)` function.

2. **Parameter order:** SA spec had `_create_worktree(plan_slug, project_path)`. Implementation uses `_create_worktree(project_path, slug)` — parameter order reversed and `plan_slug` shortened to `slug`.

3. **Worktree location:** SA spec placed worktrees in `/tmp/bellows-wt-<slug>`. Implementation uses `<project_path>/.bellows-worktrees/<slug>/` (project-local, git-ignored).

4. **Retry logic:** Not specified in SA design. Implementation adds retry-once-on-failure with 2s delay in `_create_worktree`.

5. **Dirty file copy-back:** Not specified in SA design. Implementation copies uncommitted files from worktree back to main checkout during teardown.

6. **Startup prune hook:** Not specified in SA design. Implementation adds `git worktree prune` in `Bellows.__init__` for each watched project.

7. **Plan 2 spec kwarg name:** Plan 2 spec referenced `pause_reason_code="gate_failure"` in test assertions. Actual `verdict.post_verdict_request` uses `pause_reason="gate_failure"`. Tests assert against the actual kwarg name.

---

## Output Receipt
**Agent:** Bellows Developer
**Step:** 1
**Status:** Complete

### What Was Done
Added 13 new tests (6 unit + 7 integration) covering the per-plan worktree mechanism. All tests pass. Documented spec deviations between SA design and Plan 1 implementation.

### Files Deposited
- `bellows/knowledge/development/worktree-tests-dev-log-2026-05-03.md` — this dev log

### Files Created or Modified (Code)
- `bellows/tests/test_bellows.py` — appended 6 unit tests for worktree call points in run_plan
- `bellows/tests/test_worktree.py` — created with 7 integration tests exercising real git operations

### Decisions Made
- Used call-order tracking (shared list with side_effect) instead of Mock.call_args_list cross-object ordering for cleaner sequence assertions
- Used `pytest.fixture` with `yield` + explicit cleanup in `finally` for temp git repo lifecycle
- Asserted against `pause_reason` kwarg (actual code) rather than `pause_reason_code` (Plan 2 spec typo)
- No `@pytest.mark.integration` markers — existing test suite does not use markers

### Flags for CEO
- None

### Flags for Next Step
- All 13 new tests pass. Full suite: 189 passed, 1 pre-existing failure.
- `test_run_step_timeout` failure is unrelated to this change
