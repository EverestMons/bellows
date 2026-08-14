verdict: stop
QA gate correctly failed (rule_22c) — 1 real regression, surfaced to CEO, stop confirmed. A narrow test-only corrective will be deposited.

Grounds:
- Full suite (raw evidence, knowledge/qa/evidence/.../full-suite.txt): 3 failed, 2601 passed. TWO failures are the CLAUDE.md-known pre-existing ones (test_activity_import::test_get_activity_import_page, test_fix_links::test_no_tariff_rate_has_fix_url). ONE is a real regression: test_pricing_versions_qa.py::TestDashboardUI::test_dashboard_shows_version_bar (:747), which asserts the dashboard renders the legacy version bar ("+ New Update", version labels) — deliberately HIDDEN in Step 2 (fold w2-3). Stale test asserting removed-by-design behavior; same class as the delete-form test Step 2 correctly inverted.
- The DEV work (Steps 1+2, merged to main d1ff765/fcd1d62) is CORRECT and stays; only the stale test needs updating. It slipped DEV because it lives in test_pricing_versions_qa.py (not matched by Step 2's -k contract run); the QA full suite caught it as designed.

Per verdict grammar (continue/stop only): STOP. A narrow test-only corrective plan follows — invert test_dashboard_shows_version_bar to assert the version bar is hidden (assert the widget's UNIQUE markers absent, e.g. "+ New Update" / version <select> / delete-form — not the generic "Version" substring), sweep test_pricing_versions_qa.py for siblings, then re-run full QA.
