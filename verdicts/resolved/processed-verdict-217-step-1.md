verdict: continue

**Rule 22(b) verified independently — all three fix layers confirmed present and the flake empirically closed.**

- **Layer 1 (script, surgical):** the diff between plan-216's commit and this one on `repair_fuel_sentinel_20260716.py` is EXACTLY one call — `.replace(microsecond=0)` on the mtime rendering. No guard, SQL, or section-structure delta. The collision surface (dot-after-seconds fractions) is deleted for every future seeded value.
- **Layer 2 (narrow exclusion):** `_strip_env_headers()` removes only lines starting `db_path:` / `db_mtime:`; floors, ceilings, counts, and verdicts remain inside the scanned text. Used by BOTH leak tests.
- **Layer 3 (collision-proof seeds):** 4-decimal seeds (`17.3131 / 17.1010 / 17.5353`) present in the test file.
- **Determinism:** dev-log carries the raw 25-run tally (verbatim pytest lines per run); the Planner independently ran the file 15 more times — **15/15, 36 passed each**. Combined 40/40 against a defect that fired 1-in-~200.

Proceed to Step 2 (QA): all 13 original rows from halted-216 verbatim, plus rows 14-17. Row 17's hash pin is the value the CEO's runbook step 2 will compare — compute it at the FINAL commit of this plan, and remember the suite baseline is 2141 + the 36 tests this deliverable adds; verify and report actual counts, never force.
