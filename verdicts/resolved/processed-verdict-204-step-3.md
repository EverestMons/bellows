verdict: continue

**Final step. Plan 204 complete — the root cause of the duplicate-proposal loop is fixed and the corpus is verified intact.**

## QA quality: exemplary

All 11 mechanical gates PASS, including `rule_20_self_check` (banner byte-exact) and `qa_step_detection` (correctly resolved step 3 of 3). All **8 verification rows PASS**, each carrying the DB-source column per the evidence-source rule (entries 136/137's own lesson — not reproduced).

Evidence is genuinely RAW, not summarised: the actual pytest tail (`============================== 61 passed in 0.28s ==============================`) and a **hex dump** (`2d2d2d 0a0a0a`) proving entry 137's stored `raw_content` still ends with its separator. QA also correctly adopted the **61** baseline from the Step-2 verdict rather than the stale **52** in the plan header — it reconciled a known-wrong instruction against reality instead of copying it.

## What this plan achieved

- **Root cause dead.** Whitespace-only hash flips can no longer fire the ingest update path. Verified independently by the Planner: the exact byte delta from commit `e57a22b` that caused the corruption now yields an identical hash (`3ef6407b` both sides; previously `4ff4c905` -> `b9875afa`).
- **Second line of defence.** Terminal statuses (`implemented`/`rejected`/`superseded`/`reference`) can never be silently demoted by an ingest; genuine edits surface via `terminal_proposals_flagged` instead of being swallowed.
- **Corpus restored and intact:** `implemented 97, reference 2, rejected 15, stale 3, superseded 28` — the exact pre-corruption baseline. The catastrophic 64-demotion signature did not occur.
- **Loop closed:** work list is exactly **[138, 139, 140]**; entry 137 no longer regenerates a duplicate.
- **Suite 52 -> 61, 0 regressions**, including the regression test for the precise 137 case and the catastrophic-case assertion.

## Open items — carried, NOT closed by this verdict

1. **Cycle 203 re-dispatch.** Ingestion already committed, so the re-run will report `ingested_count=0` with work list `[138, 139, 140]` — expected, not an ingest failure.
2. **Proposals 98/121/130 — CEO Gate 1 decision.** Step 2's audit recommends leaving all three `stale` (underlying rules already codified; twins 122/123/131 correctly rejected). Planner concurs, but the formal disposition is the CEO's.
3. **Plan 154's advisory — deferred to Gate 1 per CEO decision 2026-07-16.** Its first production run measured 353 DB-wide overlaps and degenerates to tag equality. Its motivating case (proposal 131) is now known to be a symptom of the bug fixed here, so its value may have largely evaporated. Untouched by this plan.

Move the plan to `Done/`.
