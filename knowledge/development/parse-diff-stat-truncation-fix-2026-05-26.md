# Dev Log: _parse_diff_stat Path Truncation Fix
**Date:** 2026-05-26
**Plan:** executable-parse-diff-stat-truncation-fix-2026-05-26

## Summary

One-parameter change in `_parse_diff_stat` (bellows.py:730) to prevent `git diff --stat` from truncating long file paths with `...` prefixes.

## Root Cause

`git diff --stat` defaults to ~80-column terminal width and truncates filenames longer than the column allocation with a `...` prefix. The bellows code invoked git without specifying a column width, so any file path exceeding git's default budget was truncated. The truncated string was then fed to `_gate_scope_check` verbatim, causing false-positive scope_check trips on two plans this session.

## Change

**File:** `bellows.py` line 730

**Before:**
```python
["git", "--no-pager", "diff", "--stat", "--relative", pre_diff, "--", "."],
```

**After:**
```python
["git", "--no-pager", "diff", "--stat=300", "--relative", pre_diff, "--", "."],
```

## Why 300

Empirically verified this session: `git --no-pager diff --stat=300 --relative HEAD~2 -- .` produces full untruncated paths in the bellows worktree. 300 chars accommodates any plausible nested-project path including governance-root absolute paths up to ~280 chars plus padding. Going higher is harmless but unnecessary.

## Impact

- Fixes false-positive `scope_check` trips caused by `...`-prefixed truncated paths in the `files_changed` list
- Affects `_gate_scope_check` and `_gate_file_change_audit` downstream consumers
- No change to function signature, return shape, or any other code path

---
## Output Receipt
**Agent:** Bellows Developer
**Step:** 1
**Status:** Complete

### What Was Done
Changed `--stat` to `--stat=300` in the `_parse_diff_stat` git subprocess invocation at bellows.py:730. This prevents git's default ~80-column path truncation that caused false-positive scope_check gate trips on long file paths.

### Files Deposited
- `knowledge/development/parse-diff-stat-truncation-fix-2026-05-26.md` — this dev log

### Files Created or Modified (Code)
- `bellows.py` — changed `--stat` to `--stat=300` at line 730 in `_parse_diff_stat`

### Decisions Made
- Used 300 as the column width (empirically verified, accommodates paths up to ~280 chars)

### Flags for CEO
- None

### Flags for Next Step
- QA should verify with `grep -n "stat=300" bellows.py` and run `pytest tests/test_bellows.py -k parse_diff_stat -v`
