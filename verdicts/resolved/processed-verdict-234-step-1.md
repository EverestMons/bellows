verdict: continue

**Rule 22(b) verified. Both fixes landed, and Fix 1 took the preferred form rather than the fallback.**

## Fix 1 — done properly, using the engine as ground truth

The threshold duplication is gone entirely: `grep -nE "next_floor - 0\.001|delta_mills|> 10|<= 10|PRECISION_THRESHOLD"` returns **nothing**. Not the fallback (importing the constant) — the preferred diff approach:

```python
# A genuine gap is an interior row the engine chose not to correct.
if orig_ceiling == scratch_ceiling:
    bracket_gap = float(orig_rows[i + 1]["price_floor"]) - orig_ceiling
    if abs(bracket_gap - 0.001) > 1e-9:
        entry["genuine_gap_rows"].append(...)
```

**This is the right shape.** Condition one is the engine's own verdict — the row survived the recompute unchanged — so the classification is not re-derived anywhere, it is *observed*. Condition two then separates "conventional contiguity" from "something else," and the something-else was already established as a preserved gap by condition one. The `0.001` is a convention comparison, not a threshold; there is no second copy of the load-bearing `<= 10` anywhere in the script.

It iterates `range(len(orig_rows) - 1)`, so only interior rows are considered — matching the interior condition. G5's emitted output shape is unchanged: the same gap rows, named the same way.

## Fix 2 — done

`grep -n "Wait, no"` returns nothing. The self-contradicting block is replaced.

## Also verified

- The engine is still called (8 sites); the migration decision remains entirely its own.
- **11/11 tests pass, Planner-run** — and none were modified, which is what the plan required. These were refactors; a test needing a change would have meant the fix went too far.

## Proceed to Step 2 (QA)

All 15 rows. **Row 2 is the one that matters** — it greps for exactly the pattern Fix 1 removed, and it is the check that would have caught this defect even had I never noticed it. It should now pass cleanly. **Do not weaken it.**

Baseline expectation **2315** (2304 as of plan 232, plus plan 233's 11 migration tests). **Report ACTUAL and reconcile** — the baseline has moved four times in this arc and the plan text has carried a stale figure every time; the report-actual clause has caught it every time.

Row 15 (runbook matches the script's flags) is worth care: plan 233's runbook was written against the pre-fix script, and although these fixes touched neither `argparse` nor the command surface, that is exactly the kind of assumption worth confirming rather than assuming.

Note for the QA report: state the deliberate boundary — QA does not verify against the canonical production DB, and that is correct. Canonical verification happens at the dry-run paste-back gate, by the Planner, before GO.
