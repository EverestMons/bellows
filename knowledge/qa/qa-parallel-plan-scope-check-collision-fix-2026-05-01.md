# QA Report: Parallel-Plan scope_check Collision Fix (File-Checksum Snapshot)

**Date:** 2026-05-01 | **Plan:** executable-parallel-plan-scope-check-collision-fix-2026-05-01 | **Step:** 2 (QA)

---

## Verification Table

| Deliverable | Expected | Status | Evidence |
|---|---|---|---|
| `_snapshot_file_state` defined in bellows.py | Function definition present | ✅ | `grep_function_definitions.txt` line 434 |
| `_diff_file_state` defined in bellows.py | Function definition present | ✅ | `grep_function_definitions.txt` line 474 |
| `_capture_git_diff` deprecation note present | DEPRECATED 2026-05-01 docstring | ✅ | `grep_function_definitions.txt` line 493, 514 |
| No remaining `_capture_git_diff` call sites in `run_plan` | Only in own definition + docstring ref | ✅ | `grep_call_sites.txt` — 3 occurrences: docstring ref (439), definition (492), `_parse_diff_stat` definition (513) |
| Test file exists with >=6 tests | `test_snapshot_file_state.py` with 6 test functions | ✅ | `test_function_count.txt` — count: 6 |
| Targeted tests all pass | 6/6 PASS | ✅ | `pytest_targeted.txt` — 6 passed |
| Full suite no new regressions | 183/184 PASS, 1 pre-existing failure | ✅ | `pytest_full.txt` — 1 failed (test_run_step_timeout, pre-existing) |
| Synthetic collision smoke shows per-file isolation | diff returns only modified file, not unrelated sibling files | ✅ | `synthetic_collision_smoke.txt` — PASS |
| Dev log deposited | File exists at expected path | ✅ | `ls -la` confirms 3413 bytes at `knowledge/development/parallel-plan-scope-check-collision-fix-2026-05-01.md` |

## Baseline Comparison

- **Pre-fix baseline:** 183 passed, 1 failed (`test_run_step_timeout` — pre-existing, tracked)
- **Post-fix result:** 183 passed, 1 failed (`test_run_step_timeout` — same pre-existing failure)
- **New regressions:** 0
- **FAILED grep count in full suite output:** 2 lines (1 test failure line + 1 summary section line; both reference the same single pre-existing failure)

## Rule 20 Self-Check

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: bellows/knowledge/qa/evidence/executable-parallel-plan-scope-check-collision-fix-2026-05-01/
Files verified: 6
```

---

## Evidence Files

All evidence in `bellows/knowledge/qa/evidence/executable-parallel-plan-scope-check-collision-fix-2026-05-01/`:

1. `grep_function_definitions.txt` — confirms `_snapshot_file_state`, `_diff_file_state` defined and deprecation notes present
2. `grep_call_sites.txt` — confirms no `_capture_git_diff` / `_parse_diff_stat` call sites remain in `run_plan`
3. `test_function_count.txt` — confirms 6 test functions
4. `pytest_targeted.txt` — 6/6 passed
5. `pytest_full.txt` — 183/184 passed (1 pre-existing)
6. `synthetic_collision_smoke.txt` — PASS, per-file isolation demonstrated
