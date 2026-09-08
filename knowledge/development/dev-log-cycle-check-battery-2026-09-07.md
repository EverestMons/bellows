# Dev Log — cycle_check in-cycle battery (plan 100041)
**Date:** 2026-09-07 / 2026-09-08

## What changed

`scripts/cycle_check.py`: Added an in-cycle quality battery (`run_battery` + `_apply_battery`) that runs on every CONTINUE/BAR_MET exit — thread 117 Ruling 2 shape (a).

`scripts/substrate_check.py` leg 3: Replaced inline fold_baseline lookup with the ONE resolver (`cycle_check.resolve_fold_baseline`).

## Why

### Thread 117 Ruling 2
Battery previously ran only at freeze (`--emit-manifest`). The CEO ruling was that it should run in-cycle so a downgrade is visible at every walk, not just at the close.

### Thread 189 shape (a)
A battery FAIL is a verdict INPUT, not a separate step. The implementation is an inner helper `_apply_battery` that all CONTINUE/BAR_MET exits call; it appends the BATTERY: line and downgrades BAR_MET to CONTINUE when plan_lint has N>0 FAILs or fold_check=DRIFT.

### Thread 190
fold_check rc≠0 previously emitted N/A. Now: rc=0 → PASS, rc=1 → DRIFT, rc=2 → VACUOUS (stdout starts "FOLD-CHECK VACUOUS") or NO_BASELINE. ESCALATE arms are untouched.

### ONE resolver (f15)
`resolve_fold_baseline` is the single source of truth for baseline resolution, used by both `run_battery` and `substrate_check` leg 3. No inline duplication.

## Key design decisions

- **Unconditional battery**: `warnings=None` means BATTERY:/WARN lines have nowhere to go; the verdict is battery-aware regardless (f49).
- **Exactly-once launches**: `emit_manifest` computes `b = run_battery(plan_path)` once, passes `battery=b` to `run_check`. `_apply_battery` uses the pre-computed dict; no second tool launch.
- **ESCALATE exits untouched**: battery adds no subprocess calls on any ESCALATE arm (test 7 confirms).
- **Downgrade vocabulary**: plan_lint N_FAIL (N>0) and fold_check=DRIFT downgrade. VACUOUS/NO_BASELINE/DIVERGENT are informational only.
- **stdout contract (P6)**: BATTERY:/WARN lines precede the verdict. Verdict is always the last line.

## Test work

Created `tests/test_cycle_check_battery.py` with 20 test cases:
- Tests 1-7: battery integration (downgrade conditions, CONTINUE no-downgrade, ESCALATE skip)
- Test 8: emit_manifest fold_check rc mapping
- Test 9: one implementation (no duplicate logic)
- Test 10: baseline resolution order (manifest fold_baseline first, beside-plan fallback)
- Test 11: test_no_subprocess_spawned rewritten in test_cycle_check_manifest_provenance.py (basename-based counting; gate adds zero battery-tool calls beyond baseline)
- Test 12: exactly-once launches (emit_manifest calls each tool exactly once)
- Test 13: one resolver (resolve_fold_baseline called exactly once per run_battery)
- Test 14: CONTINUE exits collect BATTERY: line, no WARN:
- Test 15: verdict independent of call shape (warnings=None vs warnings=[])

Fixed `tests/test_cycle_check.py`:
- Added `_stub_battery` autouse fixture (stubs `run_battery` with clean dict for all in-process tests)
- Fixed `test_assert2_valid_register_no_warn`: changed `len(warnings) == 0` to `not any(w.startswith("WARN:") for w in warnings)` — BATTERY: line is expected, register WARN is not
- Fixed `test_cli_exit_codes`: added lint-clean plan header to bar.md fixture; changed assertion to `r.stdout.strip().splitlines()[-1] == "BAR_MET"` (BATTERY: line precedes verdict)
- Fixed `test_emit_manifest_well_formed`: added lint-clean plan header
- Fixed `test_contract_last_stdout_line_is_verdict`: added lint-clean plan header

Added `_stub_battery` autouse fixture to `tests/test_cycle_check_manifest_provenance.py`.

## Measurement

Full suite: 2055 passed, 1 skipped, 0 failed (66s).

## Mutants written

`knowledge/mutants/cycle-check-battery.json`: 10 mutants covering drop-apply-battery, drop-plan-lint-downgrade, drop-fold-drift-downgrade, battery-on-escalate, fold-check-rc2-discrimination, resolve-fold-baseline logic (manifest and beside), warnings-append, battery-passed, and one-resolver invariant.
