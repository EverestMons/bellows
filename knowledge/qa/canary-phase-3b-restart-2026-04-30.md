# QA Report — Phase 3b Restart Canary

**Date:** 2026-04-30
**Plan:** executable-canary-phase-3b-restart-2026-04-30
**Step:** 2 (QA)
**Result:** PASS

---

## Deliverable Verification (Step 1 DEV)

| Deliverable | Expected | Status | Evidence |
|---|---|---|---|
| `knowledge/research/phase-3b-restart-canary-2026-04-30.md` | Exists on disk | ✅ | `os.path.isfile` confirms |
| `knowledge/research/agent-prompt-feedback.md` | Exists on disk | ✅ | `os.path.isfile` confirms |

---

## Phase 3b DB Assertions

| Assertion | Expected | Status | Evidence |
|---|---|---|---|
| `plan_slug` column in `runs` table | Column present in PRAGMA output | ✅ | `knowledge/qa/evidence/canary-phase-3b-restart-2026-04-30/pragma_runs.txt` — row `(11, 'plan_slug', 'TEXT', 0, None, 0)` |
| Canary run row with non-NULL `plan_slug` | At least one row matching slug | ✅ | `knowledge/qa/evidence/canary-phase-3b-restart-2026-04-30/canary_run_rows.txt` — `('canary-phase-3b-restart-2026-04-30', '...in-progress-executable-canary-phase-3b-restart-2026-04-30.md', 1, 'Complete')` |
| `_get_last_completed_step` returns 1 | Integer 1 | ✅ | `knowledge/qa/evidence/canary-phase-3b-restart-2026-04-30/get_last_step.txt` — value: `1` |

---

## Test Regression

- **Command:** `pytest tests/test_bellows.py -x --tb=short`
- **Result:** 70 collected, 70 passed, 0 failed
- **Evidence:** `knowledge/qa/evidence/canary-phase-3b-restart-2026-04-30/pytest_targeted.txt`
- **Regression:** None detected

---

## Rule 20 Self-Check

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: bellows/knowledge/qa/evidence/canary-phase-3b-restart-2026-04-30/
Files verified: 4
```
