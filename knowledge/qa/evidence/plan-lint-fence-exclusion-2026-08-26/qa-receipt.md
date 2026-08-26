# QA Receipt: plan-lint-fence-exclusion — 2026-08-26

**Plan:** executable-565 | **Step:** 2 (QA) | **Commit:** a3d9781

## Item 1 — Full Suite

```
python3 -m pytest tests/ --tb=short -q
1511 passed, 0 failed, 1 warning (49.73s)
```

Derivation: 1509 (baseline at 564 QA) + 2 (new fence tests) = 1511.

## Item 2 — 563 Replay

**2a — 563 draft blob (fenced constants, should NOT fire):**
Blob `155110df5d23a61ce4ebe95ffbac25f557561b89` at commit `68b5288`.
Result: `candidates=6 excluded=5 fired=0`. The `if code == 0:` on line 74 (inside fence markers lines 33–125) is excluded.

**2b — Scratch plan (bare prose constants, should fire):**
Result: `(r) WARN` fires on lines 6 and 7. Teeth intact.

**2c — cmp extraction vs live:** identical (exit 0).

## Item 3 — Hygiene

**numstat (3 files):**

| file | + | - |
|---|---|---|
| knowledge/dev-logs/plan-lint-fence-exclusion-dev-2026-08-26.md | 44 | 0 |
| scripts/plan_lint.py | 11 | 2 |
| tests/test_plan_lint_bare_constants.py | 29 | 0 |

**Toplevel:** `/Users/marklehn/Developer/GitHub/bellows/.bellows-worktrees/565`

**Reflog -n 4:**
```
a3d9781 HEAD@{0}: reset: moving to HEAD
a3d9781 HEAD@{1}:
```
0 amends.

## Verification

| Item | Check | Status |
|---|---|---|
| 1 | Full suite 1511 passed, 0 failed | ✅ |
| 2a | 563 draft: (r) fired=0 (fenced constants excluded) | ✅ |
| 2b | Scratch plan: (r) WARN fires on bare prose constants | ✅ |
| 2c | cmp extraction vs live: identical | ✅ |
| 3a | numstat: 3 files changed | ✅ |
| 3b | toplevel: worktree confirmed | ✅ |
| 3c | reflog: 0 amends | ✅ |

============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: knowledge/qa/evidence/plan-lint-fence-exclusion-2026-08-26/
Files verified: 3
