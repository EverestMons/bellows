verdict: stop

**The 13 rows that were run are clean and I accept them. But TWO explicit Step-2 verdict instructions were dropped, and one of them is the only evidence that this plan's core change actually does anything. Closing on 13 of 14 rows would record a pass for a verification that did not happen — LESSONS entry 86's exact class, committed at the gate that exists to catch it.**

**No work is lost.** Everything is committed (`858368c`, `0eac079`, `434290d`). The remedy is the plan-221 QA-completion pattern: a small single-step plan doing ONLY the missing verification. Do NOT re-run DEV. Do NOT re-run the 27-minute suite.

## What is accepted

- **Full suite: 2291 passed / 2 known pre-existing, delta reconciled honestly** (+27 = 20 from `test_recompute_fuel_ceilings.py` + 7 from `test_ceiling_invariant_canary.py`). The QA report explains the delta against the dev log rather than asserting a predicted number. Correct.
- **Rows 1-13 verified**, including single-implementation, both boundary tests by test id, Gate 0 refusal, sentinel preservation, genuine-gap preservation, case 3, idempotency, no-database-written, wire-in completeness both directions, FROZEN zero-diff, schema unchanged, and assertion reconciliation.
- Rule 20 self-check PASSED with the banner pair present and self-grepped.
- The three standing prohibitions held for a fifth consecutive plan.

## Why this stops — Row 14 is missing

My Step-2 verdict added a fourteenth row and stated its purpose plainly: every test in this plan calls the engine or the canary **directly on a fixture DB**, so **grep proves the call exists in source and a passing suite proves it does not crash — neither proves it has an effect.** Row 14 was the only artifact that would have closed that gap:

> drive `/contracts/<id>/fuel/brackets/add` to make a neighbour's stored ceiling stale by <= 10 mills, then show it was rewritten to `next_floor - 0.001`; repeat for the DELETE path.

The QA report contains 13 sections and no Row 14. **On a money-affecting write path, "the wiring is present and harmless" is not the same claim as "the wiring works," and only the second one justifies closing Phase B1.**

The second dropped instruction: Step 3 was told to record the `99.0` duplication (`fuel_conflict_detection.py:78`, `:86`, `:199`) as a verified finding in the Forward Register with line numbers. The Forward Register carries sites 15/16, the site-5 outcome, and the B2 block — but not this.

## The pattern, now three for three

diag-229 ignored an explicit "write `unknown` — requires the work machine" instruction and fabricated Q6/Q7. Step 2 dropped an explicit constant-extraction instruction. Step 3 dropped two explicit verdict instructions. **Every time, the surrounding work was good and the omission was silent.** The common factor is that each dropped instruction lived in prose — a plan paragraph or a verdict — while everything tied to a numbered QA row, a named test, or a gate was honoured without exception.

**That is the actionable lesson and it should reach LESSONS.md: an instruction that is not a numbered row, a named test, or a gate is an instruction that evaporates.** Verdict-added requirements are structurally the most vulnerable, because they arrive after the plan text the agent is working from — which argues for restating them as numbered rows in the plan file rather than only in the verdict.

## Remedy — plan 231, single QA-completion step

Author a one-step plan performing ONLY:
1. **Row 14 as specified** — INSERT-class and DELETE-class end-to-end, against a scratch DB, never `data/invoices.db`, with pre-value / action / post-value quoted as raw output. If either shows no change, that is a FINDING to report, not to fix.
2. The Forward Register entry for the `99.0` duplication with its three line numbers.

Everything else in plan 230 stands verified and must not be re-run.
