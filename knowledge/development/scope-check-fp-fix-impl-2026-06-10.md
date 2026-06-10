# scope_check Union Fix — Dev Log

**Date:** 2026-06-10
**Plan:** bellows-scope-check-fp-fix-impl-2026-06-10
**Step:** 1 (DEV)
**Design:** `knowledge/architecture/scope-check-false-positive-fix-design-2026-06-09.md`

---

## Output Receipt

**Agent:** Bellows Developer
**Step:** 1
**Status:** Complete

### What Was Done
Implemented the union-of-all-step-texts fix in `_gate_scope_check` (gates.py) per the approved design Section 2. The scope_check gate now evaluates changed files against the union of ALL step texts (steps 1 through `step_number`) instead of only the current step's text. This eliminates false positives caused by continuous-run cumulative diffs (BACKLOG #2) where prior-step files leak into later steps' `files_changed` sets.

### Changes Made

**gates.py** — `_gate_scope_check` (lines 661-710):
- Replaced single-step extraction (`step_text = _extract_step_text(plan_text, step_number)`) with a union construction: iterate `_extract_step_text(plan_text, s)` for `s` in `range(1, step_number + 1)`, collect non-empty results, join into `union_text`
- Path/basename check (line ~681) now matches against `union_text` instead of `step_text`
- Directory-mention check (line ~695) now matches against `union_text` instead of `step_text`
- Evidence display (line ~704) retains `step_text` (current step only) for diagnostic clarity

**tests/test_gates.py** — 4 new tests added:
1. `test_scope_check_union_authorizes_earlier_step_file` — 3-step plan, file from Step 1 authorized at Step 3
2. `test_scope_check_union_authorizes_file_from_step_1_at_step_2` — 2-step plan, cumulative authorization across steps
3. `test_scope_check_union_still_rejects_unmentioned_file` — unmentioned file still rejected (teeth)
4. `test_scope_check_union_does_not_blanket_authorize_across_dirs` — union doesn't create directory-wide authorization

### Additive-Only Guarantee
The change is purely additive — it only widens the text haystack for file authorization. It never moves files from in-scope to out-of-scope. The allowlist checks, directory-mention depth guard, failure-append, and all other clauses are unchanged.

### Files Created or Modified (Code)
- `gates.py` — modified `_gate_scope_check`
- `tests/test_gates.py` — added 4 tests + 2 plan fixtures

### Test Results
```
455 passed, 1 warning in 5.80s
```
Full suite green including all pre-existing scope_check tests (regression guard) and all 4 new union tests.

### Pre-Edit Verification (Rule 39)
All 6 verification blocks (V1-V6) from design Section 6 confirmed against current code before editing. No mismatches.

### Flags for Next Step
- Daemon restart required after this fix lands (gates.py loads at startup)
- QA step should verify the 4 new tests by name, run full suite, and confirm additive-only regression
