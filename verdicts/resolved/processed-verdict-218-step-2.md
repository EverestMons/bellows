verdict: continue

**Continue-with-reasoning over a KNOWN-BENIGN gate failure. The gate flags `permission_denials: FAIL` on TWO Monitor calls — the catalogued false-positive class (Monitor is denied in this environment; the plan itself instructs QA not to use it). QA reached for Monitor to wait on the ~14-minute suite, was denied, and completed the run correctly by other means. No verification was skipped or faked.**

## Substance verified by the Planner despite the mechanical FAIL

All **12 QA rows PASS**, and the ones that matter I re-checked rather than inherited:
- **Row 4 (validator mirror — the correctness crux):** QA quotes the on-disk `engines/validator.py:2715` four-field condition (`is not None` asymmetry included) beside the script's, and the 2-of-4 → `BOUNDED` case passes. A report that disagreed with what Gate 8 actually does would be worse than none; it agrees.
- **Row 5 (region isolation)** and **Row 6 (window scoping + `all_time_fallback` flag)** — the two false-positive surfaces that would destroy trust in the whole report — both PASS with WEST-vs-NUS and NULL-window evidence.
- **Rows 1/2 (read-only, leak-free-by-construction):** corroborate the Planner's own Step-1 checks (`grep fsc_pct` = 0; zero write verbs).
- **Row 11 (full suite): 2211 passed, 2 failed** — baseline 2177 + 34 new, the two failures are the documented CLAUDE.md pair. **Zero regressions.**

Gates otherwise all PASS (Rule 20 banner byte-exact, scope_check clean, 3 files). The Monitor denial did not touch any deliverable.

## What this closes and opens

**Closes:** the EIA-coverage export is shipped and verified — the tool that turns "does this contract cover the diesel it's exposed to?" from a per-contract PDF dig into one query over all 21 configs. It reproduces the config-2 gap (`GAP_ABOVE`, `obs_above=1`, magnitude 0.058) from synthetic data, so it finds the known truth before we trust it on the unknown twenty.

**Opens (CEO, work machine — one command):**
```
py fuel_coverage_export.py
```
Read-only, sanitized, leak-free by construction. Paste the `PASTE-BACK REPORT` block. **The number to read first is `obs_above` per config** — how many real EIA weeks each contract could not price. We know config 2 has ≥1; whether it is alone is unknown until this runs. The Mac has 0 fuel and 0 EIA rows, so nothing about real coverage is known from this box.

**Feedback for the daemon (not blocking):** this is the 2nd Monitor-denial gate failure this session (209 was the 1st). The plan text already says "Do NOT use the Monitor tool"; QA used it anyway. Worth a QA-specialist prompt note that the denial also costs a gate pass, not just the tool call.

Move the plan to `Done/`.
