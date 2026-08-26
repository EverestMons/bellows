# QA Receipt — gates-cross-machine-paths (2026-08-26)

**Plan:** executable-564 | **Step:** 2 (QA) | **Date:** 2026-08-26

## Hygiene

**numstat (3 files):**
```
17	0	gates.py
50	0	knowledge/dev-logs/gates-cross-machine-paths-dev-2026-08-26.md
79	0	tests/test_gates_cross_machine_paths.py
```

**toplevel:** `/Users/marklehn/Developer/GitHub/bellows/.bellows-worktrees/564`

**reflog -n 4:**
```
1d63041 HEAD@{0}: reset: moving to HEAD
1d63041 HEAD@{1}: 
```
0 amends.

## Verification

| Item | Check | Status | Evidence |
|---|---|---|---|
| Full suite | 1509 passed, 0 failed, 1 warning (1503 + 6 new = 1509) | ✅ | `pytest_full.txt` |
| 560 replay | `_resolve_deposit_path('/Users/marklehn/Developer/bellows/hooks/eluvian/wrap_check.py', '/Users/marklehn/Developer/GitHub/bellows', None)` → `/Users/marklehn/Developer/GitHub/bellows/hooks/eluvian/wrap_check.py` (non-None) | ✅ | `probes-raw.txt` |
| Probe: Strategy 4 count | `grep -cF 'Strategy 4 (cross-machine re-root)' → 1` | ✅ | `probes-raw.txt` |
| Probe: rfind(marker) count | `grep -cF 'rfind(marker)' → 1` | ✅ | `probes-raw.txt` |
| Probe: fail-closed | function ends `return None` at line 379 | ✅ | `probes-raw.txt` |
| cmp: gates.py | `diff <(git show HEAD:gates.py) gates.py → exit 0` | ✅ | `probes-raw.txt` |
| cmp: test file | `diff <(git show HEAD:tests/...) tests/... → exit 0` | ✅ | `probes-raw.txt` |
| cmp: dev log | `diff <(git show HEAD:knowledge/...) knowledge/... → exit 0` | ✅ | `probes-raw.txt` |

## Daemon-staleness caveat

The running daemon keeps the old resolver until its next restart — the fix arms then. `/eluvian` surfaces the restart need. The restart stays a deliberate act; this QA step does not perform it.

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: knowledge/qa/evidence/gates-cross-machine-paths-2026-08-26/
Files verified: 3
```
