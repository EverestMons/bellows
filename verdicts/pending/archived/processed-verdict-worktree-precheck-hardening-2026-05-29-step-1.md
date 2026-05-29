verdict: continue

Rule 22 (b) substance — PASS. DEV step (1 of 2) verified directly on main, not from the agent summary.

All three changes are physically present and correct in bellows.py:
- (a) `_create_worktree` stranded-worktree cleanup: existence guard sits after the parent_dir mkdir and before `git worktree add` — `git worktree remove --force` (failure swallowed) then `shutil.rmtree(ignore_errors=True)` then `git worktree prune`, with the stranded-worktree WARN. Mirrors the `__init__` startup-prune invocation style (same subprocess pattern, cwd, timeout, swallowed exceptions).
- (f) `.strip()` -> `.rstrip()` at the dirty-tree pre-check (lines 906-907). `_is_lifecycle_artifact` extracts the path via `porcelain_line[3:]` and handles the rename form, so preserving the leading status-code space on the first porcelain line fully closes the false-strict bug.
- (g) `_LIFECYCLE_IGNORE_RE` extended with `^\.bellows-worktrees(/|$)` — anchored, matches the bare dir and child paths, will not false-match `bellows-worktrees-imposter`.

Tests: 4 new regression tests present in test_worktree.py (2 stranded-worktree, 1 space-prefixed lifecycle line, 1 .bellows-worktrees ignore), each with positive and negative controls. Full-suite 425 -> 432 passed; the 3 target failures (test_teardown_removes_worktree_directory, test_teardown_cherry_picks_commits, test_teardown_copies_uncommitted_files) flipped green; zero new regressions. The 5 remaining failures are known worktree-context carry-over (4x test_decisions.py phrase-file artifact + 1x test_run_step_timeout), not introduced by this change.

Mechanical gates all PASS (header_pause, scope_check, deposit_exists, file_change_audit, 0 intermediate-decision phrase-matches). Step-1 teardown was clean — commits cherry-picked to main, worktree removed, no R2 recovery.

Continue to step 2 (QA).
