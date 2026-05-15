# QA Report — Bellows Reliability Fixes A+B
**Date:** 2026-04-14 | **Plan:** executable-reliability-fixes-a-b-2026-04-14.md | **QA Agent:** Step 2

## Pre-flight

```
fd75e76 fix: Bellows reliability — stranded detection, rescan race, parallel group stagger
2d31cf7 chore: QA report — is_runnable_plan parallel fix
1cd47ab fix: is_runnable_plan accepts parallel-N- prefix
```

Step 1 commit confirmed: `fd75e76`.

## Deliverable Verification

| Deliverable | Expected | Status | Evidence |
|---|---|---|---|
| STRANDED warning present in run_plan | `STRANDED` appears ≥2× in bellows.py | ✅ | print line + notifier title both contain STRANDED |
| expected_done_path defined and used | appears ≥2× in bellows.py | ✅ | line 217 (definition), line 218 (condition) |
| _seen.discard removed from _rescan | zero occurrences in _rescan body | ✅ | grep returns no matches |
| time.sleep(2) in handle_parallel_group | appears inside loop body | ✅ | line 325 inside for-loop |
| test_rescan_preserves_seen present | in tests/test_bellows.py | ✅ | line 84 |
| test_handle_parallel_group_stagger present | in tests/test_bellows.py | ✅ | line 102 |
| _is_plan_stranded helper extracted | in bellows.py + test_bellows.py | ✅ | bellows.py:121, test_bellows.py:58,66,74 |

## Test Run

```
11 passed, 1 warning in 0.07s
```

6 pre-existing tests + 5 new tests (3 × _is_plan_stranded, test_rescan_preserves_seen, test_handle_parallel_group_stagger). All 11 passed.

| Deliverable | Expected | Status | Evidence |
|---|---|---|---|
| New tests present and passing | 5 new tests pass | ✅ | pytest_targeted.txt: 11 passed |
| Existing tests still passing | 6 prior tests pass | ✅ | pytest_targeted.txt: 11 passed |

## Smoke Tests

| Deliverable | Expected | Status | Evidence |
|---|---|---|---|
| Module imports clean | `import bellows` prints `ok` | ✅ | smoke_import.txt |
| Live smoke confirms rescan preserves _seen | assertion passes, prints OK | ✅ | smoke_rescan.txt: `rescan preserves _seen: OK` |

## Summary

All 7 deliverables verified. 11/11 tests pass. Module imports clean. Live rescan smoke confirms Bug B fix is effective. Bug A stranded detection and STRANDED notifier push confirmed present in run_plan. Parallel group stagger confirmed at time.sleep(2) per thread.
