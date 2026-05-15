# Dev Log: deposit_exists Worktree-Aware Path Resolution Fix

**Date:** 2026-05-06
**Plan:** executable-deposit-exists-worktree-aware-2026-05-06
**Agent:** Bellows Developer
**Step:** 1

---

## Tests-Before / Tests-After

| Metric | Before | After |
|---|---|---|
| Collected | 212 | 212 |
| Passed | 211 | 211 |
| Failed | 1 (pre-existing: test_run_step_timeout) | 1 (same pre-existing) |
| Regressions | — | 0 |

---

## Diff Summary

### `gates.py` — 3 functions modified (+13 LOC net)

1. **`_resolve_deposit_path`** (line 128): Added `wt_path=None` parameter. Inserted Strategy 0 block (worktree-first resolution) before existing strategies S1/S2/S3. Strategy 0 handles both Form A (governance-root-relative with project basename prefix) and Form B (project-relative) paths. Guard `if wt_path is not None and wt_path != project_path` prevents double-checking on bellows-self plans.

2. **`_gate_deposit_exists`** (line 157): Added `wt_path=None` parameter. Both `_resolve_deposit_path` calls (agent-declared at line 173, plan-required at line 181) now pass `wt_path=wt_path`.

3. **`check()`** (line 36): Added `wt_path=None` parameter after `files_changed`. Forwarded to `_gate_deposit_exists` call at line 72.

### `bellows.py` — 2 call sites modified (+2 LOC changed)

1. **Line 331**: `gates.check(...)` call now passes `wt_path=wt_path`.
2. **Line 416**: `gates.check(...)` call (inside while-loop) now passes `wt_path=wt_path`.

---

## Bellows-Self Plan Compatibility Verification

For bellows-self plans, `_create_worktree()` returns `project_path` unchanged (no `.git` directory detected). Therefore `wt_path == project_path` at both call sites. The Strategy 0 guard evaluates:

```python
if wt_path is not None and wt_path != project_path:  # False — wt_path == project_path
```

This evaluates to `False`, so Strategy 0 is skipped entirely. Existing strategies S1/S2/S3 handle bellows-self plans as before. No behavioral change for bellows-self plans.

---

## What Was NOT Modified

- `scope_check`, `rule_20_self_check`, and all other gate functions — unchanged per plan instructions.
- `_teardown_worktree` ordering — unchanged; teardown still runs after gate evaluation.
- Existing resolution strategies S1/S2/S3 — preserved; Strategy 0 is inserted ahead of them.
- No other Bellows modules modified (`verdict.py`, `parser.py`, `runner.py`, etc.).

---

## Rule 20 Self-Check

```
SELF-CHECK PASSED
Dev log: knowledge/development/deposit-exists-worktree-aware-2026-05-06.md
Modified files: gates.py, bellows.py
Plan in-progress: knowledge/decisions/in-progress-executable-deposit-exists-worktree-aware-2026-05-06.md
```

---

## Output Receipt
**Agent:** Bellows Developer
**Step:** 1
**Status:** Complete

### What Was Done
Threaded `wt_path` through the gate evaluation path (`gates.check()` → `_gate_deposit_exists` → `_resolve_deposit_path`) so that newly-created deposits in worktree-isolated plans are found via Strategy 0 (worktree-first resolution). Updated both `gates.check()` call sites in `bellows.py` to pass `wt_path=wt_path`.

### Files Deposited
- `bellows/knowledge/development/deposit-exists-worktree-aware-2026-05-06.md` — this dev log

### Files Created or Modified (Code)
- `bellows/gates.py` — added `wt_path` parameter to `_resolve_deposit_path`, `_gate_deposit_exists`, and `check()`; added Strategy 0 worktree-first resolution
- `bellows/bellows.py` — updated both `gates.check()` call sites to pass `wt_path=wt_path`

### Decisions Made
- Inserted Strategy 0 as the first resolution attempt, before S1/S2/S3, per plan's CEO-locked worktree-first ordering decision
- Used `os.path.basename(project_path)` for Form A prefix-stripping rather than hardcoding any project name

### Flags for CEO
- None

### Flags for Next Step
- None
