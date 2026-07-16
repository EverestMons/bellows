verdict: continue
Step 1 verified — Bellows gates all PASS (0 failures, 7 files, all in scope) + Planner check (b) by direct read:
- New shared partial web/templates/_contract_owned_docs.html (3878 bytes).
- Included on BOTH contract_linked_docs.html:117 (replaced the inline owned-docs card) and contract_dashboard.html:208 (after Supporting Documents) — the Upload Contract Document form now renders on the dashboard.
- Dashboard route contract_dashboard (web/contracts.py:863) fetches SELECT * FROM contract_documents WHERE contract_id ORDER BY created_at DESC and passes contract_docs (line 886).
- Upload redirect: contract_upload_linked_doc uses fallback_url = request.referrer or url_for(contract_linked_docs) (line 2634) on all paths, so an upload started from the dashboard returns to the dashboard.
- Tests: 10 passed (6 existing + 4 new dashboard tests: dashboard shows Upload Contract Document + lists owned docs; upload-from-dashboard redirects back; sub-page still renders the card via the shared partial).
FROZEN core untouched. Proceed to Step 2 QA (full suite + byte-identical sub-page card + upload-from-dashboard + Rule 20).
