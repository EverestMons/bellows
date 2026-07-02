# Bellows — Reporting Phase 2: Read-Side Cycle Query Module
**Date:** 2026-07-01 | **Tier:** Medium | **Dispatch Mode:** bellows | **Test Scope:** both | **Execution:** Step 1 (SA) → Step 2 (DEV) → Step 3 (QA) | **qa_steps:** 3 | **pause_for_verdict:** after_step_1

## How to Run This Plan

Paste the bootstrap prompt into Claude Code. The agent reads the full plan file and executes Step 1 ONLY. After completing Step 1, the agent STOPS and waits for CEO confirmation ("ok") before proceeding to Step 2. This continues step by step until the plan is complete. The agent must never skip steps, auto-chain, or move the plan to Done without completing all steps including QA.

**Bootstrap prompt:**
```
Read the plan at bellows/knowledge/decisions/[plan-filename].md. Execute Step 1 ONLY. After completing Step 1, STOP and wait for my confirmation. Do NOT proceed to Step 2 or move the plan to Done.
```

---
---

## STEP 1 — SA

---

> **FIRST — before any reads or work: post a short visible message to chat (1-2 sentences) confirming you are starting this plan and stating your immediate next action.** Do NOT rename the plan file.
>
> You are the Bellows Systems Analyst. Read your specialist file at `bellows/agents/BELLOWS_SYSTEMS_ANALYST.md` first. Skip the domain glossary — this is a read-side query design task.
>
> Reporting Phase 1 shipped the lifecycle DB (`bellows/lifecycle.db`) and it now accrues complete data: `steps.cost_usd`, `steps.turns`, and `plans.plan_id` all populate correctly as of the diagnostic-6 coverage fix (commit `2df6d91`). Phase 2 is the read side: a query module that produces cycle reports from accumulated lifecycle data. Design it. Deposit a blueprint the DEV will implement in Step 2.
>
> **Design constraints, verified against the live DB — treat as authoritative, but re-confirm each against current schema at design time. (1) Timestamp-keyed, not state-keyed.** `plans.lifecycle_state` only ever holds terminal values (`closed`/`halted`/`abandoned`) — intermediate states (`claimed`/`in_progress`/`awaiting_verdict`) are defined in the CHECK constraint but NEVER written. Confirmed distribution: closed 94, halted 11, abandoned 4, zero intermediate. So any cycle query MUST window on `plans.closed_at` (full coverage: 109/109 rows populated) and MUST NOT filter or group on intermediate lifecycle_state. **(2) Counting-grain trap.** The natural throughput query joins `plans → steps` to sum per-step cost/turns, but `COUNT(*)` over that join counts STEP ROWS, not plans — a 2-step executable inflates to 2. Plan counts MUST use `COUNT(DISTINCT p.id)`; cost/turn SUMs stay over the step join. Specify exactly which aggregates are plan-grain vs step-grain in the blueprint. **(3) First cut is range-parameterized, not fixed-cycle.** No cycle-boundary state exists and none is being added. The query primitive takes an arbitrary date range `[start, end)` on `closed_at`. Named/calendar cycles are a later layer built on this primitive — out of scope here.
>
> **Scope of the report (throughput + cost spine):** per the CEO-approved lean, the first report answers throughput and cost per window: plans closed in `[start, end)`, grouped by `target_project` and plan `type` (diagnostic/executable), with `COUNT(DISTINCT plan)`, `SUM(cost_usd)`, `SUM(turns)`. This is the spine; richer rollups (gate pass/fail from `gate_events`, deposit-landed rates from `deposits`, verdict-outcome distribution from `verdicts`, diagnostic→executable lineage from `derivations`) are explicitly deferred to later plans — name them in the blueprint as follow-on scope but do NOT design them now.
>
> **Integration surface:** the new query helper follows the EXACT established pattern in `status.py` — importable, read-only (`?mode=ro`), never imports daemon internals (see the module docstring and `query_in_flight`/`query_awaiting_verdict` at status.py:188-230). Decide and specify in the blueprint: does the cycle-query helper live in `status.py` alongside the existing helpers, or in a new sibling module (e.g. `reporting.py`)? Justify the choice against the existing module's single-responsibility docstring ("Renders exactly three elements: daemon header, IN-FLIGHT, AWAITING VERDICT") — a cycle report is a different responsibility, which may argue for a new module. Specify the function signature, return shape (list of rows / dict), the exact SQL, and how a CLI entry point (if any) invokes it.
>
> Deposit the blueprint to `bellows/knowledge/decisions/` as a design doc the DEV can implement from directly — exact SQL, function signatures, file placement, and a test-case list for QA. Use the canonical Python file-write pattern or Filesystem:write_file — no heredoc. Standard prompt feedback protocol → `bellows/knowledge/research/agent-prompt-feedback.md`.
>
> **STOP. Do NOT proceed to Step 2. Do NOT move the plan to Done. Wait for CEO confirmation before continuing.**

