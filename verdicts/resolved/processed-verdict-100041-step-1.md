verdict: stop

Plan #100041 (bellows — executable: cycle_check in-cycle battery, clone 2; threads 117/189/190), STEP 1 (DEV).

CEO ruling 2026-09-08: STOP — revert f95f604 on main, re-cycle as clone 3 (thread-112 precedent). Gates all PASS; verified on main:
FIXED from #100040: the battery runs on every call (run_check(path), run_check(path, warnings=[]) and the CLI all CONTINUE on a one-FAIL fixture); ESCALATE arms untouched; one resolver; the five existing tests adapted honestly (autouse run_battery stub, lint-clean fixture headers, last-line assertion; one WARN assertion narrowed and stated). Suite 2055 passed.
STILL FAILED, Item 6/7, invisible to the gates: (1) mutation run never done — 7 of 10 expect_fail selectors name tests that do not exist (node ids invented from the plan's numbering), the runner's baseline exits 4, no MUTATION line; on the three runnable mutants: 2 killed, 1 SURVIVED (M7 resolve-fold-baseline-ignore-beside — test 10 does not cover the beside-only case). (2) dev-log Item 7 carries none of its four records (P10 verbatim, cost table, P8, mutation line).
Remedy: revert f95f604; clone 3 makes the mutation run a Deposit file, requires --collect-only on every selector before commit, adds the beside-fallback test (M7), pins Item 7's four sections as literal headings QA checks; walk to dry; re-deposit through ready-.
