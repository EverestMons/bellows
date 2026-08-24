# 514 QA Report — Fixture Corrective (e2-corrective-fixtures)

**Date:** 2026-08-24
**Plan:** executable-514
**Step:** 2 (QA)
**Role:** QA — fresh agent, re-measure

---

## B1 — Full Suite

```
1288 passed, 1 warning in 43.18s
```

**Result: PASS** — 0 failed, 0 errors. 1288 collected (matches 513's baseline growth expectation).

The 513 red census was preserved as `pytest_full_513_red.txt` before overwrite:
- SHA-256: `20765e662442b96eaec08978a20e3319cbbc330b193dfeb1c0093e957dafccc8` (matches F1 pin)

Raw suite output: `knowledge/research/pytest_full.txt`

---

## B2 — Production Byte-Stability

```
git diff 8375058..HEAD -- bellows.py depositor.py lifecycle.py gates.py scripts/plan_lint.py tools/
```

**Result: EMPTY** — zero production-code changes. All listed files are byte-identical to F3 (`8375058`).

---

## B3 — Control Arm (Flip Negative Tests)

### Negative/refusal tests identified (F4):

| Test | Class | Result |
|---|---|---|
| `test_path_mismatch_refuses` | TestClearanceRoundTrip | PASSED |
| `test_consumed_refuses` | TestClearanceRoundTrip | PASSED |
| `test_no_clearance_row` | TestIsClaimableGate | PASSED |
| `test_drift` | TestIsClaimableGate | PASSED |
| `test_consumed` | TestIsClaimableGate | PASSED |
| `test_other_path_copy_refuses` | TestReplayPair | PASSED |
| `test_post_consumption_refuses` | TestReplayPair | PASSED |
| `test_never_adds_to_seen` | TestAutoHoldArm | PASSED |

All 39 tests in `tests/test_admission_flip.py` PASSED — 0 FAILED.

### Opt-in verification:

- `grep -c "autouse" tests/conftest.py` → **3** (unchanged from F3's value of 3)
- `grep -n "clear_plan_for_test" tests/test_admission_flip.py` → **no matches** — the helper is absent from every negative test

**Result: PASS** — the helper is opt-in only; negative/refusal tests are untouched and passing.

---

## Verification Table

| Check | Expected | Observed | Status |
|---|---|---|---|
| B1: Full suite | 0 failed, 0 errors | 1288 passed, 0 failed, 0 errors | PASS |
| B1: 513 census preserved | SHA `20765e6...` | SHA matches | PASS |
| B2: Production byte-stability | Empty diff | Empty diff | PASS |
| B3: Flip negative tests pass | All PASSED | All 8 refusal tests PASSED | PASS |
| B3: autouse count unchanged | 3 (from F3) | 3 | PASS |
| B3: clear_plan_for_test absent from flip tests | 0 matches | 0 matches | PASS |

---

## Flags

None.

---

## Rule 20 — QA Self-Check Results

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: /Users/marklehn/Developer/GitHub/bellows/.bellows-worktrees/514/knowledge/research/
Files verified: 3
```
