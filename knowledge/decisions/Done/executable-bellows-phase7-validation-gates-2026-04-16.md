# Bellows — Phase 7: Validation Gates + Verdict Queue
**Date:** 2026-04-16 | **Tier:** Medium | **Test Scope:** targeted | **Priority:** 1 | **Execution:** Step 1 (DEV) → Step 2 (QA)

## Context

Today's Planner-Bellows architecture discussion reached a clear conclusion: Bellows is an execution engine + activity monitor, not an intelligence layer. planner.py's current role (spawning a claude -p subprocess to make AI-driven continue/escalate decisions between steps) is being replaced by `gates.py` — a module of mechanical validation checks that run after each step and flag anomalies for Planner review.

**The model:**
- Bellows dispatches agents, produces logs, runs validation gates after each step
- Gates are mechanical pass/fail checks: deposit exists? receipt complete? status=Complete? files in scope? cost normal? Plus activity monitoring: full file-change audit per step, scope check comparing actual file changes against plan expectations.
- When all gates pass on a non-QA step → Bellows continues autonomously
- When any gate fails OR the step is a QA step → Bellows posts a verdict request and pauses the plan
- Planner (in conversation with CEO) reads the verdict request, reads the deposit, renders continue/stop
- Verdict file written to resolved/ folder; Bellows picks it up and acts

**What this replaces:** planner.py's `consult()` function. The entire claude -p planner subprocess is removed from the step-transition loop. planner.py stays on disk but is no longer imported or called by bellows.py.

## Files changed

- **NEW:** `gates.py` — validation gate runner with 8 gates (~120 lines)
- **NEW:** `tests/test_gates.py` — test coverage for each gate (~140 lines)
- **MODIFIED:** `bellows.py` — replace `planner.consult()` calls with `gates.check()` + verdict logic (~40 lines changed)
- **MODIFIED:** `notifier.py` — add `notify_verdict_request()` function (~10 lines)
- **NEW:** `bellows/verdicts/` directory with `pending/` and `resolved/` subdirectories + `ledger.jsonl`

## How to Run This Plan

