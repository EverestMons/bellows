# Bellows — Ledger Fix RE-CANARY (multi-turn extraction live)
**Date:** 2026-06-14 | **Tier:** Small | **Dispatch Mode:** bellows | **Execution:** Step 1 (SA) | **pause_for_verdict:** after_step_1

## Context (Rule 27)
Re-canary after the ledger-extraction fix (plan 54) + restart. The original canary (plan 52) silently dropped both ledgers because the parser only read the final result message (multi-turn agents emit the Output Receipt in an intermediate turn). The fix concatenates all assistant-turn text. This re-canary proves it live: the agent emits BOTH `#### Project Status` and `#### Prompt Feedback` via the channel (writing NEITHER file), and at teardown the daemon must (a) record feedback to `prompt_feedback` (with NON-EMPTY agent column), (b) append the milestone to PROJECT_STATUS.md, and (c) log the ledger application — no silent drop. Read-only checks otherwise.

## How to Run
Bellows dispatches this plan automatically when deposited; no manual bootstrap required.

---
---

## STEP 1 — Bellows Systems Analyst

---

> **FIRST — before any reads or work: post a short visible chat message (1-2 sentences) confirming you are starting this plan and stating your immediate next action.** Liveness anchor — do NOT rename the plan file (Bellows owns the claim). **AFTER posting:** read your specialist file `agents/BELLOWS_SYSTEMS_ANALYST.md` first. One fast check with pasted output: derive your plan id from `in-progress-diagnostic-<id>.md`, then `sqlite3 "file:/Users/marklehn/Developer/GitHub/bellows/lifecycle.db?mode=ro" "SELECT id, type, lifecycle_state FROM plans WHERE id=<id>"` — confirm type=diagnostic, lifecycle_state=in_progress. **To exercise the multi-turn fix, do your reads/check across multiple turns (this is intentional — the receipt will land in a later turn than the channel content), and emit the ledger blocks in your Output Receipt at the end.**
>
> **CRITICAL — emit BOTH channels, write NEITHER file:**
> - Do NOT write/append `PROJECT_STATUS.md` or `agent-prompt-feedback.md`.
> - In your Output Receipt, include a `### Ledger Updates` section with:
>   - `#### Project Status`: `CANARY-PROJSTATUS-153330 — milestone via channel; daemon must append to PROJECT_STATUS.md (multi-turn fix).`
>   - `#### Prompt Feedback`: `CANARY-FEEDBACK3-153330 — feedback via channel; agent column must populate.`
>
> Deposit a one-screen findings file with the pasted query output and a single PASS/FAIL line to `bellows/knowledge/research/ledger-recanary-2026-06-14.md`. **BEFORE FINISHING — explicitly `git add` your deposit and `git commit` it** (`[<plan id>]` tag). Do NOT commit any change to PROJECT_STATUS.md or agent-prompt-feedback.md. Use `with open()`; no heredocs. **Deposits:**
> - `bellows/knowledge/research/ledger-recanary-2026-06-14.md`
