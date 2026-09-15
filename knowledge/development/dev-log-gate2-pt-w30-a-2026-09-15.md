# Dev Log — gate2-pt-w30-a-2026-09-15 [100109]

**Date:** 2026-09-15  
**Plan:** gate2-pt-w30-a-2026-09-15 (executable-100109)  
**Step:** 1 — DEV

---

## A0 — Branch determination: FRESH

**TREE_OK:** yes (bellows.py and tests/ present)  
**GOV_OK:** yes (PT, builder, DB all present)

**P8 UNCONDITIONAL:**
- `lesson_entries` count: 580 ✓
- `forge-cycle-w31` count: 0 ✓

**Ladder:**
1. PT_SHA = `6846b5a2da16b352` — matches P1 ✓
2. Porcelain EMPTY for PT and g2ptw30a-flip.sql ✓
3. Last subject for PT: `doctrine(PLANNER_TEMPLATE v4.111, GLOSSARY): thread 333's texts applied at the close of bellows #100105 under the CEO's delegation — Rule 23 gains the commit binding; the GLOSSARY gains the pre-check pass record` — does NOT carry `gate2-pt-w30-a` (no) ✓
4. Twelve rows all `accepted|codify` at their vintages: four at `2026-09-02T23:54:37Z`, eight at `2026-09-13T18:27:07Z` ✓
5. `86|86` (accepted population: 86, all at the two vintage stamps) ✓

**Determination: FRESH → A1**

---

## A1 — Pins re-derived

| Pin | Expected | Measured | Match |
|-----|----------|----------|-------|
| P1 PT_SHA | `6846b5a2da16b352` | `6846b5a2da16b352` | ✓ |
| P1 lines | 2515 | 2515 | ✓ |
| P1 bytes | 499815 | 499815 | ✓ |
| P4 on-disk digest | `3d96ad997d9a9b06` | `3d96ad997d9a9b06` | ✓ |
| P4 blob digest | `3d96ad997d9a9b06` | `3d96ad997d9a9b06` | ✓ |
| P4 builder commit | `c9edf8c6...` | `c9edf8c6813b827a2ef35bbaa5ee52c5428b5177` | ✓ |

**P2 anchors (all count 1):** Rule 101 Source line 1 ✓; Rule 102 Source line 1 ✓; Rule 95 Source line 1 ✓; Proposal 387 extension closing 1 ✓; Rule 31's body line 1 ✓; Rule 24 (a)'s line 1 ✓; Checklist 22 distinction sentence 1 ✓; `**Version:** 4.111` 1 ✓; `**Last Updated:** 2026-09-02 (v4.98)` 1 ✓; History header at line 2300 ✓; Checklist 19 at line 1637 ✓; Checklist 14 at line 1603 ✓; Workaround 14 at line 2023 ✓

**P3 new tokens (all 0 pre-edit):** `### 112.`=0, `### 113.`=0, `### 114.`=0, `### 115.`=0, `codified 2026-09-15 (Gate 2...)`=0, `codified 2026-09-15 — Gate 2...`=0, all extension openers=0, `says DIRTY, never MOVED`=0, `### 19. The deposit is the receipt`=0, `Write-to-temp, receipt, then the`=0, `and step prose authorizes NOTHING`=0, `on plan-required evidence files — declare the directory`=0, `**Version:** 4.112`=0, `| 2026-09-15 | v4.112`=0 ✓

**P3 retired tokens (all 1 pre-edit):** `the Planner override per Rule 22(d)...`=1 ✓; `confirm the destination filename matches`=1 ✓; `cd ~/Developer/GitHub && git --no-pager status`=1 ✓; `file PATHS must be inlined in step bodies`=1 ✓; `**(a) Write-to-temp + move.**`=1 ✓; `**Version:** 4.111`=1 ✓; `**Last Updated:** 2026-09-02 (v4.98)`=1 ✓

**P3 invariants:** `### 14.`=3 ✓; `### 19.`=2 ✓; `### 22.`=2 ✓; `### 23.`=2 ✓; `### 24.`=2 ✓; `### 31.`=2 ✓; `### 17.`=2 ✓; `### 110.`=1 ✓; `#### 14.`=1 ✓; `### 111.`=0 ✓

**P6 twelve rows:** 442–461 at `2026-09-02T23:54:37Z`, 472–590 at `2026-09-13T18:27:07Z`, all `accepted|codify` ✓; vintage stamp counts: `2026-09-02T23:54:37Z|23` and `2026-09-13T18:27:07Z|63` (exactly two rows) ✓; proposal 111=`superseded` ✓; MAX(id)=590, COUNT(*)=590 ✓

---

## A2 — Dry run (scratch→scratch)

- Builder invocation: `python3 "$B" "$PT" /tmp/g2ptw30a/PT-out.md`
- Output: `BUILT: /tmp/g2ptw30a/PT-out.md edits=14 blocks=4 lines+43 bytes+23283 post=46/46 deltas=pinned`
- `builder_exit=0` ✓
- numstat: `56	13` (exit=1 expected) ✓
- `wc -l`: 2558 ✓
- `wc -c`: 523098 ✓

