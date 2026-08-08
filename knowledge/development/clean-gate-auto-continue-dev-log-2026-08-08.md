# Dev Log — qa_and_terminal pause mode + clean_gate_auto provenance (Plan 317, Step 1)

**Date:** 2026-08-08

## What shipped

1. **`qa_and_terminal` pause mode** (bellows.py Site 1, line 391-393): new `pause_for_verdict` value that pauses at QA steps AND at the terminal step. At terminal, this wins over `auto_close: true`.
2. **`clean_gate_auto` provenance recording** (bellows.py Site 2, lines 783-787): mechanical clean-gate non-terminal advances now write a paired `record_verdict_request` + `record_verdict_outcome` row so the transition is auditable. Clones the 313 auto-close pattern.
3. **Verdicts README update** (verdicts/README.md): added `auto_close` and `clean_gate_auto` rows to the table; documented `qa_and_terminal` semantics; fixed stale `header_pause` description.
4. **Three-copy enum invariant** updated across:
   - `bellows.py` line 395: WARN literal now lists `qa_and_terminal`
   - `scripts/plan_lint.py` line 25: `RECOGNIZED_PAUSE_TOKENS` includes `qa_and_terminal`
   - `validators.py` line 120: `VALID_PAUSE_FOR_VERDICT_VALUES` includes `qa_and_terminal`
5. **Site 4(c) coupling lint** (scripts/plan_lint.py lines 250-256): warns when `qa_and_terminal` is set but `qa_steps` is missing or unparseable.

## Before / After

### bellows.py — header_says_pause (Site 1)

**Before (line 389-395):**
```python
if pv == "after_qa_step":
    return is_qa_step
if pv:
    _log("WARN", f"⚠️ unrecognized pause_for_verdict value: {pv!r} (recognized: 'always', 'after_step_1', 'after_qa_step') — treating as no-pause")
return False
```

**After (line 389-396):**
```python
if pv == "after_qa_step":
    return is_qa_step
if pv == "qa_and_terminal":
    # Pause at QA steps and at the terminal step; at terminal this wins over auto_close
    return is_qa_step or is_final_step(current_step, total_steps)
if pv:
    _log("WARN", f"⚠️ unrecognized pause_for_verdict value: {pv!r} (recognized: 'always', 'after_step_1', 'after_qa_step', 'qa_and_terminal') — treating as no-pause")
return False
```

### bellows.py — while-loop (Site 2)

**Before (line 783):**
```python
# All gates passed and not QA — continue to next step
default_next_prompt = f"Read the plan at {shadow_prompt_path}. Execute Step {current_step + 1}.{_id_tag_instruction}"
```

**After (lines 783-788):**
```python
# All gates passed and not QA — continue to next step
# Record the mechanical clean-gate continue so the transition is auditable (315 evidence; clones 313 auto-close pattern)
if plan_id:
    lifecycle.record_verdict_request(plan_id, current_step, pause_reason_code="clean_gate_auto")
    lifecycle.record_verdict_outcome(plan_id, current_step, "continue", decided_by="gate_auto")
default_next_prompt = f"Read the plan at {shadow_prompt_path}. Execute Step {current_step + 1}.{_id_tag_instruction}"
```

### scripts/plan_lint.py — RECOGNIZED_PAUSE_TOKENS (Site 4a)

**Before:** `RECOGNIZED_PAUSE_TOKENS = {"always", "after_step_1", "after_qa_step"}`
**After:** `RECOGNIZED_PAUSE_TOKENS = {"always", "after_step_1", "after_qa_step", "qa_and_terminal"}`

### validators.py — VALID_PAUSE_FOR_VERDICT_VALUES (Site 4b)

**Before:** `VALID_PAUSE_FOR_VERDICT_VALUES = {"always", "after_step_1", "after_qa_step", "after_each_step", ""}`
**After:** `VALID_PAUSE_FOR_VERDICT_VALUES = {"always", "after_step_1", "after_qa_step", "after_each_step", "qa_and_terminal", ""}`

## Disclosures

- **`after_each_step` is a GHOST value**: present in `validators.py` `VALID_PAUSE_FOR_VERDICT_VALUES` but never implemented by `header_says_pause`. It passes claim-time validation but falls through to the WARN branch at runtime. Not fixed in this plan — disclosed only.
- **`is_final_step()` called, not mirrored**: Site 1 uses `is_final_step(current_step, total_steps)` rather than reimplementing the comparison, per plan requirement.
- **`lifecycle.record_verdict_outcome` stamps ALL matching rows** (UPDATE WHERE outcome IS NULL), not just the most recent. This matches the existing auto-close pattern from plan 313.
- **test_bellows.py UNCHANGED** per plan expectation.

## Test output

### Targeted test run (Task E)
```
59 passed, 246 deselected, 1 warning in 0.96s
pytest_exit=0
```

### collect-only for qa_and_terminal
```
tests/test_plan_lint.py::test_lint_qa_and_terminal_mode_passes
tests/test_plan_lint.py::test_lint_qa_and_terminal_coupling_warns_missing_qa_steps
tests/test_validators.py::test_qa_and_terminal_accepted_by_pause_for_verdict_check

3/105 tests collected (102 deselected) in 0.02s
```

## Files modified

- `bellows.py` — Sites 1 and 2
- `verdicts/README.md` — Site 3
- `scripts/plan_lint.py` — Sites 4a and 4c
- `validators.py` — Site 4b
- `tests/test_gate_transaction_mechanization.py` — Tasks C and D (TestHeaderSaysPauseModes, TestCleanGateAutoProvenance, TestCleanGateAutoRunPlanIntegration)
- `tests/test_plan_lint.py` — qa_and_terminal enum pass + coupling check tests
- `tests/test_validators.py` — qa_and_terminal acceptance test
- `knowledge/development/clean-gate-auto-continue-dev-log-2026-08-08.md` — this file
