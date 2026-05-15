# Bellows — scope_check Monorepo Fix
**Date:** 2026-04-28 | **Tier:** Small | **Test Scope:** targeted | **Execution:** Step 1 (Bellows Developer) → Step 2 (Bellows QA)
**Priority:** 5

## Context

Closes BACKLOG #4 (`scope_check false-positive over too-wide git range`). The diagnostic at `bellows/knowledge/research/scope-check-monorepo-diagnosis-2026-04-28.md` confirmed that bellows is the only watched project without its own `.git` — it lives inside the governance-root repo at `/Users/marklehn/Desktop/GitHub/`. When `_capture_git_diff()` runs `git diff --stat` from `cwd=/Users/marklehn/Desktop/GitHub/bellows`, git walks up to the governance-root `.git` and reports the entire monorepo's diff. The existing `..`-component filter in `_parse_diff_stat` is structurally blind to monorepo-relative paths (no `..` components).

Diagnostic Q3 demonstrated that the universal fix is adding `--relative -- .` to the git diff command. For standalone repos (cwd = repo root), `-- .` is equivalent to no pathspec and `--relative` is a no-op. For nested repos, `-- .` correctly scopes to subtree and `--relative` rewrites paths to cwd-relative form. No conditional logic needed.

Diagnostic Q5 confirmed all existing `_parse_diff_stat` tests use synthetic `../`-prefixed inputs and would survive the proposed fix unchanged. Diagnostic Q6 confirmed zero false-negative risk — no plan in history has depended on scope_check seeing uncommitted cross-project files.

**Expected behavior during this plan's own close:** Per BACKLOG #14 ("plan fixing bug X tripped bug X during its own close"), the QA step's `_capture_git_diff` will run against the OLD code because Bellows daemon hasn't restarted. The QA step will likely trip scope_check on `LESSONS.md` or other governance-root files — same false positive the canary today demonstrated. This is expected, not a real failure — the Planner overrides the QA verdict manually. Live validation comes from a separate post-restart smoke plan after CEO restarts Bellows.

Test Scope: targeted — single-function change to `_capture_git_diff`. Targeted run of `pytest tests/test_bellows.py` is sufficient. No cross-bucket regression risk.

## How to Run This Plan

Bellows watcher claims this plan automatically. Step 1 modifies `bellows.py` and adds one test, then commits. Step 2 (QA) verifies the deliverables, runs the targeted test suite, deposits evidence, runs Rule 20 self-check, updates PROJECT_STATUS, commits. After Step 2's verdict, Planner performs Rule 22 verification and authorizes terminal close.

---
---

## STEP 1 — Bellows Developer

---

