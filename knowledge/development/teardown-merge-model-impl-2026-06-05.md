# Teardown Merge-FF Model — Implementation Log

**Date:** 2026-06-06 | **Agent:** Bellows Developer | **Step:** 2 (DEV)
**Plan:** executable-bellows-teardown-merge-model-2026-06-05
**Blueprint:** knowledge/architecture/teardown-merge-model-blueprint-2026-06-05.md

---

## Changes

### bellows.py

**§2 — `_create_worktree` → named branch:**
- Docstring: "detached-HEAD" → "named-branch"
- `worktree add` command: `HEAD --detach` → `-b bellows-wt/<slug> HEAD`
- Added defensive slug sanitization: `re.sub(r'[^a-zA-Z0-9._/-]', '-', slug)`
- Added sequential-invariant fail-fast: `rev-parse --verify refs/heads/bellows-wt/<slug>` before creation; raises `WorktreeCreationError` if branch pre-exists
- Stranded-cleanup now also deletes the named branch (`git branch -D bellows-wt/<slug>`) after worktree removal

**§3 — `_teardown_worktree` → merge model:**
- Legacy-worktree migration: checks for `bellows-wt/<slug>` branch; raises descriptive `WorktreeTeardownError` if missing (detached-HEAD worktree from pre-merge daemon)
- Commit enumeration preserved; removed `[::-1]` reversal (merge doesn't iterate SHAs)
- Index-lock comment: "before cherry-pick" → "before merge"
- (b2) pre-check deleted entirely (42 lines)
- (c) cherry-pick loop replaced with: `merge --ff-only` primary → `merge --no-ff --no-edit` fallback → `merge --abort` + raise on conflict
- (d) copy-back deleted entirely (24 lines)
- Branch cleanup: `git branch -d bellows-wt/<slug>` on success path (after worktree removal)
- Docstring: "cherry-pick commits back, copy dirty files" → "merge commits back to main, remove worktree and branch"
- `WorktreeTeardownError` class docstring: "cherry-pick conflict" → "merge conflict, legacy worktree"

**§4 — `_retry_recoverable_teardown` removed:**
- Function deleted (34 lines)
- Caller in `_consume_verdicts` deleted (6 lines: Gap 1c setup + call)
- Gap 1b guard comment: "cherry-picked" → "merged"

**§5 — Dead code removed:**
- `_LIFECYCLE_IGNORE_RE` (6 lines)
- `_is_lifecycle_artifact()` (9 lines)
- Comment block above them (4 lines)

### tests/test_worktree.py

- Import: removed `_is_lifecycle_artifact`
- `test_create_worktree_returns_valid_path_with_tracked_files`: added branch-exists assertion
- `test_teardown_removes_worktree_directory`: added branch-deleted assertion
- `test_teardown_cherry_picks_commits` → renamed to `test_teardown_merges_commits`, updated slug and assertions
- `test_teardown_copies_uncommitted_files`: **DELETED**
- `test_teardown_aborts_on_cherry_pick_conflict` → renamed to `test_teardown_aborts_on_merge_conflict`; updated match string, replaced CHERRY_PICK_HEAD with MERGE_HEAD check, added branch-still-exists assertion
- `test_teardown_proceeds_on_empty_commit_list`: added branch-deleted assertion
- `test_create_worktree_retries_once_on_failure`: updated mock to handle branch-check call (rev-parse returns rc=1) before worktree add calls
- `test_pre_check_recognizes_space_prefixed_lifecycle_line`: **DELETED**
- `test_pre_check_ignores_bellows_worktrees_dir`: **DELETED**
- Stranded-cleanup tests: updated `git add .` → `git add <specific_file>` to avoid submodule warnings
- git_repo fixture: added bellows-wt/* branch cleanup in teardown

**6 new permanent regression tests added:**
1. `test_landing_tolerates_dirty_main_invariant` — INVARIANT tripwire
2. `test_landing_aborts_clean_on_dirty_overlap` — dirty-tree overlap → clean abort
3. `test_landing_noff_when_main_advanced` — ff-only fails → no-ff succeeds, SHAs reachable
4. `test_landing_aborts_on_true_conflict_main_advanced` — true conflict → abort, no partial state
5. `test_sha_identity_ff_and_noff` — ff: main HEAD == wt SHA; no-ff: wt SHA reachable from HEAD
6. `test_legacy_branchless_worktree_raises_descriptive_error` — detached-HEAD → descriptive error

### tests/test_bellows.py

- `test_run_plan_pauses_on_cherry_pick_conflict` → renamed to `test_run_plan_pauses_on_merge_conflict`
- Both `WorktreeTeardownError("cherry-pick conflict")` side_effects → `"merge conflict"`
- Index-lock test docstring: "before cherry-pick" → "before merge"
- **DELETED** (11 tests): `test_teardown_pauses_when_local_main_dirty`, `test_teardown_proceeds_when_local_main_clean`, `test_teardown_dirty_tree_evidence_contains_recovery_commands`, `test_teardown_proceeds_when_git_status_errors`, `test_teardown_ignores_lifecycle_artifacts`, `test_teardown_ignores_deletion_porcelain_codes`, `test_lifecycle_artifact_regex_coverage`, `test_teardown_blocks_on_non_lifecycle_untracked`, `test_teardown_blocks_on_dirty_project_status`, `test_teardown_blocks_on_real_dirty_mixed_with_lifecycle`, `test_teardown_blocks_on_dirty_source_file`
- `test_create_worktree_proceeds_when_git_exists`: updated mock to return rc=1 for branch-check call

### tests/test_consume_verdicts.py

- `test_continue_blocked_on_worktree_teardown_failure_interstep`: evidence string updated from `worktree_teardown_dirty_tree: ...` → `merge conflict on bellows-wt/...`
- `test_continue_to_done_blocked_on_worktree_teardown_failure_final_step`: same evidence string update
- **DELETED** (4 tests): `test_retry_clears_dirty_tree_teardown_on_success`, `test_retry_skips_content_conflict`, `test_retry_skips_when_worktree_missing`, `test_retry_keeps_failure_when_teardown_raises_again`

---

## Per-Edit Pytest Results

| Edit | `pytest tests/` result |
|------|----------------------|
| All bellows.py changes | `python3 -c "import bellows"` → OK |
| test_worktree.py rewrite | 20 passed (all worktree tests) |
| test_bellows.py + test_consume_verdicts.py updates | 159 passed (all 3 target files) |
| Full suite | 443 passed, 5 failed (pre-existing in test_decisions.py + test_runner_parser.py) |

## Final Count

- Total passing: 443
- Total failing: 5 (pre-existing, unrelated)
- Total tests: 448
- Baseline: 460 → removed 18 (3 worktree + 11 bellows + 4 consume_verdicts) + added 6 = 448. ✓
- New tests: 6

## Dead-Symbol Grep

```
grep -rn "_is_lifecycle_artifact\|_LIFECYCLE_IGNORE_RE\|_retry_recoverable_teardown\|cherry-pick\|cherry_pick" bellows.py
→ No matches found

grep -rn "rebase" bellows.py
→ No matches found
```

## SHA-Identity Note

- FF path: `test_sha_identity_ff_and_noff` sub-test A confirms `main HEAD == worktree SHA` (exact identity)
- No-ff path: sub-test B confirms `worktree SHA reachable from HEAD` via `merge-base --is-ancestor`
- Both pass.

## No Rebase in Teardown

Confirmed: zero references to `rebase` in bellows.py. The teardown path uses only `merge --ff-only` and `merge --no-ff --no-edit`. Conflict → `merge --abort` + raise.

---

## Output Receipt
**Agent:** Bellows Developer
**Step:** 2
**Status:** Complete

### What Was Done
Implemented the merge-ff teardown model per the SA blueprint. Replaced cherry-pick loop with ff-only/no-ff merge, removed dirty-tree pre-check and copy-back, cut `_retry_recoverable_teardown`, removed dead lifecycle artifact code, added legacy-worktree migration detection, added branch-cleanup ordering, and added 6 permanent regression tests (including the dirty-main invariant tripwire and SHA-identity verification).

### Files Deposited
- `knowledge/development/teardown-merge-model-impl-2026-06-05.md` — this implementation log

### Files Created or Modified (Code)
- `bellows.py` — merge-ff teardown model (§2-§5 from blueprint)
- `tests/test_worktree.py` — 6 new regression tests + updated existing tests
- `tests/test_bellows.py` — deleted dead tests, updated error strings
- `tests/test_consume_verdicts.py` — updated evidence strings, deleted retry tests

### Decisions Made
- Conflict-path assertions filter `.bellows-worktrees/` from porcelain status (worktree is intentionally left alive)
- `test_create_worktree_retries_once_on_failure` mock updated to return rc=1 for branch-check call before worktree add calls (3 total subprocess calls instead of 2)
- Stranded-cleanup tests updated to use `git add <specific_file>` instead of `git add .`

### Flags for CEO
- None

### Flags for Next Step
- 5 pre-existing test failures in test_decisions.py (4) and test_runner_parser.py (1) — unrelated to this change
- Full suite: 443 passed, 5 failed (pre-existing)
