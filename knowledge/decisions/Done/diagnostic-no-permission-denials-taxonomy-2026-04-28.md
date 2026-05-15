# Bellows — no_permission_denials Gate Taxonomy Diagnostic (BACKLOG #2)
**Date:** 2026-04-28 | **Tier:** Small | **Test Scope:** none | **Execution:** Step 1 (Bellows Systems Analyst)
**Priority:** 5

## Context

BACKLOG #2: `no_permission_denials` gate trips on successful diagnostics when agents use Claude Code native tools (Grep, Glob, Read) against cross-project paths. The gate detects denials regardless of whether the denial actually blocked work — agents routinely route around denials via bash, complete the task, and self-report Status: Complete. The gate fires anyway, creating noise.

Reproduced multiple times in today's session: today's Phase 3a Step 1 tripped with 3 Grep denials against `/Users/marklehn/Desktop/GitHub/PLANNER_TEMPLATE.md`. Agent's work landed correctly (commit `7b51217`), Output Receipt clean, but gate fired.

This diagnostic maps the current `_gate_no_permission_denials` behavior, samples observed denials from recent verdict requests, and recommends a tool-taxonomy fix shape. Investigation only — no code changes. Single-step per Rule 22.

The Planner's pre-investigation hypothesis (to be tested or refuted by the diagnostic): the right fix is Option (b) from the BACKLOG entry — scope the gate to tools whose denial actually blocks execution. Read-class tools (Grep, Glob, Read) produce noise; write-class tools (Edit, Write, Bash, NotebookEdit) produce real signals. The diagnostic should confirm the tool-name taxonomy by sampling actual denials, not by trusting the Planner's hypothesis.

Test Scope: none — pure investigation.

## How to Run This Plan

Bellows watcher claims this plan automatically. Step 1 (Bellows Systems Analyst) reads the gate implementation, samples observed denials, and deposits findings. Per disable-auto-close, terminal step pauses for Planner verdict. Single-step diagnostic per Rule 22.

---
---

## STEP 1 — Bellows Systems Analyst

---

> **FIRST — claim this plan:** `import shutil; shutil.move("bellows/knowledge/decisions/diagnostic-no-permission-denials-taxonomy-2026-04-28.md", "bellows/knowledge/decisions/in-progress-diagnostic-no-permission-denials-taxonomy-2026-04-28.md")`. Read your specialist file at `bellows/agents/BELLOWS_SYSTEMS_ANALYST.md` first. **Skip the domain glossary** — code-tracing and data sampling, no Bellows-specific domain vocabulary. **Investigation scope: 5 questions.** **Q1 — current gate implementation.** Read `bellows/gates.py::_gate_no_permission_denials()`. Quote the function verbatim with line numbers. Document: (a) what shape `parsed["permission_denials"]` takes — list of dicts, list of strings, or both; (b) what fields are reliably present on each denial (`tool_name`? `tool_use_id`? `tool_input`?); (c) how the function distinguishes blocking vs non-blocking denials today (likely: it doesn't — any denial trips the gate). **Q2 — denial source.** Trace where `permission_denials` is populated. Read `bellows/parser.py` (or wherever Output Receipt parsing lives). Document: (a) what stream Bellows reads to detect denials — agent's stdout? Claude Code transcript? Output Receipt section?; (b) what triggers a denial entry being added; (c) whether `tool_name` is always populated (or sometimes missing/null). **Q3 — observed denials sample.** Run `grep -h "tool_name" bellows/verdicts/pending/*.md bellows/verdicts/resolved/processed-*.md 2>/dev/null | head -50` to extract recent denial records. From the output, build a frequency table of `tool_name` values seen across recent gate failures. Expected names based on Planner hypothesis: Grep, Glob, Read, Edit, Write, Bash. Report which appear and which don't. If unexpected tool names appear (e.g., MCP tools like `Filesystem:read_text_file`, NotebookEdit, BashOutput, KillBash, WebFetch, WebSearch), list them. **Q4 — read-vs-write taxonomy reality check.** Based on Q3's observed names, propose a concrete `READ_CLASS_TOOLS` set. State the criterion in plain language: a tool is read-class if its denial does NOT prevent the agent from completing the task (the agent can route around it via bash or alternate tools). A tool is write-class if its denial blocks the actual work. For each observed tool name, classify it. Flag any tool name where the classification is ambiguous (e.g., is `WebFetch` read-class? — it's read-only but may be the only path to fetch a specific URL). **Q5 — test coverage and edge cases.** Read `bellows/tests/test_bellows.py` (or wherever gate tests live). Find tests that exercise `_gate_no_permission_denials`. Document: (a) what scenarios are tested currently; (b) what edge cases need new tests if Option (b) ships — empty denials list, mixed read/write denials, denial with missing `tool_name`, denial with `tool_name=None`, list of strings instead of dicts (legacy format?). Also check whether the gate handles a malformed `permission_denials` field gracefully today (e.g., string instead of list, missing field entirely). **Deliverable.** Use `Filesystem:write_file` to deposit findings to `bellows/knowledge/research/no-permission-denials-taxonomy-2026-04-28.md`. Structure: (1) Executive Summary — 4–6 sentences confirming or refuting the Planner's Option (b) hypothesis with the proposed `READ_CLASS_TOOLS` set; (2) Q1 — gate implementation with quoted code; (3) Q2 — denial source trace; (4) Q3 — observed denial sample with frequency table; (5) Q4 — proposed taxonomy with classification per observed tool; (6) Q5 — test coverage and edge cases. Cite specific file:line references throughout. **Do NOT propose the actual fix or write code.** Q4's taxonomy is analysis, not implementation. **Do NOT commit anything to git** — investigation only. **Standard prompt feedback protocol** → `bellows/knowledge/research/agent-prompt-feedback.md`.
>
> **Deposits:**
> - `bellows/knowledge/research/no-permission-denials-taxonomy-2026-04-28.md`
