# Diagnostic — Rule 20 Self-Check Block Sourcing Migration Surface

**Project:** bellows
**Date:** 2026-05-10
**Author:** Planner
**Tier:** Small
**Total Steps:** 1

**pause_for_verdict:** always

---

## Context

Closes the diagnostic phase of BACKLOG `2026-05-10: Rule 20 self-check block in plans should reference canonical PLANNER_TEMPLATE, not re-author`. The BACKLOG entry's recommendation is option (c): move the canonical Rule 20 self-check block into `bellows/agents/qa.md` (and analogous QA agent files in other projects) so QA agents own the block, and plans reference "per your agent file" rather than re-authoring.

Before writing the migration executable, the Planner needs five facts pinned down:

1. The exact current canonical Rule 20 self-check block as published in PLANNER_TEMPLATE.md v4.35 (verbatim, for migration).
2. The current structure and contents of `bellows/agents/qa.md` — where the block should land, and what surrounding context exists.
3. The current structure of `invoice-pulse/agents/qa.md` (or whatever the equivalent QA agent file is) — to determine whether this migration is bellows-only or cross-project.
4. The current Rule 20 prose in PLANNER_TEMPLATE.md that mandates the block's existence — so the migration knows what to rewrite (from "include this Python block" to "run your canonical Rule 20 self-check from your agent file").
5. The set of recent Planner-authored plans (last 7 days, across all projects) that include a Rule 20 self-check block — to size the rollout and identify any in-flight plans that would break.

This diagnostic surfaces those facts so the Planner can scope the executable correctly.

---

## STEP 1 — Systems Analyst: surface migration facts

**Agent:** Bellows Systems Analyst (`bellows/agents/sa.md`)
**Working directory:** `/Users/marklehn/Desktop/GitHub/`
**Deposits:**
- `bellows/knowledge/research/rule-20-block-sourcing-migration-surface-2026-05-10.md`

### Prompt

You are the Bellows Systems Analyst. Read your agent file at `bellows/agents/sa.md` before starting. Today's diagnostic is governance-scoped, not architecture-scoped — your job is to surface facts about file layouts and current content, NOT to recommend a fix shape. The Planner makes the fix-shape decision after reading your findings.

This is a single-step investigation. Read-only. No code edits, no file moves, no commits.

Investigate the following five questions and write a single findings file at `bellows/knowledge/research/rule-20-block-sourcing-migration-surface-2026-05-10.md`. Use the questions as section headers; quote evidence verbatim with line numbers where helpful.

### Q1. PLANNER_TEMPLATE Rule 20 canonical block — verbatim

Read `/Users/marklehn/Desktop/GitHub/PLANNER_TEMPLATE.md`. Locate the Rule 20 section (titled something like "Mandatory QA self-check Python block" near rules 18–22). Quote the **full Rule 20 section verbatim** in your findings, including: any prose preamble, the Python block in full, any prose postamble, any examples. Mark exact start and end line numbers.

If Rule 20 spans multiple subsections or is referenced from other rules (e.g., Rule 22 (e)), also locate and quote those cross-references with line numbers.

### Q2. `bellows/agents/qa.md` — current structure

Read `/Users/marklehn/Desktop/GitHub/bellows/agents/qa.md` in full. In your findings, capture:

- Total line count and approximate size.
- Top-level section headers (the `## ` lines) in order.
- Any existing reference to "Rule 20" or "self-check" — quote verbatim with line numbers if present.
- A recommended insertion point for a new "Rule 20 Self-Check (Canonical Block)" section: cite the line number, the surrounding section headers, and your reasoning (e.g., "after the QA workflow section, before the Output Receipt section").

### Q3. Invoice-pulse QA agent file — current structure

Locate the analogous QA agent file in `/Users/marklehn/Desktop/GitHub/invoice-pulse/agents/`. If the file is named differently (e.g., `qa-engineer.md`, `quality-assurance.md`), use that. If multiple QA-adjacent agent files exist, list all and pick the primary. Then:

- Quote the full filename and path.
- Capture top-level section headers (the `## ` lines) in order.
- Any existing reference to "Rule 20" or the Python self-check block — quote verbatim with line numbers if present.
- Note whether invoice-pulse's QA agent file already publishes the canonical Rule 20 block locally (which would mean migration is purely consolidation, not net-new authoring).

### Q4. PLANNER_TEMPLATE Rule 20 prose that mandates the block

Quote the prose in Rule 20 (and any related rule like Rule 22 (e)) that currently tells the Planner / agent that the block must appear. Mark line numbers. This is what the migration would need to rewrite — from "include the Python block in every QA step" to "reference the canonical block in the QA agent file."

Also note: does PLANNER_TEMPLATE Rule 20 currently say anything about WHERE the block must appear? (e.g., "at the end of the QA report" vs. "anywhere in the QA report"). The gate enforces banner-presence-with-PASSED-after; the rule's positional guidance, if any, affects whether the agent-file version can be referenced positionally.

### Q5. Recent Planner-authored plans containing a Rule 20 block

Using `grep` or equivalent, find all `.md` files in `*/knowledge/decisions/` (top-level AND `Done/`) modified in the last 7 days (since 2026-05-03) that contain a Python block with `RULE 20 SELF-CHECK`, `Rule 20 — QA Self-Check Results`, or similar banner text.

For each match, report:
- Full file path.
- Project (bellows / invoice-pulse / etc.).
- Lifecycle state (Done/, top-level, halted-, in-progress-, verdict-pending-).
- Banner string used (canonical `Rule 20 — QA Self-Check Results` vs. non-canonical variants).

This is sizing data — tells the Planner how many plans the migration affects and whether any in-flight plans need to be updated.

### Output Receipt

When complete, output a receipt block in this exact format:

```
**Step:** 1
**Status:** Complete
**Deposits:**
- bellows/knowledge/research/rule-20-block-sourcing-migration-surface-2026-05-10.md (created)
```

STOP after Step 1. This is a single-step diagnostic. The Planner reviews the findings file directly per Rule 22 before authoring any migration executable.

---

## Deliverables Summary

| Step | Agent | Deliverable | Location |
|------|-------|-------------|----------|
| 1 | SA | findings file (created) | `bellows/knowledge/research/rule-20-block-sourcing-migration-surface-2026-05-10.md` |
