# Teardown Dirty-Main Root-Cause Diagnostic — Findings

**Date:** 2026-06-05 | **Agent:** Bellows Systems Analyst | **Step:** 1 (SA)
**Diagnostic:** diagnostic-bellows-teardown-dirty-main-rootcause-2026-06-05
**Scope:** Read-only on source + sandboxed reproduction in /tmp. No Bellows source change.

---

## R0 — Patch-Accretion Audit

| Date | Fix | Failure Targeted | Recurred? |
|------|-----|-----------------|-----------|
| 2026-05-27 | Dirty-tree pre-check inserted at (b2) before cherry-pick loop; raises `WorktreeTeardownError("worktree_teardown_dirty_tree: ...")` on any non-empty `git status --porcelain` | Cryptic cherry-pick conflict when main's working tree is dirty — surfaced as generic `cherry-pick conflict on <sha>` with no indication that the root cause was dirty state, not a content conflict | **YES** — false-tripped on lifecycle artifacts (session 13, 2026-05-28); blocking predicate was too broad |
| 2026-05-28 | `_LIFECYCLE_IGNORE_RE` regex + `_is_lifecycle_artifact()` filter added; pre-check narrows to non-lifecycle paths only | False-trip on daemon-managed lifecycle artifacts (`in-progress-*`, `verdict-pending-*`, `Done/`, `verdicts/`) | **NO** — filter eliminated the lifecycle-artifact false-trip class. But the underlying dirty-main sources were not addressed. |
| 2026-05-29 | Three hardening items: (a) stranded-worktree cleanup in `_create_worktree`; (f) `.strip()` → `.rstrip()` on porcelain output to preserve leading status-code space; (g) `.bellows-worktrees/` added to `_LIFECYCLE_IGNORE_RE` | (a) teardown-stranded-worktree cascade (BACKLOG #2); (f) filter misparse on space-prefixed porcelain lines; (g) false-trip on `.bellows-worktrees/` dir entry | (a) symptom changed: pre-fix was loud `WorktreeCreationError`, post-fix was silent regression of the tree (worktree recreated from main HEAD, losing un-landed commits). Fix closed the creation-failure path but introduced silent-regression path. (f,g) NO — fixed correctly. |
| 2026-05-31 | Root-cause diagnostic of the resume-regression cascade. No code shipped — blueprint for Gaps 1b/1c/2a/2b/3a. | Continue-over-failed-teardown silently advances, `_create_worktree` stranded-cleanup destroys un-landed commits, tree regresses | Confirmed mechanism. This diagnostic did not ship code; it defined the fix shapes. |
| 2026-06-01 | Gap 1b: `_consume_verdicts` continue branch blocks when prior step carries an uncleared `worktree_teardown` failure; routes to `halted-` | Silent continue-advance over a failed teardown (Step N commits orphaned) | **NO** — correctly blocks. But the dirty-tree trigger itself was not eliminated. |
| 2026-06-04 | Gap 1c: `_retry_recoverable_teardown()` helper; retries dirty-tree-only teardown at verdict-consume time before Gap 1b halt | Dirty-tree teardown failure persisting even after CEO commits the stray file; had to halt+restart | **Partially effective** — succeeded on 2026-06-05 (anvil `backups/` case, terminal log line 105). But still requires CEO to manually identify and commit the dirty file before issuing continue. |
| 2026-06-05 | Step (b) `except Exception: commit_shas = []` → raise `WorktreeTeardownError` on git-log failure/non-zero rc | Silent loss of commits when git-log fails — bypassed cherry-pick AND worktree removal, with no recorded failure | **N/A** — data-safety fix, not a dirty-tree fix. Closes a separate silent-loss vector. |

**Conclusion: These are repeated catches of one uncut cause.** The pre-check (05-27) catches dirty state. The filter (05-28) narrows false positives. The hardening (05-29) patches filter gaps. The resume-regression diagnostic (05-31) identifies the cascade. The continue-block (06-01) and retry (06-04) handle the failure once it occurs. The raise-on-failure (06-05) closes a different silent-loss vector. None of these eliminate the sources of dirty state. The patches are defense-in-depth around a symptom; the root cause is that `_teardown_worktree` uses `git cherry-pick` with `cwd=project_path`, which requires a clean working tree to operate — and the system contains multiple writers to that working tree.

---

## R1 — Dirty-Main Source Inventory

Every distinct path by which main's working tree becomes dirty during a worktree run, grounded in code and log/verdict evidence.

### Source A: Step (d) copy-back of uncommitted worktree files

- **Mechanism:** `_teardown_worktree` step (d) (bellows.py:1011-1034) runs `git status --porcelain` on the worktree (`cwd=wt_path`), then for every dirty file, copies it from `wt_path` to `project_path` via `shutil.copy2`. This writes to main's working tree AFTER the cherry-pick but BEFORE worktree removal.
- **Example paths:** `agent-prompt-feedback.md`, `PROJECT_STATUS.md`, any scratch files the agent modified but didn't commit.
- **Tracked vs untracked:** Typically modified (` M `) if the file existed in git; untracked (`??`) if the agent created a new file in the worktree that it didn't commit.
- **Writer:** The agent (running in the worktree) creates the dirty state; Bellows step (d) propagates it to main.
- **Cherry-pick overlap:** These files are NOT in the worktree's committed changes (they're the uncommitted leftovers). So they don't overlap with the cherry-pick. But they persist on main's working tree and trip the NEXT teardown's step (b2) pre-check.
- **Evidence:** The `PROJECT_STATUS.md` dirty-tree incidents (2026-05-22 BACKLOG item, 2026-05-31 diagnostic Section "Discipline points" item 2). Also implicit in every `agent-prompt-feedback.md` modification.

