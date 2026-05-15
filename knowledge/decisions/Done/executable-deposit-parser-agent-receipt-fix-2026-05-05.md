# Bellows — Deposit Parser Agent-Receipt Path Extraction Fix

**Date:** 2026-05-05 | **Tier:** Small | **Test Scope:** full-suite | **Execution:** Step 1 (Bellows Developer) → Step 2 (Bellows QA)

## How to Run This Plan

Paste the bootstrap prompt into Claude Code. The agent reads the full plan and executes Step 1 ONLY. After Step 1, the agent STOPS. Bellows dispatches Step 2 via verdict-continue once the Planner Rule 22 pass on Step 1 is recorded.

**Bootstrap:**

```
Read the plan at bellows/knowledge/decisions/executable-deposit-parser-agent-receipt-fix-2026-05-05.md. Execute Step 1 ONLY. After completing Step 1, STOP.
```

---
---

## STEP 1 — Bellows Developer

---

> **FIRST — before doing anything else, claim this plan:** `import shutil; shutil.move("bellows/knowledge/decisions/executable-deposit-parser-agent-receipt-fix-2026-05-05.md", "bellows/knowledge/decisions/in-progress-executable-deposit-parser-agent-receipt-fix-2026-05-05.md")`. **You are the Bellows Developer.** Read your specialist file at `bellows/agents/BELLOWS_DEVELOPER.md`. **Skip domain glossary read — bellows has no glossary; this is a code fix with new unit tests, no domain interpretation needed.** **Context — read this BEFORE editing.** The diagnostic at `bellows/knowledge/research/deposit-parser-prose-failure-diagnosis-2026-05-05.md` traced the `deposit_exists` false-positive root cause to the agent-receipt parser at `bellows/gates.py:157` inside `_gate_deposit_exists`. The current line uses `.strip("`")` which only removes boundary backticks. When agents follow the standard Output Receipt template format (a backtick-quoted path followed by em-dash followed by description text), the leading backtick is stripped but the trailing backtick is buried inside the line, so the extracted path includes the trailing backtick + description text and never resolves on disk. Fix: regex-extract the first backtick-quoted span if present, fall back to current `.strip("`")` behavior if no backticks. **Task — three sub-tasks: (1) apply the fix at gates.py:157, (2) add unit tests in test_gates.py, (3) close the BACKLOG entry that this fix resolves.** **Sub-task 1 — gates.py:157 fix.** First read `bellows/gates.py` lines 150-170 with `Filesystem:read_text_file` to capture the verbatim current state of the line. The current line is at 12-space indentation and reads exactly: `            path = line[2:].strip().strip("`")`. Use `Desktop Commander:edit_block` with that line as `old_string` and the following two-line replacement as `new_string`, preserving indentation:
>
> ```
>             m = re.match(r'`([^`]+)`', line[2:].strip())
>             path = m.group(1) if m else line[2:].strip().strip("`")
> ```
>
> Verify post-edit by re-reading lines 150-170: confirm both new lines are present, indentation is 12 spaces on both, and the regex literal is syntactically valid. **Sub-task 2 — unit tests in test_gates.py.** Add four new test functions at the END of `bellows/tests/test_gates.py`. Read the file first to capture the verbatim final non-blank line as `edit_block` anchor. Each test creates a real file under `/tmp/` so `_resolve_deposit_path` returns True, builds a `parsed` dict copying `_clean_parsed()` and overriding `result_text` with a synthetic Output Receipt section, calls `gates.check(parsed, PLAN_TEXT, 1, "/tmp")`, and asserts the gate passed (or for the negative case, asserts the gate failed). The four tests:
>
> 1. `test_deposit_exists_extracts_path_from_backtick_with_description` — the regression test for the actual bug. Receipt line format: `- ` followed by backtick + path + backtick + ` — description`. Asserts `result["passed"] is True` and no `deposit_exists` failure.
> 2. `test_deposit_exists_extracts_path_from_backtick_only` — backtick-quoted path with nothing after. Receipt line format: `- ` followed by backtick + path + backtick. Asserts gate passes.
> 3. `test_deposit_exists_extracts_path_from_bare_path_without_backticks` — no backticks at all. Receipt line format: `- ` followed by bare path. Asserts gate passes (fallback path).
> 4. `test_deposit_exists_still_fails_on_genuinely_missing_path_with_new_format` — backtick-with-description format pointing to `/nonexistent/path/that/does/not/exist.md`. Asserts `result["passed"] is False` AND a `deposit_exists` failure exists in `result["failures"]`. This locks in that the fix didn't accidentally turn the gate into a no-op.
>
> The four tests can share a small helper that builds the `parsed` dict from a single `### Files Deposited` line. **Sub-task 3 — close the BACKLOG entry.** Read `bellows/knowledge/BACKLOG.md` and locate the Open entry beginning `- 2026-05-05: deposit-parser captures backtick-wrapped paths from step prose with trailing description fragments as literal deposit paths.` (it's the second entry in the Open section). Remove this entry from Open. Add a corresponding Closed entry at the top of the Closed section (immediately after the `## Closed` header line and its blank line, BEFORE the existing top Closed entry which begins `- **Closed 2026-05-05:** BACKLOG `2026-04-30: scope_check diff-collision`). New Closed entry — single bullet, single line:
>
> ```
> - **Closed 2026-05-05:** BACKLOG `2026-05-05: deposit-parser captures backtick-wrapped paths from step prose`. Diagnostic at `bellows/knowledge/research/deposit-parser-prose-failure-diagnosis-2026-05-05.md` overturned the original entry's hypothesis — root cause was in agent-receipt parser at `gates.py:157` inside `_gate_deposit_exists` (not plan-text parser as the entry hypothesized). Fix: regex extraction at gates.py:157 plus fallback to legacy `.strip("`")` for lines without backticks. +4 unit tests in `test_gates.py`. Reference: `executable-deposit-parser-agent-receipt-fix-2026-05-05`, diagnostic findings file.
> ```
>
> Use `Filesystem:read_text_file` to read the entire BACKLOG.md, then `Filesystem:write_file` to write back the modified content. Single-rewrite is cleaner than two `edit_block` operations for a long-bullet move. Verify post-write by reading the file again: the string `2026-05-05: deposit-parser captures backtick-wrapped paths from step prose` must appear EXACTLY ONCE in the file (in the new Closed entry only — original Open entry fully removed). Also verify the Open section's first entry is now `- 2026-05-05: bellows-self parallel/concurrent activity exposure (known constraint`. **Output receipt and feedback.** Standard prompt feedback protocol → `bellows/knowledge/research/agent-prompt-feedback.md`. **Final commit (in `cd /Users/marklehn/Desktop/GitHub/bellows`):** `git --no-pager add gates.py tests/test_gates.py knowledge/BACKLOG.md knowledge/research/agent-prompt-feedback.md && git --no-pager commit -m "fix(gates): regex-extract path from agent receipt — closes deposit-parser backtick-prose false positive"`.
>
> **Deposits:**
> - `bellows/gates.py`
> - `bellows/tests/test_gates.py`
> - `bellows/knowledge/BACKLOG.md`
> - `bellows/knowledge/research/agent-prompt-feedback.md`
>
> **STOP. Do NOT proceed to Step 2. Do NOT move the plan to Done. Wait for CEO confirmation before continuing.**

---
---

## STEP 2 — Bellows QA

---

> **Before starting, read `bellows/knowledge/decisions/in-progress-executable-deposit-parser-agent-receipt-fix-2026-05-05.md` Step 1's Output Receipt status field. If status is not Complete, stop and report the issue to the CEO before proceeding.** **You are the Bellows QA agent.** Read your specialist file at `bellows/agents/BELLOWS_QA.md`. **Skip domain glossary read — gates.py code change + test regression + full suite, no domain interpretation needed.** **FIRST — Deliverable Verification (Rule 17).** Read Step 1's Output Receipt "Files Created or Modified (Code)" list. For EVERY listed file, verify it exists with the described change.
>
> (a) `bellows/gates.py` fix landed. Run `cd /Users/marklehn/Desktop/GitHub/bellows && grep -n "re.match" gates.py` and pipe to `bellows/knowledge/qa/evidence/executable-deposit-parser-agent-receipt-fix-2026-05-05/grep_gates_fix.txt`. Expected: at least one match in the agent-receipt-parsing region of `_gate_deposit_exists` (around line 157).
>
> (b) `bellows/tests/test_gates.py` has the 4 new test functions. Run `cd /Users/marklehn/Desktop/GitHub/bellows && grep -cE "(test_deposit_exists_extracts_path_from_backtick_with_description|test_deposit_exists_extracts_path_from_backtick_only|test_deposit_exists_extracts_path_from_bare_path_without_backticks|test_deposit_exists_still_fails_on_genuinely_missing_path_with_new_format)" tests/test_gates.py` and pipe to `evidence/grep_new_tests.txt`. Expected: count is exactly 4.
>
> (c) `bellows/knowledge/BACKLOG.md` Open entry removed and Closed entry added. Run three checks:
>
> - `cd /Users/marklehn/Desktop/GitHub/bellows && grep -c "2026-05-05: deposit-parser captures backtick-wrapped paths from step prose" knowledge/BACKLOG.md` → pipe to `evidence/grep_backlog_count.txt`. Expected: exactly 1 (only the new Closed entry references the original entry's title).
> - `cd /Users/marklehn/Desktop/GitHub/bellows && grep -n "Closed 2026-05-05.*deposit-parser captures backtick-wrapped paths" knowledge/BACKLOG.md` → pipe to `evidence/grep_backlog_closed.txt`. Expected: exactly 1 match in the Closed section.
> - `cd /Users/marklehn/Desktop/GitHub/bellows && awk '/^## Open/,/^## Closed/' knowledge/BACKLOG.md | grep -c "deposit-parser captures backtick-wrapped paths"` → pipe to `evidence/grep_open_section.txt`. Expected: count is 0.
>
> If ANY deliverable check fails, attempt to flag for re-fix or stop and report to CEO. Do NOT proceed to test execution if any deliverable verification fails.
>
> **Test execution — full suite per Rule 21 declared scope.** Run `cd /Users/marklehn/Desktop/GitHub/bellows && python -m pytest tests/ -v 2>&1 | tee bellows/knowledge/qa/evidence/executable-deposit-parser-agent-receipt-fix-2026-05-05/pytest_full.txt`. Expected: ALL tests pass except the known pre-existing `test_run_step_timeout` failure (if it still exists; recent PROJECT_STATUS notes suggest it may have been removed). The 4 new tests must all pass. ANY new test failure is a Critical fix-broken finding; ANY previously-passing test now failing is a Critical regression. Capture the literal pytest output.
>
> **Targeted run for evidence redundancy.** Also run `cd /Users/marklehn/Desktop/GitHub/bellows && python -m pytest tests/test_gates.py -v 2>&1 | tee bellows/knowledge/qa/evidence/executable-deposit-parser-agent-receipt-fix-2026-05-05/pytest_targeted.txt`. Expected: 100% pass rate on test_gates.py.
>
> **Behavioral smoke — verify the fix works against a realistic agent receipt.** Write a small Python script under `/tmp/` that imports `gates` from the bellows directory (use `sys.path.insert(0, "/Users/marklehn/Desktop/GitHub/bellows")` then `import gates`), builds a `parsed` dict simulating an actual agent receipt with the standard format (a `### Files Deposited` section containing one line in the form `- `gates.py` — agent receipt parser fix`), runs `gates.check(parsed, plan_text, 1, "/Users/marklehn/Desktop/GitHub/bellows")`, and asserts `result["passed"] is True` and no `deposit_exists` failures appear in `result["failures"]`. Print PASSED or FAILED with details. Pipe stdout+stderr to `evidence/behavioral_smoke.txt`. Expected: smoke prints PASSED with zero deposit_exists failures.
>
> **Build the QA report** at `bellows/knowledge/qa/deposit-parser-agent-receipt-fix-qa-2026-05-05.md` with a verification table `| # | Verification | Expected | Status (✅/❌) | Evidence |` covering: (1) gates.py fix landed, (2) 4 new test functions present, (3) BACKLOG.md count of original-entry-title is exactly 1 (in Closed), (4) BACKLOG.md new Closed entry exists, (5) Open section no longer contains original entry, (6) full pytest suite passes (cite pytest_full.txt), (7) targeted pytest passes (cite pytest_targeted.txt), (8) behavioral smoke confirms fix works (cite behavioral_smoke.txt). After the table, run the Rule 20 self-check (canonical block from PLANNER_TEMPLATE Rule 20) using:
>
> - `plan_slug = "executable-deposit-parser-agent-receipt-fix-2026-05-05"`
> - `qa_report_path = "bellows/knowledge/qa/deposit-parser-agent-receipt-fix-qa-2026-05-05.md"`
> - `evidence_dir = f"bellows/knowledge/qa/evidence/{plan_slug}/"`
> - `required_evidence_files = ["grep_gates_fix.txt", "grep_new_tests.txt", "grep_backlog_count.txt", "grep_backlog_closed.txt", "grep_open_section.txt", "pytest_full.txt", "pytest_targeted.txt", "behavioral_smoke.txt"]`
>
> Include the literal stdout of the self-check in the QA report. If self-check prints SELF-CHECK FAILED, STOP — do not proceed to PROJECT_STATUS update or commit; report the failure to the CEO.
>
> **Update PROJECT_STATUS.md.** If self-check passed, append a new completed milestone entry to the top of the Completed section. Read `bellows/PROJECT_STATUS.md` first, anchor the edit against the current top entry beginning `- 2026-05-05: **Session wrap deposits shipped.**`. Use `Desktop Commander:edit_block` with the verbatim current top entry as `old_string` and the following composite as `new_string`: the new entry, then a literal newline, then the verbatim current top entry. New entry text — single bullet, single line:
>
> ```
> - 2026-05-05: **Deposit-parser agent-receipt false-positive fix shipped + BACKLOG closure.** Diagnostic at `bellows/knowledge/research/deposit-parser-prose-failure-diagnosis-2026-05-05.md` traced the `deposit_exists` false-positive at `gates.py:157` to a `.strip("`")` call that only stripped boundary backticks, mangling agent-receipt paths formatted with the standard Output Receipt template. Fix replaced the line with regex extraction (`re.match` against a backtick-quoted span) plus fallback to legacy strip behavior for lines without backticks. +4 unit tests in `test_gates.py`. Full pytest suite passed; behavioral smoke confirmed the fix end-to-end. BACKLOG entry `2026-05-05: deposit-parser captures backtick-wrapped paths from step prose` closed in the same plan. REMINDER: restart Bellows daemon to load fix. Reference: `executable-deposit-parser-agent-receipt-fix-2026-05-05`.
> ```
>
> **Standard prompt feedback protocol** → `bellows/knowledge/research/agent-prompt-feedback.md`. **Final commit. Order: feedback append → final commit, per Rule 23.** Run `cd /Users/marklehn/Desktop/GitHub/bellows && git --no-pager add knowledge/qa/deposit-parser-agent-receipt-fix-qa-2026-05-05.md knowledge/qa/evidence/executable-deposit-parser-agent-receipt-fix-2026-05-05/ PROJECT_STATUS.md knowledge/research/agent-prompt-feedback.md && git --no-pager commit -m "docs(qa): deposit-parser agent-receipt fix verification 2026-05-05"`.
>
> **Do NOT move the plan to Done.** The Planner performs the terminal Done/ move after Rule 22 verification on the QA report.
>
> **Deposits:**
> - `bellows/knowledge/qa/deposit-parser-agent-receipt-fix-qa-2026-05-05.md`
> - `bellows/knowledge/qa/evidence/executable-deposit-parser-agent-receipt-fix-2026-05-05/grep_gates_fix.txt`
> - `bellows/knowledge/qa/evidence/executable-deposit-parser-agent-receipt-fix-2026-05-05/grep_new_tests.txt`
> - `bellows/knowledge/qa/evidence/executable-deposit-parser-agent-receipt-fix-2026-05-05/grep_backlog_count.txt`
> - `bellows/knowledge/qa/evidence/executable-deposit-parser-agent-receipt-fix-2026-05-05/grep_backlog_closed.txt`
> - `bellows/knowledge/qa/evidence/executable-deposit-parser-agent-receipt-fix-2026-05-05/grep_open_section.txt`
> - `bellows/knowledge/qa/evidence/executable-deposit-parser-agent-receipt-fix-2026-05-05/pytest_full.txt`
> - `bellows/knowledge/qa/evidence/executable-deposit-parser-agent-receipt-fix-2026-05-05/pytest_targeted.txt`
> - `bellows/knowledge/qa/evidence/executable-deposit-parser-agent-receipt-fix-2026-05-05/behavioral_smoke.txt`
> - `bellows/PROJECT_STATUS.md`
> - `bellows/knowledge/research/agent-prompt-feedback.md`
