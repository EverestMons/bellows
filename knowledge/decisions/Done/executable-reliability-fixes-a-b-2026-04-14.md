# Bellows — Fix: Reliability Bugs A + B (Stranded Detection, Rescan Race)
**Date:** 2026-04-14 | **Tier:** Small | **Test Scope:** targeted | **Execution:** Step 1 (DEV) → Step 2 (QA)
**Priority:** 1

## How to Run This Plan

This plan is picked up and executed by Bellows automatically.

## Context

Two reliability bugs observed in the 2026-04-14 session, root-caused via direct source read:

**Bug A — Plan completion detection does not verify disk state.** `run_plan` prints `✅ DONE` when the step loop exits, trusting the agent's `receipt_status` without checking that the plan file actually moved from `in-progress-` to `Done/`. Cycle 11 stranded file resulted from this: the plan's closing `shutil.move` never ran, but Bellows marked it done.

**Bug B — `_rescan` clears `_seen` for actively-running plans.** The anti-race check in `_rescan` removes a path from `_seen` when the file still exists on disk and no `in-progress-` version exists. This condition is also true during the window between dispatch and the agent's claim-rename (typically 5-15 seconds while `claude -p` boots). The rescan fires at 30-second intervals, so plans in the bootup window get their `_seen` entry cleared and are re-dispatched to a second thread. The second thread's agent tries to run `shutil.move` on a file that's been renamed by the first thread, fails, returns $0.00, Bellows reports the $0.00 as the authoritative outcome.

Three fixes in one plan, all in `bellows/bellows.py`:

1. Post-loop disk verification in `run_plan` (Bug A)
2. Remove the `_seen.discard` line in `_rescan` (Bug B)
3. Add 2-second stagger to `handle_parallel_group` thread starts (Bug B-adjacent mitigation — parallel groups currently start threads back-to-back, causing simultaneous `claude -p` auth hits)

---
---

## STEP 1 — DEV

---

