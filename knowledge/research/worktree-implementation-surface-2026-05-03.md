# Worktree Implementation Surface Map

**Date:** 2026-05-03 | **Plan:** diagnostic-worktree-implementation-surface-2026-05-03 | **Step:** 1

---

## Phase A1 — `_capture_git_diff` and `_parse_diff_stat` Complete Trace

### `_capture_git_diff`

**Definition:** `bellows.py:404-420` (17 lines)

```python
def _capture_git_diff(project_path: str) -> str:
    """Capture git diff --stat output for file change tracking, scoped to the project subtree.

    Uses `--relative -- .` to handle the nested-repo case where project_path is a
    subdirectory of a larger repo (e.g., bellows/ inside the governance-root repo).
    Without scoping, git walks up to the parent repo's .git and reports the entire
    monorepo's diff. Universally applicable: for standalone repos (cwd = repo root)
    `-- .` is equivalent to no pathspec and `--relative` is a no-op. Closes BACKLOG #4.
    """
    try:
        result = subprocess.run(
            ["git", "--no-pager", "diff", "--stat", "--relative", "--", "."],
            cwd=project_path, capture_output=True, text=True, timeout=10,
        )
        return result.stdout
    except Exception:
        return ""
```

**Parameters:**
- `project_path: str` — the project root directory passed from `run_plan`

**Return value:** `str` — raw stdout from `git diff --stat`, or `""` on any exception

**Subprocess argv:** `["git", "--no-pager", "diff", "--stat", "--relative", "--", "."]`
**cwd:** `project_path` (e.g., `/Users/marklehn/Desktop/GitHub/bellows`)

**Error handling:** Catches all `Exception` subclasses and returns `""`. No logging, no raise, no escalation. This means a subprocess timeout (10s), a git error (corrupt index), or a `FileNotFoundError` (missing git binary) all silently return empty string.

**Threading/concurrency primitives:** NONE. No locks, no mutex, no semaphore. This function is called from `run_plan` which runs in threads dispatched by `handle_new_plan` and `handle_parallel_group`, meaning multiple threads can call `_capture_git_diff` concurrently on the same `project_path` with no coordination.

**Call sites (4 total):**

| # | Location | Context |
|---|---|---|
| 1 | `bellows.py:265` | First step pre-diff: `pre_diff = _capture_git_diff(project_path)` — immediately before `runner.run_step()` at line 267 |
| 2 | `bellows.py:281` | First step post-diff: `post_diff = _capture_git_diff(project_path)` — immediately after `runner.run_step()` returns at line 267 |
| 3 | `bellows.py:321` | Loop step pre-diff: `pre_diff = _capture_git_diff(project_path)` — inside the `while not is_final_step` loop, before continuation `runner.run_step()` at line 323 |
| 4 | `bellows.py:339` | Loop step post-diff: `post_diff = _capture_git_diff(project_path)` — inside the loop, after continuation `runner.run_step()` returns |

**Call site 1 context (bellows.py:263-269):**
```python
        # Capture pre-step file state
        pre_diff = _capture_git_diff(project_path)

        parsed = runner.run_step(bootstrap_prompt, project_path, model,
                                  timeout=config.get("step_inactivity_timeout_seconds",
                                                     config.get("step_timeout_seconds", 300)))
```

**Call site 2 context (bellows.py:279-283):**
```python
        # Capture post-step file state and run gates
        post_diff = _capture_git_diff(project_path)
        files_changed = _parse_diff_stat(post_diff, pre_diff, project_path)
        gate_result = gates.check(parsed, plan_text, current_step, project_path, files_changed=files_changed)
```

**Call site 3 context (bellows.py:319-328):**
```python
            # Capture pre-step file state
            pre_diff = _capture_git_diff(project_path)

            parsed = runner.run_step(
                default_next_prompt, project_path, model,
                session_id=parsed.get("session_id"),
                timeout=config.get("step_inactivity_timeout_seconds",
                                   config.get("step_timeout_seconds", 300)),
            )
```

