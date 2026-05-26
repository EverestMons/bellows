# Verdict Ledger Gate-Result Preservation — Dev Log

**Date:** 2026-05-26 | **Agent:** Bellows Developer
**Plan:** executable-verdict-ledger-gate-result-preservation-2026-05-26
**Step:** 1 (DEV)

---

## Baseline

- **Pre-fix pytest:** 5 failed, 402 passed, 1 warning
- **Post-fix pytest:** 5 failed, 407 passed, 1 warning
- **Delta:** +5 tests passed (all new tests), 0 regressions

---

## Q6 Anchor Verification

All 16 anchors from the SA diagnostic Q7 verified against live code before editing. No line-number drift detected.

---

## Production Edits

### Change 1: verdict.py — Gate Result JSON metadata line

**File:** `verdict.py:235` (after `**Gate Result Passed:**` line)
**Before:** Line 234 followed directly by `**Total Steps:**` line
**After:** New line inserted:
```python
f"**Gate Result JSON:** {json.dumps({'failures': gate_result.get('failures', []), 'files_changed': gate_result.get('files_changed', [])})}\n"
```

### Change 2: bellows.py — Initialize gate_result_from_request

**File:** `bellows.py:1186` (after `precondition_failure_from_request = False`)
**Before:** No `gate_result_from_request` variable
**After:**
```python
gate_result_from_request = None
```

### Change 3: bellows.py — Parse Gate Result JSON metadata

**File:** `bellows.py:1206-1210` (after Precondition Failure parse block, inside `for req_line` loop)
**Before:** Loop ended after Precondition Failure parse
**After:**
```python
if req_line.startswith("**Gate Result JSON:**"):
    try:
        gate_result_from_request = json.loads(req_line.split(":**", 1)[1].strip())
    except (json.JSONDecodeError, IndexError):
        pass
```

### Change 4: bellows.py — Replace unconditional empty dict with fallback

**File:** `bellows.py:1231`
**Before:**
```python
gate_result = {"failures": [], "files_changed": []}
```
**After:**
```python
gate_result = gate_result_from_request or {"failures": [], "files_changed": []}
```

### Fix F: bellows.py — Terminal log expansion (two sites)

**File:** `bellows.py:496` and `bellows.py:589`
**Before (both sites):**
```python
_log("EVENT", f"gates step {current_step}: passed={gate_result['passed']}, failures={len(gate_result['failures'])}", slug=slug_for(plan_name))
```
**After (both sites):**
```python
failure_gates = ", ".join((f["gate"] if isinstance(f, dict) else str(f)) for f in gate_result["failures"]) if gate_result["failures"] else "none"
_log("EVENT", f"gates step {current_step}: passed={gate_result['passed']}, failures={len(gate_result['failures'])} ({failure_gates}), files_changed={len(gate_result.get('files_changed', []))}", slug=slug_for(plan_name))
```

**Note:** Added `isinstance(f, dict)` guard because one pre-existing test (`test_run_plan_inprogress_entry_renames_to_verdict_pending`) uses string-typed failures (`["scope_check"]` instead of `[{"gate": "scope_check", ...}]`). The guard handles both formats gracefully. This is a minor deviation from Q6's verbatim snippet — Q6 specified `f["gate"]` without the isinstance guard.

---

## New Tests (5)

| # | Test | File | Assertion |
|---|---|---|---|
| 1 | `test_post_verdict_request_includes_gate_result_json` | `tests/test_verdict.py` | Calls `post_verdict_request` with real failures/files_changed, asserts rendered markdown contains `**Gate Result JSON:**` line whose JSON parses back to the input subset |
| 2 | `test_consume_verdicts_parses_gate_result_json_continue_to_done` | `tests/test_consume_verdicts.py` | Fixture pending file with metadata line, continue on final step, asserts `log_to_ledger` receives populated arrays |
| 3 | `test_consume_verdicts_parses_gate_result_json_continue_resume` | `tests/test_consume_verdicts.py` | Same for non-final continue path, asserts `log_to_ledger` receives populated arrays |
| 4 | `test_consume_verdicts_falls_back_to_empty_when_metadata_absent` | `tests/test_consume_verdicts.py` | Pre-fix-shape pending file without metadata line, asserts `log_to_ledger` receives empty arrays (backward compat) |
| 5 | `test_gates_log_includes_failure_gates_and_files_changed_count` | `tests/test_bellows.py` | Gates return 2 failures + 3 files_changed, asserts log message includes failure gate names and `files_changed=3` |

---

## Anchor-Drift Surprises

None. All 16 Q7 anchors matched exactly.

One pre-existing test fixture surprise: `test_run_plan_inprogress_entry_renames_to_verdict_pending` uses non-standard string-typed failures, requiring the `isinstance` guard in Fix F. This was not flagged by the SA diagnostic.

---

## Output Receipt

**Agent:** Bellows Developer
**Step:** 1
**Status:** Complete

### What Was Done

Implemented E.4 (JSON metadata line for gate_result preservation) and Fix F (terminal log expansion) per the SA diagnostic Q6 hand-off. Added 5 unit tests covering the write path, all three consume paths, backward compatibility, and the expanded log format. Full pytest suite passes with the same 5 pre-existing failures and +5 new tests.

### Files Deposited

- `knowledge/development/verdict-ledger-gate-result-preservation-2026-05-26.md` — this dev log
- `knowledge/qa/evidence/executable-verdict-ledger-gate-result-preservation-2026-05-26/pytest_full_dev.txt` — full pytest output

### Files Created or Modified (Code)

- `verdict.py` — +1 line (Gate Result JSON metadata)
- `bellows.py` — +10 lines (init, parse, replace, 2x log expansion)
- `tests/test_verdict.py` — +1 test
- `tests/test_consume_verdicts.py` — +3 tests
- `tests/test_bellows.py` — +1 test

### Decisions Made

- Added `isinstance(f, dict)` guard to Fix F log computation to handle pre-existing test with string-typed failures

### Flags for CEO

- None

### Flags for Next Step

- QA should verify the `isinstance` guard is appropriate and not masking a test fixture bug
