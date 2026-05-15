# Bellows — Monorepo Worktree Fix (Option A: detect-and-skip)
**Date:** 2026-05-04 | **Tier:** Small | **Test Scope:** full-suite | **Execution:** Step 1 (DEV) → Step 2 (QA)

## How to Run This Plan

Paste the bootstrap prompt into Claude Code. The agent reads the full plan file and executes Step 1 ONLY. After completing Step 1, the agent STOPS and waits for CEO confirmation ("ok") before proceeding to Step 2.

**Bootstrap prompt:**
```
Read the plan at bellows/knowledge/decisions/executable-monorepo-worktree-fix-2026-05-04.md. Execute Step 1 ONLY. After completing Step 1, STOP and wait for my confirmation. Do NOT proceed to Step 2 or move the plan to Done.
```

**Test Scope: full-suite** — modifies load-bearing dispatch infrastructure (worktree creation/teardown). Recent regression here (2026-05-03 string-vs-dict type-contract bug) raises cross-bucket regression risk above baseline. Both targeted and full suite are required.

**Depends on:** `executable-backlog-capture-monorepo-worktree-2026-05-04.md` (BACKLOG entry must be in place before this plan ships).

---
---

## STEP 1 — BELLOWS DEVELOPER

---

> **FIRST — before doing anything else, claim this plan:** `import shutil; shutil.move("bellows/knowledge/decisions/executable-monorepo-worktree-fix-2026-05-04.md", "bellows/knowledge/decisions/in-progress-executable-monorepo-worktree-fix-2026-05-04.md")`. You are the Bellows Developer. Read your specialist file at `bellows/agents/BELLOWS_DEVELOPER.md`. Skip glossary read — this is a code-tracing and fix task, no domain interpretation required. Read the May-3 diagnostic at `bellows/knowledge/research/worktree-teardown-bug-diagnosis-2026-05-03.md` — Q2 confirms the monorepo trap and Q4 enumerates the fix-shape options. CEO has selected Option (a) — detect missing `.git` at `project_path` and skip worktree creation, fall back to in-place execution. **Goal:** modify `bellows.py` so that when `project_path` has no `.git` directory or file (i.e., bellows-self today), Bellows skips worktree creation entirely and executes the agent in `cwd=project_path` directly. Teardown for these plans is a no-op. **Reads:** read `bellows.py` to locate `_create_worktree` (cited around line 529 in the May-3 diagnostic, but verify the line — three days of edits may have shifted it) and `_teardown_worktree`. Also locate the call site that invokes `_create_worktree` (the dispatch path that decides whether the agent runs in a worktree or in-place) so you can wire in the skip path correctly. **Implementation:** at the top of `_create_worktree` (or at the call site, your choice based on what reads cleanly — flag the choice in the dev log), add a check `os.path.exists(os.path.join(project_path, ".git"))`. If False, log a clear message indicating worktree is skipped due to no project-local .git (e.g., `⚠ {project_name} has no project-local .git — running in-place without worktree isolation`), set the effective working path to `project_path` itself, and ensure the dispatcher uses `project_path` as agent cwd. The teardown path must symmetrically detect this case and become a no-op (no `git worktree remove`, no cherry-pick) — choose the cleanest signal: either return a sentinel from `_create_worktree` (e.g., `(wt_path, used_worktree: bool)`) and pass it to teardown, or have `_teardown_worktree` re-check `os.path.exists(os.path.join(project_path, ".git"))` itself. Prefer the explicit-signal approach — re-checking is fragile if the .git appears mid-execution (unlikely but possible if someone runs `git init` in bellows/ between steps). Whatever shape you pick, document it in the dev log with one sentence explaining why. **Constraints:** do NOT remove worktree creation for projects that DO have their own .git — this fix is bellows-only by detection, not by hardcoded project name. Do NOT remove the type-fix from 2026-05-03 (commit 0f2059f) — it remains the safety net for cherry-pick failures in other projects. Preserve all existing behavior for the 7 projects with their own .git (per Q3 of the May-3 diagnostic: invoice-pulse, BrewBuddy, study, ai-career-digest, freight-kb, forge, anvil). **Tests:** add at minimum (1) a unit test that `_create_worktree` returns the in-place path when project_path has no .git, (2) a unit test that `_teardown_worktree` is a no-op for the in-place case (does not invoke `git worktree remove`, does not attempt cherry-pick), (3) a unit test that the existing worktree path is unchanged for a project with its own .git (regression guard — use a mock or a temp git repo). Use existing test patterns in `tests/test_verdict.py` and the worktree tests added in BACKLOG #1's 2026-05-03 plan as references for fixture style. Run targeted tests: `pytest tests/test_bellows.py tests/test_verdict.py -v` (and any other test file that exercises worktree creation — discover via `grep -rl "worktree\|_create_worktree\|_teardown_worktree" tests/`). **Commit:** one commit, message `fix: skip worktree creation when project_path has no .git (bellows-self monorepo trap)`. Deposit dev log at `bellows/knowledge/development/monorepo-worktree-fix-dev-log-2026-05-04.md` with: (a) which line you chose for the detection (top of _create_worktree vs call site), (b) which signal-shape you chose for teardown coordination (sentinel return vs re-check), (c) one-sentence rationale per choice, (d) Output Receipt with status, files changed, decisions made, flags. After the dev log and before commit, run the standard prompt feedback protocol → `bellows/knowledge/research/agent-prompt-feedback.md`.
>
> **Deposits:**
> - `bellows/knowledge/development/monorepo-worktree-fix-dev-log-2026-05-04.md`
>
> **STOP. Do NOT proceed to Step 2. Do NOT move the plan to Done. Wait for CEO confirmation before continuing.**

