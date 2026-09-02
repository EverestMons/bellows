# Dev Log — gate2-pt-w28-a-2026-09-02 (plan 100021)

**Date:** 2026-09-02  
**Step:** 1 (DEV)  
**Agent:** bellows Developer

---

## A0 — Determination

**TREE_OK:** bellows.py and tests/ present in worktree root.  
**GOV_OK:** PLANNER_TEMPLATE.md, builder, and lessons-forge.db all present.  
**P8:** `forge-cycle-w29` grep count = 0 (Done); `lesson_entries` = 458. W=29 closed. ✓  
**P6:** accepted count = 12. ✓

**Branch ladder:**
1. SHA `c471d3afee3f9094` — matches P1. ✓
2. `git status --porcelain` — EMPTY. ✓
3. Last commit subject on PLANNER_TEMPLATE.md: `[559] gate2-w3(gate2-w3-2026-08-26): PT v4.96 Rules 100-102 + 411-413 implemented, ACC=0` — does NOT carry `gate2-pt-w28-a`. ✓
4. Four rows: 418|accepted|codify|2026-09-01T22:03:28Z, 419|accepted|codify|2026-09-01T22:03:28Z, 430|accepted|codify|2026-09-01T22:03:28Z, 434|accepted|codify|2026-09-01T22:03:28Z. ✓

**Determination: FRESH → A1.**

---

## A1 — Pins

| Pin | Value |
|-----|-------|
| P1_SHA | `c471d3afee3f9094` (matches expected) |
| P1_LINES | 2390 |
| P1_BYTES | 449584 |
| P2_LIFECYCLE_HEADING | 1 |
| P2_VERSION | 1 |
| P2_LASTUPDATED | 1 |
| P2_HISTORY_HEADER | 1 |
| P3_103 | 0 |
| P3_104 | 0 |
| P3_105 | 0 |
| P3_106 | 0 |
| P3_KILLMAP | 0 |
| P3_FIRED | 0 |
| P3_V497 | 0 |
| P3_34 | 1 |
| P4_ONDISK | `f03d62cd4f435ba7` |
| P4_BUILDER_COMMIT | `427f29c3a7bf36eca778490c5f23b3082f416d64` |
| P4_BLOB | `f03d62cd4f435ba7` (matches on-disk) |
| P6_418 | accepted\|codify\|governance_rule\|2026-09-01T22:03:28Z |
| P6_419 | accepted\|codify\|instrumentation\|2026-09-01T22:03:28Z |
| P6_430 | accepted\|codify\|governance_rule\|2026-09-01T22:03:28Z |
| P6_434 | accepted\|codify\|governance_rule\|2026-09-01T22:03:28Z |
| P6_ACCEPTED | 12 |
| P6_IMPLEMENTED | 322 (pre-flip) |
| P6_DISTINCT_STAMP | 2026-09-01T22:03:28Z (one value for all 12 accepted) |

All pins verified. No mismatches.

---

## A2 — Dry Run (scratch→scratch)

Builder: `/Users/marklehn/Developer/eluvian-governance/governance/knowledge/decisions/drafts/build-gate2-pt-w28-a-2026-09-02.py`  
Scratch dir: `/tmp/g2ptw28a/`

**Success line:** `BUILT: /tmp/g2ptw28a/PT-out.md edits=4 blocks=4 lines+33 bytes+9655 post=18/18`  
**builder_exit=0**  
**numstat:** `35\t2` (diff exit=1 expected — differing state)  
**wc -l:** 2423  
**wc -c:** 459239

**Refusals (each BUILDER REFUSED, nonzero exit):**
1. out == in: `BUILDER REFUSED: out == in` — exit=1 ✓
2. out under governance root: `BUILDER REFUSED: out is under the governance root /Users/marklehn/Developer/eluvian-governance` — exit=1 ✓
3. already built: `BUILDER REFUSED: output tokens already present in input — already built?` — exit=1 ✓

