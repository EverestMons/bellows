# Fix F isinstance Guard Removal — Dev Log

**Date:** 2026-05-26 | **Agent:** Bellows Developer
**Plan:** executable-fix-f-guard-removal-2026-05-26
**Step:** 1 (DEV)

---

## Pre-flight Scope Check

`grep -rn 'gate_result\[.failures.\]' tests/` results:
- `tests/test_consume_verdicts.py` — 6 matches (lines 573, 574, 632, 633, 686, 687) — all use dict format
- `tests/test_verdict.py` — 2 matches (lines 206, 680) — dict format
- `tests/test_bellows.py` — the non-conformant fixture at `test_run_plan_inprogress_entry_renames_to_verdict_pending` (line 1789) was the only string-list format

---

## Changes

### Change 1 — Test Fixture Update (`tests/test_bellows.py`)

**Function:** `test_run_plan_inprogress_entry_renames_to_verdict_pending`

**Before (line 1789):**
```python
            "failures": ["scope_check"],
```

**After:**
```python
            "failures": [{"gate": "scope_check", "evidence": "test fixture for scope_check failure"}],
```

The test only asserts that `verdict-pending-*` file exists and `verdict-pending-in-progress-*` does not — no assertions reference failure content, so the evidence string is a descriptive placeholder.

### Change 2 — Remove Fix F isinstance Guard at bellows.py:495

**Before:**
```python
        failure_gates = ", ".join((f["gate"] if isinstance(f, dict) else str(f)) for f in gate_result["failures"]) if gate_result["failures"] else "none"
```

**After:**
```python
        failure_gates = ", ".join(f["gate"] for f in gate_result["failures"]) if gate_result["failures"] else "none"
```

### Change 3 — Remove Fix F isinstance Guard at bellows.py:587

**Before:**
```python
            failure_gates = ", ".join((f["gate"] if isinstance(f, dict) else str(f)) for f in gate_result["failures"]) if gate_result["failures"] else "none"
```

**After:**
```python
            failure_gates = ", ".join(f["gate"] for f in gate_result["failures"]) if gate_result["failures"] else "none"
```

---

## 2026-05-21 isinstance Symmetry Pattern — Preserved

The Block 1 / Block 2 symmetric `isinstance` pattern (added 2026-05-21 for pause-reason discrimination) remains intact at:
- `bellows.py:509`: `if all(isinstance(f, dict) and f.get("gate") == "rule_22_verification" for f in gate_result["failures"]):`
- `bellows.py:600`: `if all(isinstance(f, dict) and f.get("gate") == "rule_22_verification" for f in gate_result["failures"]):`

These are structurally distinct from the Fix F guards — they're in the `all()` predicate classifying pause reasons, not in the `.join()` log expression. Only the Fix F guards (added 2026-05-26) were removed.

---

## Anchor Verification

Post-edit grep for `isinstance(f, dict)` in `bellows.py`:
- Line 509: Block 1 symmetric pattern (2026-05-21) — **kept**
- Line 600: Block 2 symmetric pattern (2026-05-21) — **kept**
- Fix F sites at former lines 495, 587: **removed** — zero matches

---

## Test Results

**Pre-edit:** 5 failed, 407 passed, 1 warning
**Post-edit:** 5 failed, 407 passed, 1 warning
**Delta:** 0 regressions, 0 new failures

The 5 pre-existing failures are:
- 4x `test_decisions.py` (worktree-context phrase file missing)
- 1x `test_run_step_timeout` (long-standing)

---

## Output Receipt

**Agent:** Bellows Developer
**Step:** 1
**Status:** Complete

### What Was Done

Updated the non-conformant test fixture in `test_run_plan_inprogress_entry_renames_to_verdict_pending` from string-list to production dict shape, then removed the Fix F `isinstance(f, dict)` defensive guards at both log-expansion sites in `bellows.py` (lines 495 and 587). Full test suite confirms zero regressions.

### Files Deposited

- `knowledge/development/fix-f-guard-removal-2026-05-26.md` — this dev log

### Files Created or Modified (Code)

- `bellows.py` — removed `isinstance(f, dict)` guard from Fix F log expansion at lines 495 and 587
- `tests/test_bellows.py` — updated `test_run_plan_inprogress_entry_renames_to_verdict_pending` fixture from `["scope_check"]` to `[{"gate": "scope_check", "evidence": "..."}]`

### Decisions Made

- Used descriptive placeholder `"test fixture for scope_check failure"` as evidence string since test only asserts file existence, not failure content

### Flags for CEO

- None

### Flags for Next Step

- QA should verify that the two Block 1 / Block 2 symmetric `isinstance` sites (lines 509 and 600) are preserved and distinct from the removed Fix F sites
- QA should confirm no other test fixture uses the non-conformant string-list format
