# Bellows — Phase 3b Restart Canary
**Date:** 2026-04-30 | **Tier:** Small | **Test Scope:** targeted | **Execution:** Step 1 (BELLOWS_DEVELOPER) → Step 2 (BELLOWS_QA)
**Priority:** 1

## Context

Phase 3b shipped 2026-04-28 (executable-step-state-resume-phase-3b-2026-04-28, commit on `bellows.db` migration + `record_run` signature + `_get_last_completed_step` helper). The CEO has confirmed Bellows daemon was restarted post-commit. This canary validates the running daemon actually loaded the new code by depositing a trivial diagnostic plan whose successful completion is implicit evidence (DDL migration ran, `record_run()` accepts `plan_slug`, no crash on INSERT) and whose QA step produces explicit positive evidence (DB query confirms `plan_slug` column populated for this run, helper returns expected value).

The canary also implicitly validates two other 2026-04-28 fixes loaded in the same restart: BACKLOG #2 (read-class permission gate exemption — Grep/Glob/Read denials no longer block) and BACKLOG #4 (monorepo scope_check fix — `--relative -- .` scopes diff to project subtree). Triple-validation in one canary.

## How to Run This Plan

Paste the bootstrap prompt into Claude Code. The agent reads the full plan file and executes Step 1 ONLY. After completing Step 1, the agent STOPS and waits for CEO confirmation ("ok") before proceeding to Step 2. Step 2 ends with the Planner-owned move-to-Done pattern (per Rule 23 v4.27): the QA agent does NOT move the plan — it commits its work and stops; the Planner performs the terminal Done/ move after Rule 22 verification passes.

**Bootstrap:**
```
Read the plan at bellows/knowledge/decisions/executable-canary-phase-3b-restart-2026-04-30.md. Execute Step 1 ONLY. After completing Step 1, STOP and wait for my confirmation. Do NOT proceed to Step 2 or move the plan to Done.
```

---
---

## STEP 1 — BELLOWS_DEVELOPER

---

> **FIRST — before doing anything else, claim this plan:** `import shutil; shutil.move("bellows/knowledge/decisions/executable-canary-phase-3b-restart-2026-04-30.md", "bellows/knowledge/decisions/in-progress-executable-canary-phase-3b-restart-2026-04-30.md")`. You are the Bellows Developer. Skip specialist file and glossary reads — this is a code-tracing canary task. Read `bellows/bellows.py` lines 30-100 to confirm three Phase 3b artifacts exist in source: (a) the `runs` table DDL includes `plan_slug TEXT`, (b) the `additions` dict in `migrate_db()` includes `"plan_slug": "TEXT"`, (c) somewhere in the file there is a function definition `def _get_last_completed_step(`. Then read `bellows/verdict.py` to confirm `slug_from_path` is exposed publicly (no leading underscore). Deposit findings as a 5-7 line markdown file confirming all four artifacts present, citing the line numbers where you found them. Use this canonical Python pattern to write the file: `content = """..."""` followed by `with open("bellows/knowledge/research/phase-3b-restart-canary-2026-04-30.md", "w") as f: f.write(content)`. Standard prompt feedback protocol → `bellows/knowledge/research/agent-prompt-feedback.md`. Commit both the findings file and the feedback append in one commit with message "docs: phase 3b restart canary — code artifacts confirmed". **Deposits:** - `bellows/knowledge/research/phase-3b-restart-canary-2026-04-30.md` - `bellows/knowledge/research/agent-prompt-feedback.md`
>
> **STOP. Do NOT proceed to Step 2. Do NOT move the plan to Done. Wait for CEO confirmation before continuing.**

---
---

## STEP 2 — BELLOWS_QA

---

