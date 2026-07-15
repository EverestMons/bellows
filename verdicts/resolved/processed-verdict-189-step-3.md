verdict: continue
Benign gate failure (rule_20_self_check) — continue-with-reasoning under delegated verdict authority.

Root cause: the executable header omitted a **Deposits:** block naming the QA evidence path, so rule_20 had nothing to match (a plan-authoring artifact on the Planner side, NOT a QA defect — a documented benign class). Corroborated by every other gate PASS: deposit_exists PASS, file_change_audit PASS (1 file), rule_22_verification PASS ("Deposits present, verification table clean, no hedging"), scope_check PASS.

Raw QA evidence verified by direct read (knowledge/qa/evidence/contract-3tab-slot-model-qa-2026-07-15.md):
- Full suite raw line: "2 failed, 2035 passed, 1 warning in 826.59s" — the 2 are the documented pre-existing failures (test_activity_import::test_get_activity_import_page, test_fix_links::test_no_tariff_rate_has_fix_url); ZERO regressions.
- Render verification: all 6 rate sections (fuel/lanes/accessorials/rates/fak/areas) show 3 tabs (Copilot Extraction / Found Information / Other), no Inline-text or PDF-Upload tab, found/other slots set, linked-docs include newly added to FAK + Areas, Open/Download control renders on all 6.
- /parse-pdf retained at web/gap_dashboard.py:2174; 9 parse-pdf tests pass.

Final step (3 of 3) — move plan 189 to Done/. 3-tab section restructure shipped clean.
