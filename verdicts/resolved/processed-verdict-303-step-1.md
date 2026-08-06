verdict: continue

Step 1 clean. Rule 22 (a)-(e) run by READING the artifacts, not the agent's summary.

=== A0-PRE AND A0-FIX BOTH DID THEIR JOBS ===

A0-PRE — the prior dispatch (302, halted for a Step 2 authoring defect) had already
committed the three checks as cc5f0e8. A0-PRE detected that, verified rather than
reapplied, and the checks are NOT duplicated: exactly one each of (g)/(h)/(i). The
already-applied-and-committed case A0 never covered is now handled.

A0-FIX — check (i) is gated on a questions region, with the reasoning in the comment
(halt-routing is a diagnostic concept; executables have steps, not questions). The
specimen is clean: (i) no longer fires on this executable, leaving only the earned T2
cold-panel WARN. Regression test present at tests/test_plan_lint.py:1273. Suite 54 passed
(up from 53), re-run independently rather than trusted from the dev log. The invariant
holds — all three checks remain bare prints touching neither results nor all_passed.

The dev log reported defects 2 and 3 (prose matching the directive regex; first-match-wins
letting a description shadow a real routing line) WITH recommendations rather than
silently broadening the check, exactly as instructed.

=== THE FORK STEP 2 MUST NOW MEASURE ===

With (i) running correctly, a five-plan sample:

  diagnostic-299   0 absent-from / 1 no-routing-line   = 1
  diagnostic-300   0 / 1                                = 1
  diagnostic-301   8 / 0                                = 8
  diagnostic-290   0 / 0                                = 0
  diagnostic-285   0 / 0                                = 0

301's EIGHT ARE ALL FALSE POSITIVES. They are plan ids it DISCUSSES — the seven
down-tiered plans and the T0 census cases — not inputs. 301's halt routing correctly
routes on the two upstream DEPOSITS, which is right. The check cannot distinguish a
subject from an input.

That is the entity-extraction problem flagged at draft time and narrowed around by
restricting to backtick-quoted ids. The narrowing moved the boundary rather than solving
it. (g) and (h) are genuinely mechanical; (i) is not, and that is now measured rather
than predicted.

CEO DIRECTED CONTINUE. Step 2's corpus sweep is exactly the instrument for this: it must
report per-check fire counts and ids across all five roots, pinned per Q0. The decision
on (i) — ship, scope harder, or drop — is the CEO's and belongs in the QA report's
findings, not in a Step 2 edit. Step 2 changes no code.

Note for Step 2: the checks are WARN-only and cannot block or change an exit code, so a
noisy (i) harms nothing while it is being measured.
