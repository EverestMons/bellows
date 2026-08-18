# on_failure canary — dev note

**Plan:** 441
**Date:** 2026-08-18
**Step:** 1 — DEV

## What was done

Added `tests/test_on_failure_canary.py` with three regression-guard tests:

1. **test_on_failure_in_recognized_tokens** — confirms `"on_failure"` remains in `RECOGNIZED_PAUSE_TOKENS` (plan_lint).
2. **test_header_says_pause_on_failure_returns_false** — confirms `header_says_pause` returns `False` for both `is_qa_step=False` and `is_qa_step=True` under `on_failure`.
3. **test_effective_auto_close_implied_by_on_failure** — source-substring assertion confirming the `on_failure` disjunct is present in the `effective_auto_close` computation inside `run_plan`.

## Test run

```
3 passed in 0.12s
```

No production code was changed.
