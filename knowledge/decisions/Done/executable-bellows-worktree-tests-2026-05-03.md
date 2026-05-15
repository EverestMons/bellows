# Bellows — Per-Plan Git Worktree Tests (Plan 2 of 2)
**Date:** 2026-05-03 | **Tier:** Medium | **Test Scope:** targeted | **Execution:** Step 1 (BELLOWS DEVELOPER) → Step 2 (BELLOWS DEVELOPER QA)

## How to Run This Plan

**This plan is staged at `/Users/marklehn/Desktop/GitHub/bellows/_staging-executable-bellows-worktree-tests-2026-05-03.md` — NOT in `bellows/knowledge/decisions/`.** Bellows will not auto-claim it. Move it into `knowledge/decisions/` after Bellows is restarted with the Plan 1 worktree code active. The CEO performs the move via `Filesystem:move_file` once restart is verified.

**Move command (CEO, post-restart):**
```
Filesystem:move_file
  source: /Users/marklehn/Desktop/GitHub/bellows/_staging-executable-bellows-worktree-tests-2026-05-03.md
  destination: /Users/marklehn/Desktop/GitHub/bellows/knowledge/decisions/executable-bellows-worktree-tests-2026-05-03.md
```

Step 1 (DEV) adds tests to `tests/test_bellows.py` and creates `tests/test_worktree.py`. Step 2 (QA) verifies test files exist with expected count and runs full test suite (the new tests exercise live worktree behavior, so this is the actual behavioral verification). The Planner performs Rule 22 verification and the terminal Done/ move after Step 2 passes.

**Bootstrap (manual fallback only — Bellows auto-dispatches once moved):**
```
Read the plan at bellows/knowledge/decisions/executable-bellows-worktree-tests-2026-05-03.md. Execute Step 1 ONLY. After completing Step 1, STOP and wait for my confirmation. Do NOT proceed to Step 2 or move the plan to Done.
```

**Pre-dispatch verification (CEO checklist before moving this plan into watched dir):**
1. Plan 1 (`executable-bellows-worktree-impl-2026-05-03`) is in `Done/`
2. Bellows daemon has been restarted (PID changed since Plan 1 commit landed)
3. Bellows startup banner showed the new source SHA (post-restart code is active)
4. No other bellows-project plans are in `in-progress-*` or `verdict-pending-*` state (quiet-window dispatch)

**Source diagnostics for design context:**
- `bellows/knowledge/research/worktree-implementation-surface-2026-05-03.md` — surface map (Phase A7 has the test surface enumeration this plan implements)
- `bellows/knowledge/research/worktree-candidate-designs-2026-05-03.md` — D7 (test surface) and D8 (smoke test design)
- Plan 1's dev log at `bellows/knowledge/development/worktree-impl-dev-log-2026-05-03.md` — actual implementation details (function signatures, line locations) to reference when writing test assertions

**Caveat on test assertion accuracy:** The test assertions written in this plan reference the SA's design spec (function names, retry shape, cherry-pick behavior). Plan 1 may have made small implementation choices that differ from spec — for example, exact exception messages, helper function placement, or precise grep targets. Before writing tests, the DEV reads Plan 1's dev log to identify any spec deviations, and adjusts test assertions to match the actual implemented code. Any deviations from this plan's spec are flagged in the dev log under "Spec Deviations from Plan 1."

---
---

## STEP 1 — BELLOWS DEVELOPER

---

