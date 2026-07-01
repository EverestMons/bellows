# Bellows — Feedback Activation LIVE CANARY
**Date:** 2026-06-14 | **Tier:** Small | **Dispatch Mode:** bellows | **Execution:** Step 1 (SA) | **pause_for_verdict:** after_step_1

## Context (Rule 27)
First plan dispatched after the feedback-ledger activation (plan 49) + daemon restart. This is the LIVE CANARY: the agent emits its prompt feedback via the NEW `### Ledger Updates > #### Prompt Feedback` Output Receipt channel (NOT by writing agent-prompt-feedback.md), so at teardown the daemon's `_apply_ledger_updates` feedback handler must (a) record the entry to the `prompt_feedback` table and (b) regenerate `agent-prompt-feedback.md` from the DB and commit it — with NO worktree-side write and NO merge conflict. Trivial otherwise. Read-only checks; no code, no fixes.

## How to Run
Bellows dispatches this plan automatically when deposited; no manual bootstrap required.

---
---

## STEP 1 — Bellows Systems Analyst

---

> **FIRST — before any reads or work: post a short visible chat message (1-2 sentences) confirming you are starting this plan and stating your immediate next action.** Liveness anchor — do NOT rename the plan file (Bellows owns the claim). **AFTER posting:** read your specialist file `agents/BELLOWS_SYSTEMS_ANALYST.md` first. Two fast checks, each with pasted command output:
>
> 1. **Self-row live:** derive your plan id from `in-progress-diagnostic-<id>.md`, then `sqlite3 "file:/Users/marklehn/Developer/GitHub/bellows/lifecycle.db?mode=ro" "SELECT id, type, lifecycle_state FROM plans WHERE id=<id>"` — confirm type=diagnostic, lifecycle_state=in_progress.
> 2. **Activation present:** `sqlite3 "file:/Users/marklehn/Developer/GitHub/bellows/lifecycle.db?mode=ro" "SELECT name FROM sqlite_master WHERE name IN ('prompt_feedback','ledger_writes')"` (expect both).
>
> **CRITICAL — feedback via the NEW channel (this is the canary):** do NOT write or append to `knowledge/research/agent-prompt-feedback.md`. Instead, in your Output Receipt, include a `### Ledger Updates` section with a `#### Prompt Feedback` subsection containing exactly this distinctive line: `CANARY-FEEDBACK-124753 — feedback emitted via Output Receipt channel, daemon should record to prompt_feedback DB and regenerate the md.` This is what the daemon will pick up at teardown.
>
> Deposit a one-screen findings file with the two pasted outputs and a single PASS/FAIL line to `bellows/knowledge/research/feedback-canary-2026-06-14.md`. **BEFORE FINISHING — explicitly `git add` your deposit and `git commit` it** (`[<plan id>]` tag). Do NOT commit any change to agent-prompt-feedback.md (you must not touch it). Use `with open()`; no heredocs. **Deposits:**
> - `bellows/knowledge/research/feedback-canary-2026-06-14.md`
