# Dev Log — Rule 26 Deposit Parser: Scope Gate + Fix Scoping Bug
**Date:** 2026-04-19 | **Plan:** executable-rule-26-deposit-parser-scope-2026-04-19.md | **Tier:** Medium

## Summary

Three changes closing BACKLOG #6 (deposit-path parser false positives) and fixing the scoping bug where `extract_primary_deposit` scanned the entire plan instead of the current step.

## Files Modified

| File | Change |
|------|--------|
| `bellows/gates.py` | Added `_extract_step_text(plan_text, step_number)` helper; replaced inline regex in `_gate_deposit_exists` and `_gate_scope_check`; taught `_extract_plan_required_deposits` to prefer declared `**Deposits:**` block (Rule 26) over legacy prose regexes |
| `bellows/verdict.py` | Added `_extract_step_text_from_plan(plan_text, step_number)` helper (duplicated from gates.py to avoid circular import); scoped `extract_primary_deposit` call in `post_verdict_request` to current step text |

## Function Signatures Added

- `gates.py::_extract_step_text(plan_text: str, step_number: int) -> Optional[str]`
- `verdict.py::_extract_step_text_from_plan(plan_text: str, step_number: int) -> Optional[str]`

## Function Signatures Modified

- `gates.py::_extract_plan_required_deposits(step_text)` — added Rule 26 `**Deposits:**` block detection before legacy fallback

## Test Results

- **Before:** 104 tests, 93 passed, 11 failed (all pre-existing runner test failures)
- **After:** 104 tests, 93 passed, 11 failed (same pre-existing failures, zero new failures)

## Commit

```
4c77e7e fix(gates): scope deposit_exists to declared **Deposits:** block; factor step-text extraction; fix extract_primary_deposit scoping in post_verdict_request
```

## Output Receipt

- **Status:** Complete
- **Deposit:** `bellows/knowledge/development/rule-26-deposit-parser-scope-2026-04-19.md`
