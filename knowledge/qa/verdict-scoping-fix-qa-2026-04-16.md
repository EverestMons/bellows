# QA Report — Verdict Scoping Fix
**Plan:** `parallel-1-executable-bellows-verdict-scoping-2026-04-16`
**Date:** 2026-04-16
**QA Agent:** Claude Sonnet 4.6

---

## Step 1 Commit Verification

| Check | Result | Status |
|-------|--------|--------|
| Commit present | `872f5a3` — fix: scope _consume_verdicts to correct project via request file | ✅ |

---

## Deliverable Verification

### (a) Scoping logic

Command: `grep -n "Plan:" bellows.py | grep -i "pending\|scoped\|plan_path_from"`

Result: 1 match (expected 2+)

```
494:                        plan_path_from_request = req_line.split("**Plan:**", 1)[1].strip()
```

Note: The grep filter (`pending|scoped|plan_path_from`) is narrower than the actual 9-line scoping block (lines 488–496). Line 493 (`req_line.startswith("**Plan:**")`) contains `Plan:` but not `pending|scoped|plan_path_from`, so it was filtered out. The full scoping logic is present and correct at lines 488–496; this is a grep-filter precision issue, not a code gap. Three of the new tests exercise this logic directly.

| Check | Lines | Status |
|-------|-------|--------|
| Request file path construction (`req_file`) | 489 | ✅ |
| `scoped_decisions_path = None` init | 490 | ✅ |
| Existence guard for request file | 491 | ✅ |
| `**Plan:**` field parse | 493–494 | ✅ |
| `scoped_decisions_path` derived | 495 | ✅ |
| `search_dirs` scoped vs fallback | 506 | ✅ |

### (b) Break after match

Command: `grep -n "break.*match\|break.*consumed\|break  #" bellows.py`

Result:
```
548:                        break  # only one match per verdict
```

| Check | Result | Status |
|-------|--------|--------|
| Break inside `_consume_verdicts` inner loop | Line 548 | ✅ |

### (c) Tests

Command: `grep -rn "scope\|scoped\|fallback\|break.*verdict" tests/ --include="*.py"`

Result: 7+ matches in `test_bellows.py` (scopes/fallback/double-consumption) plus pre-existing scope_check matches in test_gates.py and test_verdict.py.

| Check | Result | Status |
|-------|--------|--------|
| scope-to-project test (`..._scopes_to_project_from_...`) | line 591 | ✅ |
| fallback test (`..._fallback_to_all_watched_...`) | line 652 | ✅ |
| `test_consume_verdicts_break_prevents_double_consumption` | line 698 | ✅ |

---

## Test Results

### Targeted (`-k "verdict or consume or scope"`)

31 selected, 31 passed, 0 failed.

All 3 new tests included:
- `test_consume_verdicts_scopes_to_project_from_pending_file` — PASS
- `test_consume_verdicts_fallback_to_all_watched_when_pending_missing` — PASS
- `test_consume_verdicts_break_prevents_double_consumption` — PASS

Evidence: `knowledge/qa/evidence/verdict-scoping-fix/pytest_targeted.txt`

| Suite | Result | Status |
|-------|--------|--------|
| Targeted (31 tests) | 31 passed | ✅ |

### Full suite

95 collected, 95 passed, 0 failed.

Evidence: `knowledge/qa/evidence/verdict-scoping-fix/pytest_full.txt`

| Suite | Result | Status |
|-------|--------|--------|
| Full suite (95 tests) | 95 passed | ✅ |

---

## Summary

| Deliverable | Status |
|-------------|--------|
| Scoping logic in `_consume_verdicts` (lines 488–506) | ✅ |
| Break after match (line 548) | ✅ |
| 3 new targeted tests | ✅ |
| 31/31 targeted tests pass | ✅ |
| 95/95 full suite pass | ✅ |
| No regressions | ✅ |
