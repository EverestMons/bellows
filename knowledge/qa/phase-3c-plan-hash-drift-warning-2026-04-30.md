# QA Report — Phase 3c: Plan-Hash Drift Warning

**Date:** 2026-04-30
**Plan:** executable-phase-3c-plan-hash-drift-warning-2026-04-30
**Step 1 Commit:** `a30dd6d` — "phase 3c: plan-hash drift warning + test"

---

## Deliverable Verification

| Deliverable | Expected | Status | Evidence |
|---|---|---|---|
| `import hashlib` in bellows.py | `^import hashlib` matches | ✅ | `grep_hashlib_import.txt` — line 3 |
| Warning block in bellows.py | `Plan Modified` matches (1+), `hashlib.sha256` matches (2+) | ✅ | `grep_warning_block.txt` — line 254 (title), lines 250+251 (hashes) |
| Test function in test_bellows.py | `def test_run_plan_plan_hash_drift_warning` matches | ✅ | `grep_test_function.txt` — line 1855 |

---

## Test Regression

**Command:** `python3 -m pytest tests/test_bellows.py --tb=short`
**Result:** 71 collected, 71 passed, 0 failed
**Evidence:** `pytest_targeted.txt`

The 1 known pre-existing failure (`test_run_step_timeout`) lives in `tests/test_runner_parser.py` and is not picked up by `tests/test_bellows.py`. Clean 71/71.

---

## Behavioral Smoke

**Command:** Hash "AAA" and "BBB" via `hashlib.sha256(...).hexdigest()[:12]`
**Result:**
- `sha256(AAA)[:12]` = `cb1ad2119d8f`
- `sha256(BBB)[:12]` = `dcdb704109a4`
- Differ: True

Confirms `hashlib` import landed correctly and truncated hex comparison works as expected.
**Evidence:** `hash_smoke.txt`

---

## Rule 20 Self-Check

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: bellows/knowledge/qa/evidence/phase-3c-plan-hash-drift-warning-2026-04-30/
Files verified: 5
```
