# scope_check Monorepo Topology — Diagnostic Findings
**Date:** 2026-04-28 | **Diagnostic:** diagnostic-scope-check-monorepo-topology-2026-04-28 | **Agent:** Bellows Systems Analyst

---

## Q1 — Repo Topology Audit

| Project | .git status | Notes |
|---|---|---|
| `/Users/marklehn/Desktop/GitHub/` (governance root) | **directory** | Full `.git` directory with config, objects, refs — this is the parent repo |
| invoice-pulse | **directory** | Standalone repo — full `.git` with hooks, objects, refs, worktrees |
| BrewBuddy | **directory** | Standalone repo |
| study | **directory** | Standalone repo |
| ai-career-digest | **directory** | Standalone repo |
| freight-kb | **directory** | Standalone repo |
| forge | **directory** | Standalone repo |
| anvil | **directory** | Standalone repo |
| bellows | **absent** | `ls: /Users/marklehn/Desktop/GitHub/bellows/.git: No such file or directory` |

**Summary:** Bellows is the ONLY watched project without its own `.git` directory. All seven other projects are standalone repos with independent `.git` directories. Bellows is a plain subdirectory of the governance-root repo at `/Users/marklehn/Desktop/GitHub/`.

---

## Q2 — `git rev-parse --show-toplevel` Behavior

| Project | project_path | git_toplevel | Match |
|---|---|---|---|
| invoice-pulse | `/Users/marklehn/Desktop/GitHub/invoice-pulse` | `/Users/marklehn/Desktop/GitHub/invoice-pulse` | Y |
| BrewBuddy | `/Users/marklehn/Desktop/GitHub/BrewBuddy` | `/Users/marklehn/Desktop/GitHub/BrewBuddy` | Y |
| study | `/Users/marklehn/Desktop/GitHub/study` | `/Users/marklehn/Desktop/GitHub/study` | Y |
| ai-career-digest | `/Users/marklehn/Desktop/GitHub/ai-career-digest` | `/Users/marklehn/Desktop/GitHub/ai-career-digest` | Y |
| freight-kb | `/Users/marklehn/Desktop/GitHub/freight-kb` | `/Users/marklehn/Desktop/GitHub/freight-kb` | Y |
| forge | `/Users/marklehn/Desktop/GitHub/forge` | `/Users/marklehn/Desktop/GitHub/forge` | Y |
| anvil | `/Users/marklehn/Desktop/GitHub/anvil` | `/Users/marklehn/Desktop/GitHub/anvil` | Y |
| bellows | `/Users/marklehn/Desktop/GitHub/bellows` | `/Users/marklehn/Desktop/GitHub` | **N** |

**Summary:** Only bellows has `match=N`. Its `git_toplevel` resolves to the governance root (`/Users/marklehn/Desktop/GitHub/`), confirming that when `_capture_git_diff(project_path)` runs `git diff --stat` from `cwd=bellows`, git operates on the entire governance-root repo, not a bellows-scoped repo.

---

## Q3 — `git diff --stat` Path-Scoping Experiments

Test subject: bellows (the only `match=N` project). Current dirty state in the governance-root repo: `LESSONS.md` (47 insertions) and `anvil` (submodule pointer, 0 insertions).

### (a) Baseline: `git diff --stat` from `cwd=bellows`
```
 LESSONS.md | 47 +++++++++++++++++++++++++++++++++++++++++++++++
 anvil      |  0
 2 files changed, 47 insertions(+)
```
**Observation:** Reports the entire monorepo's diff. Paths are relative to the governance root (repo root), NOT relative to `cwd=bellows`. `LESSONS.md` and `anvil` have no `..` components — they are clean root-relative paths. This is the bug: the `_parse_diff_stat` filter checks for `..` components, but these paths don't have any.

### (b) Path-scoped: `git diff --stat -- bellows/` from `cwd=bellows`
```
(empty)
```
**Observation:** Empty because `bellows/` as a pathspec from `cwd=bellows` resolves to `bellows/bellows/` relative to the repo root — a nonexistent path. This syntax does NOT work for scoping.

