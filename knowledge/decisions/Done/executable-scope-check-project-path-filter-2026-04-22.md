# bellows — scope_check project-path filter (BACKLOG #2 point fix)
**Date:** 2026-04-22 | **Tier:** Small | **Test Scope:** targeted | **Execution:** Step 1 (DEV) → Step 2 (QA)

## CEO Context

Test Scope: targeted — the fix edits one helper function in bellows.py and adds unit tests. No cross-bucket regression risk. Targeted bucket is `test_bellows.py` and any dedicated `_parse_diff_stat` tests.

Point fix for BACKLOG #2 (scope_check false positives on out-of-project files). Diagnostic `diagnostic-scope-check-git-range-2026-04-22` found the mechanism is NOT a git range — it's a diff-of-diffs of `git diff --stat` output captured with `cwd=project_path`. Because git operates on the whole repo regardless of cwd, files at `/Users/marklehn/Desktop/GitHub/` (like `LESSONS.md`) or in sibling projects (`anvil/`, `invoice-pulse/`) appear in the diff output with `../` prefixes, then get flagged by scope_check because their paths don't appear in plan step text. This fix filters `files_changed` to only paths inside `project_path`. Structural fix (declaration-based scope) remains queued.

## How to Run This Plan

Paste the bootstrap prompt into Claude Code. The agent reads the full plan file and executes Step 1 ONLY. After completing Step 1, the agent STOPS and waits for CEO confirmation ("ok") before proceeding to Step 2.

**Bootstrap prompt:**
```
Read the plan at bellows/knowledge/decisions/executable-scope-check-project-path-filter-2026-04-22.md. Execute Step 1 ONLY. After completing Step 1, STOP and wait for my confirmation. Do NOT proceed to Step 2 or move the plan to Done.
```

---
---

## STEP 1 — Bellows Developer

---

> **FIRST — before doing anything else, claim this plan:** `import shutil; shutil.move("bellows/knowledge/decisions/executable-scope-check-project-path-filter-2026-04-22.md", "bellows/knowledge/decisions/in-progress-executable-scope-check-project-path-filter-2026-04-22.md")`. You are the Bellows Developer. Read your specialist file at `bellows/agents/BELLOWS_DEVELOPER.md` first. Skip domain glossary — this is a code change task. **Task:** add a project-path filter to `_parse_diff_stat` in `bellows.py` so files outside the plan's `project_path` are excluded from `files_changed` before scope_check runs. **Current signature:** `def _parse_diff_stat(post_diff: str, pre_diff: str) -> list`. **New signature:** `def _parse_diff_stat(post_diff: str, pre_diff: str, project_path: Optional[str] = None) -> list`. **Filter logic:** after computing the `changed` list, if `project_path` is provided, filter out any path that escapes the project. Since `git diff --stat` is invoked with `cwd=project_path` and operates on the full repo, paths outside the cwd appear with `../` components. The filter: drop any path whose normalized relative form contains a `..` path component. Use `os.path.normpath` and split on `os.sep` — drop entries where `".."` appears in the resulting parts. Keep the `project_path=None` default so any callers passing only two args still work (preserves backward compatibility for unit tests that don't exercise the filter). **Call sites to update:** both call sites in `run_plan` (around lines 251 and 319 — find them by searching for `_parse_diff_stat(post_diff, pre_diff)`). Pass `project_path` as the third arg at both sites. **Add a module-level docstring comment** above `_parse_diff_stat` explaining the filter: "Files outside `project_path` (paths with `..` components after normalization) are excluded — `git diff --stat` run with `cwd=project_path` still reports changes across the entire repo, and we only want to gate on files the plan could have legitimately touched." **Unit tests:** add tests to the appropriate test file (check existing test layout — likely `tests/test_bellows.py` or a new `tests/test_parse_diff_stat.py`). Test cases to add: (1) no project_path arg → returns all changed files unchanged (backward compat); (2) project_path provided, all changed files inside → returns all; (3) project_path provided, some files have `../` prefix → those are filtered out; (4) project_path provided, file in sibling project (`../anvil/foo.py`) → filtered out; (5) project_path provided, file at repo root (`../LESSONS.md`) → filtered out; (6) project_path provided, files inside project at any depth (`knowledge/research/foo.md`, `tests/test_bar.py`) → returned. Do NOT mock subprocess — `_parse_diff_stat` is a pure function over strings, test it directly with crafted pre/post diff strings. **Commit:** one commit for code + tests. Commit message: `fix: scope_check filters out-of-project files (BACKLOG #2 point fix)`. **Deposit a dev log** at `bellows/knowledge/development/scope-check-project-path-filter-2026-04-22.md` using the canonical Python file-write pattern (triple-quoted string variable, then `with open(...) as f: f.write(content)`). Dev log sections: **Change Summary**, **Files Modified** (with line refs), **Tests Added** (with test names), **Commit SHA**, **Backward Compatibility Notes**, **Output Receipt** per PLANNER_TEMPLATE format. Standard prompt feedback protocol → `bellows/knowledge/research/agent-prompt-feedback.md`.
>
> **Deposits:**
> - `bellows/knowledge/development/scope-check-project-path-filter-2026-04-22.md`
>
> **STOP. Do NOT proceed to Step 2. Do NOT move the plan to Done. Wait for CEO confirmation before continuing.**

