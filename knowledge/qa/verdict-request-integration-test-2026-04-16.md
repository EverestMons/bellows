# QA: Verdict Request Integration Test
**Date:** 2026-04-16 | **Result:** PASSED

## Signal Path Validated

**(a) Agent outputted `VERDICT_REQUESTED:` marker**
Step 1 agent outputted the following line exactly:
```
VERDICT_REQUESTED: Integration test — verifying agent self-request verdict signal path works end-to-end through Bellows.
```

**(b) Bellows paused the plan with `agent_verdict_request` pause reason**
Bellows detected the marker in runner output, called `gates.check`, and paused the plan. The verdict request file was posted to `verdicts/pending/` with an "Agent verdict request" pause reason, then resolved to `verdicts/resolved/processed-verdict-bellows-verdict-request-integration-test-2026-04-16-step-1.md`.

**(c) `continue` verdict resumed execution to Step 2**
CEO issued `verdict: continue` via the processed verdict file. Bellows resumed the plan and dispatched Step 2.

**(d) Full signal path validated**
End-to-end path confirmed working:
- Agent output → `runner.run_step` parsing → `gates.check` detection → verdict pause (agent_verdict_request) → CEO verdict → plan resume → Step 2 dispatched
