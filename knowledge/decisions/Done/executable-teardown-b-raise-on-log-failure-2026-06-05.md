# Bellows — _teardown_worktree (b): raise on commit-enumeration failure instead of silently emptying (ship)
**Date:** 2026-06-05 | **Tier:** Small | **Dispatch Mode:** bellows | **Test Scope:** full-suite | **Execution:** Step 1 (DEV) → Step 2 (QA) | **qa_steps:** 2 | **pause_for_verdict:** always | **auto_close:** false

## Execution Map

Step 1 (DEV) → Step 2 (QA). Sequential. DEV converts the bare `except` in `_teardown_worktree` step (b) (`bellows.py`) into a land-or-raise contract — raise `WorktreeTeardownError` on a `git log` exception OR non-zero returncode, while a successful-but-empty result still proceeds — plus 3 regression tests in `tests/test_worktree.py`. QA is code-level ONLY — full-suite + diff/contract verification; no live daemon run, no plan deposited into a watched `decisions/`.

## How to Run This Plan

Paste the bootstrap prompt into Claude Code. The agent reads the full plan file and executes Step 1 ONLY, then STOPS and waits for CEO verdict before Step 2. Bootstrap: `Read the plan at bellows/knowledge/decisions/executable-teardown-b-raise-on-log-failure-2026-06-05.md. Execute Step 1 ONLY. After completing Step 1, STOP and wait for my confirmation. Do NOT proceed to Step 2 or move the plan to Done.`

## CEO Context

