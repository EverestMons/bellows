# Worktree Teardown/Resume Friction Cluster — Root-Cause Diagnostic
**Date:** 2026-06-13 | **Agent:** Bellows Systems Analyst | **Plan:** diagnostic-41 | **FORWARD Rows:** 4, 5, 12, 13

---

## Section 1 — Teardown Merge Model Anatomy

### Current Landing Mechanism (post-2026-06-05 merge model)

The teardown function `_teardown_worktree` (bellows.py:1103–1238) lands worktree commits onto the project's `main` branch via **git merge** (not cherry-pick — cherry-pick was replaced by the merge model shipped in `executable-bellows-teardown-merge-model-2026-06-05`).

**Step-by-step flow:**

1. **No-op guard** (bellows.py:1110): If `wt_path == project_path` (in-place execution), return immediately.

2. **Detect main branch** (bellows.py:1114–1128): Runs `git symbolic-ref --short refs/remotes/origin/HEAD` in `project_path` to discover the default branch. Falls back to literal `"main"` on failure.

3. **Legacy worktree migration** (bellows.py:1130–1143): Verifies branch `bellows-wt/<slug>` exists via `git rev-parse --verify refs/heads/<branch>`. If absent, raises `WorktreeTeardownError` — this catches pre-merge-model detached-HEAD worktrees that cannot be merged.

4. **Collect commit SHAs** (bellows.py:1145–1166): Runs `git log --format=%H HEAD --not main` in `wt_path`. On subprocess error or non-zero return code, raises `WorktreeTeardownError` (fail-safe added 2026-06-05 to prevent silent commit loss). An empty commit list (rc=0, no output) is legitimate and proceeds.

5. **Index.lock cleanup** (bellows.py:1168–1186): Detects stale `.git/index.lock`. If >5s old, removes immediately. If fresh, waits 3s then removes if still present. Prevents lock from blocking the merge.

6. **Merge — primary (ff-only)** (bellows.py:1190–1193): `git merge --ff-only <branch_name>` with `cwd=project_path`. This is the happy path when `main` has not advanced since the worktree was forked — the branch pointer simply moves forward, no merge commit needed.

7. **Merge — fallback (no-ff)** (bellows.py:1196–1200): On ff-only failure (main advanced), falls back to `git merge --no-ff -m "Merge branch '<branch>'" <branch_name>`. Creates a merge commit preserving worktree SHAs as parents.

8. **Merge conflict → abort + raise** (bellows.py:1201–1209): If the no-ff merge also fails (true content conflict or dirty-tree overlap), runs `git merge --abort` and raises `WorktreeTeardownError`. The error propagates to the caller, which records a `worktree_teardown` gate failure in the verdict request.

9. **Worktree removal** (bellows.py:1211–1227): `git worktree remove --force`, with `shutil.rmtree` fallback.

10. **Branch cleanup** (bellows.py:1229–1236): `git branch -d <branch_name>` (safe: branch is fully merged).

### Dirty-Tree Precheck: Removed

The original dirty-tree precheck (`executable-worktree-teardown-dirty-tree-precheck-2026-05-27`) ran `git status --porcelain` on `project_path` before cherry-picking and raised `WorktreeTeardownError` on any uncommitted changes. This was **removed by the merge model plan** (P2 of `executable-bellows-teardown-merge-model-2026-06-05`), which stated "Dirty scope becomes irrelevant to landing."

**Verification:** No `git status --porcelain` call exists within `_teardown_worktree` in the current code. The only `--porcelain` call in bellows.py is in `_auto_stage_deposits` (bellows.py:1037), which operates on the worktree, not on main.

### Failure Path on Merge Conflict

When the merge fails at step 8 (bellows.py:1201–1209):
- `git merge --abort` is called (bellows.py:1203–1206)
- `WorktreeTeardownError` is raised with the merge stderr
- The **worktree and branch are left alive** for manual resolution (steps 9–10 are skipped)
- The caller appends `{"gate": "worktree_teardown", "evidence": str(e)}` to gate failures (bellows.py:626, 736, 768)
- The plan transitions to `verdict-pending-*` with a `gate_failure` pause reason
- On subsequent "continue" verdict, Gap 1b (bellows.py:1592) blocks advancement and routes to `halted-*`

### Conflict-Prone Files

