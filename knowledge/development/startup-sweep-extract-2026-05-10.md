# Dev Log — Extract `_perform_startup_sweep` from `Bellows.start()`

**Date:** 2026-05-10
**Plan:** executable-startup-sweep-extract-2026-05-10
**Step:** 1 (DEV)

---

## 1. Edits Made

### Edit 1 — `bellows/bellows.py` (new method)

Added `_perform_startup_sweep(self) -> list[str]` method to the `Bellows` class, placed between `_consume_verdicts` (line ~1059) and `start` (line ~1096). Body is a faithful move of the inline sweep logic from `start()`. Returns `orphaned_removed` list. No print statements inside the method (prints stay in `start()`).

### Edit 2 — `bellows/bellows.py` (call site simplification)

Replaced the inline sweep block in `start()` (~25 lines: `active_slugs = set()` through `orphaned_removed.append(pf)`) with a single call:

```python
orphaned_removed = self._perform_startup_sweep()
```

The print block (`if orphaned_removed: print(...)`) remains in `start()`, reading from the returned list.

### Edit 3 — `tests/test_consume_verdicts.py` (test migration)

Replaced the 26-line inline replica in `test_startup_sweep_removes_done_plan_orphans` with:

```python
with patch("bellows.BELLOWS_ROOT", tmp_path):
    orphaned_removed = b._perform_startup_sweep()
```

Removed the `NOTE: Done/ loop intentionally absent` comment (no longer applicable). Both existing assertions preserved unchanged.

## 2. LOC Delta

| File | Added | Removed | Net |
|------|-------|---------|-----|
| `bellows.py` | 30 | 17 | +13 |
| `tests/test_consume_verdicts.py` | 1 | 28 | −27 |
| **Total** | **31** | **45** | **−14** |

Net reduction of 14 lines. Diagnostic predicted ~−24; the difference is the 8-line docstring on the new method (new content, not moved). Core logic reduction matches expectations.

## 3. Test Suite Result

- **214 passed**, 1 failed
- Pre-existing failure: `test_run_step_timeout` (known, unrelated to this refactor)
- New failures: **0**

## 4. Spot Check

The `Bellows` constructor runs successfully with the test config (confirmed by all 6 `test_consume_verdicts.py` tests passing — each constructs a `Bellows` instance). The `_perform_startup_sweep()` method returns `[]` when no orphans exist and correctly returns removed filenames when orphans are present (verified by `test_startup_sweep_removes_done_plan_orphans`).

## 5. Commit SHA

`783eea7`
