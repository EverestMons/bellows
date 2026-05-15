verdict: continue
Rule 22 override on `deposit_exists` gate failure. Gate tripped on a Planner plan-authoring error, not an agent failure or a missing deliverable.

Root cause: Plan's **Deposits:** block listed `bellows/[test-file-path]` with a literal placeholder string that was supposed to be substituted by the agent during pre-edit context-read. Rule 26 makes the **Deposits:** block canonical for the gate, and the gate scanned the literal placeholder as a required path, found no such file, and failed. The agent correctly resolved the placeholder during execution (real path: `tests/test_runner.py`) but the block was the load-bearing reference.

Substantive deliverables verified via direct file inspection (not agent self-report):

- `runner.py` line 38: `_retry_attempted: bool = False,  # internal retry guard — do NOT pass externally` (kwarg signature)
- `runner.py` line 173: `transient_patterns = ["401", "unauthorized", "authentication", "429", "rate limit", "too many requests"]`
- `runner.py` lines 175-180: stderr_lower check, transient_hit detection, retry-once guard, recursive call with `_retry_attempted=True`
- `tests/test_runner.py`: both `test_run_step_retries_on_transient_401` and `test_run_step_does_not_retry_on_non_transient_error` present
- Commit `36693a5` ("feat(runner): retry once on transient claude -p failures (401/429) — lessons forge proposal 4") on main, parent `08fa9e8`
- Dev log records 17 tests pass (15 pre-existing + 2 new), zero regressions
- Dev log records daemon-restart requirement explicitly

Lessons Forge proposal 4 substantively implemented as specified. The gate failure is a noise signal, not a defect signal.

Override pattern reference: 2026-05-11 LESSONS entry on `deposit_exists` Cause 5 (plan-agent evidence path convention mismatch) — same gate, different sub-case (placeholder-not-substituted vs convention-not-followed), same Planner-override response.

Capturing as a new LESSONS entry post-close: plan **Deposits:** blocks must NOT contain placeholders that the agent will resolve during execution; the gate reads the block literally before the agent runs. If an agent must resolve a path during pre-edit context-read, the **Deposits:** block must list the directory containing the path, OR the plan must accept that the gate will fail and pre-document the override.

Proceed to Step 2 (Bellows QA).
