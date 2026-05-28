# QA Report — Gate FP Coordinated Shape (2026-05-27)

**Plan:** `executable-gate-fp-coordinated-shape-2026-05-27`
**Agent:** Bellows QA
**Step:** 2
**Date:** 2026-05-27

---

## Verification Summary

| Deliverable | Status | Notes |
|---|---|---|
| A — Code shape verification | ✅ | All three fixes verified at correct line ranges |
| B — Per-fix FP reproduction tests | ✅ | 3 tests added, all pass |
| C — Per-fix counter-tests | ✅ | 3 tests added, all pass |
| D — Adjacent surface regression check | ✅ | 133 passed, 0 failed, 0.17s |
| E — Rule 20 self-check | ✅ | See output below |

**Flags for CEO:** None. No deviations from spec. No fixture modifications beyond the documented existing-test updates. No divergence from diagnostic predictions.

---

## Deliverable A — Code shape verification

### `_is_null_flag_declaration` (Fix 1)

- `gates.py:70` — `_NULL_FLAG_RE = re.compile(r'^(none|n/a|no flags?|nothing|clean|no issues)\b', re.IGNORECASE)`
- `gates.py:73-75` — `_is_null_flag_declaration(text: str) -> bool` helper
- `gates.py:247` — consumed by `_gate_ceo_flags`: `flags = [f for f in parsed.get("ceo_flags", []) if not _is_null_flag_declaration(f)]`

### `_gate_rule_22_verification` (c) defer-and-discard (Fix 2)

- `gates.py:560-561` — table-scoped state: `current_table_failures = []`, `current_table_has_positive_row = False`
- Flush points at 4 transitions: section header (567-570), non-pipe line (576-580), separator (584-588), end-of-loop (610-611)
- `gates.py:595-600` — explicit `❌` rows still fire immediately (bypass defer-and-discard)

### `_hedging_in_status_vicinity` (Fix 3)

- `gates.py:94-115` — `_hedging_in_status_vicinity(line: str, keyword: str) -> bool` helper
- `gates.py:614` — separate `in_verification_section_d = False` tracking
- `gates.py:620` — `if not in_verification_section_d: continue` as first check in loop body
- `gates.py:624` — `if _hedging_in_status_vicinity(line, kw):` replaces old `if kw in lower:`

### Unchanged files/helpers

- `parser.py` — `git diff b3b9646..7e67b0b -- parser.py` produces no output (confirmed unchanged)
- `_is_positive_status_row()` — function body unchanged in diff (only context lines, no +/- on its lines)

---

## Deliverable B — Per-fix FP reproduction tests

Three new tests added to `tests/test_gates.py`:

1. **`test_ceo_flags_null_declaration_prose_passes`** — uses exact triggering content from `processed-verdict-planner-template-bellows-operational-workarounds-2026-05-27-step-2.md`: `"None. All SA-cited anchor lines matched verbatim. No blueprint-vs-file mismatches. No prose adjustments needed."` Assertion: zero failures. **PASS**

2. **`test_rule_22_c_enumerative_table_inside_verification_section_passes`** — uses a `## Verification Checks` section containing a 3-column enumerative table (`| # | Line | Title |`) with no status column. Content shape from `plan-authoring-checklist-qa-2026-05-27.md`. Assertion: zero (c) failures. **PASS**

3. **`test_rule_22_d_pending_in_description_cell_passes`** — uses verification rows with `pending` in description cells (`_run_pending flag lifecycle`, `pending=0, in_progress`, `pending=5`) with `✅` in status cell. Content shape from `deferred-validation-status-card-2026-05-22-step-4`. Assertion: zero (d) failures. **PASS**

---

## Deliverable C — Per-fix counter-tests

Three counter-tests added to `tests/test_gates.py`:

1. **`test_ceo_flags_real_flag_still_fires`** — `ceo_flags=["warning: build failed on macOS"]` produces one failure. **PASS**

2. **`test_rule_22_c_genuine_missing_status_still_fires`** — verification table with one `✅` row and one empty-status row produces one (c) failure with "missing status". **PASS**

3. **`test_rule_22_d_pending_in_status_cell_still_fires`** — verification row with `✅ pending` in the status cell produces one (d) failure. **PASS**

---

## Deliverable D — Adjacent surface regression check

Full `tests/test_gates.py` suite output (last 20 lines):

