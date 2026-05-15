# bellows — `extract_primary_deposit` Current Shape
**Date:** 2026-04-19 | **Tier:** diagnostic | **Execution:** Step 1 (Investigation Agent)

## How to Run This Plan

Paste the bootstrap prompt into Claude Code. The agent executes Step 1 ONLY. Read-only. No code changes.

**Bootstrap:**
```
Read the plan at bellows/knowledge/decisions/diagnostic-extract-primary-deposit-shape-2026-04-19.md. Execute Step 1 ONLY. After completing Step 1, STOP and wait for my confirmation. Do NOT move the plan to Done.
```

---
---

## STEP 1 — Investigation Agent

---

> Skip specialist file and glossary reads — this is a code-tracing task. Read-only. Read `bellows/verdict.py` top to bottom and answer the three questions below.
>
> **Question 1 — `extract_primary_deposit` verbatim.** Report: (a) exact function signature including all parameters and defaults, (b) the full function body verbatim in a fenced Python code block, (c) every module-level constant, regex pattern, or helper function the body references — quote each one verbatim with its line number.
>
> **Question 2 — All callers of `extract_primary_deposit`.** Every call site across `bellows/verdict.py`, `bellows/bellows.py`, `bellows/gates.py`, `bellows/parser.py`, `bellows/runner.py`, `bellows/planner.py`. Per call site: file path + line number + 2 lines of context + exact arguments passed.
>
> **Question 3 — Surrounding `verdict.py` context.** Report: (a) the imports at the top of `verdict.py`, (b) any module-level constants that look relevant to deposit extraction (regex patterns, keyword lists, etc.) — quote verbatim with line numbers, (c) is there a `Deposits` (plural) variant already present? If yes, quote it. If no, confirm: "No plural deposits function exists in verdict.py."
>
> **Deposit:** write findings to `bellows/knowledge/research/extract-primary-deposit-shape-2026-04-19.md` using the canonical Python file write pattern (`with open(...) as f: f.write(content)` where `content` is a triple-quoted string defined before the open call). Structure with three top-level sections matching the questions. Quote all code verbatim in fenced blocks. End with an Output Receipt.
>
> **Deposits:**
> - `bellows/knowledge/research/extract-primary-deposit-shape-2026-04-19.md`
>
> Standard prompt feedback protocol → `bellows/knowledge/research/agent-prompt-feedback.md`.
>
> **STOP. Do NOT move the plan to Done. Report completion and wait for CEO confirmation.**
