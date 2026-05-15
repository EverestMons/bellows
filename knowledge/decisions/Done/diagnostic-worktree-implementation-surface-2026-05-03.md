# Bellows — Worktree Implementation Surface + Candidate Re-evaluation Diagnostic
**Date:** 2026-05-03 | **Tier:** Diagnostic | **Test Scope:** targeted | **Execution:** Step 1 (BELLOWS DEVELOPER) → Step 2 (BELLOWS SYSTEMS ANALYST) → Step 3 (BELLOWS SYSTEMS ANALYST)

## How to Run This Plan

Paste the bootstrap prompt into Claude Code. The agent reads the full plan file and executes Step 1 ONLY. After completing Step 1, the agent STOPS and waits for CEO confirmation ("ok") before proceeding to Step 2. **CRITICAL: subsequent step prompts exist in this plan file. Read them only as reference for prior-step verification anchors. DO NOT execute Step 2 or Step 3 work during Step 1's execution window. The Planner will dispatch Step 2 separately after CEO confirmation. The agent must never auto-chain steps.**

**Bootstrap prompt:**
```
Read the plan at bellows/knowledge/decisions/diagnostic-worktree-implementation-surface-2026-05-03.md. Execute Step 1 ONLY. After completing Step 1, STOP and wait for my confirmation. Do NOT proceed to Step 2 or Step 3. Do NOT move the plan to Done.
```

**Background context (read before Step 1):** The 2026-05-03 prior diagnostic (`bellows/knowledge/research/parallel-collision-incident-timeline-2026-05-03.md` + `parallel-collision-candidate-evaluation-2026-05-03.md`) established the contamination vector with literal evidence and recommended candidate (d) per-plan git worktree. CEO accepted the recommendation in principle, but during implementation-plan authoring three open design questions surfaced (worktree location, branch/merge strategy, uncommitted-change handling) that the diagnostic's "fix shape" sketch did not resolve. Additionally, a fifth candidate — **serialize git capture via mutex around `_capture_git_diff`** — was raised post-diagnostic and not evaluated in the prior pass. This diagnostic is a design-tier follow-up: it produces an implementation-ready specification by mapping the surface area, evaluating candidates (worktree + serialize + any fifth candidate the SA surfaces), and producing a cost-vs-coverage recommendation. The Planner then authors the implementation plan from this design.

**Why three steps:** The recurring failure mode in this bug class is "candidate evaluated against categorization, not against literal incident behavior." Three separate confirmable steps force the Planner (Layer 3) to verify each phase's output against the literal Phase 1A timeline before the next phase builds on it. Step 1 (DEV) maps the implementation surface — every line of `bellows.py`, `runner.py`, `gates.py`, `verdict.py`, `bellows.db` interaction that ANY fix candidate would touch. Step 2 (SA) designs each candidate against that surface with literal answers to "what does plan A's `files_changed` contain after this fix is live?" Step 3 (SA, same agent, separate confirmation) produces the cost-vs-coverage recommendation ranked by total-cost-divided-by-coverage.

---
---

## STEP 1 — BELLOWS DEVELOPER

---

