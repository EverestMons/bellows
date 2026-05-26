# Bellows — `test_rule_26_deposit_parser` Set-Literal Assertion Follow-Up

**Date:** 2026-05-25 | **Tier:** Small | **Dispatch Mode:** bellows | **Test Scope:** targeted | **Execution:** Step 1 (DEV) → Step 2 (QA) | **qa_steps:** 2 | **pause_for_verdict:** after_step_1

## Context

The 2026-05-25 set→list plan (`executable-extract-plan-required-deposits-set-to-list-2026-05-25`, in Done/) converted `_extract_plan_required_deposits` from returning `set` to returning `list`. Its QA was scoped `targeted` per Rule 21 and ran only `pytest tests/test_gates.py -v`. It missed 6 regressions in `tests/test_rule_26_deposit_parser.py` where assertions take the form `assert result == {set literal}` — these fail because the function now returns a list.

The 2026-05-25 file_change_audit fix (just shipped — in Done/ pending) detected the 6 carry-overs during its full-suite run and classified them correctly as pre-existing.

This plan closes the regression with a minimal-surface fix: wrap the LHS in `set()` at 6 assertion sites in `tests/test_rule_26_deposit_parser.py`. These tests check membership semantics (which paths are extracted), not ordering — so `set(result) == {...}` asserts exactly what the original tests intended without re-introducing ordering dependency in the function itself. Ordering-sensitive testing lives in `test_gates.py::test_extract_plan_required_deposits_preserves_block_order` (added by the set→list plan).

