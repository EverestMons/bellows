# QA Report — Rule 20 Bold Tolerance

**Date:** 2026-05-17
**Plan:** executable-rule-20-bold-tolerance-qa-recovery-2026-05-17
**Agent:** Bellows QA
**DEV Commit:** f130573 (follow-up to 5ebc2df)

---

## Verification Table

| # | Check | Expected | Actual | Status |
|---|-------|----------|--------|--------|
| 1 | Regex extension at gates.py:374 contains `\*{0,2}` | `^\s*\*{0,2}\s*PASSED\s+—\s+SELF-CHECK\s+PASSED` | Confirmed at line 374 | ✅ |
| 2 | New tests pass (`test_rule_20_gate_tolerates_bold_passed_line`, `test_rule_20_gate_tolerates_single_asterisk_passed_line`) | 2 passed | 2 passed | ✅ |
| 3 | Full gate test suite regression | 91 passed | 91 passed, 1 warning | ✅ |
| 4 | Commit f130573 present in main history | SHA in git log | Confirmed in log output | ✅ |
| 5 | Reverse repro: old regex fails on bold, new regex succeeds | Old=False, New=True for `**PASSED...` | Verified via re.search with MULTILINE | ✅ |

---

## Evidence Files

All evidence captured in `knowledge/qa/evidence/executable-rule-20-bold-tolerance-qa-recovery-2026-05-17/`:

- `grep_regex.txt` — grep output showing line 374 regex
- `pytest_new_tests.txt` — 2 new tests passed
- `pytest_gates.txt` — 91 gate tests passed
- `git_log.txt` — commit f130573 confirmed in history
- `bug_repro_verified.txt` — reverse repro confirming old regex fails, new succeeds

---

## Rule 20 Self-Check

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: /Users/marklehn/Developer/GitHub/bellows/.bellows-worktrees/rule-20-bold-tolerance-qa-recovery-2026-05-17/knowledge/qa/evidence/executable-rule-20-bold-tolerance-qa-recovery-2026-05-17/
Files verified: 5
```

---

## Output Receipt
**Agent:** Bellows QA
**Step:** 1 (QA)
**Status:** Complete

### What Was Done
Verified the Rule 20 bold-tolerance fix (commit f130573) against all 5 DEV log claims. Regex extension confirmed at gates.py:374, both new tests pass, full 91-test gate suite passes with no regressions, commit is in main history, and reverse repro confirms the bug is fixed.

### Files Deposited
- `knowledge/qa/2026-05-17-rule-20-bold-tolerance-qa.md` — this QA report
- `knowledge/qa/evidence/executable-rule-20-bold-tolerance-qa-recovery-2026-05-17/grep_regex.txt` — grep evidence
- `knowledge/qa/evidence/executable-rule-20-bold-tolerance-qa-recovery-2026-05-17/pytest_new_tests.txt` — new test evidence
- `knowledge/qa/evidence/executable-rule-20-bold-tolerance-qa-recovery-2026-05-17/pytest_gates.txt` — full suite evidence
- `knowledge/qa/evidence/executable-rule-20-bold-tolerance-qa-recovery-2026-05-17/git_log.txt` — git log evidence
- `knowledge/qa/evidence/executable-rule-20-bold-tolerance-qa-recovery-2026-05-17/bug_repro_verified.txt` — reverse repro evidence

### Files Created or Modified (Code)
- None

### Decisions Made
- Used commit f130573 as anchor SHA (the more recent of the two fix commits; DEV log references 5ebc2df which is the initial commit, f130573 is the follow-up)

### Flags for CEO
- None

### Flags for Next Step
- None
