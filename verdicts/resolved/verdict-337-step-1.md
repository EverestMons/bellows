verdict: continue

All seven gates pass. Proceed to Step 2 (QA).

## FORWARD 46 check — performed before writing this verdict, as row 46 asks

The `steps` table was compared against the actual commits and deposits, because
`pause_for_verdict: always` is a header contract the runtime does not police and
plan 336 ran all three steps in one dispatch three hours ago.

- `steps`: **one row** — plan 337, step 1, complete. 67 turns, 1568s, $6.08.
- `git log f5e485e..HEAD`: **two commits**, both Step 1's, both expected.
- No Step-2 deposit exists. The QA report and step-2 dev log are absent.

**The step contract HELD.** This is the first plan since the row was opened where
that could be confirmed rather than assumed.

## The C2 ordering guard fired, and it is provable from git

The guard's whole point is that label-before-match leaves a trace. It did:

```
320d547  evidence(337): labelled positive set — 14 instances across 4 classes
         .../labelled-positives.txt | 66 ++++++   (1 file changed)
8b1c538  findings(337): all four classes measured, SHIP-warn blocked (0 verbatim)
         dev-log, redesigned-m-q.py, positive-controls.txt, findings  (4 files)
```

Commit 1 carries the labelled set **alone**. Nothing else is in that tree. The
agent did not need to be trusted on the ordering and was not.

## The result, and the fold that decided it

**All 14 instances are RECOVERABLE-RECONSTRUCTED. Zero verbatim. Zero unrecoverable.**
The register describes defects as descriptions, never as the lines that carried
them, so every recall figure measures a reader's reconstruction rather than the
original bytes.

**Read without the verbatim floor, this reads as m 3/3, q 1/1, r 1/1 — near-perfect
recall, and three checks ship.** The floor was one sentence added by walk 3's
Destruction lens. With it, SHIP-warn is blocked on all four. That is the
difference between a correct answer and a confident wrong one, and it is the
clearest return the drafting cycle produced on this plan.

Two further folds paid out:

- The `## Instances covered by no class` section (walk 3) caught a real defect the
  class set cannot see: a `grep -c` recount returning MORE than before, because
  corrections cite the wording they fix. No class covers "a measurement tool that
  double-counts its own corrections."
- C.2's instruction to report the authoring-time list's errors found **two of eight
  cites wrong** — line 136 is not a defect instance, line 361 is not class `r` under
  the matcher's own definition. Both removed. The Planner's starting list was 25%
  wrong and the plan said so in advance.

`r`'s single hit is an accidental one: the matcher catches the `|` inside the
pattern, not a shell pipe. The agent reported that rather than banking it.

`s` HOLD is reinforced with data — 2 of 9, missing seven known wrong counts — and
the reasoning for HOLD over RETIRE is right: the misses are in the MATCHER, not
in the CLASS.

## For Step 2

**This QA step is the independent check plan 336 never got.** Precondition 2
requires it to assert it ran as its own dispatch; that assertion is now meaningful
because the step contract held here.

Items 9, 10 and 11 are new at the confirming pass and have never been exercised:

- **Item 9** (no normalization) carries a constructed violation — tidy one em-dash
  and confirm the item reports it. Run it; do not assert it.
- **Item 11** (multi-class linking) will pass **vacuously**: the 14 instances are
  3 m + 1 q + 1 r + 9 s, so no `instance_id` appears twice. **Record that it passed
  with nothing to test** rather than as a clean pass.

## Carried

The findings name their owed successor — an instrumentation plan for fold-granular
draft history (bellows FORWARD row 49). All four classes route there, because a
reconstruction cannot price a matcher. That is the diagnostic answering the
question it was built to answer, in the negative, with the reason stated.
