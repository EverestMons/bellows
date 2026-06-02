# Bellows — Preserve Un-Landed Commits on Stranded-Worktree Cleanup (Gap 2a, ship)
**Date:** 2026-06-01 | **Tier:** Small | **Dispatch Mode:** bellows | **Test Scope:** full-suite | **Execution:** Step 1 (DEV) → Step 2 (QA) | **qa_steps:** 2 | **pause_for_verdict:** always | **auto_close:** false

## Execution Map

Step 1 (DEV) → Step 2 (QA). Sequential. DEV adds a preserve-before-destroy guard INSIDE the `if os.path.exists(wt_path):` stranded-cleanup block of `_create_worktree` (`bellows.py`), BEFORE the existing `git worktree remove --force`. When the existing worktree's HEAD holds commits not yet landed on local `main` (un-landed work), the guard creates a `bellows-preserved/<slug>-<utc-ts>` branch pointing at that HEAD — making the commits reachable instead of dangling — then proceeds with the existing remove → rmtree → prune → recreate-at-`HEAD --detach` flow UNCHANGED. Plus three regression tests in `tests/test_worktree.py`. QA is code-level ONLY — no live multi-step daemon run.

## How to Run This Plan

Paste the bootstrap prompt into Claude Code. The agent reads the full plan file and executes Step 1 ONLY, then STOPS and waits for CEO verdict before Step 2. Bootstrap: `Read the plan at bellows/knowledge/decisions/executable-preserve-unlanded-commits-on-stranded-cleanup-2026-06-01.md. Execute Step 1 ONLY. After completing Step 1, STOP and wait for my confirmation. Do NOT proceed to Step 2 or move the plan to Done.`

## CEO Context

**Bug (full mechanism in `knowledge/research/worktree-teardown-resume-regression-2026-05-31.md`, Gap 2).** `_create_worktree`'s stranded-cleanup treats ANY pre-existing `wt_path` as "stranded from a prior failed dispatch" and unconditionally destroys it (`git worktree remove --force` → `shutil.rmtree` → `git worktree prune`), recreating at `HEAD --detach`. It never inspects the worktree's commits first. When the pre-existing worktree is actually a live inter-step worktree holding Step N's un-landed commits, those commits become dangling (recoverable only via `git fsck` until GC). This was reproduced live: Step 1's dedup commit became a dangling chain tipped at `858ab10` after the stranded-cleanup nuked the worktree on resume.

**This plan ships Gap 2(a) ONLY** — the data-safety cut: *before destroying a stranded worktree, detect un-landed commits and preserve them on a branch.* It converts silent data-loss into recoverable, reachable commits. Explicitly OUT of scope (later, separate plans): Gap 2(b) recreate-from-step-branch and Gap 2(c) cherry-pick-prior-step-on-resume (both would make resume FUNCTIONALLY correct but change the core worktree-creation model and require a live multi-step run to validate — incompatible with code-level-only QA); Gap 1(c) re-attempt-teardown-on-resume; Gap 3 teardown auto-stash. **Recreate-at-`HEAD --detach` stays UNCHANGED** in this plan — the resumed step still runs from HEAD; this cut prevents loss, it does not restore the work into the tree.

**Relationship to Gap 1(b) (shipped, `8b2f952`).** Gap 1(b) blocks a continue verdict over an uncleared `worktree_teardown` failure, halting the plan with the worktree alive. So the AUTOMATIC cascade is already cut. Gap 2(a) is the BACKSTOP for the residual paths where `_create_worktree` still meets a commit-bearing worktree (manual re-dispatch, slug reuse, any future regression). Defense-in-depth, not the primary cascade-stopper.


**Injection site (verified live this session, locate by symbol — numbers drift).** In `_create_worktree` (`bellows.py`), `wt_path = os.path.join(project_path, ".bellows-worktrees", slug)`, then `if os.path.exists(wt_path):` opens the stranded-cleanup block whose first action is the `_log("WARN", "⚠ stranded worktree found ...")` line, followed by `git --no-pager worktree remove --force <wt_path>`, `shutil.rmtree(wt_path, ignore_errors=True)`, and `git --no-pager worktree prune`. The new preserve step goes at the TOP of this block, immediately after the existing WARN log and BEFORE the `worktree remove --force` call. Recreate-at-HEAD (the `git --no-pager worktree add <wt_path> HEAD --detach` that follows the block) is NOT touched.

