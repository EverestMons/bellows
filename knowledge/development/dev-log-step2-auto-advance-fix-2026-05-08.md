# Dev Log: Step 2 Auto-Advance Fix (PLANNER_TEMPLATE + Bellows Warning)

**Date:** 2026-05-08 | **Plan:** executable-step2-auto-advance-fix-2026-05-08

## Summary

Implemented two independent fixes for the step 2 auto-advance bug diagnosed earlier today.

**Fix A — PLANNER_TEMPLATE update:** Added `pause_for_verdict: after_step_1` to the standard plan header format in the Output Format section (line 329). Added a new `### pause_for_verdict Header Field` subsection under the Bellows Execution Model section, explaining recognized values (`always`, `after_step_1`, `after_qa_step`), the default for multi-step plans, and the consequence of omission.

**Fix B — Bellows warning:** Added a one-shot advisory warning in `run_plan()` that fires when `total_steps > 1` AND the parsed header has no `pause_for_verdict` field. The warning is emitted at `bellows.py:268-269`, immediately after the `plan has N steps` log line — the earliest point where `plan_name`, `total_steps`, and `header` are all available. No behavioral change: `header_says_pause()` semantics are untouched, and auto-advance still happens for headerless plans.

**Key design note:** The `_parse_plan_header()` function only parses YAML frontmatter (files starting with `---`). Standard-format plans (starting with `# Title`) return `{}`, so the warning correctly fires for all standard-format multi-step plans — which is exactly the population that auto-advances. Plans using YAML frontmatter with `pause_for_verdict` declared suppress the warning.

## Tests

4 new tests added to `tests/test_bellows.py`:
1. `test_warning_multi_step_plan_without_pause_for_verdict` — 2-step plan, no header → warning fires exactly once
2. `test_no_warning_multi_step_plan_with_pause_for_verdict` — 2-step plan, YAML frontmatter with `after_step_1` → no warning
3. `test_no_warning_single_step_plan_without_pause_for_verdict` — 1-step plan, no header → no warning
4. `test_no_warning_multi_step_plan_with_pause_always` — 2-step plan, YAML frontmatter with `always` → no warning

All tests patch `_read_shadow`/`_write_shadow`/`_delete_shadow` to avoid shadow cache state bleed between test runs.

## Test Results

- Targeted: 4/4 passed
- Full suite: 227 passed, 1 failed (pre-existing `test_run_step_timeout`)
- Baseline: 223 passed, 1 failed → +4 new tests, 0 new regressions

---

## Output Receipt

### Status
Complete

### Files Created or Modified (Code)
- `/Users/marklehn/Desktop/GitHub/PLANNER_TEMPLATE.md` — Added `pause_for_verdict: after_step_1` to plan header format; added `### pause_for_verdict Header Field` subsection under Bellows Execution Model
- `bellows/bellows.py` — Added advisory warning at line 268-269 for multi-step plans missing `pause_for_verdict` header
- `bellows/tests/test_bellows.py` — Added 4 tests for the warning behavior (fires/suppressed conditions)

### Files Deposited
- `bellows/knowledge/development/dev-log-step2-auto-advance-fix-2026-05-08.md` (this file)

### Flags for CEO
None
