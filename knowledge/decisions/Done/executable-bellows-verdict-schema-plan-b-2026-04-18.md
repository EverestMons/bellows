# Bellows — verdict.py Deposit Field Parser (Plan B)
**Date:** 2026-04-18 | **Tier:** Small | **Test Scope:** targeted | **Execution:** Step 1 (DEV) → Step 2 (QA)

## CEO Context

Test Scope: targeted — adds `extract_primary_deposit()` function to bellows.py + one modification to `post_verdict_request()` in verdict.py + new tests. No cross-module logic changes. Same targeted-scope pattern that worked for Plan A.

## How to Run This Plan

Paste the bootstrap prompt into Claude Code. The agent reads the full plan file and executes Step 1 ONLY. After completing Step 1, STOP and wait for CEO confirmation ("ok") before proceeding to Step 2. The agent must never skip steps, auto-chain, or move the plan to Done without completing all steps including QA.

**Bootstrap:**
```
Read the plan at bellows/knowledge/decisions/executable-bellows-verdict-schema-plan-b-2026-04-18.md. Execute Step 1 ONLY. After completing Step 1, STOP and wait for my confirmation. Do NOT proceed to Step 2 or move the plan to Done.
```

---
---

## STEP 1 — BELLOWS DEVELOPER

---

> **FIRST — before doing anything else, claim this plan:** `import shutil; shutil.move("bellows/knowledge/decisions/executable-bellows-verdict-schema-plan-b-2026-04-18.md", "bellows/knowledge/decisions/in-progress-executable-bellows-verdict-schema-plan-b-2026-04-18.md")`. **Skip specialist file and glossary reads — this is a mechanical parser implementation task, no domain interpretation required.** Implement the deposit-path parser for verdict request files. The diagnostic findings at `bellows/knowledge/research/deposit-path-formats-2026-04-18.md` are the source of truth — the **Proposed Implementation** and **Gap Assessment** sections specify exactly what to build. Read those two sections before making changes. Do NOT re-investigate the corpus; do NOT read plan files to verify patterns; the diagnostic already did that work. **Change 1 — add module-level regex constants to `bellows.py`.** At the top of `bellows.py` immediately after the existing `import re` statement, add four compiled regex constants: `STRICT_DEPOSIT_RE = re.compile(r'\*\*Deposits?:\*\*\s+(?:.*?\s+)?`([^`]+\.md)`')`, `BOLD_NOUN_DEPOSIT_RE = re.compile(r'\*\*(?:Deposit|Write)[^*]+\*\*\s+(?:to|at)\s+`([^`]+\.md)`', re.IGNORECASE)`, `INLINE_DEPOSIT_RE = re.compile(r'[Dd]eposit(?:ing)?\s+[\w\s]+?\s+(?:to:?|at|as)\s+`([^`]+\.md)`')`, and `FEEDBACK_EXCLUSION_RE = re.compile(r'[Ss]tandard prompt feedback protocol')`. Note: `BOLD_NOUN_DEPOSIT_RE` MUST include `re.IGNORECASE` — this is load-bearing for the ALL-CAPS `**WRITE THE QA REPORT**` variant observed in bellows plans (findings cluster B edge case). The other patterns do NOT need `re.IGNORECASE` because they use explicit `[Dd]eposit` character classes. **Change 2 — add `extract_primary_deposit()` function to `bellows.py`.** Add this function anywhere below the regex constants and above the `Bellows` class (suggested location: near `extract_step_number()` and `extract_total_steps()` which are already in the file). Implementation per the findings's **Proposed Implementation / Extraction Logic** section: iterate over lines in `step_text`, skip lines matching `FEEDBACK_EXCLUSION_RE`, try each of the three priority patterns in order (STRICT → BOLD_NOUN → INLINE), return the first match's captured path, normalize absolute paths containing `/Desktop/GitHub/` to project-relative by splitting on that substring, return `None` if no match found. Signature: `def extract_primary_deposit(step_text: str) -> Optional[str]:`. `Optional` is already imported from `typing` at top of bellows.py. **Change 3 — modify `post_verdict_request()` in `verdict.py` to call the new parser and write a `Deposit:` field.** Add a new parameter `step_text: str = ""` to the signature (default empty string for backward compatibility with any callers that don't pass it yet). After the existing `**Pause Reason Code:**` line in the content f-string and BEFORE the `**Gate Result Passed:**` line (as of Plan A's layout), write: `**Deposit:** {extract_primary_deposit(step_text) or "none"}\n`. Import `extract_primary_deposit` from `bellows` at the top of `verdict.py` — use `from bellows import extract_primary_deposit`. If that creates a circular import (verdict.py is already imported by bellows.py), instead copy the function body and regex constants into `verdict.py` directly and remove them from bellows.py. Check this before committing — grep for `import verdict` in bellows.py and decide accordingly. Whichever module owns the function, only ONE module should define it. **Change 4 — update both `post_verdict_request()` call sites in `bellows.py` to pass `step_text`.** The two call sites from Plan A are at the mid-plan pause (inside `while not is_final_step` loop) and the final-step pause (after the while loop). Both now receive `step_text=plan_text` as an additional keyword argument — `plan_text` is already in scope at both call sites (it's loaded at the top of `run_plan` via `plan_text = load_file(plan_path)`). To keep it simple, pass the full plan text at both sites and let `extract_primary_deposit` scan the whole thing — the regex patterns are step-agnostic. An optimization to scope-to-current-step is possible but out of scope for this plan; the simple approach is correct for this parser. **Verification as you go:** after making all code changes, run the targeted test suite: `cd bellows && python3 -m pytest tests/ -v 2>&1 | tee knowledge/qa/evidence/executable-bellows-verdict-schema-plan-b-2026-04-18/pytest_targeted_dev_sanity.txt`. Create the evidence directory with `mkdir -p` first. If any test fails that was passing after Plan A, stop and report. The Plan A suite had 48/48 verdict+bellows tests passing and 11 pre-existing runner test failures. Expected state after Plan B: same 11 runner failures (unrelated), 48+ verdict+bellows tests passing (new tests added in Step 2 QA, not this step). **Additional verification — manual parser smoke test.** Write a Python script that: (a) defines 5 test inputs, one per format cluster — cluster A string `"**Deposit:** \`bellows/knowledge/research/foo.md\`"`, cluster B string `"**Deposit dev log** to \`bellows/knowledge/development/bar.md\`"`, cluster B ALL-CAPS variant `"**WRITE THE QA REPORT** to \`bellows/knowledge/qa/baz.md\`"`, cluster C string `"Deposit QA report to \`bellows/knowledge/qa/qux.md\`"`, and a feedback-exclusion string `"Standard prompt feedback protocol → \`bellows/knowledge/research/agent-prompt-feedback.md\`"`; (b) calls `extract_primary_deposit()` on each; (c) asserts results: first four return the expected `.md` path, the feedback-exclusion returns `None`; (d) prints PASS/FAIL per case. Save to `bellows/knowledge/qa/evidence/executable-bellows-verdict-schema-plan-b-2026-04-18/manual_parser_smoke.py` and pipe stdout to `manual_parser_smoke.txt`. This is DEV-side validation, not the Rule 18 evidence for QA (QA will run a more comprehensive smoke test in Step 2). **Commit:** after all changes pass the DEV sanity test and manual smoke, commit `bellows.py` and `verdict.py` together with message `"feat(verdict): add Deposit field + extract_primary_deposit parser (Plan B)"`. Do NOT commit the evidence files — `knowledge/qa/evidence/` should be gitignored; verify with `git status` that evidence files are untracked before committing. If evidence files are tracked, commit them in a separate second commit with message `"test: Plan B evidence"`. **Deposit development log:** write a dev log to `bellows/knowledge/development/verdict-schema-plan-b-2026-04-18.md` using canonical Python file write pattern (`with open(path, "w") as f: f.write(content)` — NO heredoc, NO python3 -c). Dev log includes: one-bullet summary per Change 1–4, the exact feat commit hash (obtain via `git --no-pager log -1 --format=%H`), file:line ranges modified (grep for new function names and regex constants after committing), and an Output Receipt per template format. Cite the diagnostic file path (`bellows/knowledge/research/deposit-path-formats-2026-04-18.md`) in the Output Receipt's "Sources" section so future reviewers can find the authoritative design reference. **Feedback:** standard prompt feedback protocol → `bellows/knowledge/research/agent-prompt-feedback.md`.
>
> **STOP. Do NOT proceed to Step 2. Do NOT move the plan to Done. Wait for CEO confirmation before continuing.**

---
---

## STEP 2 — BELLOWS QA ANALYST

---

> Before starting, read `bellows/knowledge/development/verdict-schema-plan-b-2026-04-18.md` and check the Output Receipt status. If status is not Complete, stop and report the issue to the CEO before proceeding. **Skip specialist file and glossary reads — this is a mechanical verification task.** Verify the Plan B parser implementation is correct and covers every format cluster from the diagnostic. **FIRST — Deliverable Verification (Rule 17).** Read the dev log's "Files Created or Modified (Code)" list. Produce a verification table at the top of the QA report: `| Deliverable | Expected | Status (✅/❌) | Evidence |`. Mandatory deliverable checks: (1) `bellows.py` regex constants — grep for each constant name (`STRICT_DEPOSIT_RE`, `BOLD_NOUN_DEPOSIT_RE`, `INLINE_DEPOSIT_RE`, `FEEDBACK_EXCLUSION_RE`) and confirm each appears exactly once as a module-level assignment; deposit grep output to `bellows/knowledge/qa/evidence/executable-bellows-verdict-schema-plan-b-2026-04-18/grep_regex_constants.txt`. (2) `bellows.py` `BOLD_NOUN_DEPOSIT_RE` includes `re.IGNORECASE` — grep for `BOLD_NOUN_DEPOSIT_RE.*re.IGNORECASE` across the definition (may span multiple lines); deposit to `grep_ignorecase_flag.txt`. This is load-bearing for the ALL-CAPS variant — if this check fails, the ALL-CAPS smoke test in the next section will also fail. (3) `bellows.py` `extract_primary_deposit` function — grep for `def extract_primary_deposit` and confirm the function is defined with `Optional[str]` return type; deposit to `grep_extract_function.txt`. (4) `verdict.py` Deposit field in content template — grep for `**Deposit:**` (literal, as it appears in the f-string) and confirm it appears in the content f-string exactly once; deposit to `grep_deposit_field.txt`. (5) `verdict.py` import or copy of extractor — grep for either `from bellows import extract_primary_deposit` OR a local `def extract_primary_deposit` in `verdict.py`, and confirm exactly ONE of the two is present (not both, not neither); deposit to `grep_extractor_source.txt`. (6) `bellows.py` call site updates — grep for `post_verdict_request` in `bellows.py` and confirm both call sites now pass `step_text=plan_text` (or equivalent positional `plan_text` argument matching the new signature order); deposit to `grep_call_sites.txt`. For any ❌, attempt re-commit or re-create before proceeding; if unfixable, STOP and report to CEO. **SECOND — Targeted test run.** Run `cd bellows && python3 -m pytest tests/ -v 2>&1 | tee knowledge/qa/evidence/executable-bellows-verdict-schema-plan-b-2026-04-18/pytest_targeted.txt`. Confirm exit code 0 ignoring the 11 pre-existing runner test failures from Plan A (test_runner.py and test_runner_parser.py). New verdict+bellows tests should be 48/48+ passing. If any NEW test failure surfaces in verdict or bellows modules, investigate — if caused by the Plan B signature change (test mocks calling `post_verdict_request` without the new `step_text` parameter), update the test fixtures to pass empty string; otherwise flag as blocker. **THIRD — Comprehensive parser smoke test.** Write a Python script that tests `extract_primary_deposit` against every format cluster from the diagnostic. Each test case is a 2-tuple `(input_text, expected_result)`. Minimum 9 test cases: (a) cluster A — `"**Deposit:** \`freight-kb/knowledge/design/foo.md\`"` → `"freight-kb/knowledge/design/foo.md"`; (b) cluster A with interposed text — `"**Deposit:** Write the full schema blueprint to \`ai-career-digest/knowledge/architecture/bar.md\`"` → `"ai-career-digest/knowledge/architecture/bar.md"`; (c) cluster B bold-noun — `"**Deposit dev log** to \`bellows/knowledge/development/baz.md\`"` → `"bellows/knowledge/development/baz.md"`; (d) cluster B ALL-CAPS variant — `"**WRITE THE QA REPORT** to \`bellows/knowledge/qa/caps.md\`"` → `"bellows/knowledge/qa/caps.md"` (THIS IS THE re.IGNORECASE TEST — if it fails, Plan B ships broken); (e) cluster B Write variant — `"**Write QA report** to \`BrewBuddy/knowledge/qa/bb.md\`"` → `"BrewBuddy/knowledge/qa/bb.md"`; (f) cluster C inline prose — `"Deposit QA report to \`anvil/knowledge/qa/anv.md\`"` → `"anvil/knowledge/qa/anv.md"`; (g) cluster G inline prose "as" — `"deposit as \`forge/knowledge/research/forge.md\`"` → `"forge/knowledge/research/forge.md"`; (h) cluster H absolute path normalization — `"**Deposit:** QA report to \`/Users/marklehn/Desktop/GitHub/forge/knowledge/qa/abs.md\`"` → `"forge/knowledge/qa/abs.md"` (MUST normalize by splitting on `/Desktop/GitHub/`); (i) feedback-exclusion — `"Standard prompt feedback protocol → \`bellows/knowledge/research/agent-prompt-feedback.md\`"` → `None`; (j) no-match — `"This step has no primary deposit."` → `None`. For each case, assert the returned value equals the expected value; print PASS/FAIL per case with the input truncated to 80 chars; at the end print overall PASS if all cases passed, else FAIL with count. Save script to `bellows/knowledge/qa/evidence/executable-bellows-verdict-schema-plan-b-2026-04-18/e2e_parser_coverage.py` and pipe output to `e2e_parser_coverage.txt`. **FOURTH — End-to-end verdict write with Deposit field.** Write a second Python script that: (a) constructs a fake `plan_path`, `project_path`, `step_text` containing `"**Deposit findings** to \`bellows/knowledge/research/smoke-test.md\`"` somewhere in it; (b) calls `verdict.post_verdict_request(...)` with the new `step_text` parameter populated; (c) reads back the written file; (d) asserts that `**Deposit:** bellows/knowledge/research/smoke-test.md` appears exactly once in the output; (e) asserts that `**Deposit:** none` does NOT appear; (f) deletes the test file. Save to `e2e_verdict_deposit_field.py` and pipe to `e2e_verdict_deposit_field.txt`. If the assertion fails, that's a Critical ❌ — Plan B's integration with verdict.py is broken. **FIFTH — None-path smoke test.** Third Python script: construct `step_text = "This step has no deposits. Just commits code."`, call `post_verdict_request`, read back, assert `**Deposit:** none` appears exactly once (lowercase `none` per the Plan B spec). Save to `e2e_verdict_none_path.py` and pipe to `e2e_verdict_none_path.txt`. **WRITE THE QA REPORT** to `bellows/knowledge/qa/verdict-schema-plan-b-2026-04-18.md` using canonical Python file write pattern — NO heredoc. Report includes: (a) deliverable verification table with per-row evidence paths, (b) targeted test summary (pass/fail counts, exit code, note about 11 pre-existing runner failures), (c) parser coverage smoke test per-case results, (d) e2e verdict-write and none-path results, (e) overall status. **Final — PROJECT_STATUS.md update.** Read the current state of `bellows/PROJECT_STATUS.md` before writing the str_replace instruction — identify the Plan A milestone bullet as the anchor. Use `Desktop Commander:edit_block` with the verbatim Plan A milestone line as `old_string` and that line plus `\n- 2026-04-18: Plan B verdict schema — added `Deposit:` field to verdict request files via `extract_primary_deposit()` parser. Handles 95%+ of corpus formats (clusters A/B/C/D/F/G/H) plus absolute-path normalization plus ALL-CAPS Write variant via re.IGNORECASE. Completes Planner Rule 22 unblock alongside Plan A.` as `new_string`. Do NOT append blindly. If the Plan A anchor has moved since today, re-read and pick the most recent milestone line as the new anchor. **Feedback:** standard prompt feedback protocol → `bellows/knowledge/research/agent-prompt-feedback.md`. **Final commit:** `cd bellows && git add knowledge/qa/verdict-schema-plan-b-2026-04-18.md knowledge/qa/evidence/executable-bellows-verdict-schema-plan-b-2026-04-18/ knowledge/development/verdict-schema-plan-b-2026-04-18.md PROJECT_STATUS.md knowledge/research/agent-prompt-feedback.md && git commit -m "qa: verdict schema plan B — parser coverage + integration verified"`. **Then move-to-Done:** `import shutil; shutil.move("bellows/knowledge/decisions/in-progress-executable-bellows-verdict-schema-plan-b-2026-04-18.md", "bellows/knowledge/decisions/Done/executable-bellows-verdict-schema-plan-b-2026-04-18.md")`. The move-to-Done is the absolute last operation (Rule 23c). **Rule 20 — Mandatory QA Self-Check (run AFTER writing the QA report, BEFORE the final commit and move-to-Done):**
>
> ```python
> # Rule 20 — Mandatory QA Self-Check
> import os, sys
> plan_slug = "executable-bellows-verdict-schema-plan-b-2026-04-18"
> qa_report_path = "bellows/knowledge/qa/verdict-schema-plan-b-2026-04-18.md"
> evidence_dir = f"bellows/knowledge/qa/evidence/{plan_slug}/"
> required_evidence_files = [
>     "grep_regex_constants.txt",
>     "grep_ignorecase_flag.txt",
>     "grep_extract_function.txt",
>     "grep_deposit_field.txt",
>     "grep_extractor_source.txt",
>     "grep_call_sites.txt",
>     "pytest_targeted.txt",
>     "e2e_parser_coverage.py",
>     "e2e_parser_coverage.txt",
>     "e2e_verdict_deposit_field.py",
>     "e2e_verdict_deposit_field.txt",
>     "e2e_verdict_none_path.py",
>     "e2e_verdict_none_path.txt",
> ]
> hedging_keywords = ["pending", "inferred", "extrapolated", "estimated", "approximate", "skipped", "assumed", "close enough", "should pass", "would pass", "not run"]
> POSITIVE_STATUS_TOKENS = ["✅", "OK", "PASS", "[x]", "done", "complete", "verified"]
>
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
>
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
> Paste the self-check's literal stdout into the QA report at the end. If the self-check prints `FAILED`, STOP — do not update PROJECT_STATUS.md, do not move to Done, report to CEO. If `PASSED`, proceed with PROJECT_STATUS.md update + final commit + move-to-Done in that order (Rule 23c).
