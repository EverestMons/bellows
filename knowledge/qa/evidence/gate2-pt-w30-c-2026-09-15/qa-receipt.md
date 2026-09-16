# QA Receipt — gate2-pt-w30-c-2026-09-15

**Plan:** gate2-pt-w30-c-2026-09-15
**Step:** 2 (QA)
**Date:** 2026-09-16
**Agent:** bellows QA

## Verification

| Item | Description | Status |
|------|-------------|--------|
| 1 | Live template: governance commit `8daabb22` carries `[100119]`; 27/27 counts as pinned in A3, see probes-raw.txt; wc -l 2601; porcelain EMPTY | ✅ |
| 2 | Builder byte-identity: rebuilt from pre-edit blob `8daabb22^`, BYTE_IDENTICAL; P4 on-disk digest 5d6f66518e21c84b = blob at bfe58149; 3 refusals each BUILDER REFUSED | ✅ |
| 3 | Flip read-back: 11 rows implemented\|codify\|ceo with stamp 2026-09-16T16:01:18Z (outside vintages); accepted 51; accepted-at-vintages 51; implemented 368; capture 590 lines, 62 pre-flip accepted\|codify rows; capture committed at plan id | ✅ |
| 4 | full-suite-gate2-pt-w30-c.txt; exit=0 | ✅ |

## Follow-ups

- Four tranches remain after this one (tranches four to six and DC/PST); each is its own plan in the packet's order.
- The Planner pushes governance after the pause and projects the LESSONS.md markers.
- Thread 336 closes at the keyboard after the seventh tranche.

============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: /Users/marklehn/Developer/bellows/.bellows-worktrees/100119/knowledge/qa/evidence/gate2-pt-w30-c-2026-09-15/
Files verified: 3

