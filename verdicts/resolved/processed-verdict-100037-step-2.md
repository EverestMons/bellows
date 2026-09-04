continue

CONTINUE — step 2 QA verified independently; scope_check overridden with a committed reference; closing a 2-step plan.

BOTH FAIL-OPEN PATHS ARE NOW CLOSED, re-run here rather than read off the receipt:
  FO-1: _manifest_validation_keys(halted-executable-100031) was None (SKIPPED) and is now frozenset() — it REFUSES. That is the plan whose dispatch past a class hold motivated the gate that missed it.
  FO-3: _parse_qa_steps('none') -> set(), and the PLANNER_TEMPLATE placeholder '[comma-separated step numbers]' -> set(). Neither demands a Rule 20 banner any longer.

EVIDENCE, verified not quoted:
  - full suite from the dispatch worktree: 1870 passed, 1 skipped, 0 FAILED
  - mutation_check on knowledge/mutants/close-failopen-defaults.json: 6 killed / 0 survived / 0 error, including the placeholder mutant added late at walk 4
  - rule_20_self_check PASS (banner byte-exact), rule_22_verification PASS, deposit_exists PASS
  - the pre-declared benign qa_test_result failure did NOT fire: the QA deposited a real parseable pytest summary, so the gate could certify it. The pre-declaration was unnecessary and harmless.

THE ONE GATE FAILURE was scope_check, identical in class to step 1's and verified the same way: out-of-scope files tests/test_depositor_receipts.py and tests/test_wrap_receipts.py. Zero assertion lines changed; diffs are pure additions (+2/-0, +1/-0); test counts unchanged 23->23 and 26->26. Overridden per the CEO's step-1 ruling on the identical class, with a COMMITTED reference at knowledge/overrides/override-100037-step2-scope_check.md written before the override rather than after (thread 123's lesson).

⚠️ WHAT THIS COST TELLS US, and it is the finding worth carrying: FO-1's real blast radius is EVERY plan-fixture construction site in the test suite, not just cycle_check's own tests. Step 1 revealed it reaches cycle_check's tests; step 2 revealed it reaches the depositor and wrap suites. SEVEN WALKS identified neither. The plan's P5 argued the blast radius was a past-corpus artifact because cycle_check never scans Done/ — true, and it answered the wrong question: the exposure was never the closed corpus, it was the live fixtures.

⚠️ AND A PLAN DEFECT THE EXECUTING AGENT CAUGHT: knowledge/mutants/close-failopen-defaults.json lacked the top-level 'target' field mutation_check reads first. Item 5 specified per-mutant targets only. Seven walks missed it; the agent found it while making the kill map runnable.

Closing.