> **STOP REMINDER (TOP):** This is the test-writing step. After completing this step, STOP and wait for CEO confirmation. Do NOT execute Step 2. Do NOT move the plan to Done.
>
> **FIRST — before doing anything else, claim this plan:** `import shutil; shutil.move("bellows/knowledge/decisions/executable-bellows-worktree-tests-2026-05-03.md", "bellows/knowledge/decisions/in-progress-executable-bellows-worktree-tests-2026-05-03.md")`.
>
> You are the Bellows Developer. Read your specialist file at `bellows/agents/BELLOWS_DEVELOPER.md` first. Skip glossary read.
>
> **Read Plan 1's dev log first:** `bellows/knowledge/development/worktree-impl-dev-log-2026-05-03.md`. This contains the actual function signatures, line locations, and implementation choices made in Plan 1. Use it as the authoritative reference for test target shapes — NOT the SA design spec from `worktree-candidate-designs-2026-05-03.md`. The SA spec was the design intent; the dev log is the implementation reality. If they differ, follow the dev log.
>
> **Task: add 6 unit tests to `tests/test_bellows.py` and create `tests/test_worktree.py` with 7 integration tests covering the worktree mechanism. Run the full test suite. Document spec deviations.**
>
> **Phase 1 — Add 6 unit tests to `tests/test_bellows.py`.** These tests assert that `run_plan` calls into the worktree mechanism at the right points, using mocked `_create_worktree` and `_teardown_worktree` to isolate from real git operations:
>
> 1. **`test_run_plan_creates_worktree_before_pre_diff`** — Mock `_create_worktree` and `_capture_git_diff` and `runner.run_step`. Patch `run_plan` to dispatch a single-step plan. Assert that `_create_worktree(project_path, plan_slug)` is called BEFORE the first `_capture_git_diff` call. Use `Mock.call_args_list` ordering to verify sequence.
>
> 2. **`test_run_plan_passes_wt_path_to_capture_and_runner`** — Mock `_create_worktree` to return a sentinel string `"WT_PATH_SENTINEL"`. Mock `_capture_git_diff` and `runner.run_step`. Dispatch a single-step plan. Assert that `_capture_git_diff` is called with `"WT_PATH_SENTINEL"` (NOT `project_path`). Assert that `runner.run_step` is called with `"WT_PATH_SENTINEL"` as its second positional arg (per surface map A2, the `project_path` parameter at index 1).
>
> 3. **`test_run_plan_tears_down_worktree_after_final_gate`** — Mock `_create_worktree`, `_teardown_worktree`, `_capture_git_diff`, `runner.run_step`, and `gates.check`. Dispatch a single-step plan that auto-closes (no pause). Assert that `_teardown_worktree(project_path, wt_path, slug)` is called AFTER `gates.check` returns and BEFORE the move-to-Done logic. Use `Mock.call_args_list` ordering.
>
> 4. **`test_run_plan_strict_pause_on_creation_failure`** — Mock `_create_worktree` to raise `WorktreeCreationError("test failure")`. Mock `verdict.post_verdict_request` to capture call args. Dispatch a plan. Assert that `post_verdict_request` is called with `pause_reason_code="gate_failure"`. Assert that the plan file is renamed to `verdict-pending-` (not `in-progress-` and not in `Done/`). Assert that `runner.run_step` is NEVER called (the plan halts before agent dispatch).
>
> 5. **`test_run_plan_pauses_on_cherry_pick_conflict`** — Mock `_create_worktree` to return a path. Mock `_teardown_worktree` to raise `WorktreeTeardownError("cherry-pick conflict")`. Mock `verdict.post_verdict_request`. Dispatch an auto-close plan. Assert that `post_verdict_request` is called with `pause_reason_code="gate_failure"` and the gate failure list includes "cherry-pick" or similar. Assert plan is renamed to `verdict-pending-` (not in Done/).
>
> 6. **`test_bellows_init_runs_worktree_prune`** — Mock `subprocess.run`. Instantiate `Bellows(...)` with at least one watched project. Assert that `subprocess.run` is called with argv starting with `["git", "--no-pager", "worktree", "prune"]` and `cwd` equal to the project path. The call should happen during `__init__`, before any plan dispatch.
>
> Test file location: `bellows/tests/test_bellows.py`. Append after the existing tests. Follow the existing import patterns and `unittest.mock.patch` conventions (per surface map A7, the file already uses `from unittest.mock import patch` style). Use `Desktop Commander:edit_block` for surgical insertion at end-of-file or after a specific anchor.
>
> **Phase 2 — Create `tests/test_worktree.py` with 7 integration tests.** These tests exercise REAL git worktree operations against a temporary git repo (no mocking of git itself). Each test creates an isolated temp directory, initializes a git repo with `git init` + initial commit, then exercises `_create_worktree` and `_teardown_worktree` directly:
>
> 1. **`test_create_worktree_returns_valid_path_with_tracked_files`** — Init temp repo with 3 files committed. Call `_create_worktree(temp_repo, "test-slug")`. Assert returned path exists. Assert path contains all 3 tracked files. Cleanup: `git worktree remove --force` + remove temp dir.
>
> 2. **`test_worktree_isolation_git_diff`** — Init temp repo with 1 committed file. Create worktree. Modify the file in the MAIN checkout (not the worktree). Run `git diff --stat` inside the worktree. Assert the dirty file does NOT appear (worktree's view is clean). This is the core regression guard for the BACKLOG #1 bug.
>
> 3. **`test_teardown_removes_worktree_directory`** — Init temp repo. Create worktree. Call `_teardown_worktree`. Assert worktree directory no longer exists on disk. Assert `git worktree list` (in main repo) does NOT include the removed worktree.
>
> 4. **`test_teardown_cherry_picks_commits`** — Init temp repo with 1 committed file. Create worktree. Inside worktree, modify the file and commit (using `subprocess.run` with `cwd=worktree_path`). Call `_teardown_worktree`. Assert the commit now appears on the main checkout's HEAD (`git log` from main shows the commit message).
>
> 5. **`test_teardown_copies_uncommitted_files`** — Init temp repo. Create worktree. Inside worktree, write a NEW file (not committed). Call `_teardown_worktree`. Assert the new file appears in the main checkout at the expected relative path with the same contents.
>
> 6. **`test_teardown_aborts_on_cherry_pick_conflict`** — Init temp repo with file A.txt containing "version 1". Create worktree. In worktree, modify A.txt to "version 2" and commit. In MAIN checkout, modify A.txt to "version 3" and commit (this creates the conflict scenario). Call `_teardown_worktree` and expect it to raise `WorktreeTeardownError`. Assert: (a) main checkout's working tree is NOT in mid-cherry-pick state (`git status` shows clean state, no `CHERRY_PICK_HEAD` file), (b) the worktree directory STILL EXISTS (not removed — left for manual resolution per locked design).
>
> 7. **`test_create_worktree_retries_once_on_failure`** — This test mocks `subprocess.run` to fail on the first call (return non-zero) and succeed on the second. Patch `time.sleep` to avoid the actual 2-second wait. Call `_create_worktree(temp_repo, "test-slug")`. Assert `subprocess.run` was called twice (first failure, then retry). Assert `time.sleep(2)` was called once between the two attempts. Assert the function returned the expected path (success on retry).
>
> Test file structure: standard pytest structure with `import pytest`, `import os`, `import subprocess`, `import shutil`, `import tempfile`, plus the imports from `bellows.bellows` (or wherever the helpers live). **Before writing the import statement, read the dev log at `bellows/knowledge/development/worktree-impl-dev-log-2026-05-03.md` to identify the actual exported names.** The spec assumes `_create_worktree`, `_teardown_worktree`, `WorktreeCreationError`, `WorktreeTeardownError` — but Plan 1's DEV may have chosen different names. Use whatever names appear in the dev log's "Helper Function Signatures" section. If the names differ from the spec, document the deviation in this plan's dev log under "Spec Deviations from Plan 1" but proceed with the actual implementation names. Use `pytest.fixture` for the temp git repo setup/teardown to share across tests. Mark integration tests with `@pytest.mark.integration` if the existing test suite uses such markers (check via `grep -r "pytest.mark" bellows/tests/`).
>
> Important consideration: these tests run REAL `git` commands. They MUST clean up after themselves (remove worktree, remove temp dir) even on test failure. Use `pytest.fixture` with `yield` + cleanup in the finally clause, or use `tempfile.TemporaryDirectory()` context manager combined with explicit `git worktree remove --force` before context exit.
>
> Use canonical Python file write pattern to create the test file. Define the file content as a triple-quoted string variable, then `with open("/Users/marklehn/Desktop/GitHub/bellows/tests/test_worktree.py", "w") as f: f.write(content)`. Do NOT use heredoc syntax. Do NOT use `python3 -c`.
>
> The DEV writes the actual test bodies — the imports + fixtures + 7 test functions with complete, runnable bodies that exercise the real behavior.
>
> **Phase 3 — Run targeted test regression.** From bellows directory: `cd /Users/marklehn/Desktop/GitHub/bellows && python -m pytest tests/ -v 2>&1 | tee /tmp/pytest-after-tests.txt`. Expected: all existing tests pass + all 6 new test_bellows.py tests pass + all 7 new test_worktree.py tests pass. Total: previous baseline + 13 new tests passing. The single pre-existing `test_run_step_timeout` failure remains (unrelated).
>
> If any of the 13 new tests fail, document the failure shape in the dev log and stop. Do NOT mark Status: Complete if any test is failing — that would invalidate the verification.
>
> **Phase 4 — Document spec deviations.** Compare the actual Plan 1 implementation (per dev log + grep) against the SA design spec at `worktree-candidate-designs-2026-05-03.md` Section D2 (Candidate 1). Note any deviations: exception class names, helper function placement, exact retry-pattern shape, etc. List in dev log under "Spec Deviations from SA Design (Plan 1 implementation)" with neutral framing — these may be entirely correct implementation choices that the SA spec under-specified.
>
> **Phase 5 — Dev log deposit.** Write to `bellows/knowledge/development/worktree-tests-dev-log-2026-05-03.md` using canonical Python file write pattern. Sections: Summary, Files Modified, New Tests Added (with names + brief description), Test Results (counts before/after), Spec Deviations from Plan 1, Output Receipt.
>
> **Phase 6 — Two commits.** Tests first, then dev log:
>
> ```
> cd /Users/marklehn/Desktop/GitHub/bellows && git --no-pager add tests/test_bellows.py tests/test_worktree.py && git --no-pager commit -m "test(bellows): unit + integration tests for per-plan worktree"
> cd /Users/marklehn/Desktop/GitHub/bellows && git --no-pager add knowledge/development/worktree-tests-dev-log-2026-05-03.md && git --no-pager commit -m "docs: dev log for worktree tests"
> ```
>
> **Constraints:**
> - Do NOT modify production code in `bellows.py`. If a test failure reveals a Plan 1 bug, document it in the dev log under "Plan 1 Bugs Discovered" — do NOT fix it here. Plan 3 (a follow-up) handles fixes.
> - Do NOT use heredoc syntax for file writes. Use canonical `with open() as f: f.write(content)` pattern.
> - Do NOT skip the integration tests in test_worktree.py. They exercise the actual git operations — that's the whole point of Plan 2 over Plan 1.
> - Do NOT add tests beyond the 13 specified — scope creep here delays the canary diagnostic.
>
> Standard prompt feedback protocol → `bellows/knowledge/research/agent-prompt-feedback.md`.
>
> **Deposits:**
> - `bellows/tests/test_bellows.py`
> - `bellows/tests/test_worktree.py`
> - `bellows/knowledge/development/worktree-tests-dev-log-2026-05-03.md`
>
> **STOP REMINDER (BOTTOM):** Step 1 is COMPLETE when (a) 6 new tests added to test_bellows.py and pass, (b) test_worktree.py created with 7 new tests and all pass, (c) full test suite passes (previous baseline + 13 new), (d) two commits landed, (e) dev log deposited with spec-deviation notes. Do NOT execute Step 2. Do NOT move the plan to Done.

---
---

## STEP 2 — BELLOWS DEVELOPER (QA)

---

> **Before starting, read `bellows/knowledge/development/worktree-tests-dev-log-2026-05-03.md` and check the Output Receipt status. If status is not Complete, stop and report the issue to the CEO before proceeding.**
>
> **STOP REMINDER (TOP):** This is the QA verification step. Do NOT modify production code or test files. Do NOT move the plan to Done — the Planner performs the terminal move after Rule 22 verification passes.
>
> You are the Bellows Developer (acting as QA). Read your specialist file at `bellows/agents/BELLOWS_DEVELOPER.md` first. Skip glossary read.
>
> **Critical context:** The Bellows daemon IS running with worktree code active (Plan 1 was deposited, restarted, and Plan 2 was dispatched after restart). This means the integration tests in `test_worktree.py` exercise the live worktree code path. The QA's job here is to verify the test files exist, contain the expected tests, and that the full suite (including the new tests) passes.
>
> **Task: verify Step 1's deliverables, run the full test suite, run Rule 20 self-check, write QA report.**
>
> **Phase 1 — Create evidence directory.** `mkdir -p bellows/knowledge/qa/evidence/executable-bellows-worktree-tests-2026-05-03`.
>
> **Phase 2 — Deliverable verification (Rule 17).** Read Step 1's dev log to identify exact test names. For EACH listed deliverable, verify:
>
> 1. **`tests/test_worktree.py` exists.** Run: `ls -la /Users/marklehn/Desktop/GitHub/bellows/tests/test_worktree.py | tee bellows/knowledge/qa/evidence/executable-bellows-worktree-tests-2026-05-03/ls_test_worktree.txt`. Expected: file exists with non-zero size.
>
> 2. **6 new tests in test_bellows.py.** Run: `grep -n "^def test_run_plan_creates_worktree\|^def test_run_plan_passes_wt_path\|^def test_run_plan_tears_down_worktree\|^def test_run_plan_strict_pause_on_creation_failure\|^def test_run_plan_pauses_on_cherry_pick_conflict\|^def test_bellows_init_runs_worktree_prune" /Users/marklehn/Desktop/GitHub/bellows/tests/test_bellows.py | tee bellows/knowledge/qa/evidence/executable-bellows-worktree-tests-2026-05-03/grep_new_tests_bellows.txt`. Expected: exactly 6 matches (one per test name listed in Plan 2 spec, or the actual names if dev log notes deviations).
>
> 3. **7 tests in test_worktree.py.** Run: `grep -c "^def test_" /Users/marklehn/Desktop/GitHub/bellows/tests/test_worktree.py | tee bellows/knowledge/qa/evidence/executable-bellows-worktree-tests-2026-05-03/test_count_worktree.txt`. Expected: 7.
>
> 4. **Full test suite passes.** From bellows directory: `cd /Users/marklehn/Desktop/GitHub/bellows && python -m pytest tests/ -v 2>&1 | tee bellows/knowledge/qa/evidence/executable-bellows-worktree-tests-2026-05-03/pytest_full.txt`. Expected: previous baseline + 13 new tests passing. The pre-existing `test_run_step_timeout` failure is acceptable. Compute pass/fail counts: `grep -E "^=+.*passed|^=+.*failed" bellows/knowledge/qa/evidence/executable-bellows-worktree-tests-2026-05-03/pytest_full.txt | tee bellows/knowledge/qa/evidence/executable-bellows-worktree-tests-2026-05-03/pytest_summary.txt`.
>
> 5. **All 13 new tests pass specifically.** Run: `cd /Users/marklehn/Desktop/GitHub/bellows && python -m pytest tests/test_worktree.py tests/test_bellows.py::test_run_plan_creates_worktree_before_pre_diff tests/test_bellows.py::test_run_plan_passes_wt_path_to_capture_and_runner tests/test_bellows.py::test_run_plan_tears_down_worktree_after_final_gate tests/test_bellows.py::test_run_plan_strict_pause_on_creation_failure tests/test_bellows.py::test_run_plan_pauses_on_cherry_pick_conflict tests/test_bellows.py::test_bellows_init_runs_worktree_prune -v 2>&1 | tee bellows/knowledge/qa/evidence/executable-bellows-worktree-tests-2026-05-03/pytest_new_tests.txt`. Expected: 13 passed, 0 failed. Adjust the test names if the dev log noted deviations from spec names.
>
> 6. **Two commits landed.** Run: `cd /Users/marklehn/Desktop/GitHub/bellows && git --no-pager log --oneline -5 | tee bellows/knowledge/qa/evidence/executable-bellows-worktree-tests-2026-05-03/git_log.txt`. Expected: top two commits match Step 1 Phase 6 messages.
>
> Produce verification table: `| Deliverable | Expected | Status (✅/❌) | Evidence |`. Cite evidence file paths.
>
> **Phase 3 — Write QA report.** Deposit to `bellows/knowledge/qa/worktree-tests-qa-2026-05-03.md` using canonical Python file write pattern. Include verification table, test summary, Rule 20 self-check stdout, Output Receipt.
>
> **Phase 4 — Update PROJECT_STATUS.md.** Add a completed milestone entry. Use `Desktop Commander:edit_block` with verbatim anchor on the Plan 1 entry (which the Planner added after Plan 1's Rule 22 verification passed). Insert ABOVE that entry. Entry text:
>
> `- 2026-05-03: Plan 2 of BACKLOG #1 (parallel-plan scope_check collision) shipped — worktree test suite. 6 new unit tests in test_bellows.py exercise run_plan's worktree call points (creation before pre-diff, wt_path passed to capture and runner, teardown after final gate, strict-pause on creation failure, pause on cherry-pick conflict, startup prune in __init__). 7 new integration tests in test_worktree.py exercise REAL git operations (worktree creates with tracked files, isolation from main checkout dirty files, teardown removes directory, cherry-pick on teardown, copy-back uncommitted files, abort-on-conflict leaves worktree alive, retry-once-on-creation-failure). Full suite passes — previous baseline + 13 new tests, with 1 pre-existing unrelated failure. BACKLOG #1 implementation + tests now both shipped. NEXT: post-restart canary diagnostic to verify behavioral isolation in live dispatch (separate plan to author).`
>
> **Phase 5 — Mandatory Rule 20 self-check.** Required evidence files: `ls_test_worktree.txt`, `grep_new_tests_bellows.txt`, `test_count_worktree.txt`, `pytest_full.txt`, `pytest_summary.txt`, `pytest_new_tests.txt`, `git_log.txt`. Plan slug: `executable-bellows-worktree-tests-2026-05-03`. QA report path: `bellows/knowledge/qa/worktree-tests-qa-2026-05-03.md`.
>
> ```python
> # Rule 20 — Mandatory QA Self-Check
> import os, sys
> plan_slug = "executable-bellows-worktree-tests-2026-05-03"
> qa_report_path = "bellows/knowledge/qa/worktree-tests-qa-2026-05-03.md"
> evidence_dir = f"bellows/knowledge/qa/evidence/{plan_slug}/"
> required_evidence_files = [
>     "ls_test_worktree.txt",
>     "grep_new_tests_bellows.txt",
>     "test_count_worktree.txt",
>     "pytest_full.txt",
>     "pytest_summary.txt",
>     "pytest_new_tests.txt",
>     "git_log.txt",
> ]
> hedging_keywords = ["pending", "inferred", "extrapolated", "estimated", "approximate", "skipped", "assumed", "close enough", "should pass", "would pass", "not run"]
> POSITIVE_STATUS_TOKENS = ["✅", "OK", "PASS", "done", "complete", "verified"]
>
> def is_positive_row(line):
>     if "|" not in line:
>         return False
>     cells = [c.strip() for c in line.split("|")]
>     for cell in cells:
>         for token in POSITIVE_STATUS_TOKENS:
>             if token == "✅":
>                 if "✅" in cell:
>                     return True
>             else:
>                 if cell.lower() == token.lower():
>                     return True
>     return False
>
> failures = []
> if not os.path.isdir(evidence_dir):
>     failures.append(f"CRITICAL: evidence folder missing: {evidence_dir}")
> else:
>     for fname in required_evidence_files:
>         fpath = os.path.join(evidence_dir, fname)
>         if not os.path.isfile(fpath):
>             failures.append(f"CRITICAL: evidence file missing: {fpath}")
>         elif os.path.getsize(fpath) == 0:
>             failures.append(f"CRITICAL: evidence file empty: {fpath}")
> if os.path.isfile(qa_report_path):
>     with open(qa_report_path, "r") as f:
>         report = f.read()
>     for line in report.splitlines():
>         if is_positive_row(line):
>             lower = line.lower()
>             for kw in hedging_keywords:
>                 if kw in lower:
>                     failures.append(f"CRITICAL: hedging keyword '{kw}' in positive-status row: {line.strip()[:120]}")
>                     break
> else:
>     failures.append(f"CRITICAL: QA report not found at {qa_report_path}")
> print("=" * 60)
> print("Rule 20 — QA Self-Check Results")
> print("=" * 60)
> if failures:
>     print(f"FAILED — SELF-CHECK FAILED — {len(failures)} issue(s):")
>     for f in failures:
>         print(f"  - {f}")
>     print("\nPlan CANNOT close. Fix issues and re-run QA.")
>     sys.exit(1)
> else:
>     print("PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.")
>     print(f"Evidence folder: {evidence_dir}")
>     print(f"Files verified: {len(required_evidence_files)}")
> ```
>
> Include the literal stdout in the QA report. If self-check FAILS, agent STOPS — does NOT update PROJECT_STATUS.md, does NOT move plan to Done, reports failure to CEO and waits.
>
> **Phase 6 — Final commit.** After QA report and PROJECT_STATUS update are deposited:
>
> ```
> cd /Users/marklehn/Desktop/GitHub/bellows && git --no-pager add knowledge/qa/worktree-tests-qa-2026-05-03.md knowledge/qa/evidence/executable-bellows-worktree-tests-2026-05-03/ PROJECT_STATUS.md && git --no-pager commit -m "qa: verify worktree tests (Plan 2 of 2)"
> ```
>
> Standard prompt feedback protocol → `bellows/knowledge/research/agent-prompt-feedback.md`. Feedback append + commit are absolute last operations.
>
> **Deposits:**
> - `bellows/knowledge/qa/worktree-tests-qa-2026-05-03.md`
> - `bellows/knowledge/qa/evidence/executable-bellows-worktree-tests-2026-05-03/` (7 evidence files per Rule 20 self-check)
> - `bellows/PROJECT_STATUS.md`
>
> **STOP.** Do NOT move this plan to Done/. Per the disable-auto-close model, the Planner performs the terminal move after Rule 22 verification passes.
