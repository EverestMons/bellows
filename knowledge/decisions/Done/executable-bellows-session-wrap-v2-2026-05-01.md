# bellows — Session Wrap 2026-05-01 (v2)
**Date:** 2026-05-01 | **Tier:** Small | **Test Scope:** full-suite | **Execution:** Step 1 (DEV) → Step 2 (Documentation) → Step 3 (QA)

## CEO Context

**Test Scope: full-suite** — Rule 21 session-end requirement. Multiple plans in this session modified `bellows.py`, tests, and config; the session-end suite captures the cumulative state.

**Why -v2 in the slug:** the original wrap deposited as `executable-bellows-session-wrap-2026-05-01` collided with stale DB step-state from an earlier session's plan with the same slug (orphan verdict-request `verdict-request-bellows-session-wrap-2026-05-01-step-2.md` from 16:46:56 still in pending/). Phase 3b's `_get_last_completed_step` queried by slug, found "step 2 complete" from the prior plan, and resumed at Step 3 — Step 1 and Step 2 deliverables were never produced. Phase 3c's plan-hash drift warning fired correctly (`shadow=0b32... current=c64d...`) but the resume happened anyway because the warning is non-blocking. The original wrap was halted via verdict; this v2 uses a unique slug to bypass DB resume. **Adding a BACKLOG entry in Step 2 to capture this finding** — it's a real Phase 3b reliability gap.

**This wrap closes a session that shipped 4 plans:**

1. `executable-inactivity-timeout-bump-1800s-2026-05-01` — raised `step_inactivity_timeout_seconds` 300 → 1800 (operational unblock)
2. `diagnostic-cleanup-verdicts-call-site-gap-2026-05-01` — halted (killed by old 300s threshold before bump landed)
3. `diagnostic-cleanup-verdicts-call-site-gap-rerun-2026-05-01` — identified slug normalization mismatch as root cause of stranded verdict files
4. `executable-cleanup-slug-normalization-2026-05-01` — closed BACKLOG #3 with 4 edits to `bellows.py` + 3 regression tests

**Three governance/BACKLOG items to capture:**
- LESSON: Planner read `bellows/config.json` directly during plan-writing despite "configuration files" being on the Planner CANNOT-read list. Recurring class.
- LESSON: Rule 13 anchoring gap — plan didn't anchor `test_bellows.py` for fixup; DEV correctly fixed on initiative.
- BACKLOG: Phase 3b/3c slug-collision bug — DB step-state-resume keyed by slug alone, not by (slug + plan-hash); cross-plan slug collisions trigger phantom resumes.
- BACKLOG: Test 3 in `test_consume_verdicts.py` uses inline-replicated startup-sweep logic; future refactor to extract `_perform_startup_sweep()` would let test exercise production code.

## How to Run This Plan

Paste the bootstrap into Claude Code. The agent reads the full plan file and executes Step 1 ONLY. After each step reports Complete, CEO confirms ("ok") to advance.

**Bootstrap:**
```
Read the plan at bellows/knowledge/decisions/executable-bellows-session-wrap-v2-2026-05-01.md. Execute Step 1 ONLY. After completing Step 1, STOP and wait for my confirmation. Do NOT proceed to Step 2 or move the plan to Done.
```

---
---

## STEP 1 — BELLOWS DEVELOPER

---

