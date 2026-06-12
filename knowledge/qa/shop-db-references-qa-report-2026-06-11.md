# Shop-Level Lifecycle DB References — QA Report
**Plan:** Shop-Level Lifecycle DB References + Id-Native Naming Sync
**Date:** 2026-06-11
**Step:** 2 (QA)

---

## Verification Table

| # | Item | Method | Evidence File | Result |
|---|------|--------|---------------|--------|
| 1 | E1 — plan-side template sync | grep for new text present + old text absent | edits_landed.txt | PASS |
| 2 | E2 — COMPANY.md decisions naming | grep for new text present + old text absent | edits_landed.txt | PASS |
| 3 | E3 — COMPANY.md lifecycle system of record | grep for new paragraph present | edits_landed.txt | PASS |
| 4 | E4 — SPECIALIST_TEMPLATE.md execution context | grep for new paragraph present | edits_landed.txt | PASS |
| 5 | E5 — Verdicts README id-native filename | grep for new text present + old text absent + legacy tolerance | edits_landed.txt | PASS |
| 6 | E6 — Version bump + changelog | grep for version 4.62 + changelog row | edits_landed.txt | PASS |
| 7 | Stale-placeholder sweep | grep -rn plan-filename-without-md across 4 files | stale_placeholder.txt | PASS |
| 8 | COMPANY.md date-naming scan | grep -n YYYY-MM-DD with classification | company_dates_scan.txt | PASS |
| 9 | Verdicts README integrity | git diff HEAD~2 HEAD~1 + verdict: regex check | verdicts_readme_diff.txt | PASS |
| 10 | Version integrity | Version 4.62 exactly once + changelog row present | version_check.txt | PASS |
| 11 | Cross-reference validity | grep for headings + file existence check | crossref_check.txt | PASS |

---

## Evidence Summary

### (1) Edit Landing — E1 through E6
All six edits verified via grep. New text present at expected lines; old/replaced text absent where applicable. Full grep output in `edits_landed.txt`.

### (2) Stale-Placeholder Sweep
`grep -rn "plan-filename-without-md"` across PLANNER_TEMPLATE.md, RULE_20_SELF_CHECK_BLOCK.md, COMPANY.md, and SPECIALIST_TEMPLATE.md returned ZERO HITS.

### (3) COMPANY.md Date-Naming Scan
5 hits for YYYY-MM-DD, all classified as permitted: general knowledge-artifact naming (L148), roadmap naming within id-native paragraph (L152), flag-file naming (L229), header Date-field templates (L236, L252). No hits prescribe date-bearing deposit filenames for executable/diagnostic/qa plans.

### (4) Verdicts README Integrity
Diff of HEAD~2 vs HEAD~1 shows exactly two changed lines (E5a: verdict filename template, E5b: slug definition). The `verdict:` line-1 format regex (`^verdict:\s*(continue|stop)$`) is byte-identical between old and new versions.

### (5) Version Integrity
`**Version:** 4.62` appears exactly once (L5). Old `**Version:** 4.61` has zero hits. The v4.62 changelog row is present at L1754.

### (6) Cross-Reference Validity
- "Id-Native Naming" heading found at L410 in PLANNER_TEMPLATE.md
- "Lifecycle DB Read Protocol (Planner)" heading found at L974 in PLANNER_TEMPLATE.md
- `roadmap-reporting-vs-backlog-2026-06-09.md` exists on disk at governance root

---

## Rule 20 — QA Self-Check

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: /Users/marklehn/Developer/GitHub/bellows/.bellows-worktrees/5/knowledge/qa/evidence/shop-db-references-2026-06-11/
Files verified: 6
```
