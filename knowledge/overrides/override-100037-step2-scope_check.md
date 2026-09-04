# Override record — plan 100037, step 2, gate `scope_check`

CEO-directed by class, 2026-09-04, session 42ce7e32. The CEO ruled option 1 (override and continue) on step 1's `scope_check` failure; this is the identical class, verified identically, on different files.

## The gate was right
`scope_check` refused because QA modified `tests/test_depositor_receipts.py` and `tests/test_wrap_receipts.py`, neither declared in the plan's Scope.

## Why the change was necessary
Closing FO-1 makes an emitted, key-complete `validation:` line a precondition for BAR_MET. **Any test anywhere in the repo that constructs a plan fixture** is affected — not only `cycle_check`'s. Both files build held/claimable plan fixtures whose manifests lacked a `validation:` line, so the new gate correctly rejected them.

⚠️ **This widens FO-1's measured blast radius.** Step 1 revealed it reaches `cycle_check`'s own tests; step 2 shows it reaches the depositor and wrap suites too. The Planner's Scope anticipated neither. The blast radius of FO-1 is *every plan-fixture construction site in the test suite*, which no walk of this cycle identified.

## Verified before overriding
- assertion lines changed: **0**
- diffs are pure additions: `+2/-0` and `+1/-0`
- test counts unchanged: 23 → 23, 26 → 26
- full suite from the dispatch worktree: **1870 passed, 1 skipped, 0 failed**
- kill map re-run here: **6 killed / 0 survived / 0 error**
- FO-1 demonstration: `_manifest_validation_keys(halted-executable-100031)` → `frozenset()` (was `None`) — it REFUSES where it passed
- FO-3 demonstration: `_parse_qa_steps('none')` → `set()`; the template placeholder → `set()`

## A third deficiency the QA step found and fixed
`knowledge/mutants/close-failopen-defaults.json` lacked the top-level `target` field `mutation_check` requires; each mutant carried its own override but the tool reads the top-level one first. **That is a defect in the Planner's Item 5**, caught by the executing agent, not by any of seven walks.

## Scope
Step 2's `scope_check` only. Nothing here waives any other gate.
