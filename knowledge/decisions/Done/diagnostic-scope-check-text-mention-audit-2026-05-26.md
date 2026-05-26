# Scope_Check Text-Mention Predicate — Plan-Authoring vs Structural Gap Audit
**Date:** 2026-05-26 | **Tier:** Diagnostic | **Dispatch Mode:** bellows | **Test Scope:** targeted | **Execution:** Step 1 (SA) | **qa_steps:** | **pause_for_verdict:** after_step_1

## How to Run This Plan

Paste the bootstrap prompt into Claude Code. The agent reads the full plan file and executes Step 1 ONLY.

**Bootstrap:** `Read the plan at /Users/marklehn/Developer/GitHub/bellows/knowledge/decisions/diagnostic-scope-check-text-mention-audit-2026-05-26.md. Execute Step 1 ONLY. After completing Step 1, STOP and wait for my confirmation.`

## CEO Context

The 2026-05-26 SA diagnostic (`knowledge/research/scope-check-post-fix-behavior-2026-05-26.md`) ended with DESIGN-INTENT-AUDIT-NEEDED. It found that the Rule 21 plan's scope_check trip was NOT the plan-file rename (structurally impossible — plan files are untracked, the rename is in the main repo, and `SCOPE_ALLOWLIST_PREFIXES` already exempts `in-progress-*`). The actual trip cause is almost certainly the dev log deposit at `knowledge/development/planner-template-rule-21-contract-change-2026-05-26.md` failing the text-mention predicate at gates.py:616 (`fpath in step_text or basename in step_text`).

The disposition between two fix shapes hangs on a single empirical question: was the dev log path mentioned in Step 1's step text?

- **If yes** → the text-mention predicate has a structural failure mode (path-form mismatch, encoding, extraction gap). Fix likely lives in gates.py.
- **If no** → confirms a systemic Planner authoring pattern. Every Rule 8 split-commit DOC step risks tripping scope_check unless the Planner consistently mentions the deposit path in step prose. Fix is governance (Fix Shape D) or structural exemption via Deposits-block parsing (Fix Shape B).

The pristine cache for the Rule 21 plan is missing (likely purged at halt or session end). Source-of-truth for the step text is the halted plan body itself at `bellows/knowledge/decisions/Done/halted-executable-planner-template-rule-21-contract-change-2026-05-26.md`. Bellows only renames plan files — it never edits the body — so the halted plan body equals what the Planner originally authored and what `_extract_step_text` would have parsed at gate time. This is a safe substitute for the missing pristine cache.

This is a single SA step. No DEV, no QA chain. Recommendation lands as a Flags-for-CEO entry; the Planner picks a fix shape and authors the executable.

---
---

## STEP 1 — Bellows Systems Analyst

---

