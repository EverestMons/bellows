# Worktree Teardown Dirty-Tree Pre-Check — Surface Characterization

**Date:** 2026-05-27 | **Agent:** Bellows Systems Analyst | **Step:** 1 (SA)

---

## Section 1 — Cherry-pick call site map

The `_teardown_worktree` function is defined at `bellows.py:799-914`. The cherry-pick site is at lines 856-870.

**Pre-cherry-pick operations (in order):**

1. **No-op guard** (line 805): `if wt_path == project_path: return` — skips teardown for in-place execution (no worktree created).
2. **Main branch detection** (lines 809-823): `git symbolic-ref --short refs/remotes/origin/HEAD` with `cwd=project_path`. Falls back to `"main"`.
3. **Commit enumeration** (lines 826-833): `git log --format=%H HEAD --not <main_branch>` with `cwd=wt_path`. Collects SHAs from the worktree's detached HEAD, reversed to oldest-first for ordered cherry-pick.
4. **Stale index.lock removal** (lines 836-853): Detects and removes `.git/index.lock` in `project_path`. Stale (>5s) removed immediately; fresh lock waited 3s then removed.

**Cherry-pick loop** (lines 856-870):
```python
for sha in commit_shas:
    if not sha.strip():
        continue
    result = subprocess.run(
        ["git", "--no-pager", "cherry-pick", sha],
        cwd=project_path, capture_output=True, text=True, timeout=60,
    )
    if result.returncode != 0:
        subprocess.run(
            ["git", "--no-pager", "cherry-pick", "--abort"],
            cwd=project_path, capture_output=True, text=True, timeout=10,
        )
        raise WorktreeTeardownError(
            f"cherry-pick conflict on {sha} for slug {slug}: {result.stderr.strip()}"
        )
```

**Post-cherry-pick operations:**

5. **Dirty file copy-back** (lines 873-895): `git status --porcelain` in wt_path; copies modified/added files from worktree to project_path.
6. **Worktree removal** (lines 898-913): `git worktree remove --force`; fallback `shutil.rmtree` if directory persists.

**Error-handling flow:** `WorktreeTeardownError` propagates to the caller. Three call sites in `run_plan`:

- **Mid-plan pause** (lines 521-525): inside the `while not is_final_step` loop. Caught; `_pause_reason` overridden to `"gate_failure"`; failure dict appended with `{"gate": "worktree_teardown", "evidence": str(e)}`.
- **Final-step pause** (lines 614-618): same pattern, after the loop's final-step gate check.
- **Auto-close** (lines 643-658): same pattern; converts auto-close to `gate_failure` pause with verdict request.

All three sites flow into `verdict.post_verdict_request` with the failure dict in `gate_result["failures"]`.

---

## Section 2 — Pre-check insertion point

The dirty-tree check should be inserted **between the stale index.lock cleanup (line 853) and the cherry-pick loop (line 856)** — specifically at **line 855** (currently a blank line or comment before `# (c) Cherry-pick each commit onto main checkout`).

**Insertion point rationale:** This is the last point before any cherry-pick attempt. The index.lock cleanup must precede the dirty-tree check (a held lock would cause `git status` itself to fail or produce misleading output).

**cwd context:** The check must run against the **main checkout's working tree** at `project_path`, NOT the worktree at `wt_path`. The cherry-pick runs with `cwd=project_path` (line 860), so the dirty-tree check must use the same cwd to detect state that would conflict.

**Subprocess shape:**
```python
result = subprocess.run(
    ["git", "--no-pager", "status", "--porcelain"],
    cwd=project_path, capture_output=True, text=True, timeout=10,
)
```

**Predicate:** Dirty if `result.stdout.strip()` is non-empty.

**On dirty detection:** Raise `WorktreeTeardownError` with a structured evidence string (Section 3). The existing `WorktreeTeardownError` handler at the caller sites already produces the correct `gate_failure` pause flow with verdict request.

---

## Section 3 — Pause-message format proposal

Per CEO pre-locked decisions:
- **Dirty-detection scope:** option (1a) — any uncommitted change triggers the pre-check.
- **Pause Reason Code:** option (2a) — new code `worktree_teardown_dirty_tree`.
- **Recovery-instructions content:** option (3a) — inline literal commands.

