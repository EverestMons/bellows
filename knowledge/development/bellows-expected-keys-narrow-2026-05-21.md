# Dev Log — expected-keys warning narrow to pause_for_verdict only

**Date:** 2026-05-21
**Plan:** executable-bellows-expected-keys-narrow-2026-05-21
**Step:** 1 (DEV)
**File:** bellows.py:416-419

---

## Anchor Block (4 lines, removed)

```python
        expected_keys = {"project", "date", "author", "total_steps", "pause_for_verdict"}
        missing_keys = expected_keys - set(header.keys())
        if total_steps > 1 and missing_keys:
            _log("WARN", f"⚠️ {total_steps} steps but parsed header is missing: {sorted(missing_keys)}. Parsed keys: {sorted(header.keys())}. If pause_for_verdict was missing, the defensive default has set it to after_step_1.", slug=slug_for(plan_name))
```

## Replacement Block (2 lines)

```python
        if total_steps > 1 and "pause_for_verdict" not in header:
            _log("WARN", f"⚠️ {total_steps}-step plan missing pause_for_verdict — plan will auto-advance without pausing at intermediate steps", slug=slug_for(plan_name))
```

## Before/After Context (lines 413-420)

### Before

```python
            return
        _log("INFO", f"plan has {total_steps} steps", slug=slug_for(plan_name))
        expected_keys = {"project", "date", "author", "total_steps", "pause_for_verdict"}
        missing_keys = expected_keys - set(header.keys())
        if total_steps > 1 and missing_keys:
            _log("WARN", f"⚠️ {total_steps} steps but parsed header is missing: {sorted(missing_keys)}. Parsed keys: {sorted(header.keys())}. If pause_for_verdict was missing, the defensive default has set it to after_step_1.", slug=slug_for(plan_name))
        if model != config["default_model"]:
            _log("INFO", f"using model override: {model}", slug=slug_for(plan_name))
```

### After

```python
            return
        _log("INFO", f"plan has {total_steps} steps", slug=slug_for(plan_name))
        if total_steps > 1 and "pause_for_verdict" not in header:
            _log("WARN", f"⚠️ {total_steps}-step plan missing pause_for_verdict — plan will auto-advance without pausing at intermediate steps", slug=slug_for(plan_name))
        if model != config["default_model"]:
            _log("INFO", f"using model override: {model}", slug=slug_for(plan_name))
```

## Grep Verification

### Pre-edit

| Pattern | Expected | Actual | Status |
|---------|----------|--------|--------|
| `expected_keys = {` | 1 match (line 416) | 1 match (line 416) | PASS |
| `sparse header` | 1 match (line 383) | 1 match (line 383) | PASS |

### Post-edit

| Pattern | Expected | Actual | Status |
|---------|----------|--------|--------|
| `expected_keys = {` | 0 matches | 0 matches | PASS |
| `sparse header` | 1 match (line 383) | 1 match (line 383) | PASS |

## Authority

This edit implements Shape C from the 2026-05-21 expected-keys-shape-choice diagnostic (`knowledge/decisions/Done/diagnostic-bellows-expected-keys-shape-choice-2026-05-21.md`, findings at `knowledge/research/bellows-expected-keys-shape-choice-2026-05-21.md`), which was itself informed by the 2026-05-21 expected-keys-warning diagnostic (`knowledge/decisions/Done/diagnostic-bellows-expected-keys-warning-2026-05-21.md`, findings at `knowledge/research/bellows-expected-keys-warning-2026-05-21.md`). Shape C narrows the warning from a generic 5-key expected-keys set to a targeted `pause_for_verdict` check. The rationale is that `pause_for_verdict` is the only safety-critical key in the set — the other four (project, date, author, total_steps) are cosmetic metadata that the Planner template does not reliably emit, making the broad warning a false-positive generator. Shape C touches only the warning block (lines 416-419), leaving `_apply_defensive_header_defaults` and its call convention unchanged, so existing unit tests are unaffected.

## Test Impact Note

`grep -n 'pause_for_verdict' tests/test_bellows.py | grep -i warn` returned the following matches:

| Line | Content |
|------|---------|
| 2569 | `def test_warning_multi_step_plan_without_pause_for_verdict(capsys):` |
| 2570 | `"""Multi-step plan without pause_for_verdict header emits a sparse-header warning` |
| 2632 | `def test_no_warning_multi_step_plan_with_pause_for_verdict(capsys):` |
| 2633 | `"""Multi-step plan WITH pause_for_verdict header does NOT emit the warning."""` |
| 2686 | `f"Warning should NOT appear when pause_for_verdict is declared. stdout:\n{captured.out}"` |
| 2689 | `def test_no_warning_single_step_plan_without_pause_for_verdict(capsys):` |
| 2690 | `"""Single-step plan without pause_for_verdict header does NOT emit the warning."""` |
| 2747 | `"""Multi-step plan with pause_for_verdict: always does NOT emit the warning."""` |
| 2800 | `f"Warning should NOT appear when pause_for_verdict is 'always'. stdout:\n{captured.out}"` |

The test `test_warning_multi_step_plan_without_pause_for_verdict` at line 2569 likely asserts against the old warning text (`"steps but parsed header is missing"`) and will need its assertion updated to match the new warning text (`"will auto-advance without pausing at intermediate steps"`). The QA agent should handle this in Step 2.

---

## Output Receipt
**Agent:** Bellows Developer
**Step:** 1
**Status:** Complete

### What Was Done
Replaced the 4-line `expected_keys`/`missing_keys` warning block at bellows.py:416-419 with a 2-line targeted `pause_for_verdict` check, implementing Shape C from the 2026-05-21 expected-keys-shape-choice diagnostic.

### Files Deposited
- `knowledge/development/bellows-expected-keys-narrow-2026-05-21.md` — this dev log

### Files Created or Modified (Code)
- `bellows.py` — lines 416-419: replaced 4-line expected_keys/missing_keys block with 2-line pause_for_verdict check

### Decisions Made
- None — edit was fully specified by the plan

### Flags for CEO
- None

### Flags for Next Step
- Test `test_warning_multi_step_plan_without_pause_for_verdict` (test_bellows.py:2569) likely needs assertion update to match new warning text
- The three negative tests (lines 2632, 2689, 2747) may also need docstring or assertion updates depending on what they assert against
