# Bellows — qa_step_detection Gate Audit

**Date:** 2026-05-22 | **Tier:** Small | **Dispatch Mode:** bellows | **Test Scope:** none (read-only diagnostic) | **Execution:** Step 1 (SA) → Step 2 (SA) → Step 3 (SA) | **pause_for_verdict:** after_step_1

## Context

BACKLOG.md (2026-05-21 entry) flagged that `qa_step_detection` did not recognize "Invoice Security & Testing Analyst" as a QA agent during the fuel UI closeout plan Step 1. The verdict request showed `qa_step_detection: PASS | Not a QA step` and consequently `rule_20_self_check: PASS | N/A (not a QA step)`. The Planner manually verified Rule 20 substance instead.

The entry was deferred at the time. The defer is now in tension with PLANNER_TEMPLATE v4.48 Rule 25 codification, which routes the Planner to perform (b) substance check ONLY when both mechanized gates pass — actively suppressing the manual Rule 20 verification that was the defer's safety net. Every silent N/A on a real QA step is now a load-bearing gap.

This diagnostic characterizes the current gate, audits the population of recent QA steps to quantify the leak, and proposes a concrete header-field shape for shipping in a follow-on executable.

## How to Run This Plan

Paste the bootstrap prompt into Claude Code. The agent reads the full plan file and executes Step 1 ONLY. After completing Step 1, the agent STOPS and waits for CEO confirmation ("ok") before proceeding to Step 2. This continues step by step until the plan is complete. The agent must never skip steps, auto-chain to the next step, or move the plan to Done without completing all steps.

```
Read the plan at bellows/knowledge/decisions/diagnostic-qa-step-detection-audit-2026-05-22.md. Execute Step 1 ONLY. After completing Step 1, STOP and wait for my confirmation. Do NOT proceed to Step 2 or move the plan to Done.
```

---
---

## STEP 1 — Bellows Systems Analyst

---

> **FIRST — before doing anything else, claim this plan:** `import shutil; shutil.move("bellows/knowledge/decisions/diagnostic-qa-step-detection-audit-2026-05-22.md", "bellows/knowledge/decisions/in-progress-diagnostic-qa-step-detection-audit-2026-05-22.md")`. You are the Bellows Systems Analyst. Read your specialist file and domain glossary first. **Task:** characterize the current `_gate_qa_step_detection` mechanism end-to-end. Read `bellows/gates.py` and locate `_gate_qa_step_detection` (or its equivalent — confirm exact function name). Trace: (1) the data source the gate reads (plan prompt text, agent receipt, role name string from where exactly?), (2) the keyword set or regex pattern used to classify a step as QA, (3) the call site in `gates.check()` and what consumers depend on `is_qa_step` (search for `is_qa_step` across `bellows.py`, `gates.py`, `verdict.py` and enumerate all readers), (4) whether the gate currently reads any field from the plan header (e.g., `gates._parse_plan_header()` output), and (5) the downstream effect on `_gate_rule_20_self_check` when `is_qa_step` is False — specifically why this produces `PASS | N/A (not a QA step)` instead of failing-closed. **Deposit findings to** `bellows/knowledge/research/qa-step-detection-mechanism-2026-05-22.md` with sections: Gate Function (name, file, line range), Data Source, Classification Logic (verbatim keyword set or regex), Call Site, is_qa_step Consumers (enumerated list), Rule 20 Interaction, and Failure Mode Summary (one paragraph explaining how a real QA step gets classified as not-QA and what that suppresses). **Constraints:** read-only, no code edits, no test runs. Do not propose fixes yet — Step 3 will handle that. Standard prompt feedback protocol → `bellows/knowledge/research/agent-prompt-feedback.md`. **Deposits:**
> - `bellows/knowledge/research/qa-step-detection-mechanism-2026-05-22.md`
>
> **STOP. Do NOT proceed to Step 2. Do NOT move the plan to Done. Wait for CEO confirmation before continuing.**

---
---

## STEP 2 — Bellows Systems Analyst

---

