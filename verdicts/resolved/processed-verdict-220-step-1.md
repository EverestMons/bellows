verdict: continue

**Rule 22(b) verified independently by the Planner — helper read, both call sites confirmed, tests run, refactor-safety proven.**

## One source of truth, both paths wired

`fuel_conflict_detection.insert_bracket_or_record_conflict` is framework-free (the lone "web" grep hit is a docstring line — "no web blueprint imports"; no circular-import risk). BOTH import paths call it: `web/gap_dashboard.py:2473` (section) and `web/contract_import.py:571` (JSON). The branching is exactly the plan-219 policy: no existing row → INSERT `contract_fuel_table`, return `inserted`; identical within 0.001 → return `duplicate` (no write); differing → INSERT `fuel_bracket_conflicts` + specific warning, return `conflict`. **Change-nothing is literal** — the conflict branch performs NO `contract_fuel_table` insert or update; the `contract_fuel_table` INSERT is reachable only in the no-existing-row branch.

## The refactor is provably behavior-preserving

The plan-219 regression file `tests/test_fuel_import_conflict.py` is **UNMODIFIED** by this plan (last-touching commit is 219's `1172051`, not a 220 commit) and stays fully green — that is the proof the extraction did not alter section-path behavior. 16 tests pass across the new file + the 219 regression (Planner-run). The intra-payload duplicate test (`test_same_floor_different_value_records_conflict`) is present.

All 11 gates PASS; 5 scoped files; no schema touched (correctly — `fuel_bracket_conflicts` already exists at v18, so no version-pin exposure this time).

## Proceed to Step 2 (QA)

**The plan text already instructs QA: on ANY suite failure beyond the 2 known, REPORT and HALT — do NOT fix product code.** This is the explicit guard against repeating plan 219's QA overstep. Enforce it.

Row 7 baseline is **2220 passed, 2 failed** (the CLAUDE.md pair) plus this plan's 16 — verify actual, never force. Row 4 is the refactor-safety row: confirm `tests/test_fuel_import_conflict.py` shows NO diff and is green. Row 1 (intra-payload) and Row 3 (one source of truth — both paths call the one helper) corroborate the Planner's checks; re-verify rather than inherit.
