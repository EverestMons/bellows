# QA Receipt — restart-lock QA corrective

**Plan:** `restart-lock-fix-qa-corrective-2026-08-16`
**Step:** 2 — QA (full suite green)
**Status:** PASS
**Date:** 2026-08-16
**Branch:** `bellows-wt/431`

---

## Pre-step check

| Dev-log | Status |
|---|---|
| `restart-lock-qa-corrective-step1-2026-08-16.md` | Complete |

Step 1 (commit `a5b89fe`) added `mock_orch._shutting_down = False` to 4 tests in `tests/test_bellows.py` — per-test edits, no shared fixture.

---

## (B) Verification

### Full test suite

| Metric | Value |
|---|---|
| Pre-fix baseline (430 landed) | 1049 passed, 4 failed |
| Fix applied (Step 1) | 4 mock-orchestrator `_shutting_down` attributes added |
| Expected total | 1053 passed, 0 failed |
| Actual total | ✅ 1053 passed, 0 failed |

Raw summary line:

```
======================= 1053 passed, 1 warning in 31.83s =======================
```

Raw output: `full-suite-output.txt`

### Previously-failing tests — now PASS

All 4 tests that regressed in 430's QA now pass:

```
tests/test_bellows.py::test_handle_parallel_from_watchdog_adds_pending_not_dispatched PASSED [  3%]
tests/test_bellows.py::test_nonparallel_plan_dispatches_immediately_from_handle PASSED [  3%]
tests/test_bellows.py::test_two_parallel_siblings_collected_as_one_group PASSED [  3%]
tests/test_bellows.py::test_seen_uses_slug_not_path PASSED               [  9%]
```

### (C) Live daemon

No signals sent to the live daemon (PID 3969). All verification via test suite only.

---

### Ledger Updates

#### Prompt Feedback

Corrective fix was mechanical and exact — the QA finding from 430 specified the 4 tests and the fix (`mock_orch._shutting_down = False`), Step 1 applied it per-test, and the full suite greened on first run. No surprises.

---

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: knowledge/qa/evidence/restart-lock-qa-corrective-2026-08-16/
Files verified: 2
```

