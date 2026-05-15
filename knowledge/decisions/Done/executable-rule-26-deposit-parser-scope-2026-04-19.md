# bellows — Rule 26 Deposit Parser: Scope Gate + Fix Scoping Bug
**Date:** 2026-04-19 | **Tier:** Medium | **Test Scope:** full-suite | **Execution:** Step 1 (DEV) → Step 2 (QA)

## CEO Context

Closes BACKLOG #6 (deposit-path parser false positives) and fixes the scoping bug discovered in diagnostic-extract-primary-deposit-shape-2026-04-19. Three changes in one commit: (1) factor step-text extraction into `_extract_step_text` helper — currently duplicated inline in `_gate_deposit_exists:148` and `_gate_scope_check:199`, (2) teach `_extract_plan_required_deposits` to scope to the declared `**Deposits:**` block when present (Rule 26 convention), falling back to legacy prose-matching regexes when absent, (3) fix `post_verdict_request` to pass current-step text to `extract_primary_deposit` instead of the full plan. Verdict schema unchanged (singular `**Deposit:**` field preserved) — migration to plural field deferred to a follow-up plan. Test scope is full-suite because this touches load-bearing gate infrastructure exercised by many tests. Reference diagnostics: `bellows/knowledge/research/gates-deposit-parser-current-state-2026-04-19.md` and `bellows/knowledge/research/extract-primary-deposit-shape-2026-04-19.md`.

## How to Run This Plan

Paste the bootstrap prompt into Claude Code. The agent reads the full plan file and executes Step 1 ONLY. After completing Step 1, the agent STOPS and waits for CEO confirmation ("ok") before proceeding to Step 2.

**Bootstrap:**
```
Read the plan at bellows/knowledge/decisions/executable-rule-26-deposit-parser-scope-2026-04-19.md. Execute Step 1 ONLY. After completing Step 1, STOP and wait for my confirmation. Do NOT proceed to Step 2 or move the plan to Done.
```

---
---

## STEP 1 — Bellows Developer

---

> Skip specialist file and glossary reads — this is a targeted code change in gates.py and verdict.py. Read the two reference diagnostics first: `bellows/knowledge/research/gates-deposit-parser-current-state-2026-04-19.md` and `bellows/knowledge/research/extract-primary-deposit-shape-2026-04-19.md`. They contain verbatim current-state code for every function you'll modify.
>
> **Change 1 — Add `_extract_step_text` helper in gates.py.** Add a module-level helper function `_extract_step_text(plan_text: str, step_number: int) -> Optional[str]` that returns the text of a single step bounded by `## STEP N` and the next `## STEP` header (or end of file). Use the existing inline regex pattern `rf"## STEP {step_number}\b.*?(?=\n## STEP |\Z)"` with `re.DOTALL`. Return `None` if no match. Place the helper near the other module-level helpers in gates.py (near `_parse_plan_header` and `_extract_plan_required_deposits`).
>
> **Change 2 — Replace inline step extraction in both gates with the helper.** In `_gate_deposit_exists` (around line 148) replace the inline `step_pattern = rf"## STEP {step_number}\b.*?(?=\n## STEP |\Z)"; step_match = re.search(step_pattern, plan_text, re.DOTALL); if step_match: step_text = step_match.group(0)` block with a single call to `_extract_step_text(plan_text, step_number)`. Do the same in `_gate_scope_check` (around line 199). Preserve the surrounding control flow exactly — only the extraction itself changes.
>
> **Change 3 — Teach `_extract_plan_required_deposits` about `**Deposits:**` blocks.** Modify `_extract_plan_required_deposits(step_text) -> set[str]` to do the following: FIRST scan for a `**Deposits:**` block (the Rule 26 canonical form). If present, extract all backticked paths from the bulleted list that follows (one path per bullet, format `- \`path/to/file.md\``), ignore a `- none` bullet (return empty set if that's the only bullet), and return ONLY those paths — the legacy prose regexes are NOT applied. If no `**Deposits:**` block is present, fall back to the existing three prose-matching regex patterns (patterns 1, 2, 3 from the current implementation). Block-detection regex: `r'\*\*Deposits:\*\*\s*\n((?:\s*-\s+.*\n?)+)'` with `re.IGNORECASE` off (the field name is case-sensitive per Rule 26). Per-bullet path extraction: `r'-\s+`([^`]+)`'` applied to the captured block. The `- none` detection: after extracting paths, if paths is empty AND the block was found, return empty set (explicit "no deposits" declaration). If block was NOT found, proceed to legacy patterns.
>
> **Change 4 — Fix scoping bug in `post_verdict_request` caller.** In `verdict.py`, modify the `**Deposit:**` template line at line 94 from `f"**Deposit:** {extract_primary_deposit(step_text) or 'none'}\n"` to extract the current step's text first. Since the caller passes `step_text=plan_text` (full plan) from `bellows.py:274` and `bellows.py:333`, and verdict.py should NOT import from gates.py (circular import risk — gates imports nothing from verdict currently, keep it that way), inline the same step-text extraction regex inside `post_verdict_request`: before the content template, add `current_step_text = _extract_step_text_from_plan(step_text, step_number) or step_text` where `_extract_step_text_from_plan` is a new module-level private helper in verdict.py using the same regex as gates.py's `_extract_step_text`. Then change the template line to `f"**Deposit:** {extract_primary_deposit(current_step_text) or 'none'}\n"`. Keep the fallback to full `step_text` so behavior degrades gracefully when the regex misses (rather than silently returning 'none'). Yes, this duplicates the helper across gates.py and verdict.py — acceptable because avoiding the cross-module import is worth the ~6 lines of duplication. Note the duplication in a comment at both sites: `# Duplicated from gates.py::_extract_step_text to avoid circular import — keep in sync.`
>
> **Run the full test suite to confirm no regression:** `cd bellows && pytest tests/ -v 2>&1 | tee /tmp/pytest_dev_step.txt`. Report the final test count and any failures. Do NOT proceed if any test that was passing before now fails.
>
> **Deposit development log** to `bellows/knowledge/development/rule-26-deposit-parser-scope-2026-04-19.md` using the canonical Python file write pattern. Log: all files modified with summary of changes, function signatures added, test count before/after, git commit hash. Append commit message: "fix(gates): scope deposit_exists to declared **Deposits:** block; factor step-text extraction; fix extract_primary_deposit scoping in post_verdict_request". Commit all changes in a single commit.
>
> **Deposits:**
> - `bellows/knowledge/development/rule-26-deposit-parser-scope-2026-04-19.md`
>
> Standard prompt feedback protocol → `bellows/knowledge/research/agent-prompt-feedback.md`.
>
> **STOP. Do NOT proceed to Step 2. Do NOT move the plan to Done. Wait for CEO confirmation before continuing.**