### (c) `-C` flag: `git -C bellows diff --stat`
```
 LESSONS.md | 47 +++++++++++++++++++++++++++++++++++++++++++++++
 anvil      |  0
 2 files changed, 47 insertions(+)
```
**Observation:** Identical to (a). The `-C` flag sets working directory but git still operates on the full repo. No scoping effect.

### (d) Path-scoped from governance root: `git diff --stat -- bellows/` from `cwd=/Users/marklehn/Desktop/GitHub/`
```
(empty)
```
**Observation:** Empty because there are no actual changes inside `bellows/`. This correctly scopes to bellows files only. The output format (when files exist) would still be pipe-delimited (`filename | stat`) and parseable by `_parse_diff_stat`.

### (e) Dot pathspec: `git diff --stat -- .` from `cwd=bellows`
```
(empty)
```
**Observation:** Empty because there are no changes inside bellows. `-- .` from `cwd=bellows` correctly resolves to `bellows/` relative to the repo root. This IS the correct scoping syntax for `_capture_git_diff`. When bellows files do change, the output format would be standard `filename | stat` lines — parseable by `_parse_diff_stat`.

**Key finding on path format:** When `-- .` is used from `cwd=bellows`, git shows paths relative to the repo root by default (e.g., `bellows/some-file.py`). Adding `--relative` makes git show paths relative to cwd (e.g., `some-file.py`). The `--relative` flag is needed so that output paths match what plan step text and scope_check expect (relative paths like `knowledge/research/foo.md`, not `bellows/knowledge/research/foo.md`).

**Summary:** The correct fix syntax for `_capture_git_diff` when the project is nested is: `git --no-pager diff --stat --relative -- .`. For standalone repos (where cwd = repo root), this is equivalent to the current behavior: `-- .` covers all files, and `--relative` to root is a no-op. The fix is universally applicable — no conditional logic needed.

---

## Q4 — `_parse_diff_stat` Filter Sufficiency

**Current filter logic** (bellows.py:437-441):
```python
if project_path is not None:
    changed = [
        f for f in changed
        if ".." not in os.path.normpath(f).split(os.sep)
    ]
```

This filter drops any path whose normalized form contains a `..` path component.

**Analysis with example inputs from `git diff --stat` run from `cwd=bellows`:**

| Path from diff stat | `os.path.normpath(f).split(os.sep)` | Contains `..`? | Filtered? |
|---|---|---|---|
| `LESSONS.md` | `['LESSONS.md']` | No | **No — passes through** |
| `forge/foo.py` | `['forge', 'foo.py']` | No | **No — passes through** |
| `anvil/bar.txt` | `['anvil', 'bar.txt']` | No | **No — passes through** |
| `../LESSONS.md` (hypothetical) | `['..', 'LESSONS.md']` | Yes | Yes — filtered out |
| `../forge/foo.py` (hypothetical) | `['..', 'forge', 'foo.py']` | Yes | Yes — filtered out |

**Summary:** The filter does NOT exclude `LESSONS.md`, `forge/foo.py`, or `anvil/bar.txt` when those appear in the diff stat output from `cwd=bellows`. The paths have no `..` components because git reports them relative to the governance root (the repo root), not relative to the cwd. The `..`-component filter was designed for a standalone-repo scenario where out-of-project files genuinely have `../` prefixes. In the nested-repo scenario, all paths are clean governance-root-relative — the filter is structurally blind to the nested/non-nested distinction.

The prior BACKLOG #2 point fix (executable-scope-check-project-path-filter-2026-04-22) correctly fixed the standalone-repo case but did not account for the nested-repo case where bellows lacks its own `.git`. The existing tests (see Q5) all craft synthetic diff strings with `../` prefixes, matching the standalone-repo assumption.

---

## Q5 — Existing Test Inventory

Tests found in `tests/test_bellows.py`:

**`_capture_git_diff` usage in tests:**
- Lines 153, 210, 276, 323, 373, 613, 1114, 1147, 1183, 1225, 1272, 1315, 1362, 1630, 1690 — all mock `_capture_git_diff` with `return_value=""`, bypassing the actual git subprocess entirely. No test exercises the real git subprocess behavior.

