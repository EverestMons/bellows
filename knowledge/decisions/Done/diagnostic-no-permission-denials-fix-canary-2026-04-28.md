# Bellows — no_permission_denials Read-Class Fix Smoke Canary (BACKLOG #2 verification)
**Date:** 2026-04-28 | **Tier:** Small | **Test Scope:** none | **Execution:** Step 1 (Bellows Systems Analyst)
**Priority:** 5

## Context

Smoke test for BACKLOG #2 fix (commit `3ca8361`). The fix shipped and was verified by 7 unit tests + behavioral check against simulated denials. This canary verifies the fix is loaded in the running Bellows daemon by reproducing the exact production trigger pattern.

The agent will invoke the Grep tool against `/Users/marklehn/Desktop/GitHub/PLANNER_TEMPLATE.md` (governance root, outside agent permission profile). Claude Code will deny each Grep call. The agent then routes around via bash to complete the actual lookup. Without the BACKLOG #2 fix, `no_permission_denials` would trip with evidence `"3 denial(s): ..."`. With the fix, the gate passes silently.

The verdict signal is in the gate result:
- **Gate passes (failures=0):** Fix is loaded. Proceed with Phase 3a continuation.
- **Gate fails with evidence containing "blocking denial":** New code is loaded but failed to filter — regression, halt and investigate.
- **Gate fails with evidence containing "denial(s)" but NOT "blocking":** Old code is still running — restart didn't take, repeat restart.

Investigation only. No code changes. No commits. Single step per Rule 22.

## How to Run This Plan

Bellows watcher claims this plan automatically. Step 1 (Bellows Systems Analyst) deliberately triggers Grep denials, completes a trivial deposit via bash, and returns. Per disable-auto-close, terminal step pauses for Planner verdict. The Planner inspects the gate result on the verdict request to confirm fix loaded.

---
---

## STEP 1 — Bellows Systems Analyst

---

> **FIRST — claim this plan:** `import shutil; shutil.move("bellows/knowledge/decisions/diagnostic-no-permission-denials-fix-canary-2026-04-28.md", "bellows/knowledge/decisions/in-progress-diagnostic-no-permission-denials-fix-canary-2026-04-28.md")`. **Skip glossary read AND skip specialist file read** — trivial canary, no domain context needed. **Task 1 — deliberate Grep denials.** Use the Grep tool (NOT bash grep) THREE times against `/Users/marklehn/Desktop/GitHub/PLANNER_TEMPLATE.md` with these patterns: (a) `Resume Protocol`; (b) `Version:`; (c) `Lessons Learned`. Each will be denied (path is outside your permission profile). This is intentional — these denials are the signal under test. **Task 2 — bash fallback for ground truth.** Run `bash grep -c "Resume Protocol" /Users/marklehn/Desktop/GitHub/PLANNER_TEMPLATE.md` and capture the count (expected: at least 1). **Task 3 — deposit canary findings.** Use `Filesystem:write_file` to deposit `bellows/knowledge/research/no-permission-denials-fix-canary-2026-04-28.md` with: (1) Statement: "BACKLOG #2 read-class fix smoke canary"; (2) Number of Grep tool invocations attempted: 3; (3) bash grep count of "Resume Protocol" in PLANNER_TEMPLATE.md: \<count from Task 2\>; (4) Statement: "If this file exists and the gate passed cleanly, the fix is loaded and filtering Grep denials correctly." **Do NOT commit anything to git.** **Standard prompt feedback protocol** → `bellows/knowledge/research/agent-prompt-feedback.md`.
>
> **Deposits:**
> - `bellows/knowledge/research/no-permission-denials-fix-canary-2026-04-28.md`