> **FIRST — before doing anything else, claim this plan:** `import shutil; shutil.move("/Users/marklehn/Developer/GitHub/bellows/knowledge/decisions/diagnostic-scope-check-text-mention-audit-2026-05-26.md", "/Users/marklehn/Developer/GitHub/bellows/knowledge/decisions/in-progress-diagnostic-scope-check-text-mention-audit-2026-05-26.md")`.
>
> You are the Bellows Systems Analyst. Read your specialist file at `bellows/agents/BELLOWS_SYSTEMS_ANALYST.md` first. Skip the domain glossary read — this is a step-text predicate audit, no domain interpretation required.
>
> **Task.** Determine whether the Rule 21 plan's Step 1 text contained a reference that should have exempted the dev log deposit from scope_check's text-mention predicate, and recommend a fix shape.
>
> **Inputs to read.** (1) The halted plan body at `/Users/marklehn/Developer/GitHub/bellows/knowledge/decisions/Done/halted-executable-planner-template-rule-21-contract-change-2026-05-26.md` — this is the source-of-truth for what the Planner authored and what `_extract_step_text` parsed at gate time, since Bellows only renames plan files. (2) The post-fix behavior characterization at `bellows/knowledge/research/scope-check-post-fix-behavior-2026-05-26.md` (Q1 covers gate code shape; Q3 covers the predicate; Q6 covers fix shapes A–D). (3) `bellows/gates.py` lines 600–625 (`_gate_scope_check`) and the `_extract_step_text` helper to confirm the step-extraction boundary. (4) `bellows/gates.py` lines 23–30 for the allowlist constants.
>
> **Q1 — Empirical predicate trace.** Extract Step 1's step text from the halted plan body using the same boundary logic `_extract_step_text` uses (the `## STEP 1` section, up to but not including `## STEP 2`). Apply the three-tier in-scope predicate from gates.py:610–617 against the candidate file path `knowledge/development/planner-template-rule-21-contract-change-2026-05-26.md` (and its basename `planner-template-rule-21-contract-change-2026-05-26.md`). For each tier, report PASS or FAIL and quote the matching substring if PASS: (a) basename in `SCOPE_ALLOWLIST`, (b) basename startswith any prefix in `SCOPE_ALLOWLIST_PREFIXES`, (c) `fpath in step_text or basename in step_text`. Then check for near-misses: does the step text contain the basename minus extension? Does it contain a slug substring? Does it contain a path form with different separators or escaping? Enumerate every substring in step_text that overlaps with the deposit basename by ≥10 characters.
>
> **Q2 — Predicate failure classification.** Based on Q1, classify the failure mode as exactly one of: (i) **Planner authoring gap** — the deposit path was not mentioned anywhere in the step text, in any form. (ii) **Path-form gap** — the deposit was mentioned but in a form the substring match couldn't recognize (e.g., relative-vs-absolute, encoding, escaping, line-wrapping). (iii) **Extraction gap** — the path appears in the plan but outside the `_extract_step_text` boundary (e.g., in the CEO Context, header line, or another step). (iv) **Other** — describe.
>
> **Q3 — Fix-shape decision matrix.** Given Q2's classification, evaluate the four fix shapes from the prior diagnostic (`scope-check-post-fix-behavior-2026-05-26.md` Q6) — A (knowledge/ subtree exempt), B (parse Deposits block structurally), C (slug-substring exempt), D (governance rule). For each shape, score on three dimensions: **(blast)** how much scope_check coverage is sacrificed in trade, **(robustness)** does the fix close the failure mode or only the specific instance, **(coupling)** does it create new dependencies between gates or between Bellows and Planner discipline. Output as a table. Then recommend exactly one fix shape with a one-sentence rationale tying back to Q2's classification.
>
> **Q4 — Systemic-risk scope.** From the prior diagnostic's side-finding 3, three deposit directories are at risk: `knowledge/development/`, `knowledge/research/`, `knowledge/architecture/`. For each, enumerate which agent role typically deposits there and which plan tier or step type triggers the deposit. Estimate how many active projects in the eluvian-governance submodule set have plan templates that would trigger each deposit type. The goal is to size the population at risk so the fix shape choice can be cost-justified.
>
> **Q5 — Verification block (Rule 39).** Re-run the substring searches from Q1 and report exact byte offsets of any matches or near-matches in the step text. This is the load-bearing claim of the entire diagnostic — the disposition swings on it.
>
> **Deposit.** `bellows/knowledge/research/scope-check-text-mention-audit-2026-05-26.md` containing Q1–Q5, a Decisions Made section recording the recommended fix shape and rationale, and Flags-for-CEO containing the next-action recommendation (executable for Fix Shape B, or governance edit plan for Fix Shape D). Do NOT author the fix plan itself — flag for the Planner.
>
> **Constraints.** Do NOT modify source code. Do NOT modify gates.py. Do NOT modify the halted plan. This is a read-only investigation. Cite line numbers and quote evidence verbatim where possible.
>
> Standard prompt feedback protocol → `bellows/knowledge/research/agent-prompt-feedback.md`.
