# Bellows — Fix: is_runnable_plan Parallel Prefix Support
**Date:** 2026-04-14 | **Tier:** Small | **Test Scope:** targeted | **Execution:** Step 1 (DEV) → Step 2 (QA)
**Priority:** 1

## How to Run This Plan

This plan is picked up and executed by Bellows automatically.

---
---

## STEP 1 — DEV

---

> **FIRST — claim this plan:** `import shutil; shutil.move("bellows/knowledge/decisions/executable-is-runnable-plan-parallel-fix-2026-04-14.md", "bellows/knowledge/decisions/in-progress-executable-is-runnable-plan-parallel-fix-2026-04-14.md")`. Skip specialist file and glossary reads — mechanical fix task. Working directory is `/Users/marklehn/Desktop/GitHub/`. Context from diagnostic at `bellows/knowledge/research/is-runnable-plan-parallel-diagnostic-2026-04-14.md`: `is_runnable_plan` at `bellows/bellows.py:221-226` rejects `parallel-N-executable-*.md` and `parallel-N-diagnostic-*.md` filenames. This drops parallel plans at FIVE call sites: `_handle` (line 252, primary drop), `collect_group` (line 244), `_check_queue_drain` (line 300), `_rescan` (line 322), and startup scan (line 350). All five sites are fixed by making `is_runnable_plan` itself parallel-aware. **Single change to `bellows/bellows.py`:** Replace the current `is_runnable_plan` function body (lines 221-226) with a regex-based implementation that accepts an optional `parallel-N-` prefix. New implementation: `def is_runnable_plan(filename: str) -> bool:` returning the result of a bounded pattern match. Use `re.match(r"^(parallel-\d+-)?(executable|diagnostic)-.*\.md$", filename)` and also require the filename does NOT start with `in-progress-`. Preserve the function's existing type hint (`filename: str`) and return type (`bool`). Add `import re` at the top of `bellows.py` only if it is not already imported — check first, do not duplicate. **Update `bellows/tests/test_bellows.py`:** The existing `test_is_runnable_plan_diagnostic` test (currently covering `diagnostic-foo-*.md` and `in-progress-diagnostic-foo.md`) must continue to pass — do NOT modify it. Add a new test `test_is_runnable_plan_parallel_prefix` that asserts all six of the following: `is_runnable_plan("parallel-1-executable-foo-2026-04-14.md") is True`, `is_runnable_plan("parallel-2-diagnostic-bar-2026-04-14.md") is True`, `is_runnable_plan("parallel-10-executable-baz.md") is True`, `is_runnable_plan("parallel-1-foo.md") is False` (parallel prefix but no valid plan type), `is_runnable_plan("in-progress-parallel-1-executable-foo.md") is False` (in-progress still rejected), `is_runnable_plan("executable-foo-2026-04-14.md") is True` (non-parallel still works). **Run targeted tests:** `python3 -m pytest tests/test_bellows.py -v` from `/Users/marklehn/Desktop/GitHub/bellows/`. All tests must pass — the existing 5 tests from Phase 2B plus the 1 new test = 6 total. Commit: `fix: is_runnable_plan accepts parallel-N- prefix`. Standard prompt feedback protocol → `bellows/knowledge/research/agent-prompt-feedback.md`.
>
> **STOP. Do NOT proceed to Step 2. Do NOT move the plan to Done. Wait for CEO confirmation before continuing.**

---
---

## STEP 2 — QA

---

> Before starting, verify Step 1 committed via `git --no-pager log --oneline -3` from `/Users/marklehn/Desktop/GitHub/bellows/`. Skip specialist file and glossary reads — mechanical verification only. **Deliverable verification:** grep `bellows/bellows.py` for the new regex pattern `parallel-\\\\d\\+-` and confirm exactly one match inside `is_runnable_plan`. Grep `bellows/tests/test_bellows.py` for `test_is_runnable_plan_parallel_prefix` and confirm it exists. **Re-run targeted tests:** `python3 -m pytest tests/test_bellows.py -v` from `/Users/marklehn/Desktop/GitHub/bellows/` — write raw output to `bellows/knowledge/qa/evidence/is-runnable-plan-parallel-fix/pytest_targeted.txt` via Python file I/O. **Smoke test all 5 call sites via direct function calls:** `python3 -c "from bellows import is_runnable_plan; cases = [('executable-foo.md', True), ('diagnostic-bar.md', True), ('parallel-1-executable-foo.md', True), ('parallel-2-diagnostic-bar.md', True), ('parallel-10-executable-baz.md', True), ('in-progress-parallel-1-executable-foo.md', False), ('in-progress-executable-foo.md', False), ('parallel-1-foo.md', False), ('foo.md', False)]; [print(f, '->', is_runnable_plan(f), '(expected', e, ')') for f,e in cases]; assert all(is_runnable_plan(f) == e for f,e in cases), 'SMOKE FAILED'"` from `/Users/marklehn/Desktop/GitHub/bellows/`. Write output to `bellows/knowledge/qa/evidence/is-runnable-plan-parallel-fix/smoke_all_cases.txt`. **Smoke test module import:** `python3 -c "import bellows; print('ok')"` from `/Users/marklehn/Desktop/GitHub/bellows/`. Write to `bellows/knowledge/qa/evidence/is-runnable-plan-parallel-fix/smoke_import.txt`. Produce verification table: `| Deliverable | Expected | Status (✅/❌) | Evidence |` covering at minimum: new regex present in is_runnable_plan, new test present, 6/6 tests pass, smoke_all_cases assert passed, module imports clean. Deposit QA report to `bellows/knowledge/qa/is-runnable-plan-parallel-fix-qa-2026-04-14.md`. **Run Rule 20 self-check:**
> ```python
> import os, sys
> qa_report_path = "knowledge/qa/is-runnable-plan-parallel-fix-qa-2026-04-14.md"
> evidence_dir = "knowledge/qa/evidence/is-runnable-plan-parallel-fix/"
> required_evidence_files = ["pytest_targeted.txt", "smoke_all_cases.txt", "smoke_import.txt"]
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
> Run from `/Users/marklehn/Desktop/GitHub/bellows/`. If self-check fails, stop and report to CEO. If passes: update `bellows/PROJECT_STATUS.md` — add entry: "2026-04-14: is_runnable_plan parallel-prefix fix shipped. Parallel plans now flow through all 5 call sites (_handle, collect_group, _check_queue_drain, _rescan, startup scan)." Move plan to Done: `import shutil; shutil.move("bellows/knowledge/decisions/in-progress-executable-is-runnable-plan-parallel-fix-2026-04-14.md", "bellows/knowledge/decisions/Done/executable-is-runnable-plan-parallel-fix-2026-04-14.md")`. Commit: `chore: QA report — is_runnable_plan parallel fix`. Standard prompt feedback protocol → `bellows/knowledge/research/agent-prompt-feedback.md`.
