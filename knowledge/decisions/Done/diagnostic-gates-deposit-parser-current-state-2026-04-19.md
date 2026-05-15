# bellows — gates.py / verdict.py Current State for Rule 26 Parser Work
**Date:** 2026-04-19 | **Tier:** diagnostic | **Execution:** Step 1 (Investigation Agent)

## How to Run This Plan

Paste the bootstrap prompt into Claude Code. The agent reads the full plan file and executes Step 1 ONLY. This is a read-only investigation — no code changes. The agent deposits findings and reports completion. The Planner will read the findings directly and handle housekeeping per Rule 22.

**Bootstrap:**
```
Read the plan at bellows/knowledge/decisions/diagnostic-gates-deposit-parser-current-state-2026-04-19.md. Execute Step 1 ONLY. After completing Step 1, STOP and wait for my confirmation. Do NOT move the plan to Done.
```

---
---

## STEP 1 — Investigation Agent

---

> **FIRST — before doing anything else, claim this plan:** `import shutil; shutil.move("bellows/knowledge/decisions/diagnostic-gates-deposit-parser-current-state-2026-04-19.md", "bellows/knowledge/decisions/in-progress-diagnostic-gates-deposit-parser-current-state-2026-04-19.md")`.
>
> Skip specialist file and glossary reads — this is a code-tracing task. Read-only investigation; no code changes, no tests run. Read `bellows/gates.py` and `bellows/verdict.py` and answer the five questions below. Findings must be citable by a follow-up executable plan without re-investigation.
>
> **Question 1 — `_gate_deposit_exists` current shape.** Locate the gate 5 function in `bellows/gates.py`. Report: (a) its exact function signature including all parameters and their types/expected shapes, (b) its return shape, (c) its full body verbatim in a fenced code block, (d) every place in `bellows/gates.py` AND `bellows/bellows.py` that calls it — file path + line number + surrounding 2 lines of context per call site, (e) what inputs the callers pass (e.g., do they pass full plan text, a specific step's text, or something else?).
>
> **Question 2 — `_extract_plan_required_deposits` current shape.** Located at `gates.py:157-177` per the 2026-04-18 architecture audit. Report: (a) its exact function signature, (b) its return shape, (c) its full body verbatim in a fenced code block, (d) the exact regex patterns it uses — each one quoted verbatim with a 1-line description of what format it's trying to match, (e) how it determines the "plan" boundary — does it scan the whole file or scope to a step?, (f) every caller of this function with file path + line number.
>
> **Question 3 — `post_verdict_request` current shape in `verdict.py`.** Located at `verdict.py:26-77` per the 2026-04-18 verdict file schema diagnostic. Report: (a) its exact function signature including all parameters, (b) its full body verbatim in a fenced code block, (c) the exact template string or f-string it uses to build the verdict request file content — quoted verbatim, (d) every caller of this function in `bellows/bellows.py` with file path + line number + what arguments are passed.
>
> **Question 4 — Step-text extraction in the codebase.** Is there any existing function or pattern in `bellows/gates.py`, `bellows/bellows.py`, `bellows/parser.py`, or `bellows/verdict.py` that extracts a single step's text from a multi-step plan file (e.g., given step N, return the text between `## STEP N` and `## STEP N+1`)? If yes, report the function name, file path, line range, signature, and full body verbatim. If no, confirm explicitly: "No existing step-text extraction function found in gates.py, bellows.py, parser.py, or verdict.py."
>
> **Question 5 — Test layout for gates and verdict.** For `bellows/tests/test_gates.py` and `bellows/tests/test_verdict.py`: (a) total line count and roughly how many test functions each has (grep `def test_` count), (b) what test framework is in use (pytest? unittest?), (c) are there any fixture plan files in the test tree — check `bellows/tests/` for any `.md` files or `fixtures/` subdirectory, (d) is there an existing test function for `_gate_deposit_exists` or `_extract_plan_required_deposits`? If yes, quote the test function names. If no, confirm "No existing tests for deposit-detection gate found."
>
> **Deposit:** write findings to `bellows/knowledge/research/gates-deposit-parser-current-state-2026-04-19.md` using the canonical Python file write pattern (`with open(...) as f: f.write(content)` where content is a triple-quoted string defined before the open call). Structure the findings with five top-level sections (one per question), each with a clear heading matching the question label. Use fenced code blocks for all quoted source code and regex patterns — do NOT paraphrase code, quote it verbatim. End with an Output Receipt.
>
> **Deposits:**
> - `bellows/knowledge/research/gates-deposit-parser-current-state-2026-04-19.md`
>
> Standard prompt feedback protocol → `bellows/knowledge/research/agent-prompt-feedback.md`.
>
> **STOP. Do NOT move the plan to Done. Report completion and wait for CEO confirmation — the Planner will read the findings and handle housekeeping.**
