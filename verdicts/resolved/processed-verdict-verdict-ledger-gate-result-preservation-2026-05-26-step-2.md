verdict: continue
Rule 22 override on gate_failure. Substance verified by Planner reading the QA report and supporting evidence files; gate fired on a real syntactic issue in plan authoring, not on agent-side defect.

Substance check (Rule 22 (b)): QA report's Deliverable Verification table shows 12/12 ✅ with citations to evidence files that exist on disk. Five new tests pass (test_post_verdict_request_includes_gate_result_json, three test_consume_verdicts_* tests covering continue-to-done, continue-resume, fallback-when-absent, and test_gates_log_includes_failure_gates_and_files_changed_count). Targeted suite: 173/0/1. Full suite: 407 passed, 5 failed (pre-existing carry-overs: 4 × test_decisions.py worktree-context artifact per BACKLOG 2026-05-21 closure, 1 × test_run_step_timeout long-standing). Zero new regressions. Round-trip proof in evidence/round_trip.txt demonstrates JSON metadata survives post_verdict_request → file → parse → json.loads. Rule 20 canonical banner is byte-exact in the QA report (verified via raw bytes match: "Rule 20 \\xe2\\x80\\x94 QA Self-Check Results"). PASSED — SELF-CHECK PASSED line is also byte-exact present. Evidence dir at /Users/marklehn/Developer/GitHub/bellows/knowledge/qa/evidence/executable-verdict-ledger-gate-result-preservation-2026-05-26/ contains all 7 declared files.

Root cause of gate_failure: Planner-authored Deposits block used malformed inline format. The plan wrote `**Deposits:** \`path1.md\`, \`path2/\`.` but _extract_plan_required_deposits at gates.py:387 requires either (a) multi-line bullet block form (`**Deposits:**` on own line followed by `- ` bullets) or (b) inline form with `\`- path\`` syntax (backticked items with `-` prefix inside backticks). Neither matched, so md_paths was empty, and gate fired with "no QA deposit contains Rule 20 self-check banner" — misleading message that lumps two distinct failure modes (no md_paths vs. banner literally absent) under one evidence string.

The gate caught a real Planner-authoring discipline failure, but the underlying work is verified correct. Plan moves to Done/.

Follow-up items for session wrap:
1. LESSONS planner-discipline entry: use Rule 26 multi-line block form for Deposits, not inline.
2. BACKLOG entry: _gate_rule_20_self_check observability gap — same evidence string for two distinct failure conditions at gates.py:441 and gates.py:464.
3. BACKLOG entry: file the test fixture cleanup (test_run_plan_inprogress_entry_renames_to_verdict_pending uses string-typed failures) so Fix F's isinstance guard can be removed and contract uniformity restored.

Plan already moved to bellows/knowledge/decisions/Done/ by Planner per Rule 25 auto_close_disabled terminal-close pattern (most-similar precedent for gate_failure override).
