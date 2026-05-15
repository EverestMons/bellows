# QA Report — Worktree Teardown Type-Mismatch Fix
**Date:** 2026-05-03
**Plan:** fix-plan-worktree-teardown-type-mismatch-2026-05-03
**Step:** 2 (QA)

## Summary

Verified the four-site type-format fix in `bellows.py` that changed worktree failure entries from plain strings to dict format (`{"gate": ..., "evidence": ...}`), matching the `verdict.py` consumer contract. All four sites confirmed correct, no remnants of the old string format remain, the new regression test exists and passes, and the fix commit landed. Full targeted regression (87 tests across `test_verdict.py` and `test_bellows.py`) passes with zero failures.

## Verification Table

| # | Deliverable | Expected | Status | Evidence |
|---|-------------|----------|--------|----------|
| 1 | Site 1 — `_create_worktree` failure handler uses dict format | Line containing `{"gate": "worktree_creation", "evidence": str(e)}` | ✅ | `evidence/worktree-teardown-type-mismatch-fix-2026-05-03/grep_creation_site.txt` |
| 2 | Sites 2-4 — three `worktree_teardown` sites use dict format | Three lines containing `{"gate": "worktree_teardown", "evidence": str(e)}` | ✅ | `evidence/worktree-teardown-type-mismatch-fix-2026-05-03/grep_teardown_sites.txt` |
| 3 | No remaining old string-format sites | Zero matches for `worktree_teardown_failed` or `worktree_creation_failed` | ✅ | `evidence/worktree-teardown-type-mismatch-fix-2026-05-03/grep_old_format.txt` (empty file = pass) |
| 4 | New regression test exists | One match for `test_post_verdict_request_handles_worktree_teardown_failure_dict_format` in tests/ | ✅ | `evidence/worktree-teardown-type-mismatch-fix-2026-05-03/grep_new_test.txt` |
| 5 | Fix commit landed | Commit `272fbe4` with message starting `fix(bellows): use dict format for worktree failure entries` present in log | ✅ | `evidence/worktree-teardown-type-mismatch-fix-2026-05-03/git_log_head.txt` |
| 6 | Targeted test regression | All 87 tests in test_verdict.py and test_bellows.py pass, including new regression test | ✅ | `evidence/worktree-teardown-type-mismatch-fix-2026-05-03/pytest_targeted.txt` |

## Rule 20 Self-Check Output

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
✅ SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: /Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/evidence/worktree-teardown-type-mismatch-fix-2026-05-03/
Files verified: 6
```

---
## Output Receipt
**Agent:** Bellows QA
**Step:** 2
**Status:** Complete

### What Was Done
Verified all 4 code sites in bellows.py were correctly changed to dict format. Confirmed no remnants of old string format. Verified new regression test exists and passes. Ran full targeted regression (87 tests, 0 failures). Rule 20 self-check passed.

### Files Deposited
- `knowledge/qa/worktree-teardown-type-mismatch-fix-qa-report-2026-05-03.md` — this QA report
- `knowledge/qa/evidence/worktree-teardown-type-mismatch-fix-2026-05-03/` — 6 evidence files

### Files Created or Modified (Code)
- None

### Decisions Made
- Check 5 (commit landed): expanded git log to 3 entries since Step 1 produced 3 sequential commits; fix commit `272fbe4` confirmed present

### Flags for CEO
- None

### Flags for Next Step
- None
