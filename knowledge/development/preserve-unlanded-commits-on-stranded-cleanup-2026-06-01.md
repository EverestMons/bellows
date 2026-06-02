# Dev Log — Preserve Un-Landed Commits on Stranded-Worktree Cleanup (Gap 2a)

**Date:** 2026-06-01
**Plan:** `executable-preserve-unlanded-commits-on-stranded-cleanup-2026-06-01`
**Step:** 1 (DEV)

---

## Guard Placement

The preserve-before-destroy guard is inserted at the TOP of the `if os.path.exists(wt_path):` stranded-cleanup block in `_create_worktree` (`bellows.py`), immediately AFTER the existing `stranded worktree found` WARN log (line 813) and BEFORE the `git worktree remove --force` call (now line 846).

### Before (pre-edit)

```python
    if os.path.exists(wt_path):
        _log("WARN", f"⚠ stranded worktree found at {wt_path}, removing before re-creation", slug=slug)
        try:
            subprocess.run(
                ["git", "--no-pager", "worktree", "remove", "--force", wt_path],
                cwd=project_path, capture_output=True, text=True, timeout=10,
            )
```

### After (post-edit)

```python
    if os.path.exists(wt_path):
        _log("WARN", f"⚠ stranded worktree found at {wt_path}, removing before re-creation", slug=slug)
        # --- Gap 2a: preserve un-landed commits before stranded-cleanup ---
        try:
            wt_head_result = subprocess.run(
                ["git", "--no-pager", "-C", wt_path, "rev-parse", "--verify", "HEAD"],
                capture_output=True, text=True, timeout=10,
            )
        except Exception:
            wt_head_result = None
        if wt_head_result and wt_head_result.returncode == 0:
            wt_head = wt_head_result.stdout.strip()
            try:
                ancestor_result = subprocess.run(
                    ["git", "--no-pager", "-C", project_path, "merge-base", "--is-ancestor", wt_head, "main"],
                    capture_output=True, text=True, timeout=10,
                )
                already_landed = (ancestor_result.returncode == 0)
            except Exception:
                already_landed = False  # fail-safe: preserve under uncertainty
            if not already_landed:
                ts = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
                branch_name = f"bellows-preserved/{slug}-{ts}"
                try:
                    br_result = subprocess.run(
                        ["git", "--no-pager", "-C", project_path, "branch", branch_name, wt_head],
                        capture_output=True, text=True, timeout=10,
                    )
                    if br_result.returncode == 0:
                        _log("WARN", f"⚠ preserved un-landed worktree commits at {wt_head} on branch {branch_name} before stranded-cleanup", slug=slug)
                    else:
                        _log("ERROR", f"⚠ failed to create preservation branch {branch_name} for worktree HEAD {wt_head}: {br_result.stderr.strip()}", slug=slug)
                except Exception as e:
                    _log("ERROR", f"⚠ failed to create preservation branch {branch_name} for worktree HEAD {wt_head}: {e}", slug=slug)
        try:
            subprocess.run(
                ["git", "--no-pager", "worktree", "remove", "--force", wt_path],
```

---

## Detection Predicate

**Un-landed = NOT reachable from local `main`.**

1. Resolve the worktree HEAD: `git -C <wt_path> rev-parse --verify HEAD`. If this fails → nothing to preserve, skip.
2. If HEAD resolved, check: `git -C <project_path> merge-base --is-ancestor <wt_head> main`.
   - `returncode == 0` → already landed on main → skip preservation.
   - Any other outcome → treat as un-landed → preserve.

## Fail-Safe Bias Rules

Preservation is SKIPPED only when:
- HEAD is unreadable / `wt_path` is not a valid worktree (nothing recoverable), OR
- The `merge-base --is-ancestor` check cleanly returns 0 (definitively already landed).

ALL other outcomes (non-zero return, exception, unresolvable `main`) → create the preservation branch. This is a data-safety cut: every uncertainty biases to PRESERVE, never to destroy silently.

## Preservation Branch Naming

Pattern: `bellows-preserved/{slug}-{UTC-timestamp}`

Example: `bellows-preserved/my-plan-slug-20260601T143022Z`

Timestamp uses `time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())` since `timezone` is not imported in this module.

---

## Pre-Edit Verification Query Results

### Query 1 — stranded-cleanup block structure
```
792:def _create_worktree(project_path: str, slug: str) -> str:
812:    if os.path.exists(wt_path):
813:        _log("WARN", f"⚠ stranded worktree found at {wt_path}, removing before re-creation", slug=slug)
816:                ["git", "--no-pager", "worktree", "remove", "--force", wt_path],
821:        shutil.rmtree(wt_path, ignore_errors=True)
```
**CONFIRMED** — def, exists guard, WARN, remove --force, rmtree all present in one contiguous region.

