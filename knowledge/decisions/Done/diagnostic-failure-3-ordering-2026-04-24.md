# Bellows — Failure 3 Ordering Diagnostic (Q1–Q4)
**Date:** 2026-04-24 | **Tier:** Medium (diagnostic) | **Test Scope:** none (investigation only) | **Execution:** Step 1 (Bellows Systems Analyst)

## How to Run This Plan

Paste the bootstrap prompt into Claude Code. The agent reads the full plan file, executes Step 1, deposits findings, and reports Complete. After the agent reports Complete, the Planner (in the Projects conversation) performs Rule 22 verification on the deposited findings file and — if all checks pass — moves the plan to Done directly. There is no Step 2 consolidation per Rule 22 / v4.19 single-step diagnostic structure.

**Bootstrap prompt:**

```
Read the plan at knowledge/decisions/diagnostic-failure-3-ordering-2026-04-24.md. Execute Step 1 ONLY. After completing Step 1, STOP and wait for my confirmation. Do NOT move the plan to Done — the Planner performs Rule 22 verification and handles housekeeping.
```

---
---

## STEP 1 — BELLOWS SYSTEMS ANALYST

---

> **FIRST — before doing anything else, claim this plan:** `import shutil; shutil.move("knowledge/decisions/diagnostic-failure-3-ordering-2026-04-24.md", "knowledge/decisions/in-progress-diagnostic-failure-3-ordering-2026-04-24.md")`.
>
> You are the Bellows Systems Analyst. Read your specialist file at `agents/BELLOWS_SYSTEMS_ANALYST.md` first. Skip the domain glossary — this is a code-tracing and architecture-mapping task, no domain interpretation needed.
>
> **Context.** BACKLOG item "Move-to-Done fires before gate check (IP-blocking Failure 3 — CEO-flagged 2026-04-21/22)" describes a recurring stranded-verdict pattern. Bellows currently runs gate checks AFTER the agent has completed its final-step housekeeping (Rule 8 + Rule 23 ordering: feedback append → PROJECT_STATUS update → final commit → move-to-Done). When a terminal-step gate trips, the plan is already in `decisions/Done/` and the verdict request references a plan that has shipped. Two confirmed reproductions on invoice-pulse: `executable-base-rates-url-fix-2026-04-21` and `executable-contract-pubs-route-removal-2026-04-22`. This diagnostic maps the architectural mechanism and produces empirical grounding to support a subsequent fix-shape selection executable. Stream-json minimal switch (shipped 2026-04-23) does NOT subsume this — per `knowledge/research/stream-json-feasibility-2026-04-23.md` Q3, the terminal gates that trip in Failure 3 scenarios (receipt_status, ceo_flags, no_errors, no_permission_denials, deposit_exists) all stay post-hoc because they check fields only available in the terminal `result` event.
>
> **Task — four questions, all investigative. Do NOT propose fix designs. Report what exists today.**
>
> **Q1 — Dispatch ordering.** In `bellows.py`, map where the agent's final-step completion signal lands relative to (a) gate evaluation and (b) move-to-Done. Specifically: does move-to-Done happen inside the agent's final step (executed by the agent per Rule 8's housekeeping ordering) or after Bellows receives the completion signal? At what point in the step lifecycle does Bellows evaluate gates against the final step's commit range? Produce a sequence diagram or numbered timeline showing: agent final-step start → agent commits (feedback, PROJECT_STATUS, final) → agent moves plan to Done → agent returns → Bellows receives completion → Bellows evaluates gates → Bellows posts verdict request (if tripped). Cite `bellows.py` line ranges for each transition.
>
> **Q2 — Gate state exposure.** In `gates.py`, classify each of the 8 gates (6 blocking, 2 informational) by when its state becomes computable: (i) before the agent's final step runs (pre-step), (ii) during the agent's final step as files are written (mid-step), (iii) only after the agent returns and the completion signal lands (post-hoc). For each gate, cite the specific evidence source it reads (e.g., git diff range, verdict file field, file-on-disk check). Specifically confirm or refute: is `scope_check` purely post-hoc, or is some subset evaluable mid-step if Bellows exposes gate state to the agent? Is `deposit_exists` pre-step-evaluable given that the plan's `**Deposits:**` block declares paths up front? Produce a table: gate name | classification (pre/mid/post) | evidence source | notes.
>
> **Q3 — Agent-Bellows signaling surfaces (pure mapping, no fix design).** What writable surfaces exist TODAY that an agent could read or write during its final step to communicate with Bellows? Candidates to investigate: `.bellows-cache/` (what files land there, who writes them, who reads them, what retention policy), any CLI Bellows exposes to agents (e.g., `bellows gate-check` — does such a thing exist?), environment variables Bellows sets on the `claude -p` subprocess, sentinel-file patterns, the verdict file itself (can agents write to it? do they today?). For each surface you identify, document: read access (which party), write access (which party), current use, and whether it is persistent across the step or ephemeral. Do NOT propose fix designs or recommend which surface fits which fix shape. Mapping only. If a surface doesn't exist today but would be trivial to add (e.g., a new sentinel-file convention), note its non-existence and move on — no design work.
>
> **Q4 — Failure class attribution (bounded sample).** List the 10 most recent `verdict-pending-*` files across all projects (scan `{invoice-pulse,bellows,forge,anvil,BrewBuddy,study,SimpleScreen,freight-kb,ai-career-digest}/knowledge/decisions/` and `bellows/verdicts/pending/` if relevant — use filesystem listing and sort by modification time). For each one, determine: (i) plan filename and project, (ii) which gate tripped (read the verdict request file's gate failure section), (iii) was the plan already in `decisions/Done/` when the gate fired, or still in `decisions/` (or `in-progress-*`) — infer from whether a `Done/[same-slug].md` exists, (iv) if the plan was in Done/, confirm or refute that the commits referenced in the plan's final-step housekeeping landed successfully (spot-check with `git --no-pager log --oneline -5 -- <file>` on one representative file per project). Produce a table: filename | project | gate tripped | plan location at verdict time (Done/ vs active) | housekeeping commits landed? (yes/no/N/A). Confirm or refute the BACKLOG hypothesis: is "Failure 3" (gate tripped after move-to-Done on a fully-shipped plan) the dominant mechanism in this sample, or is there a mix?
>
> **Depositing findings.** Deposit a single markdown file at `knowledge/architecture/failure-3-ordering-2026-04-24.md` containing the Q1 timeline, Q2 table, Q3 surface inventory, and Q4 attribution table. Use the standard specialist output format per your specialist file. Include the Layer Impact section called out in your specialist file's "Project-Specific Output Notes" — state which layers (1/2/3) each finding affects. Close with the standard Output Receipt. Status should be Complete if all four questions are answered, or Partial if any question produced incomplete evidence (with a clear note on what's missing and why).
>
> **Deposits:**
> - `knowledge/architecture/failure-3-ordering-2026-04-24.md`
>
> **Do NOT propose fixes.** Do not write a follow-up executable. Do not edit BACKLOG. Do not update PLANNER_TEMPLATE. The Planner reads your findings, makes the fix-shape selection, and writes the subsequent executable as a separate plan.
>
> **Feedback.** Standard prompt feedback protocol → `knowledge/research/agent-prompt-feedback.md`.
>
> **STOP. Do NOT proceed to any housekeeping. Do NOT move the plan to Done. The Planner performs Rule 22 verification in the Projects conversation and handles the Done/ move directly. Wait for CEO confirmation that verification passed before the plan file is renamed.**

---
