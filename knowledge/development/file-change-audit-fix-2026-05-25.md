# Dev Log — file_change_audit false-negative fix

**Date:** 2026-05-25
**Plan:** `executable-file-change-audit-fix-2026-05-25`
**BACKLOG:** 2026-05-21 `file_change_audit` false-negative

## (a) bellows.py diff

```diff
--- a/bellows.py
+++ b/bellows.py
@@ -484,7 +484,7 @@
         # Capture post-step file state and run gates
         post_diff = _capture_git_diff(wt_path)
-        files_changed = _parse_diff_stat(post_diff, pre_diff, project_path)
+        files_changed = _parse_diff_stat(post_diff, pre_diff, wt_path)

@@ -575,7 +575,7 @@
             # Capture post-step file state and run gates
             post_diff = _capture_git_diff(wt_path)
-            files_changed = _parse_diff_stat(post_diff, pre_diff, project_path)
+            files_changed = _parse_diff_stat(post_diff, pre_diff, wt_path)

@@ -676,50 +676,75 @@
 def _capture_git_diff(project_path: str) -> str:
-    """Capture git diff --stat output for file change tracking..."""
-    # OLD: ["git", "--no-pager", "diff", "--stat", "--relative", "--", "."]
-    # Returned raw diff --stat text; blind to committed changes.
+    """Capture the current HEAD commit SHA..."""
+    # NEW: ["git", "--no-pager", "rev-parse", "HEAD"]
+    # Returns SHA string; captures committed state.
     try:
         result = subprocess.run(
-            ["git", "--no-pager", "diff", "--stat", "--relative", "--", "."],
+            ["git", "--no-pager", "rev-parse", "HEAD"],
             cwd=project_path, capture_output=True, text=True, timeout=10,
         )
-        return result.stdout
+        if result.returncode != 0:
+            return ""
+        return result.stdout.strip()
     except Exception:
         return ""

 def _parse_diff_stat(post_diff: str, pre_diff: str, project_path: Optional[str] = None) -> list:
-    """Parse git diff --stat output (diff-of-diffs semantics)..."""
-    # OLD: parsed pre/post diff text, compared stat maps.
+    """Return list of files changed between pre_diff (HEAD SHA) and current working tree..."""
+    # NEW: runs `git diff --stat <pre_sha> -- .` internally.
+    if not pre_diff:
+        return []
+    cwd = project_path if project_path else None
+    try:
+        result = subprocess.run(
+            ["git", "--no-pager", "diff", "--stat", "--relative", pre_diff, "--", "."],
+            cwd=cwd, capture_output=True, text=True, timeout=10,
+        )
+    except Exception:
+        return []
+    if result.returncode != 0:
+        return []
+    # Parse stat lines, filter ../ paths if project_path set.
     ...
```

Full diff available via `git --no-pager diff HEAD bellows.py` after commit.

## (b) tests/test_bellows.py diff

**Deleted 12 tests** (plan specified 10; 2 additional tests `test_parse_diff_stat_project_path_filters_repo_root` and `test_parse_diff_stat_project_path_keeps_deep_paths` were also deleted as they test the old diff-text contract — see deviations section):
- `test_parse_diff_stat_preexisting_unchanged_returns_empty`
- `test_parse_diff_stat_new_file_only_in_post`
- `test_parse_diff_stat_preexisting_changed_stat_is_reported`
- `test_parse_diff_stat_summary_line_ignored`
- `test_parse_diff_stat_empty_inputs_return_empty`
- `test_capture_git_diff_uses_relative_pathspec`
- `test_parse_diff_stat_no_project_path_returns_all`
- `test_parse_diff_stat_project_path_all_inside`
- `test_parse_diff_stat_project_path_filters_dotdot`
- `test_parse_diff_stat_project_path_filters_sibling_project`
- `test_parse_diff_stat_project_path_filters_repo_root` (plan missed)
- `test_parse_diff_stat_project_path_keeps_deep_paths` (plan missed)

**Added 6 new tests** under section header `# _capture_git_diff / _parse_diff_stat — commit-aware semantics (BACKLOG 2026-05-21 fix)`:
1. `test_capture_git_diff_returns_head_sha` — real git repo, cross-checks SHA
2. `test_capture_git_diff_returns_empty_on_no_git` — non-git tmpdir
3. `test_parse_diff_stat_empty_pre_sha_returns_empty` — short-circuit on empty pre_diff
4. `test_parse_diff_stat_detects_committed_changes` — **the regression test for the actual bug**
5. `test_parse_diff_stat_detects_uncommitted_changes` — edge case coverage
6. `test_parse_diff_stat_filters_dotdot_paths` — mock-based `../` filter test

