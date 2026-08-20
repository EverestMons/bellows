# QA Report — Component 3: In-Bellows Depositor + Dashboard DEPOSITS Panel

**Date:** 2026-08-20
**Plan:** executable-481, Step 2
**Dispatch:** bellows worktree (bellows-wt/481)

## Verification Table

| # | Check | Status | Evidence |
|---|-------|--------|----------|
| 1 | Targeted tests — 24/24 depositor tests pass | ✅ | targeted.txt |
| 2 | Full suite — 1177/1177 pass, 0 fail | ✅ | full_suite.txt |
| 3 | Live canary — read-only CLEAR | ✅ | live_canary.txt |
| 4 | Live canary — register-writing HOLD | ✅ | live_canary.txt |
| 5 | Live canary — class-mismatch HOLD (D2) | ✅ | live_canary.txt |
| 6 | Live canary — sibling collision HOLD (V2) | ✅ | live_canary.txt |
| 7 | Live canary — live knowledge/decisions/ unchanged | ✅ | live_canary.txt |
| 8 | Safety invariant — grep depositor.py for forbidden imports returns empty | ✅ | inline (exit code 1 = no match) |
| 9 | Scope — git diff --stat shows only bellows/ files (7 files changed) | ✅ | inline |

## Evidence Summary

### (1) Targeted Tests
24 depositor-specific tests pass: import whitelist (W1), class assignment (3), class mismatch (D2), collision detection (5 including file-vs-file, prefix-vs-file, prefix-vs-prefix per V4), fail-safe empty writes (DISC-4), clear mechanics, hold mechanics (A3), handle additive (D1), handle wiring (DISC-5), concurrent evaluate (W2/R4), restart re-eval (A2), Path B legacy extraction (EXEC-2), dashboard DEPOSITS rendering (3), disk low, clear deletes stale .hold.json (DISC-6).

### (2) Full Suite
1177 tests pass, 0 failures, 0 errors. No regressions.

### (3) Live Canary (scratch-only, V1)
Scratch project at /tmp/depositor-canary/ with seeded lifecycle.db containing a known in-flight plan (writes∩writes collision target). All 4 scenarios correct:
- Scenario 1: read-only plan with no collision → CLEARED (renamed to claimable)
- Scenario 2: register-writing plan → HELD with reason class:register-writing
- Scenario 3: declared read-only but writes governed register → HELD with reason class_mismatch (the catastrophic path, D2)
- Scenario 4: two colliding ready- siblings → HELD with reason collision:writes∩writes
Live knowledge/decisions/ confirmed byte-unchanged (git status --porcelain clean).

### (4) Safety Invariant
`grep -nE 'mint_and_claim|run_plan|handle_new_plan' depositor.py` returns exit code 1 (no matches). The depositor imports and calls no dispatch function.

### (5) Scope
`git diff --stat main...HEAD` shows 7 files, 1345 insertions, 5 deletions — all within bellows/:
- depositor.py (new, 550 lines)
- bellows.py (32 lines modified)
- dashboard.py (54 lines added)
- status.py (18 lines added)
- tests/test_depositor.py (new, 618 lines)
- tests/test_dashboard.py (9 lines modified)
- knowledge/development/component3-depositor-2026-08-20.md (new, 69 lines)

============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: /Users/marklehn/Developer/GitHub/bellows/.bellows-worktrees/481/knowledge/qa/evidence/executable-component3-depositor-2026-08-20/
Files verified: 3
