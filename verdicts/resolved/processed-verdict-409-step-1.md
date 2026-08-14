verdict: continue

Planner verdict on executable-409 step 1 (strip /ingest + defer enrich) -> continue to step 2 (foreground QA).

MECHANICAL GATE: all PASS (4 files: app.py, ingest.html, test_ingest_page_separation.py, dev log; scope_check PASS).

SUBSTANCE (Planner-verified in code + ran tests):
- REMOVED from ingest.html (grep = 0 remaining): Direct XML Paste form, "Stubs Needing myAP" panel, copyProList, CardLoader.init(_enrichEl) forced init.
- REMOVED from app.py: the stub query + stub_invoices from render_template (grep = 0).
- KEPT (verified): /ingest/xml-paste route (2 refs — 2nd caller invoice_detail.html), buffered-activities counter (2 refs).
- TESTS (Planner ran, foreground): 3 new — test_paste_form_and_stub_panel_absent, test_stub_query_not_run_on_load, test_enrich_xml_not_auto_fetched (the W1 fold: asserts the enrich query is not auto-fetched on load) + existing separation traces => 9 passed. Page still renders 200; the S1 stub scan no longer runs on load; the S2 enrich forced-init is gone.
- CSV/activity POST paths untouched.

Clean and correct. Proceed to step 2 — FOREGROUND full-suite QA + Rule 20.
