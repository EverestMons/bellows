# Dev Log — Forge Lifecycle Reporter Diagnostic 2026-09-09

**Plan:** 100058 | **Thread:** 256 | **Step:** 1 (DIAGNOSTIC)  
**Scratch dir:** `/tmp/forge-reporter.yQNrku` (removed after step)  
**DB backup:** `sqlite3 /Users/marklehn/Developer/bellows/lifecycle.db ".backup /tmp/forge-reporter.yQNrku/lifecycle-scratch.db"` — live DB never opened; all queries on scratch copy.

## Pins re-derived (P1–P3)

**P2 (the baseline, verbatim):** plans ≥ 100040 joined to steps: 25 step rows (24 with a duration; 100051's `running` row has none); by step: avg 22.3 min, min 4.3, max 82.4, avg turns 76, cost 86.12 USD; the longest: 100053 step 1 82.4 min / 264 turns / 12.20 USD; 100052 step 1 48.3 / 165 / 7.82; 100041 step 1 41.7 / 113 / 5.33; QA steps (step 2) 4.5–14.2 min

**P1 re-derived:** pytest summary: `20 passed in 0.11s`. `generate_reconstruction_data(100057, Path(scratch_db))` returns keys: `commits, deposits, derivations, gate_events, plan, plan_file_exists, plan_file_path, steps, totals, verdicts`. Steps row: step 1, status=awaiting_verdict, cost_usd=1.9549836, turns=55, duration_s=858.561. `get_live_plans_status(Path(scratch_db))` returns 1 row (plan 100058, this plan — DB moved; P1 measured 0 rows before 100058 started). `plan_file_path` is now a valid path (P1 measured None): `plan_doc_ref` was set in the DB when plan 100057 closed, after P1 was measured. No mechanism mismatch.

**P3 re-derived:** awaiting_verdict/closed: 16, awaiting_verdict/halted: 5, complete/closed: 67, complete/halted: 6, running/abandoned: 1, running/in_progress: 1. `steps.role`: 0 of 100 non-null (100 total rows; 99 at P3 measurement + 100058 step 1 added since).

**DB growth since P2:** 27 rows now vs 25 at P2 (100056 step 1 and 100057 step 1 added; 100058 step 1 started). P2 stats re-confirmed against 25 duration rows: avg 22.3 min, cost 86.12 USD, avg turns 76.

## The reporter on today's DB (Q1)

20 tests pass. Reporter opens the September DB with `?mode=ro` and reads all tables correctly. Key behavioral finding: `_open_lifecycle_db` (src/reporter.py:411) requires the full path to the DB **file** — passing a directory raises `OperationalError` caught as `{"error": "lifecycle.db not available"}`.

Three lists:
- **Unchanged:** all functions; all 20 tests pass including 12 lifecycle reconstruction tests.
- **Correct data, wrong resolution:** `_resolve_deposit` for relative `declared_path` values (resolves against `GITHUB_ROOT / declared_path` which gives the wrong location for paths like `knowledge/development/…`; shows `exists=False`). Absolute declared paths resolve correctly via Python pathlib semantics. Plan file, verdict, and commit resolution all work on this machine.
- **Failing:** none. Plan 7 returns `"Plan 7 not found"` — correct, it is not in the mini's DB.

`plan_file_path` shift: P1 measured None; now returns a valid path. Cause: `plan_doc_ref` was NULL at P1 measurement (plan 100057 not yet closed); now set. Resolver prefers `plan_doc_ref` when non-null (src/reporter.py:543). DB-moved count, not mechanism mismatch.

`get_live_plans_status` returns 1 row (plan 100058, this diagnostic step). P1 measured 0 rows. DB-moved count.

## Q1–Q6 in one table

| Q | question | answer |
|---|---|---|
| Q1 | Does the reporter still run? | Yes — 20 tests pass, all lifecycle functions return valid data on September DB |
| Q2 | Two-reader match on timing table? | YES for all 25 duration rows: duration_s within 0.001 s, turns exact, cost exact |
| Q3 | What does the residue show? | 16 closed-plan steps still `awaiting_verdict`; mechanism: `_consume_verdicts` never calls `record_step_end`; role column 0/100 non-null |
| Q4 | What does reporter add over 12 lines? | Derivations, gate events (with overridden/override_ref), commits with resolved subject (git call), deposit `exists` (filesystem), verdict file `exists` — plus step_timing.py code block in research doc |
| Q5 | The park pointer | Threads 256/257/258; `_open_lifecycle_db`:411, `generate_reconstruction_data`:621, `write_reconstruction_report`:729, `get_live_plans_status`:923, `_resolve_plan_file`:535; Module 4 (reporter) in PROJECT_BRIEF.md; `setup_agent_staleness_audit` in src/lab.py:655; no live code path in any watched repo |
| Q6 | Diagnostic cost | Item 0 ~28 s (backup + venv); Items 1–5 < 10 s total; all items complete in under 40 s |

**pytest correlation:** r=0.519, n=25. Moderate positive; explains ~27% of duration variance. Not deterministic. 100048 step 1 is a high-pytest outlier (404 mentions, 19.6 min); 100053 step 1 is the high-duration case (82.4 min, 244 mentions, 264 turns — turns is the better predictor than pytest count for this case).

## What the doc does not establish

One DB, one machine; `pytest` count is word frequency not run count; role column empty (DEV/QA inferred from step number); reporter resolvers were built for the Air's layout; within-type correlations not computed (n too small).
