# Bellows — Plan-Lint Feasibility Audit (Diagnostic)
**Date:** 2026-07-01 | **Tier:** Small | **Dispatch Mode:** bellows | **Test Scope:** targeted | **Execution:** Step 1 (SA)

## How to Run This Plan

Paste the bootstrap prompt into Claude Code. The agent reads the full plan and executes Step 1 ONLY — a read-only investigation. After Step 1 the agent STOPS. Single-step diagnostic; no Step 2, no move-to-Done.

**Bootstrap prompt:**
```
Read the plan at bellows/knowledge/decisions/[filename].md. Execute Step 1 ONLY. Read-only investigation — do not write, fix, or refactor anything except the findings deposit. Then stop.
```

---
---

## STEP 1 — SA

---

> Post a short chat message confirming you are starting and stating your next action. Do NOT rename the plan file. You are the Bellows Systems Analyst — read `bellows/agents/BELLOWS_SYSTEMS_ANALYST.md` first; skip the domain glossary, this is a tooling-feasibility audit.
>
> The CEO wants to offload mechanical plan-authoring discipline from the Planner (a model, unreliable at rote format checks) into a coded pre-deposit linter — a `plan-lint` gate that runs after a plan is composed in `_staging_*` and before the atomic move into the watched `decisions/` directory, exit-non-zero on violation, read-only (it blocks, it never rewrites plans). This is FORWARD row 9 ("Pre-deposit plan-lint script for strict-convention strings"). Before any module is designed, determine exactly which of the 22 Plan Authoring Checklist items are mechanically lintable and which secretly require model judgment.
>
> The checklist lives in `PLANNER_TEMPLATE.md` under `## Plan Authoring Checklist` (22 items, `### 1` through `### 22`). Read all 22 in full. For EACH item, classify into exactly one of three buckets and justify in one line: (A) LINTABLE — checkable by a deterministic scan of the plan file alone (grep/parse/structural check) with no external context and no judgment; name the concrete check (what string/structure is asserted, what a pass/fail looks like). (B) LINTABLE-WITH-CONTEXT — mechanically checkable but requires reading something beyond the plan file (the referenced blueprint, the lifecycle DB, a known-good artifact, current parser output); name the dependency and whether that dependency is reliably available at deposit time. (C) JUDGMENT — cannot be reduced to a deterministic check; requires the model to assess meaning, correctness, or intent (e.g. "does this assertion rest on a shaky input," "did the diagnostic prove its claim"). State why it resists mechanization.
>
> HARD CONSTRAINT on bucket (B): a pipeline module may only ever perform a read-only check or a trivial single-field/binary edit with zero content judgment — it never authors or interprets plan content. Apply this test to every (B) item: if its check is a read-only cross-reference (e.g. string-presence lookup in the referenced blueprint), it stays (B) and is pipeline-eligible. If its check requires deciding whether content is ADEQUATE, CORRECT, or WELL-FORMED-IN-MEANING rather than merely PRESENT, reclassify it to (C) — it is judgment wearing a mechanical costume, and it is NOT pipeline-eligible regardless of how checkable it looks. The feasibility count must reflect this: (B) counts only read-only-or-trivial-edit checks. State for each (B) item which side of this line it falls on and why.
>
> For every (A) item, also note whether a checkable signal ALREADY EXISTS in the codebase — i.e. does `gates.py` or any existing parser already implement this or half of it (cite function + line). The point: some checklist items may already be enforced at the GATE layer post-dispatch; a pre-deposit lint of those is either redundant or a valuable shift-left. Flag which.
>
> Produce a summary table: item number, one-line description, bucket (A/B/C), concrete check or reason-it-resists, existing-code overlap if any. Then a bottom-line count: how many of 22 are cleanly lintable (A), how many are lintable-with-available-context (B with reliable dependency), how many are judgment (C or B-with-unreliable-dependency). This count IS the feasibility answer — it tells the CEO how much discipline actually offloads to code versus how much stays model judgment regardless.
>
> Do NOT design the module, propose an architecture, or write any lint code — feasibility classification only. Deposit findings to `bellows/knowledge/research/plan-lint-feasibility-2026-07-01.md`. Use the canonical Python file-write pattern or Filesystem:write_file — no heredoc.
>
> **Deposits:**
> - `bellows/knowledge/research/plan-lint-feasibility-2026-07-01.md`
>
> Standard prompt feedback protocol → Output Receipt `### Ledger Updates` `#### Prompt Feedback` section.
>
> **STOP. Single-step diagnostic. Do NOT move the plan to Done.**
