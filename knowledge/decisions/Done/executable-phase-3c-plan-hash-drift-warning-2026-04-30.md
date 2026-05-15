# Bellows — Phase 3c: Plan-Hash Drift Warning
**Date:** 2026-04-30 | **Tier:** Small | **Test Scope:** targeted | **Execution:** Step 1 (BELLOWS_DEVELOPER) → Step 2 (BELLOWS_QA)
**Priority:** 1

## Context

Phase 3c closes the final sub-deliverable of BACKLOG #6 (step state across re-claim). When a plan is re-claimed for resume (verdict-pending → continue verdict → resume at step N+1), the shadow cache holds the pristine plan content from the original claim. If the CEO edited the plan file between Step N's pause and the resume, the on-disk plan text now differs from the shadow. The DB-based resume from Phase 3b (shipped 2026-04-28) correctly identifies "resume at step N+1" but does not check whether step N+1's content is still where it was when step N completed. A renumbered plan (step inserted/deleted in the middle) would dispatch the wrong step content.

Phase 3c adds a 5-LOC warning at claim time: when `resume_step > 1` and `shadow_text` exists, compute sha256(shadow_text) vs sha256(plan_text) (first 12 hex chars each), and if they differ, log a stdout warning + send a Pushover notification. **Warn-and-proceed**, not halt — per the Phase 2 design (Section 4 recommendation), trivial edits (typo fixes, formatting) shouldn't block execution. The CEO sees the alert and decides whether to intervene.

Per the Phase 2 design Section 6 Decision 2: warn-and-proceed is the recommended approach. Per Decision 3: `slug_from_path` is already public (Phase 3b shipped). Per Decision 1: `plan_slug` column already exists (Phase 3b shipped). All four design decisions resolved or auto-resolved by Phase 3b.

Test scope: targeted (`tests/test_bellows.py` only — Phase 3c touches `bellows.py` only).

## How to Run This Plan

Paste the bootstrap into Claude Code. Step 1 only. STOP and wait for "ok" before Step 2. Step 2 ends with the Planner-owned move-to-Done pattern (per Rule 23 v4.27): the QA agent commits and stops; the Planner performs the terminal Done/ move after Rule 22 verification passes.

**Bootstrap:**
```
Read the plan at bellows/knowledge/decisions/executable-phase-3c-plan-hash-drift-warning-2026-04-30.md. Execute Step 1 ONLY. After completing Step 1, STOP and wait for my confirmation. Do NOT proceed to Step 2 or move the plan to Done.
```

---
---

## STEP 1 — BELLOWS_DEVELOPER

---

