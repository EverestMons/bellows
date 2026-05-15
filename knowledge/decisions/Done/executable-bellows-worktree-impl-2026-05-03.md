# Bellows — Per-Plan Git Worktree Implementation (Plan 1 of 2)
**Date:** 2026-05-03 | **Tier:** Medium | **Test Scope:** targeted | **Execution:** Step 1 (BELLOWS DEVELOPER) → Step 2 (BELLOWS DEVELOPER QA)

## How to Run This Plan

Bellows will auto-claim. Step 1 (DEV) implements the worktree mechanism in `bellows.py` plus `.gitignore`. Step 2 (QA) verifies the code-level deliverables exist with the expected shape and runs targeted test regression. The Planner performs Rule 22 verification and the terminal Done/ move after Step 2 passes.

**This is Plan 1 of 2.** Plan 2 (`executable-bellows-worktree-tests-2026-05-03`) is staged at `/Users/marklehn/Desktop/GitHub/bellows/_staging-executable-bellows-worktree-tests-2026-05-03.md` and will be moved to `knowledge/decisions/` after Bellows is restarted with the new worktree code active. The behavioral verification (worktree isolation actually works) lives in Plan 2 — Plan 1's QA cannot test live worktree behavior because the daemon is on pre-fix code through Plan 1's entire QA window.

**Bootstrap (manual fallback only — Bellows auto-dispatches):**
```
Read the plan at bellows/knowledge/decisions/executable-bellows-worktree-impl-2026-05-03.md. Execute Step 1 ONLY. After completing Step 1, STOP and wait for my confirmation. Do NOT proceed to Step 2 or move the plan to Done.
```

**Quiet-window dispatch:** Before depositing this plan, the CEO should verify no other bellows-project plans are in `in-progress-*` or `verdict-pending-*` state. The implementation modifies `bellows.py` at 8+ sites; concurrent sibling plans would expose this plan's QA to the BACKLOG #1 collision bug it is fixing.

