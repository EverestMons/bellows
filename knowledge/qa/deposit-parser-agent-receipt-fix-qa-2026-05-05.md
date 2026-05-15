# QA Report — Deposit Parser Agent-Receipt Fix

**Plan:** `executable-deposit-parser-agent-receipt-fix-2026-05-05`
**Date:** 2026-05-05
**QA Agent:** Bellows QA (Step 2)

## Deliverable Verification (Rule 17)

| # | Verification | Expected | Status | Evidence |
|---|---|---|---|---|
| 1 | gates.py fix landed (`re.match` at line 157) | At least one match in `_gate_deposit_exists` region | ✅ | `grep_gates_fix.txt` — line 157 match |
| 2 | 4 new test functions in test_gates.py | Count = 4 | ✅ | `grep_new_tests.txt` — count is 4 |
| 3 | BACKLOG.md original-entry-title count | Exactly 1 (Closed only) | ✅ | `grep_backlog_count.txt` — count is 1 |
| 4 | BACKLOG.md new Closed entry exists | 1 match in Closed section | ✅ | `grep_backlog_closed.txt` — line 59 match |
| 5 | Open section no longer contains original entry | Count = 0 | ✅ | `grep_open_section.txt` — count is 0 |
| 6 | Full pytest suite passes | All pass except known pre-existing `test_run_step_timeout` | ✅ | `pytest_full.txt` — 197 passed, 1 failed (pre-existing `test_run_step_timeout`) |
| 7 | Targeted pytest (test_gates.py) passes | 100% pass rate | ✅ | `pytest_targeted.txt` — 38 passed in 0.02s |
| 8 | Behavioral smoke confirms fix works | PASSED with zero deposit_exists failures | ✅ | `behavioral_smoke.txt` — PASSED |

## Test Results

**Full suite:** 197 passed, 1 failed (`test_run_step_timeout` — known pre-existing, unrelated to this fix), 1 warning. Runtime: 5.88s.

**Targeted (test_gates.py):** 38 passed, 0 failed. Runtime: 0.02s.

**New tests (all 4 passed):**
- `test_deposit_exists_extracts_path_from_backtick_with_description` — regression test for the actual bug
- `test_deposit_exists_extracts_path_from_backtick_only` — backtick-quoted path without description
- `test_deposit_exists_extracts_path_from_bare_path_without_backticks` — fallback path (no backticks)
- `test_deposit_exists_still_fails_on_genuinely_missing_path_with_new_format` — negative case, gate not a no-op

**Behavioral smoke:** Simulated an agent receipt with `gates.py` backtick + em-dash + description format. `gates.check()` returned `passed=True` with zero `deposit_exists` failures.

## Rule 20 Self-Check

```
SELF-CHECK PASSED
  Evidence directory: bellows/knowledge/qa/evidence/executable-deposit-parser-agent-receipt-fix-2026-05-05/
  Evidence files present: 8/8
    grep_gates_fix.txt (61 bytes)
    grep_new_tests.txt (2 bytes)
    grep_backlog_count.txt (2 bytes)
    grep_backlog_closed.txt (628 bytes)
    grep_open_section.txt (2 bytes)
    pytest_full.txt (18906 bytes)
    pytest_targeted.txt (3607 bytes)
    behavioral_smoke.txt (114 bytes)
```

## Conclusion

All 8 verifications passed. Fix correctly regex-extracts backtick-quoted paths from agent receipts while preserving fallback behavior for bare paths. BACKLOG entry properly closed. No regressions introduced.
