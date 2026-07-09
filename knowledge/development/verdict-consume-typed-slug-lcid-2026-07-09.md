# Dev Log — Fix `_lc_plan_id` derivation for type-prefixed verdict slugs

**Date:** 2026-07-09
**Plan:** 150 (executable-150)
**Agent:** Bellows Developer
**Step:** 1 (DEV)

## Root Cause

When `_consume_verdicts` processes a verdict for a type-prefixed plan (e.g. `qa-149`), the `lookup_slug` normalization (lines 2029-2033) only strips `diagnostic-` and `executable-` prefixes — not `qa-`. So `lookup_slug` stays `qa-149`, and the `int(lookup_slug)` call at line 2089 raises `ValueError`, leaving `_lc_plan_id = None`. This silently skips all three `lifecycle.mark_plan_state` calls (continue-to-done at ~2146, halt at ~2113, stop at ~2175), so lifecycle.db never records the terminal state for any type-prefixed plan.

Bare-integer slugs (e.g. `148` for executable plans) worked only because the `executable-` prefix was stripped before the `int()` call.

## Changes

### bellows.py (~line 2086-2091)

Replaced the `int(lookup_slug)` try/except block with a regex-based parse using `plan_slug` (the full unstripped slug):

```python
_lc_id_match = re.fullmatch(r"(?:(?:diagnostic|executable|qa)-)?(\d+)", plan_slug)
_lc_plan_id = int(_lc_id_match.group(1)) if _lc_id_match else None
```

This extracts the integer id from:
- `qa-149` → 149
- `executable-148` → 148
- `diagnostic-5` → 5
- bare `148` → 148
- Legacy slug+date names (e.g. `executable-foo-bar-2026-05-28`) → `None`

Matches the regex shape used by `recover_plan_id_from_filename` (line 364-379). All three terminal branches (continue-to-done, halt, stop) already reference `_lc_plan_id` — no changes needed downstream.

### qa-149 one-off repair

lifecycle.db plan 149 was repaired:
- **BEFORE:** `lifecycle_state='abandoned'`, `plan_doc_ref='knowledge/decisions/in-progress-qa-149.md'`
- **AFTER:** `lifecycle_state='closed'`, `closed_at='2026-07-09T10:12:20.573752'`, `plan_doc_ref='bellows/knowledge/decisions/Done/qa-149.md'`

Repair was idempotent (checked current state first, only updated because state was not already `closed`).

### tests/test_consume_verdicts.py

Added three tests:
1. **`test_plan_id_derivation_from_slug`** — unit test for the regex extraction: `qa-149`→149, `executable-148`→148, `148`→148, legacy→None.
2. **`test_consume_verdict_continue_to_done_calls_mark_plan_state_for_qa_plan`** — integration test: a continue-to-done verdict for `qa-149` calls `mark_plan_state(149, "closed", ...)`.
3. **`test_consume_verdict_stop_calls_mark_plan_state_for_qa_plan`** — integration test: a stop verdict for `qa-200` calls `mark_plan_state(200, "halted", ...)`.

## Full Suite Result

```
791 passed, 1 warning in 19.47s
```

0 failures, 0 regressions.

### Ledger Updates

#### Prompt Feedback

- The `lookup_slug` normalization list (stripping `diagnostic-`, `executable-` but not `qa-`) is a naming inconsistency that should be documented or unified in a follow-up — not a bug per se, since the verdict-request filename uses the unstripped slug for `qa-` plans, but it creates a trap for any code that assumes `lookup_slug` is always a bare slug.

---

## Output Receipt
**Agent:** Bellows Developer
**Step:** 1
**Status:** Complete

### What Was Done
Fixed `_lc_plan_id` derivation in `_consume_verdicts` to handle type-prefixed verdict slugs (e.g. `qa-149`) using a regex parse instead of bare `int()`. Repaired qa-149 lifecycle row from `abandoned` to `closed`. Added unit and integration tests covering the fix.

### Files Deposited
- `knowledge/development/verdict-consume-typed-slug-lcid-2026-07-09.md` — this dev log

### Files Created or Modified (Code)
- `bellows.py` — replaced `int(lookup_slug)` block with `re.fullmatch` parse using `plan_slug`
- `tests/test_consume_verdicts.py` — added 3 tests for id derivation and lifecycle writes on qa-type plans

### Decisions Made
- Used `plan_slug` (full unstripped slug) as the regex input rather than `lookup_slug`, since `plan_slug` consistently carries the type prefix regardless of plan type

### Flags for CEO
- None

### Flags for Next Step
- The `lookup_slug` normalization not stripping `qa-` is an inconsistency worth noting but not in scope for this fix
