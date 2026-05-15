# Fence-Strip Plan Text Parsers — Development Log

**Date:** 2026-05-11 | **Plan:** executable-fence-strip-plan-text-parsers-2026-05-11 | **Step:** 1

---

## Import-vs-Duplicate Decision (Part B)

**Decision: Duplicate.** `bellows.py` imports `gates` at line 35 (`import gates`), creating a circular import if `gates.py` were to `from bellows import strip_fenced_code_blocks`. The same applies to `verdict.py` which is imported by `bellows.py` transitively through gates. The function is duplicated in all three files (`bellows.py`, `gates.py`, `verdict.py`) with matching "keep in sync" comments pointing back to `bellows.py` as the canonical copy. This follows the same pattern as the existing `_extract_step_text` / `_extract_step_text_from_plan` duplication.

---

## LOC Delta Per File

| File | Lines Added | Lines Modified | Net Delta |
|---|---|---|---|
| `bellows.py` | +10 (utility function) | +1 (call-site strip in `extract_total_steps`) | +11 |
| `gates.py` | +10 (utility function) | +2 (call-site strips in `_extract_step_text`, `_gate_is_qa_step`) | +12 |
| `verdict.py` | +10 (utility function) | +1 (call-site strip in `_extract_step_text_from_plan`) | +11 |
| `tests/test_bellows.py` | +38 (2 tests: `test_strip_fenced_code_blocks_basic`, `test_extract_total_steps_ignores_in_fence_headers`) | 0 | +38 |
| `tests/test_gates.py` | +36 (2 tests: `test_extract_step_text_ignores_in_fence_headers`, `test_gate_is_qa_step_ignores_in_fence_headers`) | 0 | +36 |
| `tests/test_verdict.py` | +18 (1 test: `test_extract_step_text_from_plan_ignores_in_fence_headers`) | 0 | +18 |
| **Total** | | | **+126** |

---

## Test Count Delta

- **Before:** 181 tests across the 3 test files
- **After:** 186 tests (+5 new tests)
- **New tests:**
  1. `test_strip_fenced_code_blocks_basic` (test_bellows.py) — utility unit test
  2. `test_extract_total_steps_ignores_in_fence_headers` (test_bellows.py) — regression test
  3. `test_extract_step_text_ignores_in_fence_headers` (test_gates.py) — regression test
  4. `test_gate_is_qa_step_ignores_in_fence_headers` (test_gates.py) — baseline + regression test
  5. `test_extract_step_text_from_plan_ignores_in_fence_headers` (test_verdict.py) — baseline + regression test

---

## Decisions Made Within Specialist Authority

1. **Duplicate path chosen over import path** for circular-import avoidance (see above). This is within specialist authority per the existing precedent set by `_extract_step_text` / `_extract_step_text_from_plan`.
2. **Regex approach used** (not state machine) per diagnostic Q6 recommendation — `re.sub(r"^```[^\n]*\n.*?^```[^\n]*$", "", text, flags=re.MULTILINE | re.DOTALL)`. Handles all plans in the current population.
3. **Strip applied at function entry** (inside each parser function), not at caller, despite the plan text suggesting "at the call site". Applying inside the function is safer because it protects all callers, and the performance cost is negligible (these functions are called once per step dispatch).

---

## Output Receipt
**Agent:** Bellows Developer
**Step:** 1
**Status:** Complete

### What Was Done
Added `strip_fenced_code_blocks()` utility function (duplicated in bellows.py, gates.py, verdict.py for circular-import avoidance) and applied it at the entry point of all 4 BUG-CONFIRMED parsers. Added 5 regression/baseline tests covering all affected parsers plus the utility itself. All 186 tests pass with no regressions.

### Files Deposited
- `bellows/knowledge/development/fence-strip-plan-text-parsers-2026-05-11.md` — this dev log
- `bellows/knowledge/qa/evidence/executable-fence-strip-plan-text-parsers-2026-05-11/pytest_targeted.txt` — full test output

### Files Created or Modified (Code)
- `bellows/bellows.py` — added `strip_fenced_code_blocks()`, applied in `extract_total_steps()`
- `bellows/gates.py` — added `strip_fenced_code_blocks()` (duplicate), applied in `_extract_step_text()` and `_gate_is_qa_step()`
- `bellows/verdict.py` — added `strip_fenced_code_blocks()` (duplicate), applied in `_extract_step_text_from_plan()`
- `bellows/tests/test_bellows.py` — added `test_strip_fenced_code_blocks_basic`, `test_extract_total_steps_ignores_in_fence_headers`
- `bellows/tests/test_gates.py` — added `test_extract_step_text_ignores_in_fence_headers`, `test_gate_is_qa_step_ignores_in_fence_headers`
- `bellows/tests/test_verdict.py` — added `test_extract_step_text_from_plan_ignores_in_fence_headers`

### Decisions Made
- Chose duplicate path over import path for `strip_fenced_code_blocks` (circular-import avoidance)
- Applied strip inside parser functions rather than at external call sites

### Flags for CEO
- None

### Flags for Next Step
- The QA agent should verify the "keep in sync" comments are present in all 3 copies of `strip_fenced_code_blocks`
- `_gate_is_qa_step` test is the first-ever test for that function (baseline, not just regression)
