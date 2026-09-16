# QA Receipt — gate2-pt-w30-d-2026-09-16

**Plan:** DOCTRINE — Gate 2, thread 336, PT tranche four (proposals 446, 455, 460, 486, 505, 507, 516, 522, 526, 539, 555, 557, 558, 571, 578)
**Step:** 2 (QA)
**Date:** 2026-09-16
**QA agent:** bellows worktree 100120

## Verification

| Item | Check | Status |
|------|-------|--------|
| Item 1 | Template commit carries `[100120]` and `gate2-pt-w30-d` in subject | ✅ |
| Item 1 | 34/34 counts as pinned in A3, see probes-raw.txt | ✅ |
| Item 1 | `wc -l` → 2624 | ✅ |
| Item 1 | `git status --porcelain` → EMPTY for PLANNER_TEMPLATE.md and g2ptw30d-flip.sql | ✅ |
| Item 2 | Pre-edit blob extracted from commit parent | ✅ |
| Item 2 | Builder BUILT: edits=11 blocks=1 lines+23 bytes+20279 post=40/40 deltas=pinned, exit=0 | ✅ |
| Item 2 | `cmp` → BYTE_IDENTICAL | ✅ |
| Item 2 | P4 on-disk digest == blob at own last commit (078a01b52081a8c2 at 6c2632e0) | ✅ |
| Item 2 | Refusal 1 (out == in) → BUILDER REFUSED | ✅ |
| Item 2 | Refusal 2 (under forbidden root) → BUILDER REFUSED | ✅ |
| Item 2 | Refusal 3 (already built) → BUILDER REFUSED | ✅ |
| Item 3 | Fifteen rows all `implemented\|codify\|ceo\|<stamp outside vintages>` | ✅ |
| Item 3 | `accepted` count → 36 | ✅ |
| Item 3 | All 36 accepted rows at the two vintage stamps | ✅ |
| Item 3 | `implemented` count → 383 | ✅ |
| Item 3 | flip-capture.txt → 590 lines | ✅ |
| Item 3 | Capture: fifteen rows show `accepted\|codify` pre-flip state | ✅ |
| Item 3 | flip-capture committed by DEV step (subject carries `[100120]`) | ✅ |
| Item 4 | Suite file: full-suite-gate2-pt-w30-d.txt, exit=0 | ✅ |

## Follow-ups (not this plan's act)

- Tranches five and six and the DC/PST tranche: the thirty-six remaining `accepted|codify` rows, each their own plan (packet order)
- Planner pushes governance and projects the LESSONS.md markers (`scripts/project_status_markers.py --apply`) after close
- Thread 336 keyboard work at the seventh tranche's close


============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: /Users/marklehn/Developer/bellows/.bellows-worktrees/100120/knowledge/qa/evidence/gate2-pt-w30-d-2026-09-16/
Files verified: 3
