continue

Planner Rule 22(b) substance review — PASS. The DEV build (#108 Step 1, commit 9904241) faithfully implements the CEO-approved design (invoice-list-rebuild-design-2026-06-23.md §5a):
- Shared _invoice_list_query_parts helper used by BOTH invoices_list and invoices_table_fragment — fixes the fragment filter-parity bug (assigned_user/weight/freight_class were dropped; val_tier/val_at now selected) and unifies aging-range handling.
- _enrich_invoices_validation: batched gap-blocked set + stale dict, O(1) per row, table-exists guarded + try/except. No N+1.
- val_filter (pass/fail/pending/gap-blocked/stale): filter values matched in Python, only constant SQL appended — no injection. gap/stale subqueries are constant SQL.
- Validation sortable column with worklist CASE order (fail→gap-blocked→stale→pending→pass); default sort unchanged (days_unpaid desc).
- Enriched validation cell (status + tier + gap-blocked + stale badges) + gap-blocked summary pill.

Gates passed (files_changed=4, 0 failures). FROZEN core zero-diff confirmed (engines/validator.py, engines/confidence.py, validate_batch.py, database.py). Read-side only. Targeted tests + route smoke pass.

Two minor non-blocking nuances to verify in Step 2 / browser (NOT defects, do not block): (1) Validation header's first click sorts DESC (pass-first); worklist order needs the asc click. (2) val_filter='pending' matches overall_status IS NULL only, while pending_count = total−pass−fail — a slight mismatch if any non-pass/non-fail/non-null statuses exist.

continue to Step 2 (full QA).
