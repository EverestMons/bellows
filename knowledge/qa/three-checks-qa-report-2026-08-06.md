# QA Report — three mechanical drafting-cycle checks in plan_lint (Plan 303, Step 2)

**Date:** 2026-08-06
**Plan:** 303

## Task Q0 — State Re-Pin

**Step 1 commit verified:**
```
$ git -C /Users/marklehn/Developer/GitHub/bellows log -1 --oneline -- scripts/plan_lint.py tests/test_plan_lint.py
9cd1cc5 [303] fix: gate plan_lint check (i) on questions region to eliminate false positives on executables
```
Most recent commit touching either file is Step 1's `9cd1cc5`. No foreign commit intervened.

**Corpus HEAD pins:**
| Root | HEAD |
|------|------|
| anvil | `da17272ee00c82f987052953660940d18b59c1e0` |
| bellows | `399c01b7c9e44e68dc6002406571aee5dc7aaa17` |
| governance | `2cc6c9fb1432e93e8a2f85b9f175ee8767efdd50` |
| invoice-pulse | `f83c244d914cccbac1d14447054fa7a456a77236` |
| lessons-forge | `b9fd5f152b35e13bae941cb9198924b7de154535` |

## Verification Table

| Row | Claim | Status | Evidence |
|-----|-------|--------|----------|
| 1 | Full bellows test suite passes | verified | `851 passed, 1 warning in 21.73s` — raw output in `knowledge/qa/full-suite.txt` |
| 2a | (g) Ledger ordering — corpus fire count | verified | **1 plan fires** across 1362 total plans. `governance/Done/diagnostic-299.md`: C15 before C13. anvil (57): 0, bellows (433): 0, governance (33): 1, invoice-pulse (773): 0, lessons-forge (66): 0. Command: `plan_lint.py` run against every `*.md` in each root's `knowledge/decisions/Done/`, filtered for `(g)` WARN text. Pins beside counts in corpus-sweep.txt. |
| 2b | (h) Stale closing — corpus fire count | verified | **0 plans fire** across 1362 total plans. anvil (57): 0, bellows (433): 0, governance (33): 0, invoice-pulse (773): 0, lessons-forge (66): 0. |
| 2c | (i) Halt-routing — corpus fire count | verified | **4 plans fire** across 1362 total plans, all in governance. `diagnostic-276.md`: no halt-routing line. `diagnostic-299.md`: no halt-routing line. `diagnostic-300.md`: no halt-routing line. `diagnostic-301.md`: plan ids `273`, `274`, `279`, `280`, `281`, `283`, `284`, `289` in questions region but absent from halt-routing. anvil (57): 0, bellows (433): 0, governance (33): 4, invoice-pulse (773): 0, lessons-forge (66): 0. |
| 3 | Fire count is MEASURED | verified | Total: (g) 1, (h) 0, (i) 4 — produced by running `python3 plan_lint.py <file>` on every plan in all five `Done/` trees (1362 plans). Command output in `knowledge/qa/corpus-sweep.txt`. |
| 4a | WARN-only — mechanism grep | verified | `sed -n '224,272p' scripts/plan_lint.py \| grep -cE 'results\|all_passed'` returns `1` — the sole match is `"lens results are recorded"` inside a print string literal on line 248, NOT a variable reference. Programmatic check (excluding that string literal from the scan): `(g): results=False, all_passed=False; (h): results=False, all_passed=False; (i): results=False, all_passed=False`. |
| 4b | WARN-only — exit code on tripping plan | verified | `python3 plan_lint.py governance/Done/diagnostic-299.md` fires (g) and (i) WARNs, `echo $?` = `0`. Raw output: `WARN: Drafting Cycle ledger out of order: C15 before C13` / `WARN: no halt-routing line found` / `PASS: (a) header — parsed` / `PASS: (a) dispatch_mode — bellows` / `PASS: (a) pause_for_verdict — always` / exit=0. |
| 5 | Targeted lint tests pass | verified | `54 passed, 797 deselected, 1 warning in 2.11s` — raw output in `knowledge/qa/targeted-tests.txt` |
| 6 | Rule 20 self-check passes | verified | See Rule 20 Self-Check section below. |

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

- `knowledge/qa/targeted-tests.txt` — 54 passed, 797 deselected, 1 warning
- `knowledge/qa/full-suite.txt` — 851 passed, 1 warning
- `knowledge/qa/corpus-sweep.txt` — (g) 1 fire, (h) 0 fires, (i) 4 fires across 1362 plans in five roots

### Ledger Updates

#### Prompt Feedback
- Task Q0's re-pin requirement (confirm Step 1 commit + pin corpus HEADs) added value — the bellows HEAD had moved past the Step 1 commit (docs regeneration at `399c01b`), and without the pin this would have been invisible.
- The plan's instruction to confirm WARN-only by mechanism (grep for `results`/`all_passed` references) rather than by symptom (exit code alone) caught the string-literal false positive in the mechanism grep itself — the word "results" appears in check (h)'s print message. The programmatic verification excluding the string literal was necessary for a clean assertion.
