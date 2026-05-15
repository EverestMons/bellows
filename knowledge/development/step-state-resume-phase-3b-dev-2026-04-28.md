# Phase 3b: DB-Based Step State Recovery + plan_slug Column — Dev Log

**Date:** 2026-04-28 | **Agent:** Bellows Developer | **Step:** 1
**Plan:** `knowledge/decisions/in-progress-executable-step-state-resume-phase-3b-2026-04-28.md`
**Design:** `knowledge/architecture/step-state-resume-design-2026-04-28.md`
**Verification:** `knowledge/research/step-state-resume-phase-3b-verification-2026-04-28.md`

---

## Summary

Implemented Deliverables 2, 3, and 5 from the Phase 3b design: renamed `_slug_from_path` → public `slug_from_path`, added `plan_slug TEXT` column to the `runs` table (all 3 DDL/migration sites), wired `plan_slug` through `record_run()`, added `_get_last_completed_step()` DB query helper, and integrated DB resume logic into `run_plan()`. Added 5 new tests covering all new functionality.

---

## Task-by-Task Changes

### Task 1 — Rename `_slug_from_path` → `slug_from_path`

**Before:** `def _slug_from_path(plan_path):` (private, verdict.py:65)
**After:** `def slug_from_path(plan_path):` (public, verdict.py:65)

Updated call sites:
- verdict.py:83 — internal caller
- bellows.py:384 — auto-close cleanup (`verdict.slug_from_path`)
- bellows.py:779 — startup orphan sweep (`verdict.slug_from_path`)
- bellows.py:781 — startup orphan sweep (`verdict.slug_from_path`)
- bellows.py:786 — Done directory scan (`verdict.slug_from_path`)

Verified: `grep -rn "_slug_from_path" *.py` returns 0 matches.

### Task 2 — Add `plan_slug` column to runs table (3 DDL sites)

**Site 1 — `migrate_db()` DDL (line 41):**
- Before: `cost REAL` as last column
- After: `cost REAL, plan_slug TEXT`

**Site 2 — `migrate_db()` additions dict (line 54):**
- Before: `"cost": "REAL"` as last entry
- After: Added `"plan_slug": "TEXT"` entry

**Site 3 — `record_run()` DDL (line 151):**
- Before: `cost REAL` as last column
- After: `cost REAL, plan_slug TEXT`

### Task 3 — Wire `plan_slug` through `record_run()`

- Added `plan_slug: str` as last parameter to `record_run()` signature
- Updated INSERT statement to include `plan_slug` column + placeholder
- Added `plan_slug = verdict.slug_from_path(base_filename)` derivation near top of `run_plan()`
- Updated all 4 `record_run()` call sites (lines ~274, ~312, ~332, ~370) to pass `plan_slug`

### Task 4 — Add `_get_last_completed_step()` helper

Added module-level function near `record_run()`:
```python
def _get_last_completed_step(db_path: str, plan_slug: str) -> Optional[int]:
```
Uses exact `WHERE plan_slug = ?` match (not LIKE). Returns highest step with `status = 'Complete'`, or None.

### Task 5 — Add DB resume logic in `run_plan()`

Inserted after shadow cache load, before atomic claim move:
```python
if resume_step is None and shadow_text is not None:
    last_step = _get_last_completed_step(db_path, plan_slug)
    if last_step is not None and last_step >= 1:
        resume_step = last_step + 1
        print(f"Bellows: DB resume — last completed step {last_step}, resuming at {resume_step}")
```

Guard: only fires when `resume_step is None` AND shadow cache exists (prior claim indicator).

### Task 6 — 5 new tests

1. `test_record_run_stores_plan_slug` — verifies plan_slug column populated
2. `test_get_last_completed_step_returns_max` — 3 rows for slug "foo", returns 3
3. `test_get_last_completed_step_no_rows` — empty DB returns None
4. `test_get_last_completed_step_excludes_non_complete` — step 1 Complete + step 2 VerdictPending → returns 1
5. `test_get_last_completed_step_exact_slug_match` — slug "foo" (step 2) vs "foo-bar" (step 3) → returns 2

### Task 7 — Targeted test output

```
======================== 70 passed, 1 warning in 0.24s =========================
```

All 65 existing tests + 5 new tests pass. Zero regressions.

---

## Output Receipt
**Agent:** Bellows Developer
**Step:** 1
**Status:** Complete

### What Was Done
Implemented DB-based step state recovery (Hybrid 1+3 Option A): renamed `_slug_from_path` to public `slug_from_path`, added `plan_slug TEXT` column across all 3 DDL/migration sites, wired `plan_slug` through `record_run()` and all 4 call sites, added `_get_last_completed_step()` helper with exact slug match, integrated DB resume logic into `run_plan()`, and added 5 new tests.

### Files Deposited
- `bellows/knowledge/development/step-state-resume-phase-3b-dev-2026-04-28.md` — this dev log

### Files Created or Modified (Code)
- `bellows/verdict.py` — renamed `_slug_from_path` → `slug_from_path` (definition + internal call site)
- `bellows/bellows.py` — added `plan_slug TEXT` column (3 DDL sites), `plan_slug: str` param to `record_run()`, `_get_last_completed_step()` helper, DB resume logic in `run_plan()`, `plan_slug` derivation + 4 call site updates, updated 4 `verdict.slug_from_path()` call sites
- `bellows/tests/test_bellows.py` — added 5 new tests for plan_slug storage, _get_last_completed_step behavior

### Decisions Made
- Updated 4 bellows.py call sites (not 3 as plan stated) — line 786 (Done directory scan) also needed updating
- Used `base_filename` (already lifecycle-prefix-stripped) as input to `verdict.slug_from_path()` for slug derivation in `run_plan()`

### Flags for CEO
- None

### Flags for Next Step
- Deliverable 4 (plan-hash drift warning) is deferred to Phase 3c per plan scope
- Pre-existing `test_run_step_timeout` test is not present in current suite (allowed per plan)
- All existing tests pass with the new `plan_slug` parameter — tests that mock `record_run` are unaffected
