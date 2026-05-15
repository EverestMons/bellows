# Bellows — BACKLOG append (3 new items from plan-mutation-source diagnostic)
**Date:** 2026-04-19 | **Tier:** Small | **Test Scope:** targeted | **Execution:** Step 1 (DOC) → Step 2 (QA)
**Priority:** 20

## How to Run This Plan

Bellows will auto-dispatch. Agent executes Step 1 ONLY, STOPS, waits for CEO confirmation, then Step 2.

**Bootstrap (only if Bellows does not auto-dispatch):**
```
Read the plan at bellows/knowledge/decisions/executable-backlog-append-2026-04-19.md. Execute Step 1 ONLY. After completing Step 1, STOP and wait for my confirmation.
```

---
---

## STEP 1 — BELLOWS DOCUMENTATION ANALYST

---

> **FIRST — before doing anything else, claim this plan:** `import shutil; shutil.move("bellows/knowledge/decisions/executable-backlog-append-2026-04-19.md", "bellows/knowledge/decisions/in-progress-executable-backlog-append-2026-04-19.md")`.
>
> You are the Bellows Documentation Analyst. Skip specialist file and glossary reads — this is a mechanical append task.
>
> **Objective:** Append three new items to the top of the `## Open` section of `bellows/knowledge/BACKLOG.md`. The three items are new findings from today's plan-mutation-source diagnostic session.
>
> **Procedure:** Use `Filesystem:edit_file` or `Desktop Commander:edit_block` to anchor on the verbatim existing line `## Open` and replace it with `## Open` followed by the three new bullets. The three bullets, in insertion order (newest first, so they appear at the top of Open):
>
> Bullet 1 (scope_check false-positive over too-wide git range):
> `- 2026-04-19: scope_check false-positive over too-wide git range — today's diagnostic (plan-mutation-source-2026-04-19) and its canary (plan-mutation-canary-2026-04-19) both tripped scope_check at their terminal step, flagging `LESSONS.md` and `bellows/knowledge/BACKLOG.md` as out-of-scope files. \`git diff --stat HEAD~3 HEAD\` confirmed those files were modified by yesterday's verdict-lifecycle-coupling commits, not by today's work. Scope_check appears to be reading a git range that extends beyond the current plan's actual commits. This is a distinct mechanism from the deposit-path parser false positives (BACKLOG #6, closed 2026-04-19) — that class was about keyword-scanning plan content; this class is about over-wide git-diff scoping. Related to BACKLOG #8 (QA-checkpoint pause decorative) — both are "gates evaluate against state that doesn't reflect the plan's actual work." Suggested fix shape: scope the git range to commits made during the plan's own dispatch window (first claim timestamp → current step), or use git's \`--since\` bounded by the plan's claim time. Full context in plan-mutation-source-2026-04-19 findings — two plans stranded in verdict-pending until manual override.`
>
> Bullet 2 (deposit parser gap):
> `- 2026-04-19: deposit parser gap for Rule 26 block form recurred — the SA's plan-mutation-source findings file was deposited correctly at \`bellows/knowledge/research/plan-mutation-source-2026-04-19.md\`, but the verdict request showed \`Deposit: none\`. This is the known parser gap documented in v4.25 Rule 26 — \`extract_primary_deposit()\` in \`verdict.py\` still reads only the singular \`**Deposit:**\` form, not the plural \`**Deposits:**\` block. The Planner is handling this via the v4.25 workaround (read the plan's declared **Deposits:** block directly and apply Rule 22 to each path), but this is friction every time a Rule 26-compliant plan runs. Promote from "known gap" to active fix: extend the parser in \`verdict.py\` to recognize the \`**Deposits:**\` block and populate the verdict request's \`Deposit:\` field accordingly. Related to BACKLOG #6 (closed 2026-04-19) — that plan scoped gates.py's \`deposit_exists\` to the block form, but the verdict-request populator was intentionally left on the legacy parser per governance-first ship pattern. Time to close the loop.`
>
> Bullet 3 (single-step diagnostic verdict-request generation):
> `- 2026-04-19: single-step diagnostic generates verdict request even on successful completion — Rule 22 v4.19 moved diagnostic plans to a single-step structure with no Step 2 consolidation, intended to eliminate stranded in-progress files. Today's plan-mutation-source diagnostic completed successfully (findings deposited, Rule 22 verification passed), but Bellows still generated a verdict request because Step 1 tripped scope_check. For single-step diagnostics where the diagnostic artifact is a research deposit (not code changes), scope_check may not be a meaningful safety check — the agent's whole job was to investigate and write a findings file. Three possible resolutions: (a) mark diagnostic plans as exempt from scope_check (plan-header flag), (b) scope_check applies only to plans that declare code-mutating intent, (c) accept as correct behavior and fix scope_check's accuracy instead (per the first item in this batch). Option (c) subsumes (a) and (b). Deferred to next governance pass.`
>
> After the three bullets, preserve the existing blank line and the existing first bullet (currently: `- 2026-04-18: Planner should read verdicts folder directly...`).
>
> After the edit, verify via `Filesystem:read_text_file` that the three new bullets are present at the top of the Open section and that the existing content below is intact. If the edit fails or produces malformed output, stop and report — do NOT proceed to commit.
>
> Commit the BACKLOG edit: `git add bellows/knowledge/BACKLOG.md && git commit -m "docs: BACKLOG — 3 new items from plan-mutation-source diagnostic"`.
>
> Standard prompt feedback protocol → `bellows/knowledge/research/agent-prompt-feedback.md`.
>
> **Deposits:**
> - `bellows/knowledge/BACKLOG.md`
>
> **STOP. Do NOT proceed to Step 2. Do NOT move the plan to Done. Wait for CEO confirmation before continuing.**

