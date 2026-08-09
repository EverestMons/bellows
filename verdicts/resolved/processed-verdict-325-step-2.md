verdict: continue

Step 2 gate failures RESOLVED -- continue-with-reasoning; both FAILs adjudicated:

1. full-suite regressions (rule_22 (c) row 1): the 3 stored-version pin assertions
   the Step-1 sweep missed were fixed by executable-327 (merged; the same scan-forward
   sweep found nothing further). PROOF from 327's raw QA evidence (full-suite.txt):
   "2 failed, 2461 passed, 1 warning in 848.63s" -- the known CLAUDE.md pair only.
   The suite over 325's shipped code is GREEN at HEAD.

2. deposit_exists / rule_22 (a) canonical-migration.txt: the plan declared it as a
   CONDITIONAL deposit ("when that pass ran"); the canonical DB does not exist in the
   bellows worktree (data/ absent), and the QA report took exactly the plan-mandated
   fallback: stated plainly, hermetic migration test (which passes, migration.txt) as
   the evidence, canonical migration deferred to next app start, rollout note carried
   forward verbatim. The gate cannot read conditionality; the absence is per-plan.

325's own deliverables were verified at the step-2 check: all 8 new tests pass
(migration fast-path + fresh-build + idempotency + stat1; EQP names the composite
index with the source-match guard; 4 preload populations; statement capture shows
zero per-row COUNTs), Rule 20 byte-exact, baseline arithmetic quoted.

CARRY-FORWARD FOR THE CEO (from the QA report's rollout section): before the first
app start on each machine after pulling v20, run the py -c backup one-liner; expect
a one-time ANALYZE pause at first start.

Terminal step: continue closes the plan to Done/.
