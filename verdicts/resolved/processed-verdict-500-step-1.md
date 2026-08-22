verdict: continue

Planner verification (Rule 22(b)) — plan 500 (CORRECTIVE to halted-499), Step 1. ALL SEVEN gates PASS. Every claim below was measured by the Planner against a `cp` copy of the corpus, with the live DB proven byte-identical by `shasum -a 256` before and after.

1. THE ACCEPTANCE CRITERION IS MET EXACTLY. The corrected `_key_heading` is the IDENTITY on **370/370** stored `source_heading` values. That is the property halted-499's version broke on 40 rows, and it is the whole point of the correction.

2. THE REGRESSION IS GONE, MEASURED BY CONTROLLED A/B (not a single-arm probe — the failure mode that made 499's defect illegible):
   - ARM A (control, no annotation): `inserted=11`, `unchanged=313`, `stale=0`
   - ARM B (3 headings annotated):   `inserted=11`, `unchanged=313`, `stale=0`
   - **(ii)** computed expectation 11 (324 parsed − 313 exact matches) == measured 11. Under 499 this arm gave **51**; the 40-row double-space regression is closed.
   - **(i)** B − A = 0 — annotation adds nothing, so 499's actual fix survives the correction.
   - **(iii)** `stale_proposals_marked = 0` in both arms — the 250 implemented proposals untouched.

3. THE CORRECTION IS BYTE-IDENTICAL TO THE FORM I VERIFIED BEFORE PRESCRIBING IT (`:52-56`): the regex gained a leading `\s*`, the body is `.sub('', heading).rstrip()`, and the internal-whitespace collapse is gone.

4. SCOPE HELD. The three call sites are untouched at `:146`, `:380`, `:480` — the plan forbade widening the change and the agent did not.

5. THE REGRESSION GUARD WAS EARNED, NOT ASSERTED. The step transcript carries 4 `1 failed` occurrences and 10 `FAILED` against 19 references to the guard — i.e. the mandated red-then-green sequence was actually run: the double-spacing test was written and observed FAILING before the fix, then passing after. A guard only ever seen green discriminates nothing; this one was shown to discriminate. Eight targeted tests added, including `test_key_heading_preserves_internal_double_spacing` (the regression guard proper) and `test_key_heading_identity_fixture`.

Continue to Step 2 (QA). ⚠️ Note for the QA step: assertion (ii) must be COMPUTED at run time as the plan directs — the authoring-time value 11 is a sanity signal, not a constant, and appending a single entry to `LESSONS.md` would legitimately change it.
