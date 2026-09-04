# Dev log — diagnostic-drafting-battery-cost (plan 100032)

**Date:** 2026-09-03  
**Plan:** `knowledge/decisions/drafts/diagnostic-drafting-battery-cost.md`  
**Tier:** T1

## What was built

Three files:
1. `tools/battery_census.py` — read-only instrument over the 163-file walk-register corpus
2. `governance/knowledge/research/drafting-battery-cost-2026-09-03.md` — research doc answering Q1–Q6
3. This dev log

## Instrument design notes

`battery_census.py` imports `walk_register_lint` (the shipped parser) and adds a shim for the `sub_q → sub_question` gap (disclosed at walk 4, not fixed here — needs its own plan). Table columns are indexed by header name, not position, per P2's finding that nine-plus distinct header shapes exist in the corpus.

Battery detection uses regex patterns over backtick-quoted tool names followed by machine output tokens (exit codes, verdict strings). `verbatim` requires a quoted name with an adjacent literal output; `paraphrase` requires only the tool name; `not_recorded` means the name is absent.

Lifecycle state is looked up from `lifecycle.db` via the `**Plan:**` line's filename.

## P1–P8 mismatches

P1: corpus is 163 (not 162) — this plan's register was committed after the pin was set.

P3: session fold rates all differ because registers were still being written when P3 was pinned at Walk 0. The gate2-dc-w28 register grew from ~10 rows to 36 rows during the diagnostic.

P4: u-qa-predicate-align completed with 18 walks/108 rows vs pinned 17/89 — cycle continued after the pin.

P7 PLANNER_TEMPLATE bullets: measured 200, pinned 202. Word counts match at 67,325/70,162 (Python split, not wc -w).

## Key findings from the instrument run

- Battery recording rate jumped from 2–49% per tool in August to 31–96% in September.
- fold_check and mutation_check are never quoted verbatim in any register.
- cycle_check is verbatim in only 5/47 recorded instances.
- Per-lens commit compliance: 80% (fresh agent), 8–20% (Planner).
- At mandated cadence (45 invocations/cycle), battery costs ~16s wall time. At observed Planner cadence (~3), it costs ~1s.
- The most common fold-introduced class (incomplete propagation, 75% of this cycle's folds) is the class propagation_check is least able to detect.

## numstat

3 writes: `tools/battery_census.py`, `governance/knowledge/research/drafting-battery-cost-2026-09-03.md`, `knowledge/development/dev-log-drafting-battery-cost-2026-09-03.md`.
