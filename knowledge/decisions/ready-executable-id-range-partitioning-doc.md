# bellows — executable: CLAUDE.md gains the multi-machine id-range runbook (CEO option b)

**Date:** 2026-08-26 | **Project:** bellows | **Tier:** Small | **Dispatch Mode:** bellows | **cycle_tier:** T1 | **Test Scope:** none (doc-only append; no code path) | **Execution:** Step 1 (DEV) → Step 2 (QA) | **qa_steps:** 2 | **pause_for_verdict:** always

**auto_close:** false

**Depends on:** the CEO's option-(b) ruling this session; the GLOSSARY.md `id-range partitioning` entry + the baton MINI ACTION (root b48bc04 — the DEFINITION and the act; this plan is the RUNBOOK half per the glossary discriminator); the measured collision (mini ids 1/2 overwrote shop processed-verdict-1/2).

## Why this exists

The law needs an operative home agents actually read when touching lifecycle.db on any machine. The glossary defines it; CLAUDE.md instructs it.

## Numbers discipline

⚠️ **Measured 2026-08-26 at authoring; Step 1 re-derives — yours supersede.**

| id | pin | value | anchor |
|---|---|---|---|
| S1 | CLAUDE.md | sha-prefix `2d689d5943bbd8cf3b79`; the append is EOF-pure (no anchor consumed) | `CLAUDE.md` (repo-relative — worktree law) |
| S2 | id_sequence | 555 (shop block 1–99999 holds comfortably) | `lifecycle.db` (read-only) |

## STEP 1 — DEV (EOF append + commit)

