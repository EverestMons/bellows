# Bellows — Model-Coupling Audit (Diagnostic)
**Date:** 2026-07-01 | **Tier:** Small | **Dispatch Mode:** bellows | **Test Scope:** targeted | **Execution:** Step 1 (SA)

## How to Run This Plan

Paste the bootstrap prompt into Claude Code. The agent reads the full plan file and executes Step 1 ONLY — a read-only investigation. After completing Step 1, the agent STOPS. This is a single-step diagnostic; there is no Step 2 and no move-to-Done.

**Bootstrap prompt:**
```
Read the plan at bellows/knowledge/decisions/[this-filename].md. Execute Step 1 ONLY. It is a read-only investigation — do not fix or refactor anything. Deposit findings, then stop.
```

---
---

## STEP 1 — SA

---

> **FIRST — before any reads or work: post a short visible message to chat (1-2 sentences) confirming you are starting this plan and stating your immediate next action.** Do NOT rename the plan file.
>
> You are the Bellows Systems Analyst. Read your specialist file at `bellows/agents/BELLOWS_SYSTEMS_ANALYST.md` first. Skip the domain glossary — this is a code-coupling audit, not a domain task.
>
> The CEO wants Eluvian's orchestration to run on any AI model, not just Claude Code, so that work can continue on a second model when usage caps out on the first. Before any architecture is designed, map exactly where Bellows is coupled to Claude Code specifically — what would break or silently misbehave if a different agent runtime (Codex, Gemini, another ACP agent) were dispatched instead.
>
> Investigate and report on three coupling surfaces. **1. Dispatch path.** How does the daemon invoke Claude Code? Identify the specific SDK/CLI call, the arguments and environment it passes, how it hands the plan file to the agent, and how it detects that the agent has started, completed, or failed. Note every place the invocation assumes Claude-Code-specific behavior (auth model, worktree handling, session lifecycle, completion signaling). **2. Gate output parsing.** In `gates.py`, do any gate checks (Rule 20 self-check banner, Rule 22 substance checks, scope_check, teardown) parse or pattern-match against the agent's output text or output structure? For each, state whether the check assumes a Claude-Code-specific output shape (banner phrasing, receipt format, verdict text, JSON structure) or whether it reads deposited files on disk independent of who produced them. Distinguish "reads the artifact" (model-agnostic) from "parses the agent's narration" (model-coupled). **3. Step-log parsing.** How are step logs in `bellows/logs/` written and read? Identify every place that assumes the log format Claude Code emits — specifically the `d["parsed"]` cost field, the `d["raw_output"]` regex extraction for `num_turns`/`duration_ms`, and any other field access that would return null or throw against a different runtime's log shape.
>
> For each coupling point, classify as: (a) **hard-coupled** — assumes Claude Code, breaks on swap; (b) **soft-coupled** — assumes a format that could be normalized behind an adapter; (c) **already model-agnostic** — reads on-disk artifacts, indifferent to producer. Where a coupling point is soft, note what an abstraction seam would need to normalize.
>
> Also check: is there a parallel or legacy dispatch path (e.g. manual_bootstrap vs bellows dispatch) that couples differently? If yes, map both.
>
> Deposit findings to `bellows/knowledge/research/model-coupling-audit-2026-07-01.md`. Use the canonical Python file-write pattern or Filesystem:write_file — no heredoc. Do not fix or refactor anything — investigate and describe only. Standard prompt feedback protocol → `bellows/knowledge/research/agent-prompt-feedback.md`.
>
> **STOP. This is a single-step diagnostic. Do NOT move the plan to Done.**
