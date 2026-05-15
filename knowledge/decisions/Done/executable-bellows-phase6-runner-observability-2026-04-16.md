# Bellows — Phase 6: Runner Timeout + Observability Fixes
**Date:** 2026-04-16 | **Tier:** Small | **Test Scope:** targeted | **Priority:** 1 | **Execution:** Step 1 (DEV) → Step 2 (QA)

## Context

Phase 5 diagnostic (`bellows-plan-2b-dispatch-failure-2026-04-16.md`) identified five issues in `bellows/runner.py`:

1. **300s subprocess timeout is hardcoded.** Plan 2b's complex Step 1 hit this and was killed mid-execution. Should be configurable (default 600s).
2. **Cost reported as 0.0 on timeout.** Misleading — looks identical to "subprocess never ran." Should be reported as None.
3. **Log files only written on success path.** Failed runs leave zero diagnostic trace. Should write logs on every code path.
4. **stderr is captured by subprocess but never read or logged.** When claude -p errors out, we lose the actual error message. Should be captured to log files.
5. **No try/except around `json.loads(result.stdout)`.** If claude -p returns non-JSON (auth error, CLI crash), the unhandled exception bypasses both log writing and DB recording. Should be wrapped.

All five fixes are in `runner.py` (77 lines, single file). Total change estimate: ~30 lines of code modification + ~30 lines of new tests.

## Test Scope Justification

`targeted` — this changes runner.py only. Test scope is `tests/test_runner.py` (and any other test file that imports runner directly). Full suite runs in session wrap.

## How to Run This Plan (manual bootstrap)

Bellows is paused for the runner.py fix. Paste into Claude Code:

```
Read the plan at /Users/marklehn/Desktop/GitHub/bellows/knowledge/decisions/executable-bellows-phase6-runner-observability-2026-04-16.md and execute Step 1 ONLY. After Step 1, STOP and wait for my confirmation. Do NOT proceed to Step 2 or move the plan to Done.
```

After Step 1 completes and CEO confirms, paste:
```
Now execute Step 2 of the same plan to completion.
```

---
---

## STEP 1 — DEV (Bellows Developer)

---

> **FIRST — claim this plan:** `import shutil; shutil.move("/Users/marklehn/Desktop/GitHub/bellows/knowledge/decisions/executable-bellows-phase6-runner-observability-2026-04-16.md", "/Users/marklehn/Desktop/GitHub/bellows/knowledge/decisions/in-progress-executable-bellows-phase6-runner-observability-2026-04-16.md")`. Skip specialist file and glossary reads — this is a small surgical fix to one file with a fully-spec'd Phase 5 diagnostic. Working directory is `/Users/marklehn/Desktop/GitHub/bellows`. Read `runner.py` (77 lines), `parser.py`, and `bellows.py` lines 1-100 for context on how runner is invoked. Then read the existing `tests/test_runner.py` to understand test conventions. **Five fixes, all in runner.py.** **Fix 1 — Configurable timeout.** Add a `timeout` parameter to `run_step()` with default `600`. The caller in `bellows.py` should pass `config.get("step_timeout_seconds", 600)`. Read `bellows.py` to find the `runner.run_step(...)` call site and update it to pass the config value. Add `"step_timeout_seconds": 600` to `config.example.json` (NOT `config.json` — that's the live config and the CEO will set it manually). **Fix 2 — Cost as None on timeout.** In the `TimeoutExpired` handler and the generic `Exception` handler, change `"cost_usd": 0.0` to `"cost_usd": None`. Update `bellows.py`'s `record_run()` call (or wherever cost is written to the DB) to handle None — write SQL NULL for None values. Also fix the "ceo_flags" message in the generic Exception handler — it currently says "Step timed out after 300s" even for non-timeout exceptions. Change to f-string with the actual exception: `f"Step failed: {str(e)[:200]}"`. **Fix 3 — Log files on every code path.** Refactor so a log file is written regardless of success/timeout/exception. Suggested structure: capture `timestamp` at the top of `run_step()`, build `log_path` early, define a small helper `_write_log(log_path, data)` that writes JSON-serializable data. On success, write `{"success": True, "raw_output": result.stdout, "stderr": result.stderr, "parsed": parsed}`. On timeout, write `{"success": False, "error": "timeout", "elapsed_seconds": <actual elapsed>, "stderr_partial": <whatever stderr was captured if any>}`. On generic exception, write `{"success": False, "error": str(e), "exception_type": type(e).__name__}`. **Fix 4 — Capture stderr on success path.** Currently `result.stderr` exists but is never read. The Fix 3 log structure already captures it on success. Also add `if result.stderr: print(f"[runner] stderr from claude -p: {result.stderr[:500]}", flush=True)` on the success path so it shows up in Bellows' stdout when claude -p emits warnings. **Fix 5 — Try/except around json.loads.** Wrap `raw = json.loads(result.stdout)` in try/except `json.JSONDecodeError`. On JSONDecodeError, write a log file with `{"success": False, "error": "json_decode_error", "raw_output": result.stdout[:5000], "stderr": result.stderr[:5000]}` and return the same dict shape as the timeout/exception handlers (`is_error: True, escalate: True, receipt_status: "Blocked", cost_usd: None, ...`). The session_id should be None since we couldn't parse it from the response. Also wrap `parsed = parse(raw)` in try/except since parser logic could fail on unexpected JSON shapes. **Tests.** Add at least 5 new tests to `tests/test_runner.py`: (1) timeout handler returns cost=None, (2) timeout handler writes a log file, (3) JSONDecodeError handler returns Blocked status with cost=None, (4) JSONDecodeError handler writes a log file with the raw output, (5) configurable timeout — assert that calling `run_step(..., timeout=10)` invokes subprocess with timeout=10. Use `unittest.mock.patch` on `subprocess.run` to inject failures and avoid actually calling claude -p in tests. **Run the tests:** `cd /Users/marklehn/Desktop/GitHub/bellows && python3 -m pytest tests/test_runner.py -v 2>&1 | tee /tmp/test_runner_output.txt`. All existing tests must continue to pass; new tests must pass. **Write a development log** to `/Users/marklehn/Desktop/GitHub/bellows/knowledge/development/bellows-phase6-runner-observability-2026-04-16.md` with: a summary of all 5 fixes (one paragraph each, including the line-range modified), the test results (count of tests run, count passed, any failures), and an Output Receipt with Status=Complete, Files Created or Modified (Code) listing runner.py, bellows.py, config.example.json, and tests/test_runner.py with one-line descriptions, Decisions Made (any judgment calls during implementation), Flags for CEO (anything ambiguous), Flags for Next Step (the QA step verifies all 5 fixes landed and tests still pass). **Final operations follow Rule 23 (feedback → commit → move-to-Done). Step A — Feedback append** to `/Users/marklehn/Desktop/GitHub/bellows/knowledge/research/agent-prompt-feedback.md` per the standard prompt feedback protocol. **Step B — Commit.** `cd /Users/marklehn/Desktop/GitHub/bellows && git add runner.py bellows.py config.example.json tests/test_runner.py knowledge/development/bellows-phase6-runner-observability-2026-04-16.md knowledge/research/agent-prompt-feedback.md && git commit -m "fix: runner.py phase 6 — configurable timeout, observability on all code paths"`. **End of Step 1. STOP and wait for CEO confirmation. Do NOT proceed to Step 2. Do NOT move the plan to Done.**

