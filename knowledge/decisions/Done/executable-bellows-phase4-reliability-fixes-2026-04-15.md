# Bellows — Phase 4: Reliability Fixes (Parser + Strand + Planner Retry)
**Date:** 2026-04-15 | **Tier:** Medium | **Test Scope:** full-suite | **Priority:** 1 | **Execution:** Step 1 (DEV) → Step 2 (QA) | **Run mode:** Manual bootstrap in Claude Code (Bellows is paused — and is the thing being fixed)

## Context

Phase 3 reproduction (`bellows-reproduce-bugs-2026-04-15.md`) confirmed two independent root causes for Bellows reliability issues:

**Bug 1 — Parser data-source mismatch.** `parser.py:14-19` searches the agent's conversational `result_text` for `**Status:** Complete`, but 28 of 30 production logs do not contain this string. The Output Receipt is written into deposited markdown files only. Result: every Bellows run records `status="Unknown"` regardless of actual outcome.

**Bug 2 — Planner consultation failures cause silent strands.** When `planner.consult()` fails (transient sonnet auth error, JSON parse error, timeout), it returns `decision="escalate"`. Bellows fires a Pushover escalation and waits 1 hour. If no CEO response, `run_plan()` returns early at line 195, **bypassing the strand check at lines 218-223**. The plan stays as `in-progress-*` forever with no STRANDED notification. Phase 3.5 confirmed today's single-step strand was environmental noise (transient sonnet auth failure), not a separate bug — this fix covers that case too.

This plan implements four fixes that close both bugs:

| Fix | File | Scope |
|---|---|---|
| **Fix 2c** | `bellows.py` | Add planner consultation logging to stdout (1 line — provides debugging visibility for the other fixes) |
| **Fix 1** | `parser.py` | Replace text-scan with stop_reason-based status inference (~8 lines) |
| **Fix 2a** | `bellows.py` | Refactor escalation early-return to pass through strand check (~10 lines) |
| **Fix 2b** | `planner.py` | Add retry-on-auth-failure with 5s delay, fall back to "continue" on transient failures, log consultation results to file (~15 lines) |

Total: ~30 lines across 3 files. Shipped together because they jointly close the strand pattern; QA needs to verify them as a set.

**Bellows is paused for this plan.** Run via manual Claude Code bootstrap. After Phase 4 ships and QA passes, Bellows can be restarted.

## How to Run This Plan

In a Claude Code session, paste:

```
Read the plan at /Users/marklehn/Desktop/GitHub/bellows/knowledge/decisions/executable-bellows-phase4-reliability-fixes-2026-04-15.md and execute Step 1. Claim the plan first by renaming it to in-progress-, then complete Step 1 and STOP. Wait for my confirmation before proceeding to Step 2.
```

After Step 1 completes, paste the same prompt with "Step 2" instead of "Step 1".

---
---

## STEP 1 — DEV (Bellows Developer)

---

