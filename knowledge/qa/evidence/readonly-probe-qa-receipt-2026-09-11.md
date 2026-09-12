# QA Receipt — readonly-probe — 2026-09-11

**Plan:** #100089 | **Step:** 2 (QA) | **Date:** 2026-09-11

## DEV commits numstat (031e2a3..f389305)

```
49	0	knowledge/development/dev-log-readonly-probe-2026-09-11.md
33	0	knowledge/mutants/readonly-probe.json
12	0	knowledge/mutants/readonly-probe.run.txt
10	1	lifecycle.py
87	0	tests/test_lifecycle_readonly.py
```

## Verification

| Item | Description | Evidence | Status |
|------|-------------|----------|--------|
| 1 | Full suite redirected — summary line: `2302 passed` — two skips (test_gate_watcher live-DB; test_fallback_live_wal_window version gate) | `readonly-probe-suite-2026-09-11.txt` last line | ✅ |
| 2 | Five attempts on copies of the live DB under `/usr/bin/python3` (SQLite 3.43.2) using `execute("PRAGMA schema_version").fetchone()` (the opener's own probe statement): attempt 1 `raised at first query`; attempt 2 `raised at first query`; attempt 3 `raised at first query`; attempt 4 `raised at first query`; attempt 5 `raised at first query` — 0 raised at connect, 5 raised at first query. Live DB opened once, read-only, for the backup: `sqlite3 "file:/Users/marklehn/Developer/bellows/lifecycle.db?mode=ro" ".backup $T/base.db"` | Item 2 stdout | ✅ |
| 3 | Production writes: none outside the two evidence files; `$T` removed; no lane file, no live lifecycle row, no daemon act | this receipt | ✅ |


============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: /Users/marklehn/Developer/bellows/.bellows-worktrees/100089/knowledge/qa/evidence/
Files verified: 1
