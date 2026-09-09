# Dev-log — drafting-battery-reprice — 2026-09-09 [100056, thread 81]

## Pins re-derived (P1–P4)

P3 pin value (verbatim from the plan):
> `scripts/lens_order_check.py` over every Done plan naming a `**Walk register:**` (84 of 561): LENS-ORDER OK 10, NO-RECORD 68, BATCHED 2, INCOMPLETE 2, N/A 2; the four 2026-09-09 cycles carry 15–40 lens commits each (100% per-lens)

Re-derived values:

- **P1**: 189 registers (pin: 188), 16 tableless, September 52 (pin: 51). Delta = 1: the plan's own register added since the pin was measured. All per-tool September counts delta by +1 tracing to that one row (plan_lint=not_recorded, cycle_check=paraphrase, fold_check=not_recorded, propagation_check=not_recorded, walk_register_lint=paraphrase, mutation_check=not_recorded).

- **P2**: August 41 of 63 Done plans with `validation: cycle_check=`, September 33 of 33 — confirmed, pin matches.

- **P3**: OK 10, NO-RECORD 68, BATCHED 1, INCOMPLETE 3, N/A 2 (vs pin: BATCHED 2, INCOMPLETE 2). Delta: `diagnostic-370.md` has both BATCHED (walk 2) and INCOMPLETE (walk 1); `lens_order_check` sorts findings by walk, so INCOMPLETE: walk 1 prints before BATCHED: walk 2. Taking the first finding as primary verdict categorizes it as INCOMPLETE. Unique violation plans: 4 in both counts.

- **P4**: September cycle_check: 5 verbatim, 39 paraphrase (pin: 38). Delta = 1 paraphrase from the new register.

## Instrument extension (three columns, byte-identical elsewhere)

Added to `tools/battery_census.py`:
- `lens_order`: calls `lens_order_check.main([plan_path])` on the Done plan resolved via `lifecycle.db` `plan_doc_ref`; caches per plan_doc_ref. Values: OK / NO-RECORD / BATCHED / INCOMPLETE / UNPROVEN / N/A / unresolved.
- `validation_line`: reads `^validation: cycle_check=` from the resolved Done plan. Values: yes / no.
- `coverage`: calls `wrl.coverage_verdict(text, fp)` on the register. Values: COVERED / INCOMPLETE / UNDECLARED / unresolved.

Added `DRAFT_LINE_RE` to extract `deposit_placeholder_name` from `Draft:` lines (complement to existing `PLAN_LINE_RE` for `**Plan:**` lines). Updated `load_lifecycle` to return `plan_doc_ref` alongside `lifecycle_state`. Added `lookup_plan_doc_ref`, `get_lens_order`, `get_validation_line`, `get_coverage` functions.

Byte-identical assertion run:
```
diff <(awk -F'\t' 'BEGIN{OFS="\t"}{print $1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,$13,$14,$15}' census_new_out.tsv) battery_census_old_out.tsv
```
Exit 0. Empty diff.

TSV written to `governance/knowledge/research/drafting-battery-reprice-2026-09-09.tsv` (190 lines: 1 header + 189 data rows, 18 columns).

## Q1–Q7 in one table

| Q | measure | Sep corpus (52) | corpus-wide (189) |
|---|---|---|---|
| Q1 (register) | cycle_check recorded | 44/52 (84%) | 68/189 (36%) |
| Q1 (manifest) | validation_line=yes | 33/33 closed Sep plans (100%) | 35 registers (19%) |
| Q2 | cycle_check paraphrase rate | 39/44 recorded (89%) | 62/68 recorded (91%) |
| Q4b | LENS-ORDER OK | 9 registers (via census); 10 Done plans (direct) | 10 OK, 68 NO-RECORD, 4 violations |
| Q3/Q5 | battery catches fold-introduced semantic gaps | 0/2 caught (f2b, f2c) | not-caught class: incomplete propagation |
| Q6 | cycle_check wall-time | ~390 ms (now includes battery) | 45 invocations/cycle = ~17.6 s |
| Q7 | what draft lane adds | parts 1 (draft lane) and 3 (scratch execution) not built; skipped class still open | cold-seat read-only contract not enforced |

Key change since 100032: cycle_check now carries the battery (plan_lint + fold_check + propagation_check) in one invocation. The manifest provides a verbatim `validation: cycle_check=` record for all September Done plans — the second record Q1 could not see in 100032. lens_order_check is now the observer (deployed 2026-09-06). The Sep-09-09 cycles show 100% per-lens compliance via the commit loop. Despite these advances, the dominant not-caught fold class (incomplete propagation) remains below the battery's resolution.

## What the doc does not establish

- No recommendation on whether to build parts 1–2 of thread 81's sketch.
- Not-caught class (incomplete propagation) is not addressable at the battery's per-commit resolution — a daemon firing the battery per lens commit would still miss it.
- The manifest verbatim record (Q1, P2) counters the register paraphrase class, but the register prose remains 89% paraphrase for cycle_check — the draft lane does not fix that.
- The cold-seat hazard (plan 100051, 2026-09-09) requires sandbox enforcement at the execution boundary; it is unresolved.

Suite run: `pytest` gated at commit. `numstat` → exactly 2 files (tools/battery_census.py, knowledge/development/dev-log-drafting-battery-reprice-2026-09-09.md).
