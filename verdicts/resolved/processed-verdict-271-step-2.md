verdict: continue
Plan 271 Step 2 (QA) verified clean by the Planner — terminal close authorized. All gates PASS (rule_20_self_check banner byte-exact; rule_22_verification table-clean-no-hedging; scope_check).

Rule 22(b) — the QA EXECUTED all 7 checks with raw evidence (echo $? shown), corroborating the DEV verification:
- Warn-first PROVEN: tier-less plan + T1-missing-ACID → WARN with exit 0 (echo $? = 0). The gate can never block a deposit — the CEO's "no hard rules immediately" property holds.
- Each §4 rule fires independently (no-tier, missing-lens naming ACID, missing-cold-panel, fold-closing → WARN; T0 tier-only → clean) — all exit 0.
- Degenerate/empty `## Drafting Cycle` block → WARNs for all missing elements, no crash/traceback.
- Compliant T2 fixture (270's real block + a cold-panel line) → clean, no drafting-cycle WARN.
- Existing behaviour intact: the ONE test edit narrowed an over-broad assertion, intent preserved; 21 lint tests pass; the FULL BELLOWS SUITE is 813 passed / 0 failures / 0 regressions.
- Scope confined to scripts/plan_lint.py (+41) + tests/test_plan_lint.py.

The Drafting Cycle system is now complete END TO END: the doctrine (DRAFTING_CYCLE.md v1.0, PLANNER_TEMPLATE v4.80) + the warn-first plan_lint §4 self-check. Blocking remains a deferred one-line WARN→FAIL flip, per the baseline-first direction.

Terminal — proceed to close (merge the plan_lint change to bellows main + move plan 271 to Done/).
