# Output Receipt — restart-lock fix Step 2

**Plan:** `bellows-restart-lock-fix-2026-08-15`
**Step:** 2 — standalone guarded stop path + dashboard wiring
**Status:** Complete
**Commit:** `39c96f6` on branch `bellows-wt/430`
**Date:** 2026-08-15

---

## Entry-point choice + rationale

Implemented the stop path as `bellows.py stop`/`bellows.py restart` CLI arguments rather than a separate `bellows_ctl.py`. Rationale: the stop logic (`stop_daemon`, `_discover_holder`, `_verify_identity`, `_check_idle`) shares imports and constants with bellows.py (signal, subprocess, fcntl, `acquire_instance_lock`, `LockAcquireError`). Putting it in the same file avoids a new module and keeps the guard sequence co-located with the lock-acquire path it builds on. The dashboard calls the stop path via `subprocess.run([sys.executable, "bellows.py", "stop"])` to avoid importing bellows.py (which pulls in heavy dependencies including server, lifecycle, notifier modules).

## Edited ranges

### bellows.py

| Lines (post-edit) | Change |
|---|---|
| 94-96 | `_STOP_SIGTERM_TIMEOUT = 5`, `_STOP_SIGKILL_TIMEOUT = 2` — documented as mirroring `dashboard.py:34-35`, not imported to avoid curses dependency |
| 99-120 | `_discover_holder(lock_path)` — calls `lsof -t`, refuses if >1 PID (ambiguous) or 0 PIDs |
| 123-132 | `_verify_identity(pid)` — identity guard via `ps -o command= -p <pid>`, checks for `bellows.py` |
| 135-152 | `_check_idle(db_path, config)` — idle guard via `status.query_in_flight`; refuses only on `status='running'`; `awaiting_verdict`/NULL do NOT block; orphaned in-progress files do NOT block |
| 155-228 | `stop_daemon(lock_path, db_path, config)` — ordered guard sequence: (1) flock acquire → (2) lsof discover → (3) identity guard → (4) idle guard → (5) SIGTERM → SIGKILL → (6) re-acquire arbiter |
| 2673-2691 | `__main__` stop/restart CLI: parses `sys.argv[1]`, calls `stop_daemon`, spawns fresh process on restart |

### dashboard.py

| Lines (post-edit) | Change |
|---|---|
| 397-421 | `_do_restart` — after `_terminate_child` + `_wait_for_lock_release` fails, delegates to `subprocess.run([sys.executable, "bellows.py", "stop"])` then retries lock release before respawning |
| 439-455 | `_main_loop` initial spawn — checks `status.probe_daemon` before spawning; if lock held by incumbent, displays "press r to restart" message instead of spawning a child that would immediately fail at the flock guard |

## Guard sequence reconciliation

**Idle guard — `in_progress ≠ running`:** The idle guard refuses ONLY when `query_in_flight` returns a row with `status='running'`. Rows with `awaiting_verdict` or NULL status represent a paused/idle daemon (the common stop target — a daemon sitting on `pause_for_verdict`). Orphaned `in-progress-*` files with no corresponding `running` row are the stuck state the operator is trying to clear — they must NOT block the stop.

**Stop path does NOT assume incumbent has the drain handler:** The SIGTERM is safe because the idle guard has already confirmed no plans are `running`. A handler-less daemon (e.g. PID 3969) receiving SIGTERM while idle exits via Python's default `SystemExit` with no mid-transition risk.

## Test names and pass output

File: `tests/test_stop_path.py`

| # | Test | What it proves |
|---|---|---|
| 1 | `test_acquire_succeeds_no_incumbent` | Flock acquire succeeds → reports "no running daemon", no kill attempted |
| 2 | `test_identity_mismatch_refuses` | PID holds lock but `ps` shows it's not bellows.py → REFUSE, no signal sent |
| 3 | `test_idle_guard_running_refuses` | DB has `status='running'` row → REFUSE, no signal sent |
| 4 | `test_both_guards_pass_sigterm_then_sigkill` | Both guards pass → SIGTERM sent; dummy process ignores SIGTERM → SIGKILL escalation; re-acquire succeeds (arbiter) |
| 5 | `test_reacquire_race_lost_refuses` | After kill, re-acquire fails (another process raced) → REFUSE |
| 6 | `test_ambiguous_lsof_refuses` | lsof returns >1 PID → REFUSE (ambiguous), no signal sent |
| 7 | `test_idle_guard_passes_awaiting_verdict_with_orphan` | `awaiting_verdict` row + orphaned in-progress file (no running row) → idle guard PASSES |

```
tests/test_stop_path.py::test_acquire_succeeds_no_incumbent PASSED
tests/test_stop_path.py::test_identity_mismatch_refuses PASSED
tests/test_stop_path.py::test_idle_guard_running_refuses PASSED
tests/test_stop_path.py::test_both_guards_pass_sigterm_then_sigkill PASSED
tests/test_stop_path.py::test_reacquire_race_lost_refuses PASSED
tests/test_stop_path.py::test_ambiguous_lsof_refuses PASSED
tests/test_stop_path.py::test_idle_guard_passes_awaiting_verdict_with_orphan PASSED
tests/test_instance_lock.py::test_acquire_writes_pid_and_timestamp PASSED
tests/test_instance_lock.py::test_failure_includes_holder_pid PASSED
tests/test_instance_lock.py::test_failure_falls_back_on_empty_file PASSED
tests/test_instance_lock.py::test_second_open_preserves_holder_pid PASSED
tests/test_instance_lock.py::test_shutting_down_refuses_dispatch PASSED
tests/test_instance_lock.py::test_drain_waits_for_active_count_zero PASSED
======================== 13 passed, 1 warning in 4.91s =========================
```

## Deviations

None. All tasks completed as specified.

---

### Ledger Updates

#### Prompt Feedback

The plan's explicit guard sequence ordering and refuse-by-default principle made the implementation straightforward — each guard maps to a clean function with a binary pass/refuse return. The requirement to use subprocess for the dashboard→bellows stop delegation (avoiding heavy bellows.py imports in dashboard.py) was the right call — it maintains clean module separation while keeping the guard sequence in one authoritative location. The cold-panel correction about orphaned in-progress files (they must NOT block the stop) was essential for test 7 and for the operational correctness of the Full scope: without it, a stuck daemon with an orphaned in-progress file from a prior crash would be unstoppable, defeating the entire purpose.