> **FIRST — claim this plan:** `import shutil; shutil.move("bellows/knowledge/decisions/executable-scope-check-monorepo-fix-2026-04-28.md", "bellows/knowledge/decisions/in-progress-executable-scope-check-monorepo-fix-2026-04-28.md")`. **Skip glossary read — this is a single-function code change, no domain content.** Read your specialist file at `bellows/agents/BELLOWS_DEVELOPER.md` first. All commands run from `/Users/marklehn/Desktop/GitHub/`. **Task A — modify `_capture_git_diff` in `bellows/bellows.py`.** Use `Filesystem:read_text_file` with `view_range` or equivalent to read the function definition (search for `def _capture_git_diff` — currently around line 398). Copy the verbatim function body (8 lines: `def` line, docstring, `try:`, `result = subprocess.run(`, the argv list line, the `cwd=` arguments line, the close paren, `return result.stdout`, `except Exception:`, `return ""`) — use that EXACT text as the `old_string` argument to `Desktop Commander:edit_block`. The `new_string` is the same function with two changes: (1) the docstring becomes `"""Capture git diff --stat output for file change tracking, scoped to the project subtree.\n\n    Uses `--relative -- .` to handle the nested-repo case where project_path is a\n    subdirectory of a larger repo (e.g., bellows/ inside the governance-root repo).\n    Without scoping, git walks up to the parent repo's .git and reports the entire\n    monorepo's diff. Universally applicable: for standalone repos (cwd = repo root)\n    `-- .` is equivalent to no pathspec and `--relative` is a no-op. Closes BACKLOG #4.\n    """`; (2) the argv list changes from `["git", "--no-pager", "diff", "--stat"]` to `["git", "--no-pager", "diff", "--stat", "--relative", "--", "."]`. Do not change the function signature, return type, or `try`/`except` structure. Do NOT modify `_parse_diff_stat` — its `..`-component filter is correct for standalone repos and harmless (inert) under the new scoping per the diagnostic's Q4 finding. **Task B — add a new unit test.** Use `Filesystem:read_text_file` to find the line `def test_parse_diff_stat_empty_inputs_return_empty():` in `bellows/tests/test_bellows.py` and the closing `assert bellows._parse_diff_stat("", "") == []` line that follows it. Use `Desktop Commander:edit_block` to anchor on those two lines plus the blank line that follows, replacing them with the same content followed by a new blank line and the new test below. The new test verbatim:
> ```python
> def test_capture_git_diff_uses_relative_pathspec():
>     """BACKLOG #4 fix: _capture_git_diff scopes diff to project subtree via --relative -- ."""
>     mock_result = MagicMock()
>     mock_result.stdout = ""
>     with patch("bellows.subprocess.run", return_value=mock_result) as mock_run:
>         bellows._capture_git_diff("/some/project")
>     assert mock_run.called
>     argv = mock_run.call_args[0][0]
>     assert "--relative" in argv, f"Expected --relative in argv: {argv!r}"
>     assert "--" in argv, f"Expected -- separator in argv: {argv!r}"
>     dash_dash_idx = argv.index("--")
>     assert dash_dash_idx + 1 < len(argv) and argv[dash_dash_idx + 1] == ".", \
>         f"Expected '.' immediately after '--' in argv: {argv!r}"
> ```
> **Task C — run the targeted test suite to confirm no regressions.** `cd /Users/marklehn/Desktop/GitHub/bellows && python3 -m pytest tests/test_bellows.py -v --tb=short 2>&1 > knowledge/development/scope-check-monorepo-fix-step-1-pytest.txt`. Verify exit code is 0 (all tests pass) AND that the new test name `test_capture_git_diff_uses_relative_pathspec` appears in the output as PASSED. If any test fails, STOP and report — do NOT commit. **Task D — deposit dev log** at `bellows/knowledge/development/scope-check-monorepo-fix-dev-log-2026-04-28.md` using `Filesystem:write_file` with: (1) the verbatim old `_capture_git_diff` body that was replaced; (2) the verbatim new body; (3) the verbatim new test code; (4) the count of tests passed (from the pytest output) and confirmation the new test appears in the passing list; (5) any anomalies. **Task E — commit:** `cd /Users/marklehn/Desktop/GitHub/bellows && git add bellows.py tests/test_bellows.py knowledge/development/scope-check-monorepo-fix-dev-log-2026-04-28.md knowledge/development/scope-check-monorepo-fix-step-1-pytest.txt && git commit -m "fix(scope_check): scope git diff to project subtree via --relative -- ."`. **Standard prompt feedback protocol** → `bellows/knowledge/research/agent-prompt-feedback.md`.
>
> **Deposits:**
> - `bellows/knowledge/development/scope-check-monorepo-fix-dev-log-2026-04-28.md`
> - `bellows/knowledge/development/scope-check-monorepo-fix-step-1-pytest.txt`

---
---

## STEP 2 — Bellows QA

---

