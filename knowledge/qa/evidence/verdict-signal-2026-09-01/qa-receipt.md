# QA Receipt — verdict-signal-2026-09-01 (plan 100009)

**Date:** 2026-09-01
**Step:** 2 (QA)
**Agent:** Bellows QA
**DEV commit:** 2e74fc7
**Interpreter:** /Users/marklehn/Developer/bellows/.venv/bin/python (Python 3.12.14)

---

## Verification Table

| Deliverable | Expected | Status | Evidence |
|---|---|---|---|
| Item 1 — P3: `lifecycle.mark_plan_state(` count in `bellows.py` | 12 | ✅ | probes-raw.txt |
| Item 1 — `"awaiting_verdict")` count in `bellows.py` | 5 | ✅ | probes-raw.txt |
| Item 1 — D1: `awaiting_verdict` in `depositor.py` `_resolve_in_flight_writes` | 1 occurrence | ✅ | probes-raw.txt |
| Item 1 — S1: `awaiting_verdict` in `status.py` `query_in_flight` | 1 occurrence | ✅ | probes-raw.txt |
| Item 1 — R1: `awaiting_verdict` in `tools/reconcile_plan.py` condition | 1 occurrence | ✅ | probes-raw.txt |
| Item 1 — `_push_pause` defined once, called once in `tools/gate_watcher.py` | 2 lines total | ✅ | probes-raw.txt |
| Item 1 — `lifecycle.py` sha unchanged | `412abd155d5099aa` | ✅ | probes-raw.txt |
| Item 1 — DEV commit scope matches Scope exactly | 11 files | ✅ | probes-raw.txt |
| Item 2 — `test_verdict_signal.py` | 4 passed (new) | ✅ | probes-raw.txt |
| Item 2 — `test_gate_watcher.py` | 50 passed (pre: 45) | ✅ | probes-raw.txt |
| Item 2 — `test_status.py` | 23 passed (pre: 22) | ✅ | probes-raw.txt |
| Item 2 — `test_depositor.py` | 25 passed (pre: 24) | ✅ | probes-raw.txt |
| Item 2 — `test_reconcile_plan.py` | 8 passed (pre: 6) | ✅ | probes-raw.txt |
| Item 2 — `test_lifecycle.py` | 95 passed (pre: 95) | ✅ | probes-raw.txt |
| Item 3 — Full suite: no regressions vs P4 baseline | 9 failed, 1642 passed | ✅ | full-suite-verdict-signal.txt |
| Item 4 — `gate_watcher --status` prints state line, no push line | state line only | ✅ | probes-raw.txt |
| Item 4 — Push fires once on transition, zero on repeated poll, zero on `--status` | `TestPushPause` 4 passed | ✅ | probes-raw.txt |
| Item 5 — `reconcile_plan` exits 3 on `awaiting_verdict` without `--killed-verified` | exit 3 | ✅ | probes-raw.txt |
| Item 5 — `reconcile_plan` proceeds on `awaiting_verdict` with `--killed-verified` | exit 0 | ✅ | probes-raw.txt |
| Item 6 — Plan 100009 reads `in_progress` in live DB (daemon predates fix) | `in_progress` | ✅ | probes-raw.txt |

### Item 3 — Full Suite Control Comparison Notes

Baseline P4: 10 failed (named set), 1629 passed.
Measured: 9 failed, 1642 passed.

The failing set is a strict subset of P4's 10. One baseline failure is absent from this run:
`tests/test_gates_cross_machine_paths.py::TestCrossMachineReRoot::test_relative_path_unchanged`
This test now passes. A fix this plan did not make — stated per plan instructions.

The 9 still-failing tests are the remaining 9 from P4's named baseline set (all thread-56 shop-layout path failures — pre-existing). No test that was passing in the baseline now fails. No new failure was introduced.

Passed count: 1642 = 1629 (baseline) + 13 new tests (4 test_verdict_signal + 5 test_gate_watcher + 1 test_status + 1 test_depositor + 2 test_reconcile_plan).

### Item 6 — Restart Discipline

Plan 100009's own pause rows read `in_progress` in the live `lifecycle.db` (queried read-only):
`100009|in_progress|knowledge/decisions/in-progress-executable-100009.md`

This is expected: the running daemon executes pre-fix code throughout this plan's lifecycle. The daemon cannot write `awaiting_verdict` to the plan row because it predates the change. The fix is proven by the tests (Items 2 and 4) and by the source probes (Item 1). The canary is the NEXT plan's pause after the CEO restarts the daemon via the dashboard `r` command — that is where the production signal is observed, not in this plan's own rows.

---

## Rule 20 Self-Check Results

============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: /Users/marklehn/Developer/bellows/.bellows-worktrees/100009/knowledge/qa/evidence/verdict-signal-2026-09-01/
Files verified: 2