> **FIRST — before doing anything else, claim this plan:** `import shutil; shutil.move("bellows/knowledge/decisions/executable-phase-3c-plan-hash-drift-warning-2026-04-30.md", "bellows/knowledge/decisions/in-progress-executable-phase-3c-plan-hash-drift-warning-2026-04-30.md")`. You are the Bellows Developer. Skip glossary read — this is a small bellows.py edit. Read your specialist file at `bellows/agents/BELLOWS_DEVELOPER.md` (Layer 1 boundaries, plan lifecycle invariants). Read `bellows/bellows.py` lines 195-260 to understand the current `run_plan()` claim path: shadow read → DB resume check → diagnostic check → header/model parsing → claim move. **Implementation.** Add `import hashlib` to the imports block at the top of `bellows.py` (currently lines 3-14, alphabetical with stdlib). In `run_plan()`, insert the plan-hash drift warning immediately AFTER the existing DB resume block (the block that prints "Bellows: DB resume — last completed step …, resuming at …") and BEFORE the `is_diagnostic = ...` line. The new block: `if resume_step is not None and resume_step > 1 and shadow_text is not None:` then compare `hashlib.sha256(shadow_text.encode()).hexdigest()[:12]` vs `hashlib.sha256(plan_text.encode()).hexdigest()[:12]`; if they differ, `print(f"Bellows: ⚠️ plan content changed since last step — shadow={shadow_hash} current={current_hash}")` and call `notifier.push(app_key, user_key, "Bellows — Plan Modified", f"Plan {plan_name} content changed since step {resume_step - 1}. Resuming at step {resume_step} with modified plan.")`. Use `app_key`, `user_key`, `plan_name` already in scope from lines 197-199. Warn-and-proceed: do NOT raise, do NOT pause, do NOT change resume_step. **Test.** Add ONE new test to `bellows/tests/test_bellows.py` named `test_run_plan_plan_hash_drift_warning` at the end of the Phase 3b test block (after `test_get_last_completed_step_exact_slug_match`). Pattern follows existing run_plan tests — set up tmpdir with decisions_dir, write plan file with `## STEP 1\n## STEP 2\n` content, create shadow cache file at `BELLOWS_ROOT/.bellows-cache/{base_filename}.pristine` with DIFFERENT content (e.g. add a comment line that's not in plan_path), insert a DB row with status=Complete step=1 plan_slug=<derived from base name>, then `bellows.run_plan(inprogress_path, config, response_server, resume_step=2)` (NOT calling at resume_step=None — passing explicitly avoids the Phase 3b DB-derivation path so the test is scoped to the warning logic). Mock `notifier.push`, `runner.run_step`, `gates.check`, `verdict.log_to_ledger`, `_capture_git_diff`, `record_run`. Assert `notifier.push` was called at least once with title containing "Plan Modified" — use `any(call.args[2] == "Bellows — Plan Modified" for call in mock_push.call_args_list)`. Use the existing helper `_make_fake_run_step_result()` and `_clean_gates(auto_close="true")`. The shadow file must be created before run_plan invocation; use `bellows._shadow_path(plan_filename).parent.mkdir(parents=True, exist_ok=True)` then `bellows._shadow_path(plan_filename).write_text("DIFFERENT CONTENT")`. **Don't add a negative test** — the existing `test_run_plan_resume_step_uses_correct_prompt` does NOT have shadow set up so it implicitly serves as the negative-shadow case; the new test focuses on the warning firing. **Run.** `cd bellows && pytest tests/test_bellows.py -x --tb=short`. Test count goes from 70 → 71. Commit message: "phase 3c: plan-hash drift warning + test". Standard prompt feedback protocol → `bellows/knowledge/research/agent-prompt-feedback.md`. Append feedback in same commit.
>
> **STOP. Do NOT proceed to Step 2. Do NOT move the plan to Done. Wait for CEO confirmation before continuing.**
>
> **Deposits:**
> - `bellows/bellows.py`
> - `bellows/tests/test_bellows.py`
> - `bellows/knowledge/research/agent-prompt-feedback.md`

---
---

## STEP 2 — BELLOWS_QA

---

> Before starting, read the prior step's commit log via `cd bellows && git --no-pager log -1 --stat` and confirm the commit landed touching `bellows.py` + `tests/test_bellows.py` + `agent-prompt-feedback.md`. If the commit is missing or doesn't include those files, stop and report. You are the Bellows QA agent. Skip specialist file and glossary reads — this is a mechanical verification task. **FIRST — Deliverable Verification.** Read the prior DEV step's git diff. Verify three deliverables: (a) `bellows/bellows.py` contains `import hashlib` (grep for `^import hashlib` → must match), (b) `bellows/bellows.py` contains the warning block — grep for `Plan Modified` → at least one match, AND grep for `hashlib.sha256` → at least 2 matches (one for shadow, one for plan_text), (c) `bellows/tests/test_bellows.py` contains `def test_run_plan_plan_hash_drift_warning` (grep for that exact function name → must match). Pipe each grep output to `bellows/knowledge/qa/evidence/phase-3c-plan-hash-drift-warning-2026-04-30/grep_<deliverable>.txt`. Build verification table: | Deliverable | Expected | Status (✅/❌) | Evidence |. **Test Regression.** Run `cd bellows && pytest tests/test_bellows.py --tb=short 2>&1 | tee knowledge/qa/evidence/phase-3c-plan-hash-drift-warning-2026-04-30/pytest_targeted.txt`. Expected: 71 passed (70 prior + 1 new). The 1 known pre-existing failure `test_run_step_timeout` lives in a DIFFERENT test file (`tests/test_runner.py`) and is NOT picked up by `tests/test_bellows.py` — so this run should be a clean 71/71. If anything else fails — STOP, report, do NOT proceed. **Behavioral Smoke.** In a Python REPL invocation: import bellows, hash the string "AAA" via `hashlib.sha256(b"AAA").hexdigest()[:12]` and the string "BBB" similarly, confirm they differ. Pipe to `evidence/phase-3c-plan-hash-drift-warning-2026-04-30/hash_smoke.txt`. This validates `hashlib` import landed correctly. **QA Report.** Deposit at `bellows/knowledge/qa/phase-3c-plan-hash-drift-warning-2026-04-30.md` with verification table, test regression summary, behavioral smoke result, and the Rule 20 self-check stdout block. **Run the Rule 20 self-check** (template below; required_evidence_files = ["grep_hashlib_import.txt", "grep_warning_block.txt", "grep_test_function.txt", "pytest_targeted.txt", "hash_smoke.txt"]). Include literal stdout in report. If FAILED — STOP, do NOT update PROJECT_STATUS, do NOT commit. **PROJECT_STATUS update.** Use `Filesystem:edit_file` to insert a new line after the canary entry from this morning. Anchor: locate the existing line `- 2026-04-30: Phase 3b restart canary — confirmed daemon loaded new DDL + record_run signature + _get_last_completed_step helper. Live DB has plan_slug column; canary's run row populated; helper returns 1.` and replace it with that exact line followed by `\n` followed by `- 2026-04-30: Phase 3c plan-hash drift warning shipped (BACKLOG #6 fully closed). Added \`import hashlib\` + 7-LOC warning block to \`run_plan()\` in \`bellows.py\` between DB resume block and is_diagnostic check. Fires when resume_step > 1 AND shadow_text present AND sha256(shadow) != sha256(plan_text). Stdout warning + Pushover notification \"Bellows — Plan Modified\". Warn-and-proceed (no halt). +1 unit test (\`test_run_plan_plan_hash_drift_warning\`), 71 total in test_bellows.py. REMINDER: restart Bellows to load.`. **Feedback append.** Standard prompt feedback protocol → `bellows/knowledge/research/agent-prompt-feedback.md`. **Final commit.** Single commit with QA report + evidence files + PROJECT_STATUS edit + feedback, message: "qa: phase 3c plan-hash drift warning — verified". **STOP.** Do NOT move this plan to Done/. Per the disable-auto-close model, the Planner performs the terminal move after Rule 22 verification passes.
>
> **Deposits:**
> - `bellows/knowledge/qa/phase-3c-plan-hash-drift-warning-2026-04-30.md`
> - `bellows/knowledge/qa/evidence/phase-3c-plan-hash-drift-warning-2026-04-30/grep_hashlib_import.txt`
> - `bellows/knowledge/qa/evidence/phase-3c-plan-hash-drift-warning-2026-04-30/grep_warning_block.txt`
> - `bellows/knowledge/qa/evidence/phase-3c-plan-hash-drift-warning-2026-04-30/grep_test_function.txt`
> - `bellows/knowledge/qa/evidence/phase-3c-plan-hash-drift-warning-2026-04-30/pytest_targeted.txt`
> - `bellows/knowledge/qa/evidence/phase-3c-plan-hash-drift-warning-2026-04-30/hash_smoke.txt`
> - `bellows/PROJECT_STATUS.md`
> - `bellows/knowledge/research/agent-prompt-feedback.md`
>
> ```python
> # Rule 20 — Mandatory QA Self-Check
> import os, sys
> plan_slug = "phase-3c-plan-hash-drift-warning-2026-04-30"
> qa_report_path = "bellows/knowledge/qa/phase-3c-plan-hash-drift-warning-2026-04-30.md"
> evidence_dir = f"bellows/knowledge/qa/evidence/{plan_slug}/"
> required_evidence_files = ["grep_hashlib_import.txt", "grep_warning_block.txt", "grep_test_function.txt", "pytest_targeted.txt", "hash_smoke.txt"]
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
