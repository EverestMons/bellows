# QA Report — Rule 22(c) Scoping Fix (Plan 532)

**Date:** 2026-08-25
**Plan:** 532 — rule_22(c) scoping — backtick-strip the failure-marker scan, bounded N/A rows
**Step:** 2 (QA)

## Q1 — Full Suite

```
python3 -m pytest tests/ -q
1445 passed, 1 warning in 47.70s
```

- **Collected:** 1445 (X5 plan estimate: 1435 — superseded per plan instruction)
- **Passed:** 1445
- **Failed:** 0
- **Raw output:** `knowledge/qa/evidence/rule22c-parser-fix/pytest_full.txt`

### Targeted rule_22 tests (15 existing + 10 new = 25 total)

```
python3 -m pytest tests/test_gates.py -k "rule_22" -v
25 passed, 144 deselected, 1 warning in 0.24s
```

All 25 rule_22 tests pass — zero regressions in the existing 15, all 10 new tests (A1-A5, B1-B5) green.

## Q2 — Reproduction Proof

The C4 and C5 rows (X6, verbatim from the processed verdicts) fed through `_gate_rule_22_verification` in a scratch harness:

### C4 reproduction (plan 523 row 89 — quoted-❌ in ✅ row)

**Row:** `| 4 | \`❌ worktree teardown failed:\` count == 2 | ✅ |`
**Result:** 0 (c)-class failures — backtick-quoted ❌ correctly stripped before scan.

### C5 reproduction (plan 524 row 75 — status-less G8 info row with N/A)

**Row:** `| G8 | ~/.claude memory entry | N/A |`
**Result:** 0 (c)-class failures — N/A row correctly skipped by `_is_na_status_row`.

### Inverted control 1 — genuine ❌ outside backticks

**Row:** `| verdict.py | ❌ | missing |`
**Result:** 1 (c)-class failure — genuine ❌ fires correctly.
**Evidence:** `(c) QA verification table row 8: | verdict.py | ❌ | missing |`

### Inverted control 2 — genuinely status-less row in mixed table

**Row:** `| info | Planner post-close act — out of scope |`
**Result:** 1 (c)-class failure — genuinely status-less check row fires correctly in a table with ✅ rows.
**Evidence:** `(c) QA verification table row 8 missing status: | info | Planner post-close act — out of scope |`

**Conclusion:** Both C4 and C5 produce zero failures under the new code; both inverted controls still fire. The fix scopes the gate without weakening genuine arms.

## Q3 — Fence

```
$ git diff HEAD~1 --stat
 gates.py            |  21 +++++-
 tests/test_gates.py | 205 ++++++++++++++++++++++++++++++++++++++++++++++++++++
 2 files changed, 225 insertions(+), 1 deletion(-)
```

**Exactly two files** — `gates.py` and `tests/test_gates.py`. No bellows.py, runner.py, depositor.py, or any other module touched.

### Three gates.py hunks

1. **S3/X3 — `NA_STATUS_TOKENS` + `_is_na_status_row`**: New constant and helper beside `_is_positive_status_row`, same bounded-cell-equality discipline (split on `|`, strip, compare case-insensitively against the token set).
2. **S1/X1 — backtick-strip before ❌ scan**: `scan_target = re.sub(r'\`[^\`]+\`', '', stripped)` then `if "❌" in scan_target:` — paired backtick spans stripped; unpaired backticks fail-safe by construction (the regex never completes).
3. **S2/X2 — N/A branch insertion**: `elif _is_na_status_row(line): pass` between the positive-status branch and the defer — the row neither fires, nor counts positive, nor defers.

## Deliverable Verification

| ID | Check | Status |
|---|---|---|
| S1 | Backtick-strip before ❌ scan (X1) | ✅ |
| S2 | N/A branch between positive-status and defer (X2) | ✅ |
| S3 | `NA_STATUS_TOKENS` + `_is_na_status_row` beside `_is_positive_status_row` (X3) | ✅ |
| S4 | 10 new tests A1-A5, B1-B5 — all pass, 15 existing unaffected (X4) | ✅ |
| S5 | Fence: exactly gates.py + tests/test_gates.py changed | ✅ |

## Rule 20 — QA Self-Check

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: knowledge/qa/evidence/rule22c-parser-fix/
Files verified: 2
```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: knowledge/qa/evidence/rule22c-parser-fix/
Files verified: 2
