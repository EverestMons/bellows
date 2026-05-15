# Bellows — PROJECT_STATUS Update for Reliability Bugs 1-3

**Date:** 2026-04-24 | **Tier:** Small | **Test Scope:** targeted | **Execution:** Step 1 (DOC)

## How to Run This Plan

Paste the bootstrap prompt into Claude Code. The agent reads the full plan file and executes Step 1 ONLY. After completing Step 1, the agent STOPS.

**Bootstrap prompt:**
```
Read the plan at bellows/knowledge/decisions/executable-project-status-reliability-bugs-1-2-3-2026-04-24.md. Execute Step 1 ONLY. After completing Step 1, STOP and wait for my confirmation. Do NOT move the plan to Done — Planner handles terminal housekeeping.
```

---
---

## STEP 1 — BELLOWS DOCUMENTATION ANALYST

---

> **FIRST — before doing anything else, claim this plan:** `import shutil; shutil.move("bellows/knowledge/decisions/executable-project-status-reliability-bugs-1-2-3-2026-04-24.md", "bellows/knowledge/decisions/in-progress-executable-project-status-reliability-bugs-1-2-3-2026-04-24.md")`.
>
> You are the Bellows Documentation Analyst. Skip specialist file and glossary reads — this is a PROJECT_STATUS update task with no domain interpretation required.
>
> Read `bellows/PROJECT_STATUS.md`. Add a new completed-milestone entry for the reliability bugs 1, 2, 3 plan. Use `read_text_file` and `edit_block` (or `Filesystem:edit_file`) to insert the entry; do NOT rewrite the entire file. Anchor the edit on the existing "Completed Milestones" section header (or whatever the canonical section is for completed work in this project's PROJECT_STATUS) — read the file first to identify the correct anchor before editing.
>
> The milestone entry should include: (a) date 2026-04-24, (b) plan slug `executable-bellows-reliability-bugs-1-2-3-2026-04-24`, (c) commit hash `c7f69f3`, (d) one-line summary per bug: Bug 1 — `_consume_verdicts` plan_matched gate + stale-verdict Done/ check; Bug 2 — base_filename canonicalization at 5 path-construction sites in `run_plan()`; Bug 3 — `extract_total_steps` case-insensitive regex tightened to `\s+\d+` with mismatch warning; (e) test count: +10 unit tests, 149/150 targeted (1 pre-existing `test_run_step_timeout` unrelated); (f) REMINDER to restart Bellows daemon to load fixes.
>
> After the edit, verify the change landed via `read_text_file` on the modified section. Commit with message: `docs: project status — reliability bugs 1-3 shipped`.
>
> **Deposits:**
> - `bellows/PROJECT_STATUS.md` (edit, not new file)
>
> Standard prompt feedback protocol → `bellows/knowledge/research/agent-prompt-feedback.md`.
>
> **STOP. Do NOT move the plan to Done. Planner handles terminal housekeeping after Rule 22 verification.**
