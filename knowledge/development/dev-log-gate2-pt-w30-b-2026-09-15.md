# Dev Log — gate2-pt-w30-b-2026-09-15 [100114]

**Date:** 2026-09-15 (UTC clock: 2026-09-16T01:06Z)
**Plan:** DOCTRINE — Gate 2, thread 336, PT tranche two (pins, measurement and instruments)

---

## A0 — Determination

**TREE_OK**: `bellows.py` and `tests/` present in worktree root.
**GOV_OK**: `PLANNER_TEMPLATE.md`, builder, and DB all present.
**P8 unconditional**: `lesson_entries` = 580 (no W=31 ingest); `forge-cycle-w31` count = 0. PASS.

**Branch ladder:**
- (1) sha = `ad895fa075675681` — matches P1
- (2) porcelain = EMPTY
- (3) last commit subject = `[100109] gate2-pt-w30-a: ...` — does NOT carry `gate2-pt-w30-b`
- (4) twelve rows all `accepted|codify` at their vintages
- (5) `74|74`

**Determination: FRESH** → A1.

---

## A1 — Pin Re-derivation

| Pin | What | Measured | Pinned | Match |
|-----|------|----------|--------|-------|
| P1 sha | PT_SHA | `ad895fa075675681` | `ad895fa075675681` | ✓ |
| P1 lines | wc -l | 2558 | 2558 | ✓ |
| P1 bytes | wc -c | 523098 | 523098 | ✓ |
| P2 E1 | blank+Rule62 heading | 1 | 1 | ✓ |
| P2 E2 | Rule 78 Source line | 1 | 1 | ✓ |
| P2 E3 | Rule 82 Source line | 1 | 1 | ✓ |
| P2 E4 | Rule 104 Source line | 1 | 1 | ✓ |
| P2 E5 | blank+Rule56 heading | 1 | 1 | ✓ |
| P2 E6 | Rule 58 Source line (bare) | 1 | 1 | ✓ |
| P2 E8 | Rule 103 Source line | 1 | 1 | ✓ |
| P2 E9 | blank+Rule98 heading | 1 | 1 | ✓ |
| P2 E10 | Version 4.112 | 1 | 1 | ✓ |
| P2 E11 | Last Updated v4.112 | 1 | 1 | ✓ |
| P2 History header | line 2342 | line 2342 | line 2342 | ✓ |
| P2 span start | Rule 111 opener | 2 (headless + History) | 2 | ✓ |
| P2 span end | Rule 77 Source line | 1 | 1 | ✓ |
| P2 span order | 111 before 77's source | IN ORDER | IN ORDER | ✓ |
| P3 new tokens | all 14 zero-before tokens | all 0 | all 0 | ✓ |
| P3 invariants | all section headings | all at expected counts | all expected | ✓ |
| P3 retired | Version 4.112, Last Updated v4.112 | 1 each | 1 each | ✓ |
| P3 moved | Rule 111 opener (2 before) | 2 | 2 | ✓ |
| P4 on-disk digest | builder sha | `284265a870342ace` | `284265a870342ace` | ✓ |
| P4 blob digest | from BC=`30781aaa` | `284265a870342ace` | `284265a870342ace` | ✓ |
| P6 twelve rows | accepted\|codify at vintages | all 12 confirmed | all 12 | ✓ |
| P6 accepted | COUNT | 74 | 74 | ✓ |
| P6 implemented | COUNT | 345 | 345 | ✓ |
| P6 vintage stamps | exactly two rows | `2026-09-02T23:54:37Z\|19`, `2026-09-13T18:27:07Z\|55` | 2 rows | ✓ |
| P6 max/count | MAX(id), COUNT(*) | 590\|590 | 590\|590 | ✓ |

---

## A2 — Dry-run (scratch→scratch)

**Builder run:** `python3 $B $GOV/PLANNER_TEMPLATE.md /tmp/g2ptw30b/PT-out.md`

Success line: `BUILT: /tmp/g2ptw30b/PT-out.md edits=12 blocks=1 lines+23 bytes+19305 post=40/40 deltas=pinned`
`builder_exit=0`

**Numstat:** `27	4` (exit 1 — expected differing state)
**wc -l:** 2581
**wc -c:** 542403

