verdict: continue
Step 4 (QA) verified — Bellows gates all PASS + Planner check (b) confirmed by direct read of the raw evidence:
- Full suite raw line: "2 failed, 2049 passed, 1 warning in 852.04s" — the 2 are the documented pre-existing failures (test_activity_import, test_fix_links); ZERO regressions. Count 2035->2049 = +14 new tests (upload 6 + file-serving 5 + re-parse 3).
- (a) /contracts/<id>/upload-linked-doc creates carrier_documents + contract_document_refs + parsed_rate_candidates (auto-parse) — 6 tests.
- (b) GET /documents/<id>/file serves PDF, rejects path traversal (os.path.realpath + startswith(data_dir) guard) — 5 tests.
- (c) _section_linked_docs Open link retargeted to /documents/<id>/file. (d) re-parse replaces candidates — 3 tests. (e) parse_pdf still green via shared helper — 9 tests. (f) FROZEN core unchanged.
- Rule 20 banner present verbatim; no rule_20 false-positive this time (Deposits block + verbatim banner authored per convention).
Final step (4 of 4) -> move plan 191 to Done/. Document-centric arc COMPLETE: Amendment A -> exec-189 (3-tab UI) -> exec-191 (upload relocation). Commits d52e324 (step 2) + 02a062f (step 3).
