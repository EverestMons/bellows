# QA Receipt — eluvian-wiring-pull (2026-08-26)

**Plan:** executable-548.md.pristine
**Step:** 2 (QA)
**CAPTURE_COMMIT:** `e389a8c34cfd75f2ecf026d10be586e36339e0a8`
**ROOT_COMMIT:** `8d2267ddee9466a09857165288a42b6926bda500`

## Verification Table

| # | Check | Expected | Actual | Status |
|---|-------|----------|--------|--------|
| 1a | grep -cF "Pull latest code" (extraction) | == 1 | 1 | ✅ |
| 1b | grep -oF "ff-only" occurrence count (extraction) | >= 2 | 2 | ✅ |
| 1c | grep -cF "never merge, rebase, stash, or reset" (extraction) | == 1 | 1 | ✅ |
| 1d | grep -cF "daemon restart needed" (extraction) | == 1 | 1 | ✅ |
| 1e | grep -cF "Recite AND assert the system wiring" (extraction) | == 1 | 1 | ✅ |
| 1f | grep -cF "ADVISORY: never refuse to proceed" (extraction) | == 1 | 1 | ✅ |
| 1g | wc -l extraction == dev note recorded value (26) | 26 | 26 | ✅ |
| 1h | cmp extraction vs live eluvian.md | 0 | 0 | ✅ |
| 2a | grep -cF "Domain knowledge deposited in the CENTRAL glossary" (root extraction) | == 1 | 1 | ✅ |
| 2b | grep -cF "scaffold-on-first-use" (root extraction) | == 0 | 0 | ✅ |
| 2c | grep -cF "R2 glossaries live since E5" (root extraction) | == 0 | 0 | ✅ |
| 2d | cmp root extraction vs live ELUVIAN_PATH.md | 0 | 0 | ✅ |
| 3a | grep -cF "git merge" (negative — unsafe verb absent) | == 0 | 0 | ✅ |
| 3b | grep -cF "git rebase" (negative — unsafe verb absent) | == 0 | 0 | ✅ |
| 3c | grep -cF "git reset" (negative — unsafe verb absent) | == 0 | 0 | ✅ |
| 3d | grep -cF "git stash" (negative — unsafe verb absent) | == 0 | 0 | ✅ |
| 3e | grep -cF "git pull --ff-only" (positive control) | >= 1 | 1 | ✅ |
| 3f | grep -cF "git fetch origin" (positive control) | >= 1 | 1 | ✅ |
| 4a | Bellows numstat file count | 2 | 2 | ✅ |
| 4b | Root numstat file count | 1 | 1 | ✅ |
| 4c | Bellows toplevel correct | worktree | worktree | ✅ |
| 4d | Root toplevel correct | /Users/marklehn/Developer/GitHub | /Users/marklehn/Developer/GitHub | ✅ |
| 4e | Bellows reflog amend count | 0 | 0 | ✅ |
| 4f | Root reflog amend count | 0 | 0 | ✅ |

**All 24 checks pass.**

Raw probe output: `probes-raw.txt` (same directory).

Gate note: probe-battery QA, no pytest scope. `qa_test_result` will report "no parseable pytest summary" — the known-benign class (12th precedent); the Planner overrides with reference to this clause and the evidence.

============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: /Users/marklehn/Developer/GitHub/bellows/.bellows-worktrees/548/knowledge/qa/evidence/eluvian-wiring-pull-2026-08-26/
Files verified: 2
