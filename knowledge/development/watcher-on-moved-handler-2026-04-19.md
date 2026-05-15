# Watcher on_moved Handler — Development Log

**Date:** 2026-04-19
**Plan:** executable-watcher-on-moved-handler-2026-04-19

## Summary

Added `on_moved` handler to `PlanHandler` class in `bellows.py`. This fixes BACKLOG #4 (filesystem watcher reliability) — macOS FSEvents fires `on_moved` for same-directory renames, but PlanHandler only overrode `on_created` and `on_modified`, silently dropping rename events.

## Code Change

3-line addition to `bellows.py`, inserted after `on_modified` (line 482-484):

```python
    def on_moved(self, event):
        if not event.is_directory:
            self._handle(event.dest_path)
```

Key design point: reads `event.dest_path` (the destination filename after rename), NOT `event.src_path`. The destination is the new filename that `is_runnable_plan` and `_handle` need to evaluate.

## Tests Added

Two tests added to `tests/test_bellows.py`:

```python
def test_on_moved_dispatches_for_non_directory_event():
    """on_moved must call _handle with event.dest_path for non-directory events."""
    mock_orch = MagicMock()
    handler = bellows.PlanHandler(mock_orch)

    event = MagicMock()
    event.is_directory = False
    event.src_path = "/some/decisions/verdict-pending-foo.md"
    event.dest_path = "/some/decisions/executable-foo.md"

    with patch.object(handler, "_handle") as mock_handle:
        handler.on_moved(event)

    mock_handle.assert_called_once_with("/some/decisions/executable-foo.md")


def test_on_moved_ignores_directory_events():
    """on_moved must NOT call _handle for directory events."""
    mock_orch = MagicMock()
    handler = bellows.PlanHandler(mock_orch)

    event = MagicMock()
    event.is_directory = True
    event.src_path = "/some/decisions/old_dir"
    event.dest_path = "/some/decisions/new_dir"

    with patch.object(handler, "_handle") as mock_handle:
        handler.on_moved(event)

    mock_handle.assert_not_called()
```

## Test Output

```
============================= test session starts ==============================
platform darwin -- Python 3.9.6, pytest-8.4.2, pluggy-1.6.0 -- /Applications/Xcode.app/Contents/Developer/usr/bin/python3
cachedir: .pytest_cache
rootdir: /Users/marklehn/Desktop/GitHub/bellows
plugins: anyio-4.12.1, cov-7.0.0
collecting ... collected 39 items / 37 deselected / 2 selected

tests/test_bellows.py::test_on_moved_dispatches_for_non_directory_event PASSED [ 50%]
tests/test_bellows.py::test_on_moved_ignores_directory_events PASSED     [100%]

================= 2 passed, 37 deselected, 1 warning in 0.13s ==================
```

---

## Output Receipt
**Agent:** Bellows Developer
**Step:** 1
**Status:** Complete

### What Was Done
Added `on_moved` handler to `PlanHandler` in `bellows.py` and two unit tests to `tests/test_bellows.py`. Both tests pass.

### Files Deposited
- `bellows/knowledge/development/watcher-on-moved-handler-2026-04-19.md` — this dev log

### Files Created or Modified (Code)
- `bellows/bellows.py` — added `on_moved` method to `PlanHandler` class (3 lines)
- `bellows/tests/test_bellows.py` — added 2 tests for on_moved handler

### Decisions Made
- Used `event.dest_path` (not `event.src_path`) per diagnostic recommendation

### Flags for CEO
- None

### Flags for Next Step
- Step 2 QA should verify the handler exists, reads dest_path, and both tests pass
