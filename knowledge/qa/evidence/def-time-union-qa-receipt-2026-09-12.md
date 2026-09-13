# QA Receipt — def-time-union — 2026-09-12 [100095]

## DEV numstat (713b423..42be298)

```
36	0	knowledge/development/dev-log-def-time-union-2026-09-12.md
12	0	knowledge/mutants/def-time-union.json
9	0	knowledge/mutants/def-time-union.run.txt
66	0	tests/test_tools_safe_to_invoke.py
1	0	tools/fold_signal_census.py
1	0	tools/gate_failopen_census.py
```

## Verification

| # | Check | Evidence | Status |
|---|-------|----------|--------|
| 1 | Full suite | `2314 passed, two skips (test_gate_watcher live-DB; test_fallback_live_wal_window version gate)` — last line of `def-time-union-suite-2026-09-12.txt` | ✅ |
| 2 | Both tools under Python 3.9; t6 PASSED | `usage: fold_signal_census.py [-h] [--json] [--max-pairs MAX_PAIRS]`; `usage: gate_failopen_census.py [-h] [--verbose] [--module MODULE]`; `tests/test_tools_safe_to_invoke.py::test_no_def_time_union_without_future_import PASSED` | ✅ |
| 3 | Production writes | None outside the two evidence files; T removed; no lane file, no lifecycle row, no daemon act | ✅ |

============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: /Users/marklehn/Developer/bellows/.bellows-worktrees/100095/knowledge/qa/evidence/
Files verified: 1
