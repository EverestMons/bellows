# Bellows — Scope-Gates Reload Canary (post-restart discriminator)
**Date:** 2026-07-02 | **Tier:** Small | **Dispatch Mode:** bellows | **Test Scope:** targeted | **Execution:** Step 1 (DEV) | **pause_for_verdict:** always

## CEO Context

Daemon restarted 2026-07-02 18:18 to load the plan-118 (rule_20 receipt fallback) and plan-119 (declared `**Scope:**` block) gates.py changes. This canary positively discriminates old vs new gate code: Step 1 creates a probe file whose name is DERIVED AT RUNTIME (so its basename cannot appear anywhere in this plan's text) under a directory declared only as a Scope-block PREFIX. Under pre-119 gates that probe is an out-of-scope gate_failure; under the new gates the declared prefix clears it silently. An all-PASS scope_check on this step is therefore proof the restarted daemon is gating with the new module. Probe content is one line; it stays as canary evidence.

## How to Run This Plan

Paste the bootstrap prompt into Claude Code. Single-step plan — the agent executes Step 1 and the daemon pauses for verdict at completion.

**Bootstrap prompt:**
```
Read the plan at bellows/knowledge/decisions/executable-scope-gates-reload-canary-2026-07-02.md. Execute Step 1. Do NOT move the plan to Done until Step 1 is fully complete.
```

---
---

## STEP 1 — DEV

---

> **FIRST — before any reads or work: post a short visible message to chat (1-2 sentences) confirming you are starting this plan and stating your immediate next action.** Do NOT rename the plan file.
>
> You are the Bellows Developer. Skip specialist file and glossary reads — two-file canary, no domain knowledge required. All commands run from `/Users/marklehn/Developer/GitHub/bellows`.
>
> **Scope:**
> - `knowledge/research/`
>
> **Action 1 — runtime-named probe.** In Python, compute `probe_name = "scope-probe-" + datetime.now(timezone.utc).strftime("%H%M%S") + ".md"` and write the file `knowledge/research/<probe_name>` containing a single line: `Scope-gates reload canary probe — created <full UTC ISO timestamp> by plan executable-scope-gates-reload-canary-2026-07-02.` The runtime-derived name is load-bearing: it must NOT be replaced with a hand-typed literal filename, because the point is that this plan's text cannot contain the probe's basename.
>
> **Action 2 — canary report (the deposit).** Write `knowledge/research/scope-gates-reload-canary-2026-07-02.md` with: (1) the probe filename actually created, (2) the probe's full path and a `ls -la` line proving it exists, (3) one sentence stating the discriminator logic (probe basename absent from plan text; only the `knowledge/research/` Scope prefix can clear it), (4) an Output Receipt with status. Use the canonical Python file-write pattern — no heredoc.
>
> **Commit BOTH files:** `git add knowledge/research/ && git commit -m "canary: scope-gates reload probe + report (post-restart discriminator)"`.
>
> In `### Ledger Updates` include `#### Prompt Feedback` only (no Project Status — canary, not a milestone).
>
> **Deposits:**
> - `bellows/knowledge/research/scope-gates-reload-canary-2026-07-02.md`
>
> On full completion, move the plan file to `bellows/knowledge/decisions/Done/` as the absolute last operation.
