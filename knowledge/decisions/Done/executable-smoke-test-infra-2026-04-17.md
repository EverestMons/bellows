# bellows — Smoke Test (New Infrastructure)
**Date:** 2026-04-17 | **Tier:** Small | **Test Scope:** targeted | **Model:** claude-sonnet-4-6 | **Priority:** 1 | **Execution:** Step 1 (DEV) → Step 2 (QA)

## How to Run This Plan

**Bootstrap:** `Read the plan at bellows/knowledge/decisions/executable-smoke-test-infra-2026-04-17.md. Execute Step 1 ONLY. After completing Step 1, STOP and wait for my confirmation. Do NOT proceed to Step 2 or move the plan to Done.`

## Context

Smoke test to verify all Bellows infrastructure shipped today: (1) per-plan model override (`**Model:** claude-sonnet-4-6` above — Bellows should print "using model override: claude-sonnet-4-6"), (2) shadow copy cache (should show "using cached plan content (2 steps)" on resume), (3) activity-based timeout (runner heartbeats should show "last output Ns ago"), (4) Gate 5 backtick-free path resolution (deposit check should pass cleanly).

---
---

## STEP 1 — DEV

---

> **FIRST — claim this plan:** `import shutil; shutil.move("bellows/knowledge/decisions/executable-smoke-test-infra-2026-04-17.md", "bellows/knowledge/decisions/in-progress-executable-smoke-test-infra-2026-04-17.md")`. Skip all reads. **Single commit.** Create a file `bellows/knowledge/research/smoke-test-infra-2026-04-17.md` with content: `# Smoke Test — Infrastructure Verification\n**Date:** 2026-04-17\n**Status:** Complete\n\nThis file exists solely to test Gate 5 deposit verification with the new path resolution and backtick stripping fixes.\n`. Use canonical Python file write: `content = "# Smoke Test — Infrastructure Verification\n**Date:** 2026-04-17\n**Status:** Complete\n\nThis file exists solely to test Gate 5 deposit verification.\n"; f = open("bellows/knowledge/research/smoke-test-infra-2026-04-17.md", "w"); f.write(content); f.close()`. Commit: `test: smoke test — bellows infrastructure verification`. **Deposit dev log** to `bellows/knowledge/development/smoke-test-infra-2026-04-17.md` using canonical Python file write. Standard prompt feedback protocol.
>
> **STOP. Do NOT proceed to Step 2. Do NOT move the plan to Done. Wait for CEO confirmation before continuing.**

---
---

## STEP 2 — QA

---

> Before starting, read `bellows/knowledge/development/smoke-test-infra-2026-04-17.md` and check Output Receipt. If not Complete, stop. **Verify:** (a) `bellows/knowledge/research/smoke-test-infra-2026-04-17.md` exists and contains "Infrastructure Verification". (b) Commit exists in git log. Pipe to `bellows/knowledge/qa/evidence/executable-smoke-test-infra-2026-04-17/grep_deliverables.txt`. **Deposit QA report** to `bellows/knowledge/qa/smoke-test-infra-qa-2026-04-17.md`. Move to Done. Commit: `chore: move smoke test to Done`.
>
> **STOP. Do NOT proceed further. Wait for CEO confirmation.**
