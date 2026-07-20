verdict: continue

**Rule 22(b) verified directly against code. All three load-bearing items clean.**

## Verified

1. **Both moved guard objects are byte-identical to plan 240's shipped versions** (`git show e19e169:...` vs `tests/path_leak_guard.py`): regex identical, helper identical. The relocation carried nothing along.
2. **The import line is the bare form in BOTH files** (`from path_leak_guard import _PATH_LEAK_RE, _assert_no_path_leak` — `test_migrate_fuel_ceilings.py:1028`, `test_fuel_coverage_export.py:10`), so collection of the 29 migration tests survives.
3. **The fix is exactly one line**: `os.path.abspath(db_path)` → `os.path.basename(db_path)` at the single emission site. Nothing else in the exporter's diff touches behaviour.
4. **68 targeted tests pass, Planner-run** — both files, including the new guard, empty-DB, and basename assertions.

## A Planner near-miss, recorded — the third of its kind today

My first byte-identity check reported the helper as CHANGED. The defect was in my own extraction (splitting the function at an internal blank line); a proper block diff shows byte-identity. Same class as the strerror-grep miss and the truncated-head miss earlier: **the verification tool producing the finding must itself be verified before the finding is asserted.** Recording because three instances in one day is a pattern, and the pattern's countermeasure — re-verify before asserting — has now caught all three.

## Proceed to Step 2 (QA)

All rows as written. The ones carrying weight: row 3b's calibration (exact invocation, count-and-line-number-only reporting, the N/A path if the CEO has remediated); row 4's both-objects byte-identity (now Planner-pre-confirmed, but QA quotes its own run); row 1's computed baseline from the dev log's before/after collect-only records. The three standing prohibitions apply.
