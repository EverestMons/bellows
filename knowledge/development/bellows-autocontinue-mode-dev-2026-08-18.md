# Auto-continue `on_failure` pause mode — Dev Note

**Plan:** 439, Step 2
**Date:** 2026-08-18

## Changes

### bellows.py
- `header_says_pause` (:627): added `if pv == "on_failure": return False` — clean steps never pause from header alone under this mode.
- `effective_auto_close` (:989): `on_failure` implies `effective_auto_close` — one header controls both behaviors.
- Three-site `is_qa_step` guard: guarded the unconditional `is_qa_step` pause trigger with `and header.get("pause_for_verdict") != "on_failure"` at all three sites (:993-996 non-final, :1117-1121 final, :1162-1166 auto-close exclusion relaxed to `or pause_for_verdict == "on_failure"`).

### scripts/plan_lint.py
- Added `on_failure` to `RECOGNIZED_PAUSE_TOKENS` (:28).
- Added FAIL branch (:427) for `on_failure` without parseable `qa_steps` — a mis-declared QA step under `on_failure` would auto-ship unchecked (Q8 safety).

### tests/test_on_failure_mode.py
- `header_says_pause` returns False for `on_failure` (all step types).
- Three-site guard: clean QA under `on_failure` auto-continues; failed QA still pauses.
- `effective_auto_close` true under `on_failure`.
- `plan_lint` FAILs `on_failure` without `qa_steps`.
- Q7 backward-compat: existing modes (`always`, `after_step_1`, `after_qa_step`, `qa_and_terminal`) unchanged.

## Safety
F8 three-legged invariant: the `is_qa_step` drop (this step) lands AFTER the QA-result gate (step 1), so no intermediate HEAD has the drop without the gate. The `plan_lint` FAIL branch ensures mis-declared QA can't slip through at authoring time.
