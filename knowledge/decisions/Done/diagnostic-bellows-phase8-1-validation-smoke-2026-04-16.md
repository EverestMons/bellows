# Bellows — Phase 8.1 Validation Smoke Test
**Date:** 2026-04-16 | **Type:** Diagnostic

## Context

Phase 8.1 shipped five minutes ago: the final-step gate check in bellows.py now fires on `not effective_auto_close`, which means clean single-step diagnostics with no YAML header should pause for verdict instead of stranding. Last night's `_parse_diff_stat` audit demonstrated the stranding bug. This diagnostic has no YAML header (triggering the diagnostic-default pause behavior) and does trivial safe work (one file read, one short deposit).

**Expected Bellows behavior:** detect plan → run step 1 (agent reads bellows.py, deposits findings, reports Complete) → gates pass clean → final-step check fires on `not effective_auto_close` → verdict request posted to `bellows/verdicts/pending/` → Pushover notification → plan renamed `verdict-pending-*` → plan sits waiting for CEO verdict.

**Failure modes to watch for:** (1) plan strands (Phase 8.1 didn't fix the bug), (2) plan auto-closes to Done (effective_auto_close evaluated wrong for diagnostics), (3) agent modifies files outside scope (scope_check false positive would mask the test signal).

## How to Run

Bellows picks this up from the watched decisions folder. No bootstrap needed — the test is watching Bellows' behavior.

---
---

## STEP 1 — DEV (Bellows Developer)

---

> Skip specialist file and glossary reads. Working directory: `/Users/marklehn/Desktop/GitHub/bellows`. **Claim the plan:** `import shutil; shutil.move("/Users/marklehn/Desktop/GitHub/bellows/knowledge/decisions/diagnostic-bellows-phase8-1-validation-smoke-2026-04-16.md", "/Users/marklehn/Desktop/GitHub/bellows/knowledge/decisions/in-progress-diagnostic-bellows-phase8-1-validation-smoke-2026-04-16.md")`. **Task:** answer one question. Read `bellows.py` and locate the `header_says_pause` function. Report its four return branches — what values of `pause_for_verdict` cause it to return True and what it returns otherwise. Nothing else. No source fixes, no test runs, no additional investigation. **Deposit** a short findings file at `/Users/marklehn/Desktop/GitHub/bellows/knowledge/research/bellows-phase8-1-validation-smoke-2026-04-16.md` with the question, the four return branches, and an Output Receipt with Status=Complete. **Feedback append** to `/Users/marklehn/Desktop/GitHub/bellows/knowledge/research/agent-prompt-feedback.md` per protocol. **Commit:** `cd /Users/marklehn/Desktop/GitHub/bellows && git add knowledge/research/bellows-phase8-1-validation-smoke-2026-04-16.md knowledge/research/agent-prompt-feedback.md && git commit -m "diagnostic: phase 8.1 validation smoke"`. **Do NOT move the plan to Done — closure is handled by Planner verdict per Phase 8 default behavior.**