**Call site 4 context (bellows.py:337-341):**
```python
            # Capture post-step file state and run gates
            post_diff = _capture_git_diff(project_path)
            files_changed = _parse_diff_stat(post_diff, pre_diff, project_path)
            gate_result = gates.check(parsed, plan_text, current_step, project_path, files_changed=files_changed)
```

### `_parse_diff_stat`

**Definition:** `bellows.py:423-456` (34 lines)

```python
def _parse_diff_stat(post_diff: str, pre_diff: str, project_path: Optional[str] = None) -> list:
    """Parse git diff --stat output to extract files changed by this step.

    Uses diff-of-diffs semantics: returns only files where the stat line
    changed between pre_diff and post_diff, eliminating false positives from
    pre-existing dirty files that the step never touched.

    Files outside `project_path` (paths with `..` components after normalization)
    are excluded — `git diff --stat` run with `cwd=project_path` still reports
    changes across the entire repo, and we only want to gate on files the plan
    could have legitimately touched.
    """
    def parse_stat_map(diff_text):
        result = {}
        for line in diff_text.strip().splitlines():
            line = line.strip()
            if "|" in line:
                filename, stat = line.split("|", 1)
                filename = filename.strip()
                if filename:
                    result[filename] = stat.strip()
        return result

    pre_map = parse_stat_map(pre_diff)
    post_map = parse_stat_map(post_diff)
    changed = [f for f, s in post_map.items() if pre_map.get(f) != s]

    if project_path is not None:
        changed = [
            f for f in changed
            if ".." not in os.path.normpath(f).split(os.sep)
        ]

    return sorted(changed)
```

**Parameters:**
- `post_diff: str` — git diff --stat output captured after the step
- `pre_diff: str` — git diff --stat output captured before the step
- `project_path: Optional[str]` — if provided, filters out files with `..` path components

**Return value:** `list` — sorted list of filenames whose stat line changed between pre and post

**Call sites (2 total):**

| # | Location | Context |
|---|---|---|
| 1 | `bellows.py:282` | `files_changed = _parse_diff_stat(post_diff, pre_diff, project_path)` — first step |
| 2 | `bellows.py:340` | `files_changed = _parse_diff_stat(post_diff, pre_diff, project_path)` — loop step |

**Threading:** No concurrency primitives. Pure function — no shared state. Safe for concurrent calls from different threads (each call has its own `pre_diff` and `post_diff` values). The contamination problem is NOT in `_parse_diff_stat` itself — it's in the fact that its inputs (`pre_diff` and `post_diff`) come from `_capture_git_diff` which reads shared working-tree state.

---

## Phase A2 — `runner.run_step` cwd Handling

**Definition:** `runner.py:25-256` (232 lines total, including all paths)

**Function signature:**
```python
def run_step(
    prompt: str,
    project_path: str,
    model: str,
    session_id: Optional[str] = None,
    allowed_tools: str = "Read,Edit,Write,Bash",
    timeout: int = 300,
) -> dict:
```

**cwd determination:** `project_path` is passed in from `bellows.py:run_plan` (which derives it from the plan file path at `bellows.py:206`: `project_path = str(plan_p.parents[2])`). The `cwd` is NOT hardcoded — it comes from the caller.

**Subprocess invocation (runner.py:49-55):**
```python
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=project_path,
        )
```

**How `claude -p` inherits filesystem state:** The subprocess runs with `cwd=project_path`, meaning it inherits the project directory as its working directory. The agent subprocess has full read/write access to the filesystem. It operates in the same working tree, same `.git/` directory, same index file as all other concurrent plan threads.

**PID exposure:** YES. `subprocess.Popen` returns a `Popen` object stored as `proc` (runner.py:49). The PID is accessible via `proc.pid`. However, `proc` is a local variable inside `run_step` — it is NOT returned to the caller (`bellows.py`). The return dict does not include the PID. The PID is available inside `run_step` during the monitoring loop (runner.py:101-127) but is not propagated.