### Source B: Daemon lifecycle file operations at `project_path`

- **Mechanism:** `run_plan` renames plan files in `knowledge/decisions/` via `shutil.move`: `executable-*` → `in-progress-*` (line 433), `in-progress-*` → `verdict-pending-*` (lines 473, 561, 654, 685), `verdict-pending-*` → `halted-*` (lines 421, 1450, 1506), `*` → `Done/` (lines 444, 701, 1480). `_consume_verdicts` renames verdict files in `verdicts/resolved/` → `processed-*` (lines 1521, 1545). These all operate at `project_path` (or BELLOWS_ROOT for verdicts).
- **Example paths:** `knowledge/decisions/in-progress-executable-*.md`, `knowledge/decisions/verdict-pending-*.md`, `knowledge/decisions/Done/*.md`, `verdicts/pending/verdict-request-*.md`, `verdicts/resolved/processed-verdict-*.md`.
- **Tracked vs untracked:** `??` (untracked) for new files; ` D` (deleted) for files that were moved away from their tracked location.
- **Writer:** The daemon itself (Bellows main loop and `run_plan`).
- **Cherry-pick overlap:** None — agents never commit to `knowledge/decisions/` lifecycle prefix paths or `verdicts/`. These are daemon-managed paths.
- **Filter status:** ALREADY FILTERED by `_LIFECYCLE_IGNORE_RE` (bellows.py:42-47). These do not trip the pre-check after the 05-28 filter fix.

### Source C: External concurrent writes to the project working tree

- **Mechanism:** Processes outside of the Bellows dispatch cycle write files to `project_path` during or between plan executions. The CEO, Planner, external tools, or background scripts create/modify files that are not committed.
- **Example paths:**
  - `backups/` directory in anvil project (2026-06-05, ledger entry 472: "added backups/ to .gitignore (54ad947)"). Writer: unknown external process or manual operation.
  - `bellows-speed-research-2026-05-29.md` in repo root (2026-05-31 diagnostic: "Untracked non-lifecycle file on main"). Writer: manual file creation, not committed.
- **Tracked vs untracked:** Typically `??` (untracked) for new files; ` M` for modified existing files.
- **Writer:** External to Bellows.
- **Cherry-pick overlap:** Unpredictable — depends on whether the agent's commits touch the same paths. In practice, unlikely for stray documentation files; possible for source files.

### Source D: Agent push creating local/origin commit divergence

- **Mechanism:** Per the 05-21 git-operations mapping, agents push to origin via `git push origin main` (instructed by Planner-authored plan step prose). Bellows cherry-picks the same commits onto local main. This produces parallel SHAs (content-identical, different commit hashes).
- **Does this dirty the working tree?** NO — commit divergence is a ref-level phenomenon, not a working-tree phenomenon. `git status --porcelain` does not report it. This source does NOT contribute to the dirty-tree pre-check failure.
- **Included for completeness:** The divergence is architecturally related (dual-path delivery) but orthogonal to the dirty-tree problem.

