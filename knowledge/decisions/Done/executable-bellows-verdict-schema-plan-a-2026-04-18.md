# Bellows — verdict.py Schema Additions (Plan A)
**Date:** 2026-04-18 | **Tier:** Small | **Test Scope:** targeted | **Execution:** Step 1 (DEV) → Step 2 (QA)

## CEO Context

Test Scope: targeted — changes are scoped to `verdict.py` + two call sites in `bellows.py`. No cross-module logic changes. Cross-bucket regression risk is low. Plan B (deposit-path extraction) is the one that will warrant full-suite because the parser logic has real ripple potential.

## How to Run This Plan

Paste the bootstrap prompt into Claude Code. The agent reads the full plan file and executes Step 1 ONLY. After completing Step 1, STOP and wait for CEO confirmation ("ok") before proceeding to Step 2. The agent must never skip steps, auto-chain, or move the plan to Done without completing all steps including QA.

**Bootstrap:**
```
Read the plan at bellows/knowledge/decisions/executable-bellows-verdict-schema-plan-a-2026-04-18.md. Execute Step 1 ONLY. After completing Step 1, STOP and wait for my confirmation. Do NOT proceed to Step 2 or move the plan to Done.
```

---
---

## STEP 1 — BELLOWS DEVELOPER

---

> **FIRST — before doing anything else, claim this plan:** `import shutil; shutil.move("bellows/knowledge/decisions/executable-bellows-verdict-schema-plan-a-2026-04-18.md", "bellows/knowledge/decisions/in-progress-executable-bellows-verdict-schema-plan-a-2026-04-18.md")`. **Skip specialist file and glossary reads — this is a mechanical code change to Bellows infrastructure, no domain interpretation required.** Add four new fields to the verdict request file format and fix one latent bug. The diagnostic findings at `bellows/knowledge/research/verdict-file-schema-2026-04-18.md` are the source of truth for why each change is being made — read the **Gap Assessment** table if you want justification for any change, otherwise the changes below are fully specified. **Change 1 — `verdict.py:post_verdict_request()`:** add a new required parameter `project_path` (string, absolute path to project root) BEFORE `step_number` in the signature. After the `**Plan:**` line in the content template, write `**Project:** {project_path}\n`. **Change 2 — `verdict.py:post_verdict_request()`:** immediately after the `**Pause Reason:** {pause_reason_label}\n` line, write `**Pause Reason Code:** {pause_reason}\n` (the raw enum value, not the human label). Do NOT change the existing `**Pause Reason:**` line — the human label stays for backwards compatibility with anything that currently reads it (notifier, ledger, CEO-eye skimming). **Change 3 — `verdict.py:post_verdict_request()`:** immediately after the `**Pause Reason Code:**` line, write `**Gate Result Passed:** {gate_result.get('passed', False)}\n` (Python bool — literal `True` or `False`, matching what `json.dumps` or `str(bool)` emits). **Change 4 — `verdict.py:post_verdict_request()`:** change the `**Total Steps:** {total_steps}\n` line so that if `total_steps is None`, the function raises `ValueError("total_steps must be an integer, got None")` BEFORE writing the file. This makes the existing default of `total_steps=None` in the signature a latent-error canary — callers must pass an int or fail loudly. Keep the default at `None` in the signature (changing it would be a breaking signature change for test mocks). **Change 5 — `verdict.py:_consume_verdicts` parser in `bellows.py:579–593`:** the existing code reads `**Total Steps:**` from a pending verdict file with `int(req_line.split(":**", 1)[1].strip())`, wrapped in `try/except (ValueError, IndexError): pass`. Find this block and add graceful handling for legacy files that still contain the literal string `"None"`: if the stripped value is `"None"`, set `total_steps_from_request = None` and continue (do not raise). This means old-on-disk verdict files don't break parsing after the write-side tightening. Add a one-line comment above the block: `# Legacy tolerance: pre-2026-04-18 verdict files may contain literal "None".`. **Change 6 — `bellows.py` call site at the mid-plan pause (inside the `while not is_final_step` loop, where `verdict.post_verdict_request(plan_path, current_step, log_path, gate_result, pause_reason=_pause_reason, total_steps=total_steps)` is called):** add `project_path=project_path` as an additional keyword argument. `project_path` is already a local variable in scope. Place the new kwarg between `log_path` and `gate_result` for readability: `verdict.post_verdict_request(plan_path, project_path, current_step, log_path, gate_result, pause_reason=_pause_reason, total_steps=total_steps)`. Since `project_path` is a positional insertion, verify the signature order in `verdict.py` matches this call — they must agree. **Change 7 — `bellows.py` call site at the final-step pause (after the `while` loop, the second `post_verdict_request` call):** identical change — add `project_path=project_path` in the same position. Verify both call sites pass positional arguments in the same order as the new `verdict.py` signature. **Verification as you go:** after making all code changes, run the targeted test suite for Bellows: `cd bellows && python -m pytest tests/ -v 2>&1 | tee knowledge/qa/evidence/executable-bellows-verdict-schema-plan-a-2026-04-18/pytest_targeted_dev_sanity.txt`. If any test fails that was passing before your changes, stop and report — do not continue to QA. This is a sanity check for Step 1, not the Rule 18 evidence file for Step 2 (QA will run the targeted suite again and deposit a separate evidence file). Create the evidence directory with `mkdir -p`. **Additional verification — manually post a fake verdict file:** write a short Python snippet that imports `verdict.post_verdict_request` and calls it with representative arguments including a `project_path`, a `total_steps=2` (NOT None), a `gate_result` dict with `passed=True`, and `pause_reason="qa_checkpoint"`. Run it. Read the file it produces. Confirm the seven top-level fields are all present (`**Plan:**`, `**Project:**`, `**Step:**`, `**Log:**`, `**Timestamp:**`, `**Pause Reason:**`, `**Pause Reason Code:**`, `**Gate Result Passed:**`, `**Total Steps:**`). Delete the fake verdict file after confirming. Do NOT commit any test-only fake verdict files to git. Write this one-off validation script to `bellows/knowledge/qa/evidence/executable-bellows-verdict-schema-plan-a-2026-04-18/manual_field_check.txt` — it is reference evidence for QA. **Commit:** after all changes pass the DEV sanity test and the manual field check, commit `verdict.py` and `bellows.py` together with message `"feat(verdict): add Project, Pause Reason Code, Gate Result Passed fields; enforce Total Steps non-None"`. Do NOT commit the evidence files (they live in `knowledge/qa/evidence/` which should be gitignored or excluded — verify before committing by running `git status`; if evidence files show as untracked and not gitignored, commit them in a separate commit after the feat commit with message `"test: verdict schema change evidence"`). **Deposit development log:** write a dev log to `bellows/knowledge/development/verdict-schema-plan-a-2026-04-18.md` using canonical Python file write pattern (`with open(path, "w") as f: f.write(content)` — NO heredoc, NO python3 -c). The dev log must include: a summary of changes made (one bullet per change 1–7), the exact commit hash of the feat commit, the file:line ranges modified (grep for the new field names after committing to confirm), and an Output Receipt per template format. **Feedback:** standard prompt feedback protocol → `bellows/knowledge/research/agent-prompt-feedback.md`.
>
> **STOP. Do NOT proceed to Step 2. Do NOT move the plan to Done. Wait for CEO confirmation before continuing.**

