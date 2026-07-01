# Bellows — Post-Dashboard Pipeline Smoke Test
**Date:** 2026-06-12 | **Tier:** Small | **Dispatch Mode:** bellows | **Execution:** Step 1 (SA) | **pause_for_verdict:** after_step_1

## Context (Rule 27)
CEO-requested smoke test of the full Bellows dispatch pipeline after today's 27-plan run and the dashboard cutover (daemon now runs as the dashboard's child, PID started 2026-06-12 ~22:58). This is a deliberately trivial single-step diagnostic whose VALUE is the act of being dispatched: it exercises claim → id-mint → in_progress write (plan 22) → dispatch → gate → verdict → close, and it should appear live in the running dashboard's IN-FLIGHT pane while executing. It also self-checks that today's shipped artifacts are present. Read-only only; no code, no fixes.

## How to Run
Bellows dispatches this plan automatically when deposited; no manual bootstrap required.

---
---

## STEP 1 — Bellows Systems Analyst

---

> **FIRST — before any reads or work: post a short visible chat message (1-2 sentences) confirming you are starting this plan and stating your immediate next action.** Liveness anchor — do NOT rename the plan file (Bellows owns the claim). **AFTER posting:** read your specialist file `agents/BELLOWS_SYSTEMS_ANALYST.md` first. This is a fast smoke test — four mechanical checks, each with pasted command output:
>
> 1. **Self-row in_progress (plan 22 live):** derive your own plan id from your bootstrap (`in-progress-diagnostic-<id>.md`), then `sqlite3 "file:/Users/marklehn/Developer/GitHub/bellows/lifecycle.db?mode=ro" "SELECT id, type, lifecycle_state FROM plans WHERE id=<id>"` — confirm it reads `in_progress` while you run (the plan-22 intermediate-state write).
> 2. **Today's ships present:** `ls -la status.py dashboard.py` — confirm both exist (plans 32, 33).
> 3. **Daemon code currency:** `git log --oneline -1` — record the HEAD SHA the dispatching daemon is running.
> 4. **Registers intact:** `grep -c '^| [0-9]' knowledge/FORWARD.md` — record the open-row count (sanity that the register survived the day).
>
> Deposit a one-screen findings file with the four pasted outputs and a single PASS/FAIL line to `bellows/knowledge/research/pipeline-smoke-2026-06-12.md`. **BEFORE FINISHING — explicitly `git add` your deposit and `git commit` it** (`[<plan id>]` tag). Use `with open()`; no heredocs. **Deposits:**
> - `bellows/knowledge/research/pipeline-smoke-2026-06-12.md`
