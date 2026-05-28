# Bellows — Worktree Teardown Dirty-Tree Pre-Check (ship)
**Date:** 2026-05-27 | **Tier:** Medium | **Dispatch Mode:** bellows | **Test Scope:** targeted | **Execution:** Step 1 (DEV) → Step 2 (QA) | **qa_steps:** 2 | **pause_for_verdict:** always | **auto_close:** false

## Execution Map

Step 1 (DEV) → Step 2 (QA). Sequential. DEV ships the pre-check + evidence string + 3 new tests in `_teardown_worktree`; QA verifies behavior, evidence-string content, and adjacent-suite green.

Surface reference: `knowledge/research/worktree-teardown-dirty-tree-precheck-surface-2026-05-27.md` (SA diagnostic, 2026-05-27).

CEO-locked decisions (do not re-open):
- Dirty scope: any uncommitted change (`git status --porcelain` non-empty) → pause.
- Gate name: `worktree_teardown_dirty_tree` in the failure dict (NOT a new `_pause_reason` enum; flows through existing `WorktreeTeardownError` → `gate_failure` path).
- Recovery: inline literal commands in the evidence string, both sub-variants, plus LESSONS.md 2026-05-27 pointer.
- `git status --porcelain` self-failure: **fail-open** (treat as clean, proceed to cherry-pick; existing path catches truly-bad state).
- Rule 25 routing-table update: NOT in scope this plan (BACKLOG follow-up).

## STEP 1 — Developer (DEV)

