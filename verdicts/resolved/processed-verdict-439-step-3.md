continue

STEP 3 (439, doctrine as opt-in) verdict: CONTINUE to STEP 4 (QA). Planner-verified:
- Bellows gate PASS (dev note deposit present). PLANNER_TEMPLATE.md edited in the governance root (outside the bellows worktree) and committed in-place: root HEAD f3f7607; bellows dev note 2d20976.
- Planner READ the doctrine: on_failure added to BOTH recognized-values lists (PLANNER_TEMPLATE:890, :894); full semantics para (:1040, modeled on qa_and_terminal :1038) incl. qa_steps-FAIL requirement, known_failures, auto-close implication, fail-closed; canary note (:1042).
- FORK-C GUARDRAIL HELD — NO default flipped: sparse default still after_step_1 (bellows.py:654), header template still after_step_1 (:396), plan_lint check 9 unchanged (:1427). on_failure is available opt-in only.
Proceed to STEP 4 — full-suite QA + canary dry-run.
