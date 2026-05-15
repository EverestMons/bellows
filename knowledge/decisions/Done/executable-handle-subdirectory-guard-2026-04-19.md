# bellows — Fix: on_moved Re-Run Cascade (Guard in _handle)
**Date:** 2026-04-19 | **Tier:** Medium | **Test Scope:** targeted | **Execution:** Step 1 (DEV) → Step 2 (QA)
**Priority:** 1

**Test Scope Justification:** `targeted` — changes one function in `bellows.py` (guard insertion at start of `_handle`), updates test fixtures in `tests/test_bellows.py`, and adds new test cases in the same file. No changes to verdict logic, gate logic, parser, or config. Cross-bucket regression risk is limited to the single test file.

## How to Run This Plan

Paste the bootstrap prompt into Claude Code. The agent reads the full plan file and executes Step 1 ONLY. After completing Step 1, STOPS. CEO confirms, then Step 2. After Step 2, plan moves to Done.

**Bootstrap:**
```
Read the plan at bellows/knowledge/decisions/executable-handle-subdirectory-guard-2026-04-19.md. Execute Step 1 ONLY. After completing Step 1, STOP and wait for my confirmation. Do NOT proceed to Step 2 or move the plan to Done.
```

---
---

## STEP 1 — BELLOWS DEVELOPER

---

