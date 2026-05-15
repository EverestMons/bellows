# Parallel-Plan scope_check Diff-Collision — Diagnostic Findings

**Date:** 2026-05-01 | **Plan:** diagnostic-parallel-plan-scope-check-collision-2026-05-01 | **Step:** 1

---

## Q1 — Current `_capture_git_diff` Behavior

**Location:** `bellows/bellows.py:434-450`

**Full current signature and body:**

```python
def _capture_git_diff(project_path: str) -> str:
    """Capture git diff --stat output for file change tracking, scoped to the project subtree."""
    try:
        result = subprocess.run(
            ["git", "--no-pager", "diff", "--stat", "--relative", "--", "."],
            cwd=project_path, capture_output=True, text=True, timeout=10,
        )
        return result.stdout
    except Exception:
        return ""
```

**Git command:** `git --no-pager diff --stat --relative -- .`
- **argv:** `["git", "--no-pager", "diff", "--stat", "--relative", "--", "."]`
- **cwd:** `project_path` (the project's root directory, e.g., `/Users/marklehn/Desktop/GitHub/bellows`)
- **Returns:** `result.stdout` (the diff stat text) or `""` on any exception

**Invocation from scope_check gate:** `_capture_git_diff` is NOT invoked from `_gate_scope_check` directly. It is called in `run_plan()` at two sites:
1. **Pre-step capture:** `bellows.py:295` (`pre_diff = _capture_git_diff(project_path)`) — before `runner.run_step()` first call
2. **Post-step capture:** `bellows.py:311` (`post_diff = _capture_git_diff(project_path)`)  — after `runner.run_step()` returns
3. Same pattern repeats in the while-loop at `bellows.py:351` (pre) and `bellows.py:369` (post)

The diff output is then parsed via `_parse_diff_stat(post_diff, pre_diff, project_path)` at `bellows.py:312` and `bellows.py:370`, and the resulting `files_changed` list is passed to `gates.check()` which routes it to `_gate_scope_check()` at `gates.py:69`.

**2026-04-28 `--relative -- .` fix:** CONFIRMED present in live code. The argv at `bellows.py:445` contains `"--relative", "--", "."`. The docstring at `bellows.py:435-441` explicitly references "Closes BACKLOG #4". The fix was shipped in commit `8db0adc`.

**Key observation for the collision problem:** `_capture_git_diff` runs `git diff --stat` against the **working tree** (unstaged + staged changes vs HEAD). It does NOT diff committed changes. This means it captures the state of ALL uncommitted modifications in the working tree at the moment it runs — regardless of which plan made them.

## Q2 — Step-Start Timestamp Availability

**Does Bellows capture a per-step-start timestamp?**

1. **`runner.py:43-45`** — `runner.run_step()` creates `timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")` (for log filename) and `start_time = time.monotonic()` (for timeout tracking). Both are **local variables** — not returned, not accessible from `bellows.py` or `_capture_git_diff`.

2. **`bellows.py:168-169`** — `record_run()` writes `datetime.now().isoformat()` to `bellows.db` in the `timestamp` column. This is called AFTER `runner.run_step()` returns (at `bellows.py:304-308` and `bellows.py:362-366`), so it records the step-end time, not step-start.

3. **`bellows.db` schema** (`bellows.py:42-52`) — the `runs` table has a single `timestamp TEXT` column. There is no `step_start_timestamp` or equivalent.

4. **Log files** (`runner.py:44`) — the log filename embeds a timestamp (`%Y%m%d-%H%M%S-step.json`) but this is the runner-internal start time, not propagated.

**Conclusion:** No per-step-start timestamp is currently accessible from where `_capture_git_diff` runs (inside `run_plan()` in `bellows.py`). However, `run_plan()` already has the call sequence:

```
pre_diff = _capture_git_diff(project_path)     # bellows.py:295
parsed = runner.run_step(...)                   # bellows.py:297-299
post_diff = _capture_git_diff(project_path)     # bellows.py:311
```

The **cleanest place** to add a step-start timestamp would be immediately before the `runner.run_step()` call at `bellows.py:297` (first step) and `bellows.py:353` (subsequent steps), e.g.:

```python
step_start_ts = datetime.now().isoformat()
# or for git-range scoping:
step_start_ts = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
```

This timestamp could then be passed to a modified `_capture_git_diff()` to produce a time-bounded diff like `git log --since=<step_start_ts> --stat --relative -- .`.

**Feasibility of fix shape (a):** Moderate. A timestamp is easy to capture, but `git diff --stat` (what `_capture_git_diff` currently runs) operates on the working tree — it doesn't take a `--since` parameter. To use a timestamp-bound range, the function would need to switch to `git log --since=<ts> --stat` or `git diff <commit-before-ts>..HEAD --stat`, which is a semantically different operation (committed changes vs working-tree state). The current pre/post diff-of-diffs approach specifically uses working-tree state.

## Q3 — Plan Slug Presence in Commit Messages

**Last 30 commits analysis:**

| Category | Count | Examples |
|---|---|---|
| (a) Slug-in-message (parseable) | **0** | None — no commit contains a full `executable-*-2026-*` or `diagnostic-*-2026-*` slug |
| (b) Conventional-format without slug | **18** | `docs:`, `chore:`, `qa:`, `fix:`, `feat:`, `test:`, `research:` prefixes |
| (c) Other (no slug, non-conventional) | **12** | `phase 3c:`, `session wrap 2026-04-30:`, `docs(backlog):`, `fix(gates):`, etc. |

**Slug-in-message rate: 0/30 = 0%.**

Many commits reference BACKLOG item numbers (e.g., "BACKLOG #11", "BACKLOG #12", "BACKLOG #6") but NOT the plan slug that produced the commit. Some commit messages contain plan-name fragments (e.g., "deposit_exists directory paths", "ledger pause_reason_code") but these are descriptive text, not parseable slugs.

**Do agent-prompt templates instruct agents to include the plan slug in commit messages?**

Checked `decisions/Done/` executable plans. The commit instructions found are of the form:
- `executable-disable-auto-close-2026-04-24.md:73`: `**Commit.** Use a descriptive commit message, e.g., "feat: disable auto-close default — terminal steps always pause for Planner".`

This instructs conventional-format commit messages with NO plan slug. This is the standard pattern across examined plans.

**Feasibility of fix shape (b): LOW.** Slug-presence rate is 0%. There is no existing convention or template instruction requiring agents to include the plan slug in commit messages. Adopting this approach would require:
1. Changing the PLANNER_TEMPLATE commit message convention
2. Waiting for all existing plans to cycle through
3. The approach is fragile even if adopted — agents may not comply, and the parser would need to handle slug variations

## Q4 — Typical Step-Diff Size Profile

**Raw data from `git log --since="2 weeks ago" --shortstat -- .` (bellows/):**

From the 31 commits in the last 2 weeks, extracting files-changed and line-delta:

| Metric | Files Changed | Insertions | Deletions | Net LOC Delta |
|---|---|---|---|---|
| **Min** | 1 | 1 | 0 | 1 |
| **Median** | 3 | 101 | 0 | ~80 |
| **Mean** | 4.6 | 133 | 1.6 | ~131 |
| **P90** | 11 | 294 | 5 | ~290 |
| **Max** | 15 | 438 | 5 | ~435 |

Breakdown of extreme commits:
- Max files (15): `86d257d chore: QA + feedback for BACKLOG hygiene sweep` — 15 files, 175 insertions (bulk doc/evidence deposit)
- Max insertions (438): `77ea478 qa: step-state resume Phase 3b verified` — 7 files, 438 insertions (QA evidence bundle)
- Most commits touch 1-6 files with <200 LOC delta

**Feasibility of fix shape (c) — snapshot-and-diff:** HIGH. The typical commit touches 3 files / ~100 LOC. Even the P90 (11 files / ~290 LOC) is well within the range where a pre-step snapshot of tracked file mtimes or checksums would be cheap. A snapshot approach does NOT require a full working-tree copy — it only needs to record the state of `git diff --stat` (or `git status --porcelain`) at step start, which is what `pre_diff` already captures. The current pre/post diff-of-diffs mechanism in `_parse_diff_stat` is already a form of this approach.

## Q5 — Parallel-N- Dispatch Timing

### (a) Discovery vs dispatch timing

When a `parallel-N-` plan is detected, Bellows does **NOT** dispatch immediately. It defers dispatch to a settle-window check.

**Flow:**
1. **On filesystem event** (`PlanHandler._handle`, `bellows.py:533-561`): when `from_rescan=False` (i.e., from a real filesystem event), the handler detects the parallel group prefix, records `_pending_groups[group] = time.time()` (`bellows.py:546`), and **returns without dispatching** (`bellows.py:547`).
2. **On rescan** (`Bellows._rescan`, `bellows.py:627-648`): every 30 seconds (`bellows.py:852`), Bellows checks pending groups against the 5-second settle window and dispatches.

### (b) `_pending_groups` data structure

**Definition:** `bellows.py:521` — `self._pending_groups: dict = {}  # group prefix → first-seen timestamp (float)`

**Population:** `bellows.py:545-546`:
```python
if group not in self._pending_groups:
    self._pending_groups[group] = time.time()
```

It maps the group prefix string (e.g., `"parallel-1"`) to a `time.time()` float representing when the first sibling in that group was detected.

### (c) The 5-second settle window

**Location:** `bellows.py:633` — `if now - handler._pending_groups[group] > 5:`

This is a **debounce delay** — Bellows waits at least 5 seconds after the first sibling in a group is detected before dispatching ANY of them. The purpose is to allow all siblings to land on disk (via Planner file writes) before Bellows collects and dispatches the group. Once the 5-second window expires on the next rescan (which runs every 30s), Bellows collects ALL runnable plans with the matching group prefix and dispatches them together.

**Effective delay:** 5-35 seconds. The settle window starts on first detection, but is only checked during rescans (30s cadence). So the actual delay before dispatch is `max(5, time_until_next_rescan)`.

### (d) Independence of parallel siblings at runtime

**Dispatch:** `Bellows.handle_parallel_group` at `bellows.py:620-625`:
```python
def handle_parallel_group(self, paths: list):
    threads = [threading.Thread(target=self._run_tracked, args=(p,), daemon=True) for p in paths]
    for t in threads:
        t.start()
        time.sleep(2)  # 2-second stagger
```

Each sibling runs in its own **thread** (not subprocess), calling `self._run_tracked(path)` → `run_plan(path, ...)`. Each `run_plan` invocation:
- Starts its own `claude -p` subprocess via `runner.run_step()` (`runner.py:49`)
- Has its own `pre_diff` / `post_diff` captures
- Runs its own `gates.check()`
- Records its own DB entry

**Shared state:** All threads share:
- The same working tree (git working directory)
- The same `bellows.db` (SQLite, with separate connections per `record_run` call)
- The same `_capture_git_diff` function reading the same git state

**Gate evaluation is independent per thread** — each thread runs `gates.check()` with its own `files_changed` list. But the `files_changed` list is derived from `_capture_git_diff` which reads shared working-tree state, so the lists can be **contaminated by sibling commits**.

### (e) Commit timing — sequential or interleaved?

Commits land **interleaved.** Each `claude -p` subprocess runs independently and commits when the agent decides to commit. There is:
- No git lock coordination between siblings
- No serialization of git operations
- The 2-second thread-start stagger (`bellows.py:623`) is purely for Claude auth rate-limiting, not for git coordination

**Critical race window:** Between `pre_diff = _capture_git_diff(project_path)` and `post_diff = _capture_git_diff(project_path)` for a given plan, a sibling plan's `claude -p` subprocess may commit files. Those committed files change `git diff --stat` output (committed files disappear from the working-tree diff), altering the `post_diff` in a way that `_parse_diff_stat`'s diff-of-diffs logic interprets as "this step changed those files."

More precisely: if sibling A has dirty file X in `pre_diff` and sibling B commits file X during A's step execution, then A's `post_diff` will NOT contain X (it's now committed). `_parse_diff_stat` sees X in `pre_map` but not in `post_map`, and treats this as a change — but `changed` only picks up files where `post_map[f] != pre_map.get(f)`, so a file disappearing from the diff would NOT be flagged (it's in pre but not post, and the list comprehension iterates `post_map.items()`).

**Correction on the actual collision vector:** The real issue is the reverse — if sibling B's `claude -p` creates new dirty files (staged or unstaged) DURING sibling A's step execution, those files appear in A's `post_diff` but not `pre_diff`, causing `_parse_diff_stat` to report them as files A changed. This is the scenario described in the BACKLOG entry: files committed by sibling `parallel-1-executable-ledger-pause-reason-code-2026-04-30` appeared in `parallel-1-executable-deposit-exists-directory-paths-2026-04-30`'s scope_check.

**Wait — re-examining:** The BACKLOG says the affected plans tripped scope_check listing files "that were actually committed by sibling." If the sibling committed them, they'd leave the working tree diff. The collision happens when:
1. Sibling B's agent modifies files → files appear dirty in working tree
2. Sibling A's `post_diff` captures B's dirty files
3. `_parse_diff_stat` reports them as changes relative to A's `pre_diff`
4. `_gate_scope_check` flags them as out-of-scope for plan A

Whether B commits before or after A's `post_diff` capture determines the exact contamination vector, but the fundamental problem is shared working-tree state.

## Q6 — Design Recommendation (Ranked Candidates)

### Candidate Rankings

**Rank 1: (c) Snapshot-at-step-start (diff-of-diffs refinement) — ALREADY PARTIALLY IMPLEMENTED**

The current code already implements a form of this: `pre_diff` and `post_diff` with `_parse_diff_stat` doing a diff-of-diffs. The problem is that `git diff --stat` reads working-tree state which is shared across threads. The fix would be to switch from working-tree diff to a mechanism that is per-plan isolated:

- **Variant c1 — file-level mtime/checksum snapshot:** At step start, record `{filename: mtime}` or `{filename: sha256}` for all tracked files in the project subtree. At step end, re-scan and diff. Only files whose mtime/checksum changed are reported. This is immune to sibling working-tree mutations because it records actual file state, not git's view of it.
  - **Pro:** Fully plan-isolated. No git dependency. Works even if siblings never commit.
  - **Con:** Slightly more expensive than `git diff --stat` for large trees, but Q4 shows the bellows tree is small.
  - **Complexity:** ~30 LOC. Replace `_capture_git_diff` with `_snapshot_file_state` and `_diff_file_state`.

- **Variant c2 — `git stash` isolation:** Stash uncommitted changes at step start, let the agent work on a clean tree, then diff. Dangerous — would interfere with sibling agents' uncommitted work.
  - **Reject:** Destructive to shared working tree.

**Rank 2: (d) Per-plan git worktree (NOT in BACKLOG proposals)**

Use `git worktree add` to create a temporary worktree for each parallel plan's `claude -p` subprocess. Each agent works in an isolated worktree with its own working-tree state.

- **Pro:** Complete isolation — each agent has its own index and working tree. No diff contamination possible.
- **Con:** Higher complexity (~50-80 LOC for worktree lifecycle management). Requires merging each worktree's commits back to the main branch. May confuse agents that expect to find files at specific absolute paths (e.g., `.bellows-cache/` paths). Doubles disk I/O for file reads.
- **Complexity:** Moderate. Would require changes to `handle_parallel_group`, `run_plan`, and the bootstrap prompt (to point `cwd` at the worktree).

**Rank 3: (a) Timestamp-bound git range**

Capture `step_start_ts` before `runner.run_step()`, then use `git log --since=<ts> --stat --relative -- .` instead of `git diff --stat`.

- **Pro:** Scopes to commits made during the step's execution window. Would correctly exclude sibling commits that landed before step start.
- **Con:** Does NOT handle uncommitted changes (only sees committed files). Does NOT handle sibling commits that land DURING the step's execution window (the race is on commit timing, not start timing). Semantically different from current working-tree diff — loses visibility into staged-but-uncommitted changes. Would miss agents that don't commit (some diagnostic steps don't commit).
- **Complexity:** ~15 LOC change.

**Rank 4: (b) Plan-slug commit-message scoping**

Filter `git log` to only commits whose message contains the plan slug.

- **Pro:** Precise per-plan scoping if slug is reliably present.
- **Con:** Current slug-in-commit-message rate is **0%** (Q3 findings). Would require PLANNER_TEMPLATE convention change AND 100% agent compliance. Fragile — agents may paraphrase, abbreviate, or omit the slug. Would not detect uncommitted changes. Requires a convention change to ship before the fix has any effect.
- **Complexity:** ~20 LOC change to `_capture_git_diff`, but blocked by convention adoption.

**Rank 5: (e) File-level mtime comparison (lightweight variant of c1)**

Instead of checksums, just compare mtimes. Faster than checksums but susceptible to clock skew or same-second writes.

- **Pro:** Very fast. No git dependency.
- **Con:** mtime granularity is 1 second on HFS+ — two writes in the same second would be missed. Less reliable than checksums.
- **Complexity:** ~20 LOC.

### Summary

| Rank | Approach | Isolation | Complexity | Handles uncommitted | Current feasibility |
|---|---|---|---|---|---|
| 1 | c1: file checksum snapshot | Full | ~30 LOC | Yes | Ready now |
| 2 | d: per-plan worktree | Full | ~50-80 LOC | Yes | Ready now |
| 3 | a: timestamp git range | Partial | ~15 LOC | No | Ready now |
| 4 | b: slug commit scoping | Full (if adopted) | ~20 LOC | No | Blocked by 0% adoption |
| 5 | e: mtime comparison | Near-full | ~20 LOC | Yes | Ready now |

**Recommendation for Planner:** (c1) file-checksum snapshot is highest-leverage. It provides full isolation at low complexity, handles both committed and uncommitted changes, requires no convention changes, and is semantically equivalent to what the current pre/post diff-of-diffs approach tries to achieve — just immune to shared-working-tree contamination.

---

### Files Deposited
- `bellows/knowledge/research/parallel-plan-scope-check-collision-diagnosis-2026-05-01.md`
