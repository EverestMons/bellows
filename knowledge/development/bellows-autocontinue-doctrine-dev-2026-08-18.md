# Step 3 dev note — `on_failure` doctrine as OPT-IN (canary, no default flip)

**Plan:** executable-bellows-autocontinue-2026-08-18
**Step:** 3
**Date:** 2026-08-18

## What shipped

PLANNER_TEMPLATE.md updated to document `on_failure` as an available `pause_for_verdict` mode:

1. **Two recognized-values enumerations updated** (lines ~890 and ~894): added `on_failure` to both lists so the Planner knows it is a valid token.

2. **Semantics paragraph** (modeled on the `qa_and_terminal` doctrine at Rule 49): documents that `on_failure` auto-continues every step (including QA and terminal) when gates pass; pauses only on gate failure; requires `qa_steps` (lint-FAIL otherwise); honors `known_failures`; implies `auto_close`; fail-closed on unparseable pytest output.

3. **Canary note**: instructions for opting in (`pause_for_verdict: on_failure` on a low-stakes plan) and what to measure (gate catch rate, clean auto-continue, notification on close).

## What did NOT change (Fork C — follow-up scope)

- `_apply_defensive_header_defaults` (bellows.py:652) — sparse-header default remains `after_step_1`
- `plan_lint` check 9 (PLANNER_TEMPLATE ~:1423) — diagnostics rule unchanged
- Header-template default (PLANNER_TEMPLATE ~:396) — still shows `after_step_1`
- No code changes — this step is doc-only; Python logic shipped in Steps 1 and 2
