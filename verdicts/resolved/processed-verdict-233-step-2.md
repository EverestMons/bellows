verdict: stop

**Stopping — and this is a PLANNER process error, not an agent failure. The agent did exactly what the plan file told it to do.**

## What Step 2 was asked to do, and did

The plan file's Step 2 says: write the CEO runbook. It did, and it did it well — `runbook-floor-only-migration-2026-07-19.md` with Prerequisites, Procedure, **Abort paths (what happens if something fails)**, Backup and restore, and a Summary. The abort-path section is the one I most wanted and it is present. The dev log is deposited. Nothing about this step's execution is deficient.

## What did not happen, and why that is my fault

My Step-1 verdict specified two required code fixes — the G5 threshold reimplementation at `:399-401`, and the self-contradicting comment at `:262-272`. Both are still present, unchanged. I re-verified by grep just now.

**I put required code changes in a verdict for a step whose plan text never mentioned them.** The agent works from the plan file. A verdict is a message to a step that has already been dispatched with its own instructions.

**This is a direct violation of the lesson I wrote one plan ago.** LESSONS entry 90 prescribes: *"restate verdict-added requirements as numbered rows **in the plan file**, rather than leaving them in the verdict alone."* I numbered them — "Fix 1 (REQUIRED, Step 2)", "Fix 2 (REQUIRED, Step 2)" — and left them in the verdict. I followed the letter and missed the mechanism.

**The refinement entry 90 needs: numbering is not the mechanism. LOCATION is.** A numbered item in a verdict is still invisible to the agent reading the plan. This is now the fourth dropped instruction in this arc and the first one where the drop was fully predictable from a lesson already on the books.

## Remedy — plan 234, the 230→231 pattern

**Do NOT re-run Step 1 or Step 2.** The script (`fb35d72`) and the runbook (`cdc447e`) are committed and stand. Plan 233 delivered both.

Author plan 234 absorbing the remaining work, with the two fixes as **numbered rows in the plan file's own Step 1**:

1. **G5 gap identification must not re-derive the classification.** Preferred: diff the scratch copy against the original — a preserved genuine gap is a row that is interior, unchanged by the engine, and whose ceiling differs from `next_floor - 0.001`. Ground truth is the engine's actual behaviour, no threshold literal. Fallback: import `PRECISION_THRESHOLD_MILLS` from `fuel_conflict_detection` rather than hardcoding.
2. **Replace `:262-272` with one sentence** stating what the code does and why the second scratch run is necessary. The current block asserts a falsehood ("for configs with last_bracket_rule='continuation', any change IS the last bracket") and then retracts it two lines later.

Then the full QA from 233's Step 3, unchanged — its row 2 is what would have caught fix 1 anyway, and it must not be weakened to accommodate the code.

**Efficiency note:** stopping now rather than letting Step 3 run saves a ~27-minute suite that would have halted on row 2 regardless.
