verdict: continue

Step 1 clean. Rule 22 (a)-(e) run by reading the deposit and re-deriving its
load-bearing claim, not by trusting the summary.

(a) exists — 37181 bytes at the declared path.
(b) answers the questions — all ten mandated sections; E1-E5 each answered with verdicts,
    raw output, positive controls and retraction tests.
(c) summary matches file — the agent's summary table matches the fire-test table.
(d) zero hedging keywords, zero fails, escalate=false, no permission denials.
(e) n/a — diagnostic, no QA report.

INDEPENDENTLY VERIFIED: exactly three plans in the corpus carry an INHERITED FROM marker
— 289, 297, 298 — matching the deposit's 3/1365 claim precisely.

=== THE RESULT ===

  inherited-premise  FIRES                        3/1365, all true positives; self-
                                                  contained; Rule 20 profile. No positive
                                                  control available, and the retraction
                                                  test caught a false positive.
  clone-drift        DOES NOT FIRE                three constructions; origin-diff NOT
                                                  CONSTRUCTIBLE (305-line diff needing
                                                  semantic judgement).
  subtractive-trim   CONSTRUCTIBLE BUT UNTESTABLE 281's pre-trim state was never
                                                  committed. Mechanizable FORWARD under
                                                  per-phase commits; untestable BACKWARD.

⚠️ THE FINDING THAT INVERTS THE PREMISE: clone-drift does not fire because THE COLD PANEL
ALREADY FIXED 282 BEFORE COMMIT. The final artifact carries all four hardenings from 281;
the drift existed only in the draft. A post-hoc check on committed plans STRUCTURALLY
CANNOT catch this class — the defect never reaches the artifact a mechanism can see.
Mechanisms and panels are not substitutes: the panel operates on the DRAFT, the checker on
the PRODUCT.

C8 earned itself on first use — the retraction test, added at ACID 2 because (h) fires on
this plan's own retraction, caught a false positive in the inherited-premise checker that
the 1365-plan corpus sweep alone would have missed.

=== CEO DECISION AT THIS GATE: LOWER THE BAR, TAKE THE REFRAMING ===

The hold's bar changes from "a mechanism that fires on ITS OWN CASE" to "a mechanism that
fires on the DETECTABLE SURFACE of its own case."

  inherited-premise  surface = the marker            -> mechanism available (FIRES)
  clone-drift        surface = the claim             -> claim check available
  subtractive-trim   NO SURFACE — the absence of a   -> routed explicitly to the cold
                     check is invisible by definition   panel and §2.7 instruction

⚠️⚠️ A RESIDUAL COST THE DECISION CREATES, RECORDED SO IT IS NOT DISCOVERED LATER: the
executable this hold guards REMOVES T-2, which removes the cold panel from the seven
down-tiered plans. Subtractive-trim is now routed to that panel. For that population the
two moves cancel: the class ends up with instruction-only coverage. 281 — a
subtractive-trim failure — is one of the seven. This is not an objection to the
reframing, which is honest about what is mechanizable; it is the trade the reframing
makes visible, and it belongs in front of the CEO before the executable ships.

Closing 305.
