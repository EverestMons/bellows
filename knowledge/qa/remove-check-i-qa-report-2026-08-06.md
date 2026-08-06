# QA Report — remove plan_lint check (i) (Plan 304, Step 2)

**Date:** 2026-08-06
**Plan:** 304

## Task Q0 — State Re-Pin

**Step 1 commit verified:**
```
$ git -C /Users/marklehn/Developer/GitHub/bellows log -1 --oneline -- scripts/plan_lint.py tests/test_plan_lint.py
8e085fa [304] fix: remove plan_lint check (i) — halt-routing plan-id coverage
```
Most recent commit touching either file is Step 1's `8e085fa`. No foreign commit intervened.

**Corpus HEAD pins:**
| Root | HEAD |
|------|------|
| anvil | `da17272ee00c82f987052953660940d18b59c1e0` |
| bellows | `8e085fab97723c9ff83f72d22a12315aa3c95a94` |
| governance | `c95a3d9d2556e88f848dfe3f01d9c76cbf166572` |
| invoice-pulse | `f83c244d914cccbac1d14447054fa7a456a77236` |
| lessons-forge | `b9fd5f152b35e13bae941cb9198924b7de154535` |

## Verification Table

| Row | Claim | Status | Evidence |
|-----|-------|--------|----------|
| 1 | Full bellows test suite passes | verified | `846 passed, 1 warning in 21.80s` — raw output in `knowledge/qa/full-suite.txt`. Predicted: 846 (851 − 5). Actual: 846. |
| 2 | Sweep diff consists of EXACTLY (i) warning lines | verified | `diff sweep-before.txt sweep-after.txt` produces: (a) bellows header HEAD change `716f6ab` → `8e085fa` (expected, Step 1 committed), (b) 11 removed `(i)` warning lines across 3 governance plans (`diagnostic-276`, `diagnostic-299`, `diagnostic-301`). No `(g)` or `(h)` lines affected. Raw diff in `knowledge/qa/sweep-diff.txt`. |
| 3 | (g) true positive survives | verified | `diagnostic-299.md` still reports `WARN: Drafting Cycle ledger out of order: C15 before C13` in the AFTER sweep. Raw: `grep -F 'diagnostic-299' sweep-after.txt` shows the warning present. |
| 4a | WARN-only — mechanism grep | verified | Programmatic check: `(g): results.append=False, all_passed=assignment=False; (h): results.append=False, all_passed=assignment=False`. The word "results" appears in (h)'s print string `"...but lens results are recorded"` — a string literal, not a variable reference. |
| 4b | WARN-only — exit code on tripping plan | verified | `python3 scripts/plan_lint.py governance/Done/diagnostic-299.md` fires (g) WARN, exit code = 0. Raw output: `WARN: Drafting Cycle closing indicates fold as last event, not a dry lens pass (DRAFTING_CYCLE.md §2)` / `WARN: Drafting Cycle ledger out of order: C15 before C13` / `PASS: (a) header — parsed` / `PASS: (a) dispatch_mode — bellows` / `PASS: (a) pause_for_verdict — always` / exit=0. |
| 5 | Rule 20 self-check passes | verified | See Rule 20 Self-Check section below. |

## Sweep Diff (raw)

```
133c133
< === bellows (434 plans, HEAD=716f6ab) ===
---
> === bellows (434 plans, HEAD=8e085fa) ===
1153,1154d1152
< diagnostic-276.md:
< WARN: no halt-routing line found
1162d1159
< WARN: no halt-routing line found
1165d1161
< WARN: no halt-routing line found
1169,1176d1164
< WARN: plan id `273` in questions region but absent from halt-routing
< WARN: plan id `274` in questions region but absent from halt-routing
< WARN: plan id `279` in questions region but absent from halt-routing
< WARN: plan id `280` in questions region but absent from halt-routing
< WARN: plan id `281` in questions region but absent from halt-routing
< WARN: plan id `283` in questions region but absent from halt-routing
< WARN: plan id `284` in questions region but absent from halt-routing
< WARN: plan id `289` in questions region but absent from halt-routing
```

Every removed line is an `(i)` warning (`halt-routing` / `plan id ... absent from halt-routing`). The bellows header HEAD change (`716f6ab` → `8e085fa`) is cosmetic — Step 1's commit moved bellows HEAD. No `(g)` or `(h)` lines were gained or lost.

## Rule 20 Self-Check

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: /Users/marklehn/Developer/GitHub/bellows/knowledge/qa/
Files verified: 3
```

## Evidence Files

- `knowledge/qa/full-suite.txt` — 846 passed, 1 warning
- `knowledge/qa/sweep-after.txt` — corpus sweep post-removal, 1362 plans across five roots
- `knowledge/qa/sweep-diff.txt` — diff showing only (i) warning lines removed

### Ledger Updates

#### Prompt Feedback
