verdict: continue
Rule 22 (b) substance — PASS. Diagnostic answers the question and overturns the BACKLOG premise with code evidence.

Gate failure was the worktree_teardown_dirty_tree pre-check (Sub-variant A — untracked claim-rename `in-progress-diagnostic-rescan-miss-disposition-2026-05-28.md` on local main), NOT a verification failure. All mechanical gates passed (deposit_exists, scope_check, rule_22_verification, etc.). The pre-check is working as designed — it surfaced the dirty tree clearly instead of a cryptic cherry-pick conflict.

Recovery applied (R2 / Sub-variant A): the findings deposit committed in worktree 88e8d91 did not land on local main because the teardown cherry-pick aborted on the dirty tree. Recovered the deposit via `git checkout 88e8d91 -- knowledge/research/rescan-miss-disposition-2026-05-28.md` and committed to main (cb57887). Did NOT cherry-pick the full commit because 88e8d91 also re-adds an in-progress-* copy of the plan file, which would duplicate the verdict-pending-* plan already on disk.

Substance verification (Rule 22 (b)) — verified independently by reading the deposit from worktree commit 88e8d91:
- Root cause identified is sharper than any Planner hypothesis: the dispatch-mode validator rejection path (bellows.py:390-395) is the only early-exit in run_plan that does NOT call _seen.discard(). A rejected diagnostic strands its slug; slug_from_path strips both diagnostic-/executable- prefixes, so a follow-on executable with the same base name inherits the stranded slug and is silently skipped on every rescan tick until daemon restart clears _seen.
- All four Planner hypotheses (a/c/d refuted, b confirmed) evaluated against the session-12 log as ground truth with specific line/timestamp evidence. The halted-diagnostic-worktree-teardown-dirty-tree-precheck-2026-05-27.md file on disk corroborates the rejection.
- The existing _rescan general-sweep (bellows.py:1172-1177, present since 2026-05-15) already does what the BACKLOG entry proposed adding — confirmed. The proposed fix is dead code; the real fix is 2 LOC.
- Disposition: narrow guard-fix (add _seen.discard at the rejection path), not a new rescan. Flagged follow-up: audit all run_plan return paths for other strand sites.

This is a clean continue on the merits. Terminal step — daemon moves the plan to Done/ on consumption.

Note for session-wrap: teardown did not complete, so the worktree at .bellows-worktrees/rescan-miss-disposition-2026-05-28 is stale and needs manual `git worktree remove --force` after this verdict resolves.
