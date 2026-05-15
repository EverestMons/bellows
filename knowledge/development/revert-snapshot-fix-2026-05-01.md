# Dev Log — Revert File-Checksum Snapshot Fix

**Date:** 2026-05-01
**Plan:** `executable-revert-snapshot-fix-and-reopen-backlog-2026-05-01`
**Step:** 1 (DEV)

## Summary

Reverted commit `9b20d94` ("fix(gates): file-checksum snapshot for parallel-plan scope_check immunity") because Planner Rule 22 verification identified the fix as structurally insufficient: file-checksum snapshots read the same shared working tree, so sibling-induced file changes during overlapping execution windows still contaminate per-plan scope_check results.

## Revert Commit

- **SHA:** `7e1d157`
- **Message:** `Revert "fix(gates): file-checksum snapshot for parallel-plan scope_check immunity"`
- **Files changed:** 2 files, +8 insertions, -214 deletions
- **Deleted:** `tests/test_snapshot_file_state.py`

## Git Log After Revert

```
7e1d157 Revert "fix(gates): file-checksum snapshot for parallel-plan scope_check immunity"
58e875b qa: parallel-plan scope_check collision fix verified — 9/9 checks pass, Rule 20 PASSED
e244915 docs: dev log + prompt feedback for parallel-plan scope_check collision fix (Step 1)
```

## Verification Results

| Check | Expected | Actual | Status |
|-------|----------|--------|--------|
| `grep -c "_snapshot_file_state" bellows.py` | 0 | 0 | PASS |
| `grep -c "_capture_git_diff" bellows.py` | ≥3 | 5 | PASS |
| `ls tests/test_snapshot_file_state.py` | No such file | No such file or directory | PASS |

## Pytest Output (tail -20)

```
=================================== FAILURES ===================================
____________________________ test_run_step_timeout _____________________________

    def test_run_step_timeout():
        with patch("runner.subprocess.run", side_effect=subprocess.TimeoutExpired("claude", 300)):
            result = runner.run_step("test prompt", "/tmp", "claude-sonnet-4-6")
>       assert result["is_error"] is True
E       assert False is True

tests/test_runner_parser.py:57: AssertionError
=============================== warnings summary ===============================
-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== short test summary info ============================
FAILED tests/test_runner_parser.py::test_run_step_timeout - assert False is True
=================== 1 failed, 177 passed, 1 warning in 4.88s ===================
```

**Result:** 177 passed, 1 failed (pre-existing `test_run_step_timeout`). No new failures from the revert.

## Output Receipt

| Deliverable | Path | Status |
|-------------|------|--------|
| Dev log | `knowledge/development/revert-snapshot-fix-2026-05-01.md` | Complete |
| Revert commit | `7e1d157` | Complete |

**Output Receipt Status: Complete**
