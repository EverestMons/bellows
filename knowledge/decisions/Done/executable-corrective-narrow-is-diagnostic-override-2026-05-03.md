# Bellows — Corrective Parser Fix: Narrow `is_diagnostic` Step-Count Override
**Date:** 2026-05-03 | **Tier:** Small | **Test Scope:** targeted | **Execution:** Step 1 (BELLOWS DEVELOPER) → Step 2 (BELLOWS DEVELOPER QA)

## How to Run This Plan

Paste the bootstrap prompt into Claude Code. The agent reads the full plan file and executes Step 1 ONLY. After completing Step 1, the agent STOPS and waits for CEO confirmation ("ok") before proceeding to Step 2. The Planner moves the plan to Done after Rule 22 verification passes.

**Bootstrap prompt:**
```
Read the plan at bellows/knowledge/decisions/executable-corrective-narrow-is-diagnostic-override-2026-05-03.md. Execute Step 1 ONLY. After completing Step 1, STOP and wait for my confirmation. Do NOT proceed to Step 2 or move the plan to Done.
```

## Background (read before executing)

This plan corrects the failed parser fix attempted earlier today. The original plan `executable-remove-is-diagnostic-step-override-2026-05-03` removed the `if is_diagnostic: total_steps = 1` override at two locations in `bellows.py`. The override removal was based on a faulty premise — the diagnostic findings file `bellows/knowledge/research/extract-total-steps-undercount-2026-05-03.md` framed the override as "dead code" preventing multi-step diagnostics from counting correctly. That framing was partially correct but missed a load-bearing semantic: at the `run_plan` site, the override was the input adapter that let header-less diagnostics flow through Phase 8.1's pause-or-close logic. Removing it broke Phase 8.1 for header-less diagnostics, which was confirmed by 3 test failures: `test_diagnostic_auto_close_moves_to_done`, `test_clean_diagnostic_no_header_posts_verdict`, `test_clean_diagnostic_auto_close_true_moves_to_done`.

The original plan was halted via stop verdict (deposited 2026-05-03 ~12:40). The broken `bellows.py` edit remains in the working tree (uncommitted) and must be discarded before applying the corrective fix.

The corrective fix narrows the override to fire only when `extract_total_steps()` returns 0. This:
- Preserves Phase 8.1 semantics for header-less diagnostics (override fires, `total_steps = 1`, plan flows through pause-or-close logic per `auto_close` header)
- Fixes the original bug (multi-step diagnostics with `## STEP N` headers count their headers correctly because `extract_total_steps()` returns a positive count and the override does NOT fire)
- Header-less executables fall through with `total_steps = 0` to the existing `is_final_step(1, 0) → True` terminal-step branch, which handles them via the same pause-or-close logic (no SKIP-and-Done bypass)

The corrective fix at the second site (`_consume_verdicts`) is also narrow but mostly cosmetic — the post-edit code there happens to work correctly for all known cases via `1 >= 0` coincidence on the `is_final_step` check. Adding the narrow override there is defensive symmetry.

**Test scope justification (`targeted`):** Single-file mechanical edit to `bellows.py` plus dev log + commits. No production code paths exercised that aren't already covered by the existing test suite. Targeted bucket = `tests/test_bellows.py` plus full suite as a safety net (treating this as `targeted` not `full-suite` because the change is purely the inverse of today's earlier removal — the affected test surface is identical).

## Related artifacts

- **Halted prior plan:** `bellows/knowledge/decisions/halted-executable-remove-is-diagnostic-step-override-2026-05-03.md` (after Bellows processes the stop verdict)
- **Diagnostic that confirmed root cause:** `bellows/knowledge/research/extract-total-steps-undercount-2026-05-03.md` (correct on the multi-step counting bug, incomplete on Phase 8.1 implications)
- **Diagnostic that surfaced the Phase 8.1 regression:** `bellows/knowledge/research/step1-phase-skip-investigation-2026-05-03.md` (closed cleanly via Rule 22)

---
---

## STEP 1 — BELLOWS DEVELOPER

---

