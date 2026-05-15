# QA Report — Rule 20 Self-Check Verification Gate

**Date:** 2026-05-05
**Plan:** `executable-rule-20-self-check-gate-2026-05-05`
**Agent:** Bellows QA
**Step:** 2

---

## Deliverable Verification

| Deliverable | Expected | Status | Evidence |
|---|---|---|---|
| `_gate_rule_20_self_check` function in `gates.py` | Signature: `(is_qa_step, plan_text, step_number, project_path, parsed, failures)` | ✅ | `evidence/grep_new_gate.txt` |
| `_resolve_deposit_path` refactored to return path-or-None | Returns `os.path.abspath(...)` or `None`, no `return True`/`return False` | ✅ | `evidence/grep_resolve_refactor.txt` |
| New gate registered in `check()` after gate 6 | Call site appears after `is_qa_step = _gate_is_qa_step(...)` | ✅ | `evidence/grep_registration.txt` |
| 8 new tests in `test_gates.py` | 6 for new gate + 2 for refactor | ✅ | `evidence/grep_new_tests.txt` (8 lines) |

---

## Targeted Test Results (`tests/test_gates.py`)

**Result:** 46 passed in 0.03s

| Test | Expected | Status | Evidence |
|---|---|---|---|
| `test_rule_20_self_check_passes_with_valid_banner_and_passed_line` | PASS | ✅ | `evidence/pytest_targeted.txt` |
| `test_rule_20_self_check_fails_when_banner_missing` | PASS | ✅ | `evidence/pytest_targeted.txt` |
| `test_rule_20_self_check_fails_when_banner_without_passed_line` | PASS | ✅ | `evidence/pytest_targeted.txt` |
| `test_rule_20_self_check_fails_when_deposit_unreadable` | PASS | ✅ | `evidence/pytest_targeted.txt` |
| `test_rule_20_self_check_..._on_non_qa_step` (no-op gate) | PASS | ✅ | `evidence/pytest_targeted.txt` |
| `test_rule_20_self_check_passes_when_passed_line_after_banner_in_multi_section_report` | PASS | ✅ | `evidence/pytest_targeted.txt` |
| `test_resolve_deposit_path_returns_absolute_path_when_found` | PASS | ✅ | `evidence/pytest_targeted.txt` |
| `test_resolve_deposit_path_returns_none_when_not_found` | PASS | ✅ | `evidence/pytest_targeted.txt` |

---

## Full Suite Results

| Metric | Baseline (pre-change) | Post-change | Delta |
|---|---|---|---|
| Passed | 197 | 205 | +8 (new tests) |
| Failed | 1 (`test_run_step_timeout`) | 1 (`test_run_step_timeout`) | 0 |
| Regressions | — | 0 | OK |

Evidence: `evidence/pytest_full.txt`

---

## Smoke Test Results (4 Scenarios)

| Scenario | Input | Expected | Actual | Status |
|---|---|---|---|---|
| (i) Banner + PASSED | QA step, deposit with banner and PASSED line | Gate passes, no `rule_20_self_check` failure | `passed=True`, 0 rule_20 failures | ✅ |
| (ii) Banner without PASSED | QA step, deposit with banner, FAILED line | Gate fails with "banner present but PASSED line missing" | `passed=False`, evidence matches | ✅ |
| (iii) No banner | QA step, deposit with no banner | Gate fails with "no QA deposit contains Rule 20 self-check banner" | `passed=False`, evidence matches | ✅ |
| (iv) DEV step | DEV step (non-QA), any deposit content | Gate is no-op, no `rule_20_self_check` failure | 0 rule_20 failures | ✅ |

Evidence: `evidence/smoke_scenarios.txt`

---

## Rule 20 — QA Self-Check

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: knowledge/qa/evidence/executable-rule-20-self-check-gate-2026-05-05/
Files verified: 7
```

---

## Output Receipt
**Agent:** Bellows QA
**Step:** 2
**Status:** Complete

### What Was Done
Verified all Step 1 deliverables (gate function, refactor, registration, tests). Ran targeted test bucket (46/46 pass), full suite (205 pass, 1 pre-existing failure, 0 regressions), and 4-scenario live smoke test (all pass). Updated PROJECT_STATUS.md with milestone entry. Rule 20 self-check PASSED.

### Files Deposited
- `bellows/knowledge/qa/rule-20-self-check-gate-qa-report-2026-05-05.md` — this QA report
- `bellows/knowledge/qa/evidence/executable-rule-20-self-check-gate-2026-05-05/` — 7 evidence files

### Files Created or Modified (Code)
- None (QA verification only)

### Decisions Made
- None (mechanical verification)

### Flags for CEO
- None

### Flags for Next Step
- None — plan is ready for Rule 22 verification and terminal close
