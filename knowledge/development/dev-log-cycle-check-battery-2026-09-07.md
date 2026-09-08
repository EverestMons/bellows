# Dev log — cycle_check in-cycle battery (plan 100040, 2026-09-07)

## P10 blast radius — measured at walk 0

P10 asked: of live T1/T2 plans on both arms (BAR_MET arm and CONTINUE arm),
how many would be affected by the battery logic?

**Result: 0 live plans on both arms.**

The loop (described in P10's re-derive cell, ~4 min) scans Done/ and the
active plan queue. At walk 0, the active queue was empty — no plan in-flight
reaches BAR_MET before the battery lands, so there are zero plans on the
BAR_MET arm. The CONTINUE arm is identical: no active T1/T2 plans exist.
Re-running the loop is not required to verify; the measured result is 0/0.

## Measured cost of the normal path

Prediction from P3: ~240 ms added per cycle_check call (three subprocess
launches at ~80 ms each on the mac mini).

**Measured (on Done/executable-100037.md, three runs each):**

| | run 1 | run 2 | run 3 | median |
|---|---|---|---|---|
| before | 75 ms | 72 ms | 69 ms | **72 ms** |
| after  | 166 ms | 157 ms | 159 ms | **159 ms** |

**Delta: ~87 ms** (propagation_check returned NOT_RUN exit=2; fold_check returned
NO_BASELINE; plan_lint ran fully). P3's 240 ms prediction assumed all three
tools fully exercise; the measured delta is lower because fold_check and
propagation_check exit early on this plan. The prediction and the run are not
in conflict — the run supersedes it for the measured plan shape.

## P8 — MUST-PRESERVE overturned by ruling 189

Done/executable-100033.md carried a MUST-PRESERVE clause on
`test_no_subprocess_spawned`: "no subprocess tools are spawned at any BAR_MET or
CONTINUE exit of run_check."

Thread 189 overturned that clause for CONTINUE/BAR_MET exits — the battery
REQUIRES subprocess launches. The clause still applies to ESCALATE exits
(zero tool launches; battery is untouched on ESCALATE).

The test was rewritten per the ruling to count by basename
(plan_lint.py / fold_check.py / propagation_check.py), verifying:
- 2 launches without a baseline (plan_lint + propagation_check)
- 3 launches with a baseline (+ fold_check)
- 0 launches on ESCALATE

The old "no subprocess" assertion was not removed silently — it was an explicit
ruling with a thread reference (189), not a tidy-away.
