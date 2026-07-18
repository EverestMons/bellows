verdict: continue

**Rule 22(b) verified independently by the Planner — with the verification concentrated on the three claims TESTS CANNOT PROVE, per the plan's own design.**

## The untestable three, verified by inspection

1. **CSRF:** `csrf_token` present ×3 in `contract_fuel_review.html` (all forms); `csrf.exempt` appears NOWHERE in either touched module. The feature will work under the global CSRFProtect, and the money route was not exempted to make tests pass — the exact watering-down the plan banned.
2. **Race-safe resolution:** the literal `WHERE id = ? AND resolved = 0` shape at ALL THREE resolution sites — keep (`contracts.py:7076`), apply (`:7119`), acknowledge (`:7206`). Double-submit aborts cleanly everywhere.
3. **Anti-tamper:** the applied values are `conflict["incoming_ceiling"]` / `conflict["incoming_pct"]` — read from the DB row, passed straight to the rowid-keyed UPDATE. The form contributes only ids and an action; no rate value can enter through this surface.

## Also Planner-verified

- **No top-level cross-import** — `contracts.py`'s header has zero `gap_dashboard` references; the app-boot hazard from drafting-pass 2 cannot fire.
- **Badge is shared-and-guarded as locked:** `fuel_review_pending` computed in `_get_child_counts` with `_table_exists` wrapping each count — pre-v19 DBs degrade to badge-0, never a 500.
- **74 tests pass Planner-run** — the new file PLUS `tests/test_contracts.py`, proving the sidebar/child_counts changes broke no existing contract page.
- All mechanical gates PASS; exactly the 6 scoped files.

## Proceed to Step 2 (QA)

All 15 rows. Row 13 (CSRF grep) and row 14 (FROZEN zero diff) are conventions tests cannot carry — they must be grep/diff evidence, not test citations. Row 11 baseline: **2240 passed, 2 failed** ± this plan's net new tests (the new file contributed a large count — verify and report ACTUAL, never force). Rows 4 and 15 quote code, not summaries. The three standing prohibitions (no Monitor, no fixing tests, no direct PROJECT_STATUS write) have held for three consecutive plans — keep the streak.
