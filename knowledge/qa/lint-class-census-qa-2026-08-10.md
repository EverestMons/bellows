# QA Report — lint-class-census-2026-08-10

**Diagnostic:** 336
**Slug:** `lint-class-census-2026-08-10`
**QA date:** 2026-08-10

---

## Deliverable Verification

| # | Item | Expected | Status | Evidence |
|---|------|----------|--------|----------|
| 1 | Nothing installed | `git status --porcelain -- scripts/ tests/` empty; diff touches only declared deposits | PASS | scripts/tests clean; diff lists only `knowledge/development/`, `knowledge/qa/evidence/`, `knowledge/research/` |
| 2 | Populations never blended | Every number names its population (final states vs. pre-fold states) | PASS | Findings doc separates Q1/Q3 (final states, from `final-state-matches.txt`) from Q2/Q4 (pre-fold states, from `pre-fold-matches.txt`). No single figure spans both. |
| 3 | Q3 is a list | 5 classified matches spot-checked by opening plan at named line | PASS | (1) m executable-330.md:209 — grep -cF probe in verification prose, em-dash in surrounding text; FALSE/R2 confirmed. (2) q executable-330.md:211 — grep -cF version probe; metachar in other quoted strings; FALSE/R2 confirmed. (3) q executable-321.md:49 — `grep -n -F "AND status != 'retired'"`, `!` in -F pattern but `!=` is not bash history; AMBIGUOUS/R4 confirmed. (4) s executable-project-docs-reset:34 — "three files" correctly counts the list; FALSE/R5 confirmed. (5) r diagnostic-flavornotes...:33 — `|` on line is a markdown pipe/prose structure, not a shell pipe; FALSE/R2 confirmed. |
| 4 | Uncovered set named | Q2/Q4 list plans they could not cover | PASS | Findings doc names uncovered set: brewbuddy-shop-import-census (no close commit, still in draft). |
| 5 | Case against present | Every SHIP recommendation carries counter-argument | PASS | No SHIP recommendations made. All four classes received REDESIGN (m, q, r) or HOLD (s). Each disposition includes a "Case against shipping" section. |
| 6 | Raw output | Every count is command stdout | PASS | Match counts from `census-matchers.py` stdout; pre-fold counts from `pre-fold-scan.py` stdout; corpus counts from `find | wc -l`; commit counts from `git log --oneline | wc -l`. All pasted from command output in dev logs. |

---

## Rule 20 — QA Self-Check Results

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: /Users/marklehn/Developer/GitHub/bellows/.bellows-worktrees/336/knowledge/qa/evidence/lint-class-census-2026-08-10/
Files verified: 3
```

---

## Deposit Inventory

| Deposit | Path | Present | Non-empty |
|---------|------|---------|-----------|
| Classification rubric | `knowledge/qa/evidence/lint-class-census-2026-08-10/classification-rubric.md` | Yes | Yes |
| Final-state matches | `knowledge/qa/evidence/lint-class-census-2026-08-10/final-state-matches.txt` | Yes | Yes |
| Pre-fold matches | `knowledge/qa/evidence/lint-class-census-2026-08-10/pre-fold-matches.txt` | Yes | Yes |
| Findings | `knowledge/research/lint-class-census-findings-2026-08-10.md` | Yes | Yes |
| Dev log step 1 | `knowledge/development/lint-class-census-dev-log-step-1-2026-08-10.md` | Yes | Yes |
| Dev log step 2 | `knowledge/development/lint-class-census-dev-log-step-2-2026-08-10.md` | Yes | Yes |
| QA report | `knowledge/qa/lint-class-census-qa-2026-08-10.md` | Yes | Yes |
| Dev log step 3 | `knowledge/development/lint-class-census-dev-log-step-3-2026-08-10.md` | Yes | Yes |
