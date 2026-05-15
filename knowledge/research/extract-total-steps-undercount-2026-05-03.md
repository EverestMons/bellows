# Diagnostic: extract_total_steps() Undercount — Findings
**Date:** 2026-05-03 | **Plan:** diagnostic-extract-total-steps-undercount-2026-05-03

---

## Phase 1 — Locate and read `extract_total_steps()`

The function is at `bellows.py:88-93`:

```python
def extract_total_steps(plan_text: str) -> int:
    case_insensitive_count = len(re.findall(r"^## STEP\s+\d+", plan_text, re.MULTILINE | re.IGNORECASE))
    case_sensitive_count = len(re.findall(r"^## STEP\s+\d+", plan_text, re.MULTILINE))
    if case_insensitive_count > 0 and case_sensitive_count == 0:
        print(f"Bellows: ⚠️  WARNING: plan has step headers but case does not match expected '## STEP N' — count={case_insensitive_count} matched case-insensitively")
    return case_insensitive_count
```

- **Regex:** `r"^## STEP\s+\d+"`
- **Flags:** `re.MULTILINE | re.IGNORECASE`
- **Return type:** `int`

**Call sites:**

1. `bellows.py:227` — initial dispatch in `run_plan()`:
   ```python
   total_steps = extract_total_steps(metadata_text)   # line 227
   if is_diagnostic:                                    # line 228
       total_steps = 1                                  # line 229
   ```

2. `bellows.py:690-703` — continue-verdict handler:
   ```python
   is_diag = original_name.startswith("diagnostic-")   # line 690
   if is_diag:                                          # line 691
       total_steps_c = 1                                # line 692
   else:                                                # line 693
       # ... calls extract_total_steps() at line 697/703
   ```

Both call sites **override** the result to `1` when the plan filename starts with `"diagnostic-"`.

---

## Phase 2 — Run the regex against the two failing plans

### Plan 1: `diagnostic-parallel-scope-check-collision-2026-05-03.md`

```
Expected step count: 2
Actual regex match count: 2
  Match at line 18: '## STEP 1'
  Match at line 50: '## STEP 2'
  → OK: regex correctly finds 2 steps
```

### Plan 2: `diagnostic-worktree-implementation-surface-2026-05-03.md`

```
Expected step count: 3
Actual regex match count: 3
  Match at line 20: '## STEP 1'
  Match at line 60: '## STEP 2'
  Match at line 102: '## STEP 3'
  → OK: regex correctly finds 3 steps
```

**The regex is not the problem.** `extract_total_steps()` returns the correct count for both plans. The count is overridden after the function returns.

---

## Phase 3 — Control case: known-passing multi-step plans

### Control 1: `executable-bellows-reliability-bugs-1-2-3-2026-04-24.md`

```
Match count: 3
  Match at line 16: '## STEP 1'
  Match at line 42: '## STEP 2'
  Match at line 70: '## STEP 3'
Filename starts with 'diagnostic-': False
→ is_diagnostic override does NOT apply → dispatched as 3 steps ✓
```

### Control 2: `executable-deposits-block-regex-blank-line-2026-04-28.md`

```
Match count: 2
  Match at line 22: '## STEP 1'
  Match at line 34: '## STEP 2'
Filename starts with 'diagnostic-': False
→ is_diagnostic override does NOT apply → dispatched as 2 steps ✓
```

**Differentiating factor:** The control plans have filenames starting with `executable-`, so the `is_diagnostic` override on line 228-229 does not fire. The failing plans have filenames starting with `diagnostic-`, so the override fires and forces `total_steps = 1` regardless of actual step count.

---

## Phase 4 — Cause identified

The cause is **none of the four suspected regex issues** (header interference, em-dash, anchor, shadow cache). The regex works correctly.

The cause is a **hardcoded `is_diagnostic` override** at two locations in `bellows.py`:

1. **Line 228-229** (`run_plan()` initial dispatch):
   ```python
   if is_diagnostic:
       total_steps = 1
   ```
   `is_diagnostic` is set at line 226: `is_diagnostic = os.path.basename(plan_path).startswith("diagnostic-")`

2. **Line 690-692** (continue-verdict handler):
   ```python
   is_diag = original_name.startswith("diagnostic-")
   if is_diag:
       total_steps_c = 1
   ```

Both locations unconditionally set the step count to 1 for any plan whose filename begins with `"diagnostic-"`. This was presumably correct when all diagnostics were single-step, but multi-step diagnostics now exist and are miscounted.

The `extract_total_steps()` function itself is correct and returns the right count. The override discards it.

---

## Phase 5 — Shadow cache cross-check

Shadow cache files for the two failing plans **do not exist**:

- `.bellows-cache/diagnostic-parallel-scope-check-collision-2026-05-03.pristine` — **not found**
- `.bellows-cache/diagnostic-worktree-implementation-surface-2026-05-03.pristine` — **not found**

This means `_read_shadow()` returned `None` for both, and `metadata_text` fell through to the live `plan_text` at line 224. The shadow cache is not a factor in this bug.

(Note: the shadow cache file for the *current* diagnostic plan — `diagnostic-extract-total-steps-undercount-2026-05-03.md.pristine` — does exist, confirming the shadow system works in general; these two plans simply weren't cached.)

---

## Cause Identified

**The `extract_total_steps()` regex is correct and not the cause.** The undercount is caused by hardcoded `is_diagnostic` overrides at `bellows.py:228-229` and `bellows.py:690-692` that unconditionally set `total_steps = 1` for any plan whose filename starts with `"diagnostic-"`. This override discards the correct count returned by `extract_total_steps()`. Both failing plans are multi-step diagnostics (2 and 3 steps respectively) that are force-counted as 1 step. Control executable plans with the same `## STEP N` header format are counted correctly because the override does not apply to them. Phase 2 (regex output) and Phase 3 (control comparison) provide the literal evidence; Phase 5 rules out shadow cache divergence.
