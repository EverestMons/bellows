# Bellows — `file_change_audit` False-Negative Fix

**Date:** 2026-05-25 | **Tier:** Small | **Dispatch Mode:** bellows | **Test Scope:** full-suite | **Execution:** Step 1 (DEV) → Step 2 (QA) | **qa_steps:** 2 | **pause_for_verdict:** after_step_1

## Context

The 2026-05-25 SA diagnostic at `bellows/knowledge/research/file-change-audit-false-negative-2026-05-25.md` CONFIRMED root cause H1: `_capture_git_diff` uses `git diff --stat` which compares working tree to index and returns empty output after commits. Since Bellows-dispatched agents commit during their step as standard practice (per Rule 23 housekeeping), both `pre_diff` and `post_diff` capture clean working trees, yielding `files_changed = []` for every code-edit step.

The cascade: empty `files_changed` causes `_gate_scope_check` at `gates.py:601` to short-circuit (`if not files_changed: return`), effectively disabling scope-violation detection for every Bellows-dispatched step that involves code changes. This is not merely an informational display bug — it's a silent bypass of a blocking gate. 8+ reproductions documented; BACKLOG `bellows/knowledge/BACKLOG.md` line 35 (added 2026-05-21) tracks this.

This plan applies a minimal-surface refactor: keep the function names `_capture_git_diff` and `_parse_diff_stat` (preserving 41 existing test-suite mock-patch sites), but change their internal contracts. `_capture_git_diff` now returns the current HEAD SHA instead of working-tree diff text. `_parse_diff_stat` now takes two SHAs, runs `git diff --stat <pre_sha> -- .` internally (which covers both committed and uncommitted changes), and returns the file list.

**Sources:**
- SA diagnostic: `bellows/knowledge/research/file-change-audit-false-negative-2026-05-25.md` (verification blocks V1, V2, V3)
- Existing implementation: `bellows/bellows.py:678-731` (the two functions)
- Call sites: `bellows/bellows.py:451, 486, 542, 577` (4 sites in `run_plan` — argument types stay the same)
- Consumer gates: `bellows/gates.py:594-624` (`_gate_file_change_audit` + `_gate_scope_check` — NOT modified)
- Existing unit tests to be rewritten: `bellows/tests/test_bellows.py:538-640` (12 tests that validate the old diff-text contract)
- Mock-patch sites in tests (NOT modified — `return_value=""` semantics carry): 41 lines throughout `tests/test_bellows.py` patching `_capture_git_diff` with empty-string return
- Semantic tests preserved: `tests/test_bellows.py:2017` (`test_worktree_creation_precedes_diff_capture`) and `tests/test_bellows.py:2064` (`test_run_plan_routes_diff_through_worktree_path`) — both keep working under the rename-preserving refactor

**Test Scope: full-suite** — change touches a function consumed by every dispatch flow; cross-bucket regression risk on Mode A detection, scope_check, file_change_audit display, runner integration. Full-suite needed.

**Worktree-prefix note for the agent:** plan references use `bellows/` prefix for Planner readability. Inside the worktree, files are at the worktree root (strip the `bellows/` prefix when reading or editing).

**Pre-existing test failures expected (5 carry-overs, not regressions):** 4 × `test_decisions.py` worktree artifacts, 1 × `test_run_step_timeout`.

## How to Run This Plan

Bellows dispatches this plan automatically when deposited; no manual bootstrap required.

---
---

## STEP 1 — Bellows Developer

---

