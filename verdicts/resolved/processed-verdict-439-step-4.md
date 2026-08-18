continue

STEP 4 (439, QA — final) verdict: CONTINUE -> continue-to-done. Planner-verified:
- Bellows gates PASS: rule_20_self_check (banner byte-exact, PASSED), rule_22 (deposits present, verification table clean, no hedging).
- Planner INDEPENDENTLY ran the full bellows suite: 1098 passed, 0 failed, 0 error (raw, matches evidence full-suite.txt). No regression from the pause-logic + gate changes.
- Canary dry-run proves the mechanism end-to-end: clean QA under on_failure auto-continues to Done (three-site no-pause + auto-close); injected regression PAUSES (test_site1/2_on_failure_failed_qa_pauses); all four existing modes (always/after_step_1/after_qa_step/qa_and_terminal) unchanged (backward compat Q7).
Mechanism SHIPPED as opt-in (canary). No default flipped. Close to Done. Follow-ups: run the canary on a live low-stakes plan, then a plan to flip the default (Fork C); the .bellows-baseline node-id file (Fork A).
