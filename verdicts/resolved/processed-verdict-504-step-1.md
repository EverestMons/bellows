verdict: continue

Planner verification (Rule 22(b)) — plan 504 (CORRECTIVE diagnostic to 503, READ-ONLY), Step 1 of 1, TERMINAL. All eleven gates PASS. Verified independently of the receipt:

1. **BOTH RULES WERE APPLIED, AND INDEPENDENTLY.** The TSV records `rule1_partly` and `rule2_circular` as separate columns and does not short-circuit: entry 121 shows **Y on both** — it is simultaneously partly-enforced and circular — which is exactly what this plan's walk-1 fold required, and it is the case that would have been lost to a first-match rule. 106 and 191 are circular-only; 96 and 109 are partly-only. Every one lands `CODIFIED`.

2. **THE CORRECTED SET IS COHERENT AND I RE-DERIVED IT.** 15 distinct `PROMOTE` entries over 18 rows; 9 `CODIFIED` over 10 rows; 24 distinct entries total = the 22 `learned` candidates plus the 2 pending-but-enforced. Composition: 503's 19, LESS the three arbitrary PARTLY promotions (96, 109, 121) and the two circular ones (106, 191), PLUS `L4599`. **Zero PARTLY and zero circular entries survive** — the two rules did the work they were written for.

3. **THE INVERSE ERROR WAS CAUGHT.** `L4599` — "*A function that computes a LOOKUP KEY must be the identity*", the exec-499/500 lesson guarded by the `test_key_heading_*` suite — was marked FULLY by 503 and silently excluded because Q4 scoped promotion to entries already labelled `learned`. It is now `PROMOTE`. The other pending-FULLY entry was correctly rejected as circular. 503's error genuinely ran both ways.

4. **THE EXECUTABLE'S INPUT IS UNAMBIGUOUS, AND Q5 DID NOT REPEAT 503'S IDENTITY TRAP.** Two sizings are given and BOTH balance to 327 — which is precisely why 503's own identity check could not discriminate. Rather than leaving that ambiguity, Q5 states the executable's set outright: **the 14 `PROMOTE` entries carrying corpus ids**, with `L4599` deferred as a separate future state. Re-derived: 14 + 225 + 74 + 14 = 327, and 225 = 239 − 14.

⚠️ **A coincidence worth naming so no one misreads it later:** the corrected set totals 15 entries, numerically identical to 503's WRONG prose figure of 15. It is not the same 15 and is not a vindication of that figure — 503's was an unenumerated miscount of its own TSV; this is a derived set with a stated rule per row.

⚠️ **One imprecision, not blocking:** Q5 justifies deferring `L4599` as "no corpus id", but the executable edits `LESSONS.md` by HEADING, not by corpus id, so the id is not the real obstacle. The DECISION is right for a better reason — promoting a `pending` entry is a different edit class from demoting a `learned` one, and mixing them would widen the executable's blast radius. The companion plan should state that reason rather than inherit this one.

The arc's question is answered on a stated rule rather than a guess: **14 entries are `learned` under the CEO's completion definition**, and every exclusion carries the rule that produced it.

Terminal step: close to Done.
