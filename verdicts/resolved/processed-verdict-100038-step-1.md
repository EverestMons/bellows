continue

CONTINUE — census complete; closing a 1-step diagnostic. It prices thread 117's RULING 2 shape question, and the pricing INVERTS the cheap-looking option.

⛔ THE DECISIVE FINDING. `propagation_check`'s SIGNAL changes in **3 of 271** fold pairs (1.1%) — and those 3 are likely ERROR lines from historical revisions the tool cannot parse, not fold-damage detections. **So C1 — adding propagation_check and cycle_check to fold_check's reader set — buys ~0 detections.** Its COUNT changes in **72 of 271 (26.6%)**, and that channel is invisible to C0 and C1 by construction. C2's count-delta extraction costs **~0.2ms per fold check** on top of C1. The valuable channel is nearly free; the intuitive one is nearly empty.

COST, measured over 6 runs each: C0 105.4ms · C1 236.2ms · C2 236.4ms. Thread 117's ~350ms estimate for the full battery holds as an upper bound.

⚠️ WHAT IS PRICED AND WHAT IS NOT — this is the load-bearing caveat and the note states it itself. The count channel's FIRE RATE is measured (26.6%). Its FALSE-POSITIVE FRACTION is NOT, and cannot be from this corpus: walk registers record fold-introduced findings at WALK granularity, not per commit, so count-only changes cannot be linked to real fold defects. **Exactly one true positive is verified** (`5ec0274`, DIVERGENCES 58→60). ⛔ Anyone choosing C2 on this note is choosing on a fire rate without a precision figure. Q3 is partially unanswerable and Q4 is unanswered; both are declared in the note's own "What this does not establish".

⛔ AND THE HABITUATION WARNING IS NOT WAIVED. Thread 117 named it as the real risk, and the measurement sharpens it: C1 delivers ~5× the output for zero additional actionable signal. A checker that fires more and says less is the exact shape of the WARNs this Planner walked past three times in one night.

METHOD — the reason I accept these numbers. The instrument was run over **321 fold boundaries across 62 plans, 271 usable**, with all 50 crashes accounted for (46 after-revisions missing, 4 before-revisions). `(o1)` was excluded from BOTH sides of every pair, so the comparison stays controlled, and the confound is declared: today's checkers run over historical revisions, which is invalid for absolute numbers and valid for deltas because the same tool version runs on both sides. ⛔ **The coverage statement AGREES with the question bodies** — it does not claim completeness it lacks. That is the specific failure diagnostic 100036 committed this same day in its Q7, and this note does not repeat it.

⚠️ TWO RECORD ITEMS, neither blocking:
  1. **No raw `.txt` evidence was deposited.** The plan's header pre-declared one, and a benign `qa_test_result` failure on account of it; in the event `qa_step_detection` correctly read this as not a QA step, that gate never ran, and no `.txt` landed. Nothing failed — but the pre-declaration describes an artifact that does not exist, so these numbers are reproducible only by re-running `tools/fold_signal_census.py`.
  2. **The census independently re-discovered thread 130.** Its 46 unusable after-revisions are plans deleted from `drafts/` on deposit — the same sidecar abandonment that makes all 63 shipped `fold_check` verdicts unverifiable. Filed 2026-09-04 from a separate measurement; the two agree.

WHAT THIS LICENSES, as measurement and not recommendation: C1 is not worth its output volume on this evidence; C2's channel is where the signal is and its overhead is negligible; and the decision between them still needs Q4's precision figure, which requires commit-granularity ground truth the registers do not carry. ⛔ Thread 117 or its successor decides. This plan priced it and chose nothing, as its brief required.

Closing.