**Timeout and stream handling:**
- Inactivity timeout: runner.py:115-119 — if no output for `timeout` seconds, `proc.kill()` is called
- Wall-clock cap: runner.py:122-127 — hard cap at `timeout * 10` seconds
- Streaming: Two daemon threads read stdout and stderr concurrently (runner.py:82-95) updating `last_output_time` via a threading lock (runner.py:80)
- The lock at runner.py:80 (`lock = threading.Lock()`) is local to each `run_step` invocation — not shared across plan threads

---

## Phase A3 — `run_plan` Dispatch Lifecycle

**Definition:** `bellows.py:194-401` (208 lines)

**Full step-execution sequence with line numbers:**

| Phase | Line(s) | Operation | Notes |
|---|---|---|---|
| Plan claim | 236-240 | `shutil.move(plan_path, inprogress_path)` + `_write_shadow()` | Atomic rename. Skipped if already `in-progress-`. Shadow written immediately after claim. |
| Header/metadata parse | 220-233 | `_read_shadow()`, `extract_total_steps()`, `_parse_plan_header()` | Uses shadow if available, else plan text directly |
| Bootstrap prompt construction | 255-262 | Builds prompt string referencing `shadow_prompt_path` | Three variants: diagnostic, resume, fresh step 1 |
| Pre-diff capture | 265 | `pre_diff = _capture_git_diff(project_path)` | Reads shared working tree state |
| Runner invocation | 267-269 | `parsed = runner.run_step(bootstrap_prompt, project_path, model, timeout=...)` | Blocking call — thread waits here |
| DB record | 274-278 | `record_run(db_path, ...)` | SQLite write with new connection |
| Post-diff capture | 281 | `post_diff = _capture_git_diff(project_path)` | Reads shared working tree state |
| Diff parse | 282 | `files_changed = _parse_diff_stat(post_diff, pre_diff, project_path)` | Diff-of-diffs |
| Gates check | 283 | `gate_result = gates.check(...)` | Includes scope_check using files_changed |
| **Loop entry** | 289 | `while not is_final_step(current_step, total_steps):` | Multi-step loop |
| Pause check | 291-315 | Check gates, QA, verdict_requested, header_pause | Posts verdict request + renames to verdict-pending |
| Loop pre-diff | 321 | `pre_diff = _capture_git_diff(project_path)` | Same as above |
| Loop runner | 323-328 | `parsed = runner.run_step(...)` with `session_id` | Resume session |
| Loop DB record | 332-336 | `record_run(...)` | |
| Loop post-diff | 339 | `post_diff = _capture_git_diff(project_path)` | |
| Loop diff parse | 340 | `files_changed = _parse_diff_stat(...)` | |
| Loop gates | 341 | `gate_result = gates.check(...)` | |
| Final step pause | 347-373 | Same pause-check logic for terminal step | |
| Auto-close | 378-397 | Move to Done/, delete shadow, push notification | Only if `effective_auto_close=True` |

**Per-thread state:** Each `run_plan` invocation (each thread) holds its own:
- `plan_path`, `inprogress_path`, `base_filename`, `plan_slug` — string locals
- `pre_diff`, `post_diff` — string locals, but their VALUES come from shared state
- `parsed` — dict from runner, private
- `current_step`, `total_cost` — int/float locals
- `gate_result` — dict, private

**Shared state across threads:**
- `project_path` working tree — read by `_capture_git_diff`, written by `claude -p` subprocesses
- `.git/` directory — read by `_capture_git_diff`, written by agent commits
- `bellows.db` — written by `record_run` (separate connections per call)
- `verdicts/pending/` — written by `verdict.post_verdict_request`
- `.bellows-cache/` — written by `_write_shadow`, read by `_read_shadow`