---
---

## STEP 2 — Bellows QA

---

> Before starting, read `bellows/knowledge/development/scope-check-project-path-filter-2026-04-22.md` and check the Output Receipt status field. If status is not Complete, stop and report the issue to the CEO before proceeding. You are the Bellows QA. Read your specialist file at `bellows/agents/BELLOWS_QA.md` first. Skip domain glossary — this is a verification task. **FIRST — Deliverable Verification.** Read the Step 1 Output Receipt "Files Created or Modified (Code)" list. For EVERY listed file: verify it exists on disk and contains the described change. Specifically grep `bellows/bellows.py` for the updated `_parse_diff_stat` signature with `project_path` parameter (`grep -n "def _parse_diff_stat" bellows/bellows.py` — pipe output to `bellows/knowledge/qa/evidence/executable-scope-check-project-path-filter-2026-04-22/grep_signature.txt`). Grep both call sites for the three-arg invocation (`grep -n "_parse_diff_stat(post_diff, pre_diff" bellows/bellows.py` — pipe to `grep_callsites.txt`). Verify the test file contains the new tests (`grep -n "project_path" bellows/tests/test_*.py` — pipe to `grep_tests.txt`). Produce a verification table: `| Deliverable | Expected | Status (✅/❌) | Evidence |`. If ANY item is ❌, stop and report to CEO — do NOT proceed. **SECOND — Targeted test run.** Run the targeted bucket: `cd bellows && python -m pytest tests/test_bellows.py tests/test_parse_diff_stat.py -v 2>&1 | tee knowledge/qa/evidence/executable-scope-check-project-path-filter-2026-04-22/pytest_targeted.txt` (if `test_parse_diff_stat.py` doesn't exist, run just `test_bellows.py`). All new tests must pass. Existing tests must not regress — compare pass count to the last known baseline if available. **THIRD — Write QA report** at `bellows/knowledge/qa/qa-scope-check-project-path-filter-2026-04-22.md` using the canonical Python file-write pattern. Sections: **Verification Table** (deliverable check results), **Targeted Test Results** (pass/fail counts, new tests enumerated), **Backward Compatibility Check** (confirm existing 2-arg callers still work by checking call sites use 3-arg form now but the default-None signature supports 2-arg in tests), **Rule 20 Self-Check** (literal stdout from the Python block below), **Output Receipt** per PLANNER_TEMPLATE format. **FOURTH — Update PROJECT_STATUS.md** — add a completed milestone entry summarizing this plan (BACKLOG #2 point fix, files changed, tests added). **FIFTH — Append prompt feedback** to `bellows/knowledge/research/agent-prompt-feedback.md`. **SIXTH — Final commit:** `git add bellows/knowledge/qa/ bellows/PROJECT_STATUS.md bellows/knowledge/research/agent-prompt-feedback.md && git commit -m "chore: QA + status for scope_check project-path filter"`. **SEVENTH — Move plan to Done:** `import shutil; shutil.move("bellows/knowledge/decisions/in-progress-executable-scope-check-project-path-filter-2026-04-22.md", "bellows/knowledge/decisions/Done/executable-scope-check-project-path-filter-2026-04-22.md")`. **Rule 20 Self-Check (run verbatim, include literal output in QA report):**
>
> ```python
> # Rule 20 — Mandatory QA Self-Check
> import os, sys
> plan_slug = "executable-scope-check-project-path-filter-2026-04-22"
> qa_report_path = "bellows/knowledge/qa/qa-scope-check-project-path-filter-2026-04-22.md"
> evidence_dir = f"bellows/knowledge/qa/evidence/{plan_slug}/"
> required_evidence_files = [
>     "grep_signature.txt",
>     "grep_callsites.txt",
>     "grep_tests.txt",
>     "pytest_targeted.txt",
> ]
> hedging_keywords = ["pending", "inferred", "extrapolated", "estimated", "approximate", "skipped", "assumed", "close enough", "should pass", "would pass", "not run"]
> POSITIVE_STATUS_TOKENS = ["✅", "OK", "PASS", "[x]", "done", "complete", "verified"]
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
> If the self-check prints `FAILED`, STOP — do NOT move the plan to Done. Report failure to CEO. Standard prompt feedback protocol → `bellows/knowledge/research/agent-prompt-feedback.md`.
>
> **Deposits:**
> - `bellows/knowledge/qa/qa-scope-check-project-path-filter-2026-04-22.md`
> - `bellows/knowledge/qa/evidence/executable-scope-check-project-path-filter-2026-04-22/grep_signature.txt`
> - `bellows/knowledge/qa/evidence/executable-scope-check-project-path-filter-2026-04-22/grep_callsites.txt`
> - `bellows/knowledge/qa/evidence/executable-scope-check-project-path-filter-2026-04-22/grep_tests.txt`
> - `bellows/knowledge/qa/evidence/executable-scope-check-project-path-filter-2026-04-22/pytest_targeted.txt`
