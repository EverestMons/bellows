# Bellows — Verdict File Format README
**Date:** 2026-04-16 | **Tier:** Small | **Test Scope:** targeted | **Execution:** Step 1 (DEV) → Step 2 (QA)

## How to Run This Plan

Paste the bootstrap prompt into Claude Code. The agent reads the full plan file and executes Step 1 ONLY. After completing Step 1, the agent STOPS and waits for CEO confirmation ("ok") before proceeding to Step 2.

**Bootstrap:**
```
Read the plan at bellows/knowledge/decisions/parallel-1-executable-verdict-readme-2026-04-16.md. Execute Step 1 ONLY. After completing Step 1, STOP and wait for CEO confirmation before proceeding.
```

---
---

## STEP 1 — DEV

---

> **FIRST — claim this plan:** `import shutil; shutil.move("/Users/marklehn/Desktop/GitHub/bellows/knowledge/decisions/parallel-1-executable-verdict-readme-2026-04-16.md", "/Users/marklehn/Desktop/GitHub/bellows/knowledge/decisions/in-progress-parallel-1-executable-verdict-readme-2026-04-16.md")`. Skip specialist file and glossary reads — bellows has no specialist files and this is a documentation-only task. **Task:** Create `bellows/verdicts/README.md` documenting the verdict file format. The file must cover: **(1) Purpose** — Bellows pauses plans for Planner/CEO review under five conditions (gate failure, QA checkpoint, agent-requested verdict, header `pause_for_verdict`, auto-close disabled). The Planner writes a verdict file to `verdicts/resolved/` to tell Bellows how to proceed. **(2) Verdict file naming** — `verdict-<plan-slug>-step-<N>.md` where `<plan-slug>` is derived from the plan filename by stripping `in-progress-`, `verdict-pending-`, `executable-`, `diagnostic-` prefixes and the `.md` extension. Example: plan `diagnostic-foo-bar-2026-04-16.md` → slug `foo-bar-2026-04-16` → verdict file `verdict-foo-bar-2026-04-16-step-1.md`. **(3) Verdict file format** — first line MUST match regex `^verdict:\s*(continue|stop)$` (case-insensitive). All subsequent lines are freeform reason text. Two valid values: `continue` (proceed to next step, or move to Done if final step) and `stop` (halt the plan, rename to `halted-`). **(4) Where to write** — `bellows/verdicts/resolved/`. Bellows scans this directory every 30 seconds via `_consume_verdicts()`. After consuming a verdict, Bellows renames it with a `processed-` prefix. **(5) What triggers a verdict request** — table listing the five pause conditions with their `pause_reason` tokens: `gate_failure`, `qa_checkpoint`, `agent_verdict_request`, `header_pause`, `auto_close_disabled`. Note: the `pause_reason` field is being added to verdict requests in a concurrent plan; the README should document the target state. **(6) Worked example** — show a minimal `verdict: continue` file with a 2-line reason. Keep the whole README under 60 lines of markdown. Clear, terse, no fluff. **Commit:** `cd /Users/marklehn/Desktop/GitHub/bellows && git add verdicts/README.md && git commit -m "docs: verdict file format README"`.
>
> **STOP. Do NOT proceed to Step 2. Do NOT move the plan to Done. Wait for CEO confirmation before continuing.**

---
---

## STEP 2 — QA

---

> Before starting, verify Step 1 committed by running `git --no-pager log --oneline -1` and confirming the commit message matches "docs: verdict file format README". If not, stop and report. **Deliverable Verification:** (a) `ls /Users/marklehn/Desktop/GitHub/bellows/verdicts/README.md` — file exists. (b) `grep -c "verdict:" /Users/marklehn/Desktop/GitHub/bellows/verdicts/README.md` — expect ≥2 (the format spec line + the worked example). (c) `wc -l /Users/marklehn/Desktop/GitHub/bellows/verdicts/README.md` — expect ≤60 lines. (d) Verify the README documents all five pause conditions by grepping for each token: `grep -c "gate_failure\|qa_checkpoint\|agent_verdict_request\|header_pause\|auto_close_disabled" /Users/marklehn/Desktop/GitHub/bellows/verdicts/README.md` — expect ≥5. Produce a verification table: `| Check | Expected | Status | Evidence |`. **Deposit:** write QA report to `/Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/verdict-readme-qa-2026-04-16.md`. **Final:** Update PROJECT_STATUS.md — add a completed milestone: "Verdict file format README added to `verdicts/README.md`." Then move this plan to Done: `import shutil; shutil.move("/Users/marklehn/Desktop/GitHub/bellows/knowledge/decisions/in-progress-parallel-1-executable-verdict-readme-2026-04-16.md", "/Users/marklehn/Desktop/GitHub/bellows/knowledge/decisions/Done/parallel-1-executable-verdict-readme-2026-04-16.md")`. Commit: `"chore: QA + status update for verdict README"`. Standard prompt feedback protocol → `/Users/marklehn/Desktop/GitHub/bellows/knowledge/research/agent-prompt-feedback.md`.
>
> **STOP. Do NOT proceed further. Plan complete after this step.**
