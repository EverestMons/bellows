# no_permission_denials Read-Class Fix — Dev Log

**Date:** 2026-04-28
**Plan:** executable-no-permission-denials-read-class-fix-2026-04-28
**Step:** 1 (Bellows Developer)
**Diagnostic:** knowledge/research/no-permission-denials-taxonomy-2026-04-28.md

---

## Changes Made

### 1. READ_CLASS_TOOLS constant added (gates.py:17-20)

```python
READ_CLASS_TOOLS = {"Grep", "Glob", "Read"}
```

Added after `SCOPE_ALLOWLIST_PREFIXES`. These three read-class tools have bash equivalents that agents use as fallbacks when permissions deny the tool call.

### 2. _gate_no_permission_denials modified (gates.py:106-120)

**Before:**
```python
def _gate_no_permission_denials(parsed, failures):
    denials = parsed.get("permission_denials", [])
    if denials:
        first = denials[0] if isinstance(denials[0], str) else str(denials[0])
        failures.append({
            "gate": "no_permission_denials",
            "evidence": f"{len(denials)} denial(s): {first}",
        })
```

**After:**
```python
def _gate_no_permission_denials(parsed, failures):
    denials = parsed.get("permission_denials", [])
    blocking = []
    for d in denials:
        if isinstance(d, dict):
            tool_name = d.get("tool_name")
            if tool_name in READ_CLASS_TOOLS:
                continue
            blocking.append(d)
        else:
            # String-form denial (legacy) has no tool_name — default to blocking
            blocking.append(d)
    if blocking:
        first = blocking[0] if isinstance(blocking[0], str) else str(blocking[0])
        failures.append({
            "gate": "no_permission_denials",
            "evidence": f"{len(blocking)} blocking denial(s): {first}",
        })
```

Key changes: iterates denials, filters read-class by `tool_name` lookup in `READ_CLASS_TOOLS`, string-form denials default to blocking (no tool_name to classify). Evidence string updated from "denial(s)" to "blocking denial(s)".

### 3. New test functions (tests/test_gates.py)

7 new tests added after `test_permission_denials_nonempty`:

1. `test_permission_denials_read_class_only_passes` — Grep+Glob+Read dicts, gate passes
2. `test_permission_denials_write_class_fails` — Edit dict, gate fails
3. `test_permission_denials_mixed_read_write_fails` — Grep+Edit, gate fails with count=1
4. `test_permission_denials_missing_tool_name_fails` — dict without tool_name key, fails
5. `test_permission_denials_none_tool_name_fails` — tool_name: None, fails
6. `test_permission_denials_unknown_tool_fails` — tool_name: "SomeNewTool", fails
7. `test_permission_denials_string_form_fails` — string-form legacy denial, fails

Existing `test_permission_denials_nonempty` updated: evidence assertion changed from `"1 denial"` to `"1 blocking denial"` to match new evidence format.

### 4. Targeted test output

```
tests/test_gates.py: 29 passed in 0.03s
```

All 22 existing + 7 new tests pass. Zero regressions.

---

## Output Receipt
**Agent:** Bellows Developer
**Step:** 1
**Status:** Complete

### What Was Done
Added `READ_CLASS_TOOLS` constant, modified `_gate_no_permission_denials` to filter read-class denials, added 7 edge-case tests per diagnostic Q5 table.

### Files Created or Modified (Code)
- `bellows/gates.py` — READ_CLASS_TOOLS constant + modified gate function
- `bellows/tests/test_gates.py` — 7 new tests + 1 existing test assertion updated

### Files Deposited
- `bellows/knowledge/development/no-permission-denials-read-class-fix-dev-2026-04-28.md`

### Decisions Made
- Evidence string changed from "denial(s)" to "blocking denial(s)" to distinguish filtered output from original
- Existing test assertion updated to match new evidence format (compatible change)

### Flags for CEO
- None

### Flags for Next Step
- None
