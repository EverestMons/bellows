verdict: stop

Step 2 (QA) — GATE FAILURE, verified real: rule_20_self_check FAIL, and the
Planner confirmed the banner is genuinely absent from the deposited report
(grep for 'Rule 20'/'PASSED' returns nothing) — the mandatory self-check
block never ran. Not the benign parser-truncation class.

What is NOT in question (Planner-verified raw, independent of this QA):
- Step 1's writes are committed and correct per id: 327/328/329/330/332
  accepted|codify|ceo, 331 reference|backlog|ceo, accepted|codify=5,
  proposed=0, entries 324 with sentinel-318 hash intact.
- The QA's substantive rows and evidence files are present and raw; only the
  mandatory Rule 20 machinery was skipped.

Disposition per the QA-process-failure convention: STOP; a QA-ONLY corrective
plan follows against the committed state (same verification rows + the Rule 20
canonical block, commit-evidence-first). Never re-run the full plan onto
already-written rows. The corrective deposit carries the stable slug's
corrective suffix and a narrowly-keyed A0.
