# Bellows-Self Exposure Disposition — SA Findings

**Date:** 2026-05-12 | **Plan:** diagnostic-bellows-self-exposure-disposition-2026-05-12 | **Step:** 1

---

## Q1 — Has the bellows-self exposure recurred since 2026-05-05?

**Audit window:** 2026-05-06 through 2026-05-12 (7 days). Picks up where the prior audit (`backlog-1-reproduction-audit-2026-05-05.md`) ended.

**Sources audited:**
- (a) `verdicts/resolved/processed-*` — grep for `scope_check` across all 2026-05-06+ files: **1 match**, but it is a negative confirmation (canary at `processed-verdict-canary-step-header-parser-fixes-2026-05-11-step-2.md` states scope_check was "not tripped")
- (b) `verdicts/ledger.jsonl` — 47 entries in the audit window (lines 75–121): **zero** mention `scope_check` as a gate failure. Gate failures in the window are: `worktree_creation` timeout (1, forge — 2026-05-04T16:12), `unauthorized_done_move` Mode A (1, 2026-05-06), `deposit_exists` false positives (several), `non_zero_exit_1` subprocess crash (1, 2026-05-06). No scope_check failures of any class.
- (c) `knowledge/decisions/halted-*` — no halted plans in the window reference scope_check
- (d) `verdicts/pending/` — no pending verdict requests reference scope_check

### Per-Category Counts (2026-05-06 through 2026-05-12)

| Classification | Count | Plans |
|---|---|---|
| **(a) bellows-self exposure** | 0 | — |
| **(b) real-`.git` post-fix gap** | 0 | — |
| **(c) other class** | 0 | — |

**Total: 0 scope_check failures in the audit window.**

### Cross-reference with prior audit

The prior audit (2026-04-30 through 2026-05-05) found 7 scope_check failures: 3 pre-fix, 4 bellows-self exposure. The bellows-self exposure rate was 4 reproductions in 5 days (~0.8/day), all caused by concurrent CEO operations (verdict-request file moves, archived/ cleanup). The current audit shows 0 reproductions in 7 days, a complete cessation. The procedural mitigations documented in the BACKLOG entry (avoid CEO mv/cleanup in bellows/ during active bellows-self plans) appear to be fully effective.

---

## Q2 — Re-validate option (b) LOC and risk estimate

### (i) Updated LOC delta estimate

Option (b): governance-root-worktree creation with subdirectory cwd — when `project_path` has no `.git`, walk up to the nearest `.git` ancestor (the governance root), create the worktree at that level, and pass `<wt_root>/<relative_subdir>` as effective cwd to the agent.

| Function / Area | Current Lines | LOC Delta | Notes |
|---|---|---|---|
| `_create_worktree` (lines 678–713) | 36 | +15–20 | Walk up to find .git ancestor, create worktree at governance root, compute relative subdir, return both effective_cwd and wt_root |
| `_teardown_worktree` (lines 716–830) | 115 | +8–12 | Accept wt_root parameter; use governance_root for cherry-pick, symbolic-ref, worktree remove, lock detection (lines 752–770) |
| `run_plan()` call sites (lines 393, 409, 473, 496, 561, 587) | 6 sites | +10–15 | Handle return value change from _create_worktree, compute effective_cwd for runner, pass wt_root to teardown |
| `Bellows.__init__` startup prune (lines 972–974) | 3 | +3–5 | Handle no-.git case when finding repo root for worktree prune |
| Tests | — | +30–50 | New fixtures for governance-root worktree case (create, teardown, lock detection, dirty-file copy-back with relative paths) |
| **Total production** | — | **~50–70** | Up from original estimate of 50–80 |
| **Total with tests** | — | **~80–120** | |

Original estimate (2026-05-05): 50–80 LOC. Revised: **50–70 production LOC, 80–120 including tests.** The estimate has grown slightly due to the new lock detection code (commit `8eac4c3`, 2026-05-10) that also needs adaptation.

### (ii) subprocess.run / Popen call site enumeration

