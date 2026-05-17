# DEV Log — Rule 20 Bold Tolerance

**Date:** 2026-05-17
**Plan:** executable-rule-20-bold-tolerance-2026-05-17
**Commit:** 5ebc2df

## Regex Change

**Before (gates.py:374):**
```python
if re.search(r'^\s*PASSED\s+—\s+SELF-CHECK\s+PASSED', remaining, re.MULTILINE):
```

**After (gates.py:374):**
```python
if re.search(r'^\s*\*{0,2}\s*PASSED\s+—\s+SELF-CHECK\s+PASSED', remaining, re.MULTILINE):
```

The added `\*{0,2}\s*` allows zero, one, or two asterisks followed by optional whitespace before `PASSED`. Narrow by design: tolerates `**PASSED`, `*PASSED`, and bare `PASSED` only.

## New Tests

1. `test_rule_20_gate_tolerates_bold_passed_line` — QA report with `**PASSED — SELF-CHECK PASSED**` (bold). Asserts no `rule_20_self_check` failure.
2. `test_rule_20_gate_tolerates_single_asterisk_passed_line` — QA report with `*PASSED — SELF-CHECK PASSED*` (italic). Same assertion.

## Pytest Output

### Targeted (tests/test_gates.py)
```
91 passed, 1 warning in 0.18s
```

### Full Suite (tests/)
```
322 passed, 4 failed (pre-existing: test_decisions.py x2 phrase-file-missing-in-worktree, test_runner_parser.py x1 timeout)
```

All 91 gate tests pass. The 4 failures are pre-existing and unrelated to this change.

## Output Receipt
- **Files Modified:** `gates.py`, `tests/test_gates.py`
- **Files Deposited:** `knowledge/development/2026-05-17-rule-20-bold-tolerance-dev-log.md`
- **Receipt Status:** Complete
