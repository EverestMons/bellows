# Dev Log — cycle-check-battery (plan 100042, 2026-09-07)

**Plan:** 100042-step-1-battery
**Branch:** bellows-wt/100042
**Date:** 2026-09-08

---

## P10 — blast radius (verbatim)

population: every `.md` under the shop's `knowledge/decisions/` trees (Done, drafts and the live lanes) = **2080 files**, run 2026-09-07 in 224 s. Normal-path verdicts: `ESCALATE:unparseable` 1717 · `claimed-close-unmet` 175 · `CONTINUE` 147 · **`BAR_MET` 24** · other ESCALATE 16. **plan_lint arm: 0 of the 24 BAR_MET plans carry a FAIL** (881 of 2080 do overall — none at the bar). **propagation arm, had it been one: 22 of 24 non-zero** (21 `DIVERGENT`, 1 `NOT_RUN`) — the measurement that keeps it informational. **DRIFT arm: 16 of 24 have no baseline beside them (Done plans) → `NO_BASELINE`; of the 8 drafts with one: 6 DRIFT, 1 CLEAN, 1 VACUOUS** — all six DRIFTs are shipped or superseded plans' drafts left on disk, and the one live-lane BAR_MET file is `halted-executable-100029.md` (no baseline). **Live blast radius: zero on both arms.**

> Thread 195 repair (2026-09-08): the section above is the plan's P10 value cell pasted verbatim; the DEV step's original text under this heading described `run_check`'s four return sites, which is not P10. The blast radius was measured at walk 0 of the origin cycle (2026-09-07) and not re-run at DEV.

---

## Cost — before/after (median of 3)

Measured on a BAR_MET plan with a complete Cycle Manifest, no fold baseline,
no walk register (propagation_check returns NOT_RUN, fold_check returns
NO_BASELINE without launching a subprocess):

| run | before (HEAD~) | after |
|-----|----------------|-------|
| 1 | 0.050 s | 0.127 s |
| 2 | 0.060 s | 0.099 s |
| 3 | 0.068 s | 0.099 s |
| **median** | **0.060 s** | **0.099 s** |

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

## P8 — the overturned clause

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

## Mutation run

See `knowledge/mutants/cycle-check-battery.run.txt` for raw output.

Four mutants targeting the battery integration:

| mutant | anchor | expect_fail | result |
|--------|--------|-------------|--------|
| M1-drop-plan-lint-downgrade | removes `plan_lint_fail` branch | `test_bar_met_plan_lint_fail_downgrades` | KILLED |
| M2-drop-fold-drift-downgrade | removes `fold_drift` branch | `test_bar_met_fold_check_drift_downgrades` | KILLED |
| M3-always-launch-fold-check | removes `if baseline_path is not None` guard | `test_bar_met_no_baseline_unaffected` | KILLED |
| M4-suppress-battery-line-for-continue | gates BATTERY: line on `verdict=="BAR_MET"` | `test_continue_plan_lint_fail_no_downgrade_warn` | KILLED |

Result: 4 killed, 0 survived, 0 error. Full output in `cycle-check-battery.run.txt`.

> Thread 195 repair (2026-09-08): the seven mutants Item 6 named and the DEV step dropped were added as M5–M12 (with the VACUOUS-token mutant), every anchor count-1 and every selector collected, and the runner re-run into the deposit file: `MUTATION: 12 killed, 0 survived, 0 error`.
