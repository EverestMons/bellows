# Worktree vs. Serialize-Capture — Candidate Implementation Designs

**Date:** 2026-05-03 | **Plan:** diagnostic-worktree-candidate-designs-2026-05-03 | **Step:** 1

---

## Candidate 1: Per-Plan Git Worktree

### D1 — Mechanism

When Bellows dispatches a plan (in `run_plan`, after the plan claim at line 240 and before the pre-diff capture at line 265), it runs `git worktree add` to create a fresh copy of the project's working tree rooted at a temporary directory. The `claude -p` subprocess and all four `_capture_git_diff` calls use this worktree path as their `cwd` instead of the shared project root. The worktree has its own git index (stored in `.git/worktrees/<name>/index`) and its own copy of every tracked file, so `git diff --stat` inside it sees only files dirtied by the plan's own agent. After the plan's final step completes (after the last `_capture_git_diff` at line 339 or 281), Bellows cherry-picks any commits the agent made back onto the main checkout's HEAD, copies uncommitted files back to the main working tree, and runs `git worktree remove` to tear down the worktree.

### D2 — Code Change Surface

| File | Function | Existing line range (Phase A) | Change type | New behavior |
|------|----------|-------------------------------|-------------|--------------|
| `bellows.py` | `run_plan` | A3: lines 240–265 (between plan claim and pre-diff) | Add | Insert worktree creation: `git worktree add <wt_path> HEAD --detach`. Store `wt_path` as local variable. |
| `bellows.py` | `run_plan` | A1: call site 1, line 265 | Modify | Change `_capture_git_diff(project_path)` → `_capture_git_diff(wt_path)`. Pre-diff now reads worktree state. |
| `bellows.py` | `run_plan` | A1: call site 2, line 281 | Modify | Change `_capture_git_diff(project_path)` → `_capture_git_diff(wt_path)`. Post-diff now reads worktree state. |
| `bellows.py` | `run_plan` | A2: line 267 (`runner.run_step`) | Modify | Change `project_path` → `wt_path` in the `runner.run_step` call so `claude -p` runs with `cwd=wt_path`. |
| `bellows.py` | `run_plan` | A1: call site 3, line 321 | Modify | Change `_capture_git_diff(project_path)` → `_capture_git_diff(wt_path)`. Loop pre-diff. |
| `bellows.py` | `run_plan` | A1: call site 4, line 339 | Modify | Change `_capture_git_diff(project_path)` → `_capture_git_diff(wt_path)`. Loop post-diff. |
| `bellows.py` | `run_plan` | A2: line 323 (`runner.run_step` in loop) | Modify | Change `project_path` → `wt_path` for continuation steps. |
| `bellows.py` | `run_plan` | A3: after line 341 (loop) or 283 (single-step), before pause/close branches | Add | Insert worktree teardown: cherry-pick commits, copy uncommitted files, `git worktree remove`. |
| `bellows.py` | Module top-level | A5: near line 17 (constants) | Add | Add helper functions: `_create_worktree(project_path, slug)` and `_teardown_worktree(project_path, wt_path, slug)`. |
| `bellows/.gitignore` | — | A6: line 12 (`.bellows-cache/`) | No change | Not needed if using `/tmp/` location. Would need `.bellows-worktrees/` added only for in-tree location. |

### D3 — Specific Design Decisions

#### (a) Worktree location

**Recommendation: in-tree `<project>/.bellows-worktrees/<slug>/`.** This contradicts the CEO's `/tmp/` preference. Rationale:

- Phase A4 (`.git/` shared state): `git worktree add` creates the worktree directory and registers it in `.git/worktrees/`. Git uses hardlinks for object storage efficiency when the worktree is on the same filesystem as the repo. On macOS, `/tmp` resolves to `/private/tmp`, which is on the same APFS volume as `/Users/` in the default single-volume layout — so hardlinking would typically work. However, this is a machine-specific assumption: any encrypted external drive, Docker mount, or non-standard partition layout would break it silently (git falls back to full copies, doubling disk usage per worktree with no warning).
- Phase A6 (gitignore): Adding `.bellows-worktrees/` to `bellows/.gitignore` follows the exact pattern already used for `.bellows-cache/` (line 12). This is a one-line change with an established convention.
- `/tmp/` semantics: macOS clears `/tmp` on reboot. If Bellows is interrupted (crash, SIGKILL, machine restart) mid-plan, the worktree directory disappears but the `.git/worktrees/<name>/` registration remains, leaving a dangling worktree entry that git complains about until `git worktree prune` is run. With in-tree location, the worktree directory and registration are on the same filesystem and survive reboots — teardown cleanup can be attempted on the next Bellows startup.
- In-tree recovery: If Bellows crashes mid-plan, an in-tree worktree persists. On the next `_rescan`, Bellows could detect orphaned `.bellows-worktrees/<slug>` directories (matching `in-progress-` plan slugs) and clean them up. With `/tmp/`, the directory is gone but the git registration is stale — a harder cleanup path.

**If the CEO prefers `/tmp/` despite these trade-offs**, the design works identically — only the base path changes. The in-tree vs. `/tmp/` choice has no impact on correctness, only on crash-recovery ergonomics and the gitignore addition.

#### (b) Branch strategy and merge-back

**Decision: detached HEAD with cherry-pick on cleanup.**

