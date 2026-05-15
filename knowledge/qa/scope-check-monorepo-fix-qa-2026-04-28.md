# QA Report — scope_check Monorepo Fix (BACKLOG #4)
**Date:** 2026-04-28 | **Plan:** executable-scope-check-monorepo-fix-2026-04-28 | **Step:** 2

---

## Deliverable Verification (Rule 17)

| Deliverable | Expected | Status | Evidence |
|---|---|---|---|
| `_capture_git_diff` argv includes `--relative -- .` | argv line contains `"--relative", "--", "."` | PASS | `knowledge/qa/evidence/executable-scope-check-monorepo-fix-2026-04-28/grep_capture_git_diff.txt` |
| New test `test_capture_git_diff_uses_relative_pathspec` exists | One match in `tests/test_bellows.py` | PASS | `knowledge/qa/evidence/executable-scope-check-monorepo-fix-2026-04-28/grep_new_test.txt` |
| Step 1 commit landed | `fix(scope_check):` commit in git log | PASS | `knowledge/qa/evidence/executable-scope-check-monorepo-fix-2026-04-28/git_log.txt` |

All three deliverables verified.

---

## Targeted Test Results

Ran `python3 -m pytest tests/test_bellows.py -v --tb=short`. Exit code: 0. All 65 tests passed, including the new `test_capture_git_diff_uses_relative_pathspec`. The passed count (65) matches the dev log's count exactly. The only warning is the pre-existing LibreSSL/urllib3 notice, unrelated to this change. No regressions detected.

Full output: `knowledge/qa/evidence/executable-scope-check-monorepo-fix-2026-04-28/pytest_targeted.txt`

---

## Rule 20 Self-Check

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: bellows/knowledge/qa/evidence/executable-scope-check-monorepo-fix-2026-04-28/
Files verified: 4
```

---

## Output Receipt
**Agent:** Bellows QA
**Step:** 2
**Status:** Complete

### What Was Done
Verified all three Step 1 deliverables (code change, new test, commit) via grep and git log evidence. Ran the targeted test suite — 65/65 passed including the new test. Ran Rule 20 self-check. Updated PROJECT_STATUS.md with BACKLOG #4 closure milestone.

### Files Deposited
- `bellows/knowledge/qa/scope-check-monorepo-fix-qa-2026-04-28.md` — this QA report
- `bellows/knowledge/qa/evidence/executable-scope-check-monorepo-fix-2026-04-28/grep_capture_git_diff.txt` — argv verification
- `bellows/knowledge/qa/evidence/executable-scope-check-monorepo-fix-2026-04-28/grep_new_test.txt` — new test verification
- `bellows/knowledge/qa/evidence/executable-scope-check-monorepo-fix-2026-04-28/git_log.txt` — commit verification
- `bellows/knowledge/qa/evidence/executable-scope-check-monorepo-fix-2026-04-28/pytest_targeted.txt` — full pytest output

### Files Created or Modified (Code)
- None (QA step — verification only)

### Decisions Made
- All deliverables verified mechanically via grep/git evidence — no judgment calls required

### Flags for CEO
- REMINDER: restart Bellows to load the fix. Per BACKLOG #14, Bellows daemon gate evaluation runs against OLD code until restart.

### Flags for Next Step
- None — plan is terminal after Planner Rule 22 verification
