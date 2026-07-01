# Bellows — PROJECT_STATUS Activation LIVE CANARY
**Date:** 2026-06-14 | **Tier:** Small | **Dispatch Mode:** bellows | **Execution:** Step 1 (SA) | **pause_for_verdict:** after_step_1

## Context (Rule 27)
First plan after the PROJECT_STATUS activation (plan 51) + daemon restart. LIVE CANARY: the agent emits a PROJECT_STATUS milestone via the NEW `### Ledger Updates > #### Project Status` channel (NOT by writing PROJECT_STATUS.md), so at teardown the daemon's `_append_project_status` handler must append it to `PROJECT_STATUS.md` on main at the canonical position and commit — no worktree write, no conflict. Also re-checks the agent-column rider (plan 51): this plan's feedback (emitted via channel) should land in `prompt_feedback` with a NON-EMPTY agent column. Read-only checks otherwise; no code.

## How to Run
Bellows dispatches this plan automatically when deposited; no manual bootstrap required.

---
---

## STEP 1 — Bellows Systems Analyst

---

> **FIRST — before any reads or work: post a short visible chat message (1-2 sentences) confirming you are starting this plan and stating your immediate next action.** Liveness anchor — do NOT rename the plan file (Bellows owns the claim). **AFTER posting:** read your specialist file `agents/BELLOWS_SYSTEMS_ANALYST.md` first. One fast check with pasted output: derive your plan id from `in-progress-diagnostic-<id>.md`, then `sqlite3 "file:/Users/marklehn/Developer/GitHub/bellows/lifecycle.db?mode=ro" "SELECT id, type, lifecycle_state FROM plans WHERE id=<id>"` — confirm type=diagnostic, lifecycle_state=in_progress.
>
> **CRITICAL — emit BOTH ledger channels, write NEITHER file (this is the canary):**
> - Do NOT write/append `PROJECT_STATUS.md` or `agent-prompt-feedback.md`.
> - In your Output Receipt, include a `### Ledger Updates` section with:
>   - a `#### Project Status` subsection containing exactly: `CANARY-PROJSTATUS-134417 — milestone emitted via Output Receipt channel; daemon should append to PROJECT_STATUS.md post-merge.`
>   - a `#### Prompt Feedback` subsection containing exactly: `CANARY-FEEDBACK2-134417 — feedback via channel; agent column should be populated.`
>
> Deposit a one-screen findings file with the pasted query output and a single PASS/FAIL line to `bellows/knowledge/research/projstatus-canary-2026-06-14.md`. **BEFORE FINISHING — explicitly `git add` your deposit and `git commit` it** (`[<plan id>]` tag). Do NOT commit any change to PROJECT_STATUS.md or agent-prompt-feedback.md. Use `with open()`; no heredocs. **Deposits:**
> - `bellows/knowledge/research/projstatus-canary-2026-06-14.md`
