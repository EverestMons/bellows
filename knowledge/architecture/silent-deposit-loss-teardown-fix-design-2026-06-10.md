# Silent Deposit-Loss at Header-Pause Teardown — Fix Design

**Date:** 2026-06-10 | **Tier:** Medium | **Diagnostic:** BACKLOG #1 (2026-06-08)

---

## Section 1 — Pin the Real Discriminator

### Preserved-vs-Lost Predicate

**A deposit is preserved if and only if the agent committed it to the worktree branch before teardown. The directory is irrelevant.**

There is **zero auto-staging code** in bellows.py, gates.py, or runner.py. No code stages `knowledge/development|research|qa` differently from `knowledge/architecture/`. The BACKLOG #1 hypothesis ("auto-staged dirs") is **REFUTED** by direct code inspection.

### Trace: What Happens to a Deposit Between Agent Completion and Teardown

1. Agent writes file to worktree (e.g., `knowledge/architecture/foo.md`).
2. `_capture_git_diff(wt_path)` captures post-step HEAD SHA (`bellows.py:495`).
3. `_parse_diff_stat(post_diff, pre_diff, wt_path)` runs `git diff --stat <pre_sha> -- .` (`bellows.py:741`). This compares pre-step HEAD to the current working tree. **Untracked files (new files never `git add`ed) are invisible to `git diff`** — so `files_changed=0`.
4. `gates.check()` runs (`bellows.py:497`). The `deposit_exists` gate (`gates.py:366`) calls `_resolve_deposit_path()` which uses `os.path.isfile()` — the file IS on disk in the worktree, so the gate **PASSes**.
5. Header pause triggers; `_teardown_worktree(project_path, wt_path, plan_slug)` is called (`bellows.py:531`).
6. `_teardown_worktree` step (b) (`bellows.py:929-941`): `git log --format=%H HEAD --not main` — enumerates COMMITTED changes on the worktree branch. If the agent didn't commit, this list is empty (legitimate empty case — no error raised per the fail-safe contract at `bellows.py:928`).
7. Step (c) (`bellows.py:966-984`): `git merge --ff-only branch_name` (or `--no-ff` fallback) — merges only **committed** changes. Untracked files are not part of any commit and are invisible to this operation.
8. Step (d) (`bellows.py:987-1002`): `git worktree remove --force` + `shutil.rmtree` — physically removes the worktree directory. **This is the moment of loss.** Any untracked file in the worktree is destroyed.

### Reconciliation of the Contradiction

**v1 `executable-anvil-lab-project-scope-fix-2026-06-08` (LOST):**
- SA step wrote `knowledge/architecture/lab-project-scope-blueprint-2026-06-08.md` **without** `git add` / `git commit`.
- File existed on disk (gate PASSed), `files_changed=0` (git diff blind to untracked), merge transferred nothing, worktree removed → file lost.
- Confirmed by stop verdict: "written as an UNTRACKED file in the worktree (hence files_changed=0 while deposit_exists PASS at gate time)."

**This session's diagnostics (SURVIVED):**
- daemon-archetype and scope_check-FP diagnostics both deposited to `knowledge/architecture/`.
- Both agents were instructed (via self-protection guidance in the diagnostic template) to explicitly `git add` + `git commit` their deposits.
- Committed files merged to main at teardown → survived.

**Why the BACKLOG framing was plausible but wrong:**
- In the v1 failure, `knowledge/development|research|qa` deposits survived while `knowledge/architecture/` didn't.
- But this correlated with **agent commit behavior**, not directory: the cycle-1 DEV agent committed its deposits; the lab-project-scope-fix SA agent did not.
- The directory was coincidental, not causal.

**The real discriminator:** `committed-to-worktree-branch` vs `uncommitted` (whether untracked, staged-only, or modified-unstaged). The continuous-run-vs-teardown-pause distinction is a red herring — continuous runs preserve files only because the worktree persists across steps; the deposit is still lost if the teardown eventually runs and the file was never committed.

---

## Section 2 — Locate the Loss in Code

### The Drop Point

**`bellows.py:987-1002`** — worktree removal is the physical loss event:

```python
# (d) Remove the worktree
result = subprocess.run(
    ["git", "--no-pager", "worktree", "remove", wt_path, "--force"],
    cwd=project_path, capture_output=True, text=True, timeout=30,
)
# ... fallback shutil.rmtree ...
```

### What the Copy-Back/Land Step Actually Covers

The teardown performs a **branch merge**, not a file copy. `git merge --ff-only` (or `--no-ff`) at `bellows.py:966-975` transfers only changes that are committed on the worktree branch (`bellows-wt/<slug>`). The coverage is:

| State of file in worktree | Visible to `git diff <pre_sha>`? | Included in merge? | Survives teardown? |
|---|---|---|---|
| Committed | Yes | Yes | **Yes** |
| Staged (`git add`ed) but not committed | Yes | **No** | **No** |
| Untracked (new, never `git add`ed) | **No** | **No** | **No** |
| Modified tracked file, not staged | Yes | **No** | **No** |

