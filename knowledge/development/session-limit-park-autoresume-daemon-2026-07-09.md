# Session-Limit Park + Auto-Resume — Daemon Wiring (Step 2)

**Date:** 2026-07-09 | **Plan:** 148 | **Step:** 2 | **Agent:** Bellows Developer

## Summary

Wired the full park + persist + auto-resume path in `bellows.py`, consuming the `session_limit` outcome that Step 1 added to `runner.py`.

## Park/Persist/Resume Wiring

### `_maybe_park_session_limit` helper

A single helper called at **both** `run_step` consumption sites (bootstrap step and while-loop step) **before** the gate/escalate handling. When `parsed.get("session_limit")` is true:

1. **Worktree teardown** — the step made no progress (num_turns=1, cost=0), so teardown is a safe no-op merge. Failure is logged but does not block the park.
2. **Rename** `in-progress-<base>` → `parked-<base>` (single `shutil.move`, restart-safe ordering).
3. **DB persist** — `INSERT OR REPLACE` into `parked_steps` table keyed on `plan_slug`.
4. **record_run** with `status="Parked"` for dashboard/status visibility.
5. **CEO notification** via Pushover — deduped per `(plan_slug, resume_step)` via `_NOTIFIED_PARKED` set.
6. **Return True** so `run_plan` returns immediately (no fallthrough to gates/escalate).

### `parked_steps` table schema

```sql
CREATE TABLE IF NOT EXISTS parked_steps (
    plan_slug TEXT PRIMARY KEY,
    plan_path TEXT,
    project TEXT,
    resume_step INTEGER,
    resets_at_epoch REAL,
    parked_at TEXT
)
```

Created in `migrate_db()` — safe to run on every startup.

### `record_park` / `clear_park`

Pair of functions next to `record_run`:
- `record_park(db_path, plan_slug, plan_path, project, resume_step, resets_at_epoch)` — `INSERT OR REPLACE` so re-park overwrites cleanly.
- `clear_park(db_path, plan_slug)` — `DELETE` by primary key.

### Scan exclusion

- `is_runnable_plan` excludes `parked-` prefix (alongside `in-progress-`, `verdict-pending-`, `halted-`).
- `slug_for`, `_shadow_path`, `run_plan` base_filename strip, and `_invalidate_seen_on_redeposit` LIFECYCLE_PREFIXES all include `parked-`.
- `_handle` skip-prefix list includes `parked-` (no "prefix not in dispatch whitelist" warn).
- `_perform_startup_sweep` treats `parked-` files as active (not orphaned).

### Auto-resume (`_resume_parked`)

Method on `Bellows` class:
1. Queries `parked_steps WHERE resets_at_epoch <= now`.
2. For each row: verifies the parked file still exists (CEO manual intervention guard), renames `parked-` → `in-progress-`, calls `clear_park`, dispatches via `handle_new_plan(path, resume_step=resume_step)`.
3. Missing parked file → `clear_park` + WARN (no crash).
4. Double-dispatch guard: `clear_park` runs **before** dispatch, so a concurrent `_resume_parked` call finds no DB row.

**Invoked from:**
- `_rescan` (30-second cycle) — catches resets during normal operation.
- `start()` startup scan — catches resets that expired during a daemon restart.

### Restart safety argument

The park survives daemon restart because:
1. The `parked-` file on disk is never deleted (only renamed on resume).
2. The `parked_steps` DB row persists across process death.
3. On startup, `_resume_parked` is called before the plan scan, so any expired parks are resumed immediately.

### Notification dedup

`_NOTIFIED_PARKED: set[tuple[str, int]]` — keyed on `(plan_slug, resume_step)`. Module-level scope resets on daemon restart (acceptable: a post-restart re-park of the same slug+step would re-notify, which is correct since the operator needs to know the park survived).

## Full Test Suite

```
788 passed, 1 warning in 20.32s
```

0 regressions. New Step 2 tests cover:
- `record_park` queryable at epoch / not returned before epoch
- `clear_park` removes row
- `is_runnable_plan` excludes `parked-`
- `_maybe_park_session_limit` rename + DB persist + Parked status
- `_maybe_park_session_limit` returns False for non-session-limit
- Resume un-park rename produces `in-progress-*` + clears DB row

**Commit:** `da86b6a`

### Ledger Updates

#### Prompt Feedback

None — Step 2 executed as designed with no deviations or surprises.

---
## Output Receipt
**Agent:** Bellows Developer
**Step:** 2
**Status:** Complete

### What Was Done
Wired the full session-limit park + auto-resume path in bellows.py: _maybe_park_session_limit helper at both run_step consumption sites, parked_steps DB table for restart persistence, _resume_parked method called from _rescan and startup scan, scan exclusion across all prefix lists, CEO notification with dedup. Extended tests to cover DB round-trip, park helper, scan exclusion, and resume rename.

### Files Deposited
- `knowledge/development/session-limit-park-autoresume-daemon-2026-07-09.md` — this dev log

### Files Created or Modified (Code)
- `bellows.py` — park helper, DB functions, resume method, prefix exclusions (+169 lines)
- `tests/test_session_limit_park.py` — 7 new Step 2 tests (+162 lines)

### Decisions Made
- Included worktree teardown in the park helper (step made no progress, so teardown is a safe no-op merge; prevents orphaned worktrees)
- Used module-level `_NOTIFIED_PARKED` set for notification dedup (resets on restart, which is correct behavior)

### Flags for CEO
- None

### Flags for Next Step
- Step 3 (QA) should verify the restart-safety argument by reading both the `_rescan` and startup-scan call sites
