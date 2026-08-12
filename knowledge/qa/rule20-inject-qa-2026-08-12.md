# QA Report — rule20-inject-2026-08-12 (Plan 367, Step 2)

**Plan:** 367 (`rule20-inject-2026-08-12`)
**CAPTURE_COMMIT:** `fdf5dcd61f4dd74e0c22bdfa77ba005b276cf613`
**Date:** 2026-08-12

## Deliverable Verification

| # | Deliverable | Status | Evidence |
|---|---|---|---|
| 1 | `QA_MANDATE_SUFFIX` constant in gates.py | ✅ | `grep -cF 'QA_MANDATE_SUFFIX' gates.py` → 2 |
| 2 | `qa_mandate_suffix` function in gates.py | ✅ | `grep -cF 'def qa_mandate_suffix' gates.py` → 1 |
| 3 | Three call sites in bellows.py | ✅ | `grep -cF 'qa_mandate_suffix' bellows.py` → 3 |
| 4 | Diagnostic bootstrap excluded | ✅ | `grep -F 'single-step investigation' bellows.py \| grep -cF 'qa_mandate_suffix'` → 0 |
| 5 | tests/test_qa_mandate.py with ≥6 cases | ✅ | 6 passed in targeted run |
| 6 | gates.py numstat: insertions ≥ 10, deletions 0 | ✅ | 18/0 |
| 7 | bellows.py numstat: deletions ≤ 3 | ✅ | 3/3 |
| 8 | tests/test_qa_mandate.py numstat: all-insertions | ✅ | 49/0 |
| 9 | Committed SHAs == live SHAs | ✅ | gates.py and bellows.py both match |
| 10 | Porcelain clean for three paths | ✅ | empty porcelain output |
| 11 | Suffix contains banner literal byte-exact | ✅ | `'Rule 20 — QA Self-Check Results' in s` → True |
| 12 | Suffix contains PASSED literal byte-exact | ✅ | `'PASSED — SELF-CHECK PASSED' in s` → True |
| 13 | Non-QA step returns empty string | ✅ | step 1 → `''` |
| 14 | test_gates baseline 159/0 | ✅ | 159 passed, 0 failed |
| 15 | test_bellows baseline 180/0 | ✅ | 180 passed, 0 failed |

## Evidence and Narrative

All deliverables verified. The `qa_mandate_suffix` function routes through `_gate_is_qa_step` (single-source QA detection per C2) and returns the mandate suffix for QA steps, empty string otherwise. The three bellows.py call sites (step-1 bootstrap, resume bootstrap, default_next_prompt) append the suffix to their prompt f-strings. The diagnostic bootstrap is correctly excluded. The suffix text contains both banner literals byte-exact, ensuring the gate that checks for them will find them. All 345 targeted tests pass with zero failures, baselines hold.

### Receipt

- **CAPTURE_COMMIT:** `fdf5dcd61f4dd74e0c22bdfa77ba005b276cf613`
- **Numstat:** gates.py 18/0, bellows.py 3/3, tests/test_qa_mandate.py 49/0
- **Probes:** `def qa_mandate_suffix` 1, `QA_MANDATE_SUFFIX` 2, bellows.py suffix count 3, diagnostic clean 0
- **Tests:** 6 + 159 + 180 = 345 passed, 0 failures

### Ledger Updates

#### Forward Register

NONE

## Rule 20 — QA Self-Check

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: /Users/marklehn/Developer/GitHub/bellows/knowledge/qa/evidence/rule20-inject-2026-08-12/
Files verified: 3
```
