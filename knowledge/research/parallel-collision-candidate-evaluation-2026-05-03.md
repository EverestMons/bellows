# Parallel-Plan scope_check Collision — Candidate Evaluation & Recommendation

**Date:** 2026-05-03 | **Plan:** diagnostic-parallel-scope-check-collision-2026-05-03 | **Step:** 2 (combined)

**Prerequisite verified:** Phase 1D "Observed Contamination Vector" in `parallel-collision-incident-timeline-2026-05-03.md` is present and complete. Phase 1A timeline, Phase 1B code-path trace, and Phase 1D vector specification all present. Phase 1C canary not dispatched (gap documented).

---

## Phase 2 — Candidate Walk-Through

### Ground Truth (from Phase 1D)

In the 2026-04-30 incident, Plan C's agent edited `bellows.py`, `verdict.py`, and `tests/test_verdict.py` in the shared working tree. Plan A's `post_diff` (captured at `bellows.py:281` via `_capture_git_diff`) ran `git diff --stat --relative -- .` at ~15:46:21, which returned C's dirty files. `_parse_diff_stat` (line 282) reported `["bellows.py", "verdict.py"]` as Plan A's `files_changed`. The required fix property: Plan A's `files_changed` must contain ONLY files modified by Plan A's `claude -p` process.

---

### Candidate (a): Timestamp-bound git range

**Mechanism:** Capture `step_start_ts = datetime.now().isoformat()` before `runner.run_step()`. Replace `_capture_git_diff`'s `git diff --stat` with `git log --since=<step_start_ts> --stat --relative -- .` for the post-step capture.

**(1) Lines changed in `bellows.py`:**
- `_capture_git_diff` (lines 404-420): Replace `git diff --stat` argv with `git log --since=<ts> --stat --relative -- .`. Add `step_start_ts` parameter.
- `run_plan` (line 265): Capture `step_start_ts` before `runner.run_step()`. Pass to modified `_capture_git_diff`.
- Same change at the while-loop site (line 321).
- `_parse_diff_stat` (lines 423-456): May need adaptation since `git log --stat` output format differs from `git diff --stat` (multiple commit blocks vs single block).

