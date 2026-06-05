# Dev Log — _teardown_worktree (b): raise on git-log failure

**Date:** 2026-06-05
**Plan:** executable-teardown-b-raise-on-log-failure-2026-06-05
**Step:** 1 (DEV)

## Replaced Block

The original step (b) in `_teardown_worktree` (bellows.py, previously at line 907):

```python
    # (b) Collect commits made in worktree
    try:
        result = subprocess.run(
            ["git", "--no-pager", "log", "--format=%H", "HEAD", "--not", main_branch],
            cwd=wt_path, capture_output=True, text=True, timeout=30,
        )
        commit_shas = result.stdout.strip().splitlines()[::-1]  # oldest-first for cherry-pick
    except Exception:
        commit_shas = []
```

Replaced with:

```python
    # (b) Collect commits made in worktree
    # Fail-safe (2026-06-05): a git-log failure here must NOT silently default to
    # an empty commit list — that would skip the cherry-pick and still remove the
    # worktree, losing un-landed commits with NO recorded worktree_teardown failure
    # (uncatchable by the Gap-1b continue-block and Gap-1c retry, both of which key
    # off a recorded failure). Raise so the failure routes to the 1b halt / 1c retry,
    # matching the rest of this function's land-or-raise contract. A successful-but-
    # empty result (returncode 0, no commits made) is legitimate and proceeds.
    try:
        result = subprocess.run(
            ["git", "--no-pager", "log", "--format=%H", "HEAD", "--not", main_branch],
            cwd=wt_path, capture_output=True, text=True, timeout=30,
        )
    except Exception as e:
        raise WorktreeTeardownError(
            f"worktree commit enumeration failed (git log exception) for slug {slug}: {e}"
        ) from e
    if result.returncode != 0:
        raise WorktreeTeardownError(
            f"worktree commit enumeration failed (git log rc={result.returncode}) for slug {slug}: {result.stderr.strip()}"
        )
    commit_shas = result.stdout.strip().splitlines()[::-1]  # oldest-first for cherry-pick
```

## Byte-Unchanged Confirmation

Steps (a), index.lock handling, (b2) dirty-tree pre-check, (c) cherry-pick loop, (d) copy-back, and (e) worktree removal are all unchanged. Only step (b) was modified.

## Fail vs Successfully-Empty Distinction

- **Fail path (exception):** `subprocess.run` raises (timeout, OS error, etc.) → `except Exception as e` catches → re-raises as `WorktreeTeardownError` with chained cause. Worktree is preserved.
- **Fail path (non-zero rc):** `subprocess.run` returns `CompletedProcess` with `returncode != 0` → `WorktreeTeardownError` raised with stderr. Worktree is preserved.
- **Successfully-empty path (preserved):** `subprocess.run` returns `CompletedProcess` with `returncode == 0`, empty stdout → `commit_shas = []` → no cherry-pick iterations → teardown proceeds to copy-back (d) and removal (e). This is the legitimate case where a step made no commits.

## Pre-edit Verification Results

1. **Step (b) bare except:** CONFIRMED at line 907. `except Exception: commit_shas = []` present, no returncode check.
2. **WorktreeTeardownError:** CONFIRMED. Class defined at line 139, raised at lines 952 (dirty-tree) and 994 (cherry-pick conflict).
3. **Test cluster:** CONFIRMED. Four `test_teardown_*` tests at lines 129, 145, 173, 195, all using `git_repo` fixture.
4. **Imports in scope:** CONFIRMED. `subprocess` at line 11, `WorktreeTeardownError` at line 139.

## Pre-edit Test Run

```
5 failed, 452 passed, 1 warning in 12.22s
```

Carry-over failures (all pre-existing):
- `tests/test_decisions.py::TestLoadPhrases::test_loads_phrases_from_file`
- `tests/test_decisions.py::TestLoadPhrases::test_includes_known_phrases`
- `tests/test_decisions.py::TestLoadPhrases::test_splits_slash_alternatives`
- `tests/test_decisions.py::TestExtractDecisionBlocks::test_s_class_blocks_from_ground_truth`
- `tests/test_runner_parser.py::test_run_step_timeout`

## Post-edit Test Run

```
5 failed, 455 passed, 1 warning in 8.56s
```

Delta: +3 passes (452 → 455), same 5 carry-over failures, zero new failures.

All 17 worktree tests pass individually (`tests/test_worktree.py`: 17 passed in 1.97s), including:
- 4 existing teardown tests: PASS
- 3 new tests: PASS

---

## Output Receipt
**Agent:** Bellows Developer
**Step:** 1
**Status:** Complete

### What Was Done
Replaced the bare `except Exception: commit_shas = []` in `_teardown_worktree` step (b) with a land-or-raise contract: raise `WorktreeTeardownError` on git-log exception or non-zero returncode, while preserving the legitimate-empty path (returncode 0, no commits). Added 3 regression tests.

### Files Deposited
- `knowledge/development/teardown-b-raise-on-log-failure-2026-06-05.md` — this dev log

### Files Created or Modified (Code)
- `bellows.py` — step (b) in `_teardown_worktree` replaced with raise-on-failure contract
- `tests/test_worktree.py` — added `test_teardown_raises_on_git_log_exception`, `test_teardown_raises_on_git_log_nonzero`, `test_teardown_proceeds_on_empty_commit_list`

### Decisions Made
- Used `OSError` as the simulated exception in the git-log-exception test (matches real-world subprocess failure modes)
- Placed new tests between the existing conflict test and the retry test, maintaining the teardown→create ordering in the file

### Flags for CEO
- None

### Flags for Next Step
- The 5 carry-over failures are pre-existing and unrelated to this change
- The legitimate-empty test (`test_teardown_proceeds_on_empty_commit_list`) is the critical negative test — QA should verify it passes to confirm the empty-case path was not broken
