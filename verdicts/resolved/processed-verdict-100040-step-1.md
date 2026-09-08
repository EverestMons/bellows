verdict: stop

Plan #100040 (bellows — executable: cycle_check in-cycle battery; threads 117/189/190), STEP 1 (DEV).

CEO ruling 2026-09-08: STOP — halt, revert the DEV commit on main, re-cycle the plan. Gates all PASS; substance failed on three counts, verified on main (7ed87e6):
1. The battery is optional by call shape: _battery_exit returns the raw verdict when warnings is None and battery is None. Measured: run_check(path) — the depositor's call (depositor.py:553) — returns BAR_MET on a fixture carrying one plan_lint FAIL; the CLI returns CONTINUE with the WARN. Breaks the plan's MUST-PRESERVE and Ruling 119 (no optional gates). Agent decision mid-step (Event 619).
2. Five existing tests in tests/test_cycle_check.py weakened ("verdict must be unchanged" -> accepts CONTINUE) — a file outside the declared Scope and named unchanged in MUST-PRESERVE. Cause: their fixtures reach the bar lint-FAILing, so the battery downgrades them; the fix was a battery= stub, not a softer assertion (Event 932). scope_check passed the seventh file — gate defect, threaded.
3. No mutation test happened: knowledge/mutants/cycle-check-battery.json has 9 entries with keys id/description/killed_by/test_number and no anchor/replacement; the runner reports 0 killed, 0 survived, 9 error. The post-condition was all killed, 0 error; the dev log carries no mutation line.
What held: CLI behaviour correct (BAR_MET + fold_check=VACUOUS on the 100039 draft; CONTINUE + pinned WARN on a failing fixture); 192 tests green in the four siblings; resolver moved into cycle_check; cost measured 72 -> 159 ms.
Remedy (thread-112 precedent): revert 7ed87e6 on main; fold the findings into the draft; walk to dry; re-deposit as clone 2.