> **Task A — worktree discipline + state branch.** ⚠️ Your cwd IS the claimed tree — never cd to `/Users/marklehn/Developer/GitHub/bellows`. Open: `cd "$(git rev-parse --show-toplevel)" && test -f CLAUDE.md && echo TREE_OK` — HALT unless TREE_OK. Probe: `/usr/bin/grep -cF -- "Multi-machine id ranges" CLAUDE.md; true` — 0 → run Task B; 1 → skip to Task C's commit-check.
>
> **Task B — append EXACTLY this section at EOF** (python, RELATIVE path; pre-write assert: the probe above still 0 AND the file's sha256 prefix matches S1 — SystemExit otherwise; append `"\n" +` the block):
>
> ```
>
> ## Multi-machine id ranges (CEO ruling 2026-08-26 — option b)
>
> Every machine mints plan ids from ITS OWN `lifecycle.db` `id_sequence`, and
> every post-claim artifact (verdict files, `Done/executable-<id>.md`, step
> logs) is keyed by that id in SHARED git namespaces. Two machines minting
> from overlapping ranges WILL collide — measured 2026-08-26: the mini's ids
> 1/2 overwrote the shop's historic `processed-verdict-1/2` files.
>
> **The law:** each machine's `id_sequence` is seeded ONCE into a disjoint
> 100000-block. Shop machine: 1–99999 (historical, continues in place).
> Mac mini: 100000–199999 (seed: `UPDATE id_sequence SET next_id = 100000;`
> on ITS database, daemon stopped or between claims). Each next machine takes
> the next block; allocation is recorded in the tuyere machine registry once
> it ships. NEVER re-seed a machine that has already minted in its block, and
> never seed into another machine's block — the seeding is one-time, per
> machine, on that machine.
>
> The claim rename and all downstream naming are UNCHANGED by this law —
> disjoint ranges make collisions arithmetically impossible without touching
> code. Definition: the central `GLOSSARY.md` `id-range partitioning` entry.
> ```
>
> Post-probes: `"Multi-machine id ranges"` == 1 AND `"100000-block"` == 1 AND `"NEVER re-seed"` == 1; MEASURE and RECORD `wc -l CLAUDE.md`.
>
> **Task C — dev note + commit.** `knowledge/dev-logs/id-range-partitioning-doc-dev-2026-08-26.md` (probe raws, recorded wc -l). Commit (WORKTREE toplevel): `cd "$(git rev-parse --show-toplevel)" && git add CLAUDE.md knowledge/dev-logs/id-range-partitioning-doc-dev-2026-08-26.md && git commit -m "[<id from your plan filename>] id-range-partitioning-doc(id-range-partitioning-doc-2026-08-26): CLAUDE.md multi-machine id-range runbook (CEO option b)" -- CLAUDE.md knowledge/dev-logs/id-range-partitioning-doc-dev-2026-08-26.md && git rev-parse HEAD` — **CAPTURE_COMMIT**; separate: numstat — exactly the two files, CLAUDE.md all-added.
>
> **Deposits:**
> - `CLAUDE.md`
> - `knowledge/dev-logs/id-range-partitioning-doc-dev-2026-08-26.md`
>
> **Scope:**
> - `CLAUDE.md`
> - `knowledge/dev-logs/id-range-partitioning-doc-dev-2026-08-26.md`

## STEP 2 — QA (committed extraction)

> **Item 1 — probes on `git show <CAPTURE_COMMIT>:CLAUDE.md`** (⚠️ braced `${VAR}:path`): the three Task-B probes == 1 each; the append is PURE (the pre-existing tail `Recommended cadence: at session-wrap or weekly.` still count-1 and every pre-existing section heading unchanged — compare `git show <CAPTURE_COMMIT>^:CLAUDE.md` line count + the new: old + section length == recorded `wc -l`); `cmp` vs live → 0. Raw → `knowledge/qa/evidence/id-range-partitioning-doc-2026-08-26/probes-raw.txt`.
> **Item 2 — cross-artifact coherence.** `/usr/bin/grep -cF "id-range partitioning" /Users/marklehn/Developer/GitHub/GLOSSARY.md` >= 1 AND the baton MINI ACTION line present (`/usr/bin/grep -cF "seed its" /Users/marklehn/Developer/GitHub/shop_next_session.md` >= 1) — the three homes agree (paste raws).
> **Item 3 — hygiene + receipt** `knowledge/qa/evidence/id-range-partitioning-doc-2026-08-26/qa-receipt.md`: numstat 2 files; toplevel; reflog `-n 4` → 0 amends; per-item table + the Rule 20 block.
>
> ⚠️ **Gate note (pre-declared):** probe-battery QA, no pytest scope — the benign class (17th precedent); Planner overrides with reference here.
>
> **Deposits:**
> - `knowledge/qa/evidence/id-range-partitioning-doc-2026-08-26/probes-raw.txt`
> - `knowledge/qa/evidence/id-range-partitioning-doc-2026-08-26/qa-receipt.md`
>
> **Scope:**
> - `knowledge/qa/evidence/id-range-partitioning-doc-2026-08-26/probes-raw.txt`
> - `knowledge/qa/evidence/id-range-partitioning-doc-2026-08-26/qa-receipt.md`

Rule 20 banner (byte-exact, inside the QA receipt's verification section):

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
```

## Drafting Cycle

**Tier:** T1 — one EOF-pure doc append; the three-home coherence (glossary DEFINITION, CLAUDE.md RUNBOOK, baton ACT) is the QA spine.

**Walk register:** `bellows/knowledge/research/walk-register-id-range-partitioning-doc-2026-08-26.md`

**Walk 0 (context pin, measured):** CLAUDE.md sha pinned; append EOF-pure; id_sequence 555; the measured collision cited; the glossary/baton halves already landed at b48bc04.

**Walks:**
- Weak spots:          w1 dry — probes earnable; the EOF-pure append asserted by line arithmetic (old + block == recorded) rather than a consumed anchor; sha pre-write guard covers concurrent edits.
- Destruction:         w1 dry — two-arm resume (probe 0/1); all writes one commit; a death pre-commit re-runs cleanly (the sha guard branches to the probe arm).
- Vulnerabilities:     w1 dry — the NEVER-re-seed and never-into-another's-block clauses close the two misuse arms of the seeding act; the act itself stays on the owning machine.
- Integration-record:  w1 dry — three-home coherence is a QA item (glossary DEFINITION, this RUNBOOK, the baton ACT); the registry-as-allocator deferred to the mini's live arc, declared.
- ACID:                w1 dry — one pathspec-limited pinned commit, all-added numstat.
- **Walk 1 total: 0 findings — all five lenses dry (a pure append with landed siblings; the standard arms pre-fitted).**
- Weak spots:          w2 dry.
- Destruction:         w2 dry.
- Vulnerabilities:     w2 dry.
- Integration-record:  w2 dry.
- ACID:                w2 dry.
- **Walk 2 total: 0 findings — all five lenses dry.**

**Closing:** ✅ **BAR MET at walk 2 — dry confirming pass, all five lenses.** T1 two-walk form; no direction-class finding; close is MANUAL (CEO-lane verdicts).

**Fold-and-deposit exactly once.**

## Cycle Manifest
tier: T1
target: bellows/CLAUDE.md
class: shop-infra
reads: /Users/marklehn/Developer/GitHub/bellows/CLAUDE.md, /Users/marklehn/Developer/GitHub/GLOSSARY.md, /Users/marklehn/Developer/GitHub/shop_next_session.md
writes: CLAUDE.md, knowledge/dev-logs/id-range-partitioning-doc-dev-2026-08-26.md, knowledge/qa/evidence/id-range-partitioning-doc-2026-08-26/probes-raw.txt, knowledge/qa/evidence/id-range-partitioning-doc-2026-08-26/qa-receipt.md
open_forks: the mini's one-time seeding act (baton MINI ACTION — the mini's next session); the registry-as-allocator integration (rides the mini's machine-registry arc)
walks: 2
yields: 0, 0
validation: cycle_check=BAR_MET, plan_lint=0_FAIL, fold_check=N/A
coherence: N/A
