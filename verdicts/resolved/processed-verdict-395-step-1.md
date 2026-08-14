verdict: continue
Clean gate — plan 395 Step 1 (DEV, test-only corrective) auto-continued under delegated verdict authority.

Grounds:
- Mechanical gate (Bellows-produced): Gate Result Passed=True, failures=[]; scope_check / deposit_exists / rule_22 / file_change_audit (2 files) / errors all PASS. TEST-ONLY: files_changed = dev log + tests/test_pricing_versions_qa.py; NO web/ or route change (as required).
- Planner-confirmed via git: commit 0392aea [395] merged to main; the stale test test_dashboard_shows_version_bar was renamed test_dashboard_hides_legacy_version_bar and its assertions inverted to assert the widget UNIQUE markers are absent (b"+ New Update" not in, b"Delete Version" not in) — not the brittle generic b"Version" substring, per the plan fold. (Minor: one duplicated "Delete Version" assertion line — harmless.)
- Tests (from the step-transcript raw pytest summary): the targeted tests/test_pricing_versions_qa.py run is green — 46 passed, 0 failed; the previously-failing test now passes.
- (b): implements Step 1 as specified — stale UI test inverted with unique-marker assertions; /versions/new route + its tests untouched (F3).

Proceeding to Step 2 (full-suite QA + Rule 20; terminal step) — expect only the 2 CLAUDE.md-known pre-existing failures.
