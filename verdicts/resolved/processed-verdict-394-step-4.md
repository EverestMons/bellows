verdict: continue

Planner verdict on executable-394 step 4 (UI + result surfacing) -> continue to step 5 (QA).

MECHANICAL GATE: all PASS, zero failures (5 files: app.py, database.py, dev log, test_activity_import.py, ingest.html; scope_check PASS).

SUBSTANCE (Planner-verified in code + by running tests):
- app.py result-key rename SWEPT: no stale invoice-side stubs_created reader remains; :667 fallback now "buffered_activities": 0. The only surviving stubs_created is result.contract_stubs_created (:372-377) — the CONTRACT-stub family, CORRECTLY untouched (MUST-PRESERVE #2, Q1 decoupling).
- ingest.html: "Buffered (awaiting myAP)" counter (:496-498) + held/auto-applied message (:510-513) + "Activities Auto-Applied" (:319) + history "Buffered" column (:536,548). Old "Stubs Created" counter replaced.
- database.py comment corrected ("activities buffer when unmatched").
- TESTS RUN (Planner, foreground): activity_import log/result/buffer subset => 11 passed, incl. test_error_fallback_uses_buffered_activities (verifies the :667 fallback key).

NON-BLOCKING: 1 intermediate-decision block benign (adding a render test).

Clean. Proceed to step 5 — QA is the safety net (full suite + Rule 20). All four DEV steps implemented correctly; the invoice-stub reframe is complete and the contract-stub family is provably untouched.
