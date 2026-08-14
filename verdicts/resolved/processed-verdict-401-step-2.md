verdict: continue

Planner verdict on executable-401 step 2 (ingest suppression skip — money pipeline) -> continue to step 3.

MECHANICAL GATE: all PASS (3 files: ingest.py, dev log, test_ingest_deleted_suppression.py; scope_check PASS).

SUBSTANCE (Planner-verified in code + ran tests):
- Tombstone preloaded ONCE per batch (ingest.py:704) with a try/except guard (:702-706) -> a DB lacking deleted_invoices degrades to deleted_ids=set() (no suppression), graceful.
- Skip at the TOP of the per-row loop (:726 `if invoice_id in deleted_ids: result.deleted_skipped += 1; continue`) — BEFORE status/carrier/whitelist checks and BEFORE all_invoice_ids/valid_rows, so a tombstoned invoice never inserts or enriches (no partial row). Correct choke point.
- result.deleted_skipped is an IngestionResult attr (:497), surfaced in summary (:515-516) and logged (:790-791) — the W1 fold (result attr, testable) landed.
- TESTS RUN (Planner, foreground): test_ingest_deleted_suppression.py = 6 passed (skip-on-tombstone, normal-import, no-partial-row).
- Existing ingest filters/insert/enrich untouched; contract-stub + pending-buffer families untouched.

Clean and correct. Proceed to step 3 (delete_not_xml.py CEO-run cascade tool). NOTE: the step-1 version-assertion gap (3 stale ==22 tests) still stands for QA — to be swept permanently.