---

## R2 — Per-Source Eliminability

### Source A: Step (d) copy-back → ELIMINABLE

**Root-cause fix:** Remove or restructure step (d). The copy-back exists to preserve uncommitted agent work when the worktree is deleted. But it creates dirty state on main that trips the next teardown.

**Options:**

1. **Remove step (d) entirely.** Agents are instructed to commit their work ("Your final operation is ALWAYS the commit" — `runner.py:23`). Uncommitted files are by definition either (a) inconsequential scraps the agent chose not to commit, or (b) a bug in the agent's execution where it forgot to commit. In either case, silently copying them to main is wrong: (a) creates noise, (b) masks an agent failure. If the agent's commit is incomplete, gates should catch it (deposit_exists, scope_check, rule_22).
   - **Blast radius:** Low. The copy-back has no downstream consumers. No code reads the copy-back files. The intent was "don't lose work," but the work that matters is in the committed files (cherry-picked in step c).
   - **Risk:** If an agent legitimately modifies a file but is unable to commit it (e.g., git commit fails), that file would be lost. Mitigated by the step (b) raise-on-failure fix (06-05): if git operations fail, teardown raises and the worktree is preserved.

2. **Replace step (d) with a declared-artifact log.** Instead of copying dirty files, log them: `_log("INFO", f"worktree had uncommitted files: {dirty_list}", slug=slug)`. This preserves observability without dirtying main.

**Recommendation:** Option 1 (remove step d) is the cleanest. Option 2 is acceptable if observability is valued. Either eliminates Source A.

### Source B: Daemon lifecycle file operations → ALREADY ELIMINATED

The `_LIFECYCLE_IGNORE_RE` filter (05-28) makes these invisible to the pre-check. No further action needed.

**Classification: ELIMINATED (by filter).**

### Source C: External concurrent writes → IRREDUCIBLE (but rare)

**Root-cause fix options:**

1. **Process discipline:** Never leave stray uncommitted files in a watched project directory. This is already documented in the 05-31 diagnostic's discipline points. It's a human/process constraint, not a code fix.

2. **`.gitignore` coverage:** Files that external tools create (e.g., `backups/`) should be added to `.gitignore` so they don't appear in `git status --porcelain`. This was done for the anvil `backups/` case (commit 54ad947).

3. **Filter expansion:** Add known external-tool output paths to `_LIFECYCLE_IGNORE_RE`. But this is fragile — new tools create new paths.

**Classification: IRREDUCIBLE at the code level.** The system cannot prevent external processes from writing to the project directory. However, this source is:
- Rare (2 observed instances across a month of operation)
- Self-correcting (CEO commits or gitignores the stray file, then Gap 1c retry succeeds)
- Addressable per-instance (add to `.gitignore` or commit)

The R3 structural lever (below) dissolves this source's impact entirely.

### Source D: Agent push divergence → NOT A DIRTY-TREE SOURCE

Does not contribute to working-tree dirtiness. Orthogonal issue addressed by removing `git push` from plan step instructions (05-21 recommendation).

---

## R3 — Teardown Model: The Structural Lever

### Current model: cherry-pick onto live working tree

The current `_teardown_worktree` step (c) (bellows.py:994-1009) cherry-picks each worktree commit individually onto the main checkout with `cwd=project_path`:

```python
for sha in commit_shas:
    result = subprocess.run(
        ["git", "--no-pager", "cherry-pick", sha],
        cwd=project_path, ...
    )
```

Cherry-pick REQUIRES a clean working tree. Any dirty file on main — tracked or untracked — can cause `cherry-pick` to fail or produce misleading conflicts. This is why the dirty-tree pre-check (b2) exists: to detect the problem early and produce a clear error instead of a cryptic cherry-pick failure.

The entire dirty-tree failure class exists because the landing mechanism (cherry-pick) is sensitive to working-tree state.

### Alternative model: branch-based fast-forward merge

Replace `cherry-pick` with `git merge --ff-only`:

