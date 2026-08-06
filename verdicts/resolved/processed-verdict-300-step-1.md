verdict: continue

Part B (doctrine edit map) — the step is logged `non_zero_exit_1`, and the verdict is
CONTINUE ANYWAY on verified evidence, not on trust. Recording why.

=== THE FAILURE IS POST-COMPLETION, NOT MID-RUN ===

raw_output is capped at 5000 chars and carries only the init line plus the plan read; there
is no NDJSON result, so `parsed` is empty and the daemon recorded exit 1. But the DEPOSIT IS
COMPLETE: 392 lines, all six mandated sections (Unresolved, CEO decisions surfaced, What this
map can and cannot establish, The "wide" definition, Edit map, Gap Assessment) plus per-question
sections B1-B7, terminating exactly on the derivation-citation instruction that the deposit
structure specifies as its last item. The process died on exit, after writing its work.

The deposit was UNCOMMITTED at discovery -- the state in which transient step deaths lose work.
Rescued to /tmp, verified, then committed as part of this close-out.

=== RULE 22(b): RE-RUN FROM LIVE STATE, NOT READ FROM THE REPORT ===

  claim "a 222-row table"
    -> sqlite3 lesson_proposals COUNT(*) = 222. EXACT.
  claim per-plan row counts (289 -> 6, 284 -> 8)
    -> executable-289.md / executable-284.md read verbatim: "route` on 6 canonical proposals",
       "route` on 8 canonical proposals". CONFIRMED.
  claim B3(c) plan_lint binds to DECLARED TIER, not triggers
    -> cited plan_lint.py:163-219 with the mechanism enumerated, and carries POSITIVE CONTROLS
       on its zero results (grep -nF 'T-7' on PLANNER_TEMPLATE.md -> 0 hits shown, not asserted).
       This is the question that decides doctrine-only vs two-repo, and it is answered with the
       anti-vacuity measure the plan mandated.

=== THE SUBSTANTIVE RESULT ===

Recommended wording adds ONE clause to T-1: "or mutates every row of a canonical table."
Case (i) -- the corpus-wide reversible UPDATE that broke the original candidate -- now FIRES
and stays T2. Case (ii) is still caught by T-5. Disposition 3 discharged.

The trade is reported without flattery: ALL SEVEN down-tiered plans still lose their panels
(they mutate 2-8 rows of 222), of which THREE of the five assessable lose a finding nothing
else would have caught. 283/284 counted as unassessable rather than folded into either outcome
-- exactly as the plan required.

Closing 300. The residual trade is a CEO decision and is surfaced, not resolved.
