# QA Receipt — diff-stat-rename-normalize (plan 567)

**Date:** 2026-08-26
**Commit:** eecc6a2 `[567] diff-stat-rename-normalize(diff-stat-rename-normalize-2026-08-26): renames normalized to the new path at the parser — scope_check + audit fed clean`

## Hygiene

**numstat (3 files):**

| file | + | - |
|---|---|---|
| bellows.py | 13 | 0 |
| knowledge/dev-logs/diff-stat-rename-normalize-dev-2026-08-26.md | 35 | 0 |
| tests/test_diff_stat_renames.py | 143 | 0 |

**toplevel:** `/Users/marklehn/Developer/GitHub/bellows/.bellows-worktrees/567`

**reflog -n 4 (0 amends):**
```
eecc6a2 HEAD@{0}: reset: moving to HEAD
eecc6a2 HEAD@{1}:
```

## Daemon-staleness caveat

bellows.py is live daemon code. The rename normalization fix arms at the next daemon restart — until then, the manifest-pin remains the move guard.

## Verification

| Item | Check | Status |
|---|---|---|
| Item 1 — full suite | `python3 -m pytest tests/ --tb=short -q` — 1522 passed, 0 failed (1517 baseline + 5 new) | ✅ |
| Item 2 — live-repo replay (cross-dir + bare) | scratch repo, real `git mv`, committed parser: returned `['c/f.md', 'normal.py', 'renamed-top.md']` — zero ` => `, zero `{` | ✅ |
| Item 2 — live-repo replay (lstrip guard) | `git mv f.md sub/f.md` → `['sub/f.md']` — no braces | ✅ |
| Item 2 — probe: "rename rendering" | count=1 in bellows.py | ✅ |
| Item 2 — probe: regex pattern | `{[^{}]* => ` count=1 in bellows.py | ✅ |
| Item 2 — probe: import re | count=1 in bellows.py | ✅ |
| Item 2 — cmp: git show vs live bellows.py | identical (exit 0) | ✅ |
| Item 2 — cmp: git show vs live test file | identical (exit 0) | ✅ |
| Item 3 — numstat | 3 files changed | ✅ |
| Item 3 — toplevel | worktree confirmed | ✅ |
| Item 3 — reflog amend check | 0 amends in reflog -n 4 | ✅ |

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: /Users/marklehn/Developer/GitHub/bellows/.bellows-worktrees/567/knowledge/qa/evidence/diff-stat-rename-normalize-2026-08-26/
Files verified: 3
```
