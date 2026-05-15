# QA Report — Parallel Group Deferred Dispatch Fix
**Plan:** parallel-1-executable-bellows-parallel-defer-2026-04-16
**Date:** 2026-04-16
**Step:** 2 (QA)
**Result:** PASSED

---

## Deliverable Verification

Grep commands run against `bellows.py` and `tests/`:

| Check | Matches Found | Threshold | Status |
|-------|--------------|-----------|--------|
| Defer dict field (`_p_groups`) | 7 | 3+ | ✅ |
| `from_rescan` parameter | 4 | 4+ | ✅ |
| Settle window logic | 6 | 2+ | ✅ |
| New test functions in `tests/` | 28 | 5+ | ✅ |

Patterns used:
- `grep -n "_pending_groups" bellows.py` → 7
- `grep -n "from_rescan" bellows.py` → 4
- `grep -n "settle" bellows.py` → 6
- `grep -rn "from_rescan\|settle\|defer" tests/` → 28

---

## Test Results

| Suite | Collected | Passed | Failed | Status |
|-------|-----------|--------|--------|--------|
| Targeted (parallel/group/defer/settle) | 9 | 9 | 0 | ✅ |
| Full regression | 104 | 104 | 0 | ✅ |

Evidence files:
- `knowledge/qa/evidence/parallel-defer-fix/pytest_targeted.txt`
- `knowledge/qa/evidence/parallel-defer-fix/pytest_full.txt`

---

## New Tests (Step 1 deliverable)

| Test Name | Validates | Status |
|-----------|-----------|--------|
| watchdog_adds_to_defer_dict_not_dispatched | watchdog path defers, no dispatch | ✅ |
| rescan_dispatches_after_settle_window | rescan dispatches after >5s | ✅ |
| rescan_holds_within_settle_window | rescan holds dispatch within 5s | ✅ |
| nonparallel_dispatches_immediately | non-parallel plans still dispatch immediately | ✅ |
| two_siblings_collected_as_one_group | two siblings collected into one group after settle | ✅ |

---

## Summary

Fix correctly defers parallel group dispatch from the watchdog `on_created` path to the `_rescan` tick with a 5-second settle window. All 5 new targeted tests pass. Full regression suite 104/104 green.
