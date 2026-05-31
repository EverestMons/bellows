verdict: continue
Rule 22 — Planner-direct QA verification, PASS. The Step 2 QA agent could not run substantively: on resume the worktree was re-created at main HEAD instead of the feature branch (BACKLOG 2026-05-30), so QA correctly found an empty tree and stopped. Verification performed directly against main after cherry-picking Step 1's commit.

Verified on invoice-pulse main (080024c):
(a) PROMPTS["fuel_combined_csv_sample"] contains SAMPLE-TABLE / PARTIAL-SNIP MODE, S1-S5, source_is_partial_snip, and the Edit B Rule 10 ("NEVER extrapolate beyond the last visible row").
(b) Production fuel_combined_csv byte-unchanged (no block, original Rule 10 intact).
(c) Scope: the cherry-picked commit touches 4 files — copilot_prompts.py, tests/test_copilot_fuel_combined.py, the dev log, agent-prompt-feedback.md. No web/gap_dashboard.py, no validator, no engine, no schema.
(d) section/columns/paste_route match production.
(e) Full suite on main: 1982 passed, 2 failed — both pre-existing (test_activity_import::test_get_activity_import_page, test_fix_links::test_no_tariff_rate_has_fix_url), zero new regressions. Targeted file 37 passed.

Step 1's commit 9b26411 is cherry-picked onto main (080024c) and pushed to origin. Continue to Done.
