verdict: continue

Planner verdict on executable-396 step 2 (foreground full-suite QA) -> continue (TERMINAL — closes 396 to Done). The stub-reframe pending-buffer feature is QA-verified and ships.

MECHANICAL GATE: all PASS — deposit_exists PASS (qa report + evidence present this time), rule_20_self_check PASS (banner byte-exact), scope_check PASS.

SUBSTANCE (Planner-verified from RAW evidence, not the agent summary):
- knowledge/qa/evidence/stub-reframe-buffer-qafix-2026-08-13/full-suite.txt tail: "2 failed, 2625 passed, 1 warning in 929.81s".
- The 2 failures are EXACTLY the CLAUDE.md-known pre-existing ones (test_activity_import.py::TestFlaskRoute::test_get_activity_import_page, test_fix_links.py::TestGate7LinehaulFixLink::test_no_tariff_rate_has_fix_url) — verified by grepping ^FAILED in the raw file.
- 2625 passed vs 2622 in the Planner's pre-fix run = the 3 version-assertion tests are now green. ZERO regressions from the reframe (steps 1-4 of 394 + the 396 fix).
- QA ran FOREGROUND this time (929s inline) and deposited evidence-first — the 394 backgrounding trap did not recur.

RECORD: this closes the stub-reframe arc's build. halted-executable-394 carries the committed DEV (steps 1-4); executable-396 completes its QA. Remaining (separate, CEO-facing): the work-machine buffer->auto-apply live test, and F4 existing-stub migration (diagnostic-390 Q6).

Clean. Close 396.
