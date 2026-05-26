# Bellows Hardening Batch — Items 1, 3, 4 — Dev Log
**Date:** 2026-05-26 | **Agent:** Bellows Developer | **Step:** 1 (DEV) | **Plan:** executable-bellows-hardening-batch-items-1-3-4-2026-05-26

---

## Pre-Edit Verification (Rule 39)

### Verification 1 — Item 1 evidence strings
**Claim:** `gates.py:441` and `gates.py:464` emit byte-identical evidence strings.
**Query:** `grep -n 'no QA deposit contains Rule 20 self-check banner' gates.py`
**Result:** Two hits at lines 441 and 464, both identical. ✅ Confirmed.

### Verification 2 — Item 3 `_seen` and `on_modified`
**Claim:** `_seen` initialized at `bellows.py:1047`; `on_modified` at `bellows.py:1032-1034` calls `_handle` without invalidating `_seen`.
**Query:** `grep -n 'self._seen' bellows.py` and `grep -n 'on_modified' bellows.py`
**Result:** `self._seen = set()` at line 1047; `on_modified` at 1032-1034 calling `self._handle(event.src_path)`; `_seen.add` at lines 1002 and 1024. No invalidation in `on_modified`. ✅ Confirmed.

### Verification 3 — Item 4 header reassignment
**Claim:** `header` is reassigned at `bellows.py:498` from `gate_result.get("plan_header", {})`.
**Query:** `grep -n 'header = gate_result.get' bellows.py`
**Result:** Exactly 1 hit at line 498. `total_steps` confirmed in scope (set at line 367, same `run_plan()` function). ✅ Confirmed.

---

## Change 1 — Item 1: Evidence String Disambiguation (`gates.py`)

### Before (gates.py:441)
```python
    if not md_paths:
        failures.append({"gate": "rule_20_self_check", "evidence": "no QA deposit contains Rule 20 self-check banner"})
        return
```

### After (gates.py:441)
```python
    if not md_paths:
        failures.append({"gate": "rule_20_self_check", "evidence": "deposits block declares no .md paths (check **Deposits:** block format — must be multi-line bullets)"})
        return
```

Line 464 (banner-not-in-content branch) left unchanged. The two branches now produce distinct evidence strings: Planner-authoring failures (no `.md` paths) route differently from QA-agent discipline failures (banner absent).

---

## Change 2 — Item 3: `_seen` Invalidation on `on_modified` (`bellows.py`)

### Before (bellows.py:1032-1034)
```python
    def on_modified(self, event):
        if not event.is_directory:
            self._handle(event.src_path)
```

### After (bellows.py:1033-1044)
```python
    def on_modified(self, event):
        if not event.is_directory:
            path = event.src_path
            filename = os.path.basename(path)
            # Invalidate _seen on corrected re-deposit so the plan can be re-dispatched.
            # Guard: don't invalidate on Bellows-managed lifecycle renames (would loop).
            LIFECYCLE_PREFIXES = ("in-progress-", "verdict-pending-", "halted-")
            if not any(filename.startswith(p) for p in LIFECYCLE_PREFIXES):
                slug = verdict.slug_from_path(path)
                if slug in self.orchestrator._seen:
                    self.orchestrator._seen.discard(slug)
            self._handle(path)
```

The lifecycle-prefix guard (`in-progress-`, `verdict-pending-`, `halted-`) prevents re-dispatch loops when Bellows renames plans during its own lifecycle transitions. The invalidation fires only for non-lifecycle files whose slug is already in `_seen`.

---

## Change 3 — Item 4: Defensive Default Re-Parse Propagation (`bellows.py`)

### Before (bellows.py:498-499)
```python
        header = gate_result.get("plan_header", {})
        effective_auto_close = str(header.get("auto_close", "false")).lower() == "true"
```

### After (bellows.py:498-500)
```python
        header = gate_result.get("plan_header", {})
        _apply_defensive_header_defaults(header, total_steps)
        effective_auto_close = str(header.get("auto_close", "false")).lower() == "true"
```

Mirrors the pre-gate call at line 382. The re-parsed header now inherits the defensive default before being passed to `header_says_pause()` at lines ~507 and ~597.

### Existing test update
`test_run_plan_continuation_prompt_uses_shadow_path` was relying on the bug (sparse re-parsed header not getting the defensive default, allowing auto-advance). Updated its gate mock to return a non-sparse `plan_header` (3 keys including `pause_for_verdict: "never"`) so the test continues testing its actual purpose (shadow path usage) without interference from the defensive default.

---

## Regression Tests

### Test 1 — `test_rule_20_self_check_distinguishes_no_md_paths_from_missing_banner` (test_gates.py)
- Branch A: patches `_extract_plan_required_deposits` to return `["knowledge/qa/evidence/"]` (no `.md`), asserts evidence contains `"deposits block declares no .md paths"`
- Branch B: creates QA report without banner, patches deposits to `["knowledge/qa/qa-report.md"]`, asserts evidence contains `"no QA deposit contains Rule 20 self-check banner"`
- Final assertion: the two evidence strings are not equal

