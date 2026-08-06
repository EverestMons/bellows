verdict: stop

HALTED FOR A PLANNER AUTHORING DEFECT IN STEP 2. Step 1 is complete, correct, and
committed — nothing about its work caused this.

=== STEP 1 PASSES RULE 22 (a)-(e), VERIFIED BY READING, NOT BY SUMMARY ===

(a) exists — scripts/plan_lint.py +45, tests/test_plan_lint.py +245, dev log +128,
    committed as cc5f0e8.
(b) does what it claims — the three checks (g)/(h)/(i) are present at :224/:234/:250,
    each a bare print(), inserted after (f) and before the results loop.
(c) summary matches file — the agent claimed "none sets all_passed, appends to results,
    or changes exit code". VERIFIED: the only all_passed/results hit in that region is
    the pre-existing results-printing loop OUTSIDE the new checks. The plan's core
    invariant holds.
(d) no hedging — receipt Complete, success true, no permission denials.
(e) n/a at this gate.

Independently re-ran the targeted suite rather than trusting the dev log: 53 passed, 797
deselected — matching the log exactly. 42 existing tests unchanged, no fixture edits
needed. plan_lint still exits 0 on a real Done plan.

=== WHY IT IS STOPPED ANYWAY ===

The DEPOSITED plan carried two gate FAILs that I did not see, because every plan_lint run
during drafting was piped through head -4/-5 and the FAIL lines sat below the truncation:

  FAIL (c) QA banner pair — Step 2 DESCRIBED the Rule 20 block instead of containing it;
           the check requires both literals present in plan_text.
  FAIL (d) step 2 scope — a PHANTOM block: Step 2 had no scope block, but a Cycle Log
           constraint quoted the scope token verbatim while listing it as dropped
           machinery, and step 2's extracted text runs to EOF and swallows the Drafting
           Cycle. The entry recording one violation committed another.

Both are STEP 2 defects. Step 2 would run from the frozen pristine and fail its QA gate
on the missing banner (Rule 22(e)) with nothing for scope_check to verify. The pristine
cannot be corrected in place — hence stop and re-dispatch rather than a fix at this gate.

=== WHAT THE RE-DEPOSIT MUST PRESERVE ===

Step 1's commit cc5f0e8 STANDS. Do not revert it.

⚠️ Task A0 as written handles a DIRTY tree; this tree is CLEAN with the work COMMITTED.
That case is not covered, and a fresh Step 1 run would find the checks already present
with no instruction on what to do. The re-deposited plan amends A0 to detect the
already-applied-and-committed state at HEAD, treat Step 1 as a verified no-op, and
proceed — rather than reapplying and duplicating the checks.

Stopping 302. The corrected plan re-deposits immediately.
