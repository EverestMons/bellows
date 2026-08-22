verdict: continue

Planner verification (Rule 22(b)) — plan 501 (diagnostic, READ-ONLY), Step 1 of 1, TERMINAL. All eleven gates PASS; no failure to adjudicate. Verified independently of the agent's Receipt:

1. THE RATIFIED CARVE-OUT WAS RESPECTED, AND I MEASURED IT RATHER THAN READING THE C5 ROW. The live corpus is byte-identical to its pre-dispatch state: 1593344 bytes, mtime Aug 19 15:13, `lesson_entries` = 370 — the same three values I recorded before deposit. No sibling `.db` in that directory has a modification time inside today. `LESSONS.md` still hashes to the same sha256 prefix (717949afd59b) it did at authoring. The A/B wrote only to `/tmp/diag-501-scratch/`, as the deviation permits.

2. THE KEY-SAFETY PROPERTY HOLDS — RE-DERIVED BY ME, NOT ACCEPTED FROM THE FINDINGS. I reconstructed the annotated heading for every row of the deposited TSV and asserted against the live corpus with `_key_heading` imported from `src/lessons_forge.py`:
   - `_key_heading(annotated_file_heading) == stored_source_heading` — **313/313**, zero failures, 14 unmatched rows correctly skipped as having no stored row.
   - `_key_heading(stored) == stored` over all stored values — **370/370**, zero failures.
   This is the strong form the plan mandated, measured against real stored data rather than a fixture. The annotation is safe to apply: it resolves to the same corpus row and inserts nothing.

3. THE A/B CONTROL ARM WAS EXECUTED, NOT MERELY DESIGNED — the requirement that motivated the contract deviation. ARM A (annotated) inserted=14; ARM B (unannotated) inserted=14; deltas identical. The 14 are the genuinely-unmatched headings, which insert on both arms, so the annotation itself adds nothing. Had ARM A exceeded ARM B, that is the exec-499 defect and the harness would have caught it mechanically.

4. THE MAPPING IS INTERNALLY CONSISTENT AND I CHECKED THE ARITHMETIC RATHER THAN THE SUMMARY. 327 rows, one per dated heading, distributing 239 learned / 74 pending / 14 unknown. Each reconciles to the plan's partition rule: 239 equals the restricted-run PASS count; 14 unknown equals 11 UNDECIDABLE plus the 3 in-file conflicting entries; 74 pending equals 63 matched-not-implemented, less those 3 quarantined, plus 14 unmatched. The 74 was predicted independently by the cold scout before the run.

5. REPRODUCTION IS HONESTLY REPORTED. 262 PASS / 20 UNDECIDABLE / 0 FAIL against 498's 260/22/0, with the delta accounted entry by entry: the FORGE_QA.md path fix flips one entry to PASS, the two walk_register_lint.py entries resolve correctly but stay UNDECIDABLE on threshold, and one entry moves on stop-list sensitivity. That is the definition of reproduction this plan set — matching after accounting for 498's three documented resolution failures — and the agent did not chase the target number by reproducing the bug.

6. THE THREE DEPOSITS EXIST AND ARE SUBSTANTIVE. `scripts/detect_learned.py` parses, opens the DB read-only, and takes the four parameters the plan required. The TSV carries the mandated six columns with a basis on every row. The findings document answers Q1-Q7 in the mandated answer order.

The gap that motivated this plan is closed: the detector 498 built but never deposited is now a re-runnable artifact, the conflicting-proposal precedence is resolved against measured data, and the annotation mapping exists as reviewable data rather than a derivation the executable would have to repeat.

⚠️ Process note, not a defect in this step: the CEO's ratification commit advanced ROOT HEAD mid-run, between this step's C7 before/after snapshots. The agent read it correctly as the ratification. It would not have been legible had the commit been unrelated — committing to a shared repo while a diagnostic's C7 baseline is open injects a foreign HEAD change into the one guard watching blast radius.

Terminal step: close to Done.
