# Bellows — no_permission_denials Read-Class Tool Taxonomy Fix (BACKLOG #2)
**Date:** 2026-04-28 | **Tier:** Small | **Test Scope:** full-suite | **Execution:** Step 1 (Bellows Developer) → Step 2 (Bellows QA)
**Priority:** 5

## Context

BACKLOG #2 fix, per the diagnostic at `bellows/knowledge/research/no-permission-denials-taxonomy-2026-04-28.md`. The diagnostic confirmed that 100% of observed `no_permission_denials` gate failures are caused by read-class tools (Grep, Glob) hitting cross-project paths — agents route around via bash, complete the task, but the gate fires anyway. Zero write-class denials have been observed in production.

Fix: add a `READ_CLASS_TOOLS` constant `{"Grep", "Glob", "Read"}` to `gates.py` and filter `permission_denials` by it. Read-class denials are skipped; write-class denials (everything else, including missing/None tool_name) trip the gate.

Per the diagnostic's Q5 edge case table, 8 test cases need coverage. The existing string-form denial test continues to pass (legacy strings default to write-class).

Touches load-bearing gate logic — full-suite test required per Rule 21.

## How to Run This Plan

Bellows watcher claims this plan automatically. Step 1 (Bellows Developer) edits `gates.py` and adds tests. Step 2 (Bellows QA) runs full pytest, performs behavioral verification, Rule 17 + Rule 20 checks, then commits + PROJECT_STATUS update. Per disable-auto-close, terminal step pauses for Planner verdict. **Bellows daemon restart required after this plan ships to load the new gate code.**

---
---

## STEP 1 — Bellows Developer

---

> **FIRST — claim this plan:** `import shutil; shutil.move("bellows/knowledge/decisions/executable-no-permission-denials-read-class-fix-2026-04-28.md", "bellows/knowledge/decisions/in-progress-executable-no-permission-denials-read-class-fix-2026-04-28.md")`. **Skip glossary read AND skip specialist file read** — gate-logic fix in load-bearing code, no domain or architecture context. **Mandatory read:** `bellows/knowledge/research/no-permission-denials-taxonomy-2026-04-28.md` — diagnostic findings that authorize this fix. Treat its Q4 taxonomy and Q5 edge case table as canonical. **Task 1 — add READ_CLASS_TOOLS constant.** Edit `bellows/gates.py`. Use `Filesystem:edit_file` with anchor — locate the `SCOPE_ALLOWLIST_PREFIXES` constant near the top of the file (around line 13). Replace the line `SCOPE_ALLOWLIST_PREFIXES = ("in-progress-", "verdict-pending-", "halted-")` with that line followed by `\n\n# Read-class tools whose denials do NOT block agent execution. Agents fall back\n# to bash equivalents (grep/rg, find/ls, cat) when these are denied. Per BACKLOG #2\n# diagnostic at knowledge/research/no-permission-denials-taxonomy-2026-04-28.md.\nREAD_CLASS_TOOLS = {"Grep", "Glob", "Read"}`. **Task 2 — modify _gate_no_permission_denials.** Edit `bellows/gates.py` again. Locate the function at line 101. Use `Filesystem:edit_file` with the entire function body as the anchor. Replace this exact text:
>
> ```
> def _gate_no_permission_denials(parsed, failures):
>     denials = parsed.get("permission_denials", [])
>     if denials:
>         first = denials[0] if isinstance(denials[0], str) else str(denials[0])
>         failures.append({
>             "gate": "no_permission_denials",
>             "evidence": f"{len(denials)} denial(s): {first}",
>         })
> ```
>
> with:
>
> ```
> def _gate_no_permission_denials(parsed, failures):
>     denials = parsed.get("permission_denials", [])
>     blocking = []
>     for d in denials:
>         if isinstance(d, dict):
>             tool_name = d.get("tool_name")
>             if tool_name in READ_CLASS_TOOLS:
>                 continue
>             blocking.append(d)
>         else:
>             # String-form denial (legacy) has no tool_name — default to blocking
>             blocking.append(d)
>     if blocking:
>         first = blocking[0] if isinstance(blocking[0], str) else str(blocking[0])
>         failures.append({
>             "gate": "no_permission_denials",
>             "evidence": f"{len(blocking)} blocking denial(s): {first}",
>         })
> ```
>
> **Task 3 — add tests.** Edit `bellows/tests/test_gates.py`. After the existing `test_permission_denials_nonempty` function (find it via grep, around line 73), append 7 new test functions covering the diagnostic's edge cases. Use `Filesystem:edit_file` with the existing test function's last line as the anchor. The new tests are: (a) `test_permission_denials_read_class_only_passes` — denials list with only Grep/Glob/Read dicts, gate should pass; (b) `test_permission_denials_write_class_fails` — denial with `tool_name: "Edit"`, gate should fail; (c) `test_permission_denials_mixed_read_write_fails` — list with Grep + Edit dicts, gate should fail with count=1 (only the write-class one counted); (d) `test_permission_denials_missing_tool_name_fails` — denial dict without `tool_name` key, gate should fail (default to write-class); (e) `test_permission_denials_none_tool_name_fails` — denial with `tool_name: None`, gate should fail; (f) `test_permission_denials_unknown_tool_fails` — denial with `tool_name: "SomeNewTool"`, gate should fail (allowlist semantics); (g) `test_permission_denials_string_form_fails` — string-form denial without dict, gate should fail (legacy support, defaults to write-class). Each test follows the existing pattern: build `parsed` via `_clean_parsed()`, set `permission_denials`, call `gates.check`, assert pass/fail and evidence. **Task 4 — run targeted tests first.** `cd /Users/marklehn/Desktop/GitHub/bellows && python -m pytest tests/test_gates.py -v 2>&1 | tail -25`. Expected: existing tests pass + 7 new tests pass. If any fail, debug before proceeding. **Task 5 — write dev log.** Use `Filesystem:write_file` to deposit `bellows/knowledge/development/no-permission-denials-read-class-fix-dev-2026-04-28.md` with: (a) the READ_CLASS_TOOLS constant added; (b) the function modification (before/after); (c) 7 new test names; (d) targeted test output tail; (e) reference to the diagnostic. **Task 6 — commit.** `cd /Users/marklehn/Desktop/GitHub/bellows && git add gates.py tests/test_gates.py knowledge/development/no-permission-denials-read-class-fix-dev-2026-04-28.md && git commit -m "fix(gates): exempt read-class tools from no_permission_denials — BACKLOG #2"`. **Standard prompt feedback protocol** → `bellows/knowledge/research/agent-prompt-feedback.md`.
>
> **Deposits:**
> - `bellows/knowledge/development/no-permission-denials-read-class-fix-dev-2026-04-28.md`

