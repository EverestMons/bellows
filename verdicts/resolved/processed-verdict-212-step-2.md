verdict: continue

**Final step. Option (b) is live — invoice-pulse now emits a sanitized, Claude-readable log of import-validation failures.**

## QA verified; Planner re-checked the load-bearing rows

All 11 gates PASS (Rule 20 banner byte-exact; `qa_step_detection` resolved step 2 of 2; **no Monitor denial** — the Step-1 warning was heeded, so 209's gate failure was not repeated). All **7 rows PASS**.

- **Row 1 (NO LEAK)** — QA seeded its own probe (`SCAC=XYZQ`, `price_floor=1.53`, `fsc_pct=4.0`), triggered the emit, and read the record **back from disk**: none appear; `Carrier A` does. This corroborates the Planner's independent Step-1 check with a *different* fixture — two independent leak tests, both clean.
- **Row 3 (payload preserved)** — `"fuel_brackets[30].price_ceiling is required"` survives verbatim. **Rows 1 and 3 both pass: leak-free AND actionable.** That was the bar; either alone would have been failure.
- **Row 6 (full suite)** — `2126 passed, 2 failed`. Planner-checked the arithmetic: baseline **2109 + 17 new = 2126** exactly, and the 2 survivors are the documented CLAUDE.md pair (`test_get_activity_import_page`, `test_no_tariff_rate_has_fix_url`). **Zero regressions.**
- **Row 4 (Channel B untouched)** — `git diff -- web/system.py` empty; `git diff --stat -- knowledge/data/` empty; the `data_examples` insert and `json_text[:50000]` capture intact. The CEO's history decision was respected exactly: purely additive.
- **Row 5** — `gap_dashboard.py:1879-1882` logs at `warning` with `exc_info=True`, not the bare `pass` beside it.

## Expected state, not a defect

`knowledge/telemetry/import-validation-failures.jsonl` **does not exist on disk yet** — the file is created lazily on first emit, and no real import failure has occurred on this machine (1 contract, 0 fuel brackets). It will be created, and auto-commit will sync it, at the **first real import failure on the work machine**. `git check-ignore knowledge/telemetry/` exits 1 — the path is not ignored, so the sync path is proven.

## What this closes, and what it does not

**Closes:** the CEO's stated goal — *"the whole point is to create a log that is sanitized to have claude read"* — for the import-validation failure class. A record now carries a complete diagnosis (`row_index: 30` of `row_count: 31`, `present.price_ceiling: false`, error string verbatim) while carrying nothing the company owns (`DHRN` -> `Carrier A`, `4.00` -> `"D.D"`).

**Does NOT close, and must not be mistaken as closed:**
1. **The DHRN bug itself is still live.** `web/contract_import.py:278` and `web/gap_dashboard.py:2302` both list `price_ceiling` in a required tuple, so an open-ended top bracket still cannot import. This plan built the channel that reports it, not the fix. **Separate executable — and the Planner has already read the bug from source, so that plan needs no diagnostic.**
2. **Channel B still leaks going forward** — `/system/export-forge-data` still ships `raw_paste` + real SCACs on every sync. Accepted, CEO-owned. Revisit only if the CEO chooses.
3. **Git history** — untouched by CEO decision. Private repo, one collaborator; latent risk, not disclosure.
4. **Fuel-bracket discovery / Phase B** — still blocked on running `fuel_discovery_export.py` on the work machine, where brackets actually exist.
5. **Channel A (`parse-failures.jsonl`) remains empty** and structurally cannot capture this class — that is by design, not a gap this plan should have filled.

## Known characteristic — recorded, deliberately unfixed

`char_classes` derive from the float repr, so `1.530` renders `"D.DD"` (Python drops the trailing zero before `to_char_classes` sees it). Leaks nothing; irrelevant to this failure class (the exact signal is `present.price_ceiling: false`). But a future precision-related failure would be mis-described by that field — recorded so it is found as a known quirk rather than discovered as a lie.

Move the plan to `Done/`.
