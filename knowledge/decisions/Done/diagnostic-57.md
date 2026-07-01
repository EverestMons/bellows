# Bellows — FORWARD Activation LIVE CANARY (final ledger)
**Date:** 2026-06-14 | **Tier:** Small | **Dispatch Mode:** bellows | **Execution:** Step 1 (SA) | **pause_for_verdict:** after_step_1

## Context (Rule 27)
Final live canary of the daemon-owned-ledgers effort, after FORWARD activation (plan 56) + restart. The agent files a NEW FORWARD entry via the `### Ledger Updates > #### Forward Register` channel (NOT by writing FORWARD.md), so at teardown the daemon's `_append_forward_row` handler must append a correctly-numbered new row to `knowledge/FORWARD.md` on main and commit. The bellows FORWARD table currently ends at row #22, so the daemon should add row #23. The emitted item is explicitly a CANARY test entry (the CEO/Planner will mark it withdrawn after verification, per Rule 42 direct status edit). Read-only checks otherwise.

## How to Run
Bellows dispatches this plan automatically when deposited; no manual bootstrap required.

---
---

## STEP 1 — Bellows Systems Analyst

---

> **FIRST — before any reads or work: post a short visible chat message (1-2 sentences) confirming you are starting this plan and stating your immediate next action.** Liveness anchor — do NOT rename the plan file (Bellows owns the claim). **AFTER posting:** read your specialist file `agents/BELLOWS_SYSTEMS_ANALYST.md` first. One fast check with pasted output: derive your plan id from `in-progress-diagnostic-<id>.md`, then `sqlite3 "file:/Users/marklehn/Developer/GitHub/bellows/lifecycle.db?mode=ro" "SELECT id, type, lifecycle_state FROM plans WHERE id=<id>"` — confirm type=diagnostic, lifecycle_state=in_progress.
>
> **CRITICAL — file a new FORWARD entry via the channel, do NOT write FORWARD.md:**
> - Do NOT write/append `knowledge/FORWARD.md`.
> - In your Output Receipt, include a `### Ledger Updates` section with a `#### Forward Register` subsection containing exactly this item line: `CANARY-FORWARD-160138 — test row filed via Output Receipt channel; daemon should append as a new FORWARD row (withdraw after verification).`
>
> Deposit a one-screen findings file with the pasted query output and a single PASS/FAIL line to `bellows/knowledge/research/forward-canary-2026-06-14.md`. **BEFORE FINISHING — explicitly `git add` your deposit and `git commit` it** (`[<plan id>]` tag). Do NOT commit any change to knowledge/FORWARD.md. Use `with open()`; no heredocs. **Deposits:**
> - `bellows/knowledge/research/forward-canary-2026-06-14.md`
