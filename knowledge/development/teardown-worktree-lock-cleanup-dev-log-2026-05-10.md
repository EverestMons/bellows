# Dev Log — _teardown_worktree stale lock detection + orphan cleanup

**Date:** 2026-05-10
**Plan:** executable-teardown-worktree-lock-cleanup-2026-05-10 (Step 1)
**BACKLOG entry:** 2026-05-07 cherry-pick fragility

---

## Diff Applied to bellows.py

### CHANGE 1 — Stale lock detection (inserted at L638, before cherry-pick loop)

```python
# Detect stale .git/index.lock that would block cherry-pick
lock_path = os.path.join(project_path, ".git", "index.lock")
if os.path.exists(lock_path):
    lock_age = time.time() - os.path.getmtime(lock_path)
    if lock_age > 5:
        try:
            os.remove(lock_path)
            print(f"Bellows: ⚠ removed stale .git/index.lock ({lock_age:.0f}s old) for {slug}")
        except OSError as e:
            print(f"Bellows: ⚠ could not remove .git/index.lock for {slug}: {e}")
    else:
        # Fresh lock — wait briefly, then remove if still present
        time.sleep(3)
        if os.path.exists(lock_path):
            try:
                os.remove(lock_path)
                print(f"Bellows: ⚠ removed .git/index.lock after 3s wait for {slug}")
            except OSError as e:
                print(f"Bellows: ⚠ could not remove .git/index.lock for {slug}: {e}")
```

**Post-edit position:** Lines 638–656

### CHANGE 2 — Orphaned directory fallback cleanup (inserted after worktree removal block)

```python
# Fallback: if `git worktree remove` failed and the directory still exists, force-remove it
if os.path.exists(wt_path):
    try:
        shutil.rmtree(wt_path, ignore_errors=True)
    except Exception as e:
        print(f"Bellows: ⚠ could not force-remove orphaned worktree dir {wt_path}: {e}")
```

**Post-edit position:** Lines 711–716

---

## New Tests Added to tests/test_bellows.py

### Test 1 — `test_teardown_worktree_removes_stale_index_lock`
- Creates temp project with `.git/index.lock` (mtime 30s ago)
- Mocks subprocess to succeed
- Asserts lock file is gone after `_teardown_worktree`

### Test 2 — `test_teardown_worktree_waits_for_fresh_index_lock`
- Creates temp project with fresh `.git/index.lock` (current mtime)
- Patches `time.sleep` to avoid actual delay
- Asserts lock file is gone after `_teardown_worktree`

### Test 3 — `test_teardown_worktree_force_removes_orphaned_directory`
- Creates temp worktree directory with content
- Mocks `git worktree remove` to fail (returncode 1)
- Asserts the worktree directory is gone (shutil.rmtree cleaned it up)

---

## Pytest Output

### test_bellows.py (verbose, tail)

```
tests/test_bellows.py::test_teardown_worktree_noop_when_wt_equals_project PASSED [ 86%]
tests/test_bellows.py::test_mode_a_detected_and_recovered PASSED         [ 87%]
tests/test_bellows.py::test_mode_a_no_detection_normal_flow PASSED       [ 88%]
tests/test_bellows.py::test_mode_a_missing_file_not_in_done PASSED       [ 89%]
tests/test_bellows.py::test_mode_a_recovery_failure PASSED               [ 90%]
tests/test_bellows.py::test_mode_a_synthetic_failure_in_verdict_request PASSED [ 91%]
tests/test_bellows.py::test_create_worktree_proceeds_when_git_exists PASSED [ 92%]
tests/test_bellows.py::test_warning_multi_step_plan_without_pause_for_verdict PASSED [ 93%]
tests/test_bellows.py::test_no_warning_multi_step_plan_with_pause_for_verdict PASSED [ 94%]
tests/test_bellows.py::test_no_warning_single_step_plan_without_pause_for_verdict PASSED [ 95%]
tests/test_bellows.py::test_no_warning_multi_step_plan_with_pause_always PASSED [ 96%]
tests/test_bellows.py::test_teardown_worktree_removes_stale_index_lock PASSED [ 97%]
tests/test_bellows.py::test_teardown_worktree_waits_for_fresh_index_lock PASSED [ 98%]
tests/test_bellows.py::test_teardown_worktree_force_removes_orphaned_directory PASSED [100%]

======================== 93 passed, 1 warning in 0.37s =========================
```

### Full suite (tail)

```
FAILED tests/test_runner_parser.py::test_run_step_timeout - assert False is True
=================== 1 failed, 245 passed, 1 warning in 5.96s ===================
```

Pre-existing `test_run_step_timeout` failure unchanged. +3 new tests passing (93 → from 90 in test_bellows.py; 245 total from 242).

---

## Confirmations

- **Line numbers (post-edit):** CHANGE 1 at L638–656, CHANGE 2 at L711–716
- **No other functions in bellows.py were touched** — only `_teardown_worktree` modified
- **No other test files were touched** — only `tests/test_bellows.py`
- **Imports verified:** `os`, `time`, `shutil` already present at top of bellows.py

---

## Output Receipt
**Agent:** Bellows Developer
**Step:** 1
**Status:** Complete

### What Was Done
Implemented stale `.git/index.lock` detection and removal before cherry-pick, and orphaned worktree directory fallback cleanup after `git worktree remove`. Added 3 regression tests.

### Files Deposited
- `bellows/knowledge/development/teardown-worktree-lock-cleanup-dev-log-2026-05-10.md` — this dev log

### Files Created or Modified (Code)
- `bellows/bellows.py` — +25 lines (lock detection + orphan cleanup in `_teardown_worktree`)
- `bellows/tests/test_bellows.py` — +93 lines (3 new regression tests)

### Decisions Made
- Used `OSError` (not generic `Exception`) for `os.remove` catch — matches git lock semantics
- Patched `time.sleep` in fresh-lock test to avoid 3s delay in CI
- Used `MagicMock` return pattern consistent with existing test_bellows.py style

### Flags for CEO
- None

### Flags for Next Step
- QA should verify the lock detection fires correctly with both stale (>5s) and fresh (<5s) locks
- The `shutil.rmtree(ignore_errors=True)` means the outer except is unreachable in practice — acceptable for defense-in-depth