> Before starting, read `bellows/knowledge/research/phase-3b-restart-canary-2026-04-30.md` and check the Output Receipt status field. If status is not Complete, stop and report the issue to the CEO before proceeding. You are the Bellows QA agent. Skip specialist file and glossary reads — this is a mechanical DB-verification task. **FIRST — Deliverable Verification.** Read the prior DEV step Output Receipt "Files Created or Modified (Code)" and "Files Deposited" lists. For every listed file: verify existence on disk via `os.path.isfile`. Produce a verification table: | Deliverable | Expected | Status (✅/❌) | Evidence |. **Phase 3b DB Assertions.** Open `bellows/bellows.db` via `sqlite3.connect()` and run three queries, writing literal output of each to the named evidence file: (a) `PRAGMA table_info(runs)` — pipe to `bellows/knowledge/qa/evidence/canary-phase-3b-restart-2026-04-30/pragma_runs.txt`; verify `plan_slug` appears in output. (b) `SELECT plan_slug, plan_path, step, status FROM runs WHERE plan_path LIKE '%canary-phase-3b-restart%' ORDER BY id DESC LIMIT 5` — pipe to `evidence/canary-phase-3b-restart-2026-04-30/canary_run_rows.txt`; verify at least one row exists with non-NULL `plan_slug` matching `executable-canary-phase-3b-restart-2026-04-30` or `canary-phase-3b-restart-2026-04-30`. (c) Import bellows and call `bellows._get_last_completed_step(bellows.DB_PATH, "canary-phase-3b-restart-2026-04-30")` — pipe the returned value (int or None) to `evidence/canary-phase-3b-restart-2026-04-30/get_last_step.txt`; verify it equals 1 (Step 1 completed). Build the verification table with one row per assertion. **Test Regression.** Run `cd bellows && pytest tests/test_bellows.py -x --tb=short 2>&1 | tee knowledge/qa/evidence/canary-phase-3b-restart-2026-04-30/pytest_targeted.txt`. The 1 known pre-existing failure (`test_run_step_timeout`) is acceptable; all others must pass. **QA Report.** Deposit at `bellows/knowledge/qa/canary-phase-3b-restart-2026-04-30.md` with verification table, all three Phase 3b assertion results citing evidence file paths in Evidence column, test regression summary, and the Rule 20 self-check stdout block. **Run the Rule 20 self-check** (template below; required_evidence_files = ["pragma_runs.txt", "canary_run_rows.txt", "get_last_step.txt", "pytest_targeted.txt"]). Include literal stdout in the report. If self-check FAILED — stop, do NOT update PROJECT_STATUS, do NOT commit. **PROJECT_STATUS update.** Add a one-line completed-milestone entry: "2026-04-30: Phase 3b restart canary — confirmed daemon loaded new DDL + record_run signature + _get_last_completed_step helper. Live DB has plan_slug column; canary's run row populated; helper returns 1." Use edit_block to insert the new line after the existing "2026-04-28: BACKLOG #5 closed" line. **Feedback append.** Standard prompt feedback protocol → `bellows/knowledge/research/agent-prompt-feedback.md`. **Final commit.** Single commit with QA report + evidence files + PROJECT_STATUS edit + feedback append, message "docs: phase 3b restart canary QA — DB assertions PASS". **STOP.** Do NOT move this plan to Done/. Per the disable-auto-close model, the Planner performs the terminal move after Rule 22 verification passes. **Deposits:** - `bellows/knowledge/qa/canary-phase-3b-restart-2026-04-30.md` - `bellows/knowledge/qa/evidence/canary-phase-3b-restart-2026-04-30/` (4 files per Rule 20 self-check) - `bellows/PROJECT_STATUS.md` - `bellows/knowledge/research/agent-prompt-feedback.md`
>
> ```python
> # Rule 20 — Mandatory QA Self-Check
> import os, sys
> plan_slug = "canary-phase-3b-restart-2026-04-30"
> qa_report_path = "bellows/knowledge/qa/canary-phase-3b-restart-2026-04-30.md"
> evidence_dir = f"bellows/knowledge/qa/evidence/{plan_slug}/"
> required_evidence_files = ["pragma_runs.txt", "canary_run_rows.txt", "get_last_step.txt", "pytest_targeted.txt"]
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
