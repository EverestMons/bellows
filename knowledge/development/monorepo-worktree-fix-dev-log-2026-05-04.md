# Dev Log — Monorepo Worktree Fix (Option A: detect-and-skip)

**Date:** 2026-05-04
**Plan:** executable-monorepo-worktree-fix-2026-05-04

## Design Choices

### (a) Detection location: top of `_create_worktree` (line 528)

Added `os.path.exists(os.path.join(project_path, ".git"))` as the first check inside `_create_worktree`. When `.git` is absent, the function logs a warning and returns `project_path` directly, skipping all worktree creation logic. Chose this location over the call site because it keeps the detection and fallback co-located with the worktree logic — the call site in `run_plan` doesn't need to know how the decision was made.

### (b) Signal shape for teardown: sentinel return value (`wt_path == project_path`)

When `_create_worktree` returns `project_path` (instead of a `.bellows-worktrees/<slug>` subdirectory), that equality IS the signal. `_teardown_worktree` checks `if wt_path == project_path: return` at line 562. This is the explicit-signal approach recommended by the plan — the return value from `_create_worktree` carries the information forward. No re-checking of `.git` state, no boolean flag, no tuple return type change. The sentinel is robust because a real worktree path is always a subdirectory of project_path, never equal to it.

## Changes

- `bellows.py:528-531` — `.git` detection + early return in `_create_worktree`
- `bellows.py:562-563` — sentinel check + early return in `_teardown_worktree`
- `tests/test_bellows.py` — 3 new tests:
  - `test_create_worktree_returns_project_path_when_no_git` — verifies in-place fallback
  - `test_teardown_worktree_noop_when_wt_equals_project` — verifies zero subprocess calls
  - `test_create_worktree_proceeds_when_git_exists` — regression guard for .git-having projects

## Test Results

Targeted: 90 passed (tests/test_bellows.py + tests/test_verdict.py), 0 failed.

---

## Output Receipt
**Agent:** Bellows Developer
**Step:** 1
**Status:** Complete

### What Was Done
Added monorepo worktree detection to `_create_worktree` — when project_path has no `.git`, worktree creation is skipped and the agent runs in-place. Teardown becomes a no-op via sentinel comparison. Three unit tests added covering the skip path, the no-op teardown, and the regression guard for projects with `.git`.

### Files Deposited
- `bellows/knowledge/development/monorepo-worktree-fix-dev-log-2026-05-04.md` — this dev log

### Files Created or Modified (Code)
- `bellows/bellows.py` — added `.git` detection in `_create_worktree` (skip + return project_path) and sentinel check in `_teardown_worktree` (no-op when wt_path == project_path)
- `bellows/tests/test_bellows.py` — 3 new unit tests for monorepo worktree skip behavior

### Decisions Made
- Detection at top of `_create_worktree` (not at call site) — co-locates decision with worktree logic
- Sentinel via `wt_path == project_path` equality (not tuple return or boolean flag) — avoids signature change, robust because real worktree paths are always subdirectories

### Flags for CEO
- None

### Flags for Next Step
- The 2026-05-03 type-fix (commit 0f2059f) at lines 340, 405, 433 is intact — QA should verify via grep
- Log message to grep for: `has no project-local .git — running in-place without worktree isolation`
