# QA Receipt — debt-date-arm — 2026-09-17 [100126]

**Plan:** bellows — drop the debt caller's 3b date arm (thread 53, CEO ruling 2026-09-17)
**Step:** 2 — QA
**Date:** 2026-09-17

## Diff (3c37f1c8..8df429e9) — two DEV commits, seven files

```
2	1	hooks/commands/wrap.md
10	2	hooks/eluvian/wrap_check.py
113	0	knowledge/development/dev-log-debt-date-arm-2026-09-17.md
26	0	knowledge/mutants/debt-date-arm.json
11	0	knowledge/mutants/debt-date-arm.run.txt
25	5	tests/test_wrap_3b_keyed.py
5	0	tests/test_wrap_r2_registry.py
```

## Verification

| Item | Description | Status |
|------|-------------|--------|
| 1 | 9 deliverable checks: dev-log headings 1+1+1; `4 failed` count 2; mutation line `MUTATION: 3 killed, 0 survived, 0 error`; `caller == "debt"` count 2; wrap.md phrase count 1; test-def count 5; mutants count 3; suite 2527 passed, two skips | ✅ |
| 2 | Seven named nodes verbose: 7 passed | ✅ |
| 3 | Scratch fixture: call 1 exit 0 (debt path, no 3b arm); controls exit 1 (date fallback), exit 1 (session arm); hook exit 0; counts `[3b/lessons]`=2, date-form=1, sid-form=1, envelope=0, empty-json=1 | ✅ |
| 4 | `hooks/commands/wrap.md` line 97: "the debt hook does not read this line — since thread 53 it reports only the repo state a wrap leaves behind" | ✅ |
| 5 | 4 files written, 0 others; 0 lane files, 0 lifecycle rows, 0 daemon invocations | ✅ |

### Ledger Updates

#### Project Status
**bellows #100126 (thread 53, 2026-09-17):** `wrap_check.check` caller `"debt"` no longer reads the sweep line. The `if caller == "debt" or not session_id:` branch is split into `if caller == "debt": pass` / `elif not session_id:` — the date arm is removed and the sid-less Stop's date fallback is preserved. Seven paths across two DEV commits: `hooks/eluvian/wrap_check.py`, `hooks/commands/wrap.md`, `tests/test_wrap_3b_keyed.py` (three tests added for Arm 5: `test_debt_caller_stale_line_no_3b`, `test_debt_caller_no_sweep_line_no_3b`, `test_debt_caller_without_sid_no_3b`), `tests/test_wrap_r2_registry.py`, `knowledge/mutants/debt-date-arm.json`, `knowledge/development/dev-log-debt-date-arm-2026-09-17.md`, `knowledge/mutants/debt-date-arm.run.txt`. UNWRAPPED SESSION DEBT DETECTED envelope count falls 1→0 on the fixture's clean tree; hook empty `{}` rises 0→1. Suite: 2527 passed, 3 mutants killed.
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: /Users/marklehn/Developer/bellows/.bellows-worktrees/100126/knowledge/qa/evidence/
Files verified: 3
