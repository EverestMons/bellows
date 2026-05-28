**Project:** bellows | **Date:** 2026-05-27 | **Author:** Planner | **Total Steps:** 1 | **Pause for Verdict:** always | **Dispatch Mode:** bellows | **Auto Close:** false

# Diagnostic — Worktree Teardown Dirty-Tree Pre-Check

## Context

The 2026-05-22 BACKLOG entry `Worktree teardown cherry-pick conflict on dirty PROJECT_STATUS.md (sequential-Planner-edit variant)` describes a failure mode where `_teardown_worktree`'s cherry-pick onto local main aborts when the local working tree has uncommitted state that would be overwritten by the merge. The entry lists three resolution shapes; **option (b)** is `teardown detects dirty working tree before attempting cherry-pick and produces a clearer pause-for-CEO with explicit recovery instructions, rather than the cryptic cherry-pick conflict surfaced today`, estimated `~20 LOC pre-cherry-pick dirty-tree check`.

Second occurrence reproduced 2026-05-27 (session 11 R2 recovery on untracked claim-rename variant). Threshold met for shipping option (b).

This diagnostic maps the surface required to ship option (b) in a follow-on executable plan. It does **not** ship code. It characterizes the cherry-pick site, identifies the pre-check insertion point, proposes the pause-message format, and enumerates the test surface.

## STEP 1 — Systems Analyst characterization (SA)

