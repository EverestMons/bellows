# QA Report — Scope_check False Positives Fix
**Plan:** executable-bellows-scope-check-fix-2026-04-16
**Date:** 2026-04-16 | **QA Step:** 2

---

## Step 1 Commit Verification

```
106d50a fix: scope_check prefix allowlist for plan file renames
3e883ee chore: untrack and gitignore verdicts/ledger.jsonl
```

Both expected commits present. ✅

---

## Deliverable Verification

| Check | Command | Expected | Result | Status |
|-------|---------|----------|--------|--------|
| (a) ledger.jsonl in .gitignore | `grep "ledger.jsonl" .gitignore` | 1 match | `verdicts/ledger.jsonl` | ✅ |
| (b) ledger.jsonl untracked | `git ls-files verdicts/ledger.jsonl` | empty output | (empty) | ✅ |
| (c) ledger.jsonl on disk | `ls verdicts/ledger.jsonl` | file present | present | ✅ |
| (d) SCOPE_ALLOWLIST_PREFIXES in gates.py | grep for constant | 2+ matches | 2 matches (lines 15, 155) | ✅ |
| (e) prefix check in scope_check | grep for startswith | 2+ matches | 2 matches | ✅ |
| (f) prefix tests in test_gates.py | grep for test functions | 3+ matches | 4 matches (lines 146, 153, 160, 167) | ✅ |

---

## Test Results

### Targeted (scope tests): 7/7 passed

```
tests/test_gates.py::test_scope_check_passes_when_files_in_plan PASSED
tests/test_gates.py::test_scope_check_fails_when_file_not_in_plan PASSED
tests/test_gates.py::test_scope_check_allowlist PASSED
tests/test_gates.py::test_scope_check_prefix_allowlist_in_progress PASSED
tests/test_gates.py::test_scope_check_prefix_allowlist_verdict_pending PASSED
tests/test_gates.py::test_scope_check_prefix_allowlist_halted PASSED
tests/test_gates.py::test_scope_check_prefix_allowlist_does_not_suppress_real_violations PASSED
```

### Full suite: 92/92 passed

All 92 tests passed, 1 warning (urllib3/LibreSSL version mismatch — unrelated to this fix).

---

## Files Deposited

- `/Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/scope-check-fix-qa-2026-04-16.md`
- `/Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/evidence/scope-check-fix/pytest_targeted.txt`
- `/Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/evidence/scope-check-fix/pytest_full.txt`
