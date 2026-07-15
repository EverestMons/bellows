verdict: continue
Findings accepted under delegated verdict authority (clean gates + Rule 22(b) pass). Bellows gates all PASS.
Planner check (b): the wire-in map thoroughly answers all 6 areas with file:line precision —
- No upload-into-linked-docs entry point today (only link-existing); new POST /contracts/<id>/upload-linked-doc needed + form on contract_linked_docs.html.
- Shared helper parse_linked_document(db, abs_path, doc_id, contract_id) = parse_pdf steps 5-8; parse_pdf rewired to call it (no behavior change).
- Sections need NO change (run_parse_reconciliation + get_section_documents both query by contract_id, source-agnostic) — confirms Amendment A parse-once/consume.
- Repair re-parse route feasible; file_path fully reachable via contract_document_refs -> carrier_documents.
- No file-serving route exists -> new GET /documents/<id>/file?scope= with path-traversal guard; Open (arrow) retargeted.
- Tier Small-Medium, 6 steps, FROZEN core untouched, no schema change, no migration required.
4 forks carry sensible default recommendations. Final step (1 of 1) -> move plan 190 to Done/. Executable authored next (with a **Deposits:** block + plan_lint pre-check this time).
