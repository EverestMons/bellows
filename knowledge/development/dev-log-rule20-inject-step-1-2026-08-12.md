# Dev Log — rule20-inject Step 1 (2026-08-12)

**Plan:** 367 (`rule20-inject-2026-08-12`)
**CAPTURE_COMMIT:** `fdf5dcd61f4dd74e0c22bdfa77ba005b276cf613`

## Numstat

| File | Insertions | Deletions |
|---|---|---|
| gates.py | 18 | 0 |
| bellows.py | 3 | 3 |
| tests/test_qa_mandate.py | 49 | 0 |

## Probes

| Probe | Value |
|---|---|
| `grep -cF 'def qa_mandate_suffix' gates.py` | 1 |
| `grep -cF 'QA_MANDATE_SUFFIX' gates.py` | 2 |
| `grep -cF 'qa_mandate_suffix' bellows.py` | 3 |
| diagnostic bootstrap clean | 0 (confirmed) |

## Test Tallies

| Module | Passed |
|---|---|
| tests/test_qa_mandate.py | 6 |
| tests/test_gates.py | 159 |
| tests/test_bellows.py | 180 |
| **Total** | **345** |

Zero failures.

## What Changed

- **gates.py:** Added `QA_MANDATE_SUFFIX` constant and `qa_mandate_suffix(plan_text, step_number, plan_header=None)` function directly after `_gate_is_qa_step`. The function routes through `_gate_is_qa_step` (single-source QA detection) and returns the suffix for QA steps, empty string otherwise.
- **bellows.py:** Appended `{gates.qa_mandate_suffix(plan_text, <step>, header)}` to three prompt f-strings: (1) step-1 bootstrap with step `1`, (2) resume bootstrap with step `resume_step`, (3) `default_next_prompt` with step `current_step + 1`. The diagnostic bootstrap is excluded (confirmed clean).
- **tests/test_qa_mandate.py:** New test module with 6 cases covering header numeric, non-QA step, header list form, keyword fallback, no step heading (diagnostic shape), and banner literal presence.

#### Prompt Feedback

None.

#### Forward Register

NONE
