# Bellows — Stream-JSON Post-Restart Smoke Test
**Date:** 2026-04-23 | **Tier:** Small | **Test Scope:** targeted | **Execution:** Step 1 (DEV) → Step 2 (DEV)

## How to Run This Plan

Bellows should claim this automatically. If running manually:

**Bootstrap:**
```
Read the plan at bellows/knowledge/decisions/executable-stream-json-smoke-test-2026-04-23.md. Execute Step 1 ONLY. After completing Step 1, STOP and wait for my confirmation.
```

**Purpose:** Verify that after restart, Bellows invokes `claude -p` with `--output-format stream-json --verbose` AND that resume (session_id passed across steps) works in the real Bellows dispatch path. Pre-restart baseline log: `bellows/logs/20260423-210526-step.json` — its `raw_output` field is a single JSON object. Post-restart logs should show NDJSON (multi-line, each line parseable as JSON).

---
---

## STEP 1 — BELLOWS DEVELOPER

---

> **FIRST — before doing anything else, claim this plan:** `import shutil; shutil.move("bellows/knowledge/decisions/executable-stream-json-smoke-test-2026-04-23.md", "bellows/knowledge/decisions/in-progress-executable-stream-json-smoke-test-2026-04-23.md")`. You are the Bellows Developer. Skip specialist file read — this is a trivial smoke test, no project-specific constraints needed. Skip glossary read — mechanical task. **Your task — keep it minimal.** Write the string `hello from step 1` to `/tmp/bellows-smoke-2026-04-23.txt` using Python: `with open("/tmp/bellows-smoke-2026-04-23.txt", "w") as f: f.write("hello from step 1\n")`. Then read the file back and confirm its content matches. That is the entire step. Do NOT investigate Bellows internals. Do NOT read any source files. Do NOT commit anything to git. This step exists solely to produce a Bellows log entry under the post-restart runner so we can verify NDJSON format and session_id capture. **Deliverable.** Append one line to `bellows/knowledge/qa/evidence/executable-stream-json-smoke-test-2026-04-23/step1-receipt.txt`: `Step 1 complete at <current UTC timestamp>`. Create the directory first if needed. **Prompt feedback.** Skip for smoke tests — this is a minimal instrumentation task, feedback would be "the prompt was correctly minimal." **Deposits:**
>
> - `bellows/knowledge/qa/evidence/executable-stream-json-smoke-test-2026-04-23/step1-receipt.txt`
>
> **STOP. Wait for CEO confirmation before continuing.**

---
---

## STEP 2 — BELLOWS DEVELOPER

---

> **Before starting, read `bellows/knowledge/qa/evidence/executable-stream-json-smoke-test-2026-04-23/step1-receipt.txt` — it should contain the Step 1 completion line. If the file is missing or empty, stop and report — Step 1 did not produce its deliverable.** **Your task — keep it minimal.** Read `/tmp/bellows-smoke-2026-04-23.txt` and confirm its content is `hello from step 1\n` (produced by Step 1). Append `goodbye from step 2` to the same file so content becomes `hello from step 1\ngoodbye from step 2\n`. Use Python: read first, then open in append mode and write the second line. That is the entire step. Do NOT investigate Bellows internals. Do NOT commit anything to git. **Session continuity check.** This step implicitly tests Bellows's resume path — if Bellows correctly extracted session_id from Step 1's NDJSON result event and passed it via `--resume` to Step 2's `claude -p` invocation, session_id continuity works under stream-json. You do not need to verify this yourself — the Planner will verify by reading both step logs post-execution. **Deliverable.** Append one line to `bellows/knowledge/qa/evidence/executable-stream-json-smoke-test-2026-04-23/step2-receipt.txt`: `Step 2 complete at <current UTC timestamp>. Step 1 content verified: yes/no. Final file content: <contents of /tmp/bellows-smoke-2026-04-23.txt>`. **Housekeeping — keep minimal.** This is a smoke test, not a full-workflow plan. Do NOT update PROJECT_STATUS.md (session wrap will cover it). Do NOT run Rule 20 self-check (not a QA step). The Planner will move this plan to Done manually after reading the logs. **Clean up the scratch file last:** `import os; os.remove("/tmp/bellows-smoke-2026-04-23.txt")`. **Deposits:**
>
> - `bellows/knowledge/qa/evidence/executable-stream-json-smoke-test-2026-04-23/step2-receipt.txt`
>
> **STOP. The Planner verifies NDJSON format + session continuity by reading the Bellows step logs directly, then moves the plan to Done.**