```
tests/test_gates.py::test_rule_22_qa_hedging_keyword PASSED              [ 84%]
tests/test_gates.py::test_rule_22_qa_both_fail_and_hedging PASSED        [ 84%]
tests/test_gates.py::test_rule_22_qa_report_missing PASSED               [ 85%]
tests/test_gates.py::test_rule_20_self_check_scopes_to_first_md_deposit_ignoring_incidental_banner_in_other_deposits PASSED [ 86%]
tests/test_gates.py::test_rule_20_self_check_fails_when_first_md_deposit_lacks_passed_line PASSED [ 87%]
tests/test_gates.py::test_rule_20_self_check_distinguishes_no_md_paths_from_missing_banner PASSED [ 87%]
tests/test_gates.py::test_rule_22_verification_c_skips_non_verification_section_tables PASSED [ 88%]
tests/test_gates.py::test_rule_22_verification_c_accepts_text_pass_status PASSED [ 89%]
tests/test_gates.py::test_rule_22_verification_c_flags_genuine_missing_status_in_verification_table PASSED [ 90%]
tests/test_gates.py::test_qa_steps_field_single_step_matches PASSED      [ 90%]
tests/test_gates.py::test_qa_steps_field_single_step_excludes_other PASSED [ 91%]
tests/test_gates.py::test_qa_steps_field_multi_step PASSED               [ 92%]
tests/test_gates.py::test_qa_steps_field_absent_falls_back_to_keyword PASSED [ 93%]
tests/test_gates.py::test_qa_steps_field_malformed_falls_back_to_keyword PASSED [ 93%]
tests/test_gates.py::test_qa_steps_field_yaml_list PASSED                [ 94%]
tests/test_gates.py::test_qa_steps_field_non_qa_role_header PASSED       [ 95%]
tests/test_gates.py::test_ceo_flags_null_declaration_prose_passes PASSED [ 96%]
tests/test_gates.py::test_rule_22_c_enumerative_table_inside_verification_section_passes PASSED [ 96%]
tests/test_gates.py::test_rule_22_d_pending_in_description_cell_passes PASSED [ 97%]
tests/test_gates.py::test_ceo_flags_real_flag_still_fires PASSED         [ 98%]
tests/test_gates.py::test_rule_22_c_genuine_missing_status_still_fires PASSED [ 99%]
tests/test_gates.py::test_rule_22_d_pending_in_status_cell_still_fires PASSED [100%]

======================== 133 passed, 1 warning in 0.17s ========================
```

**Total:** 133 tests | **Passed:** 133 | **Failed:** 0 | **Skipped:** 0 | **Time:** 0.17s

### Adjacent surface pass-through confirmation

- All existing `_gate_ceo_flags` tests: PASS (parser-side null-token handling untouched)
- All existing (c) check tests with `## Deliverable Verification` header fixtures (2026-05-24 Shape 6C): PASS
- All existing (d) check hedging tests where keyword appears in status cell: PASS
- Two existing tests updated per DEV log flags:
  - `test_rule_22_qa_hedging_keyword` — added `## Deliverable Verification` header + moved "assumed" to status cell
  - `test_rule_22_qa_both_fail_and_hedging` — moved "estimated" to status cell (`✅ estimated`)

---

## Deliverable E — Rule 20 self-check

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: knowledge/qa/evidence/gate-fp-coordinated-shape-2026-05-27/
Files verified: 0
```

RULE 20 SELF-CHECK: PASSED

---

## Output Receipt

**Agent:** Bellows QA
**Step:** 2
**Status:** Complete

### What Was Done
Verified all three gate-FP fixes (CEO Flags null-token allowlist, Rule 22 (c) defer-and-discard, Rule 22 (d) cell-scope match). Added 6 new tests (3 FP reproduction + 3 counter-tests). Updated 2 existing test fixtures per DEV log flags. Full test suite: 133 passed, 0 failed.

### Files Deposited
- `knowledge/qa/executable-gate-fp-coordinated-shape-2026-05-27.md` — this QA report
- `tests/test_gates.py` — 6 new tests added, 2 existing test fixtures updated

### Files Created or Modified (Code)
- `tests/test_gates.py` — 6 new tests + 2 fixture updates

### Decisions Made
- Updated `test_rule_22_qa_hedging_keyword` fixture: added `## Deliverable Verification` header and moved hedging keyword to status cell (per DEV log flags)
- Updated `test_rule_22_qa_both_fail_and_hedging` fixture: moved "estimated" to status cell (per DEV log flags)

### Flags for CEO
- None

### Flags for Next Step
- Daemon restart required to load new `gates.py` (Bellows does not hot-reload gate code)
