# Bellows — `PlanHandler._seen` Retry Cache Diagnostic
**Date:** 2026-05-11 | **Tier:** diagnostic | **Test Scope:** none | **Execution:** Step 1 (BELLOWS_SA) | **pause_for_verdict:** after_step_1 | **Total Steps:** 1

## How to Run This Plan

Paste the bootstrap prompt into Claude Code. The agent reads the full plan file and executes Step 1 ONLY. After completing Step 1, the agent STOPS. This is a single-step diagnostic — no Step 2. The Planner performs Rule 22 verification on the deposited findings file directly.

**Bootstrap prompt:**
```
Read the plan at bellows/knowledge/decisions/diagnostic-plan-handler-seen-retry-cache-2026-05-11.md. Execute Step 1 ONLY. After completing Step 1, STOP and wait for my confirmation. Do NOT move the plan to Done.
```

---
---

## STEP 1 — BELLOWS_SA

---

> **FIRST — before doing anything else, claim this plan:** `import shutil; shutil.move("bellows/knowledge/decisions/diagnostic-plan-handler-seen-retry-cache-2026-05-11.md", "bellows/knowledge/decisions/in-progress-diagnostic-plan-handler-seen-retry-cache-2026-05-11.md")`.
>
> You are the Bellows Systems Analyst. Skip specialist file and glossary reads — this is a code-tracing task. **Investigation only — do NOT modify any source file.** **Task:** Characterize the `PlanHandler._seen` retry cache lifecycle and produce the plumbing recommendation for the fix described in the 2026-05-06 BACKLOG entry (`bellows/knowledge/BACKLOG.md`, search for `PlanHandler._seen`). The BACKLOG entry already identifies the fix shape ("key `_seen` on plan slug + dispatch-attempt-id rather than full path string, AND clear the slug on lifecycle terminal events") and the plumbing constraint ("`PlanHandler` is owned by `Bellows.start()`'s scope and there's no clean handle to it from inside `run_plan`/`_consume_verdicts`"). This diagnostic does NOT redesign the fix — it empirically characterizes the call graph so the Planner can choose between the two plumbing options the BACKLOG entry surfaces. **Read source:** `bellows.py` only (~1,200 LOC). Do NOT read tests, do NOT read other modules. **Answer Q1 through Q6 below.** Each question is a focused empirical check with a specified output format. Cite line numbers from current code (run `git --no-pager log -1 --format=%H bellows.py` and record the SHA you read against).
>
> **Q1 — Current state map.** Locate every reference to `_seen` in `bellows.py`. For each: (a) line number, (b) operation (declare / add / read / filter), (c) the function or method the reference lives in, (d) one-line description of what the operation accomplishes. Output as a table with columns: `Line | Operation | Function | Purpose`. The BACKLOG entry cites lines 677, 686-687, 696, 807-808 as a starting set — verify these are current and find any others.
>
> **Q2 — Race-window characterization.** The BACKLOG entry asserts the dispatch-window guard is load-bearing: between `handle_new_plan` returning after `_seen.add(path)` and the eventual `shutil.move` to `in-progress-` inside `run_plan`, the plan is still at its original path with `is_runnable_plan() == True`. Trace this code path step-by-step (function call sequence with line numbers) and confirm the window exists. Identify the exact lines where the path becomes "unseen" by `is_runnable_plan` (rename to `in-progress-*` prefix). Output: numbered sequence of function calls with line ranges.
>
> **Q3 — Lifecycle terminal events and `cleanup_slug` call sites.** The BACKLOG entry asserts: "The lifecycle code already computes `cleanup_slug` for verdict cleanup at three call sites in `_consume_verdicts` (continue-to-done, halt) and in `run_plan` (auto-close); extend each to also discard the slug from `_seen`." Locate every `cleanup_slug` (or equivalent slug-computation-for-cleanup) occurrence in `bellows.py`. For each: (a) line number, (b) function, (c) the lifecycle event it follows (Done/, halted-, auto-close, etc.), (d) what cleanup operation it currently drives. Output as table. Confirm or correct the BACKLOG entry's "three call sites" assertion.
>
> **Q4 — Plumbing option (A): pass `handler` reference into `Bellows.__init__` and stash on `self`.** Examine how `PlanHandler` is currently instantiated and connected to `Bellows`. Identify: (a) the line where `PlanHandler(...)` is constructed, (b) what arguments it receives, (c) whether `Bellows` has a reference to it today, (d) which methods would need to call `self.handler._seen.discard(...)` to clear the cache on lifecycle events. List the surgical edit sites (file, line, what changes). Estimate LOC delta.
>
> **Q5 — Plumbing option (B): move `_seen` ownership onto `Bellows` and let `PlanHandler` reach into it.** Examine the alternative: `_seen` lives on `Bellows` (as `self._seen` on the orchestrator), `PlanHandler` accesses it via the orchestrator reference it already holds (verify this reference exists — if not, note it). Identify: (a) all current `PlanHandler._seen` access sites that would change to `bellows._seen` or `self._bellows._seen`, (b) the orchestrator-side reference to `Bellows` in `PlanHandler` if it exists, (c) any threading-safety concerns introduced by cross-object mutation. List the surgical edit sites. Estimate LOC delta.
>
> **Q6 — Recommendation.** Compare options (A) and (B) on three axes: (1) surgical scope (LOC + number of files touched), (2) threading safety (is the cache mutated from threads other than the watchdog thread? — characterize ownership), (3) Layer 1 invariant fit (does the option preserve the existing PlanHandler-as-event-router / Bellows-as-orchestrator separation, or blur it?). State your recommendation with a one-sentence justification per axis. The Planner will make the final call, but your recommendation is the starting point.
>
> **Deposits:**
> - `bellows/knowledge/research/plan-handler-seen-retry-cache-2026-05-11.md`
>
> Standard prompt feedback protocol → `bellows/knowledge/research/agent-prompt-feedback.md`.
>
> **STOP. Do NOT move the plan to Done. The Planner performs Rule 22 verification on the findings file and authorizes closure.**
