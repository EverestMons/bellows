verdict: continue
Rule 22 (b) substance — PASS.

Independently verified the constructed runtime prompt_text (imported the worktree module rather than trusting the dev log). PROMPTS["fuel_combined_csv_sample"] contains the SAMPLE-TABLE / PARTIAL-SNIP MODE block, S1-S5, and the Edit B Rule 10 ("NEVER extrapolate beyond the last visible row"); the old Rule 10 is absent from the sample key. Production fuel_combined_csv is byte-unchanged (no block, original Rule 10 intact). section/columns/paste_route match production.

Isolation and scope hold: branch diff main..9b26411 touches exactly 4 files — copilot_prompts.py, tests/test_copilot_fuel_combined.py, the dev log, and agent-prompt-feedback.md. No web/gap_dashboard.py, no engines/validator.py, no engine, no schema. The new source_*/extraction_warning rows are intentionally unparsed by IP this round per CEO decision 2.

Phase 2 resolved automatic-by-section: list_prompts() at copilot_prompts.py:2529 iterates PROMPTS.items(), so the contract_fuel section surfaces the new key with no selector edit.

Tests: 4 added (exists, markers, production-unchanged, metadata-match); targeted 33 to 37; full suite 1982 passed, 2 pre-existing failures unchanged (test_activity_import::test_get_activity_import_page, test_fix_links::test_no_tariff_rate_has_fix_url). Branch feat/isolated-fuel-sample-prompt-key pushed to origin; main untouched.

Non-blocking note: DEV built the key via two .replace() calls on the production prompt_text instead of duplicating it — an improvement (cannot drift from production); runtime verification confirms the result is exactly as specified. Not a behavioral deviation.

Issue continue. Advances to Step 2 (QA), which re-verifies isolation/scope via git diff and re-runs the suite.
