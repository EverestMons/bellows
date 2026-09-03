# Dev Log — gate2-pt-w28-b-2026-09-02 (plan 100026)

**Date:** 2026-09-02 | **Step:** 1 (DEV)

---

## A0 — Roots and Precondition

**Tree check:** TREE_OK (bellows.py and tests/ present)
**GOV check:** GOV_OK (PLANNER_TEMPLATE.md, builder, and DB present)

**P8 UNCONDITIONAL:**
- `lesson_entries` COUNT → 458 ✓
- `forge-cycle-w30` count → 0 ✓

**Ladder:**
1. P1 sha: `f1701a3744186869` — MATCH
2. Porcelain (PLANNER_TEMPLATE.md + g2ptw28b-flip.sql): EMPTY
3. Last commit subject for PLANNER_TEMPLATE.md: `[100021] gate2-pt-w28-a: PLANNER_TEMPLATE v4.97 — Rules 103–106 (418, 430, 434, 419)` — does NOT carry `gate2-pt-w28-b`
4. Eight rows: all `accepted|codify|2026-09-01T22:03:28Z`
5. `31|23`

**Determination: FRESH → A1**

---

## A1 — Pins Re-derived

**P1:**
- sha: `f1701a3744186869` ✓ (matches plan)
- lines: 2423
- bytes: 459239

**P2 — Nine anchors (all count 1):**
- `## Lifecycle DB Read Protocol (Planner)` → 1
- `Source: proposal 184, lesson 2026-07-22` → 1
- `confirm the method is portable across tool builds before pinning with it.` → 1
- `Source: proposal 120, lesson 2026-06-03` → 1
- `Source: proposal 105, lesson 2026-06-03` → 1
- `Source: proposal 114, lesson 2026-06-03; proposal 126, lesson 2026-06-07; proposal 148, lesson 2026-07-07` → 1
- `**Version:** 4.97` → 1
- `**Last Updated:** 2026-09-02 (v4.97)` → 1
- `| Date | Lesson |` (history header) → 1

**P3 — Zero-before tokens (all 0):**
- `### 107. ` → 0
- `### 108. ` → 0
- `### 109. ` → 0
- `v4.98` → 0
- `codified 2026-09-02 — Gate 2, cycle W=28 PT tranche two` → 0
- `codified 2026-09-02 (Gate 2, cycle W=28 PT tranche two)` → 0
- `**The DECLARATION side is read on the EXECUTING machine` → 0
- `**The amendment act OWNS the re-pin` → 0
- `**The OTHER direction — adding a CONSUMER to an existing label` → 0
- `**Arming a watcher over a directory is RETROACTIVE` → 0
- `**When a string is read by a COMPARATOR` → 0
- `skip, default, or fail-closed` → 0
- Invariants: `### 17. ` → 2; `### 106. ` → 1

**P4 — Builder digest:**
- On-disk: `5d032b8ce50e0faa`
- Committed blob (commit `917ad5c016151c27f8a1cacba0891a1c720becf9`): `5d032b8ce50e0faa`
- MATCH ✓

**P6 — FLIP_PRE:**
- All eight rows: `accepted|codify|2026-09-01T22:03:28Z` ✓
- `accepted` COUNT: 31
- `implemented` COUNT: 326
- Distinct accepted stamps: `2026-09-01T22:03:28Z` (8 rows) + `2026-09-02T23:54:37Z` (23 W=29 rows)
- MAX(id)|COUNT: `466|466`

---

## A2 — Dry Run (scratch→scratch)

**Success line:** `BUILT: /tmp/g2ptw28b/PT-out.md edits=9 blocks=3 lines+35 bytes+17383 post=29/29`
**builder_exit=0**

**Numstat:** `37	2` (37 insertions, 2 deletions) ✓
**wc -l:** 2458 ✓
**wc -c:** 476622 ✓

**Refusals:**
1. `out == in` → `BUILDER REFUSED: out == in` (exit=1) ✓
2. `under forbidden root` → `BUILDER REFUSED: out is under a forbidden root /Users/marklehn/Developer/eluvian-governance (the literal governance root, or the input's git toplevel)` (exit=1) ✓
3. `already built` → `BUILDER REFUSED: output tokens already present in input — already built?` (exit=1) ✓

