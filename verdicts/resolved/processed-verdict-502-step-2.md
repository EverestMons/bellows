verdict: continue

Planner verification (Rule 22(b)) — plan 502, Step 2 of 2 (QA, TERMINAL). Ten of eleven gates PASS. The one FAILURE is adjudicated below and CEO-ruled; it is a plan-authoring defect, not a defect in the work.

## The gate failure, and why it does not impeach the step

`rule_20_self_check` reports "no QA deposit paths found". It is CORRECT and the plan is at fault: the gate scans only `.md` deposits (`gates.py`, `md_paths = [p for p in deposit_paths if p.endswith(".md")]`), and this plan's Step 2 declares a single `.txt`. ⚠️ **The two QA gates require DIFFERENT extensions of the same deposit** — `qa_test_result` takes the `.txt` list and demands a parseable pytest summary in it, while `rule_20_self_check` takes the `.md` list and demands the banner. A QA step must therefore declare BOTH; this plan declared one. Walk 3 introduced the `.txt` specifically to satisfy `qa_test_result` and did not notice it starved `rule_20`.

**The substance each gate exists to verify is present, in that one file:** the banner `Rule 20 — QA Self-Check Results` and the `PASSED — SELF-CHECK PASSED` line both appear, and so does the pytest summary. Nothing about the evidence is missing — only its declared extension is wrong. CEO ruled `continue` on that basis.

## Verified independently of the receipt

1. THE PIN TABLE IS SATISFIED, EVERY ROW. D4q net headings added = **0**. D4r rewritten = 313 added / 313 deleted, each equal to `B`. D5 markers = **313** = `B`. D6 = 14 quarantined still bare, 0 marked. D10 body invariance by `--numstat` = `313 313`. D7 = 370 and D8 = 1593344, both identical to their authoring pins — the corpus was never touched.

2. THE SUITE IS GREEN WITH A REAL BASELINE TO COMPARE AGAINST. 63 passed / 0 failed, against `D11_BEFORE: 63 passed, 0 failed` carried in the handoff file — **delta 0**. That comparison was possible only because the inter-step channel exists; the panel built it after finding the original "persist it in your receipt" instruction had no file behind it.

3. THE COMMIT BINDING WAS DONE CORRECTLY. QA bound `$CAP` via `log --grep`, not `HEAD`, resolving to `b5d20fc…` and cross-checking it against the handoff file's `CAPTURE_COMMIT`. This is the guard that exists because a wrap interleaving during a verdict gate makes `HEAD` pass on the wrong commit.

4. QUERYABILITY — THE POINT OF THE WHOLE ARC — IS PROVEN. `grep -cE '^## .*\[status: pending\]'` returns **74**, equal to the computed `B` − `L`, not to a transcribed constant.

5. THE MARKER-INDEPENDENCE FINDING WAS REPORTED HONESTLY RATHER THAN FORCED. QA states that the cross-tab is total — every `learned` row carries a target, every pending and unknown row does not — so marker-independence cannot be demonstrated on this data, exactly as the plan required. It then PROVED the property the right way: on a scratch copy with one `[target:]` removed, the query still returned `L`, showing it matches on `[status:]` alone.

6. KEY TRANSPARENCY ON THE COMMITTED BYTES: **299/299**, with the 14 unmatched rows correctly skipped — the `B` − `C` denominator the panel established after finding the naive form would crash on rows with no corpus id.

The arc's objective is met: `LESSONS.md` is now queryable for what still needs building, and the answer is 74.

Terminal step: close to Done.
