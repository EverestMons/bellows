verdict: continue

Terminal QA step. Certifying the close on directly-read raw evidence, not agent summary.

Ten of eleven gate rows PASS, including the substantive ones: rule_20_self_check (banner byte-exact, PASSED line present), rule_22_verification (deposits present, table clean, no hedging), deposit_exists, scope_check, file_change_audit (4 files), receipt Complete.

The sole failure — qa_test_result "no .txt evidence deposit found" — is the known-benign false negative (gates.py:743 filters the Deposits block for a path ending .txt; this plan declared the evidence DIRECTORY there rather than naming the pytest .txt). Not an uncertified/failing run. Raw evidence read directly:
- check2 full suite: 2 failed, 2822 passed. The 2 failures are EXACTLY the two known pre-existing (test_activity_import::test_get_activity_import_page, test_fix_links::test_no_tariff_rate_has_fix_url); the mechanical set-difference (actual − baseline) is EMPTY → no regressions.
- check1: 46 new characterization tests pass.
- check3: DEV commit 42c0ba6c touched only tests/ and knowledge/ — no app.py/web/engines/ingestion. Additive-only invariant holds.

Planner (b) substance: the plan's purpose — a golden-master safety net for _invoice_list_query_parts before any refactor — is met (46 tests pinning where_sql/params/sort across the filter matrix, all six assigned_user sub-branches, both _has_crr branches, val_filter, order_sql NULL-handling, and the fallbacks). Every drafting-cycle fold that mattered executed correctly: the mechanical baseline compare (F8/F13) and the commit-scoped no-prod-change check (F11/F14) both worked as authored.

Authoring miss to carry forward (non-blocking): the qa_test_result .txt must be named in the DEPOSITS block, not only in the Rule 20 required_evidence_files — the cycle applied that known lesson to the wrong location. Continue → move to Done.