**`_parse_diff_stat` unit tests (lines 453-561):**

| Test | Asserts | Would survive fix? |
|---|---|---|
| `test_parse_diff_stat_preexisting_unchanged_returns_empty` (456) | Pre-existing dirty file with unchanged stat → empty list | Yes — diff-of-diffs logic unchanged |
| `test_parse_diff_stat_new_file_only_in_post` (463) | New file only in post → returned | Yes |
| `test_parse_diff_stat_preexisting_changed_stat_is_reported` (470) | Changed stat → reported | Yes |
| `test_parse_diff_stat_summary_line_ignored` (477) | Summary line (no `|`) → ignored | Yes |
| `test_parse_diff_stat_empty_inputs_return_empty` (486) | Empty strings → empty list | Yes |
| `test_parse_diff_stat_no_project_path_returns_all` (495) | No project_path → all files including `../` paths | Yes — backward compat preserved |
| `test_parse_diff_stat_project_path_all_inside` (508) | project_path set, all paths inside → returned | Yes |
| `test_parse_diff_stat_project_path_filters_dotdot` (521) | `../anvil/bar.py` filtered out | Yes |
| `test_parse_diff_stat_project_path_filters_sibling_project` (534) | `../anvil/foo.py` filtered out | Yes |
| `test_parse_diff_stat_project_path_filters_repo_root` (542) | `../LESSONS.md` filtered out | Yes |
| `test_parse_diff_stat_project_path_keeps_deep_paths` (550) | Deep nested paths → returned | Yes |

**Summary:** All existing tests pass synthetic strings with `../` prefixes and test the filter for the standalone-repo case. None test the nested-repo case where paths appear WITHOUT `../` prefixes (e.g., `LESSONS.md`, `forge/foo.py`). If the fix is applied at the `_capture_git_diff` level (changing the git command to `-- .`), all existing `_parse_diff_stat` tests would still pass because the filter is downstream and the test inputs are synthetic. New test coverage is needed for:
1. `_capture_git_diff` integration test verifying `-- .` scoping from a nested project
2. End-to-end test confirming that files outside the project subtree are NOT reported in `files_changed` for a nested project

---

## Q6 — False-Negative Risk Audit

**Search scope:** All plans in `knowledge/decisions/Done/` for patterns indicating cross-project file operations: `git add ../`, `git add.*LESSONS`, governance-root `cd /Users/marklehn/Desktop/GitHub && git commit/add` patterns.

**Hits found:** 2 plans reference governance-root operations:

1. **executable-planner-template-rule-25-2026-04-18.md** — Step commits `PLANNER_TEMPLATE.md` from `cd /Users/marklehn/Desktop/GitHub && git add PLANNER_TEMPLATE.md && git commit`. This is a governance-root commit, not a bellows-directory commit.

2. **executable-planner-template-rule-26-2026-04-18.md** — Same pattern: `cd /Users/marklehn/Desktop/GitHub && git add PLANNER_TEMPLATE.md && git commit`.

