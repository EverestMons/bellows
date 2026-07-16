verdict: continue

**CONTINUE-OVER-FAILURE — CEO-authorized 2026-07-16.** Rule 49 reserves continue-over-failure on a `gate_failure` to the CEO; this verdict carries that authorization and the false-positive justification below.

## The gate failure is a known-benign false positive

`permission_denials` FAIL — one denial: the QA agent invoked **Monitor** to await the long-running full suite, and it was denied.

**Justification (why this is a false positive, not a defect):**
- The denial **blocked no work**. The agent fell back and completed the suite: **2107 passed in 796.38s**.
- It touched **no deliverable**. The denied call was a wait-loop on a temp output file, not a read or write of any scoped artifact.
- `file_change_audit` confirms exactly **1 file** modified (the QA deposit), and `scope_check` PASSED.
- This is a catalogued benign class (alongside `rule_22c` parser truncation and `scope_check` on unnamed tests) — the Monitor denial is an environment/permission artifact, not a signal about the work.
- Every substantive gate PASSED: `receipt_status`, `rule_20_self_check` (banner byte-exact), `rule_22_verification`, `scope_check`, `deposit_exists`, `qa_step_detection` (step 2 of 2).

## All 8 QA rows PASS — and the two that license production use were proven, not asserted

- **Row 1 (read-only):** `TestReadOnly::test_db_opened_read_only` PASSED — a write attempt raises `sqlite3.OperationalError: readonly`. That is a *proof*, not a grep for absent verbs. `test_no_row_count_change` PASSED. This is what licenses running the module against the CEO's production DB.
- **Row 2 (no leak):** `_anonymize_section` + `_LabelAllocator` imported from `web.reporting`; **no `def _anonymize` in the exporter** — the plan-178 single choke point is reused, not reimplemented. Seeded `contract_id=100` is absent from output; it renders as the ordinal `"Contract 1"`.
- **Row 3 (not over-redacted):** `q4_raw` is assigned to the report **without** passing through sanitization — deliberately. The `delta_mills` aggregates survive intact. Rows 2 and 3 both passing IS the bar; either alone is trivially gameable.
- **Row 6 (threshold arithmetic):** the seeded 5-mill gap classifies `precision_gap`, the 50-mill gap `genuine_gap` — the exact 10-mill boundary the CEO's Phase B ruling turns on.
- **Row 8 (transport):** `git check-ignore knowledge/telemetry/` → exit 1 (not ignored). A report written on the work machine reaches GitHub.

## ⭐ This run discovered the v17 QA finding owed since 2026-07-15

Full suite: **2107 passed, 4 failed**. Two are the known pre-existing failures named in CLAUDE.md. **The other two are not from this plan:**

- `test_parse_track_schema.py::TestFreshDB::test_schema_version_is_16`
- `test_provenance_columns.py::TestProvenanceSchema::test_schema_version_is_16`

Planner-verified: both hardcode **16** in name and body; `database.py:24` is now `CURRENT_SCHEMA_VERSION = 17`, last touched by **`f856b9c` (exec-201's bump)**. Plan 209 never touched schema — its commits are the exporter, its QA, and docs. **These have been red since 2026-07-15 and undetected**, because exec-201's Step-2 QA was killed by a daemon restart and exec-202 died on the 5-hour cap.

**The baton's "full-suite QA still OWED" item is now effectively answered, and these two stale assertions are its finding.** CEO decision 2026-07-16: a fix plan follows (update both to 17, re-run to a clean baseline). Correctly NOT smuggled into this plan — 209's scope is the exporter.

## What this unblocks

`fuel_discovery_export.py` is ready to run **on the work machine** (`python3 fuel_discovery_export.py`). It emits a sanitized report to git-tracked `knowledge/telemetry/`, auto-commit syncs it, and the Query #4 `delta_mills` distribution gives the CEO the evidence to rule on the 10-mill threshold — opening the Phase B gate that has been un-satisfiable since 2026-05-22 and is why the DHRN open-ended top bracket cannot import.

**Still separately outstanding:** the Flask server restart to migrate `data/invoices.db` from v16 → v17 (`contract_documents` does not yet exist locally).

Move the plan to `Done/`.
