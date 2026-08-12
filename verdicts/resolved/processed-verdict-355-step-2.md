continue

Step 2 (QA) — clean gate, Rule 22(b) verified against RAW evidence (not the agent summary).

Full suite (raw full-suite.txt): `2 failed, 2518 passed, 1 warning in 840.76s`.
The 2 failures are EXACTLY the two CLAUDE.md-known pre-existing failures and
nothing else:
  - tests/test_activity_import.py::TestFlaskRoute::test_get_activity_import_page
  - tests/test_fix_links.py::TestGate7LinehaulFixLink::test_no_tariff_rate_has_fix_url
No regression.

New tests (raw enrich.txt): `5 passed` — all five landed and pass
(enrich_then_validate, no_file_still_validates, updated_xml_replaces_charges,
parse_fail_preserves, zero_charges_preserves).

Mechanical gates all PASS incl. rule_20_self_check (banner byte-exact, PASSED
line present) and rule_22 (deposits present, no hedging). The 1 intermediate
decision is benign (agent matching the QA report format).

Rule 22(b): the change fixes the original defect — the invoice-detail "Run
Validation" button now re-parses {id}.xml before validating, so gates 6–9 get
charge data instead of "No charge lines found in invoice XML", with the
data-safety guards (0-charge and parse-fail rollback) proven by passing tests.

Continue — plan complete (step 2 of 2).