> **FIRST — before doing anything else, claim this plan:** rename `diagnostic-worktree-teardown-dirty-tree-precheck-2026-05-27.md` to `in-progress-diagnostic-worktree-teardown-dirty-tree-precheck-2026-05-27.md` using `mv` in the worktree. **THEN, immediately and BEFORE any other reads or work: post a short visible message to chat (1-2 sentences) confirming you have claimed the plan and stating your immediate next action.** This is a liveness anchor — prior SA blueprint attempts hung in silent reading phases past the 600s threshold. **AFTER posting confirmation:** read `bellows/agents/BELLOWS_SYSTEMS_ANALYST.md` first, then read the files listed below.
>
> Acting as the Bellows Systems Analyst, characterize the surface required to ship a pre-cherry-pick dirty-tree check in `_teardown_worktree` that produces a clear pause-for-CEO instead of the cryptic cherry-pick conflict the current code path surfaces.
>
> **Files to read (post a 1-line "Read X." acknowledgment after each):**
>
> 1. `bellows/agents/BELLOWS_SYSTEMS_ANALYST.md` — specialist scope.
> 2. `bellows/bellows.py` — locate `_teardown_worktree` function and its caller(s) in `run_plan`. Read the cherry-pick subprocess call, the surrounding pause-construction code, and the existing `worktree_teardown_failed` failure path.
> 3. `bellows/gates.py` — locate any existing dirty-tree detection helpers if present (grep for `git status`, `porcelain`, `dirty`).
> 4. `bellows/verdict.py` — locate `post_verdict_request` to confirm the dict shape for `gate_result["failures"]` entries (`{"gate": str, "evidence": str}` per 2026-05-03 commit `272fbe4`).
> 5. `bellows/tests/test_bellows.py` — find existing tests for `_teardown_worktree` and the cherry-pick conflict pause (`test_run_plan_pauses_on_cherry_pick_conflict` is the historical hook).
> 6. The 2026-05-22 BACKLOG entry text from `bellows/knowledge/BACKLOG.md` (the entry starting `Added 2026-05-22: Worktree teardown cherry-pick conflict on dirty PROJECT_STATUS.md (sequential-Planner-edit variant)`) — re-read the three resolution shape options and the recovery commands listed.
>
> **Post a 1-line "Drafting Section N." marker at the start of each section below.**
>
> **Section 1 — Cherry-pick call site map.** Identify the line number(s) in `bellows.py` where `_teardown_worktree` runs the cherry-pick. List the surrounding code: pre-cherry-pick subprocess calls (e.g., the `git log HEAD --not main` enumeration from the 2026-05-10 multi-SHA confirmation), the cherry-pick subprocess call itself, the error-handling branch that constructs the `worktree_teardown_failed` failure dict, and the path that flows into `verdict.post_verdict_request`. Cite line numbers verbatim from current code.
>
> **Section 2 — Pre-check insertion point.** Identify the exact line where a `git status --porcelain` dirty-tree check should be inserted. The check should run **before** any cherry-pick attempt. State the cwd context (worktree path vs. project path vs. main checkout path) the check should run in — the dirty-tree check is about **local main's working tree**, not the worktree, so cwd matters. Specify the subprocess shape: `subprocess.run(["git", "status", "--porcelain"], cwd=<path>, capture_output=True, text=True)`. State the predicate: dirty if `result.stdout.strip()` is non-empty.
>
> **Section 3 — Pause-message format proposal.** Per CEO decisions locked at plan-author time (recorded here for SA reference, not for re-debate):
> - **Dirty-detection scope:** option (1a) — any uncommitted change in working tree (`git status --porcelain` returns anything). Conservative; halts even on dirty files that wouldn't conflict with the cherry-pick. False-positive cost is one CEO decision per occurrence; false-negative cost is the cryptic cherry-pick conflict we're closing.
> - **Pause Reason Code:** option (2a) — new code `worktree_teardown_dirty_tree`. Requires a follow-on PLANNER_TEMPLATE governance edit to Rule 25 routing table (filed in BACKLOG or shipped as companion plan in the same session).
> - **Recovery-instructions content:** option (3a) — inline literal commands in the pause message body, referencing the R2 recovery shape from LESSONS.md 2026-05-27.
>
> Propose the exact `evidence` string format for the failure dict. The evidence string should include:
> - The new Pause Reason Code (`worktree_teardown_dirty_tree`).
> - A 1-line statement of the cause ("local main has uncommitted changes that would conflict with cherry-pick from worktree").
> - The output of `git status --porcelain` (truncated to ~10 lines if longer) so the CEO sees exactly which files are dirty.
> - The R2 inline recovery commands (untracked-artifact sub-variant and dirty-bookkeeping-file sub-variant — both, since the pre-check doesn't distinguish; let CEO route).
> - A pointer to LESSONS.md 2026-05-27 entry on the R2 recovery shape.
>
> Render the proposed evidence string as a multi-line string literal. Aim for under 30 lines total; the CEO reads this in the verdict request.
>
> **Section 4 — Test surface enumeration.** Enumerate the new tests needed in `tests/test_bellows.py`:
> 1. `test_teardown_pauses_when_local_main_dirty` — happy-path negative: dirty tree → pre-check fires → `worktree_teardown_dirty_tree` pause, no cherry-pick attempted.
> 2. `test_teardown_proceeds_when_local_main_clean` — happy-path positive: clean tree → pre-check passes → cherry-pick attempted normally.
> 3. `test_teardown_dirty_tree_evidence_contains_recovery_commands` — verify the evidence string contains the R2 recovery commands and the LESSONS pointer.
> 4. Any existing test that needs an update because of the new pre-check (likely `test_run_plan_pauses_on_cherry_pick_conflict` — the cherry-pick-conflict path is no longer the first failure mode for dirty-tree cases; specify whether the existing test needs a fixture change to bypass the pre-check or whether it remains valid for the post-pre-check-clean cherry-pick-conflict path).
>
> Estimate LOC for each test (target: each test ~10-15 LOC; suite delta ~40-50 LOC).
>
> **Section 5 — Edge cases and risks.** Enumerate:
> 1. **Race window:** the dirty-tree check runs at time T; the cherry-pick runs at time T+ε. If something modifies the working tree between T and T+ε, the pre-check is moot. Estimate the race window in real terms; recommend whether to mitigate (e.g., re-check immediately before cherry-pick) or accept.
> 2. **Worktree-vs-main cwd confusion:** the pre-check must run against the **main checkout** working tree, not the worktree. Confirm the cwd parameter passed to the subprocess and the test fixture that catches a wrong-cwd regression.
> 3. **Submodule dirty state:** `git status --porcelain` includes submodule pointer changes. The governance root has bellows + anvil as submodules; a dirty submodule pointer at main triggers the pre-check. Recommend: accept (the pre-check should fire; submodule pointer drift IS a teardown risk).
> 4. **Bellows-self plan dispatch:** when the project being torn down is bellows itself (Bellows-self mode), the main checkout and worktree may overlap. State whether the pre-check applies to Bellows-self or needs a sentinel-skip.
> 5. **Existing teardown failures unrelated to dirty tree:** state how the new pre-check interacts with other teardown failure paths (cherry-pick conflict on shared bookkeeping files per the parallel-diagnostic 2026-05-22 BACKLOG entry; `git worktree remove --force` failures; etc.). The pre-check should be additive, not replacing.
>
> **Section 6 — LOC estimate.** Total LOC estimate for the follow-on executable plan, broken down: production code in `bellows.py` (~LOC), test code in `tests/test_bellows.py` (~LOC), any helper extracted into a shared location (~LOC if any). BACKLOG entry estimated `~20 LOC pre-cherry-pick dirty-tree check` for production; verify or refute that estimate with your characterization.
>
> **Section 7 — Open questions for the Planner.** List any CEO-decision items that the diagnostic surfaces but does not resolve. Three pre-locked decisions are listed in Section 3 (do not re-open). Anything NEW that the characterization surfaces — file here.
>
> **Deposits:**
> - `bellows/knowledge/research/worktree-teardown-dirty-tree-precheck-surface-2026-05-27.md`
>
> The deposit is a single markdown file with the seven sections above. After writing, commit with message `diag: worktree teardown dirty-tree pre-check surface (2026-05-27)`. Do NOT push — Planner handles push at session-wrap.
>
> **Pause for verdict at end of step.** Do NOT auto-advance. Do NOT move plan to Done/. Do NOT push.

## Rule 20 — QA Self-Check Block

This step is SA-only; no QA agent runs. The Rule 20 self-check block is N/A for this step. Verification happens at the Planner's Rule 22 substance check after verdict consumption.