- Phase A3 (lifecycle): `run_plan` runs within a single thread for its entire duration (lines 194–401). The worktree exists from creation (between lines 240–265) to teardown (after the last gate check). During this window, the agent may make zero, one, or multiple commits.
- Why detached HEAD: `git worktree add <path> HEAD --detach` creates a worktree at the current HEAD without creating or checking out a branch. This avoids the "branch already checked out" error when multiple concurrent worktrees are created from the same base ref. Per-plan named branches (`bellows-wt-<slug>`) would conflict if two plans with the same slug were dispatched (unlikely but possible during re-claims). Detached HEAD has no name collision vector.
- Cherry-pick on cleanup: After the plan completes, `_teardown_worktree` runs `git log --format=%H HEAD --not main` from within the worktree to collect commits made by the agent, then runs `git cherry-pick <sha>...` from the main checkout. Cherry-pick applies each commit as a new commit on main's HEAD.
- Concurrent cherry-pick conflict: If two worktrees are torn down simultaneously and both have commits touching the same files, the second cherry-pick will encounter a merge conflict. This is detectable (non-zero exit from `git cherry-pick`), and Bellows can handle it by aborting the cherry-pick and logging the conflict for CEO attention. However, this scenario requires two agents to have independently modified the same file — which is itself a logic bug (the Planner should not assign overlapping file scopes). The cherry-pick conflict surfaces the coordination failure rather than silently merging.

#### (c) Uncommitted change handling

**Decision: copy back to main checkout.**

- Phase A3 (lifecycle): The diagnostic-agent pattern is the primary consumer here. Diagnostic agents deposit findings files (e.g., `knowledge/research/*.md`) and frequently do NOT commit them — the plan step completes with uncommitted files in the working tree. The current Bellows flow works because these files land directly in the shared working tree.
- With worktrees, uncommitted files exist only in the worktree directory. On teardown, `_teardown_worktree` must: (1) run `git status --porcelain` in the worktree to identify uncommitted files, (2) copy each dirty file from `wt_path/<rel_path>` to `project_path/<rel_path>`, (3) then run `git worktree remove`.
- Why NOT auto-commit: Auto-committing before merge-back would create commits the agent did not intend, polluting git history with "worktree cleanup" commits containing half-finished work.
- Why NOT block cleanup: Blocking teardown on uncommitted files would leave the worktree alive indefinitely. Bellows has no human operator to resolve the block — it must be autonomous.

#### (d) `.bellows-cache` access

Phase A4 confirms `.bellows-cache/` is accessed via absolute path constant `BELLOWS_ROOT / ".bellows-cache"` (bellows.py:18). The bootstrap prompt references `shadow_prompt_path`, which is the absolute path to `.bellows-cache/<slug>.pristine` (Phase A4: `_shadow_path()` at bellows.py:96-104 returns `SHADOW_CACHE_DIR / f"{canonical}.pristine"`).

**Works without modification.** The agent subprocess (`claude -p`) running with `cwd=wt_path` receives the bootstrap prompt containing the absolute path `/Users/marklehn/Desktop/GitHub/bellows/.bellows-cache/<slug>.pristine`. The agent reads this path directly — it is not relative to `cwd`. The file exists on the real filesystem regardless of where the worktree lives. No copy or symlink needed.

#### (e) `bellows.db` access

Phase A4 confirms `bellows.db` path is the absolute constant `BELLOWS_ROOT / "bellows.db"` (bellows.py:17). `record_run()` at bellows.py:152-171 opens a new `sqlite3.connect(db_path)` per call using this absolute path.

