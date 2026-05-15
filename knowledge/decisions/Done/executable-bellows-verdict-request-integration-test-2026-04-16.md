# Bellows — Agent Self-Request Verdict Integration Test
**Date:** 2026-04-16 | **Tier:** Small | **Test Scope:** none | **Execution:** Step 1 (DEV) → Step 2 (DEV)

## Purpose

End-to-end validation that an agent can trigger a verdict pause by outputting `VERDICT_REQUESTED: <reason>` in its conversation output. Unit tests for the parser and gate exist (shipped today), but the full signal path (agent output → runner.run_step parsing → gates.check detection → run_plan verdict pause) has never been exercised in a real Bellows-dispatched plan. This plan is a throwaway test — it does no real work.

## How to Run This Plan

**Bootstrap:**
```
Read the plan at bellows/knowledge/decisions/executable-bellows-verdict-request-integration-test-2026-04-16.md. Execute Step 1 ONLY. After completing Step 1, STOP and wait for CEO confirmation before proceeding.
```

---
---

## STEP 1 — DEV (trigger the self-request)

---

> **FIRST — claim this plan:** `import shutil; shutil.move("/Users/marklehn/Desktop/GitHub/bellows/knowledge/decisions/executable-bellows-verdict-request-integration-test-2026-04-16.md", "/Users/marklehn/Desktop/GitHub/bellows/knowledge/decisions/in-progress-executable-bellows-verdict-request-integration-test-2026-04-16.md")`. **This step is an integration test, not real work.** Your job is to output the verdict-request marker string so Bellows can detect it. After doing the trivial task below, output the marker on its own line. **Trivial task:** Create a file at `/Users/marklehn/Desktop/GitHub/bellows/knowledge/research/verdict-request-integration-test-2026-04-16.md` containing `# Integration Test\nThis file confirms the agent self-request verdict signal path works end-to-end.\nDate: 2026-04-16`. Commit: `cd /Users/marklehn/Desktop/GitHub/bellows && git add knowledge/research/verdict-request-integration-test-2026-04-16.md && git commit -m "test: verdict request integration test artifact"`. **Then output the following line EXACTLY, on its own line, not inside a code block:**
>
> VERDICT_REQUESTED: Integration test — verifying agent self-request verdict signal path works end-to-end through Bellows.
>
> **After outputting the marker, stop. Do not proceed to Step 2.**

---
---

## STEP 2 — DEV (confirm and clean up)

---

> **If you are reading this, the verdict-request signal path worked** — Bellows paused after Step 1 because it detected your `VERDICT_REQUESTED:` output, and the CEO issued a `continue` verdict to resume. **Confirm:** Read the verdict request file that Bellows posted to `bellows/verdicts/pending/` for this plan's Step 1. It should contain a `Pause Reason: Agent verdict request` section (or similar). Report what you find. **Clean up:** Delete the test artifact: `cd /Users/marklehn/Desktop/GitHub/bellows && git rm knowledge/research/verdict-request-integration-test-2026-04-16.md && git commit -m "test: clean up verdict request integration test artifact"`. **Deposit:** Write a short summary to `/Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/verdict-request-integration-test-2026-04-16.md` confirming: (a) Step 1 agent outputted `VERDICT_REQUESTED:` marker, (b) Bellows paused the plan with an agent_verdict_request pause reason, (c) continue verdict resumed execution to Step 2, (d) full signal path validated. Commit: `git add knowledge/qa/verdict-request-integration-test-2026-04-16.md && git commit -m "test: verdict request integration test — PASSED"`. Move plan to Done: `import shutil; shutil.move("/Users/marklehn/Desktop/GitHub/bellows/knowledge/decisions/in-progress-executable-bellows-verdict-request-integration-test-2026-04-16.md", "/Users/marklehn/Desktop/GitHub/bellows/knowledge/decisions/Done/executable-bellows-verdict-request-integration-test-2026-04-16.md")`.
>
> **STOP. Plan complete after this step.**
