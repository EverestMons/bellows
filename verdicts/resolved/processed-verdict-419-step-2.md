verdict: continue

Planner verdict on executable-419 step 2 (dedup_xml_data.py cleanup tool) -> continue to step 3 (foreground QA).

MECHANICAL GATE: all PASS (3 files: dedup_xml_data.py, dev log, test_dedup_xml_data.py; scope_check PASS).

SUBSTANCE (Planner-verified in code + ran tests):
- RE-ENRICH-ONLY (the walk-1 D1 fold landed): execute() splits affected into file_present vs file_absent (via find_xml); file_absent are SKIPPED + listed ('re-fetch to clean'), NEVER deleted/emptied; file_present are re-enriched via enrich_invoice_xml (Step-1-fixed -> delete-first -> one clean set). No blind DELETE that could empty a no-file invoice.
- Count-match confirm on the file_present count (mismatch/EOF aborts); conn.commit() after the loop; per-invoice try/except.
- Dry-run DEFAULT (Probe 1-4, no mutations); --execute flag; ascii_safe (cp1252); init_db() self-migrate at start.
- TESTS RUN (Planner, foreground): test_dedup_xml_data.py = 8 passed (dry-run no-mutate, execute re-enrich-clean, no-file skipped-not-emptied, confirm-abort, ASCII-safe).

Clean and correct. Proceed to step 3 -- FOREGROUND full-suite QA + Rule 20.