**Why "preserve on a branch" saves the commits.** `git worktree remove --force` + `prune` removes the worktree's working dir and admin files but does NOT delete commits or branches. A detached worktree HEAD with no ref pointing at it becomes unreachable (dangling) after prune. Creating a branch ref at that HEAD BEFORE removal makes the commits permanently reachable and recoverable (`git branch --list 'bellows-preserved/*'`). The branch ref is independent of the worktree and survives its removal.

**Detection predicate — un-landed = NOT reachable from local `main`.** The worktree was created detached at some HEAD. "Un-landed" means that HEAD is ahead of / divergent from local `main` (its commits were never cherry-picked back). Predicate: resolve the worktree HEAD (`git -C <wt_path> rev-parse --verify HEAD`); resolve local `main` (`git -C <project_path> rev-parse --verify main`); the worktree has un-landed commits iff `git -C <project_path> merge-base --is-ancestor <wt_head> main` returns NON-zero (wt_head is NOT an ancestor of main). If it returns zero, the worktree HEAD is already on main → nothing to preserve.

**Fail-safe bias toward preservation.** This is a data-safety cut, so every uncertainty biases to PRESERVE, never to destroy-silently: if the worktree HEAD is readable BUT the `merge-base --is-ancestor` check errors or `main` is unresolvable, treat as un-landed and create the preservation branch anyway. The ONLY case that skips preservation is (a) HEAD unreadable / `wt_path` is not a valid worktree (nothing recoverable to branch), or (b) the ancestor check cleanly returns zero (definitively already landed). DEV must implement exactly this bias — do NOT invent a "force destroy" path.

**Bellows-modifies-Bellows / restart (same property as Gap 1b).** This plan edits `_create_worktree`. The running daemon executes THIS plan under PRE-edit code, so the new guard is NOT active during this plan's own DEV→QA close/resume. THIS plan does not self-trip: its own slug's `wt_path` does not pre-exist at Step-1 dispatch (fresh slug → stranded-cleanup block does not enter); at the Step-1 pause `_teardown_worktree` removes the worktree (main is clean per discipline), so at Step-2 resume `wt_path` again does not exist → block does not enter. The new behavior activates only on the next plan dispatched AFTER a daemon restart. Gap 1(b)'s guard (active, daemon restarted) protects this plan's own teardown as a backstop. QA flags the restart for the CEO.

**Why QA is code-level only.** A live multi-step integration run inside this plan would require an actual stranded-worktree-with-un-landed-commits state to exercise the preserve path — which means tripping the teardown/resume bug during the plan's own close/resume. QA verifies the preserve logic by reading the code and running unit/regression tests against `_create_worktree` with constructed fixture repos, NOT by dispatching a real multi-step plan through the daemon.

---
---

## STEP 1 — DEV

---

> **FIRST — before any reads or work: post a short visible message to chat (1-2 sentences) confirming you are starting this plan and stating your immediate next action.** This is the liveness anchor. Do NOT rename the plan file — Bellows already claimed it before invoking you.
>
> You are the Bellows Developer. Read your specialist file at `agents/BELLOWS_DEVELOPER.md` and `governance/GUARDRAILS.md` first. Skip glossary read — domain terminology is fully covered in the specialist file. Note: the worktree root IS the bellows project root — strip the `bellows/` prefix from any path references in this prompt when running commands.
>
> **Reads (mandatory, in order):** (1) `agents/BELLOWS_DEVELOPER.md` — your specialist file; (2) `knowledge/research/worktree-teardown-resume-regression-2026-05-31.md` — the diagnostic blueprint (read the Confirmed Mechanism section and the "Gap 2" fix-shape options; you implement option 2(a) ONLY); (3) the target region of `bellows.py` and `tests/test_worktree.py`, located via the Pre-edit verification queries below (do NOT trust line numbers — locate by symbol/string).
>
> **Pre-edit verification (Rule 39).** Before any edits, run each query and confirm the symbol exists. Line numbers drift; locate by string. Post a 1-line marker after each query result.
>
> 1. **Claim:** `_create_worktree` computes `wt_path` and enters an `if os.path.exists(wt_path):` stranded-cleanup block whose first action is a WARN log, then `worktree remove --force`, `shutil.rmtree`, `worktree prune`. **Query:** `grep -n "def _create_worktree\|os.path.exists(wt_path)\|stranded worktree found\|worktree.*remove.*--force\|rmtree(wt_path" bellows.py`. **Expected:** the def, the `if os.path.exists(wt_path):` guard, the `stranded worktree found` WARN, the `remove --force` subprocess, and the `shutil.rmtree(wt_path, ignore_errors=True)` all appear in one contiguous region.
> 2. **Claim:** worktrees are created detached at HEAD (so a live worktree HEAD can be ahead of main). **Query:** `grep -n "worktree.*add.*HEAD.*--detach" bellows.py`. **Expected:** ≥1 hit — `git --no-pager worktree add <wt_path> HEAD --detach`. This is the line AFTER the stranded-cleanup block; confirm you are NOT editing it.
> 3. **Claim:** `_create_worktree` already imports/uses `subprocess`, `shutil`, `os`, and `_log` in scope; there is NO ledger handle in this function's scope. **Query:** read the full `_create_worktree` body. **Expected:** `_log(...)` is callable here; `subprocess.run([...], cwd=..., capture_output=True, text=True, timeout=...)` is the established call shape; confirm whether any ledger/verdict object is reachable (it is NOT — so preservation is recorded via `_log` + the branch itself, NOT a ledger entry; do NOT add ledger plumbing).
> 4. **Claim:** `tests/test_worktree.py` exists and constructs fixture git repos to exercise `_create_worktree`. **Query:** `grep -n "_create_worktree\|worktree add\|tmp_path\|subprocess.run\|git.*init" tests/test_worktree.py | head -40`. **Expected:** existing tests build a real git repo (init + commit) and call `_create_worktree`; mirror their fixture/setup style for the new tests.
>
> If any symbol is absent or materially differs from expected, **STOP** — do not edit. Deposit a verification-mismatch report to `knowledge/flags/verification-mismatch-preserve-unlanded-commits-on-stranded-cleanup-2026-06-01-step-1.md` (claim, expected, actual, timestamp) and report to CEO.
>
> **Task — one preserve-before-destroy guard in `bellows.py`, at the TOP of the `if os.path.exists(wt_path):` stranded-cleanup block, immediately AFTER the existing `stranded worktree found` WARN log and BEFORE the `git ... worktree remove --force` call.**
>
> Implement Gap 2(a): detect un-landed commits and preserve them on a branch before the existing destruction runs. Exact behavior:
> - Resolve the worktree HEAD: `git --no-pager -C <wt_path> rev-parse --verify HEAD` (capture_output, text, timeout=10). If this fails (non-zero / exception), the worktree has no readable HEAD — nothing to preserve; SKIP preservation and fall through to the existing remove/rmtree/prune unchanged.
> - If the HEAD resolved, determine whether it is un-landed: run `git --no-pager -C <project_path> merge-base --is-ancestor <wt_head> main` (timeout=10). `returncode == 0` ⇒ wt_head is already on `main` ⇒ NOT un-landed ⇒ SKIP preservation. ANY other outcome (`returncode != 0`, OR the command raised, OR `main` could not be resolved) ⇒ treat as un-landed (fail-safe bias to preserve).
> - When un-landed: build a preservation branch name `bellows-preserved/{slug}-{ts}` where `ts` is a UTC timestamp `datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")` (confirm `datetime`/`timezone` import availability; if not imported in this module, use `time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())` since `time` is already in scope). Create it: `git --no-pager -C <project_path> branch <branch_name> <wt_head>` (timeout=10). Then emit a loud `_log("WARN", f"⚠ preserved un-landed worktree commits at {wt_head} on branch {branch_name} before stranded-cleanup", slug=slug)`. If the `branch` command itself fails, emit a LOUDER `_log("ERROR", ...)` naming `wt_head` so the SHA is recoverable from the log, but still fall through to removal (do not abort worktree creation — the plan must still run).
> - Then proceed with the EXISTING remove → rmtree → prune → recreate-at-`HEAD --detach`, byte-for-byte unchanged. The preservation branch survives the removal.
>
> Do NOT modify `_teardown_worktree`, `_consume_verdicts`, or the `worktree add ... HEAD --detach` recreate line. Do NOT change recreate-at-HEAD semantics — that is Gap 2(b), out of scope. Do NOT add a ledger handle or any new function plumbing. The change is confined to the inside-top of the `if os.path.exists(wt_path):` block in `_create_worktree`.
>
> **Regression tests — add exactly three to `tests/test_worktree.py`.** Mirror that module's existing fixture style (real git repo init + commit, `_create_worktree` invocation, any autouse reset in `conftest.py`). For each test, build a project repo with a `main` branch, create a worktree dir at `.bellows-worktrees/<slug>` (use the same path shape `_create_worktree` computes), and set up its HEAD state, then call `_create_worktree(project_path, slug)` so the `if os.path.exists(wt_path):` block runs.
>
> 1. `test_stranded_cleanup_preserves_unlanded_commits` — set up the existing worktree with a commit on its detached HEAD that is NOT on `main` (ahead of main). Capture `wt_head` before the call. Call `_create_worktree`. Assert: (a) a branch matching `bellows-preserved/<slug>-*` now exists (`git branch --list`); (b) that branch points at the captured `wt_head` (`git rev-parse <branch>` == `wt_head`); (c) the captured `wt_head` commit is still reachable (`git cat-file -e <wt_head>` succeeds / `git rev-list` from the branch contains it); (d) the worktree was still removed and recreated (a fresh worktree exists at `wt_path` whose HEAD == main HEAD). This proves preservation happens AND the existing destroy/recreate still runs.
> 2. `test_stranded_cleanup_no_preserve_when_already_landed` — set up the existing worktree with HEAD == `main` HEAD (or an ancestor of main — already landed). Call `_create_worktree`. Assert: NO `bellows-preserved/*` branch is created (`git branch --list 'bellows-preserved/*'` is empty), and the worktree is removed+recreated normally. This proves specificity — no spurious preservation branches on the already-landed/happy path.
> 3. `test_stranded_cleanup_failsafe_preserves_when_main_unresolvable` — set up the existing worktree with a real commit on its HEAD, but a project state where the `merge-base --is-ancestor ... main` check cannot cleanly return zero (e.g., no local `main` ref resolvable / orphan state). Call `_create_worktree`. Assert: a `bellows-preserved/<slug>-*` branch IS created (fail-safe bias to preserve under uncertainty), and `_create_worktree` still returns a valid recreated worktree path without raising. This locks the never-destroy-on-uncertainty bias.
>
> **Test-count note:** three is the minimum covering preserve (positive), no-preserve-when-landed (specificity), and fail-safe-under-uncertainty. Do not enumerate further permutations.
>
> **Reset module/global state between tests** following the module's existing pattern. Confirm no existing `_create_worktree`/worktree test breaks from leaked state or leftover `bellows-preserved/*` branches (clean up branches created by the new tests in their teardown so they do not leak into other tests).
>
> **Test execution.** Run the full suite pre-edit and capture the baseline: `python3 -m pytest tests/ -v 2>&1 | tail -200`. Record the pass count and the EXACT set of pre-existing failures empirically (the diagnostic notes ~4× `test_decisions.py` + `test_run_step_timeout` as known carry-over — confirm, do not assume). After edits, run the full suite again. Expected post-edit: your three new tests PASS and ZERO NEW failures beyond the pre-edit carry-over baseline. Capture both runs verbatim.
>
> **Anchor verification before commit.** Run and confirm: `grep -n "bellows-preserved/" bellows.py` (≥1 — the preservation branch name); `grep -n "merge-base.*--is-ancestor" bellows.py` (the detection predicate); `grep -n "rev-parse --verify HEAD" bellows.py` (the wt_head resolve). Confirm `_teardown_worktree` and `_consume_verdicts` are byte-unchanged and the `worktree add ... HEAD --detach` recreate line is unchanged: `git --no-pager diff -- bellows.py` touches ONLY the inside-top of the `if os.path.exists(wt_path):` block in `_create_worktree`.
>
> **Deposit:** author a dev log to `knowledge/development/preserve-unlanded-commits-on-stranded-cleanup-2026-06-01.md` documenting: the guard's placement (with a 6-10 line before/after snippet of the top of the stranded-cleanup block), the detection predicate and the fail-safe bias rules, the preservation-branch naming, the Pre-edit verification query results, the three new regression-test functions in `tests/test_worktree.py` with their assertions, the pre-edit and post-edit full-suite pytest output (pass/fail counts + the carry-over failure baseline), the anchor-verification grep results, and the Output Receipt per your specialist file.
>
> **Commit:** stage `bellows.py`, `tests/test_worktree.py`, and `knowledge/development/preserve-unlanded-commits-on-stranded-cleanup-2026-06-01.md` with message `fix(bellows): preserve un-landed worktree commits on stranded-cleanup — branch before destroy (Gap 2a)`. **DO NOT push to origin** — the Planner handles session-wrap commits.
>
> **Standard prompt feedback protocol** → append an entry to `knowledge/research/agent-prompt-feedback.md`. Second commit: `docs: prompt feedback — bellows DEV preserve-unlanded-commits-on-stranded-cleanup`. **DO NOT push.**
>
> **Deposits:**
> - `bellows/knowledge/development/preserve-unlanded-commits-on-stranded-cleanup-2026-06-01.md`
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
> **Scope note — code-level ONLY.** Do NOT dispatch or simulate a live multi-step plan through the daemon to test this. Exercising the preserve path live would require an actual stranded-worktree-with-un-landed-commits state, which means tripping the teardown/resume bug during this plan's own close/resume. Verify by reading the code and running the unit/regression suite against `_create_worktree` with fixture repos. Nothing in this step should start the daemon or move a plan into a watched `decisions/` directory.
>
> **Before starting, read `knowledge/development/preserve-unlanded-commits-on-stranded-cleanup-2026-06-01.md` (DEV's Step 1 deposit) and check its Output Receipt status; if not Complete, stop and report the blocker.**
>
> **Deliverable Verification (Rule 17).** Read DEV's Output Receipt "Files Created or Modified" list. For each, verify the file exists and the declared change is present. Produce a verification table `| # | Deliverable | Expected | Status (✅/❌) | Evidence |`. Specifically:
>
> 1. **Preserve guard present at top of stranded-cleanup block** — inside `if os.path.exists(wt_path):`, AFTER the `stranded worktree found` WARN and BEFORE `worktree remove --force`, there is a HEAD resolve (`rev-parse --verify HEAD`), a `merge-base --is-ancestor <wt_head> main` un-landed check, and a `git ... branch bellows-preserved/<slug>-<ts> <wt_head>` creation guarded by that check. Capture the block top to `evidence/preserve_guard.txt`.
> 2. **Fail-safe bias is correct** — preservation is SKIPPED only when HEAD is unreadable OR the ancestor check cleanly returns 0 (already landed); ALL other outcomes (non-zero, error, unresolvable `main`) create the branch. Confirm by reading the branch logic. Capture to `evidence/failsafe_bias.txt`.
> 3. **Destroy/recreate unchanged** — the existing `worktree remove --force` → `shutil.rmtree` → `worktree prune` → `worktree add ... HEAD --detach` sequence is byte-unchanged and still runs after the preserve step. Capture to `evidence/recreate_unchanged.txt`.
> 4. **Out-of-scope code untouched** — `git --no-pager diff -- bellows.py` shows changes confined to the inside-top of the `if os.path.exists(wt_path):` block in `_create_worktree`; `_teardown_worktree`, `_consume_verdicts`, and the recreate line are byte-unchanged. Capture the diff scope to `evidence/diff_scope.txt`.
> 5. **Three regression tests exist** — grep `tests/test_worktree.py` for `test_stranded_cleanup_preserves_unlanded_commits`, `test_stranded_cleanup_no_preserve_when_already_landed`, `test_stranded_cleanup_failsafe_preserves_when_main_unresolvable` → all three present. Capture to `evidence/new_tests_grep.txt`.
> 6. **Dev log complete** — the dev log exists with guard placement (before/after), predicate, fail-safe rules, branch naming, pre-edit verification, both pytest runs. Capture filesize + first/last 5 lines to `evidence/dev_log_check.txt`.
>
> Any ❌ blocks plan close — report to CEO.
>
> **Test execution.** Run the full suite: `python3 -m pytest tests/ -v 2>&1 | tail -200`. Capture to `evidence/pytest_full.txt`. Verify: (a) all three new tests appear in verbose output and PASS; (b) ZERO NEW failures beyond the carry-over present in DEV's pre-edit baseline; (c) total pass count == DEV's reported post-edit number.
>
> **Specificity check (no spurious branches).** Confirm `test_stranded_cleanup_no_preserve_when_already_landed` proves an already-landed worktree creates NO `bellows-preserved/*` branch — read its assertions. Capture to `evidence/no_spurious_branch.txt`.
>
> **Branch-leak check.** Confirm the new tests clean up the `bellows-preserved/*` branches they create (no leakage into other tests / no reliance on a dirty global branch namespace). Note the cleanup mechanism in the QA report.
>
> **Rule 20 self-check** — run the canonical Rule 20 self-check from `RULE_20_SELF_CHECK_BLOCK.md` at governance root. Values: `plan_slug` = `executable-preserve-unlanded-commits-on-stranded-cleanup-2026-06-01`; `qa_report_path` = `bellows/knowledge/qa/preserve-unlanded-commits-on-stranded-cleanup-2026-06-01.md`; `evidence_dir` = `bellows/knowledge/qa/evidence/preserve-unlanded-commits-on-stranded-cleanup-2026-06-01/`; `required_evidence_files` = `["preserve_guard.txt", "failsafe_bias.txt", "recreate_unchanged.txt", "diff_scope.txt", "new_tests_grep.txt", "dev_log_check.txt", "pytest_full.txt", "no_spurious_branch.txt"]`. Include literal stdout in the QA report. If FAILED, halt — report to CEO.
>
> **Final:** Update `bellows/PROJECT_STATUS.md` — prepend a 2026-06-01 entry under Completed for "Preserve un-landed worktree commits on stranded-cleanup — branch before destroy (Gap 2a)" with a one-paragraph summary, using `Filesystem:edit_file` (find the existing topmost Completed entry as anchor and insert immediately before it).
>
> **DAEMON RESTART REMINDER — put in the QA deposit under "Flags for CEO":** "REMINDER: restart the Bellows daemon to activate the preserve guard. The running daemon executed this plan with pre-edit `_create_worktree`; the guard activates on the next plan dispatched after restart. Also owed: capture this plan's organic Opus baseline (turns/wall) from the step logs for the Opus↔Sonnet A/B."
>
> **Commit:** stage `knowledge/qa/preserve-unlanded-commits-on-stranded-cleanup-2026-06-01.md`, the `knowledge/qa/evidence/preserve-unlanded-commits-on-stranded-cleanup-2026-06-01/` evidence files, and `PROJECT_STATUS.md` with message `qa(bellows): preserve-unlanded-commits-on-stranded-cleanup verified — branch-before-destroy, fail-safe bias, no spurious branches, zero new regressions (Gap 2a)`. **DO NOT push to origin** — the Planner handles session-wrap commits.
>
> **Standard prompt feedback protocol** → append an entry to `knowledge/research/agent-prompt-feedback.md`. Second commit: `docs: prompt feedback — bellows QA preserve-unlanded-commits-on-stranded-cleanup`. **DO NOT push.**
>
> **Deposits:**
> - `bellows/knowledge/qa/preserve-unlanded-commits-on-stranded-cleanup-2026-06-01.md`
> - `bellows/knowledge/qa/evidence/preserve-unlanded-commits-on-stranded-cleanup-2026-06-01/`
> - `bellows/PROJECT_STATUS.md` (modified)
> - `bellows/knowledge/research/agent-prompt-feedback.md`
