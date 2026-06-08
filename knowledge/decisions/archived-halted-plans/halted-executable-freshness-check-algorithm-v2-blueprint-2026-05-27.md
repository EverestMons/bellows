# Bellows — Freshness-Check Algorithm V2 Blueprint
**Date:** 2026-05-27 | **Tier:** small-build | **Dispatch Mode:** bellows | **Test Scope:** n/a | **Execution:** Step 1 (SA) → Step 2 (SA) | **pause_for_verdict:** always

## How to Run This Plan

Deposit into `bellows/knowledge/decisions/`. Bellows dispatches Step 1 (SA) — SA produces a thin outline of the blueprint's subsections. Plan pauses for CEO review. After continue verdict, Step 2 (SA) fills in each subsection in turn, producing the full blueprint addendum.

This plan exists because two prior SA prompts in this session timed out (713s, 730s) with no agent output captured. The chunked SA shape (thin outline first, full content second) keeps each step under the inactivity threshold by reducing the up-front planning load per dispatch.

## Context

V1 implementation at `bellows/scripts/check_backlog_freshness.py` (239 LOC) produced 6/6 false-positive flag rate. V1 blueprint at `bellows/knowledge/research/leftover-after-ship-tooling-blueprint-2026-05-26.md`. V1 live output at `bellows/knowledge/research/backlog-freshness-check-2026-05-26.md`. V1 dev log at `bellows/knowledge/development/leftover-after-ship-tooling-implementation-2026-05-26.md`.

**Failure mode:** generic shared-vocabulary terms (`project`, `status`, `output`, `files`, `match`, `verdict`, `diagnostic`, `teardown`, `parser`, `deposits`) over-match across unrelated entries. The 4 ground-truth cases all had at least one highly distinctive term (full function name, full slug, unique compound noun).

CEO scope decisions for v2:
- Keep BACKLOG Closed-section matching (Case 2's only signal)
- Lean algorithm: match only on high-distinctiveness terms
- Drop title-word matching entirely
- Preserve v1 parsing, output format, CLI, constants — algorithm change only
- Edit v1 script in place (handled by follow-up Plan B)

---
---

## STEP 1 — SA

---

> **FIRST — before doing anything else, claim this plan:** `import shutil; shutil.move("bellows/knowledge/decisions/executable-freshness-check-algorithm-v2-blueprint-2026-05-27.md", "bellows/knowledge/decisions/in-progress-executable-freshness-check-algorithm-v2-blueprint-2026-05-27.md")`. Read your specialist file and domain glossary first. **Task:** read v1 dev log at `bellows/knowledge/development/leftover-after-ship-tooling-implementation-2026-05-26.md` (this contains the ground-truth traces and the FP observation). Then produce a thin outline for the v2 blueprint addendum. The outline has 5 sections corresponding to (1) high-distinctiveness term extraction, (2) per-source matching rules, (3) FP validation against 6 currently-Open entries, (4) ground-truth re-validation against 4 recurrences, (5) implementation-edit guidance. For each section, produce ONLY a 2-3 sentence intent statement explaining what the section will contain in the full blueprint. Do NOT design the algorithm in this step — that is Step 2's job. Do NOT write regex shapes, threshold numbers, or traces. The outline is the scaffold; Step 2 fills it. **Deposits:**
> - `bellows/knowledge/research/freshness-check-algorithm-v2-outline-2026-05-27.md` — 5-section outline per the spec above; each section is just an H2 heading plus a 2-3 sentence intent paragraph
>
> Standard prompt feedback protocol → `bellows/knowledge/research/agent-prompt-feedback.md`.

---
---

## STEP 2 — SA

---

> Before starting, read `bellows/knowledge/research/freshness-check-algorithm-v2-outline-2026-05-27.md` and check the Output Receipt status field. If status is not Complete, stop and report the issue before proceeding. Read your specialist file and domain glossary first. Read v1 blueprint at `bellows/knowledge/research/leftover-after-ship-tooling-blueprint-2026-05-26.md`, v1 dev log at `bellows/knowledge/development/leftover-after-ship-tooling-implementation-2026-05-26.md`, v1 live output at `bellows/knowledge/research/backlog-freshness-check-2026-05-26.md`. **Task:** take the 5-section outline from Step 1 and fill each section in turn with the full blueprint content. Work through them sequentially. **Section 1 (high-distinctiveness term extraction):** specify the replacement for `extract_fingerprint()`. Keep only backtick-delimited identifiers (length ≥ 5), hyphenated compounds (length ≥ 12 chars total), underscore identifiers (length ≥ 8 chars, ≥ 2 underscores), executable slugs cited in the entry text. DROP title-word matching. State each regex literally. **Section 2 (per-source matching rules):** Git log requires ≥ 1 high-distinctiveness term overlap with subject. PROJECT_STATUS requires ≥ 1 slug-token overlap where the slug token is ≥ 6 chars. BACKLOG Closed requires ≥ 1 high-distinctiveness term overlap where the term is ≥ 12 chars OR is the same backticked identifier in both entries. **Section 3 (FP validation against 6 currently-Open entries):** read v1 live output. For each of the 6 Open entries, list every v1-flagged candidate, apply v2 rules, state whether v2 still flags it. Target zero false positives. **Section 4 (ground-truth re-validation):** for each of the 4 recurrences (set→list, precondition-failure-field, Phase 3b read-side, mcp\_\_vexp\_\_), trace v2 rules and confirm the catch still works. State which terms qualify as high-distinctiveness and which sources trigger. **Section 5 (implementation-edit guidance):** state what code changes are needed in `scripts/check_backlog_freshness.py` — which functions to modify, which constants change, what stays identical. A DEV agent should be able to apply this as a targeted edit, not a rewrite. **Constraints:** algorithm-only change, no parsing/output/CLI changes, Python stdlib only. **Deposits:**
> - `bellows/knowledge/research/freshness-check-algorithm-v2-blueprint-2026-05-27.md` — full blueprint with the 5 sections filled in per the spec above
>
> Standard prompt feedback protocol → `bellows/knowledge/research/agent-prompt-feedback.md`.
