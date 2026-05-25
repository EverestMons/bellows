# Dev Log: qa_steps Header Field for Authoritative QA-Step Detection

**Date:** 2026-05-25
**Plan:** executable-qa-steps-header-field-code-2026-05-25

## (a) Diff of `_gate_is_qa_step` — before/after

**Before (gates.py:556-562):**
```python
def _gate_is_qa_step(plan_text, step_number):
    plan_text = strip_fenced_code_blocks(plan_text)
    pattern = rf"^## STEP {step_number}\b[^\n]*"
    match = re.search(pattern, plan_text, re.MULTILINE)
    if match:
        return "qa" in match.group(0).lower()
    return False
```

**After (gates.py:556-575):**
```python
def _gate_is_qa_step(plan_text, step_number, plan_header=None):
    # Primary: check plan_header for qa_steps field
    if plan_header:
        qa_steps_raw = plan_header.get("qa_steps", "")
        if qa_steps_raw:
            try:
                # Handle YAML list case (e.g., [2, 4]) and string case (e.g., "2,4")
                if isinstance(qa_steps_raw, list):
                    return step_number in [int(x) for x in qa_steps_raw]
                qa_step_numbers = [int(s.strip()) for s in str(qa_steps_raw).split(",") if s.strip()]
                return step_number in qa_step_numbers
            except (ValueError, TypeError):
                logger.warning("qa_steps field malformed: %r — falling back to keyword detection", qa_steps_raw)

    # Fallback: keyword detection on step header (existing behavior)
    plan_text = strip_fenced_code_blocks(plan_text)
    pattern = rf"^## STEP {step_number}\b[^\n]*"
    match = re.search(pattern, plan_text, re.MULTILINE)
    if match:
        return "qa" in match.group(0).lower()
    return False
```

## (b) Diff of call site change in `check()`

**Before (gates.py:178):**
```python
    is_qa_step = _gate_is_qa_step(plan_text, step_number)
```

**After (gates.py:178):**
```python
    is_qa_step = _gate_is_qa_step(plan_text, step_number, plan_header=header)
```

The `header` variable is already in scope at this point — parsed earlier in `check()` via `_parse_plan_header(plan_text)`.

## (c) New test functions (7)

1. `test_qa_steps_field_single_step_matches` — qa_steps: "2", step 2 returns True
2. `test_qa_steps_field_single_step_excludes_other` — qa_steps: "2", step 1 returns False
3. `test_qa_steps_field_multi_step` — qa_steps: "1,3", step 1 True / step 2 False / step 3 True
4. `test_qa_steps_field_absent_falls_back_to_keyword` — no qa_steps, "QA" in header → True
5. `test_qa_steps_field_malformed_falls_back_to_keyword` — malformed qa_steps, keyword fallback fires with warning
6. `test_qa_steps_field_yaml_list` — qa_steps: [2, 4] (Python list), step 2 True / step 3 False
7. `test_qa_steps_field_non_qa_role_header` — leak vector closure: "Invoice Security & Testing Analyst" with qa_steps: "2" → True

## (d) Full-suite test counts

```
collected 406 items
401 passed, 5 failed, 1 warning
```

**5 pre-existing failures (all carry-overs, not regressions):**
- 3 × `test_decisions.py::TestLoadPhrases` (worktree artifact — INTERMEDIATE_DECISION_PHRASES.md missing)
- 1 × `test_decisions.py::TestExtractDecisionBlocks::test_s_class_blocks_from_ground_truth` (same worktree artifact)
- 1 × `test_runner_parser.py::test_run_step_timeout` (BACKLOG-documented runner mock mismatch)

**0 new regressions.**

## (e) Logger/warning pattern decisions

Used the existing `logger` variable (`logging.getLogger(__name__)` at gates.py:9) with `logger.warning()`. This matches the existing pattern at gates.py:98 (`logger.warning("YAML frontmatter parse failed, falling through to bold-Markdown: %s", e)`). No new logger setup was needed.

## (f) Output Receipt

**Agent:** Bellows Developer
**Status:** Complete
**Files changed:** gates.py, tests/test_gates.py, knowledge/development/qa-steps-header-field-2026-05-25.md
