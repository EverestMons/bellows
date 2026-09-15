# QA Receipt — reconcile-plan-steps-claim-lane — 2026-09-15

## Numstat (f82e25bb..ff9f5a02)

```
44	0	knowledge/development/dev-log-reconcile-plan-steps-claim-lane-2026-09-15.md
110	0	knowledge/mutants/reconcile-plan-steps-claim-lane.json
23	0	knowledge/mutants/reconcile-plan-steps-claim-lane.run.txt
256	0	tests/test_reconcile_plan.py
69	9	tools/reconcile_plan.py
```

Five files. Three new deposits, two modified (test file additions and tool edits).

## Unchanged tests check

`git diff -U0 f82e25bb..ff9f5a02 -- tests/test_reconcile_plan.py | grep -F '@@'`:

```
@@ -44,0 +45,19 @@ CREATE TABLE verdicts (
@@ -53,0 +73 @@ def _make_env(tmp):
@@ -75,0 +96,38 @@ def _dump_table(db_path, table):
@@ -244,0 +303,198 @@ class TestReconcilePlan:
```

All four hunks add lines and remove none (`,0` on the `-` side of every `@@`). STEPS_DDL inserted after VERDICTS_DDL, `conn.execute(STEPS_DDL)` added in `_make_env`, helpers and the new class appended after the file's last test. No existing test was edited. MUST-PRESERVE met.

## Item 2 — Tool read through its own tests

Fifteen PASSED lines (y1 × 3, y2, y5 × 3, y6, y8 × 3, y10, y12; plus the two from the existing class):

```
tests/test_reconcile_plan.py::TestReconcilePlan::test_in_progress_refused_without_flag PASSED [  6%]
tests/test_reconcile_plan.py::TestReconcilePlan::test_terminal_verdict_untouched PASSED [ 13%]
tests/test_reconcile_plan.py::TestReconcileStepsClaimLane::test_running_step_abandoned_on_every_target[closed] PASSED [ 20%]
tests/test_reconcile_plan.py::TestReconcileStepsClaimLane::test_running_step_abandoned_on_every_target[halted] PASSED [ 26%]
tests/test_reconcile_plan.py::TestReconcileStepsClaimLane::test_running_step_abandoned_on_every_target[abandoned] PASSED [ 33%]
tests/test_reconcile_plan.py::TestReconcileStepsClaimLane::test_awaiting_verdict_step_completed_when_closed PASSED [ 40%]
tests/test_reconcile_plan.py::TestReconcileStepsClaimLane::test_step_marks_mirror_lifecycle_writers[closed] PASSED [ 46%]
tests/test_reconcile_plan.py::TestReconcileStepsClaimLane::test_step_marks_mirror_lifecycle_writers[halted] PASSED [ 53%]
tests/test_reconcile_plan.py::TestReconcileStepsClaimLane::test_step_marks_mirror_lifecycle_writers[abandoned] PASSED [ 60%]
tests/test_reconcile_plan.py::TestReconcileStepsClaimLane::test_prints_the_claim_release_for_the_placeholder PASSED [ 66%]
tests/test_reconcile_plan.py::TestReconcileStepsClaimLane::test_lane_move_names_the_real_source_and_the_convention[closed-knowledge/decisions/Done/executable-99.md] PASSED [ 73%]
tests/test_reconcile_plan.py::TestReconcileStepsClaimLane::test_lane_move_names_the_real_source_and_the_convention[halted-knowledge/decisions/halted-executable-99.md] PASSED [ 80%]
tests/test_reconcile_plan.py::TestReconcileStepsClaimLane::test_lane_move_names_the_real_source_and_the_convention[abandoned-knowledge/decisions/Done/abandoned-executable-99.md] PASSED [ 86%]
tests/test_reconcile_plan.py::TestReconcileStepsClaimLane::test_missing_lane_file_is_reported_not_moved PASSED [ 93%]
tests/test_reconcile_plan.py::TestReconcileStepsClaimLane::test_steps_rows_printed_before_any_write PASSED [100%]
```

## Verification

| Item | Evidence | Status |
|------|----------|--------|
| 1 — full suite | `2464 passed, two skips (test_gate_watcher live-DB; test_fallback_live_wal_window version gate)` — `reconcile-plan-steps-claim-lane-suite-2026-09-15.txt` last line | ✅ |
| 2 — tool through tests | 15 PASSED lines above: y1 × 3, y2, y5 × 3, y6, y8 × 3, y10, y12; `test_in_progress_refused_without_flag` and `test_terminal_verdict_untouched` from existing class | ✅ |
| 3 — production writes | none outside the two evidence files; no lane file, no live lifecycle row, no claim, no daemon act | ✅ |

============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: /Users/marklehn/Developer/bellows/.bellows-worktrees/100110/knowledge/qa/evidence/
Files verified: 1
