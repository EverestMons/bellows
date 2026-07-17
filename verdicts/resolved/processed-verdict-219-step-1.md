verdict: continue

**Rule 22(b) verified independently by the Planner — tests run, code read, migration exercised. Not taken on the receipt's word.**

## The config-2 defect is fixed at the source

The dedup at `_import_fuel_section` is now value-aware: existing row's `price_ceiling`+`fsc_pct` selected; identical-within-0.001 → silent skip (legitimate re-paste preserved); differs → conflict. The **change-nothing guarantee is literal** — Planner grep of the conflict branch shows **zero** `UPDATE contract_fuel_table`, no `confirmation_status`/`extraction_provenance` mutation; the only write is the `fuel_bracket_conflicts` INSERT. `test_same_floor_different_ceiling_records_conflict` uses the real `6.15 / 99.999 → 6.169` shape and asserts the existing row is untouched, no duplicate floor inserted, a specific `6.169` warning present, one conflict row written. Had this existed in May, the CEO's re-paste would have surfaced instead of vanishing.

## The migration — the row this project has been bitten by twice — holds

`CURRENT_SCHEMA_VERSION = 18`. Planner ran `TestMigrateExistingDB` directly: a DB stamped at v17 with the table dropped, re-`init_db()`, → table exists AND version == 18. That proves the bump defeats the `init_db` fast-path (the exact failure mode of the two prior scars). `create_fuel_bracket_conflicts_table` is registered in the guarded migration sequence; a fresh DB builds at 18 with the table. 9/9 targeted tests pass (Planner-run).

All 11 gates PASS; 5 scoped files; `web/contract_import.py` untouched (the JSON-path dedup gap is a named fast-follow, correctly not bundled).

## Proceed to Step 2 (QA)

Row 4 is the one that matters most and CANNOT be shortcut: run `init_db` against the ACTUAL canonical `data/invoices.db` (currently v17 on this Mac) and show raw `PRAGMA table_info(fuel_bracket_conflicts)` + `SELECT version` = 18 — the migrate-EXISTING path on real data, not a fresh build. Row 7 baseline is **2211 passed, 2 failed** plus this plan's 9; verify and report actual, never force. Row 3 (change-nothing by inspection) and Row 1 (config-2 scenario) corroborate the Planner's checks — re-verify rather than inherit, this verdict is itself a generated artifact.
