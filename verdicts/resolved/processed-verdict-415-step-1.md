verdict: continue
Step 1 (DEV) — mechanical gate clean (Gate Result Passed: True; all 11 checks PASS; 3 files changed within scope: web/contracts.py, tests/test_contracts_versioning_view.py, the dev log). The 1 intermediate-decision block is the agent narrating its systematic test update, not an off-plan decision.

Planner (b) substance check — verified against HEAD, not vouched:
- `_canonical_ccode_set` helper present (`:110`); `_get_dated_siblings` new signature `(db, carrier_name, contract_type, customer_code_set, current_contract_id)` (`:121`) with the empty-set standalone branch (`:163-164`, returns only current_contract_id's row) and the non-empty member filter (`:166`, `_canonical_ccode_set(rd["customer_codes"]) == customer_code_set`).
- All 6 call sites pass both new args: list grouping `:531` (with the `__standalone__` sentinel key at `:526`) + the 5 switcher sites (`:848, :3657, :4110, :4898, :5136`).
- Money-path gate RAN and recorded ZERO hits (`grep carrier_name engines/validator.py` and `grep _get_dated_siblings engines/`) — the display/nav-only premise is proven, not assumed.
- The test-premise correction (the cycle's key catch over diag-410) landed: 11 TestGetDatedSiblings tests updated to seed shared CUST001 c-codes + new signature (not treated as signature-only), and all 5 new tests exist (test_split_differing_ccode_sets, test_join_identical_ccode_sets, test_empty_ccode_set_standalone, test_consumer_observe_split_in_list, test_helper_dual_shape).
- Raw targeted result in the dev log: `-k contract` → 421 passed, 0 failed.

Non-terminal step → continue to Step 2 (QA full suite + Rule 20).