> **STOP REMINDER (TOP):** This step is implementation surface mapping ONLY. Do NOT design fixes. Do NOT evaluate candidates. Do NOT execute Step 2 or Step 3 work even though their prompts exist below in this plan file. After completing this step, STOP and wait for CEO confirmation.
>
> **FIRST — before doing anything else, claim this plan:** `import shutil; shutil.move("bellows/knowledge/decisions/diagnostic-worktree-implementation-surface-2026-05-03.md", "bellows/knowledge/decisions/in-progress-diagnostic-worktree-implementation-surface-2026-05-03.md")`.
>
> You are the Bellows Developer. Read your specialist file at `bellows/agents/BELLOWS_DEVELOPER.md` first. Skip glossary read — Bellows has no domain glossary; this is code-path tracing. **Task: produce a complete implementation surface map for Bellows's git-state-observation infrastructure.** This is the substrate Step 2's candidate design will walk across. The surface map must be exhaustive — any code path touched by any fix candidate (worktree, serialize-capture, `git stash`, per-thread `GIT_INDEX_FILE`, reflog filtering, or any fifth approach the SA may surface) needs literal line-number documentation here.
>
> **Phase A1 — `_capture_git_diff` and `_parse_diff_stat` complete trace.** In `bellows/bellows.py`, locate `_capture_git_diff` and `_parse_diff_stat`. For each: (a) function definition with line number range, (b) every call site with line numbers and surrounding context (3 lines before and after), (c) all parameters and return values with type annotations if present, (d) the exact subprocess argv and `cwd` value, (e) what happens on subprocess timeout / non-zero exit / git error (does it raise, return empty, log?), (f) any threading or concurrency primitives currently in use (locks, semaphores, mutex). Document as a self-contained reference section with code excerpts.
>
> **Phase A2 — `runner.run_step` cwd handling.** In `bellows/runner.py`, locate `run_step`. Document: (a) the function signature with all parameters and defaults, (b) where `cwd` is determined (passed in? derived? hardcoded?), (c) the exact `subprocess.Popen` (or equivalent) call with all kwargs, (d) how the `claude -p` subprocess inherits filesystem state from its parent (does it run in `project_path`? a different directory?), (e) PID exposure — is the subprocess PID returned to the caller, accessible via the Popen object, or unavailable, (f) timeout and stream handling. This determines whether candidate (e) PID-filtering is feasible at the runner level (the prior diagnostic dismissed it on OS API grounds, but PID exposure within the runner is a separate question).
>
> **Phase A3 — `run_plan` dispatch lifecycle.** In `bellows/bellows.py`, locate `run_plan`. Document the full step-execution sequence with line numbers: (a) plan claim (filename rename to `in-progress-`), (b) `pre_diff` capture, (c) `runner.run_step` invocation, (d) `post_diff` capture, (e) `_parse_diff_stat` call, (f) `gates.check` call, (g) verdict request creation if paused, (h) the loop structure for multi-step plans. For each, note any per-thread state, any shared state across threads, and any global mutable state. Specifically identify: where in the lifecycle could a worktree be created and torn down without breaking the plan-claim contract? Where could a mutex around `_capture_git_diff` be inserted without deadlocking concurrent dispatches?
>
> **Phase A4 — Shared state inventory.** Enumerate every shared resource that concurrent plan dispatches read or write: (a) `bellows.db` — what tables, what writes happen during a step, what's the connection lifecycle, (b) `.bellows-cache/<slug>.pristine` — read by whom, written when, accessed via absolute path or relative, (c) `verdicts/pending/` and `verdicts/resolved/` — written by whom, read by `_consume_verdicts`, (d) the project's `.git/` directory — what git operations happen during a step (the subprocess `git diff --stat`, agent commits via `claude -p`, anything else?), (e) the project's working tree — agent file writes, agent commits, Bellows reads. For each, identify: would a per-plan worktree need its own copy, share with the main checkout, or access via absolute path?
>
> **Phase A5 — Threading and parallel-group dispatch.** Locate `handle_parallel_group` and the `_pending_groups` settle-window logic in `bellows.py`. Document: (a) how parallel siblings are dispatched (threads vs. processes), (b) thread lifecycle (daemon, joined, abandoned), (c) the 2-second stagger purpose and effects, (d) what state each thread holds privately vs. shares globally, (e) where in the dispatch sequence is the right place to inject per-plan isolation (worktree creation, mutex acquisition, etc.). Identify whether the existing threading model can support per-thread state (e.g., thread-local storage for a worktree path) or whether it would require additional infrastructure.
>
> **Phase A6 — Existing `.gitignore` state.** Read `bellows/.gitignore` (and project-root `.gitignore` if a separate one exists). Document existing patterns. Specifically: (a) is `.bellows-cache/` already gitignored, (b) is `.bellows-worktrees/` gitignored or would it need to be added, (c) is `/tmp/` referenced anywhere relevant, (d) what's the pattern for "directory inside project that should not be tracked." This informs the worktree-location decision in Step 2.
>
> **Phase A7 — Existing test surface.** In `bellows/tests/`, identify every test that touches `_capture_git_diff`, `_parse_diff_stat`, `runner.run_step`, `run_plan`, parallel-group dispatch, or scope_check. List each test file with line ranges and a one-line description of what it tests. This is the regression surface that ANY fix must keep passing. Note any test that currently DEPENDS on the shared-working-tree behavior (i.e., tests that would need to be updated, not just kept passing, when the fix lands).
>
> **Phase A8 — Open question: PID exposure feasibility.** The prior diagnostic eliminated candidate (e) PID-filtering on OS-API grounds (fsevents/inotify don't expose PID at user privilege). But that's the OS-watcher angle. A different angle: does Python's `subprocess.Popen` give us the `claude -p` PID? If yes, can we use that PID with `psutil` or `/proc` polling to attribute file writes? On macOS, can `dtrace` (which DOES support PID filtering) be invoked from a non-root user under any common configuration? Document feasibility briefly — this is a sanity check, not a full re-evaluation. If candidate (e) is reopenable on these grounds, flag for SA in Step 2.
>
> **Constraints:** Do NOT design fixes. Do NOT recommend candidates. Do NOT propose mutex placements or worktree locations as recommendations — only as observations of where they COULD be inserted. Do NOT modify any production code. Do NOT write tests. Do NOT dispatch a canary. Surface mapping only — the design happens in Step 2. Use `git --no-pager` for any git command. Cite line numbers for every observation; "around line 200" is not acceptable, neither is "in `run_plan`" without a line range. If any code surface is ambiguous (e.g., a function that's been refactored across versions), document the ambiguity rather than picking one interpretation.
>
> **Output format:** Single deposit file with eight sections (Phase A1 through A8). Each section is self-contained reference material. Use code blocks for excerpts. Use tables where appropriate (e.g., for call-site enumeration, shared state, test surface). End with a one-paragraph "Summary of Surface" section listing every code path the SA needs to walk through in Step 2.
>
> Standard prompt feedback protocol → `bellows/knowledge/research/agent-prompt-feedback.md`.
>
> **Deposits:**
> - `bellows/knowledge/research/worktree-implementation-surface-2026-05-03.md`
>
> **STOP REMINDER (BOTTOM):** Step 1 is COMPLETE when the deposit file is written. Do NOT execute Step 2 or Step 3. Do NOT design fixes. Do NOT move the plan to Done. The Planner will read this deposit, verify it via Rule 22, and dispatch Step 2 separately. Wait for CEO confirmation before any further action.

---
---

## STEP 2 — BELLOWS SYSTEMS ANALYST

---

> Before starting, read `bellows/knowledge/research/worktree-implementation-surface-2026-05-03.md` and check the Output Receipt status. If status is not Complete, stop and report the issue to the CEO before proceeding. Then read `bellows/knowledge/research/parallel-collision-incident-timeline-2026-05-03.md` (the prior diagnostic's Phase 1A timeline) — your candidate evaluations must walk through that timeline literally.
>
> **STOP REMINDER (TOP):** This step is candidate design ONLY. Do NOT produce the cost-vs-coverage recommendation — that is Step 3's work. Do NOT execute Step 3 even though its prompt exists below. After completing this step, STOP and wait for CEO confirmation.
>
> You are the Bellows Systems Analyst. Read your specialist file at `bellows/agents/BELLOWS_SYSTEMS_ANALYST.md` first. Skip glossary read. **Task: produce complete implementation designs for THREE candidate fixes, walking each end-to-end through the 2026-04-30 incident timeline with literal answers to falsifiability questions.** No "TBD," no "agent decides," no hedging — every design decision is made here with explicit rationale citing Step 1's surface map.
>
> **Candidate scope.** Evaluate THESE THREE candidates at minimum: **(1) per-plan git worktree** — create a worktree per plan dispatch, run `claude -p` with `cwd=worktree`, merge worktree commits back to main checkout, copy uncommitted changes back, tear down worktree; **(2) serialize git capture** — wrap `_capture_git_diff` in a global mutex so only one thread captures at a time, but DO NOT change the underlying `git diff --stat` mechanism; **(3) any fifth approach you surface during the design walk** — the prior diagnostic enumerated four candidates from the BACKLOG; if the surface map reveals a sixth or seventh option (per-thread `GIT_INDEX_FILE`, `git stash` isolation, reflog filtering, dtrace-based PID filtering if Phase A8 surfaced feasibility, or anything else), include it as a third candidate. If you cannot surface a third candidate after deliberate consideration, state so explicitly and proceed with two.
>
> **Per-candidate design — answer ALL of these for EACH candidate:**
>
> **(D1) Mechanism.** What does the fix do mechanically? In one paragraph, no jargon, no abstraction.
>
> **(D2) Code change surface.** Cite Step 1's surface map directly. List every function modified with line ranges, every new function added, every call site changed. Format: a table with columns `File | Function | Existing line range | Change type (modify/add/delete) | New behavior in 2-3 sentences`. If the surface map shows the function doesn't exist or has been refactored, state so — do not invent.
>
> **(D3) Specific design decisions, with rationale.** For worktree specifically, answer: (a) where do worktrees live (`/tmp/`, in-tree `.bellows-worktrees/`, elsewhere)? Cite trade-offs from Phase A4 (shared state) and Phase A6 (gitignore). (b) Branch strategy and merge-back: cherry-pick onto main, per-plan branch + fast-forward, detached HEAD with cherry-pick on cleanup, or other? Cite trade-offs including concurrent-cherry-pick conflicts. (c) Uncommitted change handling: copy back, auto-commit, block cleanup, or other? Cite the Phase A3 lifecycle. (d) `.bellows-cache` access: does the worktree share the main checkout's `.bellows-cache`, copy it, or work without it? (e) `bellows.db` access: same question. (f) Always-worktree vs. parallel-only: per CEO decision (always-worktree confirmed), document the per-step overhead and any plans where worktree creation could fail (e.g., disk space, locked git index). For serialize-capture specifically, answer: (a) where is the mutex acquired and released — line-level placement? (b) Lock granularity — global single mutex, per-project mutex, per-step mutex? (c) Deadlock analysis — given Phase A5's threading model, can the mutex deadlock? Under what conditions? (d) What concurrent operations are NOT serialized — agent file writes, agent commits, etc. — and how do those interact with the captured diff?
>
> **(D4) Phase 1A literal walk-through.** Take the 2026-04-30 incident as Phase 1A documents it: B dispatched at 15:44:22, A dispatched at 15:44:46, C dispatched at 15:44:48. C edits `bellows.py`, `verdict.py`, `tests/test_verdict.py` between 15:44:48 and 15:47:14. A's `post_diff` captured at ~15:46:21. With THIS candidate live, what does Plan A's `files_changed` contain at 15:46:21? Answer literally — list the files. If the answer includes any of C's files, the candidate is structurally insufficient for the literal incident vector — state so explicitly. Do the same for Plan B's `post_diff` at 15:46:27. Do the same for Plan C's `post_diff` at 15:47:20. Three answers per candidate.
>
> **(D5) Coverage matrix.** Enumerate every contamination sub-vector and mark whether THIS candidate solves it: (i) sibling's uncommitted dirty files appear in victim's `post_diff`, (ii) sibling's just-committed files appear in victim's `post_diff` between commit and end-of-diff-window, (iii) sibling's `git add`-staged-but-uncommitted files, (iv) parallel-group concurrent commits, (v) sequential-but-concurrent-dispatch (Plan B's case — not in a parallel group but dispatched while A and C were running), (vi) test-suite parallel runs that touch shared fixtures, (vii) Bellows internal writes during a step (e.g., db updates by another thread). For each, mark Solved / Not Solved / Partial / N/A and explain in one sentence.
>
> **(D6) New failure modes.** What can go wrong with THIS candidate that doesn't go wrong today? Enumerate at least five concrete scenarios. Examples: worktree creation fails due to disk full, mutex deadlock under N concurrent dispatches, `.bellows-cache` not found from worktree, agent's pytest run can't find tests because of cwd shift, merge conflict on cherry-pick. For each, classify as Likely / Unlikely / Catastrophic / Recoverable.
>
> **(D7) Test surface.** File-level test surface needed (do NOT write actual tests). For each test file: existing tests that need updates (with line range estimates) and new tests required (with one-sentence descriptions). Cite Phase A7's existing test inventory.
>
> **(D8) Live smoke test design (per candidate).** Describe a controlled live reproduction that would falsify the fix if it didn't work. Two `parallel-99-` plans dispatched simultaneously, each writing and committing distinct files at known times. The smoke captures the verdict requests and verifies plan A's `files_changed` does NOT contain plan B's files. Specify the two plans' shapes (what they write, when they sleep, when they commit) such that the timing GUARANTEES the contamination would occur in the unfixed code. **Recommend whether the canary should run as part of the implementation plan's QA, run as a separate post-implementation diagnostic, or be skipped — citing Phase A1-A5 evidence about whether a live canary inside an active Bellows-dispatched diagnostic is awkward (the prior diagnostic skipped its canary on these grounds).**
>
> **Constraints:** Do NOT produce the cost-vs-coverage recommendation — that is Step 3's work. Do NOT modify production code. Do NOT recommend an implementation plan structure. The deliverable is the design specifications for each candidate, complete and decision-ready. Reasoning that does not cite Step 1's surface map is rejected — every design decision must be anchored to a specific Phase A1-A8 observation. If the surface map is incomplete for any decision, flag it back and stop — do NOT fill in with assumptions.
>
> Standard prompt feedback protocol → `bellows/knowledge/research/agent-prompt-feedback.md`.
>
> **Deposits:**
> - `bellows/knowledge/research/worktree-candidate-designs-2026-05-03.md`
>
> **STOP REMINDER (BOTTOM):** Step 2 is COMPLETE when the deposit file is written with all (D1)–(D8) sections per candidate. Do NOT execute Step 3. Do NOT produce the cost-vs-coverage recommendation. Do NOT move the plan to Done. The Planner will read this deposit, verify it via Rule 22, and dispatch Step 3 separately. Wait for CEO confirmation before any further action.

---
---

## STEP 3 — BELLOWS SYSTEMS ANALYST

---

> Before starting, read `bellows/knowledge/research/worktree-candidate-designs-2026-05-03.md` and check the Output Receipt status. If status is not Complete, stop and report the issue to the CEO before proceeding. Read your specialist file at `bellows/agents/BELLOWS_SYSTEMS_ANALYST.md` first. Skip glossary read.
>
> **STOP REMINDER (TOP):** This step is the cost-vs-coverage recommendation ONLY. Do NOT redesign candidates. Do NOT modify production code. Do NOT begin implementation. After completing this step, STOP and wait for CEO confirmation. The Planner moves the plan to Done after Rule 22 verification.
>
> You are the Bellows Systems Analyst. **Task: produce a single ranked recommendation for which candidate to implement, with rationale ranked by total-cost-divided-by-coverage.**
>
> **Step 3A — Cost-vs-coverage matrix.** Build a side-by-side table comparing every candidate from Step 2 across these dimensions: (a) total LOC (production + tests), (b) number of files modified, (c) number of new failure modes (from D6 counts), (d) coverage % of the seven contamination sub-vectors from D5 (e.g., "5/7 = 71%"), (e) implementation rollout risk (subjective: Low/Medium/High with rationale), (f) reversibility cost — if shipped and broken, how hard is it to revert (Low/Medium/High with rationale), (g) interaction with existing Bellows infrastructure — does the candidate change observable behavior for the Planner, Pushover notifications, terminal output, or any user-facing surface?
>
> **Step 3B — Recommendation.** Pick ONE of these four recommendation shapes: (1) **Ship candidate X as designed in Step 2.** Cite which candidate and why it wins on cost-vs-coverage. (2) **Ship candidate X first as a low-cost partial mitigation, then candidate Y as a follow-up plan.** Cite which two candidates and why staging beats shipping the higher-cost one outright. (3) **Reject all designed candidates and re-investigate.** Cite specifically what the next diagnostic must explore and why none of Step 2's candidates clears the bar. (4) **Surface a hybrid** — combine elements of two or more candidates into a fifth approach not in Step 2's design. If choosing this, deliver a complete design for the hybrid (D1–D8 from Step 2's format) inline.
>
> **Step 3C — Implementation plan structure.** For the recommended shape, propose the IMPLEMENTATION PLAN STRUCTURE the Planner should author next. Specifically: (a) tier (Small/Medium/Large), (b) step count and per-step agent assignments, (c) test scope (targeted/full-suite/both), (d) whether the canary smoke from D8 belongs as a step in this plan or as a separate post-restart Phase 2 plan, (e) any specialist-file syncs needed before the implementation plan dispatches (the surface map may reveal stale specialist-file claims). Do NOT author the implementation plan itself — that's Planner work. Recommend its shape only.
>
> **Step 3D — Open questions for CEO.** Surface every decision that the recommendation defers to the CEO. Examples: "Should the implementation halt the plan on a worktree merge conflict, or attempt automatic conflict resolution?" "Should the mutex have a timeout, and if so, what's the timeout behavior on expiry?" Each open question must include the SA's lean with rationale, citing specific Step 1 or Step 2 evidence — the CEO accepts or contests, but does not invent the answer from scratch.
>
> **Constraints:** Do NOT modify production code. Do NOT author the implementation plan. Do NOT skip the cost-vs-coverage matrix in favor of prose argumentation — the matrix is the load-bearing artifact. The recommendation must be ranked by total-cost-divided-by-coverage, not by any single dimension. If the recommendation contradicts the prior diagnostic's worktree recommendation, state so explicitly with rationale — do not paper over the disagreement. The CEO has stated a preference for worktree (always-worktree scope) and `/tmp/` location; if Step 2's findings make either of those non-optimal, surface the contradiction rather than rubber-stamp the preference.
>
> Standard prompt feedback protocol → `bellows/knowledge/research/agent-prompt-feedback.md`.
>
> **Deposits:**
> - `bellows/knowledge/research/worktree-cost-coverage-recommendation-2026-05-03.md`
>
> **STOP.** Do NOT move this plan to Done/. Per the disable-auto-close model, the Planner performs the terminal move after Rule 22 verification passes.
