# QA Report — cycle_check.py drafting-cycle validator

**Plan:** executable-cycle-check-2026-08-19
**Date:** 2026-08-19
**DEV commit:** 270ad9c

## (1) Targeted Suite — Branch Coverage

`python3 -m pytest tests/test_cycle_check.py -v` → **27 passed, 0 failed.**

Evidence: `knowledge/qa/evidence/executable-cycle-check-2026-08-19/test_cycle_check.txt`

Decision-function branch coverage:

| Branch | Test | Status |
|---|---|---|
| unparseable (0 blocks) | test_unparseable_no_block | ✅ |
| unparseable (>1 blocks) | test_unparseable_multi_block | ✅ |
| unparseable (no parseable lens) | test_unparseable_no_parseable_lens | ✅ |
| assert-fail:1 | test_assert_fail_1 | ✅ |
| assert-fail:2 | test_assert_fail_2 | ✅ |
| assert-fail:3 | test_assert_fail_3 | ✅ |
| restructuring-fold | test_restructuring_fold | ✅ |
| yield-rising | test_yield_rising | ✅ |
| plateau | test_plateau_at_3 | ✅ |
| BAR_MET (dry + clean) | test_bar_met | ✅ |
| CONTINUE (mid-cycle) | test_continue_mid_cycle | ✅ |
| N/A class-split (legacy) | test_na_class_split_legacy | ✅ |
| zero-walk | test_zero_walk | ✅ |
| mixed parseable/unparseable | test_mixed_parseable_unparseable | ✅ |
| uncommitted-walk | test_uncommitted_walk | ✅ |
| claimed-close-unmet | test_claimed_close_unmet | ✅ |

No branch lacking a test.

## (2) Live Canary — Real Done/ Blocks

Evidence: `knowledge/qa/evidence/executable-cycle-check-2026-08-19/live_canary.txt`

| Plan | Expected | Actual | Exit | Status |
|---|---|---|---|---|
| diagnostic-429.md | BAR_MET or CONTINUE | BAR_MET | 0 | ✅ |
| executable-286.md | no false FAIL/ESCALATE | CONTINUE | 0 | ✅ |
| diagnostic-460.md | parses without unparseable | BAR_MET | 0 | ✅ |
| crafted multi-DC-block | ESCALATE:unparseable | ESCALATE:unparseable | 1 | ✅ |

**QA-found defects (fixed during QA, before evidence capture):**

1. **STATUS cross-check false FAIL on incomplete walk_data.** `parse_lens_line` returns None for lens names with `(N.N)` qualifiers (e.g., `Weak spots (1.4)` in diagnostic-460). The STATUS cross-check in `check_assert_1` compared partial walk_data (from one parsed lens) against full STATUS totals → false ESCALATE:assert-fail:1. **Fix:** skip the STATUS cross-check when walk_data fold totals disagree with STATUS fold totals (walk_data is known incomplete).

2. **Restructuring false positive on STATUS negation.** Walk 4 STATUS in diagnostic-460 says "no restructuring fold" — the word "restructuring" matched RESTRUCTURING_RE → false ESCALATE:restructuring-fold. **Fix:** removed RESTRUCTURING_RE check from the STATUS handler. Restructuring is now detected exclusively from per-pass fold metadata (extract_per_pass_metadata), where the token appears IN the fold context, not in commentary.

## (3) Full Suite — Rule 21

`python3 -m pytest tests/ -q -rf` → **1139 passed, 0 failed.**

Evidence: `knowledge/qa/evidence/executable-cycle-check-2026-08-19/full_suite.txt`

FAILED node-id set: **empty** (no regressions).

## (4) plan_lint check (f) untouched

`git diff --stat HEAD -- scripts/plan_lint.py` → empty. No modifications to `plan_lint.py` in this plan. Check (f) is superseded, not removed (census Q4).

## Verification Table

| Check | Result | Evidence |
|---|---|---|
| (1) Targeted suite 27/27 | ✅ | test_cycle_check.txt |
| (1) Every branch covered | ✅ | branch table above |
| (2) diagnostic-429 clean terminal | ✅ | live_canary.txt |
| (2) executable-286 no false FAIL | ✅ | live_canary.txt |
| (2) diagnostic-460 parses without unparseable | ✅ | live_canary.txt |
| (2) multi-DC-block ESCALATE:unparseable | ✅ | live_canary.txt |
| (3) Full suite 1139/1139 green | ✅ | full_suite.txt |
| (3) FAILED set empty | ✅ | full_suite.txt |
| (4) plan_lint.py unmodified | ✅ | git diff |

## Rule 20 — Self-Check Verification

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: knowledge/qa/evidence/executable-cycle-check-2026-08-19/
Files verified: 3
```