---
---

## STEP 2 — QA (Bellows QA)

---

> **Before starting, read `/Users/marklehn/Desktop/GitHub/bellows/knowledge/development/bellows-phase6-runner-observability-2026-04-16.md` and check the Output Receipt status field. If status is not Complete, stop and report the issue to the CEO before proceeding.** Skip specialist file and glossary reads — this is mechanical verification of a small surgical fix. Working directory is `/Users/marklehn/Desktop/GitHub/bellows`. Evidence directory is `/Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/evidence/executable-bellows-phase6-runner-observability-2026-04-16/` (mkdir -p first via Python). **Deliverable Verification (Rule 17).** Read the dev log's "Files Created or Modified (Code)" list and verify every listed deliverable. For each fix, confirm the change landed in runner.py by grepping for distinctive content. Build a verification table:

```python
import subprocess, os
os.makedirs("/Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/evidence/executable-bellows-phase6-runner-observability-2026-04-16", exist_ok=True)
checks = []
# Fix 1 — configurable timeout
r1 = subprocess.run(["grep", "-n", "timeout", "/Users/marklehn/Desktop/GitHub/bellows/runner.py"], capture_output=True, text=True)
checks.append(("Fix 1: configurable timeout in runner.py", "timeout=" in r1.stdout and "600" in r1.stdout, r1.stdout))
# Fix 1b — config.example.json updated
with open("/Users/marklehn/Desktop/GitHub/bellows/config.example.json") as f:
    cfg = f.read()
checks.append(("Fix 1b: step_timeout_seconds in config.example.json", "step_timeout_seconds" in cfg, cfg[:500]))
# Fix 2 — cost None on timeout
r2 = subprocess.run(["grep", "-n", "cost_usd", "/Users/marklehn/Desktop/GitHub/bellows/runner.py"], capture_output=True, text=True)
checks.append(("Fix 2: cost_usd: None in runner.py error paths", "None" in r2.stdout, r2.stdout))
# Fix 3 — log on all paths
r3 = subprocess.run(["grep", "-cn", "_write_log\\|log_path", "/Users/marklehn/Desktop/GitHub/bellows/runner.py"], capture_output=True, text=True)
checks.append(("Fix 3: log writing helper called multiple times", int(r3.stdout.strip()) >= 4, r3.stdout))
# Fix 4 — stderr captured
r4 = subprocess.run(["grep", "-n", "result.stderr", "/Users/marklehn/Desktop/GitHub/bellows/runner.py"], capture_output=True, text=True)
checks.append(("Fix 4: result.stderr referenced in runner.py", "stderr" in r4.stdout, r4.stdout))
# Fix 5 — JSONDecodeError handled
r5 = subprocess.run(["grep", "-n", "JSONDecodeError\\|json_decode_error", "/Users/marklehn/Desktop/GitHub/bellows/runner.py"], capture_output=True, text=True)
checks.append(("Fix 5: JSONDecodeError handler in runner.py", "JSONDecodeError" in r5.stdout, r5.stdout))
with open("/Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/evidence/executable-bellows-phase6-runner-observability-2026-04-16/grep_deliverables.txt", "w") as f:
    for name, ok, evidence in checks:
        status = "PASS" if ok else "FAIL"
        f.write(f"{status} | {name}\n  Evidence: {evidence[:300]}\n\n")
print("Deliverable verification written to grep_deliverables.txt")
for name, ok, evidence in checks:
    status = "✅" if ok else "❌"
    print(f"{status} {name}")
```

