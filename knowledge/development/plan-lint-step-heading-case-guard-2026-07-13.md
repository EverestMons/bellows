# plan_lint.py — Check (e): Step Heading Case/Format Guard

**Date:** 2026-07-13
**Plan:** 172

## Problem

`plan_lint.py` finds executable steps using a case-sensitive regex (`^(## STEP (\d+)\b...)`). A plan authored with title-case headings (`## Step 1` / `## Step 2`) yields zero matches, so step-scoped checks (b) deposits and (d) scope silently never run — the lint reports exit 0 despite never having validated those checks. This is the vacuous-pass trap that allowed plan 161's missing Rule-20 banner to slip through.

## Solution

Added check (e) immediately after the `step_headers` computation and before (b). It computes a case-insensitive version of the step-header regex:

- **FAIL** when `qa_steps` is declared but no uppercase `## STEP N` headings exist — this means (b)/(d) were skipped. If case-insensitive headings are found, the message points at the fix (use uppercase). Sets `all_passed = False` → exit 1.
- **WARN (print-only)** when no `qa_steps` and no uppercase headings but case-insensitive `## Step N` headings exist — a lower-confidence nudge that does NOT block exit 0.
- **Nothing** for a legit single-step diagnostic with no step headings of any case.

## Design Rationale

The (e) inconsistency is a FAIL, not a WARN, because a title-case executable makes the lint lie about coverage — it reports pass while (b)/(d) never executed. This is materially worse than a mis-gating advisory (which the qa_steps cross-check handles as WARN).

The check is gated on `qa_steps` presence to avoid false positives on legitimate diagnostics that use `## Step N` prose without being multi-step executable plans.

## Tests Added

Four tests in `tests/test_plan_lint.py`:
- `test_lint_titlecase_step_headings_with_qa_steps_fails` — qa_steps + title-case → (e) FAIL, exit 1
- `test_lint_uppercase_step_headings_no_e_fail` — correct uppercase → NO (e) row
- `test_lint_single_step_diagnostic_no_e_fail` — no qa_steps, no step headings → NO (e), NO WARN, exit 0
- `test_lint_titlecase_step_no_qa_steps_warns_only` — no qa_steps, title-case → WARN only, exit 0

---

## Output Receipt
**Agent:** Bellows Developer
**Step:** 1
**Status:** Complete

### What Was Done
Added check (e) to `scripts/plan_lint.py` to detect and fail on title-case step headings when `qa_steps` is declared, preventing the vacuous-pass trap. Added four tests covering all branches of the new check.

### Files Deposited
- `knowledge/development/plan-lint-step-heading-case-guard-2026-07-13.md` — this file

### Files Created or Modified (Code)
- `scripts/plan_lint.py` — added check (e) block after step_headers computation
- `tests/test_plan_lint.py` — added four tests for check (e) coverage

### Decisions Made
- (e) is a FAIL, not WARN, per plan rationale (vacuous-pass is worse than mis-gating)
- WARN arm is print-only with no `all_passed` assignment, matching existing WARN pattern

### Flags for CEO
- Design decision per plan: (e) is FAIL. If you'd prefer WARN-only symmetry with the plan-140 cross-check, say so at the pause.

### Flags for Next Step
- None
