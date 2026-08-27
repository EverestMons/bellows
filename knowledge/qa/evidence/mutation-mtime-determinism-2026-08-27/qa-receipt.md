# QA Receipt — mutation-mtime-determinism (exec-579, Step 2)

**Date:** 2026-08-27
**Plan:** executable-579
**DEV commit:** f8c392c `[579] mutation-mtime-determinism: force bytecode invalidation by mtime; manifest follows the measurement`
**Toplevel:** `/Users/marklehn/Developer/GitHub/bellows/.bellows-worktrees/579`

## Numstat vs DEV commit (3 files)

```
101	0	knowledge/dev-logs/mutation-mtime-determinism-dev-2026-08-27.md
1	7	knowledge/mutants/mutation_check.json
10	0	tools/mutation_check.py
```

## Reflog (last 4)

```
f8c392c HEAD@{0}: reset: moving to HEAD
f8c392c HEAD@{1}: commit
```

0 amends observed.

## Verification

| Item | Check | Result |
|------|-------|--------|
| 1 | Full pytest suite: 0 failed (1632 collected = G6) | ✅ |
| 2 | Five-run determinism: all 5 lines identical (`2 killed, 0 survived, 0 error`) | ✅ |
| 3 | Second-path proof: `/var/folders/vf/8nw0z7hj1m34w6z48l5dp54w0000gn/T/tmp.WNgICfguLi/alt` agrees (`2 killed, 0 survived, 0 error`) | ✅ |
| 4 | Live-tree integrity: pre-shasum `f7037a13…09350d712` = post-shasum `f7037a13…09350d712` | ✅ |
| 5 | gate_watcher consumer: `2 killed, 0 survived, 0 error`, exit=0 | ✅ |
| 6 | Numstat: 3 files; reflog: 0 amends | ✅ |

Five-run determinism result: all five runs returned `MUTATION: 2 killed, 0 survived, 0 error` — identical.
Second-path result: the clone at `/var/folders/vf/8nw0z7hj1m34w6z48l5dp54w0000gn/T/tmp.WNgICfguLi/alt` returned `MUTATION: 2 killed, 0 survived, 0 error` — agrees with primary path.

## Full suite detail

1631 passed, 1 skipped, 0 failed in 62.28s. (1632 collected matches G6 pin.)

## Live-tree integrity

```
PRE:  f7037a1359f175d5f6478a9a00994a56c5ef4db572a9a06b341b5fe09350d712  tools/mutation_check.py
POST: f7037a1359f175d5f6478a9a00994a56c5ef4db572a9a06b341b5fe09350d712  tools/mutation_check.py
```

============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: /Users/marklehn/Developer/GitHub/bellows/.bellows-worktrees/579/knowledge/qa/evidence/mutation-mtime-determinism-2026-08-27/
Files verified: 3
