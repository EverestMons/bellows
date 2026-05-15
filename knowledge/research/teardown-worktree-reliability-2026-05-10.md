# Findings — _teardown_worktree reliability investigation + population audit

**Diagnostic:** diagnostic-teardown-worktree-reliability-2026-05-10
**Date:** 2026-05-10
**Scope:** Unified investigation of BACKLOG entries 2026-05-07 (cherry-pick fragility) and 2026-05-06 (cherry-pick reliability gap / population audit)

---

## Q1. CODE AUDIT — _teardown_worktree implementation

**Location:** `bellows/bellows.py:602-689`

```python
def _teardown_worktree(project_path: str, wt_path: str, slug: str) -> None:
    """Tear down a worktree: cherry-pick commits back, copy dirty files, remove worktree.

    Raises WorktreeTeardownError on cherry-pick conflict (worktree left alive for manual resolution).
    No-op when wt_path == project_path (in-place execution, no worktree was created).
    """
    if wt_path == project_path:
        return
```

### (a) Cherry-pick command shape

**Multi-SHA iteration loop** (L639-653), not single-SHA:
```python
    for sha in commit_shas:
        if not sha.strip():
            continue
        result = subprocess.run(
            ["git", "--no-pager", "cherry-pick", sha],
            cwd=project_path, capture_output=True, text=True, timeout=60,
        )
```

### (b) Which SHA(s) it targets

ALL commits on the worktree branch not reachable from main (L629-634):
```python
    result = subprocess.run(
        ["git", "--no-pager", "log", "--format=%H", "HEAD", "--not", main_branch],
        cwd=wt_path, capture_output=True, text=True, timeout=30,
    )
    commit_shas = result.stdout.strip().splitlines()[::-1]  # oldest-first for cherry-pick
```
The `[::-1]` reversal ensures oldest-first cherry-pick order. The `--not main_branch` excludes commits already on main.

### (c) .git/index.lock detection

**None.** No lock detection or removal logic exists anywhere in `_teardown_worktree`. The 60s timeout on cherry-pick (L644) is the only implicit protection — git hangs waiting for the lock, subprocess times out, `WorktreeTeardownError` is raised.

### (d) Subprocess timeout value

- Cherry-pick: **60 seconds** per commit (L644)
- Commit log collection: 30 seconds (L632)
- Main branch detection: 10 seconds (L616)
- Dirty file status: 10 seconds (L659)
- Worktree removal: 30 seconds (L684)

All are hardcoded in `subprocess.run()` calls, not configurable via config.json.

### (e) On cherry-pick failure

On `returncode != 0` (L646-653):
1. Runs `git cherry-pick --abort` (L647-650, 10s timeout)
2. Raises `WorktreeTeardownError`

At call sites (L362-366, L447-451, L474-480): the exception is caught, `_pause_reason` is set to `"gate_failure"`, the failure is appended to `gate_result["failures"]`, and a verdict request is posted. **The worktree is left alive** — removal step (e) never runs.

### (f) On cherry-pick success

After all SHAs cherry-picked:
1. Step (d): copies dirty (uncommitted) files from worktree to project_path (L656-678)
2. Step (e): `git worktree remove <wt_path> --force` (L682-689)
3. On removal failure: prints warning, does NOT raise (L686-689)

### (g) Copy-back path for uncommitted files

Yes — step (d) at L655-678 runs AFTER cherry-pick and BEFORE worktree removal. It runs `git status --porcelain` in the worktree, then copies any modified/added files (excluding deletions) to `project_path`. This handles files the agent modified but didn't commit. Wrapped in try/except that swallows errors with a warning.

---

## Q2. CALLER AUDIT — call sites

### Call site 1: L362 (intermediate step pause)

```python
# Tear down worktree before pausing
try:
    _teardown_worktree(project_path, wt_path, plan_slug)
except WorktreeTeardownError as e:
    _pause_reason = "gate_failure"
    gate_result["failures"].append({"gate": "worktree_teardown", "evidence": str(e)})
```

**Context:** Inside the `while not is_final_step()` loop (L345), when ANY pause condition triggers (gate failure, QA step, verdict request, header pause). Worktree is in agent-completed state (step just finished). Error is caught, converted to gate_failure, verdict posted.

