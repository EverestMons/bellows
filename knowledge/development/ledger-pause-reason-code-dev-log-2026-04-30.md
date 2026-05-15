# Dev Log — Ledger pause_reason_code Schema Enhancement
**Date:** 2026-04-30
**Plan:** parallel-1-executable-ledger-pause-reason-code-2026-04-30
**BACKLOG:** #12

---

## 1. log_to_ledger() Signature — Before / After

**Before:**
```python
def log_to_ledger(plan_path, step_number, gate_result, verdict, reason):
```

**After:**
```python
def log_to_ledger(plan_path, step_number, gate_result, verdict, reason, pause_reason_code: Optional[str] = None):
```

## 2. Entry Dict — Before / After

**Before:**
```python
entry = {
    "timestamp": datetime.now().isoformat(),
    "plan_path": plan_path,
    "step": step_number,
    "gate_failures": gate_result.get("failures", []),
    "files_changed": gate_result.get("files_changed", []),
    "verdict": verdict,
    "reason": reason,
}
```

**After:**
```python
entry = {
    "timestamp": datetime.now().isoformat(),
    "plan_path": plan_path,
    "step": step_number,
    "gate_failures": gate_result.get("failures", []),
    "files_changed": gate_result.get("files_changed", []),
    "verdict": verdict,
    "reason": reason,
    "pause_reason_code": pause_reason_code,
}
```

## 3. Call Sites Updated in bellows.py

### Call Site 1 — Auto-close path (run_plan, line ~413)

**Before:**
```python
verdict.log_to_ledger(plan_path, current_step, gate_result, "auto-close",
                      "all gates passed, auto_close enabled — auto-closing")
```

**After:**
```python
verdict.log_to_ledger(plan_path, current_step, gate_result, "auto-close",
                      "all gates passed, auto_close enabled — auto-closing",
                      pause_reason_code="auto_close")
```

### Call Site 2 — Continue-to-done (_consume_verdicts, line ~727)

**Before:**
```python
verdict.log_to_ledger(full_plan_path, step_number, gate_result,
                      "continue-to-done",
                      "continue verdict on final step — moving to Done")
```

**After:**
```python
verdict.log_to_ledger(full_plan_path, step_number, gate_result,
                      "continue-to-done",
                      "continue verdict on final step — moving to Done",
                      pause_reason_code=pause_reason_code_from_request)
```

### Call Site 3 — Continue non-final (_consume_verdicts, line ~740)

**Before:**
```python
verdict.log_to_ledger(full_plan_path, step_number, gate_result, v, reason)
```

**After:**
```python
verdict.log_to_ledger(full_plan_path, step_number, gate_result, v, reason,
                      pause_reason_code=pause_reason_code_from_request)
```

### Call Site 4 — Stop verdict (_consume_verdicts, line ~748)

**Before:**
```python
verdict.log_to_ledger(full_plan_path, step_number, gate_result, v, reason)
```

**After:**
```python
verdict.log_to_ledger(full_plan_path, step_number, gate_result, v, reason,
                      pause_reason_code=pause_reason_code_from_request)
```

### Supporting change — pause_reason_code extraction from pending request file

Added `pause_reason_code_from_request` extraction in `_consume_verdicts()` alongside existing `total_steps_from_request` parsing:

```python
pause_reason_code_from_request = None
# ... inside the pending_req_file parsing loop:
if req_line.startswith("**Pause Reason Code:**"):
    pause_reason_code_from_request = req_line.split(":**", 1)[1].strip() or None
```

This extracts the `**Pause Reason Code:**` field written by `post_verdict_request()` so that verdict consumption paths log the original pause reason that triggered the pause.

## 4. Test Additions

Three new tests added to `tests/test_verdict.py`:

### test_log_to_ledger_without_pause_reason_code
Legacy behavior: calling `log_to_ledger` without `pause_reason_code` produces an entry with `"pause_reason_code": null` in the JSONL.

### test_log_to_ledger_with_pause_reason_code_qa_checkpoint
Explicit `pause_reason_code="qa_checkpoint"` round-trips correctly through write/read.

### test_log_to_ledger_all_pause_reason_codes
Parametric test: each of the 6 documented pause reason codes (`auto_close_disabled`, `qa_checkpoint`, `gate_failure`, `header_pause`, `agent_verdict_request`, `auto_close`) persists correctly when passed to `log_to_ledger`.

## 5. Test Run Output

```
============================= test session starts ==============================
platform darwin -- Python 3.9.6, pytest-8.4.2, pluggy-1.6.0
collected 14 items

tests/test_verdict.py ..............                                     [100%]

============================== 14 passed in 0.03s
==============================
```

14 tests total (11 existing + 3 new), all passing.

## 6. Deviations from Plan

**One design decision beyond the plan's ~5 LOC estimate:** For the 3 `_consume_verdicts` call sites, rather than passing `None` with TODO comments, I extracted `pause_reason_code_from_request` from the pending verdict request file (which already contains `**Pause Reason Code:**` written by `post_verdict_request()`). This adds ~3 lines of extraction code but produces accurate ledger entries for verdict-consumption paths rather than leaving data gaps. The extraction follows the same pattern as the existing `total_steps_from_request` parsing in the same code block.

---

## Output Receipt
**Agent:** Bellows Developer
**Step:** 1
**Status:** Complete

### What Was Done
Extended `verdict.py::log_to_ledger()` with an optional `pause_reason_code` parameter that persists to JSONL ledger entries. Updated all 4 call sites in `bellows.py` to pass the appropriate pause reason code. Added 3 new tests covering legacy (None), explicit, and exhaustive pause reason code scenarios.

### Files Deposited
- `bellows/knowledge/development/ledger-pause-reason-code-dev-log-2026-04-30.md` — this dev log

### Files Created or Modified (Code)
- `bellows/verdict.py` — added `pause_reason_code` parameter to `log_to_ledger()` and `"pause_reason_code"` field to entry dict
- `bellows/bellows.py` — updated 4 `log_to_ledger()` call sites with pause_reason_code; added `pause_reason_code_from_request` extraction in `_consume_verdicts()`
- `bellows/tests/test_verdict.py` — added 3 new tests (legacy None, explicit qa_checkpoint, all 6 codes)

### Decisions Made
- Extracted `pause_reason_code_from_request` from pending verdict request file for `_consume_verdicts` call sites (rather than passing `None` with TODO) — data is already available in the file, follows existing `total_steps_from_request` extraction pattern

### Flags for CEO
- None

### Flags for Next Step
- The `pause_reason_code` field will be `None` for ledger entries written before this change (backward compatible). New entries will have the field populated. QA should verify round-trip persistence via smoke test.