---
---

## STEP 2 — BELLOWS QA

---

> Before starting, read `bellows/knowledge/BACKLOG.md` and confirm the three new bullets from Step 1 are present at the top of the `## Open` section. If any are missing or malformed, stop and report before proceeding.
>
> Skip specialist file and glossary reads — this is a mechanical verification task.
>
> **Deliverable Verification (Rule 17):** Confirm the three new 2026-04-19 bullets are present in `bellows/knowledge/BACKLOG.md` directly above the existing `2026-04-18: Planner should read verdicts folder directly` bullet. Produce a verification table: `| Deliverable | Expected | Status (✅/❌) | Evidence |`. Evidence for each bullet: `grep -c "2026-04-19: scope_check false-positive"`, `grep -c "2026-04-19: deposit parser gap"`, `grep -c "2026-04-19: single-step diagnostic generates"` — each should return `1`. Deposit raw grep output to `bellows/knowledge/qa/evidence/executable-backlog-append-2026-04-19/grep_bullets.txt`.
>
> No test regression needed — documentation-only change, no code touched.
>
> **PROJECT_STATUS.md update:** Add a brief completed-milestone entry noting that 3 new BACKLOG items were captured from the plan-mutation-source diagnostic session, referencing `bellows/knowledge/research/plan-mutation-source-2026-04-19.md` as the source document.
>
> **Rule 20 self-check block** — run the standard Rule 20 Python block with:
> ```python
> plan_slug = "executable-backlog-append-2026-04-19"
> qa_report_path = "bellows/knowledge/qa/backlog-append-2026-04-19.md"
> evidence_dir = "bellows/knowledge/qa/evidence/executable-backlog-append-2026-04-19/"
> required_evidence_files = ["grep_bullets.txt"]
> ```
> Use the full template from PLANNER_TEMPLATE.md Rule 20. If the self-check prints `SELF-CHECK FAILED`, STOP and report. If it prints `SELF-CHECK PASSED`, proceed to final housekeeping.
>
> **Final housekeeping (per Rule 23, in this order):** (a) Feedback append to `bellows/knowledge/research/agent-prompt-feedback.md`. (b) Final commit: `git add bellows/knowledge/qa/ bellows/PROJECT_STATUS.md && git commit -m "chore: status + QA report for backlog-append plan"`. (c) Move plan to Done: `import shutil; shutil.move("bellows/knowledge/decisions/in-progress-executable-backlog-append-2026-04-19.md", "bellows/knowledge/decisions/Done/executable-backlog-append-2026-04-19.md")`.
>
> **Deposits:**
> - `bellows/knowledge/qa/backlog-append-2026-04-19.md`
> - `bellows/knowledge/qa/evidence/executable-backlog-append-2026-04-19/grep_bullets.txt`
> - `bellows/PROJECT_STATUS.md`
> - `bellows/knowledge/research/agent-prompt-feedback.md`
