# Bellows — Worktree & Dirty-Tree Pre-Check Hardening (ship)
**Date:** 2026-05-29 | **Tier:** Small | **Dispatch Mode:** bellows | **Test Scope:** full-suite | **Execution:** Step 1 (DEV) → Step 2 (QA) | **qa_steps:** 2 | **pause_for_verdict:** always | **auto_close:** false

## Execution Map

Step 1 (DEV) → Step 2 (QA). Sequential. DEV ships three independent hardening changes in `bellows.py` (stranded-worktree cleanup in `_create_worktree`; `rstrip()` + lifecycle-artifact leading-space tolerance in the dirty-tree pre-check; `.bellows-worktrees/` lifecycle-ignore coverage) plus regression tests for each. QA verifies each change independently, confirms the three pre-existing `test_worktree.py` failures flip green, and confirms zero new full-suite regressions.

## CEO Context

Batch close of three confirmed-Open Bellows BACKLOG items, all in the worktree-teardown / dirty-tree-pre-check subsystem of `bellows.py`. They are small, independent, and share one daemon-restart activation window — bundled to amortize a single restart. Source-of-truth for fix shapes is the BACKLOG entries themselves (no separate diagnostic: each entry carries reproduction, root cause, fix site, precedent, and safety analysis). Line numbers in the BACKLOG are approximate (the file has changed since the entries were authored); the DEV step's Pre-edit verification locates each site by symbol, not line number.

**Item (a) — BACKLOG 2026-05-29 (session 18): `_create_worktree` does not clean stranded worktrees from prior failed dispatches.** When `_teardown_worktree` raises (real dirty tree, cherry-pick conflict, any reason), the worktree directory at `.bellows-worktrees/<slug>/` is left intact; the verdict-driven retry calls `_create_worktree` → `git worktree add` against the same path → `fatal: '<path>' already exists` → a fresh `worktree_creation` gate failure on every retry, requiring manual `git worktree remove --force` + `git worktree prune` before the next retry can succeed. Fix: at the top of `_create_worktree` (after the `parent_dir` mkdir, before `git worktree add`), if `wt_path` already exists, clean it before re-creating: run `git worktree remove --force <wt_path>` (capture failure silently — the path may not be a registered worktree), then `shutil.rmtree(wt_path, ignore_errors=True)` as belt-and-suspenders, then `git worktree prune` to clean metadata; log a WARN when a stranded worktree is found ("⚠ stranded worktree found at <path>, removing before re-creation"). Precedent to mirror: `Bellows.__init__` already runs `git worktree prune` on startup for orphan cleanup. Safety: Bellows-managed worktrees never carry uncommitted user work that would be lost — anything in them was either cherry-picked back to main on teardown, or the dispatch never completed (in which case the worktree state is by definition stale). The startup-prune already operates on this assumption; this applies the same assumption at retry time.

**Item (f) — BACKLOG 2026-05-28 (session 14): dirty-tree pre-check `strip()` mishandles space-prefixed porcelain status codes.** The pre-check's `git status --porcelain` result is processed with `.strip()`, which strips the leading space from the first porcelain line when its status code starts with a space (` D foo.md`, ` M foo.md`); `_is_lifecycle_artifact()` then fails to recognize that first line as a lifecycle artifact even when it would otherwise match. Direction is safe (false-strict — the filter over-blocks, never under-blocks), but it is a hole in the filter spec. Fix: change the `.strip()` at the pre-check result site to `.rstrip()` to preserve leading whitespace, and ensure `_is_lifecycle_artifact` tolerates a porcelain line with OR without the leading status-code space (e.g., normalize by matching the artifact path regardless of the two-column status prefix).

**Item (g) — BACKLOG 2026-05-28 (session 14): pre-check trips on `.bellows-worktrees/` in test fixtures (3 failing `test_worktree.py` tests).** The dirty-tree pre-check trips on `?? .bellows-worktrees/` when `test_worktree.py` integration tests create real git repos that include the worktrees directory; the lifecycle filter does not cover this directory-prefix path (it is not a filename-pattern artifact in `knowledge/decisions/` or `verdicts/`). Three tests fail on main: `test_teardown_removes_worktree_directory`, `test_teardown_cherry_picks_commits`, `test_teardown_copies_uncommitted_files`. **CEO-locked approach (do not re-open):** extend the lifecycle-ignore logic so any path under `.bellows-worktrees/` is treated as a lifecycle artifact by the dirty-tree pre-check — NOT the fixture-gitignore route. Rationale: a worktree directory appearing untracked in the parent repo is normal Bellows operation, never committable main-repo work; ignoring it in the dirty-tree pre-check is correct independent of whether any given repo gitignores it, and this single fix resolves both the test failures and any real-world recurrence. Safety: identical to the existing lifecycle-filter assumption — `.bellows-worktrees/` never holds work that teardown needs to preserve.