Manual bootstrap (Bellows is the subject of the fix — don't run through Bellows itself). Paste into Claude Code:

```
Read the plan at /Users/marklehn/Desktop/GitHub/bellows/knowledge/decisions/executable-bellows-phase7-validation-gates-2026-04-16.md and execute Step 1 ONLY. After Step 1, STOP and wait for my confirmation. Do NOT proceed to Step 2 or move the plan to Done.
```


---
---

## STEP 1 — DEV (Bellows Developer)

---

> **FIRST — claim this plan:** `import shutil; shutil.move("/Users/marklehn/Desktop/GitHub/bellows/knowledge/decisions/executable-bellows-phase7-validation-gates-2026-04-16.md", "/Users/marklehn/Desktop/GitHub/bellows/knowledge/decisions/in-progress-executable-bellows-phase7-validation-gates-2026-04-16.md")`. Skip specialist file and glossary reads — this is infrastructure work with the full spec in this plan. Working directory: `/Users/marklehn/Desktop/GitHub/bellows`. Read `bellows.py`, `parser.py`, `runner.py`, `notifier.py`, and `planner.py` for current state. Also read `tests/test_planner.py` and `tests/test_bellows.py` for test conventions. **BUILD gates.py (~80 lines).** Create `gates.py` in the bellows root directory. Structure: one public function `check(parsed, plan_text, step_number, project_path)` that returns a dict `{"passed": bool, "failures": [{"gate": str, "evidence": str}], "is_qa_step": bool}`. Internally, `check()` runs each gate function and collects failures. The individual gate functions are: **(1) `_gate_receipt_status`:** checks `parsed["receipt_status"]` is "Complete". If "Partial", "Blocked", or "Unknown", fail with evidence = the actual status value. **(2) `_gate_ceo_flags`:** checks `parsed["ceo_flags"]` is empty. If non-empty, fail with evidence = the flag text. **(3) `_gate_no_errors`:** checks `parsed["is_error"]` is False. If True, fail with evidence = `parsed.get("error", "unknown error")`. **(4) `_gate_no_permission_denials`:** checks `parsed["permission_denials"]` is empty. If non-empty, fail with evidence = count and first denial text. **(5) `_gate_deposit_exists`:** parses `parsed["result_text"]` for `### Files Deposited` section, extracts file paths, checks each with `os.path.isfile()`. If any path doesn't exist, fail with evidence = the missing path(s). If no Files Deposited section found, pass with no failure (not all steps deposit files). **(6) `_gate_is_qa_step`:** not a pass/fail gate — just detects whether the current step is a QA step by checking if the plan text's `## STEP {step_number}` header contains "QA" (case-insensitive). Sets `is_qa_step` in the result. **(7) `_gate_file_change_audit`:** takes a `files_changed` list (provided by bellows.py from a pre/post `git diff --stat` — see bellows.py modifications below) and logs it as the step's activity record. This gate does NOT pass/fail — it records. The `files_changed` list is included in the gate result under `"files_changed"` for the verdict request and ledger. **(8) `_gate_scope_check`:** extracts file paths mentioned in the current step's prompt text (the blockquote under `## STEP {step_number}` in the plan) using a regex for paths containing `/` that look like project paths (e.g., `/Users/...`, `src/...`, `knowledge/...`). Compares against `files_changed` from Gate 7. If any file in `files_changed` is NOT mentioned in the step's prompt text, fail with evidence = the out-of-scope file path(s) + the plan step text that was searched (first 200 chars for context). If all changed files are mentioned in the prompt, pass. Note: some files are always expected (e.g., `agent-prompt-feedback.md` for the feedback protocol) — maintain a small allowlist of always-permitted paths that don't need explicit mention in the plan. **The `check()` function assembles results from all gates and returns.** `passed` is True only if zero failures from gates 1-5 and 8 (gates 6 and 7 are informational, not pass/fail). `is_qa_step` is always populated regardless of pass/fail. `files_changed` is always populated from Gate 7. **BUILD verdict.py (~60 lines).** Create `verdict.py` in the bellows root directory. Three functions: **(1) `post_verdict_request(plan_path, step_number, log_path, gate_result, planner_py_decision=None)`:** creates a verdict request markdown file at `bellows/verdicts/pending/verdict-request-{plan_slug}-step-{N}.md`. Contents: plan path, step number, log file path, gate failures (each gate name + evidence), timestamp. If `planner_py_decision` is provided (for backward compat during transition), include it. Creates the `verdicts/pending/` directory if it doesn't exist. **(2) `check_verdict(plan_slug, step_number)`:** checks if a verdict file exists at `bellows/verdicts/resolved/verdict-{plan_slug}-step-{N}.md`. If it exists, reads line 1 which must be `verdict: continue` or `verdict: stop`. Returns `{"found": True, "verdict": "continue"|"stop", "reason": <rest of file>}` or `{"found": False}`. **(3) `log_to_ledger(plan_path, step_number, gate_result, verdict, reason)`:** appends a JSON line to `bellows/verdicts/ledger.jsonl` containing: timestamp, plan_path, step, gate failures, verdict, reason. Creates file if it doesn't exist. **MODIFY bellows.py — replace planner.consult() with gates + verdict.** In `run_plan()`, the current planner consultation loop (lines ~194-228) becomes: **Before each step dispatch,** capture the pre-step file state by running `subprocess.run(["git", "--no-pager", "diff", "--stat"], cwd=project_path, capture_output=True, text=True, timeout=10)` — store the output (may be empty if working tree is clean). **After each step dispatch + record_run,** capture post-step file state with the same `git diff --stat` command. Parse the diff to extract the list of files changed (each line of `git diff --stat` output before the summary line contains a filename). Pass this `files_changed` list to `gates.check(parsed, plan_text, current_step, project_path, files_changed=files_changed)`. **If gate_result passed AND NOT is_qa_step:** continue to next step (use default next-step prompt, no AI consultation). **If any gate failed OR is_qa_step:** call `verdict.post_verdict_request(...)`, send Pushover notification via `notifier.notify_verdict_request(...)`, rename plan from `in-progress-` to `verdict-pending-` prefix, log to DB with status "VerdictPending", and **return from run_plan()**. The plan stops here. It will be resumed when the verdict appears. **Add a verdict-consumption scan** to the `_rescan()` method in the `Bellows` class: on each 30-second rescan, check `bellows/verdicts/resolved/` for verdict files. For each verdict file found, extract the plan_slug and step_number from the filename, find the corresponding `verdict-pending-{slug}.md` in the project's decisions folder, read the verdict (continue/stop). If continue: rename `verdict-pending-` back to `in-progress-`, log verdict to ledger, dispatch the next step. If stop: rename `verdict-pending-` to `halted-` (or leave as verdict-pending), log to ledger, send Pushover notification "Plan halted by Planner verdict." Move both the request and verdict files to `bellows/verdicts/resolved/` (request may already be there). **Remove the planner import.** Delete `import planner` from bellows.py. The `planner.consult()` call no longer exists. Leave planner.py on disk for reference but it's dead code now. **MODIFY notifier.py — add notify_verdict_request().** Add: `def notify_verdict_request(app_key, user_key, plan_name, step, gate_failures): return push(app_key, user_key, title="Bellows — Verdict Needed", message=f"Plan: {plan_name}\nStep: {step}\nGate failures: {', '.join(f['gate'] for f in gate_failures) if gate_failures else 'QA checkpoint (all gates passed)'}")`. **CREATE directory structure.** `os.makedirs("bellows/verdicts/pending", exist_ok=True)` and `os.makedirs("bellows/verdicts/resolved", exist_ok=True)` — either in verdict.py's functions or in bellows.py startup. **WRITE tests/test_gates.py.** At least 12 tests: (1) all gates pass on clean parsed output → `passed=True`, (2) receipt_status Blocked → gate fails with evidence, (3) receipt_status Partial → gate fails, (4) ceo_flags non-empty → gate fails with flag text, (5) is_error True → gate fails, (6) permission_denials non-empty → gate fails with count, (7) deposit path missing from disk → gate fails with path, (8) QA step detection → is_qa_step True when step header contains "QA", (9) file_change_audit populates files_changed list from input, (10) scope_check passes when all changed files are mentioned in plan, (11) scope_check fails when a changed file is NOT in plan, (12) scope_check allowlist — agent-prompt-feedback.md doesn't trigger failure. Use `unittest.mock.patch("os.path.isfile")` for deposit checks to avoid filesystem dependency in tests. **WRITE tests/test_verdict.py.** At least 4 tests: (1) post_verdict_request creates file in pending/ with correct content, (2) check_verdict returns found=False when no file exists, (3) check_verdict reads "verdict: continue" correctly, (4) log_to_ledger appends valid JSON line. Use `tmp_path` fixture or mock filesystem. **Run all tests:** `cd /Users/marklehn/Desktop/GitHub/bellows && python3 -m pytest tests/ -v 2>&1 | tee /tmp/test_bellows_all.txt`. All existing tests must still pass. New tests must pass. If any existing test fails because it imports or mocks planner, update it to reflect the new architecture (planner is no longer called from bellows.py). **Write a development log** to `/Users/marklehn/Desktop/GitHub/bellows/knowledge/development/bellows-phase7-validation-gates-2026-04-16.md` with: summary of all changes per file, the gate list with descriptions, the verdict flow (request → poll → consume → act), test results (count run, count passed, any failures), Output Receipt with Status=Complete. **Final operations follow Rule 23.** Step A — Feedback append to `/Users/marklehn/Desktop/GitHub/bellows/knowledge/research/agent-prompt-feedback.md`. Step B — Commit: `cd /Users/marklehn/Desktop/GitHub/bellows && git add gates.py verdict.py bellows.py notifier.py tests/test_gates.py tests/test_verdict.py knowledge/development/bellows-phase7-validation-gates-2026-04-16.md knowledge/research/agent-prompt-feedback.md && git commit -m "feat: phase 7 — validation gates replace planner.py AI consultation, verdict queue for async Planner review"`. **End of Step 1. STOP and wait for CEO confirmation. Do NOT proceed to Step 2. Do NOT move the plan to Done.**


---
---

## STEP 2 — QA (Bellows QA)

---

> **Before starting, read `/Users/marklehn/Desktop/GitHub/bellows/knowledge/development/bellows-phase7-validation-gates-2026-04-16.md` and check the Output Receipt status field. If status is not Complete, stop and report the issue to the CEO before proceeding.** Skip specialist file and glossary reads. Working directory: `/Users/marklehn/Desktop/GitHub/bellows`. Evidence directory: `/Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/evidence/executable-bellows-phase7-validation-gates-2026-04-16/` (mkdir -p first via Python). **Deliverable Verification (Rule 17).** Run the following checks and pipe output to `grep_deliverables.txt`:

```python
import os
os.makedirs("/Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/evidence/executable-bellows-phase7-validation-gates-2026-04-16", exist_ok=True)
checks = []
# Check 1: gates.py exists
checks.append(("gates.py exists", os.path.isfile("/Users/marklehn/Desktop/GitHub/bellows/gates.py"), ""))
# Check 2: verdict.py exists
checks.append(("verdict.py exists", os.path.isfile("/Users/marklehn/Desktop/GitHub/bellows/verdict.py"), ""))
# Check 3: gates.py has check() function
with open("/Users/marklehn/Desktop/GitHub/bellows/gates.py") as f:
    gc = f.read()
checks.append(("gates.py has check() function", "def check(" in gc, ""))
# Check 4: gates.py has all 6 gate functions
for gate in ["_gate_receipt_status", "_gate_ceo_flags", "_gate_no_errors", "_gate_no_permission_denials", "_gate_deposit_exists", "_gate_is_qa_step", "_gate_file_change_audit", "_gate_scope_check"]:
    checks.append((f"gates.py has {gate}", gate in gc, ""))
# Check 5: verdict.py has post/check/log functions
with open("/Users/marklehn/Desktop/GitHub/bellows/verdict.py") as f:
    vc = f.read()
for fn in ["post_verdict_request", "check_verdict", "log_to_ledger"]:
    checks.append((f"verdict.py has {fn}", fn in vc, ""))
# Check 6: bellows.py no longer imports planner
with open("/Users/marklehn/Desktop/GitHub/bellows/bellows.py") as f:
    bc = f.read()
checks.append(("bellows.py does NOT import planner", "import planner" not in bc, f"'import planner' found: {'import planner' in bc}"))
# Check 7: bellows.py imports gates
checks.append(("bellows.py imports gates", "import gates" in bc or "from gates" in bc, ""))
# Check 8: bellows.py imports verdict
checks.append(("bellows.py imports verdict", "import verdict" in bc or "from verdict" in bc, ""))
# Check 9: notifier.py has notify_verdict_request
with open("/Users/marklehn/Desktop/GitHub/bellows/notifier.py") as f:
    nc = f.read()
checks.append(("notifier.py has notify_verdict_request", "notify_verdict_request" in nc, ""))
# Check 10: verdicts directories exist
checks.append(("verdicts/pending/ exists", os.path.isdir("/Users/marklehn/Desktop/GitHub/bellows/verdicts/pending"), ""))
checks.append(("verdicts/resolved/ exists", os.path.isdir("/Users/marklehn/Desktop/GitHub/bellows/verdicts/resolved"), ""))
# Check 11: test files exist
checks.append(("tests/test_gates.py exists", os.path.isfile("/Users/marklehn/Desktop/GitHub/bellows/tests/test_gates.py"), ""))
checks.append(("tests/test_verdict.py exists", os.path.isfile("/Users/marklehn/Desktop/GitHub/bellows/tests/test_verdict.py"), ""))
with open("/Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/evidence/executable-bellows-phase7-validation-gates-2026-04-16/grep_deliverables.txt", "w") as f:
    for name, ok, evidence in checks:
        status = "PASS" if ok else "FAIL"
        f.write(f"{status} | {name} | {evidence}\n")
print("Deliverable verification:")
for name, ok, evidence in checks:
    status = "✅" if ok else "❌"
    print(f"{status} {name}")
```

> Build a verification table: `| Deliverable | Expected | Status (✅/❌) | Evidence |`. Any ❌ row blocks. **Test regression.** Run the FULL test suite: `cd /Users/marklehn/Desktop/GitHub/bellows && python3 -m pytest tests/ -v 2>&1 | tee /Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/evidence/executable-bellows-phase7-validation-gates-2026-04-16/pytest_full.txt`. Confirm all tests pass (existing + new). Note total count and any failures. If any existing test that previously imported or mocked planner now fails, that's expected and should have been fixed in Step 1 — flag but don't block. **Architecture verification.** Read bellows.py's `run_plan()` function end-to-end and confirm: (a) planner.consult() is no longer called anywhere, (b) gates.check() is called after every step dispatch, (c) verdict request is posted when gates fail OR step is QA, (d) plan is renamed to verdict-pending when a verdict is posted, (e) verdict consumption logic exists in _rescan() or equivalent. Write a 1-paragraph summary of the flow to `architecture_check.txt`. **Write the QA report** to `/Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/bellows-phase7-validation-gates-2026-04-16.md` with the verification table, test results, architecture summary, and Output Receipt. **Run the mandatory Rule 20 self-check:**

```python
import os, sys
plan_slug = "executable-bellows-phase7-validation-gates-2026-04-16"
qa_report_path = "/Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/bellows-phase7-validation-gates-2026-04-16.md"
evidence_dir = f"/Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/evidence/{plan_slug}/"
required_evidence_files = ["grep_deliverables.txt", "pytest_full.txt", "architecture_check.txt"]
hedging_keywords = ["pending", "inferred", "extrapolated", "estimated", "approximate", "skipped", "assumed", "close enough", "should pass", "would pass", "not run"]
POSITIVE_STATUS_TOKENS = ["✅", "OK", "PASS", "[x]", "done", "complete", "verified"]
def is_positive_row(line):
    if "|" not in line: return False
    cells = [c.strip() for c in line.split("|")]
    for cell in cells:
        for token in POSITIVE_STATUS_TOKENS:
            if token == "✅":
                if "✅" in cell: return True
            else:
                if cell.lower() == token.lower(): return True
    return False
failures = []
if not os.path.isdir(evidence_dir):
    failures.append(f"CRITICAL: evidence folder missing: {evidence_dir}")
else:
    for fname in required_evidence_files:
        fpath = os.path.join(evidence_dir, fname)
        if not os.path.isfile(fpath):
            failures.append(f"CRITICAL: evidence file missing: {fpath}")
        elif os.path.getsize(fpath) == 0:
            failures.append(f"CRITICAL: evidence file empty: {fpath}")
if os.path.isfile(qa_report_path):
    with open(qa_report_path, "r") as f:
        report = f.read()
    for line in report.splitlines():
        if is_positive_row(line):
            lower = line.lower()
            for kw in hedging_keywords:
                if kw in lower:
                    failures.append(f"CRITICAL: hedging keyword '{kw}' in positive-status row: {line.strip()[:120]}")
                    break
else:
    failures.append(f"CRITICAL: QA report not found at {qa_report_path}")
print("=" * 60)
print("Rule 20 — QA Self-Check Results")
print("=" * 60)
if failures:
    print(f"FAILED — SELF-CHECK FAILED — {len(failures)} issue(s):")
    for f in failures:
        print(f"  - {f}")
    sys.exit(1)
else:
    print("PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.")
    print(f"Files verified: {len(required_evidence_files)}")
```

> **Include the literal stdout of the self-check at the end of the QA report.** If self-check FAILS, stop — do NOT move plan to Done. If PASSES, continue. **Update PROJECT_STATUS.md.** Add milestone: "Phase 7 (2026-04-16) — Validation gates replace AI planner consultation. New gates.py module with 8 gates: 5 pass/fail checks (receipt_status, ceo_flags, errors, permission_denials, deposit_exists), 1 always-verdict trigger (qa_step_detection), 1 activity recorder (file_change_audit via git diff), 1 scope validator (scope_check comparing actual changes against plan). New verdict.py module for async verdict queue (pending/resolved folders + ledger). bellows.py now runs gates after each step instead of spawning claude -p for planner consultation. Verdict requests posted when gates fail or QA step completes. planner.py no longer called." **Final operations follow Rule 23 (feedback → commit → move-to-Done). Step A — Feedback append** to `/Users/marklehn/Desktop/GitHub/bellows/knowledge/research/agent-prompt-feedback.md`. **Step B — Final commit:** `cd /Users/marklehn/Desktop/GitHub/bellows && git add knowledge/qa/ knowledge/research/agent-prompt-feedback.md PROJECT_STATUS.md && git commit -m "qa: phase 7 validation gates verification + status update"`. **Step C — Move-to-Done as the absolute last operation:** `import shutil; shutil.move("/Users/marklehn/Desktop/GitHub/bellows/knowledge/decisions/in-progress-executable-bellows-phase7-validation-gates-2026-04-16.md", "/Users/marklehn/Desktop/GitHub/bellows/knowledge/decisions/Done/executable-bellows-phase7-validation-gates-2026-04-16.md")`. **The move-to-Done is the absolute LAST operation per Rule 23.**
