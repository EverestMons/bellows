# DEPOSITS_BLOCK_RE Blank-Line Tolerance — Dev Log

**Date:** 2026-04-28 | **Plan:** executable-deposits-block-regex-blank-line-2026-04-28

## Bug Case

Live evidence in `verdict-request-permission-prompt-substrate-2026-04-23-step-1.md`: the verdict request shows `Deposit: none` despite the plan declaring a valid block-form deposit at `bellows/knowledge/research/permission-prompt-substrate-2026-04-23.md`. The plan step structure has `**Deposits:**\n>\n> - \`...\`` — a blank quoted line (`>\n`) between the header and the first bullet. The regex `[> ]*-\s+...` requires `-` immediately after the optional blockquote prefix and cannot match the empty `>\n` line.

## Regex Change

**Before:** `[> ]*\*\*Deposits:\*\*\s*\n((?:[> ]*-\s+.*\n?)+)`
**After:** `[> ]*\*\*Deposits:\*\*\s*\n(?:[> ]*\n)*((?:[> ]*-\s+.*\n?)+)`

Single insertion of `(?:[> ]*\n)*` between `\n` and the bullet capture group. This allows zero or more blank quoted lines (lines containing only `>` and spaces) between the `**Deposits:**` header and the first bullet.

## Files Edited

1. `verdict.py` line 14 — constant `DEPOSITS_BLOCK_RE`
2. `gates.py` line 175 — inline regex in `_extract_plan_required_deposits()`

Both locations updated per the keep-in-sync comment.

## New Tests (6 total)

**In `tests/test_extract_primary_deposit_blocks.py` (3 tests):**
- `test_block_with_blank_quoted_line_between_header_and_bullets` — single blank `>` line, expects match
- `test_block_with_multiple_blank_quoted_lines` — two blank `>` lines, expects match
- `test_block_does_not_span_paragraphs` — empty line (no `>`) breaks block, expects None

**In `tests/test_rule_26_deposit_parser.py` (3 tests):**
- `test_extract_plan_required_deposits_blank_quoted_line` — single blank, expects `{'bellows/foo.md'}`
- `test_extract_plan_required_deposits_multiple_blank_quoted_lines` — multi-blank, expects same
- `test_extract_plan_required_deposits_does_not_span_paragraphs` — cross-paragraph, expects empty set

## Pytest Output

157 total tests: 156 passed, 1 pre-existing failure (`test_run_step_timeout` — unrelated). All 6 new tests pass. Zero regressions.