> **FIRST — claim this plan:** `import shutil; shutil.move("bellows/knowledge/decisions/executable-reliability-fixes-a-b-2026-04-14.md", "bellows/knowledge/decisions/in-progress-executable-reliability-fixes-a-b-2026-04-14.md")`. Skip specialist file and glossary reads — mechanical fix task. Working directory is `/Users/marklehn/Desktop/GitHub/bellows/`. Three targeted edits to `bellows.py`, then update tests. **Edit 1 — Bug A stranded detection in `run_plan`.** Locate the `run_plan` function. Find the line `print(f"Bellows: ✅ DONE — {plan_name} (${total_cost:.4f})")` near the end of the `try` block (it follows the `while not is_final_step(...)` loop and precedes `notifier.notify_complete(...)`). Insert a disk-state verification block BEFORE that print line. The new block must compute `expected_done_path = os.path.join(plan_dir, "Done", plan_filename)` and check whether the inprogress file still exists OR the Done file does not exist. If either is true, print a stranded warning, send a stranded Pushover notification, and return early (do NOT call `notifier.notify_complete`). The exact new block to insert:
>
> ```python
>         expected_done_path = os.path.join(plan_dir, "Done", plan_filename)
>         if os.path.exists(inprogress_path) or not os.path.exists(expected_done_path):
>             stranded_msg = f"{plan_name} reported step complete but plan file not in Done/"
>             print(f"Bellows: ⚠️  STRANDED — {stranded_msg}")
>             notifier.push(app_key, user_key, "Bellows — Stranded Plan", stranded_msg)
>             return
> ```
>
> Insert this block immediately BEFORE the `print(f"Bellows: ✅ DONE — ...")` line. Do NOT remove the DONE print or the `notifier.notify_complete` call — they still run on the happy path when neither stranded condition is true.
>
> **Edit 2 — Bug B rescan race fix.** Locate the `_rescan` method on the `Bellows` class. Find the existing loop body:
>
> ```python
>     def _rescan(self, handler):
>         for decisions_path in self.config.get("watched_projects", []):
>             if os.path.isdir(decisions_path):
>                 for fname in os.listdir(decisions_path):
>                     if is_runnable_plan(fname):
>                         full_path = os.path.join(decisions_path, fname)
>                         # Only clear from _seen if the file exists AND no in-progress version exists
>                         # This prevents double-execution when a thread has already claimed the plan
>                         inprogress = os.path.join(decisions_path, f"in-progress-{fname}")
>                         if full_path in handler._seen and os.path.exists(full_path) and not os.path.exists(inprogress):
>                             handler._seen.discard(full_path)
>                         handler._handle(full_path)
> ```
>
> Replace the entire method body with the simpler version that does NOT clear `_seen` entries. The replacement:
>
> ```python
>     def _rescan(self, handler):
>         for decisions_path in self.config.get("watched_projects", []):
>             if os.path.isdir(decisions_path):
>                 for fname in os.listdir(decisions_path):
>                     if is_runnable_plan(fname):
>                         full_path = os.path.join(decisions_path, fname)
>                         handler._handle(full_path)
> ```
>
> The rationale goes in the commit message, not the code. The anti-race check was removing seen entries for plans in their claim-rename bootup window, causing re-dispatch. Removing the discard line means `_handle`'s existing `path in self._seen` check correctly short-circuits re-dispatch. A tradeoff: plans whose dispatching thread crashes without claiming will now remain stuck in `_seen` until Bellows restarts. That is acceptable — thread crashes are rare, and surfacing them via Bug A's stranded detection is better than blindly re-dispatching.
>
> **Edit 3 — Parallel group stagger.** Locate `handle_parallel_group` in the `Bellows` class:
>
> ```python
>     def handle_parallel_group(self, paths: list):
>         threads = [threading.Thread(target=self._run_tracked, args=(p,), daemon=True) for p in paths]
>         [t.start() for t in threads]
>         print(f"Bellows: ▶ started {len(threads)} parallel threads")
> ```
>
> Replace with a version that staggers thread starts by 2 seconds each, matching `handle_new_plan`'s stagger pattern:
>
> ```python
>     def handle_parallel_group(self, paths: list):
>         threads = [threading.Thread(target=self._run_tracked, args=(p,), daemon=True) for p in paths]
>         for t in threads:
>             t.start()
>             time.sleep(2)
>         print(f"Bellows: ▶ started {len(threads)} parallel threads")
>     ```
>
> **Test updates in `tests/test_bellows.py`.** Add two new tests. Read the existing test file first to understand how `PlanHandler` and `Bellows` are imported, what fixtures exist, and how existing tests structure their mocks. Fit the new tests into the existing style. **New test 1 — `test_rescan_preserves_seen`.** Verify that `_rescan` does NOT clear entries from `handler._seen` even when the file exists on disk and no in-progress version exists. Setup: create a temp directory to act as decisions_path, write a valid plan file (e.g. `executable-foo-2026-04-14.md`) with at least one `## STEP` header, create a minimal `Bellows` instance with a config pointing `watched_projects` at the temp directory, create a `PlanHandler` bound to a mock orchestrator, add the plan path to `handler._seen`, call `bellows._rescan(handler)`, assert the path is STILL in `handler._seen` after the call, assert the mock orchestrator's `handle_new_plan` was NOT called a second time (it was never called in the first place — `_seen` should prevent re-dispatch). **New test 2 — `test_handle_parallel_group_stagger`.** Verify `handle_parallel_group` waits between thread starts. Patch `time.sleep` to record call args. Call `handle_parallel_group` with a list of 3 dummy paths. Assert `time.sleep` was called at least 3 times with argument `2`. Use a mock for `_run_tracked` so threads don't actually execute. **Bug A stranded detection test is harder** to write without mocking the full runner/planner chain. The DEV agent should EITHER extract the stranded check into a helper function (e.g. `_is_plan_stranded(inprogress_path: str, expected_done_path: str) -> bool`) and test the helper directly, OR skip the Bug A test and document in the commit message why. Prefer extracting the helper — it makes the logic testable and the intent clearer. If the helper is extracted, add `test_is_plan_stranded_returns_true_when_inprogress_exists`, `test_is_plan_stranded_returns_true_when_done_missing`, `test_is_plan_stranded_returns_false_on_happy_path`. **Run targeted tests:** `python3 -m pytest tests/test_bellows.py -v` from `/Users/marklehn/Desktop/GitHub/bellows/`. All existing tests must still pass (6 tests from prior work) plus the 2 or 5 new tests. Commit: `fix: Bellows reliability — stranded detection, rescan race, parallel group stagger`. Standard prompt feedback protocol → `bellows/knowledge/research/agent-prompt-feedback.md`.
>
> **STOP. Do NOT proceed to Step 2. Do NOT move the plan to Done. Wait for CEO confirmation before continuing.**

---
---

## STEP 2 — QA

---

