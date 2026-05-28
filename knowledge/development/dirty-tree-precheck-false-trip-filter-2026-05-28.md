# Dirty-Tree Pre-Check False-Trip Filter — DEV Log

**Date:** 2026-05-28 | **Plan:** executable-dirty-tree-precheck-false-trip-filter-2026-05-28 | **Step:** 1 (DEV)

---

## What Was Done

Implemented the lifecycle-artifact filter for the `worktree_teardown_dirty_tree` pre-check per the diagnostic spec at `knowledge/research/dirty-tree-precheck-false-trip-surface-2026-05-28.md` Section 3.

### Implementation 1 — `_LIFECYCLE_IGNORE_RE` and `_is_lifecycle_artifact()`

- **Location:** `bellows.py` lines 32-51
- `_LIFECYCLE_IGNORE_RE` definition: lines 36-40
- `_is_lifecycle_artifact()` function: lines 43-51
- Placed between the misplaced-verdict-scan constants and the terminal output infrastructure section
- Regex is byte-for-byte faithful to the diagnostic Section 3 spec

### Implementation 2 — Pre-check filter integration

- **Location:** `bellows.py` lines 885-916 (modified pre-check block)
- Replaced blanket `if dt_result.stdout.strip()` predicate with filter pass:
  - `dirty_lines = dt_result.stdout.strip().splitlines()`
  - `blocking_lines = [line for line in dirty_lines if not _is_lifecycle_artifact(line)]`
  - `if blocking_lines:` — only raises `WorktreeTeardownError` for non-lifecycle dirty files
- Evidence string updated:
  - Count uses `len(blocking_lines)` (not total `dirty_lines`)
  - Added filtered-count annotation line
- Recovery instructions (Sub-variant A / Sub-variant B) unchanged
- Fail-open behavior on `git status` subprocess failure unchanged

### Evidence string format (final)

```
worktree_teardown_dirty_tree: local main has uncommitted changes that would conflict with cherry-pick from worktree.

Dirty files in local main ({len(blocking_lines)} blocking file(s)):
{dirty_display}
({len(dirty_lines) - len(blocking_lines)} lifecycle artifacts filtered, {len(blocking_lines)} blocking file(s) remain)

Recovery (choose based on dirty-file type):
  Sub-variant A — ...
  Sub-variant B — ...
  Then: re-issue continue verdict to retry teardown.
  Reference: LESSONS.md 2026-05-27 R2 recovery shape.
```

### Confirmations

- `import re` already present at line 8 — no addition needed
- `_create_worktree` was NOT modified (confirmed via `git diff` — zero matches)
- Copy-back logic at lines 939-960 was NOT modified
- `python3 -c "import bellows; print('ok')"` → `ok`

---

## Output Receipt
**Agent:** Bellows Developer
**Step:** 1
**Status:** Complete

### What Was Done
Added `_LIFECYCLE_IGNORE_RE` regex and `_is_lifecycle_artifact()` predicate to `bellows.py` (lines 32-51). Modified the `_teardown_worktree` pre-check block (lines 885-916) to filter lifecycle artifacts before the blocking predicate. Evidence string updated with filtered-count annotation.

### Files Deposited
- `knowledge/development/dirty-tree-precheck-false-trip-filter-2026-05-28.md` — this DEV log

### Files Created or Modified (Code)
- `bellows.py` — added lifecycle filter (lines 32-51), modified pre-check block (lines 885-916)

### Decisions Made
- Placed regex/helper at module level between misplaced-verdict-scan and terminal-output sections (existing code organization pattern)
- Used `"\n".join(blocking_lines)` for display instead of raw `dirty_output` to ensure only blocking lines appear in the evidence

### Flags for CEO
- None

### Flags for Next Step
- Existing tests `test_teardown_pauses_when_local_main_dirty` and `test_teardown_dirty_tree_evidence_contains_recovery_commands` use non-lifecycle paths (`PROJECT_STATUS.md`, `untracked.md`) — should pass without fixture updates, but QA should verify
- The `untracked.md` path in `test_teardown_dirty_tree_evidence_contains_recovery_commands` does NOT match the lifecycle filter (it's not under `knowledge/decisions/` or `verdicts/`) — test remains valid