> **FIRST — before doing anything else, claim this plan:** `import shutil; shutil.move("bellows/knowledge/decisions/executable-handle-subdirectory-guard-2026-04-19.md", "bellows/knowledge/decisions/in-progress-executable-handle-subdirectory-guard-2026-04-19.md")`. **Read your specialist file and skip glossary reads — this is a surgical code fix and test update task.** The prior diagnostic at `bellows/knowledge/research/on-moved-fix-shape-2026-04-19.md` identified that `PlanHandler`'s watchdog event handlers (`on_moved`, `on_created`, `on_modified`) dispatch to `_handle()` without filtering for subdirectory destinations, causing Bellows to re-claim plans the Planner moves to `decisions/Done/`. The fix is a subdirectory guard placed at the start of `_handle()` (not in individual event handlers) so all three paths are protected simultaneously with a single edit. **Your task has three parts:** **(1) Insert the subdirectory guard in `_handle()`.** Read `bellows.py` and locate the `_handle()` method (diagnostic cites it at L452, confirm exact line before editing). Insert the following guard immediately after the method signature line, before any existing logic in the method: `path_parent = str(Path(path).parent); watched = self.orchestrator.config.get("watched_projects", []); if path_parent not in watched: return`. Format the insertion with the project's existing style (single-line or multi-line based on surrounding code). Ensure `Path` is imported at the top of `bellows.py` — if not already imported, add `from pathlib import Path` to the existing imports block. **(2) Update the broken existing test.** Diagnostic flagged that `test_on_moved_dispatches_for_non_directory_event` at `tests/test_bellows.py` L1020 will break because its MagicMock orchestrator has no `config` attribute, so the new guard's `self.orchestrator.config.get("watched_projects", [])` returns a MagicMock that fails the `in` check. Update the test: set `mock_orch.config = {"watched_projects": ["/some/decisions"]}` before the `on_moved` call, and ensure the event's `dest_path` parent matches `/some/decisions`. **(3) Audit ALL tests that call `_handle()` directly OR indirectly.** Grep `tests/test_bellows.py` for callers of `_handle`, `on_moved`, `on_created`, `on_modified`, and `_rescan` (since `_rescan` iterates and calls `_handle`). For each test, verify: (a) does the test's mock orchestrator have `config` set with a `watched_projects` list? (b) does the path passed to the handler match one of the watched paths' parents? If either is NO, update the test fixture to set `mock_orch.config = {"watched_projects": [<matching path>]}`. The diagnostic flagged these specifically but may have missed others — audit exhaustively. **(4) Add the three new tests from diagnostic §6.** Add to `tests/test_bellows.py`: (a) `test_on_moved_dispatches_for_top_level_dest` — event.dest_path in watched dir → _handle called. (b) `test_on_moved_rejects_subdirectory_dest` — event.dest_path in Done/ subdirectory → _handle NOT called. (c) `test_on_moved_dispatches_same_directory_rename` — src and dest both in watched dir (BACKLOG #4 case) → _handle called. All three follow the fixture shape of the existing `test_on_moved_*` tests. Use MagicMock orchestrator with `config = {"watched_projects": ["/proj/knowledge/decisions"]}`. **(5) Run targeted tests.** Execute `pytest tests/test_bellows.py -v 2>&1 | tee /tmp/pytest_targeted_step1.txt` from the bellows project root. Review output. All tests (existing + new) must pass. If any fail, fix and re-run. Do NOT proceed to commit until green. **(6) Commit.** Single commit message: `"fix: guard _handle against subdirectory dispatch (on_moved re-run cascade)"`. Include `bellows.py` and `tests/test_bellows.py` changes in the same commit. Deposit a dev log to `bellows/knowledge/development/handle-subdirectory-guard-2026-04-19.md` describing: what was changed in bellows.py (exact function + line range), what test was updated (name + line), what tests were added (names), total test count before and after, commit SHA. **Write the deposit using the canonical Python file-write pattern:** `with open("bellows/knowledge/development/handle-subdirectory-guard-2026-04-19.md", "w") as f: f.write(content)` where `content` is a triple-quoted Python string defined before the open call. Do NOT use heredoc. Do NOT use `python3 -c`. Standard prompt feedback protocol → `bellows/knowledge/research/agent-prompt-feedback.md`.
>
> **Deposits:**
> - `bellows/knowledge/development/handle-subdirectory-guard-2026-04-19.md`
> - `bellows/knowledge/research/agent-prompt-feedback.md`
>
> **STOP. Do NOT proceed to Step 2. Do NOT move the plan to Done. Wait for CEO confirmation before continuing.**

---
---

## STEP 2 — BELLOWS QA

---

> **Before starting, read `bellows/knowledge/development/handle-subdirectory-guard-2026-04-19.md` and check the Output Receipt status field. If status is not Complete, stop and report the issue to the CEO before proceeding.** Read your specialist file and skip glossary reads — this is a mechanical deliverable verification and regression test task. **FIRST — Deliverable Verification (Rule 17).** Read the Step 1 dev log's "Files Created or Modified (Code)" list. For every listed file: verify it exists on disk and contains the described change. Specifically: (a) grep `bellows.py` for the new guard condition — confirm `path_parent = str(Path(path).parent)` or equivalent exists in the `_handle` method. Write grep output to `bellows/knowledge/qa/evidence/executable-handle-subdirectory-guard-2026-04-19/grep_guard.txt`. (b) grep `tests/test_bellows.py` for the 3 new test function names (`test_on_moved_dispatches_for_top_level_dest`, `test_on_moved_rejects_subdirectory_dest`, `test_on_moved_dispatches_same_directory_rename`) — confirm all 3 exist. Write grep output to `bellows/knowledge/qa/evidence/executable-handle-subdirectory-guard-2026-04-19/grep_new_tests.txt`. (c) confirm the commit SHA cited in the dev log exists via `git --no-pager log -1 <sha>` — write output to `bellows/knowledge/qa/evidence/executable-handle-subdirectory-guard-2026-04-19/git_log.txt`. Produce a verification table: `| Deliverable | Expected | Status (✅/❌) | Evidence |` citing each evidence file by path. If ANY item is ❌, STOP and report to CEO — do NOT move plan to Done. **Targeted test run.** Execute `pytest tests/test_bellows.py -v 2>&1 | tee bellows/knowledge/qa/evidence/executable-handle-subdirectory-guard-2026-04-19/pytest_targeted.txt`. The evidence file must be the literal pytest output. Count passed/failed from the output. ALL tests must pass. If any fail, mark ❌ and STOP. **Write the QA report to `bellows/knowledge/qa/handle-subdirectory-guard-2026-04-19.md`** using the canonical Python file-write pattern (`with open(...) as f: f.write(content)`, content as a pre-defined triple-quoted string). Report structure: (a) Deliverable verification table per Rule 17, (b) test results summary (N passed, 0 failed), (c) Rule 20 self-check output (copy-paste the literal stdout of the self-check block below). **Rule 20 mandatory self-check:** execute the following Python block exactly as written and include its literal stdout in the QA report:
>
> ```python
> import os, sys
> plan_slug = "executable-handle-subdirectory-guard-2026-04-19"
> qa_report_path = "bellows/knowledge/qa/handle-subdirectory-guard-2026-04-19.md"
> evidence_dir = f"bellows/knowledge/qa/evidence/{plan_slug}/"
> required_evidence_files = ["grep_guard.txt", "grep_new_tests.txt", "git_log.txt", "pytest_targeted.txt"]
> hedging_keywords = ["pending", "inferred", "extrapolated", "estimated", "approximate", "skipped", "assumed", "close enough", "should pass", "would pass", "not run"]
> POSITIVE_STATUS_TOKENS = ["✅", "OK", "PASS", "[x]", "done", "complete", "verified"]
> def is_positive_row(line):
>     if "|" not in line: return False
>     cells = [c.strip() for c in line.split("|")]
>     for cell in cells:
>         for token in POSITIVE_STATUS_TOKENS:
>             if token == "✅":
>                 if "✅" in cell: return True
>             else:
>                 if cell.lower() == token.lower(): return True
>     return False
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
>     with open(qa_report_path, "r") as f: report = f.read()
>     for line in report.splitlines():
>         if is_positive_row(line):
>             lower = line.lower()
>             for kw in hedging_keywords:
>                 if kw in lower:
>                     failures.append(f"CRITICAL: hedging keyword '{kw}' in positive-status row: {line.strip()[:120]}")
>                     break
> else:
>     failures.append(f"CRITICAL: QA report not found at {qa_report_path}")
> print("=" * 60); print("Rule 20 — QA Self-Check Results"); print("=" * 60)
> if failures:
>     print(f"FAILED — {len(failures)} issue(s):")
>     for f in failures: print(f"  - {f}")
>     print("\nPlan CANNOT close."); sys.exit(1)
> else:
>     print(f"PASSED — all evidence files present, no hedging keywords found.")
>     print(f"Evidence folder: {evidence_dir}"); print(f"Files verified: {len(required_evidence_files)}")
> ```
>
> If self-check prints FAILED, STOP, report to CEO, do NOT proceed to housekeeping. If self-check prints PASSED, proceed with housekeeping in this order per Rule 23: **(A) Feedback append.** Append a dated entry to `bellows/knowledge/research/agent-prompt-feedback.md` per standard prompt feedback protocol. **(B) PROJECT_STATUS.md update.** Read `bellows/PROJECT_STATUS.md` to get the current file contents. Use `Desktop Commander:edit_block` to add a milestone entry — the exact old_string and new_string will depend on the file's current shape; pick a stable anchor line (the last milestone entry's last line) and append a new entry summarizing: fixed on_moved re-run cascade via `_handle` subdirectory guard; updated 1 existing test; added 3 new tests; commit SHA from dev log. **(C) Final commit.** Include feedback log, QA report, evidence folder, and PROJECT_STATUS.md update in one commit: `git --no-pager add bellows/knowledge/qa/handle-subdirectory-guard-2026-04-19.md bellows/knowledge/qa/evidence/executable-handle-subdirectory-guard-2026-04-19/ bellows/knowledge/research/agent-prompt-feedback.md bellows/PROJECT_STATUS.md && git --no-pager commit -m "chore: QA + status for handle-subdirectory-guard"`. **(D) DO NOT MOVE THE PLAN TO DONE.** The `on_moved` event would trigger the pre-fix code still running in the daemon (the fix is in the committed code but NOT yet loaded — loading requires a Bellows restart). Moving the plan to Done/ now would cause the unfixed daemon to re-claim and re-execute from Done/, producing a cascading re-run. Instead: leave the plan in `in-progress-*` state in `decisions/`. The CEO will restart Bellows and then move the plan to Done manually via `shutil.move` after the restart has loaded the fix. **FLAG FOR CEO — add to the QA report's Flags section in bold, at the top:** "BELLOWS RESTART REQUIRED BEFORE MOVE-TO-DONE. The plan is intentionally left in `in-progress-executable-handle-subdirectory-guard-2026-04-19.md` state. After CEO restarts Bellows to load the guard fix, CEO manually moves the plan to Done via `shutil.move('bellows/knowledge/decisions/in-progress-executable-handle-subdirectory-guard-2026-04-19.md', 'bellows/knowledge/decisions/Done/executable-handle-subdirectory-guard-2026-04-19.md')` then commits. Five verdict-pending-* plans currently in decisions/ will remain safe from re-run only after the restart." Standard prompt feedback protocol already covered above in (A).
>
> **Deposits:**
> - `bellows/knowledge/qa/handle-subdirectory-guard-2026-04-19.md`
> - `bellows/knowledge/qa/evidence/executable-handle-subdirectory-guard-2026-04-19/grep_guard.txt`
> - `bellows/knowledge/qa/evidence/executable-handle-subdirectory-guard-2026-04-19/grep_new_tests.txt`
> - `bellows/knowledge/qa/evidence/executable-handle-subdirectory-guard-2026-04-19/git_log.txt`
> - `bellows/knowledge/qa/evidence/executable-handle-subdirectory-guard-2026-04-19/pytest_targeted.txt`
> - `bellows/knowledge/research/agent-prompt-feedback.md`
> - `bellows/PROJECT_STATUS.md`
