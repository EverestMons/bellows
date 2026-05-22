# Bellows — `.claude/settings.local.json` Permission Gap Diagnostic

**Date:** 2026-05-22 | **Tier:** Small | **Dispatch Mode:** bellows | **Test Scope:** none (read-only diagnostic) | **Execution:** Step 1 (SA) → Step 2 (SA) → Step 3 (SA) | **pause_for_verdict:** after_step_1

## Context

BACKLOG.md (2026-05-21 entry) flagged that the agent `Edit` tool was denied on `.claude/settings.local.json` during the tier-1 batch plan, despite the file being the explicit target of the plan's task. The agent shipped the correct state on disk via a bash fallback, but the `no_permission_denials` gate fired correctly as blocking and produced a `gate_failure` verdict request. Rule 22 override resolved the immediate plan.

Three resolution shapes were proposed at filing time: (1) document the bash-fallback pattern in BELLOWS_DEVELOPER.md, (2) add `.claude/settings.local.json` to a permitted-Edit list at the plan-prompt level when needed, (3) move `.claude/settings.local.json` operations out of agent scope entirely. The entry explicitly defers shape selection on the grounds that diagnostic characterization of the permission gap is required first: "is it Edit-tool-specific, file-path-specific, or claude-code-config-directory-specific?"

This diagnostic answers that question, audits historical permission-denial events to quantify recurrence risk, and proposes a concrete resolution shape with governance-edit or workaround-documentation specifics.

## How to Run This Plan

Paste the bootstrap prompt into Claude Code. The agent reads the full plan file and executes Step 1 ONLY. After completing Step 1, the agent STOPS and waits for CEO confirmation ("ok") before proceeding to Step 2. This continues step by step until the plan is complete. The agent must never skip steps, auto-chain to the next step, or move the plan to Done without completing all steps.

```
Read the plan at bellows/knowledge/decisions/diagnostic-claude-settings-permission-gap-2026-05-22.md. Execute Step 1 ONLY. After completing Step 1, STOP and wait for my confirmation. Do NOT proceed to Step 2 or move the plan to Done.
```

---
---

## STEP 1 — Bellows Systems Analyst

---

> **FIRST — before doing anything else, claim this plan:** `import shutil; shutil.move("bellows/knowledge/decisions/diagnostic-claude-settings-permission-gap-2026-05-22.md", "bellows/knowledge/decisions/in-progress-diagnostic-claude-settings-permission-gap-2026-05-22.md")`. You are the Bellows Systems Analyst. Read your specialist file and domain glossary first. **Task:** characterize the permission-gap mechanism that denied the agent Edit-tool call on `bellows/.claude/settings.local.json` during the tier-1 batch plan. Three sub-investigations: **(a) settings.local.json content audit** — read `bellows/.claude/settings.local.json` and enumerate the structure: what fields exist (`permissions.allow`, `permissions.deny`, others?), what tool families are present in `permissions.allow` (Bash patterns, Read patterns, Edit patterns, etc.), and is there a `permissions.deny` block that explicitly excludes Edit calls on this file or this path. **(b) Claude Code permission semantics** — search the web for current Anthropic Claude Code documentation on `settings.local.json` permission evaluation, specifically: how does Claude Code decide whether a given tool call is permitted? Is the default behavior "allow unless denied" or "deny unless allowed"? How does the `allow` list interact with the `deny` list? Does the Edit tool have a default-allow regardless of the file path, or does Edit require an entry in `allow` like Bash does? Cite the documentation URL(s) read. **(c) denial reproduction trace** — locate the original denial event in `bellows/logs/` from 2026-05-21 (search for tier-1 batch plan slug `executable-bellows-tier-1-batch-2026-05-21` or similar; check `logs/terminal/bellows-2026-05-21.log` and any step JSON files). Extract the literal denial message text and the tool call that triggered it. Identify which of three patterns it matches: (i) Edit-tool-specific (Edit denied on any file regardless of path), (ii) file-path-specific (Edit denied on `.claude/settings.local.json` specifically, allowed on other files in the same step), (iii) claude-code-config-directory-specific (Edit denied on anything under `.claude/`). **Deposit findings to** `bellows/knowledge/research/claude-settings-permission-gap-2026-05-22.md` with sections: settings.local.json Structure, Permission Semantics (with cited URLs), Denial Reproduction Trace, Pattern Classification (one of i/ii/iii with evidence), and Failure Mode Summary (one paragraph explaining when Edit denials will recur). **Constraints:** read-only, no code edits, no test runs. Use `git --no-pager` for any git commands. Use web_search for Claude Code permission docs. Do not propose fixes yet — Step 3 will handle that. Standard prompt feedback protocol → `bellows/knowledge/research/agent-prompt-feedback.md`. **Deposits:**
> - `bellows/knowledge/research/claude-settings-permission-gap-2026-05-22.md`
>
> **STOP. Do NOT proceed to Step 2. Do NOT move the plan to Done. Wait for CEO confirmation before continuing.**

