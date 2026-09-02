# QA Receipt — gate2-pt-w28-a-2026-09-02

**Plan:** DOCTRINE — Gate 2, cycle W=28 PT tranche one: proposals 418, 419, 430, 434
**Step:** 2 (QA)
**Date:** 2026-09-02
**QA agent:** bellows worktree 100021

Step 1 receipt status: Complete (commit 7101295 — `[100021] gate2-pt-w28-a: PT v4.97 + flip landed (dev log, flip capture)`)

## Verification Table

| Item | Check | Status |
|------|-------|--------|
| 1 | `git log` for PLANNER_TEMPLATE.md carries `[100021]` and `gate2-pt-w28-a` | ✅ |
| 1 | 16/16 Task C counts as pinned in A3, see probes-raw.txt | ✅ |
| 1 | `wc -l` PLANNER_TEMPLATE.md = 2423 | ✅ |
| 1 | `git status --porcelain` for PT and flip SQL = empty | ✅ |
| 2 | Builder re-ran on pre-edit blob and produced BYTE_IDENTICAL output | ✅ |
| 2 | Builder exit = 0, BUILT line present with edits=4 blocks=4 post=18/18 | ✅ |
| 2 | P4 on-disk digest = f03d62cd4f435ba7; committed blob = f03d62cd4f435ba7 | ✅ |
| 2 | Three refusals: all BUILDER REFUSED, nonzero exit | ✅ |
| 3 | Rows 418/419/430/434 read back as implemented|codify|ceo with stamp 2026-09-02T20:38:47Z | ✅ |
| 3 | accepted count = 8 | ✅ |
| 3 | Eight remaining accepted = 415,417,421,422,425,431,435,437 all at vintage stamp | ✅ |
| 3 | implemented count = 326 | ✅ |
| 3 | flip-capture.txt = 441 lines | ✅ |
| 3 | Capture rows for 418/419/430/434 show accepted|codify (pre-flip state) | ✅ |
| 4 | Full suite: full-suite-gate2-pt-w28-a.txt, exit=0 | ✅ |

## Follow-ups

- Tranche two (415, 417, 421, 422, 425, 431, 435, 437 — eight remaining accepted, thread 76) awaits its own plan.
- The Planner pushes governance after verdict.
- The italic kinship opener on Rules 103 and 106 is deliberate — the CEO's to restyle.
- Bold `**VALUE**` pin rows so `propagation_check` can run on plans of this shape.

## Rule 20 Self-Check — Canonical Block Stdout

============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: /Users/marklehn/Developer/bellows/.bellows-worktrees/100021/knowledge/qa/evidence/gate2-pt-w28-a-2026-09-02/
Files verified: 3
