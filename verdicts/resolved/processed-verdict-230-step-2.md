verdict: continue

**Rule 22(b) verified independently. The wiring is real and lands in 9 sites. Two findings — one closed in Step 3 as a verification row, one deferred as a follow-up. Neither blocks.**

## My prediction was wrong, and the hedge is why that was safe

I estimated ~25 existing assertions would change. **Zero did; 314 tests pass unchanged.** The plan said "re-derive the list by grep, do not trust this one" — and that clause is the only reason a wrong Planner number did not become a wrong instruction. This is the fifth wrong prediction in this lineage and Checklist #29 has now caught all five.

**The explanation is benign and I verified it:** test fixtures are written contiguously (`(1.20, 1.349)` under `(1.35, ...)` — already `next_floor - 0.001`), and most top out with a `99.999` sentinel that case 1 preserves. Recompute is a genuine no-op on well-formed fixtures. That is the engine behaving exactly as designed, not the wiring being skipped.

## Verified

- **9 sites wired**, 5 of them in `contracts.py` (`:4180`, `:4273`, `:4608`, `:4684`, `:6338`), plus `contract_import.py`, `gap_dashboard.py`, `contract_template_routes.py`, `documents.py`, `carrier_profiles.py`. Import-side calls sit in the CALLER's loop, not inside `insert_bracket_or_record_conflict` — the O(n²) trap avoided.
- **Site 5 (fuel-infer) handled correctly.** `TestMaterializationAgreement` proves the engine and the materialization logic agree (`rows_changed: 0`), so recompute was wired rather than deferred, and it is not silently overwriting inferred rows. This was the plan's named trap and it was met head-on.
- **The canary shares `PRECISION_THRESHOLD_MILLS` with the engine** — no second copy of the threshold, as required. It returns violations and does not raise.
- **The wiring executes in the live request path.** `/contracts/<id>/fuel/brackets/add`, `/bulk`, and `/delete-all` are exercised by `test_contracts.py`, `test_forms_and_uploads.py`, `test_upload_endpoints.py`, and `test_upload_6_fuel.py`. 314 passing tests through those routes proves `fuel["id"]` resolves, no exception is raised, and the transaction is not broken.

## Finding 1 — the wiring is proven LIVE, not proven EFFECTIVE. Close this in Step 3.

Every new test calls the engine or the canary **directly** on a fixture DB. Nothing drives a **route** and asserts that a stale ceiling was actually corrected as a consequence of the wiring. Grep proves the call is present in source; passing tests prove it does not crash. **Neither proves it does anything.**

That gap is my authoring error — QA row 10 asked for wire-in completeness "by grep," and grep presence is necessary, not sufficient. It is also the same shape as LESSONS entry 86 and as diag-229's struck Q6/Q7: evidence that cannot observe the thing it certifies.

**Step 3 closes it as a VERIFICATION row, not by authoring feature tests** (QA verifies; it does not repair — the plan-219 boundary). Add this row, with raw output:

> **Row 14 — end-to-end wiring effect.** Using an authenticated test client against a scratch DB (never `data/invoices.db`): seed a config with two contiguous brackets; POST a NEW bracket to `/contracts/<id>/fuel/brackets/add` whose floor falls between them, making the lower bracket's stored ceiling stale by <= 10 mills; then SELECT that lower bracket's `price_ceiling` and show it was rewritten to `next_floor - 0.001`. Quote the pre-value, the POST, and the post-value as raw output. Repeat once for the DELETE path (`/fuel/brackets/delete/<bracket_id>`), showing the surviving neighbour's ceiling corrected. **If either shows no change, that is a FINDING — report it, do not fix it.**

Two rows, one INSERT-class and one DELETE-class. That is sufficient; the remaining sites share the same call shape.

## Finding 2 — the constant extraction did not happen. Deferring.

My Step-1 verdict instructed Step 2 to extract `SENTINEL_CEILING_MIN = 99.0` and use it at both `:78` and `:199`. **It was not done** — `99.0` still appears three times (`:78`, `:86`, `:199`) — and the dev log and commit message do not mention it. A direct instruction was dropped without being flagged.

No live bug: Gate 0 still guarantees nothing malformed reaches `:199`. Blocking a 3-step plan to extract a constant is disproportionate, and Step 3 is QA and must not touch product code. **Deferring to a small follow-up.** Step 3 reports the duplication as a verified finding in the Forward Register with the exact line numbers.

**Noting the pattern for the record, since it is now twice in one arc:** diag-229 ignored an explicit "write unknown" instruction; Step 2 here dropped an explicit constant-extraction instruction. Both times the work was otherwise good and the omission was silent. Instructions that are not tied to a test or a gate are the ones that evaporate.

## Proceed to Step 3 (QA)

All 13 rows as written, plus Row 14 above. Baseline **2264 passed / 2 known** plus this plan's net new tests — the new files contributed a large count, so **report ACTUAL and reconcile against the dev log; never force the number.** Rows 2, 3, 9, 10 quote raw greps and diffs, not summaries. Row 9 (no database written) is the one that must not be waved through — this plan is forbidden from touching production data, and B2 is the plan that will.

The three standing prohibitions have now held for four consecutive plans: no Monitor, report-don-t-fix failing tests, PROJECT_STATUS via receipt only. Keep the streak.
