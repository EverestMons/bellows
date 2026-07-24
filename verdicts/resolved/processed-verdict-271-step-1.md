verdict: continue
Plan 271 Step 1 (DEV) verified clean by the Planner. All gates PASS (scope_check, deposit_exists, rule_22; 3 files_changed = plan_lint.py + test file + dev-log).

Rule 22(b) — the §4 self-check is implemented correctly and warn-first as designed:
- WARN-FIRST proven: every WARN is a print(), never touches the results list that controls exit code; the live runs show plan_lint exits 0 on both a tier-less plan (WARN fires) and a real T2 plan (WARN fires). It can never block a deposit — the property the CEO's "no hard rules immediately" rests on.
- Behaviour matches DRAFTING_CYCLE.md §4: cycle_tier declaration, `## Drafting Cycle` block for T1/T2, all five lenses (case-insensitive keyword match), cold-panel line for T2, a dry-closing (not fold) check, T0 tier-only. Degenerate/malformed blocks WARN, never crash; reads UTF-8.
- Tests OBSERVE the effect (sub-question 3.2 applied to its own gate): the compliant-T2 test uses plan 270's REAL Cycle Log block; the tier-less test uses plan 265's REAL header; plus synthetic fixtures (T1-missing-ACID, T0-clean, fold-closing). 21 tests pass (15 existing + 6 new).
- Destruction lens handled: ONE existing test (`test_lint_single_step_diagnostic_no_e_fail`) asserted `"WARN" not in stdout` (too broad); narrowed to `"consider using uppercase" not in stdout`, preserving its original intent (no step-heading-case WARN) rather than weakening the new check. No other test broke.

⭐ The gate validated itself on its first real target: plan 270 (a T2 plan) has no cold-panel line in its Cycle Log, so the check correctly WARNs — warn-first, so nothing blocked, but the reminder is exactly the point. (A minor authoring gap in 270 that the gate now surfaces going forward.)

Proceed to Step 2 (QA — full bellows suite + independent reproduction of warn-first + each §4 rule).