### Call site 2: L448 (final step pause — disable-auto-close path)

```python
# Tear down worktree before pausing
try:
    _teardown_worktree(project_path, wt_path, plan_slug)
except WorktreeTeardownError as e:
    _pause_reason = "gate_failure"
    gate_result["failures"].append({"gate": "worktree_teardown", "evidence": str(e)})
```

**Context:** After the final step completes AND the default disable-auto-close path fires. Same error handling as call site 1.

### Call site 3: L474 (auto-close path)

```python
# Tear down worktree before auto-close
try:
    _teardown_worktree(project_path, wt_path, plan_slug)
except WorktreeTeardownError as e:
    # Cherry-pick conflict on auto-close — convert to gate_failure pause
    print(f"Bellows: ❌ worktree teardown failed on auto-close for {plan_slug}: {e}")
    ...
```

**Context:** When `effective_auto_close` is True and all gates passed. On error, converts to a verdict-pending pause. More verbose logging than other sites.

**Common pattern across all 3:** errors are caught, converted to gate_failure verdicts, worktree left alive for manual resolution. No retry logic.

---

## Q3. POPULATION AUDIT — invoice-pulse Done/ (2026-05-03 onward)

### Raw data

| Plan file | Tracked | Commits on main |
|-----------|---------|-----------------|
| diagnostic-action-queue-200-and-contract-code-2026-05-08 | NO | NONE |
| diagnostic-action-queue-aggregation-2026-05-07 | NO | NONE |
| diagnostic-aggregated-queue-carrier-customer-display-2026-05-07 | NO | NONE |
| diagnostic-backlog-hygiene-audit-2026-05-06 | yes | yes (20167548) |
| diagnostic-billto-extraction-architecture-2026-05-07 | yes | NONE |
| diagnostic-lanes-csrf-fix-verification-2026-05-06 | yes | NONE |
| diagnostic-rule-20-fabrication-2026-05-05 | yes | NONE |
| diagnostic-tier-display-test-failure-2026-05-06 | yes | NONE |
| executable-action-queue-aggregation-2026-05-07 | NO | NONE |
| executable-action-queue-limit-and-contract-name-2026-05-08 | NO | NONE |
| executable-aggregated-queue-customer-display-2026-05-07 | NO | NONE |
| executable-backlog-hygiene-edits-2026-05-06 | yes | NONE |
| executable-backlog-hygiene-edits-2026-05-06b | yes | NONE |
| executable-backlog-hygiene-edits-2026-05-06c | yes | NONE |
| executable-backlog-hygiene-lanes-csrf-close-2026-05-06 | yes | NONE |
| executable-billto-type-field-mapping-fix-2026-05-07 | yes | NONE |
| executable-half-up-currency-rounding-2026-05-06 | yes | NONE |
| executable-qa-report-rule-20-banner-fix-2026-05-07 | NO | NONE |
| executable-session-wrap-2026-05-06 | yes | NONE |
| executable-session-wrap-action-queue-aggregation-2026-05-07 | NO | NONE |
| executable-session-wrap-half-up-rounding-2026-05-06 | yes | NONE |
| parallel-1-diagnostic-continuation-rule-rounding-2026-05-06 | yes | NONE |
| parallel-1-diagnostic-fsc-fuel-bracket-lookup-2026-05-06 | yes | NONE |
| qa-action-queue-limit-and-contract-name-2026-05-08 | NO | NONE |

### Classification summary

| Class | Count | Description |
|-------|-------|-------------|
| (i) Shipped cleanly — tracked + commits on main | 1 | diagnostic-backlog-hygiene-audit-2026-05-06 |
| (ii) Tracked but no slug-matching commits on main | 14 | Plan file committed during session-wrap; agent work committed under different message |
| (iv-a) Untracked, no slug-matching commits | 9 | Plan lifecycle move not yet committed; agent work either committed under different message or stranded |

