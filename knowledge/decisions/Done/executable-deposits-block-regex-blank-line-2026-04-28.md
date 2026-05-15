# Bellows — DEPOSITS_BLOCK_RE Blank-Line Tolerance
**Date:** 2026-04-28 | **Tier:** Small | **Test Scope:** full-suite | **Execution:** Step 1 (Bellows Developer) → Step 2 (Bellows Security & Testing)
**Priority:** 5

## Context

Closes BACKLOG #5. `DEPOSITS_BLOCK_RE` (defined in `verdict.py:13`, duplicated inline in `gates.py::_extract_plan_required_deposits`) fails to match when a blank blockquote line `>\n` sits between the `**Deposits:**` header and the first bullet. Live evidence: `verdict-request-permission-prompt-substrate-2026-04-23-step-1.md` shows `Deposit: none` despite the plan declaring a valid block-form deposit at `bellows/knowledge/research/permission-prompt-substrate-2026-04-23.md`. The plan structure has `**Deposits:**\n>\n> - \`...\`` — the regex pattern `[> ]*-\s+...` cannot match the empty `>\n` line because it requires `-` after the optional blockquote prefix.

Empirical validation (7 test cases): inserting `(?:[> ]*\n)*` between the header-newline and the bullet group fixes all blank-line variants (single blank, multi-blank, blank with leading prose, blank with trailing STOP) while preserving the negative property — cross-paragraph spans still correctly fail to match. Same regex appears in `verdict.py` line 13 (constant `DEPOSITS_BLOCK_RE`) and `gates.py` line ~174 (inline in `_extract_plan_required_deposits`); both must be fixed in the same commit per the existing keep-in-sync comment.

Existing tests in `test_extract_primary_deposit_blocks.py` and `test_rule_26_deposit_parser.py` did not catch this bug because they use clean block forms without blank `>` lines. The plan adds positive (blank-line tolerance) and negative (cross-paragraph rejection) tests to both test files to lock in both properties.

Test Scope: full-suite — touches load-bearing parser code with a duplicated regex; full pytest run is the safe default.

## How to Run This Plan

Bellows watcher claims this plan automatically. Step 1 (Bellows Developer) edits both regexes and adds tests. Step 2 (Bellows Security & Testing) runs the full pytest suite, performs Rule 17 deliverable verification, behavioral check against a real plan with the bug-trigger structure, Rule 20 self-check, then commits + updates PROJECT_STATUS.md. Per disable-auto-close, terminal step pauses for Planner verdict.

---
---

## STEP 1 — Bellows Developer

---

> **FIRST — claim this plan:** `import shutil; shutil.move("bellows/knowledge/decisions/executable-deposits-block-regex-blank-line-2026-04-28.md", "bellows/knowledge/decisions/in-progress-executable-deposits-block-regex-blank-line-2026-04-28.md")`. **Skip glossary read AND skip specialist file read — this is a regex fix in load-bearing parser code, no domain or architecture content.** All file paths below are absolute under `/Users/marklehn/Desktop/GitHub/`. **Task 1 — verdict.py regex.** Edit `bellows/verdict.py` line 13. Use `Filesystem:edit_file` to change `DEPOSITS_BLOCK_RE = re.compile(r'[> ]*\*\*Deposits:\*\*\s*\n((?:[> ]*-\s+.*\n?)+)')` to `DEPOSITS_BLOCK_RE = re.compile(r'[> ]*\*\*Deposits:\*\*\s*\n(?:[> ]*\n)*((?:[> ]*-\s+.*\n?)+)')` — single insertion of `(?:[> ]*\n)*` between `\n` and the bullet group. **Task 2 — gates.py inline regex.** Edit `bellows/gates.py` inside `_extract_plan_required_deposits()`. Find the line `block_match = re.search(r'[> ]*\*\*Deposits:\*\*\s*\n((?:[> ]*-\s+.*\n?)+)', step_text)` and change to `block_match = re.search(r'[> ]*\*\*Deposits:\*\*\s*\n(?:[> ]*\n)*((?:[> ]*-\s+.*\n?)+)', step_text)`. Same character insertion. **Task 3 — verdict.py tests.** Edit `bellows/tests/test_extract_primary_deposit_blocks.py`. Add a new test class or three new test functions: (a) `test_block_with_blank_quoted_line_between_header_and_bullets` — feeds `extract_primary_deposit` a step text containing `**Deposits:**\n>\n> - \`bellows/foo.md\`\n` and asserts return value is `bellows/foo.md` (not None); (b) `test_block_with_multiple_blank_quoted_lines` — same with `\n>\n>\n> - ...`; (c) `test_block_does_not_span_paragraphs` — feeds `**Deposits:**\n>\n\nSome other prose.\n\n- \`unrelated/bar.md\`\n` and asserts return value is None (the empty line breaks the bullet group). **Task 4 — gates.py tests.** Edit `bellows/tests/test_rule_26_deposit_parser.py`. Add three parallel tests calling `_extract_plan_required_deposits` with the same three inputs as Task 3: blank-line case returns `{'bellows/foo.md'}`, multi-blank returns same, cross-paragraph returns empty set. **Task 5 — run pytest.** `cd /Users/marklehn/Desktop/GitHub/bellows && python -m pytest tests/ -v 2>&1 | tail -30`. Expected: all prior tests pass + 6 new tests pass. **Task 6 — dev log.** Use `Filesystem:write_file` to write a development log to `bellows/knowledge/development/deposits-block-regex-blank-line-dev-2026-04-28.md` with: (a) the empirical bug case (cite `verdict-request-permission-prompt-substrate-2026-04-23-step-1.md` showing `Deposit: none`); (b) regex change shown as before/after on a single line; (c) which two files were edited; (d) summary of 6 new tests added; (e) pytest output tail showing test count delta. **Task 7 — commit.** `cd /Users/marklehn/Desktop/GitHub/bellows && git add verdict.py gates.py tests/test_extract_primary_deposit_blocks.py tests/test_rule_26_deposit_parser.py knowledge/development/deposits-block-regex-blank-line-dev-2026-04-28.md && git commit -m "fix(parser): DEPOSITS_BLOCK_RE tolerates blank quoted lines between header and bullets"`. **Standard prompt feedback protocol** → `bellows/knowledge/research/agent-prompt-feedback.md`.
>
> **Deposits:**
> - `bellows/knowledge/development/deposits-block-regex-blank-line-dev-2026-04-28.md`

