# Bellows — R3 Inline Step Text: Prompt-Construction Surface Diagnostic
**Date:** 2026-04-19 | **Tier:** Diagnostic | **Test Scope:** n/a | **Execution:** Step 1 (SA)

**Purpose:** Map the current bootstrap prompt construction in `runner.py` and every place the agent is expected to know the plan file path, so the Planner can design the R3 fix (inline step text in bootstrap prompt, eliminate plan-file path from agent context) with full knowledge of downstream breakage risk.

**Context:** Plan-mutation-source diagnostic (2026-04-19) confirmed the `claude -p` agent is the sole source of plan file truncation (BACKLOG #6/#7). R3 — inline the step text into the bootstrap prompt instead of passing the plan file path — was the top-ranked fix recommendation. Before authoring that fix, the Planner needs to know (a) the exact prompt-construction code surface, (b) every agent capability that depends on knowing the plan file path, (c) whether `--resume` session semantics preserve prior-step context or require re-delivery, and (d) the minimal R3 variant that preserves required capabilities.

## How to Run This Plan

Paste the bootstrap prompt into Claude Code. The agent reads the full plan file and executes Step 1. After Step 1's findings are deposited, the agent reports Complete and the Planner reads the findings file directly to perform Rule 22 verification. This is a single-step diagnostic per Rule 22 v4.19 — there is no Step 2 consolidation.

**Bootstrap:**
```
Read the plan at bellows/knowledge/decisions/diagnostic-r3-inline-step-text-surface-2026-04-19.md. Execute Step 1 ONLY. After completing Step 1, STOP and wait for my confirmation. Do NOT do any housekeeping beyond the deposit.
```

---
---

## STEP 1 — Bellows Systems Analyst

---

> **FIRST — claim this plan:** `import shutil; shutil.move("bellows/knowledge/decisions/diagnostic-r3-inline-step-text-surface-2026-04-19.md", "bellows/knowledge/decisions/in-progress-diagnostic-r3-inline-step-text-surface-2026-04-19.md")`.
>
> You are the Bellows Systems Analyst. Skip specialist file and glossary reads — this is a code-tracing diagnostic. Investigate the current bootstrap prompt construction surface in Bellows to prepare for the R3 fix (inline step text in bootstrap prompt, eliminate plan-file path from agent context). Do NOT propose or implement fixes. Do NOT modify any code. Deposit findings only.
>
> **Q1 — Map the current bootstrap prompt construction.** Read `bellows/runner.py` in full. Identify every function that constructs the prompt string sent to `claude -p`. For each, quote the exact prompt template (as a Python string literal or f-string) and name the function + line number. Then read `bellows/bellows.py` and identify every call site that invokes the runner — quote the arguments passed at each call site. Also grep the entire `bellows/` root (`*.py` only, exclude `tests/`, `.bellows-cache/`, `.pytest_cache/`) for any other location that builds prompt strings (e.g., `planner.py`'s consultation prompt, if relevant) — report any additional prompt-construction sites found. Produce an exact inventory: which function builds the prompt, which arguments it receives, which arguments appear in the final prompt text, how the plan file path is interpolated. The output should include verbatim code excerpts (5-15 lines per call site) so the fix design can cite line-accurate references.
>
> **Q2 — Enumerate every agent capability that depends on knowing the plan file path.** Grep `bellows/` for any instruction the runner or bellows.py puts in the prompt that references `{plan_path}`, the plan filename, or the plan's directory. Separately, read the PLANNER_TEMPLATE's agent prompt conventions (already inlined in the Bootstrap prompt format and in Rule 8's closeout instructions) and list every capability a typical agent prompt expects the agent to perform that requires the plan path: (a) reading the plan file to find its step text, (b) moving the plan file to Done/ or to in-progress- via `shutil.move`, (c) appending to the feedback log using paths relative to the plan, (d) committing the plan file in git during housekeeping, (e) any other path-dependent action. Produce a table: | Capability | Where expected (runner prompt / plan step text / Rule 8) | Requires plan path? | Alternative if path unknown |.
>
> **Q3 — Check downstream dependencies on full-plan context.** Multi-step plans depend on the agent being able to reference earlier steps' content (prior-step verification per Rule 15, cross-step Deposits blocks per Rule 26, step transitions). Read 3 representative executable plans from `bellows/knowledge/decisions/Done/` (pick a recent Small-tier plan, a recent Medium-tier plan, and the most recent plan in Done/) and enumerate every reference inside Step N to content that lives in Step M where M ≠ N. Examples: "read the prior step's deposit at X", "the final step reads the DEV Output Receipt and verifies", "see the **Deposits:** block in Step 1". Report the count per plan and classify each reference as (a) requires reading the plan file for Step M content, (b) satisfiable by reading a deposited artifact from Step M, (c) satisfiable by content already present in the current step's own prompt text. This tells us whether R3's strictest variant (only current step injected) is feasible, or whether the agent structurally needs access to sibling steps.
>
> **Q4 — Debunk or confirm `--resume` session context preservation.** Read `bellows/runner.py`'s subprocess invocation and identify whether `--resume session_id` is used for multi-step plans. If so, quote the exact `claude -p` invocation line. Then check the Claude Code CLI documentation behavior for `--resume`: does the resumed session preserve the full prompt/response history from Step 1, or does Step 2 need to re-establish context? If the docs are not reachable from the agent's tools, report what the code assumes and flag it as an open empirical question. This determines whether R3-inline-current-step-only is viable for multi-step plans, or whether each step must re-deliver all prior context.
>
> **Q5 — Confirm the minimal R3 variant.** Based on Q1-Q4, enumerate the R3 variants in order of smallest-diff to largest-diff, each with a one-paragraph description of what changes in `runner.py`'s prompt construction. The variants to consider are at least: (a) **Inline current step only** — bootstrap contains just the current step's text, no plan path; (b) **Inline full plan, strip path** — bootstrap contains the full plan content but no plan path, agent can cross-reference steps but can't modify the file because it doesn't know where it is; (c) **Pass shadow cache path as read-only** — instead of the mutable in-progress path, pass `.bellows-cache/{name}.pristine`; (d) **Hybrid** — inline full plan text in the prompt AND pass the plan path for housekeeping moves only (not for reading). For each variant, flag which Q2 capabilities it breaks and which it preserves. Do NOT recommend one — the Planner picks after reading. Request that the finding be written in a way that supports direct quotation in the follow-up executable's SA blueprint (exact code fragments, exact line references, exact capability breakage per variant).
>
> **Output format:** deposit findings at `bellows/knowledge/research/r3-inline-step-text-surface-2026-04-19.md`. Structure: (a) Summary (3-4 sentences), (b) Q1 findings with verbatim code excerpts, (c) Q2 capability table, (d) Q3 cross-step reference counts per plan, (e) Q4 resume-semantics finding, (f) Q5 variants table with per-capability impact, (g) Output Receipt. Write the content to a Python variable first, then use `with open("bellows/knowledge/research/r3-inline-step-text-surface-2026-04-19.md", "w") as f: f.write(content)`. Do NOT use heredoc. Do NOT use python3 -c with embedded quotes. Do NOT modify any Bellows source code.
>
> Standard prompt feedback protocol → `bellows/knowledge/research/agent-prompt-feedback.md`.
>
> **Deposits:**
> - `bellows/knowledge/research/r3-inline-step-text-surface-2026-04-19.md`
> - `bellows/knowledge/research/agent-prompt-feedback.md` (append)
>
> **STOP. This is a single-step diagnostic. Do NOT create a Step 2. Do NOT move the plan to Done — the Planner will verify findings and handle housekeeping per Rule 22.**
