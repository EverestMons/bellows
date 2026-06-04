# Dev Log — Invalidate _seen on Re-Deposit via on_created / on_moved (#7)

**Date:** 2026-06-04
**Plan:** executable-seen-invalidate-on-created-moved-2026-06-04
**Step:** 1 (DEV)

---

## Pre-Edit Verification Results

| # | Claim | Query | Result |
|---|-------|-------|--------|
| 1 | `on_modified` has inline `_seen` invalidation; `on_created`/`on_moved` do not | Grep callbacks + LIFECYCLE_PREFIXES | Confirmed: `on_modified` (L1194) has inline invalidation with `LIFECYCLE_PREFIXES` guard; `on_created` (L1190) is bare `_handle(event.src_path)`; `on_moved` (L1207) is bare `_handle(event.dest_path)` |
| 2 | `_handle` has `_seen` guard; reachable from `_rescan` | Grep `_handle`, `_seen`, `from_rescan` | Confirmed: `_seen` guard at L1166; `from_rescan=True` call at L1297 |
| 3 | Two existing tests mirror-template present | Grep test names | Confirmed: L3267 `test_on_modified_invalidates_seen_for_runnable_plan`, L3295 `test_on_modified_preserves_seen_for_lifecycle_renames` |
| 4 | `os`, `verdict`, `_log`, `slug_for` in scope | Grep imports + definitions | Confirmed: `os` (L6), `verdict` (L149), `_log` (L66), `slug_for` (L93) |

---

## Helper Body — `_invalidate_seen_on_redeposit`

```python
def _invalidate_seen_on_redeposit(self, path: str):
    # Invalidate _seen on a re-deposit at an already-seen slug so a genuinely new plan
    # file (e.g. a follow-on executable deposited at the same base slug after the prior
    # plan was closed OUT-OF-BAND via a Planner-direct move to Done/, which the daemon
    # never observes) can be re-dispatched. Guard: never invalidate on Bellows-managed
    # lifecycle renames (in-progress-/verdict-pending-/halted-) — that would loop.
    filename = os.path.basename(path)
    LIFECYCLE_PREFIXES = ("in-progress-", "verdict-pending-", "halted-")
    if any(filename.startswith(p) for p in LIFECYCLE_PREFIXES):
        return
    slug = verdict.slug_from_path(path)
    if slug in self.orchestrator._seen:
        self.orchestrator._seen.discard(slug)
        _log("INFO", f"re-deposit at seen slug — invalidated _seen so plan can re-dispatch", slug=slug_for(filename))
```

---

## Wired Callbacks

```python
def on_created(self, event):
    if not event.is_directory:
        self._invalidate_seen_on_redeposit(event.src_path)
        self._handle(event.src_path)

def on_modified(self, event):
    if not event.is_directory:
        self._invalidate_seen_on_redeposit(event.src_path)
        self._handle(event.src_path)

def on_moved(self, event):
    if not event.is_directory:
        self._invalidate_seen_on_redeposit(event.dest_path)
        self._handle(event.dest_path)
```

---

## `_handle` and Rescan Path — Byte-Unchanged

Confirmed `_handle` (L1153) still contains the `_seen` guard at L1166 (`if verdict.slug_from_path(path) in self.orchestrator._seen: return`) and is NOT modified. No invalidation added inside `_handle` or the `_rescan` sweep (L1297). The invalidation lives exclusively in the watcher callbacks via the shared helper.

---

## Lifecycle Guard Parity

The `LIFECYCLE_PREFIXES` tuple is exactly `("in-progress-", "verdict-pending-", "halted-")` in the new helper, matching the prior inline version in `on_modified`. The guard logic is preserved verbatim — early-return on any lifecycle prefix match.

---

## Test Results

### Pre-Edit Baseline
- **448 total** (including 4 tests not yet written): N/A
- **Actual:** 444 passed, 5 failed (carry-over)
- Carry-over failures: 4x `test_decisions.py` (missing `INTERMEDIATE_DECISION_PHRASES.md`), 1x `test_runner_parser.py::test_run_step_timeout`

### Post-Edit
- **448 passed, 5 failed** (same 5 carry-over)
- Delta: +4 new tests all passing
- 2 existing `on_modified` tests still green

### New Tests Added
1. `test_on_created_invalidates_seen_for_runnable_plan` — PASSED
2. `test_on_created_preserves_seen_for_lifecycle_renames` — PASSED
3. `test_on_moved_invalidates_seen_for_runnable_plan` — PASSED
4. `test_on_moved_preserves_seen_for_lifecycle_renames` — PASSED

### Existing Tests Preserved
1. `test_on_modified_invalidates_seen_for_runnable_plan` — PASSED (unchanged)
2. `test_on_modified_preserves_seen_for_lifecycle_renames` — PASSED (unchanged)

---

## Output Receipt
**Agent:** Bellows Developer
**Step:** 1
**Status:** Complete

### What Was Done
Extracted the inline `_seen`-invalidation logic from `on_modified` into a new `PlanHandler._invalidate_seen_on_redeposit(self, path)` helper method. Wired all three watcher callbacks (`on_created`, `on_modified`, `on_moved`) to call the helper before `_handle`. Added 4 regression tests mirroring the existing `on_modified` pair for the create and move paths.

### Files Deposited
- `knowledge/development/seen-invalidate-on-created-moved-2026-06-04.md` — this dev log

### Files Created or Modified (Code)
- `bellows.py` — added `_invalidate_seen_on_redeposit` helper; rewired `on_created`, `on_modified`, `on_moved` to call it
- `tests/test_bellows.py` — added 4 new regression tests for create/move `_seen` invalidation

### Decisions Made
- Added a `_log("INFO", ...)` line in the helper that fires only on actual discard (per plan spec) — the only behavioral addition vs the prior inline logic

### Flags for CEO
- None

### Flags for Next Step
- `_handle` and the rescan path are byte-unchanged — QA can verify via diff
- Pre-edit baseline: 444 passed / 5 failed; post-edit: 448 passed / 5 failed — same carry-over failures
