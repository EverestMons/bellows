# Bellows — Per-Plan Diff Baseline (Parallel-Plan scope_check Contamination Fix)
**Date:** 2026-06-12 | **Tier:** Small | **Dispatch Mode:** bellows | **Execution:** Step 1 (DEV) → Step 2 (QA) | **pause_for_verdict:** always | **qa_steps:** 2 | **Test Scope:** full suite

## Context (Rule 27)
This executable implements diagnostic 27 (first of two serialized fix plans — the validators plan deposits only after this one closes; same-repo plans must not run concurrently while this very bug is live). CEO fork verdicts (processed-verdict-27-step-1): row 21 = Option A — store a per-plan diff baseline at dispatch start instead of diffing against a moving live HEAD, so a concurrent plan's merges to main can never enter this plan's `files_changed` (observed live: plan 19's QA artifacts flagged in plan 20's gate). Also per fork (2): FORWARD row 16 closes as ALREADY FIXED by the union scope_check commit `706fbe7` (2026-06-10, pre-id era) — register disposition only, no code change for it. The diagnostic findings at `knowledge/research/gate-fp-cluster-root-cause-2026-06-12.md` are AUTHORITATIVE — its Gap Assessment row "In-place diff contamination" names the change (`_capture_git_diff` callsites at bellows.py:534/644 per the diagnostic; re-verify by grep) and its Verification Blocks must be re-verified at edit time; halt-and-report on divergence. DAEMON RESTART REQUIRED after close (flag in receipt).

## How to Run
Bellows dispatches this plan automatically when deposited; no manual bootstrap required.

---
---

## STEP 1 — Bellows Developer

---

> **FIRST — before any reads or work: post a short visible chat message (1-2 sentences) confirming you are starting this plan and stating your immediate next action.** Liveness anchor — do NOT rename the plan file (Bellows owns the claim). **AFTER posting:** read your specialist file `agents/BELLOWS_DEVELOPER.md`, then the diagnostic IN FULL (Sections 1, 2, 4, 5 minimum). **Scope is exactly: `bellows.py`, `tests/`.**
>
> Implement the diagnostic's Option A: capture the plan's diff baseline ONCE at dispatch start (where the current initial `pre_diff` is taken) and make every subsequent diff capture for this plan compare against that stored baseline rather than re-reading live state that concurrent plans can move. Follow the diagnostic's mechanism analysis exactly — it is authoritative for which callsites change and how the in-place mode behaves; preserve the existing per-step pre/post semantics for computing each step's OWN files_changed (the fix isolates the plan from FOREIGN changes; it must not merge successive steps' changes into one another — re-read the diagnostic's row-16 analysis to keep these concerns separate, since union-text matching already handles cross-step scope).
>
> **Tests:** extend the existing worktree/gates test patterns: (a) a file changed outside the plan's baseline lineage (simulating a concurrent plan's merge) does NOT appear in files_changed; (b) the plan's own step changes still DO appear; (c) multi-step: step 2's files_changed reflects step 2's changes per existing semantics. Then run the FULL suite (`python3 -m pytest tests/`) to an explicit pass/fail and READ THE TAIL. Write the dev log (edits with line ranges, test count before/after, suite tail) to `bellows/knowledge/development/diff-baseline-fix-dev-log-2026-06-12.md`. Use `with open()` for deposits; no heredocs. Standard prompt feedback → `knowledge/research/agent-prompt-feedback.md`. **Deposits:**
> - `bellows/knowledge/development/diff-baseline-fix-dev-log-2026-06-12.md`

---
---

## STEP 2 — Bellows QA

---

> **FIRST — post a short visible chat message (1-2 sentences) confirming you are starting this step.** Do NOT rename the plan file. **AFTER posting:** read your specialist file `agents/BELLOWS_QA.md`, the dev log, and the diagnostic Sections 1 and 5. **Verify, each with executed evidence (files into `knowledge/qa/evidence/diff-baseline-fix-2026-06-12/`):** (1) **Full suite** — final 15 lines, zero failures/errors, new-test count matches dev log; output to `full_suite_tail.txt`. (2) **Mechanism landed** — grep the baseline storage at dispatch start and confirm every `_capture_git_diff`-class callsite uses it per the diagnostic's Gap row; `git diff HEAD~1 -- bellows.py` scoped to those sites only; output to `mechanism_check.txt`. (3) **Behavioral proof** — run the new contamination tests in isolation with `-v`; output to `behavior_check.txt`. (4) **FORWARD reconciliation (Rule 42)** — update `knowledge/FORWARD.md`: row 21 Status → `closed-by-plan-<this plan's id>` with Plan-id link set; row 16 Status → `withdrawn` with Item suffix ` — withdrawn 2026-06-12: already fixed pre-id by union scope_check (commit 706fbe7); per diagnostic 27`; output the diff to `forward_reconciliation.txt`.
>
> Run the canonical Rule 20 self-check from `RULE_20_SELF_CHECK_BLOCK.md` at the governance root. Use these values when filling in the template: `plan_slug`: `diff-baseline-fix-2026-06-12`; `qa_report_path`: `<your worktree absolute path>/knowledge/qa/diff-baseline-fix-qa-report-2026-06-12.md`; `evidence_dir`: `<your worktree absolute path>/knowledge/qa/evidence/diff-baseline-fix-2026-06-12/`; `required_evidence_files`: `[full_suite_tail.txt, mechanism_check.txt, behavior_check.txt, forward_reconciliation.txt]`. Include the literal stdout output of the block in the QA report. If the block prints `FAILED`, halt and report to CEO instead of closing. Write the QA report with a verification table (item | method | evidence file | PASS/FAIL) and the Rule 20 banner block to `bellows/knowledge/qa/diff-baseline-fix-qa-report-2026-06-12.md`. **Receipt Flags for CEO must include:** DAEMON RESTART REQUIRED; live canary: the next pair of overlapping same-repo plans gates without foreign files in files_changed. Use `with open()` for deposits; no heredocs. **Deposits:**
> - `bellows/knowledge/qa/diff-baseline-fix-qa-report-2026-06-12.md`
> - `bellows/knowledge/qa/evidence/diff-baseline-fix-2026-06-12/` (four evidence files per Rule 20 self-check)
