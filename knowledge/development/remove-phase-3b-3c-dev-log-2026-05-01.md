# Dev Log — Remove Phase 3b/3c DB Step-State-Resume Logic
**Date:** 2026-05-01
**Plan:** executable-remove-phase-3b-3c-2026-05-01

## Pre-Edit Verification — Line Numbers vs SA Findings

| SA Citation | Actual Line | Match? |
|------------|-------------|--------|
| L175-188: `_get_last_completed_step` definition | L175 (definition), L244 (call site) | Exact match |
| L243-247: DB-resume guard | L243-247 | Exact match |
| L249-254: Phase 3c hash-drift block | L249-254 | Exact match |

No drift from SA findings.

## Test Discovery Grep Output

```
tests/test_bellows.py:1789:def test_get_last_completed_step_returns_max         — Phase 3b ONLY → DELETED
tests/test_bellows.py:1809:def test_get_last_completed_step_no_rows             — Phase 3b ONLY → DELETED
tests/test_bellows.py:1817:def test_get_last_completed_step_excludes_non_complete — Phase 3b ONLY → DELETED
tests/test_bellows.py:1836:def test_get_last_completed_step_exact_slug_match    — Phase 3b ONLY → DELETED
tests/test_bellows.py:1855:def test_run_plan_plan_hash_drift_warning            — Phase 3c ONLY → DELETED
```

All 5 tests exercised ONLY removed functionality. No tests incidentally referenced removed functions for other purposes.

## Edits

### Edit 1 — Remove `_get_last_completed_step` function definition
- **Before:** L175-188, 14-line function definition (`def _get_last_completed_step(db_path, plan_slug) -> Optional[int]`)
- **After:** Removed entirely. `is_final_step` now follows directly after `record_run`.

### Edit 2 — Remove DB-resume guard (L243-247)
- **Before:** 5-line block: `if resume_step is None and shadow_text is not None: last_step = _get_last_completed_step(...)...`
- **After:** Removed entirely.

### Edit 3 — Remove Phase 3c hash-drift block (L249-254) + `import hashlib`
- **Before:** 6-line block computing shadow/current hashes and pushing notification on mismatch. Plus `import hashlib` at L3.
- **After:** Both removed. `hashlib` had no other uses in `bellows.py`.

### Edit 4 — Delete Phase 3b/3c canary tests
- **File:** `tests/test_bellows.py`
- **Removed:** 5 test functions (L1789-1903): `test_get_last_completed_step_returns_max`, `test_get_last_completed_step_no_rows`, `test_get_last_completed_step_excludes_non_complete`, `test_get_last_completed_step_exact_slug_match`, `test_run_plan_plan_hash_drift_warning`

### Edit 5 — Add regression test
- **File:** `tests/test_consume_verdicts.py`
- **Added:** `test_dispatch_starts_fresh_when_db_has_orphan_slug_rows` — creates orphan DB rows for the same slug + shadow cache, calls `run_plan(resume_step=None)`, asserts first `runner.run_step` call's bootstrap prompt contains "Step 1" (not "Step 3").
- **Also added:** `_make_fake_run_step_result()` and `_clean_gates()` helper functions (copied from `test_bellows.py`).

## Test Results

```
176 passed, 1 failed, 1 warning in 5.85s
```
- 1 failure: `test_run_step_timeout` — known pre-existing failure (unrelated to this change)
- Baseline was 180 tests. Removed 5 Phase 3b/3c tests, added 1 regression test = 176. Correct.

## Files Created or Modified

| File | Action |
|------|--------|
| `bellows/bellows.py` | Modified — removed `_get_last_completed_step` (14 LOC), DB-resume guard (5 LOC), Phase 3c hash-drift block (6 LOC), `import hashlib` (1 LOC). Net ~26 LOC removed. |
| `bellows/tests/test_bellows.py` | Modified — removed 5 Phase 3b/3c test functions (~115 LOC) |
| `bellows/tests/test_consume_verdicts.py` | Modified — added regression test + helper functions (~75 LOC) |
| `bellows/knowledge/development/remove-phase-3b-3c-dev-log-2026-05-01.md` | Created — this file |
| `bellows/knowledge/research/agent-prompt-feedback.md` | Updated — appended Step 1 DEV feedback |

## Notes

- CEO restart required to load modified `bellows.py`.
- `plan_slug` column and `record_run()` slug population preserved per F3 design.
- Shadow cache system preserved (still used for metadata extraction, total_steps, prompt routing).
