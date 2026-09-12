# Dev log — readonly-probe — 2026-09-11

## Pins re-derived (P1, P3)

#100083's QA receipt `knowledge/qa/evidence/readonly-wal-open-qa-receipt-2026-09-11.md`, its Item 2: a `.backup` of the live DB as `copy.db`, then `rm copy.db-shm copy.db-wal && sync && sleep 2`, then under `/usr/bin/python3` (SQLite 3.43.2) `sqlite3.connect("file:<copy>?mode=ro", uri=True).execute("SELECT count(*) FROM plans")` → `OperationalError: unable to open database file`; its note: the `mode=ro` connect "sometimes returns a Connection object that defers the CANTOPEN to `execute()` (the error text is identical)"; #100083's P2 (a tmp DB after `init_lifecycle_db`, sidecars removed, the same interpreter) raised at connect

**P1 re-derived (`sed -n '452,480p' lifecycle.py`):**

`lifecycle.py:452` `def connect_readonly(db_path, timeout=5.0):` — after the edit: `ro = None`; `try: ro = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True, timeout=timeout)`; `ro.execute("PRAGMA schema_version").fetchone()`; `return ro`; `except sqlite3.OperationalError as exc:` closes `ro` if not None (nested try/except Exception: pass around `ro.close()`), then `if "unable to open database file" not in str(exc) or not os.path.exists(db_path): raise`; then `conn = sqlite3.connect(db_path, timeout=timeout)`, `conn.execute("PRAGMA query_only = 1")`, `return conn`; callers `status.py:231` and `:251` (`conn = connect_readonly(db_path)`), `depositor.py:564` (`conn = lifecycle.connect_readonly(self._db_path)`), `tools/gate_watcher.py:68` (`conn = connect_readonly(path, timeout=5)`)

**P3 re-derived (first 160 lines of `tests/test_lifecycle_readonly.py`):**

`tests/test_lifecycle_readonly.py`, `class TestConnectReadonly`: t1 `test_fallback_on_file_uri_error`, t1b `test_fallback_live_wal_window` (`skipif sqlite3.sqlite_version_info >= (3, 44)`), t2 `test_uri_reads_when_writer_open`, t3 `test_missing_file_propagates`, t4 `test_fallback_connection_is_readonly`, t5 `test_resolve_in_flight_writes_returns_list`, t6 `test_no_mode_ro_outside_lifecycle`, `test_no_python3_status_in_hooks`; the module preamble loads the worktree's `status.py` by path (`importlib.util.spec_from_file_location`). t7–t9 not yet present (as expected — this step adds them).

No mechanism mismatch: no probe read inside the opener's `try`, no close of the read-only connection present before this step.

## Failing-first (red, then green)

Red (t7–t9 added, before lifecycle.py edit): `3 failed, 7 passed, 1 skipped in 0.27s`

Three reasons:
- t7 (`test_fallback_on_deferred_refusal`): `assert False is True` — the stand-in was returned unprobed and never closed; `deferred.closed` was still `False`
- t8 (`test_deferred_other_error_propagates`): `Failed: DID NOT RAISE <ExceptionInfo OperationalError() tblen=...>` — the stand-in was returned directly; `connect_readonly` did not raise
- t9 (`test_status_reads_through_deferred_refusal`): `sqlite3.OperationalError: unable to open database file` — raised inside `status.query_in_flight` when the stand-in's `execute` ran

Green (after lifecycle.py edit):
- Readonly file: `10 passed, 1 skipped in 0.20s`
- Full suite: `2302 passed, 2 skipped in 112.31s`

## The two forms caught (t7, t8)

**t7 `test_fallback_on_deferred_refusal`** — wrapper returns `_DeferredRefusal()` for `file:` connects; after fix, `ro.execute("PRAGMA schema_version")` raises inside the `try`; `ro.close()` is called; fallback runs.

Assertions and outcomes:
- `assert deferred.closed is True` → PASSES (close was called before the fallback path)
- `assert len(calls) == 2` → PASSES (first: `file:` uri; second: plain path)
- `assert conn.execute("SELECT count(*) FROM plans").fetchone() == (0,)` → PASSES (real fallback connection)
- `assert conn.execute("PRAGMA query_only").fetchone() == (1,)` → PASSES

**t8 `test_deferred_other_error_propagates`** — wrapper returns `_DeferredRefusal("database is locked")`; after fix, `ro.execute("PRAGMA schema_version")` raises `OperationalError("database is locked")`; `ro.close()` is called; message test sees `"unable to open database file" not in "database is locked"` → True → re-raises.

Assertions and outcomes:
- `with pytest.raises(sqlite3.OperationalError, match="locked")` → PASSES (exception re-raised)
- `assert deferred.closed is True` → PASSES (close ran before the re-raise)
- `assert len(calls) == 1` → PASSES (no fallback connect)

## Mutation run

`MUTATION: 4 killed, 0 survived, 0 error`
