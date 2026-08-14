verdict: continue

Planner verdict on executable-404 step 1 (self-migrate hardening) -> continue to step 2 (foreground QA).

MECHANICAL GATE: all PASS (3 files: delete_not_xml.py, dev log, test_delete_not_xml.py; scope_check PASS).

SUBSTANCE (Planner-verified in code + ran tests):
- Import extended: delete_not_xml.py:19 `from database import get_connection, init_db`.
- init_db() at main() start (:312) BEFORE conn = get_connection() (:313), OUTSIDE the delete try/except — so a stale DB is migrated (deleted_invoices created) before any query, and a migration error surfaces plainly rather than as a rolled-back delete.
- Delete logic untouched (dry-run default, --execute, --no-export, export-verify, atomic cascade, INSERT OR REPLACE tombstone, cp1252-safe all unchanged).
- REGRESSION test added: test_main_self_migrates_and_deletes with a pre_v23_db fixture (reproduces the exact work-machine `no such table: deleted_invoices` state) -> the tool self-migrates and completes the delete. Directly proves the live bug is fixed.
- tests/test_delete_not_xml.py = 14 passed (13 prior + the regression).

Clean and correct. Proceed to step 2 — FOREGROUND full-suite QA + Rule 20.
