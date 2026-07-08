verdict: continue
Step 1 (DEV) gate clean (all mechanical PASS, 8 files in scope). Planner check (b) confirmed by diff inspection of cba0cbe:
- Engine: compute_materialization_rows applies `start_mills += 1` guarded by `pattern_source == "rule_fallback"` only; cold/seeded unaffected (F1/F5).
- Preview: contract_fuel_infer sets preview_start = preview_rows[0]["price_floor"] for rule_fallback, leaves result.start_price unmutated (F2/F3) — corroboration/TOCTOU stable.
- scripts/remat_fallback_fuel_offset.py present; boundary-alignment test uses composite table-then-formula effective_fsc vs the validator formula (correct gate_8 model). The agent's mid-step adjustment (eia=6.049 exclusive-ceiling → formula fallback) is correct gate_8 behavior, not a defect.

REQUIREMENT FOR STEP 2 QA: the boundary-alignment test currently checks only the first two rows (5.999-6.099). Because the fix is a single uniform anchor shift this proves the whole grid, but the CEO specifically raised cumulative drift across the table. Step 2 MUST verify table-vs-formula alignment at a FAR-OUT row near the $10 ceiling (e.g. eia ~9.999 and its adjacent boundary) — either by extending test_fallback_materialization_matches_validator_at_boundaries or an explicit QA spot-check with evidence. Also verify the remat tool dry-run+apply on a TEST db only, and that the QA report FLAGS the production re-materialization as a manual CEO step.

CEO delegated verdict authority. Proceed to Step 2 QA.