> **STOP REMINDER (TOP):** This is the implementation step. After completing this step, STOP and wait for CEO confirmation. Do NOT execute Step 2 (QA verification). Do NOT move the plan to Done — the Planner performs the terminal move after Rule 22 verification passes. **If any phase below fails, write the failure details to `bellows/knowledge/development/corrective-narrow-override-failure-log-2026-05-03.md` BEFORE stopping. Do not stop silently.**
>
> **FIRST — before doing anything else, claim this plan:** `import shutil; shutil.move("bellows/knowledge/decisions/executable-corrective-narrow-is-diagnostic-override-2026-05-03.md", "bellows/knowledge/decisions/in-progress-executable-corrective-narrow-is-diagnostic-override-2026-05-03.md")`.
>
> You are the Bellows Developer. Skip specialist file and glossary reads — this is a code-tracing task with a known fix shape from the Planner. Working directory is `/Users/marklehn/Desktop/GitHub/bellows`.
>
> **Phase 1 — Verify uncommitted state and discard the broken edit.** Run: `cd /Users/marklehn/Desktop/GitHub/bellows && git --no-pager status --short bellows.py`. Expected: ` M bellows.py` (modified, unstaged). If output is empty (no uncommitted changes), the broken edit already landed in a commit — STOP and write to the failure log: "broken edit appears already committed; expected uncommitted state. Last 3 commits: [paste git log -3 output]." If output shows the modified file as expected, proceed: `cd /Users/marklehn/Desktop/GitHub/bellows && git --no-pager checkout bellows.py`. Verify the file is now clean: `cd /Users/marklehn/Desktop/GitHub/bellows && git --no-pager status --short bellows.py` should produce empty output. **Do NOT proceed to Phase 2 if Phase 1 did not produce a clean working tree for `bellows.py`.**
>
> **Phase 2 — Apply narrow override at `run_plan` site.** The `run_plan` function in `bellows.py` originally had `is_diagnostic = ...; total_steps = extract_total_steps(metadata_text); if is_diagnostic: total_steps = 1` near line 228. After Phase 1's checkout, that pre-edit code is now restored. Use `Desktop Commander:edit_block` to replace it with the narrow override. The exact `old_string` is the verbatim 4-line block ending with the override:
>
> ```
>         is_diagnostic = os.path.basename(plan_path).startswith("diagnostic-")
>         total_steps = extract_total_steps(metadata_text)
>         if is_diagnostic:
>             total_steps = 1
> ```
>
> The `new_string` replaces the unconditional override with a narrow one and adds an explanatory comment:
>
> ```
>         is_diagnostic = os.path.basename(plan_path).startswith("diagnostic-")
>         total_steps = extract_total_steps(metadata_text)
>         # NOTE 2026-05-03: Narrow override — fires only when extract_total_steps()
>         # returned 0 (no `## STEP N` headers). Multi-step diagnostics with headers
>         # count correctly. Header-less diagnostics flow through Phase 8.1 pause-or-close
>         # logic via this single-step fallback. Test fixtures that depend on this:
>         # test_diagnostic_auto_close_moves_to_done, test_clean_diagnostic_no_header_posts_verdict,
>         # test_clean_diagnostic_auto_close_true_moves_to_done.
>         if total_steps == 0 and is_diagnostic:
>             total_steps = 1
> ```
>
> Use `expected_replacements=1`. If the edit_block reports a near-miss diff, STOP and write the diff output to the failure log — do NOT make speculative manual edits. Verify the edit landed: `grep -n "Narrow override" /Users/marklehn/Desktop/GitHub/bellows/bellows.py` should return one match in the run_plan area (~line 230-240).
>
> **Phase 3 — Apply narrow override at `_consume_verdicts` site (optional defensive symmetry).** The `_consume_verdicts` method has a similar pre-edit pattern: `is_diag = original_name.startswith("diagnostic-"); if is_diag: total_steps_c = 1; else: total_steps_c = extract_total_steps(plan_text_c)` near line 690. Use `Desktop Commander:edit_block` to replace it with a narrow-override pattern. The exact `old_string` block to find (verbatim from the pre-edit code, restored by Phase 1's checkout):
>
> ```
>                         if v == "continue":
>                             is_diag = original_name.startswith("diagnostic-")
>                             # Fallback chain: shadow → verdict metadata → load_file
>                             shadow_text_c = _read_shadow(original_name)
>                             if shadow_text_c is not None:
>                                 total_steps_c = extract_total_steps(shadow_text_c) if not is_diag else 1
>                                 print(f"Bellows: using cached plan content ({total_steps_c} steps)")
>                             elif total_steps_from_request is not None:
>                                 total_steps_c = total_steps_from_request
>                             else:
>                                 plan_text_c = load_file(full_plan_path)
>                                 total_steps_c = extract_total_steps(plan_text_c) if not is_diag else 1
> ```
>
> **IMPORTANT:** The exact pre-edit `old_string` shape may differ slightly from what's reproduced above — the Planner is reasoning from memory of the post-edit comment "Removed is_diag override (see first removal site comment)" and inferring what the pre-edit shape was. **Before invoking edit_block, read the actual current state at `bellows.py:680-720` (post Phase 1 checkout) and adjust the `old_string` to match exactly.** If the actual pre-edit shape doesn't conditionally call `extract_total_steps` based on `is_diag`, simplify Phase 3 to: read the actual code, write a narrow-override edit that mirrors Phase 2's pattern (compute extract_total_steps unconditionally, then `if total_steps_c == 0 and is_diag: total_steps_c = 1`), and apply via edit_block. Verification grep: `grep -n "is_diag" /Users/marklehn/Desktop/GitHub/bellows/bellows.py | wc -l` should return at least one match (the narrow-override line) and the surrounding code should compute `total_steps_c` via `extract_total_steps` unconditionally.
>
> **Phase 4 — Run targeted test suite.** From `bellows/` directory: `cd /Users/marklehn/Desktop/GitHub/bellows && python3 -m pytest tests/test_bellows.py -v 2>&1 | tee /tmp/pytest-corrective-after-fix.txt`. Expected outcome:
>
> 1. `test_diagnostic_auto_close_moves_to_done` — **PASS** (was failing under broken edit; should pass under narrow override)
> 2. `test_clean_diagnostic_no_header_posts_verdict` — **PASS** (same)
> 3. `test_clean_diagnostic_auto_close_true_moves_to_done` — **PASS** (same)
> 4. `test_run_step_timeout` — **expected pre-existing failure** (per agent's bisect findings on the prior diagnostic; NOT introduced by this fix and NOT this plan's responsibility to fix)
> 5. All other tests in `test_bellows.py` — **PASS** (no regressions introduced)
>
> Report the pass/fail count and the names of any failures. **If any test that was passing pre-fix is now failing, OR if the 3 previously-failing tests are still failing, STOP and write to the failure log: include the full pytest output for the failing tests, and a one-paragraph hypothesis about what went wrong.** Do NOT proceed to Phase 5 if Phase 4 reveals unexpected failures.
>
> **Phase 5 — Commit the corrective fix.** `cd /Users/marklehn/Desktop/GitHub/bellows && git --no-pager add bellows.py && git --no-pager commit -m "fix(bellows): narrow is_diagnostic step-count override to total_steps==0"`. Verify the commit landed: `cd /Users/marklehn/Desktop/GitHub/bellows && git --no-pager log -1 --oneline`.
>
> **Phase 6 — Dev log deposit.** Write a development log to `bellows/knowledge/development/corrective-narrow-override-dev-log-2026-05-03.md` documenting: (a) confirmation that the broken prior edit was discarded via `git checkout` (cite the `git status` output before and after), (b) the two file:line locations modified in Phase 2 and Phase 3, (c) the test result counts (note: Phase 4 expects 4 failures total — 3 fixed by this plan, 1 pre-existing `test_run_step_timeout` not addressed here), (d) the commit SHA from Phase 5. Use the canonical Python file write pattern: `with open("bellows/knowledge/development/corrective-narrow-override-dev-log-2026-05-03.md", "w") as f: f.write(content)`. Commit the dev log: `cd /Users/marklehn/Desktop/GitHub/bellows && git --no-pager add knowledge/development/corrective-narrow-override-dev-log-2026-05-03.md && git --no-pager commit -m "docs: dev log for corrective narrow override fix"`.
>
> **Constraints:**
> - Do NOT modify `runner.py`, `gates.py`, `verdict.py`, `parser.py`, or any other module. The fix is two locations in `bellows.py` only.
> - Do NOT add new tests — that's Step 2 (QA) verification work. Phase 4 runs the EXISTING test suite as regression check.
> - Do NOT use heredoc syntax for any file write (banned per PLANNER_TEMPLATE Rule 5). Use canonical `with open() as f: f.write(content)` Python pattern or `Desktop Commander:edit_block` for surgical edits.
> - Do NOT modify the failing `test_run_step_timeout` — it's a pre-existing failure unrelated to this plan's scope.
> - **Failure-deposit discipline:** if any phase fails, write the failure details to `bellows/knowledge/development/corrective-narrow-override-failure-log-2026-05-03.md` BEFORE stopping. The Planner cannot see your conversation text — it can only see deposited files and Bellows's gate output.
>
> Standard prompt feedback protocol → `bellows/knowledge/research/agent-prompt-feedback.md`.
>
> **Deposits:**
> - `bellows/knowledge/development/corrective-narrow-override-dev-log-2026-05-03.md`
>
> **STOP REMINDER (BOTTOM):** Step 1 is COMPLETE when (a) `git checkout` discarded the broken edit, (b) Phase 2 narrow override landed at the run_plan site, (c) Phase 3 narrow override landed at the _consume_verdicts site (or was simplified per the in-line caveat), (d) Phase 4 pytest shows the 3 previously-failing tests now pass with no new failures introduced, (e) Phase 5 commit landed, (f) Phase 6 dev log deposited and committed. Do NOT execute Step 2 (QA verification). Do NOT move the plan to Done. Wait for CEO confirmation before any further action.

---
---

## STEP 2 — BELLOWS DEVELOPER (QA)

---

> Before starting, read `bellows/knowledge/development/corrective-narrow-override-dev-log-2026-05-03.md` and check the Output Receipt status. If the dev log doesn't exist OR if its status is not Complete, stop and report the issue to the CEO before proceeding. Also check whether `bellows/knowledge/development/corrective-narrow-override-failure-log-2026-05-03.md` exists — if it does, Step 1 hit a failure path and Step 2 should NOT proceed; report to CEO instead.
>
> **STOP REMINDER (TOP):** This is the QA verification step. Do NOT modify production code. Do NOT move the plan to Done — the Planner performs the terminal move after Rule 22 verification passes.
>
> You are the Bellows Developer (acting as QA for this plan). Skip specialist file and glossary reads.
>
> **Task: verify Step 1's deliverables exist with the expected content, run the test suite as regression check, run the Rule 20 mandatory self-check, write the QA report.**
>
> **Phase 1 — Deliverable verification (Rule 17).** Read Step 1's dev log to identify the exact files modified. For EACH listed deliverable, verify it exists with the expected change:
>
> 1. **`bellows.py` narrow override at run_plan site.** Run: `grep -n "Narrow override" /Users/marklehn/Desktop/GitHub/bellows/bellows.py | tee /Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/evidence/corrective-narrow-override-2026-05-03/grep_narrow_override.txt`. Expected: at least one match in the run_plan area.
> 2. **`bellows.py` narrow override at _consume_verdicts site.** Run: `grep -n "is_diag" /Users/marklehn/Desktop/GitHub/bellows/bellows.py | tee /Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/evidence/corrective-narrow-override-2026-05-03/grep_is_diag.txt`. Expected: at least one match referencing the narrow override pattern.
> 3. **No SKIP branch present.** Run: `grep -n "SKIPPED.*has no.*STEP headers" /Users/marklehn/Desktop/GitHub/bellows/bellows.py | tee /Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/evidence/corrective-narrow-override-2026-05-03/grep_skip_branch.txt`. Expected: zero matches (the SKIP branch added by the previous broken plan should NOT exist; if it does, Phase 1's git checkout didn't fully restore the pre-edit state).
> 4. **Commits landed.** Run: `cd /Users/marklehn/Desktop/GitHub/bellows && git --no-pager log --oneline -5 | tee /Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/evidence/corrective-narrow-override-2026-05-03/git_log.txt`. Expected: top 2 commits are the dev log commit and the bellows.py commit (in that order, since dev log committed last per Phase 6).
>
> Produce a verification table: `| Deliverable | Expected | Status (✅/❌) | Evidence |`. Cite the evidence file paths in the Evidence column. Any ❌ item is a Critical finding that blocks the plan from closing — do NOT proceed to subsequent phases. Attempt to fix ❌ items if possible (re-run a missed grep, re-deposit a missed file); if unfixable, stop and report to CEO.
>
> **Phase 2 — Test regression check.** From `bellows/` directory: `cd /Users/marklehn/Desktop/GitHub/bellows && python3 -m pytest tests/test_bellows.py -v 2>&1 | tee /Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/evidence/corrective-narrow-override-2026-05-03/pytest_targeted.txt`. Expected outcome (matching Phase 4 of Step 1):
>
> - `test_diagnostic_auto_close_moves_to_done` — **PASS**
> - `test_clean_diagnostic_no_header_posts_verdict` — **PASS**
> - `test_clean_diagnostic_auto_close_true_moves_to_done` — **PASS**
> - `test_run_step_timeout` — **expected pre-existing failure**
> - All other tests — **PASS**
>
> Report the pass/fail count. If anything differs from the expected outcome, mark the relevant verification table row ❌ Critical.
>
> **Phase 3 — Behavioral spot-check.** Verify the narrow override produces the right `total_steps` value for both header-less and multi-step diagnostic plans. Write a small Python script via canonical pattern (NOT heredoc, NOT `python3 -c "..."`):
>
> 1. Write the script to `/tmp/spot_check_narrow_override.py` using `with open() as f: f.write(content)`.
> 2. The script imports `extract_total_steps` from `bellows.bellows` and runs it against three inputs: (a) a header-less diagnostic plan content (`"## Diagnostic\nSingle-step.\n"`) — expected return 0; (b) the live content of `bellows/knowledge/decisions/Done/diagnostic-worktree-implementation-surface-2026-05-03.md` (a known 3-step diagnostic) — expected return 3; (c) the live content of `bellows/knowledge/decisions/Done/diagnostic-step1-phase-skip-investigation-2026-05-03.md` if it has been moved to Done by the time this runs (a known 1-step diagnostic) — expected return 1.
> 3. Print results.
> 4. Run: `python3 /tmp/spot_check_narrow_override.py 2>&1 | tee /Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/evidence/corrective-narrow-override-2026-05-03/spot_check.txt`.
> 5. Verify all three returns match expected.
> 6. Cleanup: `rm /tmp/spot_check_narrow_override.py`.
>
> If any return diverges from expected, flag as ❌ Critical.
>
> **Phase 4 — Write the QA report.** Deposit to `bellows/knowledge/qa/corrective-narrow-override-qa-2026-05-03.md`. Include: (a) Phase 1 deliverable verification table with evidence file paths cited; (b) Phase 2 test regression result with pass/fail counts; (c) Phase 3 behavioral spot-check result; (d) Output Receipt with Status; (e) the Rule 20 self-check stdout output appended at the end. Use canonical Python file write pattern.
>
> **Phase 5 — Update PROJECT_STATUS.md.** Add a completed milestone entry summarizing this corrective plan's changes (one short bullet point referencing the corrective parser fix and the Phase 8.1 preservation). Use `Desktop Commander:edit_block` with exact anchor (the existing line above the Completed Milestones list). If you can't find a clear anchor, append at the end of the Completed Milestones section.
>
> **Phase 6 — Mandatory Rule 20 self-check.** Run the standard self-check Python block at the end of this step. Required evidence files (must all be present in the evidence directory): `grep_narrow_override.txt`, `grep_is_diag.txt`, `grep_skip_branch.txt`, `git_log.txt`, `pytest_targeted.txt`, `spot_check.txt`. Plan slug: `executable-corrective-narrow-is-diagnostic-override-2026-05-03`. QA report path: `bellows/knowledge/qa/corrective-narrow-override-qa-2026-05-03.md`. Include the literal stdout of the self-check in the QA report.
>
> ```python
> # Rule 20 — Mandatory QA Self-Check
> import os, sys
> plan_slug = "executable-corrective-narrow-is-diagnostic-override-2026-05-03"
> qa_report_path = "bellows/knowledge/qa/corrective-narrow-override-qa-2026-05-03.md"
> evidence_dir = "bellows/knowledge/qa/evidence/corrective-narrow-override-2026-05-03/"
> required_evidence_files = [
>     "grep_narrow_override.txt",
>     "grep_is_diag.txt",
>     "grep_skip_branch.txt",
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
> **Hedging-keyword note for the spot-check evidence:** The "skipped" hedging keyword will appear in `spot_check.txt` because the spot-check verifies `extract_total_steps` returns 0 for header-less plans (the comment may include "skipped" as a domain term). The hedging scan only fires on positive-status table ROWS in the QA report — it does NOT scan evidence file contents. So no concern there as long as you don't write a verification table row that says "✅ ... skipped ..." — phrase positive-status rows without hedging keywords.
>
> If the self-check prints `FAILED`, the agent STOPS — does NOT update PROJECT_STATUS.md, does NOT move the plan to Done, reports the failure to the CEO and waits.
>
> **Phase 7 — Final commit.** After QA report and PROJECT_STATUS.md edit are deposited, single final commit: `cd /Users/marklehn/Desktop/GitHub/bellows && git --no-pager add knowledge/qa/corrective-narrow-override-qa-2026-05-03.md knowledge/qa/evidence/corrective-narrow-override-2026-05-03/ PROJECT_STATUS.md && git --no-pager commit -m "qa: verify corrective narrow override fix"`.
>
> Standard prompt feedback protocol → `bellows/knowledge/research/agent-prompt-feedback.md`.
>
> **Deposits:**
> - `bellows/knowledge/qa/corrective-narrow-override-qa-2026-05-03.md`
> - `bellows/knowledge/qa/evidence/corrective-narrow-override-2026-05-03/` (six evidence files per Rule 20 self-check)
>
> **STOP.** Do NOT move this plan to Done/. Per the disable-auto-close model, the Planner performs the terminal move after Rule 22 verification passes.