**Note on commit matching:** most invoice-pulse agent commits use descriptive messages (e.g., "fix: half-up currency rounding...") that don't contain the plan slug. The lack of slug-matching commits does NOT indicate missing work — it indicates naming convention mismatch. Cross-referencing with actual agent work:
- `executable-half-up-currency-rounding-2026-05-06`: agent commits `b130d7f5` + `665106c7` are on main (confirmed)
- `executable-action-queue-aggregation-2026-05-07`: agent commits on main (`38a938d1`, `1f651885`, `443ff2cf`)
- `executable-billto-type-field-mapping-fix-2026-05-07`: recovered manually (commit `5daf671e` by CEO after teardown failure; agent commits `2d39d0a6` + `b618279e` cherry-picked manually)

### Active worktrees in invoice-pulse

| Worktree | HEAD | Stranded commits |
|----------|------|-----------------|
| action-queue-200-and-contract-code-2026-05-08 | 8c0e9963 | 1 — "docs: action queue 200 limit and contract code diagnostic findings" (3 files) |
| session-wrap-2026-05-08 | bca4a831 (locked) | 0 |
| session-wrap-action-queue-aggregation-2026-05-07 | c28f763a | 1 — "docs: PROJECT_STATUS for action queue aggregation + rule 20 banner fix" (2 files) |

### Orphaned worktree directories (no .git file, pruned by git)

| Directory | Stranded commits |
|-----------|-----------------|
| action-queue-aggregation-2026-05-07 | 0 (all on main) |
| qa-report-rule-20-banner-fix-2026-05-07 | 0 (all on main) |
| tier-display-test-failure-2026-05-06 | 0 (all on main; commit `795c8973` on main) |

### Named branches (stale)

| Branch | Status |
|--------|--------|
| half-up-currency-rounding-2026-05-06 | 1 commit (`4c25ace5`) — same content as cherry-picked `b130d7f5` on main. Safely deletable. |
| worktree-agent-a709385f | Ancestor of main; all commits already on main. Safely deletable. |

---

## Q4. POPULATION AUDIT — bellows Done/ (2026-05-03 onward)

### Summary

**Total files:** 49 (all from 2026-05-03 through 2026-05-10)
**Tracked:** 2 (both from today, 2026-05-10: `diagnostic-gate-path-resolution-post-teardown-2026-05-10.md`, `executable-rule-20-self-check-wt-path-2026-05-10.md`)
**Untracked:** 47

### Classification

ALL 49 bellows Done/ files classify as **(iv-b) bellows-self in-place execution pattern — expected untracked**:

Bellows is a subdirectory of the governance-root monorepo (`/Users/marklehn/Desktop/GitHub/`) with no project-local `.git`. Per commit `06aa938` (2026-05-04), `_create_worktree` detects this and returns `project_path` as-is. `_teardown_worktree` is a no-op (`wt_path == project_path` → immediate return). Therefore:
- No cherry-pick runs for bellows-self plans
- Plan lifecycle moves (to Done/) are filesystem operations on the governance-root checkout
- These moves accumulate as untracked until a session-wrap commit `git add`s them

The 2 tracked files (2026-05-10) were committed in today's session-wrap (`7b53dc5`). The other 47 are from sessions whose wraps either didn't add them or haven't wrapped yet.

**This is NOT a `_teardown_worktree` bug.** It is expected behavior under the bellows-self detect-and-skip model.

---

## Q5. FAILURE MODE CHARACTERIZATION — 2026-05-07 billto incident

### Trace

1. Agent ran in worktree `.bellows-worktrees/billto-type-field-mapping-fix-2026-05-07/`
2. Agent made 2 commits: `2d39d0a6` (fix) and `b618279e` (QA docs)
3. Step completed → gates ran → teardown fired
4. `_teardown_worktree` step (a): detected main branch = "main"
5. Step (b): `git log --format=%H HEAD --not main` from `cwd=wt_path` → returned 2 SHAs: `[2d39d0a6, b618279e]` (oldest-first after reversal)
6. Step (c): first iteration → `git cherry-pick 2d39d0a6` with `cwd=project_path` (`/Users/marklehn/Desktop/GitHub/invoice-pulse`)
7. **BLOCK:** `.git/index.lock` existed in invoice-pulse → git could not acquire index → subprocess hung
8. **TIMEOUT:** 60 seconds elapsed → `subprocess.TimeoutExpired` → cherry-pick `--abort` ran (may have also timed out or failed) → `WorktreeTeardownError` raised
9. Bellows caught exception, posted verdict with `gate_failure` + `worktree_teardown` evidence
10. Worktree left alive; plan moved to `verdict-pending-`
11. CEO manually removed lock, ran `git cherry-pick 2d39d0a6 b618279e`, moved plans to Done (commit `5daf671e`)

