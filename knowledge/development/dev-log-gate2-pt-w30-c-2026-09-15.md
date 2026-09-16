# Dev Log — gate2-pt-w30-c-2026-09-15 (plan #100119)

## A0 — Determination

**Precondition:** TREE_OK (bellows.py, tests/ present). GOV_OK (PLANNER_TEMPLATE.md, builder, DB all present).

**P8 unconditional:** `lesson_entries` = 580 (no W=31 ingest); `forge-cycle-w31` count = 0.

**Ladder:**
- (1) P1 sha = `a2847e81389ef164` — matches pin
- (2) Porcelain — EMPTY (FRESH)
- (3) Last commit subject for PLANNER_TEMPLATE.md — does NOT carry `gate2-pt-w30-c` (the thread-322 doctrine act is the last commit)
- (4) Eleven rows: all `accepted|codify` at their vintages (453,462,463,464 at `2026-09-02T23:54:37Z`; 480,500,509,520,544,559,583 at `2026-09-13T18:27:07Z`)
- (5) `62|62`

**Determination: FRESH → A1**

## A1 — Pins Re-derived

| pin | value | pin |
|-----|-------|-----|
| P1 sha | `a2847e81389ef164` | MATCH |
| P1 lines | 2582 | MATCH |
| P1 bytes | 543627 | MATCH |
| P2 anchors spot-check | `**Version:** 4.114` → 1; `**Last Updated:** 2026-09-16 (v4.114)` → 1; Rule 115 Source → 1; Lifecycle heading → 1 | MATCH |
| P3 zero-tokens (sample) | `### 116. ` → 0; `ONE parser` → 0; `682 plans` → 0; `from the callee` → 0; `by EFFECT` → 0 | MATCH |
| P4 on-disk digest | `5d6f66518e21c84b` | MATCH |
| P4 blob digest (builder last commit `bfe58149`) | `5d6f66518e21c84b` | MATCH |
| P6 eleven rows | 453,462,463,464 `accepted\|codify\|planner\|2026-09-02T23:54:37Z`; 480,500,509,520,544,559,583 `accepted\|codify\|planner\|2026-09-13T18:27:07Z` | MATCH |

## A2 — Dry Run

Scratch dir: `/tmp/g2ptw30c`

Builder output:
```
BUILT: /tmp/g2ptw30c/PT-out.md edits=9 blocks=1 lines+19 bytes+14712 post=35/35 deltas=pinned
builder_exit=0
```

numstat: `21	2` (exit 1 expected — differing state) ✓

wc -l: 2601 ✓
wc -c: 558339 ✓

Three refusals:
- Refusal 1 (out == in): `BUILDER REFUSED: out == in` exit=1 ✓
- Refusal 2 (under forbidden root): `BUILDER REFUSED: out is under a forbidden root /Users/marklehn/Developer/eluvian-governance (the literal governance root, or the input's git toplevel)` exit=1 ✓
- Refusal 3 (already built): `BUILDER REFUSED: output tokens already present in input — already built?` exit=1 ✓

## A3 — Apply and Measure (Task C)

`cp /tmp/g2ptw30c/PT-out.md $GOV/PLANNER_TEMPLATE.md` — cp_exit=0

Task C counts (27/27):

| token | count | expected |
|-------|-------|----------|
| `### 116. One contract, ONE parser, every consumer calls it` | 1 | 1 ✓ |
| `**Rule 116 — one contract, ONE parser` | 1 | 1 ✓ |
| `*Source: proposal 443, entry 435 (2026-09-01), codified 2026-09-15 (Gate 2, thread 336 — PT tranche one)*` | 1 | 1 ✓ |
| `**An edit surface is enumerated from the CALLEE's definition` | 1 | 1 ✓ |
| `**A shared list's consumers are enumerated by member name AND by EFFECT` | 1 | 1 ✓ |
| `**A recalled fact is checked before it is offered` | 1 | 1 ✓ |
| `**A vocabulary that looks one value short resolves through its EXISTING states first` | 1 | 1 ✓ |
| `**A log whose lines carry times without dates` | 1 | 1 ✓ |
| `codified 2026-09-16 — Gate 2, thread 336, PT tranche three` | 5 | 5 ✓ |
| `codified 2026-09-16 (Gate 2, thread 336 — PT tranche three)` | 1 | 1 ✓ |
| `**Version:** 4.115` | 1 | 1 ✓ |
| `**Version:** 4.114` | 0 | 0 ✓ |
| `**Last Updated:** 2026-09-16 (v4.115)` | 1 | 1 ✓ |
| `**Last Updated:** 2026-09-16 (v4.114)` | 0 | 0 ✓ |
| `\| 2026-09-16 \| v4.115: Gate 2, thread 336` | 1 | 1 ✓ |
| `\| 2026-09-16 \| v4.114: CEO act at the close of bellows plan 100118` | 1 | 1 ✓ |
| `\| 2026-09-15 \| v4.113: Gate 2, thread 336` | 1 | 1 ✓ |
| `\| 2026-09-15 \| v4.112: Gate 2, thread 336` | 1 | 1 ✓ |
| `## Lifecycle DB Read Protocol (Planner)` | 1 | 1 ✓ |
| `### 38. ` | 1 | 1 ✓ |
| `### 45. ` | 1 | 1 ✓ |
| `### 59. ` | 1 | 1 ✓ |
| `### 81. ` | 1 | 1 ✓ |
| `### 40. ` | 1 | 1 ✓ |
| `### 115. ` | 1 | 1 ✓ |
| `### 14. ` | 3 | 3 ✓ |
| `### 17. ` | 2 | 2 ✓ |

wc -l: 2601 ✓
cmp: silent (byte-identical to scratch output) ✓
git diff --stat: 1 file changed, 21 insertions(+), 2 deletions(-) ✓

Governance commit: `8daabb22` — `[100119] gate2-pt-w30-c: PLANNER_TEMPLATE v4.115 — five extensions (453, 544+462+500, 463+464+480, 520+559, 583), Rule 116 (509)`

## A4 — The Flip

Backup: `/Users/marklehn/Developer/forge_lessons/pre-gate2-pt-w30-c-110100.db` (backup_exit=0)

Backup integrity: `PRAGMA integrity_check` → `ok`
Backup count: live=590 bk=590 (match)
Backup eleven accepted check: 11 ✓

SQL written to: `$GOV/governance/knowledge/development/g2ptw30c-flip.sql`

Run output:
```
PRE_F=11
CHANGES_F=11
EXCL_F=11
ACC_POST=51
IMPL_POST=368
```

Read-back (FRESH read-only connection):
- Eleven rows: all `implemented|codify|ceo|2026-09-16T16:01:18Z` (stamp outside both vintages) ✓
- `accepted` count: 51 ✓
- `implemented` count: 368 ✓
- Capture file: 590 lines ✓
- Eleven capture rows: all show `accepted|codify` (pre-flip state) ✓

flip-capture.txt copied to: `knowledge/qa/evidence/gate2-pt-w30-c-2026-09-15/flip-capture.txt`

SQL commit (governance): `38b93e15` — `[100119] gate2-pt-w30-c: the flip SQL (453, 462, 463, 464, 480, 500, 509, 520, 544, 559, 583 -> implemented)`