> **FIRST — claim this plan:** `import shutil; shutil.move("/Users/marklehn/Desktop/GitHub/bellows/knowledge/decisions/executable-bellows-phase4-reliability-fixes-2026-04-15.md", "/Users/marklehn/Desktop/GitHub/bellows/knowledge/decisions/in-progress-executable-bellows-phase4-reliability-fixes-2026-04-15.md")`. Skip specialist file and glossary reads — implementation references are fully specified in this plan from Phase 2 and Phase 3 findings. Working directory is `/Users/marklehn/Desktop/GitHub/bellows`. **Read the Phase 2 and Phase 3 findings first to confirm context:** `knowledge/research/bellows-dispatch-path-2026-04-15.md` and `knowledge/research/bellows-reproduce-bugs-2026-04-15.md`. **Implement four fixes in dependency order.** **Fix 2c first (logging — provides debugging visibility for the other three).** In `bellows.py`, find the call to `planner.consult()` inside the while loop in `run_plan()` (around line 180-195 per Phase 2). Immediately after the `consult()` call returns, add a single line: `print(f"Bellows: Planner decision for {plan_name} step {current_step}: {decision} — {reason}")`. Use the actual variable names returned by `consult()` — the Phase 2 findings indicated `decision` and `reason` are the keys but verify against the actual code. **Fix 1 second (parser).** In `parser.py`, replace the text-scan logic at lines 14-19 with stop_reason-based inference. The current code searches `result_text` for `**Status:** Complete`. Replace with the logic Phase 3 specified: `if is_error: receipt_status = "Blocked"; elif stop_reason == "end_turn": receipt_status = "Complete"; elif stop_reason == "max_tokens": receipt_status = "Partial"; else: receipt_status = "Unknown"`. Use the actual variable names from the parser context — `is_error` and `stop_reason` come from the JSON output. Make sure both fields are extracted from the input dict before the conditional. Remove the now-dead text-scan loop. **Fix 2a third (strand check refactor).** In `bellows.py` `run_plan()`, the current control flow has an early `return` at the escalation timeout path (Phase 2 identified this around line 195) that bypasses the strand check at lines 218-223. Refactor so that all exits from `run_plan()` pass through the strand check. Specifically: replace the early `return` with a `break` out of the while loop, OR set a flag (`escalation_aborted = True`) before the return and check it after the loop. Either approach works — pick the one that requires fewer changes. The strand check at lines 218-223 should then run on the escalation-aborted plans, fire the STRANDED notification (instead of silent halt), and exit. **Fix 2b fourth (planner retry).** In `planner.py`, find the function that calls `claude -p --model claude-sonnet-4-6` (likely `consult()` or similar). Add: (a) **retry on auth failure** — if the subprocess returns a 401 auth error, sleep 5 seconds and retry once. (b) **fallback to continue on transient failure** — if the second attempt also fails OR if the subprocess returns a JSON parse error or non-judgment failure, return `decision="continue"` with `reason="Planner unavailable — defaulting to continue"`. The fallback should NOT apply to genuine judgment outputs (e.g., the planner returns `escalate` deliberately) — only to subprocess failures. (c) **log consultation results to a file** — append every consultation result (success or failure, decision, reason, model used, duration) to `logs/planner-consultation.jsonl` as a single-line JSON object. Create the file if it doesn't exist. **After all four fixes are in place:** run the full test suite: `python3 -m pytest tests/ -v`. Report pass/fail count. Run `python3 -m pytest tests/ -v 2>&1 | tee knowledge/qa/evidence/executable-bellows-phase4-reliability-fixes-2026-04-15/pytest_targeted.txt` to capture evidence (mkdir -p the evidence dir first via Python). **Write a development log** to `knowledge/development/bellows-phase4-reliability-fixes-2026-04-15.md` documenting what was changed in each file, the rationale (citing Phase 2 line numbers and Phase 3 hypothesis confirmations), any tests that needed updating, and any unexpected interactions discovered during implementation. Include the Output Receipt with Status=Complete, Files Created or Modified (Code) listing each of the 3 files with a one-line description of the change, Decisions Made (e.g., which refactor approach was used for Fix 2a), Flags for CEO (anything unexpected), Flags for Next Step (what QA should focus on). **Step A — Findings deposit (the dev log above is the deposit).** **Step B — Feedback append** to `knowledge/research/agent-prompt-feedback.md` per the standard prompt feedback protocol. **Step C — Final commit.** `cd /Users/marklehn/Desktop/GitHub/bellows && git add parser.py bellows.py planner.py knowledge/development/bellows-phase4-reliability-fixes-2026-04-15.md knowledge/research/agent-prompt-feedback.md knowledge/qa/evidence/executable-bellows-phase4-reliability-fixes-2026-04-15/ && git commit -m "fix: bellows reliability — parser stop_reason, escalation strand check, planner retry, consultation logging"`. **STOP. Do NOT proceed to Step 2. Do NOT move the plan to Done. Wait for CEO confirmation before continuing.**

---
---

## STEP 2 — QA (Bellows QA)

---

