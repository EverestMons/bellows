# `file_change_audit` False-Negative — Root Cause Analysis

**Date:** 2026-05-25 | **Investigator:** Bellows Systems Analyst

---

## (a) Lifecycle Timeline: pre_diff → agent_run → commit → post_diff → teardown

```
1. _create_worktree(project_path, plan_slug)     → wt_path created (clean)
2. pre_diff = _capture_git_diff(wt_path)          → git diff --stat → "" (clean tree)
3. runner.run_step(prompt, wt_path, ...)          → agent executes in wt_path
   3a. Agent reads files, makes edits              → working tree dirty
   3b. Agent runs `git add` + `git commit`         → working tree clean again ← KEY
4. post_diff = _capture_git_diff(wt_path)         → git diff --stat → "" (clean tree)
5. files_changed = _parse_diff_stat(post_diff, pre_diff, project_path)
   → pre_diff="" and post_diff="" → parse_stat_map returns {} for both → [] ← BUG
6. gates.check(..., files_changed=[])             → _gate_file_change_audit reports "0 files"
                                                   → _gate_scope_check short-circuits (empty list)
7. verdict.post_verdict_request(...)              → gate result shipped with empty files_changed
8. _teardown_worktree(wt_path)                    → worktree removed
```

The critical gap is between steps 3b and 4. `git diff --stat` (without `--cached` or a commit range) compares the working tree against the index. Once the agent commits, the working tree is clean and indistinguishable from the pre-step state.

---

## (b) H1 Test Results — Commits Hide Diff

**Hypothesis:** `git --no-pager diff --stat --relative -- .` shows only uncommitted changes. Agents commit during the step, leaving the working tree clean at post-step capture.

**Test environment:** Scratch worktree at `/tmp/bellows-h1-test`, detached HEAD at `0601471`.

| Capture | Command output | Content |
|---|---|---|
| `pre_clean` | `git diff --stat --relative -- .` before any edit | `""` (empty) |
| `post_dirty` | Same command after `echo >> bellows.py` (tracked file) | `bellows.py \| 2 ++` |
| `post_committed` | Same command after `git add && git commit` | `""` (empty) |

**Result:** `post_committed` is empty despite a real edit and commit — **exactly as H1 predicts.** The diff command cannot detect committed changes.

---

## (c) H2 Examination — Today's Run Logs

**Target run:** `executable-extract-plan-required-deposits-set-to-list-2026-05-25`

**Log file:** `logs/20260525-201532-step.json` (Step 1 — DEV)

**Evidence from log line 67-68:** The agent ran `git add gates.py tests/test_gates.py ...` and committed with message `fix(gates): _extract_plan_required_deposits set→list ...` producing commit `a386eb7`. This happened **during** the agent's step execution (inside `runner.run_step`), before bellows captured `post_diff` at bellows.py:486.

**Verdict files confirm the false-negative:**
- `processed-verdict-...-step-1.md` line 19: `file_change_audit | PASS | 0 files modified` — "despite git log showing 3 files / 136 insertions"
- `processed-verdict-...-step-2.md` line 14: same false-negative, noted as "7th reproduction"

**Conclusion:** H2 (timing race vs teardown) is **not** the cause. The agent commits well before teardown. H1 is fully supported — the commit happens during the step, between pre_diff and post_diff capture, leaving both captures empty.

---

## (d) H3 Analysis — cwd / Path Scope

**Naming discrepancy:** `_capture_git_diff` parameter is named `project_path` (bellows.py:678), but all 4 call sites (lines 451, 486, 542, 577) pass `wt_path`. Inside the function, `cwd=project_path` (line 690) therefore correctly receives the worktree path.

**Git root verification:**
```
$ git -C <worktree> rev-parse --show-toplevel
→ /Users/.../bellows/.bellows-worktrees/file-change-audit-false-negative-2026-05-25
```

The worktree's `--show-toplevel` resolves to the worktree itself, not the main repo. The `.git` file in the worktree points to the main repo's worktrees directory, which is standard git worktree behavior. The `cwd` is correct — `git diff` runs scoped to the worktree.

**Conclusion:** The naming discrepancy (`project_path` vs `wt_path`) is cosmetic. The actual path passed is correct. H3 is **refuted** — the diff is captured in the right directory.

---

## (e) Controlled Reproduction

**Setup:** Scratch worktree at `/tmp/bellows-repro`, detached HEAD.

**Sequence (mirrors bellows.py flow exactly):**
1. `pre_diff = capture_git_diff(wt_path)` → `""`
2. Edit `bellows.py` (append marker text)
3. `git add bellows.py && git commit -m "repro: controlled test commit"`
4. `post_diff = capture_git_diff(wt_path)` → `""`
5. `files_changed = parse_diff_stat(post_diff, pre_diff, wt_path)` → `[]`

**Result:** `files_changed` is `[]` despite a real edit and commit. **Smoking-gun reproduction of H1.**

The intermediate capture (between edit and commit) correctly showed `bellows.py | 2 ++`, confirming the diff command works when there are uncommitted changes. The commit clears the signal.

---

## (f) Verdict Per Hypothesis

