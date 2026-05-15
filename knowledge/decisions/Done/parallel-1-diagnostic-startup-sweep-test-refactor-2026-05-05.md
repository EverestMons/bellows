# Bellows — Diagnostic: Startup Sweep Test Refactor Surface
**Date:** 2026-05-05 | **Tier:** Small | **Test Scope:** targeted | **Execution:** Step 1 (Bellows Developer)

## How to Run This Plan

Paste the bootstrap prompt into Claude Code. The agent reads the full plan file and executes Step 1 ONLY. After completing Step 1, the agent STOPS and waits for CEO confirmation. The agent does NOT move the plan to Done — the Planner performs the Done/ move after Rule 22 verification on the deposited findings.

Bootstrap prompt:
```
Read the plan at bellows/knowledge/decisions/parallel-1-diagnostic-startup-sweep-test-refactor-2026-05-05.md. Execute Step 1 ONLY. After completing Step 1, STOP and wait for my confirmation. Do NOT proceed beyond Step 1. Do NOT move the plan to Done.
```

---
---

## STEP 1 — Bellows Developer

---

> **FIRST — before doing anything else, claim this plan:** `import shutil; shutil.move("bellows/knowledge/decisions/parallel-1-diagnostic-startup-sweep-test-refactor-2026-05-05.md", "bellows/knowledge/decisions/in-progress-parallel-1-diagnostic-startup-sweep-test-refactor-2026-05-05.md")`. Skip specialist file and glossary reads — this is a code-tracing and refactor-scoping task. You are the Bellows Developer. **Context:** BACKLOG entry 2026-05-01 notes that `test_startup_sweep_removes_done_plan_orphans` (the regression test for the cleanup-slug-normalization fix shipped 2026-05-01 via commit `bc09bb5`) replicates the production startup-sweep collection-and-removal logic inline in the test file rather than calling `Bellows.start()` and patching the observer/event-loop apparatus. The BACKLOG entry hypothesizes the fix is a ~10 LOC refactor extracting a `_perform_startup_sweep()` private method on `Bellows` that both `start()` and the test can call. Investigate whether that hypothesis holds. **Investigation tasks:** (1) Locate the test in question — search `bellows/tests/` for the test name `test_startup_sweep_removes_done_plan_orphans` and `test_cleanup_normalizes_prefixed_verdict_slug` (the bug-regression test cited in the BACKLOG entry as exercising production code directly). Report which file each lives in. (2) Read the inline-replicated test logic for the orphan-removal test in full — quote the exact lines that constitute the replicated logic. (3) Locate the production startup sweep in `bellows.py` — find the corresponding code path inside `Bellows.start()` (or wherever `start()` calls it). Quote the exact lines. (4) Compare the two: enumerate every divergence between the test's inline replica and the production code. Identify any production behavior the test does NOT replicate (mocks, side effects, ordering, error handling). (5) Sketch the refactor: what would `_perform_startup_sweep(self)` need as a signature? What dependencies (db, paths, watched_projects, observer state) would it need access to as `self.*` attributes vs parameters? Would the production `start()` call site become a single-line invocation, or are there mid-sweep observer-setup steps that prevent clean extraction? (6) Validate the LOC estimate: is the refactor really ~10 LOC, or is it larger because of dependency wiring? (7) Identify any test-side adjustments needed: would the test need to construct a `Bellows` instance and patch its dependencies, or can it call the static refactor target with manual fixtures? (8) Surface any risks not anticipated by the BACKLOG entry — for example, if `start()` does work BEFORE the sweep that the sweep depends on, extraction may not be straightforward. Deposit findings to `bellows/knowledge/research/startup-sweep-test-refactor-surface-2026-05-05.md` using `Filesystem:write_file`. Format: numbered sections (1) Test locations and content, (2) Production sweep location and content, (3) Divergences enumerated, (4) Refactor sketch with proposed signature and call-site changes, (5) LOC estimate (revised), (6) Test-side migration cost, (7) Risks and unanticipated complications, (8) Recommendation: proceed with refactor / defer / abandon (with reasoning). Standard prompt feedback protocol → `bellows/knowledge/research/agent-prompt-feedback.md`. **Deposits:**
> - `bellows/knowledge/research/startup-sweep-test-refactor-surface-2026-05-05.md`
>
> **STOP. Do NOT proceed beyond Step 1. Do NOT move the plan to Done. Wait for CEO confirmation.**