**Closes the last uncovered silent-loss path in the worktree teardown/resume family (filed 2026-06-05).** `_teardown_worktree` step (b) collects un-landed worktree commits via `git log --format=%H HEAD --not <main_branch>` wrapped in `try/except Exception: commit_shas = []`. If that `git log` ever fails — subprocess exception (timeout/OS error) OR non-zero returncode — the bare except defaults `commit_shas` to empty: teardown then cherry-picks NOTHING, records NO `worktree_teardown` failure, copies dirty files, and removes the worktree. The committed work is lost. Because no failure is recorded, the Gap-1b continue-block and Gap-1c retry cannot catch it (both key off a `worktree_teardown` entry in `gate_result`), and Gap-2a does not cover it (2a guards the stranded-cleanup path in `_create_worktree`, not teardown's own removal). Surfaced by the 2026-06-05 Planner-direct diagnostic that confirmed Gap 2(b)/(c)'s resume-regression target is already closed.

**Fix (fix (a), fail-safe): raise instead of swallow.** On a `git log` exception, raise `WorktreeTeardownError` (chained); on a non-zero returncode, raise `WorktreeTeardownError` with the stderr. This routes the failure into the existing 1b halt / 1c retry, matching the rest of `_teardown_worktree`'s land-or-raise contract (the cherry-pick conflict path already raises). **The legitimate-empty case is preserved:** a successful `git log` (returncode 0) that returns zero commits — a step that made no commits — must NOT raise; teardown proceeds to copy-back and removal as before. This distinction (fail vs successfully-empty) is the crux of the change.

**No diagnostic.** Direct code read this session fully established the baseline — the exact `try/except Exception: commit_shas = []` block and its missing returncode check (Rule 10 bar met).

**Restart owed, no self-trip.** This plan edits `_teardown_worktree`; the running daemon executes this plan's own steps under the PRE-edit teardown, so this plan's own teardowns at each pause use the OLD code (which works on clean `main`). The fix activates only after a daemon restart. Keep local `main` CLEAN at the pause so this plan's own teardown succeeds.

**Why QA is code-level only.** The contract is fully provable by unit tests against `_teardown_worktree` with a `git_repo` fixture + a `subprocess.run` wrapper that fails ONLY the `git log` invocation. No daemon start, no live deposit, no filesystem event a running daemon would observe.

---
---

## STEP 1 — DEV

---

> **FIRST — before any reads or work: post a short visible message to chat (1-2 sentences) confirming you are starting this plan and stating your immediate next action.** This is the liveness anchor. Do NOT rename the plan file — Bellows already claimed it before invoking you.
>
> You are the Bellows Developer. Read your specialist file at `agents/BELLOWS_DEVELOPER.md` and `governance/GUARDRAILS.md` first. Skip glossary read — domain terminology is fully covered in the specialist file. Note: the worktree root IS the bellows project root — strip the `bellows/` prefix from any path references in this prompt when running commands.
>
> **Reads (mandatory, in order):** (1) `agents/BELLOWS_DEVELOPER.md` — your specialist file; (2) the `_teardown_worktree` step (b) block in `bellows.py` and the `test_teardown_*` cluster in `tests/test_worktree.py`, located via the Pre-edit verification queries — do NOT trust line numbers, locate by symbol/string.
>
> **Pre-edit verification (Rule 39).** Before any edits, run each query and confirm the symbol exists. Line numbers drift; locate by string. Post a 1-line marker after each query result.
>
> 1. **Claim:** `_teardown_worktree` step (b) currently reads `git log --format=%H HEAD --not <main_branch>` inside `try: result = subprocess.run([...]) ; commit_shas = result.stdout.strip().splitlines()[::-1]` with `except Exception: commit_shas = []`, and there is NO `result.returncode` check. **Query:** `grep -n "# (b) Collect commits made in worktree" bellows.py` then read the ~12 lines following. **Expected:** the bare `except Exception: commit_shas = []` is present; no returncode check between the subprocess call and the `commit_shas` assignment.
> 2. **Claim:** `WorktreeTeardownError` is defined in `bellows.py` and is the exception the cherry-pick-conflict path already raises. **Query:** `grep -n "class WorktreeTeardownError\|raise WorktreeTeardownError" bellows.py`. **Expected:** class defined; at least one existing `raise WorktreeTeardownError(...)` in the cherry-pick path.
> 3. **Claim:** the worktree teardown tests use a `git_repo` fixture and call `_teardown_worktree(...)` directly. **Query:** `grep -n "def test_teardown\|git_repo\|def _teardown_worktree\|_teardown_worktree(" tests/test_worktree.py | head` and read `test_teardown_cherry_picks_commits` and `test_teardown_aborts_on_cherry_pick_conflict`. **Expected:** four `test_teardown_*` tests; they construct a real git repo + worktree and assert on teardown behavior; the conflict test asserts `WorktreeTeardownError` is raised AND the worktree is left alive.
> 4. **Claim:** `subprocess` and `WorktreeTeardownError` are in scope at the edit site. **Query:** `grep -n "^import subprocess\|^import\|class WorktreeTeardownError" bellows.py | head`. **Expected:** `subprocess` imported; `WorktreeTeardownError` in the same module.
>
> If any symbol is absent or materially differs from expected, **STOP** — do not edit. Deposit a verification-mismatch report to `knowledge/flags/verification-mismatch-teardown-b-raise-2026-06-05-step-1.md` (claim, expected, actual, timestamp) and report to CEO.
>
> **Task — convert step (b) to a land-or-raise contract; change nothing else in the function.**
>
> Replace the step-(b) block (from the `# (b) Collect commits made in worktree` comment through the `commit_shas = result.stdout.strip().splitlines()[::-1]` line) with EXACTLY:
> ```
>     # (b) Collect commits made in worktree
>     # Fail-safe (2026-06-05): a git-log failure here must NOT silently default to
>     # an empty commit list — that would skip the cherry-pick and still remove the
>     # worktree, losing un-landed commits with NO recorded worktree_teardown failure
>     # (uncatchable by the Gap-1b continue-block and Gap-1c retry, both of which key
>     # off a recorded failure). Raise so the failure routes to the 1b halt / 1c retry,
>     # matching the rest of this function's land-or-raise contract. A successful-but-
>     # empty result (returncode 0, no commits made) is legitimate and proceeds.
>     try:
>         result = subprocess.run(
>             ["git", "--no-pager", "log", "--format=%H", "HEAD", "--not", main_branch],
>             cwd=wt_path, capture_output=True, text=True, timeout=30,
>         )
>     except Exception as e:
>         raise WorktreeTeardownError(
>             f"worktree commit enumeration failed (git log exception) for slug {slug}: {e}"
>         ) from e
>     if result.returncode != 0:
>         raise WorktreeTeardownError(
>             f"worktree commit enumeration failed (git log rc={result.returncode}) for slug {slug}: {result.stderr.strip()}"
>         )
>     commit_shas = result.stdout.strip().splitlines()[::-1]  # oldest-first for cherry-pick
> ```
> Do NOT modify step (a), the index.lock handling, the dirty-tree pre-check (b2), the cherry-pick loop (c), the dirty-file copy-back (d), or the worktree removal (e). The change is confined to step (b). The legitimate empty-commit path (returncode 0, empty stdout → `commit_shas = []` → no cherry-pick → normal removal) MUST be preserved — do not raise on a successful-but-empty result.
>
> **Regression tests** in `tests/test_worktree.py` — add adjacent to the existing `test_teardown_*` cluster, mirroring its `git_repo`-fixture style. Use a `subprocess.run` wrapper (monkeypatch) that fails ONLY the `git log ... --not ...` invocation and delegates all other git calls (symbolic-ref, status, cherry-pick, worktree remove) to the real `subprocess.run`, so the rest of teardown behaves normally up to the failure point:
> - `test_teardown_raises_on_git_log_exception` — the `git log` invocation raises (e.g. `subprocess.TimeoutExpired` or a generic `OSError`). Assert `_teardown_worktree(...)` raises `WorktreeTeardownError` AND the worktree directory STILL EXISTS afterward (commits not lost, worktree preserved for recovery).
> - `test_teardown_raises_on_git_log_nonzero` — the `git log` invocation returns a `CompletedProcess` with `returncode=1`, `stderr="fatal: bad revision"`. Assert `_teardown_worktree(...)` raises `WorktreeTeardownError`; worktree still exists.
> - `test_teardown_proceeds_on_empty_commit_list` — CRITICAL negative test for the preserved path: a real `git_repo` worktree created at `main` HEAD with NO new commits made in it (HEAD == main). Assert `_teardown_worktree(...)` does NOT raise and the worktree directory is removed (legitimate empty case proceeds exactly as before). If the existing fixtures already cover a no-commit teardown, mirror that setup.
> Confirm the four EXISTING teardown tests still pass unchanged (parity), especially `test_teardown_cherry_picks_commits` (commits still land) and `test_teardown_aborts_on_cherry_pick_conflict` (conflict still raises + worktree alive).
>
> **Pre-edit baseline:** run `python3 -m pytest tests/ 2>&1 | tail -15` and record pass/fail counts (note the known carry-over failures) BEFORE editing. Re-run AFTER editing; the only delta must be the 3 new tests passing — ZERO new failures, all existing teardown tests still green.
>
> **Commit** (do NOT push — Planner handles session-wrap): stage `bellows.py`, `tests/test_worktree.py`, the dev log, and `knowledge/research/agent-prompt-feedback.md`; message `fix(bellows): _teardown_worktree (b) raises on git-log failure instead of silently emptying commit list`.
>
> **Dev log** → `knowledge/development/teardown-b-raise-on-log-failure-2026-06-05.md`: the replaced block verbatim, confirmation steps (a)/(b2)/(c)/(d)/(e) are byte-unchanged, the fail-vs-successfully-empty distinction, pre-edit verification results, both pytest runs (before/after counts). Include an **Output Receipt** with a "Files Created or Modified" list.
>
> **Standard prompt feedback protocol** → append an entry to `knowledge/research/agent-prompt-feedback.md`.
>
> **Deposits:**
> - `bellows/knowledge/development/teardown-b-raise-on-log-failure-2026-06-05.md`
> - `bellows/knowledge/research/agent-prompt-feedback.md`
> - `bellows/bellows.py` (modified)
> - `bellows/tests/test_worktree.py` (modified)
>
> **STOP. Do NOT proceed to Step 2. Do NOT move the plan to Done. Wait for CEO verdict before continuing.**

---
---

## STEP 2 — QA

---

> **FIRST — before any reads or work: post a short visible message to chat (1-2 sentences) confirming you are starting this step and stating your immediate next action.** This is the liveness anchor. Do NOT rename the plan file — Bellows already claimed it before invoking you.
>
> You are the Bellows QA Agent. Read your specialist file at `agents/BELLOWS_QA.md` and `governance/GUARDRAILS.md` first. Skip glossary read — domain terminology is fully covered in the specialist file. Note: the worktree root IS the bellows project root — strip the `bellows/` prefix from any path references in this prompt when running commands.
>
> **Scope note — code-level ONLY.** Do NOT start the daemon, do NOT deposit any plan into a watched `decisions/` directory, do NOT simulate a live dispatch. Verify by reading the code and running the suite. Nothing in this step should produce a filesystem event a running daemon would observe.
>
> **Before starting, read `knowledge/development/teardown-b-raise-on-log-failure-2026-06-05.md` (DEV's Step 1 deposit) and check its Output Receipt status; if not Complete, stop and report the blocker.**
>
> **Deliverable Verification (Rule 17).** Read DEV's Output Receipt "Files Created or Modified" list. For each, verify the file exists and the declared change is present. Produce a verification table `| # | Deliverable | Expected | Status (PASS/FAIL) | Evidence |` (use the literal words PASS / FAIL in the Status column — not glyphs). Specifically:
>
> 1. **Exception path raises** — step (b) wraps the `git log` `subprocess.run` in `try/except Exception as e: raise WorktreeTeardownError(...) from e`. Capture the try/except to `evidence/raise_paths.txt`.
> 2. **Non-zero returncode raises** — immediately after, `if result.returncode != 0: raise WorktreeTeardownError(...)` with the stderr. Capture to `evidence/raise_paths.txt` (same file, both raise sites).
> 3. **Legitimate-empty preserved** — on a successful `git log` (returncode 0), `commit_shas = result.stdout.strip().splitlines()[::-1]` still runs and an empty result does NOT raise. Capture the post-check assignment + a one-line statement that returncode-0-empty does not raise to `evidence/empty_case_preserved.txt`.
> 4. **Rest of function byte-unchanged** — steps (a), index.lock handling, (b2) dirty-tree pre-check, (c) cherry-pick loop, (d) copy-back, (e) removal are unchanged. Capture the full `_teardown_worktree` body to `evidence/block_body.txt` and confirm only step (b) changed.
> 5. **Diff scope** — `git --no-pager diff -- bellows.py` shows changes confined to step (b); nothing else in `bellows.py` changed. Capture to `evidence/diff_scope.txt`.
> 6. **Three new tests exist** — grep `tests/test_worktree.py` for `test_teardown_raises_on_git_log_exception`, `test_teardown_raises_on_git_log_nonzero`, `test_teardown_proceeds_on_empty_commit_list` → all three present. Capture to `evidence/new_tests_grep.txt`.
> 7. **Existing teardown tests intact** — `test_teardown_removes_worktree_directory`, `test_teardown_cherry_picks_commits`, `test_teardown_copies_uncommitted_files`, `test_teardown_aborts_on_cherry_pick_conflict` all still present and passing. Capture to `evidence/existing_tests.txt`.
> 8. **Dev log complete** — exists with the replaced block, byte-unchanged confirmation, fail-vs-empty distinction, pre-edit verification, both pytest runs. Capture filesize + first/last 5 lines to `evidence/dev_log_check.txt`.
>
> Any FAIL blocks plan close — report to CEO.
>
> **Test execution.** Run the full suite: `python3 -m pytest tests/ -v 2>&1 | tail -200`. Capture to `evidence/pytest_full.txt`. Verify: (a) all three new tests appear in verbose output and PASS — in particular `test_teardown_proceeds_on_empty_commit_list` PASS (proves the legitimate-empty path was NOT broken); (b) the four existing teardown tests still PASS; (c) ZERO NEW failures beyond the carry-over present in DEV's pre-edit baseline; (d) total pass count == DEV's reported post-edit number.
>
> **Rule 20 self-check** — run the canonical Rule 20 self-check from `RULE_20_SELF_CHECK_BLOCK.md` at governance root. Values: `plan_slug` = `executable-teardown-b-raise-on-log-failure-2026-06-05`; `qa_report_path` = `bellows/knowledge/qa/teardown-b-raise-on-log-failure-2026-06-05.md`; `evidence_dir` = `bellows/knowledge/qa/evidence/teardown-b-raise-on-log-failure-2026-06-05/`; `required_evidence_files` = `["raise_paths.txt", "empty_case_preserved.txt", "block_body.txt", "diff_scope.txt", "new_tests_grep.txt", "existing_tests.txt", "dev_log_check.txt", "pytest_full.txt"]`. Include literal stdout in the QA report. If FAILED, halt — report to CEO.
>
> **Final:** Update `bellows/PROJECT_STATUS.md` — prepend a 2026-06-05 entry under Completed for "_teardown_worktree (b) raise on git-log failure (last worktree-family silent-loss path)" with a one-paragraph summary, using `Filesystem:edit_file` (find the existing topmost Completed entry as anchor and insert immediately before it).
>
> **DAEMON RESTART REMINDER — put in the QA deposit under "Flags for CEO":** "REMINDER: restart the Bellows daemon to activate the teardown-(b) raise. The running daemon executed this plan under the pre-edit `_teardown_worktree`; the fail-safe activates on the next teardown after restart. Also owed: capture this plan's organic Opus baseline (turns/wall/cost) from the step logs for the Opus<->Sonnet A/B."
>
> **Commit:** stage `knowledge/qa/teardown-b-raise-on-log-failure-2026-06-05.md`, the `knowledge/qa/evidence/teardown-b-raise-on-log-failure-2026-06-05/` evidence files, and `PROJECT_STATUS.md` with message `qa(bellows): teardown-b-raise verified — land-or-raise contract, empty-case preserved, zero new regressions`. **DO NOT push to origin** — the Planner handles session-wrap commits.
>
> **Standard prompt feedback protocol** → append an entry to `knowledge/research/agent-prompt-feedback.md`. Second commit: `docs: prompt feedback — bellows QA teardown-b-raise`. **DO NOT push.**
>
> **Deposits:**
> - `bellows/knowledge/qa/teardown-b-raise-on-log-failure-2026-06-05.md`
> - `bellows/knowledge/qa/evidence/teardown-b-raise-on-log-failure-2026-06-05/`
> - `bellows/PROJECT_STATUS.md` (modified)
> - `bellows/knowledge/research/agent-prompt-feedback.md`
