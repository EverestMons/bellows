continue

Planner Rule 22(b) substance review — PASS, CEO-approved to proceed to QA. The DEV build (commit 2164ff4) faithfully implements the approved per-charge view design and is fully committed.

Verified by diff inspection:
- READ-SIDE ONLY confirmed: commit touches only app.py (+134), web/templates/invoice_detail.html (+174/-10), web/templates/_tier_badge.html (+6), tests/test_percharge_view.py (new), dev log, feedback. ZERO touch to engines/validator.py, engines/confidence.py, validate_batch.py, database.py.
- Handler (app.py invoice_detail): charge grouping linehaul/fuel/accessorial by accessorial_code per the design classification rule; gate_result_map; batched document/version name resolution (collects unique scope+id pairs from gate-level AND Gate-9 per-line results, resolves in 2-3 parameterized IN queries against global_documents/carrier_documents/contract_pricing_versions); NULL-provenance fallback to "Contract terms"/"Carrier rules tariff"; per-group display reads first-class columns (expected/invoice linehaul+fsc, gross_charge, discount_pct, eia_price, fsc_pct, fuel_base, weight). Parameterized SQL, defensive NULL handling.
- Field map followed: 15/16 first-class columns consumed (C); data_json only for the marked-D calc-chain detail + Gate-9 per-line results[].
- DEV caught + fixed a real bug: grand-total row sum(attribute='weight') crashes on NULL weight → summed from group subtotals instead.
- Preserved behaviors: gate cards (Row 8), diagnostics sidebar, XML-recovery banner unchanged.
- Targeted tests: 24 passed, 0 failed (18 new tests; -k filter excluded the 2 known pre-existing).

The lone gate failure (scope_check on tests/test_percharge_view.py) is a BENIGN false-positive: Step-1 item 5 directed the DEV to add tests; the new file fulfills it but wasn't inlined by exact name. Rule 22(b) Planner-adjudicated continue (precedent #98, #81, clusters 8/9/10).

Proceed to Step 2 (QA): full suite -v/--tb=line once; view renders for a validated invoice (grouped table + per-charge tier/document/version + expected-vs-billed + rate_confirmed); ZERO diff to engine/schema; preserved behaviors; count reconciliation; closeout to Done + PROJECT_STATUS. Disk guard active (~21GB). continue.