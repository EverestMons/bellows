verdict: continue
Findings accepted (delegated authority; clean gates + substance verified). Root cause nailed:
- GET /invoices/<id> (app.py:1358-1364) runs run_batch UNCONDITIONALLY on every view — 30-80ms, 70-80% of wall time — and BYPASSES the existing stale-check because passing explicit invoice_ids skips smart-scoping (validate_batch.py:55-56).
- Search itself ~1ms (indexed idx_invoices_pro); list view does NOT per-row validate. So the bottleneck is purely on-view live validation.
- "Always fresh on view" is NOT a deliberate invariant — the stale-flag infra (validation_results.stale, invoices.last_validated_at, contracts.updated_at) already exists but is not wired into the view path (the batch path already uses it).
- Recommended fix (Tier Small, web-layer, NO FROZEN edit): A1 conditional re-validate (skip run_batch when stale=0 AND validated_at <5min, serve cached gate rows) + A2 drop _update_validation_quality_summary() from the view path + A3 skip _preflight() for single-invoice. Expected 30-80ms saved on repeat views.
- Index work (B1/B2) + FROZEN gate consolidation (C1-C3) = separate plans (C needs explicit CEO approval).
- Open edge: invoice field edits do not currently set stale=1; POST /validate/<id> force-refresh button is the escape hatch.
Final step (1 of 1) -> move plan 192 to Done/. Executable authored after CEO confirms freshness policy + edit-staleness handling.
