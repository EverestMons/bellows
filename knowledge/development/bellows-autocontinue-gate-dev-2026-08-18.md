# Auto-continue QA-result gate — dev log (plan 439, step 1)

**Date:** 2026-08-18

## What shipped

`_gate_qa_test_result` in `gates.py` — a blocking gate that parses the pytest summary line from QA evidence files and fails if regressions exceed `known_failures`.

### Gate logic
- No-op on non-QA steps.
- Resolves the `.txt` evidence deposit from the plan step's `**Deposits:**` block (prefers `*full-suite*` basename).
- Fail-closed if no `.txt` deposit exists.
- Parses the LAST `=====` summary line for `failed`, `errors`, and `passed` counts independently.
- `bad = failed + errors` — the F-Cold2 keystone: `errors` (collection/fixture failures) counted separately by pytest.
- Fail-closed if no `passed` count found (crash, "no tests ran", unrecognized format).
- `known_failures` sourced from plan header with `try/except` fail-close on malformed values (F-Cold3).
- Wired into `check()` after `_gate_rule_20_self_check`, using `check()`'s already-parsed `header` local (F-Cold1).

### plan_lint
`known_failures` accepted as int-typed header field. FAIL (not warn) if present but non-integer.

### Tests
`tests/test_gate_qa_test_result.py` — 16 cases covering: clean pass, failures > known, failures == known, no summary (fail-closed), errors-only, failed+errors, non-QA no-op, malformed known_failures, no .txt deposit, last-summary-wins.
