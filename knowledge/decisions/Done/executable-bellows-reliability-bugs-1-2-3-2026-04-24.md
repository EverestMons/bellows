# Bellows — Reliability Bugs 1, 2, 3 (BACKLOG top three, 2026-04-24)
**Date:** 2026-04-24 | **Tier:** Medium | **Test Scope:** targeted | **Execution:** Step 1 (SA) → Step 2 (DEV) → Step 3 (QA)

## How to Run This Plan

Paste the bootstrap prompt into Claude Code. The agent reads the full plan file and executes Step 1 ONLY. After completing Step 1, the agent STOPS and waits for CEO confirmation ("ok") before proceeding to Step 2. This continues step by step until the plan is complete. The agent must never skip steps, auto-chain to the next step, or move the plan to Done without completing all steps including QA.

**Bootstrap prompt:**
```
Read the plan at bellows/knowledge/decisions/executable-bellows-reliability-bugs-1-2-3-2026-04-24.md. Execute Step 1 ONLY. After completing Step 1, STOP and wait for my confirmation. Do NOT proceed to Step 2 or move the plan to Done.
```

---
---

## STEP 1 — BELLOWS SYSTEMS ANALYST

---

> **FIRST — before doing anything else, claim this plan:** `import shutil; shutil.move("bellows/knowledge/decisions/executable-bellows-reliability-bugs-1-2-3-2026-04-24.md", "bellows/knowledge/decisions/in-progress-executable-bellows-reliability-bugs-1-2-3-2026-04-24.md")`.
>
> You are the Bellows Systems Analyst. Read your specialist file and domain glossary first. Also read `bellows/knowledge/architecture/failure-3-ordering-2026-04-24.md` for line-level context on the pause branch (L332-358) and auto-close branch (L363-381) already mapped today. This blueprint shape-verifies the fixes for three reliability bugs enumerated in `bellows/knowledge/BACKLOG.md` (the three dated 2026-04-24 at the top of Open). **Your job is NOT to redesign — the CEO wrote fix shapes already. Your job is to confirm each shape against live code, surface edge cases, and produce a blueprint DEV can implement against verbatim.** Skip specialist file and glossary reads if they do not contain relevant Bellows-side code knowledge (they mostly do not) — this is a code-tracing task.
>
> **Bug 1 — `_consume_verdicts` unconditional `shutil.move` to `processed-*`.** Locate `_consume_verdicts()` in `bellows.py`. Read the full function end-to-end. Identify: (a) the outer verdict-iteration loop, (b) the inner plan-search loop, (c) the terminal `shutil.move(str(resolved_dir / fname), str(processed_path))` that fires unconditionally. Confirm the CEO's fix shape: add a `plan_matched = False` before the inner loop, set to `True` inside the inner loop on successful dispatch (at the `break`), gate the final `shutil.move` on `if plan_matched:`. If `plan_matched` is False, leave the verdict in `resolved/` and print/log a warning so it retries on next scan. **Edge cases to enumerate and resolve in the blueprint:** (i) legitimate stale verdicts — if the plan slug corresponds to a plan already in `Done/` (e.g., verdict posted for a plan that auto-closed before the verdict landed), leaving the verdict in `resolved/` would create a permanent orphan that trips this same branch every scan, looping the warning log forever; propose whether to still move-to-processed in this specific case (plan slug has no in-progress/verdict-pending/executable form on disk AND has a Done/ form) OR to move to a separate `orphaned/` subdirectory OR to rely on the existing startup sweep to clean these. Recommend one path. (ii) `resolved/` dir empty or missing — confirm current code is defensive. (iii) inner loop raises exception — confirm `plan_matched` is correctly False in that branch. Cite exact line numbers for all references.
>
> **Bug 2 — pause-time rename wrong-path when plan enters at `in-progress-*`.** Locate `run_plan()` in `bellows.py`, specifically the pause-branch rename logic (per today's architecture doc: L332-358, look for `inprogress_path = os.path.join(plan_dir, f"in-progress-{plan_filename}")`). Confirm the bug: when `plan_filename` already carries the `in-progress-` prefix (resume dispatch case), `inprogress_path` becomes `in-progress-in-progress-{name}` which does not exist on disk, and the `if os.path.exists(inprogress_path)` guard silently skips the rename-to-`verdict-pending-*`. **Fix variant choice:** BACKLOG lists two options — (a) canonicalize `plan_filename` by stripping the lifecycle prefix before constructing `inprogress_path`, or (b) use the existing `plan_path` variable directly since it reflects actual on-disk location. Read the surrounding function to determine: does `plan_path` remain current across the full step lifecycle (including after intermediate renames, e.g., shadow-cache claim or any other rename hops), or does it become stale? If `plan_path` is reliably current, variant (b) is one line and zero new failure modes. If `plan_path` can be stale, variant (a) is safer. Pick the variant you can defend; state your reasoning. Also verify: are there OTHER call sites in `bellows.py` or adjacent modules that construct `in-progress-{plan_filename}` with the same assumption? If yes, enumerate them — any fix shape must cover all sites or explain why it does not.
>
> **Bug 3 — `extract_total_steps()` case-sensitive regex.** Locate `extract_total_steps()` in `bellows.py`. Read the function and all its callers. Confirm: (i) the regex is `r"^## STEP"` with `re.MULTILINE`, (ii) a plan with `## Step 1 — X` yields 0, (iii) the skip branch at roughly L252-257 moves such plans to `Done/` without dispatching. **Fix:** add `re.IGNORECASE` to the flags AND add a secondary detection — if the case-sensitive count is 0 but a case-insensitive `^##\s+step` scan matches, log a warning (`WARNING: plan has step headers but case does not match expected "## STEP N" — count=X matched case-insensitively`). This gives both correctness and loud-fail visibility on future mixed-case authoring. Enumerate callers of `extract_total_steps()` and confirm none depend on the current case-sensitive behavior (e.g., a caller that passes plan text known to have lowercase `step` in non-header contexts that would now accidentally match). If any caller would regress, call it out.
>
> **Deliverable — blueprint file.** Produce a single blueprint at `bellows/knowledge/architecture/reliability-bugs-1-2-3-blueprint-2026-04-24.md` with the following structure: (1) per-bug section containing current-code excerpt with line numbers, confirmed fix shape, edge cases resolved, any caller impact; (2) unit test enumeration — list the specific test cases DEV must add, per bug, with pass/fail expectation; (3) interaction matrix — does fixing bug 1 in isolation produce any regression without bug 2 also fixed, and vice versa (the BACKLOG notes they compound); (4) restart requirement — mark explicitly that all three fixes require a Bellows daemon restart to load, since they are in `bellows.py` (the running daemon holds pre-fix code in memory).
>
> **Deposits:**
> - `bellows/knowledge/architecture/reliability-bugs-1-2-3-blueprint-2026-04-24.md`
>
> Standard prompt feedback protocol → `bellows/knowledge/research/agent-prompt-feedback.md`.
>
> **STOP. Do NOT proceed to Step 2. Do NOT move the plan to Done. Wait for CEO confirmation before continuing.**

---
---

## STEP 2 — BELLOWS DEVELOPER

---

> Before starting, read `bellows/knowledge/architecture/reliability-bugs-1-2-3-blueprint-2026-04-24.md` and check the Output Receipt status field. If status is not Complete, stop and report the issue to the CEO before proceeding.
>
> You are the Bellows Developer. Read your specialist file first. Skip the domain glossary — this is a Bellows-internal code change, no domain terminology involved.
>
> Implement the three fixes specified in the blueprint. Cite blueprint sections rather than restating specifications. **Bug 1:** apply the `plan_matched` boolean gate to `_consume_verdicts()` per blueprint Section 1, including the edge-case handling the blueprint recommends for the stale-verdict case. **Bug 2:** apply the fix variant the blueprint chose (either canonicalize `plan_filename` or use `plan_path` directly) to the pause-branch rename per blueprint Section 2. If the blueprint identified additional call sites with the same pattern, fix those too — enumerate them in your dev log. **Bug 3:** add `re.IGNORECASE` to the regex in `extract_total_steps()` and add the case-mismatch warning per blueprint Section 3.
>
> Add unit tests per the blueprint's unit test enumeration (Section "unit test enumeration"). Each bug gets its own test cases. At minimum: (a) bug 1 — test that a verdict with no matching plan remains in `resolved/` (not moved to `processed/`) AND a verdict with a matching plan does move to `processed/` as before; (b) bug 2 — test that a plan entering the pause branch with `in-progress-` prefix already on `plan_filename` correctly renames to `verdict-pending-*` (no double-prefix); (c) bug 3 — test that `## Step 1 — X` plans are counted correctly AND the warning fires for case mismatch. Add any additional cases the blueprint specifies.
>
> Run the targeted test suite after changes: `cd bellows && pytest tests/ -v`. All tests must pass before committing. If any existing test fails, stop and report — do not attempt to patch around a regression.
>
> Commit with message: `fix(bellows): reliability bugs 1-3 — verdict consume gate, pause-rename canonical path, case-insensitive step count`.
>
> Write a dev log at `bellows/knowledge/development/reliability-bugs-1-2-3-dev-log-2026-04-24.md` with: files changed (with line numbers), tests added (with names), full targeted pytest output pasted into the log, commit hash, notes on any edge cases encountered during implementation that the blueprint did not anticipate.
>
> **Deposits:**
> - `bellows/knowledge/development/reliability-bugs-1-2-3-dev-log-2026-04-24.md`
>
> Standard prompt feedback protocol → `bellows/knowledge/research/agent-prompt-feedback.md`.
>
> **STOP. Do NOT proceed to Step 3. Do NOT move the plan to Done. Wait for CEO confirmation before continuing.**

---
---

## STEP 3 — BELLOWS QA

---

> Before starting, read `bellows/knowledge/development/reliability-bugs-1-2-3-dev-log-2026-04-24.md` and check the Output Receipt status field. If status is not Complete, stop and report the issue to the CEO before proceeding.
>
> You are the Bellows QA Specialist. Read your specialist file first. Skip the domain glossary.
>
> **FIRST — Deliverable Verification.** Read the DEV Output Receipt "Files Created or Modified (Code)" list. For EVERY listed file: verify it exists on disk and contains the described change (grep for key content). Specifically: (a) grep `bellows.py` for `plan_matched` and confirm the boolean gate is present in `_consume_verdicts` — deposit grep output to `bellows/knowledge/qa/evidence/executable-bellows-reliability-bugs-1-2-3-2026-04-24/grep_plan_matched.txt`; (b) grep `bellows.py` for the bug 2 fix (either `plan_filename.lstrip` / `re.sub` pattern if canonicalization was chosen, OR `plan_path` usage if variant b was chosen) — deposit to `grep_bug2_fix.txt`; (c) grep `bellows.py` for `re.IGNORECASE` in `extract_total_steps` — deposit to `grep_ignorecase.txt`; (d) verify the dev log's tests-added list is present in `tests/` — deposit ls output to `ls_tests_added.txt`. Produce a verification table: `| Deliverable | Expected | Status (✅/❌) | Evidence |`. Any ❌ blocks the plan from moving to Done.
>
> **SECOND — Targeted test regression.** Run `cd bellows && pytest tests/ -v` and pipe full output to `bellows/knowledge/qa/evidence/executable-bellows-reliability-bugs-1-2-3-2026-04-24/pytest_targeted.txt`. All tests must pass. Compare test count before (from DEV's dev log) and after (this run) — they should match DEV's count or exceed it (new tests added). If any test fails, mark Critical and halt.
>
> **THIRD — Behavioral smoke for each bug.** (i) Bug 1 smoke: write a synthetic `resolved/` verdict file whose slug does not match any on-disk plan, call `_consume_verdicts` via a small Python harness, confirm the verdict remains in `resolved/` and is NOT moved to `processed/`. Capture output to `smoke_bug1.txt`. (ii) Bug 2 smoke: construct a mock `plan_filename` with `in-progress-` prefix, exercise the pause-rename path (unit test already covers this but a runtime invocation confirms no surprises) — capture to `smoke_bug2.txt`. (iii) Bug 3 smoke: feed a plan string containing `## Step 1 — X` to `extract_total_steps` directly, confirm it returns 1 and the warning fires, capture to `smoke_bug3.txt`. These smokes are light — unit tests are the primary verification.
>
> **FOURTH — write QA report** to `bellows/knowledge/qa/reliability-bugs-1-2-3-qa-2026-04-24.md` with: (a) deliverable verification table, (b) targeted test result summary citing `pytest_targeted.txt`, (c) per-bug smoke results citing evidence files, (d) explicit REMINDER section at the top of the report stating `REMINDER: restart Bellows daemon to load bug fixes from bellows.py — running daemon holds pre-fix code in memory until restart`. Mark severity per finding if any issues surface.
>
> **FIFTH — Planner will perform Rule 22 verification and Done/ move.** Do NOT move the plan to Done yourself. Do NOT update PROJECT_STATUS.md (Planner or Documentation Agent will handle via separate flow post-verification). Report completion via Output Receipt and wait.
>
> **Deposits:**
> - `bellows/knowledge/qa/reliability-bugs-1-2-3-qa-2026-04-24.md`
> - `bellows/knowledge/qa/evidence/executable-bellows-reliability-bugs-1-2-3-2026-04-24/` (multiple files per Rule 20 self-check)
>
> Standard prompt feedback protocol → `bellows/knowledge/research/agent-prompt-feedback.md`.
>
> **SIXTH — Rule 20 Mandatory QA Self-Check.** Execute the following Python block verbatim. Include its literal stdout in the QA report. If output is FAILED, STOP — do NOT report Complete, wait for CEO guidance.
>
> ```python
> # Rule 20 — Mandatory QA Self-Check
> import os, sys
> plan_slug = "executable-bellows-reliability-bugs-1-2-3-2026-04-24"
> qa_report_path = "bellows/knowledge/qa/reliability-bugs-1-2-3-qa-2026-04-24.md"
> evidence_dir = f"bellows/knowledge/qa/evidence/{plan_slug}/"
> required_evidence_files = [
>     "grep_plan_matched.txt",
>     "grep_bug2_fix.txt",
>     "grep_ignorecase.txt",
>     "ls_tests_added.txt",
>     "pytest_targeted.txt",
>     "smoke_bug1.txt",
>     "smoke_bug2.txt",
>     "smoke_bug3.txt",
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
> **STOP. Do NOT move the plan to Done. Do NOT update PROJECT_STATUS.md. Planner will perform Rule 22 verification and terminal housekeeping.**