**Where a worktree COULD be created and torn down:**
- **Creation:** Between plan claim (line 240) and pre-diff capture (line 265). This is the natural insertion point — the worktree needs to exist before `_capture_git_diff` is called and before `runner.run_step` launches `claude -p`. Worktree `cwd` would replace `project_path` in both `_capture_git_diff` calls and `runner.run_step` call.
- **Teardown:** After the final gates check (line 341 in loop, or line 283 for single-step plans) and before the pause/auto-close branches. Specifically: after the last `_capture_git_diff` call but before plan lifecycle transitions (verdict post, Done move).
- **Loop consideration:** For multi-step plans, the worktree must persist across all steps within a single `run_plan` invocation (the same thread). It does NOT need to persist across verdict-pending pauses (a new `run_plan` call is dispatched for the resume).

**Where a mutex around `_capture_git_diff` COULD be inserted:**
- As a module-level `threading.Lock()` in `bellows.py` (next to `BELLOWS_ROOT`, `DB_PATH`, etc. at the top of the file).
- Acquired at lines 265, 281, 321, 339 (each `_capture_git_diff` call site).
- Risk: If the mutex wraps only `_capture_git_diff`, the window between pre-diff and post-diff is NOT protected. A sibling can still modify the working tree during `runner.run_step` execution. The mutex would need to wrap the entire pre-diff → post-diff window to be effective, which means holding the lock during the blocking `runner.run_step` call — this would serialize ALL plan executions, defeating parallel dispatch.

---

## Phase A4 — Shared State Inventory

### (a) `bellows.db`

| Aspect | Details |
|---|---|
| Path | `BELLOWS_ROOT / "bellows.db"` (`bellows.py:17`) — absolute path constant |
| Tables | `runs` — single table with columns: id, timestamp, plan_path, project, session_id, step, status, cost, plan_slug |
| Writes during step | `record_run()` at bellows.py:274-278 (after first step) and bellows.py:312-313 (pause), 332-336 (loop), 370-371 (final pause) |
| Connection lifecycle | Each `record_run()` call opens a new `sqlite3.connect()`, executes INSERT, commits, closes (`bellows.py:152-171`). No persistent connection. |
| Concurrency safety | SQLite handles concurrent writers via internal locking (WAL mode by default on macOS). Each connection is short-lived. No Bellows-level locking needed. |
| Worktree impact | **None.** DB path is absolute (`BELLOWS_ROOT / "bellows.db"`). A per-plan worktree does NOT need its own DB copy — all worktrees share the same DB via absolute path. |

### (b) `.bellows-cache/<slug>.pristine`

| Aspect | Details |
|---|---|
| Path | `BELLOWS_ROOT / ".bellows-cache"` (`bellows.py:18`) — absolute path constant |
| Written by | `_write_shadow()` at bellows.py:107-111, called from `run_plan` at line 240 (immediately after plan claim) |
| Read by | `_read_shadow()` at bellows.py:114-119, called from `run_plan` at line 220; also by agents via the bootstrap prompt which references `shadow_prompt_path` (the absolute path to the `.pristine` file) |
| Access | Via absolute path — `_shadow_path()` at bellows.py:96-104 returns `SHADOW_CACHE_DIR / f"{canonical}.pristine"` |
| Deleted by | `_delete_shadow()` at bellows.py:122-126, called on auto-close (line 393), continue-to-done verdict (line 715), and stop verdict (line 735) |
| Worktree impact | **Shared — no per-worktree copy needed.** The shadow cache stores pristine plan content for agents to read. It's accessed via absolute path in the bootstrap prompt. Agents in a worktree can read it via the same absolute path. No modification by agents. |

### (c) `verdicts/pending/` and `verdicts/resolved/`

| Aspect | Details |
|---|---|
| Path | `BELLOWS_ROOT / "verdicts"` (`verdict.py:11`) — absolute path constant |
| Written to `pending/` by | `verdict.post_verdict_request()` — called from `run_plan` at bellows.py:304 (loop pause) and bellows.py:363 (final pause) |
| Read from `pending/` by | `_consume_verdicts()` at bellows.py:620-768 — scans `BELLOWS_ROOT / "verdicts" / "pending"` for request files |
| Read from `resolved/` by | `_consume_verdicts()` — scans `BELLOWS_ROOT / "verdicts" / "resolved"` for verdict files |
| Worktree impact | **Shared — no per-worktree copy needed.** Verdicts are a Bellows-internal queue, not part of the project working tree. Accessed via absolute path from `BELLOWS_ROOT`. |

