continue

Step 1 verified: all 5 gates PASS; every A3 measurement independently reproduced against the Planner's walk-13 scratch build (builder 11/11, suite 65, earnability 22F/43P, M1-M4 all killed by their named tests, hunks 0/7/2/1); all MUST-PRESERVE prose-only invariants confirmed by reading the diff (lock containment, arm between sweep and slug check, no holder query under off, unconditional recording, SC-3 on both decline paths, basename-in-column); production config carries no project_lock so the claim path stays decision-identical.
