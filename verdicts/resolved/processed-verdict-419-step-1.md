verdict: continue

Planner verdict on executable-419 step 1 (idempotent enrich fix) -> continue to step 2 (dedup cleanup tool).

MECHANICAL GATE: all PASS (3 files: ingest.py, dev log, test_xml_enrich_idempotency.py; scope_check PASS).

SUBSTANCE (Planner-verified in code + ran tests):
- apply_xml_to_invoice now: SAVEPOINT sp_apply_xml -> DELETE invoice_charges + DELETE locations (inside savepoint, before insert loops) -> existing header UPDATE + insert loops + xml_parsed -> RELEASE on success; except: ROLLBACK TO sp_apply_xml + RELEASE + raise. Exactly the validate-route atomicity pattern (417 Q2).
- Delete targets ONLY charges+locations (XML-exclusive per 417 Q1); header UPDATE untouched; no xml_parsed skip-guard added (re-fetch stays allowed, 417 Q5).
- TESTS RUN (Planner, foreground) = 8 passed: idempotency (double/triple enrich stable charge+location counts), ATOMICITY (test_failed_reenrich_keeps_prior_charges/_locations + test_failed_enrich_never_zero_charges — the never-zero-charge guarantee, 3 ways), fresh-invoice no-op + xml_parsed set.

Clean and correct — the Fetch-XML duplication bug is fixed at the choke point, atomically. Proceed to step 2 (dedup_xml_data.py cleanup tool; re-enrich-only per the walk-1 fold — never empties a no-file invoice).