### Why `deposit_exists` Passes Despite Imminent Loss

`gates.py:366` — `_resolve_deposit_path()` checks `os.path.isfile()` against the worktree path. At gate time (before teardown), the file physically exists in the worktree directory. The gate has no awareness of git status — it checks filesystem presence only.

### Why `files_changed` Is Zero

`bellows.py:741` — `git diff --stat <pre_sha> -- .` does not report untracked files. New files that have never been `git add`ed are invisible to `git diff`. So `files_changed=[]` and `file_change_audit` reports 0.

---

## Section 3 — Fix Design

### Shape (a): PRESERVE — Auto-Stage-and-Commit Declared Deposits at Step End

**Location:** Between step completion (after `gates.check()`) and `_teardown_worktree()` call — three call sites at `bellows.py:531`, `bellows.py:623`, `bellows.py:651`.

**Mechanism:**
1. Extract declared deposit paths from the plan text (using `gates._extract_plan_required_deposits()` for prose-declared, or `plan_header.get("deposits")` for frontmatter-declared).
2. For each declared deposit path, resolve it against the worktree (`_resolve_deposit_path(path, project_path, wt_path=wt_path)`).
3. For each resolved path that exists in the worktree, run `git status --porcelain -- <path>` to check if it's untracked (`??`) or modified-unstaged (`M ` / `A `).
4. If any untracked/unstaged deposits are found, `git add` them and create a Bellows-authored commit: `bellows: auto-stage declared deposits before teardown`.
5. Log the auto-stage action so it's visible in the terminal log.

**Why this is the right primary fix:** It preserves work that the agent produced. The agent completed its task and deposited the file — the only thing missing was a `git commit`. This is a mechanical omission that Bellows can fix without judgment.

### Shape (b): FAIL-LOUD — Gate Failure When Declared Deposit Is Uncommitted at Teardown Pause

**Location:** `gates.py:_gate_deposit_exists()` — extend to check git commit status.

**Mechanism:**
1. After confirming the file exists on disk (current behavior), additionally check `git status --porcelain -- <path>` in the worktree.
2. If the file shows as untracked (`??`) or unstaged-new, append a gate failure: `deposit_uncommitted: <path> exists on disk but is not committed — will be lost at teardown`.
3. This gate failure routes the plan to verdict-pending with a descriptive failure, surfacing the issue to the CEO.

**Why this is the right secondary fix:** If (a) fails for any reason (path resolution mismatch, git error, edge case), (b) catches the issue loudly rather than silently succeeding. Together, (a)+(b) provides defense-in-depth.

### Recommendation: (a) + (b)

| Shape | Role | Alone sufficient? |
|---|---|---|
| (a) PRESERVE | Fixes the common case automatically | No — could silently fail on path mismatch |
| (b) FAIL-LOUD | Catches edge cases loudly | No — forces re-dispatch for a fixable condition |
| **(a)+(b)** | **Primary fix + safety net** | **Yes — mechanical + observable** |

### Interaction with Hardened Teardown/Resume Family (CRITICAL)

| Component | Impact | Reasoning |
|---|---|---|
| `_teardown_worktree` land-or-raise contract | **UNCHANGED** | Auto-stage runs BEFORE teardown is called. It adds commits to the worktree branch. The merge step sees these commits normally through its existing path. |
| Gap-1b guard (block continue over uncleared `worktree_teardown` failure) | **UNCHANGED** | Auto-staging is a pre-teardown step in the step-completion path. It does not touch the teardown failure handling or the continue-verdict path. |
| Gap-1c (re-attempt recoverable dirty-tree teardown on continue-resume) | **UNCHANGED** | Gap-1c operates at resume time in `_consume_verdicts`. Auto-staging operates at step-completion time, before the first teardown attempt. |
| Stranded-cleanup preserve-branch logic (Gap 2a) | **UNCHANGED** | Gap-2a operates in `_create_worktree` during stranded-cleanup. Auto-staging operates in the step-completion path, a completely separate code path. |
| Deposit exists gate (`gates.py:_gate_deposit_exists`) | **EXTENDED** — (b) adds a git-status check after the existing `os.path.isfile` check. The existing check is preserved; (b) is purely additive. |

**Confirmation: the proposed changes are strictly additive to the hardened teardown family. No existing contract, guard, or safety mechanism is altered.**

---

## Section 4 — Test Surface

### Positive Tests (new behavior works)

1. **`test_auto_stage_preserves_untracked_deposit_on_teardown`** (`tests/test_worktree.py`): Create worktree → write untracked file matching a declared deposit → run auto-stage logic → teardown → assert file exists on main after merge.

2. **`test_auto_stage_handles_multiple_deposits`** (`tests/test_worktree.py`): Multiple declared deposits: one committed, one untracked, one staged-only → auto-stage → teardown → all three exist on main.