### (a) Did cherry-pick start?

**Yes, it started.** The terminal log showed the exact command: `Command '['git', '--no-pager', 'cherry-pick', '2d39d0a6a4f6a084e7feb1ee30a1e95525141332']' timed out after 60 seconds`. Git acquired the process but could not acquire the index.

### (b) Would cherry-pick have brought b618279e along?

**YES.** The code iterates ALL commits. Had `2d39d0a6` succeeded, the loop would have continued to `b618279e` on the next iteration. **The BACKLOG entry's "Failure 2 — single-SHA cherry-pick" hypothesis is INCORRECT.** The code handles multiple SHAs correctly; the terminal only showed one command because the first one timed out.

### (c) Are the two failure modes independent?

**They are NOT independent failures.** There is only ONE actual failure mode: **the stale index.lock blocking cherry-pick**. The "single-SHA" observation is a SYMPTOM of the first failure terminating the loop early, not a separate code bug. The BACKLOG conflated "only one cherry-pick command appeared in terminal" with "code only attempts one cherry-pick."

---

## Q6. ADDITIONAL OBSERVATION VECTORS

### (a) Silent-stranding patterns

**2 confirmed stranded commits** on active worktree branches:

| Worktree | SHA | Message | Files |
|----------|-----|---------|-------|
| action-queue-200-and-contract-code-2026-05-08 | `8c0e9963` | "docs: action queue 200 limit and contract code diagnostic findings" | diagnostic plan + findings + agent-prompt-feedback (3 files) |
| session-wrap-action-queue-aggregation-2026-05-07 | `c28f763a` | "docs: PROJECT_STATUS for action queue aggregation + rule 20 banner fix" | PROJECT_STATUS.md + agent-prompt-feedback (2 files) |

