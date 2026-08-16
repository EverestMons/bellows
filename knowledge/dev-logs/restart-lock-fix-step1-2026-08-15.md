# Output Receipt — restart-lock fix Step 1

**Plan:** `bellows-restart-lock-fix-2026-08-15`
**Step:** 1 — self-diagnosing lock + SIGTERM drain handler
**Status:** Complete
**Commit:** `8066311` on branch `bellows-wt/430`
**Date:** 2026-08-15

---

## Thread-model finding

Worker threads are `daemon=True` — confirmed at two spawn sites:
- `bellows.py:2046` — `threading.Thread(..., daemon=True)` in `handle_new_plan`
- `bellows.py:2057` — `threading.Thread(..., daemon=True)` in `handle_parallel_group`

Because daemon threads are killed on main-thread exit, the SIGTERM drain handler is MANDATORY: it must wait for `_active_count == 0` before exiting. On drain timeout (30s) or second-signal override, in-flight daemon threads WILL be abandoned mid-transition — this re-enters the 2026-05-24 divergence hazard and is logged as an accepted last-resort.

## Edited ranges

### bellows.py

| Lines (post-edit) | Change |
|---|---|
| 10 | Added `import signal` |
| 48 | Added `_DRAIN_TIMEOUT = 30` constant |
| 51-91 | New `LockAcquireError` exception + `acquire_instance_lock(lock_path)` function — non-truncating open (`os.O_RDWR | os.O_CREAT`), flock acquire, PID+timestamp write on success, diagnostic error with holder identity on failure |
| 1994 | Added `self._shutting_down = False` to `Bellows.__init__` |
| 2011-2017 | `_run_tracked` — removed increment (moved to callers), kept `finally` decrement |
| 2040-2049 | `handle_new_plan` — added `_shutting_down` gate + pre-spawn increment under `_active_lock` |
| 2051-2063 | `handle_parallel_group` — added `_shutting_down` gate + per-path increment under `_active_lock` before thread creation |
| 1895-1897 | `PlanHandler._handle` — added `self.orchestrator._shutting_down` gate before dispatch |
| 2439-2462 | `_sigterm_handler` closure inside `Bellows.start()` — registered after `observer` creation; sets `_shutting_down`, drains with 30s timeout, stops observer + response_server, `sys.exit(0)` on clean drain. Second signal forces immediate exit via `sys.exit(1)`. |
| 2464 | `signal.signal(signal.SIGTERM, _sigterm_handler)` registration |
| 2561-2568 | `__main__` block — replaced old `open("w")` + inline flock with `acquire_instance_lock()` call, `LockAcquireError` catch |

### SIGINT coexistence

SIGTERM handler is registered alone. The existing `except KeyboardInterrupt: observer.stop()` at line 2531 remains intact. If Ctrl+C arrives during the SIGTERM drain loop, KeyboardInterrupt propagates out of the handler (the drain loop has no bare `except:`) and is caught by the existing handler at 2531, which calls `observer.stop()` — exactly one shutdown path fires.

## Test names and pass output

File: `tests/test_instance_lock.py`

| # | Test | What it proves |
|---|---|---|
| 1 | `test_acquire_writes_pid_and_timestamp` | After acquire, lock file contains this process's PID and a parseable ISO-8601 timestamp |
| 2 | `test_failure_includes_holder_pid` | Failure-branch error string includes the holder's PID |
| 2 (fallback) | `test_failure_falls_back_on_empty_file` | When lock file is empty (pre-deploy reality), falls back to generic error without crashing |
| 2b | `test_second_open_preserves_holder_pid` | A second open in the acquire path's exact mode (`O_RDWR|O_CREAT`) leaves the holder PID readable — MUST fail against the old `"w"` open |
| 3 | `test_shutting_down_refuses_dispatch` | `_shutting_down=True` causes `handle_new_plan` to return without starting a thread (`_active_count` stays 0) |
| 4 | `test_drain_waits_for_active_count_zero` | Drain pattern blocks while `_active_count > 0`, unblocks when it reaches 0 |

```
tests/test_instance_lock.py::test_acquire_writes_pid_and_timestamp PASSED
tests/test_instance_lock.py::test_failure_includes_holder_pid PASSED
tests/test_instance_lock.py::test_failure_falls_back_on_empty_file PASSED
tests/test_instance_lock.py::test_second_open_preserves_holder_pid PASSED
tests/test_instance_lock.py::test_shutting_down_refuses_dispatch PASSED
tests/test_instance_lock.py::test_drain_waits_for_active_count_zero PASSED
========================= 6 passed, 1 warning in 0.50s =========================
```

## Deviations

None. All tasks completed as specified.

---

### Ledger Updates

#### Prompt Feedback

The cold-panel corrections in the plan were essential and saved significant investigation time: (a) placing the SIGTERM handler registration inside `start()` rather than at module level was correct — `observer` is a local variable inside `start()`, unreachable from the module scope; (b) the `daemon=True` finding was confirmed at both spawn sites (lines 2046 and 2057), making the drain mandatory. The instruction to extract `acquire_instance_lock()` as a testable function was well-placed — it allowed all lock tests to exercise the production code path directly. The non-truncating open requirement (fold 2.1) was the most critical correctness constraint: without it, the second starter's `open("w")` truncates the holder's PID before the flock check, defeating the entire diagnostic feature.
