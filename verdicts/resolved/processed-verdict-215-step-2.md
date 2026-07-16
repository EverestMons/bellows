verdict: continue

**Final step. The Gate 8 fuel bracket lookup is deterministic — a live FSC mis-charge is closed.**

## QA verified; Planner re-checked the arithmetic and the survivors

All 11 gates PASS (Rule 20 banner byte-exact; `qa_step_detection` resolved step 2 of 2; no Monitor denial — the plan's warning was heeded). All **7 rows PASS**.

**QA wrote its OWN reproductions rather than re-running the DEV's tests** (rows 2, 4, 5), exactly as instructed. That mattered here: this is a non-determinism bug, and a test passing for the wrong reason is the specific failure mode. Two independent reproductions plus the Planner's own — three parties, same answer.

**Row 7 — full suite `2141 passed, 2 failed`.** Planner checked the arithmetic rather than accepting it: the new test file collects exactly **15** tests, `2126 + 15 = 2141`, and the 2 survivors are the documented CLAUDE.md pair (`test_get_activity_import_page`, `test_no_tariff_rate_has_fix_url`). **Zero regressions in core validation logic.**

**Row 6 — the diff is +4 lines, nothing removed:** 2 `ORDER BY price_floor DESC` clauses + 2 comments, at both `:2695` (carrier) and `:2705` (contract). Predicate, `if not fsc_pct:` fallback, and signature untouched.

**Row 3 — the no-op claim is proven, not asserted:** `test_well_formed_single_row_match` asserts `row_count == 1` on well-formed data, which is the real proof (only one row satisfies the predicate, so ordering cannot matter). A test that merely checked "returns something" would not have established it. Planner independently confirmed ordered == unordered at four prices including a bracket boundary.

**Row 5 — the continuation fallback still fires:** 21 tests green, and QA's own probe at EIA `5.00` correctly produced "outside fuel bracket range".

## What is now closed, and what is not

**Closed:** the Gate 8 ambiguity. Where a `99.999` sentinel overlaps real brackets, the most specific bracket now wins deterministically. Verified three times over: `EIA 6.175 -> 16.5%` regardless of physical row order (was `15.0` vs `16.5`). **The unbounded semantic is preserved** where a sentinel is legitimately last (`EIA 9.50 -> 15.0%`) — the fix did not trade one bug for a worse one.

**NOT closed — do not let this verdict imply otherwise:**
1. **The sentinel census (diag-214 Q2)** — still unknown how many `99.999` rows exist and how many are legitimately last. The SQL is written and waiting for the work machine. **This still gates Phase B's sentinel handling.**
2. **Contract 1's data question** — this fix makes the lookup correct *either way*, but does not adjudicate whether that mid-table sentinel is an error. The census answers that.
3. **Phase B itself** — the threshold ruling is recorded (`retain 10 mills`); `_recompute_fuel_ceilings()` still does not exist. Note the fix removes the accidental-repair coupling: Phase B's rewrite of Contract 1 is now a pure data decision, not a silent correctness fix.
4. **DHRN** — unrelated, and per the 2026-07-16 exchange-history finding it was a truncated copilot extraction the CEO already worked around. **Do NOT make `price_ceiling` optional.**

Move the plan to `Done/`.