**Note on Pause Reason Code routing:** The `worktree_teardown_dirty_tree` code is NOT a new top-level `_pause_reason` enum value in `run_plan`. It flows through the existing `WorktreeTeardownError` → `gate_failure` path. The code appears in the `evidence` string of the failure dict `{"gate": "worktree_teardown_dirty_tree", ...}`, distinguishing it from the existing `worktree_teardown` gate (cherry-pick conflict). A follow-on PLANNER_TEMPLATE Rule 25 routing table edit may reference this gate name; filed in BACKLOG or shipped as companion plan.

**Proposed evidence string:**

```python
dirty_output = result.stdout.strip()
# Truncate to first 10 lines if longer
dirty_lines = dirty_output.splitlines()
if len(dirty_lines) > 10:
    dirty_display = "\n".join(dirty_lines[:10]) + f"\n... ({len(dirty_lines) - 10} more files)"
else:
    dirty_display = dirty_output

evidence = (
    f"worktree_teardown_dirty_tree: local main has uncommitted changes "
    f"that would conflict with cherry-pick from worktree.\n"
    f"\n"
    f"Dirty files in local main ({len(dirty_lines)} file(s)):\n"
    f"{dirty_display}\n"
    f"\n"
    f"Recovery (choose based on dirty-file type):\n"
    f"\n"
    f"  Sub-variant A — untracked artifact (e.g., claim-rename):\n"
    f"    cd {project_path}\n"
    f"    git add <file(s)>\n"
    f"    git commit -m 'chore: commit untracked artifact before teardown'\n"
    f"\n"
    f"  Sub-variant B — dirty bookkeeping file (e.g., PROJECT_STATUS.md):\n"
    f"    cd {project_path}\n"
    f"    git add <file(s)>\n"
    f"    git commit -m 'chore: commit dirty bookkeeping before teardown'\n"
    f"\n"
    f"  Then: re-issue continue verdict to retry teardown.\n"
    f"\n"
    f"Reference: LESSONS.md 2026-05-27 R2 recovery shape."
)
```

This is 22 lines (under the 30-line target). The CEO sees the dirty files, both recovery sub-variants, and the LESSONS pointer.

---

## Section 4 — Test surface enumeration

### New tests

**1. `test_teardown_pauses_when_local_main_dirty`** (~12 LOC)

Happy-path negative: mock `subprocess.run` so `git status --porcelain` returns non-empty output for the `project_path` cwd. Assert `WorktreeTeardownError` is raised. Assert no cherry-pick subprocess call was made (cherry-pick should never be attempted). Assert the error message contains `worktree_teardown_dirty_tree`.

**2. `test_teardown_proceeds_when_local_main_clean`** (~10 LOC)

Happy-path positive: mock `subprocess.run` so `git status --porcelain` returns empty stdout for the `project_path` cwd. Assert no `WorktreeTeardownError` raised. Assert cherry-pick subprocess calls proceed normally (the rest of teardown runs).

**3. `test_teardown_dirty_tree_evidence_contains_recovery_commands`** (~15 LOC)

Mock `subprocess.run` to return a dirty `git status --porcelain` output (e.g., `" M PROJECT_STATUS.md\n?? untracked.md"`). Catch the `WorktreeTeardownError`. Assert the error string contains:
- `worktree_teardown_dirty_tree`
- `Sub-variant A`
- `Sub-variant B`
- `LESSONS.md 2026-05-27`
- `PROJECT_STATUS.md` (from the dirty output)

### Existing test impact

**4. `test_run_plan_pauses_on_cherry_pick_conflict`** (line 2179) — **remains valid, no fixture change needed.** This test patches `_teardown_worktree` entirely (line 2198: `patch("bellows._teardown_worktree", side_effect=bellows.WorktreeTeardownError(...))`), so the pre-check code inside `_teardown_worktree` never runs. The test exercises the *caller's* handling of `WorktreeTeardownError`, not the internal pre-check logic. It continues to cover the post-pre-check-clean cherry-pick-conflict path (the case where local main is clean but the cherry-pick itself fails due to content conflicts).