> Before starting, read `bellows/knowledge/research/qa-step-detection-mechanism-2026-05-22.md` and check the Output Receipt status field. If status is not Complete, stop and report the issue to the CEO before proceeding. You are the Bellows Systems Analyst. **Task:** quantify the qa_step_detection leak rate across recent Bellows activity. **Method:** enumerate verdict-request files from the past 30 days (sources: `bellows/verdicts/pending/archived/`, `bellows/verdicts/resolved/processed-*`, `bellows/logs/*.json` if applicable — confirm which sources are reachable). For each verdict request with `pause_reason_code` indicating a QA-relevant pause OR with a verdict file path naming a QA step OR referencing a project's QA specialist by role name, classify into: (a) gate correctly detected QA (`qa_step_detection: PASS | <QA detected>` or similar), (b) gate said `Not a QA step` but the work was substantively QA (cross-reference the prior step's deposited files in `knowledge/qa/` to confirm), (c) genuinely not a QA step (no `knowledge/qa/` deposit, no QA-role specialist invoked). **Per-project breakdown required** — at minimum invoice-pulse, bellows, forge, anvil, study, BrewBuddy, SimpleScreen, freight-kb, ai-career-digest (audit only projects with activity in the 30-day window; note projects with zero QA steps as such). For each classified (b) case, capture the plan slug, the QA role name that was used, and a one-line summary of why the gate missed it. **Deposit findings to** `bellows/knowledge/research/qa-step-detection-population-audit-2026-05-22.md` with sections: Audit Window (date range and source files counted), Methodology, Per-Project Tables (one table per project with columns: plan slug, step number, QA role name, gate verdict, classification a/b/c, notes), Leak Rate Summary (total class-b count vs total QA-step count), and Notable Patterns (any role names that recur in class-b — these are the population that needs coverage). **Constraints:** read-only, no code edits, no test runs. Use `git --no-pager` for any git commands. Standard prompt feedback protocol. **Deposits:**
> - `bellows/knowledge/research/qa-step-detection-population-audit-2026-05-22.md`
>
> **STOP. Do NOT proceed to Step 3. Do NOT move the plan to Done. Wait for CEO confirmation before continuing.**

---
---

## STEP 3 — Bellows Systems Analyst

---

> Before starting, read `bellows/knowledge/research/qa-step-detection-mechanism-2026-05-22.md` and `bellows/knowledge/research/qa-step-detection-population-audit-2026-05-22.md` and check both Output Receipt status fields. If either is not Complete, stop and report the issue to the CEO before proceeding. You are the Bellows Systems Analyst. **Task:** propose the concrete shape for the `qa_steps` plan-header field as the structural fix. Given the gate mechanism characterized in Step 1 and the leak surface quantified in Step 2, specify: (1) **header field placement** — where in the plan header line does `qa_steps` go (between which existing fields), and what is the canonical value format (comma-separated integers like `qa_steps: 1,3`? Range syntax like `qa_steps: 1-3`? Bool-per-step?) — pick one and justify against existing PLANNER_TEMPLATE header conventions; (2) **parse path** — what change to `gates._parse_plan_header()` (or wherever the header is parsed) is required to extract the field, and what change to `_gate_qa_step_detection` consumes it; (3) **fallback semantics** — when a plan has no `qa_steps` field (legacy plans, manual_bootstrap plans, parallel-group plans), what behavior preserves current correctness (keyword fallback? Default to all-steps-non-QA with WARN?); (4) **governance edit** — concrete edit shape for PLANNER_TEMPLATE.md to specify the new field. Include the exact paragraph wording proposed (read PLANNER_TEMPLATE.md to locate the right insertion point — likely near Rule 26 deposits convention or the Plan File Structure section, recommend which); (5) **migration risk surface** — enumerate concrete risks (e.g., existing in-flight plans without the field, plans authored mid-transition by CEO from older template, parallel-group plans where only one sibling has the field) and how the fallback handles each. **Deposit findings to** `bellows/knowledge/research/qa-step-detection-fix-shape-2026-05-22.md` with one section per numbered item above plus a final "Recommended Next Plan" section that names the executable plan filename and sketches its step structure (DEV → QA expected, but confirm). **Constraints:** read-only investigation. Do NOT author the executable plan — that's the next session's work after CEO reviews this findings file. Do NOT read project source code beyond bellows itself (PLANNER_TEMPLATE.md and bellows files only). Standard prompt feedback protocol. **Deposits:**
> - `bellows/knowledge/research/qa-step-detection-fix-shape-2026-05-22.md`
>
> **STOP. Do NOT move the plan to Done. Wait for CEO confirmation. Per Rule 22, the Planner performs the move-to-Done after verification.**
