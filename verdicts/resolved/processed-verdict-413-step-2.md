verdict: continue
Clean gate -- plan 413 Step 2 (terminal QA) auto-continued under delegated verdict authority. 413 to Done.

Grounds:
- Mechanical gate: Gate Result Passed=True, failures=[]; permission_denials PASS (no Monitor denial -- the foreground-no-Monitor instruction worked), rule_20_self_check PASS (banner byte-exact), rule_22_verification PASS (deposits present, table clean, no hedging).
- Raw full-suite evidence (knowledge/qa/evidence/no-validation-on-invoice-view-2026-08-14/full-suite.txt): 2 failed, 2668 passed; the 2 failures are EXACTLY the CLAUDE.md-known pre-existing (test_activity_import::test_get_activity_import_page, test_fix_links::test_no_tariff_rate_has_fix_url). ZERO regressions.
- Step 1 removed the auto-validation-on-view block; the new caching tests lock run_batch NOT-called on any view + called on the button.

Feature landed via a genuine 3-walk cycle: invoice-detail view no longer auto-validates; validation runs only on the Run Validation button. Move plan 413 to Done.
