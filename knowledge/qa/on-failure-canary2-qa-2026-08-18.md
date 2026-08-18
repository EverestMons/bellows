# QA Report — on_failure canary #2

**Plan:** `executable-on-failure-canary2-2026-08-18.md`
**Step:** 2 (QA — full suite)
**Date:** 2026-08-18
**known_failures:** 0

## Test run

```
python3 -m pytest tests/ -q 2>&1 | cat
1105 passed, 1 warning in 31.15s
```

## Verification table

| Check | Status | Evidence |
|---|---|---|
| Full suite passes (0 failed, 0 errors) | ✅ | `evidence/on-failure-canary2-2026-08-18/full-suite.txt` |
| Result matches known_failures: 0 | ✅ | 1105 passed, 0 failed, 0 errors |
| Raw output deposited | ✅ | `evidence/on-failure-canary2-2026-08-18/full-suite.txt` |

## Rule 20 — QA Self-Check Results

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: /Users/marklehn/Developer/GitHub/bellows/.bellows-worktrees/443/knowledge/qa/evidence/on-failure-canary2-2026-08-18/
Files verified: 1
```

**PASSED — SELF-CHECK PASSED**
