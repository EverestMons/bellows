verdict: continue

Planner verdict on executable-394 step 3 (myAP auto-apply drain) -> continue to step 4.

MECHANICAL GATE: all PASS, zero failures (5 files: ingest.py, dev log, test_ingest_buffer_apply.py [new], test_ingest_decoupling.py [new], test_ingest_performance.py; scope_check PASS).

SUBSTANCE (Planner-verified in code + by running tests):
- _apply_pending_activities (ingest.py:926) normalizes the lookup with the SAME _normalize_id/_normalize_load Step 2 buffered with (the V1 representation invariant is honored on BOTH sides — buffer-write and drain-read agree).
- SELECT pending_activities by normalized (pro,load) -> INSERT OR IGNORE into invoice_activities under the new invoice_id -> DELETE the drained rows. Idempotent (a second call finds nothing).
- Called on all THREE new-invoice paths (:822 PRO-match-supersedes, :835 PRO-match-older, :846 no-match new) — each AFTER _insert_new_invoice_cached + cache.mark_inserted, so the invoice exists before the drain (FK-safe; the ACID ordering the plan required).
- _try_upgrade_stub (:867) UNTOUCHED — legacy drain intact (MUST-PRESERVE).
- result.activities_applied_from_buffer counter added.
- TESTS RUN (Planner, foreground): test_ingest_buffer_apply.py (6) + test_ingest_decoupling.py (23) => 29 passed. The decoupling suite is a bonus covering diagnostic-390 Q1 (invoice-stub vs contract-stub independence).

NON-BLOCKING: 3 intermediate-decision blocks benign — existing fixtures lacked the pending_activities table (Step 1 migration), agent added it to those fixtures (a test-setup fix, not a production issue; the migration IS wired into init_db per Step 1).

Clean and correct. Proceed to step 4 (UI counters).
