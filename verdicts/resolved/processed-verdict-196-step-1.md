verdict: continue
Step 1 (schema) verified — one benign scope_check failure, continue-with-reasoning under delegated authority.
Benign: scope_check flagged tests/test_contract_document_schema.py + tests/test_parse_track_schema.py — new schema-coverage test files the DEV added; the plan Step-1 test line used a -k filter (schema or migration or contract_document) without naming files, so scope_check couldnt match them. Legitimate coverage; the benign unnamed-tests class. All other gates PASS (receipt Complete, deposit present, rule_22 PASS, 4 files).
Planner check (b) confirmed by direct read of contract_tables.py:
- CREATE TABLE contract_documents at :979 (id PK, contract_id FK, doc_name, doc_type, file_path, created_at, updated_at); idx_contract_docs_contract at :990.
- Additive parsed_rate_candidates columns via _safe_add_column: contract_document_id (:1653, REFERENCES contract_documents) + doc_source_scope TEXT (:1655); also present in the fresh-DB CREATE (:2105-2106).
- FROZEN database.py untouched (all schema additive in contract_tables.py).
Proceed to Step 2 (parse_linked_document doc_scope extension + re-point contract-page upload to contract_documents/data/contract_docs + Tier-1 confirm wiring), Step 3 (file-serve scope=contract + re-parse route + owned-docs UI + glossary), Step 4 (QA full suite + Tier-1 verification).
