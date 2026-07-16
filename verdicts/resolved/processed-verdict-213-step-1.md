verdict: continue

**Findings accepted with a CORRECTION that the Planner verified against the CEO's real data. The core structural findings stand; one load-bearing factual claim is FALSE and must not propagate into an executable.**

## ❌ CORRECTION — "DHRN has uniform 0.020 steps" is FALSE

Q4 and Q5 both rest on this. Planner measured the actual submitted data (`knowledge/data/pending/data_examples_20260716_104026_826177.json`, the CEO's real DHRN paste):

```
brackets: 31 | first floor: 1.15 | last floor: 1.53
STEP DISTRIBUTION: {0.05: 2, 0.01: 28}   uniform? False   median step: 0.010
first 6 floors: [1.15, 1.2, 1.25, 1.26, 1.27, 1.28]
```

**DHRN steps are NOT uniform and 0.020 appears nowhere in the data.** The table opens with two 50-mill steps (1.150 -> 1.200 -> 1.250) then runs 28 consecutive 10-mill steps.

**Consequences — both conclusions are unsafe as written:**
- **Q4's "the gate is irrelevant for DHRN"** was justified by "DHRN has uniform 0.020 steps -> no gaps to classify." The premise is false, so the conclusion is unsupported as argued. It may still be true for other reasons — it must be re-derived, not inherited.
- **Q5's last-bracket ceiling** `floor + 0.020 - 0.001 = floor + 0.019` is computed from a step size that does not exist. With the real median (0.010) the derived ceiling is `1.539`, not `1.549`.
- **The deeper irony: DHRN is EXACTLY the hazard blueprint v2 §2.2 names** — *"If steps are non-uniform, the median step may not accurately represent the last bracket's intended coverage range."* The diagnostic classified DHRN as the safe uniform case when it is the precise non-uniform case the design flagged. **The one carrier we have real data for is the one the blueprint warned about.**

## ❌ The proposed mitigation is unsound on the derive path

Q5 suggests warning when `next_floor - ceiling > 0.010`. On the derive path `ceiling := next_floor - 0.001` **by construction**, so that delta is always exactly 1 mill and the warning can never fire. It only works for supplied ceilings. In floor-only data a genuine gap manifests as a **floor-step outlier** (e.g. floors 1.25 -> 2.00 against a 0.010 median), not a ceiling delta. Any future mitigation must test step outliers.

## ✅ What stands — and it is the valuable half

These do not depend on the step claim and are well-evidenced:

- **Q1 (the central question): the blueprints do NOT reach the import path.** Confirmed: v2 has zero mentions of `_validate_contract_json`. **Three** validator sites require the ceiling — `contract_import.py:278`, `gap_dashboard.py:2320`, and `gap_dashboard.py:1247` (`_parse_fuel_bracket_csv`, **which the Planner missed**) — plus two INSERT sites that would crash on absence (`contract_import.py:576`, `gap_dashboard.py:2470`, both `float(fb["price_ceiling"])`). Floor-only fixes the read model and leaves the CEO's actual failure site untouched.
- **Q4's separability argument — which REFUTES the Planner's central hypothesis.** I told the CEO "the DHRN fix appears to BE Phase B." The finding shows they are separable: importing new brackets does not run the data migration, so the fix does not require the 10-mill ruling. The gate blocks migrating EXISTING data and authoring `_recompute_fuel_ceilings()`. **That reasoning is sound independent of the step error and is the most useful thing here** — it means the DHRN fix is not blocked on the work-machine export.

## Disposition

Findings deposited at `knowledge/research/dhrn-import-vs-floor-only-phase-b-2026-07-16.md`. **No executable may be authored from Q5 as written** — its last-bracket rule is derived from a non-existent step size, for the one carrier where the blueprint's non-uniform hazard actually applies. The open question is now sharper and genuinely hard: **what SHOULD the last bracket's ceiling be for a non-uniform table?** DHRN's own continuation data (`continuation_start_price: 5.00`) and the unexplained gap between floor `1.530` and `5.00` are the likely key — and the Planner still does not understand that gap.

The CEO decides: re-scope a follow-up on the last-bracket rule, ship only the interior-bracket half (unambiguous: `next_floor - 0.001`, no threshold needed), or wait for the work-machine export to show whether non-uniform tables are typical.

Move the plan to `Done/`.
