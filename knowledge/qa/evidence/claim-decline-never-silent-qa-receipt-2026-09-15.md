# QA Receipt — claim-decline-never-silent — 2026-09-15

## DEV commit numstat (c1193914..6b12d222)

```
1       2       bellows.py
45      0       knowledge/development/dev-log-claim-decline-never-silent-2026-09-15.md
94      0       knowledge/mutants/claim-decline-never-silent.json
22      0       knowledge/mutants/claim-decline-never-silent.run.txt
18      6       plan_claim.py
138     0       tests/test_bellows.py
99      0       tests/test_plan_claim.py
```

Seven files changed across the two DEV commits (0949c475 and 6b12d222).

## Unchanged-test hunks (git diff -U0 c1193914..6b12d222 -- tests/)

```
@@ -5835,0 +5836,138 @@ def test_resumed_step_records_only_its_own_commits():
@@ -520,0 +521,99 @@ class TestDeclineDedupe:
```

Both hunks add lines only (zero removals). The five z6–z10 items appended after
`tests/test_bellows.py`'s last line (:5835) and the five z1–z5 items inserted
after `TestDeclineDedupe`'s last line (:520). No existing test was edited.

## Item 2 — logging read through its own tests (14 PASSED)

```
tests/test_plan_claim.py::TestDeclineNeverSilent::test_repeat_decline_relogged_after_interval_with_count PASSED [  7%]
tests/test_plan_claim.py::TestDeclineNeverSilent::test_interval_restarts_from_the_last_repeat PASSED [ 14%]
tests/test_plan_claim.py::TestDeclineNeverSilent::test_repeats_inside_the_interval_stay_quiet PASSED [ 21%]
tests/test_plan_claim.py::TestDeclineNeverSilent::test_repeat_blocked_relogged_after_interval PASSED [ 28%]
tests/test_plan_claim.py::TestDeclineNeverSilent::test_decline_after_a_proceed_is_logged_in_full PASSED [ 35%]
tests/test_bellows.py::test_declined_claim_logs_no_started PASSED        [ 42%]
tests/test_bellows.py::test_passing_claim_logs_started_once_after_the_mint PASSED [ 50%]
tests/test_bellows.py::test_resumed_plan_logs_started PASSED             [ 57%]
tests/test_bellows.py::test_handle_new_plan_does_not_log_started PASSED  [ 64%]
tests/test_bellows.py::test_handle_parallel_group_does_not_log_started PASSED [ 71%]
tests/test_plan_claim.py::TestDeclineDedupe::test_consecutive_declines_one_warn PASSED [ 78%]
tests/test_plan_claim.py::TestDeclineDedupe::test_outcome_change_logs_anew PASSED [ 85%]
tests/test_plan_claim.py::TestDeclineDedupe::test_repeated_after_change_silent PASSED [ 92%]
tests/test_plan_claim.py::TestDeclineDedupe::test_advisory_error_logs_every_time PASSED [100%]
```

## Verification

| Item | Evidence | Status |
|------|----------|--------|
| 1 — full suite | `claim-decline-never-silent-suite-2026-09-15.txt` summary: `2442 passed`, two skips (test_gate_watcher live-DB; test_fallback_live_wal_window version gate), no failures | ✅ |
| 2 — logging read through tests | 14 PASSED lines above; z1–z10 and the four TestDeclineDedupe tests all green | ✅ |
| 3 — production writes | None outside the two evidence files (`claim-decline-never-silent-qa-receipt-2026-09-15.md`, `claim-decline-never-silent-suite-2026-09-15.txt`); no lane file, no live lifecycle row, no claim, no daemon act | ✅ |

============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: /Users/marklehn/Developer/bellows/.bellows-worktrees/100107/knowledge/qa/evidence/
Files verified: 1
