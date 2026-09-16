# Dev Log — gate2-pt-w30-f-2026-09-16 (plan 100122)

## A0 — Branch Determination

**FRESH arm.**

- TREE_OK: bellows.py and tests/ present in worktree root.
- GOV_OK: PT, builder, and DB all exist at absolute paths.
- P8 unconditional: lesson_entries=580 ✓; forge-cycle-w31 count=0 ✓.
- Ladder (1): sha=`fa7f800a63abe875` = P1 ✓
- Ladder (2): porcelain EMPTY ✓
- Ladder (3): last commit subject does NOT carry `gate2-pt-w30-f` ✓
- Ladder (4): eight rows all `accepted|codify` at their vintages (444@`2026-09-02T23:54:37Z`, 474/489/513/518/538/567/587@`2026-09-13T18:27:07Z`) ✓
- Ladder (5): `25|25` ✓
- → **FRESH**

## A1 — Pins Re-derived

| pin | value | expected | match |
|---|---|---|---|
| P1 sha | `fa7f800a63abe875` | `fa7f800a63abe875` | ✓ |
| P1 lines | 2639 | 2639 | ✓ |
| P1 bytes | 591416 | 591416 | ✓ |
| P2 anchors | all 10 count=1 | all 1 | ✓ |
| P3 zero-tokens | all 14 pre-tokens count=0 | all 0 | ✓ |
| P4 on-disk digest | `a03e802789dd5462` | `a03e802789dd5462` | ✓ |
| P4 blob at `59c2ec28` | `a03e802789dd5462` | `a03e802789dd5462` | ✓ |
| P6 eight rows | all `accepted\|codify` at vintages | as stated | ✓ |
| P6 accepted | 25 | 25 | ✓ |
| P6 implemented | 394 | 394 | ✓ |
| P6 vintage groups | `2026-09-02T23:54:37Z\|8` and `2026-09-13T18:27:07Z\|17` | two rows only | ✓ |
| P6 max_id\|total | `590\|590` | `590\|590` | ✓ |

## A2 — Dry Run

- Builder output: `BUILT: /tmp/g2ptw30f/PT-out.md edits=10 blocks=1 lines+29 bytes+14485 post=47/47 deltas=pinned`
- `builder_exit=0`
- numstat: `31	2` (exit 1 expected) ✓
- `wc -l`: 2668 ✓
- `wc -c`: 605901 ✓

Refusals (all `BUILDER REFUSED`, nonzero exit):
1. out==in: `BUILDER REFUSED: out == in` ✓
2. under forbidden root: `BUILDER REFUSED: out is under a forbidden root /Users/marklehn/Developer/eluvian-governance (the literal governance root, or the input's git toplevel)` ✓
3. already built: `BUILDER REFUSED: output tokens already present in input — already built?` ✓

## A3 — Apply and Commit

Task C counts (47/47 on the live file):
- `### 119. A check on a single-home store carries the home in its contract` → 1 ✓
- `### 120. The visibility of a bookkeeping failure is a property of WHERE it is written` → 1 ✓
- `**Rule 119 — a single-home store's check carries the home**` → 1 ✓
- `**Rule 120 — a failure the operator must act on is written where a gate looks**` → 1 ✓
- `codified 2026-09-16 (Gate 2, thread 336 — PT tranche six)` → 2 ✓
- `codified 2026-09-16 — Gate 2, thread 336, PT tranche six` → 6 ✓
- `**A precondition read before the re-entry ladder never depends on state the plan's own steps move` → 1 ✓
- `**A QA step ASSEMBLES pinned fixtures — it never designs them` → 1 ✓
- `**Size a divergence by the exact-file intersection of the two \`--name-only\` sets` → 1 ✓
- `**The evidence an instrument repair owes names the real artifact whose verdict the repair should move` → 1 ✓
- `**A table's key is only as fine as the context that wrote it` → 1 ✓
- `**A copy of live state includes the process that took it` → 1 ✓
- `**Version:** 4.118` → 1 ✓
- `**Version:** 4.117` → 0 ✓
- `**Last Updated:** 2026-09-16 (v4.118)` → 1 ✓
- `**Last Updated:** 2026-09-16 (v4.117)` → 0 ✓
- `| 2026-09-16 | v4.118: Gate 2, thread 336` → 1 ✓
- `| 2026-09-16 | v4.117: Gate 2, thread 336` → 1 ✓
- `| 2026-09-16 | v4.116: Gate 2, thread 336` → 1 ✓
- `| 2026-09-16 | v4.115: Gate 2, thread 336` → 1 ✓
- `| 2026-09-16 | v4.114: CEO act at the close of bellows plan 100118` → 1 ✓
- `| 2026-09-15 | v4.113: Gate 2, thread 336` → 1 ✓
- `| 2026-09-15 | v4.112: Gate 2, thread 336` → 1 ✓
- `## Lifecycle DB Read Protocol (Planner)` → 1 ✓
- `**Canonical queries.**` → 1 ✓
- `### pause_for_verdict Header Field` → 1 ✓
- `**Net-zero-cost failures still warrant correction.**` → 1 ✓
- `### The self-repair exemption` → 1 ✓
- `### 35. ` → 1 ✓
- `### 56. ` → 1 ✓
- `### 57. ` → 1 ✓
- `### 84. ` → 1 ✓
- `### 85. ` → 1 ✓
- `### 99. ` → 1 ✓
- `### 105. ` → 1 ✓
- `### 118. ` → 1 ✓
- `### 119. ` → 1 ✓
- `### 120. ` → 1 ✓
- `### 121. ` → 0 ✓
- `#### 11. ` → 1 ✓
- `#### 12. ` → 1 ✓
- `#### 15. ` → 1 ✓
- `#### 16. ` → 0 ✓
- `### 14. ` → 3 ✓
- `### 17. ` → 2 ✓
- `Source: proposal 78, lesson 2026-05-27` → 1 ✓
- `*Source: proposals 576 and 581, entries 568 and 573 (2026-09-11, 2026-09-12), codified 2026-09-16 (Gate 2, thread 336 — PT tranche five)*` → 1 ✓

wc -l: 2668 ✓; cmp byte-identical ✓; git diff --stat: 31 insertions, 2 deletions ✓

Governance commit: `3d2dbaf5`

## A4 — Flip

Backup: `/Users/marklehn/Developer/forge_lessons/pre-gate2-pt-w30-f-150649.db`
- `PRAGMA integrity_check` → `ok` ✓
- backup total rows: 590 (equals live) ✓
- BK=8 (eight target rows `accepted`) ✓

Flip run sentinels:
- `PRE_F=8` ✓
- `CHANGES_F=8` ✓
- `EXCL_F=8` ✓
- `ACC_POST=17` ✓
- `IMPL_POST=402` ✓

Read-back (fresh read-only connection):
- Eight rows: `implemented|codify|ceo|2026-09-16T20:07:10Z` (stamp outside both vintages) ✓
- accepted=17 ✓
- seventeen at vintages ✓
- implemented=402 ✓
- capture file: 590 lines ✓
- capture pre-flip accepted|codify rows: 25 ✓
- Eight capture rows for target ids all `|accepted|codify|` (pre-flip state) ✓

SQL governance commit: `5e090284`