> Build a verification table from the script results: `| Deliverable | Expected | Status (✅/❌) | Evidence |`. Any ❌ row blocks the plan from moving to Done. **Test regression.** Run targeted test suite: `cd /Users/marklehn/Desktop/GitHub/bellows && python3 -m pytest tests/test_runner.py -v 2>&1 | tee /Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/evidence/executable-bellows-phase6-runner-observability-2026-04-16/pytest_targeted.txt`. Confirm all tests pass (existing + new). Note the count of tests run vs the count expected from the dev log. **Write the QA report** to `/Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/bellows-phase6-runner-observability-2026-04-16.md` with the verification table, test results summary, and a short prose summary. Include the standard Output Receipt. **Run the mandatory Rule 20 self-check:**

```python
# Rule 20 — Mandatory QA Self-Check
import os, sys
plan_slug = "executable-bellows-phase6-runner-observability-2026-04-16"
qa_report_path = "/Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/bellows-phase6-runner-observability-2026-04-16.md"
evidence_dir = f"/Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/evidence/{plan_slug}/"
required_evidence_files = [
    "grep_deliverables.txt",
    "pytest_targeted.txt",
]
hedging_keywords = ["pending", "inferred", "extrapolated", "estimated", "approximate", "skipped", "assumed", "close enough", "should pass", "would pass", "not run"]
POSITIVE_STATUS_TOKENS = ["✅", "OK", "PASS", "[x]", "done", "complete", "verified"]

def is_positive_row(line):
    if "|" not in line:
        return False
    cells = [c.strip() for c in line.split("|")]
    for cell in cells:
        for token in POSITIVE_STATUS_TOKENS:
            if token == "✅":
                if "✅" in cell:
                    return True
            else:
                if cell.lower() == token.lower():
                    return True
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
    print("\nPlan CANNOT close. Fix issues and re-run QA.")
    sys.exit(1)
else:
    print("PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.")
    print(f"Evidence folder: {evidence_dir}")
    print(f"Files verified: {len(required_evidence_files)}")
```

> **Include the literal stdout of the self-check at the end of the QA report.** If self-check FAILS, stop — do NOT move plan to Done. Report failure to CEO. If self-check PASSES, continue. **Update PROJECT_STATUS.md.** Read the current PROJECT_STATUS.md, identify a clear anchor line (use the first line under the most recent milestone section). Add a milestone entry summarizing Phase 6: "Phase 6 (2026-04-16) — runner.py observability + configurable timeout. Five fixes: configurable subprocess timeout (default 600s), cost reported as None on timeout, log files written on all code paths, stderr captured, JSONDecodeError handled. ~30 lines runner.py + tests. Resolves Plan 2b dispatch failure mode (300s timeout was killing complex Bellows steps mid-execution)." **Final operations follow Rule 23 (feedback → commit → move-to-Done). Step A — Feedback append** to `/Users/marklehn/Desktop/GitHub/bellows/knowledge/research/agent-prompt-feedback.md` per the standard prompt feedback protocol. **Step B — Final commit.** `cd /Users/marklehn/Desktop/GitHub/bellows && git add knowledge/qa/ knowledge/research/agent-prompt-feedback.md PROJECT_STATUS.md && git commit -m "qa: bellows phase 6 verification + status update"`. **Step C — Move-to-Done as the absolute last operation:** `import shutil; shutil.move("/Users/marklehn/Desktop/GitHub/bellows/knowledge/decisions/in-progress-executable-bellows-phase6-runner-observability-2026-04-16.md", "/Users/marklehn/Desktop/GitHub/bellows/knowledge/decisions/Done/executable-bellows-phase6-runner-observability-2026-04-16.md")`. **The move-to-Done is the absolute LAST operation per Rule 23.**
