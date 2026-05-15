# Output Receipt — PlanHandler._seen Slug Refactor

**Date:** 2026-05-11
**Plan:** `executable-plan-handler-seen-slug-refactor-2026-05-11`
**Step:** 1 (BELLOWS_DEV)

---

## Files Created or Modified (Code)

| File | Change |
|------|--------|
| `bellows.py` | Moved `_seen` from `PlanHandler.__init__` to `Bellows.__init__`; re-keyed all 8 access sites from path to slug via `verdict.slug_from_path()`; added `bellows=None` parameter to `run_plan` and passed `bellows=self` from `_run_tracked`; added `discard()` calls at 3 lifecycle terminal events (auto-close, continue-to-done, halt) |

## Files Created or Modified (Tests)

| File | Change |
|------|--------|
| `tests/test_bellows.py` | Added `import verdict`; updated 8 existing tests to use slug-keyed `_seen` on orchestrator (`mock_orch._seen = set()`); added 4 new regression tests |

## Files Created (Knowledge)

| File | Purpose |
|------|---------|
| `bellows/knowledge/development/plan-handler-seen-slug-refactor-2026-05-11.md` | This dev log |

## Commits

| # | SHA | Message |
|---|-----|---------|
| 1 | `63dd6ed` | `fix(bellows): re-key _seen by slug, move ownership to Bellows, clear on lifecycle events` |
| 2 | `130649b` | `test(bellows): regression tests for _seen slug-keying and lifecycle discards` |
| 3 | *(this commit)* | `docs: dev log for _seen slug refactor` |

## Test Results

| Metric | Before | After |
|--------|--------|-------|
| Total passed | 97 | 101 |
| Total failed | 0 | 0 |

**New test names:**
- `test_seen_uses_slug_not_path`
- `test_seen_dispatch_window_guard_holds`
- `test_seen_cleared_on_continue_to_done`
- `test_seen_cleared_on_halt`

## Constraints Verified

- **Dispatch-window guard preserved:** `_seen.add()` calls remain in `PlanHandler._handle` at all original sites — the 2-second stagger race-window guard is intact. Verified by `test_seen_dispatch_window_guard_holds`.
- **No new threading primitives:** No locks, semaphores, or conditions added. GIL atomicity on `set.add`/`set.discard` is sufficient.
- **`verdict.slug_from_path` unchanged:** Zero edits to `verdict.py`.

## Status: Complete