**Test scope justification:** full-suite. Item (g) flips three pre-existing `test_worktree.py` failures to green, changing the known-failing baseline; full-suite confirms the flip and zero new regressions across the worktree / pre-check / teardown surface that all three items touch. Item (a) touches `_create_worktree` (worktree integration tests). Item (f) touches the pre-check predicate path. The combined surface warrants full-suite verification.

**Daemon-restart note:** this is a Bellows-modifies-Bellows plan. The running daemon executes this plan under PRE-edit code; all three fixes activate only on the next plan dispatched AFTER a daemon restart. The DEV step's own teardown therefore still runs the old `_create_worktree` (item a's fix does not protect this plan's own teardown — if a stranded worktree collision occurs during this plan, recover manually as today). QA flags the restart for the CEO.

---
---

## STEP 1 — DEV

---

> **FIRST — before any reads or work: post a short visible message to chat (1-2 sentences) confirming you are starting this plan and stating your immediate next action.** This is the liveness anchor. Do NOT rename the plan file — Bellows already claimed it before invoking you.
>
> You are the Bellows Developer. Read your specialist file at `agents/BELLOWS_DEVELOPER.md` and `governance/GUARDRAILS.md` first. Skip glossary read — domain terminology is fully covered in the specialist file. Note: worktree root IS the bellows project root — strip the `bellows/` prefix from any path references in this prompt when running commands.
>
> **Reads (mandatory, in order):** (1) `agents/BELLOWS_DEVELOPER.md` — your specialist file; (2) the three target regions in `bellows.py`, located via the Pre-edit verification queries below (do NOT trust the BACKLOG line numbers — locate by symbol).
>
> **Pre-edit verification (Rule 39).** Before any edits, run each query and confirm the symbol exists. The BACKLOG line numbers are approximate; the file has changed since the entries were authored.
>
> 1. **Claim:** `_create_worktree` exists and invokes `git worktree add` against a path under `.bellows-worktrees/`. **Query:** `grep -n "def _create_worktree" bellows.py` then read the function body. **Expected:** one definition; a `git worktree add` invocation; a `parent_dir`/mkdir step before it.
> 2. **Claim:** `Bellows.__init__` runs `git worktree prune` on startup (the precedent to mirror for item a). **Query:** `grep -n "worktree prune" bellows.py`. **Expected:** at least one hit; confirm one is inside `__init__`.
> 3. **Claim:** the dirty-tree pre-check parses `git status --porcelain` output, filters via `_is_lifecycle_artifact` / `_LIFECYCLE_IGNORE_RE`, and applies `.strip()` to the porcelain result. **Query:** `grep -n "porcelain" bellows.py`, `grep -n "_is_lifecycle_artifact" bellows.py`, `grep -n "_LIFECYCLE_IGNORE_RE" bellows.py`, and read the pre-check block. **Expected:** a pre-check that splits porcelain lines and skips lifecycle artifacts; `_LIFECYCLE_IGNORE_RE` defined near module top; an `_is_lifecycle_artifact` predicate; a `.strip()` on the porcelain result (item f's target).
>
> If any symbol is absent or materially differs from expected, **STOP** — do not edit. Deposit a verification-mismatch report to `knowledge/flags/verification-mismatch-worktree-precheck-hardening-2026-05-29-step-1.md` (claim, expected, actual, timestamp) and report to CEO.
>
> **Task — three independent changes in `bellows.py`.**
>
> **Change 1 (item a) — stranded-worktree cleanup in `_create_worktree`.** At the top of the function, after the `parent_dir` mkdir and before `git worktree add`, insert a guard: if `wt_path` already exists on disk, clean it before re-creating. Sequence: (1) `git worktree remove --force <wt_path>` via subprocess, capturing and silently ignoring failure (the path may exist on disk without being a registered worktree); (2) `shutil.rmtree(wt_path, ignore_errors=True)` as belt-and-suspenders; (3) `git worktree prune` to clean stale metadata. Emit a WARN through the existing logger when a stranded worktree is found: `⚠ stranded worktree found at <wt_path>, removing before re-creation`. Match the subprocess/logging style of the existing `git worktree prune` call in `Bellows.__init__` (mirror its invocation pattern — same subprocess helper, same cwd, same error handling). The diff should be ~10-15 LOC.
>
> **Change 2 (item f) — `rstrip()` + leading-space tolerance in the pre-check.** At the pre-check site where the `git status --porcelain` result is processed, change `.strip()` to `.rstrip()` so leading whitespace on the first porcelain line is preserved. Then ensure `_is_lifecycle_artifact` recognizes the artifact whether or not the porcelain line carries the leading status-code space — i.e., when extracting the path from a porcelain line, account for the two-column status prefix (`XY filename`) including the space-prefixed forms (` D `, ` M `, `?? `). If `_is_lifecycle_artifact` already strips the status columns robustly, the `.rstrip()` change alone suffices; confirm by reading the predicate. Add a brief inline comment noting why `rstrip` not `strip` (preserve leading status-code space for first-line artifacts).
>
> **Change 3 (item g) — `.bellows-worktrees/` lifecycle-ignore coverage.** Extend the dirty-tree pre-check's lifecycle-ignore logic so any porcelain entry whose path is, or is under, `.bellows-worktrees/` is treated as a lifecycle artifact and skipped. Prefer extending `_LIFECYCLE_IGNORE_RE` (or `_is_lifecycle_artifact`) to match the `.bellows-worktrees/` directory prefix, consistent with how the existing regex matches `knowledge/decisions/` lifecycle paths. Do NOT modify test fixtures or add a `.gitignore` rule — the fix lives in the pre-check logic so it holds in real-world operation too. Add a regex/predicate that matches both `.bellows-worktrees` (the bare dir) and `.bellows-worktrees/<anything>`.
>
> **Regression tests (add new; do not modify existing unless a change requires it).**
>
> 1. **Item a** — in the worktree test module (`tests/test_worktree.py` or wherever `_create_worktree` is covered): add `test_create_worktree_cleans_stranded_directory` (a bare directory pre-exists at the target `wt_path` → `_create_worktree` removes it and succeeds) and `test_create_worktree_cleans_stranded_registered_worktree` (a registered worktree pre-exists at the target path → `_create_worktree` runs `worktree remove --force` + prune and succeeds). Assert the worktree is usable afterward and a WARN was logged.
> 2. **Item f** — add `test_pre_check_recognizes_space_prefixed_lifecycle_line`: construct porcelain output whose FIRST line is a space-prefixed lifecycle artifact (e.g. ` D knowledge/decisions/verdict-pending-foo.md`) and assert the pre-check treats it as a lifecycle artifact (does not raise). Pair with a negative control (a space-prefixed REAL dirty file still blocks).
> 3. **Item g** — add `test_pre_check_ignores_bellows_worktrees_dir`: porcelain output containing `?? .bellows-worktrees/` (and `?? .bellows-worktrees/some-slug/file.py`) → pre-check does not raise. Negative control: a real untracked file outside `.bellows-worktrees/` still blocks.
>
> **CRITICAL SAFETY — preserve the negative (blocking) behavior.** The three pre-existing filter-negative tests (real dirty conditions MUST still block teardown) must remain green. Do not weaken the pre-check's ability to catch genuine uncommitted work.
>
> **Test execution.** Run the full suite pre-edit and capture the baseline: `python3 -m pytest tests/ -v 2>&1 | tail -120`. Record the pass count and the exact set of pre-existing failures — you should see the three `test_worktree.py` failures (`test_teardown_removes_worktree_directory`, `test_teardown_cherry_picks_commits`, `test_teardown_copies_uncommitted_files`) plus any other carry-over (e.g. `test_run_step_timeout`). After edits, run full suite again. Expected post-edit: the three named `test_worktree.py` failures now PASS, your new regression tests PASS, and zero NEW failures appear beyond any non-worktree carry-over present in the pre-edit baseline. Capture both runs.
>
> **Anchor verification before commit.** Run and confirm: `grep -n "stranded worktree found" bellows.py` (≥1 hit — item a WARN); `grep -n "\.rstrip()" bellows.py` (the pre-check now uses rstrip — item f); `grep -n "bellows-worktrees" bellows.py` (≥1 hit in the lifecycle-ignore logic — item g); `grep -n "def _create_worktree" bellows.py` (unchanged signature).
>
> **Deposit:** author a dev log to `knowledge/development/worktree-precheck-hardening-2026-05-29.md` documenting: each of the three changes with before/after snippets (3-5 lines context each), the Pre-edit verification query results, the three new regression-test functions with their assertions, the pre-edit and post-edit full-suite pytest output (pass/fail counts + the worktree-failures-now-green confirmation), the four anchor-verification grep results, and the Output Receipt per your specialist file.
>
> **Commit:** stage `bellows.py`, the test additions, and the dev log with message `fix(bellows): worktree & dirty-tree pre-check hardening — stranded-worktree cleanup in _create_worktree, rstrip+leading-space tolerance, .bellows-worktrees/ lifecycle-ignore (BACKLOG a/f/g)`. **DO NOT push to origin** — the Planner handles session-wrap commits.
>
> **Standard prompt feedback protocol** → append an entry to `knowledge/research/agent-prompt-feedback.md`. Second commit: `docs: prompt feedback — bellows DEV worktree/pre-check hardening`. **DO NOT push.**
>
> **Deposits:**
> - `bellows/knowledge/development/worktree-precheck-hardening-2026-05-29.md`
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
> You are the Bellows QA Agent. Read your specialist file at `agents/BELLOWS_QA.md` and `governance/GUARDRAILS.md` first. Skip glossary read — domain terminology is fully covered in the specialist file. Note: worktree root IS the bellows project root — strip the `bellows/` prefix from any path references in this prompt when running commands.
>
> **Before starting, read `knowledge/development/worktree-precheck-hardening-2026-05-29.md` (DEV's Step 1 deposit) and check its Output Receipt status; if not Complete, stop and report the blocker.**
>
> **Deliverable Verification (Rule 17).** Read DEV's Output Receipt "Files Created or Modified" list. For each, verify the file exists and the declared change is present. Produce a verification table `| # | Deliverable | Expected | Status (✅/❌) | Evidence |`. Specifically:
>
> 1. **Item a — stranded-worktree cleanup present** — `_create_worktree` contains an existence guard that runs `git worktree remove --force` + `shutil.rmtree(..., ignore_errors=True)` + `git worktree prune` and logs the stranded-worktree WARN. Read the function and confirm the cleanup sits AFTER the parent-dir mkdir and BEFORE `git worktree add`. Capture the function body to `evidence/create_worktree_cleanup.txt`.
> 2. **Item a — WARN string present** — `grep -n "stranded worktree found" bellows.py` → ≥1 hit. Capture to `evidence/item_a_warn_grep.txt`.
> 3. **Item f — rstrip in pre-check** — the dirty-tree pre-check uses `.rstrip()` (not `.strip()`) on the porcelain result. `grep -n "\.rstrip()" bellows.py` and read the surrounding pre-check block. Confirm `.strip()` is no longer applied to the porcelain result at that site. Capture to `evidence/item_f_rstrip.txt`.
> 4. **Item f — leading-space tolerance** — read `_is_lifecycle_artifact` (and any path-extraction helper) and confirm a space-prefixed porcelain line (` D ...`, ` M ...`, `?? ...`) resolves to the artifact path correctly. Capture the predicate to `evidence/item_f_predicate.txt`.
> 5. **Item g — `.bellows-worktrees/` ignore** — the lifecycle-ignore logic matches `.bellows-worktrees/` (bare and with a child path). `grep -n "bellows-worktrees" bellows.py` → ≥1 hit in the ignore logic (NOT in a test fixture or a comment only). Capture to `evidence/item_g_ignore.txt`. Confirm DEV did NOT modify test fixtures or add a `.gitignore` rule for this (the fix must be in the pre-check logic): `git diff HEAD~2 HEAD --stat` (or HEAD~1 if one DEV commit) and confirm no fixture/.gitignore changes for item g. Capture to `evidence/item_g_no_fixture_change.txt`.
> 6. **Regression tests exist** — `grep -n "test_create_worktree_cleans_stranded\|test_pre_check_recognizes_space_prefixed_lifecycle_line\|test_pre_check_ignores_bellows_worktrees_dir" tests/` → expect the new test functions (≥4 total per the DEV plan). Capture to `evidence/new_tests_grep.txt`.
> 7. **Dev log complete** — `knowledge/development/worktree-precheck-hardening-2026-05-29.md` exists with three change-block sections (before/after snippets), pre-edit verification results, and both pytest runs. Verify by reading; capture filesize + first/last 5 lines to `evidence/dev_log_check.txt`.
>
> Any ❌ blocks plan close — report to CEO.
>
> **Test execution.** Run the full suite: `python3 -m pytest tests/ -v 2>&1 | tail -160`. Capture to `evidence/pytest_full.txt`. Verify ALL of: (a) the three previously-failing `test_worktree.py` tests — `test_teardown_removes_worktree_directory`, `test_teardown_cherry_picks_commits`, `test_teardown_copies_uncommitted_files` — now PASS; (b) the new regression tests appear in verbose output and all PASS; (c) zero NEW failures beyond any non-worktree carry-over (e.g. `test_run_step_timeout`) that was present in DEV's pre-edit baseline; (d) total pass count = DEV's reported post-edit number.
>
> **Structural-compliance checks.**
>
> (a) **CRITICAL SAFETY — blocking behavior preserved.** Confirm the dirty-tree pre-check still RAISES on a genuine uncommitted change. The filter-negative tests (real dirty conditions block teardown) must be green. List the filter-negative test names and their pass status. Capture to `evidence/blocking_preserved.txt`. If any filter-negative test was weakened or removed, FLAG it — this is a safety regression.
> (b) **Item a scope** — confirm item a's change is bounded to `_create_worktree` and mirrors the `Bellows.__init__` startup-prune invocation style (same subprocess helper / error handling). Capture both call sites side-by-side to `evidence/item_a_symmetry.txt`. Flag any divergence in subprocess pattern.
> (c) **Item g matches `.bellows-worktrees/` only as a directory prefix** — confirm the ignore pattern does not accidentally match unrelated paths containing the substring elsewhere (anchor to the path component). Capture the pattern to `evidence/item_g_anchor.txt`.
>
> **Rule 20 self-check** — run the canonical Rule 20 self-check from `RULE_20_SELF_CHECK_BLOCK.md` at governance root. Values: `plan_slug` = `executable-worktree-precheck-hardening-2026-05-29`; `qa_report_path` = `bellows/knowledge/qa/worktree-precheck-hardening-2026-05-29.md`; `evidence_dir` = `bellows/knowledge/qa/evidence/worktree-precheck-hardening-2026-05-29/`; `required_evidence_files` = `["create_worktree_cleanup.txt", "item_a_warn_grep.txt", "item_f_rstrip.txt", "item_f_predicate.txt", "item_g_ignore.txt", "item_g_no_fixture_change.txt", "new_tests_grep.txt", "dev_log_check.txt", "pytest_full.txt", "blocking_preserved.txt", "item_a_symmetry.txt", "item_g_anchor.txt"]`. Include literal stdout in the QA report. If FAILED, halt — report to CEO.
>
> **Final:** Update `bellows/PROJECT_STATUS.md` — prepend a 2026-05-29 entry under Completed for "Worktree & dirty-tree pre-check hardening — stranded-worktree cleanup (`_create_worktree`), rstrip + leading-space tolerance, `.bellows-worktrees/` lifecycle-ignore (BACKLOG a/f/g)" with a one-paragraph summary, using `Filesystem:edit_file` (find the existing topmost Completed entry as anchor and insert immediately before it).
>
> **DAEMON RESTART REMINDER — put in the QA deposit under "Flags for CEO":** "REMINDER: restart the Bellows daemon to activate (a) stranded-worktree cleanup in `_create_worktree`, (f) the `rstrip()` + leading-space pre-check tolerance, and (g) `.bellows-worktrees/` lifecycle-ignore. The running daemon executed this plan with pre-edit code; the three fixes activate on the next plan dispatched after restart."
>
> **Commit:** stage the QA report, evidence files, and PROJECT_STATUS update with message `qa(bellows): worktree/pre-check hardening verified — 3 prior worktree failures now green, new regression tests pass, zero new regressions, blocking behavior preserved (BACKLOG a/f/g)`. **DO NOT push to origin** — the Planner handles session-wrap commits.
>
> **Standard prompt feedback protocol** → append an entry to `knowledge/research/agent-prompt-feedback.md`. Second commit: `docs: prompt feedback — bellows QA worktree/pre-check hardening`. **DO NOT push.**
>
> **Deposits:**
> - `bellows/knowledge/qa/worktree-precheck-hardening-2026-05-29.md`
> - `bellows/knowledge/qa/evidence/worktree-precheck-hardening-2026-05-29/`
> - `bellows/PROJECT_STATUS.md` (modified)
> - `bellows/knowledge/research/agent-prompt-feedback.md`
