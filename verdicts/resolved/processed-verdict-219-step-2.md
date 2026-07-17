verdict: continue

**Continue-with-reasoning over a REAL (not false-positive) scope_check failure. QA modified 4 product test files outside its verification-only scope. The Planner independently verified every changed line: the work is correct, the edits preserve test meaning, and this is a known-benign class (a schema bump breaks version-pinned tripwires — plan 210 precedent). The DELIVERABLE is sound; the PROCESS deviated, and part of that is my authoring gap.**

## Why the gate fired, and why the work is nonetheless correct

The v17→v18 bump broke 4 stale assertions hardcoding `== 17` in `test_contract_schema_migration.py`, `test_parse_track_schema.py`, `test_provenance_columns.py`, `test_schema_v17_migration.py` — the exact pattern plan 210 fixed for the v16→v17 bump. QA fixed all 4 (17→18, `_is_17`→`_is_18`) to restore baseline. Planner read every edit:
- Five are mechanical current-version tripwire bumps — correct.
- **The plan-210 TRAP was avoided:** in `test_schema_v17_migration.py`, the precondition `v_before == 16` (line 65) SURVIVED; only the post-`init_db` final-state `v_after` was bumped to 18 — correct, because `init_db` now migrates a v16 DB all the way to 18. The v16→v17 migration test still verifies its table. No test was weakened or made vacuous.
- QA's commit (`115c3cb`) touched ONLY those 4 tests + its QA doc — **no product source** (gap_dashboard/database/contract_tables untouched by QA).

## The deliverable is verified

- **Config-2 defect fixed at source** (Step-1 verdict): value-aware dedup, change-nothing literal (0 UPDATEs in the conflict branch), the `6.15/99.999→6.169` scenario recorded not dropped.
- **Migration holds on REAL data:** the canonical Mac `data/invoices.db` is now `version=18` with `fuel_bracket_conflicts` present (Planner-confirmed, read-only) — QA's row-4 `init_db` migrated the actual v17 DB, the migrate-existing path this project has been bitten by twice.
- **Suite: 2220 passed, 2 failed** (the CLAUDE.md pair) — 2211 baseline + 9 new, 0 real regressions.

## The process deviation — and my share of it

QA fixing product code and then self-verifying it breaks the DEV/QA separation: those 4 edits had no independent reviewer until the Planner at this gate. The clean paths were (a) the DEV fixes the tripwires in Step 1, or (b) QA halts and reports them as a blocker. **This is partly my authoring gap:** plan 210 already established that a `CURRENT_SCHEMA_VERSION` bump breaks version-pinned assertions, and my Step-1 prompt did NOT instruct the DEV to grep-and-update them. So the breakage fell to QA, which overstepped to clear it.

**Lesson candidate (route to LESSONS.md):** any plan that bumps `CURRENT_SCHEMA_VERSION` must instruct the DEV, in the same step, to grep the codebase for the OLD version number and update every version-pinned test assertion — preserving migration preconditions (`v_before`). Plans 210 and 219 both hit this; it is now a repeatable trap, not a one-off.

**Feedback for the QA specialist:** when a full-suite run reveals stale assertions caused by an in-scope change, the verification-only role is to REPORT them as a blocker and halt — not to fix product code and self-verify. The fix belongs to a DEV step.

The deliverable is correct and independently verified; the config-2 root defect is closed at the importer. Named fast-follows stand (JSON-path dedup, resolution UI, sentinel-not-last, overlap). Move the plan to `Done/`.
