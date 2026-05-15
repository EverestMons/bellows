# Bellows — Remove Hardcoded `is_diagnostic` Step-Count Override
**Date:** 2026-05-03 | **Tier:** Small | **Test Scope:** targeted | **Execution:** Step 1 (BELLOWS DEVELOPER) → Step 2 (BELLOWS DEVELOPER QA)

## How to Run This Plan

Paste the bootstrap prompt into Claude Code. The agent reads the full plan file and executes Step 1 ONLY. After completing Step 1, the agent STOPS and waits for CEO confirmation ("ok") before proceeding to Step 2. The Planner moves the plan to Done after Rule 22 verification passes.

**Bootstrap prompt:**
```
Read the plan at bellows/knowledge/decisions/executable-remove-is-diagnostic-step-override-2026-05-03.md. Execute Step 1 ONLY. After completing Step 1, STOP and wait for my confirmation. Do NOT proceed to Step 2 or move the plan to Done.
```

**Background context (read before executing):** Today's diagnostic `diagnostic-extract-total-steps-undercount-2026-05-03` (closed; findings at `bellows/knowledge/research/extract-total-steps-undercount-2026-05-03.md`) identified the cause of multi-step diagnostic plans being dispatched as 1-step. The cause is NOT a regex bug — `extract_total_steps()` works correctly. The cause is hardcoded `is_diagnostic` overrides at `bellows.py:228-229` and `bellows.py:690-692` that unconditionally set `total_steps = 1` for any plan whose filename starts with `"diagnostic-"`. This was likely a safety net from when diagnostics were single-step by convention, but multi-step diagnostics are now legitimate (today's investigation chain produced three of them). The override is now actively wrong.

**Audit confirmed Option A is safe:** Every diagnostic plan in `bellows/knowledge/decisions/Done/` uses `## STEP N — <agent>` headers (54 diagnostics + 3 parallel-1-diagnostic plans, all checked). No legacy bare-diagnostic plans exist that would dispatch as 0-step after the override is removed. Removing the override is safe.

**This plan is an `executable-` prefix, not a `diagnostic-` prefix.** Bellows will correctly count its multi-step structure (the override does not fire on executables). The two-step plan will dispatch as a 2-step plan.

---
---

## STEP 1 — BELLOWS DEVELOPER

---

