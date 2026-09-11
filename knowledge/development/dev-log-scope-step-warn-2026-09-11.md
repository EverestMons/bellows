# dev-log: scope-step-warn-2026-09-11 [100074]

## Pins re-derived (P1, P2, P3, P4)

P5 verbatim: `Done/diagnostic-100071.md` and `governance/knowledge/research/qa-scope-census-2026-09-11.md`: the gate's own per-step record (`step_files`, 157 rows, 35 steps, 20 plans) — own 153, earlier-step-only 1 (`100061` step 2 `scripts/close_cycle.py`, `d6da69b`), undeclared 3 (the ledger's fails, overridden); Q3 rate **1 of 37** QA steps; residue 0; the ledger's six `scope_check` fails all `tests/` files; Q5's 18 of 95 rests on the `commits` arm and is inflated by thread 275's attribution — not used here

P1 re-derived: `gates.py:1127` `def _gate_scope_check(plan_text, step_number, files_changed, failures, project_path=None):` (now with `warnings=None`); `:1133` `for s in range(1, step_number + 1):`; `:1145–1147` Scope union; `:1152–1158` `declared_files ∪ Deposits`; `:1161–1170` P14 normalization; `:1180–1182` `SCOPE_ALLOWLIST / SCOPE_ALLOWLIST_PREFIXES`; `:1189` `d == fpath or ("/" in d and d.split("/", 1)[1] == fpath)`; `:1193–1198` prefix arm; `:1203–1219` legacy prose/directory arms; `:1223–1228` `failures.append({"gate": "scope_check", …})`. Extractors: `_extract_step_text` `:565`, `_extract_plan_scope` `:643`, `_extract_deposits_block_paths` `:1103`. No mismatch: no `warnings` key in result, no `scope_step` in `_KNOWN_GATES` or `standard_gates`, CHECK admits only `pass`/`fail`.

P2 re-derived: `gates.check` (`:270`) returns 6 keys (`passed`, `failures`, `is_qa_step`, `files_changed`, `plan_header`, `verdict_requested`) — no `warnings` key yet; `_gate_scope_check` Gate 8 at `:310`; `verdict._build_verification_results_table` (`:105`) with `_KNOWN_GATES` 15 tuples at `:112–128`, `scope_check` 8th; two display-only rows (`qa_step_detection`, `file_change_audit`).

P3 re-derived: `lifecycle.record_gate_events(step_id, gate_result, db_path=None)` at `:522`; `standard_gates` = 12 names; `gate_events` schema `:130–138`: `result TEXT NOT NULL CHECK (result IN ('pass', 'fail'))`, `reason_code TEXT`. No `scope_step` in `standard_gates`; CHECK does not admit `warn`.

P4 re-derived: `tests/test_gate_transaction_mechanization.py:15–28` `STANDARD_GATES` 12 names; `tests/test_gates.py:22–33` `PLAN_TEXT` two steps, NO Scope block; `tests/test_lifecycle.py TestRecordGateEvents.test_records_pass_and_fail` `:508` row shape; `conftest.isolate_lifecycle_db` `:31`.

## Failing-first (red, then green)

Red (before edits): `tests/test_scope_step.py` t1–t12 all failed — t1/t2/t4/t5 failed with `assert False is True` (other gates fired from fixture's `qa_steps: 2` and Deposits blocks); t3 passed but t6 assertion wrong; t7/t8 no `scope_step` row in verdict table; t9/t10/t11 no `scope_step` row in `gate_events`; t12 failed `assert False is True`. `tests/test_gate_transaction_mechanization.py` 1 failure: `AssertionError: assert 12 == 13`. Summary red: `13 failed, 19 passed in 0.57s`. After fixture fix (`qa_steps: none`, no Deposits blocks): all fixture-driven failures resolved. After all three edits (gates.py, verdict.py, lifecycle.py): `32 passed in 0.48s`. Full suite: `2254 passed, 1 skipped in 97.82s`.

## The arm observed (t2, t7, t9)

t2 `warnings` list: `[{'gate': 'scope_step', 'evidence': 'gates.py'}]`, `passed: True`

t7 table row: `| scope_step | WARN | 1 file(s) declared by an earlier step only: gates.py |`; adjacent: `| scope_check | PASS | All changes within plan scope |`

t9 ledger row: `('pass', 'earlier-step-only: gates.py')`

## Mutation run

MUTATION: 5 killed, 0 survived, 0 error