> **Before starting, read `bellows/knowledge/development/scope-check-monorepo-fix-dev-log-2026-04-28.md` and check the Output Receipt status field. If status is not Complete, stop and report the issue to the CEO before proceeding.** **Skip glossary read — this is mechanical verification.** Read your specialist file at `bellows/agents/BELLOWS_QA.md` first. All commands run from `/Users/marklehn/Desktop/GitHub/`. **FIRST — Deliverable Verification (Rule 17).** Create the evidence directory: `mkdir -p bellows/knowledge/qa/evidence/executable-scope-check-monorepo-fix-2026-04-28/`. (a) Verify the `_capture_git_diff` argv contains the new flags: `grep -A 2 'git", "--no-pager", "diff", "--stat"' bellows/bellows.py > bellows/knowledge/qa/evidence/executable-scope-check-monorepo-fix-2026-04-28/grep_capture_git_diff.txt 2>&1`. The output should contain `--relative` and `--`. If it doesn't, the deliverable is missing. (b) Verify the new test exists: `grep -n 'def test_capture_git_diff_uses_relative_pathspec' bellows/tests/test_bellows.py > bellows/knowledge/qa/evidence/executable-scope-check-monorepo-fix-2026-04-28/grep_new_test.txt 2>&1`. The output should show one match. (c) Verify Step 1's commit landed: `git --no-pager log --oneline -3 -- bellows/bellows.py bellows/tests/test_bellows.py > bellows/knowledge/qa/evidence/executable-scope-check-monorepo-fix-2026-04-28/git_log.txt`. The output should show the `fix(scope_check):` commit. Build a verification table in the QA report with columns `| Deliverable | Expected | Status | Evidence |`, citing the evidence file paths in the Evidence column. **Run the targeted test suite:** `cd /Users/marklehn/Desktop/GitHub/bellows && python3 -m pytest tests/test_bellows.py -v --tb=short 2>&1 > knowledge/qa/evidence/executable-scope-check-monorepo-fix-2026-04-28/pytest_targeted.txt`. Verify (i) exit code is 0; (ii) the new test `test_capture_git_diff_uses_relative_pathspec` appears in the PASSED list; (iii) total passed count matches the dev log's count. **Deposit QA report** at `bellows/knowledge/qa/scope-check-monorepo-fix-qa-2026-04-28.md` containing the verification table, a one-paragraph summary of the targeted test results, and the literal output of the Rule 20 self-check. **Run the Rule 20 self-check** at the end of the QA report. Use `plan_slug = "executable-scope-check-monorepo-fix-2026-04-28"`, `qa_report_path = "bellows/knowledge/qa/scope-check-monorepo-fix-qa-2026-04-28.md"`, `evidence_dir = "bellows/knowledge/qa/evidence/executable-scope-check-monorepo-fix-2026-04-28/"`, and `required_evidence_files = ["grep_capture_git_diff.txt", "grep_new_test.txt", "git_log.txt", "pytest_targeted.txt"]`. Include the literal stdout in the QA report. If `FAILED`, STOP and report. If `PASSED`, proceed. **Update PROJECT_STATUS.md** at `bellows/PROJECT_STATUS.md` — find a recent milestone entry as anchor (use `Filesystem:read_text_file` to identify), then use `Desktop Commander:edit_block` to insert a new bullet directly after the most recent milestone heading or below the most recent existing bullet under "Completed Milestones" (or whichever section is the milestone log). The new bullet text: `- 2026-04-28: BACKLOG #4 closed — scope_check false-positive over too-wide git range. Fix: scoped \`_capture_git_diff\` to project subtree via \`--relative -- .\`. Universally applicable across nested and standalone repos. Reference: \`executable-scope-check-monorepo-fix-2026-04-28\`. REMINDER: restart Bellows to load the fix.` **Append prompt feedback** to `bellows/knowledge/research/agent-prompt-feedback.md` per standard protocol. **Final commit:** `cd /Users/marklehn/Desktop/GitHub/bellows && git add knowledge/qa/scope-check-monorepo-fix-qa-2026-04-28.md knowledge/qa/evidence/executable-scope-check-monorepo-fix-2026-04-28/ PROJECT_STATUS.md knowledge/research/agent-prompt-feedback.md && git commit -m "qa: scope_check monorepo fix — verified, BACKLOG #4 closeable pending Bellows restart"`. **STOP.** Do NOT move this plan to Done/. Per the disable-auto-close model, the Planner performs the terminal move after Rule 22 verification passes. **Note:** Per BACKLOG #14, Bellows's gate evaluation of THIS step will run against the OLD `_capture_git_diff` code (daemon hasn't restarted) and may trip scope_check on `LESSONS.md` or other governance-root files. This is expected, not a real failure.
>
> **Deposits:**
> - `bellows/knowledge/qa/scope-check-monorepo-fix-qa-2026-04-28.md`
> - `bellows/knowledge/qa/evidence/executable-scope-check-monorepo-fix-2026-04-28/grep_capture_git_diff.txt`
> - `bellows/knowledge/qa/evidence/executable-scope-check-monorepo-fix-2026-04-28/grep_new_test.txt`
> - `bellows/knowledge/qa/evidence/executable-scope-check-monorepo-fix-2026-04-28/git_log.txt`
> - `bellows/knowledge/qa/evidence/executable-scope-check-monorepo-fix-2026-04-28/pytest_targeted.txt`
