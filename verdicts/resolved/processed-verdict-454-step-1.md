verdict: continue

Mechanical gate clean: Gate Result Passed: True, no failures, pause is header_pause (the plan's own pause_for_verdict: after_step_1). files_changed = tests/test_invoice_list_query_parts.py + the dev-log append only.

Planner (b) substance check, verified directly:
- F18: `test_days_since_shipment_uses_expression` asserts `order_sql` contains `CAST(julianday('now') - julianday(i.shipment_date) AS INTEGER)` — the `_sort_expr_map` expression walk 7 found unpinned. Pins the silent-regression-risk branch.
- F19: `test_..._val_filter="__none__"` pins the fall-through (no clause) case.
- Ran `pytest -k "days_since_shipment or none or val_filter"` myself → 2 passed. Suite now 54 (was 52).
- `git show --name-only 658d8d98` = tests/ only, no production source.

Closes F18 + F19, the last two coverage gaps from walk 7's complete matrix audit. Continue to Step 2 QA.