3. **`test_gate_fails_on_uncommitted_deposit`** (`tests/test_gates.py`): Mock `_resolve_deposit_path` to find a file, mock `git status --porcelain` to return `??` → gate fails with `deposit_uncommitted` evidence string.

4. **`test_gate_deposit_uncommitted_evidence_message`** (`tests/test_gates.py`): Verify the failure evidence contains the deposit path and a clear description of the uncommitted state.

### Negative / Regression Tests (existing behavior preserved)

5. **`test_teardown_merges_commits`** (existing, `test_worktree.py:168`): Committed files still merge correctly → PASS.

6. **`test_teardown_proceeds_on_empty_commit_list`** (existing, `test_worktree.py:314`): No commits, no deposits → teardown proceeds without error → PASS.

7. **`test_landing_tolerates_dirty_main_invariant`** (existing, `test_worktree.py:588`): Dirty main + committed worktree files → merge succeeds → PASS.

8. **`test_auto_stage_noop_when_all_committed`** (`tests/test_worktree.py`): All declared deposits already committed → no extra commit created, no log output → clean no-op.

9. **`test_gate_passes_when_deposit_committed`** (`tests/test_gates.py`): Committed deposit at gate time → gate passes (existing behavior preserved, regression check).

10. **`test_teardown_raises_on_git_log_exception`** (existing, `test_worktree.py:256`): Git-log failure → WorktreeTeardownError raised → PASS (confirms auto-stage doesn't interfere with the fail-safe).

---

## Section 5 — Layer Impact + Executable Hand-Off

**Affected layer:** Layer 1 (mechanical — staging/diff/gate logic)

### Files the Executable Will Touch

| File | Change |
|---|---|
| `bellows.py` | Add `_auto_stage_deposits()` helper; call it at the three pre-teardown sites (~lines 530, 623, 651) |
| `gates.py` | Extend `_gate_deposit_exists()` with git-status commit check |
| `tests/test_worktree.py` | Add tests 1, 2, 8 (auto-stage positive + no-op regression) |
| `tests/test_gates.py` | Add tests 3, 4, 9 (gate uncommitted-deposit positive + regression) |
| `knowledge/BACKLOG.md` | Update BACKLOG #1 entry status to reference this diagnostic |

### Constraints

- **Daemon restart required** after fix deployment (new bellows.py code).
- **Tight-scope:** Changes limited to the step-completion → teardown path (auto-stage) and the deposit_exists gate (commit check). No changes to `_teardown_worktree` itself, no changes to runner.py, no changes to verdict.py.
- **Self-fix applied:** This diagnostic's own deposit is explicitly `git add`ed + committed before finishing (self-protection against the very bug being diagnosed).

### Gap Assessment Table

| Gap | Current State (file:line) | Proposed State | Change Required |
|---|---|---|---|
| Untracked deposits lost at teardown | `bellows.py:987-1002` — worktree removal destroys untracked files silently | Pre-teardown auto-stage commits declared deposits | Add `_auto_stage_deposits()` call before each `_teardown_worktree()` invocation |
| `deposit_exists` gate blind to git status | `gates.py:366` — `os.path.isfile()` only, no git awareness | Gate fails when deposit is uncommitted (untracked/unstaged) | Extend `_gate_deposit_exists` with `git status --porcelain` check |
| `files_changed` blind to untracked files | `bellows.py:741` — `git diff` excludes untracked | Auto-stage makes files committed before diff runs | No direct change needed — auto-stage at step end makes the diff capture them on subsequent steps |

---

## Section 6 — Verification Blocks

### Rule 39 Verification Triples

| # | Claim | Query | Expected Output |
|---|---|---|---|
| 1 | There is no auto-staging code in bellows.py, gates.py, or runner.py | `grep -rn "auto.stage\|git add.*knowledge" bellows.py gates.py runner.py` | No matches (zero auto-staging logic exists) |
| 2 | `_teardown_worktree` merges via `git merge`, not file copy | Read `bellows.py:966-984` | `git merge --ff-only branch_name` with `--no-ff` fallback; no `cp`, `shutil.copy`, or file-iteration logic |
| 3 | `_resolve_deposit_path` uses `os.path.isfile`/`os.path.isdir` only, no git status | Read `gates.py:309-347` | Only `os.path.isfile()` and `os.path.isdir()` checks; no subprocess calls, no `git status` |
| 4 | `_parse_diff_stat` uses `git diff` which excludes untracked files | Read `bellows.py:741` | Command is `git diff --stat <pre_sha> -- .`; `git diff` by design excludes untracked files |
| 5 | The three pre-teardown call sites are at bellows.py lines ~531, ~623, ~651 | `grep -n "_teardown_worktree" bellows.py` | Three calls: mid-plan pause (~531), final-step pause (~624), auto-close (~652) |
| 6 | `test_teardown_proceeds_on_empty_commit_list` confirms empty-commit is legitimate | Read `tests/test_worktree.py:314-330` | Test creates worktree, makes no commits, calls `_teardown_worktree()`, asserts no error and worktree removed |
