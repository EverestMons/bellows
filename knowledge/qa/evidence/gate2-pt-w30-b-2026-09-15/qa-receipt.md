# QA Receipt — gate2-pt-w30-b-2026-09-15

**Plan id:** 100114
**Step:** 2 (QA)
**Date:** 2026-09-15
**Slug:** gate2-pt-w30-b-2026-09-15

## Verification Table

| Item | Check | Status |
|------|-------|--------|
| 1 | Template commit carries `[100114]` and `gate2-pt-w30-b` | ✅ |
| 1 | git status --porcelain for PLANNER_TEMPLATE.md and g2ptw30b-flip.sql — EMPTY | ✅ |
| 1 | 26/26 counts as pinned in A3, see probes-raw.txt | ✅ |
| 1 | wc -l PLANNER_TEMPLATE.md → 2581 | ✅ |
| 2 | Builder rebuilt from pre-edit blob: BYTE_IDENTICAL | ✅ |
| 2 | builder_exit=0, BUILT line: edits=12 blocks=1 lines+23 bytes+19305 post=40/40 deltas=pinned | ✅ |
| 2 | P4 digest on-disk matches blob at builder's own commit (30781aaa): 284265a870342ace | ✅ |
| 2 | Refusal 1 (out==in): BUILDER REFUSED, exit=1 | ✅ |
| 2 | Refusal 2 (under forbidden root): BUILDER REFUSED, exit=1 | ✅ |
| 2 | Refusal 3 (already built): BUILDER REFUSED, exit=1 | ✅ |
| 3 | 12 rows: implemented\|codify\|ceo, stamp outside two vintages | ✅ |
| 3 | accepted count → 62 | ✅ |
| 3 | accepted at two vintages → 62 | ✅ |
| 3 | implemented count → 357 | ✅ |
| 3 | flip-capture.txt → 590 lines | ✅ |
| 3 | capture's 12 rows: accepted\|codify at their vintage stamps (pre-flip) | ✅ |
| 3 | flip-capture.txt committed by Step 1 (commit subject carries 100114) | ✅ |
| 4 | full-suite-gate2-pt-w30-b.txt, exit=0 | ✅ |

## Follow-ups

- The five remaining tranches of Gate 2 (tranches three to six and the DC/PST tranche), each its own plan per the packet's order
- The Planner pushes governance and projects the LESSONS.md markers after close
- Thread 336 closed at the keyboard after the seventh tranche


============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: /Users/marklehn/Developer/bellows/.bellows-worktrees/100114/knowledge/qa/evidence/gate2-pt-w30-b-2026-09-15/
Files verified: 3
