# Bellows — Fix: on_moved Handler for PlanHandler
**Date:** 2026-04-19 | **Tier:** Small | **Test Scope:** targeted | **Execution:** Step 1 (Bellows Developer) → Step 2 (Bellows QA)

**Test Scope justification:** targeted — adding a single event handler method to `PlanHandler` with a corresponding unit test. No cross-bucket regression risk — handler dispatch is isolated from gate/verdict/parser logic. Full suite run happens at session-wrap per Rule 21.

**Prior diagnostic:** `bellows/knowledge/research/watcher-reliability-2026-04-19.md` — root cause and exact fix specified in Option A.

## How to Run This Plan

Paste the bootstrap prompt into Claude Code. The agent reads the full plan file and executes Step 1 ONLY. After completing Step 1, the agent STOPS and waits for CEO confirmation ("ok") before proceeding to Step 2.

**Bootstrap:**
```
Read the plan at /Users/marklehn/Desktop/GitHub/bellows/knowledge/decisions/executable-watcher-on-moved-handler-2026-04-19.md. Execute Step 1 ONLY. After completing Step 1, STOP and wait for my confirmation. Do NOT proceed to Step 2 or move the plan to Done.
```

---
---

## STEP 1 — Bellows Developer

---

> **FIRST — before doing anything else, claim this plan:** `import shutil; shutil.move("/Users/marklehn/Desktop/GitHub/bellows/knowledge/decisions/executable-watcher-on-moved-handler-2026-04-19.md", "/Users/marklehn/Desktop/GitHub/bellows/knowledge/decisions/in-progress-executable-watcher-on-moved-handler-2026-04-19.md")`.
>
> You are the Bellows Developer. Skip specialist file read — the diagnostic is the blueprint. **Reads (mandatory):** (1) `/Users/marklehn/Desktop/GitHub/bellows/knowledge/research/watcher-reliability-2026-04-19.md` — the diagnostic with exact fix specification, (2) `/Users/marklehn/Desktop/GitHub/bellows/bellows.py` lines 435-484 (the `PlanHandler` class). **Task:** Add a single `on_moved` handler method to the `PlanHandler` class in `bellows.py`, immediately after the `on_modified` method (currently at lines 482-484). Use `edit_block` with the verbatim existing `on_modified` method as the anchor. The new method must be exactly:
>
> ```python
>     def on_moved(self, event):
>         if not event.is_directory:
>             self._handle(event.dest_path)
> ```
>
> Critically — it reads `event.dest_path` (the destination of the rename), NOT `event.src_path`. The destination is the new filename after the rename; `_handle` must process the renamed file, not the old filename.
>
> Then add ONE unit test to `/Users/marklehn/Desktop/GitHub/bellows/tests/test_bellows.py`. Look for the existing test class that tests `PlanHandler` (search for `PlanHandler` in test_bellows.py). Add a test named `test_on_moved_dispatches_for_non_directory_event` that: (1) creates a mock orchestrator (follow the pattern of existing PlanHandler tests), (2) creates a `PlanHandler` instance, (3) patches or mocks `handler._handle`, (4) creates a `MovedEvent` mock with `is_directory=False`, `src_path="/some/decisions/verdict-pending-foo.md"`, `dest_path="/some/decisions/executable-foo.md"`, (5) calls `handler.on_moved(event)`, (6) asserts `handler._handle` was called once with the dest_path. Also add a sibling test `test_on_moved_ignores_directory_events` that passes `is_directory=True` and asserts `_handle` was NOT called. Use the existing test patterns in `test_bellows.py` for imports and fixture setup — do not introduce new testing dependencies.
>
> Run only the new tests: `cd /Users/marklehn/Desktop/GitHub/bellows && python -m pytest tests/test_bellows.py -k "on_moved" -v`. Both must pass. If either fails, fix before proceeding.
>
> Write a dev log to `/Users/marklehn/Desktop/GitHub/bellows/knowledge/development/watcher-on-moved-handler-2026-04-19.md` documenting: (1) the exact diff added to `bellows.py` (show the 3-line addition), (2) the test code added, (3) `pytest` output for the two new tests. Use the canonical Python file write pattern: triple-quoted string variable, then `with open("/absolute/path", "w") as f: f.write(content)`. No heredoc.
>
> Commit: `cd /Users/marklehn/Desktop/GitHub/bellows && git add bellows.py tests/test_bellows.py knowledge/development/watcher-on-moved-handler-2026-04-19.md && git commit -m "fix: PlanHandler now handles on_moved events (BACKLOG #4 partial)"`. Standard prompt feedback protocol → `/Users/marklehn/Desktop/GitHub/bellows/knowledge/research/agent-prompt-feedback.md`.
>
> **Deposits:**
> - `/Users/marklehn/Desktop/GitHub/bellows/bellows.py` (modified)
> - `/Users/marklehn/Desktop/GitHub/bellows/tests/test_bellows.py` (modified, 2 new tests)
> - `/Users/marklehn/Desktop/GitHub/bellows/knowledge/development/watcher-on-moved-handler-2026-04-19.md` (new)
> - `/Users/marklehn/Desktop/GitHub/bellows/knowledge/research/agent-prompt-feedback.md` (append only)
>
> **STOP. Do NOT proceed to Step 2. Do NOT move the plan to Done. Wait for CEO confirmation before continuing.**

