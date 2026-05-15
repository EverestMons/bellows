# bellows — Remove Phase 3b/3c DB Step-State-Resume Logic
**Date:** 2026-05-01 | **Tier:** Small | **Test Scope:** full-suite | **Execution:** Step 1 (DEV) → Step 2 (QA)

## CEO Context

**Test Scope: full-suite** — touches `run_plan` (core lifecycle code) and removes a private helper (`_get_last_completed_step`) consumed by tests. Cross-bucket regression risk on every test that exercises plan dispatch.

**Background.** The diagnostic at `bellows/knowledge/research/phase-3b-mechanism-and-cost-benefit-2026-05-01.md` confirmed with literal SQL evidence that today's session-wrap v1 phantom-resume bug was caused by Phase 3b's `_get_last_completed_step` querying `runs` rows from a prior same-slug plan. The diagnostic's Q6 evaluation determined that **Phase 3b/3c is dead code** — it guards a manual-rename resume path that's unsupported per Rule 25, while the supported verdict-resume path passes `resume_step` explicitly and never consults the DB. Zero legitimate uses of the DB-resume path exist in operational history; one phantom-resume bug observed (today's wrap).

**Fix shape: F3 (Remove).** Three code blocks removed from `bellows.py`:
1. **L175–188:** `_get_last_completed_step` function definition
2. **L243–247:** DB-resume guard (`if resume_step is None and shadow_text is not None: ...`)
3. **L249–254:** Phase 3c hash-drift warning block

**What is preserved:**
- `runs.plan_slug` column (analytics/debugging value)
- `record_run()` continuing to populate `plan_slug` (recording is independently useful)
- Shadow cache system (used for metadata extraction, total_steps, prompt routing — all still needed)
- Verdict-resume path unchanged (`_consume_verdicts` already passes `resume_step` explicitly; the removed code was never on this path)

**Tests removed:** Phase 3b canary tests (the diagnostic SA noted these exist but did not pin their file location). The DEV greps to identify and removes the tests that exercise `_get_last_completed_step` directly. New regression test added: deposit an executable plan whose slug matches a Done/ plan; verify Bellows dispatches step 1, not phantom-resumes step 3.

**End-to-end trace verified by Planner.** Original bug: v1 wrap fresh deposit → DB query found "step 2 complete" from prior session → phantom resume at step 3 → step 1+2 deliverables never produced. After F3: fresh deposit → guard removed entirely → `resume_step` stays None → bootstrap dispatches step 1 → fresh start. Verdict-resume path: `_consume_verdicts` calls `handle_new_plan(inprogress_path, resume_step=N+1)` — `resume_step` is not None, the removed block was unreachable on this path anyway, no change.

**Crash-recovery non-regression confirmed.** The SA flagged "loss of crash-recovery resume" as a tradeoff. Planner traced this and found it illusory: if the daemon crashes mid-step, the plan is at `in-progress-*`, the watcher does NOT re-claim `in-progress-*` files (per the on_moved fix shipped 2026-04-19), so Phase 3b never had the chance to recover. F3 doesn't lose any working recovery path; it loses a path that never worked.

## How to Run This Plan

Paste the bootstrap into Claude Code. The agent reads the full plan file and executes Step 1 ONLY. After Step 1 reports Complete, CEO confirms ("ok") to advance to Step 2. After Step 2, CEO must restart Bellows to load the removed code.

**Bootstrap:**
```
Read the plan at bellows/knowledge/decisions/executable-remove-phase-3b-3c-2026-05-01.md. Execute Step 1 ONLY. After completing Step 1, STOP and wait for my confirmation. Do NOT proceed to Step 2 or move the plan to Done.
```

---
---

## STEP 1 — BELLOWS DEVELOPER

---

> **FIRST — before doing anything else, claim this plan:** `import shutil; shutil.move("bellows/knowledge/decisions/executable-remove-phase-3b-3c-2026-05-01.md", "bellows/knowledge/decisions/in-progress-executable-remove-phase-3b-3c-2026-05-01.md")`.
>
> You are the Bellows Developer. **Read the diagnostic findings at `bellows/knowledge/research/phase-3b-mechanism-and-cost-benefit-2026-05-01.md` first** — Q1–Q4 document the mechanism, Q6 specifies the F3 removal scope. Skip specialist file and glossary reads — this is a code-removal fix following an SA blueprint. Use the `Edit` tool (NOT `Desktop Commander:edit_block` — not available in Claude Code).
>
> **Pre-edit verification.** Run `grep -n "_get_last_completed_step" bellows/bellows.py` and capture every match (definition + call sites). The SA cited L175-188 (definition) and L243-247 (single call site at the DB-resume guard). Verify line numbers; report drift in dev log if any.
>
> **Pre-edit test discovery.** Run `grep -rn "_get_last_completed_step\|DB resume\|plan_hash\|hash drift" bellows/tests/` to identify every test file that exercises Phase 3b or Phase 3c functionality. The diagnostic mentioned `canary-phase-3b-restart-2026-04-30` and `canary-phase-3c-plan-hash-drift-warning-2026-04-30` plans (in `Done/`) but did not pin which test file the canaries touched. Report the full grep output in the dev log; identify which tests need to be deleted (those that test ONLY removed functionality) vs updated (tests that incidentally reference removed functions but cover other behavior).
>
> **Edit 1 — Remove `_get_last_completed_step` function definition.** SA cited L175-188. Verify the function body matches the diagnostic snippet (Q2 verbatim text). Use `Edit` with the full function body as `old_str` (including the line above and below for unique anchoring) and remove it cleanly. The function should not be referenced anywhere else after Edit 2 lands; if Edit 1 happens first, run will fail until Edit 2 lands.
>
> **Edit 2 — Remove DB-resume guard.** SA cited L243-247:
> ```python
> if resume_step is None and shadow_text is not None:
>     last_step = _get_last_completed_step(db_path, plan_slug)
>     if last_step is not None and last_step >= 1:
>         resume_step = last_step + 1
>         print(f"Bellows: DB resume — last completed step {last_step}, resuming at {resume_step}")
> ```
> Use `Edit` with this entire block as `old_str` and replace with empty string (or remove via deletion). Verify with `grep -n "DB resume" bellows/bellows.py` returns zero matches.
>
> **Edit 3 — Remove Phase 3c hash-drift block.** SA cited L249-254:
> ```python
> if resume_step is not None and resume_step > 1 and shadow_text is not None:
>     shadow_hash = hashlib.sha256(shadow_text.encode()).hexdigest()[:12]
>     current_hash = hashlib.sha256(plan_text.encode()).hexdigest()[:12]
>     if shadow_hash != current_hash:
>         print(f"Bellows: ⚠️ plan content changed since last step — shadow={shadow_hash} current={current_hash}")
>         notifier.push(app_key, user_key, "Bellows — Plan Modified",
>                       f"Plan {plan_name} content changed since step {resume_step - 1}. Resuming at step {resume_step} with modified plan.")
> ```
> Use `Edit` to remove. After this edit, search for any remaining references to `hashlib` in `bellows.py` — if `hashlib` is no longer used elsewhere in the file, remove the `import hashlib` line at the top. Verify with `grep -n "hashlib" bellows/bellows.py`.
>
> **Edit 4 — Delete Phase 3b/3c canary tests.** Based on the test discovery grep, identify the test functions that ONLY exercise removed functionality (e.g., `test_get_last_completed_step_*`, `test_db_resume_*`, `test_phase_3c_*`, `test_hash_drift_*`). Use `Edit` to remove each test function in turn. Do NOT delete tests that incidentally call `_get_last_completed_step` for setup but actually test other behavior — update those tests to remove the unused setup. List every removal/update in the dev log with file path and test name.
>
> **Edit 5 — Add regression test for the F3 fix.** Append to `bellows/tests/test_consume_verdicts.py` (the file created in this morning's cleanup-slug-normalization plan; suitable home for the new test):
>
> ```python
> def test_dispatch_starts_fresh_when_db_has_orphan_slug_rows():
>     """When a new executable plan is deposited and the DB contains rows for the same slug
>     from a prior session (orphan rows from a Done/ or halted plan), Bellows must dispatch
>     step 1 fresh — not phantom-resume to a later step. Regression for the 2026-05-01
>     phantom-resume bug fixed by F3 removal of Phase 3b/3c DB-resume logic."""
>     # The test verifies the absence of DB-resume code by asserting that resume_step
>     # remains None after run_plan setup (no DB query), even when the runs table contains
>     # Complete rows for the plan's slug.
>     # ...
> ```
> The DEV writes the test body. The assertion must directly verify that step 1 is dispatched, NOT that some intermediate variable equals None — the test name promises "dispatches fresh," so the assertion must verify dispatch behavior. Per the test-name-vs-assertion lesson from this session, if the assertion cannot be written to encode the property the name implies, the test name must change. The test should patch `_dispatch_step` (or whatever function actually dispatches the bootstrap) and assert it is called with `step_number=1`. If the test ends up asserting only that `_get_last_completed_step` was not called (because it doesn't exist), rename the test to `test_get_last_completed_step_no_longer_exists` and add a SECOND test that verifies dispatch behavior end-to-end.
>
> **Verify edits.** After all edits, run:
> 1. `python3 -c "import ast; ast.parse(open('bellows/bellows.py').read()); print('valid')"` — expect output `valid`
> 2. `grep -n "_get_last_completed_step\|DB resume\|hash drift" bellows/bellows.py` — expect zero matches
> 3. `cd bellows && python3 -m pytest tests/ -x -v 2>&1 | tail -100` — expect full suite passes (180 baseline + new regression test = 181, minus deleted Phase 3b/3c canary tests). Report the exact pass/fail count.
>
> **Deposit dev log** at `bellows/knowledge/development/remove-phase-3b-3c-dev-log-2026-05-01.md` containing: (a) verified line numbers vs SA findings, (b) test discovery grep output (which tests were found, which were deleted, which were updated), (c) verbatim before/after for each of the 5 edits, (d) test results, (e) note that CEO restart is required. Use the canonical Python file write pattern.
>
> Standard prompt feedback protocol → `bellows/knowledge/research/agent-prompt-feedback.md`.
>
> **Commit:** `cd /Users/marklehn/Desktop/GitHub && git add bellows/bellows.py bellows/tests/ bellows/knowledge/development/remove-phase-3b-3c-dev-log-2026-05-01.md bellows/knowledge/research/agent-prompt-feedback.md && git commit -m "remove: Phase 3b/3c DB-resume logic — dead code that fires only as a bug (BACKLOG slug-collision)"`.
>
> **Deposits:**
> - `bellows/bellows.py`
> - `bellows/tests/test_consume_verdicts.py`
> - (variable) test files identified by discovery grep
> - `bellows/knowledge/development/remove-phase-3b-3c-dev-log-2026-05-01.md`
> - `bellows/knowledge/research/agent-prompt-feedback.md`
>
> **STOP. Do NOT proceed to Step 2. Do NOT move the plan to Done. Wait for CEO confirmation before continuing.**

---
---

## STEP 2 — BELLOWS QA

---

> Before starting, read `bellows/knowledge/development/remove-phase-3b-3c-dev-log-2026-05-01.md` and check the Output Receipt status. If status is not Complete, stop and report.
>
> You are the Bellows QA Agent. Skip specialist file and glossary reads — this is verification of code removal.
>
> **FIRST — Deliverable Verification (Rule 17).** Read the Step 1 dev log "Files Created or Modified" list. For each listed deliverable, verify it exists on disk with the described change (or absence, for removals). Produce a verification table.
>
> **Run eight verification checks** with output to evidence files. Create the directory: `mkdir -p bellows/knowledge/qa/evidence/executable-remove-phase-3b-3c-2026-05-01`.
>
> Check 1 — `_get_last_completed_step` function removed: `grep -n "_get_last_completed_step" bellows/bellows.py > bellows/knowledge/qa/evidence/executable-remove-phase-3b-3c-2026-05-01/grep_function_removed.txt 2>&1; echo "exit=$?" >> bellows/knowledge/qa/evidence/executable-remove-phase-3b-3c-2026-05-01/grep_function_removed.txt` — expect zero matches in bellows.py (exit code 1 is correct for grep no-match; the file should still be created with "exit=1" appended). If the function name appears in tests/ that's fine — only `bellows.py` must be clean.
>
> Check 2 — DB-resume log line removed: `grep -rn "DB resume" bellows/bellows.py > bellows/knowledge/qa/evidence/executable-remove-phase-3b-3c-2026-05-01/grep_db_resume_removed.txt 2>&1; echo "exit=$?" >> bellows/knowledge/qa/evidence/executable-remove-phase-3b-3c-2026-05-01/grep_db_resume_removed.txt` — expect zero matches.
>
> Check 3 — Phase 3c hash-drift block removed: `grep -n "plan content changed since last step" bellows/bellows.py > bellows/knowledge/qa/evidence/executable-remove-phase-3b-3c-2026-05-01/grep_hash_drift_removed.txt 2>&1; echo "exit=$?" >> bellows/knowledge/qa/evidence/executable-remove-phase-3b-3c-2026-05-01/grep_hash_drift_removed.txt` — expect zero matches.
>
> Check 4 — File parses as Python: `python3 -c "import ast; ast.parse(open('bellows/bellows.py').read()); print('valid')" > bellows/knowledge/qa/evidence/executable-remove-phase-3b-3c-2026-05-01/syntax_valid.txt` — expect output `valid`.
>
> Check 5 — `record_run` still populates plan_slug (NOT removed): `grep -n "plan_slug" bellows/bellows.py > bellows/knowledge/qa/evidence/executable-remove-phase-3b-3c-2026-05-01/grep_plan_slug_preserved.txt` — expect at least one match showing `record_run()` or its surrounding code still references plan_slug. The column was preserved per the F3 design; this check guards against over-removal.
>
> Check 6 — New regression test passes: `cd bellows && python3 -m pytest tests/test_consume_verdicts.py -v > knowledge/qa/evidence/executable-remove-phase-3b-3c-2026-05-01/pytest_regression_test.txt 2>&1` — expect the new test (whatever name the DEV gave it; check dev log) plus the 3 prior tests = 4 tests passing.
>
> Check 7 — Full test suite passes: `cd bellows && python3 -m pytest tests/ > knowledge/qa/evidence/executable-remove-phase-3b-3c-2026-05-01/pytest_full.txt 2>&1` — expect all tests pass (or only the known pre-existing `test_run_step_timeout` failure). Report total count; expect (180 baseline - N deleted Phase 3b/3c tests + 1 new regression test) = approximately 178-180 passing.
>
> Check 8 — Diff bounded to expected files: `git --no-pager diff HEAD~1 HEAD --stat > bellows/knowledge/qa/evidence/executable-remove-phase-3b-3c-2026-05-01/git_diff_stat.txt` — expect changes only to `bellows/bellows.py`, test files identified in Step 1, dev log, and agent-prompt-feedback. Verify net line count is NEGATIVE (removal plan should remove more lines than it adds — ~20 LOC removed minus ~30 LOC of new regression test ≈ small negative or near-zero, but bellows.py specifically should be net negative).
>
> Deposit the QA report at `bellows/knowledge/qa/remove-phase-3b-3c-qa-2026-05-01.md` with a verification table citing each evidence file path. Use the canonical Python file write pattern.
>
> **Then run the mandatory Rule 20 self-check Python block:**
>
> ```python
> # Rule 20 — Mandatory QA Self-Check
> import os, sys
> plan_slug = "executable-remove-phase-3b-3c-2026-05-01"
> qa_report_path = "bellows/knowledge/qa/remove-phase-3b-3c-qa-2026-05-01.md"
> evidence_dir = f"bellows/knowledge/qa/evidence/{plan_slug}/"
> required_evidence_files = [
>     "grep_function_removed.txt",
>     "grep_db_resume_removed.txt",
>     "grep_hash_drift_removed.txt",
>     "syntax_valid.txt",
>     "grep_plan_slug_preserved.txt",
>     "pytest_regression_test.txt",
>     "pytest_full.txt",
>     "git_diff_stat.txt",
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
> Include the literal stdout in the QA report. If the self-check fails, STOP and report. If it passes, proceed.
>
> **Final:** Update `bellows/PROJECT_STATUS.md` and `bellows/knowledge/BACKLOG.md` via two anchored edits:
>
> Edit A (PROJECT_STATUS): Read the file first to identify the verbatim anchor — the entry added earlier today by the session-wrap-v2 plan should be near the top of Completed/Recent Activity. Append a new entry below it: "2026-05-01 (later): Removed Phase 3b/3c DB step-state-resume logic per F3 recommendation in `phase-3b-mechanism-and-cost-benefit-2026-05-01.md`. Dead code that guarded the unsupported manual-rename resume path; verdict-resume path passes resume_step explicitly and never used the DB-query path. Eliminates the slug-collision phantom-resume bug class entirely. plan_slug column preserved for analytics. Net ~20 LOC removed. CEO restart required." Use `Edit` with verbatim anchor.
>
> Edit B (BACKLOG): Read the file first. The "Phase 3b/3c slug-collision" entry was added at the top of Open earlier today by the session-wrap-v2 plan. Move that entry to the Closed section with a closure note. Use `Edit` to (1) remove the verbatim Phase 3b/3c entry from Open, (2) add a new entry at the top of Closed: "**Closed 2026-05-01:** Phase 3b/3c DB step-state-resume slug-collision. Diagnostic at `knowledge/research/phase-3b-mechanism-and-cost-benefit-2026-05-01.md` confirmed phantom-resume mechanism with literal SQL evidence (rows 554-556 from prior session triggered phantom resume of fresh v1 wrap deposit). Q6 cost-benefit recommended F3 (remove dead code) over F1 (patch slug+hash) and F2 (block on hash drift) — Phase 3b/3c guards a manual-rename resume path that's unsupported per Rule 25, and the supported verdict-resume path passes resume_step explicitly without consulting the DB. Reference: `executable-remove-phase-3b-3c-2026-05-01`."
>
> Standard prompt feedback protocol. Final commit: `cd /Users/marklehn/Desktop/GitHub && git add bellows/knowledge/qa/remove-phase-3b-3c-qa-2026-05-01.md bellows/knowledge/qa/evidence/executable-remove-phase-3b-3c-2026-05-01/ bellows/PROJECT_STATUS.md bellows/knowledge/BACKLOG.md bellows/knowledge/research/agent-prompt-feedback.md && git commit -m "qa: Phase 3b/3c removal verified + close BACKLOG slug-collision entry"`. **STOP.** Do NOT move this plan to Done/. Per the disable-auto-close model, the Planner performs the terminal move after Rule 22 verification passes.
>
> **Deposits:**
> - `bellows/knowledge/qa/remove-phase-3b-3c-qa-2026-05-01.md`
> - `bellows/knowledge/qa/evidence/executable-remove-phase-3b-3c-2026-05-01/`
> - `bellows/PROJECT_STATUS.md`
> - `bellows/knowledge/BACKLOG.md`
> - `bellows/knowledge/research/agent-prompt-feedback.md`
