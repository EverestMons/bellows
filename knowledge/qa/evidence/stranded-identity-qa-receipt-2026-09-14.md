# QA Receipt — stranded-identity-2026-09-14

**Plan:** bellows #100118
**Step:** 2 (QA)
**Base:** `d1ac5cdb` (bellows #100117 Step 1 — implementation on main)
**DEV second commit:** `ee763b4b`

## DEV Commits — Numstat (`d1ac5cdb..ee763b4b`)

```
68      0       knowledge/development/dev-log-stranded-identity-2026-09-14.md
243     243     knowledge/mutants/stranded-identity.json
57      0       knowledge/mutants/stranded-identity.run.txt
159     49      tests/test_worktree.py
```

`bellows.py` is NOT among them — it landed with #100117's `d1ac5cdb`. ✓

## Unchanged Tests

`git diff d1ac5cdb..ee763b4b -- tests/test_abandoned_runner_close.py tests/test_consume_verdicts.py tests/test_bellows.py` → empty ✓

## Hunks in `tests/test_worktree.py`

`git diff -U0 d1ac5cdb..ee763b4b -- tests/test_worktree.py | grep -F '@@'` — every hunk's old line at or after 1199, none at or above 1074:

```
@@ -1199 +1199 @@ def test_stranded_plain_directory_does_not_preserve_checkout_head(git_repo):
@@ -1207 +1207,18 @@ def test_stranded_plain_directory_does_not_preserve_checkout_head(git_repo):
@@ -1208,0 +1226,3 @@ def test_stranded_plain_directory_does_not_preserve_checkout_head(git_repo):
@@ -1332,0 +1353 @@ def test_stranded_symlink_to_checkout_head_neither_read_nor_preserved(git_repo):
@@ -1336,5 +1357,8 @@ def test_stranded_symlink_to_checkout_head_neither_read_nor_preserved(git_repo):
@@ -1349,0 +1374,2 @@ def test_stranded_symlink_to_checkout_head_neither_read_nor_preserved(git_repo):
@@ -1437 +1463 @@ def test_stranded_failed_tip_preservation_stops_before_removal(git_repo):
@@ -1440,0 +1467,2 @@ def test_stranded_failed_tip_preservation_stops_before_removal(git_repo):
@@ -1527 +1555,2 @@ def test_stranded_own_worktree_through_case_variant_path(git_repo):
@@ -1529,13 +1558,14 @@ def test_stranded_own_worktree_through_case_variant_path(git_repo):
@@ -1624,0 +1655,4 @@ def test_stranded_failed_save_stops_before_removal(git_repo, case_id):
@@ -1631 +1665 @@ def test_stranded_failed_save_stops_before_removal(git_repo, case_id):
@@ -1634,0 +1669,2 @@ def test_stranded_failed_save_stops_before_removal(git_repo, case_id):
@@ -1669,0 +1706,11 @@ def test_stranded_registered_detached_head_through_case_variant_path(git_repo):
@@ -1671,13 +1718,5 @@ def test_stranded_registered_detached_head_through_case_variant_path(git_repo):
@@ -1756 +1795,2 @@ def test_stranded_unremovable_symlink_stops_before_worktree_add(git_repo):
@@ -1758,0 +1799 @@ def test_stranded_unremovable_symlink_stops_before_worktree_add(git_repo):
@@ -1774,2 +1815,2 @@ def test_stranded_unremovable_symlink_stops_before_worktree_add(git_repo):
@@ -1785 +1826 @@ def test_stranded_unremovable_symlink_stops_before_worktree_add(git_repo):
@@ -1787 +1827,0 @@ def test_stranded_unremovable_symlink_stops_before_worktree_add(git_repo):
@@ -1795,0 +1836,45 @@ def test_stranded_unremovable_symlink_stops_before_worktree_add(git_repo):
@@ -2164,3 +2248,0 @@ def test_stranded_symlink_failed_save_names_the_symlink_and_unlink(git_repo, cas
@@ -2222,3 +2304,3 @@ def test_stranded_symlink_removal_stop_branch_not_deletable(git_repo):
@@ -2538 +2620 @@ def test_stranded_stop_retry_reposts_the_request_the_consumer_keeps(
@@ -2568,0 +2651,4 @@ def test_stranded_stop_retry_reposts_the_request_the_consumer_keeps(
@@ -2574,0 +2661 @@ def test_stranded_stop_retry_reposts_the_request_the_consumer_keeps(
@@ -2578 +2665 @@ def test_stranded_stop_retry_reposts_the_request_the_consumer_keeps(
@@ -2672,0 +2760,23 @@ def test_stranded_separate_git_dir_clone_left_intact(git_repo):
```

## Twenty-Seven Items Base Check

`git show "12d92347^:tests/test_worktree.py" | wc -l` → `1074`

`git diff -U0 "12d92347^"..ee763b4b -- tests/test_worktree.py | grep -F '@@'`:

```
@@ -1074,0 +1075,1762 @@ def test_auto_stage_noop_when_all_committed(git_repo):
```

One hunk: appends 1762 lines after line 1074, removes none. The twenty-six frozen tests untouched. ✓

## Item 2 — Cleanup Tests (34 PASSED lines)

`/Users/marklehn/Developer/bellows/.venv/bin/python -m pytest -v` over x1–x27, the two recovery tests, and the five existing stranded-cleanup tests:

```
tests/test_worktree.py::test_stranded_plain_directory_preserves_branch_tip PASSED [  2%]
tests/test_worktree.py::test_stranded_plain_directory_does_not_preserve_checkout_head PASSED [  5%]
tests/test_worktree.py::test_stranded_detached_head_and_branch_tip_both_preserved PASSED [  8%]
tests/test_worktree.py::test_stranded_symlink_to_checkout_head_neither_read_nor_preserved PASSED [ 11%]
tests/test_worktree.py::test_stranded_plain_directory_registered_detached_head_preserved PASSED [ 14%]
tests/test_worktree.py::test_stranded_failed_tip_preservation_stops_before_removal PASSED [ 17%]
tests/test_worktree.py::test_stranded_nested_repository_stops_before_any_read_or_removal PASSED [ 20%]
tests/test_worktree.py::test_stranded_own_worktree_through_case_variant_path PASSED [ 23%]
tests/test_worktree.py::test_stranded_failed_save_raises_before_worktree_add PASSED [ 26%]
tests/test_worktree.py::test_stranded_unremovable_symlink_stops_before_worktree_add PASSED [ 29%]
tests/test_worktree.py::test_stranded_partly_removable_directory_stops_before_worktree_add PASSED [ 32%]
tests/test_worktree.py::test_stranded_symlink_to_live_worktree_leaves_the_target_intact PASSED [ 35%]
tests/test_worktree.py::test_stranded_dangling_symlink_reaches_the_helper[no-branch] PASSED [ 38%]
tests/test_worktree.py::test_stranded_dangling_symlink_reaches_the_helper[unlanded-branch] PASSED [ 41%]
tests/test_worktree.py::test_stranded_stop_on_resumed_dispatch_pauses_at_the_dispatched_step PASSED [ 44%]
tests/test_worktree.py::test_stranded_symlink_failed_save_names_the_symlink_and_unlink[link-to-live-worktree] PASSED [ 47%]
tests/test_worktree.py::test_stranded_symlink_failed_save_names_the_symlink_and_unlink[link-to-checkout] PASSED [ 50%]
tests/test_worktree.py::test_stranded_symlink_removal_stop_branch_not_deletable PASSED [ 52%]
tests/test_worktree.py::test_stranded_failed_identity_lookup_reads_as_not_own[lookup-nonzero] PASSED [ 55%]
tests/test_worktree.py::test_stranded_failed_identity_lookup_reads_as_not_own[lookup-raises] PASSED [ 58%]
tests/test_worktree.py::test_stranded_stop_at_final_step_continue_retries_the_step[two-step-final] PASSED [ 61%]
tests/test_worktree.py::test_stranded_stop_at_final_step_continue_retries_the_step[one-step] PASSED [ 64%]
tests/test_worktree.py::test_final_step_gate_failure_continue_still_closes_to_done PASSED [ 67%]
tests/test_worktree.py::test_stranded_stop_retry_reposts_the_request_the_consumer_keeps PASSED [ 70%]
tests/test_worktree.py::test_stranded_clone_of_the_project_left_intact PASSED [ 73%]
tests/test_worktree.py::test_stranded_separate_git_dir_clone_left_intact PASSED [ 76%]
tests/test_worktree.py::test_stranded_dot_git_symlink_stops_before_any_read PASSED [ 79%]
tests/test_worktree.py::test_stranded_symlink_save_fail_names_the_symlink PASSED [ 82%]
tests/test_worktree.py::test_stranded_dot_git_file_no_gitdir_line_is_foreign PASSED [ 85%]
tests/test_worktree.py::test_create_worktree_cleans_stranded_directory PASSED [ 88%]
tests/test_worktree.py::test_create_worktree_cleans_stranded_registered_worktree PASSED [ 91%]
tests/test_worktree.py::test_stranded_cleanup_preserves_unlanded_commits PASSED [ 94%]
tests/test_worktree.py::test_stranded_cleanup_no_preserve_when_already_landed PASSED [ 97%]
tests/test_worktree.py::test_stranded_cleanup_failsafe_preserves_when_main_unresolvable PASSED [100%]
============================== 34 passed in 7.60s ==============================
```

## Item 3 — Production Writes

None outside the two evidence files; no lane file, no live lifecycle row, no daemon act.

`git -C /Users/marklehn/Developer/bellows branch --list 'bellows-preserved/t322-*' 'bellows-wt/t322-*' 'bellows-preserved'`:

```

```

(empty)

## Verification

| Item | Evidence | Status |
|------|----------|--------|
| 1 — full suite | 2522 passed, two skips (test_gate_watcher live-DB; test_fallback_live_wal_window version gate) | ✅ |
| 2 — cleanup tests | 34 PASSED lines above; x1–x27, two recovery tests, five existing cleanup tests | ✅ |
| 3 — production writes | none outside evidence files; branch listing empty | ✅ |

============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: /Users/marklehn/Developer/bellows/.bellows-worktrees/100118/knowledge/qa/evidence/
Files verified: 1
