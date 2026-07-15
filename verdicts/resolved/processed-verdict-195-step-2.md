verdict: continue
Step 2 (QA) verified — one benign scope_check failure, continue-with-reasoning under delegated authority. Final step (2 of 2) -> move plan 195 to Done/.
scope_check flagged two out-of-scope files, both defensible:
- knowledge/research/agent-prompt-feedback.md — benign old-style feedback write (recurring class; a code-scope non-issue).
- tests/test_validation_results.py — a LEGITIMATE QA fix of a real regression the behavior change caused: INV-004 fixture had only a hidden gate (gate_1_legitimacy); with validation now skipped for fresh invoices, no visible gate rendered so assert b"Pass" failed. QA added a visible gate (gate_2_contract) to the fixture. Correct + necessary; not pre-declarable since it surfaced during QA.
Raw QA evidence (direct read, knowledge/qa/evidence/snappier-pro-open-qa-2026-07-15.md):
- Full suite: "2 failed, 2056 passed, 1 warning in 819.87s" — the 2 are the documented pre-existing; zero remaining regressions.
- (a) stale=0 -> run_batch NOT called (spy: test_fresh_invoice_skips_run_batch); (b) stale/unvalidated -> called once; (c) contract edit forces revalidation; (d) invoice edit forces revalidation; (e) POST /validate/<id> force-refresh unaffected (app.py:1985-2004 unconditional); (f) FROZEN core unchanged. Rule 20 banner present verbatim.
Snappier-PRO-open fix shipped: fresh invoice opens now skip the full validation pass (~30-80ms) and render cached gate rows; stale/edited invoices re-validate. Step 1 commit d0cce33.
