# QA Report — DEPOSITS_BLOCK_RE Blank-Line Tolerance

**Date:** 2026-04-28 | **Plan:** executable-deposits-block-regex-blank-line-2026-04-28

## Rule 17 — Deliverable Verification

| # | Deliverable | Check | Status |
|---|------------|-------|--------|
| a | `verdict.py` — `DEPOSITS_BLOCK_RE` contains `(?:[> ]*\n)*` | `grep -n "DEPOSITS_BLOCK_RE = re.compile" verdict.py` shows fix at line 14 | ✅ |
| b | `gates.py` — inline regex contains `(?:[> ]*\n)*` | `grep -n "block_match = re.search" gates.py` shows fix at line 175 | ✅ |
| c | `test_extract_primary_deposit_blocks.py` — 3 new test functions | `grep -c` returns 3 | ✅ |
| d | `test_rule_26_deposit_parser.py` — 3 new test functions | `grep -c` returns 3 | ✅ |

Evidence: `knowledge/qa/evidence/executable-deposits-block-regex-blank-line-2026-04-28/grep_deliverables.txt`

## Test Execution Summary

Full pytest suite: **157 total, 156 passed, 1 failed** (pre-existing `test_run_step_timeout` — unrelated to this change).

All 6 new tests pass:
- `test_block_with_blank_quoted_line_between_header_and_bullets` — PASSED
- `test_block_with_multiple_blank_quoted_lines` — PASSED
- `test_block_does_not_span_paragraphs` — PASSED
- `test_extract_plan_required_deposits_blank_quoted_line` — PASSED
- `test_extract_plan_required_deposits_multiple_blank_quoted_lines` — PASSED
- `test_extract_plan_required_deposits_does_not_span_paragraphs` — PASSED

Zero regressions. Evidence: `knowledge/qa/evidence/executable-deposits-block-regex-blank-line-2026-04-28/pytest_full.txt`

## Behavioral Verification

Ran `extract_primary_deposit` and `_extract_plan_required_deposits` against the real plan that exposed the bug (`diagnostic-permission-prompt-substrate-2026-04-23.md`, Step 1).

- `extract_primary_deposit`: `bellows/knowledge/research/permission-prompt-substrate-2026-04-23.md`
- `_extract_plan_required_deposits`: `{'bellows/knowledge/research/permission-prompt-substrate-2026-04-23.md'}`

Both return the expected path. Previously both returned `None` / empty set. Evidence: `knowledge/qa/evidence/executable-deposits-block-regex-blank-line-2026-04-28/behavioral_check.txt`

## Rule 20 — QA Self-Check

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: /Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/evidence/executable-deposits-block-regex-blank-line-2026-04-28/
Files verified: 3
```

## BACKLOG #5 Verdict

**Closeable.** The regex fix in `verdict.py` and `gates.py` resolves the blank-quoted-line tolerance gap. 6 new tests lock in both the positive property (blank lines tolerated) and the negative property (cross-paragraph spans rejected). Behavioral check confirms the real-world plan that exposed the bug now extracts correctly.