> **STOP REMINDER (TOP):** This is the implementation step. Do NOT execute Step 2 (QA verification) work even though its prompt exists below. After completing this step, STOP and wait for CEO confirmation. Do NOT move the plan to Done — the Planner performs the terminal move after Rule 22 verification passes.
>
> **FIRST — before doing anything else, claim this plan:** `import shutil; shutil.move("bellows/knowledge/decisions/executable-remove-is-diagnostic-step-override-2026-05-03.md", "bellows/knowledge/decisions/in-progress-executable-remove-is-diagnostic-step-override-2026-05-03.md")`.
>
> You are the Bellows Developer. Read your specialist file at `bellows/agents/BELLOWS_DEVELOPER.md` first. Skip glossary read — this is a small targeted fix.
>
> **Task: remove the hardcoded `is_diagnostic` step-count override at two locations in `bellows.py`, replace with a code comment documenting the prior assumption and why it's removed, run the existing test suite as regression check, commit.**
>
> **Phase 1 — Edit `bellows.py:228-229`.** Read the current code at lines 226-229 (or whatever range surrounds the override; use the diagnostic findings file at `bellows/knowledge/research/extract-total-steps-undercount-2026-05-03.md` Phase 4 for the exact location). The current code looks approximately like:
>
> ```python
> total_steps = extract_total_steps(metadata_text)
> is_diagnostic = os.path.basename(plan_path).startswith("diagnostic-")
> if is_diagnostic:
>     total_steps = 1
> ```
>
> Remove the `if is_diagnostic: total_steps = 1` block. Keep the `is_diagnostic` variable definition if it is used elsewhere in `run_plan` for branching (check via grep before deleting); if it's only used for the removed override, remove it too. Replace the removed lines with a comment explaining the prior assumption:
>
> ```python
> # NOTE 2026-05-03: Removed hardcoded `if is_diagnostic: total_steps = 1` override.
> # Multi-step diagnostics are now legitimate (e.g., investigation chains with multiple
> # phases). extract_total_steps() returns the correct count from `## STEP N` headers
> # in the plan file regardless of filename prefix. See diagnostic findings at
> # bellows/knowledge/research/extract-total-steps-undercount-2026-05-03.md.
> ```
>
> Use `Desktop Commander:edit_block` with exact `old_string`/`new_string` pairs per Rule 24.
>
> **Phase 2 — Edit `bellows.py:690-692`.** Same pattern at the second location (continue-verdict handler). Current code looks approximately like:
>
> ```python
> is_diag = original_name.startswith("diagnostic-")
> if is_diag:
>     total_steps_c = 1
> else:
>     # ... extract_total_steps call
> ```
>
> Remove the `is_diag` derivation and the `if is_diag: total_steps_c = 1` block. The else-branch becomes the unconditional path. Replace with a brief comment referencing the diagnostic findings file (a one-liner is sufficient at this site since the primary explanation is already at the first call site).
>
> **Phase 3 — Run the existing test suite.** From `bellows/` directory: `cd /Users/marklehn/Desktop/GitHub/bellows && python -m pytest tests/ -v 2>&1 | tee /tmp/pytest-after-removal.txt`. Report the pass/fail count. The expected outcome: all currently-passing tests continue to pass. If any test fails that wasn't failing before, document the failure and stop — do NOT push through; the Planner will assess.
>
> **Phase 4 — Commit.** Single commit with a descriptive message: `cd /Users/marklehn/Desktop/GitHub/bellows && git --no-pager add bellows.py && git --no-pager commit -m "fix(bellows): remove hardcoded is_diagnostic step-count override"`.
>
> **Phase 5 — Dev log deposit.** Write a brief development log to `bellows/knowledge/development/remove-is-diagnostic-override-dev-log-2026-05-03.md` documenting: (a) the two file:line locations modified, (b) the test result counts (before vs after — if the test count is unchanged, state so), (c) the commit SHA. Use the canonical Python file write pattern: `with open("bellows/knowledge/development/remove-is-diagnostic-override-dev-log-2026-05-03.md", "w") as f: f.write(content)`. Commit the dev log: `cd /Users/marklehn/Desktop/GitHub/bellows && git --no-pager add knowledge/development/remove-is-diagnostic-override-dev-log-2026-05-03.md && git --no-pager commit -m "docs: dev log for is_diagnostic override removal"`.
>
> **Constraints:**
> - Do NOT add new tests — that's done as part of Step 2 (QA) verification, not implementation.
> - Do NOT add the `## STEP N` warning logic the diagnostic findings mention as future work — out of scope. This plan removes ONE thing.
> - Do NOT modify `runner.py`, `gates.py`, `verdict.py`, `parser.py`, or any other module. The fix is two locations in `bellows.py` only.
> - Do NOT use heredoc syntax for any file write (banned per PLANNER_TEMPLATE Rule 5). Use canonical `with open() as f: f.write(content)` Python pattern or `Desktop Commander:edit_block` for surgical edits.
>
> Standard prompt feedback protocol → `bellows/knowledge/research/agent-prompt-feedback.md`.
>
> **Deposits:**
> - `bellows/knowledge/development/remove-is-diagnostic-override-dev-log-2026-05-03.md`
>
> **STOP REMINDER (BOTTOM):** Step 1 is COMPLETE when (a) both `bellows.py` overrides are removed with replacement comment, (b) test suite passes with no new failures, (c) commit landed, (d) dev log deposited and committed. Do NOT execute Step 2 (QA verification). Do NOT move the plan to Done. Wait for CEO confirmation before any further action.

---
---

