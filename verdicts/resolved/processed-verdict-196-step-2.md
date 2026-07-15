verdict: continue
Step 2 verified — one benign scope_check failure, continue-with-reasoning under delegated authority. (pause was gate_failure, not the after_step_1 checkpoint.)
Benign scope_check (2 files): tests/test_contract_document_schema.py (Step-1 test updated again) + web/documents.py (LEGITIMATE Step-2 work my plan mis-located to Step 3 — Tier-1 confirm wiring lives in the extraction path in web/documents.py). Other gates PASS (receipt Complete, deposit present, rule_22 PASS, 7 files).
Planner check (b), by direct read + DEV log:
- parse_linked_document(...doc_scope=carrier) extended; contract branch: carrier_document_id=NULL, contract_document_id=doc_id, doc_source_scope=contract.
- Upload re-point (web/contracts.py:2642-2652): data/contract_docs/<id>/, INSERT INTO contract_documents, skip bridge, parse doc_scope=contract.
- Tier-1 wiring (web/documents.py:849): src_doc_id=None if scope==contract -> source_document_id NULL = Tier 1; carrier/global unchanged = Tier 2.
- _load_document scope==contract branch (web/documents.py:85) also landed (pulled forward from Step 3 — fine).
- GOOD CATCH: DEV found PRAGMA foreign_keys=ON (database.py:51), so the diag-193/plan carrier_document_id=0 sentinel would VIOLATE the FK; it correctly used NULL + rebuilt parsed_rate_candidates nullable. Corrects a shared misconception.
Minor non-blocking: parse_linked_document docstring (~:6436) still says carrier_document_id=0 sentinel — stale; code uses NULL. Fix in a later sweep.
Proceed to Step 3 (re-parse-contract-doc route + owned-docs UI card + glossary; file-serve branch already in) and Step 4 QA.