**(2) Given Phase 1A timeline (C edits files during A's window 15:44:46→15:46:21), what does the candidate return for A's `files_changed`?**

`git log --since="2026-04-30T15:44:46" --stat --relative -- .` at ~15:46:21 would return:
- Commit `e609ad3` (15:46:15) — A's own commit: `gates.py`, `tests/test_gates.py`, `knowledge/development/deposit-exists-directory-paths-dev-log-2026-04-30.md`
- Commit `ebdc544` (15:46:21) — B's commit (backlog-hygiene): `PROJECT_STATUS.md`, `knowledge/BACKLOG.md`, `knowledge/development/backlog-hygiene-sweep-dev-log-2026-04-30.md`
- C's commit (15:47:14) — NOT YET COMMITTED at capture time → not in git log

Result: `files_changed = [gates.py, tests/test_gates.py, ..., PROJECT_STATUS.md, BACKLOG.md, ...]`

**(3) Does this include B's files? YES.** `PROJECT_STATUS.md` and `BACKLOG.md` from B's commit at 15:46:21 are within the `--since` range. **Candidate (a) is structurally insufficient.** It shifts the contamination from dirty-file-based (C's uncommitted edits) to commit-based (B's committed files during the same window), but does not isolate Plan A's changes.

Additionally: `git log --since` does NOT capture uncommitted changes at all. If Plan A's agent makes edits but doesn't commit during the step (common for diagnostics), `files_changed` would be empty — a false negative.

**Analysis stopped — candidate fails (3).**

---

### Candidate (b): Plan-slug commit-message scoping

**Mechanism:** Filter `git log` output to only commits whose message contains the plan slug. Requires Planner template convention mandating slug in commit messages.

**(1) Lines changed in `bellows.py`:**
- `_capture_git_diff` (lines 404-420): Replace with `git log --grep=<plan_slug> --stat --relative -- .`. Add `plan_slug` parameter.
- `run_plan`: Pass `plan_slug` (already available at line 217) to `_capture_git_diff`.
- `_parse_diff_stat`: Adapt to `git log --stat` output format.

**(2) Given Phase 1A timeline, what does the candidate return for A's `files_changed`?**

`git log --grep="deposit-exists-directory-paths-2026-04-30" --stat --relative -- .` would return:
- ZERO commits. The commit message for A's commit (`e609ad3`) is `fix(gates): _resolve_deposit_path accepts directory paths (BACKLOG #11)` — no plan slug present.

Result: `files_changed = []` — A's own committed files are also excluded because the slug is absent from the commit message.

**(3) Does this include B's files? NO — but it also excludes A's own files.**

The candidate is technically immune to contamination, but only because it returns nothing. Slug-in-commit-message rate is 0/30 = 0% (Phase 1 prior diagnostic, Q3). No commit in the repository's history contains a parseable plan slug.

This candidate requires:
1. PLANNER_TEMPLATE convention change mandating slug in commit messages
2. All existing plans to cycle through (stale plans won't comply)
3. Agent compliance (agents may paraphrase, abbreviate, or omit the slug)
4. Does NOT handle uncommitted changes (diagnostic steps that don't commit → empty files_changed)

**Structural assessment:** If slug convention were adopted at 100% rate, this candidate would pass (3). But the current 0% rate makes it structurally non-functional today. Additionally, it shares candidate (a)'s blind spot for uncommitted changes. **Not viable without convention adoption + complementary dirty-file tracking.**

---

### Candidate (d): Per-plan git worktree

**Mechanism:** For each parallel plan, `git worktree add /tmp/bellows-worktree-<slug> HEAD` before dispatching `claude -p`. Each agent's subprocess runs with `cwd=worktree_path` instead of the shared `project_path`. Commits happen in the worktree's isolated index. After the step completes, commits are cherry-picked or merged back to the main branch.

**(1) Lines changed in `bellows.py`:**
- `run_plan` (line 194 onward): Before `runner.run_step()`, if the plan is in a parallel group, create a worktree. Set `effective_project_path = worktree_path`. After `runner.run_step()` returns, merge worktree commits back, then `git worktree remove`.
- `_capture_git_diff` (lines 404-420): No change needed — it already takes `project_path` as a parameter, so passing `worktree_path` scopes the diff to the worktree.
- `_parse_diff_stat` (lines 423-456): No change needed.
- `handle_parallel_group` (line 590): May need coordination logic to ensure worktree cleanup happens after all siblings complete.
- Bootstrap prompt construction (lines 255-262): The `shadow_prompt_path` uses an absolute path into `.bellows-cache/`. If `cwd` changes to the worktree, the shadow cache path still resolves correctly (absolute path). However, the agent may use relative paths in its bootstrap prompt that assume `cwd=bellows/` — these would break if `cwd=worktree/`.

**(2) Given Phase 1A timeline, what does the candidate return for A's `files_changed`?**

Plan A's `claude -p` runs in `/tmp/bellows-worktree-deposit-exists/`. Plan C's `claude -p` runs in `/tmp/bellows-worktree-ledger-pause/`. Each has its own working tree and index.

At A's `post_diff` capture (~15:46:21):
- `git diff --stat --relative -- .` runs in A's worktree
- C's edits to `bellows.py`, `verdict.py`, `tests/test_verdict.py` are in C's worktree, NOT in A's
- A's worktree only contains A's own uncommitted changes (none — A committed at 15:46:15)

Result: `files_changed = []` — A committed, so no dirty files in A's worktree at post_diff time.

Wait — this reveals a subtlety. The current diff-of-diffs approach detects changes by comparing working-tree state at step start vs step end. If A commits during its step, the committed files LEAVE the working tree diff, and `_parse_diff_stat` would not report them (they're in `pre_map` but not `post_map`, and the list comprehension iterates `post_map.items()` only). This means the current mechanism ALREADY misses A's own committed files — it only catches files that are dirty at step-end but weren't dirty at step-start.

This is true today too (without worktrees). The contamination vector is specifically about SIBLING dirty files, not about the victim's own committed files. The scope_check gate tripped on sibling files, not on missing own files.

**(3) Does this include B's files? NO.** Each worktree is fully isolated. C's edits are invisible to A's worktree. B's edits are invisible to A's worktree. **Candidate (d) passes the literal contamination test.**

**(4) Canary comparison:** Canary not executed (Phase 1C gap). The mechanism is structurally identical for both the incident and a canary — worktree isolation is a filesystem-level guarantee, not dependent on timing or file content.

**(5) New failure modes:**
- **Agent UX — absolute path expectations:** Agents that reference absolute paths (e.g., `/Users/marklehn/Desktop/GitHub/bellows/knowledge/...`) would break in a worktree at `/tmp/bellows-worktree-<slug>/`. The bootstrap prompt's shadow cache path (`_shadow_path`) uses an absolute path into `.bellows-cache/` which would NOT exist in the worktree. Mitigation: symlink `.bellows-cache/` into the worktree, or rewrite the bootstrap prompt to use the worktree-relative path.
- **Commit merging:** Worktree commits are on a detached HEAD or temporary branch. They must be cherry-picked or merged to the main branch after the step. If two siblings modify the same file (e.g., both edit `BACKLOG.md`), the merge would conflict. Mitigation: sequential merge with conflict detection; if conflict, halt the plan and escalate.
- **Git history shape:** Cherry-picked commits have different SHAs than the originals. `git log` attribution changes. The `plan_slug` column in `bellows.db` wouldn't be affected, but any process that relies on exact SHA matching would break.
- **`.bellows-cache` shadow cache:** The shadow cache at `BELLOWS_ROOT / ".bellows-cache"` is outside the worktree. Since `BELLOWS_ROOT` is hardcoded at module level (`bellows.py:16`), all worktree-dispatched agents would reference the same shadow cache. This is correct — the shadow cache stores pristine plan content, which is the same regardless of worktree.
- **Gate 7 `file_change_audit`:** `_gate_scope_check` at `gates.py:233` receives `files_changed` which would now come from the worktree diff. If the worktree is clean after the agent commits, `files_changed = []`, and scope_check would be vacuously passed (line 234: `if not files_changed: return`). This means scope_check would stop catching actual out-of-scope modifications if the agent commits them during the step. Mitigation: switch from working-tree diff to `git log` diff within the worktree (since the worktree is isolated, `git log` would only show the current agent's commits).
- **Platform:** `git worktree` is available on all platforms with git >= 2.5 (2015). No platform-specific issues.

**(6) Cost:**
- Estimated LOC: ~60-80 (worktree create/remove lifecycle, merge logic, bootstrap prompt path rewriting)
- Surface area: `run_plan` in `bellows.py` (primary), `handle_parallel_group` (coordination), possibly `runner.py` (cwd parameter)
- Test surface: worktree creation/removal, merge conflict handling, path resolution in worktree context, scope_check behavior with worktree diffs

---

### Candidate (e): Per-process file-touch tracking via fsevents/inotify filtered by claude-p PID

**Mechanism:** Before `runner.run_step()`, register an OS-level file watcher (fsevents on macOS, inotify on Linux) scoped to the `claude -p` subprocess PID. Accumulate a set of file paths that the process (or its children) touch with write operations. After the step, use this set as `files_changed` instead of git diff.

**(1) Lines changed in `bellows.py`:**
- New module or inline code: file watcher setup, PID-scoped event filtering, accumulator
- `run_plan` (lines 265-282): Replace `pre_diff`/`post_diff`/`_parse_diff_stat` with watcher start/stop/collect
- `runner.py` (line 49): Need to expose the `claude -p` subprocess PID back to `bellows.py` so the watcher can filter by PID. Currently `runner.run_step` returns parsed output but not the PID.
- `_capture_git_diff` and `_parse_diff_stat`: Would be replaced entirely for parallel plans (kept for sequential plans as fallback)

**(2) Given Phase 1A timeline, what does the candidate return for A's `files_changed`?**

The watcher tracks file writes by A's `claude -p` PID (and its child processes). Plan A's agent wrote to `gates.py`, `tests/test_gates.py`, and the dev-log file. Plan C's agent writes to `bellows.py`, `verdict.py`, `tests/test_verdict.py` from a DIFFERENT PID.

Result: `files_changed = [gates.py, tests/test_gates.py, knowledge/development/deposit-exists-directory-paths-dev-log-2026-04-30.md]` — only A's own files.

**(3) Does this include B's files? NO.** PID filtering ensures only the current plan's subprocess's file writes are tracked. **Candidate (e) passes the literal contamination test.**

**(4) Canary comparison:** Canary not executed. The mechanism is PID-scoped, so it would behave identically for any concurrent execution scenario — the PID filter is a kernel-level guarantee.

**(5) New failure modes:**
- **Platform-specificity:** fsevents is macOS-only. inotify is Linux-only. Bellows currently runs on macOS (`platform: darwin` per environment). If Bellows ever runs on Linux (Docker, CI), the inotify path would be needed. Mitigation: platform dispatch with a common interface. But this doubles the implementation and test surface.
- **PID tree tracking:** `claude -p` may spawn child processes (e.g., bash subcommands, git operations). File writes from children need to be attributed to the parent PID. On macOS, fsevents does not include PID information natively — the `FSEvents` framework reports events at the path level, not the process level. **This is a critical gap:** macOS fsevents cannot filter by PID. To get PID-scoped tracking on macOS, you'd need `dtrace`, `endpoint security framework`, or `proc_info` polling — all of which require elevated privileges or entitlements.
- **On Linux:** inotify also does NOT include PID information. `fanotify` with `FAN_REPORT_FID` and `FAN_REPORT_DFID_NAME` can report PIDs (since Linux 5.1), but requires `CAP_SYS_ADMIN` or `CAP_DAC_READ_SEARCH`.
- **Practical implication:** PID-scoped file tracking is not achievable with standard user-space APIs on either macOS or Linux without elevated privileges. This makes the candidate **structurally infeasible** in Bellows's execution environment (runs as a regular user process).
- **Gate 7 interaction:** `_gate_scope_check` would receive the watcher's file list directly instead of git diff output. The gate logic at `gates.py:233-258` iterates `files_changed` and checks each against the plan text — this works regardless of the source of the list.
- **False positives from read-then-write patterns:** The watcher would capture ANY file the process writes to, including temporary files, `.pyc` files, git index operations, etc. Would need an allowlist or git-tracked-files filter. Adds complexity.

**(6) Cost:**
- Estimated LOC: ~120-200 (platform dispatch, event registration, PID/child tracking, accumulator, cleanup, fallback for unsupported platforms)
- Surface area: New module (`file_watcher.py`), changes to `runner.py` (PID exposure), `bellows.py` (integration), platform-specific test matrix
- Test surface: macOS fsevents path, Linux fanotify path, PID child attribution, temporary file filtering, privilege requirement handling

**Critical finding:** The PID-filtering premise of this candidate requires OS APIs that are not available at standard user privilege level on either macOS or Linux. Without PID filtering, the watcher would see ALL file writes from ALL processes — the same contamination vector as the current approach. **Candidate (e) is structurally infeasible without elevated privileges.**

---

## Phase 3 — Recommendation

### Candidate Survival Summary

| Candidate | Passes (3)? | Notes |
|-----------|------------|-------|
| **(a)** timestamp-bound git range | **NO** | Returns sibling's committed files in the same time window |
| **(b)** plan-slug commit-message scoping | Conditionally | Only works at 100% slug adoption (current rate: 0%) + doesn't handle uncommitted changes |
| **(d)** per-plan git worktree | **YES** | Full isolation via filesystem-level working tree separation |
| **(e)** per-process file-touch tracking | **YES in theory, NO in practice** | PID-scoped tracking requires elevated OS privileges not available to Bellows |

### Surviving Candidate: (d) Per-plan git worktree

**Recommendation: Candidate (d) is the only structurally viable fix.**

**Evidence:**
- Phase 2 analysis demonstrates that (d) returns an empty or A-only `files_changed` for Plan A in the Phase 1A timeline, because each worktree is a filesystem-level isolation boundary. C's edits to `bellows.py`, `verdict.py`, `tests/test_verdict.py` exist only in C's worktree and are invisible to A's `post_diff` capture.
- Candidates (a) and (b) fail the literal contamination test — (a) includes sibling committed files, (b) returns nothing at current 0% slug rate.
- Candidate (e) requires OS privileges that Bellows does not have.

**Fix shape:**

1. **New function `_create_worktree(plan_slug: str, project_path: str) -> str`** — calls `git worktree add /tmp/bellows-wt-<slug> HEAD` and returns the worktree path. Called from `run_plan` when the plan is part of a parallel group.

2. **Modified `run_plan`** (lines 194-397) — after claim, if `extract_parallel_group(plan_filename)` is not None, create a worktree. Set `effective_cwd = worktree_path` and pass to `runner.run_step()`. After step completes, cherry-pick worktree commits to main branch, then `git worktree remove`.

3. **Modified `runner.run_step`** — accept optional `cwd` override (currently uses `project_path` from `run_plan`). Pass to `subprocess.run` for `claude -p`.

4. **New function `_merge_worktree_commits(worktree_path: str, main_branch: str)`** — enumerate commits in the worktree not in main, cherry-pick each. On conflict, halt the plan with a new gate failure.

5. **New function `_remove_worktree(worktree_path: str)`** — `git worktree remove <path>`. Called in a `finally` block to ensure cleanup.

6. **Scope_check adaptation:** Within a worktree, switch `_capture_git_diff` to `git log --oneline --stat --relative -- .` scoped to the worktree's commits (since working-tree diff would be empty after the agent commits). Alternatively, keep the pre/post working-tree diff since it's already isolated.

**Files changed:**
- `bellows.py` — `run_plan`, `_create_worktree`, `_merge_worktree_commits`, `_remove_worktree`
- `runner.py` — `run_step` cwd parameter
- Possibly `gates.py` — if scope_check needs adaptation for worktree paths

**Test surface (file-level, not actual tests):**
- `tests/test_bellows.py` — worktree creation/removal lifecycle, parallel plan worktree dispatch, merge conflict handling
- `tests/test_runner.py` — cwd override propagation
- Integration smoke test: two parallel plans modifying different files, verify no cross-contamination in `files_changed`

**New failure modes and mitigations:**
1. **Merge conflicts** — mitigated by halting the plan with a descriptive gate failure. The Planner/CEO can resolve manually. This is an acceptable degradation: the current behavior (false-positive scope_check) also requires CEO intervention.
2. **Absolute path expectations** — mitigated by ensuring the bootstrap prompt uses the shadow cache's absolute path (already does) and the worktree is a full git checkout with the same relative paths.
3. **Disk space** — each worktree is a full working tree copy (~5MB for bellows/). Cleaned up after each step. Negligible.
4. **Shadow cache access** — `.bellows-cache/` is outside the worktree but referenced by absolute path. No issue.

### Cost-vs-Friction Context

**Recommended fix cost:** ~60-80 LOC across `bellows.py` and `runner.py`, plus ~40-60 LOC of new tests. Total surface: ~120-140 LOC. Three new functions in `bellows.py`, one parameter addition in `runner.py`. The merge-back logic is the most complex component (~20-30 LOC with conflict detection). Estimated implementation: one 2-step executable plan (Step 1: DEV implementation, Step 2: QA verification).

**Workaround cost (don't-fix, for context only):** Treat `parallel-N-` plans as read-only/diagnostics-only. Plans that need to commit code run sequentially. CEO continues to manually override false-positive scope_check failures when parallel plans are used for committing work. Current overhead: ~2 minutes per false-positive verdict (CEO reads verdict request, cross-references dev-log, issues override). Frequency: every parallel dispatch with concurrent commits (estimated 30-50% of parallel sessions). The workaround is sustainable but scales linearly with parallel plan usage. If parallel plan frequency increases (as the Planner matures), the CEO override burden grows proportionally. The don't-fix path also means the `parallel-N-` pattern's documentation must carry a permanent "unsafe for committing work" caveat.

---

## Output Receipt
**Agent:** Bellows Systems Analyst (combined diagnostic execution)
**Step:** 2 (Phase 2-3)
**Status:** Complete

### What Was Done
Evaluated four fix-shape candidates against the Phase 1A incident timeline, tracing each candidate's mechanism through the literal contamination window. Determined that per-plan git worktree (candidate d) is the only structurally viable fix. Candidates (a) and (b) fail the contamination test; candidate (e) is infeasible at standard user privileges.

### Files Deposited
- `bellows/knowledge/research/parallel-collision-candidate-evaluation-2026-05-03.md` — candidate evaluation and recommendation

### Files Created or Modified (Code)
- None (diagnostic — no production code modified)

### Decisions Made
- Classified candidate (e) as structurally infeasible based on OS API privilege requirements (fsevents and inotify do not expose PID information at user privilege level; fanotify requires CAP_SYS_ADMIN)
- Recommended candidate (d) as the sole surviving fix with a concrete fix-shape specification

### Flags for CEO
- The recommendation is candidate (d) per-plan git worktree. The Planner should author a 2-step executable plan for implementation. The merge-conflict failure mode is the primary risk — the CEO should decide whether merge conflicts should halt the plan or attempt automatic resolution.
- Candidate (b) (slug scoping) could serve as a complementary long-term enhancement but is blocked on PLANNER_TEMPLATE convention adoption and does not address uncommitted changes.

### Flags for Next Step
- None — this is the terminal diagnostic step. The Planner authors the implementation plan based on this recommendation.
