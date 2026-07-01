# Bellows — Diagnostic Pipeline Smoke Test (plan_doc_ref + type-label live check)
**Date:** 2026-06-13 | **Tier:** Small | **Dispatch Mode:** bellows | **Execution:** Step 1 (SA) | **pause_for_verdict:** after_step_1

## Context (Rule 27)
CEO-requested diagnostic smoke test. Trivial single-step SA diagnostic whose value is being dispatched: it exercises the diagnostic claim → id-mint → in_progress write → dispatch → gate → verdict → close cycle, and should appear live in the dashboard as `diagnostic #<id>` (the type-label ship, plan 36). It also self-checks two recent ships from inside the run: its own `plan_doc_ref` (plan 37) and the type-qualified id. Read-only; no code, no fixes.

## How to Run
Bellows dispatches this plan automatically when deposited; no manual bootstrap required.

---
---

## STEP 1 — Bellows Systems Analyst

---

> **FIRST — before any reads or work: post a short visible chat message (1-2 sentences) confirming you are starting this plan and stating your immediate next action.** Liveness anchor — do NOT rename the plan file (Bellows owns the claim). **AFTER posting:** read your specialist file `agents/BELLOWS_SYSTEMS_ANALYST.md` first. Three fast checks, each with pasted command output:
>
> 1. **Self-row is a diagnostic in_progress, with plan_doc_ref live:** derive your own plan id from your bootstrap (`in-progress-diagnostic-<id>.md`), then `sqlite3 "file:/Users/marklehn/Developer/GitHub/bellows/lifecycle.db?mode=ro" "SELECT id, type, lifecycle_state, plan_doc_ref FROM plans WHERE id=<id>"`. Confirm type=`diagnostic`, lifecycle_state=`in_progress`, and plan_doc_ref shows `knowledge/decisions/in-progress-diagnostic-<id>.md` — i.e. the plan-37 writer populated your own row live during a diagnostic claim.
> 2. **Daemon code currency:** `git -C /Users/marklehn/Developer/GitHub/bellows log --oneline -1` — record the HEAD SHA the dispatching daemon is running.
> 3. **Type-label render:** `python3 /Users/marklehn/Developer/GitHub/bellows/status.py` — confirm the IN-FLIGHT line for your own plan reads `diagnostic #<id>` (the plan-36 label ship). Paste the IN-FLIGHT section.
>
> Deposit a one-screen findings file with the three pasted outputs and a single PASS/FAIL line to `bellows/knowledge/research/diagnostic-smoke-2026-06-13.md`. **BEFORE FINISHING — explicitly `git add` your deposit and `git commit` it** (`[<plan id>]` tag). Use `with open()`; no heredocs. **Deposits:**
> - `bellows/knowledge/research/diagnostic-smoke-2026-06-13.md`
