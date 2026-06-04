verdict: continue

Step 1 (DEV) — Gap 1c implementation. All Bellows gates PASS; Gate Result JSON carries failures=[] (no hidden worktree_teardown failure — teardown succeeded, main was clean). Planner (b) substance check PASS against the committed diff on main (2153fc1):

- Helper `_retry_recoverable_teardown(gate_result, project_path, wt_path, slug)` placed immediately after `_teardown_worktree`. Predicate order matches spec exactly: (1) no worktree_teardown failures -> return False; (2) `not os.path.isdir(wt_path)` -> INFO skip, return False; (3) not all failures carry `worktree_teardown_dirty_tree` in evidence -> INFO skip, return False; (4) try `_teardown_worktree` -> on success clear ALL worktree_teardown entries from gate_result["failures"] + EVENT log + return True; WorktreeTeardownError -> WARN + False; Exception -> WARN + False. Never raises.
- Failure-clearing is correctly scoped: list comprehension removes only `gate == "worktree_teardown"` entries; other failures preserved.
- Call site at the TOP of the `if v == "continue":` branch, BEFORE the Gap-1b guard, with correct path reconstruction (`os.path.dirname(os.path.dirname(decisions_path))` + `cleanup_slug`, which equals the worktree dir name `_create_worktree` uses). Gap-1b guard body byte-unchanged below it. `_teardown_worktree` / `_create_worktree` untouched.
- Four regression tests in tests/test_consume_verdicts.py, all non-vacuous: success (result True, failure cleared, `_teardown_worktree` called once with correct args); content-conflict (result False, failure retained, NOT called); missing-worktree (result False, retained, NOT called); raises-again (result False, retained -> Gap-1b still halts).
- Pre/post-edit pytest: 440 -> 444, same 5 carry-over failures, zero new failures.

Implementation is exactly to spec and self-certifying via the four-branch tests. Proceed to Step 2 (QA, code-level only).