> Before starting, verify Step 1 committed via `git --no-pager log --oneline -3` from `/Users/marklehn/Desktop/GitHub/bellows/`. Skip specialist file and glossary reads — mechanical verification only. **Deliverable verification:** grep `bellows.py` for `STRANDED` — must appear at least twice (print statement + notifier title). Grep for `expected_done_path` — must appear at least twice (definition + use in the condition). Grep for `_rescan` and inspect its body — confirm `handler._seen.discard` does NOT appear inside `_rescan`. Grep `handle_parallel_group` and confirm `time.sleep(2)` appears inside its loop body. Grep `tests/test_bellows.py` for `test_rescan_preserves_seen` and `test_handle_parallel_group_stagger` — both must be present. If the DEV agent extracted a `_is_plan_stranded` helper, grep for it in both `bellows.py` and `test_bellows.py`. **Re-run targeted tests:** `python3 -m pytest tests/test_bellows.py -v` from `/Users/marklehn/Desktop/GitHub/bellows/` — write raw output to `bellows/knowledge/qa/evidence/reliability-fixes-a-b/pytest_targeted.txt` via Python file I/O. All tests must pass. **Smoke test module import:** `python3 -c "import bellows; print('ok')"` from `/Users/marklehn/Desktop/GitHub/bellows/`. Write to `bellows/knowledge/qa/evidence/reliability-fixes-a-b/smoke_import.txt`. **Smoke test rescan behavior directly:** `python3 -c "import tempfile, os, bellows; from unittest.mock import MagicMock; d = tempfile.mkdtemp(); open(os.path.join(d, 'executable-foo-2026-04-14.md'), 'w').write('## STEP 1\\nfoo'); b = bellows.Bellows({'watched_projects': [d], 'callback_port': 5999}); h = bellows.PlanHandler(MagicMock()); h._seen.add(os.path.join(d, 'executable-foo-2026-04-14.md')); b._rescan(h); assert os.path.join(d, 'executable-foo-2026-04-14.md') in h._seen, 'rescan cleared _seen — Bug B not fixed'; print('rescan preserves _seen: OK')"` from `/Users/marklehn/Desktop/GitHub/bellows/`. Write to `bellows/knowledge/qa/evidence/reliability-fixes-a-b/smoke_rescan.txt`. Produce verification table: `| Deliverable | Expected | Status (✅/❌) | Evidence |` covering: STRANDED warning present in run_plan, _seen.discard removed from _rescan, time.sleep(2) present in handle_parallel_group, new tests present and passing, existing tests still passing, module imports clean, live smoke confirms rescan preserves _seen. Deposit QA report to `bellows/knowledge/qa/reliability-fixes-a-b-qa-2026-04-14.md`. **Run Rule 20 self-check:**
> ```python
> import os, sys
> qa_report_path = "knowledge/qa/reliability-fixes-a-b-qa-2026-04-14.md"
> evidence_dir = "knowledge/qa/evidence/reliability-fixes-a-b/"
> required_evidence_files = ["pytest_targeted.txt", "smoke_import.txt", "smoke_rescan.txt"]
> hedging_keywords = ["pending","inferred","extrapolated","estimated","approximate","skipped","assumed","close enough","should pass","would pass","not run"]
> POSITIVE_STATUS_TOKENS = ["✅","OK","PASS","[x]","done","complete","verified"]
> def is_positive_row(line):
>     if "|" not in line: return False
>     cells = [c.strip() for c in line.split("|")]
>     for cell in cells:
>         for token in POSITIVE_STATUS_TOKENS:
>             if token == "✅":
>                 if "✅" in cell: return True
>             elif cell.lower() == token.lower(): return True
>     return False
> failures = []
> if not os.path.isdir(evidence_dir): failures.append(f"CRITICAL: evidence folder missing: {evidence_dir}")
> else:
>     for fname in required_evidence_files:
>         fpath = os.path.join(evidence_dir, fname)
>         if not os.path.isfile(fpath): failures.append(f"CRITICAL: evidence file missing: {fpath}")
>         elif os.path.getsize(fpath) == 0: failures.append(f"CRITICAL: evidence file empty: {fpath}")
> if os.path.isfile(qa_report_path):
>     with open(qa_report_path) as f: report = f.read()
>     for line in report.splitlines():
>         if is_positive_row(line):
>             lower = line.lower()
>             for kw in hedging_keywords:
>                 if kw in lower: failures.append(f"CRITICAL: hedging keyword '{kw}' in positive-status row: {line.strip()[:120]}"); break
> else: failures.append(f"CRITICAL: QA report not found at {qa_report_path}")
> print("="*60)
> print("Rule 20 — QA Self-Check Results")
> print("="*60)
> if failures:
>     print(f"FAILED — {len(failures)} issue(s):")
>     for f in failures: print(f"  - {f}")
>     sys.exit(1)
> else:
>     print("PASSED — all evidence files present, no hedging keywords.")
> ```
> Run from `/Users/marklehn/Desktop/GitHub/bellows/`. If self-check fails, stop and report to CEO. If passes: update `bellows/PROJECT_STATUS.md` — add entry: "2026-04-14: Reliability fixes A+B shipped. Bug A: stranded plan detection added to run_plan (checks inprogress_path gone + Done/ file present before emitting ✅ DONE). Bug B: _rescan no longer clears _seen entries, preventing double-dispatch during agent bootup window. Parallel group thread starts now staggered by 2s, matching handle_new_plan. REMINDER: restart Bellows process manually to load the fix — running process still on old code." Move plan to Done: `import shutil; shutil.move("knowledge/decisions/in-progress-executable-reliability-fixes-a-b-2026-04-14.md", "knowledge/decisions/Done/executable-reliability-fixes-a-b-2026-04-14.md")`. Commit: `chore: QA report — Bellows reliability fixes A+B`. Standard prompt feedback protocol → `knowledge/research/agent-prompt-feedback.md`.
