# Bellows — Diagnostic: Verdict Schema Refresh (pre-executable)
**Date:** 2026-04-19 | **Tier:** Small | **Test Scope:** targeted (read-only investigation, no code changes) | **Execution:** Step 1 (Bellows Developer)

**Purpose:** Refresh the 2026-04-18 verdict schema diagnostic findings before writing the schema-change executable. Rule 26 parser work shipped 2026-04-19 touched `verdict.py`, so line numbers and possibly function signatures have drifted. Five targeted questions; each answer must be anchored to a verbatim line-numbered code snippet.

**Blocks:** the verdict schema executable (A–E: fix Total Steps: None, add Pause Reason Code, Gate Result Passed, Project, Deposit fields).

## How to Run This Plan

Paste the bootstrap prompt into Claude Code. The agent reads the full plan file and executes Step 1. This is a single-step diagnostic — no Step 2. After completing Step 1, the agent STOPS. The Planner reads the deposited findings file in the Project conversation, performs Rule 22 verification, and handles housekeeping (move-to-Done + PROJECT_STATUS update) directly.

**Bootstrap:**
```
Read the plan at /Users/marklehn/Desktop/GitHub/bellows/knowledge/decisions/diagnostic-verdict-schema-refresh-2026-04-19.md. Execute Step 1. After completing Step 1, STOP and wait for my confirmation.
```

---
---

## STEP 1 — Bellows Developer

---

> **FIRST — before doing anything else, claim this plan:** `import shutil; shutil.move("/Users/marklehn/Desktop/GitHub/bellows/knowledge/decisions/diagnostic-verdict-schema-refresh-2026-04-19.md", "/Users/marklehn/Desktop/GitHub/bellows/knowledge/decisions/in-progress-diagnostic-verdict-schema-refresh-2026-04-19.md")`.
>
> You are the Bellows Developer. **Reads (mandatory):** (1) `/Users/marklehn/Desktop/GitHub/bellows/agents/BELLOWS_DEVELOPER.md` — your specialist file, (2) `/Users/marklehn/Desktop/GitHub/bellows/knowledge/research/verdict-file-schema-2026-04-18.md` — prior diagnostic this refreshes, (3) `/Users/marklehn/Desktop/GitHub/bellows/verdict.py`, (4) `/Users/marklehn/Desktop/GitHub/bellows/bellows.py`. Skip domain glossary — no glossary exists for Bellows and this is pure code-tracing. This is a **read-only investigation**. Do NOT modify any source file. Do NOT write the executable — that is the Planner's job after reviewing your findings.
>
> **Answer five questions. Each answer MUST include a verbatim line-numbered code snippet from the current codebase, not a paraphrase.**
>
> **Q1 — Callers of `post_verdict_request()`.** List every call site in `bellows.py` (and any other module). For each: (a) file path + line number of the call, (b) name of the function containing the call, (c) how `total_steps` is computed or whether it's omitted/None at the call site, (d) what scope variables are available at that point — is `project_path` in scope? is plan content in scope? is a step number available? Include a 6-line verbatim snippet showing the call and its immediate context.
>
> **Q2 — `extract_primary_deposit()` signature.** State the current signature (parameters, types, return value), the file and line where it's defined, and any helper functions it calls (e.g., `_extract_step_text`, block parsers). Include the full function definition as a verbatim snippet. Answer whether `post_verdict_request()` can call `extract_primary_deposit()` directly without circular imports given current import structure.
>
> **Q3 — `_pause_reason_labels` current state.** Paste the exact current dict (keys + values) as a verbatim snippet with line numbers. List every unique string value passed to `pause_reason` at any call site of `post_verdict_request()` — cross-reference against the dict keys. Flag any caller passing a key not in the dict. State whether the pause reasons are defined as string constants or an Enum elsewhere in the codebase.
>
> **Q4 — Test coverage for `verdict.py`.** Run `ls /Users/marklehn/Desktop/GitHub/bellows/tests/` and list every file. For each file that imports from or references `verdict.py` (grep for `verdict` or `post_verdict_request` or `extract_primary_deposit` in `bellows/tests/`), report: file name, number of tests targeting verdict.py functions, assertion style (per-field assertions vs. whole-content assertions), whether there's a pytest fixture that posts a verdict request. Include a verbatim snippet of one representative test.
>
> **Q5 — Circular import risk.** Paste the current `import` section at the top of `verdict.py`. Paste the current `import` section at the top of `bellows.py`. State whether `verdict.py` currently imports anything from `bellows.py` (directly or transitively). If the executable needs `post_verdict_request()` to call `extract_primary_deposit()` (which reads plan file content), identify whether that creates a new import dependency. If yes, propose the cleanest resolution (lazy import inside the function, move `extract_primary_deposit` to a neutral module, pass plan content as a parameter instead).
>
> **Deposit format.** Write your findings to `/Users/marklehn/Desktop/GitHub/bellows/knowledge/research/verdict-schema-refresh-2026-04-19.md` using the canonical Python file write pattern: define the full content as a triple-quoted string variable, then `with open("/absolute/path", "w") as f: f.write(content)`. Do NOT use heredoc. Structure the findings as: Q1 heading → snippet → prose answer; Q2 heading → snippet → prose answer; etc. End with an Output Receipt. Then commit: `cd /Users/marklehn/Desktop/GitHub/bellows && git add knowledge/research/verdict-schema-refresh-2026-04-19.md && git commit -m "research: verdict schema refresh diagnostic findings"`. Standard prompt feedback protocol → `/Users/marklehn/Desktop/GitHub/bellows/knowledge/research/agent-prompt-feedback.md`.
>
> **Deposits:**
> - `/Users/marklehn/Desktop/GitHub/bellows/knowledge/research/verdict-schema-refresh-2026-04-19.md`
> - `/Users/marklehn/Desktop/GitHub/bellows/knowledge/research/agent-prompt-feedback.md` (append only)
>
> **STOP. Do NOT write the executable. Do NOT proceed to move the plan to Done. The Planner handles housekeeping after reading your findings.**
