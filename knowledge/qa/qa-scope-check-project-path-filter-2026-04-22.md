# QA Report: scope_check project-path filter (BACKLOG #2 point fix)
**Date:** 2026-04-22 | **Plan:** executable-scope-check-project-path-filter-2026-04-22

## Verification Table

| Deliverable | Expected | Status | Evidence |
|---|---|---|---|
| `_parse_diff_stat` signature updated | `(post_diff, pre_diff, project_path=None)` | ✅ | `grep_signature.txt` — line 400 |
| Call site 1 passes `project_path` | 3-arg invocation at line 267 | ✅ | `grep_callsites.txt` — line 267 |
| Call site 2 passes `project_path` | 3-arg invocation at line 325 | ✅ | `grep_callsites.txt` — line 325 |
| 6 new project_path tests | Tests in `tests/test_bellows.py` | ✅ | `grep_tests.txt` — 6 test functions found |
| Dev log deposited | `knowledge/development/scope-check-project-path-filter-2026-04-22.md` | ✅ | File exists, 60 lines, complete Output Receipt |

## Targeted Test Results

**Command:** `python3 -m pytest tests/test_bellows.py -v`
**Result:** 52 passed, 0 failed, 1 warning
**Evidence:** `pytest_targeted.txt`

### New Tests (all pass)

| Test Name | Status |
|---|---|
| `test_parse_diff_stat_no_project_path_returns_all` | ✅ |
| `test_parse_diff_stat_project_path_all_inside` | ✅ |
| `test_parse_diff_stat_project_path_filters_dotdot` | ✅ |
| `test_parse_diff_stat_project_path_filters_sibling_project` | ✅ |
| `test_parse_diff_stat_project_path_filters_repo_root` | ✅ |
| `test_parse_diff_stat_project_path_keeps_deep_paths` | ✅ |

### Existing Tests

All 46 pre-existing tests in `test_bellows.py` pass. No regressions.

## Backward Compatibility Check

- `_parse_diff_stat` retains 2-arg signature via `project_path=None` default
- All 5 pre-existing `_parse_diff_stat` tests call with 2 args and continue to pass
- Both live call sites in `run_plan` now pass the 3-arg form (lines 267 and 325)

## Rule 20 Self-Check

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: knowledge/qa/evidence/executable-scope-check-project-path-filter-2026-04-22/
Files verified: 4
```

---
## Output Receipt
**Agent:** Bellows QA
**Step:** 2
**Status:** Complete

### What Was Done
Verified all Step 1 deliverables (signature change, call site updates, 6 new tests, dev log). Ran targeted test suite — 52/52 pass. Confirmed backward compatibility. Rule 20 self-check passed.

### Files Deposited
- `knowledge/qa/qa-scope-check-project-path-filter-2026-04-22.md` — this QA report
- `knowledge/qa/evidence/executable-scope-check-project-path-filter-2026-04-22/grep_signature.txt` — signature grep evidence
- `knowledge/qa/evidence/executable-scope-check-project-path-filter-2026-04-22/grep_callsites.txt` — call site grep evidence
- `knowledge/qa/evidence/executable-scope-check-project-path-filter-2026-04-22/grep_tests.txt` — test grep evidence
- `knowledge/qa/evidence/executable-scope-check-project-path-filter-2026-04-22/pytest_targeted.txt` — test run output

### Files Created or Modified (Code)
- None (QA step — verification only)

### Decisions Made
- Ran self-check with corrected paths (without `bellows/` prefix) per PATH-001 pattern — execution CWD is already inside the bellows directory

### Flags for CEO
- None

### Flags for Next Step
- None — plan complete
