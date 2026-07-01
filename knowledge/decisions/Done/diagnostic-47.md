# Bellows — Clean-Restart Smoke Test
**Date:** 2026-06-14 | **Tier:** Small | **Dispatch Mode:** bellows | **Execution:** Step 1 (SA) | **pause_for_verdict:** after_step_1

## Context (Rule 27)
CEO-requested smoke test after the clean dashboard-owned-daemon relaunch (dashboard pid 15681 + child daemon 15682, Jun 14 11:45). Trivial single-step SA diagnostic: exercises the dispatch cycle and confirms the daemon is healthy on a clean single-instance launch. Should appear live as `diagnostic #<id>` in the dashboard. Read-only; no code, no fixes.

## How to Run
Bellows dispatches this plan automatically when deposited; no manual bootstrap required.

---
---

## STEP 1 — Bellows Systems Analyst

---

> **FIRST — before any reads or work: post a short visible chat message (1-2 sentences) confirming you are starting this plan and stating your immediate next action.** Liveness anchor — do NOT rename the plan file (Bellows owns the claim). **AFTER posting:** read your specialist file `agents/BELLOWS_SYSTEMS_ANALYST.md` first. Three fast checks, each with pasted command output:
>
> 1. **Self-row live:** derive your plan id from `in-progress-diagnostic-<id>.md`, then `sqlite3 "file:/Users/marklehn/Developer/GitHub/bellows/lifecycle.db?mode=ro" "SELECT id, type, lifecycle_state, plan_doc_ref FROM plans WHERE id=<id>"`. Confirm type=diagnostic, lifecycle_state=in_progress, plan_doc_ref populated.
> 2. **Single daemon (flock guard working):** confirm exactly one `bellows.py` holds the lock — `ps aux | grep "[b]ellows.py" | wc -l` (expect 1).
> 3. **Daemon currency:** `git -C /Users/marklehn/Developer/GitHub/bellows log --oneline -1` — record HEAD SHA.
>
> Deposit a one-screen findings file with the pasted outputs and a single PASS/FAIL line to `bellows/knowledge/research/clean-restart-smoke-2026-06-14.md`. **BEFORE FINISHING — explicitly `git add` your deposit and `git commit` it** (`[<plan id>]` tag). Use `with open()`; no heredocs. **Deposits:**
> - `bellows/knowledge/research/clean-restart-smoke-2026-06-14.md`
