verdict: continue

CEO-directed continue. Diagnostic 290 answered all 11 questions; deposit carries all
five mandated sections and `## Unresolved` names exactly one item — Decision 1 — and
states explicitly that no other question is unresolved.

=== CEO DECISION 1 — RESOLVED 2026-08-01: OPTION A ===

Gate 2 is a SINGLE GOVERNANCE PLAN. There is no Plan B.

205 is codified as PROSE ONLY (the Checklist #26 amendment in PLANNER_TEMPLATE.md).
No `plan_lint` check ships. The CEO accepts that this codifies a discipline the record
shows failing 3-of-3, in preference to shipping a mechanical check that the diagnostic
proved cannot enforce the remedy's core.

Consequences that follow and bind the Gate 2 plan:
- No `Depends on:` — single plan, no dispatch ordering question.
- DECISION 2 (205 status-flip timing, from Q8) resolves trivially: with no code half,
  205 flips to 'implemented' with the other five. No proposal is held back.
- Gap Assessment applies at TEN doctrine edits (six proposals + two version bumps +
  two changelog rows), not twelve. Plan A must reconcile against 10.

=== WHY Q1's ANSWER IS ACCEPTED ===

Q1 concluded no useful subset of 205's remedy is statically checkable, and PROVED it
by execution rather than asserting it:
- Prototypes ran under /tmp only; `plan_lint.py` and bellows/ were never touched.
- Should-PASS and should-FAIL sets were reported separately, as mandated.
- The positive control is what killed the candidate: BOTH negative controls PASSED
  (ledger removed, ledger stubbed) because ledger references are scattered through the
  plan body, so the check cannot distinguish a populated ledger from an absent one.
  Without the control this would have returned "4 of 4 shipped plans pass" and read as
  validated.
- It further found plan 287 — a SHIPPED plan — scoring WARN, and drew the correct
  conclusion that a check failing a shipped plan is defective.
- Root cause is structural: "later folds are checked against it" is a drafting-time
  process, invisible to any deposit-time check. Ledger presence cannot be mandated at
  all (DRAFTING_CYCLE.md §4:137 — the self-check never gates on the Conflict Ledger,
  and the ledger is legitimately absent when no cross-lens conflict arises).

The diagnostic used its own escape clause rather than manufacturing a plausible
candidate. That is the outcome the question was built to permit.

Close the diagnostic. Gate 2 Plan A authors from this map by citation under Rule 27.
