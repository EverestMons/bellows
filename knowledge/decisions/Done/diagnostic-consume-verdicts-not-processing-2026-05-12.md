# Bellows — `_consume_verdicts` Pending Verdicts Not Processing
**Date:** 2026-05-12 | **Tier:** Diagnostic | **Test Scope:** n/a (investigation) | **Execution:** Step 1 (SA) | **pause_for_verdict:** after_step_1

## How to Run This Plan

Paste the bootstrap prompt into Claude Code. The agent reads the full plan file and executes Step 1 ONLY. After completing Step 1, the agent STOPS and waits for CEO confirmation ("ok") before the Planner advances to closeout.

## CEO Context

Two Planner-deposited continue verdicts are sitting in `bellows/verdicts/pending/` and have not been consumed by the running daemon despite a daemon restart at 13:49:27 and at least two heartbeat cycles since (13:54:30 and 13:59:31, both reporting "5 awaiting verdict"). The verdict files were rewritten at 13:55 to match the format of recently-consumed verdicts in `resolved/processed-verdict-*.md` (plain `verdict: continue` first line, no markdown decoration).

**Files in `bellows/verdicts/pending/`:**
- `verdict-bellows-self-exposure-disposition-2026-05-12-step-1.md` (Planner-deposited continue verdict)
- `verdict-bellows-self-exposure-wontfix-close-2026-05-12-step-1.md` (Planner-deposited continue verdict)
- `verdict-request-action-queue-aggregation-2026-05-07-step-1.md` (stranded request, ~5 days old)
- `verdict-request-action-queue-aggregation-2026-05-07-step-3.md` (stranded request, ~5 days old)
- `verdict-request-bellows-self-exposure-disposition-2026-05-12-step-1.md` (today's request)
- `verdict-request-bellows-self-exposure-wontfix-close-2026-05-12-step-1.md` (today's request)
- `verdict-request-session-wrap-2026-05-08-step-1.md` (stranded request, ~3 days old)

**Plan files in `bellows/knowledge/decisions/`:**
- `verdict-pending-diagnostic-bellows-self-exposure-disposition-2026-05-12.md`
- `verdict-pending-executable-bellows-self-exposure-wontfix-close-2026-05-12.md`

**Daemon health:** PID 76157, started 13:49:27, heartbeating cleanly, module fingerprints from current commits (`bellows.py @ git:07a87ad`, `gates.py @ git:0fab609`, `parser.py @ git:1d1dabf`, `runner.py @ git:b11ecc4`, `verdict.py @ git:0fab609`). No errors in log.

**Verdict file properties:** UTF-8, plain LF newlines, no BOM, 590–606 bytes, owned by marklehn:staff, mode 644, identical type signature to the consumed example at `resolved/processed-verdict-terminal-notification-backlog-close-2026-05-12-step-2.md`.

Investigate why `_consume_verdicts` (or the equivalent function in current `bellows.py @ git:07a87ad`) is not processing these files. The Planner has exhausted format-and-permission-side hypotheses and needs an architectural answer.

---
---

## STEP 1 — SA

---

> **FIRST — before doing anything else, claim this plan:** `import shutil; shutil.move("/Users/marklehn/Desktop/GitHub/bellows/knowledge/decisions/diagnostic-consume-verdicts-not-processing-2026-05-12.md", "/Users/marklehn/Desktop/GitHub/bellows/knowledge/decisions/in-progress-diagnostic-consume-verdicts-not-processing-2026-05-12.md")`.
>
> You are the Bellows Systems Analyst. Read your specialist file at `bellows/agents/BELLOWS_SYSTEMS_ANALYST.md` first. Skip the domain glossary — Bellows has no glossary and this is an architectural debugging task. **Investigate four questions and deposit findings. Do not propose plans, do not fix anything, do not modify any source.** **Q1 — What triggers `_consume_verdicts`?** Read the current `bellows/bellows.py` and identify every call site of `_consume_verdicts` (or any equivalent verdict-processing function). For each call site, state: (i) what triggers it (startup, heartbeat tick, file-watcher event, plan-completion event, other), (ii) the conditional guards that gate the call, (iii) the function's expected filename pattern for verdict files (literal regex or `startswith` check). Cite line numbers. **Q2 — Does the current code match Planner-deposited verdict files?** The two pending files are `verdict-bellows-self-exposure-disposition-2026-05-12-step-1.md` and `verdict-bellows-self-exposure-wontfix-close-2026-05-12-step-1.md`. The corresponding plans are at `verdict-pending-diagnostic-bellows-self-exposure-disposition-2026-05-12.md` and `verdict-pending-executable-bellows-self-exposure-wontfix-close-2026-05-12.md`. Trace through the consumer's filename-to-plan matching logic against these specific filename pairs and identify exactly which check (if any) returns False or otherwise causes the file to be skipped. Cite the line where the rejection happens. **Q3 — Why didn't startup sweep consume them?** The daemon restarted at 13:49:27 and the first heartbeat at 13:54:30 reported "5 awaiting verdict" — the same count as pre-restart. Either (a) the startup sweep does not call `_consume_verdicts`, (b) it calls it but the consumer rejects the files for the reason in Q2, or (c) it calls it before some required state is initialized. Identify which. Cite the relevant function (`_perform_startup_sweep` per the 2026-05-10 startup-sweep-extract close, or its current name) and the relevant line numbers. **Q4 — Recommendation.** Given Q1–Q3, state the corrective action as one of: (i) the verdict files need to be renamed or rewritten in a specific way (state what), (ii) the daemon needs to be restarted with a specific precondition met (state what), (iii) there is a code defect in the consumer logic (describe the defect and identify the fix shape — Planner will route to a separate executable), (iv) something else (explain). Also include a "Layer Impact" section per your specialist output convention. Deposit findings to `/Users/marklehn/Desktop/GitHub/bellows/knowledge/architecture/consume-verdicts-not-processing-2026-05-12.md`. **Deposits:** `- /Users/marklehn/Desktop/GitHub/bellows/knowledge/architecture/consume-verdicts-not-processing-2026-05-12.md`. Standard prompt feedback protocol → `bellows/knowledge/research/agent-prompt-feedback.md`. Commit with message: `docs: SA findings — _consume_verdicts not processing pending verdicts 2026-05-12`.
>
> **STOP. Do NOT proceed to any further step. Do NOT move the plan to Done. Wait for CEO confirmation before continuing.**

---
