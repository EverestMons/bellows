# Dev Log — Gate 2c Step 1 (gates.py fixes for strikes 4 & 5)

Pre-edit verification:
- _extract_plan_required_deposits at line 265: match yes
- _gate_rule_20_self_check at line 312: match yes

Fix 1 — _staging_ filter:
- Added _filter_transient_paths() helper at line 265 (before _extract_plan_required_deposits)
- Applied filter at all three return points (structured block, inline, legacy)
- Diff summary: +8 lines for helper, 3 return statements changed from `return paths` to `return _filter_transient_paths(paths)`

Fix 2 — tolerant rule_20 banner matching:
- Replaced line-by-line `line.startswith("PASSED — SELF-CHECK PASSED")` with re.search(re.MULTILINE)
- Pattern: `r'^\s*PASSED\s+—\s+SELF-CHECK\s+PASSED'` with re.MULTILINE
- Tolerates: leading whitespace/indentation, variable spacing around em-dash, decoration lines between banner and PASSED

Tests added: 10
- test_extract_deposits_filters_staging_prefix
- test_extract_deposits_filters_staging_in_structured_block
- test_extract_deposits_filters_staging_in_inline_format
- test_extract_deposits_filters_staging_in_legacy_prose
- test_rule_20_banner_in_fenced_block
- test_rule_20_banner_with_decoration
- test_rule_20_banner_with_shell_prompt_prefix
- test_rule_20_passed_line_with_indentation
- test_rule_20_no_banner
- test_rule_20_banner_without_passed

Test results: 84 passed in tests/test_gates.py (0.10s). Full suite: 314 passed, 5 failed (all pre-existing: 4 in test_decisions.py due to missing phrase file in worktree, 1 in test_runner_parser.py pre-existing timeout test). No regressions introduced.

Commit: f059af7
