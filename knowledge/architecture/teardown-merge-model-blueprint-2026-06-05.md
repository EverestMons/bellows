# Teardown Merge-FF Model — Edit Map & Regression-Test Plan

**Date:** 2026-06-05 | **Agent:** Bellows Systems Analyst | **Step:** 1 (SA)
**Plan:** executable-bellows-teardown-merge-model-2026-06-05
**Source Diagnostic:** knowledge/research/teardown-dirty-main-rootcause-2026-06-05.md

---

## §1 — Step-(d) Consumer Trace — HARD GATE

### Evidence

| Check | Result |
|-------|--------|
| `grep -rn "shutil.copy" bellows.py` | Single hit: line 1032 — step (d) itself |
| `grep -rn "shutil.copy\|copy_back\|dirty.file\|uncommitted" gates.py` | Zero hits |
| `grep -rn "shutil.copy\|copy_back\|dirty.file\|uncommitted" runner.py` | Zero hits |
| `grep -rn "shutil.copy\|copy_back\|dirty.file\|uncommitted" verdict.py` | Zero hits |

Step (d) (bellows.py:1011-1034) copies uncommitted worktree files to `project_path` via `shutil.copy2`. No gate, verdict, or runner code reads these copied files. The copy-back has no downstream consumers — it writes to the working tree and returns nothing. The only reference to the copy-back outside the function itself is the WARN log at line 1034.

### Verdict: **REMOVE-SAFE**

Remove step (d) entirely. Agents are instructed to commit ("Your final operation is ALWAYS the commit" — runner.py:23). Uncommitted files are either inconsequential scraps or an agent commit failure — copying them to main masks the failure and creates Source A dirty state. The raise-on-log-failure contract (lines 907-927) ensures worktree preservation if git operations fail.

---

## §2 — `_create_worktree` Edit Map

### Current (bellows.py:863)
```python
cmd = ["git", "--no-pager", "worktree", "add", wt_path, "HEAD", "--detach"]
```

### New
```python
branch_name = f"bellows-wt/{slug}"
cmd = ["git", "--no-pager", "worktree", "add", wt_path, "-b", branch_name, "HEAD"]
```

### Slug → git-ref-name safety

`slug` comes from `verdict.slug_from_path()` (verdict.py:82-92) which strips prefixes and `.md`. Observed slug character set: `[a-z0-9-]`. Combined with the `bellows-wt/` prefix, the full ref is `bellows-wt/<slug>` — valid per `git check-ref-format`. No sanitization needed for current slug generation, but DEV should add a defensive check: `re.sub(r'[^a-zA-Z0-9._/-]', '-', slug)` before constructing the branch name.

### Sequential-invariant fail-fast

After stranded-worktree cleanup and before the `worktree add` command, check if the branch already exists:

```python
# Fail-fast: branch bellows-wt/<slug> must not pre-exist (sequential invariant)
branch_check = subprocess.run(
    ["git", "--no-pager", "rev-parse", "--verify", f"refs/heads/{branch_name}"],
    cwd=project_path, capture_output=True, text=True, timeout=10,
)
if branch_check.returncode == 0:
    raise WorktreeCreationError(
        f"branch '{branch_name}' already exists — sequential invariant violated "
        f"(prior worktree for this slug was not fully cleaned up)"
    )
```

This catches leaked branches from prior incomplete teardowns.

### Stranded-worktree cleanup update (lines 812-860)

The stranded cleanup already removes the worktree directory and prunes. After worktree removal, also delete the branch:

```python
# After worktree remove + rmtree + prune (existing lines 846-860):
# Clean up the named branch if it exists (prevents sequential-invariant failure)
try:
    subprocess.run(
        ["git", "--no-pager", "branch", "-D", f"bellows-wt/{slug}"],
        cwd=project_path, capture_output=True, text=True, timeout=10,
    )
except Exception:
    pass  # branch may not exist (legacy detached-HEAD worktree)
```

Note: `-D` (force-delete) because the branch may not be merged — stranded cleanup is a recovery path.

### Code assuming detached HEAD

- Line 793: docstring `"""Create a detached-HEAD git worktree"""` → update to `"""Create a named-branch git worktree"""`
- No other code in `_create_worktree` assumes detached HEAD. The stranded-cleanup `rev-parse HEAD` (line 817) works identically on a named-branch worktree.

