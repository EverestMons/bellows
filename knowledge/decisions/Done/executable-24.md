# Bellows — Persist Partial Output on Inactivity-Timeout Kill
**Date:** 2026-06-12 | **Tier:** Small | **Dispatch Mode:** bellows | **Execution:** Step 1 (DEV) → Step 2 (QA) | **pause_for_verdict:** always | **qa_steps:** 2 | **Test Scope:** full suite

## Context (Rule 27)
This executable implements diagnostic 23. CEO fork verdicts (processed-verdict-23-step-1): Fork 1 = shape (a), persist the reader's accumulated buffer on the kill path; Fork 2 = 5000-char truncation cap, consistent with the other error paths. The diagnostic findings at `knowledge/research/partial-output-timeout-loss-2026-06-12.md` are AUTHORITATIVE — its Gap Assessment (G1: timeout `_write_log` dict omits `raw_output`; G2: timeout return dict writes `result_text: ""` despite `result_stdout` holding the accumulated pre-stall output) defines the work; re-verify its Verification Blocks at edit time and halt-and-report on divergence rather than improvising. This closes FORWARD row 18 (Step 2 reconciles it per Rule 42). DAEMON RESTART REQUIRED after close for the fix to take effect (flag in receipt).

## How to Run
Bellows dispatches this plan automatically when deposited; no manual bootstrap required.

---
---

## STEP 1 — Bellows Developer

---

> **FIRST — before any reads or work: post a short visible chat message (1-2 sentences) confirming you are starting this plan and stating your immediate next action.** Liveness anchor — do NOT rename the plan file (Bellows owns the claim). **AFTER posting:** read your specialist file `agents/BELLOWS_DEVELOPER.md`, then the diagnostic IN FULL. **Scope is exactly: `runner.py`, `tests/`.**
> - **G1:** add `"raw_output": result_stdout[:5000]` to the timeout-path `_write_log` dict (diagnostic locates it; re-verify by grep on the timeout branch).
> - **G2:** change the timeout return dict's `"result_text": ""` to `"result_text": result_stdout[:5000]`.
> - Make no other changes — the success path's uncapped `raw_output` and the other error paths' existing 5000-caps are out of scope.
>
> **Tests:** extend `tests/test_runner.py` (or `test_runner_parser.py` per existing pattern): a timeout-killed fake process whose reader accumulated output yields a result dict carrying that output (truncated at 5000) in `result_text`, and the written step JSON carries it in `raw_output`; plus a regression case for the genuinely-silent stall (empty buffer → empty strings, no exception). Then run the FULL suite (`python3 -m pytest tests/`) to an explicit pass/fail and READ THE TAIL. Write the dev log (both edits with line numbers, test count before/after, suite tail) to `bellows/knowledge/development/partial-output-persist-dev-log-2026-06-12.md`. Use `with open()` for deposits; no heredocs. Standard prompt feedback → `knowledge/research/agent-prompt-feedback.md`. **Deposits:**
> - `bellows/knowledge/development/partial-output-persist-dev-log-2026-06-12.md`

---
---

## STEP 2 — Bellows QA

---

> **FIRST — post a short visible chat message (1-2 sentences) confirming you are starting this step.** Do NOT rename the plan file. **AFTER posting:** read your specialist file `agents/BELLOWS_QA.md`, the dev log, and the diagnostic Section 4. **Verify, each with executed evidence (files into `knowledge/qa/evidence/partial-output-persist-2026-06-12/`):** (1) **Full suite** — `python3 -m pytest tests/` final 15 lines, zero failures/errors, new-test count matches the dev log; output to `full_suite_tail.txt`. (2) **G1/G2 landed** — grep the timeout branch for both `result_stdout[:5000]` sites and confirm no other `raw_output`/`result_text` site changed (`git diff HEAD~1 -- runner.py` scoped to the timeout branch); output to `edits_check.txt`. (3) **Behavioral proof** — run the new timeout tests in isolation with `-v` and include the output; output to `behavior_check.txt`. (4) **FORWARD reconciliation (Rule 42)** — update `knowledge/FORWARD.md` row 18: Status → `closed-by-plan-<this plan's id>`, Plan-id link → `<this plan's id>`; output the diff to `forward_reconciliation.txt`.
>
> Run the canonical Rule 20 self-check from `RULE_20_SELF_CHECK_BLOCK.md` at the governance root. Use these values when filling in the template: `plan_slug`: `partial-output-persist-2026-06-12`; `qa_report_path`: `<your worktree absolute path>/knowledge/qa/partial-output-persist-qa-report-2026-06-12.md`; `evidence_dir`: `<your worktree absolute path>/knowledge/qa/evidence/partial-output-persist-2026-06-12/`; `required_evidence_files`: `[full_suite_tail.txt, edits_check.txt, behavior_check.txt, forward_reconciliation.txt]`. Include the literal stdout output of the block in the QA report. If the block prints `FAILED`, halt and report to CEO instead of closing. Write the QA report with a verification table (item | method | evidence file | PASS/FAIL) and the Rule 20 banner block to `bellows/knowledge/qa/partial-output-persist-qa-report-2026-06-12.md`. **Receipt Flags for CEO must include:** DAEMON RESTART REQUIRED — no hot reload; live canary is the next inactivity-timeout kill carrying non-empty raw_output. Use `with open()` for deposits; no heredocs. **Deposits:**
> - `bellows/knowledge/qa/partial-output-persist-qa-report-2026-06-12.md`
> - `bellows/knowledge/qa/evidence/partial-output-persist-2026-06-12/` (four evidence files per Rule 20 self-check)