**5. Existing teardown tests** (lines 2265, 2795, 2823, 2851) — all mock `subprocess.run` directly. Need review:
- `test_teardown_worktree_noop_when_wt_equals_project` (line 2265): unaffected — exits at the `wt_path == project_path` guard before the pre-check.
- `test_teardown_worktree_removes_stale_index_lock` (line 2795): **needs fixture update** — the `fake_subprocess_run` must return empty stdout for `git status --porcelain` calls (currently returns `""` for all commands via `mock_result.stdout = ""`, which is correct by coincidence — empty string means clean). Verify explicitly.
- `test_teardown_worktree_waits_for_fresh_index_lock` (line 2823): same as above — verify `stdout = ""` handles the pre-check cleanly.
- `test_teardown_worktree_force_removes_orphaned_directory` (line 2851): same pattern. Should pass without changes since `stdout = ""` is clean.

**LOC estimate:** 3 new tests ~37 LOC total; 0-2 lines of fixture adjustment in existing tests ~2 LOC. **Suite delta: ~40 LOC.**

---

## Section 5 — Edge cases and risks

### 1. Race window

The dirty-tree check runs at time T; the cherry-pick runs at time T+ε. The interval between them is:
- The `for sha in commit_shas` loop entry (a few microseconds of Python overhead)
- No I/O between the pre-check and the first cherry-pick

**Estimate:** ε < 1ms in practice. The only realistic race is an external process (e.g., Planner editing PROJECT_STATUS.md in another terminal) writing to the working tree during this window. This is the same race window as the index.lock check, and the probability is negligible.

**Recommendation:** accept the race. A re-check immediately before cherry-pick would double the `git status` subprocess calls (one per SHA) for negligible safety gain. The existing cherry-pick error handling catches any race-induced conflict and surfaces it through the existing `WorktreeTeardownError` path.

### 2. Worktree-vs-main cwd confusion

The pre-check MUST run with `cwd=project_path` (the main checkout), NOT `cwd=wt_path` (the worktree). The cherry-pick itself runs with `cwd=project_path` (line 860), so dirty state in the **main checkout** is what blocks it.

**Test fixture that catches wrong-cwd regression:** `test_teardown_pauses_when_local_main_dirty` should use a `fake_subprocess_run` that returns dirty output ONLY when `kwargs.get("cwd") == project_path` and the command is `git status --porcelain`. If cwd is `wt_path`, return clean. This ensures the pre-check is checking the right tree.

### 3. Submodule dirty state

