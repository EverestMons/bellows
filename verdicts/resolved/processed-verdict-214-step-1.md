verdict: continue

**Findings accepted. Strong, honest, and correctly decided nothing. All 11 gates PASS.**

## Q1 — the live correctness bug is CONFIRMED, and the Planner reproduced it independently

Not theorised: the agent demonstrated it on a synthetic DB, and I re-ran the exact Gate 8 query from `engines/validator.py:2697` myself against the Contract-1 shape:

```
EIA 6.175 — sentinel row inserted FIRST : 15.0%
EIA 6.175 — sentinel row inserted SECOND: 16.5%
```

**Same query, same data, different answer.** A 1.5-point FSC error selected by physical row order. `LIMIT 1` without `ORDER BY` is not contractual in SQLite, so whenever a `99.999` sentinel is NOT the last bracket, its range `[floor, 99.999)` overlaps every bracket above it and the charged FSC is undefined. **This is a live invoice-correctness bug, not a migration concern** — it exists today, independent of Phase B.

## Q4 — the finding that matters: no option is safe across all three cases

The summary matrix is the real deliverable, and it refutes the tidy answer I was drifting toward ("skip `>= 99.0`"):

| Case | Phase B as-is | Skip sentinel |
|---|---|---|
| Sentinel IS last, no continuation | **Destroys** the unbounded semantic -> validation fails above the narrow ceiling (a REGRESSION from today) | Preserves correctly |
| Sentinel NOT last (Contract 1) | Accidentally fixes the ambiguity | **Preserves a live bug** |

**Skipping is wrong for Contract 1; not skipping is wrong for a legitimate last-bracket sentinel.** Phase B cannot proceed on a blanket rule — it needs to distinguish *intentional* sentinels (last bracket, "and above") from *erroneous* ones (mid-table, copilot error). That distinction is a data question, which is Q2.

Also correctly caught: Phase B as-is fixes Contract 1 **silently** — no log entry, no detection, no human review of whether the unbounded semantic was intentional. A migration that repairs a correctness bug by accident and says nothing is not a repair.

## Q2/Q3 — the right answer was "unknown"

**Q2 correctly refused to generalise from the empty Mac DB** and supplied the exact census SQL for the work machine, with the reason the current report is blind: Queries #1/#4 `INNER JOIN` the next floor, so a sentinel that IS last is filtered out — the only sentinel we can see is visible *because* it is anomalous. **That restraint is the single most valuable behaviour here**; the opposite error is what left the Phase B gate un-satisfiable for eight weeks.

## Q5 — the documentation gap is confirmed

`99.999` appears **only** in `copilot_prompts.py`. Nothing reads it specially. **The sentinel works purely by arithmetic accident** (`99.999 > any real diesel price`) and no code, glossary entry, or blueprint records the intent. Phase B would inherit that — and any future engineer reading `_recompute_fuel_ceilings()` would see a magic number with no explanation.

## Disposition — findings only; no plan may be authored yet

Deposited at `knowledge/research/fuel-sentinel-ceiling-99999-2026-07-16.md`. **Phase B remains blocked**, now on a different and smaller question than the threshold: the sentinel census (Q2). The CEO decides the sequence. Two things are now separable and worth stating plainly:

1. **The Gate 8 ambiguity (Q1) is a live bug that exists today** and does not need Phase B, the census, or the floor-only model to fix — an `ORDER BY price_floor DESC` (narrowest matching bracket wins) is a candidate, but that is a design decision and this diagnostic correctly did not make it.
2. **Phase B's sentinel handling** needs the Q2 census first — the CEO runs the supplied SQL on the work machine, exactly as with the threshold ruling.

Move the plan to `Done/`.
