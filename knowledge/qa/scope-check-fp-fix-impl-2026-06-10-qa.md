# QA Report — scope_check Union Fix

**Date:** 2026-06-10
**Plan:** bellows-scope-check-fp-fix-impl-2026-06-10
**Step:** 2 (QA)
**Dev Log:** `knowledge/development/scope-check-fp-fix-impl-2026-06-10.md`

---

## Output Receipt

**Agent:** Bellows QA
**Step:** 2
**Status:** Complete

---

## Deliverable Verification (Rule 17)

| Deliverable | Expected | Status | Evidence |
|---|---|---|---|
| `gates.py` union construction | `range(1, step_number + 1)` iteration + `union_text` variable | ✅ | gates.py:667 `for s in range(1, step_number + 1)`, lines 673/685/699 use `union_text` |
| `test_scope_check_union_authorizes_earlier_step_file` | Test exists in test_gates.py | ✅ | test_gates.py:1938 |
| `test_scope_check_union_authorizes_file_from_step_1_at_step_2` | Test exists in test_gates.py | ✅ | test_gates.py:1955 |
| `test_scope_check_union_still_rejects_unmentioned_file` | Test exists in test_gates.py | ✅ | test_gates.py:1961 |
| `test_scope_check_union_does_not_blanket_authorize_across_dirs` | Test exists in test_gates.py | ✅ | test_gates.py:1968 |

---

## QA Checks

### (1) Union Positive

2 positive union tests pass: `test_scope_check_union_authorizes_earlier_step_file` and `test_scope_check_union_authorizes_file_from_step_1_at_step_2`. Earlier-step files are correctly authorized at later steps.

| Check | Status | Evidence |
|---|---|---|
| Union positive tests (2/2) | ✅ | `evidence/bellows-scope-check-fp-fix-impl-2026-06-10/union_positive.txt` — 2 passed |

### (2) Teeth (Load-Bearing)

2 negative union tests pass: `test_scope_check_union_still_rejects_unmentioned_file` and `test_scope_check_union_does_not_blanket_authorize_across_dirs`. Ad-hoc check confirms `never_mentioned_anywhere.py` is correctly rejected by scope_check with evidence string.

| Check | Status | Evidence |
|---|---|---|
| Negative tests (2/2) + ad-hoc | ✅ | `evidence/bellows-scope-check-fp-fix-impl-2026-06-10/teeth.txt` — 2 passed + ad-hoc PASSED |

### (3) Additive-Only Regression

Pre-existing single-step scope_check tests `test_scope_check_passes_when_files_in_plan` and `test_scope_check_fails_when_file_not_in_plan` pass unchanged in the full suite run.

| Check | Status | Evidence |
|---|---|---|
| Pre-existing scope_check tests | ✅ | `evidence/bellows-scope-check-fp-fix-impl-2026-06-10/pytest_full.txt` — both pass in full run |

### (4) Full Suite

455 passed, 1 warning. Green. Baseline was 451 prior to this plan's branch; 4 new tests added = 455 total.

| Check | Status | Evidence |
|---|---|---|
| Full pytest suite | ✅ | `evidence/bellows-scope-check-fp-fix-impl-2026-06-10/pytest_full.txt` — 455 passed |

---

## Rule 20 — QA Self-Check Results

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: /Users/marklehn/Developer/GitHub/bellows/.bellows-worktrees/bellows-scope-check-fp-fix-impl-2026-06-10/knowledge/qa/evidence/bellows-scope-check-fp-fix-impl-2026-06-10/
Files verified: 4
```

---

## Files Verified
- `gates.py` — `_gate_scope_check` union construction confirmed
- `tests/test_gates.py` — 4 new union tests confirmed by name and execution

## Flags for CEO
- DAEMON RESTART REQUIRED to activate the fix (gates.py loads at startup)
- BACKLOG #2 (continuous-run cumulative diff) closed fully by this fix
- BACKLOG #9 (blueprint delegation) partially addressed — blueprint file path authorized via union, but files listed inside blueprint still not followed
