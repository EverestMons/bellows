verdict: continue
Rule 22 verification on the deposit (`invoice-pulse/knowledge/research/pytest-xdist-fixture-characterization-2026-05-18.md`) passes. All 7 investigation steps addressed with concrete findings:

Fixture inventory: 4 conftest fixtures (db, _isolate_knowledge_writes, app_client, seeded_db), ALL individually xdist-safe. db uses :memory:, app_client uses tmp_path.

Root cause identified: `app.py:119 init_db()` executes at module-level import time, causing 10 xdist workers to race on `data/invoices.db` during collection. This is the structural problem, not the fixtures. The `--ignore=tests/test_routes.py` experiment validated this — workers still deadlocked because 11 other test files also `from app import app` at module level.

Classification: Medium (4-14 files, ~90-105 LOC). Why not Small: app.py change is structural, can't be localized to one test file. Why not Large: per-test isolation is already good.

Recommended fix pattern: (1) Defer `app.py:119 init_db()` under `__name__ == "__main__"` guard, (2) Add per-worker session fixture in conftest.py via `tmp_path_factory.getbasetemp()`, (3) Refactor test_routes.py and test_all_routes_modes.py module-level code into fixtures, (4) Exclude/rename 10 dead `test_upload_*.py` files via `collect_ignore`.

Production safety check confirmed: invoice-pulse runs as `python3 app.py` (line 5388), so `if __name__ == "__main__"` guard preserves production init. The existing comment at line 5396 ("init_db() already ran at module level — no need to call again") needs to be updated in the Dev plan since init would no longer run at module level.

Pause Reason Code was `header_pause` with `Gate Result Passed: True`; auto-proceeded per the 2026-05-18 LESSONS routing extension.