---

## A3 — Apply and Task C

**cp /tmp/g2ptw28b/PT-out.md to live file:** done

**Task C — 19 counts (all match):**
- `### 107. A STOP arm keys on the claim that would make the work WORTHLESS` → 1
- `### 108. Before optimizing a system's LIFECYCLE, confirm what the system is FOR` → 1
- `### 109. An OPTIONAL datum's consumers silently disagree about absence` → 1
- `codified 2026-09-02 (Gate 2, cycle W=28 PT tranche two)` → 3
- `codified 2026-09-02 — Gate 2, cycle W=28 PT tranche two` → 5
- `**The DECLARATION side is read on the EXECUTING machine` → 1
- `**The amendment act OWNS the re-pin` → 1
- `**The OTHER direction — adding a CONSUMER to an existing label` → 1
- `**Arming a watcher over a directory is RETROACTIVE` → 1
- `**When a string is read by a COMPARATOR, the shipped corpus is the known-good artifact` → 1
- `**Version:** 4.98` → 1
- `**Version:** 4.97` → 0
- `**Last Updated:** 2026-09-02 (v4.98)` → 1
- `**Last Updated:** 2026-09-02 (v4.97)` → 0
- `| 2026-09-02 | v4.98: Gate 2, cycle W=28 PT tranche two` → 1
- `| 2026-09-02 | v4.97: Gate 2, cycle W=28 PT tranche one` → 1
- `## Lifecycle DB Read Protocol (Planner)` → 1
- `### 106. ` → 1
- `### 17. ` → 2

**wc -l:** 2458 ✓
**cmp:** SILENT (byte-identical) ✓
**git diff --stat:** 37 insertions(+), 2 deletions(-) ✓

**Governance commit:** `de662398` — `[100026] gate2-pt-w28-b: PLANNER_TEMPLATE v4.98 — Rules 107–109 (422, 425, 431) + five extensions (415, 417, 421, 435, 437)`

---

## A4 — The Flip

**Backup:** `/Users/marklehn/Developer/forge_lessons/pre-gate2-pt-w28-b-201835.db`
- sqlite `.backup` used ✓
- integrity_check: ok ✓
- live_count=466, backup_count=466 ✓
- BK=8 (eight `accepted` in backup) ✓

**SQL file written:** `$GOV/governance/knowledge/development/g2ptw28b-flip.sql`

**Flip execution sentinels:**
- `PRE_F=8` ✓
- `CHANGES_F=8` ✓
- `EXCL_F=8` ✓
- `ACC_POST=23` ✓
- `IMPL_POST=334` ✓

**Read-back (fresh read-only connection):**
- 415|implemented|codify|ceo|2026-09-03T01:18:58Z ✓
- 417|implemented|codify|ceo|2026-09-03T01:18:58Z ✓
- 421|implemented|codify|ceo|2026-09-03T01:18:58Z ✓
- 422|implemented|codify|ceo|2026-09-03T01:18:58Z ✓
- 425|implemented|codify|ceo|2026-09-03T01:18:58Z ✓
- 431|implemented|codify|ceo|2026-09-03T01:18:58Z ✓
- 435|implemented|codify|ceo|2026-09-03T01:18:58Z ✓
- 437|implemented|codify|ceo|2026-09-03T01:18:58Z ✓
- accepted COUNT: 23 ✓
- implemented COUNT: 334 ✓
- flip-capture.txt: 466 lines ✓
- capture `|accepted|codify|` rows: 31 (pre-flip state) ✓
- All stamps ≠ `2026-09-01T22:03:28Z` ✓

**capture copied to:** `knowledge/qa/evidence/gate2-pt-w28-b-2026-09-02/flip-capture.txt`

**SQL governance commit:** `9679c21c` — `[100026] gate2-pt-w28-b: the flip SQL (415, 417, 421, 422, 425, 431, 435, 437 → implemented)`