> **Before starting, read `/Users/marklehn/Desktop/GitHub/bellows/knowledge/development/bellows-phase4-reliability-fixes-2026-04-15.md` and check the Output Receipt status field. If status is not Complete, stop and report the issue to the CEO before proceeding.** Skip specialist file and glossary reads — this is mechanical verification. Working directory is `/Users/marklehn/Desktop/GitHub/bellows`. Evidence directory is `knowledge/qa/evidence/executable-bellows-phase4-reliability-fixes-2026-04-15/`. **FIRST — Deliverable Verification (Rule 17).** Read the DEV step's Output Receipt "Files Created or Modified (Code)" list. For each listed file, verify the change exists. Specifically: (a) `parser.py` — grep for `stop_reason` to confirm the new logic is in place; grep for the old `for status in ("Complete", "Partial", "Blocked")` to confirm the dead loop was removed. Deposit `grep_parser.txt`. (b) `bellows.py` — grep for `Planner decision for` to confirm Fix 2c logging is in place; check the structure around line 195 to confirm Fix 2a refactor (no early return that bypasses strand check). Deposit `grep_bellows.txt`. (c) `planner.py` — grep for retry logic (`time.sleep(5)` or similar), grep for the consultation log file path (`planner-consultation.jsonl`). Deposit `grep_planner.txt`. Build a verification table: `| Deliverable | Expected | Status (✅/❌) | Evidence |`. **Verification 1 — Parser fix unit test.** Create `tests/test_phase4_parser.py` with three tests: (1) `test_parser_returns_complete_for_end_turn`: pass a dict with `stop_reason="end_turn"`, `is_error=False` and verify the parser returns `receipt_status="Complete"`. (2) `test_parser_returns_blocked_for_error`: pass a dict with `is_error=True` and verify `receipt_status="Blocked"`. (3) `test_parser_returns_partial_for_max_tokens`: pass a dict with `stop_reason="max_tokens"` and verify `receipt_status="Partial"`. Run the new tests: `python3 -m pytest tests/test_phase4_parser.py -v 2>&1 | tee knowledge/qa/evidence/executable-bellows-phase4-reliability-fixes-2026-04-15/parser_unit_tests.txt`. All three must pass. **Verification 2 — Strand check coverage on escalation path.** Read the refactored `run_plan()` in `bellows.py`. Confirm there is no longer an early `return` between the planner consultation timeout and the strand check at lines 218-223 (or whatever line numbers the strand check now lives at). Document the control flow change in a comparison: before (early return → silent halt) vs after (break → strand check → STRANDED notification). Deposit `strand_path_audit.txt`. **Verification 3 — Planner retry behavior.** Create `tests/test_phase4_planner_retry.py` with two tests: (1) `test_planner_retries_on_auth_failure`: mock the subprocess to return a 401 error on first call and success on second call, verify `consult()` returns the success result. (2) `test_planner_falls_back_to_continue_on_persistent_failure`: mock the subprocess to fail twice (auth error both times), verify `consult()` returns `decision="continue"` with the fallback reason. Run: `python3 -m pytest tests/test_phase4_planner_retry.py -v 2>&1 | tee knowledge/qa/evidence/executable-bellows-phase4-reliability-fixes-2026-04-15/planner_retry_tests.txt`. Both must pass. **Verification 4 — Full test suite regression.** Run `python3 -m pytest tests/ -v 2>&1 | tee knowledge/qa/evidence/executable-bellows-phase4-reliability-fixes-2026-04-15/pytest_full.txt`. All tests must pass (existing + the 5 new ones). If any pre-existing test fails, capture the failure details and flag for CEO — do NOT mark as ✅. **Verification 5 — Smoke test.** Reuse the Phase 3 reproduction pattern. Build a minimal 4-substep test plan at `/tmp/bellows-phase4-smoke-2026-04-15.md` (write marker + append + git commit + move-to-Done). Run via direct claude -p with the standard Bellows bootstrap. Verify (a) the marker file is written, (b) the plan moves to Done, (c) the run can be inspected for the new logging output (planner consultation log, if multi-step) and the new status (Complete instead of Unknown — but this requires Bellows DB recording, which the smoke test can't fully exercise without restarting Bellows). For this verification, the smoke test only needs to confirm the agent completes all substeps. Cleanup temp files at end. Deposit `smoke_test.txt`. **Write the QA report** to `knowledge/qa/bellows-phase4-reliability-fixes-2026-04-15.md` with the verification table at the top, sections for each verification, and the standard Output Receipt. **Run the mandatory Rule 20 self-check:**

```python
# Rule 20 — Mandatory QA Self-Check
import os, sys
plan_slug = "executable-bellows-phase4-reliability-fixes-2026-04-15"
qa_report_path = "knowledge/qa/bellows-phase4-reliability-fixes-2026-04-15.md"
evidence_dir = f"knowledge/qa/evidence/{plan_slug}/"
required_evidence_files = [
    "grep_parser.txt",
    "grep_bellows.txt",
    "grep_planner.txt",
    "parser_unit_tests.txt",
    "strand_path_audit.txt",
    "planner_retry_tests.txt",
    "pytest_full.txt",
    "smoke_test.txt",
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

> **Include the literal stdout of the self-check at the end of the QA report.** If self-check FAILS, stop — do NOT update PROJECT_STATUS.md, do NOT move plan to Done. Report failure to CEO. If self-check PASSES, continue. **Final operations in strict order — feedback → commit → move-to-Done.** **Step A — PROJECT_STATUS.md update.** Update `/Users/marklehn/Desktop/GitHub/bellows/PROJECT_STATUS.md`: read it first, identify the most recent entry as the verbatim anchor, append a new milestone entry summarizing the four fixes shipped (parser stop_reason inference, escalation path strand check, planner retry on auth failure, consultation logging) with the DEV commit SHA. **Step B — Feedback append** to `knowledge/research/agent-prompt-feedback.md` per the standard prompt feedback protocol. **Step C — Final commit.** `cd /Users/marklehn/Desktop/GitHub/bellows && git add knowledge/qa/ tests/test_phase4_parser.py tests/test_phase4_planner_retry.py PROJECT_STATUS.md knowledge/research/agent-prompt-feedback.md && git commit -m "qa: bellows phase 4 reliability fixes — verification + status update"`. **Step D — Move-to-Done as the absolute last operation:** `import shutil; shutil.move("/Users/marklehn/Desktop/GitHub/bellows/knowledge/decisions/in-progress-executable-bellows-phase4-reliability-fixes-2026-04-15.md", "/Users/marklehn/Desktop/GitHub/bellows/knowledge/decisions/Done/executable-bellows-phase4-reliability-fixes-2026-04-15.md")`. **Strict order: deliverable verification → unit tests → strand audit → retry tests → full suite → smoke test → QA report → self-check → PROJECT_STATUS update → feedback append → final commit → move-to-Done. The move-to-Done is the absolute LAST operation — it is the structural completion gate Bellows uses to mark the plan complete. If any earlier step fails (feedback append, final commit, etc.), the plan correctly strands BEFORE the move and the failure is visible. Putting move-to-Done last preserves both Bellows' strand-detection guarantee AND the recoverability of upstream failures.**