| Hypothesis | Rating | Rationale |
|---|---|---|
| **H1 — Commits hide diff** | **CONFIRMED** | Direct reproduction: `git diff --stat` returns empty after commit. All 4 Bellows call sites capture post-step diff after agent has already committed. Corroborated by log evidence from today's run (`a386eb7` committed during step). |
| **H2 — Timing race vs teardown** | **LOW (refuted)** | Log evidence shows the agent commits during `runner.run_step`, well before `post_diff` capture and teardown. Teardown timing is irrelevant — the diff is already empty by step 4 of the lifecycle. |
| **H3 — Wrong scope / cwd mismatch** | **LOW (refuted)** | `_capture_git_diff` receives `wt_path` (correct), and `rev-parse --show-toplevel` confirms the worktree resolves to its own root. Parameter naming (`project_path`) is misleading but functionally correct. |

**Root cause:** H1 is the sole root cause. `_capture_git_diff` uses `git diff --stat` which compares working tree to index. Once changes are committed, this diff is empty. The diff-of-diffs approach (`_parse_diff_stat`) inherits this blindness — `{} - {} = {}` regardless of commits.

---

## (g) Verification Blocks (Rule 39)

### V1: `git diff --stat` returns empty after commit

**Claim:** `git --no-pager diff --stat --relative -- .` produces empty output in a worktree after all changes are committed.

**Query:**
```bash
git worktree add /tmp/bellows-v1 HEAD --detach
cd /tmp/bellows-v1
echo "# v1 marker" >> bellows.py
git add bellows.py && git commit -m "v1 check"
git --no-pager diff --stat --relative -- .
# Expected: empty output (no lines)
git worktree remove /tmp/bellows-v1 --force
```

**Expected output:** The `git diff --stat` command produces zero lines of output.

### V2: `_parse_diff_stat` returns `[]` when both inputs are empty

**Claim:** `_parse_diff_stat("", "", "/any/path")` returns `[]`.

**Query:**
```python
python3 -c "
import os
def parse_diff_stat(post_diff, pre_diff, project_path=None):
    def parse_stat_map(diff_text):
        result = {}
        for line in diff_text.strip().splitlines():
            line = line.strip()
            if '|' in line:
                filename, stat = line.split('|', 1)
                filename = filename.strip()
                if filename:
                    result[filename] = stat.strip()
        return result
    pre_map = parse_stat_map(pre_diff)
    post_map = parse_stat_map(post_diff)
    changed = [f for f, s in post_map.items() if pre_map.get(f) != s]
    if project_path is not None:
        changed = [f for f in changed if '..' not in os.path.normpath(f).split(os.sep)]
    return sorted(changed)

result = parse_diff_stat('', '', '/any/path')
assert result == [], f'Expected [], got {result}'
print('PASS: returns []')
"
```

**Expected output:** `PASS: returns []`

### V3: Agent commits during `runner.run_step` (not after)

**Claim:** The agent's commit occurs inside the `runner.run_step` call, before bellows captures `post_diff`.

**Query:**
```bash
# In any recent step log, search for commit evidence within the runner output:
python3 -c "
import json, sys
d = json.load(sys.stdin)
raw = d.get('raw_output', '')
if '[detached HEAD' in raw:
    print('CONFIRMED: agent committed during step')
else:
    print('NOT FOUND')
" < logs/20260525-201532-step.json
```

**Expected output:** `CONFIRMED: agent committed during step`

---

## (h) Related Observations

1. **Parameter naming discrepancy in `_capture_git_diff`:** The function signature says `project_path` (bellows.py:678) but all callers pass `wt_path`. The docstring also references "project subtree" semantics. A fix plan should rename the parameter to `wt_path` for clarity, though this is cosmetic and does not affect behavior.

2. **`_gate_scope_check` silent no-op:** When `files_changed` is empty, `_gate_scope_check` returns immediately (gates.py:601). This means **scope-violation detection is effectively disabled** for every step where the agent commits — which is the standard agent pattern. The false-negative in `file_change_audit` cascades into a complete bypass of scope checking.

3. **`_parse_diff_stat`'s `..` path filtering:** The `..` component filter (bellows.py:724-728) is a separate defense against out-of-scope paths. With H1 confirmed, this filter never fires on committed changes because `post_map` is always empty. Once the diff capture is fixed, this filter should be retested to ensure it interacts correctly with the new diff source.

4. **Fix direction (not a proposal — for context only):** The fix will likely need to replace `git diff --stat` with a commit-range diff, e.g., `git diff --stat HEAD~N..HEAD` or compare `HEAD` SHAs before/after the step. The pre/post capture sites are correct; only the `_capture_git_diff` implementation needs to change.

---

## (i) Output Receipt

**Status:** Complete

**Artifacts produced:**
- This file: `knowledge/research/file-change-audit-false-negative-2026-05-25.md`

**Summary:** H1 (commits hide diff) is **CONFIRMED** as the sole root cause of the `file_change_audit` false-negative. `git diff --stat` compares working tree to index and returns empty output after commits. Since agents commit during their step as standard practice, both `pre_diff` and `post_diff` are empty, yielding `files_changed=[]`. This cascades into `_gate_scope_check` silently no-oping, effectively disabling scope-violation detection for all code-edit steps.
