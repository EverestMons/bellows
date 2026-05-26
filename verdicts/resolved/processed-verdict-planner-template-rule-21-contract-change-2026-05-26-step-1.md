verdict: stop

Step 1 gate_failure on scope_check flagged the plan file's own claim rename as out-of-scope. Need to characterize the new detection behavior before continuing.

Substance landed correctly per direct file read: Edit A (carve-out paragraph), Edit B (version 4.50 → 4.51, date 2026-05-25 → 2026-05-26), and Edit C (Lessons row) all visible at correct anchors. Two commits split per Rule 8. The substance is fine — the gate trip is the question.

Hypothesis: the 2026-05-25 `executable-file-change-audit-fix` (commit `950436c`) rewrote `_capture_git_diff` to use HEAD SHA + commit-range diff. This newly catches committed changes that the prior working-tree-vs-index diff missed. The plan-file claim rename (`shutil.move` to `in-progress-*`) may be one of those newly-caught changes flowing through to `_gate_scope_check`. Yesterday's plans were structurally identical and did not trip; the daemon restart between yesterday and today loaded the new code into the live daemon for the first time.

Next: Planner authors a diagnostic to characterize what the post-fix scope_check is comparing, what's in-scope vs out-of-scope under the new code path, and whether the plan-file rename is genuinely a regression or a known cost. No code changes until diagnostic findings are in.