---

## A3 — Apply, Task C, Commit

Applied: `cp /tmp/g2ptw28a/PT-out.md /Users/marklehn/Developer/eluvian-governance/PLANNER_TEMPLATE.md`

**Task C — sixteen counts from live file:**

| Count | Token | Value | Expected |
|-------|-------|-------|----------|
| C01 | `### 103. Move the test ORACLE outside the author's model` | 1 | 1 ✓ |
| C02 | `### 104. A detector's fire count is a RATIO` | 1 | 1 ✓ |
| C03 | `### 105. An environment variable is a property of a PROCESS TREE` | 1 | 1 ✓ |
| C04 | `### 106. Earnability is not discrimination` | 1 | 1 ✓ |
| C05 | `### 34. ` | 1 | 1 ✓ |
| C06 | `Report the kill map, not the pass count` | 1 | 1 ✓ |
| C07 | `fired / evaluated / skipped` | 3 | 3 ✓ |
| C08 | `codified 2026-09-02 (Gate 2, cycle W=28 PT tranche one)` | 4 | 4 ✓ |
| C09 | `Extends Rule 14's enumeration-as-code clause` | 1 | 1 ✓ |
| C10 | `Kin of Rule 55's positive-control clause` | 1 | 1 ✓ |
| C11 | `**Version:** 4.97` | 1 | 1 ✓ |
| C12 | `**Version:** 4.96` | 0 | 0 ✓ |
| C13 | `**Last Updated:** 2026-09-02 (v4.97)` | 1 | 1 ✓ |
| C14 | `**Last Updated:** 2026-08-26 (v4.96)` | 0 | 0 ✓ |
| C15 | `\| 2026-09-02 \| v4.97: Gate 2, cycle W=28 PT tranche one` | 1 | 1 ✓ |
| C16 | `\| 2026-08-26 \| v4.96: Gate 2, cycle W=3` | 1 | 1 ✓ |

**wc -l:** 2423 ✓  
**cmp:** SILENT ✓  
**git diff --stat:** 35 insertions(+), 2 deletions(-) ✓

**Governance commit:** `db6d665e` — `[100021] gate2-pt-w28-a: PLANNER_TEMPLATE v4.97 — Rules 103–106 (418, 430, 434, 419)`

---

## A4 — Flip

**Backup:** `/Users/marklehn/Developer/forge_lessons/pre-gate2-pt-w28-a-153821.db` — `backup_exit=0`  
**Backup verification (via `immutable=1`):**
- `PRAGMA integrity_check` → `ok`
- Live count: 466, Backup count: 466 (match)
- `BK=4` (four accepted in 418,419,430,434)

**SQL written:** `/Users/marklehn/Developer/eluvian-governance/governance/knowledge/development/g2ptw28a-flip.sql`

**Flip execution sentinels:**
- `PRE_F=4` ✓
- `CHANGES_F=4` ✓
- `EXCL_F=4` ✓
- `ACC_POST=8` ✓
- `IMPL_POST=326` ✓

**Read-back (fresh read-only connection):**
- 418|implemented|codify|ceo|2026-09-02T20:38:47Z (stamp ≠ 2026-09-01T22:03:28Z) ✓
- 419|implemented|codify|ceo|2026-09-02T20:38:47Z ✓
- 430|implemented|codify|ceo|2026-09-02T20:38:47Z ✓
- 434|implemented|codify|ceo|2026-09-02T20:38:47Z ✓
- accepted=8 ✓
- implemented=326 ✓
- capture file: 441 lines ✓

**Capture copied to worktree:** `knowledge/qa/evidence/gate2-pt-w28-a-2026-09-02/flip-capture.txt`

**SQL governance commit:** `f69690e0` — `[100021] gate2-pt-w28-a: the flip SQL (418, 419, 430, 434 → implemented)`

---

## Status: Complete