**Sources:**
- Failing tests: `bellows/tests/test_rule_26_deposit_parser.py` lines 26, 52, 72, 123, 137, 153 (6 assertion sites)
- Set→list plan (in Done/): `bellows/knowledge/decisions/Done/executable-extract-plan-required-deposits-set-to-list-2026-05-25.md`
- Carry-over detection: `bellows/knowledge/qa/executable-file-change-audit-fix-2026-05-25.md` (today's QA report listing the 6 failures)
- Production code (NOT modified): `bellows/gates.py:372` (`_extract_plan_required_deposits` — already returns list per set→list plan)

**Test Scope: targeted** — single test file with 6 surgical assertion edits, no production code changes, no cross-bucket regression risk.

**Worktree-prefix note for the agent:** plan references use `bellows/` prefix for Planner readability. Inside the worktree, files are at the worktree root.

**Pre-existing test failures expected after this fix lands (5 carry-overs):** 4 × `test_decisions.py` worktree artifacts, 1 × `test_run_step_timeout`. The 6 `test_rule_26` failures will be closed by this plan.

## How to Run This Plan

Bellows dispatches this plan automatically when deposited; no manual bootstrap required.

---
---

## STEP 1 — Bellows Developer

---

> You are the Bellows Developer. Skip specialist file and glossary reads — this is a surgical 6-line edit to a single test file. **Task:** update 6 set-literal `==` assertions in `tests/test_rule_26_deposit_parser.py` to use `set(result) == ...` so they continue testing membership semantics after `_extract_plan_required_deposits` changed from returning `set` to returning `list`.
>
> **Read first** `tests/test_rule_26_deposit_parser.py` in full (175 lines) to confirm the 6 sites and verify no other assertion forms need updating.
>
> **Edit instructions — 6 surgical replacements in `tests/test_rule_26_deposit_parser.py`:**
>
> | Site | Line (approx) | Old assertion | New assertion |
> |------|---------------|---------------|---------------|
> | 1 | 26 | `assert result == {"knowledge/dev/alpha.md", "knowledge/dev/beta.md"}` | `assert set(result) == {"knowledge/dev/alpha.md", "knowledge/dev/beta.md"}` |
> | 2 | 52 | `assert result == set()` | `assert set(result) == set()` |
> | 3 | 72 | `assert result == {"knowledge/dev/real-deposit.md"}` | `assert set(result) == {"knowledge/dev/real-deposit.md"}` |
> | 4 | 123 | `assert result == {"bellows/foo.md"}` | `assert set(result) == {"bellows/foo.md"}` |
> | 5 | 137 | `assert result == {"bellows/foo.md"}` | `assert set(result) == {"bellows/foo.md"}` |
> | 6 | 153 | `assert result == set()` | `assert set(result) == set()` |
>
> **DO NOT** modify:
> - Any `assert "..." in result` or `assert "..." not in result` lines (these work on lists already).
> - Any production code (`gates.py`, `bellows.py`, etc.).
> - Any other test file.
>
> **Verification before committing:** run from the worktree root: `python3 -m pytest tests/test_rule_26_deposit_parser.py -v` and confirm all 6 previously-failing tests now PASS, and that no test in this file regresses. Capture the output to confirm.
>
> **Deposit a dev log** at `knowledge/development/test-rule-26-set-to-list-followup-2026-05-25.md` with sections: (a) verbatim diff of `tests/test_rule_26_deposit_parser.py` (use `git --no-pager diff tests/test_rule_26_deposit_parser.py`), (b) pytest output showing the 6 previously-failing tests now PASS, (c) confirmation that only `tests/test_rule_26_deposit_parser.py` was modified (use `git --no-pager status --short` after commit to confirm clean tree), (d) any deviations from this plan and why, (e) Output Receipt with Status: Complete. **Commit** with message `test(rule_26): wrap result LHS in set() for 6 membership assertions — closes set→list carry-over` and a brief body. Standard prompt feedback protocol → `knowledge/research/agent-prompt-feedback.md`.
>
> **Deposits:**
> - `bellows/knowledge/development/test-rule-26-set-to-list-followup-2026-05-25.md`

---
---

## STEP 2 — Bellows QA

---

> Before starting, read `bellows/knowledge/development/test-rule-26-set-to-list-followup-2026-05-25.md` and check the Output Receipt status field. If status is not Complete, stop and report the blocker before proceeding. You are the Bellows QA agent. Skip specialist file and glossary reads — this is a mechanical 6-line verification. **FIRST — Deliverable Verification.** Build a verification table with these checks, each row including line-number evidence and a verbatim quote excerpt: (1) Line 26 now reads `assert set(result) == {"knowledge/dev/alpha.md", "knowledge/dev/beta.md"}`; (2) Line 52 now reads `assert set(result) == set()`; (3) Line 72 now reads `assert set(result) == {"knowledge/dev/real-deposit.md"}`; (4) Line 123 now reads `assert set(result) == {"bellows/foo.md"}`; (5) Line 137 now reads `assert set(result) == {"bellows/foo.md"}`; (6) Line 153 now reads `assert set(result) == set()`; (7) No other lines in `tests/test_rule_26_deposit_parser.py` modified — `git --no-pager diff HEAD~1 tests/test_rule_26_deposit_parser.py` shows exactly 6 changed lines (12 if counting + and -). Mark each row ✅ or ❌ with evidence. If any ❌, stop and report.
>
> **Then — targeted pytest.** Run from the worktree root: `python3 -m pytest tests/test_rule_26_deposit_parser.py -v` and capture output to `evidence/pytest_targeted.txt`. Expected: all tests in this file PASS — specifically the 6 that were failing pre-fix (`test_extract_plan_required_deposits_prefers_declared_block`, `test_extract_plan_required_deposits_handles_none_bullet`, `test_extract_plan_required_deposits_ignores_paths_in_code_fences_when_block_present`, `test_extract_plan_required_deposits_blank_quoted_line`, `test_extract_plan_required_deposits_multiple_blank_quoted_lines`, `test_extract_plan_required_deposits_does_not_span_paragraphs`) must now show PASSED. Grep the output for each test name to confirm.
>
> **Then — structural compliance check.** Run `git --no-pager show --stat HEAD` and confirm the DEV commit touched exactly 2 files: `tests/test_rule_26_deposit_parser.py`, `knowledge/development/test-rule-26-set-to-list-followup-2026-05-25.md`. Capture to `evidence/dev_commit.txt`. Run `git --no-pager diff HEAD~1 tests/test_rule_26_deposit_parser.py` and confirm exactly 6 assertion lines changed (LHS wrapped in `set(...)`). Capture to `evidence/diff_test_rule_26.txt`.
>
> **Then — Rule 20 self-check.** Run the canonical Rule 20 self-check from `RULE_20_SELF_CHECK_BLOCK.md` at the governance root. Use these values: `plan_slug`: `executable-test-rule-26-set-to-list-followup-2026-05-25`; `qa_report_path`: `<absolute-path-to-knowledge/qa/executable-test-rule-26-set-to-list-followup-2026-05-25.md>`; `evidence_dir`: `<absolute-path-to-knowledge/qa/evidence/executable-test-rule-26-set-to-list-followup-2026-05-25/>`; `required_evidence_files`: `["pytest_targeted.txt", "dev_commit.txt", "diff_test_rule_26.txt"]`. Include the literal stdout output of the block in the QA report under an `**Output:**` heading. If FAILED, halt and report to CEO.
>
> **Then — QA report deposit.** Write `knowledge/qa/executable-test-rule-26-set-to-list-followup-2026-05-25.md` with the verification table, targeted pytest summary, structural compliance results, Rule 20 self-check stdout, and Output Receipt with Status: Complete. **DEPOSITS RULE:** declare ONLY the QA report file and the evidence directory in the **Deposits** block below. Do NOT list PROJECT_STATUS.md as a deposit even though you will update it.
>
> **Final:** Update `PROJECT_STATUS.md` — prepend a new Completed entry under today's date (2026-05-25) summarizing: `tests/test_rule_26_deposit_parser.py` updated — 6 set-literal membership assertions wrapped in `set(...)` to accommodate `_extract_plan_required_deposits` now returning list (per 2026-05-25 set→list plan); closes the carry-over regression detected during today's file_change_audit fix full-suite run. Use `Filesystem:edit_file` with verbatim anchor on the existing top entry. **STOP.** Do NOT move this plan to Done/. Standard prompt feedback protocol → `knowledge/research/agent-prompt-feedback.md`.
>
> **Deposits:**
> - `bellows/knowledge/qa/executable-test-rule-26-set-to-list-followup-2026-05-25.md`
> - `bellows/knowledge/qa/evidence/executable-test-rule-26-set-to-list-followup-2026-05-25/`
