# Cycle Manifest Tooling — Dev Log
**Date:** 2026-08-19 | **Plan:** executable-474 (component 2b) | **Step:** 1 (DEV)

## Summary

Implemented two gaps from diagnostic-472's Rule 27 Gap Assessment:
- **(e)** `cycle_check --emit-manifest <plan>` — computes and emits a complete `## Cycle Manifest` stanza to STDOUT
- **(f)** `plan_lint` stanza-shape check — validates a `## Cycle Manifest` stanza if present (non-disruptive: no warn on absence)

## Changes

### `scripts/cycle_check.py`

Added `--emit-manifest` mode that computes four fields from the plan's Drafting Cycle block:
- `walks:` — walk count from walk_data
- `yields:` — per-walk instruction-class series (N/A when class splits not parseable)
- `validation:` — runs cycle_check, plan_lint, and fold_check; encodes results as `checker=verdict` pairs
- `coherence:` — register coverage ratio, or `N/A (no register declared)` for the common register-less plan

Merges authored declarations (`tier`, `target`, `class`, `reads`, `writes`, `open_forks`) from a Planner-prefilled partial `## Cycle Manifest` stanza. Undeclared fields emit `<declare>` placeholder. Tier falls back to the DC block `**Tier:**` line or header `cycle_tier`.

Preserves component 1's invariants: STDOUT only, no file writes, no plan modification. All 27 existing tests pass unchanged.

New functions: `parse_manifest_stanza()`, `_extract_tier_from_plan()`, `_compute_coherence()`, `emit_manifest()`.

### `scripts/plan_lint.py`

Extended check (f) with stanza-shape validation (WARN-only, after the existing DC-block checks):
- All 10 fields present + non-empty
- `class:` ∈ `{read-only, governed-tooling, register-writing}`
- `reads:` non-empty for any plan; `writes:` non-empty for non-read-only plans
- `validation:` contains at least `cycle_check=` and `plan_lint=` entries
- `<declare>` placeholder → WARN (incomplete template)

Presence-optional: plans without a `## Cycle Manifest` stanza produce zero stanza WARNs. Every current stanza-less plan lints identically.

### Tests

**`tests/test_cycle_check.py`** — 5 new tests:
- `test_emit_manifest_well_formed` — 10-field stanza, correct computed fields (walks/yields), tier extraction
- `test_emit_manifest_stdout_only` — plan file byte-unchanged, no new files
- `test_emit_manifest_declare_placeholders` — undeclared authored fields → `<declare>`
- `test_emit_manifest_na_yields_no_class_split` — N/A yields when no class splits
- `test_emit_manifest_coherence_no_register` — coherence N/A when register-less

**`tests/test_plan_lint.py`** — 6 new tests:
- `test_lint_stanza_well_formed_no_warn` — well-formed stanza passes clean
- `test_lint_stanza_missing_field_warns` — missing field → WARN
- `test_lint_stanza_bad_class_warns` — invalid class → WARN
- `test_lint_stanza_empty_reads_warns` — empty reads → WARN
- `test_lint_stanza_declare_placeholder_warns` — `<declare>` → WARN
- `test_lint_stanza_absent_no_warn` — no stanza → no stanza WARN

## Dogfood

```
$ python3 scripts/cycle_check.py --emit-manifest knowledge/decisions/Done/executable-464.md
## Cycle Manifest
tier: T1
target: <declare>
class: <declare>
reads: <declare>
writes: <declare>
open_forks: <declare>
walks: 6
yields: 5, 2, 2, 1, 1, 0
validation: cycle_check=BAR_MET, plan_lint=0_FAIL, fold_check=N/A
coherence: N/A (no register declared)
```

Computed fields match executable-464's known data: 6 walks, yields series 5→2→2→1→1→0, cycle_check=BAR_MET, plan_lint=0_FAIL. Plan file byte-unchanged after run.

## Test Results

- Targeted: `163 passed` (tests/test_cycle_check.py + tests/test_plan_lint.py)
- Full suite: `1153 passed, 0 failed`

## Deposits

- `scripts/cycle_check.py`
- `scripts/plan_lint.py`
- `tests/test_cycle_check.py`
- `tests/test_plan_lint.py`
- `knowledge/development/cycle-manifest-tooling-2026-08-19.md`
