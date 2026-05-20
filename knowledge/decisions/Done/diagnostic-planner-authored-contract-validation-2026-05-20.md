# bellows — Planner-Authored Contract Validation Surface
**Date:** 2026-05-20 | **Tier:** Small | **Dispatch Mode:** bellows | **Test Scope:** none (diagnostic) | **Execution:** Step 1 (Bellows Systems Analyst) | **pause_for_verdict:** after_step_1

## How to Run This Plan

Bellows dispatches this plan automatically when deposited; no manual bootstrap required. Single-step diagnostic — the SA enumerates Planner-authored artifacts with strict downstream contracts, classifies failure modes, and evaluates per-artifact response options. Deposits findings; appends prompt feedback; commits. The Planner performs the terminal Done/ move after Rule 22 verification on the findings file.

---

## STEP 1 — Bellows Systems Analyst

---

> **FIRST — before doing anything else, claim this plan:** `import shutil; shutil.move("bellows/knowledge/decisions/diagnostic-planner-authored-contract-validation-2026-05-20.md", "bellows/knowledge/decisions/in-progress-diagnostic-planner-authored-contract-validation-2026-05-20.md")`.
>
> You are the Bellows Systems Analyst. Skip the domain glossary read — this is an architecture audit, not a domain-interpretation task. Read your specialist file at `bellows/agents/BELLOWS_SA.md` for output format expectations. **Context:** the 2026-05-12 LESSONS entry (governance-root `LESSONS.md`) identified a structural asymmetry — "Bellows has eight gates evaluating agent work and zero validators evaluating Planner-deposited files" — and recommended a diagnostic at this exact path to enumerate Planner-authored artifacts with strict downstream contracts, classify each, and evaluate per-artifact responses. Since that entry, one validator has shipped (`bellows/validators.py` dispatch-mode validator, executable-bellows-dispatch-mode-validator-2026-05-19) and at least three more contract-mismatch failures have been observed (verdict file format 2026-05-12; Rule 26 evidence paths 2026-05-11; today 2026-05-20 missing Dispatch Mode header field). The narrow per-validator shipping pace is not addressing the class. This diagnostic produces the surface enumeration that lets the next set of validator-implementation plans land coherently rather than reactively. **Investigate and report on six questions.**
>
> **Q1 — Enumerate Planner-authored artifacts with strict downstream contracts.** A "Planner-authored artifact" is any file the Planner writes that Bellows or another deterministic component subsequently parses. Strict contract means the parser fails or produces wrong behavior on shape deviation. For each artifact, capture: (a) file type / path pattern, (b) consuming component (Bellows module + function), (c) the contract shape (header fields required, format constraints, regex patterns, line-position requirements), (d) the parser's failure mode on contract violation (silent skip, raised exception, gate_failure, etc.), (e) any current Bellows-side validation that fires before the violation. Known starting set to extend, not exhaustively pre-enumerate: plan files (header schema, `**Deposits:**` block, `## STEP N` headers, filename pattern, dispatch mode), verdict response files (`verdict:` prefix regex from `bellows/verdicts/README.md`), and any other surfaces discovered. Produce a table.
>
> **Q2 — Failure mode classification per artifact.** For each artifact from Q1, classify the contract violation failure mode along these axes: (a) **detectability** — does the parser raise, log, silently skip, or produce wrong-but-not-error behavior? (b) **recovery cost** — how long does the typical recovery take (seconds via re-author, minutes via mechanical fix, hours via debugging silent-skip), and how is the failure surfaced to the Planner (Bellows error log, daemon notification, manual investigation, never)? (c) **observation count** — how many times has this failure class been observed in the LESSONS.md log or BACKLOG entries (cite specific entries)? Produce a table with one row per artifact.
>
> **Q3 — Response option evaluation per artifact.** For each artifact from Q1, evaluate three response options: **(a) Schema validator** — `bellows/validators.py`-style pre-claim check that rejects with a specific error message before the artifact is consumed. **(b) Writer helper** — a Planner-facing utility function (or MCP-exposed helper) that authors the artifact correctly by construction, taking parameters and emitting the file. The Planner calls the helper rather than authoring free-form. **(c) Observability-only** — Bellows logs the violation visibly (warn or error) without blocking, surfacing failures to the Planner faster without changing the artifact-authoring path. For each artifact, recommend ONE response and justify the choice. The justification must address why the other two options are wrong for that artifact. Note that (b) writer helpers are a more invasive architectural change than (a) validators — they require either a Planner-side MCP tool, a code path the Planner conversation can invoke, or a Bellows-watched stage where Planner-deposited drafts get rewritten by a helper into compliant form. Surface that cost honestly.
>
> **Q4 — Shipping order and dependencies.** Given the per-artifact recommendations from Q3, what's the right shipping order? Group the recommendations by (a) effort estimate (small / medium / large with rough LOC + tests), (b) blast radius (single function vs cross-module), (c) recurrence rate (highest first — the LESSONS log gives empirical counts). Identify any inter-validator dependencies (e.g., if validator A and validator B both need to read the plan header, they should share a parsed-header helper). Produce a recommended sequence and call out which validators can ship in parallel.
>
> **Q5 — Anti-recommendations.** Identify any artifacts that look like validator candidates but should NOT get one. Likely candidates to evaluate: plan body prose (LLM-judged content, not strict contract), test-scope justifications (free text in CEO Context section), agent prompts (intentional flexibility for Planner authoring). For each, explain why the validator-versus-LLM-judgment line falls where it does. This question exists because the Planner's value is exactly the LLM-judgment portion of plan authoring; conflating "shape" with "content" by over-validating would break the system. The audit must distinguish the two explicitly.
>
> **Q6 — Gap Assessment.** Synthesize Q1–Q5 into a Gap Assessment table per the Diagnostic Prompt Engineering convention: `| Gap | Current State | Proposed Response | Validator/Helper/Observability | Effort | Priority (1-3) |`. One row per artifact recommended for new infrastructure. Sort by priority. Include a brief Notes column where dependency or sequencing considerations apply. This table is the executable plan author's checklist for the follow-on work — each row should be authorable as a small executable plan without further investigation.
>
> **Cite exact file paths and line numbers** for every contract surface and parser function referenced. Anchor recommendations to actual code, not abstract proposals.
>
> **Deposit** findings to `bellows/knowledge/research/planner-authored-contract-validation-2026-05-20.md`. End with a standard Output Receipt.
>
> **Then** append a standard prompt-feedback entry to `bellows/knowledge/research/agent-prompt-feedback.md` per the protocol at the top of that file.
>
> **Commit** with message `docs: planner-authored contract validation surface diagnostic findings`.
>
> **Deposits:**
> - `bellows/knowledge/research/planner-authored-contract-validation-2026-05-20.md`
> - `bellows/knowledge/research/agent-prompt-feedback.md`
