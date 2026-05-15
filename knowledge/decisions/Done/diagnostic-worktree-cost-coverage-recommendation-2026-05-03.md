# Bellows — Worktree vs. Serialize-Capture Cost-vs-Coverage Recommendation
**Date:** 2026-05-03 | **Tier:** Diagnostic | **Test Scope:** targeted | **Execution:** Step 1 (BELLOWS SYSTEMS ANALYST)

## How to Run This Plan

Paste the bootstrap prompt into Claude Code. The agent reads the plan file and executes Step 1. After completing Step 1, the agent STOPS and waits for CEO confirmation. The Planner moves the plan to Done after Rule 22 verification passes.

**Bootstrap prompt:**
```
Read the plan at bellows/knowledge/decisions/diagnostic-worktree-cost-coverage-recommendation-2026-05-03.md. Execute Step 1. After completing, STOP and wait for my confirmation. Do NOT move the plan to Done.
```

**Background context (read before executing):** This is the third and final diagnostic in the parallel-collision investigation chain:

1. `diagnostic-parallel-scope-check-collision-2026-05-03` — established the literal contamination vector via incident reconstruction
2. `diagnostic-worktree-implementation-surface-2026-05-03` — produced the implementation surface map (Phase A1–A8)
3. `diagnostic-worktree-candidate-designs-2026-05-03` — produced complete designs for worktree and serialize-capture candidates (D1–D8 each), rejected three novel candidates with structural reasoning

**This plan's task:** produce a ranked cost-vs-coverage recommendation, an implementation plan structure proposal, and explicit open questions for CEO. The substantive design work is already done — the SA in this step does NOT redesign candidates. It compares them against a structured matrix and produces a single ranked recommendation that the Planner can use to author the implementation plan.

**CEO decisions already locked (do NOT re-evaluate):**
- Worktree location: in-tree `<project>/.bellows-worktrees/<slug>/` (CEO accepted SA recommendation, contradicting initial `/tmp/` preference)
- Worktree scope: always-worktree (every plan dispatch creates a worktree, not just `parallel-N-` group plans)
- Don't-fix is excluded as a candidate (CEO direction from the first diagnostic chain)

**The implementation plan itself is a future risk vector worth surfacing:** any implementation plan that fixes the parallel-collision bug will also be subject to the parallel-collision bug during its own QA step (since the daemon is still pre-fix code at close time). Recent Bellows fixes have hit this pattern repeatedly (LESSONS.md 2026-04-19). The SA should account for this in rollout-risk dimension.

---
---

## STEP 1 — BELLOWS SYSTEMS ANALYST

---

