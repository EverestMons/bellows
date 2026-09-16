# QA Receipt — gate2-pt-w30-e-2026-09-16

**Plan:** bellows #100121 — Gate 2, PT tranche five (proposals 447, 456, 459, 497, 517, 527, 546, 573, 576, 581, 582)
**QA date:** 2026-09-16
**Step:** 2 of 2

## Verification Table

| Item | Check | Status |
|------|-------|--------|
| Item 1 — template commit | `[100121]` subject on `PLANNER_TEMPLATE.md` | ✅ |
| Item 1 — Task C counts | 30/30 counts as pinned in A3, see probes-raw.txt | ✅ |
| Item 1 — wc -l | 2639 | ✅ |
| Item 1 — porcelain | EMPTY for PLANNER_TEMPLATE.md and g2ptw30e-flip.sql | ✅ |
| Item 2 — builder rebuild | BYTE_IDENTICAL from pre-edit blob, builder_exit=0 | ✅ |
| Item 2 — P4 digest | cba5026c71ba6f99 = blob at 668fcaf0 | ✅ |
| Item 2 — refusal 1 (out==in) | BUILDER REFUSED | ✅ |
| Item 2 — refusal 2 (forbidden root) | BUILDER REFUSED | ✅ |
| Item 2 — refusal 3 (already built) | BUILDER REFUSED | ✅ |
| Item 3 — eleven rows status | implemented\|codify\|ceo\|2026-09-16T19:12:15Z (outside vintages) | ✅ |
| Item 3 — accepted count | 25 | ✅ |
| Item 3 — accepted at vintages | 25 of 25 | ✅ |
| Item 3 — implemented count | 394 | ✅ |
| Item 3 — flip-capture line count | 590 | ✅ |
| Item 3 — capture pre-flip state | all 11 read accepted\|codify | ✅ |
| Item 3 — capture committed by DEV | [100121] subject confirmed | ✅ |
| Item 4 — suite file | full-suite-gate2-pt-w30-e.txt, exit=0 | ✅ |

## Follow-ups

- The two remaining tranches (tranche six and the DC/PST tranche) are their own plans, per the packet order.
- The Planner pushes governance after the pause and projects the `LESSONS.md` markers (`scripts/project_status_markers.py --apply`).
- Thread 336 remains open until the seventh tranche closes.

============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: /Users/marklehn/Developer/bellows/.bellows-worktrees/100121/knowledge/qa/evidence/gate2-pt-w30-e-2026-09-16
Files verified: 3