---
---

## STEP 2 — DEV

---

> Before starting, read the Step 1 blueprint deposit and check its Output Receipt status. If status is not Complete, stop and report the blocker before proceeding.
>
> You are the Bellows Developer. Read your specialist file at `bellows/agents/BELLOWS_DEVELOPER.md` first. Skip the domain glossary — read-side query implementation.
>
> Implement the cycle-reporting query module exactly as the Step 1 blueprint specifies — file placement, function signature, SQL, and return shape are all defined there; do not re-decide them. Honor the three design constraints the blueprint carries: window on `closed_at` (never intermediate `lifecycle_state`), `COUNT(DISTINCT plan)` for plan-grain counts vs `SUM` over the step join for cost/turns, and range-parameterized `[start, end)` input. All DB access read-only (`?mode=ro`); never import daemon internals — match the `status.py` helper pattern.
>
> Write unit tests per the blueprint's test-case list. At minimum: (a) a range that includes multi-step executables returns correct `COUNT(DISTINCT plan)` — NOT inflated by step count; (b) cost/turn SUMs match hand-computed expected values for a known fixture range; (c) an empty range returns empty/zero, not an error; (d) the boundary is half-open `[start, end)` — a plan closed exactly at `end` is excluded. Run the FULL suite with `timeout 600 pytest tests/` to an explicit pass/fail and READ THE TAIL — never infer green from a subset or collect count. Commit with a descriptive message.
>
> Standard prompt feedback protocol → `bellows/knowledge/research/agent-prompt-feedback.md`.
>
> **STOP. Do NOT proceed to Step 3. Do NOT move the plan to Done. Wait for CEO confirmation.**

---
---

## STEP 3 — QA

---

> Before starting, read the Step 2 deposit / commit and check the Output Receipt status. If status is not Complete, stop and report the blocker before proceeding.
>
> You are Bellows QA. Read your specialist file at `bellows/agents/BELLOWS_QA.md` first.
>
> **Rule 20 self-check is gate-enforced on this step.** Your QA report MUST include the byte-exact banner `Rule 20 — QA Self-Check Results` and a `PASSED — SELF-CHECK PASSED` line; the verification table below does NOT by itself satisfy the gate — end with a self-grep confirming the banner is present in your deposited report.
>
> Verify the Phase 2 query module against the blueprint. Produce a verification table, one row per claim: (1) the module exists at the blueprint-specified path with the specified signature; (2) plan-grain counts use `COUNT(DISTINCT)` — prove with a fixture containing a multi-step executable that the count is NOT step-inflated; (3) cost/turn SUMs match hand-computed values; (4) the query windows on `closed_at` and does not reference intermediate `lifecycle_state`; (5) half-open `[start, end)` boundary is correct (plan at `end` excluded); (6) all DB access is `?mode=ro` and no daemon internals are imported. Re-run the full suite to a pass/fail result and show the tail. Confirm the four DEV unit tests exist and pass. If any row fails, report it and stop — do not pass a broken deliverable.
>
> On completion, update `PROJECT_STATUS.md` with the Phase 2 read-side ship, and move the plan to `Done/`. Standard prompt feedback protocol → `bellows/knowledge/research/agent-prompt-feedback.md`.
