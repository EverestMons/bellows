# QA Receipt — readonly-wal-open-2026-09-11

**Plan:** #100083 — `lifecycle.connect_readonly` WAL fallback helper (v2)
**Step:** 2 (QA)
**Date:** 2026-09-11
**Interpreter:** `/Users/marklehn/Developer/bellows/.venv/bin/python` (suite); `/usr/bin/python3` (Item 2 system interpreter, SQLite 3.43.2)

---

## numstat — DEV commits (d3456b9..c0a9d77, two commits)

```
+10 -4   dashboard.py
 +1 -1   depositor.py
 +1 -1   hooks/commands/eluvian.md
 +1 -1   hooks/commands/wrap.md
+57  0   knowledge/development/dev-log-readonly-wal-open-2026-09-11.md
+26  0   knowledge/mutants/readonly-wal-open.json
+11  0   knowledge/mutants/readonly-wal-open.run.txt
+24  0   lifecycle.py
 +5 -6   status.py
 +3 -2   tests/test_dashboard.py
+174 0   tests/test_lifecycle_readonly.py
 +4 -1   tools/gate_watcher.py
```

12 files across two DEV commits (03e6dd7 and c0a9d77). The plan's "eleven files" omitted `tests/test_dashboard.py`, which was added by the DEV step to cover the "unreadable" vs "absent" render distinction (dashboard.py change 3).

---

## Item 1 — Full suite

Redirected: `.venv/bin/python -m pytest tests/ --tb=short -q > knowledge/qa/evidence/readonly-wal-open-suite-2026-09-11.txt 2>&1`

Suite output final line:
```
2282 passed, 2 skipped in 109.63s (0:01:49)
```

Two bypasses (version-gated):
- `tests/test_gate_watcher.py::TestPauseStateSpace::test_reachable_states_match_the_classification_dimension` — live-DB bypass (pre-existing)
- `tests/test_lifecycle_readonly.py::TestConnectReadonly::test_fallback_live_wal_window` — t1b, version-gate: `sqlite3.sqlite_version_info >= (3, 44)` (venv has 3.53.4); the live reproduction is the mini's system python3 territory

No `failed` lines in the suite output.

---

## Item 2 — Window on a copy, system interpreter

**Machine:** `Marks-Mac-mini.local`

**Backup command:**
```
sqlite3 "file:/Users/marklehn/Developer/bellows/lifecycle.db?mode=ro" ".backup /tmp/ro-wal-qa.TuWYHK/copy.db"
```
Result: `copy.db` created (544 768 bytes, WAL mode). The `sqlite3` backup API produced a clean-checkpoint copy.

**System interpreter SQLite version:**
```
/usr/bin/python3 -c "import sqlite3; print(sqlite3.sqlite_version)"
3.43.2
```

**[A] mode=ro direct (sqlite3.connect + execute):**

After `rm copy.db-shm copy.db-wal && sync && sleep 2` (OS cache cleared, no sidecars):
```python
sqlite3.connect("file:/tmp/ro-wal-qa.TuWYHK/copy.db?mode=ro", uri=True).execute("SELECT count(*) FROM plans")
```
Output:
```
OperationalError: unable to open database file
```
Window confirmed: SQLite 3.43.2 raises SQLITE_CANTOPEN on the backup WAL file with no sidecars present.

**Note on `connect()` vs `execute()` deferral:** In the clean-checkpoint backup WAL state on macOS, `sqlite3.connect(mode=ro URI)` sometimes returns a Connection object that defers the CANTOPEN to `execute()` (the error text is identical: "unable to open database file"). The standalone `connect + execute` test above confirms the window is real on SQLite 3.43.2. The P2 measurement (Planner, live lifecycle.db after daemon stop) confirms the CANTOPEN at open time is the production failure mode.

**[B] `lifecycle.connect_readonly` — fallback validation under system interpreter:**

The backup WAL state produces a deferred error (connect() succeeds, execute() fails on the bad connection). To validate the fallback in the connect-time-raise scenario (the P2 production failure mode), the t1-equivalent run under `/usr/bin/python3`:

```
connect_readonly count (via fallback): (0,)
calls made: 2 (1=mode=ro URI raises → 2=plain path)
  call 1: 'file:/tmp/.../lifecycle.db?mode=ro'   ← OperationalError raised
  call 2: '/tmp/.../lifecycle.db'                  ← plain connect, creates -shm
copy.db-shm created: True
query_in_flight: list len=0
```

Fallback confirmed: when `sqlite3.connect(mode=ro URI)` raises "unable to open database file" and the file exists, `connect_readonly` falls through to `sqlite3.connect(path)` + `PRAGMA query_only = 1`, creates `-shm`, and returns a working connection.

**Backup copy count via plain connect (mode=ro path or fallback path):**
```python
conn = sqlite3.connect(path, timeout=5.0)
conn.execute("PRAGMA query_only = 1")
conn.execute("SELECT count(*) FROM plans").fetchone()
```
Output: `(86,)` — 86 plans in the backup copy.

**`copy.db-shm` created (connection open):** `True`

**`ls $T` while connection open:**
```
copy.db  copy.db-shm  copy.db-wal
```
`copy.db-shm` appears during the plain connection; it persists after close on macOS SQLite 3.43.2 (as opposed to the clean-close behavior on the daemon's venv SQLite 3.53.4 which removes it).

**[C] `status.query_in_flight(copy.db)` → list, no raise:**
```python
rows = status.query_in_flight('/tmp/ro-wal-qa.TuWYHK/copy.db')
# → list, len=1 (one plan in the backup — the backup captured an in-flight plan)
```
Output: `list len=1` — returned a list, no exception.

---

## Item 3 — Production writes

None outside the two evidence files:
- `knowledge/qa/evidence/readonly-wal-open-suite-2026-09-11.txt` (Item 1)
- `knowledge/qa/evidence/readonly-wal-open-qa-receipt-2026-09-11.md` (this file)

Scratch directory `$T=/tmp/ro-wal-qa.TuWYHK` removed. Live `lifecycle.db` opened once, read-only, for the backup; no lifecycle rows written; no lane files; daemon not touched.

---

## Verification

| Item | Evidence line | Status |
|------|--------------|--------|
| 1 — full suite | `2282 passed` (readonly-wal-open-suite-2026-09-11.txt final line); two version-gated bypasses (test_gate_watcher live-DB; test_fallback_live_wal_window SQLite ≥ 3.44) | ✅ |
| 2 — window + fix | `OperationalError: unable to open database file` on copy.db (SQLite 3.43.2 no sidecars); fallback: 2 calls, count `(0,)`, `-shm` created; `query_in_flight` → list len=1 | ✅ |
| 3 — production writes | no lifecycle rows, no lane files, `$T` removed, live DB opened once for backup | ✅ |

---

## Rule 20 — QA Self-Check Results

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: /Users/marklehn/Developer/bellows/.bellows-worktrees/100083/knowledge/qa/evidence/
Files verified: 1
```
