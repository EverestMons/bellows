# Bellows isinstance Asymmetry Fix — Dev Log

**Date:** 2026-05-21
**Plan:** executable-bellows-isinstance-asymmetry-fix-2026-05-21
**Authority:** 2026-05-21 isinstance-asymmetry diagnostic findings (`knowledge/research/bellows-isinstance-asymmetry-2026-05-21.md`)

## Anchor

Line 594 in `bellows.py` — the only occurrence of `f["gate"] == "rule_22_verification"` without a defensive `isinstance(f, dict)` guard.

## Before (lines 591–597)

```python
                or not effective_auto_close):
            log_path = str(BELLOWS_ROOT / "logs")
            if not gate_result["passed"]:
                if all(f["gate"] == "rule_22_verification" for f in gate_result["failures"]):
                    _pause_reason = "rule_22_check_failed"
                else:
                    _pause_reason = "gate_failure"
```

## After (lines 591–597)

```python
                or not effective_auto_close):
            log_path = str(BELLOWS_ROOT / "logs")
            if not gate_result["passed"]:
                if all(isinstance(f, dict) and f.get("gate") == "rule_22_verification" for f in gate_result["failures"]):
                    _pause_reason = "rule_22_check_failed"
                else:
                    _pause_reason = "gate_failure"
```

## Grep Verification

**Pre-edit:**
- `f["gate"] == "rule_22_verification"` → 1 match (line 594) ✓
- `isinstance(f, dict) and f.get("gate") == "rule_22_verification"` → 1 match (line 505) ✓

**Post-edit:**
- `isinstance(f, dict) and f.get("gate") == "rule_22_verification"` → 2 matches (lines 505, 594) ✓
- `f["gate"] == "rule_22_verification"` (old pattern) → 0 matches ✓

## Summary

Applied symmetric `isinstance(f, dict)` guard at bellows.py:594 (Block 2) to mirror the existing defensive pattern at line 505 (Block 1). Both blocks were introduced in commit `4bd1c84` (2026-05-21 verdict-enrichment). The asymmetry was identified as an authorial oversight per the 2026-05-21 isinstance-asymmetry diagnostic findings (Section 4, Gap Assessment row (a)). The fix adds `isinstance(f, dict) and` before `f.get("gate")` and changes direct subscript `f["gate"]` to `.get("gate")`, ensuring a graceful `gate_failure` pause instead of a `TypeError` crash on any hypothetical non-dict entry in `gate_result["failures"]`.

---
## Output Receipt
**Agent:** Bellows Developer
**Step:** 1
**Status:** Complete

### What Was Done
Applied a 1-line defensive edit at bellows.py:594 to add an `isinstance(f, dict)` guard mirroring Block 1's pattern at line 505. Verified symmetry with grep (2 matches post-edit, 0 old pattern remaining).

### Files Deposited
- `knowledge/development/bellows-isinstance-asymmetry-fix-2026-05-21.md` — this dev log

### Files Created or Modified (Code)
- `bellows.py:594` — added `isinstance(f, dict) and` guard, changed `f["gate"]` to `f.get("gate")`

### Decisions Made
- None beyond the plan specification (fully mechanical edit)

### Flags for CEO
- None

### Flags for Next Step
- The edit is purely defensive — no behavioral change on dict inputs. All tests should pass unchanged.
- The 5 pre-existing test failures (`test_run_step_timeout` + 4 `test_decisions.py`) are unrelated to this change.