**Three refusals:**
1. out==in: `BUILDER REFUSED: out == in` (exit=1) ✓
2. under forbidden root: `BUILDER REFUSED: out is under a forbidden root /Users/marklehn/Developer/eluvian-governance (the literal governance root, or the input's git toplevel)` (exit=1); x.md not written ✓
3. already built: `BUILDER REFUSED: output tokens already present in input — already built?` (exit=1) ✓

---

## A3 — Apply and measure, governance commit

**cp applied:** `/tmp/g2ptw30a/PT-out.md` → `$GOV/PLANNER_TEMPLATE.md`

**Task C counts from live file:**

| Token | Expected | Measured |
|-------|----------|----------|
| `### 112. Two records of one fact DIVERGE...` | 1 | 1 ✓ |
| `### 113. A ruling` | 1 | 1 ✓ |
| `### 114. A migration to a better substrate DROPS...` | 1 | 1 ✓ |
| `### 115. The machine that is not working is the COLD READER` | 1 | 1 ✓ |
| `codified 2026-09-15 (Gate 2, thread 336 — PT tranche one)` | 5 | 5 ✓ |
| `codified 2026-09-15 — Gate 2, thread 336, PT tranche one` | 9 | 9 ✓ |
| `**Doctrine states the OUTCOME a function produces` | 1 | 1 ✓ |
| `**A refuted REMEDY left standing in the corpus` | 1 | 1 ✓ |
| `**A step body has one reader and MANY copiers` | 1 | 1 ✓ |
| `**A lesson codified into doctrine reads as DISCHARGED` | 1 | 1 ✓ |
| `says DIRTY, never MOVED` | 1 | 1 ✓ |
| `cd ~/Developer/GitHub && git --no-pager status` | 0 | 0 ✓ |
| `### 19. The deposit is the receipt, then the` | 1 | 1 ✓ |
| `confirm the destination filename matches` | 0 | 0 ✓ |
| `Write-to-temp, receipt, then the` | 1 | 1 ✓ |
| `**(a) Write-to-temp + move.**` | 0 | 0 ✓ |
| `and step prose authorizes NOTHING` | 1 | 1 ✓ |
| `file PATHS must be inlined in step bodies (scope_check requirement)` | 0 | 0 ✓ |
| `on plan-required evidence files — declare the directory` | 1 | 1 ✓ |
| `the Planner override per Rule 22(d) is the correct disposition` | 0 | 0 ✓ |
| `**Version:** 4.112` | 1 | 1 ✓ |
| `**Version:** 4.111` | 0 | 0 ✓ |
| `**Last Updated:** 2026-09-15 (v4.112)` | 1 | 1 ✓ |
| `\| 2026-09-15 \| v4.112: Gate 2, thread 336` | 1 | 1 ✓ |
| `\| 2026-09-09 \| v4.105: CEO act at the close of bellows plan 100052` | 1 | 1 ✓ |
| `## Lifecycle DB Read Protocol (Planner)` | 1 | 1 ✓ |
| `### 110.` | 1 | 1 ✓ |
| `### 111.` | 0 | 0 ✓ |
| `### 14.` | 3 | 3 ✓ |
| `### 17.` | 2 | 2 ✓ |

**wc -l:** 2558 ✓  
**cmp:** SILENT (byte-identical) ✓  
**git diff --stat:** 56 insertions(+), 13 deletions(-) ✓

**Governance commit:** `f402a9dd`  
Subject: `[100109] gate2-pt-w30-a: PLANNER_TEMPLATE v4.112 — Rules 112-115 (442, 458, 461, 443), four extensions (472, 476, 477, 498), Rule 31 rewritten (490), three sweeps (523, 589, 590)`

---

## A4 — The flip

**Backup:** `/Users/marklehn/Developer/forge_lessons/pre-gate2-pt-w30-a-154856.db`  
- `sqlite3 "$DB" ".backup ..."` exit=0 ✓
- Backup integrity check: `ok` ✓
- Live count: 590; Backup count: 590 (equal) ✓
- BK=12 (twelve `accepted` rows in backup) ✓

**Flip SQL written to:** `$GOV/governance/knowledge/development/g2ptw30a-flip.sql`

**Execution:** `sqlite3 -bail "$DB" < g2ptw30a-flip.sql`

**Sentinels:**
- `PRE_F=12` ✓
- `CHANGES_F=12` ✓
- `EXCL_F=12` ✓
- `ACC_POST=74` ✓
- `IMPL_POST=345` ✓

**Read-back (fresh read-only connection):**
- All twelve rows: `implemented|codify|ceo|2026-09-15T20:49:16Z` — outside the two vintages ✓
- Accepted count: 74 ✓
- Accepted at two vintages: 74 ✓ (remaining 74 still at their vintage stamps)
- Implemented count: 345 ✓
- Capture file: 590 lines ✓
- Capture has 86 rows with `|accepted|codify|` ✓
- Twelve capture rows show `accepted|codify|governance_rule|planner|<vintage_stamp>` (pre-flip state) ✓

**Capture copied to:** `knowledge/qa/evidence/gate2-pt-w30-a-2026-09-15/flip-capture.txt` (590 lines) ✓

**SQL commit:** `d73893d3`  
Subject: `[100109] gate2-pt-w30-a: the flip SQL (442, 443, 458, 461, 472, 476, 477, 490, 498, 523, 589, 590 -> implemented)`
