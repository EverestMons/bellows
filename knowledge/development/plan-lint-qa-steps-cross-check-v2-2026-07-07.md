# plan_lint qa_steps cross-check — Dev Log (Plan 140)
**Date:** 2026-07-07

## Change 1 — Parse Helper

Added `_parse_qa_steps(qa_steps_raw)` at `scripts/plan_lint.py:28`.

### Helper logic (plan_lint)
```python
def _parse_qa_steps(qa_steps_raw):
    """Parse qa_steps header value into a set of ints, mirroring gates._gate_is_qa_step."""
    try:
        if isinstance(qa_steps_raw, list):
            return {int(x) for x in qa_steps_raw}
        s = str(qa_steps_raw).strip().strip("[]")
        return {int(tok.strip()) for tok in s.split(",") if tok.strip()}
    except (ValueError, TypeError):
        return set()
```

### gates._gate_is_qa_step logic (gates.py:724-736)
```python
def _gate_is_qa_step(plan_text, step_number, plan_header=None):
    if plan_header:
        qa_steps_raw = plan_header.get("qa_steps", "")
        if qa_steps_raw:
            try:
                if isinstance(qa_steps_raw, list):
                    return step_number in [int(x) for x in qa_steps_raw]
                qa_step_numbers = [int(s.strip()) for s in str(qa_steps_raw).split(",") if s.strip()]
                return step_number in qa_step_numbers
            except (ValueError, TypeError):
                logger.warning("qa_steps field malformed: %r — falling back to keyword detection", qa_steps_raw)
```

**Match confirmation:** Both handle list-form (`isinstance` check), comma-string (`str().split(",")`), and malformed values (`ValueError`/`TypeError` → skip). The helper additionally strips `[]` brackets because the pipe header parser stores `[2]` as the string `"[2]"` rather than a Python list — this is an adaptation for plan_lint's context where headers always arrive as strings.

## Change 2 — Cross-Check WARN Block

Added at `scripts/plan_lint.py:141-150`, immediately after the test-scope WARN block and before the results print loop:

```python
    # WARN: qa_steps ↔ step-label cross-check
    qa_steps_raw = header.get("qa_steps", "") if header else ""
    if qa_steps_raw:
        qa_steps_set = _parse_qa_steps(qa_steps_raw)
        qa_labeled_steps = {int(sn) for hl, sn in step_headers if "qa" in hl.lower()}
        for n in sorted(qa_labeled_steps - qa_steps_set):
            print(f"WARN: step {n} is QA-labeled but absent from qa_steps={qa_steps_raw!r} — it will not be Rule 20/22 gated")
        for n in sorted(qa_steps_set - qa_labeled_steps):
            print(f"WARN: qa_steps lists step {n} but step {n} is not QA-labeled — it will be gated as QA (plan-133 trap)")
```

### No-dead-branch grep result
```
$ grep -n 'all_passed' scripts/plan_lint.py | grep -c 'WARN\|cross-check'
0
```
The new block contains zero `all_passed` assignments, zero `return` statements, and uses two separate `for` loops with distinct print messages (no `if/else` with identical branches).

## Change 3 — Tests

Six new tests added to `tests/test_plan_lint.py`:

| Test | Rationale |
|---|---|
| `test_lint_qa_steps_cross_check_good` | (a) Good DEV→QA plan (qa_steps: 2, STEP 2 QA) — no false WARN, exit 0 |
| `test_lint_qa_steps_plan133_trap` | (b) Plan-133 shape (qa_steps: 1, STEP 1 DEV / STEP 2 QA) — emits both WARNs, exit 0 |
| `test_lint_qa_steps_qa_labeled_absent` | (c) QA-labeled step absent from qa_steps — "will not be gated" WARN, exit 0 |
| `test_lint_qa_steps_list_form` | (d) List-form `qa_steps: [2]` parses correctly — no false WARN |
| `test_lint_qa_steps_malformed` | (e) Malformed `qa_steps: abc` — no crash, no traceback |
| `test_lint_qa_steps_absent_no_warn` | (f) No qa_steps field — no qa_steps WARN emitted |

All tests assert on exact WARN substrings so a regression to a dead-branch form would be caught.

## Full Suite Tail

```
tests/test_worktree.py::test_auto_stage_handles_multiple_deposits PASSED [ 99%]
tests/test_worktree.py::test_auto_stage_noop_when_all_committed PASSED   [100%]

======================= 755 passed, 1 warning in 28.84s ========================
```

## Commit

`fe1e8cf` — `feat(plan_lint): WARN when qa_steps disagrees with step labels (plan-133 trap guard) [140]`

### Ledger Updates

#### Prompt Feedback

No new prompt feedback to record. The plan instructions were clear and the implementation matched on first pass (two test fixture adjustments for pipe-header string semantics were mechanical, not prompt issues).

---
## Output Receipt
**Agent:** Bellows Developer
**Step:** 1
**Status:** Complete

### What Was Done
Added a WARN-only qa_steps ↔ step-label cross-check to `scripts/plan_lint.py` with a `_parse_qa_steps` helper mirroring `gates._gate_is_qa_step`. Six tests added covering all specified cases. Full suite passes (755/755).

### Files Deposited
- `knowledge/development/plan-lint-qa-steps-cross-check-v2-2026-07-07.md` — this dev log

### Files Created or Modified (Code)
- `scripts/plan_lint.py` — added `_parse_qa_steps` helper and WARN-only cross-check block
- `tests/test_plan_lint.py` — added 6 tests for qa_steps cross-check coverage

### Decisions Made
- Added `strip("[]")` to the parse helper beyond what `gates._gate_is_qa_step` does, because the pipe header parser stores `[2]` as the string `"[2]"` rather than a Python list — necessary adaptation for plan_lint's context

### Flags for CEO
- None

### Flags for Next Step
- None
