# QA Report — Rule 20 Single-Source Migration

**Plan:** executable-rule-20-single-source-2026-05-10
**Agent:** Bellows QA
**Date:** 2026-05-10
**Step:** 2

---

## Verification Matrix

| # | Property | Expected | Actual | Status |
|---|----------|----------|--------|--------|
| 1 | `RULE_20_SELF_CHECK_BLOCK.md` exists at governance root | `True` | `True` | ✅ |
| 2 | Canonical banner survives migration byte-exact | `grep -c` ≥ 1 | `4` (banner appears in print statement, prose, and history) | ✅ |
| 3 | PASSED line survives migration byte-exact | `grep -c` ≥ 1 | `3` (appears in code block, prose, and history) | ✅ |
| 4 | PLANNER_TEMPLATE Rule 20 no longer inlines the Python block | `grep -c "^import os, sys$"` = 0 | `0` | ✅ |
| 5 | PLANNER_TEMPLATE Rule 20 references the canonical file | `grep -c "RULE_20_SELF_CHECK_BLOCK.md"` ≥ 1 | `4` | ✅ |
| 6 | PLANNER_TEMPLATE version bumped | `4.36` | `**Version:** 4.36` | ✅ |
| 7 | BELLOWS_QA.md has new Rule 20 reference section | `grep -c` = 1 | `1` | ✅ |
| 8 | BELLOWS_QA.md does NOT inline the Python block | `grep -c "^import os, sys$"` = 0 | `0` | ✅ |
| 9 | INVOICE_SECURITY_TESTING_ANALYST.md has new Rule 20 reference section | `grep -c` = 1 | `1` | ✅ |
| 10 | INVOICE_SECURITY_TESTING_ANALYST.md does NOT inline the Python block | `grep -c "^import os, sys$"` = 0 | `0` | ✅ |
| 11 | Single-source invariant: canonical block published in exactly one file | Active publication (`import os, sys` standalone line) only in `RULE_20_SELF_CHECK_BLOCK.md` | Confirmed. Banner string appears in 140+ files (historical QA reports, verdicts, research, plan files) as prose references — but the actual Python block (active publication) exists only in `RULE_20_SELF_CHECK_BLOCK.md`. PLANNER_TEMPLATE.md, BELLOWS_QA.md, and ISTA.md all return 0 for `^import os, sys$`. | ✅ |
| 12 | Bellows test suite unchanged | 246 passed, 1 pre-existing failure | `1 failed, 246 passed, 1 warning in 5.97s` — pre-existing `test_run_step_timeout` only | ✅ |
| 13 | Three commits exist | All dated 2026-05-10 | Gov root: `a109e47` feat(governance), Bellows: `b05dc42` docs(qa), Invoice-pulse: `02702201` docs(qa) | ✅ |
| 14 | LESSONS entry added to PLANNER_TEMPLATE | `grep` ≥ 1 match | Found: `2026-05-10 | Rule 20 single-source migration: the canonical Python block migrated...` | ✅ |

Migration verified — 14/14 checks passed.

---

## Evidence Files

| File | Location |
|------|----------|
| `canonical-banner-grep.txt` | `bellows/knowledge/qa/evidence/rule-20-single-source-2026-05-10/` |
| `inline-block-search.txt` | `bellows/knowledge/qa/evidence/rule-20-single-source-2026-05-10/` |
| `test-suite-result.txt` | `bellows/knowledge/qa/evidence/rule-20-single-source-2026-05-10/` |

---

## Rule 20 Self-Check (canonical block from RULE_20_SELF_CHECK_BLOCK.md)

Block sourced from `/Users/marklehn/Desktop/GitHub/RULE_20_SELF_CHECK_BLOCK.md` § Canonical Python Block. Four placeholders filled from plan prompt. No other lines modified.

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: /Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/evidence/rule-20-single-source-2026-05-10/
Files verified: 3
```

---

## Output Receipt
**Agent:** Bellows QA
**Step:** 2
**Status:** Complete

### What Was Done
Executed 14-point verification matrix for the Rule 20 single-source migration. All checks passed: canonical file exists with byte-exact banner, PLANNER_TEMPLATE no longer inlines the block, both QA agent files reference the canonical file without inlining, test suite unchanged (246 passed, 1 pre-existing failure), all three commits present and dated 2026-05-10, LESSONS entry added. Ran the Rule 20 self-check using the new single-source pattern (first plan to do so) — PASSED.

### Files Deposited
- `bellows/knowledge/qa/rule-20-single-source-qa-2026-05-10.md` — QA report (this file)
- `bellows/knowledge/qa/evidence/rule-20-single-source-2026-05-10/canonical-banner-grep.txt` — grep output for banner invariant
- `bellows/knowledge/qa/evidence/rule-20-single-source-2026-05-10/inline-block-search.txt` — grep output confirming no inline blocks
- `bellows/knowledge/qa/evidence/rule-20-single-source-2026-05-10/test-suite-result.txt` — pytest tail output

### Files Created or Modified (Code)
- None (QA step — no code changes)

### Decisions Made
- Ran full test suite without `-x` to get accurate pass count (214 with `-x` due to early abort vs. 246 without)
- Classified banner appearances in 140+ historical files as prose references (not active publication) for check 11

### Flags for CEO
- None

### Flags for Next Step
- None — all 14 checks passed, self-check PASSED, migration structurally verified
