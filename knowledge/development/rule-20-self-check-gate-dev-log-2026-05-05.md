# Rule 20 Self-Check Verification Gate — Dev Log

**Date:** 2026-05-05
**Plan:** `executable-rule-20-self-check-gate-2026-05-05`

---

## Summary of Changes

Added a new blocking gate (`_gate_rule_20_self_check`) to `gates.py` that detects Rule 20 self-check fabrication and omission in QA-deposited reports. The gate runs only on QA steps (gate 6 `is_qa_step` is True), reads the deposited QA report file, and verifies the literal banner string `Rule 20 — QA Self-Check Results` is present AND a line starting with `PASSED — SELF-CHECK PASSED` follows it. Refactored `_resolve_deposit_path` to return the resolved absolute path string (or `None`) instead of a boolean, enabling the new gate to read deposit files by path.

---

## File-Level Diff Summary

### `gates.py`

- **`_resolve_deposit_path` (Part A refactor):** Changed return type from `bool` to `str | None`. Returns `os.path.abspath(resolved)` when found, `None` when not found. Updated docstring accordingly.
- **`_gate_deposit_exists`:** Updated two call sites to use `is None` instead of `not` for the refactored return type.
- **`_gate_rule_20_self_check` (Part B new gate):** Added new blocking gate function. Signature: `(is_qa_step, plan_text, step_number, project_path, parsed, failures)`. Behavior: no-op on non-QA steps; extracts step deposits; resolves `.md` deposit paths; reads file content; checks for banner + PASSED line ordering; appends to `failures` with three evidence message variants.
- **`check()` dispatcher:** Registered new gate after gate 6 (`is_qa_step` computation) as gate 6b.

### `tests/test_gates.py`

- **Updated 4 existing `_resolve_deposit_path` tests:** Changed assertions from `is True`/`is False` to `is not None`/`is None` + `os.path.isabs()` checks to match the refactored return type.
- **Added 6 new Rule 20 gate tests:** (a) passes with valid banner + PASSED line, (b) fails when banner missing, (c) fails when banner present but PASSED line missing, (d) fails when deposit unreadable (overlaps with gate 5), (e) skipped on non-QA step, (f) passes with multi-section report.
- **Added 2 new `_resolve_deposit_path` refactor tests:** (g) returns absolute path when found, (h) returns None when not found.

---

## Test Results Summary

### Targeted Bucket (`tests/test_gates.py`)

- **Result:** 46 passed in 0.05s
- **Breakdown:** 38 existing tests (4 updated for refactor) + 8 new tests

### Full Suite

- **Baseline (pre-change):** 1 failed (`test_run_step_timeout` — pre-existing), 197 passed
- **Post-change:** 1 failed (`test_run_step_timeout` — same pre-existing), 205 passed
- **New failures:** 0
- **Delta:** +8 tests (all new tests for Rule 20 gate + refactor)

---

## Output Receipt
**Agent:** Bellows Developer
**Step:** 1
**Status:** Complete

### What Was Done
Implemented the Rule 20 self-check verification gate in `gates.py` with full test coverage. Refactored `_resolve_deposit_path` to return resolved path or None. Registered the new gate in the `check()` dispatcher. Added 8 new tests covering all specified scenarios. All tests pass with no regressions.

### Files Deposited
- `bellows/knowledge/development/rule-20-self-check-gate-dev-log-2026-05-05.md` — this dev log

### Files Created or Modified (Code)
- `bellows/gates.py` — refactored `_resolve_deposit_path` return type; added `_gate_rule_20_self_check` gate function; registered gate in `check()` dispatcher
- `bellows/tests/test_gates.py` — updated 4 existing tests for refactor; added 8 new tests (6 for new gate + 2 for refactor)

### Decisions Made
- Placed new gate registration as "Gate 6b" between gate 6 and gate 7 in `check()`, since it depends on `is_qa_step` from gate 6
- Used `os.path.abspath()` in `_resolve_deposit_path` for consistent absolute path returns
- New gate checks all `.md` deposits (not just primary) for the Rule 20 banner — handles multi-deposit QA steps

### Flags for CEO
- None

### Flags for Next Step
- The test count is 46 (not 38 as estimated in the plan) because the test file had 38 existing tests, not 30. All pass.
- The pre-existing `test_run_step_timeout` failure is unrelated to this change.
