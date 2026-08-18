# on_failure canary #2 — DEV note (Step 1)

**Plan:** `executable-on-failure-canary2-2026-08-18.md`
**Date:** 2026-08-18

## What changed

Added an explanatory comment above `_PYTEST_SUMMARY_RE` in `gates.py` (line ~726)
documenting why the regex is content-based (borders optional):

- Piped pytest output (`-q | cat`) writes a borderless counts line.
- A border-requiring regex (`=+...=+`) fail-closes on clean suites.
- Origin: canary 441 finding / fix 442.

No logic change — comment only.

## Targeted test run

```
python3 -m pytest tests/test_gate_qa_test_result.py -q 2>&1 | cat
20 passed, 1 warning in 0.23s
```

All gate tests pass; the comment has no effect on behavior.