**Three refusals (all BUILDER REFUSED, exit 1):**
1. out == in: `BUILDER REFUSED: out == in`
2. under forbidden root: `BUILDER REFUSED: out is under a forbidden root /Users/marklehn/Developer/eluvian-governance (the literal governance root, or the input's git toplevel)`
3. already built: `BUILDER REFUSED: output tokens already present in input — already built?`

---

## A3 — Apply, Measure, Commit

**Apply:** `cp /tmp/g2ptw30b/PT-out.md $GOV/PLANNER_TEMPLATE.md`

**Task C counts (26/26 pass):**
- `### 111. Diagnostic output...` heading: 1
- `**Rule 111 — diagnostic output` (old headless, History only): 1
- `*Source: proposal 267, codified 2026-08-11 (Gate 2 batch 2)*`: 1
- `**A pin's producing command names its TARGET, and a pin protects a CLAIM, not a digest`: 1
- `**A quantifier clause's POPULATION is pinned before the freeze`: 1
- `**A scoping argument that correctly excludes one population is not a bound on the risk`: 1
- `**A check is priced by its MARGINAL count, calibrated on the corpus before it is wired`: 1
- `**A positive control proves the instrument works, not that you CALLED it correctly`: 1
- `**A pattern that explains three defects is a HYPOTHESIS about the fourth`: 1
- `**A diagnostic's authority extends only to what its instrument executed`: 1
- `**The defect class just fixed is the one reproduced next`: 1
- `**A COPIES claim needs three facts`: 1
- `codified 2026-09-15 — Gate 2, thread 336, PT tranche two`: 9
- `codified 2026-09-15 (Gate 2, thread 336 — PT tranche two)`: 1
- `**Version:** 4.113`: 1
- `**Version:** 4.112`: 0
- `**Last Updated:** 2026-09-15 (v4.113)`: 1
- `**Last Updated:** 2026-09-15 (v4.112)`: 0
- `| 2026-09-15 | v4.113: Gate 2, thread 336`: 1
- `| 2026-09-15 | v4.112: Gate 2, thread 336` (tranche one survives): 1
- `## Lifecycle DB Read Protocol (Planner)`: 1
- `### 77. `: 1
- `### 78. `: 1
- `### 112. `: 1
- `### 14. `: 3
- `### 17. `: 2

**wc -l:** 2581
**cmp:** IDENTICAL (scratch vs live)
**git diff --stat:** 27 insertions(+), 4 deletions(-)

**Governance commit:** `f0d8694b` — `[100114] gate2-pt-w30-b: PLANNER_TEMPLATE v4.113 — eight extensions (471+502, 469, 482, 501+512+553, 488, 492, 506, 449), Rule 111's heading (484)`

---

## A4 — The Flip

**Backup:** `sqlite3 "$DB" ".backup /Users/marklehn/Developer/forge_lessons/pre-gate2-pt-w30-b-200537.db"`
- integrity_check: ok
- backup count: 590 (equal to live)
- BK check (12 rows accepted): 12

**Flip SQL written to:** `$GOV/governance/knowledge/development/g2ptw30b-flip.sql`

**Flip execution:** `sqlite3 -bail "$DB" < "$GOV/governance/knowledge/development/g2ptw30b-flip.sql"`

Sentinels:
- `PRE_F=12` ✓
- `CHANGES_F=12` ✓
- `EXCL_F=12` ✓
- `ACC_POST=62` ✓
- `IMPL_POST=357` ✓

**Read-back (fresh read-only connection):**
- 12 rows `implemented|codify|ceo|2026-09-16T01:06:00Z` (stamp NOT one of the two vintages) ✓
- Accepted: 62 ✓
- Implemented: 357 ✓
- Accepted at vintages: 62 (all remaining accepted rows at the two vintage stamps) ✓
- Capture file: 590 lines ✓
- Capture: 12 rows had `accepted|codify` (pre-flip state) ✓

**SQL commit:** `bd30369a` — `[100114] gate2-pt-w30-b: the flip SQL (449, 469, 471, 482, 484, 488, 492, 501, 502, 506, 512, 553 -> implemented)`

**Capture copied to worktree:** `knowledge/qa/evidence/gate2-pt-w30-b-2026-09-15/flip-capture.txt`