### Sandbox confirmation

```
/tmp/bellows-sa-sandbox4: git branch bellows-wt/test-slug && git worktree add -b bellows-wt/test-slug
→ fatal: a branch named 'bellows-wt/test-slug' already exists (rc=255)
```

Git's own branch-exists check fires at `worktree add -b` time, providing a second layer behind our explicit fail-fast.

---

## §3 — `_teardown_worktree` Edit Map

### Overview

| Sub-step | Action | Lines affected |
|----------|--------|---------------|
| (a) REMOVE (b2) pre-check | DELETE | 950-992 |
| (b) REPLACE cherry-pick loop | REPLACE with merge | 994-1009 |
| (c) ff-fail fallback | NEW | (inserted at former cherry-pick location) |
| (d) Conflict handling | NEW merge --abort | (replaces cherry-pick --abort) |
| (e) Step (d) copy-back | DELETE | 1011-1034 |
| (f) Branch-cleanup ordering | NEW | (after worktree removal) |
| (g) Legacy-worktree migration | NEW | (before commit enumeration) |

### §3a — REMOVE (b2) pre-check (lines 950-992)

Delete the entire block:
```python
    # (b2) Pre-cherry-pick dirty-tree check on main checkout
    try:
        dt_result = subprocess.run(
            ...
        raise WorktreeTeardownError(
            f"worktree_teardown_dirty_tree: ..."
        )
    except WorktreeTeardownError:
        raise
    except Exception:
        _log("WARN", f"⚠ dirty-tree pre-check failed (proceeding to cherry-pick)", slug=slug)
```

This entire 42-line block is unnecessary: merge tolerates dirty working-tree state for non-overlapping files, and overlapping files produce a clean abort (no conflict markers).

### §3b — REPLACE cherry-pick loop (lines 994-1009) with merge

**Old:**
```python
    # (c) Cherry-pick each commit onto main checkout
    for sha in commit_shas:
        if not sha.strip():
            continue
        result = subprocess.run(
            ["git", "--no-pager", "cherry-pick", sha],
            cwd=project_path, capture_output=True, text=True, timeout=60,
        )
        if result.returncode != 0:
            subprocess.run(
                ["git", "--no-pager", "cherry-pick", "--abort"],
                cwd=project_path, capture_output=True, text=True, timeout=10,
            )
            raise WorktreeTeardownError(
                f"cherry-pick conflict on {sha} for slug {slug}: {result.stderr.strip()}"
            )
```

**New:**
```python
    branch_name = f"bellows-wt/{slug}"

    # (c) Merge worktree branch onto main
    # Primary: --ff-only (linear history when main has not advanced)
    result = subprocess.run(
        ["git", "--no-pager", "merge", "--ff-only", branch_name],
        cwd=project_path, capture_output=True, text=True, timeout=60,
    )
    if result.returncode != 0:
        # Fallback: --no-ff when main advanced (merge commit preserves worktree SHAs as parents)
        result = subprocess.run(
            ["git", "--no-pager", "merge", "--no-ff", "--no-edit", branch_name],
            cwd=project_path, capture_output=True, text=True, timeout=60,
        )
        if result.returncode != 0:
            # True content conflict or dirty-tree overlap — abort cleanly
            subprocess.run(
                ["git", "--no-pager", "merge", "--abort"],
                cwd=project_path, capture_output=True, text=True, timeout=10,
            )
            raise WorktreeTeardownError(
                f"merge conflict on {branch_name} for slug {slug}: {result.stderr.strip()}"
            )
```

### Sandbox confirmation

| Scenario | ff-only | no-ff | abort | Result |
|----------|---------|-------|-------|--------|
| Dirty main, non-overlapping | rc=0 | — | — | Lands clean, dirty preserved |
| Main advanced, no conflict | rc=128 | rc=0 | — | Merge commit, worktree SHAs reachable |
| Main advanced + content conflict | rc=128 | rc=1 | rc=0 | Clean abort, no markers, MERGE_HEAD removed |
| SHA identity (ff path) | main HEAD == branch tip | — | — | Identical SHAs |

### §3c — DELETE step (d) copy-back (lines 1011-1034)

