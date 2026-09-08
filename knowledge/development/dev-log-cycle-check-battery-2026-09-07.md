# Dev Log — cycle-check-battery (plan 100042, 2026-09-07)

**Plan:** 100042-step-1-battery
**Branch:** bellows-wt/100042
**Date:** 2026-09-08

---

## P10 Blast Radius

P10 = the four CONTINUE/BAR_MET return sites inside `run_check`. Every site
that previously returned a bare `"CONTINUE"` or `"BAR_MET"` string now calls
`_apply_battery(plan_path, verdict, warnings, battery=battery)`. ESCALATE
arms are untouched.

Files modified:

| file | change |
|------|--------|
| `scripts/cycle_check.py` | +3 functions (`resolve_fold_baseline`, `run_battery`, `_apply_battery`); 4 return sites updated; `emit_manifest` private subprocess blocks replaced with single `run_battery` call; `run_check` signature: `battery=None` kwarg |
| `scripts/substrate_check.py` | Leg 3 rewritten to call `cycle_check.resolve_fold_baseline` instead of its own inline baseline logic |
| `tests/test_cycle_check_battery.py` | New file, 16 tests |
| `tests/test_cycle_check.py` | `_make_plan` / `_build_ss_plan` / 2 fixtures updated for plan_lint compliance; 2 assertions adapted to P8 multi-line stdout |
| `tests/test_cycle_check_manifest_provenance.py` | 3 helpers updated for plan_lint compliance; `test_no_subprocess_spawned` rewritten — ruling 189 |
| `knowledge/mutants/cycle-check-battery.json` | New, 4 mutants |
| `knowledge/mutants/cycle-check-battery.run.txt` | New, mutation run output |

No other scripts import `cycle_check._apply_battery` or `cycle_check.run_battery` —
blast radius is entirely contained in the two scripts files and their test files.

---

## Cost Before / After

Measured on a BAR_MET plan with a complete Cycle Manifest, no fold baseline,
no walk register (propagation_check returns NOT_RUN, fold_check returns
NO_BASELINE without launching a subprocess):

| run | before (HEAD~) | after |
|-----|----------------|-------|
| 1 | 0.050 s | 0.127 s |
| 2 | 0.060 s | 0.099 s |
| 3 | 0.068 s | 0.099 s |

Delta: ~0.03–0.06 s per invocation. Two subprocesses launch for a plan
without a fold baseline (`plan_lint.py` + `propagation_check.py`); a plan
with a baseline adds a third (`fold_check.py`). `resolve_fold_baseline`
checks the beside-plan path with `Path.exists()` — zero subprocess overhead
when no baseline file is found.

Daemon impact: `emit_manifest` previously launched plan_lint + fold_check +
propagation_check with its own subprocess blocks; it now calls `run_battery`
once and passes `battery=b` to `run_check` to avoid a second launch. Total
subprocess count at deposit time is unchanged: 3 (or 2 without baseline).

---

## P8 Overturned Clause

P8 (plan 100033, DC:253): "verdict is always the ONLY stdout line emitted by
cycle_check."

Ruling 189 overturns the ONLY clause. The new contract (P8 amendment):
**verdict is always the LAST stdout line**; it may be preceded by
`BATTERY: plan_lint=… fold_check=… propagation_check=…` and zero or more
`WARN: …` lines when a downgrade occurs.

ESCALATE exits are exempt: no BATTERY line, no WARN lines, single-line
stdout.

Test coverage of the new contract:
- `test_battery_line_printed_before_verdict` — BATTERY precedes BAR_MET
- `test_contract_last_stdout_line_is_verdict` (test_cycle_check.py) — adapted to `splitlines()[-1]`
- `test_cli_exit_codes` — same adaptation

---

## Mutation Run

See `knowledge/mutants/cycle-check-battery.run.txt` for raw output.

Four mutants targeting the battery integration:

| mutant | anchor | expect_fail | result |
|--------|--------|-------------|--------|
| M1-drop-plan-lint-downgrade | removes `plan_lint_fail` branch | `test_bar_met_plan_lint_fail_downgrades` | KILLED |
| M2-drop-fold-drift-downgrade | removes `fold_drift` branch | `test_bar_met_fold_check_drift_downgrades` | KILLED |
| M3-always-launch-fold-check | removes `if baseline_path is not None` guard | `test_bar_met_no_baseline_unaffected` | KILLED |
| M4-suppress-battery-line-for-continue | gates BATTERY: line on `verdict=="BAR_MET"` | `test_continue_plan_lint_fail_no_downgrade_warn` | KILLED |

Result: 4 killed, 0 survived, 0 error. Full output in `cycle-check-battery.run.txt`.