### (d) Project `.git/` directory

| Aspect | Details |
|---|---|
| Used by | `_capture_git_diff()` — runs `git diff --stat` with `cwd=project_path`, which uses the project's `.git/` |
| Agent operations | `claude -p` running with `cwd=project_path` performs: `git add`, `git commit`, `git diff`, `git status`, `git log`, and other git commands as part of code changes |
| Concurrent access | Multiple `claude -p` subprocesses + multiple `_capture_git_diff` calls can all access the same `.git/` directory simultaneously |
| Worktree impact | **This is the core problem resource.** A per-plan worktree (`git worktree add`) creates a separate working tree with its own `HEAD` reference but shares the same object store (`.git/objects/`). Each worktree has its own index (`.git/worktrees/<name>/index`). `git diff --stat` in a worktree reads that worktree's index, NOT the main checkout's index. This is exactly the isolation property needed. |

### (e) Project working tree (file system)

| Aspect | Details |
|---|---|
| Written by | Agent subprocesses (`claude -p`) — creating, modifying, deleting files as instructed by the plan step |
| Read by | `_capture_git_diff()` (indirectly via git), agents (reading existing code), `gates.check()` via `_resolve_deposit_path()` for deposit existence checks |
| Worktree impact | **Each per-plan worktree would have its own working tree copy.** Agent file writes go to the worktree, not the main checkout. `_capture_git_diff` with `cwd=worktree_path` sees only that worktree's changes. This provides complete isolation. |

---

## Phase A5 — Threading and Parallel-Group Dispatch

### `handle_parallel_group`

**Definition:** `bellows.py:590-595` (6 lines)

```python
    def handle_parallel_group(self, paths: list):
        threads = [threading.Thread(target=self._run_tracked, args=(p,), daemon=True) for p in paths]
        for t in threads:
            t.start()
            time.sleep(2)
        print(f"Bellows: ▶ started {len(threads)} parallel threads")
```

### `handle_new_plan`

**Definition:** `bellows.py:584-588` (5 lines)

```python
    def handle_new_plan(self, path: str, resume_step: Optional[int] = None):
        t = threading.Thread(target=self._run_tracked, args=(path,), kwargs={"resume_step": resume_step}, daemon=True)
        t.start()
        time.sleep(2)  # Stagger thread starts to avoid simultaneous claude -p auth hits
        print(f"Bellows: ▶ started {os.path.basename(path)}")
```

### `_pending_groups` settle-window logic

**Definition:** `PlanHandler.__init__` at `bellows.py:491` — `self._pending_groups: dict = {}`

**Population:** `PlanHandler._handle` at `bellows.py:515-516`:
```python
                if group not in self._pending_groups:
                    self._pending_groups[group] = time.time()
```

**Consumption:** `Bellows._rescan` at `bellows.py:601-612`:
```python
        for group in list(handler._pending_groups.keys()):
            if now - handler._pending_groups[group] > 5:
                # ... collect siblings and dispatch ...
                del handler._pending_groups[group]
```

### Dispatch analysis