---
---

## STEP 2 — Bellows Security & Testing

---

> **Before starting, read `bellows/knowledge/development/deposits-block-regex-blank-line-dev-2026-04-28.md` and check the Output Receipt status. If status is not Complete, stop and report the blocker before proceeding.** **Skip glossary read AND skip specialist file read — this is regression verification of a regex fix.** **FIRST — Deliverable Verification (Rule 17).** Read the Step 1 Output Receipt "Files Created or Modified (Code)" list. For each listed file, verify the change landed: (a) `grep -n "DEPOSITS_BLOCK_RE = re.compile" bellows/verdict.py` should show `(?:[> ]*\n)*` in the pattern; (b) `grep -n "block_match = re.search" bellows/gates.py` should show `(?:[> ]*\n)*` in the inline regex; (c) `grep -c "test_block_with_blank_quoted_line\|test_block_with_multiple_blank_quoted_lines\|test_block_does_not_span_paragraphs" bellows/tests/test_extract_primary_deposit_blocks.py` should return ≥3; (d) same grep against `bellows/tests/test_rule_26_deposit_parser.py` should return ≥3. Pipe each grep output to `bellows/knowledge/qa/evidence/executable-deposits-block-regex-blank-line-2026-04-28/grep_deliverables.txt`. Build a verification table with these four rows. **Task 1 — full pytest suite.** `cd /Users/marklehn/Desktop/GitHub/bellows && python -m pytest tests/ -v 2>&1 | tee bellows/knowledge/qa/evidence/executable-deposits-block-regex-blank-line-2026-04-28/pytest_full.txt`. Expected: prior 65 tests pass + 6 new tests pass = 71 passing (or whatever the prior baseline was, +6). All other tests must still pass — zero regressions. **Task 2 — behavioral verification against real plan.** Run this Python script to confirm the fix works on the actual stranded plan that exposed the bug, and capture output to `bellows/knowledge/qa/evidence/executable-deposits-block-regex-blank-line-2026-04-28/behavioral_check.txt`: `cd /Users/marklehn/Desktop/GitHub/bellows && python3 -c "
from verdict import extract_primary_deposit, _extract_step_text_from_plan
from gates import _extract_plan_required_deposits
plan_path = '/Users/marklehn/Desktop/GitHub/bellows/knowledge/decisions/Done/diagnostic-permission-prompt-substrate-2026-04-23.md'
with open(plan_path) as f: plan_text = f.read()
step_text = _extract_step_text_from_plan(plan_text, 1)
print('extract_primary_deposit:', extract_primary_deposit(step_text))
print('_extract_plan_required_deposits:', _extract_plan_required_deposits(step_text))
" 2>&1 | tee bellows/knowledge/qa/evidence/executable-deposits-block-regex-blank-line-2026-04-28/behavioral_check.txt`. Expected output: `extract_primary_deposit: bellows/knowledge/research/permission-prompt-substrate-2026-04-23.md` and `_extract_plan_required_deposits: {'bellows/knowledge/research/permission-prompt-substrate-2026-04-23.md'}`. If output shows `None` or empty set, the fix is not loaded — flag as Critical and stop. **Task 3 — write QA report.** Use `Filesystem:write_file` to write `bellows/knowledge/qa/deposits-block-regex-blank-line-qa-2026-04-28.md` containing: (a) Rule 17 deliverable verification table (4 rows, all should be ✅); (b) test execution summary citing `pytest_full.txt` (test count before/after, all passing); (c) behavioral check summary citing `behavioral_check.txt` (real-plan extraction now returns expected path); (d) verdict on closure of BACKLOG #5. **Task 4 — Rule 20 self-check.** Run this Python block exactly as written, with `<plan-filename-without-md>` filled in as `executable-deposits-block-regex-blank-line-2026-04-28`, and include the literal stdout in the QA report:
>
> ```python
> # Rule 20 — Mandatory QA Self-Check
> import os, sys
> plan_slug = "executable-deposits-block-regex-blank-line-2026-04-28"
> qa_report_path = "/Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/deposits-block-regex-blank-line-qa-2026-04-28.md"
> evidence_dir = f"/Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/evidence/{plan_slug}/"
> required_evidence_files = ["grep_deliverables.txt", "pytest_full.txt", "behavioral_check.txt"]
> hedging_keywords = ["pending", "inferred", "extrapolated", "estimated", "approximate", "skipped", "assumed", "close enough", "should pass", "would pass", "not run"]
> POSITIVE_STATUS_TOKENS = ["✅", "OK", "PASS", "done", "complete", "verified"]
> def is_positive_row(line):
>     if "|" not in line:
>         return False
>     cells = [c.strip() for c in line.split("|")]
>     for cell in cells:
>         for token in POSITIVE_STATUS_TOKENS:
>             if token == "✅":
>                 if "✅" in cell:
>                     return True
>             else:
>                 if cell.lower() == token.lower():
>                     return True
>     return False
> failures = []
> if not os.path.isdir(evidence_dir):
>     failures.append(f"CRITICAL: evidence folder missing: {evidence_dir}")
> else:
>     for fname in required_evidence_files:
>         fpath = os.path.join(evidence_dir, fname)
>         if not os.path.isfile(fpath):
>             failures.append(f"CRITICAL: evidence file missing: {fpath}")
>         elif os.path.getsize(fpath) == 0:
>             failures.append(f"CRITICAL: evidence file empty: {fpath}")
> if os.path.isfile(qa_report_path):
>     with open(qa_report_path, "r") as f:
>         report = f.read()
>     for line in report.splitlines():
>         if is_positive_row(line):
>             lower = line.lower()
>             for kw in hedging_keywords:
>                 if kw in lower:
>                     failures.append(f"CRITICAL: hedging keyword '{kw}' in positive-status row: {line.strip()[:120]}")
>                     break
> else:
>     failures.append(f"CRITICAL: QA report not found at {qa_report_path}")
> print("=" * 60)
> print("Rule 20 — QA Self-Check Results")
> print("=" * 60)
> if failures:
>     print(f"FAILED — SELF-CHECK FAILED — {len(failures)} issue(s):")
>     for f in failures:
>         print(f"  - {f}")
>     print("\nPlan CANNOT close. Fix issues and re-run QA.")
>     sys.exit(1)
> else:
>     print("PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.")
>     print(f"Evidence folder: {evidence_dir}")
>     print(f"Files verified: {len(required_evidence_files)}")
> ```
>
> If self-check prints FAILED, stop and report to CEO — do NOT update PROJECT_STATUS.md, do NOT proceed. If PASSED, proceed. **Task 5 — Update PROJECT_STATUS.md.** Add a Completed Milestone entry summarizing this plan: BACKLOG #5 closed, regex fix in `verdict.py` + `gates.py`, 6 new tests, behavioral check confirmed real plan now extracts correctly. Use `Filesystem:edit_file` with a verbatim anchor from the current file content. **Task 6 — Standard prompt feedback protocol** → `bellows/knowledge/research/agent-prompt-feedback.md`. **Task 7 — final commit.** `cd /Users/marklehn/Desktop/GitHub/bellows && git add knowledge/qa/deposits-block-regex-blank-line-qa-2026-04-28.md knowledge/qa/evidence/executable-deposits-block-regex-blank-line-2026-04-28/ knowledge/PROJECT_STATUS.md knowledge/research/agent-prompt-feedback.md && git commit -m "qa: deposits-block-regex blank-line fix verified, BACKLOG #5 closed"`. **STOP.** Do NOT move this plan to Done/. Per the disable-auto-close model, the Planner performs the terminal move after Rule 22 verification passes.
>
> **Deposits:**
> - `bellows/knowledge/qa/deposits-block-regex-blank-line-qa-2026-04-28.md`
> - `bellows/knowledge/qa/evidence/executable-deposits-block-regex-blank-line-2026-04-28/grep_deliverables.txt`
> - `bellows/knowledge/qa/evidence/executable-deposits-block-regex-blank-line-2026-04-28/pytest_full.txt`
> - `bellows/knowledge/qa/evidence/executable-deposits-block-regex-blank-line-2026-04-28/behavioral_check.txt`
