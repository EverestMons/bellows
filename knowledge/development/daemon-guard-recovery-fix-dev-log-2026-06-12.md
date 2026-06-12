# Dev Log — Daemon Single-Instance Guard + Project-Scoped Recovery + Age Guard + in_progress Write

**Date:** 2026-06-12 | **Plan:** 22, Step 1 | **Agent:** Bellows Developer

---

## Summary

Implemented all four gaps (G1–G4) from diagnostic 21 to prevent cross-project recovery misclassification, daemon double-start, premature abandonment, and missing intermediate lifecycle state.

---

## Per-Gap Edits

### G1 — Project-scoped recovery (lifecycle.py:190–251)

- Added `project_root` parameter to `recover_half_claimed()`
- When `project_root` is provided, the SELECT filters by `target_project = ?` — only plans belonging to the scanned project are considered
- Added `created_at` to the SELECT columns (shared with G3)
- Callsite in `bellows.py:1835–1842`: derives `project_root` from `decisions_path` via `Path(decisions_path).parent.parent` and passes it to `recover_half_claimed()`
- Backward-compatible: when `project_root` is None (legacy callers), the global query is used

### G2 — flock single-instance guard (bellows.py:1828–1835)

- Added `import fcntl` at module top (bellows.py:1)
- In `__main__`, before `migrate_db()`: opens `.bellows.lock` at `BELLOWS_ROOT`, acquires `fcntl.flock(fd, LOCK_EX | LOCK_NB)`
- On `BlockingIOError` / `OSError`: logs ERROR "another Bellows instance holds .bellows.lock — exiting" and exits non-zero
- File descriptor intentionally kept open at module scope — kernel releases flock on process death, no cleanup code needed

### G3 — Age guard, N=5min (lifecycle.py:235–244)

- Before the abandoned fallthrough branch: checks `created_at` age vs `age_guard_seconds` (default 300s = 5min per DF3)
- If plan is younger than the threshold: logs INFO "recovery: plan <id> younger than 5m — skipping", appends `(plan_id, "skipped_too_recent")`, continues
- Handles malformed timestamps gracefully (falls through to abandon)

### G4 — in_progress write (bellows.py:460–464)

- After `shutil.move(plan_path, inprogress_path)`: calls `lifecycle.mark_plan_state(plan_id, "in_progress")`
- Log-and-continue semantics: wrapped in try/except with a warning log on failure
- Recovery SELECT remains `WHERE lifecycle_state = 'claimed'` — plans that reach `in_progress` are fully claimed and won't be re-processed by recovery

---

## Tests

### New tests added (8 tests in tests/test_lifecycle.py)

| # | Class | Test | Coverage |
|---|---|---|---|
| 1 | TestRecoverCrossProjectIsolation | test_plan_for_project_x_not_touched_when_scanning_project_y | G1: plan for X invisible when scanning Y |
| 2 | TestRecoverCrossProjectIsolation | test_plan_for_project_x_found_when_scanning_project_x | G1: plan for X found when scanning X |
| 3 | TestRecoverAgeGuard | test_young_plan_not_abandoned | G3: plan < 5min → skipped_too_recent |
| 4 | TestRecoverAgeGuard | test_old_plan_is_abandoned | G3: plan > 5min → abandoned |
| 5 | TestFlockGuard | test_second_flock_acquisition_fails | G2: second flock raises |
| 6 | TestFlockGuard | test_flock_released_after_fd_close | G2: flock released on fd close |
| 7 | TestInProgressAfterClaim | test_mark_in_progress_updates_state | G4: state transitions to in_progress |
| 8 | TestInProgressAfterClaim | test_in_progress_plan_not_selected_by_recovery | G4: in_progress plans invisible to recovery |

### Existing test adjustment

- `TestRecoverHalfClaimed.test_deposit_absent_marks_abandoned`: backdated `created_at` by 10 minutes so the age guard does not interfere with the abandoned-path test

### Test count

- Before: 524 passed
- After: 532 passed (8 new tests)

---

## Full Suite Tail

```
======================== 532 passed, 1 warning in 9.61s ========================
```

---

## Output Receipt
**Agent:** Bellows Developer
**Step:** 1
**Status:** Complete

### What Was Done
Implemented all four diagnostic-21 gaps (G1–G4): project-scoped recovery filter, flock single-instance guard, 5-minute age guard, and in_progress lifecycle state write after claim rename. Added 8 new tests covering all four gaps plus regression verification.

### Files Deposited
- `knowledge/development/daemon-guard-recovery-fix-dev-log-2026-06-12.md` — this dev log

### Files Created or Modified (Code)
- `lifecycle.py` — recover_half_claimed: project_root filter (G1), created_at SELECT + age guard (G3)
- `bellows.py` — flock guard in __main__ (G2), mark_plan_state in_progress after claim rename (G4), import fcntl, callsite project_root derivation
- `tests/test_lifecycle.py` — 8 new tests (G1–G4), backdated existing abandoned test for age guard compatibility

### Decisions Made
- Recovery SELECT remains WHERE lifecycle_state = 'claimed' (no need to add in_progress — plans that reach in_progress are fully claimed)
- G4 mark_plan_state wrapped in try/except with log-and-continue semantics, consistent with all other lifecycle writes
- Age guard parameter exposed as age_guard_seconds kwarg (default 300) for testability

### Flags for CEO
- DAEMON RESTART REQUIRED — no hot reload; the running daemon keeps its loaded code
- Live canaries after restart: (1) first claimed plan shows lifecycle_state='in_progress' mid-run, (2) deliberate second python3 bellows.py exits immediately on flock

### Flags for Next Step
- Existing test_deposit_absent_marks_abandoned was adjusted (backdated created_at) — QA should verify the adjustment is appropriate
- .bellows.lock file will be created on first run — gitignore entry may be desired