1. **`_create_worktree`** changes from `git worktree add <path> HEAD --detach` to `git worktree add <path> -b bellows-wt/<slug> HEAD`. The worktree runs on a named branch instead of a detached HEAD.

2. **`_teardown_worktree` step (c)** replaces the cherry-pick loop with:
   ```python
   result = subprocess.run(
       ["git", "--no-pager", "merge", "--ff-only", f"bellows-wt/{slug}"],
       cwd=project_path, ...
   )
   ```
   After merge: `git branch -d bellows-wt/{slug}` to clean up.

3. **Step (b2) dirty-tree pre-check becomes unnecessary.** `git merge --ff-only` succeeds despite dirty working-tree state (both tracked and untracked), as long as the dirty files are not in the merge's file set.

### /tmp sandbox proof

**Test 1 — dirty main, merge touches different files:**
```
/tmp/bellows-ff-test: main has dirty status.md + untracked.txt
  git merge --ff-only worktree-branch → EXIT CODE: 0
  file.txt updated, status.md preserved dirty, untracked.txt preserved
```

**Test 2 — dirty main, merge touches SAME file (overlap):**
```
/tmp/bellows-ff-test2: main has dirty file.txt, merge also touches file.txt
  git merge --ff-only worktree-branch → EXIT CODE: 1
  "Your local changes would be overwritten by merge" — clean abort, no conflict markers
```

**Test 3 — active worktree on branch during merge:**
```
/tmp/bellows-wt-merge-test: worktree still active on bellows-wt/test-slug
  git merge --ff-only bellows-wt/test-slug → EXIT CODE: 0
  Commits land correctly, dirty state preserved, worktree unaffected
```

**Test 4 — SHA identity:**
```
/tmp/bellows-sha-test: worktree SHA = 669e978, main SHA after merge = 669e978
  SHAs match: YES — no parallel-SHA divergence
```

### What this dissolves

| Problem | Cherry-pick model | Merge --ff-only model |
|---------|------------------|----------------------|
| Dirty-tree pre-check false trips | Requires `_LIFECYCLE_IGNORE_RE` filter, filter maintenance | Pre-check unnecessary — merge tolerates dirty tree |
| Source A (copy-back dirtying main) | Trips next teardown's pre-check | Irrelevant — next merge also tolerates dirty tree |
| Source C (external stray files) | Trips pre-check, requires CEO intervention | Irrelevant — merge tolerates dirty tree |
| Gap 1b/1c (continue-over-failed-teardown) | Needed because dirty-tree teardown fails | Failure class dissolved — no dirty-tree teardown failure |
| Resume-regression cascade (05-31) | Caused by dirty-tree → failed teardown → stranded worktree | Teardown succeeds despite dirty tree → no cascade |
| Parallel-SHA divergence (05-21) | Cherry-pick creates new SHAs | Merge preserves exact SHAs (test 4) |
| Overlap case (dirty file = merge file) | Cryptic cherry-pick conflict markers | Clean abort with clear error message, no markers |

### What breaks or needs migration

1. **`_create_worktree`:** Change `HEAD --detach` to `-b bellows-wt/{slug} HEAD`. ~2 lines.
2. **`_teardown_worktree` step (c):** Replace cherry-pick loop with single merge + branch delete. ~5 lines net (replacing ~15 lines).
3. **Step (b2) pre-check:** Can be removed entirely, along with `_LIFECYCLE_IGNORE_RE` and `_is_lifecycle_artifact()`. ~35 lines removed.
4. **`_retry_recoverable_teardown`:** Dirty-tree case dissolved. The function can be simplified or removed if the only failure mode it handles is dirty-tree. ~35 lines.
5. **Step (b) commit collection:** `git log --format=%H HEAD --not main` still works from the worktree — the branch has the same commits. No change needed.
6. **Step (d) copy-back:** Still works — `git status --porcelain` in the worktree still finds uncommitted files. But per R2 Source A, step (d) should be removed or replaced with logging regardless.
7. **Tests:** All tests that mock cherry-pick subprocess calls need updating. Estimate: 8-12 test fixtures.
8. **Fast-forward guarantee:** `--ff-only` fails if main has advanced since worktree creation. This requires Bellows to be single-plan-per-project (current architecture) and CEO not to manually commit to main during plan execution. Both are current invariants.