---
---

## STEP 2 — Bellows QA

---

> Before starting, read `bellows/knowledge/development/rule-26-deposit-parser-scope-2026-04-19.md` and check the Output Receipt status field. If status is not Complete, stop and report the issue to the CEO before proceeding.
>
> Skip specialist file and glossary reads — this is a test and verification task.
>
> **FIRST — Deliverable Verification (Rule 17).** Read the DEV step Output Receipt's "Files Created or Modified (Code)" list. For EVERY listed file: verify it exists on disk AND contains the described change. Specifically check: (a) `bellows/gates.py` contains a function named `_extract_step_text` (grep for `def _extract_step_text`), (b) `bellows/gates.py` `_gate_deposit_exists` body calls `_extract_step_text` (grep for `_extract_step_text(plan_text`), (c) `bellows/gates.py` `_gate_scope_check` body calls `_extract_step_text` (same grep — should return 2 matches), (d) `bellows/gates.py` `_extract_plan_required_deposits` contains a pattern matching `\*\*Deposits:\*\*` (grep for `Deposits:\\*\\*` or `Deposits:` in that function), (e) `bellows/verdict.py` contains the scoping fix — grep for `current_step_text` or the new helper name. Pipe all grep outputs to `bellows/knowledge/qa/evidence/rule-26-deposit-parser-scope-2026-04-19/grep_deliverables.txt`. Produce a verification table: | Deliverable | Expected | Status (✅/❌) | Evidence |. If ANY item is ❌, stop and report before running tests.
>
> **Full test suite regression:** run `cd bellows && pytest tests/ -v 2>&1 | tee bellows/knowledge/qa/evidence/rule-26-deposit-parser-scope-2026-04-19/pytest_full.txt`. Compare to the baseline run in `/tmp/pytest_dev_step.txt` from the DEV step if available. Report: total tests, passing, failing, new failures vs DEV step run (should be zero new failures).
>
> **Targeted behavioral tests — write these new tests and run them.** Add a new test file `bellows/tests/test_rule_26_deposit_parser.py` with the following test cases (use pytest, follow existing test_gates.py style — inline plan text as Python multi-line strings, no fixture files):
>
> 1. `test_extract_plan_required_deposits_prefers_declared_block` — plan step contains `**Deposits:**` block with 2 backticked paths AND prose "deposit findings to `other-path.md`"; assert return set is exactly the 2 declared paths, NOT the prose path.
>
> 2. `test_extract_plan_required_deposits_falls_back_to_legacy_when_no_block` — plan step has only prose "Deposit findings to `prose-path.md`" and no `**Deposits:**` block; assert return set contains `prose-path.md`.
>
> 3. `test_extract_plan_required_deposits_handles_none_bullet` — plan step has `**Deposits:**` block with single `- none` bullet; assert return set is empty.
>
> 4. `test_extract_plan_required_deposits_ignores_paths_in_code_fences_when_block_present` — plan step has `**Deposits:**` block declaring one path, AND a fenced code block containing `path/to/file.md` prose; assert return set is exactly the declared path. This is the direct BACKLOG #6 regression test (the Rule 26 plan's own false-positive case).
>
> 5. `test_extract_primary_deposit_scoping_in_post_verdict_request` — construct a fake plan with two steps, Step 1 declaring `**Deposits:** - \`step-1.md\``, Step 2 declaring `**Deposits:** - \`step-2.md\``. Call `post_verdict_request` with `step_number=2` and `step_text=<full plan>`. Read the written verdict file and assert the `**Deposit:**` field is `step-2.md`, NOT `step-1.md`. This is the scoping bug regression test. Use `tmp_path` pytest fixture to avoid polluting `bellows/verdicts/pending/`.
>
> 6. `test_extract_step_text_helper_gates_py` — call `gates._extract_step_text(plan_text, 2)` with a 3-step plan; assert return value starts with `## STEP 2` and does not contain `## STEP 3`.
>
> Run only the new tests: `cd bellows && pytest tests/test_rule_26_deposit_parser.py -v 2>&1 | tee bellows/knowledge/qa/evidence/rule-26-deposit-parser-scope-2026-04-19/pytest_targeted.txt`. All 6 must pass. Then run the full suite again (already captured above) — confirm no regression.
>
> **Deposit QA report** to `bellows/knowledge/qa/rule-26-deposit-parser-scope-qa-2026-04-19.md` using the canonical Python file write pattern. Report must include: (a) deliverable verification table (Rule 17), (b) full suite before/after counts, (c) new targeted-test results table with 6 rows, (d) the Rule 20 mandatory self-check Python block output verbatim.
>
> **Mandatory Rule 20 self-check** — include this Python block verbatim at the end of the QA step, execute it, include the literal stdout in the QA report. If FAILED, stop and do NOT proceed to housekeeping:
>
> ```python
> # Rule 20 — Mandatory QA Self-Check
> import os, sys
> plan_slug = "executable-rule-26-deposit-parser-scope-2026-04-19"
> qa_report_path = "bellows/knowledge/qa/rule-26-deposit-parser-scope-qa-2026-04-19.md"
> evidence_dir = f"bellows/knowledge/qa/evidence/{plan_slug}/"
> required_evidence_files = ["grep_deliverables.txt", "pytest_full.txt", "pytest_targeted.txt"]
> hedging_keywords = ["pending", "inferred", "extrapolated", "estimated", "approximate", "skipped", "assumed", "close enough", "should pass", "would pass", "not run"]
> POSITIVE_STATUS_TOKENS = ["✅", "OK", "PASS", "[x]", "done", "complete", "verified"]
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
> **If Rule 20 self-check prints PASSED:** proceed to housekeeping in this order per Rule 23. Step A — append a dated entry to `bellows/knowledge/research/agent-prompt-feedback.md` with Agent name, prompt summary, unnecessary reads, over/under-scoping, what would have made the prompt more efficient, then review Patterns Identified section and update if warranted. Step B — update `bellows/PROJECT_STATUS.md` with a new completed milestone entry summarizing the changes: closes BACKLOG #6, fixes scoping bug, adds 6 new tests, factor step-text extraction helper, Rule 26 `**Deposits:**` block recognition landed. Use edit_block with anchored old_string (read the current Completed Milestones section first). Step C — final commit: "test(rule-26): add deposit parser scope tests + QA report + status update". Step D — move plan to Done: `import shutil; shutil.move("bellows/knowledge/decisions/in-progress-executable-rule-26-deposit-parser-scope-2026-04-19.md", "bellows/knowledge/decisions/Done/executable-rule-26-deposit-parser-scope-2026-04-19.md")`. Move-to-Done is the absolute last operation.
>
> **Deposits:**
> - `bellows/knowledge/qa/rule-26-deposit-parser-scope-qa-2026-04-19.md`
> - `bellows/knowledge/qa/evidence/rule-26-deposit-parser-scope-2026-04-19/` (grep_deliverables.txt, pytest_full.txt, pytest_targeted.txt per Rule 20 self-check)
>
> Standard prompt feedback protocol → `bellows/knowledge/research/agent-prompt-feedback.md`.
