verdict: continue

Scope_check false positive. forge.db is the EXPECTED target — the plan runs ALTER TABLE + UPDATE against the live DB. Migration code confirmed at db.py:168 (valid INTEGER column + backfill). Query filter (valid=1) confirmed in src/. Tests confirmed in test_refinery.py. Proceed to Step 2 QA.
