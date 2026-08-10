verdict: continue

Terminal step. All seven gates pass, Rule 20 PASSED, all eleven deliverable
items verified. Close to `Done/`.

## FORWARD 46 check — run again, as at step 1

- `steps`: two rows, step 1 and step 2, both complete. No third.
- Step 1 ended 13:53:57; step 2 started 14:02:53. **Nine minutes and a verdict
  gate apart — separate dispatches, separate contexts.**
- Commits: two from Step 1, one from Step 2. No overlap.

**This QA is the independent check plan 336 never got**, and unlike 336 the
independence is demonstrable rather than asserted. Precondition 1 re-derived the
register pin to the full 40-character sha and found it unmoved; Precondition 2
proved Step 1's dispatch from git.

## The two items that had never been exercised

**Item 9 was RUN, not asserted.** The QA constructed the violation the plan
mandated — replaced one em-dash with a hyphen — and reported the detection with
its byte offset and both contexts:

```
original: 0xe2 (context: b'SS m \xe2\x80\x94 n')
tidied:   0x2d (context: b'SS m - non')
CONSTRUCTED VIOLATION DETECTED
```

That is the observe-the-effect standard met on its first outing, on a check
written three passes earlier specifically because presence-tests were passing
vacuously across this plan.

**Item 11 passed, and it passed VACUOUSLY — the report shows this but does not
say it.** The 14 instances are 3 m + 1 q + 1 r + 9 s, so no `instance_id` appears
twice and the linking rule had nothing to exercise. The step-1 verdict asked for
that to be recorded as "passed with nothing to test". The data is laid out
plainly enough that any reader can see it, so this is **record-class and does not
justify a stop** — but it is worth naming, because a check with no reachable
failing state, reported as a clean PASS, is precisely the class C6 exists for.
**It appeared inside the QA report of the plan that opened C6.**

## The answer this diagnostic was built to produce

**All 14 instances are RECOVERABLE-RECONSTRUCTED. Zero verbatim, zero
unrecoverable.** The walk register preserved *descriptions* of the defects, never
the lines that carried them.

Dispositions: **m, q, r REDESIGN · s HOLD. No class reaches SHIP-warn**, because
every recall figure rests on a reader's reconstruction and the floor requires at
least one verbatim hit.

**FORWARD 48 is answered and can be closed against this plan.** The question was
whether a recall measurement would overturn 336's rejections. It does not — but
it replaces a null over the wrong population with a measured result over the
right one, and it says exactly why the right population cannot yet carry the
measurement.

## What this closes and what it opens

`m`/`q`/`r`'s REDESIGN and `s`'s HOLD now rest on precision AND recall, stated as
a pair, as the plan required. **No build plan is authorized by any of them.**

The owed successor is named in the findings: an instrumentation plan for
fold-granular draft history (**FORWARD row 49**). All four classes route there.
A reconstruction cannot price a matcher; only real pre-fold text can, and the
shop does not currently produce it — except for this plan's own cycle, whose
per-phase-committed walk register is the first instance of the record row 49
asks for.
