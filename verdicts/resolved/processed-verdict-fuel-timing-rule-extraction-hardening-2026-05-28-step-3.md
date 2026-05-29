verdict: continue
Rule 22 (b) substance — PASS. Final QA is clean.

All 8 dimensions verified with concrete evidence on disk:
- Dimension A (4 prompts): "Common patterns:" gone from all in-scope prompts, UNKNOWN inline with timing_rule and effective_day, 3-field MOR blocks present
- Dimension B (write parser): _parse_fuel_combined_csv at gap_dashboard.py:1177, dispatch entries in _SECTION_PARSERS (1612-1619) and importers (2024-2027) and _SECTION_HEADERS (utils.py:99-100), template section_type updated
- Dimension C (validator): _RECOGNIZED_TIMING_RULES set, UNKNOWN/unrecognized detection, verbatim failure messages match blueprint, prior_monday branch correct, same_week handler added
- Dimension D (dropdown): all 6 options present with legacy value mapping
- Dimension E (schema): no schema change confirmed, NOT NULL columns intact with original defaults
- Dimension F (tests): independent re-run 1973 passed = baseline + 27 new, same 2 pre-existing failures (test_get_activity_import_page, test_no_tariff_rate_has_fix_url), zero regressions, exact match to blueprint and dev log predictions
- Dimension G (end-to-end trace): seven-step prose trace through user upload → sanitize → parse → import → store → validate → resolve, correct at each step
- Dimension H (regression): bracket-only path unaffected, _SECTION_PARSERS["fuel"] untouched, defaults still apply for empty params

Evidence directory contains all 10 expected files. Spot-checked full-suite.txt directly: "2 failed, 1971 passed" honest match.

Rule 20 self-check passed with verbatim banner. PROJECT_STATUS milestone appended at top of Current Sprint section, accurate summary.

DEV deviation (same_week branch addition) reviewed and accepted - correct fix for blueprint omission, transparent reporting.

Out-of-scope handling correct: dead fuel_combined prompt's "Common patterns:" at L1504 left untouched per CEO decision #4. QA called this out in Decisions Made.

Final step — Bellows will now move plan to Done/.

Original CEO goal: "if the prompt cannot find anything then i would like the result to be null instead of filling in something false."
Achieved end-to-end:
- Prompts now instruct UNKNOWN when contract is silent on timing
- Write path preserves the UNKNOWN value (params section no longer stripped)
- Storage stores "UNKNOWN" verbatim as string sentinel
- Validator fails Gate 8 loudly with actionable fix URL when UNKNOWN reaches validation
- Dropdown surfaces UNKNOWN as a manual option for the resolution flow

Plan complete. Authorize close.