**Analysis of false-negative risk:** Both plans commit their changes (via `git add` + `git commit`) from the governance root. After the commit, the file is no longer in the unstaged diff. `_capture_git_diff` captures `git diff --stat` (unstaged working tree vs. index), NOT `git log`. Committed files do NOT appear in `git diff --stat`. Therefore, even with the current unscoped diff, these governance-root commits would not be flagged by scope_check (they're committed before the post-step diff capture).

**Count of plans that legitimately need cross-project dirty-file detection:** 0.

**Additional search:** Grep for `git add ../` in Done/ plans — 0 hits. No plan in history adds uncommitted files from outside its project directory.

**Summary:** False-negative risk is effectively zero. No legitimate plan in history has depended on scope_check seeing uncommitted cross-project files. Scope_check can be cleanly scoped to the project subtree without an opt-out mechanism. The two governance-root edit plans commit their changes before the post-step diff capture, so scoping the diff to bellows would correctly report them as having zero bellows file changes (which is accurate — they modify PLANNER_TEMPLATE.md, not bellows files).

---

## Recommended Fix Shape

**This section describes the structural shape of the fix, NOT the implementation. The executable plan will be written by the Planner after CEO review.**

### Primary fix: scope `_capture_git_diff` to the project subtree

**Function:** `_capture_git_diff(project_path)` in `bellows.py:398-407`

**Current command:** `["git", "--no-pager", "diff", "--stat"]` with `cwd=project_path`

**Proposed command:** `["git", "--no-pager", "diff", "--stat", "--relative", "--", "."]` with `cwd=project_path`

**Effect of each addition:**
- `-- .` — pathspec restricting diff to files under the current directory (project subtree). For standalone repos where cwd = repo root, this is equivalent to no pathspec (`.` = entire repo). For nested repos like bellows, this restricts to just the project directory.
- `--relative` — makes output paths relative to cwd instead of relative to repo root. For standalone repos, this is a no-op (cwd IS repo root). For bellows, this changes output from `bellows/knowledge/foo.md` to `knowledge/foo.md`, which is what plan text and scope_check expect.

**Universality:** The fix applies to ALL projects uniformly — no conditional logic, no repo-root detection. For standalone repos (7 of 8 watched projects), the behavior is unchanged. For bellows (the only nested repo), the behavior is correctly scoped.

### Secondary: `_parse_diff_stat` `..`-component filter

**Recommendation:** Keep the existing `..`-component filter as defense-in-depth. It correctly handles the standalone-repo case and is harmless for the nested-repo case (where `-- .` already prevents out-of-project paths from appearing). No changes needed to `_parse_diff_stat`.

### Test coverage needed

1. New integration-style test for `_capture_git_diff`: mock `subprocess.run` and verify the command argv includes `--relative`, `--`, `.`
2. New `_parse_diff_stat` test case for the nested-repo scenario: paths WITHOUT `../` prefix (e.g., `LESSONS.md`, `forge/foo.py`) — verify these are handled correctly when the upstream `_capture_git_diff` fix is in place (i.e., they should never reach `_parse_diff_stat` because `-- .` excludes them)

### What does NOT need to change

- `_gate_scope_check` in `gates.py` — no changes; it consumes `files_changed` which will already be correctly scoped
- `_parse_diff_stat` filter logic — keep as-is for defense-in-depth
- `run_plan` call sites — no changes; they already pass `project_path` correctly
- Config format — no new fields needed
- No opt-out mechanism needed — false-negative risk is zero (Q6)

---

## Output Receipt
**Agent:** Bellows Systems Analyst
**Step:** 1 (single-step diagnostic)
**Status:** Complete

### What Was Done
Investigated six questions about the scope_check monorepo topology bug (BACKLOG #4). Confirmed bellows is the only nested project (no `.git`, `git_toplevel` mismatch), mapped the exact mechanism by which `_capture_git_diff` reports monorepo-wide diffs, demonstrated that the existing `..`-component filter in `_parse_diff_stat` is blind to nested-repo paths, inventoried existing tests (all assume standalone-repo `../` prefixes), and confirmed zero false-negative risk from scoping the diff.

### Files Deposited
- `bellows/knowledge/research/scope-check-monorepo-diagnosis-2026-04-28.md` — this file

### Files Created or Modified (Code)
- None (investigation only)

### Decisions Made
- Recommended fix shape: add `--relative -- .` to `_capture_git_diff`'s git command — universally applicable, no conditional logic needed
- Confirmed zero false-negative risk — no opt-out mechanism needed

### Flags for CEO
- The fix is a 2-line change to `_capture_git_diff` plus new test coverage. Low risk, high impact — closes BACKLOG #4 structurally.
- The existing `_parse_diff_stat` `..`-component filter (BACKLOG #2 point fix) is correct for standalone repos but structurally blind to the nested-repo case. The recommended fix addresses the root cause upstream.

### Flags for Next Step
- None — this diagnostic is complete. The Planner will write the executable fix plan after CEO review.
