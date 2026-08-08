# QA Report — gate→verdict transaction-mechanization test (Plan 312, Step 2)

**Date:** 2026-08-07
**Plan:** executable-312 — gate→verdict transaction-mechanization test
**Step:** 2 (QA)
**Test file:** `tests/test_gate_transaction_mechanization.py`

---

## Task Q0 — Re-pin state

```
$ git log -1 --oneline -- tests/test_gate_transaction_mechanization.py
ab7137f [312] test: gate→verdict transaction-mechanization — pin mechanical guarantees and decided_by gap
```

Most recent commit is Step 1's `ab7137f`. No foreign commits. **PASS.**

---

## Verification

| # | Check | Status | Evidence |
|---|-------|--------|----------|
| 1 | Full `bellows` test suite passes | ✅ | `full-suite.txt` — `873 passed, 1 warning in 22.52s` |
| 2 | Targeted subset passes (5/5) | ✅ | `targeted-tests.txt` — `5 passed, 1 warning in 0.15s` |
| 3 | Invariant 1 — gate_events mechanical image: `test_single_failure_produces_exact_rows` PASSED, `test_all_failures_produces_zero_pass_rows` PASSED | ✅ | `targeted-tests.txt` |
| 4 | Invariant 2 — gates.check deterministic: `test_identical_inputs_produce_identical_outputs` PASSED, `test_failing_receipt_status` PASSED | ✅ | `targeted-tests.txt` |
| 5 | Invariant 3 — decided_by gap pinned: `test_both_verdicts_record_ceo` PASSED — asserts `rows[0] == (1, "ceo")` and `rows[1] == (2, "ceo")` | ✅ | `targeted-tests.txt`, source lines 170-172 |

---

## Rule 20 — QA Self-Check

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: knowledge/qa/
Files verified: 2
```

---

## QA Receipt

- **Full suite:** 873 passed, 1 warning in 22.52s
- **Targeted tests:** 5 passed, 1 warning in 0.15s
- **All three invariants pass.** Invariant 3 confirms both verdict rows carry `decided_by == "ceo"`, pinning the gap described in the plan.
- **Evidence files:** `full-suite.txt`, `targeted-tests.txt`