Added `import subprocess` to test file imports.

Full diff available via `git --no-pager diff HEAD tests/test_bellows.py` after commit.

## (c) Full-suite pytest output

```
407 collected, 396 passed, 11 failed

All 6 new tests PASSED:
  test_capture_git_diff_returns_head_sha PASSED
  test_capture_git_diff_returns_empty_on_no_git PASSED
  test_parse_diff_stat_empty_pre_sha_returns_empty PASSED
  test_parse_diff_stat_detects_committed_changes PASSED
  test_parse_diff_stat_detects_uncommitted_changes PASSED
  test_parse_diff_stat_filters_dotdot_paths PASSED

11 failures — ALL pre-existing carry-overs:
  5 known carry-overs (per plan):
    4 × test_decisions.py (worktree artifacts)
    1 × test_run_step_timeout
  6 additional carry-overs from set→list refactor (commit 4e805fa):
    test_extract_plan_required_deposits_prefers_declared_block
    test_extract_plan_required_deposits_handles_none_bullet
    test_extract_plan_required_deposits_ignores_paths_in_code_fences_when_block_present
    test_extract_plan_required_deposits_blank_quoted_line
    test_extract_plan_required_deposits_multiple_blank_quoted_lines
    test_extract_plan_required_deposits_does_not_span_paragraphs

Zero new regressions.
```

## (d) Scope_check no longer silently no-opping

```
$ python3 -c "from bellows import _capture_git_diff, _parse_diff_stat; ..."
_capture_git_diff returned: 3ddb48b93afa...
HEAD~1: 060147167a21...
Files changed in last commit: ['.../file-change-audit-false-negative-2026-05-25.md', 'bellows.py', 'knowledge/research/agent-prompt-feedback.md', 'tests/test_bellows.py']
PASS: scope_check is no longer silently no-opping on committed changes
```

Under the old implementation, this would have returned `files_changed = []` because both working trees were clean (the commit was already done). The new implementation compares HEAD SHAs and runs `git diff --stat <pre_sha> -- .`, which correctly captures committed changes.

## (e) Deviations from plan

1. **12 tests deleted instead of 10.** The plan listed 10 test names to delete (lines 538-636). Two additional tests at lines 642-660 (`test_parse_diff_stat_project_path_filters_repo_root` and `test_parse_diff_stat_project_path_keeps_deep_paths`) were also deleted because they test the old diff-text contract. The `keeps_deep_paths` test would fail under the new implementation (empty `pre_diff` → short-circuit → `[]` ≠ expected list). The `filters_repo_root` test would pass by coincidence but tests an obsolete contract.

2. **2 call sites updated, not 4.** The plan referenced "4 call sites" for `_parse_diff_stat`, but there are only 2 `_parse_diff_stat` call sites (lines 487, 578). The "4" in the plan refers to the 4 `_capture_git_diff` call sites, which did not need modification.

3. **Pre-edit verification check 3: 32 mock-patch sites, not ≥38.** `grep -c 'patch."bellows._capture_git_diff", return_value=""'` returned 32, below the plan's expected ≥38. The plan acknowledges "exact count drifts with unrelated test churn". 32 is close enough, and the key constraint (these sites must not be modified) holds. All 32 `return_value=""` sites continue to work: empty-string return → `_parse_diff_stat` short-circuits to `[]`.

4. **11 pre-existing failures instead of 5.** The plan expected 5 carry-over failures. 6 additional failures in `test_rule_26_deposit_parser.py` are pre-existing from the `set→list` refactor (commit 4e805fa, landed after the plan was written). Not caused by this change.

## (f) Output Receipt

**Status: Complete**

- `_capture_git_diff`: rewritten to return HEAD SHA via `git rev-parse HEAD`
- `_parse_diff_stat`: rewritten to run `git diff --stat <pre_sha> -- .` internally
- 2 call sites updated: `project_path` → `wt_path` as third argument
- 12 old tests deleted, 6 new tests added (all passing)
- 32 existing `return_value=""` mock-patch sites unchanged and working
- Live verification confirms committed changes now detected
- Closes BACKLOG 2026-05-21 `file_change_audit` false-negative
- Closes cascading silent bypass of `_gate_scope_check`
