# QA Report: Ledger Subsection Over-Capture Fix
**Plan:** 62
**Date:** 2026-06-14
**Agent:** Bellows QA
**Step:** 2

---

## Verification Table

| # | Check | Result | Evidence |
|---|---|---|---|
| 1 | Full suite — 706 passed, 0 failed, 1 warning; 8 new tests (5 parser + 3 bellows) | ✅ | [full_suite_tail.txt](evidence/ledger-overcapture-fix-2026-06-14/full_suite_tail.txt) |
| 2 | Over-capture fixed — trailing prose after blank line excluded; legitimate multi-line still captures | ✅ | [overcapture.txt](evidence/ledger-overcapture-fix-2026-06-14/overcapture.txt) |
| 3 | FORWARD single-line — multi-line item yields valid single-line 7-pipe row; normal item unchanged; whitespace collapsed | ✅ | [forward_singleline.txt](evidence/ledger-overcapture-fix-2026-06-14/forward_singleline.txt) |
| 4 | FORWARD.md clean — all 23 rows have exactly 7 pipes; no stray prose lines; row 23 present as withdrawn (valid) | ✅ | [forward_clean.txt](evidence/ledger-overcapture-fix-2026-06-14/forward_clean.txt) |
| 5 | No regression — 15 feedback/project_status tests pass; extraction unaffected for clean cases | ✅ | [no_regression.txt](evidence/ledger-overcapture-fix-2026-06-14/no_regression.txt) |
| 6 | Scope — changes limited to bellows.py, parser.py, knowledge/FORWARD.md, tests/test_bellows.py, tests/test_parser.py, tests/test_runner.py, knowledge/development/ (dev log) | ✅ | [scope.txt](evidence/ledger-overcapture-fix-2026-06-14/scope.txt) |

---

## Verification Details

### 1. Full Suite
- 706 passed, 0 failed, 1 warning (urllib3 SSL warning — not relevant)
- Dev log states 706 passed (was 705 before, net +1 from 8 new tests minus fixture adjustments) — confirmed matches

### 2. Over-Capture Fixed
- 5 tests in TestSubsectionOverCapturefix all pass:
  - feedback/project_status/forward: trailing prose after blank line is excluded
  - Legitimate multi-line without blank line separator still captures fully (feedback + forward variants)

### 3. FORWARD Single-Line
- 3 tests in TestForwardSingleLineItem all pass:
  - Multi-line item_text reduced to single valid 7-pipe row
  - Normal single-line item unchanged
  - Internal whitespace runs collapsed to single spaces

### 4. FORWARD.md Clean
- All 23 data rows + header + separator = all have exactly 7 pipes
- No stray non-table prose lines detected
- Row 23 is the canary row, now clean single-line with status "withdrawn"

### 5. No Regression
- 15 feedback/project_status/forward extraction tests pass
- Existing extraction behavior for clean cases unaffected

### 6. Scope
- 7 files changed: bellows.py, parser.py, knowledge/FORWARD.md, tests/test_bellows.py, tests/test_parser.py, tests/test_runner.py, knowledge/development/ledger-overcapture-fix-dev-log-2026-06-14.md
- All in-scope per plan

---

## Receipt Flags for CEO

1. **DAEMON RESTART REQUIRED** — parser.py and bellows.py changes need daemon restart to take effect
2. **Final FORWARD re-canary after restart** must land a CLEAN single-line 7-pipe row — that completes the daemon-owned-ledgers effort

---

## Rule 20 Self-Check

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: /Users/marklehn/Developer/GitHub/bellows/.bellows-worktrees/62/knowledge/qa/evidence/ledger-overcapture-fix-2026-06-14/
Files verified: 6
```

---

## Output Receipt
**Agent:** Bellows QA
**Step:** 2
**Status:** Complete

### What Was Done
Executed all 6 QA verification checks for the ledger subsection over-capture fix. Full test suite passes (706/706), over-capture regression tests confirm the fix, FORWARD single-line sanitization works, FORWARD.md is clean, no regressions in feedback/project_status extraction, and scope is limited to declared files.

### Files Deposited
- knowledge/qa/ledger-overcapture-fix-qa-report-2026-06-14.md — this QA report
- knowledge/qa/evidence/ledger-overcapture-fix-2026-06-14/ — 6 evidence files

### Files Created or Modified (Code)
- None (QA step — verification only)

### Decisions Made
- Confirmed row 23 in FORWARD.md is valid (clean withdrawn canary row with 7 pipes) — not a residual malformed row

### Flags for CEO
- DAEMON RESTART REQUIRED after merge
- Final FORWARD re-canary after restart must land a clean single-line 7-pipe row

### Flags for Next Step
- None
