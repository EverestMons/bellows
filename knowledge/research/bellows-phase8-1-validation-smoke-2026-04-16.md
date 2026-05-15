# Bellows Phase 8.1 Validation Smoke — Findings

**Date:** 2026-04-16
**Plan:** diagnostic-bellows-phase8-1-validation-smoke-2026-04-16.md
**Step:** 1 (DEV — Investigation)

## Question

What are the four return branches of `header_says_pause` in `bellows.py`, and what values of `pause_for_verdict` cause it to return `True`?

## Findings

Function location: `bellows.py:123`

```python
def header_says_pause(header: dict, current_step: int, total_steps: int, is_qa_step: bool) -> bool:
    """Return True if plan header's pause_for_verdict field matches current step."""
    pv = header.get("pause_for_verdict", "")
    if pv == "always":
        return True
    if pv == "after_step_1":
        return current_step == 1
    if pv == "after_qa_step":
        return is_qa_step
    return False
```

### Four Return Branches

1. **`pv == "always"`** → returns `True` unconditionally. Every step pauses for verdict.
2. **`pv == "after_step_1"`** → returns `True` when `current_step == 1`, `False` otherwise. Pauses only on the first step.
3. **`pv == "after_qa_step"`** → returns `True` when `is_qa_step == True`, `False` otherwise. Pauses whenever the gate check flags the current step as a QA step.
4. **Any other value** (including the default empty string `""`) → returns `False`. No pause triggered by header.

### This Diagnostic's Behavior

This plan file has no YAML header, so `header.get("pause_for_verdict", "")` returns `""` — branch 4 applies and `header_says_pause` returns `False`. The final-step pause in Phase 8.1 is triggered instead by `not effective_auto_close` (`bellows.py:251`), because `effective_auto_close` defaults to `"false"` for diagnostics (no `auto_close: true` header). The gate check at `bellows.py:247–251` evaluates to `True` via that condition, correctly routing the plan to `verdict-pending` status.

---

## Output Receipt

| Field | Value |
|---|---|
| Status | Complete |
| Step | 1 |
| Files written | `knowledge/research/bellows-phase8-1-validation-smoke-2026-04-16.md` |
| Files modified | `knowledge/research/agent-prompt-feedback.md` |
| Source files read | `bellows.py` |
| Scope | Read-only on source; deposit only |
