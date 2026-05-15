# Worktree vs. Serialize-Capture — Cost-vs-Coverage Recommendation

**Date:** 2026-05-03 | **Plan:** diagnostic-worktree-cost-coverage-recommendation-2026-05-03 | **Step:** 1

**CEO-locked decisions (not re-evaluated):**
- Worktree location: in-tree `<project>/.bellows-worktrees/<slug>/`
- Worktree scope: always-worktree (every plan dispatch)
- Don't-fix excluded

---

## Step 1A — Cost-vs-Coverage Matrix

| Dimension | Worktree | Serialize-Capture |
|-----------|----------|-------------------|
| **Total LOC (production)** | ~35–45 LOC. Two new helper functions `_create_worktree` and `_teardown_worktree` (~20–25 LOC combined), 6 line modifications in `run_plan` (4 cwd swaps + creation insertion + teardown insertion), 1 constant, 1 gitignore line (D2, 9 change rows). | ~15–20 LOC. 1 module-level lock declaration, 4 acquire/release pairs wrapped in `try/finally`, per-project lock dict with `_locks_lock` guard (~5 lines) (D2, 5 change rows). |
| **Total LOC (new tests)** | ~13 new tests: 6 in `test_bellows.py` + 7 in new `test_worktree.py` (D7). Estimated ~200–250 lines of test code. | ~5 new tests in `test_bellows.py` (D7). Estimated ~80–120 lines of test code. |
| **Files modified in `bellows.py`** | 8 change sites: 2 new helper functions, 1 constant, worktree creation insertion, 4 cwd replacements (project_path to wt_path), teardown insertion (D2). | 5 change sites: 1 lock declaration, 4 acquire/release pairs (D2). |
| **New helper functions** | 2: `_create_worktree(project_path, slug)`, `_teardown_worktree(project_path, wt_path, slug)` (D2). | 0. Inline lock acquire/release. Per-project lock dict uses `setdefault` — no dedicated function (D2, D3b). |
| **Coverage of 7 contamination sub-vectors** | **5 Solved, 1 Partial, 1 N/A.** Solved: (i) sibling uncommitted dirty files, (ii) sibling committed files, (iii) staged-but-uncommitted, (iv) parallel-group concurrent commits, (v) sequential-but-concurrent dispatch. Partial: (vi) test-suite external resources not isolated by worktrees. N/A: (vii) DB writes (D5). | **6 Solved, 0 Partial, 1 N/A.** Solved: (i)–(v) same as worktree, plus (vi) test-suite runs are serialized so shared fixtures cannot collide. N/A: (vii) DB writes (D5). |
| **Number of new failure modes** | 7 (D6: disk full, cherry-pick conflict, pytest cwd shift, uncommitted files lost mid-copy, stale worktree registrations, absolute path reads, concurrent creation index lock). | 5 actual (D6: long step blocks peers, exception without finally, parallel-group wall-clock blowup, thread starvation, _locks_lock contention; #5 is N/A by design). |
| **Likely-Catastrophic failure modes** | 0 modes that are both Likely AND Catastrophic. Breakdown: 2 Likely/Recoverable (#3 pytest cwd shift, #5 stale registrations). 1 Unlikely/Catastrophic (#4 uncommitted files lost if teardown crashes mid-copy — mitigated by in-tree persistence) (D6). | 0 modes that are both Likely AND Catastrophic. Breakdown: 2 Likely/Recoverable (#1 long step blocks peers up to 18000s, #3 parallel wall-clock blowup). 1 Unlikely/Catastrophic (#2 exception without `finally` release deadlocks all project threads — mitigated by mandatory `try/finally`) (D6). |
| **Wall-clock overhead per plan (sequential)** | ~0.5–1.5 seconds (worktree creation ~0.3–0.8s + teardown ~0.1–0.3s + cherry-pick ~0.1–0.2s per commit). <1% of typical step time (D3f). | ~0 seconds. Lock acquire/release is instant. No contention for sequential dispatch — only one plan holds the lock (D3a, D3d). |
| **Wall-clock overhead per parallel-3 group** | ~1.5–4.5 seconds total overhead across 3 plans, but **parallelism preserved**: group wall-clock ≈ max(A,B,C) + per-plan overhead. For three 120s steps: ~122s (D3f). | **Parallelism collapsed**: group wall-clock ≈ A + B + C. For three 120s steps: ~360s vs ~120s concurrent. 3x wall-clock regression (D3d). |
| **Reversibility cost (revert if shipped + broken)** | Single revert commit removes 2 helper functions + 6 line changes + gitignore line. Moderate complexity — must verify no orphaned worktrees remain after revert. `git worktree prune` cleans stale registrations. | Single revert commit removes 1 lock + 4 acquire/release pairs + lock dict. Very clean — no persistent state. Lock removal leaves no residue. |
| **Implementation rollout risk** | **Moderate.** Implementation plan modifies bellows.py at 8 sites. If dispatched alongside any other bellows plan, the QA step's own `post_diff` is subject to the contamination bug (the daemon runs pre-fix code). More code changes = more diff surface for false-positive scope_check. Mitigation: quiet-window dispatch (Step 1C). | **Low.** Implementation plan modifies bellows.py at 5 sites. Same exposure as worktree, but fewer change sites = smaller diff surface. Additionally, the bug only fires when something else runs concurrently — if the implementation plan is the only bellows plan at dispatch time, the bug is silent (Step 1C). |
| **Interaction with future infrastructure** | **High value.** Per-plan worktrees create isolated sandboxes that naturally support future features: terminal output redesign (per-plan working directory), notification audit (per-plan file state), future verdict mechanization (per-plan diff isolation). The worktree abstraction is reusable infrastructure. | **Low value.** Mutex is specific to diff-capture serialization. Does not help future features. If future features need per-plan isolation, worktrees would still be required later — serialize-capture is throwaway scaffolding in that scenario. |

---

## Step 1B — Parallel Commit Usage Analysis

### Historical parallel-N- plan count

From `knowledge/decisions/Done/`, 10 plans match the `parallel-\d+-` filename pattern:

| Plan | Date | Type | Group |
|------|------|------|-------|
| `parallel-1-diagnostic-bellows-reliability-2026-04-14` | 2026-04-14 | diagnostic | parallel-1 |
| `parallel-1-diagnostic-bellows-parallel-group-collection-2026-04-16` | 2026-04-16 | diagnostic | parallel-1 |
| `parallel-1-diagnostic-bellows-rescan-duplicate-runs-2026-04-16` | 2026-04-16 | diagnostic | parallel-1 |
| `parallel-1-executable-bellows-claim-at-entry-2026-04-16` | 2026-04-16 | executable | parallel-1 |
| `parallel-1-executable-bellows-parallel-defer-2026-04-16` | 2026-04-16 | executable | parallel-1 |
| `parallel-1-executable-bellows-verdict-scoping-2026-04-16` | 2026-04-16 | executable | parallel-1 |
| `parallel-1-executable-parse-diff-stat-fix-2026-04-16` | 2026-04-16 | executable | parallel-1 |
| `parallel-1-executable-verdict-readme-2026-04-16` | 2026-04-16 | executable | parallel-1 |
| `parallel-1-executable-deposit-exists-directory-paths-2026-04-30` | 2026-04-30 | executable | parallel-1 |
| `parallel-1-executable-ledger-pause-reason-code-2026-04-30` | 2026-04-30 | executable | parallel-1 |

**Totals:** 10 parallel-N- plans. 7 executable (committed code), 3 diagnostic (read-only).

### Group dispatch frequency

Three distinct parallel group dispatches across the observation window (2026-04-14 to 2026-05-03, 19 days):

| Date | Group size | Executables in group | Diagnostics in group |
|------|-----------|---------------------|---------------------|
| 2026-04-14 | 1 | 0 | 1 |
| 2026-04-16 | 7 | 5 | 2 |
| 2026-04-30 | 2 | 2 | 0 |

**Rate:** 3 parallel group dispatches in 19 days ≈ **4.7 groups/month**.

Of these 3 groups, 2 contained executable plans that committed code (2026-04-16 and 2026-04-30). Only the 2026-04-30 group produced the observed contamination incident — the 2026-04-16 group may have experienced contamination silently (no archived verdict evidence was examined for that date).

### Wall-clock cost of serialize-capture

Under serialize-capture, a parallel-N group of K plans at average step time T completes in K × T wall-clock instead of max(K plans) × ~T. The delta is (K-1) × T per group versus worktree (which preserves parallelism).

| Scenario | Groups/month (N) | Plans/group (K) | Avg step time (T) | Monthly delta vs. worktree |
|----------|------------------|-----------------|--------------------|---------------------------|
| Historical rate | 4.7 | 3.3 avg | 120s | 4.7 × (3.3-1) × 120s = **1,298s ≈ 22 min/month** |
| Low estimate | 2 | 2 | 120s | 2 × 1 × 120s = **240s ≈ 4 min/month** |
| High estimate | 8 | 4 | 180s | 8 × 3 × 180s = **4,320s ≈ 72 min/month** |
| Conservative (current) | 3 | 2.5 | 120s | 3 × 1.5 × 120s = **540s ≈ 9 min/month** |

**Interpretation:** At historical rates, serialize-capture costs ~9–22 minutes of additional wall-clock per month compared to worktree. This is modest in absolute terms. However, the cost scales linearly with parallel group frequency. If the Planner increases parallel dispatch (e.g., to parallelize diagnostic chains or batch executables), the serialize-capture penalty grows proportionally while worktree overhead remains constant at ~1–1.5 seconds per plan.

**Note on the 2026-04-30 incident:** The incident involved 3 concurrent plans (2 parallel-1 + 1 sequential `executable-backlog-hygiene-sweep`). The sequential plan was NOT in the parallel group but ran concurrently by coincidence. Under serialize-capture with per-project mutex, ALL three plans serialize — the mutex does not distinguish parallel-group from coincidentally-concurrent plans. Under worktree with always-worktree scope, all three get their own worktrees and run truly concurrently. The "always-worktree" locked decision means worktree handles this case natively; serialize-capture penalizes it.

---

## Step 1C — Rollout Risk Under Unfixed Bug

Both candidates require modifying `bellows.py`. The implementation plan that ships either candidate will itself be subject to the parallel-collision bug during its own QA step, since the daemon runs pre-fix code until restart.

### Worktree rollout risk

**Exposure:** The implementation plan modifies `bellows.py` at 8 sites (D2). If the implementation plan dispatches alongside ANY other bellows-project plan, the implementation plan's own `post_diff` will capture dirty files from the concurrent sibling — triggering a false-positive `scope_check` failure on the implementation plan itself. This is the exact bug the plan is fixing.

**Probability estimate:** Moderate. Bellows dispatches plans as they appear in `knowledge/decisions/`. If the CEO deposits the implementation plan during a period when other bellows plans are in-progress or pending, concurrency is possible. The 2026-04-30 incident occurred precisely because a sequential plan (`backlog-hygiene-sweep`) was dispatched alongside a parallel group — demonstrating that concurrency can be coincidental, not just explicit.

**Mitigations:**
1. **Quiet-window dispatch:** CEO deposits the implementation plan when no other bellows plans are in-progress or pending. Verify with `bellows.db` query or Bellows console output.
2. **Halt other bellows plans:** If any bellows plans are in-progress, wait for completion before depositing the implementation plan.
3. **Manual restart between implementation and QA observation:** The implementation plan ships code changes. CEO restarts Bellows (so the new code is active). Only then does the CEO or Planner author and dispatch the smoke test canary.

**Residual risk after mitigations:** Low. If the implementation plan is the ONLY bellows plan running, no concurrent sibling exists, and the contamination bug cannot fire. The quiet-window approach is the standard safe deployment pattern for Bellows code changes (LESSONS.md 2026-04-19 pattern).

### Serialize-capture rollout risk

**Exposure:** The implementation plan modifies `bellows.py` at 5 sites (D2). Same exposure shape as worktree — if something else runs concurrently, the bug fires.

**Probability estimate:** Low. The same quiet-window dispatch mitigations apply, and they are easier to execute for serialize-capture because the implementation plan is smaller (5 change sites vs 8). Fewer modified lines = smaller diff surface = lower chance of a false-positive `scope_check` match even if a sibling is running.

**Key difference:** Serialize-capture's smaller change surface makes rollout marginally safer, but the difference is small — both candidates require quiet-window dispatch for safe rollout. The bug fires based on *any* concurrent sibling editing *any* file, not based on the implementation plan's own diff size.

### Meta-observation

The LESSONS.md 2026-04-19 pattern ("recent Bellows fixes have hit this pattern repeatedly") applies to BOTH candidates identically. The mitigation is operational (quiet-window dispatch), not technical. Neither candidate is structurally immune to its own rollout risk — the fix cannot bootstrap itself.

---

## Step 1D — Recommendation

**Recommendation: Option 1 — Ship worktree as designed.**

### Rationale by dimension

**Dimensions favoring worktree:**
- **Parallelism preservation** (Step 1A, wall-clock overhead row): Worktree preserves concurrent execution. Serialize-capture collapses parallelism entirely. At historical rates, this is a 9–22 min/month wall-clock difference (Step 1B), scaling linearly with parallel frequency.
- **Future infrastructure value** (Step 1A, interaction row): Worktree creates reusable per-plan sandboxes. Serialize-capture is single-purpose scaffolding that would need replacement if future features require per-plan isolation.
- **Always-worktree scope alignment** (CEO-locked decision): The CEO locked "always-worktree" scope, meaning every plan dispatch creates a worktree. This decision signals intent for per-plan isolation as infrastructure, not a minimal targeted fix. Shipping serialize-capture would deliver a different architecture than what the CEO specified.
- **Coincidental concurrency handling** (Step 1B, 2026-04-30 note): The literal incident involved a sequential plan (`backlog-hygiene-sweep`) running alongside a parallel group. Under always-worktree, this is handled natively. Under serialize-capture, the sequential plan is penalized by the mutex despite not being in any parallel group.

**Dimensions favoring serialize-capture (acknowledged):**
- **Lower LOC** (Step 1A): ~15–20 vs ~35–45 production LOC. A real but modest difference — both are small implementations.
- **Fewer tests** (Step 1A): 5 vs 13 new tests. Serialize-capture's test surface is smaller because the mechanism is simpler.
- **Marginally better coverage** (Step 1A): 6/6 Solved vs 5/6 Solved + 1 Partial. The Partial (vi: test-suite external resources) is a narrow edge case — worktrees isolate git-tracked files but not external resources like databases or `/tmp` fixtures. In practice, Bellows-dispatched agents rarely run test suites that depend on shared external fixtures.
- **Lower rollout risk** (Step 1C): 5 change sites vs 8. Both require quiet-window dispatch; the difference is marginal.
- **Cleaner revert** (Step 1A): Lock removal leaves no residue. Worktree revert requires verifying no orphaned worktrees, though `git worktree prune` handles this.

**Why the marginal cost is justified:**
The cost delta between worktree and serialize-capture is ~20 LOC production + ~8 additional tests + ~2 additional failure modes. Against this:
1. Worktree preserves the parallelism property that the existing `parallel-N-` dispatch infrastructure was built to provide.
2. Worktree delivers the "always-worktree" scope the CEO locked — serialize-capture does not.
3. Worktree's infrastructure value means the investment is load-bearing for future Bellows evolution. Serialize-capture would be throwaway code replaced by worktrees when isolation needs expand.

**No contradiction with CEO-locked decisions.** The recommendation aligns with all three locked decisions: in-tree location, always-worktree scope, don't-fix excluded.

---

## Step 1E — Implementation Plan Structure Proposal

### Tier: Medium

**Rationale:** 2 production files modified (`bellows.py`, `.gitignore`), 1 new test file (`test_worktree.py`), ~35–45 production LOC, ~13 new tests across 2 test files (D2, D7). Too many moving parts for Small (cherry-pick merge-back logic, uncommitted file copy-back, startup prune hook, fallback-on-failure). Not Large — the change is confined to `bellows.py` + tests with no cross-module restructuring.

### Step structure: Two separate single-step plans

Given the multi-step parsing bug (BACKLOG 2026-05-03), the implementation should be authored as **two separate single-step plans** dispatched sequentially:

**Plan 1 — Implementation (Bellows Developer):**
- Add `_create_worktree(project_path, slug)` and `_teardown_worktree(project_path, wt_path, slug)` helper functions
- Wire worktree creation into `run_plan` between plan claim (line 240) and pre-diff (line 265)
- Replace `project_path` with `wt_path` in all 4 `_capture_git_diff` calls and both `runner.run_step` calls
- Add worktree teardown after final gates check (cherry-pick + uncommitted file copy-back)
- Add `git worktree prune` call in `Bellows.__init__` for startup cleanup (D3g)
- Add `.bellows-worktrees/` to `bellows/.gitignore`
- Add fallback-to-shared-tree on worktree creation failure (D3g: try/except with warning log)
- Run existing test suite to verify no regressions

**Plan 2 — Tests (Bellows Developer):**
- Add 6 new tests to `tests/test_bellows.py` (D7: worktree lifecycle assertions in `run_plan` mocks)
- Create `tests/test_worktree.py` with 7 integration tests (D7: isolation verification, teardown, cherry-pick, concurrent creation)
- Run full test suite

**Why two plans instead of one:** The implementation (Plan 1) is self-contained and testable via existing tests. The new tests (Plan 2) are verification of the implementation. Separating them means Plan 1 can ship and restart Bellows before Plan 2 runs — Plan 2's integration tests then exercise the actual worktree code path. If bundled, the integration tests would run against the just-written-but-not-yet-restarted code, which doesn't exercise the real dispatch path.

**If the multi-step parsing bug is fixed first:** A single two-step plan would be preferable (Step 1: implementation by Bellows Developer, Step 2: tests by Bellows Developer). The two-step structure avoids the restart gap between implementation and tests.

### Test scope: Targeted

**Rationale:** D7 identifies specific test needs — 13 new tests covering worktree lifecycle, isolation, teardown, cherry-pick, and concurrent creation. No existing tests need modification (D7 confirms all existing tests mock `_capture_git_diff` and are worktree-agnostic). The existing test suite should be run as a regression check, but no full-suite expansion beyond the D7 surface is needed.

### Live smoke test placement: Separate post-implementation diagnostic

**Confirmed per D8 recommendation.** Both candidate designs recommended the canary as a separate post-implementation diagnostic, and Step 1C reinforces this: the implementation plan's own QA step runs pre-fix code, so a canary dispatched within the implementation plan would test unfixed Bellows. The canary must run after Bellows restart with the new worktree code active. The Planner should author the canary diagnostic after Plan 1 ships and Bellows restarts.

### Specialist file syncs needed before dispatch

- **Bellows Developer specialist file:** Should reference `_create_worktree` and `_teardown_worktree` in its Key Sources section once implemented. Not a blocker — the implementation plan's agent reads `bellows.py` directly.
- **Bellows Systems Analyst specialist file:** No update needed. The SA's domain is architecture decisions, not implementation details.
- **Test surface documentation:** Phase A7 of the surface map documents the current test surface. After Plan 2 ships, the surface map is stale but archival — no update needed.

### Pre-implementation prerequisites

| Prerequisite | Required? | Rationale |
|---|---|---|
| Multi-step parsing bug fix (BACKLOG 2026-05-03) | **No** (but beneficial). Two separate single-step plans work around the bug. If fixed first, a single two-step plan is cleaner. | Workaround exists. |
| `git worktree prune` startup hook | **Bundled into Plan 1.** D3g specifies this as part of the worktree implementation — adding it to `Bellows.__init__` is a 2-line change. | Not a separate prep plan. |
| `.gitignore` update | **Bundled into Plan 1.** One-line change following the `.bellows-cache/` pattern (D3a, Phase A6). | Not a separate prep plan. |
| Quiet-window deployment | **Operational, not a plan.** CEO ensures no other bellows plans are running at Plan 1 dispatch time (Step 1C). | Pre-dispatch checklist item. |

---

## Step 1F — Open Questions for CEO

### 1. Cherry-pick merge conflict behavior

**Question:** Should the implementation halt the plan on cherry-pick merge conflict during worktree teardown, or attempt automatic conflict resolution?

**SA lean: Halt and log for CEO attention.** Cherry-pick conflicts mean two agents independently modified the same file — a Planner coordination failure that should surface as a visible error, not be silently auto-merged. D3b explicitly states: "The cherry-pick conflict surfaces the coordination failure rather than silently merging." Auto-resolution (e.g., `git cherry-pick --strategy-option=theirs`) risks silently choosing one agent's version and discarding the other's work.

### 2. Worktree persistence across Bellows restart

**Question:** Should worktrees be torn down on Bellows shutdown (SIGTERM/SIGINT handler), or persisted for crash recovery on next startup?

**SA lean: Persist.** In-tree worktrees survive reboots by design (D3a: this was a key argument for in-tree over `/tmp/`). On next startup, the `git worktree prune` call (D3g) cleans stale registrations, and Bellows can detect orphaned `.bellows-worktrees/<slug>` directories matching `in-progress-` plan slugs. Tearing down on shutdown risks losing uncommitted deposit files from interrupted diagnostics (D3c: diagnostic agents frequently leave files uncommitted). A graceful shutdown handler could attempt teardown for completed plans but should preserve in-progress worktrees.

### 3. Fallback-to-shared-tree scope

**Question:** Should the fallback-to-shared-tree on worktree creation failure (D3g) be a silent degradation with a warning log, or should it pause the plan for CEO review?

**SA lean: Silent degradation with warning log.** The fallback restores pre-fix behavior — the plan runs exactly as it would without the worktree feature. Pausing for CEO review on a disk-full or index-lock error blocks the plan until CEO intervenes, which defeats Bellows's autonomous operation model. The warning log gives the CEO visibility without blocking execution. If the CEO wants stricter enforcement (worktree-or-nothing), this can be tightened in a follow-up.

### 4. Implementation plan dispatch sequencing

**Question:** Should Plan 1 (implementation) and Plan 2 (tests) be dispatched back-to-back with a Bellows restart between them, or should Plan 2 wait for explicit CEO confirmation after Plan 1?

**SA lean: CEO confirmation between Plan 1 and Plan 2.** Plan 1 modifies `bellows.py`. The CEO should verify the implementation by reading the diff before restarting Bellows. After restart, the CEO confirms Plan 2 dispatch. This adds a human checkpoint at the highest-risk transition (pre-restart → post-restart) without requiring a full verdict cycle. The alternative (back-to-back with automatic restart) assumes Plan 1's code is correct before any human review.

### 5. Canary authoring timing

**Question:** Should the smoke test canary plan (D8 design) be authored now (ready for post-restart dispatch) or after Plan 1 ships?

**SA lean: After Plan 1 ships.** The canary design is fully specified in D8 of the candidate designs deposit. Authoring it now adds queue noise — it cannot be dispatched until worktree code is live and Bellows is restarted. Writing it after Plan 1 ships means the Planner can reference the actual implemented code (function names, error handling) in the canary's observation criteria, rather than the D8 design spec.

---

## Output Receipt
**Agent:** Bellows Systems Analyst
**Step:** 1
**Status:** Complete

### What Was Done
Produced a ranked cost-vs-coverage recommendation comparing per-plan git worktree against serialize-capture across 12 dimensions with D-section citations. Analyzed historical parallel-N- dispatch frequency (10 plans, 3 group dispatches, 4.7 groups/month). Quantified serialize-capture's wall-clock penalty (9–22 min/month at historical rates). Assessed rollout risk for both candidates under the unfixed bug. Recommended shipping worktree as designed (Option 1). Proposed a two-plan implementation structure (implementation + tests) with Medium tier. Surfaced 5 open questions for CEO with SA leans and rationale.

### Files Deposited
- `bellows/knowledge/research/worktree-cost-coverage-recommendation-2026-05-03.md` — full recommendation with sections 1A–1F

### Files Created or Modified (Code)
- None (diagnostic — no production code modified)

### Decisions Made
- Recommended Option 1 (ship worktree as designed) over Options 2–4, citing parallelism preservation, CEO-locked always-worktree scope alignment, and future infrastructure value as the deciding dimensions
- Proposed two separate single-step plans to work around the multi-step parsing bug
- Confirmed canary as separate post-implementation diagnostic per D8
- Classified all pre-implementation prerequisites as bundleable into Plan 1 (no separate prep plans needed)

### Flags for CEO
- **5 open questions in Step 1F require CEO decisions** before the Planner can author the implementation plan. The SA has provided leans with rationale for each.
- **No contradiction with CEO-locked decisions.** The recommendation aligns with in-tree location, always-worktree scope, and don't-fix exclusion.

### Flags for Next Step
- None — this is a single-step diagnostic. The Planner reads this deposit, verifies via Rule 22, and authors the implementation plan after CEO acceptance.
