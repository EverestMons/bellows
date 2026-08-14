verdict: continue

Planner verdict on executable-396 step 1 (fix 3 stale version assertions) -> continue to step 2 (foreground QA).

MECHANICAL GATE: all PASS, zero failures (3 files: test_forge_export_sanitization.py, test_fuel_import_conflict.py, dev log; scope_check PASS — tests/ only).

SUBSTANCE (Planner-verified in code + ran the two files):
- All 3 assertions now read == 22: test_forge_export_sanitization.py:326, test_fuel_import_conflict.py:266 and :291.
- Targeted run of both files: 32 passed, 0 failed — the 3 formerly-failing (assert ==21) are green, nothing else disturbed.
- Change is test-literal only; no production code touched.

Clean. Proceed to step 2 — the FOREGROUND full suite QA + Rule 20. (The plan loudly forbids backgrounding, which was 394 Step 5's halt cause.)
