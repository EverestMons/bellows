# Dev Log — receipt-key fix (thread 321, 2026-09-14)

## Pins re-derived (P1, P2, P3)

`notifier.py`: `_DEFAULT_EVENTS` :38, `verdict_needed`, `plan_halted`, `failure`, `checkout_stale` and `plan_abandoned` on; `owned_by_live_session(plan_slug, receipts_dir=None, window=None)` :218, its glob `receipt-{plan_slug}-*.json` :234 and the newest match by mtime :238, no slug check; `notify_event` :264, the ownership call `owned_by_live_session(plan_slug)` :285 under `if plan_scoped and plan_slug`; the plan-scoped wrappers `notify_plan_halted` :306, `notify_plan_abandoned` :314, `notify_failure` :344, `notify_verdict_request` :360 and `notify_checkout_stale` :386; `notify_class_hold` :377, `plan_scoped=False`

## Failing-first (red, then green)

Red (16 new nodes on unmodified code): `12 failed, 4 passed in 0.35s`

Green (two test files against the fix): `61 passed in 93.54s`

Full suite: `2483 passed, 2 skipped in 238.21s`

## The pages counted (6a, 6c, 9f, 9h, c-t26)

```
tests/test_notifier_coverage.py::test_6a_receipt_key_attended_suppresses_page PASSED [ 20%]
tests/test_notifier_coverage.py::test_6c_neighbour_receipt_slug_mismatch_pages PASSED [ 40%]
tests/test_notifier_coverage.py::test_9f_final_verdict_page_carries_receipt_key PASSED [ 60%]
tests/test_notifier_coverage.py::test_9h_failure_page_after_mint_pages_when_attended PASSED [ 80%]
tests/test_abandoned_runner_close.py::test_refusal_page_pages_when_attended PASSED [100%]
```

## Mutation run

`MUTATION: 15 killed, 0 survived, 0 error`
