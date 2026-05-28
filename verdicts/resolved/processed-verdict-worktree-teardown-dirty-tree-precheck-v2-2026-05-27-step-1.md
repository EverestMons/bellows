verdict: continue
Rule 22 substance check (b) PASS. Deposit answers the question: full surface characterization for the dirty-tree pre-check executable.

Verification:
- Cherry-pick call site mapped (bellows.py:856-870), insertion point identified (line 855, after index.lock cleanup, before cherry-pick loop), cwd correctly scoped to project_path (main checkout, not worktree).
- Evidence-string format proposed (22 lines, under target), includes dirty-file listing + dual-variant R2 recovery commands + LESSONS pointer.
- Test surface enumerated: 3 new tests (~37 LOC) + existing-test impact analysis. test_run_plan_pauses_on_cherry_pick_conflict correctly identified as needing no fixture change (patches entire _teardown_worktree).
- 5 edge cases worked (race window, cwd confusion, submodule dirty state, Bellows-self, additive-not-replacing).
- LOC estimate ~65 total (~25 prod + ~40 test); BACKLOG ~20 estimate refuted as production-only/pre-evidence-string.

Two SA corrections accepted:
- The gate is NOT a new top-level _pause_reason enum; it flows through the existing WorktreeTeardownError -> gate_failure path with a new gate name in the failure dict. Cleaner, smaller blast radius. No run_plan change.
- LESSONS.md 2026-05-27 R2 recovery shape pointer is valid; the entry was promoted this session before dispatch, so Section 7 Q2 resolves itself.

Three CEO decisions locked for the executable:
- git status --porcelain failure handling: fail-open (SA rec). Transient git errors proceed to cherry-pick; the existing cherry-pick path catches truly-bad state. Fail-closed would add a new failure mode against the goal of fewer cryptic pauses.
- PLANNER_TEMPLATE Rule 25 routing-table update for the new gate name: BACKLOG it, ship code-only this session. Gate name is self-documenting in the evidence string; routing-table update is a refinement, not a blocker.
- Proceed to executable now.

Executable plan will follow as a separate deposit.
