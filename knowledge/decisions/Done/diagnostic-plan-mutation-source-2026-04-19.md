# Bellows — Diagnostic: Plan File Mutation Source
**Date:** 2026-04-19 | **Tier:** Medium | **Test Scope:** targeted | **Execution:** Step 1 (SA)
**Priority:** 10

## How to Run This Plan

Paste the bootstrap prompt into Claude Code. The agent reads the full plan file and executes Step 1 ONLY. After Step 1 completes, the agent STOPS. The Planner then reads the deposited findings file directly (Rule 22) and performs housekeeping (PROJECT_STATUS update, move-to-Done) from the Planner conversation. There is no Step 2 — this is a single-step diagnostic per Rule 22.

**Bootstrap prompt:**
```
Read the plan at bellows/knowledge/decisions/diagnostic-plan-mutation-source-2026-04-19.md. Execute Step 1 ONLY. After completing Step 1, STOP and wait for my confirmation. Do NOT move the plan to Done.
```

**Purpose:** BACKLOG #6 (plan file truncation v2) and #7 (agent rewrites plan files) both observe that plan files are truncated during execution, but it is unclear whether Bellows itself is the truncation source or whether the agent's tool use causes it. The 2026-04-18 reproduction (`diagnostic-forge-scoping-2026-04-18.md`) was truncated despite the agent's stated task being read-only investigation — suggesting Bellows may be the source. The fix shape for #6 and #7 depends entirely on this answer. This diagnostic runs a controlled reproduction that captures intermediate file states during a full Bellows dispatch-and-execute cycle to identify exactly which component mutates the plan file and when.

---
---

## STEP 1 — BELLOWS SYSTEMS ANALYST

---

