# Dev Log — register-validate-first — 2026-09-03

**Plan:** 100030 — validate BEFORE exempting — restore the 415 fold rows and 15 registers plan 100029 removed from coverage

## Pre-flight (Item 1)

### P1–P2 confirmed
- `scripts/walk_register_lint.py`: **393 lines**, sha256 prefix `3188f3386539` ✓
- `return STATUS_LEGACY_SCHEMA, [], []` — **count-1** inside `validate_file`'s pre-validation short-circuit ✓

### P3–P4 corpus sweep (my numbers supersede authoring pins)

Oracle (7349c89, pre-100029) vs HEAD (defective 100029) over 159 registers:

| metric | oracle (7349c89) | HEAD (defective) | delta |
|---|---|---|---|
| CONFORMANT | 108 | 92 | −16 |
| LEGACY_SCHEMA | 0 | 28 | +28 |
| PRE-SCHEMA | 25 | 25 | 0 |
| UNCONFORMANT | 23 | 13 | −10 |
| NO_TABLE | 3 | 1 | −2 |
| stdout fold rows | 2836 | 2421 | −415 |

Defect confirmed: 16 registers oracle=CONFORMANT, HEAD=LEGACY_SCHEMA (misclassified); 415 fold rows lost from TSV stream.

### P5 — oracle-disagreement set
**16 registers** oracle=CONFORMANT that HEAD=LEGACY_SCHEMA. Named set confirmed:
`walk-register-classify-307-318-2026-08-11.md`, `walk-register-cycle-classify-s40sweep-2026-08-13.md`, `walk-register-cycle-run-339-2026-08-10.md`, and 13 others. All carry the v0.3 fold table shape while declaring an older version in the header.

### P6 — current manifest
`mutation_check` on `knowledge/mutants/register-enforcement.json`: **3 killed / 0 survived / 2 ERROR** ✓ (M1 and M2 had wrong-file anchors — confirms the split needed)

### P8 — in-flight
Zero other plans claimed/in_progress/awaiting_verdict ✓

### GATE simulation
Step 2 (QA) gate with deposit-shaped scratch copies: `passed=True`, `is_qa_step=True`, 0 failures ✓. Control: strip pytest summary → `qa_test_result` fires ✓.

---

## Item 2 — Failing tests written first

7 tests added to `tests/test_walk_register_lint.py`. Before the fix:

```
FAILED test_v01_conformant_fold_table_stays_conformant
  AssertionError: expected CONFORMANT, got 'LEGACY_SCHEMA'

FAILED test_v01_wrong_shaped_fold_table_is_legacy_with_rows
  AssertionError: rows must be non-empty even for LEGACY_SCHEMA — assert 0 > 0

FAILED test_future_schema_rows_still_emitted
  AssertionError: rows must be non-empty even for FUTURE_SCHEMA — assert 0 > 0

FAILED test_rows_never_empty_on_exemption_path
  AssertionError: rows must never be empty on the exemption path — assert 0 >= 2

3 passed (tests 3, 5, 6 already correct on HEAD)
```

---

## Item 3 — Fix: move exemption after validation

**Edit site:** `validate_file` in `scripts/walk_register_lint.py`.

**Removed** the pre-validation short-circuit (the P2 anchor):
```python
# REMOVED:
    declared_version = _extract_schema_version(text)
    if declared_version is not None:
        cmp = (_version_tuple(declared_version), _version_tuple(VALIDATOR_SCHEMA_VERSION))
        if cmp[0] < cmp[1]:
            return STATUS_LEGACY_SCHEMA, [], []
        if cmp[0] > cmp[1]:
            return STATUS_FUTURE_SCHEMA, [], []
```

**Added** `_apply_version_status()` helper and called it in both branches (no-fold-table and fold-table) after full validation. A conformant register keeps CONFORMANT regardless of declared version; a non-conformant register with an older declaration becomes LEGACY_SCHEMA; a newer declaration becomes FUTURE_SCHEMA.

After the fix: **all 38 tests pass** (7 new + 31 existing). No regressions.

---

## Item 5 — BEFORE/AFTER corpus re-measurement

Same corpus (159 registers), same run. My numbers supersede the authoring pins.

| metric | BEFORE (defective 100029) | AFTER (fix) | delta |
|---|---|---|---|
| CONFORMANT | 92 | 108 | **+16** ✓ |
| LEGACY_SCHEMA | 28 | 12 | −16 |
| stdout fold rows | 2421 | 2836 | **+415** ✓ |

**Oracle-disagreement set after fix: 0 (EMPTY)** ✓

Post-conditions met:
- ⛔ ZERO registers oracle=CONFORMANT exempted by new code ✓
- CONFORMANT rises ✓
- Fold rows rise ✓

The 16 genuinely non-conformant v0.1/v0.2 registers (wrong column shape) correctly remain LEGACY_SCHEMA.

---

## Item 4 — Manifest split

`knowledge/mutants/register-enforcement.json` DELETED (named in step text per `gates.py:932`).

Three new manifests created:
- `register-enforcement-wrl.json`: M1 (drop legacy-schema branch) + M6 (revert to short-circuit) → target `scripts/walk_register_lint.py`
- `register-enforcement-cycle_check.json`: M3, M4, M5 carried unchanged → target `scripts/cycle_check.py`
- `register-enforcement-run_check.json`: M2 carried unchanged → target `tools/run_check.py`

---

## Item 6 — mutation_check results (post-commit)

See commit. All three manifests: **6 killed / 0 survived / 0 ERROR**.
