# Bellows — Two-Step Resume-Path Smoke Test
**Date:** 2026-06-12 | **Tier:** Small | **Dispatch Mode:** bellows | **Execution:** Step 1 (DEV) → Step 2 (QA) | **pause_for_verdict:** always | **qa_steps:** 2 | **Test Scope:** targeted

**Test Scope justification:** targeted — appends two lines to a scratch smoke-log file; no production code, no suite.

## Context (Rule 27)
CEO-requested second smoke test, deliberately a 2-step executable (the first, plan 34, was single-step) to exercise the parts the first did not: the post-verdict RESUME dispatch (the diagnostic-6 fix, plans 6/7) and two-row step coverage with `turns` populated on both rows. Trivial harmless content — each step appends one timestamped line to a scratch file and verifies. Watchable live in the dashboard across two steps and two pauses. Read/write limited to the scratch file + standard deposits.

## How to Run
Bellows dispatches this plan automatically when deposited; no manual bootstrap required.

---
---

## STEP 1 — Bellows Developer

---

> **FIRST — before any reads or work: post a short visible chat message (1-2 sentences) confirming you are starting this plan and stating your immediate next action.** Liveness anchor — do NOT rename the plan file (Bellows owns the claim). **AFTER posting:** read your specialist file `agents/BELLOWS_DEVELOPER.md`. **Scope: exactly `knowledge/development/resume-smoke-2026-06-12.md` (the scratch file) and the dev-log deposit below.** Using `with open(..., "w")` (no heredocs), create `bellows/knowledge/development/resume-smoke-2026-06-12.md` containing a title line and one line: `Step 1 (DEV) wrote this at <current ISO timestamp from datetime.now().isoformat()> — plan id <your id, from the in-progress-executable-<id>.md filename>.` Then write a one-paragraph dev log (what you wrote, your plan id, confirmation the scratch file exists) to `bellows/knowledge/development/resume-smoke-dev-log-2026-06-12.md`. **Deposits:**
> - `bellows/knowledge/development/resume-smoke-2026-06-12.md`
> - `bellows/knowledge/development/resume-smoke-dev-log-2026-06-12.md`

---
---

## STEP 2 — Bellows QA

---

> **FIRST — post a short visible chat message (1-2 sentences) confirming you are starting this step.** Do NOT rename the plan file. **Context: you were dispatched via the post-verdict RESUME path — the path the diagnostic-6 fix repaired. Confirm it worked from inside the run.** **AFTER posting:** read your specialist file `agents/BELLOWS_QA.md` and the Step 1 scratch file + dev log. **Scope: exactly the scratch file (append) + the QA deposits below.** **Verify, each with executed evidence (files into `knowledge/qa/evidence/resume-smoke-2026-06-12/`):** (1) **Step 1 landed** — `cat knowledge/development/resume-smoke-2026-06-12.md` shows Step 1's line with a plausible timestamp and plan id; output to `step1_landed.txt`. (2) **Resume-path step rows (the headline)** — derive your plan id, then `sqlite3 "file:/Users/marklehn/Developer/GitHub/bellows/lifecycle.db?mode=ro" "SELECT step_number, status, turns FROM steps WHERE plan_id=<id> ORDER BY step_number"` — confirm step 1 is `complete` with a non-NULL positive `turns` (proves the diagnostic-6 G2/G3 passthrough survived the resume dispatch) and that YOUR step-2 row exists as `running` (proves the resume-path step-row write, G1); output to `resume_step_rows.txt`. Then append one line to the scratch file via `with open(..., "a")`: `Step 2 (QA) verified this at <ISO timestamp> — resume path OK.`
>
> Run the canonical Rule 20 self-check from `RULE_20_SELF_CHECK_BLOCK.md` at the governance root. Use these values when filling in the template: `plan_slug`: `resume-smoke-2026-06-12`; `qa_report_path`: `<your worktree absolute path>/knowledge/qa/resume-smoke-qa-report-2026-06-12.md`; `evidence_dir`: `<your worktree absolute path>/knowledge/qa/evidence/resume-smoke-2026-06-12/`; `required_evidence_files`: `[step1_landed.txt, resume_step_rows.txt]`. Include the literal stdout output of the block in the QA report. If the block prints `FAILED`, halt and report to CEO instead of closing. Write the QA report with a verification table (item | method | evidence file | PASS/FAIL) and the Rule 20 banner block to `bellows/knowledge/qa/resume-smoke-qa-report-2026-06-12.md`. Use `with open()`; no heredocs. **Deposits:**
> - `bellows/knowledge/qa/resume-smoke-qa-report-2026-06-12.md`
> - `bellows/knowledge/qa/evidence/resume-smoke-2026-06-12/` (two evidence files per Rule 20 self-check)
