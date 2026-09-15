# Dev log — claim-decline-never-silent — 2026-09-15

## Pins re-derived (P1, P2, P3)

`plan_claim.py`: the seam contract in the docstring :1–8; `import datetime as _dt` :10; `_outcome_memo = {}` :22, `_release_errored` :23; `_reset_memo` :30–33; `claim_gate` :123 — its docstring :124, `claim_for_deposit(…)` :125, `slug` :126; the proceed :128–131; the memo — `last = _outcome_memo.get(slug)` :133, `if last == outcome:` :134, its `return False` :135, `_outcome_memo[slug] = outcome` :136; the hint's condition :147; the decline's WARN :150; the block's ERROR :152; the last `return False` :154

Line-number drift on P2 (uniformly +5 on the run_plan block; larger shift on dispatcher lines):
- `⏳ RUNNING` :1552 (plan: :1547)
- `if not plan_claim.claim_gate(…)` :1675 (plan: :1670)
- `lifecycle.mint_and_claim(` :1683 (plan: :1678)
- `minted id` :1714 (plan: :1709)
- `plan has {total_steps} steps` :1749 (plan: :1744)
- `parallel group` lines :3310, :3640 (plan: :3249, :3579)
- `⏳ detected plan` :3314 (plan: :3253)
- `handle_new_plan` :3450 (plan: :3389)
- thread start + stagger :3456–3457 (plan: :3396–3397)
- `▶ started` :3459 (plan: :3398)
- `handle_parallel_group` :3461 (plan: :3400)
- `▶ started {len(threads)} parallel threads` :3473 (plan: :3412)
- `rescan_interval = 30` :4205 (plan: :4144)
No mechanism mismatch: no prior `_DECLINE_REPEAT_SECS`, no `▶ started` in run_plan, `handle_new_plan` still logged it.

P3: `tests/test_plan_claim.py` 657 lines, 49 tests; `TestDeclineDedupe` :455–520; `TestSlugParity` :525. `tests/test_bellows.py` 5835 lines, 187 test functions, 193 collected.

## Failing-first (red, then green)

Red (base code, before edits):
`8 failed, 2 passed in 2.28s`

Green (after edits):
`10 passed in 0.26s`
`252 passed in 7.94s`
compile OK (py_compile under /usr/bin/python3 3.9.6)
`2442 passed, 2 skipped, 9 warnings in 237.68s`

## The logging observed (z1, z5, z7, z9)

tests/test_plan_claim.py::TestDeclineNeverSilent::test_repeat_decline_relogged_after_interval_with_count PASSED [ 25%]
tests/test_plan_claim.py::TestDeclineNeverSilent::test_decline_after_a_proceed_is_logged_in_full PASSED [ 50%]
tests/test_bellows.py::test_passing_claim_logs_started_once_after_the_mint PASSED [ 75%]
tests/test_bellows.py::test_handle_new_plan_does_not_log_started PASSED  [100%]

## Mutation run

MUTATION: 12 killed, 0 survived, 0 error