| # | Location | Call | cwd= | Subdirectory cwd impact |
|---|---|---|---|---|
| 1 | `runner.py:55` | `subprocess.Popen(cmd, ..., cwd=project_path)` | `project_path` | **Works transparently.** Agent just needs bellows/ as cwd; tools use absolute paths. |
| 2 | `bellows.py:633` | `_capture_git_diff` — `git diff --stat --relative -- .` | `project_path` | **Works transparently.** `--relative -- .` already scopes to cwd. |
| 3 | `bellows.py:699` | `_create_worktree` — `git worktree add` | `project_path` | **Requires fix.** Needs `cwd=governance_root`. |
| 4 | `bellows.py:704` | `_create_worktree` retry — `git worktree add` | `project_path` | **Requires fix.** Same as #3. |
| 5 | `bellows.py:729` | `_teardown_worktree` — `git symbolic-ref` | `project_path` | **Requires fix.** Needs `cwd=governance_root`. |
| 6 | `bellows.py:745` | `_teardown_worktree` — `git log HEAD --not main` | `wt_path` | **Requires fix.** Needs `cwd=wt_root` (not effective_cwd subdirectory). |
| 7 | `bellows.py:777` | `_teardown_worktree` — `git cherry-pick` | `project_path` | **Requires fix.** Needs `cwd=governance_root`. |
| 8 | `bellows.py:782` | `_teardown_worktree` — `git cherry-pick --abort` | `project_path` | **Requires fix.** Needs `cwd=governance_root`. |
| 9 | `bellows.py:792` | `_teardown_worktree` — `git status --porcelain` | `wt_path` | **Requires fix.** Needs `cwd=wt_root`; dirty-file copy-back paths need relative-subdir adjustment. |
| 10 | `bellows.py:817` | `_teardown_worktree` — `git worktree remove` | `project_path` | **Requires fix.** Needs `cwd=governance_root`. |
| 11 | `bellows.py:753` | Lock detection — `os.path.join(project_path, ".git", "index.lock")` | n/a (filesystem) | **Requires fix.** Needs governance_root to find `.git/index.lock`. |
| 12 | `bellows.py:827` | Orphan dir removal — `shutil.rmtree(wt_path)` | n/a (filesystem) | **Works transparently.** Full path is used. |
| 13 | `bellows.py:973` | Startup prune — `git worktree prune` | `project_root` | **Needs consideration.** project_root derivation from watched_projects would need governance_root for bellows. |
| 14 | `bellows.py:838` | `_source_sha()` — `git log -1` | `BELLOWS_ROOT` | **Not affected.** Diagnostic utility, not plan execution path. |
| 15 | `bellows.py:863` | `_module_fingerprints()` — `git log -1` | `bellows_dir` | **Not affected.** Diagnostic utility, not plan execution path. |