> **FIRST — before doing anything else, claim this plan:** `import shutil; shutil.move("bellows/knowledge/decisions/executable-bellows-session-wrap-v2-2026-05-01.md", "bellows/knowledge/decisions/in-progress-executable-bellows-session-wrap-v2-2026-05-01.md")`.
>
> You are the Bellows Developer. Skip specialist file and glossary reads — this is a session-end test run with evidence capture.
>
> **Run the full test suite and capture output.** Create the evidence directory: `mkdir -p bellows/knowledge/qa/evidence/session-2026-05-01`. Then run: `cd bellows && python3 -m pytest tests/ > knowledge/qa/evidence/session-2026-05-01/pytest_session_end.txt 2>&1`. Expect 183 passed + 1 pre-existing failure (`test_run_step_timeout` in `test_runner_parser.py`, unrelated to this session's work). If the failure count differs from 1, flag in the dev log — that's a regression.
>
> **Compute before/after suite delta.** This session's first plan ran on a 180/181 baseline (per `executable-cleanup-slug-normalization-2026-05-01` QA report). Report in dev log: starting baseline (180/181), ending baseline (counts from session_end), delta (new tests added).
>
> **Deposit dev log** at `bellows/knowledge/development/session-wrap-dev-log-2026-05-01.md` containing: (a) full suite passed/failed counts, (b) list of any new failures (should be none), (c) before/after delta vs session start. Use the canonical Python file write pattern.
>
> Standard prompt feedback protocol → `bellows/knowledge/research/agent-prompt-feedback.md`.
>
> **Commit:** `cd /Users/marklehn/Desktop/GitHub && git add bellows/knowledge/qa/evidence/session-2026-05-01/ bellows/knowledge/development/session-wrap-dev-log-2026-05-01.md bellows/knowledge/research/agent-prompt-feedback.md && git commit -m "qa: session-end full suite 2026-05-01"`.
>
> **Deposits:**
> - `bellows/knowledge/qa/evidence/session-2026-05-01/`
> - `bellows/knowledge/development/session-wrap-dev-log-2026-05-01.md`
> - `bellows/knowledge/research/agent-prompt-feedback.md`
>
> **STOP. Do NOT proceed to Step 2. Do NOT move the plan to Done. Wait for CEO confirmation before continuing.**

---
---

## STEP 2 — BELLOWS DOCUMENTATION ANALYST

---

> Before starting, read `bellows/knowledge/development/session-wrap-dev-log-2026-05-01.md` and check the Output Receipt status. If status is not Complete, stop and report.
>
> You are the Bellows Documentation Analyst. Skip specialist file and glossary reads — this is governance and project-doc updates with anchored edits.
>
> **Edit 1 — PROJECT_STATUS.md.** Read `bellows/PROJECT_STATUS.md` first to identify the existing "Recent Activity" or equivalent section. Use the `Edit` tool with a verbatim anchor. Add a new entry covering the 2026-05-01 session: "2026-05-01 (session): Closed BACKLOG #3 (cleanup_verdicts_for_slug call-site gap → diagnosed as slug normalization mismatch, fixed via cleanup_slug + lookup_slug + Done/-loop removal in startup sweep, +3 regression tests; commit `bc09bb5`). Raised step_inactivity_timeout_seconds 300→1800 (operational unblock for SA cross-referencing tasks). Halted one diagnostic plan that was killed by the old timeout before re-running successfully under the new threshold. Halted original session-wrap plan due to Phase 3b slug-collision bug; re-shipped as -v2."
>
> **Edit 2 — Append two lessons to `/Users/marklehn/Desktop/GitHub/PLANNER_TEMPLATE.md`.** This file is at the governance root, NOT inside bellows/. Read it first to identify the Lessons Learned table and the most recent row. Use the `Edit` tool with a verbatim anchor — anchor on the most recent row's verbatim text and append two new rows after it. Lesson rows:
>
> Row A: `| 2026-05-01 | Planner read `bellows/config.json` directly during plan-writing despite "configuration files" being on the CANNOT-read list. Same pattern logged 2026-03-24 (Planner read migration files), 2026-04-07 (Planner reading code despite explicit guardrail). The temptation is the same every time: "I need to know the schema before writing the plan; just one file feels faster than writing a diagnostic." It's not — it bypasses specialist guardrails AND removes the agent's chance to flag schema drift. **Reinforcement, not new rule:** the existing guardrails are correct; the discipline gap is in the moment of temptation. Future Planner sessions: when about to read a config file, source file, or schema definition to "confirm something cheaply," that confirmation is the diagnostic. Write it as a one-line agent prompt instead. |`
>
> Row B: `| 2026-05-01 | Rule 13 anchoring gap: when a plan modifies production code that an existing test encodes as "correct" (i.e., the test was passing because it was testing the buggy path), the plan should anchor that test for update — not let the DEV discover it on initiative. Observed in `executable-cleanup-slug-normalization-2026-05-01`: the production fix (slug normalization) made `test_consume_verdicts_deletes_pending_file` in `test_bellows.py` fail because the existing test was constructing pending files with the prefixed-slug filename convention (which production no longer produces). DEV correctly fixed the test on initiative and documented in dev log — outcome was clean, but the cleaner pattern is for the Planner to identify "this test will fail after the fix" during plan-writing. **How to apply:** when writing a fix plan that changes the shape of a value (slug, filename, schema field, etc.), grep the test directory for tests that construct that shape, and anchor those tests in the plan's deliverables list. The DEV stays in scope; nothing surprises. |`
>
> **Important:** the PLANNER_TEMPLATE.md file lives at the governance root (`/Users/marklehn/Desktop/GitHub/PLANNER_TEMPLATE.md`), which means edits commit to the governance-root repo (`/Users/marklehn/Desktop/GitHub/`). Both bellows files and governance-root PLANNER_TEMPLATE live in the same physical repo (governance root contains bellows as a subdirectory), so edits land in one repo but should be split into separate commits with distinct messages so the git log clearly shows what changed where.
>
> **Edit 3 — Append TWO BACKLOG entries to `bellows/knowledge/BACKLOG.md`.** Read the file first to identify the verbatim first line under the "## Open" section header. Use the `Edit` tool with a verbatim anchor — anchor on the first existing Open entry and prepend BOTH new entries above it (so the most-recent BACKLOG entry is at the top). Entry texts:
>
> Entry 1 (NEW — Phase 3b slug-collision finding):
>
> `- 2026-05-01: Phase 3b/3c DB step-state-resume slug-collision bug. The DB resume mechanism in bellows.py keys by plan slug alone (via _get_last_completed_step). When two plans across different sessions share a slug (e.g., executable-bellows-session-wrap-2026-05-01 deposited fresh, while a prior plan with the same slug left orphan DB step-state from an earlier session), the new plan triggers phantom resume. Observed today on the 2026-05-01 session-wrap: prior orphan verdict-request (mtime 16:46:56) for slug bellows-session-wrap-2026-05-01 left DB state showing "last completed step 2." When the new wrap was deposited, Phase 3b queried by slug, found step 2 complete, resumed at Step 3 — but Step 1 and Step 2 deliverables were never produced (the new plan's Step 1+2 work was different from the prior plan's). Phase 3c plan-hash drift warning fired correctly (shadow=0b32... current=c64d...) but the resume happened anyway because the warning is non-blocking. Recovery: halted the original plan via verdict, re-shipped as -v2 with unique slug to bypass DB resume. Fix shape: (a) make Phase 3c drift warning blocking when hash mismatch detected (likely too aggressive — legitimate same-plan edits would also be blocked), (b) key DB step-state by (slug, plan-hash) tuple instead of slug alone — different plans can never collide, same-plan edits resume correctly, (c) clear DB step-state when a plan transitions to terminal state (Done/halted) so orphan rows can't accumulate. Recommend (b) + (c) together: (b) prevents the collision class, (c) prevents orphan accumulation. Medium priority — collision is rare in practice (requires same-day same-slug-pattern collision) but the failure mode is silent and confusing. Surfaced during 2026-05-01 session wrap; resolved tactically with unique slug. References: heartbeat output "DB resume — last completed step 2, resuming at 3" + "plan content changed since last step — shadow=0b32403e5789 current=c64d9688fd4e".`
>
> Entry 2 (test-quality improvement):
>
> `- 2026-05-01: test_startup_sweep_removes_done_plan_orphans uses inline-replicated sweep logic — the regression test for the startup sweep fix (shipped today via executable-cleanup-slug-normalization-2026-05-01) replicates the startup-sweep collection-and-removal logic inline in the test file rather than calling Bellows.start() and patching the observer/event-loop apparatus. Documented as a NOTE comment in the test. Bounded drift risk: if Bellows.start() refactors and the production startup sweep diverges from the test's inline replica, the test continues to pass while production regresses. Refactor opportunity: extract _perform_startup_sweep() as a private method on Bellows that both start() and the test can call. ~10 LOC refactor, eliminates the indirection. Low priority — fix is verified directly via grep evidence (grep_active_slugs.txt), the bug-regression test (test_cleanup_normalizes_prefixed_verdict_slug) DOES exercise production _consume_verdicts directly. Test-quality improvement, not a reliability gap.`
>
> Standard prompt feedback protocol.
>
> **Two commits required (split-commit pattern):**
>
> Commit 1 (project files): `cd /Users/marklehn/Desktop/GitHub && git add bellows/PROJECT_STATUS.md bellows/knowledge/BACKLOG.md bellows/knowledge/research/agent-prompt-feedback.md && git commit -m "docs: session wrap 2026-05-01 — PROJECT_STATUS + 2 BACKLOG entries"`
>
> Commit 2 (governance-root): `cd /Users/marklehn/Desktop/GitHub && git add PLANNER_TEMPLATE.md && git commit -m "docs: PLANNER_TEMPLATE lessons — config-read recurrence + Rule 13 test-anchoring gap (2026-05-01)"`
>
> **Deposits:**
> - `bellows/PROJECT_STATUS.md`
> - `/Users/marklehn/Desktop/GitHub/PLANNER_TEMPLATE.md`
> - `bellows/knowledge/BACKLOG.md`
> - `bellows/knowledge/research/agent-prompt-feedback.md`
>
> **STOP. Do NOT proceed to Step 3. Do NOT move the plan to Done. Wait for CEO confirmation before continuing.**

---
---

## STEP 3 — BELLOWS QA

---

> Before starting, read `bellows/PROJECT_STATUS.md`, `bellows/knowledge/BACKLOG.md`, and `/Users/marklehn/Desktop/GitHub/PLANNER_TEMPLATE.md` to verify Step 2 edits landed. If any anchor was missed, stop and report.
>
> You are the Bellows QA Agent. Skip specialist file and glossary reads — this is verification of documentation edits.
>
> **FIRST — Deliverable Verification (Rule 17).** Read Step 1 dev log and Step 2 commit log. Verify each deliverable exists with the described change. Produce a verification table.
>
> **Run six verification checks** with output to evidence files. Create the directory: `mkdir -p bellows/knowledge/qa/evidence/executable-bellows-session-wrap-v2-2026-05-01`.
>
> Check 1 — Session-end suite evidence file exists and shows expected pass count: `tail -5 bellows/knowledge/qa/evidence/session-2026-05-01/pytest_session_end.txt > bellows/knowledge/qa/evidence/executable-bellows-session-wrap-v2-2026-05-01/session_end_summary.txt` — expect tail to include "passed" with the count from the dev log.
>
> Check 2 — PROJECT_STATUS includes the 2026-05-01 session entry: `grep -A 1 "2026-05-01 (session)" bellows/PROJECT_STATUS.md > bellows/knowledge/qa/evidence/executable-bellows-session-wrap-v2-2026-05-01/grep_project_status.txt` — expect match showing the new entry text.
>
> Check 3 — PLANNER_TEMPLATE has both new lessons. Run two greps: `grep "Planner read.*config.json.*directly" /Users/marklehn/Desktop/GitHub/PLANNER_TEMPLATE.md > bellows/knowledge/qa/evidence/executable-bellows-session-wrap-v2-2026-05-01/lessons_check.txt` and `grep "Rule 13 anchoring gap" /Users/marklehn/Desktop/GitHub/PLANNER_TEMPLATE.md >> bellows/knowledge/qa/evidence/executable-bellows-session-wrap-v2-2026-05-01/lessons_check.txt` — expect both lines present (file should have grown by exactly 2 new rows).
>
> Check 4 — BACKLOG has BOTH new entries near top of Open: `head -20 bellows/knowledge/BACKLOG.md > bellows/knowledge/qa/evidence/executable-bellows-session-wrap-v2-2026-05-01/grep_backlog.txt` — expect to see "Phase 3b/3c DB step-state-resume slug-collision" AND "test_startup_sweep_removes_done_plan_orphans uses inline" both visible in the head output.
>
> Check 5 — Both commits landed: `git --no-pager log --oneline -5 > bellows/knowledge/qa/evidence/executable-bellows-session-wrap-v2-2026-05-01/git_log_commits.txt` — expect two recent commits matching the Step 2 messages.
>
> Check 6 — Diff bounded to expected files: `git --no-pager diff HEAD~2 HEAD --stat > bellows/knowledge/qa/evidence/executable-bellows-session-wrap-v2-2026-05-01/git_diff_stat.txt` — expect changes only to: `bellows/PROJECT_STATUS.md`, `bellows/knowledge/BACKLOG.md`, `bellows/knowledge/research/agent-prompt-feedback.md`, `PLANNER_TEMPLATE.md`. No unexpected files.
>
> Deposit the QA report at `bellows/knowledge/qa/session-wrap-v2-qa-2026-05-01.md` with the verification table citing each evidence file.
>
> **Then run the mandatory Rule 20 self-check Python block:**
>
> ```python
> # Rule 20 — Mandatory QA Self-Check
> import os, sys
> plan_slug = "executable-bellows-session-wrap-v2-2026-05-01"
> qa_report_path = "bellows/knowledge/qa/session-wrap-v2-qa-2026-05-01.md"
> evidence_dir = f"bellows/knowledge/qa/evidence/{plan_slug}/"
> required_evidence_files = [
>     "session_end_summary.txt",
>     "grep_project_status.txt",
>     "lessons_check.txt",
>     "grep_backlog.txt",
>     "git_log_commits.txt",
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
> Include the literal stdout in the QA report. Standard prompt feedback protocol.
>
> **Final commit:** `cd /Users/marklehn/Desktop/GitHub && git add bellows/knowledge/qa/session-wrap-v2-qa-2026-05-01.md bellows/knowledge/qa/evidence/executable-bellows-session-wrap-v2-2026-05-01/ bellows/knowledge/research/agent-prompt-feedback.md && git commit -m "qa: session wrap v2 verified — all 4 plans this session in proper closure state"`. **STOP.** Do NOT move this plan to Done/. Per the disable-auto-close model, the Planner performs the terminal move after Rule 22 verification passes.
>
> **Deposits:**
> - `bellows/knowledge/qa/session-wrap-v2-qa-2026-05-01.md`
> - `bellows/knowledge/qa/evidence/executable-bellows-session-wrap-v2-2026-05-01/`
> - `bellows/knowledge/research/agent-prompt-feedback.md`
