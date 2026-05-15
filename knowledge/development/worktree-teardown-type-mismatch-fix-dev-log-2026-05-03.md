# Worktree Teardown Type-Mismatch Fix — Dev Log
**Date:** 2026-05-03

## Sites Edited

Four sites in `bellows.py` were changed from plain-string failure entries to dict format matching the `verdict.py` consumer contract (`{"gate": ..., "evidence": ...}`):

| # | Site | Line | Gate Value | Old Format |
|---|------|------|------------|------------|
| 1 | `_create_worktree` exception handler | 286 | `worktree_creation` | `f"worktree_creation_failed: {e}"` |
| 2 | Mid-step teardown (pause path) | 340 | `worktree_teardown` | `f"worktree_teardown_failed: {e}"` |
| 3 | Final-step teardown (pause path) | 405 | `worktree_teardown` | `f"worktree_teardown_failed: {e}"` |
| 4 | Auto-close teardown (cherry-pick conflict) | 433 | `worktree_teardown` | `f"worktree_teardown_failed: {e}"` |

## Consumer Contract Verification

Verified at `verdict.py:99-102`. When `pause_reason == "gate_failure"` and `gate_result["failures"]` is non-empty, the function iterates:
```python
for f in gate_result["failures"]:
    failures_text += f"- **{f['gate']}**: {f['evidence']}\n"
```
The dict shape `{"gate": str, "evidence": str}` is confirmed as the expected contract. All existing tests in `test_verdict.py` already use this format.

## New Regression Test

`test_post_verdict_request_handles_worktree_teardown_failure_dict_format` added to `tests/test_verdict.py`:
- Constructs a `gate_result` with `{"gate": "worktree_teardown", "evidence": "simulated teardown error"}` in failures
- Calls `post_verdict_request` with `pause_reason="gate_failure"`
- Asserts no TypeError raised
- Asserts the deposited verdict-request file contains `## Gate Failures`, `worktree_teardown`, and `simulated teardown error`

## Existing Test Update

`test_run_plan_pauses_on_cherry_pick_conflict` in `tests/test_bellows.py` was updated: changed `" ".join(failures)` string assertion to `any(f["gate"] == "worktree_teardown" for f in failures)` dict-aware assertion.

## Test Results

87 passed, 0 failed across `test_verdict.py` (15 tests) and `test_bellows.py` (72 tests).

## Commit

SHA: 272fbe4

---
## Output Receipt
**Agent:** Bellows Developer
**Step:** 1
**Status:** Complete

### What Was Done
Fixed type-contract violation between bellows.py and verdict.py. Four sites in bellows.py appended plain strings to gate_result["failures"]; verdict.py's post_verdict_request iterates failures expecting dicts with "gate" and "evidence" keys. All four sites now produce the correct dict format. Added a regression test and updated one existing test.

### Files Deposited
- `knowledge/development/worktree-teardown-type-mismatch-fix-dev-log-2026-05-03.md` — this dev log

### Files Created or Modified (Code)
- `bellows.py` — changed 4 failure-entry sites from string to dict format (lines 286, 340, 405, 433)
- `tests/test_verdict.py` — added `test_post_verdict_request_handles_worktree_teardown_failure_dict_format`
- `tests/test_bellows.py` — updated `test_run_plan_pauses_on_cherry_pick_conflict` assertion to expect dict format

### Decisions Made
- Updated existing test `test_run_plan_pauses_on_cherry_pick_conflict` to match new dict format (it was written assuming the old string format, which was the bug)

### Flags for CEO
- None

### Flags for Next Step
- None
