# stop_prose Pattern Narrowing — Dev Log

**Date:** 2026-06-12 | **Plan:** 29 | **Agent:** Bellows Developer | **Step:** 1

---

## Pattern Diffs

### validators.py:12-16 — STOP_PROSE_PATTERNS

**Before (3 patterns):**
```python
STOP_PROSE_PATTERNS = [
    re.compile(r"STOP\.", re.IGNORECASE),                    # Pattern 0
    re.compile(r"wait for confirmation", re.IGNORECASE),     # Pattern 1
    re.compile(r"do not proceed", re.IGNORECASE),            # Pattern 2
]
```

**After (2 patterns):**
```python
STOP_PROSE_PATTERNS = [
    re.compile(r"^\s*(?:>\s*)*STOP\.", re.IGNORECASE),                  # Pattern 0 (narrowed)
    re.compile(r"^\s*(?:>\s*)*(?:do )?not proceed", re.IGNORECASE),     # Pattern 1 (narrowed, renumbered)
]
```

### Changes applied:
1. **Pattern 0 (`STOP.`)**: Narrowed from anywhere-in-line match to imperative-at-line-start. Regex anchored to `^` with optional whitespace and blockquote markers (`>\s*`). Bold-wrapped forms (`**STOP.`) no longer match — eliminates Class 1 FP (PLANNER_TEMPLATE step-boundary blocks). Mid-sentence forms (`...and STOP.`) no longer match — eliminates Class 2 FP (error-handling prose).
2. **Pattern 1 (`wait for confirmation`)**: REMOVED. Zero activations (true or false positive) across entire operational history (2026-05-28 through 2026-06-12). Dead pattern contributing only potential noise.
3. **Pattern 2 (`do not proceed`)**: Narrowed from anywhere-in-line match to imperative-at-line-start, same anchoring as Pattern 0. Conditional forms (`If X fails, do not proceed`) no longer match — eliminates Class 3 FP (Rule 20 instructional prose) and Class 4 FP (self-referencing prose). Renumbered to Pattern 1.

### Exclusions preserved (untouched):
- Fenced code block exclusion (validators.py:88-92)
- Deposits block exclusion (validators.py:95-104)
- Inline backtick stripping (validators.py:107)

---

## Test Count Before/After

| Metric | Before | After |
|--------|--------|-------|
| Total tests (full suite) | 538 | 545 |
| New tests added | — | 7 |
| Tests modified | — | 3 (tests 6, 7, 12) |

### New tests (tests/test_validators.py):
- **Test 25** (`test_stop_prose_fp_class1_planner_template_no_fire`): Class 1 FP — `**STOP. Do NOT proceed to Step 2...` no longer fires
- **Test 26** (`test_stop_prose_fp_class2_error_handling_no_fire`): Class 2 FP — mid-sentence `...and STOP.` no longer fires
- **Test 27** (`test_stop_prose_fp_class3_rule20_instructional_no_fire`): Class 3 FP — conditional `If X fails, do not proceed` no longer fires
- **Test 28** (`test_stop_prose_fp_class4_self_referencing_no_fire`): Class 4 FP — self-referencing prose no longer fires
- **Test 29** (`test_stop_prose_dangerous_stop_at_line_start_fires`): Positive — bare `STOP.` at line start DOES fire
- **Test 30** (`test_stop_prose_dangerous_do_not_proceed_at_line_start_fires`): Positive — bare `Do not proceed` at line start DOES fire
- **Test 31** (`test_stop_prose_removed_wait_for_confirmation_no_trigger`): Regression — removed `wait for confirmation` text triggers nothing

### Modified tests:
- **Test 6** (`test_warn_stop_prose_in_bellows_mode`): Updated step_body from mid-sentence to line-start form (`"Do not proceed until verified."`)
- **Test 7** (`test_no_warn_stop_prose_in_manual_bootstrap_mode`): Same body update for consistency
- **Test 12** (`test_multiple_stop_prose_patterns_detected`): Updated to use two line-start forms (`"STOP. Wait here.\nDo not proceed until verified."`)

---

## Full Suite Tail

```
tests/test_worktree.py::test_auto_stage_handles_multiple_deposits PASSED [ 99%]
tests/test_worktree.py::test_auto_stage_noop_when_all_committed PASSED   [100%]

=============================== warnings summary ===============================
../../../../../Library/Python/3.9/lib/python/site-packages/urllib3/__init__.py:35
  /Users/marklehn/Library/Python/3.9/lib/python/site-packages/urllib3/__init__.py:35: NotOpenSSLWarning: urllib3 v2 only supports OpenSSL 1.1.1+, currently the 'ssl' module is compiled with 'LibreSSL 2.8.3'. See: https://github.com/urllib3/urllib3/issues/3020

======================== 545 passed, 1 warning in 9.65s ========================
```

---

## Output Receipt
**Agent:** Bellows Developer
**Step:** 1
**Status:** Complete

### What Was Done
Narrowed two stop_prose validator patterns to imperative-at-line-start forms and removed one zero-activation pattern, per diagnostic 27 shape A+C2. All four observed FP classes eliminated. Added 7 new tests (4 FP-class regression, 2 positive, 1 removal regression) and updated 3 existing tests. Full suite passes (545/545).

### Files Deposited
- `bellows/knowledge/development/stop-prose-narrowing-dev-log-2026-06-12.md` — this dev log

### Files Created or Modified (Code)
- `validators.py` — narrowed STOP_PROSE_PATTERNS (lines 12-15): 3 patterns → 2 patterns, line-start anchoring
- `tests/test_validators.py` — added tests 25-31, updated tests 6/7/12

### Decisions Made
- Excluded bold markers (`\*{0,2}`) from the narrowed STOP regex to ensure Class 1 FP (PLANNER_TEMPLATE `**STOP...`) does not fire — the diagnostic's illustrative regex included bold markers, but the plan's test requirements (all 4 FP classes must not fire) require excluding them
- Used `re.IGNORECASE` on both narrowed patterns for consistency with original implementation

### Flags for CEO
- Restart pending-set now includes plans 24, 28, and 29 (stop_prose is a claim-time validator, not a runtime gate, so urgency is low)

### Flags for Next Step
- The narrowed patterns preserve blockquote-prefixed forms (`> STOP.`, `> Do not proceed`) as matches — QA should verify this is intentional via corpus replay