### Recommendation: REDESIGN

The merge model dissolves the entire dirty-tree failure class (pre-check, filter, retry, resume-cascade) rather than patching each dirty-main source individually. The migration cost is moderate (~50 lines changed, ~70 lines removed, ~10 tests updated). The fast-forward guarantee holds under current Bellows invariants (sequential plan execution, no concurrent main commits). The SHA-identity benefit also resolves the 05-21 parallel-SHA divergence.

**Keep-current is defensible only if:** (a) the fast-forward guarantee is at risk (concurrent plans or concurrent main commits), or (b) the test migration cost is considered too high for the current session. Neither appears to be the case.

---

## R4 — Residual + Backstop Judgment

### After R2 eliminations and R3 redesign

If the R3 merge model is adopted:
- **Source A (copy-back):** Dissolves — merge tolerates the dirty state, and step (d) should be removed/replaced per R2.
- **Source B (lifecycle):** Already filtered; merge makes filter unnecessary.
- **Source C (external writes):** Dissolves — merge tolerates the dirty state.

**The residual is empty.** No dirty-main case survives the merge model.

### The one remaining edge case

The overlap case: a dirty file on main IS ALSO modified by the merge. `git merge --ff-only` aborts cleanly with "Your local changes would be overwritten." This is:
- **Extremely rare:** Requires an external process to modify the exact same file the agent committed to. In practice, agents modify source/test files; external dirty state is typically documentation or artifacts.
- **Self-describing:** The error message names the conflicting file. No cryptic conflict markers.
- **Not a pre-check concern:** This is a legitimate conflict that should block landing. The current pre-check also blocks this (correctly). The merge model handles it with a better error message and no conflict marker residue.

This case does NOT justify auto-stash — it is a real conflict that needs human resolution, not automated stashing.

### Auto-stash evaluation

**Auto-stash is dead complexity.** With the merge model, there is no residual dirty-tree case that auto-stash would backstop.

Even under the current cherry-pick model, auto-stash is risky:

**/tmp sandbox proof of stash-pop conflict:**
```
/tmp/bellows-stash-test: stash -u (main-dirty-content in file.txt + untracked.txt)
  → cherry-pick touches file.txt
  → stash pop → CONFLICT (content): Merge conflict in file.txt
  → file.txt has <<<<<<< conflict markers
  → stash retained (not dropped)
  → EXIT CODE: 1
```

**/tmp sandbox proof of clean pop (no overlap):**
```
/tmp/bellows-stash-test2: stash -u (dirty status.md + untracked.txt)
  → cherry-pick touches ONLY file.txt
  → stash pop → clean, EXIT CODE: 0
```

**Stash -u flag analysis:**
- `-u` stashes untracked files. Required because untracked files are the most common dirty-main source (Source A copy-back, Source C stray files).
- `-a` (all, including ignored) is never appropriate — would stash `.pyc`, `__pycache__`, `.env`, etc.
- `-u` is the correct flag IF stash were used.

**Pop-conflict risk:** When a cherry-picked commit touches the same path as a stashed file, `git stash pop` produces conflict markers in the working tree and retains the stash entry (not dropped). This leaves main with conflict markers — worse than the original dirty state. The land-or-raise contract would need to detect this (check exit code, abort if non-zero, restore from stash), adding significant complexity for a scenario that the merge model eliminates entirely.

**Disposition: CUT.** Auto-stash adds complexity, has a conflict-marker risk that violates the land-or-raise contract, and solves nothing that the merge model doesn't dissolve outright.

---

## Verdict

### (1) Root-cause elimination plan (ranked)

| Priority | Source | Fix | Scope | Status |
|----------|--------|-----|-------|--------|
| **P0** | Structural: cherry-pick sensitivity to working-tree state | Replace cherry-pick with `git merge --ff-only` on named branch (R3 redesign) | `_create_worktree`, `_teardown_worktree` steps (b2), (c) | **New follow-up plan** |
| **P1** | Source A: step (d) copy-back dirtying main | Remove step (d) or replace with log-only | `_teardown_worktree` step (d) | **Bundle with P0** (same function) |
| **P2** | Filter/pre-check dead code removal | Remove `_LIFECYCLE_IGNORE_RE`, `_is_lifecycle_artifact()`, step (b2) pre-check | bellows.py:38-59, 950-992 | **Bundle with P0** (redundant after merge model) |
| **P3** | Gap 1c simplification | Simplify or remove `_retry_recoverable_teardown` — dirty-tree retry is dissolved | bellows.py:1055-1087 | **Evaluate after P0** — may still serve content-conflict retry in future |

