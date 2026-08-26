# QA Receipt: plan-lint-bare-constants — (r) WARN check

**Plan:** executable-561
**Date:** 2026-08-26
**Step:** 2 (QA)

## Hygiene

**Numstat (3 files, HEAD~1..HEAD):**

| added | removed | file |
|---|---|---|
| 92 | 0 | knowledge/dev-logs/plan-lint-bare-constants-dev-2026-08-26.md |
| 35 | 0 | scripts/plan_lint.py |
| 45 | 0 | tests/test_plan_lint_bare_constants.py |

**Toplevel:** `/Users/marklehn/Developer/GitHub/bellows/.bellows-worktrees/561`

**Reflog -n 4:**

```
bb6ca1d HEAD@{0}: reset: moving to HEAD
bb6ca1d HEAD@{1}: commit
```

Amends: 0.

## Verification

| Item | Check | Status |
|---|---|---|
| 1 | Full test suite: 1488 passed, 0 failed (derivation: 1483 baseline + 5 new = 1488) | ✅ |
| 1 | pytest output saved to `pytest_full.txt` | ✅ |
| 2 | Firing plan (governance/Done/executable-559.md): `(r) WARN: line 23` printed, EXIT_CODE=0 | ✅ |
| 2 | Quiet plan (bellows/Done/executable-560.md): no `(r) WARN` lines, EXIT_CODE=0 | ✅ |
| 2 | Warn-first proven live: both plans exit 0 regardless of (r) WARN firing | ✅ |
| 2 | `(r) WARN` count in plan_lint.py: 2 (>= 1) | ✅ |
| 2 | `def test_` count in test file: 5 (== 5) | ✅ |
| 2 | `cmp` plan_lint.py committed vs live: exit=0 | ✅ |
| 2 | `cmp` test file committed vs live: exit=0 | ✅ |
| 3 | numstat: 3 files, additions only | ✅ |
| 3 | toplevel: worktree 561 | ✅ |
| 3 | reflog -n 4: 0 amends | ✅ |

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: /Users/marklehn/Developer/GitHub/bellows/.bellows-worktrees/561/knowledge/qa/evidence/plan-lint-bare-constants-2026-08-26/
Files verified: 3
```
