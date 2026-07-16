verdict: continue

**Rule 22(b) verified independently — the Planner extracted the LIVE patched query from `engines/validator.py` by regex and re-ran the bug against it, rather than reading the agent's tests.**

## The bug is dead, and all three properties hold

**1. Deterministic and correct** — the same Contract-1 shape that failed this morning:
```
EIA 6.175 | sentinel inserted first: 16.5%  | sentinel inserted second: 16.5%
```
Was `15.0` vs `16.5` depending on row order. Now both orders return **16.5** — the most specific bracket. **A live FSC mis-charge is closed.**

**2. The unbounded semantic is preserved** — the regression that would have mattered most. A legitimately-last sentinel still matches:
```
EIA 9.50 -> 15.0%   EIA 6.20 -> 15.0%   EIA 1.16 -> 1.1%
```
The "and above" bracket still swallows high diesel prices. The fix did NOT trade one bug for a worse one.

**3. The no-op claim is TRUE, not asserted** — on a well-formed contiguous table, ordered and unordered queries return identical results at four prices including a bracket boundary (`1.199`). **The change has effect only where the result was previously undefined.** That is the property that makes this shippable on core validation logic.

## The diff is exactly right

Four added lines, **zero removed**, both sites:
```
+        # ORDER BY: sentinel ceilings (99.999) overlap real brackets; highest floor = most specific match
+            ORDER BY price_floor DESC
```
`grep -c "ORDER BY price_floor DESC"` = **2** — contract AND carrier. A one-sided fix would have left the carrier path exposed; it didn't. The predicate, the `if not fsc_pct:` continuation fallback, and the function signature are all untouched.

**The comment is the right kind:** it states the constraint the code cannot show (sentinels overlap; most-specific wins) rather than narrating what `ORDER BY` does. Without it a future reader deletes the line as noise — which is exactly how this bug would come back.

## Proceed to Step 2 (QA)

Row 2 is the one that matters: **write your own reproduction, do not re-run the DEV's test.** This bug is non-determinism — a test that passes for the wrong reason is the specific failure mode here. Extract the live query from the source rather than transcribing it, or you are testing a copy.

Row 7's baseline is **`2126 passed, 2 failed`** (plan 212); the 2 knowns are `test_get_activity_import_page` and `test_no_tariff_rate_has_fix_url` (CLAUDE.md). Verify and report ACTUAL counts — do not force them. **This is core validation logic touching real money: any fuel or gate-8 regression is a HALT, not a note.**