**Works without modification.** The DB path is not derived from `cwd` or `project_path` — it uses the module-level constant. Worktree-internal git operations (agent's `git add`, `git commit`) affect the worktree's own index and HEAD, not the main checkout's. These operations do not touch `bellows.db`.

#### (f) Always-worktree overhead

Estimated per-plan overhead:
- `git worktree add <path> HEAD --detach`: For a repo the size of bellows (~100 tracked files, ~50 MB working tree), this takes approximately 0.3–0.8 seconds. Git creates the worktree directory, checks out all tracked files (hardlinked objects, new working copies), and registers the worktree in `.git/worktrees/`. On SSD (standard macOS), this is dominated by file creation I/O.
- `git worktree remove <path>`: Approximately 0.1–0.3 seconds. Removes the directory and deregisters.
- Cherry-pick per commit: ~0.1–0.2 seconds per commit for small commits.
- Uncommitted file copy-back: Negligible (a few `shutil.copy2` calls).

**Total overhead: ~0.5–1.5 seconds per plan dispatch** (creation + teardown + cherry-pick). Current per-plan overhead for the same lifecycle segment (claim + shadow write, lines 236-240): ~0.05 seconds. So worktree adds roughly 0.5–1.5 seconds.

**Acceptable for sequential plans.** A typical plan step runs for 60–300 seconds (`runner.run_step` timeout, Phase A2). An additional 1–1.5 seconds is <1% overhead. For sequential plans (no parallelism benefit to protect), this is negligible.

#### (g) Failure modes during creation

- **Disk full:** `git worktree add` fails with a filesystem error. Bellows detects non-zero exit code. **Proposed handling:** Fall back to running without a worktree — pass `project_path` as before. Log a warning. The plan executes in the legacy shared-tree mode. This degrades isolation but doesn't block execution.
- **Locked git index:** If another process holds `.git/index.lock`, `git worktree add` may fail. Phase A3 shows no explicit index locking by Bellows. The lock would come from a concurrent `git` operation (agent's `git add` in another thread). **Proposed handling:** Retry once after 2-second sleep (matching the existing stagger in Phase A5, bellows.py:593). If retry fails, fall back to shared-tree mode.
- **Branch already checked out:** Not applicable with detached HEAD strategy — `--detach` does not check out a branch.
- **Stale worktree registration:** If a prior crash left a `.git/worktrees/<name>` entry without the actual directory, `git worktree add` with the same name may fail. **Proposed handling:** Run `git worktree prune` once at Bellows startup (in `Bellows.__init__`) to clean stale entries.

### D4 — Phase 1A Literal Walk-Through

With per-plan worktrees live:

**Setup:**
- 15:44:22 — B dispatched. Bellows creates worktree at `.bellows-worktrees/executable-backlog-hygiene-sweep-2026-04-30/` from HEAD. B's `claude -p` runs with `cwd=<wt_B>`. B's `pre_diff` captured in `<wt_B>` (clean).
- 15:44:46 — A dispatched. Worktree at `.bellows-worktrees/parallel-1-executable-deposit-exists-directory-paths-2026-04-30/` from HEAD. A's `claude -p` runs with `cwd=<wt_A>`. A's `pre_diff` captured in `<wt_A>` (clean).
- 15:44:48 — C dispatched. Worktree at `.bellows-worktrees/parallel-1-executable-ledger-pause-reason-code-2026-04-30/` from HEAD. C's `claude -p` runs with `cwd=<wt_C>`. C's `pre_diff` captured in `<wt_C>` (clean).

**Execution:**
- 15:44:48–15:47:14 — C's agent edits `bellows.py`, `verdict.py`, `tests/test_verdict.py` **in `<wt_C>` only**. These edits are NOT visible in `<wt_A>` or `<wt_B>` or the main checkout.
- 15:46:15 — A's agent commits `gates.py`, `tests/test_gates.py` **in `<wt_A>`**.
- ~15:46:21 — A's `post_diff` captured **in `<wt_A>`**:
  - `git diff --stat --relative -- .` with `cwd=<wt_A>`.
  - `<wt_A>` has its own index. A committed at 15:46:15 — `gates.py` and `tests/test_gates.py` are clean.
  - C's dirty files (`bellows.py`, `verdict.py`) exist only in `<wt_C>`, NOT in `<wt_A>`.
  - **A's `files_changed`: `[]`** (no dirty files in A's worktree; A's own files were committed, the dev-log may appear if uncommitted).

  More precisely — A committed `gates.py`, `tests/test_gates.py`, and `knowledge/development/deposit-exists-directory-paths-dev-log-2026-04-30.md`. If A's agent left any files uncommitted, those would appear. But C's files do NOT appear. **No contamination.**

- 15:46:21 — B's agent commits `PROJECT_STATUS.md`, `BACKLOG.md` **in `<wt_B>`**.
- ~15:46:27 — B's `post_diff` captured **in `<wt_B>`**:
  - `git diff --stat --relative -- .` with `cwd=<wt_B>`.
  - B committed at 15:46:21. B's committed files are clean.
  - C's dirty files exist only in `<wt_C>`, NOT in `<wt_B>`.
  - **B's `files_changed`: `[]`** (or only B's own uncommitted files, if any). **No contamination.**

- 15:47:14 — C commits its files **in `<wt_C>`**.
- ~15:47:20 — C's `post_diff` captured **in `<wt_C>`**:
  - C committed `bellows.py`, `verdict.py`, `tests/test_verdict.py`. They are now clean in `<wt_C>`.
  - **C's `files_changed`: `[]`** (or only C's uncommitted dev-log). **No contamination.**

**Result: No plan's `files_changed` contains any sibling's files. The worktree candidate defeats the literal 2026-04-30 incident vector.**

### D5 — Coverage Matrix

