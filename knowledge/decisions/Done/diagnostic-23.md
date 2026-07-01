# Bellows — Partial-Output Loss on Inactivity-Timeout Kill (Design Diagnostic)
**Date:** 2026-06-12 | **Tier:** Small | **Dispatch Mode:** bellows | **Execution:** Step 1 (SA) | **pause_for_verdict:** after_step_1

## Context (Rule 27)
FORWARD row 18 (`knowledge/FORWARD.md`; verbose context in `knowledge/BACKLOG-ARCHIVE.md`, entry "Added 2026-06-11"): when the runner kills a stalled step (inactivity timeout, no output for the configured window), the step JSON lands with empty `raw_output` — plan 1's ~2 minutes of pre-stall output were lost on 2026-06-11, leaving zero forensics for the very failure class where forensics matter most. The runner DOES stream output incrementally for its elapsed-time logging (the `last output Ns ago` lines prove a reader thread sees the stream), so the data transits memory and is discarded on the kill path. This diagnostic designs the fix: where the buffer lives, why the kill path drops it, and the minimal change to persist it. Investigation ONLY — author no fix code. Anchors as of today: `runner.py::run_step` at line 34; `raw_output` writes at runner.py:192/231/256/280 (several already truncate to 5000 chars — note which paths) — re-verify by grep, never trust line numbers.

## How to Run
Bellows dispatches this plan automatically when deposited; no manual bootstrap required.

---
---

## STEP 1 — Bellows Systems Analyst

---

> **FIRST — before any reads or work: post a short visible chat message (1-2 sentences) confirming you are starting this plan and stating your immediate next action.** Liveness anchor — do NOT rename the plan file (Bellows owns the claim). **AFTER posting:** read your specialist file `agents/BELLOWS_SYSTEMS_ANALYST.md` first. **Post a 1-line "Read X." after each file read and a 1-line "Drafting Section N." at the start of each section.** Ground every claim at file:line.
>
> **Section 1 — Stream lifecycle anatomy.** Read `runner.py` in full. Document at file:line: how the subprocess's stdout/stderr are consumed (reader thread, buffer variable, line accumulation); how the inactivity timer is fed by the reader; the EXACT kill path on timeout (what is killed, in what order, and what happens to the accumulated buffer variable); and every `raw_output` write site with its truncation behavior (which paths cap at 5000 chars, which don't, and what the timeout path writes — empty? partial? nothing?). Name the precise line where the pre-stall output is lost.
>
> **Section 2 — Evidence reconciliation.** Locate plan 1's timeout-killed step JSON from 2026-06-11 (logs/ rotation permitting — if rotated out, say so and reconstruct from the daemon log instead). Confirm what `raw_output` actually contained, and cross-check the daemon log's `runner: Ns elapsed, last output Ns ago` lines to estimate how much output was produced before the stall. State the loss precisely.
>
> **Section 3 — Fix shapes.** Propose and compare at least: (a) persist the accumulated buffer on the kill path (write whatever the reader collected into the step JSON before returning the timeout result — likely a few lines); (b) incremental spill — reader appends to a per-step `.partial` file as it reads, deleted on clean completion, retained on kill; (c) both. For each: crash-safety (does a daemon crash mid-step lose it anyway?), disk behavior, truncation policy consistency with the existing 5000-char convention (and whether that cap is itself right for forensics — recommend keep/raise/structure), and blast radius at file:line. Recommend one shape.
>
> **Section 4 — Gap Assessment + `### Verification Blocks` (Rule 39).** Gap Assessment table `| Gap | Current State (file:line) | Proposed State | Change Required |` for the fix executable. Verification Blocks with `(claim, query, expected_output)` triples for: the buffer-loss line, the timeout-path `raw_output` content, and the truncation-behavior census. Close with **CEO decision forks** (each with a recommendation): fix shape (a)/(b)/(c); truncation policy for the persisted partial output.
>
> **BEFORE FINISHING — explicitly `git add` your deposit file and `git commit` it.** Use `with open()` for the deposit; no heredocs. Standard prompt feedback → `knowledge/research/agent-prompt-feedback.md`. **Deposits:**
> - `bellows/knowledge/research/partial-output-timeout-loss-2026-06-12.md`
