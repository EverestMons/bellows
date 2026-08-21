verdict: continue

Step 2 (QA) of exec-484 (contract-merge pick-main) is clean and the raw evidence certifies it green. Terminal step — continue closes the plan. Pick-main SHIPPED; the contract-merge arc is complete (Phase 2b smart-union + lane-specific-FAK pick-main deferred).

Planner-verified facts:
- Step 1 (DEV) auto-proceeded with no pause (no verdict-request-484-step-1) → gate clean. Step 2 (QA) Gate Result Passed: True; failures: []. scope_check PASS, rule_20_self_check PASS (banner byte-exact, PASSED line present).
- Raw pytest evidence read directly (knowledge/qa/contract-merge-pick-main-pytest.txt): `611 passed, 2360 deselected, 1 warning in 56.97s` — 0 failed, 0 errors, matching known_failures: 0. Targeted selector (2360 deselected + 57s) — temp-leak avoided.
- Substance (Planner check b) verified against the committed engine (engines/contract_merge.py): `merge_with_main` defined; the lane-specific-FAK presence block; the Q1 non-child-ref fix (invoice_charges / fuel_bracket_conflicts / fuel_bracket_structural_issues, 5 refs); 26 tests in tests/test_merge_pick_main.py.
- The LOAD-BEARING money-path property (Q2 combine-free — the 3rd cold read's core confirmation) is directly TESTED and passing: test_one_set_main_survivor + test_one_set_main_loser (the anti-combine one-set post-condition for BOTH main choices — survivor ends with exactly the main's set, none of the other's); test_fak_delete_never_touches_lane_specific (F-C3 `contract_lane_id IS NULL` filter); test_contract_wide_fak_differs_resolved_by_main / _loser_wins; test_invoice_charges_lane_ref_nulled (Q1-F2, the common-case safe-but-blocks fix).

Continue closes exec-484. The full contract-merge arc: diag-465 + exec-469 (version-dated links) + exec-475 (identical-or-empty merge) + exec-477 (reconciliation diff UI) + exec-480 (differ-check completeness) + exec-484 (pick-main). Deferred: Phase 2b smart-union fold; lane-specific-FAK pick-main.
