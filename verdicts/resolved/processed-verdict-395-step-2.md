verdict: continue
Clean gate — plan 395 Step 2 (terminal QA) auto-continued; CEO-approved. 395 completes and moves to Done.

Grounds:
- Mechanical gate (Bellows-produced): Gate Result Passed=True, failures=[]; rule_20_self_check PASS (banner byte-exact), rule_22 PASS (verification table clean, no hedging), scope_check / deposit_exists / qa_step_detection PASS.
- Planner-confirmed: plan 395 is test-only — git diff HEAD~1..HEAD shows ONLY tests/test_pricing_versions_qa.py + the dev log; the previously-failing test_dashboard_shows_version_bar (now _hides_legacy_version_bar) passes. ZERO regressions from 395.
- Full-suite raw evidence: 5 failed, 2620 passed. TWO are the CLAUDE.md-known pre-existing (test_activity_import, test_fix_links). THREE (test_forge_export_sanitization::test_table_created_on_existing_v19_database; test_fuel_import_conflict::MigrateExistingDB test_v17_db_gets_table_after_init + test_fresh_db_has_table_at_v19) are STALE schema-version pins asserting SCHEMA_VERSION==21 while the schema is now v22 (database.py:26) — introduced by the CONCURRENT plan 394 schema-v22 bump (commit 4788b01), NOT by 395. The QA report documents this accurately and correctly attributes 0 regressions to 395.
- CEO decision: continue 395 -> Done; a separate small test-only corrective will update the 3 stale ==21 pins.

Terminal step -> move plan 395 to Done/.
