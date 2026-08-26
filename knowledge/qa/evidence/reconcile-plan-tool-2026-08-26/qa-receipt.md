# QA Receipt — reconcile-plan-tool-2026-08-26

**Plan:** 566 | **Step:** 2 (QA) | **Date:** 2026-08-26

## Hygiene

**numstat (4 files):**

| File | Added | Removed |
|---|---|---|
| tools/reconcile_plan.py | 144 | 0 |
| tools/issue_verdict.py | 2 | 2 |
| tests/test_reconcile_plan.py | 204 | 0 |
| knowledge/dev-logs/reconcile-plan-tool-dev-2026-08-26.md | 23 | 0 |

**toplevel:** `/Users/marklehn/Developer/GitHub/bellows/.bellows-worktrees/566`

**reflog -n 4:**

```
5fb2ff6 HEAD@{0}: reset: moving to HEAD
5fb2ff6 HEAD@{1}:
```

Amends: 0

## Verification

| Item | Check | Status |
|---|---|---|
| 1 | Full pytest suite: 1517 passed, 0 failed (1511 + 6 = 1517) | ✅ |
| 2a | Closed-plan reconcile on scratch copy: exit 0, look-before-mutate matches read-only query | ✅ |
| 2b | in_progress refusal without --killed-verified: exit 3, refusal text present | ✅ |
| 2c | Byte-unchanged after refusal: plans and verdicts table dumps identical pre/post | ✅ |
| 3 | numstat: 4 files, counts recorded | ✅ |
| 3 | toplevel: worktree root confirmed | ✅ |
| 3 | reflog -n 4: 0 amends | ✅ |

============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: /Users/marklehn/Developer/GitHub/bellows/.bellows-worktrees/566/knowledge/qa/evidence/reconcile-plan-tool-2026-08-26/
Files verified: 3