| Aspect | Details |
|---|---|
| Dispatch method | `threading.Thread` — each plan runs in a separate daemon thread |
| Thread lifecycle | Daemon threads (`daemon=True`). Not joined. Not tracked by reference (the `Thread` objects are local variables that go out of scope after `.start()`). Thread lifetime = duration of `self._run_tracked(path)` → `run_plan(path, ...)`. |
| 2-second stagger | `time.sleep(2)` between each `t.start()` (both `handle_new_plan` and `handle_parallel_group`). Purpose: avoid simultaneous `claude -p` auth hits (API rate limiting). NOT for git coordination. |
| Private state per thread | Local variables within `run_plan`: `plan_path`, `pre_diff`, `post_diff`, `parsed`, `current_step`, `gate_result`, etc. |
| Shared state across threads | Working tree, `.git/`, `bellows.db`, `verdicts/`, `.bellows-cache/`, `_active_count` (via `_active_lock`). |
| `_active_lock` | `bellows.py:550` — `self._active_lock = threading.Lock()`. Protects `self._active_count` increment/decrement in `_run_tracked` (lines 554-560). NOT used for git coordination. |

### Where per-plan isolation COULD be injected

1. **In `_run_tracked` (bellows.py:553-561):** Before calling `run_plan()`, create a worktree. After `run_plan()` returns, tear down the worktree. This wraps the entire plan lifecycle.

2. **In `run_plan` (bellows.py:194):** After plan claim (line 240) and before pre-diff capture (line 265), create a worktree. Pass `worktree_path` instead of `project_path` to `_capture_git_diff` and `runner.run_step`. After plan completion (before auto-close/verdict branches), merge worktree changes back and tear down.

3. **Thread-local storage:** Python's `threading.local()` could store a per-thread worktree path. However, since `run_plan` already has its own local variables, simple function parameters are sufficient — thread-local storage adds no benefit over passing the worktree path as a local variable.

### Threading model compatibility

The existing model CAN support per-thread state without additional infrastructure. Each thread already has its own stack frame for `run_plan`. The worktree path is naturally a local variable within `run_plan` or `_run_tracked`. No thread-local storage, no shared data structures, and no locking needed for the worktree path itself.

---

## Phase A6 — Existing `.gitignore` State

### `bellows/.gitignore` (read at project root level)

```
bellows.db
*.db-shm
*.db-wal
logs/
.DS_Store
__pycache__/
*.pyc
.venv/
config.json
.env
verdicts/ledger.jsonl
.bellows-cache/
```

### Parent repo `.gitignore` (`/Users/marklehn/Desktop/GitHub/.gitignore`)

```
# Ignore project repos (they have their own git)
BrewBuddy/
SimpleScreen/
ai-career-digest/
forge/
freight-kb/
invoice-pulse/
study/
Uncategorized/

# System files
.DS_Store
*.swp
*~

# Sensitive
github-recovery-codes.txt
bellows/config.json

# Claude config
.claude/
```

### Analysis

| Question | Answer |
|---|---|
| Is `.bellows-cache/` gitignored? | **YES** — listed in `bellows/.gitignore` line 12 |
| Is `.bellows-worktrees/` gitignored? | **NO** — would need to be added |
| Is `/tmp/` referenced? | **NO** — not in either `.gitignore` |
| Pattern for in-project untracked dirs | `.bellows-cache/`, `logs/`, `__pycache__/`, `.venv/` — all use trailing `/` in `.gitignore` |
| Would `/tmp/` worktrees need gitignore? | **NO** — `/tmp/` is outside the repo entirely, so `.gitignore` is irrelevant |
| Would in-tree `.bellows-worktrees/` need gitignore? | **YES** — must add `.bellows-worktrees/` to `bellows/.gitignore` to prevent tracking |

---

## Phase A7 — Existing Test Surface