### Test 2 — `test_on_modified_invalidates_seen_for_runnable_plan` (test_bellows.py)
- Adds slug to `_seen`, fires `on_modified` against non-lifecycle file
- Asserts slug removed from `_seen` and `_handle` called

### Test 3 — `test_on_modified_preserves_seen_for_lifecycle_renames` (test_bellows.py)
- Iterates all three lifecycle prefixes (`in-progress-`, `verdict-pending-`, `halted-`)
- Adds slug to `_seen`, fires `on_modified` against lifecycle-prefixed file
- Asserts slug remains in `_seen` and `_handle` still called

### Test 4 — `test_apply_defensive_header_defaults_propagates_to_reparsed_header` (test_bellows.py)
- Creates 2-step plan, mocks `gates.check` to return sparse `plan_header: {"project": "bellows"}`
- Spies on `header_says_pause` to capture the header dict
- Asserts the captured header contains `pause_for_verdict: "after_step_1"` (the defensive default)

---

## Test Suite Results

```
=================== 5 failed, 411 passed, 1 warning in 6.67s ===================
```

- **411 passed** (407 baseline + 3 new regression tests + 1 existing test fixed)
- **5 failed** (all known carry-overs):
  - 4 × `test_decisions.py` — worktree-context `INTERMEDIATE_DECISION_PHRASES.md` not found
  - 1 × `test_runner_parser.py::test_run_step_timeout` — long-standing assertion mismatch
- **Zero regressions** — no new failures beyond the known carry-overs

---

## Anchor Verification Results

| # | Grep | Expected | Actual | Status |
|---|------|----------|--------|--------|
| 1 | `grep -n 'deposits block declares no .md paths' gates.py` | 1 hit at ~441 | 1 hit at line 441 | ✅ |
| 2 | `grep -n 'no QA deposit contains Rule 20 self-check banner' gates.py` | 1 hit at ~464 | 1 hit at line 464 | ✅ |
| 3 | `grep -n '_seen.discard' bellows.py` | ≥1 new hit in on_modified | New hit at line 1043 (`self.orchestrator._seen.discard(slug)`) + 3 pre-existing | ✅ |
| 4 | `grep -n '_apply_defensive_header_defaults' bellows.py` | 3 hits (def + 2 calls) | 3 hits: line 318 (def), 382 (call 1), 499 (call 2) | ✅ |

---

## Output Receipt
**Agent:** Bellows Developer
**Step:** 1
**Status:** Complete

### What Was Done
Implemented three independent hardening fixes for BACKLOG items 1, 3, and 4: disambiguated the `_gate_rule_20_self_check` evidence string (Item 1), added `_seen` invalidation with lifecycle-prefix guard to `on_modified` (Item 3), and propagated `_apply_defensive_header_defaults` to the re-parsed header after `gates.check()` (Item 4). Added 4 regression tests (3 new + 1 existing test fix).

### Files Deposited
- `bellows/knowledge/development/bellows-hardening-batch-items-1-3-4-2026-05-26.md` — this dev log

### Files Created or Modified (Code)
- `bellows/gates.py` — Item 1: disambiguated evidence string at line 441 for the no-md-paths branch
- `bellows/bellows.py` — Item 3: added `_seen` invalidation with lifecycle-prefix guard in `on_modified` (lines 1033-1044); Item 4: added `_apply_defensive_header_defaults(header, total_steps)` after header reassignment at line 499
- `bellows/tests/test_gates.py` — added `test_rule_20_self_check_distinguishes_no_md_paths_from_missing_banner`
- `bellows/tests/test_bellows.py` — added `test_on_modified_invalidates_seen_for_runnable_plan`, `test_on_modified_preserves_seen_for_lifecycle_renames`, `test_apply_defensive_header_defaults_propagates_to_reparsed_header`; updated `test_run_plan_continuation_prompt_uses_shadow_path` to use non-sparse gate mock

### Decisions Made
- Used `self.orchestrator._seen.discard(slug)` in `on_modified` (not `self._seen`) because `PlanHandler` accesses `_seen` through the orchestrator reference, consistent with all other `_seen` access patterns in the handler class
- Updated `test_run_plan_continuation_prompt_uses_shadow_path` to use a non-sparse `plan_header` (3 keys) to avoid defensive-default interference — the test's purpose is shadow-path verification, not pause behavior

### Flags for CEO
- None

### Flags for Next Step
- The `test_run_plan_continuation_prompt_uses_shadow_path` update is a consequence of Item 4's fix: the test was previously succeeding because the defensive default didn't propagate to the re-parsed header. QA should verify this is a correct behavioral change, not a regression.
