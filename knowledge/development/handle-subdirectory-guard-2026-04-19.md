# Dev Log: _handle Subdirectory Guard

**Date:** 2026-04-19
**Plan:** executable-handle-subdirectory-guard-2026-04-19
**Status:** Complete

## Changes

### bellows.py — `_handle()` (L452–455)

Inserted a subdirectory guard at the start of `PlanHandler._handle()`. The guard resolves the parent directory of the incoming path and checks it against the orchestrator's `watched_projects` list. If the path's parent is not a watched directory (e.g. `decisions/Done/`), the method returns immediately, preventing re-dispatch of plans moved to subdirectories.

```python
path_parent = str(Path(path).parent)
watched = self.orchestrator.config.get("watched_projects", [])
if path_parent not in watched:
    return
```

### tests/test_bellows.py — Updated Existing Tests

Updated 7 existing tests to set `mock_orch.config = {"watched_projects": [...]}` so the guard's `.config.get("watched_projects", [])` resolves to a real list instead of a MagicMock:

- `test_rescan_preserves_seen`
- `test_handle_parallel_from_watchdog_adds_pending_not_dispatched`
- `test_rescan_dispatches_pending_group_after_settle`
- `test_rescan_does_not_dispatch_pending_group_within_settle`
- `test_nonparallel_plan_dispatches_immediately_from_handle`
- `test_two_parallel_siblings_collected_as_one_group`
- `test_on_moved_dispatches_for_non_directory_event`

### tests/test_bellows.py — New Tests Added

- `test_on_moved_dispatches_for_top_level_dest` — verifies on_moved dispatches _handle for dest_path in watched dir
- `test_on_moved_rejects_subdirectory_dest` — verifies guard rejects Done/ subdirectory dest (handle_new_plan NOT called)
- `test_on_moved_dispatches_same_directory_rename` — verifies on_moved dispatches _handle for same-dir rename

## Files Created or Modified (Code)

- `bellows.py` — guard insertion in `_handle()` at L452–455
- `tests/test_bellows.py` — 7 test fixture updates + 3 new tests

## Test Counts

- Before: 39 tests
- After: 42 tests (3 added)
- All 42 passed

## Commit

SHA: fb1d5f3
Message: `fix: guard _handle against subdirectory dispatch (on_moved re-run cascade)`
