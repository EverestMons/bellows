verdict: continue

Planner verdict on executable-403 step 1 (permanent version-assertion fix) -> continue to step 2 (foreground QA).

MECHANICAL GATE: all PASS (3 files: test_forge_export_sanitization.py, test_fuel_import_conflict.py, dev log; scope_check PASS — tests/ only).

SUBSTANCE (Planner-verified in code + ran both files):
- `from database import CURRENT_SCHEMA_VERSION` added to both files.
- The 3 assertions now reference the constant, NOT a literal: test_forge_export_sanitization.py:328 `assert int(version) == CURRENT_SCHEMA_VERSION`; test_fuel_import_conflict.py:268 + :293 `assert version["version"] == CURRENT_SCHEMA_VERSION`. Bump-proof — this ends the 394->396->401 recurrence.
- Legacy-DB fixture setup lines that stamp an OLD version were left intact (correct).
- Targeted run of both files: 32 passed, 0 failed.

Clean. Proceed to step 2 — FOREGROUND full-suite QA + Rule 20 (exercises the whole delete-not-xml feature from 401 + these fixes).
