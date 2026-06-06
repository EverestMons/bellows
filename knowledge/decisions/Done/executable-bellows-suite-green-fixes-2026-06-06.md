# Bellows — Suite-Green Fixes (load_phrases worktree-root + stale timeout test)
**Date:** 2026-06-06 | **Tier:** Executable | **Dispatch Mode:** bellows | **Test Scope:** full | **Execution:** Step 1 (SA) → Step 2 (DEV) → Step 3 (QA) | **Priority:** 2

**auto_close:** false
**pause_for_verdict:** always

## Execution Map
Step 1 (SA: edit map for both fixes) → Step 2 (DEV: implement) → Step 3 (QA: full suite green + Rule 20). Sequential.

## Context

The bellows suite has carried 5 red tests (confirmed pre-existing on baseline `bf3b679`), which makes every "Rule 21: all green" assertion hollow. Two independent root causes, both diagnosed:

- **Fix #1 (code) — `load_phrases()` worktree-root fragility.** `decisions.py:11 GOVERNANCE_ROOT = Path(__file__).parent.parent` resolves to the canonical checkout's parent when run canonically, but to `.bellows-worktrees/<wt>/` when the module runs from a worktree — so `PHRASES_FILE` (`INTERMEDIATE_DECISION_PHRASES.md`, which lives at the governance root, not in the worktree) is not found, `load_phrases()` returns `[]`, and the 4 `test_decisions.py` tests that assert known phrases fail. Latent production angle: any worktree-context call to `load_phrases()` silently gets zero phrases (degraded decision detection). This is the **third instance** of `__file__`-relative worktree-root confusion (anvil `ANVIL_ROOT`/F8 → Plan A; this). **Fix:** introduce a reusable `resolve_governance_root()` that walks up from `__file__` to the nearest ancestor containing the stable marker `COMPANY.md` (present at governance root, absent inside bellows), and derive `GOVERNANCE_ROOT` from it. NOT an inline patch — the helper is the reusable pattern; the four latent `BELLOWS_ROOT = Path(__file__).parent` siblings are filed for a separate audited follow-up (BACKLOG 2026-06-06), out of scope here.

- **Fix #2 (test-only) — stale `test_run_step_timeout`.** `runner.run_step` handles timeouts via `subprocess.Popen` + an inactivity/wall-clock polling loop (`runner.py:61` Popen; `:126-128` inactivity kill; `:151-167` timeout result). The test mocks `runner.subprocess.run` (which `run_step` no longer calls), so the mock never fires, Popen runs for real, no timeout triggers, and `is_error` comes back `False`. The implementation is correct; the test is stale. **Fix:** rewrite the test to mock `subprocess.Popen` with a fake process that produces no output and does not exit, so the inactivity-timeout path fires and returns `is_error=True`, `stop_reason="timeout"`, `escalate=True`.

`test_decisions.py` needs NO edit — its 4 failures resolve once `GOVERNANCE_ROOT` resolves correctly (including from the QA worktree, where the walk-up reaches the governance root). Expected outcome: full suite **448 passed, 0 failed**.

**This plan doubles as the first real canary of the merge-ff teardown model** (Plan B, now live post-restart): it is the first multi-step plan to land via `git merge` teardown. If teardown lands clean here, that is live validation of the merge model. If teardown misbehaves, treat it as a merge-model regression (revert Plan B `3de01a5` + restart), not a fault of these fixes.

## How to Run This Plan
Bellows dispatches normally; pauses after every step. No daemon restart needed (no daemon-code change — `decisions.py`/`runner.py` are imported by the daemon, but this plan does not require the running daemon to reload to validate; the fixes are validated in-worktree by QA). Keep bellows main clean.

---
---

## STEP 1 — BELLOWS SYSTEMS ANALYST

---

