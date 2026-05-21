verdict: continue
Rule 22 verification PASSED on `bellows/knowledge/qa/deposit-exists-path-form-normalization-2026-05-27.md`. All four deliverables verified on disk with line-number citations (Component A at gates.py:295/303/310, Component B at gates.py:254/257/258, `_normalize_deposit_path` helper at gates.py:216-236, 6 new tests at test_gates.py:1204-1274). Targeted suite 99/99 PASS, full suite +6 delta matching Step 1's claim, zero new failures. The five pre-existing failures (`test_decisions.py` x4, `test_run_step_timeout` x1) match prior session documentation.

Substance spot-check on the regression smoke test: evidence file `regression_smoke_repl.txt` shows synthetic inputs in the exact 2026-05-23 abs-vs-rel reproduction shape (plan-required absolute path under tmp/.../bellows/scripts/migrate_config.py, agent-declared relative path bellows/scripts/migrate_config.py, file present at project location) and gate now passes with empty deposit_exists failures list. The fix lands the bug the diagnostic identified.

Rule 20 self-check banner byte-exact PASSED with 4 evidence files verified. No CEO flags, no Critical/Major/Minor findings.

Closes shop_next_session.md Thread 3 (`_gate_deposit_exists` path-form normalization fix). Both Component A (normalization in agent_declared membership check) and Component B (Strategy 0 absolute-path remap) shipped in the same change set.

**Operational reminder:** daemon restart required to load the new gate code. Until restart, the running daemon continues to use pre-fix path comparison and the 2026-05-23 failure mode remains possible on any plan that uses absolute paths in its `**Deposits:**` block.

Authorized by CEO 2026-05-20.