`git status --porcelain` includes submodule pointer changes (e.g., ` M bellows` when the bellows submodule's HEAD has advanced). The governance root has bellows + anvil as submodules.

**Recommendation:** accept. A dirty submodule pointer at main IS a teardown risk — if the agent's cherry-pick modifies the same submodule pointer, the cherry-pick would conflict. The pre-check firing on submodule pointer drift is the correct conservative behavior. False-positive cost is one CEO decision; false-negative cost is the cryptic cherry-pick conflict. This aligns with the CEO's pre-locked decision (1a) — any uncommitted change triggers.

### 4. Bellows-self plan dispatch

When the project being torn down is bellows itself (Bellows-self mode), `project_path` is the bellows directory (e.g., `/Users/marklehn/Developer/GitHub/bellows`). BUT: bellows is a submodule of the governance root. `_create_worktree` checks for `os.path.join(project_path, ".git")` — for a submodule, `.git` is a file (pointer to the parent's `.git/modules/`), not a directory. The `os.path.exists` check passes, so worktrees ARE created for bellows-self.

The pre-check runs `git status --porcelain` with `cwd=project_path` (the bellows submodule directory). This correctly checks the bellows submodule's working tree, not the governance root's. **No sentinel-skip needed.** The pre-check applies correctly to Bellows-self.

### 5. Interaction with other teardown failure paths

The pre-check is **additive**, inserted before the cherry-pick loop. It does NOT replace any existing failure path:

- **Cherry-pick content conflicts** (existing path at lines 863-870): still fires if local main is clean but the cherry-pick produces a content conflict (e.g., two agents modified the same line). The pre-check does not catch this — it only catches dirty-tree state.
- **`git worktree remove --force` failures** (lines 898-906): unaffected — these occur after the cherry-pick loop, downstream of the pre-check.
- **Dirty file copy-back failures** (lines 873-895): unaffected — downstream of cherry-pick.
- **Worktree creation failures** (separate `WorktreeCreationError` path at lines 432-448): completely independent; the pre-check is inside `_teardown_worktree`, not `_create_worktree`.

The pre-check adds a new failure mode that fires BEFORE the cherry-pick, preventing the cryptic cherry-pick conflict message. The existing cherry-pick conflict path remains as a fallback for conflicts that are not caused by dirty-tree state.

---

## Section 6 — LOC estimate

| Component | LOC |
|---|---|
| Production code in `bellows.py` (dirty-tree check + evidence string construction) | ~25 |
| Test code in `tests/test_bellows.py` (3 new tests + fixture adjustments) | ~40 |
| Helper extraction | 0 (no shared helper needed — check is self-contained) |
| **Total** | **~65** |

**BACKLOG estimate verification:** The BACKLOG entry estimated `~20 LOC pre-cherry-pick dirty-tree check` for production code. The actual estimate is ~25 LOC, slightly higher due to the multi-line evidence string with recovery instructions (the BACKLOG entry likely estimated the check + raise without the detailed evidence formatting). The estimate is directionally correct and within the "small" effort band.

---

## Section 7 — Open questions for the Planner

1. **PLANNER_TEMPLATE Rule 25 routing table update.** The new gate name `worktree_teardown_dirty_tree` in the failure dict needs to be recognized by the Planner's verdict-consumption routing. The existing `worktree_teardown` gate routes to the generic "cherry-pick conflict" handling. The new gate should route to "commit dirty files, re-issue continue verdict" guidance. **Decision needed:** ship the Rule 25 update as a companion plan in the same session, or file a BACKLOG entry and ship separately? This is a governance-root edit, not a bellows code change.

2. **Evidence string reference to LESSONS.md 2026-05-27.** The proposed evidence string references `LESSONS.md 2026-05-27 R2 recovery shape`. At the time of this diagnostic, the R2 recovery shape is documented in `NEXT_SESSION.md` (lines 56, 113) but may not yet be promoted to LESSONS.md as a formal entry. If the executable plan ships before the LESSONS promotion, the pointer will be forward-looking. **Decision needed:** should the evidence string reference `NEXT_SESSION.md` instead, or should the LESSONS promotion be a pre-requisite for the executable plan?

3. **`git status --porcelain` failure handling.** If `git status --porcelain` itself fails (e.g., corrupt index, git not found), should the pre-check (a) treat it as clean and proceed to cherry-pick (fail-open), or (b) treat it as dirty and pause (fail-closed)? **Recommendation:** fail-open — the cherry-pick itself will fail if the state is truly bad, producing the existing error path. Fail-closed would add a new failure mode for transient git errors.

---

## Output Receipt
**Agent:** Bellows Systems Analyst
**Step:** 1 (SA)
**Status:** Complete

### What Was Done
Characterized the full surface required to ship a pre-cherry-pick dirty-tree check in `_teardown_worktree`. Mapped the cherry-pick call site, identified the insertion point (line 855), proposed the evidence string format with R2 recovery instructions, enumerated 3 new tests + existing test impact, analyzed 5 edge cases, and estimated ~65 total LOC.

### Files Deposited
- `knowledge/research/worktree-teardown-dirty-tree-precheck-surface-2026-05-27.md` — SA surface characterization (7 sections)

### Files Created or Modified (Code)
- None (diagnostic only)

### Decisions Made
- Pre-check insertion point: after index.lock cleanup (line 853), before cherry-pick loop (line 856)
- Gate name: `worktree_teardown_dirty_tree` (distinct from existing `worktree_teardown`)
- Evidence string format: 22-line structured message with dirty file listing + dual-variant recovery commands
- Race window: accept (ε < 1ms, existing cherry-pick handler catches any race-induced conflict)
- Submodule dirty state: accept (fire pre-check — correct conservative behavior per CEO decision 1a)
- Bellows-self: no sentinel-skip needed (submodule .git file passes exists check; cwd correctly scoped)
- Existing test `test_run_plan_pauses_on_cherry_pick_conflict`: no fixture change needed (patches entire `_teardown_worktree`)

### Flags for CEO
- None

### Flags for Next Step
- Three open questions for Planner (Section 7): Rule 25 routing table companion plan timing, LESSONS.md reference validity, `git status` failure-mode handling (fail-open recommended)