> **FIRST — before doing anything else, claim this plan:** `import shutil; shutil.move("bellows/knowledge/decisions/diagnostic-plan-mutation-source-2026-04-19.md", "bellows/knowledge/decisions/in-progress-diagnostic-plan-mutation-source-2026-04-19.md")`.
>
> You are the Bellows Systems Analyst. Read your specialist file at `bellows/agents/BELLOWS_SYSTEMS_ANALYST.md` first — domain context matters for this investigation. Skip the domain glossary — this is a code-tracing and filesystem-instrumentation task.
>
> **Objective:** Identify exactly what mutates the plan file during a Bellows dispatch-and-execute cycle. The class of mutation we care about is content truncation or rewriting — anything that reduces the plan's byte count or modifies its text content between first claim and Done-move. We do NOT care about the rename operations themselves (executable- → in-progress- → verdict-pending- → Done/executable-) — those are expected. We care about writes to the file content.
>
> **Preconditions to verify BEFORE starting:** Bellows daemon is running the current code (should be post-restart as of this session). Run `ps aux | grep -i bellows` to confirm a daemon process exists. If no daemon is running, stop and report — this diagnostic requires Bellows to actively dispatch a plan. Do NOT start the daemon yourself.
>
> **Investigation — Part A: Static source analysis.** Read `bellows/bellows.py`, `bellows/runner.py`, `bellows/verdict.py`, and `bellows/gates.py`. Enumerate every code path in Bellows itself that writes to a file in `knowledge/decisions/`. For each write path, record: (a) the function name and line range, (b) the trigger condition, (c) the write mode (whole-file rewrite vs. append vs. edit), (d) whether the write targets the plan file or a sibling (verdict request, ledger, etc.), (e) whether `Write`, `Edit`, or any content-mutating tool is invoked on the plan file. Produce a table: `| Location | Function | Trigger | Write Target | Tool/Mode |`. Be exhaustive — this table is the ground truth for "what Bellows itself does to plan files."
>
> **Investigation — Part B: Agent tool configuration.** Read the Bellows runner's agent invocation code (in `runner.py` or wherever `claude -p` is invoked). Identify: (a) what tools the agent is granted access to (Read, Write, Edit, Bash, etc.), (b) whether the agent receives the plan content via file path, stdin, or inlined prompt, (c) whether the plan file is marked read-only at any point, (d) whether the agent's working directory is constrained. Record findings in the same research file.
>
> **Investigation — Part C: Controlled reproduction.** Create a dummy 2-step plan with a known structure and capture intermediate file states during execution.
>
> **C.1 — Prepare the dummy plan.** Create `bellows/knowledge/decisions/executable-plan-mutation-canary-2026-04-19.md` via `Write` tool with this exact content (the plan should be innocuous — no commits, no DB changes, no code modifications; each step just writes a sentinel file):
>
> ```
> # Bellows — Plan Mutation Canary
> **Date:** 2026-04-19 | **Tier:** Small | **Test Scope:** targeted | **Execution:** Step 1 (SA) → Step 2 (QA)
> **Priority:** 99
>
> ## How to Run This Plan
> Canary plan for BACKLOG #6/#7 investigation. Writes sentinel files only. Do NOT move to Done manually.
>
> ---
> ---
>
> ## STEP 1 — BELLOWS SYSTEMS ANALYST
> ---
>
> > Write the literal string `step1-sentinel` to `bellows/knowledge/research/_canary-step1-2026-04-19.txt` using `Write` tool. Then report Output Receipt with Status: Complete, Files Created: that one path. Do NOT read or modify any other files. Do NOT read this plan file again. **STOP. Wait for CEO confirmation.**
>
> ---
> ---
>
> ## STEP 2 — BELLOWS QA
> ---
>
> > Before starting, read `bellows/knowledge/research/_canary-step1-2026-04-19.txt` and verify it contains `step1-sentinel`. Write the literal string `step2-sentinel` to `bellows/knowledge/research/_canary-step2-2026-04-19.txt`. Report Output Receipt with Status: Complete. Move this plan to Done: `import shutil; shutil.move("bellows/knowledge/decisions/in-progress-executable-plan-mutation-canary-2026-04-19.md", "bellows/knowledge/decisions/Done/executable-plan-mutation-canary-2026-04-19.md")`.
>
> **Deposits:**
> - `bellows/knowledge/research/_canary-step1-2026-04-19.txt`
> - `bellows/knowledge/research/_canary-step2-2026-04-19.txt`
> ```
>
> Record the exact byte length of this canary plan file immediately after creation via `os.path.getsize()` — this is the baseline.
>
> **C.2 — Deploy the filesystem watcher.** Before the canary plan is dispatched, start a watcher script that logs every modification event on the canary plan file. Create `bellows/scripts/_canary_watcher.py` with this logic: use `watchdog.observers.Observer` monitoring `bellows/knowledge/decisions/` and `bellows/knowledge/decisions/Done/` non-recursively, filter events to filenames containing `plan-mutation-canary`, and for every `FileModifiedEvent`, `FileCreatedEvent`, `FileMovedEvent`, or `FileDeletedEvent`, append a timestamped line to `bellows/knowledge/research/_canary-watcher-log-2026-04-19.txt` containing: ISO8601 timestamp, event type, source path, dest path (if move), current file size via `os.path.getsize` (if file exists), and SHA-256 of current content (if file exists, truncated to first 16 hex chars). The watcher runs indefinitely; you'll stop it manually after the canary plan completes. Launch it in the background with `nohup python3 bellows/scripts/_canary_watcher.py > /tmp/canary-watcher-stdout.log 2>&1 &` and record the PID.
>
> **C.3 — Also capture a pre-dispatch git baseline.** Run `cd /Users/marklehn/Desktop/GitHub/bellows && git --no-pager log --oneline -5 -- knowledge/decisions/executable-plan-mutation-canary-2026-04-19.md` (will be empty; the file isn't committed). Instead, commit the canary plan first so we have a git baseline: `git add knowledge/decisions/executable-plan-mutation-canary-2026-04-19.md && git commit -m "diag: canary plan for BACKLOG #6/#7 investigation"`. Record the commit SHA.
>
> **C.4 — Dispatch.** Wait for Bellows to pick up the canary plan via its filesystem watcher (should happen within seconds of the canary being written, assuming `_handle` / `on_created` fires). Observe the Bellows terminal output. Do NOT paste a bootstrap prompt — Bellows auto-dispatches. If after 60 seconds the canary has not been claimed (no rename to `in-progress-`), stop and report this as a separate finding (the watcher reliability fix from earlier today may not be covering new-file creation).
>
> **C.5 — Let the cycle complete.** The canary plan is designed to run Step 1 → pause → Step 2 → close. Let Bellows dispatch both steps (entering "ok" or the equivalent confirmation at the QA-checkpoint pause if needed). Do NOT interrupt. The cycle should complete within a few minutes. If Bellows strands the plan in `verdict-pending-*` state or a gate trips, record that as a finding but let the watcher keep running until the file either lands in Done/ or you manually terminate (after waiting 10 minutes).
>
> **C.6 — Capture post-cycle state.** After the plan lands in Done/, record: (a) the final byte length of the plan file via `os.path.getsize("bellows/knowledge/decisions/Done/executable-plan-mutation-canary-2026-04-19.md")`, (b) the `git diff` between the committed baseline and the final Done/ version: `cd /Users/marklehn/Desktop/GitHub/bellows && git --no-pager diff HEAD -- knowledge/decisions/Done/executable-plan-mutation-canary-2026-04-19.md`, (c) the full watcher log.
>
> **C.7 — Stop the watcher.** Kill the watcher process via the PID recorded in C.2: `kill <PID>`. Verify the log file has captured events.
>
> **Analysis — Part D: Correlate.** Produce an event timeline by merging the watcher log events with the Bellows terminal output (copy the relevant terminal output into the findings file, or have the CEO paste it if not captured). For each modification event that changed the file's size or content hash, identify: (a) what component was active at that moment (Bellows daemon or claude -p agent), (b) what the size/hash change was, (c) whether it corresponds to a known write path from Part A's static analysis or represents an unaccounted-for write. Any unaccounted-for write is a finding that warrants follow-up. Specifically answer: is the truncation event (if any) caused by (i) Bellows's own code, (ii) the claude -p agent's tool calls, or (iii) some third actor (the runner's I/O handling, a macOS FSEvents-level coalescing artifact, etc.)?
>
> **Analysis — Part E: Hypothesis check.** The 2026-04-18 reproduction noted that a read-only diagnostic was truncated despite no Edit instructions. Three hypotheses for this class of failure, in priority order: **H1 — Bellows itself** mutates the plan file (e.g., stripping completed step sections to signal progress, updating metadata in-place). **H2 — The agent** has Edit tool access and uses it autonomously (e.g., as part of "updating the plan" behavior unrelated to explicit instructions). **H3 — The runner's I/O handling** writes a truncated stream back to disk (e.g., if `claude -p`'s output stream is ever written over the plan file path). The static analysis in Part A and the watcher log in Part C.6 should together refute or confirm each hypothesis. State explicitly which hypothesis is supported by the evidence and which are ruled out.
>
> **Deposit findings to:** `bellows/knowledge/research/plan-mutation-source-2026-04-19.md`. Use this structure: (1) Preconditions checked, (2) Part A static analysis table + summary, (3) Part B agent tool configuration findings, (4) Part C reproduction results (baseline size, watcher log summary, terminal output summary, post-cycle size, git diff), (5) Part D event timeline correlation, (6) Part E hypothesis check with verdict per hypothesis, (7) Recommendations for BACKLOG #6 / #7 fix shape based on the evidence. The recommendations section should propose concrete fix candidates for each identified mutation source (e.g., "if Bellows itself is mutating to strip completed steps, the fix is to maintain step state in bellows.db instead of the plan file"). Do NOT implement any fix — this is investigation only.
>
> **Cleanup:** After depositing findings, if the canary plan landed in Done/, leave it there. If it stranded in verdict-pending or in-progress state, rename it to `bellows/knowledge/decisions/Done/_canary-stranded-2026-04-19.md` so it doesn't interfere with future runs. Leave the watcher log at its deposited path for evidence — do NOT delete `_canary-watcher-log-2026-04-19.txt` or the sentinel files. The `_canary_watcher.py` script can be deleted once findings are deposited.
>
> Use `git --no-pager` on every git command. Standard prompt feedback protocol → `bellows/knowledge/research/agent-prompt-feedback.md`.
>
> **Deposits:**
> - `bellows/knowledge/research/plan-mutation-source-2026-04-19.md`
> - `bellows/knowledge/research/_canary-watcher-log-2026-04-19.txt`
> - `bellows/knowledge/research/_canary-step1-2026-04-19.txt`
> - `bellows/knowledge/research/_canary-step2-2026-04-19.txt`
>
> **STOP. Do NOT move the plan to Done. Wait for CEO confirmation — the Planner will read your findings directly and handle housekeeping per Rule 22.**
