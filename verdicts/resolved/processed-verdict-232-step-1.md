verdict: continue

**Rule 22(b) verified — both load-bearing claims reproduced independently by the Planner rather than read from the dev log.**

## The leak boundary holds — Planner-run seeded proof

Seeded a scratch DB with unmistakable values in every forbidden field, ran `run_export`, and grepped the serialized report:

```
Seeded: fsc_pct=77.777  continuation_surcharge_steps="88.888"  continuation_start_fsc=66.666
        carrier_name="Leak Carrier"  SCAC="LEAKC"

  fsc_pct value      present in output: False
  surcharge_steps    present in output: False
  start_fsc          present in output: False
  carrier name       present in output: False
  SCAC               present in output: False

  price_floor 1.5              present: True
  continuation_increment 0.05  present: True
```

**NO LEAK, and the structure B2 needs IS present.** Both halves matter — an export that leaked nothing by emitting nothing would be useless.

**Stronger than the plan required:** `grep -n "fsc_pct" fuel_discovery_export.py` returns **nothing**. The rate column is not filtered out of the output, it is never read. That is a structural guarantee rather than a behavioural one — the module cannot leak `fsc_pct` because it never touches it. `SELECT *` appears nowhere; every query names its columns, so plan 211's leak cannot re-enter here.

## The conflation is fixed, and I reproduced the exact defect

```
contract_id=5      -> Contract 1
contract_fuel_id=5 -> Config 1
Distinct: True        (stable on repeat: True)
```

Before this change both rendered as the same `Contract N` string. `_ENTITY_LABEL_CONFIG` gained `"fuel_config": ("Config", False)` (`web/reporting.py:86`), and every fuel-config FK in the four sanitizers now labels under `"fuel_config"` while `contract_id` stays on `"contract"` (`_sanitize_q5_rows:213-215` keeps them correctly split). A config now carries one label everywhere it appears.

**This is what unblocks B2's verification steps** — they can finally key on a config identity that means the same thing in every section.

## Also verified

- Read-only preserved; the export writes nothing.
- Five files, all in scope; the plan-178 `_anonymize_section` choke point intact, with no second labeling path introduced.
- `_ENTITY_LABEL_CONFIG` still has exactly one consumer (the keyed lookup at `:105`), so the addition could not regress the safe-export path — the Step-1 instruction was to confirm this rather than re-derive it, and it holds.

## Proceed to Step 2 (QA)

All 9 rows. The ones that carry the weight:

- **Row 2 (the seeded leak proof)** is the row that must not be waved through. I have now run it independently and it passes — but QA runs it on its own seeds and deposits raw output. **A grep proving absence of a value that was never present proves nothing; the seed is what makes the row real.** Show the seed values alongside the zero-hit greps.
- **Row 4/5 (label regression + consistency)** — quote the tests by id.
- **Row 8 (assertion reconciliation)** — every existing assertion changed in Step 1 must appear in the dev log with its classification. `tests/test_fuel_discovery_export.py` was touched, so there IS a reconciliation to account for here, unlike plan 230 where the answer was legitimately zero.

Baseline: **2291 passed / 2 known** as of plan 231, not the 2264 in the plan text — plans 230/231 landed in between. **Report ACTUAL and reconcile; do not force either number.**

The three standing prohibitions have held for six consecutive plans. Keep the streak.
