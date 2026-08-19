verdict: continue

Terminal QA step of the cycle-21 corrective. Certifying the close on directly-read raw evidence, not agent summary.

Ten of eleven gate rows PASS, including the substantive ones: rule_20_self_check (banner byte-exact, PASSED line present), rule_22_verification (deposits present, verification table clean, no hedging), deposit_exists (all declared deposits on disk), scope_check, and receipt_status Complete.

The sole failure — qa_test_result "no .txt evidence deposit found" — is a false negative in the gate's evidence-locator, not an uncertified or failing test run. gates.py:743 filters the agent's declared deposit paths for one ending in ".txt"; this plan declared the QA evidence as a directory (knowledge/qa/evidence/executable-anvil-cycle-21-qa-2026-08-18/) rather than naming pytest_full.txt explicitly, so the locator found no .txt path. The file is present and I read it directly: "262 passed in 3.11s" — full suite green, zero failures/errors, above the ≥219 baseline (suite grew to 262).

Planner (b) substance check, verified against ground truth: cycle_21_row.txt = (21, 295, 5166, 3283, 2026-08-19T01:43:01Z), matching the anvil.db cycle_reports row; the audit-findings deposit is present at the canonical invoice-pulse path (audit-findings-2026-08-19.md); the Untested Complexity section is present; the phantom flag is confirmed (phantom_dispute_brief.txt shows 0 matches for `def dispute_brief` in app.py — the deleted function is genuinely absent from source, so the Planner correctly excludes it at triage). files_scanned=295 is the accurate invoice-pulse source-file count, not a regression. Cycle 21 QA is clean → move to Done.

Follow-up (non-blocking, captured for future cycle-QA plans): the qa_test_result gate requires the pytest .txt evidence file to be named explicitly in Deposits / the Output Receipt, not just its containing directory.
