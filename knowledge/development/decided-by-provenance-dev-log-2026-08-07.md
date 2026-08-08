# Dev Log — decided_by transition provenance (plan 313)

**Date:** 2026-08-07
**Plan:** 313 — record decided_by transition provenance: gate_auto vs verdict_file
**Depends on:** 312 (shipped the invariant 3 characterization test that pinned the gap)

---

## Task B — bellows.py edits

### Site 1 (prose path) — bellows.py:2121

**Before:**
```python
lifecycle.record_verdict_outcome(_lc_plan_id, step_number, v, decided_by="ceo", disposition_summary=reason)
```

**After:**
```python
lifecycle.record_verdict_outcome(_lc_plan_id, step_number, v, decided_by="verdict_file", disposition_summary=reason)
```

### Site 2 (auto-close path) — bellows.py:935-937

**Before:** no lifecycle calls existed between `verdict.log_to_ledger(...)` and `done_dir = ...`

**After (inserted):**
```python
# Record mechanical auto-continue so the transition is auditable (312 gap)
lifecycle.record_verdict_request(plan_id, current_step, pause_reason_code="auto_close")
lifecycle.record_verdict_outcome(plan_id, current_step, "continue", decided_by="gate_auto")
```

---

## Task C — invariant 3 flip

Replaced `TestDecidedByGap.test_both_verdicts_record_ceo` (plan 312's characterization test asserting both rows are `"ceo"`) with `TestDecidedByDiscrimination.test_gate_auto_and_verdict_file_are_distinct`. The new test records one outcome with `decided_by="gate_auto"` and one with `decided_by="verdict_file"`, then asserts they are DISTINCT and each equals its expected literal. Docstring updated to state the gap is CLOSED and references plan 313.

---

## Task D — auto-close provenance test

Added `TestAutoCloseProvenance.test_auto_close_produces_gate_auto_row` to `test_gate_transaction_mechanization.py`. The test asserts at the lifecycle layer that `record_verdict_request(pause_reason_code="auto_close")` + `record_verdict_outcome(decided_by="gate_auto")` produces a queryable row with `outcome="continue"`, `decided_by="gate_auto"`, and `pause_reason_code="auto_close"`.

**run_plan-level assertion decision:** deferred. The auto-close branch in `run_plan` requires extensive mocking (worktree, gates, notifier, validators, response_server, etc.) already covered by `test_bellows.py::test_diagnostic_auto_close_moves_to_done`. The lifecycle-layer test isolates the provenance guarantee without duplicating that harness. A comment in the test class docstring states this rationale explicitly.

---

## Task E — targeted test output (RAW)

```
......................................                                   [100%]
=============================== warnings summary ===============================
../../../Library/Python/3.9/lib/python/site-packages/urllib3/__init__.py:35
  /Users/marklehn/Library/Python/3.9/lib/python/site-packages/urllib3/__init__.py:35: NotOpenSSLWarning: urllib3 v2 only supports OpenSSL 1.1.1+, currently the 'ssl' module is compiled with 'LibreSSL 2.8.3'. See: https://github.com/urllib3/urllib3/issues/3020
    warnings.warn(

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
38 passed, 148 deselected, 1 warning in 0.69s
EXIT_CODE=0
```

All 38 selected tests passed. Exit code 0.

---

### Ledger Updates

#### Prompt Feedback

None — the plan's specifications were unambiguous and the implementation followed them directly. The quoted anchors for both bellows.py sites matched exactly. The lifecycle layer test approach for Task D was the right call — the plan's explicit instruction to state why the run_plan-level assertion was included or deferred made the decision transparent.
