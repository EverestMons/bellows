continue

STEP 2 (439, on_failure mode + three-site guard) verdict: CONTINUE to STEP 3. Planner-verified:
- Bellows gates PASS; commit 47c31c9; files bellows.py, plan_lint.py, test_on_failure_mode.py, dev note.
- Planner READ the diff: all THREE is_qa_step sites mode-scoped — non-final :999 and final :1123 use (is_qa_step and pause_for_verdict != on_failure); auto-close :1168 uses (not is_qa_step or == on_failure). header_says_pause :639 returns False for on_failure. effective_auto_close :991-994 = (auto_close==true OR pause_for_verdict==on_failure) — line 993 confirmed part of that assignment, NOT a pause condition. plan_lint :28 adds the token; :427-431 FAILs on_failure without qa_steps.
- Backward compat: every guard is mode-scoped, so always/after_step_1/after_qa_step/qa_and_terminal are untouched.
- Planner INDEPENDENTLY ran tests/test_on_failure_mode.py: 29 passed (raw). And py_compile bellows.py/plan_lint.py/gates.py OK (no restart-brick).
Proceed to STEP 3 (doctrine as OPT-IN — no default flip, Fork C canary).
