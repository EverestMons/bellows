verdict: continue

Step 1 clean — all 11 gates PASS, 11 files changed, all in scope. Verified from the
artifacts (Rule 22(b), merged tree + dev log), not the agent summary:

=== THE FLAG I CHECKED, RESOLVED ===
- tests/test_ingest_perf_index_preload.py (325's file) changed because it calls
  _run_ingestion_rows(..., skip_xml=True) at 5 sites. The caller enumeration RECOVERED
  this caller (one I had not even named in the plan) and removed the kwargs;
  collect-only unchanged 8→8. This is the R1 caller-enumeration fold working as
  designed — a signature-change ripple, correctly handled, not scope creep.

=== LOAD-BEARING FOLDS CONFIRMED IN THE DIFF ===
- A-w2-1 SAVEPOINT isolation: enrich_pending_xml (ingest.py:377) wraps each invoice in
  SAVEPOINT sp_enrich (:425) / ROLLBACK TO sp_enrich (:460) — the batch-atomicity gap
  is closed.
- D2-1/D2-2 caps: ENRICH_PANEL_CAP=200, VALIDATE_PANEL_CAP=200 in config.py (259/260)
  with inline comments, from-imported into app.py's panel routes (:848/:876) — the
  bulk-hang the removed threshold prevented is re-bounded, cloning the STUB_PANEL_CAP
  pattern.
- Deliberate test updates recorded: test_run_ingestion_accepts_skip_xml DELETED (sole
  purpose was the removed param), 3 TestSkipXml tests updated to the new invariant.
- Blast-radius sweep (destruction D2) documented: consumers of invoice_charges/
  locations/lane_id/validation_results all use LEFT JOIN / WHERE patterns, no INNER-JOIN
  or [0]-index or divide-by-count — no THROW risk. The QA full suite is the backstop.
- D4 cadence: no ingest-time dependency on check_false_resolutions confirmed.
- BULK_VALIDATION_THRESHOLD retired cleanly (only app.py import+use, both removed).
- Deprecated _process_row cluster UNTOUCHED, imports preserved (W3).

=== CARRIED TO STEP 2 (QA) ===
- 23 tests in the new file; the three -k evidence buckets (mechanical 1, enrich 10,
  validate_panel 3) sum to 14 — the other 9 (always-defer, CLI-parity, template,
  empty-backlog, isolation, the validate cap test) are captured by full-suite.txt,
  which is the authoritative evidence. Verify the validate cap test ran (it is the only
  observer of VALIDATE_PANEL_CAP's LIMIT).
- The button-flow flow.txt and the full-suite arithmetic (baseline 2461+2, plus the
  new-file delta minus the deleted skip_xml test) are the Step-2 gates.

Proceed to Step 2 (QA).
