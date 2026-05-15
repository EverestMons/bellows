# Dev Log — R3 Variant (c): Shadow Cache Read-Only Prompt
**Date:** 2026-04-19 | **Blueprint:** r3-shadow-cache-blueprint-2026-04-19

## Starting SHA
`0fba5a18d72e1a39e3fd0487e1866572365a5fc8`

## Implementation Summary

Implemented the R3 variant (c) per SA blueprint sections B1–B5. B1 required no new helper (existing `_shadow_path` reused). B4 found no gap (no housekeeping fallback needed). Two commits:

### Commit 1 — B3: Prompt f-string updates
**SHA:** `6b085b8`
- Added `shadow_prompt_path = str(_shadow_path(plan_filename))` before the prompt construction block
- Replaced `{plan_path}` with `{shadow_prompt_path}` at lines 241, 243, 245
- Replaced `{inprogress_path}` with `{shadow_prompt_path}` at line 301
- **Test results after commit:** 113 passed, 12 failed (11 pre-existing test_runner.py/test_runner_parser.py + 1 expected failure in `test_run_plan_bootstrap_prompt_uses_inprogress_path` which still asserted old path)

### Commit 2 — B5: Test changes
**SHA:** `5297a06`
- Renamed `test_run_plan_bootstrap_prompt_uses_inprogress_path` → `test_run_plan_bootstrap_prompt_uses_shadow_path` with updated assertions (shadow path present, in-progress absent)
- Updated `test_run_plan_resume_step_uses_correct_prompt` with shadow path assertions
- Added `test_run_plan_continuation_prompt_uses_shadow_path` — exercises mid-loop continuation (2-step plan, captures second prompt)
- Added `test_run_plan_diagnostic_prompt_uses_shadow_path` — exercises diagnostic variant
- Added `test_run_plan_resume_prompt_uses_shadow_path` — exercises verdict-continue resume variant
- Added `test_shadow_path_resolves_after_claim` — verifies shadow file exists with pristine content during runner execution
- **Test results after commit:** 118 passed, 11 failed (all 11 pre-existing in test_runner.py/test_runner_parser.py)

## Files Created or Modified (Code)

| File | Change |
|---|---|
| `bellows/bellows.py` | Added `shadow_prompt_path` variable; replaced `{plan_path}`/`{inprogress_path}` with `{shadow_prompt_path}` in 4 prompt f-strings (lines 241, 243, 245, 302) |
| `bellows/tests/test_bellows.py` | Renamed+updated 1 test, updated 1 test with new assertions, added 4 new tests for shadow path prompt coverage |

## Output Receipt

**Step:** 2 (DEV)
**Status:** Complete
**Escalate:** No
**CEO Flags:** None
**Blockers:** None
