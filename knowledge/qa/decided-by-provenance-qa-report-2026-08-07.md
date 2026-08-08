# QA Report — decided_by provenance (gate_auto vs verdict_file)

**Plan:** 313 — record decided_by transition provenance
**Date:** 2026-08-07
**Step:** 2 (QA)
**Baseline:** 873 passed (plan 312 QA)
**Fresh count:** 874 passed (Task D added one test)

---

## Q0 — State Re-pin

```
$ git -C /Users/marklehn/Developer/GitHub/bellows log -1 --oneline -- bellows.py tests/test_gate_transaction_mechanization.py
1f735e1 [313] dev: decided_by provenance — gate_auto vs verdict_file discrimination
```

Most recent commit touching both files is Step 1's. ✅

---

## Item 1 — Full Test Suite

```
874 passed, 1 warning in 22.23s
```

Raw output deposited in `full-suite.txt`.

---

## Item 2 — Targeted Test Subset

Command: `python3 -m pytest tests/test_gate_transaction_mechanization.py tests/test_bellows.py -k "verdict or decided or auto_close or transaction" --tb=short -q`

```
38 passed, 148 deselected, 1 warning in 0.68s
```

Raw output deposited in `targeted-tests.txt`.

---

## Item 3 — Grep Confirmation

**`grep -F 'decided_by="gate_auto"' bellows.py`** — exits 0, prints:
```
            lifecycle.record_verdict_outcome(plan_id, current_step, "continue", decided_by="gate_auto")
```

**`grep -F 'decided_by="verdict_file"' bellows.py`** — exits 0, prints:
```
                        lifecycle.record_verdict_outcome(_lc_plan_id, step_number, v, decided_by="verdict_file", disposition_summary=reason)
```

**`grep -F 'decided_by="ceo"' bellows.py`** — exits 1, prints nothing. The old literal is fully replaced.

---

## Verification Summary

| # | Check | Status | Evidence |
|---|-------|--------|----------|
| 1 | Full test suite passes | ✅ | 874 passed, 1 warning — `full-suite.txt` |
| 2 | Targeted tests pass | ✅ | 38 passed, 148 deselected — `targeted-tests.txt` |
| 3a | `gate_auto` literal present in bellows.py | ✅ | grep exits 0, one line printed |
| 3b | `verdict_file` literal present in bellows.py | ✅ | grep exits 0, one line printed |
| 3c | `ceo` literal absent from bellows.py | ✅ | grep exits 1, no output |
| 4 | Rule 20 self-check passes | ✅ | See block output below |

---

## Rule 20 Self-Check

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: /Users/marklehn/Developer/GitHub/bellows/knowledge/qa/
Files verified: 2
```