### Query 2 — detached HEAD creation
```
831:        cmd = ["git", "--no-pager", "worktree", "add", wt_path, "HEAD", "--detach"]
```
**CONFIRMED** — present after the stranded-cleanup block. NOT edited.

### Query 3 — imports and scope
`_create_worktree` uses `subprocess`, `shutil`, `os`, `_log`, and `time` — all in scope. No ledger/verdict handle reachable. `from datetime import datetime` and `import time` both at module top. Used `time.strftime` for timestamp since `timezone` is not imported.

### Query 4 — test file fixture style
`tests/test_worktree.py` exists with `git_repo` fixture (real git repo init + commit), imports `_create_worktree` from `bellows`, uses `subprocess.run` for git commands. New tests mirror this style.

---

## Regression Tests

Three new tests added at the end of `tests/test_worktree.py`:

### 1. `test_stranded_cleanup_preserves_unlanded_commits`
- Sets up worktree with un-landed commit (ahead of main)
- Calls `_create_worktree` again (triggers stranded-cleanup)
- Asserts: (a) `bellows-preserved/<slug>-*` branch exists; (b) branch points at captured `wt_head`; (c) `wt_head` is still reachable; (d) worktree was removed and recreated (new HEAD == main HEAD)

### 2. `test_stranded_cleanup_no_preserve_when_already_landed`
- Sets up worktree with HEAD == main HEAD (no new commits)
- Calls `_create_worktree` again
- Asserts: NO `bellows-preserved/*` branch created; worktree recreated normally

### 3. `test_stranded_cleanup_failsafe_preserves_when_main_unresolvable`
- Sets up worktree with a real commit, then deletes the `main` branch from the project repo
- Calls `_create_worktree` (merge-base check cannot resolve `main`)
- Asserts: `bellows-preserved/<slug>-*` branch IS created (fail-safe bias); branch points at `wt_head`; `_create_worktree` returns valid path without raising

All three tests clean up `bellows-preserved/*` branches in their `finally` blocks to prevent leakage.

---

## Test Results

### Pre-edit baseline
```
5 failed, 437 passed, 1 warning in 6.87s
```
Known carry-over failures:
- `tests/test_decisions.py::TestLoadPhrases::test_loads_phrases_from_file`
- `tests/test_decisions.py::TestLoadPhrases::test_includes_known_phrases`
- `tests/test_decisions.py::TestLoadPhrases::test_splits_slash_alternatives`
- `tests/test_decisions.py::TestExtractDecisionBlocks::test_s_class_blocks_from_ground_truth`
- `tests/test_runner_parser.py::test_run_step_timeout`

### Post-edit
```
5 failed, 440 passed, 1 warning in 6.75s
```
3 new tests PASS. ZERO new failures. Same 5 carry-over failures as baseline.

---

## Anchor Verification

```
grep -n "bellows-preserved/" bellows.py
834:                branch_name = f"bellows-preserved/{slug}-{ts}"

grep -n "merge-base.*--is-ancestor" bellows.py
826:                    ["git", "--no-pager", "-C", project_path, "merge-base", "--is-ancestor", wt_head, "main"],

grep -n "rev-parse.*--verify.*HEAD" bellows.py
817:                ["git", "--no-pager", "-C", wt_path, "rev-parse", "--verify", "HEAD"],
```

`git diff -- bellows.py` touches ONLY the inside-top of the `if os.path.exists(wt_path):` block in `_create_worktree` (lines 814–845 added). `_teardown_worktree`, `_consume_verdicts`, and the `worktree add ... HEAD --detach` recreate line are byte-unchanged.

---

## Output Receipt
**Agent:** Bellows Developer
**Step:** 1
**Status:** Complete

### What Was Done
Added a preserve-before-destroy guard to `_create_worktree` in `bellows.py` that detects un-landed commits on a stranded worktree's detached HEAD and creates a `bellows-preserved/{slug}-{ts}` branch pointing at that HEAD before the existing force-remove/rmtree/prune cleanup runs. Added three regression tests covering preservation (positive), no-preserve-when-landed (specificity), and fail-safe-under-uncertainty.

### Files Deposited
- `knowledge/development/preserve-unlanded-commits-on-stranded-cleanup-2026-06-01.md` — this dev log

### Files Created or Modified (Code)
- `bellows.py` — added 32-line preserve guard at top of stranded-cleanup block in `_create_worktree`
- `tests/test_worktree.py` — added 3 regression tests for Gap 2a preserve behavior

### Decisions Made
- Used `time.strftime` for UTC timestamp rather than `datetime` since `timezone` is not imported in this module
- Tests clean up `bellows-preserved/*` branches in `finally` blocks rather than a shared fixture, matching the module's existing per-test cleanup pattern

### Flags for CEO
- None

### Flags for Next Step
- The guard is in place; QA should verify the fail-safe bias logic (preservation skipped ONLY on clean ancestor-check return 0 or unreadable HEAD) and confirm no out-of-scope code was touched
- Daemon restart required to activate the guard for future plans