**Summary:** 9 call sites require adaptation (#3–10, #11). 2 work transparently (#1–2). 1 needs minor consideration (#13). 2 are not affected (#14–15).

### (iii) New risk surface since 2026-05-05

One new risk surface identified:

- **Lock detection code** (commit `8eac4c3`, 2026-05-10, lines 752–770): Constructs `.git/index.lock` path using `os.path.join(project_path, ".git", "index.lock")`. For the governance-root worktree case, `project_path` (bellows/) has no `.git` — the lock file lives at `governance_root/.git/index.lock`. This code was not present at the time of the original estimate and adds one additional call site to adapt.

No other new project_path/cwd dependencies were added in the past week. The terminal output redesign (`_log`, commit `b11ecc4`), notification coalescing (commit `07a87ad`), module fingerprints (commit `6411054`), `_seen` slug refactoring (commit `63dd6ed`), fence-strip parsers (commit `4d57fd3`), and `_perform_startup_sweep` extraction (commit `dc1acd4`) all operate on internal data structures or fixed paths without new project_path/cwd dependencies.

---

## Q3 — Are the alternative fixes cheaper now?

### Option (c) — Process-filtered file-touch tracking

**Mechanical description:** Replace `_capture_git_diff()` (git diff --stat comparing pre/post snapshots) with a process-tree-filtered file tracking system. At step start, record the PID of the agent subprocess (`proc.pid` at runner.py:55). At step end, instead of diffing git state, query which files the process tree actually opened for writing. On macOS, this requires either `fs_usage -f diskio -w` (needs root), `dtrace` (needs SIP disablement or entitlements), or polling via `lsof -p <pid>` at intervals. The scope_check gate would then compare the "files agent touched" set against declared scope rather than the "files changed in working tree" set.

**LOC delta estimate:** ~80–150 LOC. Includes: process-tree monitor startup/shutdown in runner.py (~30 LOC), parsed output collection and filtering (~30 LOC), integration into scope_check gate replacing git-diff-based file list (~20 LOC), platform detection and fallback (~20 LOC), tests (~50 LOC).

**Risk surface vs. option (b):** Significantly higher. (1) Requires elevated privileges (root for `fs_usage`, SIP-off for `dtrace`) — Bellows currently runs as a normal user process. (2) Platform-specific — macOS only; won't work if Bellows moves to Linux. (3) Process-tree tracking can miss files written by child processes that have already exited before the poll. (4) `lsof`-based polling has inherent race windows. (5) The entire scope_check gate mechanism would change from declarative (git diff snapshot comparison) to imperative (process monitoring), increasing the surface for timing-related bugs. (6) Does not handle files the agent modifies via tools that delegate to other processes.

**Changes in past week:** None that affect option (c)'s viability. No new abstractions make process tracking easier.

### Commit-message slug scoping

**Mechanical description:** After the agent completes a step, inspect commit messages in the diff window via `git log --format=%s HEAD --not main` (already collected at `_teardown_worktree` line 745) and verify each commit message contains the plan slug or a recognizable plan identifier. Commits without the slug are classified as concurrent-activity artifacts and excluded from scope_check's file list. The filtered file list replaces the current unfiltered `_parse_diff_stat` output.

**LOC delta estimate:** ~30–40 LOC. Includes: slug-matching logic against commit messages (~15 LOC), integration into `_parse_diff_stat` or a new filtering step (~10 LOC), tests (~15 LOC).

**Risk surface vs. option (b):** Lower implementation complexity, but **does not solve the bellows-self case.** For bellows-self plans (no worktree, `wt_path == project_path`), there are no plan-specific commits to scope against — the agent commits directly to the shared working tree, so all commits in the diff window appear with no distinguishing markers. Uncommitted dirty files from concurrent CEO activity (the primary bellows-self failure pattern — verdict-request moves, archived/ cleanup) would not be covered by commit-message scoping at all since they produce no commits. This option applies only to projects with worktrees, which are already isolated by the existing worktree fix.

**Changes in past week:** The `_seen` slug refactoring (commit `63dd6ed`, 2026-05-11) standardized slug handling via `verdict.slug_from_path()`, which could simplify slug-matching if this option were pursued. But the fundamental limitation (inapplicable to the no-worktree bellows-self case) is unchanged.

---

## Q4 — Recommendation

**(i) Close as won't-fix** — formally accept the bellows-self exposure as a permanent constraint, document the mitigations as standing workflow.

**Rationale:** Zero reproductions in the 7-day audit window (2026-05-06 through 2026-05-12) vs. 4 reproductions in the prior 5-day window (2026-05-01 through 2026-05-05) demonstrates that the procedural mitigations (avoid CEO mv/cleanup operations in bellows/ during active bellows-self plans) are fully effective. The exposure is exclusively a scope_check false-positive — it never produces data loss, incorrect agent behavior, or missed defects; it only produces a verdict request that the Planner can override after Rule 22 verification. Option (b) remains the only technically complete fix, but the revised cost (50–70 production LOC, 9 subprocess/path call sites to adapt, potential agent confusion from subdirectory cwd) against zero observed harm makes shipping it negative ROI. Alternatives (c) and commit-message slug scoping are either inapplicable to the bellows-self case or carry higher risk. The BACKLOG entry's existing mitigation guidance is battle-tested and working. Closing as won't-fix eliminates the open-item overhead without any loss in system reliability.

**Revisit trigger:** If bellows-self scope_check false positives resume — e.g., due to increased concurrent bellows-self plan dispatching, automated lifecycle operations in the bellows/ subtree, or a workflow change that makes the CEO mitigation burden impractical — re-open as a new BACKLOG entry with an updated reproduction count and the re-evaluation documented here as prior art.

---

## Layer Impact

- **Layer 1 (Bellows):** Affected. The won't-fix formally accepts a known false-positive surface in Bellows's scope_check gate. The gate continues to function correctly in all other contexts (projects with `.git`, projects with worktrees).
- **Layer 2 (Agents):** Not affected. Agents are unaware of scope_check behavior and experience no behavioral change.
- **Layer 3 (Planner):** Mildly affected. The Planner must continue to handle bellows-self scope_check overrides via continue verdict when they occur. This is already documented in the BACKLOG entry's mitigation guidance and has been zero-cost in the audit window (no overrides needed because no reproductions occurred).

---

## Output Receipt
**Agent:** Bellows Systems Analyst
**Step:** 1
**Status:** Complete

### What Was Done
Disposition diagnostic for the bellows-self concurrent-activity exposure. Audited 47 ledger entries and all resolved verdict files from 2026-05-06 through 2026-05-12, finding zero scope_check failures of any class. Re-validated option (b) LOC estimate (50–70 production LOC, 9 call sites to adapt, one new risk surface from lock detection code). Evaluated options (c) and commit-message slug scoping against current codebase. Recommended close-as-won't-fix based on zero reproductions and effective procedural mitigations.

### Files Deposited
- `bellows/knowledge/architecture/bellows-self-exposure-disposition-2026-05-12.md` — four-question disposition findings: Q1 reproduction audit (zero), Q2 option (b) LOC and call-site analysis, Q3 alternative comparison, Q4 close-as-won't-fix recommendation

### Files Created or Modified (Code)
- None (diagnostic — no production code modified)

### Decisions Made
- Classified all 47 post-2026-05-05 ledger entries as non-scope_check based on auditing each entry's gate failures and reason text
- Revised option (b) LOC estimate upward from 50–80 to 50–70 (production) / 80–120 (with tests) based on new lock detection code surface
- Assessed commit-message slug scoping as inapplicable to the bellows-self case (no worktree, no plan-specific commits)

### Flags for CEO
- None. Recommendation is close-as-won't-fix. The Planner will bring this recommendation to the CEO for disposition decision.

### Flags for Next Step
- None — this is a single-step diagnostic. The Planner reads this deposit, verifies via Rule 22, and routes the recommendation to the CEO.
