# Dev Log — gate2-pt-w30-e-2026-09-16 (plan #100121)

## A0 — Branch determination

**P8 unconditional:** `lesson_entries` → 580 ✓; `forge-cycle-w31` count → 0 ✓

**Ladder:**
- (1) SHA `23969632693f592c` — matches P1 ✓
- (2) porcelain EMPTY ✓
- (3) last commit subject does NOT carry `gate2-pt-w30-e` (it is `gate2-pt-w30-d`) ✓
- (4) eleven rows all `accepted|codify` at vintages (447/456/459 at `2026-09-02T23:54:37Z`; 497/517/527/546/573/576/581/582 at `2026-09-13T18:27:07Z`) ✓
- (5) `36|36` ✓

**Determination: FRESH → A1**

## A1 — Pins re-derived

| pin | value | matches |
|-----|-------|---------|
| P1 sha | `23969632693f592c` | ✓ |
| P1 lines | 2624 | ✓ |
| P1 bytes | 578618 | ✓ |
| P2 anchors | all 6 count = 1 | ✓ |
| P3 new tokens | all 0 before | ✓ |
| P3 invariants | ### 55./56./105./106./116./117. = 1; ### 14. = 3; ### 17. = 2; Restart Discipline = 1; Dispatch Path Rules = 1; Rule 105 Source = 1; Rule 117 Source = 1 | ✓ |
| P4 on-disk | `cba5026c71ba6f99` | ✓ |
| P4 blob at 668fcaf0 | `cba5026c71ba6f99` | ✓ |
| P6 eleven rows | all `accepted\|codify` at vintages | ✓ |
| P6 accepted | 36 | ✓ |
| P6 implemented | 383 | ✓ |
| P6 stamps | exactly `2026-09-02T23:54:37Z\|11` and `2026-09-13T18:27:07Z\|25` | ✓ |
| P6 MAX(id)/COUNT(*) | 590\|590 | ✓ |

## A2 — Dry-run

```
BUILT: /tmp/g2ptw30e/PT-out.md edits=7 blocks=1 lines+15 bytes+12798 post=30/30 deltas=pinned
builder_exit=0
```

numstat: `17  2` ✓  
wc -l: 2639 ✓  
wc -c: 591416 ✓

**Refusal 1 (out == in):** `BUILDER REFUSED: out == in` ✓  
**Refusal 2 (forbidden root):** `BUILDER REFUSED: out is under a forbidden root /Users/marklehn/Developer/eluvian-governance (the literal governance root, or the input's git toplevel)` ✓  
**Refusal 3 (already built):** `BUILDER REFUSED: output tokens already present in input — already built?` ✓

## A3 — Apply and Task C counts

Applied `cp /tmp/g2ptw30e/PT-out.md "$GOV/PLANNER_TEMPLATE.md"`. Task C (30 probes on live file):

| token | count |
|-------|-------|
| `### 118. The interpreter is a PIN` | 1 |
| `**Rule 118 — the interpreter is a PIN` | 1 |
| Rule 117 Source | 1 |
| Rule 105 Source | 1 |
| `**The dispatch environment has four more axes the process tree does not name` | 1 |
| `**A restart is proven by the process's own facts and a canary through the changed path` | 1 |
| `**A liveness test reads a signal the death REMOVES` | 1 |
| `codified 2026-09-16 — Gate 2, thread 336, PT tranche five` | 3 |
| `codified 2026-09-16 (Gate 2, thread 336 — PT tranche five)` | 1 |
| `**Version:** 4.117` | 1 |
| `**Version:** 4.116` | 0 |
| `**Last Updated:** 2026-09-16 (v4.117)` | 1 |
| `**Last Updated:** 2026-09-16 (v4.116)` | 0 |
| `\| 2026-09-16 \| v4.117: Gate 2, thread 336` | 1 |
| `\| 2026-09-16 \| v4.116: Gate 2, thread 336` | 1 |
| `\| 2026-09-16 \| v4.115: Gate 2, thread 336` | 1 |
| `\| 2026-09-16 \| v4.114: CEO act at the close of bellows plan 100118` | 1 |
| `\| 2026-09-15 \| v4.113: Gate 2, thread 336` | 1 |
| `\| 2026-09-15 \| v4.112: Gate 2, thread 336` | 1 |
| `## Lifecycle DB Read Protocol (Planner)` | 1 |
| `### Restart Discipline` | 1 |
| `### Dispatch Path Rules` | 1 |
| `### 55. ` | 1 |
| `### 56. ` | 1 |
| `### 105. ` | 1 |
| `### 106. ` | 1 |
| `### 116. ` | 1 |
| `### 117. ` | 1 |
| `### 14. ` | 3 |
| `### 17. ` | 2 |

wc -l: 2639 ✓  
cmp: CMP_SILENT ✓  
diff --stat: 17 insertions, 2 deletions ✓

**Governance commit:** `0f5c34bd` — `[100121] gate2-pt-w30-e: PLANNER_TEMPLATE v4.117 — three extensions (447+517+527+546, 459+497+573+456, 582), Rule 118 (576+581)`

## A4 — Flip

**Backup:** `/Users/marklehn/Developer/forge_lessons/pre-gate2-pt-w30-e-141151.db`  
backup_exit=0; integrity_check: ok; live count 590 = backup count 590; BK=11 ✓

**Sentinels:**
```
PRE_F=11
CHANGES_F=11
EXCL_F=11
ACC_POST=25
IMPL_POST=394
```

**Read-back (fresh read-only):**
- Eleven rows: all `implemented|codify|ceo|2026-09-16T19:12:15Z` (stamp outside the two vintages) ✓
- accepted = 25 ✓
- implemented = 394 ✓
- capture: 590 lines, 36 rows containing `|accepted|codify|` ✓

**SQL commit:** `80a30fe2` — `[100121] gate2-pt-w30-e: the flip SQL (447, 456, 459, 497, 517, 527, 546, 573, 576, 581, 582 -> implemented)`
