# QA Report — Planner Contract Validators: Three-Validator Drop

**Date:** 2026-05-20
**Plan:** `executable-planner-contract-validators-three-validator-drop-2026-05-20`
**Agent:** Bellows QA
**Dev Log:** `knowledge/development/planner-contract-validators-three-validator-drop-2026-05-20.md`

---

## CEO Restart Required

The Bellows daemon does NOT hot-reload Python modules. These three validators will take effect in live plan dispatch only after a daemon restart.

---

## Deliverable Verification (Rule 17)

| Deliverable | Expected | Status | Evidence |
|---|---|---|---|
| V1 production code | `_consume_verdicts()` in `bellows.py` emits WARN + notification on malformed verdict filename (file starts with `verdict-` but doesn't match slug-step regex and isn't `processed-*` or `verdict-request-*`) | ✅ | grep_v1_prod.txt |
| V1 tests | `tests/test_bellows.py` contains ≥3 tests covering positive/negative/boundary cases for malformed verdict filename | ✅ | grep_v1_test.txt |
| V2 production code | `validators.py` contains `check_pause_for_verdict_value` function with enum check against `{"always", "after_step_1", "after_qa_step", "after_each_step", ""}` | ✅ | grep_v2_prod.txt |
| V2 registration | `check_pause_for_verdict_value` is called inside `validate_at_claim` | ✅ | grep_v2_reg.txt |
| V2 tests | `tests/test_validators.py` contains ≥3 tests covering positive/negative/boundary cases for pause_for_verdict enum | ✅ | grep_v2_test.txt |
| V3 production code | `validators.py` contains `check_header_field_types` function enumerating `auto_close`, `pause_for_verdict`, `dispatch_mode` for string-type check | ✅ | grep_v3_prod.txt |
| V3 registration | `check_header_field_types` is called inside `validate_at_claim` | ✅ | grep_v3_reg.txt |
| V3 tests | `tests/test_validators.py` contains ≥3 tests covering positive/negative/boundary cases for header field types | ✅ | grep_v3_test.txt |

### Verification Details

**V1 production code:** `bellows.py:1125-1126` — WARN log with filename and expected pattern + `verdict._notify_malformed_verdict()` call. Located inside `_consume_verdicts()` (line 1106), immediately before the existing `continue` on regex non-match. Confirmed: file still skipped after logging.

**V1 tests:** 4 tests in `tests/test_bellows.py`:
- `test_consume_verdicts_malformed_filename_logs_warn_and_notifies` — negative case: malformed filename triggers WARN + notification
- `test_consume_verdicts_malformed_filename_still_skipped` — behavioral: malformed file is skipped (check_verdict not called)
- `test_consume_verdicts_valid_filename_not_flagged` — positive case: correctly-formatted filename produces no warning
- `test_consume_verdicts_verdict_request_not_flagged_as_malformed` — boundary case: verdict-request-* files excluded before format check

**V2 production code:** `validators.py:121-138` — `VALID_PAUSE_FOR_VERDICT_VALUES` set at line 121, `check_pause_for_verdict_value()` at line 126. String coercion via `str(raw).strip().lower()` before enum check. Returns WARN-level dict with invalid value and expected enum in message.

**V2 registration:** `validators.py:195` — `check_pause_for_verdict_value(header)` called inside `validate_at_claim()`, result appended to warnings list.

**V2 tests:** 4 tests in `tests/test_validators.py`:
- `test_pause_for_verdict_valid_values_no_warning` — positive: all 5 valid values produce no warning
- `test_pause_for_verdict_invalid_values_warn` — negative: 5 plausible YAML-think values all produce WARN
- `test_pause_for_verdict_absent_no_warning` — boundary: absent field handled gracefully
- `test_pause_for_verdict_warn_surfaces_in_validate_at_claim` — integration: warning surfaces in orchestrator output

**V3 production code:** `validators.py:123,141-152` — `STRING_TYPED_HEADER_FIELDS` tuple at line 123, `check_header_field_types()` at line 141. Iterates fields, checks `isinstance(value, str)` when value is not None.

**V3 registration:** `validators.py:200` — `check_header_field_types(header)` called inside `validate_at_claim()`, results extended into warnings list.

**V3 tests:** 7 tests in `tests/test_validators.py`:
- `test_header_field_types_all_strings_no_warning` — positive: all-string fields pass silently
- `test_header_field_types_bool_warns` — negative: YAML bool produces WARN
- `test_header_field_types_int_warns` — negative: YAML int produces WARN
- `test_header_field_types_none_value_no_warning` — boundary: None treated as absent
- `test_header_field_types_absent_fields_no_warning` — boundary: missing fields pass silently
- `test_header_field_types_multiple_non_string_fields` — boundary: multiple violations each produce own warning
- `test_header_field_types_warn_surfaces_in_validate_at_claim` — integration: warning surfaces in orchestrator output

---

## Targeted Test Results (Rule 21)

**Scope:** targeted (changes scoped to `validators.py`, `bellows.py` verdict consumption, and dedicated test files)

**Command:** `python3 -m pytest tests/test_validators.py tests/test_bellows.py -v`

**Result:** 140 passed, 0 failed

**Evidence:** `knowledge/qa/evidence/executable-planner-contract-validators-three-validator-drop-2026-05-20/pytest_targeted.txt`

---

## DEV Deviations Noted

1. **V2 enum set extended:** DEV added `after_each_step` to the valid set (plan specified `{"always", "after_step_1", "after_qa_step", ""}`). Verified: `after_each_step` is used in plan headers (this plan itself uses it). Extension is correct — prevents false positives on valid plans.

2. **Notification helper reuse:** DEV called `verdict._notify_malformed_verdict()` from `bellows.py` (cross-module via existing import). Verified: dedup key `("malformed_content")` has no collision risk — files with malformed filenames never reach the content validator.

---

## Rule 20 — QA Self-Check

**Output:**

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: /Users/marklehn/Developer/GitHub/bellows/.bellows-worktrees/planner-contract-validators-three-validator-drop-2026-05-20/knowledge/qa/evidence/executable-planner-contract-validators-three-validator-drop-2026-05-20/
Files verified: 9
```

---

## Output Receipt
**Agent:** Bellows QA
**Step:** 2
**Status:** Complete

### What Was Done
Verified all 3 validators (V1 verdict filename format, V2 pause_for_verdict enum, V3 header field types) per Rule 17 deliverable verification. Ran targeted tests (140 passed). Updated PROJECT_STATUS.md with milestone entry. Produced QA report with evidence files.

### Files Deposited
- `knowledge/qa/planner-contract-validators-three-validator-drop-qa-2026-05-20.md` — this QA report
- `knowledge/qa/evidence/executable-planner-contract-validators-three-validator-drop-2026-05-20/` — 9 evidence files (8 grep + 1 pytest)

### Files Created or Modified (Code)
- `PROJECT_STATUS.md` — added milestone entry for Planner Contract Validators V1+V2+V3

### Decisions Made
- Confirmed DEV's `after_each_step` enum extension is correct (used in live plan headers)
- Confirmed cross-module notification helper reuse has no dedup collision risk

### Flags for CEO
- **Restart required:** Bellows daemon must be restarted for these validators to take effect on live plan dispatch

### Flags for Next Step
- None (terminal QA step — Planner performs Rule 22 verification and Done/ move)
