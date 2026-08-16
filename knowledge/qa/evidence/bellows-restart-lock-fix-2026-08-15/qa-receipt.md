# QA Receipt — restart-lock fix

**Plan:** `bellows-restart-lock-fix-2026-08-15`
**Step:** 3 — QA
**Status:** FAIL
**Date:** 2026-08-15
**Branch:** `bellows-wt/430`

---

## Pre-step check

| Dev-log | Status |
|---|---|
| `restart-lock-fix-step1-2026-08-15.md` | Complete |
| `restart-lock-fix-step2-2026-08-15.md` | Complete |

---

## (B) Verification

### Full test suite

| Metric | Value |
|---|---|
| Pre-change baseline | 1040 passed, 0 failed |
| Tests added (Steps 1-2) | 13 (6 in test_instance_lock.py + 7 in test_stop_path.py) |
| Expected total | 1053 passed, 0 failed |
| Actual total | 1049 passed, 4 failed |
| Delta | -4 (regression) |

**Verdict:** ❌ FAIL — 4 pre-existing tests regressed.

Raw output: `full-suite-output.txt`

### Regression investigation

The 4 failing tests all hit the `_shutting_down` gate added by Step 1 at `bellows.py:2031` in `PlanHandler._handle`. Each test constructs a `MagicMock()` orchestrator with `mock_orch._seen = set()` but does not set `mock_orch._shutting_down = False`. Since `MagicMock()` auto-creates truthy attributes, the shutdown guard fires and returns early, preventing the test from reaching the behavior it asserts.

| # | Test | Root cause |
|---|---|---|
| 1 | `test_handle_parallel_from_watchdog_adds_pending_not_dispatched` | `mock_orch._shutting_down` is truthy MagicMock — guard returns before `_pending_groups` is populated |
| 2 | `test_nonparallel_plan_dispatches_immediately_from_handle` | `mock_orch._shutting_down` is truthy MagicMock — guard returns before `handle_new_plan` is called |
| 3 | `test_two_parallel_siblings_collected_as_one_group` | `mock_orch._shutting_down` is truthy MagicMock — guard returns before `_pending_groups` is populated |
| 4 | `test_seen_uses_slug_not_path` | `mock_orch._shutting_down` is truthy MagicMock — guard returns before `_seen` is populated |

**Fix (not applied — QA does not repair):** Add `mock_orch._shutting_down = False` to each test's mock setup.

### Step-1 and Step-2 targeted tests

All 13 targeted tests pass:

```
tests/test_instance_lock.py::test_acquire_writes_pid_and_timestamp PASSED
tests/test_instance_lock.py::test_failure_includes_holder_pid PASSED
tests/test_instance_lock.py::test_failure_falls_back_on_empty_file PASSED
tests/test_instance_lock.py::test_second_open_preserves_holder_pid PASSED
tests/test_instance_lock.py::test_shutting_down_refuses_dispatch PASSED
tests/test_instance_lock.py::test_drain_waits_for_active_count_zero PASSED
tests/test_stop_path.py::test_acquire_succeeds_no_incumbent PASSED
tests/test_stop_path.py::test_identity_mismatch_refuses PASSED
tests/test_stop_path.py::test_idle_guard_running_refuses PASSED
tests/test_stop_path.py::test_both_guards_pass_sigterm_then_sigkill PASSED
tests/test_stop_path.py::test_reacquire_race_lost_refuses PASSED
tests/test_stop_path.py::test_ambiguous_lsof_refuses PASSED
tests/test_stop_path.py::test_idle_guard_passes_awaiting_verdict_with_orphan PASSED
======================== 13 passed, 1 warning in 4.90s =========================
```

Raw output: `targeted-tests-output.txt`

### Guard sequence verification (code reading)

The ordered guard sequence in `stop_daemon` (`bellows.py:155-228`) is intact:

1. **Flock acquire** (line 163-168): `acquire_instance_lock(lock_path)` — success means no incumbent, no kill
2. **lsof discover** (line 171-173): `_discover_holder(lock_path)` — refuses on None or >1 PID (ambiguous)
3. **Identity guard** (line 176-178): `_verify_identity(holder_pid)` — checks `ps -o command=` for `bellows.py`
4. **Idle guard** (line 181-183): `_check_idle(db_path, config)` — refuses only on `status='running'`; `awaiting_verdict`/NULL do not block
5. **Signal** (line 186-220): SIGTERM → wait 5s → SIGKILL if still alive → wait 2s
6. **Re-acquire arbiter** (line 222-228): `acquire_instance_lock(lock_path)` — authoritative success criterion

No kill path bypasses both guards. All `os.kill` calls with SIGTERM/SIGKILL are at lines 187 and 210, both inside `stop_daemon` after both guards pass (line 185 comment: "Both guards passed").

### SIGTERM handler verification

The handler is registered at `bellows.py:2602` inside `Bellows.start()`, after `observer` creation at line 2570:

```python
signal.signal(signal.SIGTERM, _sigterm_handler)
```

The `_sigterm_handler` closure (lines 2576-2600):
- Sets `self._shutting_down = True` (line 2582)
- Drains with 30s timeout checking `self._active_count == 0` (lines 2584-2591)
- On timeout, logs abandoned daemon threads as divergence hazard (lines 2592-2596)
- Stops `observer` and `self.response_server` (lines 2598-2599)
- Second signal during drain forces immediate exit via `sys.exit(1)` (line 2581)

Dispatch refusal gates confirmed at:
- `PlanHandler._handle` line 2031: `if self.orchestrator._shutting_down:`
- `Bellows.handle_new_plan` line 2178: `if self._shutting_down:`
- `Bellows.handle_parallel_group` line 2189: `if self._shutting_down:`

### (C) Live daemon

No signals sent to the live daemon (PID 3969). All verification via test suite and code reading.

---

### Ledger Updates

#### Prompt Feedback

Step 1's `_shutting_down` gate at `PlanHandler._handle` (line 2031) was correctly specified and implemented, but its interaction with 4 pre-existing tests that use `MagicMock()` orchestrators was not caught by the targeted test strategy. These tests auto-create truthy `_shutting_down` attributes. The fix is trivial (`mock_orch._shutting_down = False`), but since only targeted tests were specified for Steps 1-2, the regression was invisible until the full-suite QA run. A future plan adding a gate to a hot path like `_handle` should include a directive to audit existing mock-based tests for the new attribute.

---

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: /Users/marklehn/Developer/GitHub/bellows/.bellows-worktrees/430/knowledge/qa/evidence/bellows-restart-lock-fix-2026-08-15/
Files verified: 3
```