---
---

## STEP 2 — BELLOWS QA

---

> Before starting, read `bellows/knowledge/development/monorepo-worktree-fix-dev-log-2026-05-04.md` and check the Output Receipt status. If status is not Complete, stop and report the issue to the CEO before proceeding. You are the Bellows QA agent. Read your specialist file at `bellows/agents/BELLOWS_QA.md`. Skip glossary read. **FIRST — Deliverable Verification.** Read the DEV step Output Receipt's "Files Created or Modified (Code)" list. For EACH file: verify on disk, grep for the key change. Specifically: (1) verify `bellows.py` contains the new detection check — `grep -n "os.path.exists.*\.git" bellows.py` should show at least one new match in or near `_create_worktree`; (2) verify the in-place fallback path exists — search for the log message string the DEV chose (read the dev log first to know what to grep for); (3) verify new unit tests are present in the test file the DEV modified — `git --no-pager show HEAD --stat` should show test files among changed files; (4) verify the type-fix from 2026-05-03 is still in place — `grep -n '"gate": "worktree_teardown"' bellows.py` should still match (the 3 sites identified by the May-3 diagnostic at lines 340, 405, 433 — verify all 3 are intact post-fix). Pipe each grep output to evidence files: `grep_detection_check.txt`, `grep_log_message.txt`, `grep_type_fix_intact.txt` under `bellows/knowledge/qa/evidence/executable-monorepo-worktree-fix-2026-05-04/`. Pipe the `git --no-pager show HEAD --stat` output to `git_show_commit.txt`. Produce a verification table: `| Deliverable | Expected | Status (✅/❌) | Evidence |` with one row per item above. **SECOND — Test Regression.** Run targeted tests first: `pytest tests/test_bellows.py tests/test_verdict.py -v 2>&1 | tee bellows/knowledge/qa/evidence/executable-monorepo-worktree-fix-2026-05-04/pytest_targeted.txt`. Confirm new tests pass and no targeted regressions. Then run the full suite: `pytest tests/ -v 2>&1 | tee bellows/knowledge/qa/evidence/executable-monorepo-worktree-fix-2026-05-04/pytest_full.txt`. Compare failure count against the most recent known baseline — per memory, baseline as of 2026-05-03 was approximately 190 tests passing with 1 pre-existing `test_run_step_timeout` failure. Document any deviation in the QA report. **THIRD — Cross-project regression smoke.** Confirm the fix does NOT affect projects with their own .git by writing a small unit test fixture that creates a temp directory with a `.git` subdir and verifies `_create_worktree` proceeds with worktree creation (mock the `git worktree add` subprocess call). If this is already covered by an existing test added in Step 1, cite that test in the verification table. Pipe the test output to `pytest_cross_project.txt` under the evidence dir. Deposit QA report at `bellows/knowledge/qa/monorepo-worktree-fix-qa-2026-05-04.md` with: verification table, targeted test summary, full suite summary, cross-project regression confirmation, Output Receipt. Run the Rule 20 self-check Python block at the end and include literal stdout in the QA report. If self-check FAILED, STOP — do NOT update PROJECT_STATUS.md, do NOT touch the plan file, report to CEO and wait. If PASSED: **update PROJECT_STATUS.md** — add a completed milestone entry summarizing this plan: monorepo worktree fix (Option A: detect-and-skip), files changed, tests added, baseline test count delta. Then run the standard prompt feedback protocol → `bellows/knowledge/research/agent-prompt-feedback.md`. Then commit with message `qa: monorepo worktree fix verification passed`. Do NOT move the plan to Done — Planner performs the move after Rule 22 verification.
>
> **Deposits:**
> - `bellows/knowledge/qa/monorepo-worktree-fix-qa-2026-05-04.md`
> - `bellows/knowledge/qa/evidence/executable-monorepo-worktree-fix-2026-05-04/grep_detection_check.txt`
> - `bellows/knowledge/qa/evidence/executable-monorepo-worktree-fix-2026-05-04/grep_log_message.txt`
> - `bellows/knowledge/qa/evidence/executable-monorepo-worktree-fix-2026-05-04/grep_type_fix_intact.txt`
> - `bellows/knowledge/qa/evidence/executable-monorepo-worktree-fix-2026-05-04/git_show_commit.txt`
> - `bellows/knowledge/qa/evidence/executable-monorepo-worktree-fix-2026-05-04/pytest_targeted.txt`
> - `bellows/knowledge/qa/evidence/executable-monorepo-worktree-fix-2026-05-04/pytest_full.txt`
> - `bellows/knowledge/qa/evidence/executable-monorepo-worktree-fix-2026-05-04/pytest_cross_project.txt`
>
> **Rule 20 self-check (run at end of QA step, include literal stdout in QA report):**
>
> ```python
> # Rule 20 — Mandatory QA Self-Check
> import os, sys
> plan_slug = "executable-monorepo-worktree-fix-2026-05-04"
> qa_report_path = "bellows/knowledge/qa/monorepo-worktree-fix-qa-2026-05-04.md"
> evidence_dir = f"bellows/knowledge/qa/evidence/{plan_slug}/"
> required_evidence_files = [
>     "grep_detection_check.txt",
>     "grep_log_message.txt",
>     "grep_type_fix_intact.txt",
>     "git_show_commit.txt",
>     "pytest_targeted.txt",
>     "pytest_full.txt",
>     "pytest_cross_project.txt",
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