**Locked design decisions** (per CEO 2026-05-03):
1. Worktree location: in-tree `<project>/.bellows-worktrees/<slug>/`
2. Always-worktree (every plan dispatch creates one)
3. Detached HEAD with cherry-pick on cleanup
4. Copy-back uncommitted files
5. Halt-on-cherry-pick-conflict (abort cherry-pick, leave worktree alive, post gate_failure verdict)
6. Persist-on-shutdown (worktrees survive Bellows restart; startup `git worktree prune` cleans stale registrations)
7. Strict-pause-on-creation-failure WITH retry-once: first `git worktree add` failure → sleep 2s → retry → if second attempt fails, post gate_failure verdict
8. CEO confirmation between Plan 1 and Plan 2 (this plan and the tests plan)
9. Canary authored now / dispatched post-restart (separate diagnostic, NOT part of this plan's QA)

**Source diagnostics for design context** (read if implementation questions arise):
- `bellows/knowledge/research/worktree-implementation-surface-2026-05-03.md` — line-numbered code surface
- `bellows/knowledge/research/worktree-candidate-designs-2026-05-03.md` — D-section design specs
- `bellows/knowledge/research/worktree-cost-coverage-recommendation-2026-05-03.md` — cost analysis and rollout risk

---
---

## STEP 1 — BELLOWS DEVELOPER

---

> **STOP REMINDER (TOP):** This is the implementation step. Do NOT execute Step 2 (QA verification) work even though its prompt exists below. After completing this step, STOP and wait for CEO confirmation. Do NOT move the plan to Done — the Planner performs the terminal move after Rule 22 verification passes.
>
> **FIRST — before doing anything else, claim this plan:** `import shutil; shutil.move("bellows/knowledge/decisions/executable-bellows-worktree-impl-2026-05-03.md", "bellows/knowledge/decisions/in-progress-executable-bellows-worktree-impl-2026-05-03.md")`.
>
> You are the Bellows Developer. Read your specialist file at `bellows/agents/BELLOWS_DEVELOPER.md` first. Skip glossary read — this is implementation. **Read the implementation surface map at `bellows/knowledge/research/worktree-implementation-surface-2026-05-03.md`** for line numbers and call-site context. The current line numbers in that document MAY HAVE DRIFTED from today's commits. Always grep for the actual current location before editing. Verify each cited line range against current `bellows.py` content via `grep -n` before applying any edit.
>
> **Task: implement per-plan git worktree isolation in `bellows.py` per locked design decisions, plus `.gitignore` update.**
>
> **Phase 1 — Update `bellows/.gitignore`.** Use `Desktop Commander:edit_block` to add `.bellows-worktrees/` after the existing `.bellows-cache/` line. The `.gitignore` must end with newlines preserved. Anchor on the verbatim existing `.bellows-cache/` line.
>
> **Phase 2 — Add `_create_worktree(project_path: str, slug: str) -> str` helper to `bellows.py`.** Place definition near the existing `_capture_git_diff` and `_parse_diff_stat` helpers (per surface map A1 these are at approximately lines 404-456 — verify current location). The helper:
> - Computes `wt_path = os.path.join(project_path, ".bellows-worktrees", slug)`
> - Computes `parent_dir = os.path.join(project_path, ".bellows-worktrees")` and ensures it exists via `os.makedirs(parent_dir, exist_ok=True)`
> - Runs `subprocess.run(["git", "--no-pager", "worktree", "add", wt_path, "HEAD", "--detach"], cwd=project_path, capture_output=True, text=True, timeout=60)`
> - On non-zero return code: print warning `f"Bellows: ⚠ worktree creation failed for {slug}, retrying in 2s: {result.stderr.strip()}"` to stdout, sleep 2 seconds, retry the same `subprocess.run` call once
> - On second non-zero return code: raise `WorktreeCreationError(f"worktree creation failed after retry for {slug}: {result.stderr.strip()}")` where `WorktreeCreationError` is a custom exception class defined at module top-level (subclass of `Exception`)
> - On success: return `wt_path`
> - Wrap the entire body in try/except for `subprocess.TimeoutExpired` and `OSError` — these convert to `WorktreeCreationError` with a descriptive message
>
> Define `WorktreeCreationError` and a sibling `WorktreeTeardownError` at module top-level near the other constants (per surface map A4 these are around lines 17-18). These are signaling exceptions — `run_plan` catches them and converts to verdict requests.
>
> **Phase 3 — Add `_teardown_worktree(project_path: str, wt_path: str, slug: str) -> None` helper to `bellows.py`.** The helper performs four sub-operations in order:
>
> (a) **Detect main branch** for cherry-pick base: `subprocess.run(["git", "--no-pager", "symbolic-ref", "--short", "refs/remotes/origin/HEAD"], cwd=project_path, ...)`. Strip the leading `origin/` from stdout. If this fails (e.g., no `origin/HEAD` reference), fall back to `"main"` and print a warning. Store as `main_branch`.
>
> (b) **Collect commits made in worktree.** Run `subprocess.run(["git", "--no-pager", "log", "--format=%H", "HEAD", "--not", main_branch], cwd=wt_path, ...)`. Each line of stdout is a commit SHA, oldest-first reversed (since `git log` is newest-first, `splitlines()[::-1]` gives chronological order for cherry-pick).
>
> (c) **Cherry-pick each commit onto main checkout.** For each SHA in chronological order: run `subprocess.run(["git", "--no-pager", "cherry-pick", sha], cwd=project_path, ...)`. On non-zero return code from any cherry-pick: run `subprocess.run(["git", "--no-pager", "cherry-pick", "--abort"], cwd=project_path, ...)` to reset the main checkout state, then raise `WorktreeTeardownError(f"cherry-pick conflict on {sha} for slug {slug}: {result.stderr.strip()}")`. Do NOT run `git worktree remove` — leave the worktree alive for manual resolution. The exception propagates to `run_plan` which converts to a gate_failure verdict.
>
> (d) **Copy uncommitted dirty files back.** Run `subprocess.run(["git", "--no-pager", "status", "--porcelain"], cwd=wt_path, ...)`. For each line, parse the status code (first 2 chars) and filename (chars 3+). For status codes that indicate file presence (`??`, ` M`, `M `, `A `, `MM`, etc. — anything that's not `D ` deletion-only), copy `os.path.join(wt_path, filename)` → `os.path.join(project_path, filename)` using `shutil.copy2` (preserves metadata). Create parent directories with `os.makedirs(parent, exist_ok=True)` if needed. Skip files where the source doesn't exist on disk.
>
> (e) **Remove the worktree.** Run `subprocess.run(["git", "--no-pager", "worktree", "remove", wt_path, "--force"], cwd=project_path, ...)`. The `--force` flag is necessary because uncommitted files in the worktree (which we just copied back) would otherwise block removal. On non-zero return code: print warning but do NOT raise — the worktree directory may persist, but the next `git worktree prune` (at startup) will clean it. Document this in the warning message.
>
> **Phase 4 — Add `git worktree prune` startup hook to `Bellows.__init__`.** Per surface map A5, `Bellows.__init__` is around line 540-555. Locate the `__init__` method via grep. Inside `__init__`, after existing initialization (after `_active_lock` is created but before `start()` is called), iterate over `self.watched_projects` and run `subprocess.run(["git", "--no-pager", "worktree", "prune"], cwd=project_path, capture_output=True, text=True, timeout=10)` for each. Catch any exception and print a warning (don't fail startup). This cleans stale worktree registrations from prior crashes.
>
> **Phase 5 — Wire worktree creation into `run_plan`.** Per surface map A3, the natural insertion point is between plan claim (current line ~240) and pre-diff capture (current line ~265). Verify these line numbers are still accurate via `grep -n "_write_shadow" bellows/bellows.py` and `grep -n "pre_diff = _capture_git_diff" bellows/bellows.py` before editing.
>
> Insert: `try: wt_path = _create_worktree(project_path, plan_slug); except WorktreeCreationError as e: <post strict-pause verdict request, rename plan to verdict-pending-, return>`. The strict-pause verdict request uses `verdict.post_verdict_request` with: pause_reason `"Worktree creation failed"`, pause_reason_code `"gate_failure"`, plan_path, project, step=1, total_steps (from extracted metadata), deposit=`"none"`, gate_passed=False, and a gate failure list `["worktree_creation_failed: " + str(e)]`. After posting, rename the plan from `in-progress-*` to `verdict-pending-*` (mirror the existing pause-rename logic at surface-map line ~304/363) and return from `run_plan`. The plan will sit in verdict-pending awaiting CEO judgment, consistent with all other gate_failure paths.
>
> **Phase 6 — Replace `project_path` with `wt_path` at six call sites in `run_plan`:**
> - Surface-map A1 call site 1 (line ~265): `pre_diff = _capture_git_diff(project_path)` → `pre_diff = _capture_git_diff(wt_path)`
> - Surface-map A2 line ~267-269: `runner.run_step(bootstrap_prompt, project_path, model, ...)` → `runner.run_step(bootstrap_prompt, wt_path, model, ...)`
> - Surface-map A1 call site 2 (line ~281): `post_diff = _capture_git_diff(project_path)` → `post_diff = _capture_git_diff(wt_path)`
> - Surface-map A1 call site 3 (line ~321, inside loop): `pre_diff = _capture_git_diff(project_path)` → `pre_diff = _capture_git_diff(wt_path)`
> - Surface-map A2 line ~323-328 (inside loop): `runner.run_step(default_next_prompt, project_path, model, ...)` → `runner.run_step(default_next_prompt, wt_path, model, ...)`
> - Surface-map A1 call site 4 (line ~339, inside loop): `post_diff = _capture_git_diff(project_path)` → `post_diff = _capture_git_diff(wt_path)`
>
> Important: do NOT replace `project_path` in `_parse_diff_stat(post_diff, pre_diff, project_path)` calls. The `project_path` argument to `_parse_diff_stat` is the project root for relative-path filtering — it must remain the project root, not the worktree path. Verify this by reading the existing `_parse_diff_stat` signature (surface map A1, line ~423).
>
> Also do NOT replace `project_path` in `gates.check(parsed, plan_text, current_step, project_path, files_changed=files_changed)` calls (surface map A1 line ~283/341). The gates module uses `project_path` for deposit-existence resolution against the real project tree (deposits land at the real path post-teardown).
>
> Also do NOT replace `project_path` in `record_run(...)` calls — DB writes use absolute paths and shouldn't be reframed to worktree-relative paths.
>
> **Phase 7 — Wire worktree teardown into `run_plan`.** The teardown happens at three exit points (per surface map A3):
>
> (a) **Auto-close path** (around line ~378-397): Just before the move-to-Done logic, call `try: _teardown_worktree(project_path, wt_path, plan_slug); except WorktreeTeardownError as e: <post gate_failure verdict, rename to verdict-pending-, return>`. The gate_failure on cherry-pick conflict matches Phase 5's pattern — the plan halts at verdict-pending for CEO review with the worktree alive at `.bellows-worktrees/<slug>/` for manual resolution.
>
> (b) **Mid-plan pause path** (around line ~291-315 for loop pause and ~347-373 for final-step pause): Just before the verdict-request post and rename to verdict-pending-, call `_teardown_worktree(project_path, wt_path, plan_slug)`. Wrap in try/except for `WorktreeTeardownError`. On teardown success, the verdict-request post and rename proceed normally. On teardown error, the verdict-request post must include the teardown error in its pause reason — but the plan still pauses (it would have paused anyway), so the rename to verdict-pending- still happens.
>
> Important consideration for mid-plan pauses: when a multi-step plan pauses between steps, the worktree must be torn down OR preserved across the pause. **Decision: tear down on pause.** Each step's worktree is created fresh in `run_plan` via `_create_worktree` at the top, so a resumed plan (verdict continue dispatching step N+1) creates a NEW worktree from the current main HEAD (which now includes the cherry-picked commits from step N). This is the simplest model — each `run_plan` invocation creates and tears down exactly one worktree.
>
> **Verify this assumption holds:** Read the resume dispatch path in `_consume_verdicts` and `handle_new_plan(path, resume_step=N)` — confirm that resume dispatch calls `run_plan` afresh (which would invoke `_create_worktree` at the top). If resume dispatch keeps an existing worktree alive, this design needs revision.
>
> (c) **Verdict-request-from-agent path** (around line ~291-315): Same pattern as (b) — tear down before the rename to verdict-pending-.
>
> **Phase 8 — Targeted test regression.** From the bellows directory: `cd /Users/marklehn/Desktop/GitHub/bellows && python -m pytest tests/ -v 2>&1 | tee /tmp/pytest-after-worktree-impl.txt`. Expected baseline (per PROJECT_STATUS): all tests pass except 1 pre-existing failure (`test_run_step_timeout`, unrelated). If the failure count is 1, proceed. If new failures appear, document each in the dev log under "Test Regressions" and stop — do NOT push through; the Planner will assess.
>
> **Phase 9 — Dev log deposit.** Write to `bellows/knowledge/development/worktree-impl-dev-log-2026-05-03.md` using canonical Python file write pattern (NOT heredoc, NOT `python3 -c`). The dev log must include sections: Summary, Files Modified (with line ranges), Helper Function Signatures (exact names + line numbers — Plan 2 reads these), Retry Behavior, Cherry-Pick Conflict Handling, Test Results (before/after counts), Commit SHAs, and an Output Receipt.
>
> Use the canonical pattern: `content = """..."""` defined as a triple-quoted string variable, then `with open("/Users/marklehn/Desktop/GitHub/bellows/knowledge/development/worktree-impl-dev-log-2026-05-03.md", "w") as f: f.write(content)`. Do NOT use heredoc. Do NOT use `python3 -c`.
>
> **Phase 10 — Two commits.** Code first, then dev log:
>
> ```
> cd /Users/marklehn/Desktop/GitHub/bellows && git --no-pager add bellows.py .gitignore && git --no-pager commit -m "fix(bellows): per-plan git worktree for parallel-collision isolation"
> cd /Users/marklehn/Desktop/GitHub/bellows && git --no-pager add knowledge/development/worktree-impl-dev-log-2026-05-03.md && git --no-pager commit -m "docs: dev log for worktree implementation"
> ```
>
> **Constraints:**
> - Do NOT add new tests — Plan 2 covers tests. Adding tests here exceeds scope.
> - Do NOT modify `runner.py`, `gates.py`, `verdict.py`, `parser.py`, or any other module. The implementation is confined to `bellows.py` + `.gitignore`.
> - Do NOT use heredoc syntax (`<<`) for file writes. Use canonical `with open() as f: f.write(content)` Python pattern.
> - Do NOT use `python3 -c "..."` with embedded code — same ban (per Rule 5).
> - Do NOT remove `_capture_git_diff` or `_parse_diff_stat` — keep them as-is, they're called with worktree path now but the functions themselves don't change.
> - Do NOT modify `_parse_diff_stat`'s `project_path` argument — it stays as project root, not worktree path.
>
> Standard prompt feedback protocol → `bellows/knowledge/research/agent-prompt-feedback.md`.
>
> **Deposits:**
> - `bellows/bellows.py`
> - `bellows/.gitignore`
> - `bellows/knowledge/development/worktree-impl-dev-log-2026-05-03.md`
>
> **STOP REMINDER (BOTTOM):** Step 1 is COMPLETE when (a) `.gitignore` updated, (b) `_create_worktree` and `_teardown_worktree` and the two exception classes defined in `bellows.py`, (c) startup prune hook added to `Bellows.__init__`, (d) 6 cwd swaps in `run_plan`, (e) creation wired with strict-pause-on-failure, (f) teardown wired at all three exit points, (g) targeted test regression matches baseline, (h) two commits landed, (i) dev log deposited. Do NOT execute Step 2. Do NOT move the plan to Done. Wait for CEO confirmation.

---
---

## STEP 2 — BELLOWS DEVELOPER (QA)

---

> **Before starting, read `bellows/knowledge/development/worktree-impl-dev-log-2026-05-03.md` and check the Output Receipt status. If status is not Complete, stop and report the issue to the CEO before proceeding.**
>
> **STOP REMINDER (TOP):** This is the QA verification step. Do NOT modify production code. Do NOT move the plan to Done — the Planner performs the terminal move after Rule 22 verification passes.
>
> **Critical context for QA scope:** The Bellows daemon is on PRE-FIX code through this entire QA window. The new worktree code in `bellows.py` is committed but not loaded by the running daemon. This QA is therefore a CODE-LEVEL verification only — grep for shape, run unit tests, inspect the dev log. The behavioral verification (does worktree isolation actually work end-to-end?) lives in Plan 2 (`executable-bellows-worktree-tests-2026-05-03`), which dispatches AFTER Bellows is restarted with the new code active. Do NOT attempt to exercise the new code path here — any test that triggers a real `git worktree add` runs against pre-fix Bellows behavior and will produce misleading results.
>
> You are the Bellows Developer (acting as QA). Read your specialist file at `bellows/agents/BELLOWS_DEVELOPER.md` first. Skip glossary read.
>
> **Task: verify Step 1's deliverables exist with the expected shape, run targeted test regression, run Rule 20 self-check, write QA report.**
>
> **Phase 1 — Create evidence directory.** `mkdir -p bellows/knowledge/qa/evidence/executable-bellows-worktree-impl-2026-05-03`.
>
> **Phase 2 — Deliverable verification (Rule 17, code-level only).** Read Step 1's dev log to identify exact line locations. For EACH listed deliverable, verify via grep with output piped to evidence directory:
>
> 1. **`.bellows-worktrees/` in `.gitignore`.** Run: `grep -n "bellows-worktrees" /Users/marklehn/Desktop/GitHub/bellows/.gitignore | tee bellows/knowledge/qa/evidence/executable-bellows-worktree-impl-2026-05-03/grep_gitignore.txt`. Expected: at least one match.
>
> 2. **`_create_worktree` function defined.** Run: `grep -n "^def _create_worktree" /Users/marklehn/Desktop/GitHub/bellows/bellows.py | tee bellows/knowledge/qa/evidence/executable-bellows-worktree-impl-2026-05-03/grep_create_worktree.txt`. Expected: exactly one match.
>
> 3. **`_teardown_worktree` function defined.** Run: `grep -n "^def _teardown_worktree" /Users/marklehn/Desktop/GitHub/bellows/bellows.py | tee bellows/knowledge/qa/evidence/executable-bellows-worktree-impl-2026-05-03/grep_teardown_worktree.txt`. Expected: exactly one match.
>
> 4. **Custom exception classes defined.** Run: `grep -n "class WorktreeCreationError\|class WorktreeTeardownError" /Users/marklehn/Desktop/GitHub/bellows/bellows.py | tee bellows/knowledge/qa/evidence/executable-bellows-worktree-impl-2026-05-03/grep_exceptions.txt`. Expected: exactly two matches.
>
> 5. **Retry-once pattern present.** Run: `grep -n -A 5 "worktree creation failed" /Users/marklehn/Desktop/GitHub/bellows/bellows.py | tee bellows/knowledge/qa/evidence/executable-bellows-worktree-impl-2026-05-03/grep_retry_pattern.txt`. Expected: matches showing the retry pattern (sleep + second worktree add attempt). Also confirm a `time.sleep(2)` appears in the helper.
>
> 6. **Cherry-pick conflict handling present.** Run: `grep -n -B 1 -A 3 "cherry-pick.*--abort\|cherry-pick conflict" /Users/marklehn/Desktop/GitHub/bellows/bellows.py | tee bellows/knowledge/qa/evidence/executable-bellows-worktree-impl-2026-05-03/grep_cherry_pick_abort.txt`. Expected: matches showing `cherry-pick --abort` invocation in `_teardown_worktree`.
>
> 7. **Startup prune hook in `__init__`.** Run: `grep -n -B 2 -A 3 "worktree.*prune\|worktree prune" /Users/marklehn/Desktop/GitHub/bellows/bellows.py | tee bellows/knowledge/qa/evidence/executable-bellows-worktree-impl-2026-05-03/grep_startup_prune.txt`. Expected: at least one match within `Bellows.__init__` body.
>
> 8. **6 cwd swaps in `run_plan` (worktree path used in capture and runner calls).** Run: `grep -n "wt_path" /Users/marklehn/Desktop/GitHub/bellows/bellows.py | tee bellows/knowledge/qa/evidence/executable-bellows-worktree-impl-2026-05-03/grep_wt_path_usage.txt`. Expected: at least 8 matches in `run_plan` (4 `_capture_git_diff` calls + 2 `runner.run_step` calls + helper return + creation call), plus the `_create_worktree` and `_teardown_worktree` definitions.
>
> 9. **Teardown wired at all three exit points.** Run: `grep -n "_teardown_worktree(" /Users/marklehn/Desktop/GitHub/bellows/bellows.py | tee bellows/knowledge/qa/evidence/executable-bellows-worktree-impl-2026-05-03/grep_teardown_calls.txt`. Expected: at least 4 matches — 1 function definition + 3 call sites in `run_plan` (auto-close path, mid-plan pause path, verdict-request-from-agent path). If fewer than 4 matches, one of the exit paths was missed and worktrees will leak. Flag as ❌ Critical if count < 4.
>
> 10. **Two commits landed.** Run: `cd /Users/marklehn/Desktop/GitHub/bellows && git --no-pager log --oneline -5 | tee bellows/knowledge/qa/evidence/executable-bellows-worktree-impl-2026-05-03/git_log.txt`. Expected: top two commits match the messages from Phase 10 of Step 1 ("fix(bellows): per-plan git worktree..." and "docs: dev log for worktree implementation").
>
> Produce a verification table: `| Deliverable | Expected | Status (✅/❌) | Evidence |`. Cite the evidence file paths in the Evidence column. ANY ❌ item is a Critical finding that blocks the plan from closing.
>
> **Phase 3 — Targeted test regression.** From bellows directory: `cd /Users/marklehn/Desktop/GitHub/bellows && python -m pytest tests/ -v 2>&1 | tee bellows/knowledge/qa/evidence/executable-bellows-worktree-impl-2026-05-03/pytest_targeted.txt`. Expected: same baseline as Step 1 dev log reports (all tests pass except 1 pre-existing `test_run_step_timeout`). Compare counts to dev log.
>
> If new failures appear, this is a CRITICAL regression — Plan 1 modified `run_plan`'s structure, and a regression here means the existing test mocks may be brittle to the new code shape. Document each new failure in the QA report and STOP. Do NOT proceed to Phase 4.
>
> **Phase 4 — Write QA report.** Deposit to `bellows/knowledge/qa/worktree-impl-qa-2026-05-03.md` using canonical Python file write pattern. Include: (a) Phase 2 verification table with all 10 deliverables and evidence file paths, (b) Phase 3 test regression result with pass/fail counts, (c) Output Receipt with Status, (d) the Rule 20 self-check stdout output appended at the end (see Phase 6).
>
> **Phase 5 — Update PROJECT_STATUS.md.** Add a completed milestone entry. Use `Desktop Commander:edit_block` with verbatim anchor. The anchor should be the existing first line under the "## Completed" section header (currently the 2026-05-03 multi-step parser fix entry). Insert the new entry ABOVE that line (so the new entry becomes the new most-recent). Entry text:
>
> `- 2026-05-03: Plan 1 of BACKLOG #1 (parallel-plan scope_check collision) shipped — per-plan git worktree implementation. Two new helpers in bellows.py: \`_create_worktree(project_path, slug)\` (with retry-once-then-strict-pause-via-gate_failure-verdict on creation failure) and \`_teardown_worktree(project_path, wt_path, slug)\` (cherry-pick + uncommitted file copy-back + abort-on-conflict). 6 cwd swaps in \`run_plan\` route capture and runner calls through worktree path. Startup \`git worktree prune\` hook added to \`Bellows.__init__\` for stale-registration cleanup after crashes. \`.bellows-worktrees/\` added to \`bellows/.gitignore\`. Targeted test regression matches baseline. Plan 2 (tests) staged at \`_staging-executable-bellows-worktree-tests-2026-05-03.md\` for post-restart dispatch. REMINDER: restart Bellows daemon to load worktree code; behavioral verification ships via Plan 2 + post-restart canary.`
>
> **Phase 6 — Mandatory Rule 20 self-check.** Run the standard self-check Python block at the end of this step. Required evidence files: `grep_gitignore.txt`, `grep_create_worktree.txt`, `grep_teardown_worktree.txt`, `grep_exceptions.txt`, `grep_retry_pattern.txt`, `grep_cherry_pick_abort.txt`, `grep_startup_prune.txt`, `grep_wt_path_usage.txt`, `grep_teardown_calls.txt`, `git_log.txt`, `pytest_targeted.txt`. Plan slug: `executable-bellows-worktree-impl-2026-05-03`. QA report path: `bellows/knowledge/qa/worktree-impl-qa-2026-05-03.md`.
>
> ```python
> # Rule 20 — Mandatory QA Self-Check
> import os, sys
> plan_slug = "executable-bellows-worktree-impl-2026-05-03"
> qa_report_path = "bellows/knowledge/qa/worktree-impl-qa-2026-05-03.md"
> evidence_dir = f"bellows/knowledge/qa/evidence/{plan_slug}/"
> required_evidence_files = [
>     "grep_gitignore.txt",
>     "grep_create_worktree.txt",
>     "grep_teardown_worktree.txt",
>     "grep_exceptions.txt",
>     "grep_retry_pattern.txt",
>     "grep_cherry_pick_abort.txt",
>     "grep_startup_prune.txt",
>     "grep_wt_path_usage.txt",
>     "grep_teardown_calls.txt",
>     "git_log.txt",
>     "pytest_targeted.txt",
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
> Include the literal stdout in the QA report. If the self-check FAILS, the agent STOPS — does NOT update PROJECT_STATUS.md, does NOT move the plan to Done, reports the failure to the CEO and waits.
>
> **Phase 7 — Final commit.** After the QA report and PROJECT_STATUS.md edit are deposited, single final commit:
>
> ```
> cd /Users/marklehn/Desktop/GitHub/bellows && git --no-pager add knowledge/qa/worktree-impl-qa-2026-05-03.md knowledge/qa/evidence/executable-bellows-worktree-impl-2026-05-03/ PROJECT_STATUS.md && git --no-pager commit -m "qa: verify worktree implementation (Plan 1 of 2)"
> ```
>
> Standard prompt feedback protocol → `bellows/knowledge/research/agent-prompt-feedback.md`. The feedback append + commit are the absolute last operations.
>
> **Deposits:**
> - `bellows/knowledge/qa/worktree-impl-qa-2026-05-03.md`
> - `bellows/knowledge/qa/evidence/executable-bellows-worktree-impl-2026-05-03/` (11 evidence files per Rule 20 self-check)
> - `bellows/PROJECT_STATUS.md`
>
> **STOP.** Do NOT move this plan to Done/. Per the disable-auto-close model, the Planner performs the terminal move after Rule 22 verification passes.
