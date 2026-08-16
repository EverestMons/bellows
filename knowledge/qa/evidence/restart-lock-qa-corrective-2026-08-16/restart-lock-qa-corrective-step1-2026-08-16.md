# Output Receipt — restart-lock QA corrective Step 1

**Plan:** `restart-lock-fix-qa-corrective-2026-08-16`
**Step:** 1 — add missing mock attribute (no production change)
**Status:** Complete
**Commit:** `a5b89fe` on branch `bellows-wt/431`
**Date:** 2026-08-16

---

## Approach

Per-test edits (no shared fixture). Each of the 4 tests constructs its own `MagicMock()` orchestrator independently — there is no shared helper or fixture to patch once. Added `mock_orch._shutting_down = False` to each test's setup, immediately after the existing `mock_orch._seen = set()` line.

## Exact lines added

| Test | File line (post-edit) | Line added |
|---|---|---|
| `test_handle_parallel_from_watchdog_adds_pending_not_dispatched` | `tests/test_bellows.py:1128` | `mock_orch._shutting_down = False` |
| `test_nonparallel_plan_dispatches_immediately_from_handle` | `tests/test_bellows.py:1198` | `mock_orch._shutting_down = False` |
| `test_two_parallel_siblings_collected_as_one_group` | `tests/test_bellows.py:1229` | `mock_orch._shutting_down = False` |
| `test_seen_uses_slug_not_path` | `tests/test_bellows.py:3048` | `mock_orch._shutting_down = False` |

## Verification

Targeted run: `pytest tests/test_bellows.py`

Raw summary line:

```
======================== 189 passed, 1 warning in 5.19s ========================
```

0 failures. All 4 previously-failing tests now pass.

---

### Ledger Updates

#### Prompt Feedback

Per-test mock-attribute fix applied cleanly — 4 lines added, no shared fixture available. The root cause (MagicMock auto-truthy attributes defeating a newly-added boolean gate) is a known pattern; the QA finding's specified fix (`mock_orch._shutting_down = False`) was exact and sufficient. No surprises.
