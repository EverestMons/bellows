verdict: continue

**Rule 22(b) verified independently by the Planner. The deposit is SPLIT: Q1-Q5 and Q8 are sound and verified; Q6 and Q7 are UNSOUND and are struck.** The diagnostic is closed (1/1 steps) with errata annotated into the findings doc. Phase B proceeds on B1 only.

## Verified sound — Planner re-derived each independently

1. **Q2 (the highest-leverage question) is CORRECT.** `insert_bracket_or_record_conflict` is called from exactly two non-test sites — `gap_dashboard.py:2473` and `contract_import.py:571`. It is NOT a general INSERT choke point. The 7 named bypasses are real. Phase B therefore wires N sites, not one; v2 §135's per-route invariant risk is fully realized, as reported.
2. **Q4 is CORRECT and is the best news in the document.** `detect_bracket_structural_issues` (`fuel_conflict_detection.py:55-90`) is a genuinely pure function — no DB, no side effects, takes `(floor, ceiling, pct)` tuples for one config. Its predicate `if ceiling >= 99.0 and floor != max_floor:` (`:70`) is an EXACT, not approximate, implementation of the settled discriminator. Reuse closes constraint 2's biggest hazard.
3. **Q5 is CORRECT.** `gap_after` has zero producers, confirmed. The finding that the 10-mill threshold alone classifies genuine-vs-precision at recompute time is sound, and it means constraint 3 is honorable without populating the column. Good, honest reasoning.
4. **Q3 and Q1 hold.** The trigger assessment reaches the right conclusion by the right route — the batch-INSERT ordering defeat is the real dealbreaker, not the O(n^2) cost. The DELETE class is correctly identified as requiring recompute, and #8/#9 correctly identified as safe to skip.

## Struck — Q6 and Q7 rest on data that does not exist

**The plan instructed, verbatim: "If a data question cannot be answered from the exports, write 'unknown — requires the work machine' and name the exact query that would settle it. That sentence is a valid finding; a confident generalization from 0 rows is not." Q6 and Q7 did the forbidden thing instead.**

- **Neither export carries per-bracket rows.** The coverage export holds 21 aggregate config records (bracket_count, floor_min, ceiling_max, top_status, region, exposure) and nothing per-bracket. The discovery export holds 82 inconsistency rows + 3 genuine-gap rows = **85 of 2,088 rows**. There is no full bracket listing anywhere on this machine.
- **Q7's step distributions are therefore fabricated.** "Contract 3 (278 brackets): steps are 0.05 for the first 2 brackets (1.15->1.20, 1.20->1.25), then 0.01 for the remaining ~275" is not derivable from any available data — it appears to be the DHRN figure `{0.05: 2, 0.01: 28}` pattern-matched onto an unrelated config. Q7's load-bearing conclusion — *"Non-uniform steps only appear in configs that also have continuation formulas, so the median-step fallback never needs to handle the truly ambiguous case"* — rests entirely on it and does not survive.
- **Q6's "~99 rows touched" is a bare predicted number** (Checklist #29) built from "~21 last-bracket rows," which needs each config's stored last-bracket ceiling — available for only 4 configs. Unverifiable here.

## The two material corrections Phase B MUST carry

**C1 — Q7's case table would derive a top for seven configs the record forbids touching.** It assigns "Uniform step, no continuation -> `last_floor + step - 0.001`" to Contracts 1, 2, 7, 9, 15, 17, 18, 19, 20. Cross-referenced against the coverage export: **15/17/18/19/20 are the five missing-continuation configs** (all BOUNDED, all `obs_above=67`) whose continuation formula was DROPPED AT EXTRACTION per plan 218 Thread B, and **7 and 9 are the two Thread A truncation candidates** (GAP_ABOVE, obs_above 15 and 14). Synthesizing a last-bracket ceiling for a table that is itself truncated IS the inference the baton explicitly forbids ("Do NOT run fuel-infer on a truncated table"). **Seven of the nine configs in that row are configs Phase B must EXCLUDE or BLOCK, not derive.** Only Contracts 1 and 2 are legitimately in that class.

**C2 — the sanitized exports have NO stable config identity, and Q6/Q7 built config-specific rules on top of the labels anyway.** `_anonymize_section` assigns ordinal labels PER SECTION, so the same config carries different labels in different queries — demonstrated **within a single file**: discovery `query_1` attributes the 3 genuine-gap rows to "Contract 2" while `query_5` attributes the same 3 gaps to "Contract 5". Across files it is worse: coverage's "Contract 16" is the legitimate `99.999` open sentinel, while discovery's "Contract 1" is the repaired malformed sentinel at floor 6.15 — and coverage's "Contract 5" has zero brackets. The findings doc half-noticed ("Contract 2/'Contract 5' in discovery") and then proceeded to key an entire rule table to these labels. **No B2 verification step may be keyed to an export label.**

## Consequence — a better phase boundary than the one proposed

The document proposed B1 then B2, with B2 "low-risk given the 128-row footprint." That footprint is exactly the unverifiable number. But the split still works, and cleanly:

- **B1 (core wire-in) depends only on Q1-Q5 and Q8 — all verified sound. It is authorable now.** Recompute helper, N-site wiring, `detect_bracket_structural_issues` reuse, 10-mill threshold, runtime canary, and Q8's deferral (leave the import ceiling-require sites alone; the supplied ceiling is the NOT NULL placeholder and gets overwritten — no active conflict, correctly reasoned).
- **B2 (migration) depends on Q6/Q7 and is BLOCKED.** It needs a real per-bracket export with stable config identity. That is a CEO-side run on the work machine, and it is a new prerequisite this diagnostic surfaced rather than satisfied.

## Errata to annotate (diag-160 precedent)

Annotate the findings doc with a Planner errata section recording: Q6/Q7 struck with reasons; C1 and C2 in full; the 85-of-2,088 data-coverage fact; and the B1-authorable / B2-blocked split. Q1-Q5 and Q8 stand as written and are the authoritative wire-in map.

## Prompt-feedback note

The agent's self-reported "What worked" credits the Planner's three pre-deposit findings — correct, they were all confirmed. But the same receipt reports Q6/Q7 as answered "with grep-sourced evidence" when they had no evidence to source. **The instruction to write "unknown" was explicit and was not followed; that is the lesson candidate here, and it is the same class as LESSONS entry 86** (a step reporting success for a verification it could not actually perform).
