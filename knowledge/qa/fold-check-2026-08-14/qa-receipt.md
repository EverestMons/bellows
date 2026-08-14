# QA Receipt — gate2-348-2026-08-14 (fold_check tool)

**Plan:** 418
**Step:** 2 (QA)
**CAPTURE_COMMIT:** `47133e9`
**Date:** 2026-08-14
**Slug:** `gate2-348-2026-08-14`

## Precondition — Step 1 independence

```
$ git log --oneline -1 -- scripts/fold_check.py
47133e9 [418] fold-check(gate2-348-2026-08-14): the fold post-condition tool — diff the machine-readable state against a pre-fold baseline
```

Step 1 commit `47133e9` was made by a prior dispatch context, not this one.

## Deliverable Verification

| Item | Check | Result |
|------|-------|--------|
| 1 | Task C probe battery (committed content): `def fold_check`=0, `class ReaderCrashed`=1, `FOLD-CHECK DRIFT`=1, `FOLD-CHECK CLEAN`=1, `def test_`=15 | ✅ |
| 2 | C1 byte-identity: both `diff` exits 0; references committed at `f9ac2c1`, porcelain clean | ✅ |
| 3 | C4 CAPTURE_COMMIT: numstat shows 3 paths, 1 parent (non-amend), subject matches Task D form | ✅ |
| 4 | C5 gate-wiring: `fold_check` count 0 in `gates.py` and `bellows.py`; positive controls >0 (8, 478) | ✅ |
| 5 | Full suite: 1040 passed / 0 failed in 25.78s (baseline 1025 + 15 new) | ✅ |
| 6 | Live proof (executable-302.md, scratch-only): BASELINE SAVED then exit 1 with FOLD-CHECK DRIFT | ✅ |
| 7 | Raw output: all commands foreground, raw in `probes-raw.txt` | ✅ |

#### Forward Register

The routed text names "probe battery" as a reader class. Probes are prose instructions with no machine-readable declaration, so `fold_check` cannot execute them deterministically today. The `readers_for` function is the extensibility point; wiring probes in is future work — owed, not dropped.

## Evidence

- `probes-raw.txt` — all raw command output for Items 1-7

```
============================================================
Rule 20 — QA Self-Check Results
============================================================
PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.
Evidence folder: knowledge/qa/fold-check-2026-08-14/
Files verified: 2
```
