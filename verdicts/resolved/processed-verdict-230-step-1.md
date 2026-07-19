verdict: continue

**Rule 22(b) verified independently by the Planner — engine read line by line, tests Planner-run (19/19 pass, 2.19s), and every load-bearing constraint checked against the code rather than the receipt.**

## The five things that could have destroyed this plan, each verified

1. **The `<=` survived.** `PRECISION_THRESHOLD_MILLS = 10` (`:19`) with `if delta_mills <= PRECISION_THRESHOLD_MILLS` (`:188`). Not tidied to `<`. The boundary tests are two INDEPENDENT classes — `TestBoundaryDeltaMills10` (stored 1.989 vs derived 1.999 = exactly 10 → rewrites) and `TestBoundaryDeltaMills11` (stored 1.988 = exactly 11 → preserves, `preserved_genuine_gaps == 1`) — each asserting both the summary dict AND the on-disk value. Constructed from exact mill arithmetic as specified, not near-boundary approximations.
2. **Gate 0 works and is ordered correctly.** Gate 0b (duplicate floors) runs first with its own specific reason, then Gate 0 delegates to `detect_bracket_structural_issues`. The config-2 shape test seeds `(6.15, 99.999)` under `(6.17, ...)` and asserts refusal with **zero UPDATEs** — the malformation cannot be laundered into a "genuine gap" and preserved. This was the defect the drafting cycle existed to catch.
3. **Case 3 is present and tested.** Last bracket with neither sentinel nor continuation falls to `last_bracket_rule: "preserved"` with no UPDATE. The truncated configs cannot be given a synthetic top.
4. **The `1.38` sentinel is safe.** Case 1 precedes case 2, so a legitimate open-ended top wins over a continuation increment even where both exist — the conservative branch, and correct given sentinel and continuation are mutually exclusive by design.
5. **`fsc_pct` is never read or written.** The engine SELECTs only `id, price_floor, price_ceiling`, and passes a literal `0.0` as the pct slot into the structural checker (which ignores it). Every UPDATE is `SET price_ceiling`. The money column is untouchable by construction, not merely by intent.

## Also verified

- **Exactly ONE implementation** — `grep -rn "def recompute_fuel_ceilings"` returns a single hit. Table-agnostic via `_PARENT_TABLE` (`:14`), not duplicated per table.
- **The engine fetches its own continuation increment** (`:166`) from the correct parent, and `contract_fuel` / `carrier_fuel` both have `id INTEGER PRIMARY KEY` — the `WHERE id = ?` join is right.
- **Idempotent by integer mills, not float equality.** `if delta_mills != 0` guards every UPDATE, so a second call reports `rows_changed: 0`. No float `==` anywhere in the change detection.
- **No overlap false-positive on clean data.** With `ceiling_i = floor_next - 0.001`, the checker's `ceiling_i >= floor_next - 1e-9` is false; and a 10-mill precision gap sits further below still. Gate 0 will not refuse the very configs that need recomputation.
- Gates all PASS; exactly the 2 scoped files; no database written.

## One finding to FOLD INTO STEP 2 — not a blocker

**The sentinel threshold `99.0` now appears TWICE in production code:** at `fuel_conflict_detection.py:78` inside the shared discriminator, and again inline at `:199` in the engine's case-1 check. The engine is correct today, and Gate 0 guarantees no non-last sentinel reaches that line, so there is no live bug. But this is precisely the divergence the plan warned about — change the threshold in one place and the two silently disagree.

This is defensible as written: `detect_bracket_structural_issues` detects *malformed* sentinels and has no "is this a legitimate sentinel" accessor, so case 1 could not simply call it. The fix is not to restructure that function.

**In Step 2, extract a module-level `SENTINEL_CEILING_MIN = 99.0` and use it at BOTH sites.** One constant, two references, no behavior change. Add it to the Step-2 dev log. Do not change the value, and do not attempt to route case 1 through the structural checker.

(The redundant `floor == max_floor` at `:199` — the last row is always max_floor once Gate 0b has excluded duplicates — is harmless defensive coding. Leave it.)

## Proceed to Step 2

The wire-in and the existing-test reconciliation. Three things carry the most risk:

- **Site 1 goes in the CALLER'S loop, not in `insert_bracket_or_record_conflict`.** Recomputing per row is O(n²) and wrong on partial sets.
- **Site 5 (fuel-infer) is the trap.** Recompute AFTER the re-INSERT. If the engine and the materialization logic disagree on a ceiling, leave site 5 UNWIRED and report it — do not let recompute silently win.
- **Enumerate every changed existing assertion in the dev log with its classification.** ~25 assertions across 11 files by the plan's estimate; re-derive by grep rather than trusting that number. This is in DEV precisely because plan 219's QA repaired assertions and self-verified.
