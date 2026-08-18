# Dev Log: QA gate borderless pytest summary fix

**Plan:** 442 — corrective: test-result gate mis-parses borderless pytest summaries
**Step:** 1 (DEV)
**Date:** 2026-08-18

## Problem

`_PYTEST_SUMMARY_RE` used `r'=+\s+.+\s+=+'` with `.match()`, requiring `=====` borders around the summary line. Real piped pytest output (`-q | cat`) produces borderless counts lines like `1101 passed, 1 warning in 31.08s`. The gate matched `=== warnings summary ===` instead (no counts), failed to find `passed`, and fail-closed on clean suites. Surfaced by canary 441.

## Fix

- `gates.py:726`: replaced border-dependent regex with content-based `r'\b\d+\s+(?:passed|failed|error|errors|xfailed|xpassed)\b'` — matches count tokens, ignores borders, rejects non-summary lines like `warnings summary` or `collected N items`.
- `gates.py:765`: changed `.match()` to `.search()` — bordered lines don't start with `\d`, so `.match` would miss them; `.search` handles both bordered and borderless.

## Tests added

4 borderless regression tests in `tests/test_gate_qa_test_result.py` (`TestBorderlessEvidence`):
- `test_borderless_clean_passes` — borderless clean output with `=== warnings summary ===` header present
- `test_borderless_failed_pauses` — borderless with failures
- `test_borderless_zero_failed_with_errors` — F-Cold2 class, borderless
- `test_warnings_summary_header_not_matched` — confirms warnings header is not selected as summary

## Test result

`python3 -m pytest tests/test_gate_qa_test_result.py -q 2>&1 | cat` — 20 passed, 0 failed.