---
---

## STEP 2 — Bellows Systems Analyst

---

> Before starting, read `bellows/knowledge/research/claude-settings-permission-gap-2026-05-22.md` and check the Output Receipt status field. If status is not Complete, stop and report the issue to the CEO before proceeding. You are the Bellows Systems Analyst. **Task:** audit historical permission-denial events to characterize recurrence patterns. **Method:** enumerate every `no_permission_denials` gate failure in Bellows history (sources: `bellows/verdicts/resolved/processed-*` files containing `no_permission_denials` in the gate failure section, `bellows/logs/*.json` step files with permission-denial entries, and ledger entries with `gate_failure` pause reason). For each event, extract: (1) plan slug, (2) step number, (3) the file path the denied operation targeted, (4) the tool that was denied (Edit, Write, Bash, Read, etc.), (5) the agent role that hit the denial. Classify each event into buckets: (a) `.claude/settings.local.json` edits specifically, (b) other `.claude/` directory edits, (c) edits to project-source files outside `.claude/`, (d) Bash command denials unrelated to Edit. **Per-bucket counts required.** For bucket (a), produce a per-occurrence table with plan slug, date, the specific change being attempted, and whether the agent successfully worked around via bash fallback. **Deposit findings to** `bellows/knowledge/research/permission-denial-history-audit-2026-05-22.md` with sections: Audit Window (date range and source files counted), Methodology, Event Inventory Tables (per bucket), Bucket Counts Summary, and Recurrence Pattern (does bucket (a) recur monthly, weekly, only on Bellows-self plans editing the allowlist itself, etc. — quantify). **Constraints:** read-only, no code edits, no test runs. Use `git --no-pager` for any git commands. Standard prompt feedback protocol. **Deposits:**
> - `bellows/knowledge/research/permission-denial-history-audit-2026-05-22.md`
>
> **STOP. Do NOT proceed to Step 3. Do NOT move the plan to Done. Wait for CEO confirmation before continuing.**

---
---

## STEP 3 — Bellows Systems Analyst

---

> Before starting, read `bellows/knowledge/research/claude-settings-permission-gap-2026-05-22.md` and `bellows/knowledge/research/permission-denial-history-audit-2026-05-22.md` and check both Output Receipt status fields. If either is not Complete, stop and report the issue to the CEO before proceeding. You are the Bellows Systems Analyst. **Task:** given the mechanism characterized in Step 1 and the recurrence audit in Step 2, recommend a resolution shape and specify its implementation surface. Evaluate the three BACKLOG-proposed shapes against the evidence: **(1) document the bash-fallback workaround pattern in BELLOWS_DEVELOPER.md** — what specific paragraph addition is required, where in the specialist file does it go, and does this shape close the recurrence vector or only mitigate it; **(2) add `.claude/settings.local.json` to a permitted-Edit list at the plan-prompt level** — concrete prompt-template addition (what literal text gets injected into agent prompts that need to edit this file), where in PLANNER_TEMPLATE.md would this be codified, what is the field/tag name (`permitted_edits: .claude/settings.local.json`?), and does this shape require any Bellows-side gate change to recognize the prompt-level allowance; **(3) move `.claude/settings.local.json` operations out of agent scope entirely** — what governance edit (PLANNER_TEMPLATE rule or BELLOWS_DEVELOPER constraint) declares this file CEO-only, how does a plan signal "this edit goes through the CEO" instead of through an agent step, and what is the operational handoff (CEO performs the edit manually after agent reports the desired state, or agent deposits a `.diff`/`.patch` file the CEO applies?). For each shape, score on three axes: (i) coverage of the failure mode surfaced in Step 1 evidence, (ii) compatibility with the recurrence pattern in Step 2 (frequent → shape must close vector; rare → shape can document workaround), (iii) authorship burden on the Planner per plan. Then **make a single recommendation** with reasoning. **Deposit findings to** `bellows/knowledge/research/claude-settings-permission-gap-fix-shape-2026-05-22.md` with sections: Shape 1 Evaluation, Shape 2 Evaluation, Shape 3 Evaluation, Scoring Matrix (3-shape × 3-axis), Recommendation, and Recommended Next Plan (executable plan filename and step-structure sketch — likely DEV → QA if governance edit, or Documentation Agent only if specialist file edit). **Constraints:** read-only investigation. Do NOT author the executable plan — that's the next session's work after CEO reviews this findings file. Do NOT read project source code beyond bellows itself and PLANNER_TEMPLATE.md / BELLOWS_DEVELOPER.md / governance files. Standard prompt feedback protocol. **Deposits:**
> - `bellows/knowledge/research/claude-settings-permission-gap-fix-shape-2026-05-22.md`
>
> **STOP. Do NOT move the plan to Done. Wait for CEO confirmation. Per Rule 22, the Planner performs the move-to-Done after verification.**
