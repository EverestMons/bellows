# Bellows — stop_prose Pattern Narrowing (Zero-True-Positive Census Fix)
**Date:** 2026-06-12 | **Tier:** Small | **Dispatch Mode:** bellows | **Execution:** Step 1 (DEV) → Step 2 (QA) | **pause_for_verdict:** always | **qa_steps:** 2 | **Test Scope:** full suite

## Context (Rule 27)
This executable implements diagnostic 27 (second of two serialized fix plans; the diff-baseline fix closed as plan 28). CEO fork verdicts (processed-verdict-27-step-1): row 17 = shape A+C2 — narrow the `STOP\.` and `do not proceed` patterns to imperative-at-line-start forms, and REMOVE the `wait for confirmation` pattern entirely (zero activations ever recorded); justified by the diagnostic's true-positive census: across the complete 2026-05-28→2026-06-12 log corpus, all ~26 stop_prose firings were false positives in four classes, zero true positives. Per fork (4), FORWARD rows 8 and 11 close as subsumed (both are instances of the same pattern-broadness problem). The diagnostic findings at `knowledge/research/gate-fp-cluster-root-cause-2026-06-12.md` are AUTHORITATIVE — its Section 3 FP-class analysis and Gap Assessment rows name the exact patterns at `validators.py:12-16` (re-verify by grep); halt-and-report on divergence. NOTE: stop_prose is a claim-time WARN-severity validator — no daemon-restart urgency beyond the existing pending restarts, but flag it anyway for completeness.

## How to Run
Bellows dispatches this plan automatically when deposited; no manual bootstrap required.

---
---

## STEP 1 — Bellows Developer

---

> **FIRST — before any reads or work: post a short visible chat message (1-2 sentences) confirming you are starting this plan and stating your immediate next action.** Liveness anchor — do NOT rename the plan file (Bellows owns the claim). **AFTER posting:** read your specialist file `agents/BELLOWS_DEVELOPER.md`, then the diagnostic Sections 3, 4, 5. **Scope is exactly these files: `validators.py`, `tests/test_validators.py`.**
>
> Implement A+C2 per the diagnostic: (1) narrow the `STOP\.` pattern to the imperative-at-line-start form the diagnostic specifies (it must still match the genuinely-dangerous directive shape — a line opening with the STOP imperative — while no longer matching mid-sentence instructional or self-referencing prose); (2) narrow `do not proceed` the same way; (3) remove the `wait for confirmation` pattern. Preserve the existing fence/deposits-block/inline-backtick exclusions untouched.
>
> **Tests:** extend `tests/test_validators.py`: one test per diagnostic FP class proving it no longer fires (PLANNER_TEMPLATE step-boundary language, error-handling prose, Rule 20 instructional prose, self-referencing prose — take the verbatim examples from the diagnostic's Section 3), plus positive tests proving a genuinely dangerous line-start directive still fires for both retained patterns, plus a regression test that the removed pattern's text no longer triggers anything. Then run the FULL suite (`python3 -m pytest tests/`) to an explicit pass/fail and READ THE TAIL. Write the dev log (pattern diffs, test count before/after, suite tail) to `bellows/knowledge/development/stop-prose-narrowing-dev-log-2026-06-12.md`. Use `with open()` for deposits; no heredocs. Standard prompt feedback → `knowledge/research/agent-prompt-feedback.md`. **Deposits:**
> - `bellows/knowledge/development/stop-prose-narrowing-dev-log-2026-06-12.md`

---
---

## STEP 2 — Bellows QA

---

> **FIRST — post a short visible chat message (1-2 sentences) confirming you are starting this step.** Do NOT rename the plan file. **AFTER posting:** read your specialist file `agents/BELLOWS_QA.md`, the dev log, and the diagnostic Section 3. **Verify, each with executed evidence (files into `knowledge/qa/evidence/stop-prose-narrowing-2026-06-12/`):** (1) **Full suite** — final 15 lines, zero failures/errors, new-test count matches dev log; output to `full_suite_tail.txt`. (2) **Patterns landed** — `git diff HEAD~1 -- validators.py` shows exactly the two narrowed regexes and the one removal, nothing else; output to `patterns_check.txt`. (3) **Corpus replay (the census check)** — run the NEW patterns over the diagnostic's four verbatim FP-class examples AND over this very plan file's own step text (which contains the phrases in instructional positions): zero matches; then over a synthetic dangerous line-start directive: match; output to `corpus_replay.txt`. (4) **FORWARD reconciliation (Rule 42)** — update `knowledge/FORWARD.md`: row 17 Status → `closed-by-plan-<this plan's id>` with Plan-id link; rows 8 and 11 Status → `closed-by-plan-<this plan's id>` with Item suffix ` — closed 2026-06-12: subsumed by row 17 fix (diagnostic 27)`; output the diff to `forward_reconciliation.txt`.
>
> Run the canonical Rule 20 self-check from `RULE_20_SELF_CHECK_BLOCK.md` at the governance root. Use these values when filling in the template: `plan_slug`: `stop-prose-narrowing-2026-06-12`; `qa_report_path`: `<your worktree absolute path>/knowledge/qa/stop-prose-narrowing-qa-report-2026-06-12.md`; `evidence_dir`: `<your worktree absolute path>/knowledge/qa/evidence/stop-prose-narrowing-2026-06-12/`; `required_evidence_files`: `[full_suite_tail.txt, patterns_check.txt, corpus_replay.txt, forward_reconciliation.txt]`. Include the literal stdout output of the block in the QA report. If the block prints `FAILED`, halt and report to CEO instead of closing. Write the QA report with a verification table (item | method | evidence file | PASS/FAIL) and the Rule 20 banner block to `bellows/knowledge/qa/stop-prose-narrowing-qa-report-2026-06-12.md`. **Receipt Flags for CEO:** restart pending-set now includes plans 24, 28, and this plan. Use `with open()` for deposits; no heredocs. **Deposits:**
> - `bellows/knowledge/qa/stop-prose-narrowing-qa-report-2026-06-12.md`
> - `bellows/knowledge/qa/evidence/stop-prose-narrowing-2026-06-12/` (four evidence files per Rule 20 self-check)