## STEP 2 — BELLOWS DEVELOPER (QA)

---

> Before starting, read `bellows/knowledge/development/remove-is-diagnostic-override-dev-log-2026-05-03.md` and check the Output Receipt status. If status is not Complete, stop and report the issue to the CEO before proceeding.
>
> **STOP REMINDER (TOP):** This is the QA verification step. Do NOT modify production code. Do NOT move the plan to Done — the Planner performs the terminal move after Rule 22 verification passes.
>
> You are the Bellows Developer (acting as QA for this plan). Read your specialist file at `bellows/agents/BELLOWS_DEVELOPER.md` first. Skip glossary read.
>
> **Task: verify Step 1's deliverables exist with the expected content, run the test suite as regression check, run the Rule 20 mandatory self-check, write the QA report.**
>
> **Phase 1 — Deliverable verification (Rule 17).** Read Step 1's dev log at `bellows/knowledge/development/remove-is-diagnostic-override-dev-log-2026-05-03.md` to identify the exact files modified. For EACH listed deliverable, verify it exists with the expected change:
>
> 1. **`bellows.py:~228-229` override removed.** Run: `grep -n "if is_diagnostic" /Users/marklehn/Desktop/GitHub/bellows/bellows.py | tee /Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/evidence/remove-is-diagnostic-override-2026-05-03/grep_is_diagnostic.txt`. Expected: zero matches (or one match in a comment line, no `if` statement). If the grep returns an active `if is_diagnostic:` line, the override was not removed — flag as ❌ Critical.
> 2. **`bellows.py:~690-692` override removed.** Run: `grep -n "if is_diag" /Users/marklehn/Desktop/GitHub/bellows/bellows.py | tee /Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/evidence/remove-is-diagnostic-override-2026-05-03/grep_is_diag.txt`. Expected: zero matches.
> 3. **Replacement comment present at first removal site.** Run: `grep -n "Removed hardcoded.*is_diagnostic" /Users/marklehn/Desktop/GitHub/bellows/bellows.py | tee /Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/evidence/remove-is-diagnostic-override-2026-05-03/grep_replacement_comment.txt`. Expected: at least one match (the comment Step 1's prompt specified).
> 4. **Commit landed.** Run: `cd /Users/marklehn/Desktop/GitHub/bellows && git --no-pager log --oneline -5 | tee /Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/evidence/remove-is-diagnostic-override-2026-05-03/git_log.txt`. Expected: top commit is the override-removal commit.
>
> Produce a verification table: `| Deliverable | Expected | Status (✅/❌) | Evidence |`. Cite the evidence file paths in the Evidence column. Any ❌ item is a Critical finding that blocks the plan from closing — do NOT proceed to subsequent phases.
>
> **Phase 2 — Test regression check.** From `bellows/` directory: `cd /Users/marklehn/Desktop/GitHub/bellows && python -m pytest tests/ -v 2>&1 | tee /Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/evidence/remove-is-diagnostic-override-2026-05-03/pytest_targeted.txt`. Compare pass/fail counts to Step 1's dev log baseline. Expected: same pass/fail counts (or better — if any previously-failing test now passes due to the fix, document that as an unexpected positive).
>
> **Phase 3 — Behavioral spot-check.** Run a quick functional test of `extract_total_steps` and the surrounding logic against a known multi-step diagnostic plan. Write a small Python script via canonical pattern (NOT heredoc, NOT `python3 -c "..."`):
>
> 1. Write the script to `/tmp/spot_check_extract_total_steps.py` using `with open() as f: f.write(content)`.
> 2. The script imports `extract_total_steps` from `bellows.bellows` and runs it against the live content of `bellows/knowledge/decisions/Done/diagnostic-worktree-implementation-surface-2026-05-03.md` (a known 3-step diagnostic).
> 3. Print the returned count.
> 4. Then exercise the dispatch path that previously had the override: simulate what `run_plan` would compute for `total_steps` given a diagnostic-prefixed plan with 3 step headers. The expected outcome: 3 (not 1).
> 5. Run the script: `python /tmp/spot_check_extract_total_steps.py 2>&1 | tee /Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/evidence/remove-is-diagnostic-override-2026-05-03/spot_check.txt`.
> 6. Verify the output shows count=3 for the multi-step diagnostic.
> 7. Cleanup: `rm /tmp/spot_check_extract_total_steps.py`.
>
> If the spot-check returns count=1 instead of count=3, the override is still firing somewhere — flag as ❌ Critical.
>
> **Phase 4 — Write the QA report.** Deposit to `bellows/knowledge/qa/remove-is-diagnostic-override-qa-2026-05-03.md`. Include: (a) Phase 1 deliverable verification table with evidence file paths cited; (b) Phase 2 test regression result with pass/fail counts; (c) Phase 3 behavioral spot-check result; (d) Output Receipt with Status; (e) the Rule 20 self-check stdout output appended at the end. Use canonical Python file write pattern.
>
> **Phase 5 — Update PROJECT_STATUS.md.** Add a completed milestone entry summarizing this plan's changes (one short bullet point referencing the override removal and the diagnostic chain). Use `Desktop Commander:edit_block` with exact anchor (the existing line above the Completed Milestones list).
>
> **Phase 6 — Mandatory Rule 20 self-check.** Run the standard self-check Python block at the end of this step. Required evidence files (must all be present in the evidence directory): `grep_is_diagnostic.txt`, `grep_is_diag.txt`, `grep_replacement_comment.txt`, `git_log.txt`, `pytest_targeted.txt`, `spot_check.txt`. Plan slug: `executable-remove-is-diagnostic-step-override-2026-05-03`. QA report path: `bellows/knowledge/qa/remove-is-diagnostic-override-qa-2026-05-03.md`. Include the literal stdout of the self-check in the QA report.
>
> ```python
> # Rule 20 — Mandatory QA Self-Check
> import os, sys
> plan_slug = "executable-remove-is-diagnostic-step-override-2026-05-03"
> qa_report_path = "bellows/knowledge/qa/remove-is-diagnostic-override-qa-2026-05-03.md"
> evidence_dir = f"bellows/knowledge/qa/evidence/{plan_slug}/"
> required_evidence_files = [
>     "grep_is_diagnostic.txt",
>     "grep_is_diag.txt",
>     "grep_replacement_comment.txt",
>     "git_log.txt",
>     "pytest_targeted.txt",
>     "spot_check.txt",
> ]
> hedging_keywords = ["pending", "inferred", "extrapolated", "estimated", "approximate", "skipped", "assumed", "close enough", "should pass", "would pass", "not run"]
> POSITIVE_STATUS_TOKENS = ["✅", "OK", "PASS", "done", "complete", "verified"]
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
> If self-check FAILS, the agent STOPS — does NOT update PROJECT_STATUS.md, does NOT move the plan to Done, reports the failure to the CEO and waits.
>
> **Phase 7 — Final commit.** After QA report and PROJECT_STATUS.md edit are deposited, single final commit: `cd /Users/marklehn/Desktop/GitHub/bellows && git --no-pager add knowledge/qa/remove-is-diagnostic-override-qa-2026-05-03.md knowledge/qa/evidence/remove-is-diagnostic-override-2026-05-03/ PROJECT_STATUS.md && git --no-pager commit -m "qa: verify is_diagnostic override removal"`.
>
> Standard prompt feedback protocol → `bellows/knowledge/research/agent-prompt-feedback.md`.
>
> **Deposits:**
> - `bellows/knowledge/qa/remove-is-diagnostic-override-qa-2026-05-03.md`
> - `bellows/knowledge/qa/evidence/executable-remove-is-diagnostic-step-override-2026-05-03/` (six evidence files per Rule 20 self-check)
>
> **STOP.** Do NOT move this plan to Done/. Per the disable-auto-close model, the Planner performs the terminal move after Rule 22 verification passes.