> **Pre-edit verification (per Rule 39):**
> Before performing any edits in this step, re-run each query below. If the output differs materially from the recorded output, STOP — do not proceed with edits. Instead, deposit a verification-mismatch report to `bellows/knowledge/flags/verification-mismatch-file-change-audit-fix-2026-05-25-step-1.md` documenting the claim, expected output, actual output, and timestamp. The Planner will triage the mismatch.
>
> 1. **Claim:** Current `_capture_git_diff` uses `git diff --stat` (uncommitted-only) and returns empty after commits.
>    **Query:**
>    ```bash
>    cd /Users/marklehn/Developer/GitHub/bellows && grep -A 3 "def _capture_git_diff" bellows.py | head -8
>    ```
>    **Expected output:** Function definition showing `["git", "--no-pager", "diff", "--stat", "--relative", "--", "."]` as the argv.
>
> 2. **Claim:** All 4 call sites pass `wt_path` to `_capture_git_diff`.
>    **Query:**
>    ```bash
>    cd /Users/marklehn/Developer/GitHub/bellows && grep -n "_capture_git_diff(wt_path)" bellows.py | wc -l | tr -d ' '
>    ```
>    **Expected output:** `4`
>
> 3. **Claim:** 41 test-file mock-patch sites use `patch("bellows._capture_git_diff", return_value="")` form.
>    **Query:**
>    ```bash
>    cd /Users/marklehn/Developer/GitHub/bellows && grep -c 'patch."bellows._capture_git_diff", return_value=""' tests/test_bellows.py
>    ```
>    **Expected output:** A number ≥ 38 and ≤ 41. (The exact count drifts with unrelated test churn; the point is that there are ~40 mock-patch sites whose `return_value=""` semantics MUST carry through the refactor unchanged.)
>
> You are the Bellows Developer. Skip specialist file and glossary reads — this is a small refactor with explicit edit instructions. **Task:** rewrite `_capture_git_diff` to return the HEAD SHA, and rewrite `_parse_diff_stat` to take SHAs and run the actual diff command internally. Preserve all function names and call-site signatures. This is a minimal-surface refactor.
>
> **Read first** `bellows.py:430-490` (run_plan first-step diff flow), `bellows.py:540-580` (loop-step diff flow), `bellows.py:678-731` (the two functions to rewrite), `gates.py:594-624` (consumer gates — DO NOT modify these), and `tests/test_bellows.py:538-640` (existing unit tests to rewrite).
>
> **Edit 1 — Rewrite `_capture_git_diff` in `bellows.py`.** Replace the entire function body (preserving signature `def _capture_git_diff(project_path: str) -> str:` — keep the parameter name `project_path` for backward compatibility even though callers pass `wt_path`) with:
>
> ```python
> def _capture_git_diff(project_path: str) -> str:
>     """Capture the current HEAD commit SHA, scoped to the directory at project_path.
>
>     Returns the short SHA as a string, or empty string on subprocess error or
>     missing git. The function name and signature are preserved from a prior
>     implementation; "diff" in the name is now anachronistic but the contract
>     change is necessary to fix the file_change_audit false-negative documented
>     in BACKLOG 2026-05-21 (diagnostic: knowledge/research/file-change-audit-false-negative-2026-05-25.md).
>     Prior implementation returned `git diff --stat` output, which was blind to
>     committed changes — agents commit during their step as standard practice,
>     leaving both pre- and post-step working trees clean.
>     """
>     try:
>         result = subprocess.run(
>             ["git", "--no-pager", "rev-parse", "HEAD"],
>             cwd=project_path, capture_output=True, text=True, timeout=10,
>         )
>         if result.returncode != 0:
>             return ""
>         return result.stdout.strip()
>     except Exception:
>         return ""
> ```
>
> **Edit 2 — Rewrite `_parse_diff_stat` in `bellows.py`.** Replace the entire function body (preserving signature `def _parse_diff_stat(post_diff: str, pre_diff: str, project_path: Optional[str] = None) -> list:` — keep parameter names `post_diff`/`pre_diff` even though they now hold SHAs) with:
>
> ```python
> def _parse_diff_stat(post_diff: str, pre_diff: str, project_path: Optional[str] = None) -> list:
>     """Return list of files changed between pre_diff (HEAD SHA before step) and the
>     current working-tree state, scoped to project_path.
>
>     Uses `git diff --stat <pre_diff> -- .` (run with cwd=project_path) which captures
>     BOTH committed and uncommitted changes since pre_diff. This covers the agent's
>     standard commit-during-step pattern as well as edge cases where the agent edits
>     but does not commit.
>
>     Parameters retain legacy names for backward compatibility:
>       - `post_diff`: currently unused; retained so call-site signatures don't change.
>       - `pre_diff`: HEAD SHA captured at step start by `_capture_git_diff`.
>       - `project_path`: directory to run git in AND the scope filter for `..` paths.
>
>     Files outside `project_path` (paths with `..` components after normalization) are
>     excluded — same filter as the prior implementation. Returns sorted list. Returns
>     [] on subprocess error, empty pre_diff, or no changes.
>
>     Closes BACKLOG 2026-05-21 file_change_audit false-negative (root cause: prior
>     implementation used `git diff --stat` working-tree-vs-index, blind to commits).
>     """
>     if not pre_diff:
>         return []
>     # cwd must be the same directory where _capture_git_diff captured pre_diff.
>     # Callers pass project_path consistently across both calls.
>     cwd = project_path if project_path else None
>     try:
>         result = subprocess.run(
>             ["git", "--no-pager", "diff", "--stat", "--relative", pre_diff, "--", "."],
>             cwd=cwd, capture_output=True, text=True, timeout=10,
>         )
>     except Exception:
>         return []
>     if result.returncode != 0:
>         return []
>
>     changed = []
>     for line in result.stdout.strip().splitlines():
>         line = line.strip()
>         if "|" not in line:
>             continue
>         filename, _stat = line.split("|", 1)
>         filename = filename.strip()
>         if not filename:
>             continue
>         changed.append(filename)
>
>     if project_path is not None:
>         changed = [
>             f for f in changed
>             if ".." not in os.path.normpath(f).split(os.sep)
>         ]
>
>     return sorted(changed)
> ```
>
> **Edit 3 — Call site cwd correctness check.** The new `_parse_diff_stat` runs git with `cwd=project_path`. The 4 call sites in `run_plan` look like:
> ```python
> pre_diff = _capture_git_diff(wt_path)
> # ... agent runs ...
> post_diff = _capture_git_diff(wt_path)
> files_changed = _parse_diff_stat(post_diff, pre_diff, project_path)
> ```
> Under the new contract, `_capture_git_diff(wt_path)` captures HEAD in the worktree, but `_parse_diff_stat(..., project_path=project_path)` runs git in `project_path` — a different directory. The pre_sha was captured in the worktree's git context (which IS the same repo as `project_path` since worktree shares the main repo's object database). `git rev-parse HEAD` in the worktree returns the worktree's HEAD; `git diff --stat <pre_sha>` in project_path will diff between that SHA and project_path's working tree — but the agent's changes are in the WORKTREE, not project_path's tree.
>
> **The fix is to change the 4 call sites** to pass `wt_path` (not `project_path`) as the third argument to `_parse_diff_stat`:
>
> ```python
> files_changed = _parse_diff_stat(post_diff, pre_diff, wt_path)
> ```
>
> at all 4 sites (lines 487, 578 region, etc.). The variable name `project_path` is fine when passed in — what matters is that `cwd` is the directory where the changes happened. Confirm by reading each of the 4 sites and updating consistently.
>
> **Edit 4 — Rewrite the 10 unit tests in `tests/test_bellows.py:538-636`.** Delete the following test functions:
> - `test_parse_diff_stat_preexisting_unchanged_returns_empty`
> - `test_parse_diff_stat_new_file_only_in_post`
> - `test_parse_diff_stat_preexisting_changed_stat_is_reported`
> - `test_parse_diff_stat_summary_line_ignored`
> - `test_parse_diff_stat_empty_inputs_return_empty`
> - `test_capture_git_diff_uses_relative_pathspec`
> - `test_parse_diff_stat_no_project_path_returns_all`
> - `test_parse_diff_stat_project_path_all_inside`
> - `test_parse_diff_stat_project_path_filters_dotdot`
> - `test_parse_diff_stat_project_path_filters_sibling_project`
>
> Also delete the section comment headers `# _parse_diff_stat — diff-of-diffs semantics` and `# _parse_diff_stat — project_path filter (BACKLOG #2 point fix)`.
>
> **Edit 5 — Add 6 new tests** to `tests/test_bellows.py` in the location where the deleted ones were. Use a single section comment header: `# _capture_git_diff / _parse_diff_stat — commit-aware semantics (BACKLOG 2026-05-21 fix)`.
>
> 1. `test_capture_git_diff_returns_head_sha` — Create a tempdir, `git init`, make a commit, call `bellows._capture_git_diff(tmpdir)`, assert the returned value is a non-empty 40-char-or-7-char hex string matching `git rev-parse HEAD` run independently.
>
> 2. `test_capture_git_diff_returns_empty_on_no_git` — Call `bellows._capture_git_diff("/tmp")` (assuming /tmp is not a git repo at test time; if it is, use `tempfile.TemporaryDirectory` without `git init`). Assert returns `""`.
>
> 3. `test_parse_diff_stat_empty_pre_sha_returns_empty` — Call `bellows._parse_diff_stat("", "", "/any/path")`. Assert returns `[]`. Same call with non-empty post_diff: `bellows._parse_diff_stat("post_sha", "", "/any/path")` also returns `[]` (empty pre_sha is the short-circuit).
>
> 4. `test_parse_diff_stat_detects_committed_changes` — Create a tempdir with `git init`, make an initial commit, capture `pre_sha = bellows._capture_git_diff(tmpdir)`. Edit a tracked file, `git add && git commit`. Call `bellows._parse_diff_stat("", pre_sha, tmpdir)`. Assert the edited file appears in the returned list. This is the regression test for the actual bug.
>
> 5. `test_parse_diff_stat_detects_uncommitted_changes` — Same setup as #4, but DO NOT commit the edit. Call `bellows._parse_diff_stat("", pre_sha, tmpdir)`. Assert the edited file appears in the returned list. (Edge case: covers agents that edit-without-commit.)
>
> 6. `test_parse_diff_stat_filters_dotdot_paths` — Mock `bellows.subprocess.run` to return a synthetic `git diff --stat` stdout with a mix of in-scope and `../` paths. Call `bellows._parse_diff_stat("post", "pre", "/some/project")`. Assert the `../` paths are filtered out. Mirrors the intent of the deleted `test_parse_diff_stat_project_path_filters_dotdot`.
>
> Use `tempfile.TemporaryDirectory` + `subprocess.run(["git", "init"], ...)` inside the temp dir, plus initial config (`git config user.email "test@test"; git config user.name "test"`) and a first commit to ensure HEAD exists. This pattern is already used elsewhere in the test suite — search for `git init` in `tests/` to find an existing template.
>
> **Note on existing patches (DO NOT modify):** The 41 `patch("bellows._capture_git_diff", return_value="")` lines throughout `tests/test_bellows.py` continue to work without modification — an empty-string return from `_capture_git_diff` is now interpreted as "empty SHA" by `_parse_diff_stat`, which short-circuits to `[]` (matching the prior empty-diff-text behavior). The 2 semantic tests at approximately lines 2017 and 2064 (`test_worktree_creation_precedes_diff_capture` and the wt_path routing test) also continue to work — they test ordering and call routing, both of which are preserved.
>
> **Verification before committing:** run from the worktree root: `python3 -m pytest tests/ -v` (full suite). Expected: 5 pre-existing carry-over failures (4 × test_decisions.py, 1 × test_run_step_timeout), zero new regressions, all 6 new tests PASSED. Capture full output to confirm count.
>
> **Deposit a dev log** at `knowledge/development/file-change-audit-fix-2026-05-25.md` with sections: (a) verbatim diff of all edits in `bellows.py` (use `git --no-pager diff bellows.py`), (b) verbatim diff of tests/test_bellows.py (use `git --no-pager diff tests/test_bellows.py`), (c) full-suite pytest output showing the 6 new tests passing and the 5 carry-over failures, (d) confirmation that scope_check is no longer silently no-opping (run `_capture_git_diff` + `_parse_diff_stat` on a real recent commit and show non-empty output), (e) any deviations from this plan and why, (f) Output Receipt with Status: Complete. **Commit** with message `fix(bellows): file_change_audit now detects committed changes — closes BACKLOG 2026-05-21` and a body listing the two files changed and noting that this closes the cascading silent bypass of _gate_scope_check. Standard prompt feedback protocol → `knowledge/research/agent-prompt-feedback.md`.
>
> **Deposits:**
> - `bellows/knowledge/development/file-change-audit-fix-2026-05-25.md`

