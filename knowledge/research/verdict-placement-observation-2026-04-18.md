# Observation — Bellows Verdict Placement (Structure vs. Reasoning)

**Date:** 2026-04-18
**Recorded by:** Planner (during Lessons Forge design session)
**Category:** Architecture / Placement audit
**Status:** Captured for future Bellows work — no action this session

---

## The observation

Bellows is already a structural (Layer 1) state machine: files transition between prefixes (`executable-*`, `diagnostic-*` → `in-progress-*` → `verdict-pending-*` → `Done/`), and gate validation runs mechanical checks at each boundary. This is Layer 1 infrastructure doing exactly what Layer 1 should do — mechanical, deterministic, no reasoning required.

However, the current verdict step requires Planner (AI reasoning / Layer 3) involvement for every transition, even when the verification work is itself mechanical. When a plan hits `verdict-pending-*`, the Planner:

1. Reads the findings file
2. Runs Rule 22 checks: does the file exist, does it answer the questions, does the summary match content, is there hedging language, are required evidence files present
3. If all checks pass → renames file to `in-progress-*` (resume) or `Done/` (close)
4. If any check fails → escalates

Steps 2 and 3 are mechanical. They are deterministic yes/no questions with deterministic outcomes. There is no judgment involved in "file exists" or "this row contains 'pending' which is a hedging keyword" or "rename on clean check." The Planner is currently running these checks manually with prose narration, but the work itself is Layer 1.

## The misplacement

This is a case of Layer 3 (real-time AI reasoning) being applied to work that belongs at Layer 1 (mechanical enforcement). The symptoms of misplacement are:

- Planner spends context window on narrating verification checks that could be mechanically validated
- Each verdict cycle requires a Planner conversation, even when the outcome is deterministic
- The same check patterns get run over and over with slight variation in framing
- The only cases where AI reasoning genuinely adds value are when verification fails — the common case (clean pass) is pure mechanism wearing a reasoning costume

## The target state

Bellows grows a verdict-validation stage that runs the Rule 22 checks mechanically:

- `verdict-pending-*` file is created after step completion
- Bellows (or an associated validator) reads the deposited findings file
- Runs the deterministic checks: file existence, keyword scan for hedging language, evidence manifest matching, content-vs-deliverable-list validation
- If all checks pass: auto-transition to `in-progress-*` (for mid-plan) or `Done/` (for terminal step)
- If any check fails: verdict-pending persists, Planner is flagged for judgment call

Under this model, Planner involvement in verdicts becomes the exception rather than the rule. The Planner is summoned when mechanical validation can't decide, which is where AI reasoning genuinely adds value. Clean plans proceed at Layer 1 speed.

## Why this observation matters

The three-layer architecture was committed in ADR-001 on this same day (2026-04-18). Within 30 minutes of ratifying the placement model, a real case of misplacement surfaced through conversational work, not through Forge analysis — the CEO noticed it directly. This validates two things:

1. The continuous-audit principle works even without formal Forge machinery. Placement misfits can surface through normal operations by anyone paying attention.
2. Lessons Forge, when built, should catch observations like this one systematically. This observation is exactly the shape of input Lessons Forge's classifier should recognize as a re-placement candidate (current: Layer 3; target: Layer 1).

## Recommended action

No action this session. Captured for future Bellows work. When Bellows next gets meaningful attention — likely during the verdict-mechanization or plan-truncation work already in BACKLOG — this observation should inform the design. The Rule 22 check set (file existence, hedging keyword scan, evidence file presence, summary-vs-content check) is a concrete starting point for what mechanical validation should cover.

## Relationship to existing BACKLOG items

The 2026-04-17 BACKLOG items on plan truncation and agent file rewriting are about protecting plan files from agent modification. This observation is about *reducing Planner involvement in verdicts* by moving verification to Bellows itself. Orthogonal but complementary — both push Bellows further toward Layer 1 self-sufficiency.

---

## References

- `ARCHITECTURE.md` — three-layer decision-flow architecture (Layer 1 / 2 / 3)
- `governance/adr/ADR-001-three-layer-decision-flow-architecture.md` — commitment to placement model
- `PLANNER_TEMPLATE.md` Rule 22 — Planner verification of deposited files (current mechanism, Layer 3)
- `forge/knowledge/research/bellows-writing-prefix-filtering-2026-04-18.md` — Bellows' current allowlist-based scanning (from today's diagnostic)
