# Cycle-Nudge Trigger — Dev Log

**Date:** 2026-07-06
**Plan:** 129 (diagnostic-127 gap 2)
**Agent:** Bellows Developer

---

## Summary

Implemented the cycle-nudge trigger: a mechanical counter that compares plans closed since last lessons-forge ingestion against a configurable threshold, firing a Pushover notification when the learning loop goes dormant.

---

## Changes

### Change 1 — config.json (gitignored)

Added `cycle_nudge` block and `notifications.events.cycle_nudge` flag:

```json
"cycle_nudge": {
  "enabled": true,
  "plans_closed_threshold": 10,
  "interval_hours": 24
},
```

```json
"notifications": {
  "events": {
    ...
    "cycle_nudge": true
  }
}
```

Config reads use safe defaults: absent `cycle_nudge` block → disabled (enabled defaults to `False`).

### Change 2 — evaluator (bellows.py)

Two module-level functions:

**`_get_last_ingestion_ts()`** — reads `MAX(ingested_at)` from lessons-forge.db via read-only URI (`file:...?mode=ro`). Returns `None` on any failure (missing DB, missing table).

**`_count_plans_closed_since(since_ts)`** — queries lifecycle.db `SELECT COUNT(*) FROM plans WHERE lifecycle_state = 'closed' AND closed_at > ?`. When `since_ts` is `None`, counts all closed plans. Returns 0 on any failure.

Both functions catch all exceptions, log a WARN, and return a safe default — never raise into the rescan loop.

### Change 3 — cadence + suppression (bellows.py)

**Instance state** added to `Bellows.__init__`:
- `_cycle_nudge_last_eval: float = 0.0` — last evaluation epoch
- `_cycle_nudge_suppressed_ts: Optional[str] = None` — ingestion timestamp at fire time

**`_evaluate_cycle_nudge()`** method:
1. Checks `cycle_nudge.enabled` (absent → disabled)
2. Interval gate: skips if `now - last_eval < interval_hours * 3600`
3. Reads `MAX(ingested_at)` from lessons-forge.db
4. Suppression check: if suppressed and ingestion hasn't advanced, logs and returns
5. Counts plans closed since last ingestion
6. If count >= threshold, fires notifier and sets suppression timestamp
7. Outer `except` catches any unexpected failure — logs WARN, no re-raise

**Rescan hook** at the main loop call site (~line 2136):
```python
if time.time() - last_rescan >= rescan_interval:
    self._rescan(handler)
    self._evaluate_cycle_nudge()
    last_rescan = time.time()
```

**Suppression-state design note:** All state is in-memory. A daemon restart resets `_cycle_nudge_suppressed_ts` to `None` and `_cycle_nudge_last_eval` to `0.0`. Worst case: one repeat nudge after restart if the threshold is still exceeded. This is accepted and documented — no persistence needed for a non-urgent notification.

### Change 4 — notifier.py

**`notify_cycle_nudge(count, since_ts)`** — follows the existing named-function pattern. Event-gated by `notifications.events["cycle_nudge"]`. Uses `_enqueue_deferred` (non-urgent) so it coalesces with other deferred events.

**`_flush_buffer`** updated to handle `cycle_nudge` event type in the digest message:
```
Learning loop nudge: {count} plans closed since last ingestion ({since_ts}).
```

### Change 5 — tests (tests/test_cycle_nudge.py)

All tests use throwaway temp DBs; never touch canonical lifecycle.db or lessons-forge.db.

| Test | Rationale |
|---|---|
| `test_count_plans_closed_since_with_timestamp` | (a) Count-since query correctness with a timestamp filter |
| `test_count_plans_closed_since_null_ingestion` | (a) NULL-ingestion branch counts all closed plans |
| `test_threshold_boundary_fires_at_threshold` | (b) count == threshold fires notification |
| `test_threshold_boundary_no_fire_below` | (b) count == threshold-1 does not fire |
| `test_missing_lessons_db_no_exception` | (c) Missing lessons-forge.db → logged no-op, no exception |
| `test_interval_gating` | (d) Second evaluation inside the window is a no-op |
| `test_post_fire_suppression` | (e) Suppressed until ingested_at advances past fire-time value |
| `test_absent_config_disabled` | (f) Absent cycle_nudge config block → disabled, no exception |

---

## Full Suite Tail

```
tests/test_worktree.py::test_auto_stage_noop_when_all_committed PASSED   [100%]

=============================== warnings summary ===============================
../../../Library/Python/3.9/lib/python/site-packages/urllib3/__init__.py:35
  /Users/marklehn/Library/Python/3.9/lib/python/site-packages/urllib3/__init__.py:35: NotOpenSSLWarning: urllib3 v2 only supports OpenSSL 1.1.1+, currently the 'ssl' module is compiled with 'LibreSSL 2.8.3'. See: https://github.com/urllib3/urllib3/issues/3020
    warnings.warn(

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
======================= 749 passed, 0 failed, 1 warning in 28.67s ========================
```

---

### Ledger Updates

#### Prompt Feedback

No daemon-owned prompt feedback items surfaced during this implementation.

---

## Output Receipt
**Agent:** Bellows Developer
**Step:** 1
**Status:** Complete

### What Was Done
Implemented the cycle-nudge trigger: config block, evaluator with read-only cross-DB queries, interval gating, post-fire suppression, notifier integration, and 8 tests covering all specified cases. Full suite green (749 passed).

### Files Deposited
- `bellows/knowledge/development/cycle-nudge-trigger-2026-07-06.md` — this dev log

### Files Created or Modified (Code)
- `bellows/bellows.py` — added `LESSONS_FORGE_DB` constant, `_get_last_ingestion_ts()`, `_count_plans_closed_since()`, `_evaluate_cycle_nudge()` method, rescan hook, instance state
- `bellows/notifier.py` — added `notify_cycle_nudge()`, updated `_flush_buffer` for cycle_nudge event type
- `bellows/config.json` — added `cycle_nudge` block and `notifications.events.cycle_nudge` flag (gitignored)
- `bellows/tests/test_cycle_nudge.py` — 8 new tests

### Decisions Made
- Evaluator placed as module-level functions (matching existing utility pattern) with method wrapper on Bellows class
- Suppression state is in-memory only — daemon restart resets (accepted: worst case one repeat nudge)
- `notify_cycle_nudge` uses deferred (non-urgent) delivery path, coalescing with other routine notifications

### Flags for CEO
- None

### Flags for Next Step
- New code is INERT until daemon restart — QA should verify at code level only, not attempt live validation
- config.json is gitignored; the edit is in the working copy and will be picked up at next daemon start
- Post-restart live canary is a mandatory follow-up
