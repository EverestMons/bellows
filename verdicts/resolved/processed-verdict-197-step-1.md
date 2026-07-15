verdict: continue
Step 1 verified — Bellows gates all PASS + Planner check (b) confirmed by direct read.
- runner.py: park-blocking guard relaxed to block only on has_mutating_tool_use (num_turns/total_output_tokens now log-only). The granted-park branch logs "...no committable progress (turns=N, tokens=T, mutating=False); parking" (the governance ask); code comment cites the exec-194 regression + the bellows.py backstop.
- Backstop verified intact and NOT modified: bellows._maybe_park_session_limit (bellows.py:427-437) still checks worktree HEAD vs plan_baseline_sha, wired at both call sites (678, 803) — relaxing the runner guard cannot strand committed work (no mutating tool = no commit; the backstop catches any commit regardless).
- Tests: new test_exit1_exec194_regression_read_only_turns_parkable (turns=4, tokens=48, mutating=False -> park dict) + high-turns/tokens-without-mutating -> parks + Bash tool_use -> still None; existing progress-not-parkable (uses Write) still holds. Targeted run: 60 passed.
Scope clean (runner.py + tests/test_session_limit_park.py + DEV log). Proceed to Step 2 (full bellows suite + behavior verification + Rule 20).
