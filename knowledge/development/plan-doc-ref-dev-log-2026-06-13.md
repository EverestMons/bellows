# Plan Doc Ref (plan_doc_ref) — Dev Log 2026-06-13

## Summary

Added `plan_doc_ref TEXT` column to the `plans` table in lifecycle.db. This column stores the project-relative path to the plan document at its CURRENT filesystem location, updated at each state transition that moves the file.

## Migration

- Added `plan_doc_ref TEXT` to the `CREATE TABLE IF NOT EXISTS plans` definition (fresh DBs).
- Added idempotent `ALTER TABLE plans ADD COLUMN plan_doc_ref TEXT` migration guarded by `PRAGMA table_info` check (existing DBs).
- Migration runs at next daemon startup via `init_lifecycle_db()`.

## Writer — mark_plan_state extended

Extended `mark_plan_state()` with optional `plan_doc_ref` parameter. When provided, the column is written alongside the state update. Uses dynamic SQL construction to avoid touching the column when not provided (preserves existing value).

## Write sites covered

All 5 `mark_plan_state` callsites in bellows.py updated:

| # | Site | State | plan_doc_ref value |
|---|------|-------|--------------------|
| 1 | Claim rename (bellows.py:462) | in_progress | `knowledge/decisions/in-progress-<type>-<id>.md` |
| 2 | Auto-close (bellows.py:793) | closed | `knowledge/decisions/Done/<type>-<id>.md` |
| 3 | Verdict halt — worktree teardown blocked (_consume_verdicts) | halted | `knowledge/decisions/halted-<type>-<id>.md` |
| 4 | Verdict continue-to-done (_consume_verdicts) | closed | `knowledge/decisions/Done/<type>-<id>.md` |
| 5 | Verdict stop — halt (_consume_verdicts) | halted | `knowledge/decisions/halted-<type>-<id>.md` |

Recovery paths in lifecycle.py `recover_half_claimed` also updated:
- `already_renamed`: sets plan_doc_ref to in-progress path (knowable).
- `re_renamed`: sets plan_doc_ref to in-progress path (knowable).
- `abandoned`: leaves plan_doc_ref unchanged (no file on disk).

### Sites with file moves but NO lifecycle write (noted, not in scope)

- **Claim-time halt** (bellows.py:419): dispatch-mode validation rejection moves to `halted-<base>`. Occurs BEFORE `mint_and_claim`, so no plan_id exists — no lifecycle row to update.
- **0-step skip to Done** (bellows.py:494): moves to Done/ but has no `mark_plan_state` call. Pre-existing gap; not introduced by this plan.

## Backfill

One-time `backfill_plan_doc_ref()` function added to lifecycle.py. Guarded by `WHERE plan_doc_ref IS NULL` (idempotent). Candidate logic mirrors Forge reporter: closed_at not null → Done/<type>-<id>.md; else probe in-progress-, halted-, bare.

**Production backfill result: 37 backfilled, 0 left NULL.**

## SELECT evidence (read-only, production lifecycle.db)



## Tests added (4 new test classes, 11 new tests)

- `TestPlanDocRefMigration`: column present on fresh DB, added to existing DB, idempotent double-init (3 tests)
- `TestMarkPlanStateWithDocRef`: writes plan_doc_ref, updates on close, omitting leaves unchanged (3 tests)
- `TestPlanDocRefClaimToClose`: full claim→close sequence leaves Done/<type>-<id>.md (1 test)
- `TestBackfillPlanDocRef`: closed row resolves to Done path, nonexistent left NULL, idempotent, in-progress resolves (4 tests)

## Full suite result

**597 passed, 0 failed** (python3 -m pytest tests/ -v)

---
## Output Receipt
**Agent:** Bellows Developer
**Step:** 1
**Status:** Complete

### What Was Done
Added plan_doc_ref column to plans table with migration, writer integration at all 5 mark_plan_state callsites + 2 recovery paths, backfill function, and 11 new tests. Production backfill populated all 37 existing rows.

### Files Deposited
- knowledge/development/plan-doc-ref-dev-log-2026-06-13.md — this dev log

### Files Created or Modified (Code)
- lifecycle.py — added plan_doc_ref to CREATE TABLE, ALTER TABLE migration, extended mark_plan_state, updated recover_half_claimed, added backfill_plan_doc_ref
- bellows.py — updated all 5 mark_plan_state callsites to pass plan_doc_ref
- tests/test_lifecycle.py — added 4 test classes (11 tests) for migration, writer, claim→close, backfill

### Decisions Made
- Recovery path "abandoned" leaves plan_doc_ref unchanged (no file exists to reference)
- 0-step skip-to-Done and pre-mint claim-time halt not covered (no lifecycle row / no mark_plan_state call — pre-existing gaps)
- Backfill uses os.path.relpath for project-relative paths, matching deposits.declared_path convention

### Flags for CEO
- DAEMON RESTART REQUIRED — migration runs at next startup against live lifecycle.db

### Flags for Next Step
- QA should verify: column populated on all rows, write sites grep, migration idempotent re-run, full suite pass, FORWARD row for Forge reader follow-up
