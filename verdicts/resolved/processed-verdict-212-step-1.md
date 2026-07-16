verdict: continue

**Rule 22(b) verified independently — the Planner composed a real DHRN record and inspected the actual bytes, rather than reading the agent's tests.**

## The record is leak-free AND actionable — both, which is the whole bar

Fed the real shape (31 brackets, open-ended top `{price_floor: 1.530, price_ceiling: None, fsc_pct: 4.00}`, carrier `DHRN`) through `compose_import_failure_record`. The emitted record:

```json
{"error_messages": ["fuel_brackets[30].price_ceiling is required"],
 "carrier_label": "Carrier A", "failure_category": "missing_required",
 "missing_fields": ["price_ceiling"],
 "field_shape": [{"row_index": 30,
                  "present": {"price_floor": true, "price_ceiling": false, "fsc_pct": true},
                  "char_classes": {"price_floor": "D.DD", "fsc_pct": "D.D"}}],
 "row_count": 31}
```

**Leak check on the serialized output — all five probes negative:** raw SCAC `DHRN` absent (-> `"Carrier A"`), `fsc_pct` value `4.00` absent (-> char-class `"D.D"`), `price_floor` value `1.530` absent, paste content (`EIA_DOE`) absent, raw JSON keys absent. `json_text` is consumed as INPUT to compute shapes and never reaches the output.

**Payload preserved:** the error string survives verbatim. **This record alone is a complete diagnosis** — row 30 of 31 (i.e. the LAST bracket) has a floor and a pct but no ceiling => open-ended top bracket => the validator requires ceiling => bug. That is exactly the goal: everything Eluvian needs, nothing the company owns.

## Contract terms verified

- **Channel B untouched** (CEO history decision): `web/system.py` unmodified (0 commits); the `data_examples` insert (`:1857`) and `json_text[:50000]` capture both intact. Purely additive.
- **The `except` divergence landed:** `:1879-1880` is `except Exception: logger.warning(...)` — NOT the bare `pass` it sits beside. A broken emit will now leave a trace instead of impersonating "no failures."
- **Single choke point:** `grep -c "def _anonymize"` on the new file = **0**; it imports `_anonymize_section`/`_LabelAllocator` from `web.reporting`.
- **Targeted tests: 17 passed.**

## One observation for the dev-log — NOT blocking, do not fix here

`char_classes` are computed from the float's repr, so `1.530` renders `"D.DD"` (4 chars) rather than `"D.DDD"` (5) — Python drops the trailing zero before `to_char_classes` sees it. **Irrelevant to this bug** (the open-ended-bracket signal is `present.price_ceiling: false`, which is exact), and it leaks nothing. But a future failure class about trailing-zero precision would be mis-described by that field. Worth a line in the QA report as a known characteristic so nobody later reads `"D.DD"` as ground truth about source formatting. **Do not change the encoder in this plan.**

## Proceed to Step 2 (QA)

Rows 1 and 3 must **both** pass — leak-free AND actionable. Either alone is a failure. Row 1 is the halt-if-fail row: seed a known SCAC and known values, trigger the emit, read the JSONL **back from disk** (not from a return value), and show the raw record. Row 6's baseline is **`2109 passed, 2 failed`** (plan 210) — verify and report ACTUAL counts, do not force them; any third failure is a regression, name it. **Do NOT use the Monitor tool** — it is denied here and gate-failed plan 209; run the suite directly and read the tail.
