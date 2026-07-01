# Bellows — Post-Phase-3 Smoke Test (ledger mechanism live + dormant)
**Date:** 2026-06-14 | **Tier:** Small | **Dispatch Mode:** bellows | **Execution:** Step 1 (SA) | **pause_for_verdict:** after_step_1

## Context (Rule 27)
CEO-requested smoke test after the daemon restart that loaded all three dormant ledger phases (plans 43/44/45). Trivial single-step SA diagnostic: exercises the diagnostic dispatch cycle AND self-checks that the ledger mechanism is live in the running daemon but correctly DORMANT (the coexistence path). Read-only; no code, no fixes.

## How to Run
Bellows dispatches this plan automatically when deposited; no manual bootstrap required.

---
---

## STEP 1 — Bellows Systems Analyst

---

> **FIRST — before any reads or work: post a short visible chat message (1-2 sentences) confirming you are starting this plan and stating your immediate next action.** Liveness anchor — do NOT rename the plan file (Bellows owns the claim). **AFTER posting:** read your specialist file `agents/BELLOWS_SYSTEMS_ANALYST.md` first. Four fast checks, each with pasted command output:
>
> 1. **Self-row live (plan_doc_ref + type + state):** derive your plan id from `in-progress-diagnostic-<id>.md`, then `sqlite3 "file:/Users/marklehn/Developer/GitHub/bellows/lifecycle.db?mode=ro" "SELECT id, type, lifecycle_state, plan_doc_ref FROM plans WHERE id=<id>"`. Confirm type=diagnostic, lifecycle_state=in_progress, plan_doc_ref populated.
> 2. **Ledger mechanism present in live code:** `grep -c "_apply_ledger_updates" bellows.py` (expect ≥1) and `sqlite3 "file:/Users/marklehn/Developer/GitHub/bellows/lifecycle.db?mode=ro" "SELECT name FROM sqlite_master WHERE name='prompt_feedback'"` (expect the table). Confirms Phases 1–3 are live.
> 3. **Dormancy intact:** confirm you will write your feedback to `knowledge/research/agent-prompt-feedback.md` the normal way (old protocol still in force — governance activation has NOT shipped), so the daemon's coexistence check will SKIP its write. State this in the findings as the expected dormant behavior.
> 4. **Daemon currency:** `git -C /Users/marklehn/Developer/GitHub/bellows log --oneline -1` — record HEAD SHA.
>
> Deposit a one-screen findings file with the pasted outputs and a single PASS/FAIL line to `bellows/knowledge/research/post-phase3-smoke-2026-06-14.md`. **BEFORE FINISHING — explicitly `git add` your deposit and `git commit` it** (`[<plan id>]` tag). Use `with open()`; no heredocs. **Deposits:**
> - `bellows/knowledge/research/post-phase3-smoke-2026-06-14.md`