---
---

## STEP 2 — BELLOWS QA ANALYST

---

> Before starting, read `bellows/knowledge/development/verdict-schema-plan-a-2026-04-18.md` and check the Output Receipt status field. If status is not Complete, stop and report the issue to the CEO before proceeding. **Skip specialist file and glossary reads — this is a mechanical verification task.** Verify the Plan A verdict schema additions were implemented correctly and test the full behavior. **FIRST — Deliverable Verification (Rule 17).** Read the dev log's "Files Created or Modified (Code)" list. For EVERY listed deliverable, verify it exists and contains the described change. Produce a verification table at the top of the QA report: `| Deliverable | Expected | Status (✅/❌) | Evidence |`. Mandatory deliverable checks: (1) `verdict.py:post_verdict_request` signature — grep for `def post_verdict_request` in `verdict.py` and confirm `project_path` is in the parameter list; deposit the grep output to `bellows/knowledge/qa/evidence/executable-bellows-verdict-schema-plan-a-2026-04-18/grep_signature.txt`. (2) `verdict.py` content-template additions — grep for each of the four new field-writing lines (`**Project:**`, `**Pause Reason Code:**`, `**Gate Result Passed:**`) in `verdict.py` and confirm each appears exactly once as a write in the content f-string; deposit output to `grep_new_fields.txt`. (3) `verdict.py` Total Steps guard — grep for `ValueError.*total_steps` in `verdict.py` and confirm the raise is present; deposit to `grep_total_steps_guard.txt`. (4) `bellows.py:_consume_verdicts` legacy tolerance — grep for `Legacy tolerance` in `bellows.py` and confirm the comment + handling is present; deposit to `grep_legacy_tolerance.txt`. (5) `bellows.py` call site updates — grep for `post_verdict_request` in `bellows.py` and confirm both call sites now pass `project_path`; deposit to `grep_call_sites.txt`. For any ❌, attempt a re-run or re-commit before proceeding; if unfixable, STOP and report to CEO — do not move to Done. **SECOND — Targeted test run.** Run `cd bellows && python -m pytest tests/ -v 2>&1 | tee knowledge/qa/evidence/executable-bellows-verdict-schema-plan-a-2026-04-18/pytest_targeted.txt`. Confirm exit code 0. If any pre-existing tests fail that were passing before Plan A, investigate — if the failure is caused by the signature change (test mocks calling `post_verdict_request` positionally with the old argument order), either update the tests (minor test fixture update, allowed in this plan) or flag as blocker. The targeted suite is the primary test evidence. **THIRD — End-to-end verdict-write smoke test.** Write a Python script that: (a) constructs a fake `plan_path`, `project_path`, `gate_result` dict with `passed=True, failures=[], files_changed=[]`, `pause_reason="auto_close_disabled"`, `total_steps=1`; (b) calls `verdict.post_verdict_request(...)` with all required arguments; (c) reads back the file that was written; (d) asserts that the string `**Project:** /fake/project` appears exactly once, `**Pause Reason Code:** auto_close_disabled` appears exactly once, `**Gate Result Passed:** True` appears exactly once, `**Total Steps:** 1` appears exactly once (not "None"); (e) prints PASS or FAIL with the mismatched field name; (f) deletes the fake file at the end. Save the script to `bellows/knowledge/qa/evidence/executable-bellows-verdict-schema-plan-a-2026-04-18/e2e_verdict_write.py` and pipe its stdout to `bellows/knowledge/qa/evidence/executable-bellows-verdict-schema-plan-a-2026-04-18/e2e_verdict_write.txt`. The script must assert all four new fields; if any assertion fails, the QA row for that field is ❌. **FOURTH — Total Steps guard test.** Write a second small script that calls `verdict.post_verdict_request(...)` with `total_steps=None` explicitly and confirms a `ValueError` is raised (expected behavior). Save to `e2e_total_steps_guard.py` and pipe stdout to `e2e_total_steps_guard.txt`. If the call does NOT raise, that's ❌. **FIFTH — Legacy tolerance test.** Write a third small script that: (a) creates a fake pending verdict file in `bellows/verdicts/pending/verdict-request-fake-legacy-step-1.md` containing `**Plan:** /fake\n**Step:** 1\n**Total Steps:** None\n`; (b) invokes the parser logic from `_consume_verdicts` (or simulates it by importing the relevant code path if reachable, else copies the parser block inline) against that file; (c) confirms the parser does NOT raise and sets `total_steps_from_request = None`; (d) cleans up the fake file. Save to `e2e_legacy_tolerance.py` and pipe to `e2e_legacy_tolerance.txt`. **WRITE THE QA REPORT** to `bellows/knowledge/qa/verdict-schema-plan-a-2026-04-18.md`. The report includes: (a) the deliverable verification table, (b) the targeted test summary (pass/fail counts, exit code), (c) the three end-to-end smoke test results, (d) overall status. Write via canonical Python file write pattern — NO heredoc. **Final — PROJECT_STATUS.md update.** Add a completed milestone entry to `bellows/PROJECT_STATUS.md` summarizing this plan: "Plan A verdict schema additions (Project, Pause Reason Code, Gate Result Passed) plus Total Steps non-None enforcement with legacy-file tolerance. Four new fields in every verdict request file. Unblocks Planner Rule 22 verdict-routing (pending Plan B for Deposit field)." Use `Desktop Commander:edit_block` or exact-anchor `str_replace` with a verbatim existing-line anchor — do NOT append blindly. **Feedback:** standard prompt feedback protocol → `bellows/knowledge/research/agent-prompt-feedback.md`. **Final commit:** `cd bellows && git add knowledge/qa/verdict-schema-plan-a-2026-04-18.md knowledge/qa/evidence/executable-bellows-verdict-schema-plan-a-2026-04-18/ knowledge/development/verdict-schema-plan-a-2026-04-18.md PROJECT_STATUS.md knowledge/research/agent-prompt-feedback.md && git commit -m "qa: verdict schema plan A — deliverable verification + smoke tests passed"`. **Then move-to-Done:** `import shutil; shutil.move("bellows/knowledge/decisions/in-progress-executable-bellows-verdict-schema-plan-a-2026-04-18.md", "bellows/knowledge/decisions/Done/executable-bellows-verdict-schema-plan-a-2026-04-18.md")`. The move-to-Done is the absolute last operation (Rule 23c). **Rule 20 — Mandatory QA Self-Check (run AFTER writing the QA report, BEFORE the final commit and move-to-Done):**
>
> ```python
> # Rule 20 — Mandatory QA Self-Check
> import os, sys
> plan_slug = "executable-bellows-verdict-schema-plan-a-2026-04-18"
> qa_report_path = "bellows/knowledge/qa/verdict-schema-plan-a-2026-04-18.md"
> evidence_dir = f"bellows/knowledge/qa/evidence/{plan_slug}/"
> required_evidence_files = [
>     "grep_signature.txt",
>     "grep_new_fields.txt",
>     "grep_total_steps_guard.txt",
>     "grep_legacy_tolerance.txt",
>     "grep_call_sites.txt",
>     "pytest_targeted.txt",
>     "e2e_verdict_write.py",
>     "e2e_verdict_write.txt",
>     "e2e_total_steps_guard.py",
>     "e2e_total_steps_guard.txt",
>     "e2e_legacy_tolerance.py",
>     "e2e_legacy_tolerance.txt",
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
