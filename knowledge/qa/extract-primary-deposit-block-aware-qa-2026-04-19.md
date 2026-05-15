# QA Report — extract_primary_deposit Block-Aware
**Date:** 2026-04-19 | **Plan:** executable-extract-primary-deposit-block-aware-2026-04-19

## Deliverable Verification (Rule 17)

| Deliverable | Expected | Status | Evidence |
|---|---|---|---|
| `bellows/verdict.py` — `DEPOSITS_BLOCK_RE` constant | `DEPOSITS_BLOCK_RE =` on line 14 | ✅ | grep_deliverables.txt line 2 |
| `bellows/verdict.py` — `BLOCK_BULLET_RE` constant | `BLOCK_BULLET_RE =` on line 15 | ✅ | grep_deliverables.txt line 5 |
| `bellows/verdict.py` — `DEPOSITS_BLOCK_RE.search` in function body | `DEPOSITS_BLOCK_RE.search` on line 38 | ✅ | grep_deliverables.txt line 8 |
| `bellows/tests/test_extract_primary_deposit_blocks.py` — `test_block_single_md_path_returned` | def on line 11 | ✅ | grep_deliverables.txt line 11 |
| `bellows/tests/test_extract_primary_deposit_blocks.py` — `test_block_multiple_md_first_returned` | def on line 26 | ✅ | grep_deliverables.txt line 12 |
| `bellows/tests/test_extract_primary_deposit_blocks.py` — `test_block_none_bullet_returns_none` | def on line 38 | ✅ | grep_deliverables.txt line 13 |
| `bellows/tests/test_extract_primary_deposit_blocks.py` — `test_block_directory_only_returns_none` | def on line 49 | ✅ | grep_deliverables.txt line 14 |
| `bellows/tests/test_extract_primary_deposit_blocks.py` — `test_no_block_falls_back_to_legacy` | def on line 64 | ✅ | grep_deliverables.txt line 15 |
| `bellows/tests/test_extract_primary_deposit_blocks.py` — `test_block_with_blockquote_prefix_still_matches` | def on line 74 | ✅ | grep_deliverables.txt line 16 |

## Targeted Test Results

| Test File | Tests | Result |
|---|---|---|
| `test_extract_primary_deposit_blocks.py` | 6 | 6/6 PASSED |
| `test_verdict.py` | 11 | 11/11 PASSED |
| `test_gates.py` | 22 | 22/22 PASSED |
| `test_rule_26_deposit_parser.py` | 6 | 6/6 PASSED |
| **Total** | **45** | **45/45 PASSED** |

Zero regressions across all buckets.

## Rule 20 — Mandatory QA Self-Check

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: bellows/knowledge/qa/evidence/extract-primary-deposit-block-aware-2026-04-19/
Files verified: 2
```
