verdict: continue
Step 1 verified — Bellows gates all PASS + Planner check (b) confirmed by direct read:
- parse_linked_document(db, abs_path, doc_id, contract_id) defined at web/contracts.py:6293 (exact signature); parse_pdf rewired to import + call it (web/gap_dashboard.py:2223-2224), keeping its own file-save + carrier_documents insert + JSON response shape.
- Failure-path (extraction_status=failed) branch preserved.
- Targeted tests GREEN — DEV log raw line: "9 passed, 1 warning in 0.92s" (test_parse_pdf_endpoint 8 + test_e2e_parse_loop 1); refactor is behavior-preserving.
Scope correct (3 files: web/contracts.py + web/gap_dashboard.py + DEV log). Proceed to Step 2 (upload-into-linked-docs route + form + auto-parse), Step 3 (file route + retarget Open + re-parse trigger), Step 4 (QA full suite).
