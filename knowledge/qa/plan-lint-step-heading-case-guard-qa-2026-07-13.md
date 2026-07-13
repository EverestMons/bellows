# QA Report — plan_lint.py Check (e): Step Heading Case/Format Guard

**Date:** 2026-07-13
**Plan:** 172
**Agent:** Bellows QA
**Step:** 2

## Verification Table

| # | Claim | Status | Evidence |
|---|---|---|---|
| 1 | New (e) block sits after `step_headers` computation and BEFORE the (b) deposits loop | PASS | `step_headers` computed at `scripts/plan_lint.py:68`; (e) block at lines 70-79; (b) deposits loop begins at line 82. Ordering is correct. |
| 2 | FAIL arm sets `all_passed = False` and appends to `results`; WARN arm is print-only | PASS | FAIL arm (lines 72-77): `results.append(("FAIL", "(e) step heading format", msg))` then `all_passed = False`. WARN arm (lines 78-79): `print("WARN: ...")` only — no `all_passed` assignment, no `return`, no `results.append`. |
| 3 | Case-insensitive regex anchored to level-2 headings (`^##\s+step\s+\d`), NOT bare "step" in prose | PASS | Line 71: `r'^(##\s+step\s+(\d+)\b[^\n]*)'` with `re.IGNORECASE | re.MULTILINE`. Pattern requires `^##\s+` (start-of-line, two hashes, whitespace) before `step`, so it cannot match the word "step" in prose. |
| 4 | Test (a): title-case `qa_steps` plan -> (e) FAIL + exit 1 | PASS | `test_lint_titlecase_step_headings_with_qa_steps_fails` (line 302): asserts `result.returncode == 1`, `"(e)" in result.stdout`, `"vacuous pass" in result.stdout`, `"uppercase" in result.stdout.lower()`. |
| 5 | Test (b): correct uppercase plan -> NO (e) row | PASS | `test_lint_uppercase_step_headings_no_e_fail` (line 331): asserts `"(e)" not in result.stdout`. Uses `GOOD_PLAN` fixture which has uppercase `## STEP N`. |
| 6 | Test (c): single-step diagnostic -> NO (e) FAIL, NO case WARN, exit 0 | PASS | `test_lint_single_step_diagnostic_no_e_fail` (line 337): plan has no `qa_steps`, no step headings of any case; asserts `result.returncode == 0`, `"(e)" not in result.stdout`, `"WARN" not in result.stdout`. Critical no-false-positive row. |
| 7 | Test (d): no-`qa_steps` `## Step` prose -> WARN + exit 0 | PASS | `test_lint_titlecase_step_no_qa_steps_warns_only` (line 353): plan has `## Step 1` but no `qa_steps`; asserts `result.returncode == 0`, `"WARN" in result.stdout`, `"uppercase" in result.stdout.lower()`, `"(e)" not in result.stdout`. |
| 8 | Pre-existing tests unchanged — `git diff HEAD~1 -- tests/` shows additions only | PASS | Diff output shows only `+` lines appended after line 297 (end of `test_lint_qa_steps_absent_no_warn`). No deletions, no modifications to any existing test. |
| 9 | Full suite green | PASS | `python3 -m pytest tests/ -v` output: `795 passed, 1 warning in 19.88s`. Zero failures. |

## Rule 20 — QA Self-Check Results

All 9 verification rows passed. The (e) check is correctly positioned, correctly scoped (FAIL only when `qa_steps` present, WARN-only otherwise), and does not false-positive on single-step diagnostics. The case-insensitive regex is properly anchored to level-2 headings. All four new tests assert on exact substrings and exit codes. Pre-existing tests are untouched. Full suite is green.

**PASSED — SELF-CHECK PASSED**

---

## Output Receipt
**Agent:** Bellows QA
**Step:** 2
**Status:** Complete

### What Was Done
Performed code-level verification of check (e) in `scripts/plan_lint.py` against 9 claims: block ordering, FAIL/WARN arm behavior, regex anchoring, all four test cases, additions-only diff, and full suite pass. All rows verified.

### Files Deposited
- `knowledge/qa/plan-lint-step-heading-case-guard-qa-2026-07-13.md` — this QA report

### Files Created or Modified (Code)
- None (QA step — verification only)

### Decisions Made
- All verification rows pass; no issues found requiring escalation

### Flags for CEO
- None

### Flags for Next Step
- None