> **STOP REMINDER (TOP):** This plan has ONE step. Complete it, then STOP and wait for CEO confirmation. Do NOT move the plan to Done — the Planner performs the terminal move after Rule 22 verification passes.
>
> **FIRST — before doing anything else, claim this plan:** `import shutil; shutil.move("bellows/knowledge/decisions/diagnostic-worktree-cost-coverage-recommendation-2026-05-03.md", "bellows/knowledge/decisions/in-progress-diagnostic-worktree-cost-coverage-recommendation-2026-05-03.md")`.
>
> **Required reads (in order):**
>
> 1. Your specialist file: `bellows/agents/BELLOWS_SYSTEMS_ANALYST.md`. Skip glossary read.
> 2. Candidate designs (the substrate for this recommendation): `bellows/knowledge/research/worktree-candidate-designs-2026-05-03.md` — complete D1–D8 specs for both worktree and serialize-capture candidates, plus the rejected-novel-candidates section.
> 3. Surface map (referenced by D2 in the candidate designs): `bellows/knowledge/research/worktree-implementation-surface-2026-05-03.md` — eight phases of code-path traces with literal line numbers. Skim this for context; do not re-derive.
> 4. Incident timeline (the literal vector both candidates must defeat): `bellows/knowledge/research/parallel-collision-incident-timeline-2026-05-03.md` — Phase 1A reconstruction.
>
> You are the Bellows Systems Analyst. **Task: produce a ranked cost-vs-coverage recommendation comparing per-plan git worktree (in-tree, always-worktree scope) against serialize-capture (per-project mutex). Do NOT redesign candidates. Do NOT propose new candidates. Do NOT modify production code. Compare what's already designed and produce the ranked recommendation.**
>
> **Step 1A — Cost-vs-coverage matrix.** Build a side-by-side table comparing the two candidates across these dimensions. Cite specific D-section evidence from the candidate-designs deposit for each cell.
>
> | Dimension | Worktree | Serialize-Capture |
> |-----------|----------|-------------------|
> | Total LOC (production) | (cite D2) | (cite D2) |
> | Total LOC (new tests) | (cite D7) | (cite D7) |
> | Files modified in `bellows.py` | (cite D2) | (cite D2) |
> | New helper functions | (cite D2) | (cite D2) |
> | Coverage % of 7 contamination sub-vectors | (cite D5, count Solved / Partial / N/A) | (cite D5) |
> | Number of new failure modes | (cite D6 row count) | (cite D6 row count) |
> | Likely-Catastrophic failure modes | (cite D6, count Likely + Catastrophic) | (cite D6) |
> | Wall-clock overhead per plan (sequential dispatch) | (cite D3f) | (cite D3a + D3d) |
> | Wall-clock overhead per parallel-3 group | (cite D3f and parallelism preservation) | (cite D3d, parallelism collapse) |
> | Reversibility cost (revert if shipped + broken) | (judgment: how many commits, complexity of revert) | (judgment) |
> | Implementation rollout risk under parallel-collision bug | (consider: implementation plan's own QA step is subject to the bug being fixed) | (consider same) |
> | Interaction with future Bellows infrastructure | (consider: terminal output redesign, notification audit, future verdict mechanization) | (consider same) |
>
> **Step 1B — Parallel commit usage analysis.** The serialize-capture candidate's primary cost is parallelism collapse — `parallel-N-` group plans no longer execute concurrently when committing. Quantify this cost honestly:
>
> - Read `bellows/knowledge/decisions/Done/` and count how many `parallel-N-` plans have been dispatched historically. Use `Filesystem:list_directory` on the Done/ directory and count filenames matching the pattern `parallel-\d+-`.
> - Of those, how many were `executable-` (committed code) vs. `diagnostic-` (read-only)? The parallel-N- pattern is unsafe for committing per the open BACKLOG entry — but past plans may have committed anyway and produced the false-positive scope_check failures.
> - Express the wall-clock cost of serialize-capture as a function of expected future parallel-commit usage. Example framing: "If you dispatch N parallel-commit groups per month at average step time T, serialize-capture adds (N-1) × T wall-clock per group versus worktree." Pick a realistic N range (0–10/month based on historical data) and produce a concrete time-budget delta in minutes per month.
>
> **Step 1C — Rollout risk under unfixed bug.** This is a meta-cost dimension specific to this fix. The implementation plan that ships either candidate will itself be subject to the parallel-collision bug during its own QA step (since the daemon is still pre-fix code until restart). Surface this risk for both candidates:
>
> - For worktree: the implementation plan's QA step modifies `bellows.py`. If the implementation plan dispatches alongside ANY other plan in the bellows project, the QA step may trip the very bug it's fixing. Estimate the probability and propose mitigations (e.g., dispatch the implementation plan during a quiet window, halt all other bellows plans during dispatch, ship as a sequential plan with manual restart between steps).
> - For serialize-capture: same exposure but differently shaped. The implementation plan modifies `bellows.py`. Until restart, the existing code (no mutex) runs. After restart, the new code (mutex) runs. The implementation plan itself doesn't NEED concurrent dispatch to be at risk — the bug only fires when something else is concurrent. If only the implementation plan is running at dispatch time, the bug is silent.
>
> **Step 1D — Recommendation.** Pick exactly ONE recommendation shape. Cite the cost-vs-coverage matrix and Step 1B+1C analysis as evidence. Do NOT hedge with "consider both" or "either is acceptable" — pick one with rationale.
>
> 1. **Ship worktree as designed.** Cite specifically: which dimensions favor worktree, what's the marginal cost over serialize-capture, why the marginal cost is justified.
> 2. **Ship serialize-capture as designed.** Cite specifically: which dimensions favor serialize-capture, what coverage/parallelism trade-offs are acceptable, what the residual concerns are.
> 3. **Ship serialize-capture first as a low-cost partial mitigation, then worktree as a follow-up plan.** Cite specifically: what staging buys (e.g., faster correctness ship + observation period before larger change), what the carrying cost of running serialize-capture is in the interim.
> 4. **Reject both designed candidates and re-investigate.** Cite specifically what the next diagnostic must explore and why neither candidate clears the bar. (This is the "actually we missed something" outcome — uncomfortable but valid.)
>
> The recommendation must be ranked by total-cost-divided-by-coverage, not by any single dimension. If the recommendation contradicts a CEO-locked decision (in-tree location, always-worktree scope, don't-fix excluded), state so explicitly with rationale — but the SA must not override locked decisions, only surface contradictions for CEO review.
>
> **Step 1E — Implementation plan structure proposal.** For the recommended candidate, propose the structure of the implementation plan the Planner will author next:
>
> - **Tier:** Small / Medium / Large with rationale (cite D2 file count, LOC).
> - **Step structure:** Number of steps, agent assignments per step, what each step produces. Account for the multi-step parsing bug (BACKLOG 2026-05-03) — the implementation plan should likely be authored as separate single-step plans for now, OR include explicit guidance on how to structure if the parser bug is fixed first.
> - **Test scope:** targeted / full-suite / both, with rationale (cite D7 test surface).
> - **Live smoke test placement:** Per D8 in the candidate designs, both candidates recommended canary as a separate post-implementation diagnostic. Confirm or contest, citing rollout-risk evidence from Step 1C.
> - **Specialist file syncs needed before dispatch:** Surface map A7 documented Bellows test files and surface; if the recommended candidate requires new specialist-file claims (e.g., "Bellows Developer's specialist file mentions worktrees" or "the test surface section in the SA specialist file is updated"), flag it.
> - **Pre-implementation prerequisites:** Are there any prep plans that must ship first? Examples: BACKLOG 2026-05-03 multi-step parsing bug fix (would unblock multi-step implementation plans), `git worktree prune` startup hook (D3g for worktree), gitignore update (in-tree worktree).
>
> **Step 1F — Open questions for CEO.** Surface every decision the recommendation defers to the CEO. Each must include the SA's lean with rationale citing specific evidence — the CEO accepts or contests, but does not invent the answer from scratch. Examples (illustrative, not exhaustive):
>
> - "Should the implementation halt the plan on cherry-pick merge conflict, or attempt automatic conflict resolution?"
> - "Should worktrees be torn down on Bellows shutdown, or persisted across restarts for crash recovery?"
> - "Should the gitignore update be a separate plan that ships before the implementation plan, or bundled into Step 1 of the implementation plan?"
> - "Should the smoke test canary be authored now (so it's ready for post-restart dispatch) or after the implementation plan ships?"
>
> Cap at 5 open questions. If you have more than 5, prioritize the highest-impact ones and flag the rest in a final paragraph. The CEO has limited bandwidth — open questions should be load-bearing decisions, not minor implementation details.
>
> **Constraints:**
> - Do NOT modify production code. Do NOT redesign candidates. Do NOT propose novel approaches not in the candidate-designs deposit (those were already evaluated and rejected).
> - The CEO has locked: in-tree worktree location, always-worktree scope, don't-fix excluded. Do NOT re-evaluate these decisions. If the cost-vs-coverage matrix surfaces evidence that a locked decision is suboptimal, flag it as an open question — do NOT silently choose differently.
> - Reasoning that does not cite the candidate-designs deposit or the surface map is rejected. Every claim in the matrix must reference a specific D-section or Phase-A observation.
> - Do NOT author the implementation plan itself. The Planner does that after this recommendation lands and Rule 22 verification passes.
>
> **Output format:** Single deposit file with six sections (1A through 1F). Use tables for 1A. Use prose-with-citations for 1B–1F. Final section is the open-questions list.
>
> Standard prompt feedback protocol → `bellows/knowledge/research/agent-prompt-feedback.md`.
>
> **Deposits:**
> - `bellows/knowledge/research/worktree-cost-coverage-recommendation-2026-05-03.md`
>
> **STOP REMINDER (BOTTOM):** Step 1 is COMPLETE when the deposit file is written with all six sections (1A through 1F). Do NOT move the plan to Done. Do NOT begin authoring the implementation plan — that is Planner work. The Planner reads this deposit, verifies it via Rule 22, and authors the implementation plan as a separate executable plan after CEO acceptance. Wait for CEO confirmation before any further action.
