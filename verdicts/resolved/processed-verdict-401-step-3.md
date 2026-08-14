verdict: stop

Planner verdict on executable-401 step 3 (delete_not_xml.py tool) -> STOP (halt), NOT for a step-3 defect. Steps 1-3 are complete + Planner-verified correct; halting BEFORE the known-doomed step-4 QA to fold a permanent fix + one clean QA into a corrective (Bellows grammar: no redo; stop + re-deposit).

STEP 3 IS CORRECT (Planner-verified in code + ran 13 tests, all pass):
- Dry-run is the DEFAULT; --execute + --no-export flags.
- Export VERIFIED before the transaction (D1 fold): aborts if the JSON is missing/empty/count-mismatched; --no-export prints the loud IRREVERSIBLE warning.
- Atomic FK-safe cascade: HARD_FK_CHILDREN(7) -> SOFT_REF_TABLES(4, incl action_queue_audit) -> DELETE FROM invoices, then INSERT OR REPLACE deleted_invoices (V1 fold), one commit, rollback on any exception.
- Materialized target set (preview==delete), count-match confirm, cp1252-safe (ascii_safe).
- MUST-PRESERVE #5: Planner INDEPENDENTLY re-grepped `REFERENCES invoices` at HEAD = exactly the 7 the script lists; child map complete.
- tests/test_delete_not_xml.py = 13 passed (dry-run, execute+cascade, no-orphans, confirm-abort, ASCII-safe).

WHY STOP NOW: step-1's 22->23 bump left 3 pre-existing tests asserting `== 22` (test_forge_export_sanitization.py:326, test_fuel_import_conflict.py:266/291) — Planner-confirmed FAILING (3 failed, 29 passed). Step 4's full-suite QA is therefore guaranteed to fail. Halting before that wasted run.

CORRECTIVE (to be deposited): DEV step rewrites those 3 assertions to reference imported CURRENT_SCHEMA_VERSION (PERMANENT fix — bump-proof, ends the recurrence 394->396->401), then a FOREGROUND full-suite QA + Rule 20. Steps 1-3 stay committed at HEAD; the corrective's QA validates the whole delete-not-xml feature.