| Test File | Lines | Relevant Tests | Description |
|---|---|---|---|
| `tests/test_bellows.py` | 1-1789 | 38 tests total | Core orchestration tests |
| | 456-488 | `test_parse_diff_stat_*` (5 tests) | Diff-of-diffs semantics — pre-existing unchanged, new file, changed stat, summary line, empty inputs |
| | 491-503 | `test_capture_git_diff_uses_relative_pathspec` | Verifies `--relative -- .` argv — BACKLOG #4 fix |
| | 510-575 | `test_parse_diff_stat_project_path_*` (6 tests) | Project-path `..` filtering — BACKLOG #2 fix |
| | 582-644 | `test_run_plan_resume_step_uses_correct_prompt` | Resume prompt contains "Step N" and shadow path |
| | 386-397 | `test_handle_parallel_group_stagger` | Verifies 2-second sleep stagger |
| | 943-1068 | Parallel group deferred dispatch (6 tests) | Tests `_pending_groups` settle-window, deferred dispatch, two-sibling collection |
| | 1100-1168 | Claim-at-entry (3 tests) | Tests plan claim before runner, idempotent claim |
| | 1171-1386 | Shadow path bootstrap (5 tests) | Bootstrap/continuation/diagnostic/resume prompts reference `.bellows-cache/` |
| `tests/test_runner.py` | 1-253 | 14 tests | Runner subprocess management |
| | 50-64 | `test_configurable_timeout_respected` | Inactivity timeout |
| | 130-139 | `test_success_writes_log_file` | Log file creation on success path |
| | 181-206 | `test_ndjson_parse_valid_stream` | NDJSON parsing happy path |
| | 238-253 | `test_resume_session_flag_in_command` | `--resume` flag in command argv |
| `tests/test_gates.py` | 1-304 | 26 tests | Gate validation |
| | 172-175 | `test_scope_check_passes_when_files_in_plan` | Scope check happy path |
| | 178-181 | `test_scope_check_fails_when_file_not_in_plan` | Scope check failure |
| | 217-258 | Scope check prefix allowlist (5 tests) | `in-progress-`, `verdict-pending-`, `halted-` prefixes |
| `tests/test_verdict.py` | 1-241 | 14 tests | Verdict posting, checking, ledger |
| `tests/test_cleanup_verdicts.py` | 58 lines | 3 tests | `_cleanup_verdicts_for_slug` |
| `tests/test_consume_verdicts.py` | 274 lines | ~10 tests | `_consume_verdicts` scoping and lifecycle |

### Tests that currently DEPEND on shared-working-tree behavior

**None found.** All existing tests mock `_capture_git_diff` (via `patch("bellows._capture_git_diff", return_value="")`) or pass pre-built diff strings directly to `_parse_diff_stat`. No test exercises the actual `git diff --stat` subprocess against a live shared working tree. This means:

1. No existing tests would break from switching to worktree-isolated diffs.
2. No existing tests would catch a worktree regression either — new tests are needed.
3. The `test_capture_git_diff_uses_relative_pathspec` test (line 491-503) mocks `subprocess.run` and checks argv — it would need updating if the argv changes (e.g., if cwd changes to a worktree path).

---

## Phase A8 — PID Exposure Feasibility

### PID availability from `subprocess.Popen`

**YES.** `subprocess.Popen` exposes `proc.pid` (runner.py:49). The PID is the OS process ID of the spawned `claude -p` subprocess. It is accessible within `run_step` for the duration of the subprocess execution.

**However:** The PID is NOT returned to the caller (`bellows.py:run_plan`). The return dict from `run_step` does not include `proc.pid`. To make the PID available in `run_plan` (where `_capture_git_diff` is called), `run_step` would need to be modified to either:
- Return `proc.pid` in the result dict, OR
- Accept a callback that receives the PID before the monitoring loop starts, OR
- Return the `Popen` object itself (breaking encapsulation)

### PID-based file attribution on macOS

| Approach | Feasibility |
|---|---|
| `psutil` polling | Python `psutil` can enumerate open files per PID (`psutil.Process(pid).open_files()`). However, this shows currently-open files, not historical writes. Would need continuous polling during the step, which is expensive and racey. |
| `/proc` polling | macOS does NOT have `/proc` filesystem. Not feasible. |
| `dtrace` PID filtering | macOS `dtrace` supports `-p PID` flag and can trace `write()` syscalls per process. **However:** SIP is enabled (`System Integrity Protection status: enabled`). Under SIP, dtrace is severely restricted — it cannot attach to processes not owned by the user or to system processes, and many probes are disabled. `claude -p` is a user process, so dtrace CAN attach to it. But dtrace requires root for most provider usage, and running Bellows as root is not practical. |
| `fs_usage` | macOS `fs_usage -w -f filesys -p <pid>` can trace file operations per PID. Requires root. Not feasible for non-root Bellows. |
| `lsof` | `lsof -p <pid>` shows open files but is a snapshot, not a trace. Same limitation as `psutil`. |