> **Identity:** You are the Bellows Systems Analyst. Begin with `SA claim: suite-green fixes edit map` BEFORE any reads. **Reads (in order):** `agents/BELLOWS_SYSTEMS_ANALYST.md`; `decisions.py` (esp. lines 11-50, the `GOVERNANCE_ROOT`/`PHRASES_FILE`/`load_phrases` region); `tests/test_decisions.py` (the failing `TestLoadPhrases` + `TestExtractDecisionBlocks::test_s_class_blocks_from_ground_truth`); `runner.py` lines 33-170 (`run_step` Popen + inactivity/wall-clock loop); `tests/test_runner_parser.py::test_run_step_timeout`. Ack each read.
>
> **Task:** Produce a precise edit map. No source changes. Sandbox any checks in /tmp. Prefix each section with a 1-line marker.
>
> (1) **`resolve_governance_root()` helper.** Specify a function that walks up from `Path(__file__).resolve()` through parents until it finds one containing `COMPANY.md`, returning that path; with an explicit fallback (raise a clear error, or fall back to the current `.parent.parent`) if no marker is found before filesystem root. Map exactly how `GOVERNANCE_ROOT` (line 11) and `PHRASES_FILE` (line 12) are rewritten to use it. Confirm `PHRASES_FILE` is the SOLE consumer of `GOVERNANCE_ROOT` in `decisions.py` (grep). Confirm the walk-up reaches the governance root from BOTH the canonical checkout AND a worktree path `bellows/.bellows-worktrees/<wt>/` (sandbox-verify the parent chain). State whether `COMPANY.md` is the right marker or another (e.g. `PLANNER_TEMPLATE.md`) is more stable.
> (2) **Timeout-test rewrite.** Map exactly how to rewrite `test_run_step_timeout` to exercise the real Popen inactivity-timeout path: what fake object to substitute for `subprocess.Popen` (a stub whose `poll()` returns `None`, whose `stdout`/`stderr` readline yields no output / blocks-then-empty, and that the inactivity timer will kill), how to keep the test fast (patch the `timeout` arg small, or patch the clock/sleep), and which return fields to assert (`is_error is True`, `stop_reason == "timeout"`, `escalate is True`). The test must NOT actually launch `claude`. Confirm the inactivity path (`runner.py:126-128`) is the one exercised and the result is built at `:151-167`.
> (3) **Scope confirmation.** Confirm the only files needing edits are `decisions.py` and `tests/test_runner_parser.py`; confirm `test_decisions.py` needs NO edit (its assertions pass once `GOVERNANCE_ROOT` resolves). State the expected post-fix suite count (448 passed, 0 failed).
>
> Mark anything unsettled OPEN. Standard prompt-feedback protocol.
>
> **Deposits:**
> - `knowledge/architecture/suite-green-fixes-blueprint-2026-06-06.md`

---
---

## STEP 2 — BELLOWS DEVELOPER

---

> Before starting, read `knowledge/architecture/suite-green-fixes-blueprint-2026-06-06.md`; if any item is OPEN, STOP and report.
>
> **Identity:** You are the Bellows Developer. Begin with `DEV claim: suite-green fixes impl`. **Reads:** `agents/BELLOWS_DEVELOPER.md`, the blueprint, the cited `decisions.py`/`runner.py`/test regions. Ack each.
>
> **Scope — you will edit exactly these files:** `decisions.py`, `tests/test_runner_parser.py`. Nothing else. Do NOT edit `test_decisions.py` (it passes once the path resolves).
>
> **Task:** Implement the blueprint exactly, `python3 -m pytest tests/ -q` after each change:
> 1. Add `resolve_governance_root()` to `decisions.py` (walk-up-to-`COMPANY.md` with fallback per blueprint §1); rewrite `GOVERNANCE_ROOT`/`PHRASES_FILE` to use it.
> 2. Rewrite `test_run_step_timeout` to mock `subprocess.Popen` and exercise the inactivity-timeout path (blueprint §2); keep it fast; assert `is_error`/`stop_reason`/`escalate`.
>
> **Self-verify before deposit:** full `pytest tests/` is **448 passed, 0 failed** (the 4 `test_decisions` + 1 `test_runner_parser` reds now green); `decisions.py` resolves `GOVERNANCE_ROOT` correctly when imported from a worktree path (demonstrate, e.g. import from a /tmp copy or assert the walk-up logic); the timeout test does not launch `claude` and runs in well under the real timeout.
>
> If blueprint and code disagree, STOP and flag. Standard prompt-feedback protocol.
>
> **Deposits:**
> - `decisions.py`
> - `tests/test_runner_parser.py`
> - `knowledge/development/suite-green-fixes-impl-2026-06-06.md` (changes, per-edit pytest, final count = 448/0, worktree-resolution demonstration, confirmation `claude` not launched). Output Receipt.