Delete the entire block per §1 REMOVE-SAFE verdict:
```python
    # (d) Copy uncommitted dirty files back
    try:
        result = subprocess.run(
            ["git", "--no-pager", "status", "--porcelain"],
            cwd=wt_path, ...
        )
        for line in result.stdout.splitlines():
            ...
            shutil.copy2(src, dst)
    except Exception as e:
        _log("WARN", f"⚠ dirty file copy-back failed: {e}", slug=slug)
```

### §3d — Branch-cleanup ordering (after worktree removal)

**On success (ff or no-ff merge landed):** merge → remove worktree → `git branch -d bellows-wt/<slug>`.

After the existing worktree removal block (lines 1036-1053), add:

```python
    # Clean up the worktree branch (safe: branch is fully merged)
    try:
        subprocess.run(
            ["git", "--no-pager", "branch", "-d", branch_name],
            cwd=project_path, capture_output=True, text=True, timeout=10,
        )
    except Exception:
        _log("WARN", f"⚠ branch cleanup failed for {branch_name}", slug=slug)
```

Note: `-d` (not `-D`) because the branch IS merged at this point. If `-d` fails, something unexpected happened — log and proceed (worktree is already gone, the branch is cosmetic at this point).

**On conflict (raise path):** the worktree AND branch persist for manual resolution. Stranded-worktree cleanup (in `_create_worktree`) uses `-D` to force-delete the branch during recovery.

### §3e — Legacy-worktree migration

Insert after the main-branch detection (step (a), ~line 905) and before step (b) commit enumeration:

```python
    # Legacy-worktree migration: detect pre-merge-model detached-HEAD worktrees
    branch_name = f"bellows-wt/{slug}"
    branch_check = subprocess.run(
        ["git", "--no-pager", "rev-parse", "--verify", f"refs/heads/{branch_name}"],
        cwd=project_path, capture_output=True, text=True, timeout=10,
    )
    if branch_check.returncode != 0:
        raise WorktreeTeardownError(
            f"legacy detached-HEAD worktree detected for slug {slug}: "
            f"expected branch '{branch_name}' does not exist. "
            f"This worktree was created by a pre-merge-model Bellows daemon. "
            f"Manual resolution required: land commits from the worktree, "
            f"then remove it with 'git worktree remove --force {wt_path}'."
        )
```

Sandbox confirmation: `git rev-parse --verify bellows-wt/legacy-slug` returns rc=128 for a detached-HEAD worktree → detection works.

### §3f — Preserve step (b) commit enumeration

The step (b) block (lines 907-928) is **preserved unchanged**. It still enumerates commits for logging/validation. The raise-on-log-failure contract still fires before the merge attempt.

Update the comment at line 928:
```python
# Old:
commit_shas = result.stdout.strip().splitlines()[::-1]  # oldest-first for cherry-pick
# New:
commit_shas = result.stdout.strip().splitlines()  # enumerated for logging; merge uses branch name
```

