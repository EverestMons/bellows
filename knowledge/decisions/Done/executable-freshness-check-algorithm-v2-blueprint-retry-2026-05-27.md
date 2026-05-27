# Bellows — Freshness-Check Algorithm V2 Blueprint (Retry)
**Date:** 2026-05-27 | **Tier:** small-build | **Dispatch Mode:** bellows | **Test Scope:** n/a | **Execution:** Step 1 (SA) | **pause_for_verdict:** always

## How to Run This Plan

Deposit into `bellows/knowledge/decisions/`. Bellows dispatches Step 1 (SA) — single step. SA fills the v2 blueprint sections per the outline from a prior step. Plan pauses for CEO review.

This is a retry. Prior attempt (Plan A Step 2 in `halted-executable-freshness-check-algorithm-v2-blueprint-2026-05-27.md`) timed out at 636s with no agent output. The retry adds an explicit early-output instruction at the start of the step to anchor the agent in producing visible work before the inactivity threshold.

## Context

V1 implementation at `bellows/scripts/check_backlog_freshness.py` (239 LOC) produced 6/6 false-positive flag rate. Outline of v2 blueprint at `bellows/knowledge/research/freshness-check-algorithm-v2-outline-2026-05-27.md` (5 sections with intent statements). V1 blueprint at `bellows/knowledge/research/leftover-after-ship-tooling-blueprint-2026-05-26.md`. V1 dev log at `bellows/knowledge/development/leftover-after-ship-tooling-implementation-2026-05-26.md`. V1 live output at `bellows/knowledge/research/backlog-freshness-check-2026-05-26.md`.

CEO scope decisions for v2:
- Keep BACKLOG Closed-section matching (Case 2's only signal)
- Lean algorithm: match only on high-distinctiveness terms
- Drop title-word matching entirely
- Preserve v1 parsing, output format, CLI, constants
- Algorithm-only change, Python stdlib only

---
---

## STEP 1 — SA

---

> **FIRST — before doing anything else, claim this plan:** `import shutil; shutil.move("bellows/knowledge/decisions/executable-freshness-check-algorithm-v2-blueprint-retry-2026-05-27.md", "bellows/knowledge/decisions/in-progress-executable-freshness-check-algorithm-v2-blueprint-retry-2026-05-27.md")`. **THEN, immediately and BEFORE any other reads or work: post a short visible message to chat (1-2 sentences) confirming you have claimed the plan and stating your immediate next action.** This is a liveness anchor to defeat the inactivity timeout — prior attempts at this work hung in a silent reading phase past the 600s threshold. Examples of acceptable confirmation messages: "Plan claimed. Reading the outline and v1 dev log now." OR "Claimed. Starting with v2 outline read, then v1 dev log, then drafting Section 1." Keep it brief. **AFTER posting the confirmation:** read your specialist file and domain glossary. Then read the v2 outline at `bellows/knowledge/research/freshness-check-algorithm-v2-outline-2026-05-27.md` — this gives you the 5 sections you are filling. Then read v1 blueprint at `bellows/knowledge/research/leftover-after-ship-tooling-blueprint-2026-05-26.md`, v1 dev log at `bellows/knowledge/development/leftover-after-ship-tooling-implementation-2026-05-26.md`, and v1 live output at `bellows/knowledge/research/backlog-freshness-check-2026-05-26.md`. **As you finish reading each file, post a 1-line acknowledgment** (e.g., "Read v2 outline." → "Read v1 blueprint." → "Read v1 dev log." → "Read v1 live output."). These keep the inactivity timer warm. **After reads complete, draft the blueprint section by section. Post a 1-line marker as you START each section** ("Drafting Section 1." → "Drafting Section 2." etc). **Section 1 — High-distinctiveness term extraction:** specify the replacement for `extract_fingerprint()`. Keep only backtick-delimited identifiers (length ≥ 5), hyphenated compounds (length ≥ 12 chars total), underscore identifiers (length ≥ 8 chars, ≥ 2 underscores), and executable slugs cited in the entry text. DROP title-word matching. State each regex literally. **Section 2 — Per-source matching rules:** Git log requires ≥ 1 high-distinctiveness term overlap with subject. PROJECT_STATUS requires ≥ 1 slug-token overlap where the slug token is ≥ 6 chars. BACKLOG Closed requires ≥ 1 high-distinctiveness term overlap where the term is ≥ 12 chars OR is the same backticked identifier in both entries. **Section 3 — FP validation against 6 currently-Open entries:** for each of the 6 Open entries from v1 live output, list every v1-flagged candidate, apply v2 rules, state whether v2 still flags it. Target zero false positives. **Section 4 — Ground-truth re-validation against 4 recurrences:** for each of the 4 cases (set→list, precondition-failure-field, Phase 3b read-side, mcp\_\_vexp\_\_), trace v2 rules and confirm the catch still works. State which terms qualify as high-distinctiveness and which sources trigger. **Section 5 — Implementation-edit guidance:** state what code changes are needed in `scripts/check_backlog_freshness.py` — which functions to modify, which constants change, what stays identical. **Constraints:** algorithm-only change, no parsing/output/CLI changes, Python stdlib only. **Deposits:**
> - `bellows/knowledge/research/freshness-check-algorithm-v2-blueprint-2026-05-27.md` — full blueprint with all 5 sections filled per the spec above
>
> Standard prompt feedback protocol → `bellows/knowledge/research/agent-prompt-feedback.md`.
