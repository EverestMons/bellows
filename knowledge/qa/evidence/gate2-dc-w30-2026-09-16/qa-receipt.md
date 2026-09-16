# QA Receipt — gate2-dc-w30-2026-09-16

**Plan:** gate2-dc-w30-2026-09-16
**Step:** 2 (QA)
**Date:** 2026-09-16
**QA agent:** bellows worktree 100123

## Verification Table

| Item | Check | Status |
|------|-------|--------|
| 1 | Both files committed in the same [100123] governance commit | ✅ |
| 1 | git status porcelain empty (DC, PST, flip SQL) | ✅ |
| 1 | 55/55 counts as pinned in A3, see probes-raw.txt | ✅ |
| 1 | wc -l: DC=403, PST=43 | ✅ |
| 2 | Builder byte-identity: BYTE_IDENTICAL on both files | ✅ |
| 2 | builder_exit=0, BUILT line matches P5 | ✅ |
| 2 | P4: on-disk digest 86865d1aebba8468 = blob at f83bbb29 | ✅ |
| 2 | Three builder refusals confirmed | ✅ |
| 3 | All 17 rows: implemented, route=codify, updated_by=ceo, stamp outside vintages | ✅ |
| 3 | accepted=0 (no accepted row remains — Gate 2 complete) | ✅ |
| 3 | implemented=419 | ✅ |
| 3 | flip-capture.txt: 590 lines; 17 pre-flip rows accepted|codify at vintages | ✅ |
| 3 | flip-capture.txt committed in [100123] dev log commit | ✅ |
| 4 | full-suite-gate2-dc-w30.txt: exit=0 | ✅ |

## Follow-ups

- Gate 2 over W=29 and W=30 is now complete: no accepted row remains.
- The Planner pushes governance and projects the LESSONS.md markers after the close.
- Thread 336 closes at the keyboard.
- No further DC/PST tranche — this was the seventh and last.

============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: /Users/marklehn/Developer/bellows/.bellows-worktrees/100123/knowledge/qa/evidence/gate2-dc-w30-2026-09-16
Files verified: 3
