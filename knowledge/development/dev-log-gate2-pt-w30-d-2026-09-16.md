# Dev Log — gate2-pt-w30-d-2026-09-16 (plan #100120)

**Date:** 2026-09-16  
**Step:** 1 (DEV)  
**Plan:** PT tranche four — verdict read, deposit mechanics, conversation, threads and authority  
**Proposals:** 446, 455, 460, 486, 505, 507, 516, 522, 526, 539, 555, 557, 558, 571, 578

---

## A0 — Branch determination: FRESH

- TREE_OK: bellows.py and tests/ present in worktree
- GOV_OK: PLANNER_TEMPLATE.md, builder, and lessons-forge.db all present
- P8 UNCONDITIONAL: lesson_entries=580 ✓, forge-cycle-w31 count=0 ✓
- Ladder (1): sha=`d61b6c1108ab8608` matches P1 ✓
- Ladder (2): porcelain EMPTY ✓
- Ladder (3): last commit subject does NOT carry `gate2-pt-w30-d` ✓
- Ladder (4): fifteen rows all `accepted|codify` at their vintages (446/455/460 at `2026-09-02T23:54:37Z`; 486–578 at `2026-09-13T18:27:07Z`) ✓
- Ladder (5): `51|51` ✓
- **Determination: FRESH → A1**

---

## A1 — Pins re-derived

| Pin | Value | Match |
|-----|-------|-------|
| P1 sha | `d61b6c1108ab8608` | ✓ |
| P1 lines | 2601 | ✓ |
| P1 bytes | 558339 | ✓ |
| P2 anchors | E1–E11 all at their expected lines; counts each 1 | ✓ |
| P3 new tokens | all 0 before edit | ✓ |
| P3 invariants | `### 2.`=5, `### 3.`=5, `### 4.`=5, `### 22.`=2, `### 23.`=2, `### 24.`=2, `### 49.`=1, `### 50.`=1, `### 52.`=1, `### 53.`=1, `### 116.`=1, `### 14.`=3, `### 17.`=2 | ✓ |
| P4 on-disk | `078a01b52081a8c2` | ✓ |
| P4 blob at `6c2632e0` | `078a01b52081a8c2` | ✓ |
| P6 fifteen rows | all `accepted\|codify` at vintages | ✓ |
| P6 accepted count | 51 | ✓ |
| P6 implemented count | 368 | ✓ |
| P6 accepted grouped | `2026-09-02T23:54:37Z\|14` and `2026-09-13T18:27:07Z\|37` (two rows only) | ✓ |
| P6 max id / count | `590\|590` | ✓ |

---

## A2 — Dry-run (scratch → scratch)

Builder output:
```
BUILT: /tmp/g2ptw30d/PT-out.md edits=11 blocks=1 lines+23 bytes+20279 post=40/40 deltas=pinned
builder_exit=0
```

numstat: `25	2` (exit 1 as expected — differing state) ✓  
wc -l: 2624 ✓  
wc -c: 578618 ✓

**Three refusals:**
1. `BUILDER REFUSED: out == in` (exit 1) ✓
2. `BUILDER REFUSED: out is under a forbidden root /Users/marklehn/Developer/eluvian-governance` (exit 1) ✓
3. `BUILDER REFUSED: output tokens already present in input — already built?` (exit 1) ✓

---

## A3 — Apply + measure + commit

`cp /tmp/g2ptw30d/PT-out.md "$GOV/PLANNER_TEMPLATE.md"` ✓

**Task C counts (34 probes):**
| Token | Count |
|-------|-------|
| `### 117. A tracked thread` | 1 |
| `**Rule 117 — a thread` | 1 |
| Rule 116 Source line (tranche three) | 1 |
| `**The (b) read runs a shipped tool on the ordinary case` | 1 |
| `**A tool that reads COMMITTED state runs after the commit it audits` | 1 |
| `**A refused verdict is a question about the ACCEPTING path` | 1 |
| `**A design captured from conversation is a HYPOTHESIS: SURVEY before SKETCH` | 1 |
| `**Before offering choices, read the standing queue` | 1 |
| `**An automated approval shows the human` | 1 |
| `**A standing ruling carries its PREMISE` | 1 |
| `codified 2026-09-16 — Gate 2, thread 336, PT tranche four` | 7 |
| `codified 2026-09-16 (Gate 2, thread 336 — PT tranche four)` | 1 |
| `**Version:** 4.116` | 1 |
| `**Version:** 4.115` | 0 |
| `**Last Updated:** 2026-09-16 (v4.116)` | 1 |
| `**Last Updated:** 2026-09-16 (v4.115)` | 0 |
| `\| 2026-09-16 \| v4.116: Gate 2, thread 336` | 1 |
| `\| 2026-09-16 \| v4.115: Gate 2, thread 336` | 1 |
| `\| 2026-09-16 \| v4.114: CEO act at the close of bellows plan 100118` | 1 |
| `\| 2026-09-15 \| v4.113: Gate 2, thread 336` | 1 |
| `\| 2026-09-15 \| v4.112: Gate 2, thread 336` | 1 |
| `## Lifecycle DB Read Protocol (Planner)` | 1 |
| `### The Verdict Cycle` | 1 |
| `### The Disable-Auto-Close Model` | 1 |
| `## Decision Authority` | 1 |
| `## Planning Conversation Flow` | 1 |
| `### 22. ` | 2 |
| `### 23. ` | 2 |
| `### 24. ` | 2 |
| `### 52. ` | 1 |
| `### 53. ` | 1 |
| `### 116. ` | 1 |
| `### 14. ` | 3 |
| `### 17. ` | 2 |

wc -l: 2624 ✓  
cmp: IDENTICAL ✓  
git diff --stat: 25 insertions, 2 deletions ✓

**Governance commit:** `d04f2f4a`  
Subject: `[100120] gate2-pt-w30-d: PLANNER_TEMPLATE v4.116 — seven extensions (557+571+578, 526, 455+522, 446, 486+507, 460+555, 539+558+516), Rule 117 (505)`

---

## A4 — Flip (doctrine before DB)

**Backup:** `sqlite3 "$DB" ".backup /Users/marklehn/Developer/forge_lessons/pre-gate2-pt-w30-d-121617.db"`  
Integrity check: `ok` ✓  
Backup row count: 590 (matches live) ✓  
BK=15 (fifteen accepted in backup) ✓

**Flip sentinels:**
```
PRE_F=15
CHANGES_F=15
EXCL_F=15
ACC_POST=36
IMPL_POST=383
```

**Read-back (fresh read-only connection):**
- Fifteen rows: `implemented|codify|ceo|2026-09-16T17:16:40Z` ✓ (stamps NOT the two vintages)
- accepted=36 ✓
- implemented=383 ✓
- flip-capture.txt: 590 lines ✓
- Capture has 51 `|accepted|codify|` rows (pre-flip state) ✓

Capture copied to `knowledge/qa/evidence/gate2-pt-w30-d-2026-09-16/flip-capture.txt` ✓

**SQL commit in governance:** `b43da79a`  
Subject: `[100120] gate2-pt-w30-d: the flip SQL (446, 455, 460, 486, 505, 507, 516, 522, 526, 539, 555, 557, 558, 571, 578 -> implemented)`