### Verdict on candidate (e) PID-filtering

**NOT reopenable on practical grounds.** While `proc.pid` is accessible, no macOS mechanism provides non-root, continuous, per-PID file-write attribution suitable for building a `files_changed` list. The prior diagnostic's dismissal on OS-API grounds stands. The PID is useful for other purposes (process management, timeout enforcement) but not for diff isolation.

---

## Summary of Surface

The SA in Step 2 needs to walk through these code paths:

1. **`_capture_git_diff`** (bellows.py:404-420) — the contamination entry point. Four call sites (lines 265, 281, 321, 339) all reading shared working-tree state via `git diff --stat --relative -- .` with `cwd=project_path`.

2. **`_parse_diff_stat`** (bellows.py:423-456) — the diff-of-diffs engine. Pure function, no shared state, but its outputs are only as clean as its inputs.

3. **`runner.run_step`** (runner.py:25-256) — the `claude -p` launcher. `cwd=project_path` at line 54 determines where the agent operates. PID available via `proc.pid` but not returned.

4. **`run_plan`** (bellows.py:194-401) — the step lifecycle orchestrator. Natural worktree creation point: between lines 240 and 265. Natural teardown point: after the final `_capture_git_diff` call (line 339 in loop, or 281 for single-step). Mutex insertion around `_capture_git_diff` alone is insufficient — the entire pre-diff → run_step → post-diff window would need locking, which serializes execution.

5. **`handle_parallel_group`** (bellows.py:590-595) and **`handle_new_plan`** (bellows.py:584-588) — thread dispatch. Daemon threads, 2-second stagger, no shared mutable state beyond `_active_count`.

6. **Shared resources:** `bellows.db` (absolute path, safe for concurrent access), `.bellows-cache/` (absolute path, read-only by agents), `verdicts/` (absolute path, Bellows-internal), `.git/` (the problem resource — shared index and working tree), project working tree (the other problem resource — shared file system).

7. **Test surface:** 38 tests in test_bellows.py, 14 in test_runner.py, 26 in test_gates.py. No tests depend on shared-working-tree behavior. `test_capture_git_diff_uses_relative_pathspec` mocks subprocess.run and checks argv. All `run_plan` tests mock `_capture_git_diff`.

8. **`.gitignore`:** `.bellows-cache/` already gitignored. `.bellows-worktrees/` would need to be added if in-tree. `/tmp/` locations need no gitignore entry.

---

## Output Receipt
**Agent:** Bellows Developer
**Step:** 1
**Status:** Complete

### What Was Done
Produced a complete implementation surface map across 8 phases (A1–A8) documenting every code path, call site, shared resource, threading model, test surface, and PID feasibility relevant to any fix candidate for the parallel-plan diff contamination bug.

### Files Deposited
- `bellows/knowledge/research/worktree-implementation-surface-2026-05-03.md` — comprehensive surface map (8 phases)

### Files Created or Modified (Code)
- None (surface mapping only — no production code modified)

### Decisions Made
- PID-filtering candidate (e) confirmed NOT reopenable on macOS with SIP enabled — no non-root mechanism for continuous per-PID file-write attribution

### Flags for CEO
- None

### Flags for Next Step
- Phase A8 confirms PID-filtering is not feasible — SA should evaluate only worktree, serialize-capture, and any novel third candidate
- No existing tests depend on shared-working-tree behavior — the test regression surface for any fix is clean
- The mutex-around-`_capture_git_diff`-only approach is structurally insufficient (does not protect the pre-diff → run_step → post-diff window) — SA should note this when evaluating the serialize candidate
