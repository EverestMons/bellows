# Bellows — FORWARD Final Re-Canary (clean row after over-capture fix)
**Date:** 2026-06-14 | **Tier:** Small | **Dispatch Mode:** bellows | **Execution:** Step 1 (SA) | **pause_for_verdict:** after_step_1

## Context (Rule 27)
Final FORWARD canary after the over-capture fix (plan 62) + restart. Prior re-canary (plan 61) appended but produced a MALFORMED row because the parser over-captured trailing prose into the item, splitting the table row. Plan 62 tightened subsection capture (stop at blank line) and single-lines the FORWARD item. This canary proves the FORWARD ledger lands a CLEAN single-line 7-pipe row: the agent files a new FORWARD entry via the `### Ledger Updates > #### Forward Register` channel (NOT by writing FORWARD.md) AND deliberately includes trailing prose after the block (to exercise the over-capture fix). At teardown the daemon's `_append_forward_row` must append a well-formed row #24 (table currently ends at #23) — single line, exactly 7 pipes, containing only the item (no trailing prose). The item is a CANARY test row. Read-only checks otherwise.

## How to Run
Bellows dispatches this plan automatically when deposited; no manual bootstrap required.

---
---

## STEP 1 — Bellows Systems Analyst

---

> **FIRST — before any reads or work: post a short visible chat message (1-2 sentences) confirming you are starting this plan and stating your immediate next action.** Liveness anchor — do NOT rename the plan file (Bellows owns the claim). **AFTER posting:** read your specialist file `agents/BELLOWS_SYSTEMS_ANALYST.md` first. One fast check with pasted output: derive your plan id from `in-progress-diagnostic-<id>.md`, then `sqlite3 "file:/Users/marklehn/Developer/GitHub/bellows/lifecycle.db?mode=ro" "SELECT id, type, lifecycle_state FROM plans WHERE id=<id>"` — confirm type=diagnostic, lifecycle_state=in_progress.
>
> **CRITICAL — file a new FORWARD entry via the channel, do NOT write FORWARD.md, and DO add trailing prose after the block (to test the over-capture fix):**
> - Do NOT write/append `knowledge/FORWARD.md`.
> - In your Output Receipt, include a `### Ledger Updates` section with a `#### Forward Register` subsection containing exactly this single item line: `CANARY-FORWARD3-182555 — clean-row test after over-capture fix; daemon should append one well-formed single-line FORWARD row (withdraw after verification).`
> - AFTER that subsection, deliberately write a blank line and then a sentence of trailing prose (e.g. "All checks complete; closing out.") so the over-capture fix is exercised — the daemon must NOT include this prose in the row.
>
> Deposit a one-screen findings file with the pasted query output and a single PASS/FAIL line to `bellows/knowledge/research/forward-final-canary-2026-06-14.md`. **BEFORE FINISHING — explicitly `git add` your deposit and `git commit` it** (`[<plan id>]` tag). Do NOT commit any change to knowledge/FORWARD.md. Use `with open()`; no heredocs. **Deposits:**
> - `bellows/knowledge/research/forward-final-canary-2026-06-14.md`
