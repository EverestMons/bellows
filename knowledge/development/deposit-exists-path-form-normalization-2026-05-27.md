# deposit_exists Path-Form Normalization — Dev Log

**Date:** 2026-05-27 | **Plan:** executable-deposit-exists-path-form-normalization-2026-05-27 | **Step:** 1

---

## Implementation Summary

Implemented two components to fix the abs-vs-rel path-form mismatch in `_gate_deposit_exists` that caused three Planner overrides on 2026-05-23 (RC3, per diagnostic `deposit-exists-path-form-normalization-2026-05-27.md`).

### Component A — `_normalize_deposit_path` helper + membership-check normalization

Added `_normalize_deposit_path(path, project_path)` at `gates.py:216-236`. The function reduces any of four input forms to canonical project-relative form:
- Absolute under `project_path` → strips `project_path + os.sep` prefix
- Absolute under `dirname(project_path)` → strips parent prefix
- Project-prefixed relative (e.g. `bellows/foo.md`) → strips basename prefix
- Already project-relative → returns unchanged

Updated three call sites in `_gate_deposit_exists`:
- **Line 295** (`agent_declared.add`): now normalizes before adding to the set
- **Line 303** (frontmatter check): normalizes plan-required path before membership check
- **Line 310** (prose-block check): normalizes plan-required path before membership check

Both the normalized membership check AND the `_resolve_deposit_path` fallback are preserved — the gate passes if either succeeds.

### Component B — Strategy 0 absolute-path remap in `_resolve_deposit_path`

Added an `os.path.isabs(path)` branch at `gates.py:254-261` inside Strategy 0. When the path is absolute and starts with `project_path + os.sep`, it strips the prefix to get a project-relative remainder and joins with `wt_path`. This fixes the issue where `os.path.join(wt_path, absolute_path)` returned `absolute_path` unchanged (Python `os.path.join` semantics), silently bypassing worktree-first resolution.

---

## Lines Changed

### `gates.py` — before/after

**New function** (`_normalize_deposit_path`, lines 216-236):
```python
def _normalize_deposit_path(path, project_path):
    """Normalize deposit path to canonical project-relative form for comparison."""
    abs_project = os.path.abspath(project_path)
    if os.path.isabs(path):
        prefix = abs_project + os.sep
        if path.startswith(prefix):
            return path[len(prefix):]
        parent_prefix = os.path.dirname(abs_project) + os.sep
        if path.startswith(parent_prefix):
            return path[len(parent_prefix):]
    project_basename = os.path.basename(abs_project)
    if path.startswith(project_basename + os.sep):
        return path[len(project_basename) + 1:]
    return path
```

**`_gate_deposit_exists` line 295** (was `agent_declared.add(path)`):
```python
# Before:
agent_declared.add(path)
# After:
agent_declared.add(_normalize_deposit_path(path, project_path))
```

**`_gate_deposit_exists` line 303** (frontmatter membership check):
```python
# Before:
if path not in agent_declared and _resolve_deposit_path(...) is None:
# After:
if _normalize_deposit_path(path, project_path) not in agent_declared and _resolve_deposit_path(...) is None:
```

**`_gate_deposit_exists` line 310** (prose-block membership check):
```python
# Before:
if path not in agent_declared and _resolve_deposit_path(...) is None:
# After:
if _normalize_deposit_path(path, project_path) not in agent_declared and _resolve_deposit_path(...) is None:
```

**`_resolve_deposit_path` Strategy 0** (lines 254-261):
```python
# Before:
wt_candidate = os.path.join(wt_path, path)
# After:
if os.path.isabs(path):
    prefix = abs_project + os.sep
    if path.startswith(prefix):
        wt_candidate = os.path.join(wt_path, path[len(prefix):])
    else:
        wt_candidate = os.path.join(wt_path, path)
```

---

## Test Count Delta

- **Before:** 93 tests in `test_gates.py`, 366 total
- **After:** 99 tests in `test_gates.py`, 372 total
- **Delta:** +6

### New tests added to `test_gates.py`

| Test | Type | Description |
|------|------|-------------|
| `test_normalize_deposit_path_abs_to_rel` | Positive | Absolute path under project_path → bare project-relative |
| `test_normalize_deposit_path_prefixed_to_rel` | Positive | Project-prefixed relative → project-relative |
| `test_normalize_deposit_path_already_rel` | Positive | Already project-relative → unchanged |
| `test_gate_deposit_exists_cross_form_abs_vs_rel` | Positive | Plan declares absolute, agent declares relative, file exists — gate passes (regression test for 2026-05-23) |
| `test_gate_deposit_exists_actually_missing` | Negative | File genuinely missing — gate still fails |
| `test_resolve_deposit_path_absolute_worktree_remap` | Positive | Absolute path remapped to worktree finds file via Strategy 0 |

---

## Pytest Output — Targeted (`tests/test_gates.py`)

```
99 passed, 1 warning in 0.17s
```

All 99 tests pass (93 pre-existing + 6 new). Zero regressions.

## Pytest Output — Full Suite (`tests/`)

```
5 failed, 367 passed, 1 warning in 6.24s
```

372 total tests. 5 failures are all pre-existing:
- `test_decisions.py::TestLoadPhrases::test_loads_phrases_from_file`
- `test_decisions.py::TestLoadPhrases::test_includes_known_phrases`
- `test_decisions.py::TestLoadPhrases::test_splits_slash_alternatives`
- `test_decisions.py::TestExtractDecisionBlocks::test_s_class_blocks_from_ground_truth`
- `test_runner_parser.py::test_run_step_timeout`

These are documented in prior QA reports (disable-autoupdater QA). Zero NEW failures.

---

## Known Issues

None. The fix is additive (new function + call-site normalization + Strategy 0 branch). No behavioral change for paths that were already matching correctly.

---

## Output Receipt
**Agent:** Bellows Developer
**Step:** 1
**Status:** Complete

### What Was Done
Implemented both components of the deposit_exists path-form normalization fix: (A) added `_normalize_deposit_path` helper and normalized all three membership-check call sites in `_gate_deposit_exists`, and (B) added absolute-path-to-worktree remap in `_resolve_deposit_path` Strategy 0. Added 6 unit tests covering positive, negative, and regression scenarios. All tests pass with zero regressions.

### Files Deposited
- `bellows/knowledge/development/deposit-exists-path-form-normalization-2026-05-27.md` — this dev log

### Files Created or Modified (Code)
- `bellows/gates.py` — added `_normalize_deposit_path` function (lines 216-236), updated 3 call sites in `_gate_deposit_exists` (lines 295, 303, 310), added absolute-path remap in `_resolve_deposit_path` Strategy 0 (lines 254-261)
- `bellows/tests/test_gates.py` — added 6 new tests for normalization and abs-vs-rel regression coverage

### Decisions Made
- Adapted diagnostic Q5 reference implementation directly — behavior matches specification exactly
- Preserved both normalized membership check AND `_resolve_deposit_path` fallback at all call sites per plan specification

### Flags for CEO
- None

### Flags for Next Step
- QA should verify the cross-form regression test (`test_gate_deposit_exists_cross_form_abs_vs_rel`) matches the 2026-05-23 reproduction shape
- Daemon restart required for the new gate code to take effect in production
