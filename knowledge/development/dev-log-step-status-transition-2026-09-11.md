# dev-log — step-status-transition — 2026-09-11 [100073]

## Pins re-derived (P1, P3, P4)

P2 verbatim: `steps.status` × `plans.lifecycle_state`: `awaiting_verdict\|closed` 17, `awaiting_verdict\|halted` 6, `complete\|closed` 94, `complete\|halted` 6, `running\|abandoned` 1 (step id 90, plan 100051 step 2 — the tool lists it, never touches it), `running\|in_progress` 1 (#100072, in flight at drafting); the 17 closed rows by step id: 4 (plan 3/2), 7 (100001/2), 20 (100007/3), 22 (100008/2), 29 (100013/1), 49 (100023/2), 56 (100027/2), 69 and 70 (100037/1, /2), 77 (100042/2), 81 (100045/2), 91 and 92 (100052/1, /2), 93 and 94 (100053/1, /2), 98 (100056/1), 99 (100057/1), plus #100071's step 1 (closed 00:40 tonight); the 6 halted: 1 (1/1), 17 (100006/2), 47 (100022/2), 62 (100031/1), 82 (100046/1), 95 (100054/1)

P1 re-derived: `:1219` and `:1378` both read `lifecycle.record_step_end(_lc_step_id, status="complete" if gate_result["passed"] else "awaiting_verdict",` (the pause-side writes). `awk 'NR>=3157&&NR<=3420&&/record_step_end/' bellows.py` produced no output — no `record_step_end` anywhere in `_consume_verdicts`. Close branch at `:3336`: `lifecycle.mark_plan_state(_lc_plan_id, "closed", ...)` with `_retire_receipts` at `:3337`, `release_for_plan` at `:3338`, `enqueue_thread_reviews` at `:3339`. Advance branch: `next_step = step_number` at `:3351` (precondition retry) / `next_step = step_number + 1` at `:3354`; `lifecycle.mark_plan_state(_lc_plan_id, "in_progress")` at `:3357`; `self.handle_new_plan(inprogress_path, resume_step=next_step)` at `:3360`. No mechanism mismatch.

P3 re-derived: `steps` schema (`lifecycle.py:83–90`): `status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending','running','awaiting_verdict','complete'))`, `step_started_at`, `step_ended_at`. `record_step_start` at `:462` (INSERT, returns lastrowid). `record_step_end` at `:481` (UPDATE by step id). `LIFECYCLE_DB_PATH` at `:21`. `get_step_id` at `:822`.

P4 re-derived: `tests/test_consume_verdicts.py:1082` — `test_consume_verdict_continue_to_done_calls_mark_plan_state_for_qa_plan`. Six patches (check_verdict, log_to_ledger, push, mark_plan_state, record_verdict_outcome, get_overridden_gates_for_step). `conftest.isolate_lifecycle_db` at `:31` is autouse — `monkeypatch.setattr(lifecycle, "LIFECYCLE_DB_PATH", tmp)` + `init_lifecycle_db`.

## Failing-first (three red, then green)

Red — test_lifecycle.py: `5 failed, 96 passed in 1.08s`
Red — test_consume_verdicts.py: `2 failed, 34 passed in 2.36s`
Red — test_reconcile_steps.py: `3 failed in 1.85s`

Green — full suite: `2242 passed, 1 skipped in 98.56s`

## The transition observed (t6, t7)

t6 BEFORE FIX: `step_status='awaiting_verdict'`, `plan_state='closed'` — plan-side write works, step-side does not.
t6 AFTER FIX: `step_status='complete'`, `plan_state='closed'` — both correct.

t7 BEFORE FIX: `step_status='awaiting_verdict'` — step row untouched by advance branch.
t7 AFTER FIX: `step_status='complete'`, `handle_new_plan` called once with `resume_step=2`.

## Mutation run

MUTATION: 5 killed, 0 survived, 0 error