| # | Contamination sub-vector | Status | Explanation |
|---|--------------------------|--------|-------------|
| (i) | Sibling's uncommitted dirty files in victim's post_diff | **Solved** | Each worktree has its own working tree copy (Phase A4e). Dirty files in `<wt_C>` are invisible to `git diff` run with `cwd=<wt_A>` (D4 walk-through). |
| (ii) | Sibling's just-committed files in victim's post_diff | **Solved** | Commits in `<wt_C>` go to C's detached HEAD. A's `git diff` reads A's own HEAD and index — it does not see C's commits (Phase A4d: separate index per worktree). |
| (iii) | Sibling's `git add`-staged-but-uncommitted files | **Solved** | Each worktree has its own index (`.git/worktrees/<name>/index` per Phase A4d). Staging in `<wt_C>` does not affect `<wt_A>`'s index. |
| (iv) | Parallel-group concurrent commits | **Solved** | Commits go to separate detached HEADs. No interaction until cherry-pick merge-back, which happens after all diffs are captured (D3b). |
| (v) | Sequential-but-concurrent dispatch (Plan B's case) | **Solved** | Always-worktree means B gets its own worktree even though it's not in a parallel group. Same isolation as (i)–(iv). |
| (vi) | Test-suite parallel runs touching shared fixtures | **Partial** | If an agent runs `pytest` inside its worktree, tests execute against the worktree's file copies — isolated from siblings. However, tests that access external resources (databases, network, `/tmp` fixtures) are NOT isolated by worktrees. Worktrees isolate git-tracked files only. |
| (vii) | Bellows internal writes during a step (DB updates by another thread) | **N/A** | `bellows.db` is accessed via absolute path (Phase A4a). DB writes by other threads do not affect any worktree's git state. SQLite handles concurrent access internally. |

### D6 — New Failure Modes

| # | Scenario | Classification | Description |
|---|----------|----------------|-------------|
| 1 | Worktree creation fails (disk full) | **Unlikely / Recoverable** | `git worktree add` needs disk space for a full working tree copy. For bellows (~50 MB), unlikely on a dev machine. If it occurs, fallback to shared-tree mode (D3g). Recovery: automatic. |
| 2 | Cherry-pick merge conflict on teardown | **Unlikely / Recoverable** | Two agents modify the same file independently, and their commits conflict during cherry-pick. Detectable via non-zero exit code. Recovery: abort cherry-pick, leave commits in worktree, log error for CEO. The worktree persists until manual resolution. |
| 3 | Agent's pytest can't find test files due to cwd shift | **Likely / Recoverable** | Agents use `cwd=wt_path`. If tests import from relative paths or use `conftest.py` fixtures that assume the main checkout path, they may fail. Recovery: the worktree is a full checkout — `conftest.py` and all test files are present. Standard `pytest` discovery from project root works. Only tests with hardcoded absolute paths would break. |
| 4 | Uncommitted files lost if teardown crashes mid-copy | **Unlikely / Catastrophic** | If Bellows crashes between starting copy-back and completing it, some uncommitted files may be in the worktree (which persists in-tree) but not yet in the main checkout. With in-tree worktrees, the files are recoverable from `.bellows-worktrees/<slug>/`. With `/tmp/`, the files are lost on reboot. |
| 5 | Stale worktree registrations after crash | **Likely / Recoverable** | If Bellows is killed mid-plan, the worktree directory and `.git/worktrees/<name>` registration persist. Next `git worktree add` with the same name fails. Recovery: `git worktree prune` at startup (D3g). |
| 6 | Agent reads files outside worktree via absolute path | **Unlikely / Recoverable** | If an agent uses absolute paths (e.g., reads `/Users/.../bellows/bellows.py` instead of `./bellows.py`), it reads the main checkout, not the worktree. The agent's writes still go to the worktree (via relative paths from `cwd`). This creates an asymmetric view but does not cause diff contamination — the diff is captured in the worktree regardless. |
| 7 | Concurrent worktree creation under git index lock | **Unlikely / Recoverable** | If two `git worktree add` calls execute simultaneously, they may contend on `.git/index.lock`. Git's internal locking handles this — the second call waits or fails. Recovery: retry with backoff (D3g). |

### D7 — Test Surface

| Test File | Existing tests needing updates | New tests needed |
|-----------|-------------------------------|------------------|
| `tests/test_bellows.py` | **`test_capture_git_diff_uses_relative_pathspec`** (A7: lines 491-503): Currently mocks `subprocess.run` and checks argv. No signature change to `_capture_git_diff` itself, so mock remains valid. BUT any tests that mock `_capture_git_diff` and assert it's called with `project_path` will need updating if `run_plan` passes `wt_path` instead. Scan all `run_plan` tests that patch `bellows._capture_git_diff` — Phase A7 confirms all existing tests mock it, so mocks remain valid (they don't assert the `project_path` arg). No updates needed to existing mocks. | **New:** (1) `test_worktree_created_before_pre_diff` — assert `git worktree add` is called between plan claim and first `_capture_git_diff`. (2) `test_worktree_torn_down_after_final_diff` — assert `git worktree remove` is called after the last gate check. (3) `test_worktree_path_passed_to_runner` — assert `runner.run_step` receives `wt_path`, not `project_path`. (4) `test_worktree_fallback_on_creation_failure` — assert fallback to `project_path` if `git worktree add` fails. (5) `test_cherry_pick_on_teardown` — assert commits from worktree are cherry-picked to main. (6) `test_uncommitted_files_copied_back` — assert dirty files in worktree are copied to main checkout on teardown. |
| `tests/test_runner.py` | None. Phase A7 confirms `run_step` takes `project_path` as a parameter (A2: line 27). Worktree passes `wt_path` as this parameter — the runner's interface does not change. Existing tests that mock subprocess.Popen with `cwd=project_path` remain valid (they pass their own test paths). | None needed — runner is worktree-agnostic. |
| `tests/test_gates.py` | None. Gates receive `files_changed` as a parameter (A7: lines 172-181). The source of `files_changed` changes (worktree diff instead of shared-tree diff) but the gates interface does not. | None needed — gates are worktree-agnostic. |
| `tests/test_verdict.py` | None. Verdict posting uses absolute paths (Phase A4c). | None needed. |
| `tests/test_cleanup_verdicts.py` | None. | None needed. |
| `tests/test_consume_verdicts.py` | None. | None needed. |
| **New file**: `tests/test_worktree.py` | — | (1) `test_create_worktree_returns_valid_path` — integration test: create worktree, verify path exists and contains tracked files. (2) `test_worktree_isolation_git_diff` — integration test: dirty a file in main checkout, create worktree, verify `git diff` in worktree does NOT show the dirty file. (3) `test_teardown_removes_worktree_directory` — verify directory is gone after teardown. (4) `test_teardown_cherry_picks_commits` — make a commit in worktree, teardown, verify commit appears on main HEAD. (5) `test_teardown_copies_uncommitted_files` — write a file in worktree without committing, teardown, verify file appears in main checkout. (6) `test_concurrent_worktree_creation` — create two worktrees simultaneously, verify both succeed. (7) `test_worktree_prune_on_startup` — create a stale registration, run prune, verify clean state. |

### D8 — Live Smoke Test Design

**Canary plan shapes:**

- **Plan X** (`parallel-99-canary-worktree-X`): Step 1 writes `knowledge/research/canary-X-marker.txt` with content "X was here", then `time.sleep(30)`, then commits. The 30-second sleep ensures X's file is dirty in whatever workspace it operates in for a long window.
- **Plan Y** (`parallel-99-canary-worktree-Y`): Step 1 writes `knowledge/research/canary-Y-marker.txt` with content "Y was here", then commits immediately (no sleep), then `time.sleep(30)` after commit.

