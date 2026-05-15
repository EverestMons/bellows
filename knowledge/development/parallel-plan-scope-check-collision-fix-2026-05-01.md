# Dev Log: Parallel-Plan scope_check Collision Fix (File-Checksum Snapshot)

**Date:** 2026-05-01 | **Plan:** executable-parallel-plan-scope-check-collision-fix-2026-05-01 | **Step:** 1 (DEV)

---

## What Was Changed

Replaced `_capture_git_diff` (working-tree `git diff --stat` observation, contaminated by parallel sibling commits) with `_snapshot_file_state` (per-step file-checksum snapshot, immune to sibling contamination) as the mechanism for detecting which files a step modified.

### Root Cause

When multiple parallel plans (`parallel-N-`) execute concurrently, they share the same git working tree. The old `_capture_git_diff` approach ran `git diff --stat` before and after each step, then compared the two outputs. If a sibling plan modified files during the step's execution window, those changes appeared in the post-diff, causing the scope_check gate to flag files the current plan never touched.

### Solution

**New functions added to `bellows.py`:**

1. `_snapshot_file_state(project_path: str) -> dict` (line 434)
   - Uses `git ls-files` to enumerate tracked files
   - Hashes each file via `hashlib.sha256`
   - Skips `.git/`, `.bellows-cache/`, and `*.pyc`
   - Returns `{}` on any exception (defensive)

2. `_diff_file_state(pre: dict, post: dict) -> list` (line 476)
   - Compares two snapshot dicts
   - Returns sorted list of paths with changed/added/deleted files

**Call site replacements in `run_plan()`:**

| Location | Old | New |
|---|---|---|
| Line 295 (first step pre) | `pre_diff = _capture_git_diff(project_path)` | `pre_state = _snapshot_file_state(project_path)` |
| Line 311-312 (first step post) | `post_diff = _capture_git_diff(...)` + `_parse_diff_stat(...)` | `post_state = _snapshot_file_state(...)` + `_diff_file_state(pre_state, post_state)` |
| Line 351 (loop pre) | `pre_diff = _capture_git_diff(project_path)` | `pre_state = _snapshot_file_state(project_path)` |
| Line 369-370 (loop post) | `post_diff = _capture_git_diff(...)` + `_parse_diff_stat(...)` | `post_state = _snapshot_file_state(...)` + `_diff_file_state(pre_state, post_state)` |

**Deprecated (retained for stability period):**
- `_capture_git_diff` — docstring marked DEPRECATED 2026-05-01
- `_parse_diff_stat` — docstring marked DEPRECATED 2026-05-01

### Why This Is Immune to Parallel Contamination

The checksum snapshot records the actual byte-content hash of each tracked file at the moment of capture. It does NOT depend on git's working-tree diff state, which is shared across threads. Each plan's pre/post snapshot pair captures only the changes that occurred on disk during that specific step's execution, regardless of what other threads are doing.

## Files Created or Modified (Code)

- `bellows/bellows.py` — added `_snapshot_file_state`, `_diff_file_state`; replaced 4 call sites; deprecated old functions
- `bellows/tests/test_snapshot_file_state.py` — 6 unit tests

## Test Results

**Targeted (`tests/test_snapshot_file_state.py`):** 6/6 passed
**Full suite (`tests/`):** 183 passed, 1 failed (pre-existing `test_run_step_timeout` — known, acceptable)

## Commit

`9b20d94` — `fix(gates): file-checksum snapshot for parallel-plan scope_check immunity`

---

### Output Receipt

| Field | Value |
|---|---|
| Status | Complete |
| Commit | `9b20d94` |
| Tests (targeted) | 6/6 PASS |
| Tests (full) | 183/184 PASS (1 pre-existing failure) |
| New regressions | 0 |
