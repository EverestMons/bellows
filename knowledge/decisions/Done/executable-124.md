# Bellows — Gates-122 Reload Canary (parenthetical-strip discriminator)
**Date:** 2026-07-02 | **Tier:** Small | **Dispatch Mode:** bellows | **Test Scope:** targeted | **Execution:** Step 1 (DEV) | **pause_for_verdict:** always

## CEO Context

Daemon relaunched 2026-07-02 19:10 to load the plan-122 gates.py/verdict.py changes (case-insensitive `## STEP` extractors + `_strip_trailing_parenthetical` on deposit paths). This canary positively discriminates old vs new gate code via the parenthetical strip: Step 1's `**Deposits:**` block declares its deposit path with a trailing parenthetical INSIDE the backticks, while the file created on disk carries NO parenthetical. Under pre-122 gates, `_extract_plan_required_deposits` returns the path-with-parenthetical and `deposit_exists` FAILS (no such file). Under the restarted daemon's new gates, the trailing parenthetical is stripped and `deposit_exists` PASSES. An all-PASS deposit_exists on this step is therefore proof the daemon reloaded the 122 module. Probe content is one line; it stays as canary evidence.

## How to Run This Plan

Paste the bootstrap prompt into Claude Code. Single-step plan — the agent executes Step 1 and the daemon pauses for verdict at completion.

**Bootstrap prompt:**
```
Read the plan at bellows/knowledge/decisions/executable-gates122-reload-canary-2026-07-02.md. Execute Step 1. Do NOT move the plan to Done until Step 1 is fully complete.
```

---
---

## STEP 1 — DEV

---

> **FIRST — before any reads or work: post a short visible message to chat (1-2 sentences) confirming you are starting this plan and stating your immediate next action.** Do NOT rename the plan file.
>
> You are the Bellows Developer. Skip specialist file and glossary reads — one-file canary, no domain knowledge required. All commands run from `/Users/marklehn/Developer/GitHub/bellows`.
>
> **Scope:**
> - `knowledge/research/`
>
> **Action.** Write the file `knowledge/research/gates122-reload-probe-2026-07-02.md` (EXACT name, NO parenthetical in the filename) containing a single line: `Gates-122 reload canary probe — created <full UTC ISO timestamp> — confirms parenthetical-strip + case-insensitive-header module reloaded.` Use the canonical Python file-write pattern — no heredoc.
>
> **Note the deliberate discriminator:** the `**Deposits:**` block below declares this file's path WITH a trailing `(122 reload canary)` qualifier inside the backticks. Create the file WITHOUT that qualifier — the mismatch is the whole point. Do NOT "correct" the Deposits block to match the filename, and do NOT add the parenthetical to the actual filename.
>
> **Commit:** `git add knowledge/research/gates122-reload-probe-2026-07-02.md && git commit -m "canary: gates-122 reload probe (parenthetical-strip discriminator)"`.
>
> In `### Ledger Updates` include `#### Prompt Feedback` only (no Project Status — canary, not a milestone).
>
> **Deposits:**
> - `knowledge/research/gates122-reload-probe-2026-07-02.md (122 reload canary)`
>
> On full completion, move the plan file to `bellows/knowledge/decisions/Done/` as the absolute last operation.