### (2) Keep-current vs redesign: REDESIGN

The merge model (R3) dissolves the dirty-tree failure class at the structural level. Seven patches across a month caught symptoms; one structural change eliminates the cause. Migration cost is moderate. The fast-forward guarantee holds under current invariants. SHA-identity preservation also resolves the 05-21 parallel-SHA divergence as a side benefit.

### (3) Auto-stash disposition: CUT

Auto-stash has no residual to backstop after the merge redesign. Even under the current model, it introduces pop-conflict risk (conflict markers, retained stash) that violates the land-or-raise contract. It is dead complexity that should not be built.

### Open items

- **OPEN: Step (d) copy-back — are there consumers?** R2 recommends removing step (d). Before shipping, verify no downstream code reads files that step (d) copies to main. Grep for `shutil.copy2` consumers and check if any gate or verdict logic depends on uncommitted worktree files appearing on main. Preliminary evidence: no such consumers found, but a formal grep-and-trace should confirm.
- **OPEN: `_retry_recoverable_teardown` scope after redesign.** If the merge model eliminates the dirty-tree failure class, does `_retry_recoverable_teardown` serve any purpose? It currently only retries dirty-tree failures. If content-conflict retries are not needed, the entire function can be removed. If content-conflict retries are desired (CEO resolves a conflict, issues continue, retry lands the merge), the function needs restructuring.
- **OPEN: Fast-forward guarantee under concurrent execution.** The merge model requires `--ff-only` to succeed, which requires main not to have advanced since worktree creation. Current invariant: one plan per project at a time. If Bellows ever supports concurrent plans on the same project, `--ff-only` would fail for the second plan. This is a future architectural constraint, not a current blocker.

---

## Output Receipt
**Agent:** Bellows Systems Analyst
**Step:** 1
**Status:** Complete

### What Was Done
Root-cause diagnostic of the dirty-main teardown failure class. Built a patch-accretion audit (R0: 7 patches, one uncut cause), dirty-main source inventory (R1: 4 sources, 1 already filtered, 1 not a dirty-tree source), per-source eliminability analysis (R2), structural teardown model evaluation (R3: merge --ff-only dissolves the failure class), and residual/backstop judgment (R4: empty residual, auto-stash is dead complexity). All reproduction in /tmp sandbox with 4 independent scenarios.

### Files Deposited
- `knowledge/research/teardown-dirty-main-rootcause-2026-06-05.md` — this diagnostic findings file

### Files Created or Modified (Code)
- None (read-only diagnostic)

### Decisions Made
- Classified 7 teardown patches as repeated catches of one uncut cause (cherry-pick sensitivity to working-tree state)
- Identified 3 active dirty-main sources: copy-back (eliminable), lifecycle (already filtered), external writes (irreducible but dissolved by merge model)
- Recommended merge --ff-only redesign over keep-current + source-by-source patching
- Recommended auto-stash be cut (no residual to backstop, pop-conflict risk)
- Recommended step (d) copy-back be removed (Source A elimination)

### Flags for CEO
- **Redesign scope:** The merge model is a moderate refactor (~50 lines changed, ~70 lines removed, ~10 tests updated). It should be its own executable plan with full QA. Not a patch.
- **Fast-forward invariant:** The merge model requires sequential plan execution per project. If concurrent plans are ever desired, the landing model would need further evolution.

### Flags for Next Step
- The P0 follow-up plan (merge model redesign) should be authored as a Bellows executable, not a diagnostic. It modifies `_create_worktree` and `_teardown_worktree` and requires full regression testing.
- Step (d) removal (P1) should bundle with P0 since both modify `_teardown_worktree`.
- Dead code removal (P2) should also bundle — removing the pre-check, filter regex, and filter function in the same plan that eliminates their necessity.