---
---

## STEP 2 — Bellows QA

---

> Before starting, read `/Users/marklehn/Desktop/GitHub/bellows/knowledge/development/watcher-on-moved-handler-2026-04-19.md` and check the Output Receipt status field. If status is not Complete, stop and report the issue to the CEO before proceeding. You are the Bellows QA specialist. Skip domain glossary — this is mechanical verification. **Reads:** (1) `/Users/marklehn/Desktop/GitHub/bellows/agents/BELLOWS_QA.md` — your specialist file, (2) the dev log from Step 1, (3) `/Users/marklehn/Desktop/GitHub/bellows/bellows.py` lines 435-490 to verify the addition, (4) `/Users/marklehn/Desktop/GitHub/bellows/tests/test_bellows.py` to verify the test additions.
>
> **FIRST — Deliverable Verification (Rule 17).** Read the Step 1 Output Receipt "Files Created or Modified (Code)" list. For EVERY listed deliverable, verify it exists on disk with the described change. Specifically: (a) `grep -n "def on_moved" /Users/marklehn/Desktop/GitHub/bellows/bellows.py` must return a line inside the PlanHandler class — pipe output to `knowledge/qa/evidence/executable-watcher-on-moved-handler-2026-04-19/grep_on_moved_handler.txt`; (b) `grep -n "dest_path" /Users/marklehn/Desktop/GitHub/bellows/bellows.py` must return a line showing the handler reads `event.dest_path` — pipe to `knowledge/qa/evidence/executable-watcher-on-moved-handler-2026-04-19/grep_dest_path.txt`; (c) `grep -n "on_moved" /Users/marklehn/Desktop/GitHub/bellows/tests/test_bellows.py` must return 2 test functions — pipe to `knowledge/qa/evidence/executable-watcher-on-moved-handler-2026-04-19/grep_test_on_moved.txt`. Produce a verification table: `| Deliverable | Expected | Status (✅/❌) | Evidence |`. If ANY item is ❌, attempt to fix (re-commit, re-create) before proceeding. If unfixable, stop and report to CEO.
>
> **Run targeted tests (Rule 21).** Run the tests for this change AND all existing PlanHandler tests to confirm no regressions: `cd /Users/marklehn/Desktop/GitHub/bellows && python -m pytest tests/test_bellows.py -v 2>&1`. Pipe the full output to `/Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/evidence/executable-watcher-on-moved-handler-2026-04-19/pytest_targeted.txt`. Confirm: (1) the 2 new `on_moved` tests pass, (2) all previously-passing tests in `test_bellows.py` still pass. If there are PRE-EXISTING failures in `test_bellows.py` unrelated to this change, note them in the QA report but do NOT block closure — only regressions from this change block closure.
>
> Deposit the QA report to `/Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/watcher-on-moved-verification-2026-04-19.md` using the canonical Python file write pattern. Include: (a) deliverable verification table with evidence file citations, (b) test run summary (pass count / fail count / regression count), (c) the Rule 20 self-check output.
>
> **Rule 20 mandatory self-check** — execute this Python block at the end of your QA report and include the literal stdout:
>
> ```python
> import os, sys
> plan_slug = "executable-watcher-on-moved-handler-2026-04-19"
> qa_report_path = "/Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/watcher-on-moved-verification-2026-04-19.md"
> evidence_dir = f"/Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/evidence/{plan_slug}/"
> required_evidence_files = [
>     "grep_on_moved_handler.txt",
>     "grep_dest_path.txt",
>     "grep_test_on_moved.txt",
>     "pytest_targeted.txt",
> ]
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
>         if not os.path.isfile(fpath): failures.append(f"CRITICAL: evidence file missing: {fpath}")
>         elif os.path.getsize(fpath) == 0: failures.append(f"CRITICAL: evidence file empty: {fpath}")
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
>     print(f"FAILED — SELF-CHECK FAILED — {len(failures)} issue(s):")
>     for f in failures: print(f"  - {f}")
>     print("\nPlan CANNOT close. Fix issues and re-run QA.")
>     sys.exit(1)
> else:
>     print("PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.")
>     print(f"Evidence folder: {evidence_dir}")
>     print(f"Files verified: {len(required_evidence_files)}")
> ```
>
> If the self-check prints FAILED, STOP — do NOT update PROJECT_STATUS.md, do NOT move the plan to Done. Report the failure to CEO and wait.
>
> If PASSED, proceed in this exact order (Rule 23): **(Step A — feedback append)** append a dated entry to `/Users/marklehn/Desktop/GitHub/bellows/knowledge/research/agent-prompt-feedback.md`. **(Step B — BACKLOG update)** use `edit_block` to add a closure entry to `/Users/marklehn/Desktop/GitHub/bellows/knowledge/BACKLOG.md`. Anchor: find the Closed section header `## Closed` followed by the first bullet — insert a new bullet BEFORE the existing first bullet. The new bullet: `- **Closed 2026-04-19:** filesystem watcher reliability (BACKLOG #4) — PlanHandler now overrides on_moved. Root cause was that macOS FSEvents fires on_moved (not on_created) for same-directory renames, and PlanHandler inherited the default no-op on_moved from FileSystemEventHandler. Fix adds a 3-line on_moved override that calls _handle(event.dest_path). Two new unit tests. Diagnostic: knowledge/research/watcher-reliability-2026-04-19.md. Executable: knowledge/decisions/Done/executable-watcher-on-moved-handler-2026-04-19.md. The open BACKLOG entry "2026-04-18: filesystem watcher reliability" can be removed from the Open section — it is now closed. REMINDER: restart Bellows manually to load the fix.` **(Step C — PROJECT_STATUS update)** use `edit_block` to append a milestone entry to `/Users/marklehn/Desktop/GitHub/bellows/PROJECT_STATUS.md`. Anchor on the last Completed entry — insert AFTER it: `- 2026-04-19 — Filesystem watcher reliability fix shipped. PlanHandler now overrides on_moved to catch rename events (BACKLOG #4 closed). Root cause: macOS FSEvents fires on_moved — not on_created — for same-directory renames; default no-op on_moved was silently dropping events. 3-line handler added + 2 unit tests. REMINDER: restart Bellows to load.` **(Step D — final commit)** `cd /Users/marklehn/Desktop/GitHub/bellows && git add knowledge/qa/ knowledge/research/agent-prompt-feedback.md knowledge/BACKLOG.md PROJECT_STATUS.md && git commit -m "docs: QA verification + close BACKLOG #4 for watcher on_moved fix"`. **(Step E — move plan to Done, ABSOLUTE LAST operation)** `import shutil; shutil.move("/Users/marklehn/Desktop/GitHub/bellows/knowledge/decisions/in-progress-executable-watcher-on-moved-handler-2026-04-19.md", "/Users/marklehn/Desktop/GitHub/bellows/knowledge/decisions/Done/executable-watcher-on-moved-handler-2026-04-19.md")`. Then `cd /Users/marklehn/Desktop/GitHub/bellows && git add knowledge/decisions/ && git commit -m "chore: move watcher on_moved plan to Done"`.
>
> **Deposits:**
> - `/Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/watcher-on-moved-verification-2026-04-19.md`
> - `/Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/evidence/executable-watcher-on-moved-handler-2026-04-19/grep_on_moved_handler.txt`
> - `/Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/evidence/executable-watcher-on-moved-handler-2026-04-19/grep_dest_path.txt`
> - `/Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/evidence/executable-watcher-on-moved-handler-2026-04-19/grep_test_on_moved.txt`
> - `/Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/evidence/executable-watcher-on-moved-handler-2026-04-19/pytest_targeted.txt`