Files most likely to cause merge conflicts are **append-only project-wide bookkeeping files** that every plan touches:
- `PROJECT_STATUS.md` — updated by agents to record plan outcomes
- `knowledge/research/agent-prompt-feedback.md` — prompt feedback log
- `knowledge/FORWARD.md` — forward register (row additions)
- `knowledge/BACKLOG-ARCHIVE.md` — backlog archive entries
- `knowledge/LESSONS.md` — lessons learned entries

These files are conflict-prone because:
1. **Every plan appends to EOF** — two parallel plans forked from the same base both add at the same insertion point, which git's 3-way merge treats as a conflict.
2. **No structural merge driver** — git uses textual merge, which cannot reason about the semantic "append" intent.
3. **Cross-plan scope** — unlike code files (scoped to one plan's domain), these files are project-wide and touched by every plan execution regardless of scope.

---

## Section 2 — Resume Worktree Re-Creation Anatomy

### Resume Path Trace

When a CEO issues a "continue" verdict for a non-final step, the code path is:

1. **Verdict consumption** (bellows.py:1587–1656): `_consume_verdicts` finds the resolved verdict file, matches it to a `verdict-pending-*` plan, and determines the next step:
   - If `precondition_failure_from_request` is True → `next_step = step_number` (retry same step)
   - Otherwise → `next_step = step_number + 1` (advance)

2. **Gap 1b guard** (bellows.py:1592–1608): Before dispatching, checks if the prior step's verdict request contained a `worktree_teardown` gate failure. If so, blocks the continue verdict and routes the plan to `halted-*`. This prevents advancing on top of un-landed commits.

3. **Rename + dispatch** (bellows.py:1645–1656): Renames `verdict-pending-*` → `in-progress-*`, then calls `self.handle_new_plan(inprogress_path, resume_step=next_step)`.

4. **Thread spawn** (bellows.py:1436–1439): `handle_new_plan` spawns a thread that calls `run_plan(path, ..., resume_step=next_step)`.

5. **Worktree creation** (bellows.py:514–516, delegated to bellows.py:893–1000): `run_plan` calls `_create_worktree(project_path, plan_slug)`.

### `_create_worktree` on Resume (bellows.py:893–1000)

**Key line (bellows.py:985):**
```python
cmd = ["git", "--no-pager", "worktree", "add", wt_path, "-b", branch_name, "HEAD"]
```

The worktree is **always created from `HEAD`** — which is `main`'s current tip in `project_path`.

**This is the Row 12 question — definitive answer:**

In the current merge-model architecture, this is **correct behavior**, not a bug:
- **Teardown of the prior step merged its branch into main** (Section 1, steps 6–7). The prior step's commits are now part of `main`.
- `HEAD` in `project_path` points to the post-merge `main`, which **includes all prior step's work**.
- The new worktree therefore starts with the prior step's work as its base.

**Pre-merge-model (when Row 12 was filed, 2026-05-30):** The old cherry-pick model could fail, leaving commits un-landed on main. The worktree was also created detached (`HEAD --detach`) rather than on a named branch. This combination meant the resumed worktree lacked the prior step's work.

### Stranded Worktree Cleanup on Re-Creation (bellows.py:912–969)

If a worktree directory exists at `wt_path` when `_create_worktree` runs (stranded from a prior failed dispatch or daemon crash):

1. **Preserve un-landed commits** (bellows.py:916–946, Gap 2a shipped 2026-06-01): Checks if `wt_head` is an ancestor of `main`. If not (un-landed), creates branch `bellows-preserved/<slug>-<utc-ts>` pointing at the worktree HEAD.

2. **Force-remove worktree** (bellows.py:947–961): `git worktree remove --force`, `shutil.rmtree`, `git worktree prune`.

3. **Delete named branch** (bellows.py:962–969): `git branch -D bellows-wt/<slug>`.

4. **Proceed to create new worktree from HEAD** (bellows.py:984–985).

### Where Prior Step's Commits Live Between Steps

| Phase | Location |
|---|---|
| During step execution | On branch `bellows-wt/<slug>` in the worktree at `wt_path` |
| After successful teardown | Merged into `main` (branch deleted) |
| After failed teardown | Still on branch `bellows-wt/<slug>` (worktree + branch left alive) |
| After daemon restart with stranded worktree | Preserved on `bellows-preserved/<slug>-<ts>` (if un-landed); original worktree destroyed |

---

## Section 3 — Per-Row Root Cause

### Row 4 — Teardown cherry-pick conflict on dirty `PROJECT_STATUS.md`

**Status: PARTIALLY RESOLVED by merge model.**

**Original mechanism (2026-05-22):** The old cherry-pick model ran `git cherry-pick <sha>` in `project_path`. If `project_path` had uncommitted edits to any file also touched by the cherry-picked commit (e.g., `PROJECT_STATUS.md`), git refused with "Your local changes would be overwritten by merge." The dirty-tree precheck was added (`executable-worktree-teardown-dirty-tree-precheck-2026-05-27`) to detect this before cherry-picking and provide a clear error.

**Current state (post merge model):** Cherry-pick is gone. The merge (bellows.py:1190–1200) runs `git merge --ff-only` then `--no-ff` fallback. Dirty-tree precheck is removed (P2 of merge model plan). However, **`git merge` also fails on a dirty tree when the dirty files overlap with files changed on the merge source branch.** The failure manifests at bellows.py:1201 → merge --abort → `WorktreeTeardownError`.

**Resolution surface:** The cherry-pick-specific failure mode (which was sensitive to ANY dirty file regardless of overlap) is eliminated. The merge-model failure is narrower — only overlapping dirty files cause a conflict. For the specific Row 4 scenario (Planner edits `PROJECT_STATUS.md`, agent also appends to it), the conflict still occurs. For cases where dirty files don't overlap with the worktree's changes, the merge succeeds silently.

**Evidence:** bellows.py:1201–1209 (merge conflict abort path). No dirty-tree precheck exists to catch this earlier.

### Row 5 — Parallel-diagnostic cherry-pick conflicts on shared append-only files

**Status: PARTIALLY RESOLVED by merge model.**

**Original mechanism (2026-05-22):** Two parallel plans in the same project both modified `PROJECT_STATUS.md` and `agent-prompt-feedback.md`. The first teardown cherry-picked cleanly. The second hit cherry-pick conflicts because those files had been modified by the first cherry-pick.

**Current state (post merge model):** The first plan's teardown merges via ff-only (main hasn't advanced). This works. The second plan's worktree was forked from the same main HEAD as the first. When it tries to merge, ff-only fails (main advanced). The `--no-ff` fallback attempts a 3-way merge. For append-only files where both branches added at EOF:
- Git's 3-way merge sees the base (original EOF), left (first plan's additions), and right (second plan's additions)
- **If both additions start at the exact same line (EOF of the base), git treats this as a conflict** — both sides modified the same region
- Git cannot auto-resolve "both sides added different content at the same insertion point"

**Residual conflict surface:** Parallel plans that both append to the same project-wide files will still conflict at merge time. The conflict is structural: two independent additions to the same insertion point in a text file.

**Evidence:** bellows.py:1196–1200 (no-ff fallback) → bellows.py:1201–1209 (conflict abort). BACKLOG-ARCHIVE.md Row 5 entry: "Any two parallel plans within a project conflict at teardown regardless of code overlap."

### Row 12 — Worktree re-creation on resume checks out main HEAD, not the step's branch

**Status: RESOLVED by merge model.**

**Original mechanism (2026-05-30):** Pre-merge-model, teardown cherry-picked commits (which could fail), and worktrees were created detached. On daemon restart during a verdict pause, the worktree was destroyed by stranded-cleanup, and re-creation started from main HEAD — which lacked the prior step's un-landed commits.

**Current state (post merge model):** The normal verdict-resume path (bellows.py:1587–1656) is now safe:
1. The prior step's teardown MERGED its branch into main (bellows.py:1190–1200)
2. If teardown failed, Gap 1b (bellows.py:1592) blocks the continue verdict → plan halts
3. If teardown succeeded, main HEAD includes prior step's work → new worktree from HEAD has the correct base

**The daemon-restart scenario** is also covered:
1. If teardown succeeded before the restart → commits on main → resume is safe
2. If teardown failed before the restart → verdict request has `worktree_teardown` failure → Gap 1b blocks continue → halted
3. If the daemon crashed DURING step execution (before teardown) → the plan stays `in-progress-*`, which is not re-dispatched by the rescan (`is_runnable_plan` returns False for `in-progress-*` prefix) → manual intervention required (this is the separate BACKLOG #5 step-state-persistence issue, not in scope)

**Evidence:** bellows.py:985 (`HEAD` is main, post-merge), bellows.py:1190–1200 (merge lands work on main), bellows.py:1592 (Gap 1b guard).

### Row 13 — Auto-resume-from-branch + auto-stash (deferred friction-reduction)

**Status: PARTIALLY SUBSUMED by merge model.**

Row 13 covered three remaining gaps from the teardown/resume regression family:

| Gap | Description | Current Status |
|---|---|---|
| Gap 2b | Auto-resume from prior step's branch on re-creation | **Subsumed** — merge model lands commits on main; resume from HEAD is correct |
| Gap 2c | Auto-detect and incorporate preservation branches on resume | **Subsumed** — with merge model, preservation branches are a backstop for abnormal paths; Gap 1b blocks advancement before they matter |
| Gap 3 | Auto-stash dirty main before teardown | **Still open** — dirty files on main still block `git merge`; no auto-stash exists |

**Does fixing Row 12 dissolve Row 13?** Partially. Gap 2b/2c are subsumed because the merge model makes "resume from main HEAD" the correct behavior. Gap 3 (auto-stash) remains independently useful as friction-reduction for the dirty-tree merge conflict scenario (Row 4's residual surface).

**Does an append-only-merge strategy fix both Row 4 and Row 5?** Yes, if implemented broadly: a custom merge driver or pre-merge stash-and-reapply for known append-only files would dissolve both the dirty-tree overlap (Row 4) and the parallel append conflict (Row 5). However, these are different mechanisms — Row 4 is uncommitted-vs-merge, Row 5 is branch-vs-branch.

---

## Section 4 — Fix Shapes

### Problem Cluster A: Append-Only File Merge Conflicts (Rows 4 + 5)

These share a root cause: append-only project-wide files that are modified by both the merge source (worktree branch) and the merge target (main's working tree or another merged branch).

#### Option A1: Pre-merge stash of dirty main + union merge driver for append-only files

**Mechanism:** Before the merge (bellows.py:1188, before step (c)):
1. Run `git stash push --keep-index` in `project_path` if `git status --porcelain` shows dirty files
2. Run the merge (ff-only then no-ff fallback)
3. `git stash pop` after merge
4. Register a `.gitattributes` merge driver (`merge=union`) for known append-only files

**Blast radius:** bellows.py:1188–1210 (insert stash logic around merge), project `.gitattributes` (add union merge driver entries).

**Pros:** Handles both Row 4 (stash resolves dirty-tree overlap) and Row 5 (union driver auto-resolves parallel appends). Union merge concatenates both sides' additions without conflict markers.

**Cons:** Union merge is **content-unaware** — it could produce duplicate entries or disordered content in non-append-only files if misconfigured. Requires maintaining a list of union-merge files. `git stash` can itself conflict on pop if the merge changed stashed files.

**Test strategy:** (1) Create worktree with append to `agent-prompt-feedback.md`, add uncommitted edit to same file on main, verify teardown succeeds with stash. (2) Create two parallel worktrees both appending to same file, verify sequential teardown succeeds with union merge. (3) Verify stash pop conflict handling when merge changes stashed file.

#### Option A2: Pre-merge auto-commit of dirty main files

**Mechanism:** Before the merge (bellows.py:1188):
1. Run `git status --porcelain` in `project_path`
2. If dirty files exist, `git add -A && git commit -m "bellows: auto-commit dirty main before teardown merge"`
3. Proceed with merge (which now operates on a clean tree)

**Blast radius:** bellows.py:1188–1190 (insert auto-commit before merge).

**Pros:** Completely eliminates dirty-tree as a failure class. Simple implementation. No custom merge drivers needed.

**Cons:** Creates potentially unwanted commits on main from Planner-side work-in-progress. Does NOT address Row 5 (parallel branch-vs-branch conflicts on append-only files). May surprise the CEO by committing incomplete edits.

**Test strategy:** (1) Add uncommitted `PROJECT_STATUS.md` edit on main, verify auto-commit + merge. (2) Verify auto-commit message is identifiable for later cleanup.

#### Option A3: Teach teardown to detect and union-merge append-only files on conflict

**Mechanism:** After merge conflict abort (bellows.py:1203–1206):
1. Parse `git diff --name-only --diff-filter=U` to get conflicting files
2. For files on a known append-only list, resolve by concatenating both sides' additions
3. `git add` resolved files and retry merge commit
4. If non-append-only files conflict, raise as before

**Blast radius:** bellows.py:1203–1210 (replace immediate raise with conflict-resolution attempt).

**Pros:** Targeted: only auto-resolves known-safe append-only files. Doesn't require `.gitattributes` changes. Handles both Row 4 (after stashing uncommitted changes) and Row 5 (branch-vs-branch).

**Cons:** Significant implementation complexity. Requires a robust append-only detection heuristic. Still needs dirty-tree stash for Row 4.

**Recommendation for Cluster A:** **Option A1** (pre-merge stash + union merge driver). It's the cleanest solution that addresses both rows. The union merge driver is a well-understood git feature for append-only files. The stash handles the dirty-tree case. The append-only file list is small and stable (PROJECT_STATUS.md, agent-prompt-feedback.md, FORWARD.md, BACKLOG-ARCHIVE.md, LESSONS.md).

### Problem Cluster B: Resume Base (Row 12)

#### Option B1: No-op (already resolved)

**Mechanism:** The merge model's teardown lands commits on main. Resume creates worktree from HEAD (main), which includes prior step's work. Gap 1b blocks advancement on teardown failure.

**Blast radius:** None — no code change needed.

**Pros:** Zero risk. The architecture already handles this correctly.

**Cons:** None identified.

#### Option B2: Create resumed worktree from prior step's branch instead of HEAD

**Mechanism:** Modify `_create_worktree` to accept an optional `from_ref` parameter. On resume, pass the prior step's branch name.

**Blast radius:** bellows.py:893 (signature change), bellows.py:985 (use `from_ref` instead of `HEAD`), bellows.py:516 (pass `from_ref` on resume).

**Pros:** Explicitly uses the prior step's branch, making the intent clear.

**Cons:** The prior step's branch is deleted after successful teardown (bellows.py:1229–1236). Would require keeping the branch alive across steps, complicating cleanup. The merge model already makes this unnecessary.

**Recommendation for Cluster B:** **Option B1** (no-op). Row 12 is resolved by the merge model. No code change needed. Close the FORWARD row with "closed-by-merge-model" disposition.

### Problem Cluster C: Row 13 Friction-Reduction

#### Option C1: Implement Gap 3 auto-stash only (subsume into Cluster A fix)

**Mechanism:** The auto-stash from Option A1 IS Gap 3. Implementing Cluster A's fix inherently delivers Row 13's remaining Gap 3.

**Blast radius:** Same as Option A1.

**Pros:** No separate work item needed.

**Cons:** None — it's the same work.

#### Option C2: Keep Row 13 open as separate tracking item

**Mechanism:** No code change. Row 13 stays open to track any residual friction after Cluster A ships.

**Blast radius:** None.

**Pros:** Preserves tracking granularity.

**Cons:** Redundant if Cluster A fully addresses it.

**Recommendation for Cluster C:** **Option C1** — close Row 13 as subsumed by the Cluster A fix (Option A1). Gap 2b/2c are subsumed by the merge model. Gap 3 is delivered by Option A1's pre-merge stash.

### Executable Count Recommendation

**One executable** for Cluster A (pre-merge stash + union merge driver for append-only files), closing Rows 4, 5, and 13. Row 12 closes as a FORWARD annotation (resolved by shipped merge model, no code change needed).

---

## Section 5 — Gap Assessment + Verification Blocks

### Gap Assessment

| Gap | Current State (file:line) | Proposed State | Change Required |
|---|---|---|---|
| Dirty-tree blocks merge (Row 4) | No precheck; merge fails on dirty+overlapping files; `WorktreeTeardownError` raised (bellows.py:1201–1209) | Pre-merge stash of dirty main; merge operates on clean tree; stash popped after merge | Insert stash/pop around merge block (bellows.py:1188–1210) |
| Parallel append-only conflicts (Row 5) | 3-way merge conflict on concurrent EOF appends; `WorktreeTeardownError` raised (bellows.py:1201–1209) | Union merge driver registered for known append-only files; git auto-resolves concurrent appends | Add `.gitattributes` entries for append-only files; verify union merge behavior |
| Resume base uses main HEAD (Row 12) | `_create_worktree` creates from `HEAD` (bellows.py:985); teardown merges prior step to main (bellows.py:1190–1200); Gap 1b guards failed teardown (bellows.py:1592) | No change — current behavior is correct post-merge-model | None (close FORWARD row) |
| Auto-stash on dirty main (Row 13 Gap 3) | No auto-stash exists; dirty main blocks merge | Pre-merge stash (same as Row 4 fix) | Same as Row 4 change |
| Auto-resume-from-branch (Row 13 Gap 2b/c) | Not implemented; not needed post-merge-model | No change — subsumed by merge model | None (close as subsumed) |

### Verification Blocks

```
Claim: Teardown landing mechanism is git merge (not cherry-pick)
Query: grep -n "cherry-pick\|merge" bellows.py | grep -i "_teardown_worktree" -A 50
Expected: Lines 1190-1200 show `git merge --ff-only` and `git merge --no-ff` commands; no `cherry-pick` commands in _teardown_worktree
```

```
Claim: Resume worktree is created from HEAD (main tip, which includes prior step's merged work)
Query: Read bellows.py:985
Expected: cmd = ["git", "--no-pager", "worktree", "add", wt_path, "-b", branch_name, "HEAD"]
```

```
Claim: Conflict-prone files are append-only project-wide bookkeeping files
Query: grep -rn "PROJECT_STATUS\|agent-prompt-feedback\|FORWARD\|BACKLOG-ARCHIVE\|LESSONS" in worktree teardown failure verdict-request files
Expected: These file names appear in worktree_teardown gate failure evidence strings from historical incidents
```

```
Claim: Row 12 is subsumed by merge model — Gap 1b prevents advancement on failed teardown
Query: Read bellows.py:1592
Expected: `if any(f.get("gate") == "worktree_teardown" for f in gate_result.get("failures", [])):`
```

```
Claim: Dirty-tree precheck was removed (no porcelain check in _teardown_worktree)
Query: grep -n "porcelain" bellows.py
Expected: Only match is in _auto_stage_deposits (line ~1037), not in _teardown_worktree
```

```
Claim: Row 13 Gap 2b/2c subsumed by merge model
Query: Read bellows.py:1190-1200 (teardown merges to main) + bellows.py:985 (resume from HEAD)
Expected: Teardown lands on main → resume from HEAD includes prior work → auto-resume-from-branch unnecessary
```

### CEO Decision Forks

1. **Fix shape for Cluster A (Rows 4 + 5 + Row 13 Gap 3):**
   - **Option A1** (recommended): Pre-merge stash + `.gitattributes` union merge driver for append-only files. Single mechanism addresses all three remaining gaps.
   - **Option A2** (alternative): Pre-merge auto-commit of dirty main. Simpler but doesn't address Row 5 and may create unwanted commits.
   - **Option A3** (alternative): Post-conflict union-merge resolution for append-only files. Most targeted but most complex.

2. **Row 12 disposition:**
   - **Recommendation:** Close as resolved-by-merge-model. No code change needed. The current architecture correctly creates resumed worktrees from main HEAD (which includes prior step's merged work), guarded by Gap 1b on teardown failure.

3. **Executable count:**
   - **Recommendation:** One executable for Cluster A (stash + union driver), closing Rows 4, 5, 13. Row 12 closes via FORWARD annotation only.
   - **Alternative:** Two executables — one for stash (Rows 4 + 13), one for union driver (Row 5). Enables independent shipping but adds dispatch overhead for a small blast radius.

4. **Row 13 disposition after Cluster A ships:**
   - **Recommendation:** Close as subsumed. Gap 2b/2c → merge model. Gap 3 → Cluster A's stash. No residual work remains.

---

## Output Receipt
**Agent:** Bellows Systems Analyst
**Step:** 1 (SA diagnostic)
**Status:** Complete

### What Was Done
Root-cause diagnostic of the worktree teardown/resume friction cluster (FORWARD rows 4, 5, 12, 13). Traced the current merge-model teardown mechanism, resume worktree re-creation path, and per-row root causes against the shipped merge model. Identified that Row 12 is fully resolved, Rows 4 and 5 retain a residual merge-conflict surface for append-only files, and Row 13 is partially subsumed.

### Files Deposited
- `knowledge/research/worktree-teardown-resume-cluster-2026-06-13.md` — full root-cause diagnostic with fix shapes and CEO decision forks

### Files Created or Modified (Code)
- None (investigation only)

### Decisions Made
- Row 12 assessed as resolved by shipped merge model (within SA authority to assess architecture state)
- Row 13 Gap 2b/2c assessed as subsumed by merge model

### Flags for CEO
- Decision fork: fix shape for Cluster A (Option A1 recommended — pre-merge stash + union driver)
- Decision fork: Row 12 disposition (recommend close-as-resolved)
- Decision fork: one executable vs two for Cluster A

### Flags for Next Step
- If CEO selects Option A1: implementation needs append-only file list (5 files identified), stash insertion point at bellows.py:1188, `.gitattributes` union merge entries, and test fixtures for dirty-tree + parallel append scenarios