> **FIRST — before anything else, claim this plan:** rename `executable-worktree-teardown-dirty-tree-precheck-2026-05-27.md` to `in-progress-executable-worktree-teardown-dirty-tree-precheck-2026-05-27.md` via `mv` in the worktree. **THEN immediately post a 1-2 sentence chat message confirming the claim and stating your next action** (liveness anchor). **AFTER that:** read `bellows/agents/BELLOWS_DEVELOPER.md` first, then `knowledge/research/worktree-teardown-dirty-tree-precheck-surface-2026-05-27.md` (the SA surface map — your implementation spec).
>
> Implement a pre-cherry-pick dirty-tree check in `_teardown_worktree` (`bellows.py`).
>
> **Production change (bellows.py, ~line 855, between index.lock cleanup at line 853 and the cherry-pick loop at line 856):**
>
> Insert a dirty-tree check that runs `git --no-pager status --porcelain` with `cwd=project_path` (the main checkout — NOT `wt_path`), `capture_output=True, text=True, timeout=10`.
>
> - **fail-open:** if the subprocess raises or returns non-zero, log a warning and proceed to the cherry-pick loop (do NOT raise). Only a successful `git status` with non-empty `stdout.strip()` triggers the pause.
> - **dirty predicate:** `result.returncode == 0 and result.stdout.strip()` non-empty.
> - **on dirty:** raise `WorktreeTeardownError` with the evidence string below. Do NOT attempt any cherry-pick.
>
> **Evidence string** (build exactly as the SA spec'd, Section 3 — gate name `worktree_teardown_dirty_tree`, dirty-file listing truncated to 10 lines, both recovery sub-variants, LESSONS.md 2026-05-27 pointer). Use the SA's proposed string literal verbatim as the starting point; adjust only to match surrounding code style (f-string interpolation of `project_path` and the truncated dirty output).
>
> The raised `WorktreeTeardownError` propagates to the existing caller sites (bellows.py:521-525 mid-plan, :614-618 final-step, :643-658 auto-close), which already convert it to a `gate_failure` pause with `{"gate": "worktree_teardown", "evidence": str(e)}`. **Override the gate name** at those sites — or, simpler and preferred, ensure the evidence string itself leads with `worktree_teardown_dirty_tree:` so the distinct code is visible in the verdict request without touching the three caller sites. Confirm in your log which approach you took and why.
>
> **Tests (tests/test_bellows.py, 3 new):**
>
> 1. `test_teardown_pauses_when_local_main_dirty` — `fake_subprocess_run` returns non-empty `git status --porcelain` ONLY when `cwd == project_path` (clean for `wt_path`). Assert `WorktreeTeardownError` raised; assert NO cherry-pick subprocess call made; assert error message contains `worktree_teardown_dirty_tree`.
> 2. `test_teardown_proceeds_when_local_main_clean` — `git status --porcelain` returns empty stdout. Assert no raise; assert cherry-pick proceeds.
> 3. `test_teardown_dirty_tree_evidence_contains_recovery_commands` — dirty output `" M PROJECT_STATUS.md\n?? untracked.md"`. Catch the error; assert string contains `worktree_teardown_dirty_tree`, `Sub-variant A`, `Sub-variant B`, `LESSONS.md 2026-05-27`, and `PROJECT_STATUS.md`.
>
> Also add a fail-open test if low-cost: `test_teardown_proceeds_when_git_status_errors` — `git status` returns non-zero or raises; assert no `WorktreeTeardownError` from the pre-check, cherry-pick attempted.
>
> **Existing-test check:** verify `test_teardown_worktree_removes_stale_index_lock`, `test_teardown_worktree_waits_for_fresh_index_lock`, `test_teardown_worktree_force_removes_orphaned_directory` still pass — their `fake_subprocess_run` returns `stdout=""` (clean), which the pre-check treats as clean. If any fixture returns non-empty stdout for `git status --porcelain`, patch it to return clean for that specific command. `test_run_plan_pauses_on_cherry_pick_conflict` patches the whole function — no change.
>
> **Run the targeted suite:** `python3 -m pytest tests/test_bellows.py -k "teardown" -q` plus the 3 new tests. Report pass/fail counts and timing.
>
> **Deposits:**
> - `bellows.py` (modified — pre-check + evidence string)
> - `tests/test_bellows.py` (modified — 3-4 new tests)
>
> Commit with message `feat: worktree teardown dirty-tree pre-check (worktree_teardown_dirty_tree gate)`. Do NOT push. **Pause for verdict.** Do NOT advance to QA. Do NOT move plan to Done/.

## STEP 2 — QA

> **FIRST — claim handoff:** post a 1-2 sentence chat message confirming you are starting QA on this plan and your first action (liveness anchor). **THEN:** read `bellows/agents/BELLOWS_QA.md` first, then the SA surface map at `knowledge/research/worktree-teardown-dirty-tree-precheck-surface-2026-05-27.md`, then the DEV's commit diff.
>
> Verify the dirty-tree pre-check ship against the SA spec.
>
> **Verification checklist (report each as a status row):**
>
> 1. **Pre-check location** — confirm the `git status --porcelain` check sits before the cherry-pick loop and runs with `cwd=project_path` (NOT `wt_path`). A wrong-cwd implementation checks the worktree, not main — this is the primary regression risk. Inspect the diff.
> 2. **fail-open** — confirm a `git status` error/non-zero does NOT raise `WorktreeTeardownError` from the pre-check (proceeds to cherry-pick). Confirm a successful non-empty result DOES raise.
> 3. **Gate name visible** — confirm `worktree_teardown_dirty_tree` appears in the evidence string and would surface in the verdict request (trace the evidence through to the failure dict at one caller site).
> 4. **Evidence content** — confirm the evidence string contains: dirty-file listing (with 10-line truncation logic), both recovery sub-variants (A untracked, B bookkeeping), and the `LESSONS.md 2026-05-27` pointer.
> 5. **New tests present and green** — run `python3 -m pytest tests/test_bellows.py -k "teardown" -q`. Confirm the 3 (or 4) new tests exist and pass. Report counts + timing.
> 6. **No cherry-pick on dirty** — confirm `test_teardown_pauses_when_local_main_dirty` asserts the cherry-pick subprocess is never called when the tree is dirty.
> 7. **Existing teardown tests green** — confirm no regressions in the four existing teardown tests.
> 8. **Adjacent suite** — run the broader `python3 -m pytest tests/test_bellows.py -q` and report total pass/fail/timing. Flag any failure not attributable to this change.
>
> **Rule 20 self-check block** (mandatory — emit verbatim banner):
> ```
> RULE 20 SELF-CHECK: <PASSED|FAILED>
> - All checklist rows have explicit status: <yes/no>
> - Positive-status rows use {✅, OK, PASS, [x], done, complete, verified}: <yes/no>
> - Test counts reported with timing: <yes/no>
> - Any deviation from SA spec flagged: <yes/no>
> ```
>
> **Deposits:**
> - `knowledge/qa/executable-worktree-teardown-dirty-tree-precheck-2026-05-27.md` (QA report — 8-row checklist + Rule 20 banner)
>
> Commit with message `qa: worktree teardown dirty-tree pre-check verification`. Do NOT push. **Pause for verdict.** Do NOT move plan to Done/.
