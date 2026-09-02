# Dev Log — checker-kill-gap-2026-09-02

**Plan:** 100025 | **Step:** 1 (DEV) | **Date:** 2026-09-02

## P1 — SHAs (re-derived at claim; propagation-check-pin-forms wrote cycle_check.py and test_cycle_check.py)

| file | sha256[:16] | note |
|---|---|---|
| `scripts/cycle_check.py` | `12c23a3345a88e96` | differs from plan table — 100023 wrote this file |
| `tests/test_cycle_check.py` | `b57060de1037d308` | differs from plan table — 100023 wrote this file |
| `knowledge/mutants/checker-defects-cycle_check.json` | `12c9fc2940d812f0` | matches plan table |

## P2 — Four checker test files (pre-edit)

```
317 passed in 8.83s
```

(Plan expected 316 + whatever 100023 added = 317.)

## P3 — Kill map before (four manifests)

```
=== checker-defects-cycle_check ===
MUTANT M1-drop-walk-signal-guard: KILLED — suite caught the defect
MUTANT M2-drop-negation-stripping: SURVIVED — suite does not discriminate this defect
MUTANT M3-drop-oserror-guard: SURVIVED — suite does not discriminate this defect
MUTANT M4-accept-unresolved-as-ok: KILLED — suite caught the defect
MUTATION: 2 killed, 2 survived, 0 error

=== checker-defects-cycle_yields ===
MUTANT M5-revert-weakspots-prefix: KILLED — suite caught the defect
MUTATION: 1 killed, 0 survived, 0 error

=== checker-defects-plan_lint ===
MUTANT M6-revert-lint-weakspots-pattern: KILLED — suite caught the defect
MUTANT M7-invert-receipt-first-check: KILLED — suite caught the defect
MUTATION: 2 killed, 0 survived, 0 error

=== propagation-check.json ===
ERROR: manifest must have 'target' and non-empty 'mutants'
```

Exactly M2 and M3 SURVIVED; propagation-check.json REFUSED.

## P3b — Four propagation mutant anchors and selectors

Each anchor occurs exactly once in its target. Four selectors: `4 passed`.

| mutant | target | expect_fail |
|---|---|---|
| M1-hex-exclusion-removed | scripts/propagation_check.py | tests/test_propagation_check.py::test_hex_excluded |
| M2-row-id-fallback-removed | scripts/propagation_check.py | tests/test_propagation_check.py::test_row_id_symbol |
| M3-judge-propagation-rc2-as-pass | tools/run_check.py | tests/test_run_check.py::TestJudgePropagation::test_not_run_fail |
| M4-manifest-propagation-pair-dropped | scripts/cycle_check.py | tests/test_cycle_check.py::test_emit_manifest_propagation_field |

## P4 — Discrimination proof (six fixture runs)

Mutants applied to scratch copies at `/tmp/ckg/m2/` and `/tmp/ckg/m3/`.
- M2 anchor occurred exactly 1 time; M3 anchor occurred exactly 1 time.

| fixture | live | M2 copy | M3 copy |
|---|---|---|---|
| negclaim (no register line, plain dir) | CONTINUE | ESCALATE:claimed-close-unmet | CONTINUE |
| longref3 (git root with scripts/) | ESCALATE:assert-fail:2 | ESCALATE:assert-fail:2 | OSError: [Errno 63] File name too long |

Each fixture flips exactly its own mutant. Matches P4 exactly.

## P5 — Full suite (pre-edit)

```
1812 passed, 1 skipped in 51.11s
```

## P6 — Anchors in manifest (each exactly once)

```
tests/test_cycle_check.py::test_58_not_closed_returns_continue — count: 1
tests/test_cycle_check.py::test_c2_long_component_no_traceback — count: 1
```

## A3 — Two new node IDs

- `tests/test_cycle_check.py::test_58_negated_claim_phrase_stripped_continue`
- `tests/test_cycle_check.py::test_c2_oversized_backticked_ref_escalates_no_traceback`

Four-checker targeted run after F1: `319 passed` (317 + 2).

## F3 — Multiset proof (propagation manifest split)

```
Written: knowledge/mutants/propagation-check-propagation_check.json  (2 mutants)
Written: knowledge/mutants/propagation-check-run_check.json  (1 mutants)
Written: knowledge/mutants/propagation-check-cycle_check.json  (1 mutants)

Multiset proof: IDENTICAL
  4 mutants in old, 4 in new three files
Target keys verified: each new file's target equals the dropped per-mutant target
```

## Full suite (post-edit)

```
1814 passed, 1 skipped in 50.60s
```

P5 + 2 = 1814. Exit 0.

## Status: Complete
