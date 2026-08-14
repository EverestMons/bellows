# Dev Note — fold_check (gate2-348-2026-08-14)

## What landed

Two files copied from committed references in `governance/knowledge/research/`:
- `scripts/fold_check.py` — the fold post-condition tool
- `tests/test_fold_check.py` — 15 targeted tests

Both are byte-identical reference copies; no hand-authoring.

## B1/B2 — cmp closes

- B1 (`scripts/fold_check.py`): `cmp_exit=0`
- B2 (`tests/test_fold_check.py`): `cmp_exit=0`

## Task C — probe results

```
grep -oF "def fold_check" scripts/fold_check.py | wc -l        → 0  ✓
grep -oF "class ReaderCrashed" scripts/fold_check.py | wc -l   → 1  ✓
grep -oF "FOLD-CHECK DRIFT" scripts/fold_check.py | wc -l      → 1  ✓
grep -oF "FOLD-CHECK CLEAN" scripts/fold_check.py | wc -l      → 1  ✓
grep -oF "def test_" tests/test_fold_check.py | wc -l          → 15 ✓
```

## Targeted suite

```
...............                                                          [100%]
15 passed, 1 warning in 1.05s
```

## Live proof

**Plan 392** (scratch-only): baselined (`BASELINE SAVED`, readers=1 signals=14), appended fallback line `A count-only test is not sufficient.` — tool reported `FOLD-CHECK CLEAN` (exit 0). The appended text does not alter lint signals, so no drift was detected. Per plan instruction ("If the chosen plan yields no drift, say so and pick another"), moved to plan 306.

**Plan 306** (scratch-only): baselined (`BASELINE SAVED`, readers=1 signals=5), removed ledger entry `C6` line — tool reported:
```
FOLD-CHECK DRIFT — the fold changed the machine-readable state:
  VANISHED: plan_lint: (p) WARN: C6 has no backtick-quoted command or check: token

If a change is INTENDED, re-save the baseline and say so in the fold's record.
drift_exit=1
```

Exit 1 with `FOLD-CHECK DRIFT` confirmed. The tool correctly detects signal-level changes.