---
---

## STEP 2 — Bellows QA

---

> Before starting, read `bellows/knowledge/development/file-change-audit-fix-2026-05-25.md` and check the Output Receipt status field. If status is not Complete, stop and report the blocker before proceeding. You are the Bellows QA agent. Skip specialist file and glossary reads — this is a mechanical refactor verification. **FIRST — Deliverable Verification.** Build a verification table with these checks, each row including line-number evidence and a verbatim quote excerpt from `bellows.py` or `tests/test_bellows.py`: (1) `_capture_git_diff` body rewritten to call `git rev-parse HEAD` (grep for `rev-parse` in `bellows.py` returns this function as one of the hits); (2) `_capture_git_diff` returns empty string on subprocess error (verify via reading the function — `return ""` on both `returncode != 0` and Exception paths); (3) `_parse_diff_stat` body rewritten to call `git diff --stat --relative <pre_diff> -- .` (grep `bellows.py` for `"--stat"` and confirm this is the only occurrence, plus the call site uses `pre_diff` as the SHA argument); (4) `_parse_diff_stat` short-circuits on empty `pre_diff` (verify `if not pre_diff: return []` is present early in the function); (5) `_parse_diff_stat` preserves the `..` path filter (verify the `if project_path is not None` block with `os.path.normpath` is present); (6) Exactly 4 call sites in `bellows.py` now pass `wt_path` (NOT `project_path`) as the third argument to `_parse_diff_stat` — grep `_parse_diff_stat(post_diff, pre_diff, wt_path)` returns 4 hits; (7) 10 old tests deleted — grep returns no hit for any of the 10 deleted test function names listed in Step 1 Edit 4; (8) 6 new test functions present (the names from Step 1 Edit 5); (9) The 41 existing `patch("bellows._capture_git_diff", return_value="")` mock-patch sites unchanged — `git diff HEAD~1 tests/test_bellows.py` should show NO modifications to lines 200-500 except the deletions of the old 10 tests. Mark each row ✅ or ❌ with evidence. If any ❌, stop and report.
>
> **Then — full pytest suite.** Run from the worktree root: `python3 -m pytest tests/ -v` and capture output to `evidence/pytest_full.txt`. Expected: 5 pre-existing carry-over failures (4 × `test_decisions.py`, 1 × `test_run_step_timeout`), zero new regressions, all 6 new tests PASSED. Grep the output for each new test name to confirm PASSED status. Grep for `test_run_step` and `test_decisions` to confirm the carry-overs are the same 5 (not more).
>
> **Then — live smoke verification.** In the worktree, run:
> ```bash
> python3 -c "
> import sys, subprocess
> sys.path.insert(0, '.')
> from bellows import _capture_git_diff, _parse_diff_stat
> # Get current HEAD SHA via the rewritten function
> head_sha = _capture_git_diff('.')
> print(f'_capture_git_diff returned: {head_sha[:12]}...')
> assert head_sha, 'EXPECTED non-empty SHA; got empty string'
> # Get HEAD~1 SHA independently
> result = subprocess.run(['git', '--no-pager', 'rev-parse', 'HEAD~1'], capture_output=True, text=True)
> head_minus_1 = result.stdout.strip()
> print(f'HEAD~1: {head_minus_1[:12]}...')
> # Run the new _parse_diff_stat with HEAD~1 as pre_diff
> changed = _parse_diff_stat('', head_minus_1, '.')
> print(f'Files changed in last commit: {changed}')
> assert changed, 'EXPECTED non-empty file list; got []'
> print('PASS: scope_check is no longer silently no-opping on committed changes')
> "
> ```
> Capture stdout to `evidence/smoke_test.txt`. Confirm output ends with `PASS:`. This is the contract test that proves the bug is fixed — committed changes are now detected.
>
> **Then — structural compliance check.** Run `git --no-pager show --stat HEAD` and confirm the DEV commit touched exactly 3 files: `bellows.py`, `tests/test_bellows.py`, `knowledge/development/file-change-audit-fix-2026-05-25.md`. Capture to `evidence/dev_commit.txt`. Run `git --no-pager diff HEAD~1 bellows.py` and confirm the diff is bounded to: (a) `_capture_git_diff` function body (signature unchanged), (b) `_parse_diff_stat` function body (signature unchanged), (c) 4 call sites in `run_plan` changing the third arg of `_parse_diff_stat` from `project_path` to `wt_path`. No other functions modified. Capture to `evidence/diff_bellows.txt`. Run `git --no-pager diff HEAD~1 tests/test_bellows.py` and capture to `evidence/diff_tests.txt`. Confirm via word count that the test file diff is bounded to roughly the lines 538-640 region plus the new test additions — no changes elsewhere.
>
> **Then — Rule 20 self-check.** Run the canonical Rule 20 self-check from `RULE_20_SELF_CHECK_BLOCK.md` at the governance root. Use these values: `plan_slug`: `executable-file-change-audit-fix-2026-05-25`; `qa_report_path`: `<absolute-path-to-knowledge/qa/executable-file-change-audit-fix-2026-05-25.md>`; `evidence_dir`: `<absolute-path-to-knowledge/qa/evidence/executable-file-change-audit-fix-2026-05-25/>`; `required_evidence_files`: `["pytest_full.txt", "smoke_test.txt", "dev_commit.txt", "diff_bellows.txt", "diff_tests.txt"]`. Include the literal stdout output of the block in the QA report under an `**Output:**` heading. If FAILED, halt and report to CEO.
>
> **Then — QA report deposit.** Write `knowledge/qa/executable-file-change-audit-fix-2026-05-25.md` with the verification table, full-suite pytest summary, smoke test result, structural compliance results, Rule 20 self-check stdout, and Output Receipt with Status: Complete. **DEPOSITS RULE:** declare ONLY the QA report file and the evidence directory in the **Deposits** block below. Do NOT list PROJECT_STATUS.md as a deposit even though you will update it.
>
> **Final:** Update `PROJECT_STATUS.md` — prepend a new Completed entry under today's date (2026-05-25) summarizing: `_capture_git_diff` and `_parse_diff_stat` rewritten to use HEAD SHA + commit-range diff; new mechanism captures BOTH committed and uncommitted changes since step start (single `git diff --stat <pre_sha> -- .` command); function names and signatures preserved (41 existing mock-patch sites in test suite continue working unchanged); 10 obsolete unit tests deleted, 6 new tests added; closes BACKLOG 2026-05-21 `file_change_audit` false-negative AND the cascading silent bypass of `_gate_scope_check`. Include the **REMINDER: restart Bellows daemon** line. Use `Filesystem:edit_file` with verbatim anchor on the existing top entry. Also update `bellows/knowledge/BACKLOG.md` — move the 2026-05-21 `file_change_audit` entry from Open to Closed with a one-line closure note citing this plan. **STOP.** Do NOT move this plan to Done/. Standard prompt feedback protocol → `knowledge/research/agent-prompt-feedback.md`.
>
> **Deposits:**
> - `bellows/knowledge/qa/executable-file-change-audit-fix-2026-05-25.md`
> - `bellows/knowledge/qa/evidence/executable-file-change-audit-fix-2026-05-25/`