---
---

## STEP 2 — Bellows QA

---

> **Before starting, read `bellows/knowledge/development/no-permission-denials-read-class-fix-dev-2026-04-28.md` and check the Output Receipt status. If status is not Complete, stop and report the blocker before proceeding.** **Skip glossary AND specialist file reads** — gate-logic verification. **FIRST — Deliverable Verification (Rule 17).** Read the Step 1 Output Receipt "Files Created or Modified (Code)" list. For each listed file, verify changes landed: (a) `grep -n "READ_CLASS_TOOLS" /Users/marklehn/Desktop/GitHub/bellows/gates.py` should return at least 2 matches (constant definition + use in function); (b) `grep -n "blocking" /Users/marklehn/Desktop/GitHub/bellows/gates.py` should show the new variable in the modified function; (c) `grep -c "test_permission_denials_" /Users/marklehn/Desktop/GitHub/bellows/tests/test_gates.py` should return at least 8 (1 existing + 7 new). Pipe ALL output to `bellows/knowledge/qa/evidence/executable-no-permission-denials-read-class-fix-2026-04-28/grep_deliverables.txt`. Build a 3-row verification table. **Task 1 — full pytest suite.** `cd /Users/marklehn/Desktop/GitHub/bellows && python -m pytest tests/ -v 2>&1 | tee bellows/knowledge/qa/evidence/executable-no-permission-denials-read-class-fix-2026-04-28/pytest_full.txt`. Expected: prior baseline + 7 new tests, zero regressions. The pre-existing `test_run_step_timeout` failure (per BACKLOG #2 closure note) is allowed. **Task 2 — behavioral verification.** Run this Python and pipe output to `bellows/knowledge/qa/evidence/executable-no-permission-denials-read-class-fix-2026-04-28/behavioral_check.txt`: `cd /Users/marklehn/Desktop/GitHub/bellows && python3 -c "
import gates
# Simulate a production denial — Grep against governance root (BACKLOG #2's exact pattern)
real_denial = {'tool_name': 'Grep', 'tool_use_id': 'toolu_test', 'tool_input': {'pattern': 'test', 'path': '/Users/marklehn/Desktop/GitHub/PLANNER_TEMPLATE.md'}}
parsed = {'receipt_status': 'Complete', 'ceo_flags': [], 'is_error': False, 'permission_denials': [real_denial], 'result_text': ''}
result = gates.check(parsed, '## STEP 1 — Test\n\nNo deposits required.\n', 1, '/tmp')
gate_failures = [f for f in result['failures'] if f['gate'] == 'no_permission_denials']
print('Real production denial (Grep against governance root):')
print(f'  no_permission_denials gate fired: {len(gate_failures) > 0}')
print(f'  Expected: False (read-class denial should be filtered)')
# Compare to write-class denial
write_denial = {'tool_name': 'Edit', 'tool_use_id': 'toolu_test', 'tool_input': {}}
parsed['permission_denials'] = [write_denial]
result2 = gates.check(parsed, '## STEP 1 — Test\n\nNo deposits required.\n', 1, '/tmp')
gate_failures2 = [f for f in result2['failures'] if f['gate'] == 'no_permission_denials']
print()
print('Write-class denial (Edit):')
print(f'  no_permission_denials gate fired: {len(gate_failures2) > 0}')
print(f'  Expected: True (write-class denial should still trip gate)')
" 2>&1 | tee bellows/knowledge/qa/evidence/executable-no-permission-denials-read-class-fix-2026-04-28/behavioral_check.txt`. Expected output: Grep denial does NOT fire gate (False); Edit denial DOES fire gate (True). If either is wrong, flag as Critical. **Task 3 — write QA report.** Use `Filesystem:write_file` to write `bellows/knowledge/qa/no-permission-denials-read-class-fix-qa-2026-04-28.md` with: (1) Rule 17 deliverable verification table (3 rows ✅); (2) test execution summary citing pytest_full.txt (count before/after, all passing); (3) behavioral check summary citing behavioral_check.txt (Grep filtered, Edit blocked); (4) verdict on closure of BACKLOG #2. **Task 4 — Rule 20 self-check.** Run this Python block exactly as written and include literal stdout in QA report:
>
> ```python
> # Rule 20 — Mandatory QA Self-Check
> import os, sys
> plan_slug = "executable-no-permission-denials-read-class-fix-2026-04-28"
> qa_report_path = "/Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/no-permission-denials-read-class-fix-qa-2026-04-28.md"
> evidence_dir = f"/Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/evidence/{plan_slug}/"
> required_evidence_files = ["grep_deliverables.txt", "pytest_full.txt", "behavioral_check.txt"]
> hedging_keywords = ["pending", "inferred", "extrapolated", "estimated", "approximate", "skipped", "assumed", "close enough", "should pass", "would pass", "not run"]
> POSITIVE_STATUS_TOKENS = ["✅", "OK", "PASS", "done", "complete", "verified"]
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
> If FAILED, stop and report. If PASSED, proceed. **Task 5 — Update PROJECT_STATUS.md.** Use `Filesystem:edit_file` to add a milestone entry referencing BACKLOG #2 closure, the read-class taxonomy, 7 new tests, and the Bellows-restart requirement. Anchor: read the current file first to identify the exact heading or top of Completed Milestones. **Task 6 — Standard prompt feedback protocol** → `bellows/knowledge/research/agent-prompt-feedback.md`. **Task 7 — final commit.** `cd /Users/marklehn/Desktop/GitHub/bellows && git add PROJECT_STATUS.md knowledge/qa/no-permission-denials-read-class-fix-qa-2026-04-28.md knowledge/qa/evidence/executable-no-permission-denials-read-class-fix-2026-04-28/ knowledge/research/agent-prompt-feedback.md && git commit -m "qa: no_permission_denials read-class fix verified, BACKLOG #2 closed"`. **STOP.** Do NOT move this plan to Done/. The Planner performs the terminal move after Rule 22 verification passes.
>
> **Deposits:**
> - `bellows/knowledge/qa/no-permission-denials-read-class-fix-qa-2026-04-28.md`
> - `bellows/knowledge/qa/evidence/executable-no-permission-denials-read-class-fix-2026-04-28/grep_deliverables.txt`
> - `bellows/knowledge/qa/evidence/executable-no-permission-denials-read-class-fix-2026-04-28/pytest_full.txt`
> - `bellows/knowledge/qa/evidence/executable-no-permission-denials-read-class-fix-2026-04-28/behavioral_check.txt`
