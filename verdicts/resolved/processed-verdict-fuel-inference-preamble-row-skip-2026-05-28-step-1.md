verdict: continue
Rule 22 (b) substance — PASS. Diagnostic answers all 7 areas (call sites, input contract, start_price/start_fsc consumers, materialization data flow, test surface, existing preamble handling, blockers) with file:line citations and per-consumer shift-safety analysis. No paraphrasing, no hedging.

Key findings affirmed:
- Brackets are SQL-sorted ascending and unfiltered at both `/fuel/infer` (contract_fuel_infer at web/contracts.py:5749) and `/fuel/infer/apply` (contract_fuel_infer_apply at web/contracts.py:5863). Skip logic belongs in the engine, not at call sites.
- All 11 consumers of start_price/start_fsc handle the shift to the first post-preamble row correctly (template labels, Gate 8 _compute_continuation_fsc, TOCTOU stale check, DB writes, EIA lookup JS). No silent breakage.
- Recommendation (ii) for materialization adopted: embed `preamble_rows: List[dict]` and `preamble_rows_skipped: int` in InferenceResult. compute_materialization_rows requires zero changes — preamble rows already survive at the apply endpoint because the DELETE/INSERT cycle only touches `source='inferred'` rows.
- No existing prior art for zero-floor/zero-FSC handling anywhere in engines/web/ingestion. Net-new logic.
- Test surface: 11 unit tests + 16 integration tests, none use price_floor==0.000 fixtures. New tests required.

Open questions resolved with CEO:
- Q1 (endpoint <6 gate): option (a) — move the gate to check post-skip count (analysis_count = len(brackets) - preamble_count). Preserves UX intent under new logic.
- Q2 (multi-row preamble): coded defensively for N rows even though production data is not expected to contain multiple zero-FSC rows. Strip contiguous leading rows where both price_floor==0.000 AND fsc_pct==0.00 hold; stop at first row where either condition fails.
- Q3 (_corroborate_inference start_price mismatch): pre-existing semantic difference between Copilot-extracted "last bracket ceiling" and inference "first bracket floor". Not affected by skip. No action.

Executable scope is engine-only + endpoint gate adjustment + tests. No UI/template changes required.