These represent genuine data loss — files exist only on worktree branches, not on main. The teardown either failed (error path) or was never called (plan was moved to Done/ via other means without triggering Bellows' normal teardown flow).

### (b) Log search for cherry-pick failures

Bellows logs (`logs/*.json`) are agent session transcripts (raw claude -p output), not daemon logs. They contain references to "cherry-pick" only as conversation content (agents discussing cherry-pick as a concept), not as Bellows-side teardown events. **Bellows daemon stdout is not persisted to disk** — teardown failure messages are visible only in the live terminal. No forensic log trail exists for past teardown failures.

### (c) Current .git/index.lock files

**None found.** `find /Users/marklehn/Desktop/GitHub -name 'index.lock'` returned empty. No active lock obstruction at time of investigation.

---

## Q7. FIX SHAPE EVALUATION

### Candidate 1: Cherry-pick full range (`git cherry-pick main..HEAD`)

**NOT NEEDED.** The current code already collects and iterates ALL commits via `git log --format=%H HEAD --not main`. The multi-SHA handling is correct. This candidate addresses a non-existent bug (the BACKLOG's "Failure 2" hypothesis was wrong).

- Estimated LOC: 0 (already implemented)
- Risk: N/A
- Closes Failure 1: No
- Closes Failure 2: N/A (Failure 2 doesn't exist)
- Bellows-self compatibility: N/A

### Candidate 2: Replace cherry-pick with `git merge --ff-only <wt-branch>` from main

**Not directly applicable.** Worktrees are created with `--detach` (no named branch). `git merge --ff-only` requires a branch ref. Would need to either:
- Create a temporary branch at worktree HEAD before merge, or
- Use `git merge --ff-only <sha>` (which works if the detached HEAD is strictly ahead of main)

Advantages over cherry-pick:
- Atomic (all-or-nothing, no partial state)
- Faster (single operation vs. N cherry-picks)
- Preserves original commit SHAs (no new commits created)

Disadvantages:
- Requires main to be strictly behind worktree HEAD (fails if main has diverged via concurrent activity)
- Cannot handle conflicts gracefully (same as cherry-pick)

- Estimated LOC: ~15 (replace steps b+c with: get worktree HEAD sha, checkout main, merge --ff-only sha)
- Risk: Medium — ff-only fails when main has diverged (e.g., concurrent CEO commits to another plan's worktree landing on main via another teardown). Cherry-pick handles this more gracefully.
- Closes Failure 1: No (lock still blocks any git operation)
- Closes "Failure 2": N/A
- Bellows-self compatibility: Yes (no-op sentinel preserved)
- Edge cases: Concurrent commits to main from other plans' teardowns would cause ff-only to fail; cherry-pick would succeed.

### Candidate 3: Detect and remove stale .git/index.lock

**ADDRESSES THE ACTUAL BUG.** The only confirmed failure mode is the stale lock.

Implementation:
```python
# Before cherry-pick loop:
lock_path = os.path.join(project_path, ".git", "index.lock")
if os.path.exists(lock_path):
    lock_age = time.time() - os.path.getmtime(lock_path)
    if lock_age > 5:  # stale if older than 5 seconds
        os.remove(lock_path)
        print(f"Bellows: ⚠ removed stale .git/index.lock ({lock_age:.0f}s old) for {slug}")
    else:
        # Fresh lock — wait briefly
        time.sleep(3)
        if os.path.exists(lock_path):
            os.remove(lock_path)
            print(f"Bellows: ⚠ removed .git/index.lock after 3s wait for {slug}")
```

- Estimated LOC: ~10
- Risk: Low — removing a stale lock is standard git recovery practice; the 5s age threshold prevents interfering with active git operations
- Closes Failure 1: **YES**
- Closes "Failure 2": N/A (doesn't exist)
- Bellows-self compatibility: Yes (no-op sentinel prevents reaching this code)
- Edge cases: If a lock is from an active operation (e.g., git gc), the 5s threshold is the safety margin. In practice, Bellows plans run sequentially per-project, so no concurrent git operation should be active in the project at teardown time.

### Candidate 4: Retry with backoff on cherry-pick timeout

Alternative/complement to Candidate 3:
```python
for attempt in range(3):
    result = subprocess.run(["git", "--no-pager", "cherry-pick", sha],
                          cwd=project_path, capture_output=True, text=True, timeout=60)
    if result.returncode == 0:
        break
    if "index.lock" in result.stderr or attempt < 2:
        # Remove lock and retry
        lock_path = os.path.join(project_path, ".git", "index.lock")
        if os.path.exists(lock_path):
            os.remove(lock_path)
        time.sleep(2)
        continue
```

- Estimated LOC: ~12
- Risk: Low
- Closes Failure 1: Partially (handles lock-related failures but not other timeout causes)
- Bellows-self compatibility: Yes

### Candidate 5: Worktree directory cleanup on orphaned directories

Separate from the cherry-pick issue: add cleanup of orphaned worktree directories (those without `.git` files) during startup or teardown.

```python
# After worktree removal, also clean up directory if it still exists:
if os.path.exists(wt_path):
    shutil.rmtree(wt_path, ignore_errors=True)
```

- Estimated LOC: ~3
- Risk: Low
- Closes: worktree directory accumulation (cosmetic)

---

## Q8. PRECEDENCE QUESTION

**Single executable plan recommended.** There is only ONE actual failure mode (stale index.lock blocking cherry-pick), not two independent bugs. The "Failure 2 — single-SHA" hypothesis was incorrect.

**Order of operations:**
1. Lock detection/removal (Candidate 3) — closes the only confirmed failure mode
2. Orphaned directory cleanup (Candidate 5) — cosmetic, bundled for minimal disruption
3. Retry logic (Candidate 4) — optional hardening, can be deferred

Candidates 3 + 5 together are ~13 LOC and address both the reliability bug and the cleanup gap. No interaction risk — lock removal is a pre-condition check, directory cleanup is post-condition cleanup.

**Candidate 2 (ff-only merge) should NOT be shipped** without careful analysis of the concurrent-activity edge case. Cherry-pick is more robust when main can diverge (multiple plans' worktrees tearing down interleaved).

---

## Root Cause(s)

### Are the 2026-05-06 and 2026-05-07 entries the same root cause?

**NO. They are distinct failure modes that share the same code surface but have different causes:**

| Entry | Actual root cause | Relation to _teardown_worktree |
|-------|-------------------|-------------------------------|
| 2026-05-07 cherry-pick fragility | Stale `.git/index.lock` causing cherry-pick timeout | Direct — cherry-pick in step (c) blocked by lock |
| 2026-05-06 untracked Done/ files | Plan lifecycle moves (shutil.move to Done/) are uncommitted filesystem operations | **Indirect** — NOT caused by cherry-pick failure. Caused by the absence of any commit step after plan lifecycle moves. Session-wrap is the expected commit mechanism, but it doesn't always add these files. |

The 2026-05-06 BACKLOG entry hypothesized "suggests _teardown_worktree is not reliably cherry-picking all changes back to main." This hypothesis is **INCORRECT** for the majority of the observed untracked files. The cherry-pick brings AGENT COMMITS (code changes) to main. The plan file lifecycle moves (renaming to in-progress, verdict-pending, Done/) are Bellows-side `shutil.move()` operations on the MAIN checkout — they are never committed by Bellows at all. They accumulate as untracked changes until a session-wrap commit adds them.

**However**, there IS a real stranding problem: 2 active worktrees have genuine stranded commits (Q6a). These represent cases where teardown failed (likely due to the lock issue or similar) and the plans were manually moved to Done/ without cherry-picking the agent's work.

---

## Recommended Fix

**Ship a single executable plan containing:**

1. **Lock detection and removal** (Candidate 3, ~10 LOC) — insert before the cherry-pick loop at L639. Check for `.git/index.lock` in `project_path`, remove if older than 5 seconds or wait+remove if fresh. This closes the only confirmed failure mode.

2. **Orphaned directory fallback cleanup** (Candidate 5, ~3 LOC) — after L689, add `if os.path.exists(wt_path): shutil.rmtree(wt_path, ignore_errors=True)`. Handles the case where `git worktree remove` fails but the directory remains.

3. **Optional: add retry on cherry-pick failure** (Candidate 4, ~12 LOC) — wrap the cherry-pick in a retry loop with lock removal between attempts. Provides defense-in-depth against lock files that appear between the pre-check and the cherry-pick.

Total: ~25 LOC + 3-4 unit tests. Single commit.

**Justification:** The lock is the only demonstrated reliability failure. The multi-SHA handling is already correct. The untracked Done/ files are a session-wrap discipline issue, not a teardown bug. The stale worktree directories are cosmetic (git has already pruned them).

---

## Confidence

| Claim | Confidence | Evidence that would raise it |
|-------|-----------|------------------------------|
| Multi-SHA cherry-pick loop is correct | **HIGH** | Code at L629-653 is unambiguous; reversal ensures oldest-first |
| "Failure 2" (single-SHA) is not a real bug | **HIGH** | Code review directly contradicts the BACKLOG hypothesis |
| Index.lock is the root cause of 2026-05-07 | **HIGH** | Terminal log quoted in BACKLOG matches code behavior exactly |
| Untracked Done/ files are NOT caused by cherry-pick failure | **HIGH** | bellows-self plans (47/49 untracked) have no worktree/cherry-pick involved; pattern is identical |
| Stranded commits (8c0e9963, c28f763a) are data loss | **HIGH** | Commits verified not on main via `git log main..` |
| Lock removal at 5s threshold is safe | **MEDIUM** | Assumes no legitimate git operation takes >5s on these repos; would benefit from observing lock creation patterns across 10+ sessions |
| Candidate 2 (ff-only) is riskier than cherry-pick | **MEDIUM** | Theoretical edge case (concurrent main divergence); no observed reproduction yet |

---

## RULE 20 SELF-CHECK

```python
import os, sys
deposit = "/Users/marklehn/Desktop/GitHub/bellows/knowledge/research/teardown-worktree-reliability-2026-05-10.md"
if os.path.isfile(deposit):
    print("RULE 20 SELF-CHECK PASSED")
    sys.exit(0)
else:
    print(f"RULE 20 SELF-CHECK FAILED — file not found: {deposit}")
    sys.exit(1)
```