---
---

## STEP 3 — BELLOWS QA

---

> Before starting, read `knowledge/development/suite-green-fixes-impl-2026-06-06.md`; if Status not Complete, STOP.
>
> **Identity:** You are the Bellows QA Analyst. Begin with `QA claim: suite-green fixes regression`. **Reads:** `agents/BELLOWS_QA.md`, blueprint, dev log. Evidence → `knowledge/qa/evidence/executable-bellows-suite-green-fixes-2026-06-06/` (`mkdir -p`).
>
> **MANDATORY — DO NOT SKIP (gate-enforced):** This step is REJECTED by the daemon's `rule_20_self_check` gate unless your QA report contains the literal banner `Rule 20 — QA Self-Check Results` followed by `PASSED — SELF-CHECK PASSED`. The verification table does NOT satisfy this. You MUST run the canonical Rule 20 block (check (4)) and paste its FULL stdout into the report under a `## Rule 20 Self-Check` heading. Before finishing, grep your own report for the banner; if absent, you have NOT completed this step.
>
> (1) **Full suite GREEN (Rule 21).** `pytest tests/ -q > .../pytest_full.txt 2>&1`. Expected: **448 passed, 0 failed** — explicitly confirm 0 failures (this plan's whole purpose is a green suite; ANY failure is a check-(1) FAIL, not a footnote). Read and record the tail line.
> (2) **The 5 formerly-red tests pass.** `pytest tests/test_decisions.py::TestLoadPhrases tests/test_decisions.py::TestExtractDecisionBlocks::test_s_class_blocks_from_ground_truth tests/test_runner_parser.py::test_run_step_timeout -v > .../formerly_red.txt 2>&1`. Confirm all 5 pass.
> (3) **Worktree resolution.** Confirm (from the dev log / a direct check) that `decisions.GOVERNANCE_ROOT` resolves to the governance root (the dir containing `COMPANY.md`) and `load_phrases()` returns a non-empty list when imported from the QA worktree path. Evidence to `.../worktree_resolution.txt`.
> (4) **Rule 20 self-check — REQUIRED, gate-enforced.** Copy `/Users/marklehn/Developer/GitHub/RULE_20_SELF_CHECK_BLOCK.md` VERBATIM, replace ONLY the four placeholders: `plan_slug = "executable-bellows-suite-green-fixes-2026-06-06"`, `qa_report_path = "/Users/marklehn/Developer/GitHub/bellows/knowledge/qa/2026-06-06-suite-green-fixes-qa.md"`, `evidence_dir = "/Users/marklehn/Developer/GitHub/bellows/knowledge/qa/evidence/executable-bellows-suite-green-fixes-2026-06-06/"`, `required_evidence_files = ["pytest_full.txt","formerly_red.txt","worktree_resolution.txt"]`. Run with `python3`; paste FULL stdout (banner + PASSED line) under `## Rule 20 Self-Check`. If FAILED, fix and re-run. Agent does NOT move to Done — Planner issues the terminal verdict.
> (5) **QA report** `knowledge/qa/2026-06-06-suite-green-fixes-qa.md` with `| Check | Expected | Status | Evidence |` over (1)-(3) + the Rule 20 section. Hedging in a ✅ row auto-fails.
>
> **Final self-verify:** `grep -c "Rule 20 — QA Self-Check Results" knowledge/qa/2026-06-06-suite-green-fixes-qa.md` ≥1.
>
> Standard prompt-feedback protocol.
>
> **Deposits:**
> - `knowledge/qa/2026-06-06-suite-green-fixes-qa.md` (MUST contain the Rule 20 banner + PASSED line)
> - `knowledge/qa/evidence/executable-bellows-suite-green-fixes-2026-06-06/`
