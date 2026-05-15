# Bellows — Worktree vs. Serialize-Capture Candidate Designs
**Date:** 2026-05-03 | **Tier:** Diagnostic | **Test Scope:** targeted | **Execution:** Step 1 (BELLOWS SYSTEMS ANALYST)

## How to Run This Plan

Paste the bootstrap prompt into Claude Code. The agent reads the plan file and executes Step 1. After completing Step 1, the agent STOPS and waits for CEO confirmation. The Planner moves the plan to Done after Rule 22 verification passes.

**Bootstrap prompt:**
```
Read the plan at bellows/knowledge/decisions/diagnostic-worktree-candidate-designs-2026-05-03.md. Execute Step 1. After completing, STOP and wait for my confirmation. Do NOT move the plan to Done.
```

**Background context (read before executing):** This is the second of three follow-up plans to the prior diagnostic `diagnostic-parallel-scope-check-collision-2026-05-03` (the one whose Phase 1A timeline established the literal contamination vector). The prior plan `diagnostic-worktree-implementation-surface-2026-05-03` (closed today) produced an exhaustive surface map of every code path any fix candidate would touch. This plan builds on that surface map: produce complete implementation designs for the two surviving candidates (worktree and serialize-capture), walk each through the 2026-04-30 incident timeline with literal answers, enumerate failure modes and test surface. The third plan in the chain will produce the cost-vs-coverage recommendation. **Why three separate plans instead of one three-step plan:** Bellows currently mis-counts step headers and reports multi-step plans as 1-step (BACKLOG 2026-05-03). Workaround in effect until the parser bug is fixed.

