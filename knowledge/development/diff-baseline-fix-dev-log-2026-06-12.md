# Per-Plan Diff Baseline Fix — Dev Log
**Date:** 2026-06-12 | **Plan:** 28 | **Agent:** Bellows Developer

---

## Edits

### bellows.py
- **Line 534** (was: `pre_diff = _capture_git_diff(wt_path)`): Added `plan_baseline_sha` variable with comment documenting per-plan isolation intent. `pre_diff` set from `plan_baseline_sha`.
- **Lines 826-858** (`_parse_diff_stat`): Changed diff command to use `post_diff` when non-empty. When `post_diff` is provided, runs `git diff --stat pre_diff post_diff -- .` (two-commit diff, isolates from concurrent plan changes). When `post_diff` is empty, falls back to `git diff --stat pre_diff -- .` (working-tree diff, backward-compatible). Updated docstring to reflect new semantics.

### tests/test_bellows.py
- **Lines 647-743** (new section: "Per-plan diff baseline fix"): Added 3 integration tests using real git repos:
  1. `test_parse_diff_stat_excludes_concurrent_plan_changes` — verifies files committed by a concurrent plan after post_diff capture do NOT appear in files_changed
  2. `test_parse_diff_stat_includes_own_step_changes_with_post_diff` — verifies the plan's own committed changes between pre_diff and post_diff DO appear
  3. `test_parse_diff_stat_multistep_per_step_isolation` — verifies step 2's files_changed only reflects step 2's changes, not step 1's

## Test Counts
- **Before:** 535
- **After:** 538 (+3 new)

## Suite Tail (final 15 lines)
```
tests/test_verdict.py .......................................            [ 95%]
tests/test_worktree.py .......................                           [100%]

=============================== warnings summary ===============================
../../../../../Library/Python/3.9/lib/python/site-packages/urllib3/__init__.py:35
  /Users/marklehn/Library/Python/3.9/lib/python/site-packages/urllib3/__init__.py:35: NotOpenSSLWarning: urllib3 v2 only supports OpenSSL 1.1.1+, currently the 'ssl' module is compiled with 'LibreSSL 2.8.3'. See: https://github.com/urllib3/urllib3/issues/3020
    warnings.warn(

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
======================== 538 passed, 1 warning in 9.88s ========================
```

## Mechanism Summary
The root cause (diagnostic 27, Section 1): `_parse_diff_stat` diffed from `pre_diff` SHA to the live working tree via `git diff --stat <pre_diff> -- .`. In in-place execution mode (no worktree isolation), concurrent plan commits between `pre_diff` capture and gate evaluation appeared in the diff, contaminating `files_changed` with foreign plan artifacts.

The fix makes `_parse_diff_stat` use its previously-unused `post_diff` parameter: when non-empty, the diff command becomes `git diff --stat <pre_diff> <post_diff> -- .`, scoping the diff to committed changes between two captured SHAs. Concurrent plan commits that land after `post_diff` capture are excluded. The fallback to working-tree diff when `post_diff` is empty preserves backward compatibility.

**Acknowledged limitation** (per diagnostic Section 4, Option A): concurrent plan commits that occur DURING a step's execution window (between pre_diff and post_diff captures) are still included, since both SHAs bracket the concurrent commit. Full isolation requires worktree mode.

---

## Output Receipt
**Agent:** Bellows Developer
**Step:** 1
**Status:** Complete

### What Was Done
Implemented per-plan diff baseline fix (diagnostic 27, Option A). Changed `_parse_diff_stat` to use the `post_diff` parameter for two-commit diffing, isolating each step's `files_changed` from concurrent plan commits that land after the step completes. Added 3 integration tests covering concurrent exclusion, own-change inclusion, and multi-step per-step isolation.

### Files Deposited
- `knowledge/development/diff-baseline-fix-dev-log-2026-06-12.md` — this dev log

### Files Created or Modified (Code)
- `bellows.py` — `_parse_diff_stat`: use `post_diff` for two-commit diff; added `plan_baseline_sha` variable at dispatch start
- `tests/test_bellows.py` — 3 new integration tests for concurrent plan isolation

### Decisions Made
- Used `post_diff` parameter (previously unused) rather than adding a new function or parameter — smallest blast radius
- Kept per-step `pre_diff` re-capture at line 644 unchanged — in worktree mode the worktree branch provides isolation, in in-place mode the re-capture advances past between-step concurrent commits
- Backward-compatible: empty `post_diff` falls back to working-tree diff

### Flags for CEO
- DAEMON RESTART REQUIRED after plan close (new `_parse_diff_stat` behavior takes effect on restart)

### Flags for Next Step
- QA should verify the `_capture_git_diff` callsites at bellows.py lines 534, 576, 644, 686 all pass through `_parse_diff_stat` with non-empty `post_diff`
- QA should verify diagnostic Section 5 Verification Block: `grep -n "rev-parse HEAD" bellows.py` still returns the expected line
