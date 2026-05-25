# MCP READ_CLASS_TOOLS Extension — Dev Log

**Date:** 2026-05-25 | **Agent:** Bellows Developer | **Plan:** executable-mcp-read-class-tools-extension-2026-05-25 | **Step:** 1

---

## (a) READ_CLASS_TOOLS Diff

`gates.py` line 35 — before:

```python
READ_CLASS_TOOLS = {"Grep", "Glob", "Read", "mcp__vexp__run_pipeline"}
```

After:

```python
READ_CLASS_TOOLS = {
    "Grep", "Glob", "Read",
    "mcp__vexp__run_pipeline",
    "mcp__vexp__get_context_capsule",
    "mcp__vexp__get_session_context",
    "mcp__vexp__get_skeleton",
    "mcp__vexp__index_status",
    "mcp__vexp__search_memory",
}
```

Set extended from 4 to 9 entries. Multi-line format for readability.

---

## (b) New Test Functions

6 new tests added to `tests/test_gates.py`, inserted after the existing `test_permission_denials_vexp_run_pipeline_exempt`:

1. **`test_permission_denials_vexp_get_context_capsule_exempt`** — asserts `mcp__vexp__get_context_capsule` denial is filtered (gate does NOT fire)
2. **`test_permission_denials_vexp_get_session_context_exempt`** — asserts `mcp__vexp__get_session_context` denial is filtered (gate does NOT fire)
3. **`test_permission_denials_vexp_get_skeleton_exempt`** — asserts `mcp__vexp__get_skeleton` denial is filtered (gate does NOT fire)
4. **`test_permission_denials_vexp_index_status_exempt`** — asserts `mcp__vexp__index_status` denial is filtered (gate does NOT fire)
5. **`test_permission_denials_vexp_search_memory_exempt`** — asserts `mcp__vexp__search_memory` denial is filtered (gate does NOT fire)
6. **`test_permission_denials_vexp_save_observation_is_not_exempted`** — critical negative test asserting `mcp__vexp__save_observation` denial DOES fire the gate (write-class tool, denials must not be silenced)

All tests follow the existing pattern from `test_permission_denials_vexp_run_pipeline_exempt`: construct a `parsed` dict via `_clean_parsed()`, set `permission_denials` with the tool name, call `gates.check()`, assert pass/fail and gate presence/absence.

---

## (c) Full-Suite Test Counts

```
collected 412 items
407 passed, 5 failed, 1 warning
```

**5 pre-existing failures (all carry-overs, not regressions):**
- 4 × `test_decisions.py` — worktree artifact (phrase file path resolves to worktree root, not project root)
- 1 × `test_run_step_timeout` — pre-existing runner timeout test issue

**Targeted run (`-k 'vexp or save_observation or read_class'`):** 8 selected, 8 passed.

---

## (d) save_observation Denial Test Confirmation

`test_permission_denials_vexp_save_observation_is_not_exempted` — **PASSED**. The test constructs a denial with `tool_name: "mcp__vexp__save_observation"`, calls `gates.check()`, and asserts:
- `result["passed"] is False`
- `failures` contains an entry with `gate == "no_permission_denials"` and `"1 blocking denial"` in evidence

This confirms `save_observation` is NOT in `READ_CLASS_TOOLS` and its denials correctly fire the gate.

---

## (e) Deviations from SA Section 3 Tool List

None. All 5 tools added match the SA Section 3 classification table exactly:
- `mcp__vexp__get_context_capsule` — read-class
- `mcp__vexp__get_session_context` — read-class
- `mcp__vexp__get_skeleton` — read-class
- `mcp__vexp__index_status` — read-class
- `mcp__vexp__search_memory` — read-class

`mcp__vexp__save_observation` correctly excluded as write-class per SA classification.

---

## (f) Output Receipt

**Agent:** Bellows Developer
**Step:** 1
**Status:** Complete

### What Was Done
Extended `READ_CLASS_TOOLS` in `gates.py` with 5 read-class vexp tools identified by the 2026-05-25 SA diagnostic. Added 6 regression tests (5 positive exemption tests + 1 critical negative test for `save_observation`). All tests pass; full suite shows zero new regressions.

### Files Deposited
- `knowledge/development/mcp-read-class-tools-extension-2026-05-25.md` — this dev log

### Files Created or Modified (Code)
- `gates.py` — extended `READ_CLASS_TOOLS` set from 4 to 9 entries
- `tests/test_gates.py` — added 6 new test functions for vexp tool exemption coverage

### Decisions Made
- Formatted `READ_CLASS_TOOLS` as multi-line set literal for readability (consistent with SA Section 4 Shape A recommendation)
- Placed new tests immediately after the existing `test_permission_denials_vexp_run_pipeline_exempt` for logical grouping

### Flags for CEO
- None

### Flags for Next Step
- Daemon restart required for the new exemptions to take effect in production
- The 5 pre-existing test failures are all carry-overs (4 × worktree artifact, 1 × runner timeout) — QA should classify them as such