The `[::-1]` reversal is no longer needed (merge doesn't iterate SHAs). Drop it.

### §3g — Index-lock detection (lines 930-948)

**Keep** with updated comment. The stale-lock issue applies to merge operations too. Change:
```python
# Old:
    # Detect stale .git/index.lock that would block cherry-pick
# New:
    # Detect stale .git/index.lock that would block merge
```

### §3h — Docstring update

```python
# Old:
    """Tear down a worktree: cherry-pick commits back, copy dirty files, remove worktree.

    Raises WorktreeTeardownError on cherry-pick conflict (worktree left alive for manual resolution).
# New:
    """Tear down a worktree: merge commits back to main, remove worktree and branch.

    Raises WorktreeTeardownError on merge conflict (worktree + branch left alive for manual resolution).
```

### §3i — `WorktreeTeardownError` class docstring

```python
# Old (line 140):
    """Raised when worktree teardown fails (e.g. cherry-pick conflict)."""
# New:
    """Raised when worktree teardown fails (e.g. merge conflict, legacy worktree)."""
```

---

## §4 — Cut `_retry_recoverable_teardown` + Caller

### Function (bellows.py:1055-1087)

**Delete entirely.** The function only retries `worktree_teardown_dirty_tree` failures (line 1073). With the merge model, this failure class is dissolved — merge tolerates dirty working-tree state. Content-conflict failures are already excluded (line 1073-1075 returns False). The function has no purpose after the redesign.

### Caller (bellows.py:1430-1435)

**Delete the call site and setup lines:**
```python
# DELETE these lines:
                            # Gap 1c: re-attempt a recoverable (dirty-tree) teardown before the Gap-1b halt decision.
                            # By verdict time the operator has usually committed the stray dirty file, so the retry
                            # lands Step N's commits and clears the failure — letting the normal advance proceed.
                            _c_project_path = os.path.dirname(os.path.dirname(decisions_path))
                            _c_wt_path = os.path.join(_c_project_path, ".bellows-worktrees", cleanup_slug)
                            _retry_recoverable_teardown(gate_result, _c_project_path, _c_wt_path, cleanup_slug)
```

### Other callers

**Confirmed zero.** Production code: only the one call at line 1435. Test code: `tests/test_consume_verdicts.py` lines 1029-1124 (4 tests) — these are deleted as part of §6 test-impact.

### Gap 1b guard — KEEP (lines 1436-1449)

The Gap 1b guard still blocks continue on `worktree_teardown` failures. These can still occur via merge conflict. Update the comment:

```python
# Old:
                            # An uncleared worktree_teardown failure means Step N's commits were never
                            # cherry-picked to main — advancing would orphan them.
# New:
                            # An uncleared worktree_teardown failure means Step N's commits were never
                            # merged to main — advancing would orphan them.
```

### Rebase-conflict path: **no longer exists**

With the merge model, teardown conflict → `WorktreeTeardownError` → Gap-1b halt is the only recovery path. There is no rebase anywhere in the teardown. CEO manually resolves the conflict in the preserved worktree, then issues a continue verdict. The Gap-1b guard blocks the continue (teardown failure uncleared), routing to halted- for manual R2 recovery. This is the correct behavior — a merge conflict requires manual resolution, not automated retry.

---

## §5 — P2 Dead-Code Removal Map

### `_LIFECYCLE_IGNORE_RE` (lines 42-47)

```python
# DELETE:
_LIFECYCLE_IGNORE_RE = re.compile(
    r'^knowledge/decisions/(in-progress-|verdict-pending-|halted-|executable-|diagnostic-).*\.md$'
    r'|^knowledge/decisions/Done/'
    r'|^verdicts/(pending|resolved)/'
    r'|^\.bellows-worktrees(/|$)'
)
```

### `_is_lifecycle_artifact()` (lines 50-58)

```python
# DELETE:
def _is_lifecycle_artifact(porcelain_line: str) -> bool:
    """Return True if the porcelain line is a daemon-managed lifecycle artifact."""
    if len(porcelain_line) < 4:
        return False
    path = porcelain_line[3:]
    if " -> " in path:
        path = path.split(" -> ", 1)[1]
    return bool(_LIFECYCLE_IGNORE_RE.match(path.strip()))
```

### Comment referencing cherry-pick (lines 38-40)

```python
# DELETE:
# --- Lifecycle artifact filter for dirty-tree pre-check ---
# Daemon-managed bookkeeping paths that agents never commit to.
# These are safe to ignore for cherry-pick conflict purposes.
# See: knowledge/research/dirty-tree-precheck-false-trip-surface-2026-05-28.md Section 3
```

### Zero-caller verification

After removing the (b2) pre-check (§3a), the only production caller of `_is_lifecycle_artifact` (line 959) is gone. The only production user of `_LIFECYCLE_IGNORE_RE` is `_is_lifecycle_artifact` (line 58). Both symbols are dead after the pre-check removal.

Remaining references are in:
- Tests (deleted as part of §6 test-impact)
- `knowledge/BACKLOG.md` (historical documentation, not code — no change needed)
- `knowledge/decisions/` (archived plans — no change)

---

## §6 — Regression-Test Plan

### New permanent tests — `tests/test_worktree.py`

All use the existing `git_repo` fixture (tmp-repo, real git ops, NO writes outside tmp).

#### (i) `test_landing_tolerates_dirty_main_invariant`

**INVARIANT test — future-proofing tripwire.**

```
Setup: Create worktree, commit a file (e.g., new_file.txt) in worktree.
       Dirty main with a DIFFERENT file (e.g., dirty.txt untracked + README.md modified).
Act:   _teardown_worktree(...)
Assert:
  - Teardown succeeds (no raise)
  - new_file.txt exists on main (merge landed)
  - dirty.txt still exists on main (preserved, not cleaned)
  - README.md still modified on main (preserved)
  - Worktree directory removed
  - Branch bellows-wt/<slug> deleted

Docstring: "INVARIANT: landing must never require a clean main working tree.
If this test breaks, a checkout-based teardown step was reintroduced.
See: knowledge/research/teardown-dirty-main-rootcause-2026-06-05.md §R3"
```

#### (ii) `test_landing_aborts_clean_on_dirty_overlap`

```
Setup: Create worktree, modify file.txt in worktree and commit.
       Dirty main by also modifying file.txt (uncommitted).
Act:   _teardown_worktree(...)
Assert:
  - Raises WorktreeTeardownError
  - No conflict markers in file.txt on main (cat file.txt, check for <<<<<<<)
  - No MERGE_HEAD in .git/
  - git status --porcelain shows only the original dirty state (the modified file.txt)
  - Worktree still exists (left for manual resolution)
  - Branch bellows-wt/<slug> still exists
```

#### (iii) `test_landing_noff_when_main_advanced`

```
Setup: Create worktree, commit new_file.txt in worktree.
       On main, commit a DIFFERENT file (main_new.txt) — main advances.
Act:   _teardown_worktree(...)
Assert:
  - Teardown succeeds (no raise)
  - new_file.txt on main (merge landed)
  - main_new.txt on main (main's commit preserved)
  - Merge commit exists: git log --oneline -1 contains "Merge"
  - Worktree commit SHA reachable from HEAD:
    git merge-base --is-ancestor <wt_sha> HEAD → rc=0
  - Worktree directory removed
  - Branch cleaned up
```

#### (iv) `test_landing_aborts_on_true_conflict_main_advanced`

```
Setup: Create worktree, modify file.txt and commit in worktree.
       On main, modify file.txt DIFFERENTLY and commit — true content conflict.
Act:   _teardown_worktree(...)
Assert:
  - Raises WorktreeTeardownError matching "merge conflict"
  - No MERGE_HEAD (abort was clean)
  - No conflict markers in file.txt
  - git status --porcelain is clean (no partial merge state)
  - Worktree still exists
  - Branch still exists (not fully merged, `-d` would fail)
```

#### (v) `test_sha_identity_ff_and_noff`

```
# Sub-test A: ff path
Setup: Create worktree, commit, record worktree HEAD SHA.
Act:   _teardown_worktree(...)
Assert: git rev-parse HEAD on main == recorded worktree SHA (exact identity)

# Sub-test B: no-ff path
Setup: Create worktree, commit, record worktree HEAD SHA.
       Advance main with a non-conflicting commit.
Act:   _teardown_worktree(...)
Assert: git merge-base --is-ancestor <wt_sha> HEAD → rc=0
        (worktree SHA reachable from merge commit)
```

#### (vi) `test_legacy_branchless_worktree_raises_descriptive_error`

```
Setup: Create a DETACHED-HEAD worktree manually:
       git worktree add <wt_path> HEAD --detach
       (Do NOT create bellows-wt/<slug> branch)
Act:   _teardown_worktree(...)
Assert:
  - Raises WorktreeTeardownError matching "legacy detached-HEAD"
  - Error message contains "bellows-wt/<slug>"
  - Worktree still exists
```

### Test-impact list — existing tests

#### `tests/test_worktree.py`

| Test | Action | Notes |
|------|--------|-------|
| `test_create_worktree_returns_valid_path_with_tracked_files` | **UPDATE** | Add assertion: branch `bellows-wt/test-slug` exists after creation |
| `test_worktree_isolation_git_diff` | **KEEP** | No change — isolation semantics identical |
| `test_teardown_removes_worktree_directory` | **UPDATE** | Add assertion: branch `bellows-wt/<slug>` deleted after teardown |
| `test_teardown_cherry_picks_commits` | **UPDATE** | Rename to `test_teardown_merges_commits`. Update assertion message. Remove cherry-pick references. |
| `test_teardown_copies_uncommitted_files` | **DELETE** | Step (d) removed — no copy-back |
| `test_teardown_aborts_on_cherry_pick_conflict` | **UPDATE** | Rename to `test_teardown_aborts_on_merge_conflict`. Remove `CHERRY_PICK_HEAD` assertion. Add `MERGE_HEAD` absence check (merge was aborted). Update error match string. Ensure conflict setup creates a main-advanced scenario (both sides commit to same file). Add branch-still-exists assertion. |
| `test_teardown_raises_on_git_log_exception` | **KEEP** | Raise-on-log-failure contract unchanged |
| `test_teardown_raises_on_git_log_nonzero` | **KEEP** | Raise-on-log-failure contract unchanged |
| `test_teardown_proceeds_on_empty_commit_list` | **UPDATE** | Branch `bellows-wt/<slug>` must still be cleaned up even with no commits. Add branch-absence assertion. |
| `test_create_worktree_retries_once_on_failure` | **UPDATE** | Mocked subprocess command changes (no `--detach`, has `-b`) |
| `test_create_worktree_cleans_stranded_directory` | **UPDATE** | Stranded cleanup now also deletes the branch |
| `test_create_worktree_cleans_stranded_registered_worktree` | **UPDATE** | Same — branch cleanup in stranded path |
| `test_pre_check_recognizes_space_prefixed_lifecycle_line` | **DELETE** | `_is_lifecycle_artifact` removed |
| `test_pre_check_ignores_bellows_worktrees_dir` | **DELETE** | `_is_lifecycle_artifact` removed |
| `test_stranded_cleanup_preserves_unlanded_commits` | **UPDATE** | Worktree now uses named branch; update creation to match |
| `test_stranded_cleanup_no_preserve_when_already_landed` | **UPDATE** | Same |
| `test_stranded_cleanup_failsafe_preserves_when_main_unresolvable` | **UPDATE** | Same |

**Import line (line 25):** Remove `_is_lifecycle_artifact` from import.

#### `tests/test_bellows.py`

| Test / Line | Action | Notes |
|-------------|--------|-------|
| `test_run_plan_pauses_on_cherry_pick_conflict` (line 2179) | **UPDATE** | Rename. Update side_effect error string from "cherry-pick conflict" to "merge conflict" |
| Lines 2796 (index-lock comment) | **UPDATE** | "before cherry-pick" → "before merge" |
| `test_teardown_dirty_tree_*` tests (~2893-2965) | **DELETE** | Dirty-tree pre-check removed — these test the old pre-check |
| `test_status_failure_*` (~2969-3025) | **UPDATE** | Remove references to "proceed to cherry-pick"; the fail-open path no longer exists (pre-check removed) |
| `_is_lifecycle_artifact` unit tests (~3063-3092) | **DELETE** | Function removed |
| Line 4171 | **UPDATE** | Error string update |

#### `tests/test_consume_verdicts.py`

| Test | Action | Notes |
|------|--------|-------|
| `test_continue_blocked_on_worktree_teardown_failure_interstep` (line 813) | **UPDATE** | Change evidence string from `worktree_teardown_dirty_tree: ...` to `merge conflict on bellows-wt/...` |
| `test_continue_to_done_blocked_on_worktree_teardown_failure_final_step` (line 887) | **UPDATE** | Same evidence string update |
| `test_continue_advances_normally_without_teardown_failure` (line 955) | **KEEP** | No change — tests absence of teardown failure |
| `test_retry_clears_dirty_tree_teardown_on_success` (line 1029) | **DELETE** | `_retry_recoverable_teardown` removed |
| `test_retry_skips_content_conflict` (line 1052) | **DELETE** | Same |
| `test_retry_skips_when_worktree_missing` (line 1080) | **DELETE** | Same |
| `test_retry_keeps_failure_when_teardown_raises_again` (line 1106) | **DELETE** | Same |

---

## §7 — Contract Composition Check

### The 2026-06-05 raise-on-log-failure contract (bellows.py:907-927)

This contract raises `WorktreeTeardownError` when the step (b) `git log --format=%H HEAD --not main` fails (exception or non-zero returncode), preventing silent commit loss.

**Composition with merge semantics: CORRECT — no adjustment needed.**

| Aspect | Cherry-pick model | Merge model | Change? |
|--------|------------------|-------------|---------|
| Git-log command | `git log --format=%H HEAD --not main`, cwd=wt_path | Identical | None |
| `HEAD` resolution | Detached HEAD SHA | Branch tip (bellows-wt/slug) — resolves identically | None |
| `--not main` | Works: log shows commits since fork from main | Works: branch forked from main at same point | None |
| On failure | Raise before cherry-pick | Raise before merge | None |
| On success (empty) | No commits → no cherry-picks → proceed | No commits → merge is no-op → proceed | None |
| On success (non-empty) | commit_shas used by cherry-pick loop | commit_shas used for logging only; merge uses branch name | Strictly more conservative |
| Raise routing | Gap-1b halt / Gap-1c retry | Gap-1b halt (Gap-1c retry removed, but halt still works) | None |

The contract triggers identically on the merge path. It is actually MORE conservative under the merge model: a git-log failure blocks a merge that could succeed without needing the SHA list (the merge operates on the branch name, not individual SHAs). This is the correct conservative choice — if git-log is broken, something is wrong with the worktree's git state.

**Finding: CLOSED — composes correctly, no adjustment.**

---

## Summary — Edit Scope

| File | Lines added (est.) | Lines removed (est.) | Net |
|------|-------------------|---------------------|-----|
| `bellows.py` | ~30 | ~105 | -75 |
| `tests/test_worktree.py` | ~120 (6 new tests) | ~40 (3 deleted tests + imports) | +80 |
| `tests/test_bellows.py` | ~5 (string updates) | ~80 (deleted dead tests) | -75 |
| `tests/test_consume_verdicts.py` | ~5 (evidence string updates) | ~100 (4 deleted retry tests) | -95 |

No OPEN items remain. All 7 sections have definitive verdicts.

---

## Output Receipt
**Agent:** Bellows Systems Analyst
**Step:** 1
**Status:** Complete

### What Was Done
Produced a precise edit map + regression-test plan for the merge-ff teardown model. Seven analysis sections: (1) step-(d) consumer trace confirming REMOVE-SAFE, (2) `_create_worktree` edit map with named-branch creation + sequential-invariant fail-fast + stranded-cleanup branch deletion, (3) `_teardown_worktree` edit map with ff-only primary/no-ff fallback/merge-abort on conflict/branch-cleanup ordering/legacy-worktree migration/step-(d) removal, (4) `_retry_recoverable_teardown` removal map with caller, (5) P2 dead-code removal of `_LIFECYCLE_IGNORE_RE` and `_is_lifecycle_artifact()`, (6) 6 permanent regression tests + test-impact list for 3 test files, (7) raise-on-log-failure contract composition check confirming no adjustment needed. All findings confirmed via /tmp sandbox (4 scenarios, all confirmed).

### Files Deposited
- `knowledge/architecture/teardown-merge-model-blueprint-2026-06-05.md` — edit map + regression-test plan

### Files Created or Modified (Code)
- None (analysis-only, no source changes)

### Decisions Made
- Step-(d) copy-back: REMOVE-SAFE (zero downstream consumers confirmed across gates.py, runner.py, verdict.py)
- `_retry_recoverable_teardown`: CUT (only retries dirty-tree failures, which are dissolved by merge model; zero other callers in production)
- Raise-on-log-failure contract: composes correctly with merge semantics, no adjustment needed
- Branch-cleanup ordering: merge → worktree remove → branch -d (on success); worktree + branch persist (on conflict)
- Stranded-cleanup branch deletion: `-D` (force) because stranded cleanup is a recovery path

### Flags for CEO
- None

### Flags for Next Step
- No OPEN items — DEV may proceed
- `test_create_worktree_retries_once_on_failure` uses fully-mocked subprocess; the mocked command list must be updated to match the new `-b` flag structure
- The `test_teardown_aborts_on_cherry_pick_conflict` (→ renamed) test needs its conflict setup adjusted: under the merge model, conflicting commits on BOTH sides are required (not just worktree-commit vs main-committed-change, because ff-only would fail first and no-ff tries next)
- For sandbox tests in the 6 new regression tests, `git add .` on main after creating the worktree will pick up the `.bellows-worktrees/` subdirectory. Use `git add <specific_file>` instead of `git add .` to avoid git submodule warnings
