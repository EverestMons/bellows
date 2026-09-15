# dev-log: reconcile-plan-steps-claim-lane — 2026-09-15

## Pins re-derived (P1, P2, P4)

P1: `tools/reconcile_plan.py`, 144 lines: the docstring :2–16; `VALID_STATES` :29; `main` :33; the look — the plan row :63–72, the NULL-outcome verdicts :74–81, the pending files :83–87; the refusal :89–96, `in_progress` or `awaiting_verdict` without `--killed-verified` (#100009's R1); `now_utc` :98; the transaction :99–115 — `UPDATE plans` :101–104, `UPDATE verdicts` :105–109, `conn.commit()` :110; the summary :117–119; the archive :121–127, `os.rename` :126; `dest_name` :131–135; `Remaining human acts` :137, its `git mv knowledge/decisions/{plan_type}-{args.plan_id}.md` :138–139 and `git commit -m` :140; no `steps` in the file

Re-derived: `grep -n -E 'UPDATE|steps|git mv|Remaining|killed_verified|dest_name' tools/reconcile_plan.py` — UPDATE at :102, :106; killed_verified at :89; dest_name at :133, :135; Remaining at :137; git mv at :138–139; no `steps` match; `wc -l` = 144. MATCH.

P2: `lifecycle.py` steps table at :83, CHECK at :89; `deposit_placeholder` at :364; `record_step_start` at :623; `record_step_end` at :655, UPDATE at :664; `mark_step_complete` at :675, UPDATE at :683; `mark_step_abandoned` at :696, UPDATE at :704. All line numbers confirmed by reading the file. MATCH.

P4: `tests/test_reconcile_plan.py`: 8 tests in 244 lines; `PLANS_DDL` at :14 (drift from :15), `VERDICTS_DDL` at :32 (drift from :33), `_make_env` at :46, `_run` at :62, `class TestReconcilePlan` at :76. Line-number drift only; mechanism matches. MATCH.

## Failing-first (red, then green)

Red (unedited tool, 16 tests from the new class fail):
`16 failed, 11 passed in 3.32s`

Green (edited tool, test file):
`27 passed in 1.10s`

Green (py_compile under /usr/bin/python3 3.9.6):
`py_compile OK` (exit 0 for both tools/reconcile_plan.py and tests/test_reconcile_plan.py)

Green (full suite):
`2464 passed, 2 skipped, 9 warnings in 238.61s`

## The marks and the acts observed (y1, y5, y8, y12)

```
tests/test_reconcile_plan.py::TestReconcileStepsClaimLane::test_running_step_abandoned_on_every_target[closed] PASSED [ 10%]
tests/test_reconcile_plan.py::TestReconcileStepsClaimLane::test_running_step_abandoned_on_every_target[halted] PASSED [ 20%]
tests/test_reconcile_plan.py::TestReconcileStepsClaimLane::test_running_step_abandoned_on_every_target[abandoned] PASSED [ 30%]
tests/test_reconcile_plan.py::TestReconcileStepsClaimLane::test_step_marks_mirror_lifecycle_writers[closed] PASSED [ 40%]
tests/test_reconcile_plan.py::TestReconcileStepsClaimLane::test_step_marks_mirror_lifecycle_writers[halted] PASSED [ 50%]
tests/test_reconcile_plan.py::TestReconcileStepsClaimLane::test_step_marks_mirror_lifecycle_writers[abandoned] PASSED [ 60%]
tests/test_reconcile_plan.py::TestReconcileStepsClaimLane::test_lane_move_names_the_real_source_and_the_convention[closed-knowledge/decisions/Done/executable-99.md] PASSED [ 70%]
tests/test_reconcile_plan.py::TestReconcileStepsClaimLane::test_lane_move_names_the_real_source_and_the_convention[halted-knowledge/decisions/halted-executable-99.md] PASSED [ 80%]
tests/test_reconcile_plan.py::TestReconcileStepsClaimLane::test_lane_move_names_the_real_source_and_the_convention[abandoned-knowledge/decisions/Done/abandoned-executable-99.md] PASSED [ 90%]
tests/test_reconcile_plan.py::TestReconcileStepsClaimLane::test_steps_rows_printed_before_any_write PASSED [100%]
```

## Mutation run

`MUTATION: 15 killed, 0 survived, 0 error`
