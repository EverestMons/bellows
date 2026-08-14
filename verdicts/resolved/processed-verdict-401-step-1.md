verdict: continue

Planner verdict on executable-401 step 1 (deleted_invoices tombstone schema) -> continue to step 2.

MECHANICAL GATE: all PASS (11 files; scope_check PASS).

SUBSTANCE (Planner-verified in code + ran schema tests):
- CURRENT_SCHEMA_VERSION = 23 (bumped from 22); _migrate_add_deleted_invoices defined (database.py:2387) + registered in init_db (:179); deleted_invoices table created with invoice_id PK.
- tests/test_deleted_invoices_schema.py has the REQUIRED migrate-existing-DB path (legacy_db fixture stamped v22 -> init_db -> table appears) + PK-rejects-duplicate. Schema tests pass (30 passed across the schema files run).

⚠️ KNOWN, NON-BLOCKING-FOR-STEP-1, WILL-FAIL-STEP-4-QA (Planner-identified now, not by the gate): the 22->23 bump updated 8 version-asserting test files but MISSED 3 that hardcode the version — tests/test_forge_export_sanitization.py:326, tests/test_fuel_import_conflict.py:266 and :291 (all `assert version == 22`, now fail == 23). These are the SAME 3 that plan 396 fixed at the 21->22 bump (a recurring co-update blind spot, now recorded in memory). They are INDEPENDENT of the delete-not-xml feature and of steps 2-3. Continuing so the feature DEV proceeds; the 3 will be swept PERMANENTLY (rewrite to assert against imported CURRENT_SCHEMA_VERSION) at the QA step / a QA-fix corrective. Confirmed by Planner: `pytest test_forge_export_sanitization.py test_fuel_import_conflict.py` = 3 failed, 29 passed, all 3 the version literal.

The schema migration itself is correct and complete. Proceed to step 2 (ingest suppression skip).
