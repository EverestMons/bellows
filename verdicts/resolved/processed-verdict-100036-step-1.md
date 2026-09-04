continue

CONTINUE — census complete; closing a 1-step diagnostic. It settles FO-2, and it inverts what the author expected.

Q3 — HAS THE FALLBACK EVER BEEN SILENTLY WRONG? 3 blind spots (oracle=True, neutralised-fallback=False), all three the `[2]` plans — executable-312, -313, -324. ⛔ But ZERO actual outcome changes in the current corpus: all three carry `## STEP 2 — QA` headings, so the fallback coincidentally agrees. **The gate is correct by coincidence of heading text, not by mechanism.** Rename a heading and QA enforcement silently vanishes with `[2]` still declared. Latent, not realised.

⛔ AND A SEPARATE DEFECT CLASS THE QUESTION DID NOT ASK FOR. The 4 plans spelling `qa_steps: none` agree under the neutralised test (both sides False) — but IN PRODUCTION the fallback fires on the real heading and returns True while the oracle returns False. Those are FALSE POSITIVES: the fallback asserts a QA step exists where the declaration says there is none. The neutralised protocol made them invisible; they surfaced only because the instrument reported production behaviour alongside it.

Q5 — BLAST RADIUS, and this is the decisive number:
  (a) parse the list form in BOTH, keep the fallback  -> **0 plan+step outcomes change**
  (b) parse in both, REMOVE the fallback              -> **168 outcomes change**, current True -> False
168 legacy step executions have the fallback as their SOLE QA detector. Removing it would silently suppress QA enforcement across all of them. ⚠️ The author's instinct before measuring was that the fallback is a fail-open worth removing; the measurement says removing it is by far the more destructive option, and closing the parse gap is free.

Q6 — ONE PARSER OR TWO? One. Both consumers answer the same question ("is step N a QA step?"); they differ only in WHEN they ask — authoring vs dispatch. No semantic difference justifies two implementations.

Q7 — THREAD 102's NUMBERS: they were counting a DIFFERENT defect class (the old-format bare-number header corpus), not the bracket-spelling class. For the bracket class specifically: 3 plans, 10 fallback pairs, 3 blind spots. Thread 102 can now be re-scoped rather than carried as an open unknown.

WHAT THIS LICENSES, stated as measurement not recommendation: candidate (a) is free and closes a latent fragility; candidate (b) is measured at 168 suppressed enforcements. The `none` false-positive class is newly surfaced and is NOT addressed by either candidate — it belongs with FO-3's normalization work, which is already drafted in `close-failopen-defaults`.

Closing.
