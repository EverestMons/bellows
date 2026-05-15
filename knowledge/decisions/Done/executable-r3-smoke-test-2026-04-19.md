# Bellows — R3 Smoke Test: Shadow Cache Prompt Validation
**Date:** 2026-04-19 | **Tier:** Small | **Test Scope:** targeted | **Execution:** Step 1 (SA) → Step 2 (SA)

**SMOKE TEST — throwaway plan.** Validates the R3 variant (c) fix (executable-r3-shadow-cache-prompt-2026-04-19, shipped earlier this session) now that Bellows has been restarted. Exercises two of the four prompt construction sites in `bellows.py`: line 247 (fresh Step 1 dispatch) via Step 1, and line 303 (continuation prompt) via Step 2. Each agent records the literal plan-file path it was told to read, giving direct evidence of which prompt variant fired.

**Success criteria:** (1) both sentinel files are deposited, (2) each sentinel contains a `.bellows-cache/` path (shadow cache), NOT a path containing `in-progress-` (mutable), (3) the plan file byte count pre/post dispatch is unchanged (byte-level proof the canonical file was untouched).

## How to Run This Plan

Deposit the file to `bellows/knowledge/decisions/`. Bellows auto-dispatches on file creation. Step 1 executes, then Step 2 via the continuation path. Final step passes all gates → Bellows auto-closes to Done. If anything trips, the verdict system posts a request per normal flow.

---
---

## STEP 1 — Bellows Systems Analyst

---

> Skip specialist file and glossary reads — this is a mechanical smoke test. Your job is to record the exact plan-file path you were told to read in the bootstrap prompt. Do this by writing a single line to a sentinel file, then report Complete.
>
> Look at the bootstrap prompt you were given. It contains a phrase like `Read the plan at <path>`. Extract that `<path>` value verbatim. Write it to `bellows/knowledge/research/_r3-smoke-step1-2026-04-19.txt` as a single line. Use the Write tool directly — no Python wrapper needed.
>
> After writing the sentinel, produce an Output Receipt with Status: Complete. Do NOT modify any other files. Do NOT read any other files. Do NOT perform any housekeeping.
>
> **Deposits:**
> - `bellows/knowledge/research/_r3-smoke-step1-2026-04-19.txt`

---
---

## STEP 2 — Bellows Systems Analyst

---

> Skip specialist file and glossary reads — this is the second half of the smoke test. Same task as Step 1: record the exact plan-file path from your bootstrap prompt to a sentinel file.
>
> Look at the bootstrap prompt you were given in THIS step (not Step 1's). It contains a phrase like `Read the plan at <path>`. Extract that `<path>` value verbatim. Write it to `bellows/knowledge/research/_r3-smoke-step2-2026-04-19.txt` as a single line. Use the Write tool directly.
>
> After writing the sentinel, produce an Output Receipt with Status: Complete. Do NOT modify any other files. Do NOT perform any housekeeping. Bellows will auto-close the plan per final-step gate evaluation.
>
> **Deposits:**
> - `bellows/knowledge/research/_r3-smoke-step2-2026-04-19.txt`
