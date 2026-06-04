# Dev Log — Re-Attempt Recoverable Dirty-Tree Teardown on Continue-Resume (Gap 1c)

**Date:** 2026-06-04
**Plan:** executable-reattempt-teardown-on-continue-resume-2026-06-04
**Step:** 1 (DEV)

## Summary

Added `_retry_recoverable_teardown()` helper to `bellows.py` and a call site at the top of the `if v == "continue":` branch in `_consume_verdicts`, immediately before the existing Gap-1b halt guard. The helper re-attempts a worktree teardown when the prior step's failure was the dirty-tree variant only. On success, it clears the `worktree_teardown` failure from `gate_result["failures"]` so the normal continue/advance proceeds. On any skip or failure, it leaves the failure for the Gap-1b guard to halt.

## Helper Placement

`_retry_recoverable_teardown` is placed at module level between `_teardown_worktree` (ends ~line 1041) and `_source_sha` (formerly line 1042, now ~1078). This keeps all teardown-related logic in one region.

## Predicate Order (exact sequence in the helper)

1. **No worktree_teardown failures** → `return False` (nothing to retry)
2. **Worktree directory missing** (`not os.path.isdir(wt_path)`) → log INFO, `return False` (commits are on a `bellows-preserved/*` branch per Gap 2a; Gap-1b halts)
3. **Non-dirty-tree variant** (`not all("worktree_teardown_dirty_tree" in evidence)`) → log INFO, `return False` (content-conflict won't self-heal; Gap-1b halts)
4. **Attempt `_teardown_worktree`:**
   - Success → clear all worktree_teardown failures in place, log EVENT, `return True`
   - `WorktreeTeardownError` → log WARN, `return False` (retry failed; Gap-1b halts)
   - `Exception` → log WARN, `return False` (unexpected error; Gap-1b halts)

The helper never raises and never removes non-worktree_teardown failures.

## Skip Rules

- **Dirty-tree only:** the retry fires ONLY when ALL worktree_teardown failures contain the `worktree_teardown_dirty_tree` token in their evidence. A content-conflict failure skips the retry entirely.
- **Missing worktree:** if the worktree directory doesn't exist (e.g., destroyed by `_create_worktree`'s stranded-cleanup), the retry is skipped. Gap 2a's `bellows-preserved/*` branch preserves the un-landed commits.
- **Repeat failure:** if `_teardown_worktree` raises again on retry, the failure is left in place for Gap-1b.

## Call-Site Location

At the TOP of the `if v == "continue":` branch in `_consume_verdicts`, IMMEDIATELY BEFORE the Gap-1b guard comment. The call reconstructs paths from in-scope values:
- `_c_project_path = os.path.dirname(os.path.dirname(decisions_path))`
- `_c_wt_path = os.path.join(_c_project_path, ".bellows-worktrees", cleanup_slug)`

The existing Gap-1b guard runs UNCHANGED against the possibly-cleared `gate_result["failures"]`.

## Pre-Edit Verification Results

| # | Claim | Query | Result |
|---|-------|-------|--------|
| V1 | Gap-1b guard is first statement in continue branch | grep + read lines 1372-1414 | CONFIRMED — guard at line 1377 |
| V2 | `_teardown_worktree` raises `WorktreeTeardownError("worktree_teardown_dirty_tree: ...")` before cherry-pick | grep + read lines 937-975 | CONFIRMED — raise at line 952, before (c) cherry-pick |
| V3 | `cleanup_slug` matches worktree slug | grep for `cleanup_slug =` and `_create_worktree` slug | CONFIRMED — both use `verdict.slug_from_path` |
| V4 | `project_path = str(plan_p.parents[2])` ≡ `dirname(dirname(decisions_path))` | grep line 375 | CONFIRMED |
| V5 | Module scope has `os`, `subprocess`, `_log`, `_teardown_worktree`, `WorktreeTeardownError` | read imports + definitions | CONFIRMED — all present |

## Pytest Results

### Pre-edit baseline
```
5 failed, 440 passed, 1 warning in 7.88s
```
Known carry-over failures: `test_decisions.py` (3× TestLoadPhrases + 1× TestExtractDecisionBlocks), `test_runner_parser.py::test_run_step_timeout`

### Post-edit
```
5 failed, 444 passed, 1 warning in 7.64s
```
Same 5 carry-over failures. **+4 new tests, all passing.** Zero new failures.

### New tests (all PASSED)
```
tests/test_consume_verdicts.py::test_retry_clears_dirty_tree_teardown_on_success PASSED
tests/test_consume_verdicts.py::test_retry_skips_content_conflict PASSED
tests/test_consume_verdicts.py::test_retry_skips_when_worktree_missing PASSED
tests/test_consume_verdicts.py::test_retry_keeps_failure_when_teardown_raises_again PASSED
```

---

## Output Receipt
**Agent:** Bellows Developer
**Step:** 1
**Status:** Complete

### What Was Done
Added `_retry_recoverable_teardown()` module-level helper to `bellows.py` that re-attempts a recoverable (dirty-tree-only) worktree teardown at verdict-consume time. Added a 6-line call site at the top of the `if v == "continue":` branch, immediately before the Gap-1b halt guard. Added 4 regression tests targeting the helper directly.

### Files Deposited
- `knowledge/development/reattempt-teardown-on-continue-resume-2026-06-04.md` — this dev log

### Files Created or Modified (Code)
- `bellows.py` — added `_retry_recoverable_teardown()` helper (~35 lines near `_teardown_worktree`) and 6-line call site in `_consume_verdicts` continue branch
- `tests/test_consume_verdicts.py` — added 4 regression tests: success/clear, content-conflict skip, missing-worktree skip, retry-still-fails

### Decisions Made
- Placed helper immediately after `_teardown_worktree` definition for locality (specialist authority)
- Used `_c_` prefix for call-site local vars to avoid name collisions in the large `_consume_verdicts` method

### Flags for CEO
- None

### Flags for Next Step
- Pre-edit baseline: 5 failed / 440 passed; post-edit: 5 failed / 444 passed
- The 4 new tests target the helper directly (monkeypatched `_teardown_worktree`) — no live daemon needed
- Existing Gap-1b tests still pass because the helper's `os.path.isdir(wt_path)` check returns False for the tmp dirs used in those tests (worktree doesn't exist) → helper returns False → Gap-1b guard fires as before
