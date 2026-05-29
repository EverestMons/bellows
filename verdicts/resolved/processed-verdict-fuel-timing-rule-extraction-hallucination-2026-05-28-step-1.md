verdict: continue
Rule 22 (b) substance — PASS. The diagnostic answers the original question and goes further than expected.

Sections A–F all hit. Filename truthfulness intact. Output Receipt complete with comprehensive Files Read list.

Substance check: the diagnostic doesn't just characterize hallucination risk in the prompt — it surfaces a more severe finding. The CSV file upload path silently strips the params section via sanitize_copilot_csv's header matching against _SECTION_HEADERS["fuel"] = {price_floor, price_ceiling, fsc_pct}. The LLM's extracted timing_rule never reaches the DB on this path. The hardcoded default 'prior_tuesday' is applied regardless of LLM output (web/contracts.py:4174 read-side fallback, but applied at write time when fuel_data["fuel"] is empty because params were stripped). Confirmed by direct Planner-side read of web/utils.py:97-178: _SECTION_HEADERS knows about a "fuel_params" section type ({field, value}) but the import-section route never invokes it for the params half of a combined CSV.

This reframes the CEO's reported symptom. The "random rule applied" is not LLM hallucination — it's the architectural strip + hardcoded default. The LLM may be hallucinating in parallel, but it's irrelevant on the CSV upload path: nothing the LLM emits for timing_rule survives to storage.

Additional confirmed findings:
- D1 route (/fuel/import-combined) is dead — handles combined format correctly but no UI/JS references it (G7)
- D2 paste tab sends section_type='fuel_combined_paste' which has no handler in the importers dict — paste path errors out (G8)
- The original fuel_combined prompt at L1443 is dead code — alias at L1865 replaces it with fuel_combined_csv (clean correction to 05-21 findings which assumed it was live)
- fuel_params and carrier_rules_tariff_fuel prompts have NO UNKNOWN escape hatch — different surface but same hallucination class
- Validator handles "prior_monday" and "UNKNOWN" via the custom else block at validator.py:2860 — silent behavioral degradation, not error

The 3-change remediation set in Section F is concrete and ordered correctly: write path fix (G6/G7/G8) is highest-leverage because it unblocks the prompt fix from mattering. Without it, prompt hardening is moot — params still get stripped.

Proceed to author the executable. Carrying these findings forward for CEO review before drafting the fix plan.
