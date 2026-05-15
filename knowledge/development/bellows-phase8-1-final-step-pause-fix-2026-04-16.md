# Bellows Phase 8.1 — Final-Step Pause Logic Fix

**Date:** 2026-04-16
**Plan:** executable-bellows-phase8-1-final-step-pause-fix-2026-04-16.md
**Step:** 1 (DEV)

## Summary

Phase 8 left a gap in `run_plan()`'s final-step gate check: it only tested two pause conditions (`not gate_result["passed"]` and `gate_result["is_qa_step"]`) while the while-loop check tested four. For single-step diagnostics the while-loop is never entered, so all pause logic must live in the final-step block. With Phase 8's defaults flip making `auto_close=false` the diagnostic default, clean single-step diagnostics with no header stranded.

This plan adds the missing three conditions to the final-step block: `verdict_requested`, `header_says_pause()`, and `not effective_auto_close`. The last is the critical addition — it catches the "clean gates + diagnostic default pause" case that stranded the `_parse_diff_stat` audit last night.

## Changes Per File

### MODIFIED: bellows.py (~7 lines, one logical change)

**Before** (final-step block, line 245):

```python
# Final step completed — check gates one last time
if not gate_result["passed"] or gate_result["is_qa_step"]:
    log_path = str(BELLOWS_ROOT / "logs")
    verdict.post_verdict_request(plan_path, current_step, log_path, gate_result)
    ...
```

**After:**

```python
# Final step completed — check gates one last time. Mirrors the while-loop
# pause conditions plus `not effective_auto_close` so single-step plans
# (where the loop is never entered) get the full set of pause checks.
if (not gate_result["passed"]
        or gate_result["is_qa_step"]
        or gate_result.get("verdict_requested", {}).get("requested", False)
        or header_says_pause(header, current_step, total_steps, gate_result["is_qa_step"])
        or not effective_auto_close):
    log_path = str(BELLOWS_ROOT / "logs")
    verdict.post_verdict_request(plan_path, current_step, log_path, gate_result)
    ...
```

No other changes to `run_plan()`. The auto-close branch below it remains unchanged (it already checks `effective_auto_close` positively).

### Case Analysis

| Case | gates.passed | is_qa | verdict_req | header_pause | effective_auto_close | Final-step check | Correct? |
|---|---|---|---|---|---|---|---|
| Clean exec, `auto_close: true` | T | F | F | F | T | All conditions False → fall through → auto-close fires | ✅ |
| Clean diagnostic, no header | T | F | F | F | F | `not effective_auto_close` → True → post verdict | ✅ (new) |
| Diagnostic, `pause_for_verdict: after_step_1` | T | F | F | T | F | header + effective_auto_close both True → post verdict | ✅ (new) |
| Exec with flag fires | F | F | F | F | T | `not passed` → True → post verdict | ✅ |
| Diagnostic with `auto_close: true` | T | F | F | F | T | All False → fall through → auto-close | ✅ (new — today's test path) |

### MODIFIED: tests/test_bellows.py (+118 lines, 2 new tests)

**Test A — `test_clean_diagnostic_no_header_posts_verdict`**

Reproduces last night's stranding scenario. Setup:
- Tmp diagnostic plan with no YAML header
- `clean_gates["plan_header"] = {}` (empty → triggers `effective_auto_close = False` for diagnostic default)
- All other gates pass, no QA, no verdict-request, no header pause

Patches `bellows.verdict.post_verdict_request` and `bellows.notifier.notify_verdict_request` (in addition to existing patches).

Asserts:
- `post_verdict_request` called once
- `notify_verdict_request` called
- Plan NOT in `Done/`
- `verdict.log_to_ledger` was NOT called with `"auto-close"` (because the auto-close branch did not fire)

**Test B — `test_clean_diagnostic_auto_close_true_moves_to_done`**

Regression test confirming the existing Phase 7-polish auto-close path still works after the Phase 8.1 fix. Same setup as Test A but `clean_gates["plan_header"] = {"auto_close": "true"}`. Asserts plan moved to `Done/`, `log_to_ledger` called with `"auto-close"`, `notifier.push` invoked.

The existing `test_diagnostic_auto_close_moves_to_done` was preserved unchanged — both tests now exercise the same code path with slightly different naming/intent for documentation clarity.

## Test Results

`python3 -m pytest tests/ -v 2>&1 | tee /tmp/test_bellows_phase81.txt`

```
======================== 66 passed, 1 warning in 0.71s =========================
```

64 pre-existing + 2 new = 66 passed. Zero regressions. Both new tests passed on first run.

Key tests (verified individually in the output):
- `test_diagnostic_auto_close_moves_to_done` PASSED (regression check)
- `test_clean_diagnostic_no_header_posts_verdict` PASSED (the stranded-case fix)
- `test_clean_diagnostic_auto_close_true_moves_to_done` PASSED (auto-close still works)

---

## Output Receipt

**Agent:** Bellows Developer
**Step:** 1
**Status:** Complete

### Files Deposited
- `/Users/marklehn/Desktop/GitHub/bellows/bellows.py`
- `/Users/marklehn/Desktop/GitHub/bellows/tests/test_bellows.py`
- `/Users/marklehn/Desktop/GitHub/bellows/knowledge/development/bellows-phase8-1-final-step-pause-fix-2026-04-16.md`

### Flags for CEO
- None
