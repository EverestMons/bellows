# Type-Qualified Plan IDs — Dev Log 2026-06-12

## Summary
Changed the rendered plan ID label from bare `#N` to `{type} #N` (e.g. `executable #35`, `diagnostic #34`) in BOTH the IN-FLIGHT and AWAITING VERDICT panes of `status.py`. Since `dashboard.py` imports `status.py` render functions, both surfaces are fixed by this single change.

## Changes Made

### status.py
- **IN-FLIGHT query** (`query_in_flight`): Added `p.type` to the SELECT projection (table already joined as `plans p`).
- **IN-FLIGHT render** (`render_in_flight`): Reads `row["type"]`, builds `id_label` as `f"{ptype} #{plan_id}"` when type is present, falls back to bare `f"#{plan_id}"` when type is NULL/empty.
- **AWAITING VERDICT query** (`query_awaiting_verdict`): Added `LEFT JOIN plans p ON p.id = v.plan_id` and projected `p.type`.
- **AWAITING VERDICT render** (`render_awaiting_verdict`): Same pattern — type-qualified label with NULL fallback.
- All DB connects remain `?mode=ro`.

### tests/test_status.py
- Added a `diagnostic` plan (id 13) to the `status_db` fixture for type diversity.
- Updated `TestInFlightRendering` to assert `executable #10` and `diagnostic #13`.
- Updated `TestAwaitingVerdictRendering` to assert `executable #11`.
- Simplified all test queries to use the `status.query_*` helper functions (DRY, and ensures tests exercise the actual queries).
- Added `TestTypeQualifiedIds` class with:
  - `test_in_flight_executable_and_diagnostic` — both types render correctly
  - `test_awaiting_verdict_executable` — type renders in verdict pane
  - `test_null_type_fallback_in_flight` — NULL and empty type fall back to bare `#N`
  - `test_null_type_fallback_awaiting_verdict` — same for verdict pane

### tests/test_dashboard.py
- No changes needed. Existing assertions use `#33` substring checks which still match within `executable #33`.

## Test Results
Full suite: **586 passed**, 0 failed.

## Live Output
```
$ python3 status.py
● Bellows RUNNING  pid 28289  sha 6274d1a  up 13m

IN-FLIGHT
 executable #36  bellows   Step 1/2  running   3m    Bellows — Type-Qualified Plan IDs in …

AWAITING VERDICT
 (none)
```

## Alignment Note
"executable" and "diagnostic" are both exactly 10 characters, so column alignment is naturally preserved.

## Dashboard Note
The running dashboard imports `status.py` at startup. This change takes effect on the next dashboard restart (the `r` key).

---
## Output Receipt
**Agent:** Bellows Developer
**Step:** 1
**Status:** Complete

### What Was Done
Added type-qualified plan ID labels (`executable #N` / `diagnostic #N`) to both IN-FLIGHT and AWAITING VERDICT panes in `status.py`. Added NULL/empty type defensive fallback. Updated and extended test suite with type diversity and fallback coverage.

### Files Deposited
- `knowledge/development/type-qualified-ids-dev-log-2026-06-12.md` — this dev log

### Files Created or Modified (Code)
- `status.py` — added p.type to both queries, type-qualified id_label in both render functions, NULL fallback
- `tests/test_status.py` — diagnostic fixture row, updated assertions, new TestTypeQualifiedIds class with 4 tests

### Decisions Made
- Used dict-based mock rows for NULL fallback tests since the DB schema has a NOT NULL constraint on plans.type
- Simplified test queries to use status.query_* helpers instead of inline SQL

### Flags for CEO
- Dashboard shows new labels only after next `r` restart (status.py is imported at startup)

### Flags for Next Step
- None