**The candidate space is partially settled:** Phase A8 of the surface map confirmed PID-filtering candidate (e) is not feasible on macOS-with-SIP — `psutil`, `dtrace`, `fs_usage`, `lsof` all eliminated. Phase A1 + A3 + A5 also surfaced that mutex-around-`_capture_git_diff`-alone is structurally insufficient because contamination occurs during the entire pre-diff → run_step → post-diff window. This means the serialize-capture candidate must wrap the full window, which has parallelism implications. The SA evaluates worktree and serialize-capture (with the full-window constraint) as the two real candidates. If during the design walk a genuinely novel third approach surfaces (one not in the prior diagnostic's enumeration), include it — but do not invent third candidates for completeness.

---
---

## STEP 1 — BELLOWS SYSTEMS ANALYST

---

> **STOP REMINDER (TOP):** This plan has ONE step. Complete it, then STOP and wait for CEO confirmation. Do NOT move the plan to Done — the Planner performs the terminal move after Rule 22 verification passes.
>
> **FIRST — before doing anything else, claim this plan:** `import shutil; shutil.move("bellows/knowledge/decisions/diagnostic-worktree-candidate-designs-2026-05-03.md", "bellows/knowledge/decisions/in-progress-diagnostic-worktree-candidate-designs-2026-05-03.md")`.
>
> **Required reads (in order):**
>
> 1. Your specialist file: `bellows/agents/BELLOWS_SYSTEMS_ANALYST.md`. Skip glossary read.
> 2. Surface map (the substrate for this design): `bellows/knowledge/research/worktree-implementation-surface-2026-05-03.md` — eight phases (A1–A8) with literal line numbers and code excerpts. Every design decision in your deposit must cite a specific Phase A observation.
> 3. Incident timeline (the literal vector your designs must defeat): `bellows/knowledge/research/parallel-collision-incident-timeline-2026-05-03.md` — Phase 1A reconstructs the 2026-04-30 incident with timestamps and contamination evidence.
>
> You are the Bellows Systems Analyst. **Task: produce complete implementation designs for two candidate fixes (worktree, serialize-capture) walking each end-to-end through the 2026-04-30 incident timeline. No "TBD," no "agent decides," no hedging — every design decision is made here with explicit rationale citing the surface map.**
>
> **Candidate scope.** Evaluate THESE TWO candidates: **(1) per-plan git worktree** — every plan dispatch creates a worktree (always-worktree per CEO direction), `claude -p` runs with `cwd=worktree`, worktree commits merged back to main checkout, uncommitted changes copy-back, worktree torn down post-step; **(2) serialize git capture** — wrap the ENTIRE pre-diff → run_step → post-diff window in a global mutex (Phase A1+A3+A5 confirms wrapping `_capture_git_diff` alone is insufficient), serializing parallel-plan step execution at the git-state-observation level. **If during your design walk you surface a genuinely novel third approach** (per-thread `GIT_INDEX_FILE` env var, `git stash` isolation, reflog-based filtering, or anything else not in the prior diagnostic's candidate list), include it as candidate (3). Do NOT invent third candidates for completeness — only include if substantively viable.
>
> **Per-candidate design — answer ALL of these for EACH candidate:**
>
> **(D1) Mechanism.** What does the fix do mechanically? One paragraph, no jargon, no abstraction.
>
> **(D2) Code change surface.** Cite Phase A directly. Table format: `File | Function | Existing line range (from Phase A) | Change type (modify/add/delete) | New behavior in 2-3 sentences`. Every row must reference a specific Phase A line range or call-site identifier.
>
> **(D3) Specific design decisions, with rationale.** For worktree, answer:
> - **(a) Worktree location.** CEO has expressed preference for `/tmp/bellows-wt-<slug>` per SA recommendation. Phase A6 documented `.gitignore` state. Cite specific trade-offs: `/tmp/` semantics (macOS clears on reboot, separate mount may break git's hardlinking of objects) vs. in-tree `<project>/.bellows-worktrees/<slug>/` (same filesystem, gitignore needed). State whether you confirm `/tmp/` or recommend in-tree, with rationale citing Phase A4 (shared state) and Phase A6 (gitignore patterns). If you contradict CEO preference, say so explicitly.
> - **(b) Branch strategy and merge-back.** Three options: cherry-pick worktree commits onto main, per-plan branch + fast-forward/rebase, detached HEAD with cherry-pick on cleanup. Pick one with rationale citing Phase A3 (lifecycle) and concurrent-cherry-pick conflict semantics.
> - **(c) Uncommitted change handling.** Three options: copy back to main checkout, auto-commit before merge-back, block cleanup if uncommitted. Pick one with rationale citing Phase A3 lifecycle and the diagnostic-agent pattern of depositing findings without committing.
> - **(d) `.bellows-cache` access.** Phase A4 says `.bellows-cache/` is at absolute path. Worktrees at `/tmp/` or `<project>/.bellows-worktrees/` — what does the agent see when reading `.bellows-cache/<slug>.pristine` from inside the worktree? Cite Phase A4. Confirm whether this works without modification or whether a copy/symlink is needed.
> - **(e) `bellows.db` access.** Same question as (d). Phase A4 says absolute path. Confirm whether worktree-internal git operations affect the main checkout's bellows.db.
> - **(f) Always-worktree overhead.** CEO confirmed always-worktree (every plan, not just parallel groups). Estimate `git worktree add` + `git worktree remove` time per plan dispatch. Compare against current per-plan overhead. State whether the overhead is acceptable for sequential plans.
> - **(g) Failure modes during creation.** What if `git worktree add` fails (disk full, locked git index, branch already checked out elsewhere)? Cite Phase A3 and propose handling.
>
> For serialize-capture, answer:
> - **(a) Mutex placement.** The Phase A1 + A3 + A5 finding says `_capture_git_diff`-alone serialization is insufficient. Where is the mutex acquired? Cite the line numbers. The mutex must wrap pre-diff → run_step → post-diff. Released when?
> - **(b) Lock granularity.** Global single mutex, per-project mutex, per-step mutex? Cite Phase A4 (each project has its own working tree) and Phase A5 (threading model).
> - **(c) Deadlock analysis.** Given Phase A5's threading model (daemon threads, no joining, `_active_lock`), can the new mutex deadlock with existing locks? Under what conditions? Cite specific call paths.
> - **(d) Parallelism collapse.** If the mutex wraps the full pre-diff → run_step → post-diff window, parallel siblings ARE NOT parallel — they execute serially. Confirm explicitly: under serialize-capture, does the `parallel-N-` group prefix retain any execution-parallelism benefit, or does it become a no-op for grouping? Cite Phase A5.
> - **(e) Mutex timeout behavior.** Does the mutex have a timeout? What happens if a step holds the mutex for the full step_inactivity_timeout (1800s per current config)? Cite Phase A2 timeout handling.
>
> **(D4) Phase 1A literal walk-through.** Take the 2026-04-30 incident verbatim:
> - 15:44:22 — B (backlog-hygiene-sweep) dispatched
> - 15:44:46 — A (deposit-exists) dispatched
> - 15:44:48 — C (ledger-pause-reason-code) dispatched as `parallel-1` group with A
> - 15:44:48–15:47:14 — C edits `bellows.py`, `verdict.py`, `tests/test_verdict.py` in shared working tree
> - 15:46:15 — A commits its own files (`gates.py`, `tests/test_gates.py`)
> - ~15:46:21 — A's `post_diff` captured
> - 15:46:21 — B commits its own files
> - ~15:46:27 — B's `post_diff` captured
> - 15:47:14 — C commits its files
> - ~15:47:20 — C's `post_diff` captured
>
> With THIS candidate live, what does each plan's `files_changed` contain at its post_diff capture moment? Answer literally — list the exact file paths. Three answers per candidate (A, B, C). If any answer for a victim plan includes a sibling's files, the candidate is structurally insufficient for the literal incident vector — state so explicitly and STOP THE WALK FOR THAT CANDIDATE.
>
> **(D5) Coverage matrix.** Enumerate the seven contamination sub-vectors and mark whether THIS candidate solves each: (i) sibling's uncommitted dirty files appear in victim's post_diff, (ii) sibling's just-committed files appear in victim's post_diff between commit and end-of-diff-window, (iii) sibling's `git add`-staged-but-uncommitted files, (iv) parallel-group concurrent commits, (v) sequential-but-concurrent-dispatch (Plan B's case — not in a parallel group but dispatched while A and C were running), (vi) test-suite parallel runs that touch shared fixtures, (vii) Bellows internal writes during a step (e.g., db updates by another thread). For each: Solved / Not Solved / Partial / N/A, with one-sentence explanation citing Phase A or D4 evidence.
>
> **(D6) New failure modes.** What can go wrong with THIS candidate that doesn't go wrong today? Enumerate at least five concrete scenarios with classification: Likely / Unlikely / Catastrophic / Recoverable. Examples: worktree creation fails due to disk full, mutex deadlock under N concurrent dispatches, `.bellows-cache` not found from worktree, agent's pytest run can't find tests because of cwd shift, merge conflict on cherry-pick, uncommitted dev-log lost on worktree teardown, mutex timeout expiring mid-step.
>
> **(D7) Test surface.** File-level test surface needed (do NOT write actual tests). For each test file from Phase A7's inventory: existing tests that need updates (with line range estimates) and new tests required (with one-sentence descriptions). Be specific: which existing tests' mocks need adjusting because the function signature changes? Which new tests assert worktree creation/teardown? Which assert mutex acquisition? Cite Phase A7.
>
> **(D8) Live smoke test design (per candidate).** Describe a controlled live reproduction that would falsify THIS candidate if it didn't work. Two `parallel-99-` plans dispatched simultaneously, each writing and committing distinct files at known times. Specify the two plans' shapes (what they write, when they sleep, when they commit) such that the timing GUARANTEES the contamination would occur in unfixed code. **Recommend whether the canary should run as part of the implementation plan's QA, run as a separate post-implementation diagnostic, or be skipped — citing Phase A1+A3+A5 evidence about whether a live canary inside an active Bellows-dispatched diagnostic is structurally awkward (the prior diagnostic skipped its canary on these grounds).**
>
> **Constraints:**
> - Do NOT produce a cost-vs-coverage recommendation. That work is the THIRD plan in this chain (which the Planner authors after this deposit lands and Rule 22 verification passes). The deliverable here is the design specifications only — complete and decision-ready.
> - Do NOT modify production code. Do NOT recommend an implementation plan structure. Do NOT pick a winner between candidates.
> - Reasoning that does not cite the surface map is rejected. Every design decision must be anchored to a specific Phase A1-A8 observation.
> - If the surface map is incomplete for any decision (e.g., A4 doesn't cover a shared resource you need to evaluate), flag it back and stop — do NOT fill in with assumptions.
> - The CEO's preferences are not binding. CEO has expressed preference for `/tmp/` worktree location and always-worktree scope. If your Phase A analysis makes either non-optimal, surface the contradiction with rationale rather than rubber-stamp the preference.
>
> **Output format:** Single deposit file with two (or three, if you surface a novel candidate) candidate sections. Each candidate has its eight subsections (D1–D8). Use code blocks for code references. Use tables for D2 (code change surface) and D5 (coverage matrix).
>
> Standard prompt feedback protocol → `bellows/knowledge/research/agent-prompt-feedback.md`.
>
> **Deposits:**
> - `bellows/knowledge/research/worktree-candidate-designs-2026-05-03.md`
>
> **STOP REMINDER (BOTTOM):** Step 1 is COMPLETE when the deposit file is written with all (D1)–(D8) sections per candidate. Do NOT produce a cost-vs-coverage recommendation. Do NOT move the plan to Done. The Planner reads this deposit, verifies it via Rule 22, and authors the third diagnostic (cost-vs-coverage) as a separate plan. Wait for CEO confirmation before any further action.