**Timing guarantee:** Plans X and Y are dispatched as a `parallel-99` group with 2-second stagger (Phase A5: bellows.py:593). Y commits its file ~5–10 seconds after dispatch. X's agent has not yet committed (30-second sleep). X's `post_diff` is captured after X's sleep + commit (~35 seconds after dispatch). At X's `post_diff` capture moment in unfixed code, Y has already committed (Y's file is clean in the shared tree) BUT X's file was dirty for 30 seconds — more importantly, the reverse: at Y's `post_diff` capture (~12 seconds after dispatch), X's `canary-X-marker.txt` is DIRTY in the shared tree (X hasn't committed yet). **In unfixed code, Y's `files_changed` would include `canary-X-marker.txt`.** With worktrees, Y's `git diff` runs in `<wt_Y>` and cannot see `<wt_X>`'s dirty file.

**Falsification criterion:** If, after implementing worktrees, Plan Y's verdict request includes `canary-X-marker.txt` in `files_changed` or `scope_check` failure, the worktree candidate failed. If Y's `files_changed` contains only `canary-Y-marker.txt` (or is empty if Y committed), the candidate passed.

**Canary execution recommendation: Run as a separate post-implementation diagnostic, NOT as part of the implementation plan's QA.** Rationale: Phase A1 + A3 + A5 establish that a canary dispatched from within a Bellows-executed plan creates structural awkwardness — the canary plans would be dispatched by Bellows alongside the diagnostic's own execution threads, and the diagnostic agent cannot observe Bellows internal state (verdict request content, `files_changed` lists) from within its own `claude -p` subprocess. The prior diagnostic (Phase 1C of the incident timeline) explicitly skipped its canary on these grounds. A separate post-implementation diagnostic dispatched by the Planner (or manually by the CEO) avoids this structural conflict.

---

## Candidate 2: Serialize Git Capture

### D1 — Mechanism

A global mutex (Python `threading.Lock`) is added at module level in `bellows.py`. Every plan thread acquires this lock before capturing its `pre_diff` and holds it through the entire `runner.run_step` call until after its `post_diff` is captured and parsed. This means only one plan step executes at a time — while one thread holds the lock (running `pre_diff` → `claude -p` → `post_diff`), all other plan threads are blocked waiting to acquire it. The lock guarantees that when `git diff --stat` runs for plan A's post_diff, no other plan's agent is running and modifying the shared working tree. All plans still share the same working tree and `.git/` directory.

### D2 — Code Change Surface

| File | Function | Existing line range (Phase A) | Change type | New behavior |
|------|----------|-------------------------------|-------------|--------------|
| `bellows.py` | Module top-level | A5: near line 17 (constants) | Add | Add `_git_capture_lock = threading.Lock()` as a module-level constant. |
| `bellows.py` | `run_plan` | A1: call site 1, line 265 (pre-diff) | Modify | Wrap with `_git_capture_lock.acquire()` before line 265. The lock is acquired BEFORE the pre-diff capture. |
| `bellows.py` | `run_plan` | A1: call site 2, line 281–283 (post-diff + parse + gates) | Modify | `_git_capture_lock.release()` after line 283 (after `_parse_diff_stat` and `gates.check`). The lock covers the entire pre-diff → run_step → post-diff → parse window. |
| `bellows.py` | `run_plan` | A1: call site 3, line 321 (loop pre-diff) | Modify | `_git_capture_lock.acquire()` before line 321. Same pattern as first step. |
| `bellows.py` | `run_plan` | A1: call site 4, line 339–341 (loop post-diff + parse + gates) | Modify | `_git_capture_lock.release()` after line 341. |
| `bellows.py` | `run_plan` | A3: lines 267–269, 323–328 (runner.run_step calls) | No change | `runner.run_step` itself is unchanged — it runs inside the lock window. |

### D3 — Specific Design Decisions

#### (a) Mutex placement

The mutex is acquired and released at these points (citing Phase A1 call sites and Phase A3 lifecycle):

- **First step:** Acquire at line 264 (before `pre_diff = _capture_git_diff(project_path)` at line 265). Release at line 284 (after `gate_result = gates.check(...)` at line 283). This wraps: pre-diff (265) → `runner.run_step` (267) → DB record (274-278) → post-diff (281) → diff parse (282) → gate check (283).
- **Loop steps:** Acquire at line 320 (before `pre_diff = _capture_git_diff(project_path)` at line 321). Release at line 342 (after `gate_result = gates.check(...)` at line 341). Same window.
- **Error handling:** The acquire/release MUST use `try/finally` to ensure the lock is released if `runner.run_step` raises an exception or times out (Phase A2: timeout at runner.py:115-119 raises after `proc.kill()`). Without `finally`, a timed-out step would hold the lock forever, deadlocking all other plan threads.

#### (b) Lock granularity

**Decision: per-project mutex.**

- Phase A4 (shared state inventory): Each project has its own working tree (Phase A4e). Two plans targeting different projects (e.g., `bellows/` vs. `forge/`) have separate working trees — their diffs cannot contaminate each other.
- Phase A5 (threading model): Bellows dispatches plans from `PlanHandler` instances, one per watched project (bellows.py:491 context). Multiple projects can have concurrent plans.
- A global single mutex would serialize ALL plan execution across ALL projects — unnecessarily blocking `forge/` plans while a `bellows/` plan runs.
- **Implementation:** `_git_capture_locks: dict[str, threading.Lock] = {}` with a small `_locks_lock = threading.Lock()` to protect dict access. `run_plan` would do: `with _locks_lock: lock = _git_capture_locks.setdefault(project_path, threading.Lock())` then use `lock` for the capture window.

#### (c) Deadlock analysis

- Phase A5: The only existing lock is `_active_lock` (bellows.py:550), which protects `_active_count` in `_run_tracked` (lines 554-560). This lock is acquired at the START of `_run_tracked` (before `run_plan`) and at the END (after `run_plan`). It is never held during `run_plan` execution.
- The new `_git_capture_lock` is acquired INSIDE `run_plan` (lines 264/320).
- **No nested locking:** `_active_lock` and `_git_capture_lock` are never held simultaneously. `_active_lock` is released before `run_plan` starts, and reacquired after it returns. Therefore, no circular wait condition exists.
- **Self-deadlock:** Python's `threading.Lock` is non-reentrant. If `run_plan` somehow called itself recursively, it would deadlock. Phase A3 confirms `run_plan` is not recursive — it's a straight-line function called once per thread. No self-deadlock risk.
- **Multi-step loop:** The lock is released after each step's gate check (line 284/342) and reacquired at the next loop iteration (line 320). Between release and reacquire, other threads CAN run their steps. The lock does NOT span the entire multi-step plan — it spans each individual step. This means inter-step gaps (pause checks at lines 291-315) do NOT hold the lock.

#### (d) Parallelism collapse

**Confirmed: under serialize-capture, the `parallel-N-` group prefix retains NO execution-parallelism benefit.**

- Phase A5 (handle_parallel_group, bellows.py:590-595): The group dispatches N threads that each call `run_plan`. Each `run_plan` acquires `_git_capture_lock` before its first `_capture_git_diff` call. Since the lock wraps the entire pre-diff → run_step → post-diff window (which is the vast majority of each step's execution time), only one thread can be inside this window at a time.
- The 2-second stagger (Phase A5: bellows.py:593) means threads start 2 seconds apart. The first thread acquires the lock at its pre-diff (line 265). The second thread, starting 2 seconds later, reaches line 265 and blocks on `_git_capture_lock.acquire()`. It waits until the first thread's step completes and releases the lock at line 284/342.
- **Effective behavior:** Parallel siblings execute sequentially. The `parallel-N-` prefix becomes purely a grouping label — the execution order is first-to-acquire, then second, then third. Total wall-clock time for N parallel siblings ≈ sum of individual step times, NOT max.
- **Inter-step gaps:** Between steps (pause check, verdict post), the lock is released. If two plans from different projects happen to interleave at this point, they can briefly overlap. But within a single project, siblings serialize fully.

#### (e) Mutex timeout behavior

**Decision: no timeout on the mutex itself.**

- Phase A2 (timeout handling): `runner.run_step` has an inactivity timeout (configurable, default 300s, currently 1800s per config). If the agent produces no output for `timeout` seconds, `proc.kill()` is called (runner.py:115-119). There's also a wall-clock cap at `timeout * 10` (runner.py:122-127, so 18000s = 5 hours at current config).
- If one step holds the mutex for the full 1800s inactivity timeout, all other plan threads in the same project are blocked for 1800s. If the step hits the wall-clock cap (18000s), other threads wait 18000s.
- **Why no mutex timeout:** Using `_git_capture_lock.acquire(timeout=X)` would mean that if a step takes longer than X seconds, the next thread's acquire returns `False`, and Bellows must decide: (a) skip diff capture entirely (losing `files_changed` data), or (b) capture diff without the lock (reintroducing the contamination bug). Neither is acceptable. The mutex's purpose is correctness — a timeout would trade correctness for liveness.
- **Mitigation via existing timeout:** The runner's inactivity timeout (1800s) and wall-clock cap (18000s) bound the maximum lock-hold duration. If the step times out, `runner.run_step` returns (with timeout status), and the `finally` block releases the lock. The worst case is one peer thread blocked for up to 18000s — not a deadlock, but a severe liveness degradation.

### D4 — Phase 1A Literal Walk-Through

With serialize-capture (per-project mutex) live:

**Setup:**
- 15:44:22 — B dispatched. Thread B reaches line 264 → acquires `_git_capture_lock`. B's `pre_diff` captured (line 265). B's `runner.run_step` starts (line 267). **Lock held by B.**
- 15:44:46 — A dispatched. Thread A reaches line 264 → **blocks on `_git_capture_lock.acquire()`**. A cannot proceed until B releases.
- 15:44:48 — C dispatched. Thread C reaches line 264 → **blocks on `_git_capture_lock.acquire()`**. C cannot proceed until A releases (and A cannot proceed until B releases).

**Execution (serialized):**
- 15:44:22–~15:46:27 — B runs alone. B's agent edits and commits `PROJECT_STATUS.md`, `BACKLOG.md` at 15:46:21. B's `post_diff` captured. B's `files_changed` computed. **B releases lock at ~15:46:27.**
  - B's `files_changed`: Only B's own files. **No contamination** (no other agent was running).
- ~15:46:27 — A acquires the lock (was waiting since 15:44:46). A's `pre_diff` captured. A's `runner.run_step` starts. **Lock held by A.**
  - Note: C is still blocked.
  - A's agent edits and commits `gates.py`, `tests/test_gates.py`. A's `post_diff` captured. A's `files_changed` computed. **A releases lock.**
  - A's `files_changed`: Only A's own files. **No contamination** (C was blocked, never started editing).
- After A releases — C acquires the lock. C's `pre_diff` captured. C's `runner.run_step` starts. C's agent edits `bellows.py`, `verdict.py`, `tests/test_verdict.py`. C commits. C's `post_diff` captured. C's `files_changed` computed. C releases lock.
  - C's `files_changed`: Only C's own files. **No contamination.**

**Result: No plan's `files_changed` contains any sibling's files. The serialize-capture candidate defeats the literal 2026-04-30 incident vector.**

**Critical difference from the actual incident:** The actual timeline had all three agents running concurrently (15:44:22–15:47:20, ~3 minutes total wall-clock). Under serialize-capture, the three plans run sequentially: B ~2 minutes, then A ~1.5 minutes, then C ~2.5 minutes ≈ ~6 minutes total wall-clock. The incident is defeated by elimination of concurrency.

### D5 — Coverage Matrix

| # | Contamination sub-vector | Status | Explanation |
|---|--------------------------|--------|-------------|
| (i) | Sibling's uncommitted dirty files in victim's post_diff | **Solved** | The mutex ensures only one agent runs at a time (D4 walk-through). No sibling's agent can be editing files while the victim's post_diff is captured. |
| (ii) | Sibling's just-committed files in victim's post_diff | **Solved** | A sibling's commits happen during that sibling's lock-hold window. The victim's post_diff is captured during the victim's lock-hold window — a different, non-overlapping window. Committed files don't appear in `git diff --stat` (they're clean). |
| (iii) | Sibling's `git add`-staged-but-uncommitted files | **Solved** | Staging happens during the sibling's lock-hold window. `git diff --stat` shows unstaged changes, not staged. But even `git diff --cached --stat` (staged changes) would be clean during the victim's window because no sibling is running. |
| (iv) | Parallel-group concurrent commits | **Solved** | Parallel siblings execute serially under the mutex (D3d). No concurrent commits within a project. |
| (v) | Sequential-but-concurrent dispatch (Plan B's case) | **Solved** | The mutex serializes ALL plans in the same project, regardless of whether they were dispatched as a parallel group or sequentially. B's case (non-parallel plan running alongside A and C) is handled identically. |
| (vi) | Test-suite parallel runs touching shared fixtures | **Solved** | Since only one agent runs at a time, test suites from different plans cannot execute concurrently. Shared fixtures are accessed sequentially. |
| (vii) | Bellows internal writes during a step (DB updates by another thread) | **N/A** | `bellows.db` writes use absolute path and separate SQLite connections (Phase A4a). The mutex does not cover DB writes (they're outside the lock window — `record_run` at line 274 is inside the window but uses its own SQLite connection, which is safe). |

### D6 — New Failure Modes

| # | Scenario | Classification | Description |
|---|----------|----------------|-------------|
| 1 | Long step blocks all peers for up to 18000s | **Likely / Recoverable** | A step that runs for the full wall-clock cap (18000s = 5 hours) blocks all other plans in the same project for that duration. Recovery: wait — the timeout mechanism eventually kills the step and releases the lock. But 5 hours of blocked plans is a severe liveness degradation. |
| 2 | Exception in `runner.run_step` without `finally` release | **Unlikely / Catastrophic** | If an unhandled exception propagates past the lock acquisition and the release is not in a `finally` block, the lock is never released. All other project threads deadlock permanently. Recovery: requires Bellows restart. Mitigation: `try/finally` is mandatory (D3a). |
| 3 | Parallel-group wall-clock blowup | **Likely / Recoverable** | A `parallel-3-` group that currently completes in ~max(A,B,C) time now completes in ~A+B+C time. For three 2-minute steps, this is 6 minutes instead of 2. Not a failure per se, but user-visible performance regression. Recovery: none under this candidate — it's inherent to the design. |
| 4 | Thread starvation under lock contention | **Unlikely / Recoverable** | Python's `threading.Lock` does not guarantee FIFO ordering. Under heavy load (5+ concurrent plans in the same project), some threads may be repeatedly preempted. Recovery: use `threading.Condition` or a queue for fairness. Unlikely in practice — Bellows rarely dispatches more than 3 plans simultaneously. |
| 5 | Lock held during pause-check between steps | **Not applicable (by design)** | Per D3a, the lock is released after each step's gate check and reacquired at the next step's pre-diff. The pause-check window (lines 291-315) runs without the lock. However, if the implementation accidentally holds the lock across the pause boundary, it would block ALL other plans for the entire multi-step plan duration (potentially hours during verdict-pending waits). This is a correctness-of-implementation risk, not an inherent design flaw. |
| 6 | `_locks_lock` contention for per-project lock dict | **Unlikely / Recoverable** | The small lock protecting `_git_capture_locks.setdefault()` (D3b) is held for microseconds. No practical contention risk. |

### D7 — Test Surface

| Test File | Existing tests needing updates | New tests needed |
|-----------|-------------------------------|------------------|
| `tests/test_bellows.py` | **`test_handle_parallel_group_stagger`** (A7: lines 386-397): This test verifies that parallel group dispatch includes 2-second sleeps. Under serialize-capture, threads still start with stagger, but they immediately block on the mutex. The test's assertions about `time.sleep` calls remain valid — the stagger still happens; the mutex blocking is additional. **No update needed.** All `run_plan` tests that mock `_capture_git_diff` and `runner.run_step` remain valid — the mutex is transparent when these functions are mocked (the lock is acquired and released around mocked calls, which return instantly). **No updates needed to existing tests.** | **New:** (1) `test_serialize_capture_lock_acquired_before_pre_diff` — assert `_git_capture_lock` is acquired before `_capture_git_diff`. (2) `test_serialize_capture_lock_released_after_gates` — assert lock is released after `gates.check`. (3) `test_serialize_capture_lock_released_on_exception` — assert lock released via `finally` when `runner.run_step` raises. (4) `test_serialize_capture_per_project_lock` — assert two plans on different projects acquire different locks. (5) `test_serialize_capture_blocks_concurrent_same_project` — two threads targeting same project, assert second thread's pre_diff waits until first thread releases. |
| `tests/test_runner.py` | None. Runner is unchanged. | None. |
| `tests/test_gates.py` | None. Gates are unchanged. | None. |
| `tests/test_verdict.py` | None. | None. |
| `tests/test_cleanup_verdicts.py` | None. | None. |
| `tests/test_consume_verdicts.py` | None. | None. |

### D8 — Live Smoke Test Design

**Canary plan shapes:**

- **Plan X** (`parallel-99-canary-serialize-X`): Step 1 writes `knowledge/research/canary-X-marker.txt`, then `time.sleep(30)`, then commits. The sleep ensures X holds the mutex for ~35 seconds (pre-diff + 30s sleep + commit + post-diff).
- **Plan Y** (`parallel-99-canary-serialize-Y`): Step 1 writes `knowledge/research/canary-Y-marker.txt`, commits immediately.

**Timing under serialize-capture:** X and Y are dispatched as `parallel-99` group. X's thread acquires the lock first (2-second stagger means X starts first). Y's thread blocks at lock acquisition. X runs for ~35 seconds. Y's pre-diff capture doesn't start until X releases. Y then runs alone (~10 seconds).

**Falsification criterion under unfixed code:** Without the mutex, Y starts ~2 seconds after X. Y commits after ~5 seconds. X's `post_diff` at ~35 seconds captures X's own working tree — but by then Y has already committed, so Y's file is clean. However, the reverse: at Y's `post_diff` (~7 seconds after dispatch), X's `canary-X-marker.txt` is DIRTY (X hasn't committed yet — X is sleeping). Y's `files_changed` includes `canary-X-marker.txt`. **This is the contamination.**

**Falsification criterion under serialize-capture:** Y's pre-diff doesn't start until X's lock is released (~35 seconds). By then X has committed — X's file is clean. Y runs alone. Y's `files_changed` includes only Y's own file. If Y's verdict request includes `canary-X-marker.txt`, the mutex candidate failed.

**Canary execution recommendation: Run as a separate post-implementation diagnostic.** Same rationale as Candidate 1 (D8): a Bellows-dispatched diagnostic cannot observe its own sibling plans' verdict request content from within its `claude -p` subprocess (Phase 1C gap). Additionally, the serialize-capture canary has a unique observation challenge: under serialize-capture, the canary plans execute sequentially, so the absence-of-contamination result is trivially true — the canary cannot distinguish "the mutex prevented contamination" from "the timing happened to avoid contamination." The canary's value is in confirming the mutex is actually acquired (i.e., that deployment didn't miss a code path). This is better verified by unit tests (D7, test #5) than by a live canary.

---

## Candidate 3 Assessment — Novel Approaches

During the design walk, three potential novel approaches were considered:

1. **Per-thread `GIT_INDEX_FILE` env var:** Each thread sets `GIT_INDEX_FILE=/tmp/bellows-index-<slug>` before running `git diff --stat`. This gives each thread its own index, so staged files don't cross-contaminate. However, Phase A4d establishes that the contamination vector is **working-tree dirty files**, not index-staged files. `git diff --stat` compares the working tree against the index. Even with separate indices, all threads share the same working tree files on disk — a sibling's uncommitted edits to `bellows.py` are still visible to `git diff` regardless of which index is used. **Structurally insufficient for the literal incident vector.** Not included as a candidate.

2. **`git stash` isolation:** Before pre-diff, stash all current changes; after post-diff, pop. This is structurally racy — a sibling could dirty files between the stash-pop and the next stash-save. Also, `git stash` modifies the shared working tree (reverting dirty files), which would interfere with concurrently running agents. **Structurally insufficient and introduces new interference.** Not included.

3. **Reflog-based commit attribution:** Instead of diffing the working tree, attribute changes by reading `git reflog` to identify which commits were made during a plan's execution window, then compute `files_changed` from `git diff-tree` on those commits. This would be immune to dirty-file contamination because it only looks at committed changes. However, it would NOT detect uncommitted files at all — agents that deposit findings without committing (the diagnostic-agent pattern, per D3c) would have empty `files_changed`, breaking the scope_check gate for plans that intentionally leave files uncommitted. Also, Phase A1 confirms the current diff-of-diffs semantics explicitly includes uncommitted changes by design. **Incomplete coverage of the file-change observation contract.** Not included.

No genuinely novel third candidate survived analysis. The two-candidate space (worktree, serialize-capture) is confirmed.

---

## Output Receipt
**Agent:** Bellows Systems Analyst
**Step:** 1
**Status:** Complete

### What Was Done
Produced complete implementation designs for two candidates (per-plan git worktree and serialize git capture) with all eight subsections (D1–D8) per candidate. Each design decision cites specific Phase A observations from the surface map. Both candidates were walked through the literal 2026-04-30 incident timeline with file-level answers confirming they defeat the contamination vector. Three potential novel candidates were evaluated and rejected with structural rationale.

### Files Deposited
- `bellows/knowledge/research/worktree-candidate-designs-2026-05-03.md` — complete design specifications for two candidates, eight subsections each

### Files Created or Modified (Code)
- None (diagnostic — no production code modified)

### Decisions Made
- Worktree location: recommended in-tree `.bellows-worktrees/<slug>/` over CEO's `/tmp/` preference, citing crash-recovery ergonomics and cross-filesystem hardlink risk (D3a)
- Worktree branch strategy: detached HEAD with cherry-pick on cleanup, avoiding branch name collisions (D3b)
- Uncommitted change handling: copy back to main checkout, preserving diagnostic-agent deposit pattern (D3c)
- Serialize-capture lock granularity: per-project mutex, avoiding unnecessary cross-project serialization (D3b for Candidate 2)
- Serialize-capture mutex timeout: no timeout, prioritizing correctness over liveness (D3e for Candidate 2)
- Three novel candidates (per-thread GIT_INDEX_FILE, git stash, reflog attribution) rejected as structurally insufficient
- Both canary smoke tests recommended as separate post-implementation diagnostics, not inline QA

### Flags for CEO
- **Worktree location contradiction:** D3a recommends in-tree over CEO's `/tmp/` preference. If CEO prefers `/tmp/` despite the crash-recovery trade-off, the design works identically — only the base path changes.

### Flags for Next Step
- The third plan in the chain (cost-vs-coverage recommendation) has all design specifications needed to make a selection. Key differentiators: worktree preserves parallelism but adds merge-back complexity; serialize-capture is simpler but collapses parallel execution to serial.
- No surface map gaps were encountered — all design decisions are anchored to Phase A1–A8.
