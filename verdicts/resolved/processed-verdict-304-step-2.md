verdict: continue

Step 2 clean. Rule 22 (a)-(e) run by reading the deposits and re-deriving the diff
accounting, not by trusting the report.

=== THE DIFF CLOSES EXACTLY ===

  13 lines removed = 11 (i) warnings
                   + 1 orphaned header (diagnostic-276 produced ONLY an (i) warning, so
                     with (i) gone the plan emits nothing and its header disappears)
                   + 1 HEAD-pin line
   1 line added    = the new HEAD pin (bellows 716f6ab -> 8e085fa, Step 1's commit)

⚠️ ZERO (g) or (h) lines appear in the diff. That is the proof a warning count could not
give: a count cannot see a (g) line silently lost while an (i) line disappeared. The diff
can, and nothing but (i) moved.

(g)'s true positive SURVIVES corpus-wide — "ledger out of order: C15 before C13" is
present in sweep-after.txt at :1159, not merely in a local control.

Full suite 846 passed, matching the prediction exactly. Predicted numbers landed across
this plan — 49 targeted, 846 full, ~24 lines against an actual 23 — and every one was
reported as an actual rather than asserted.

Task Q0's re-pin: most recent commit touching either file is Step 1's 8e085fa, no foreign
commit intervened.

Rule 20 banner and PASSED line byte-exact. Zero hedging keywords, zero fails.

=== RESULT ===

plan_lint now carries two drafting-cycle checks, both earning their place:
  (g) ledger ordering  — 1 fire across 1362 plans, a TRUE POSITIVE in a shipped, closed
                         plan that a full drafting cycle, an ACID pass and a cold panel
                         had all read without noticing.
  (h) stale closing    — 0 corpus fires, and it catches on demand the class that recurred
                         five times across four plans today, every previous time caught
                         only by a manual sweep.

(i) is gone with its five tests. It could not distinguish a plan id a diagnostic
DISCUSSES from one it DEPENDS ON — the entity-extraction problem flagged when it was
first scoped, which narrowing to backtick-quoted ids moved rather than solved.

Closing 304.
