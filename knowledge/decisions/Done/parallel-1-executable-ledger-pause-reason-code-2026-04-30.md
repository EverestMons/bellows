# Bellows — Ledger pause_reason_code Schema Enhancement
**Date:** 2026-04-30 | **Tier:** Small | **Test Scope:** targeted | **Execution:** Step 1 (Bellows Developer) → Step 2 (Bellows QA)
**Priority:** 4

## Context

BACKLOG #12 (2026-04-30): `verdict.py::log_to_ledger()` records resolution outcomes but does NOT propagate the `Pause Reason Code` field that exists in verdict request files. Surfaced by today's verdict mechanization distribution audit (`knowledge/research/verdict-mechanization-distribution-audit-2026-04-30.md` Phase 1, "Critical schema gap" callout). Pause reasons can be inferred from verdict type and reason text, but inference is unreliable for `continue` without gate failure language (could be `qa_checkpoint` or `header_pause`). Fix: add `pause_reason_code` field to the JSONL schema, write it from `verdict.py` at log time, persist for future analysis. Cheap fix (~5 LOC + threading through call sites) that pays dividends on every future audit. Low priority — analytical only, doesn't affect runtime correctness.

Test Scope: targeted — `verdict.py` change with matching test additions in `test_verdict.py`. No cross-module impact: `gates.py`, `bellows.py`, `runner.py`, `parser.py` unchanged. Call sites in `bellows.py` need new keyword argument added to `log_to_ledger()` calls — but the field defaults to `None` for backward compatibility (so existing call sites continue to compile if not updated, but this plan updates them anyway for completeness).

Parallel-1 with `parallel-1-executable-deposit-exists-directory-paths-2026-04-30.md` — disjoint files (verdict.py vs gates.py, test_verdict.py vs test_gates.py), safe to dispatch simultaneously.

## How to Run This Plan

Paste the bootstrap prompt into Claude Code. The agent reads the full plan file and executes Step 1 ONLY. After completing Step 1, the agent STOPS and waits for CEO confirmation ("ok") before proceeding to Step 2.

**Bootstrap prompt:**
```
Read the plan at bellows/knowledge/decisions/parallel-1-executable-ledger-pause-reason-code-2026-04-30.md. Execute Step 1 ONLY. After completing Step 1, STOP and wait for my confirmation. Do NOT proceed to Step 2 or move the plan to Done.
```

---
---

## STEP 1 — Bellows Developer

---

> **FIRST — before doing anything else, claim this plan:** `import shutil; shutil.move("bellows/knowledge/decisions/parallel-1-executable-ledger-pause-reason-code-2026-04-30.md", "bellows/knowledge/decisions/in-progress-parallel-1-executable-ledger-pause-reason-code-2026-04-30.md")`. Read your specialist file at `bellows/agents/BELLOWS_DEVELOPER.md` first. **Skip glossary read — this is a code-tracing + schema-additive task, no domain interpretation needed.** All commands run from `/Users/marklehn/Desktop/GitHub/`. **The fix:** extend `verdict.py::log_to_ledger()` to accept and persist a `pause_reason_code` field. (a) Add `pause_reason_code: Optional[str] = None` parameter to the `log_to_ledger()` signature (after the existing `reason` parameter, defaulting to `None` for backward compatibility). (b) Add `"pause_reason_code": pause_reason_code` to the entry dict written to `ledger.jsonl`. (c) Find all call sites of `log_to_ledger` in `bellows.py` (use `grep -n "log_to_ledger" bellows.py` — there should be multiple). For each call site, determine the appropriate `pause_reason_code` value to pass: if the call site is downstream of a pause-reason determination (e.g., the same code path that calls `post_verdict_request` with a pause_reason argument), pass the same value; if the call site is for an auto-close path with no pause, pass `"auto_close"`; if uncertain, pass `None` and add a TODO comment. **Add tests** to `bellows/tests/test_verdict.py` covering: (a) `log_to_ledger` called WITHOUT `pause_reason_code` (legacy behavior — entry dict has key with `None` value or missing); (b) `log_to_ledger` called WITH `pause_reason_code="qa_checkpoint"` — assert the resulting JSONL line, when parsed, has `pause_reason_code == "qa_checkpoint"`; (c) `log_to_ledger` called with each documented pause reason code (`auto_close_disabled`, `qa_checkpoint`, `gate_failure`, `header_pause`, `agent_verdict_request`, `auto_close`) — assert each persists correctly. Three new tests minimum, more if natural. **Do not** rename existing fields, change field order in a way that breaks JSON parsers, or alter the `verdict` field semantics. Purely additive: a new optional field. **Run tests:** `cd /Users/marklehn/Desktop/GitHub/bellows && python3 -m pytest tests/test_verdict.py --tb=short`. Report the count. **Deposit dev log** at `bellows/knowledge/development/ledger-pause-reason-code-dev-log-2026-04-30.md` with: (1) verbatim before/after of `log_to_ledger()` signature and entry dict, (2) enumeration of every call site updated in `bellows.py` with old-and-new arguments, (3) verbatim test additions, (4) test run output (count, pass/fail), (5) any deviations from the plan. **Commit:** `cd /Users/marklehn/Desktop/GitHub/bellows && git add verdict.py bellows.py tests/test_verdict.py knowledge/development/ledger-pause-reason-code-dev-log-2026-04-30.md && git --no-pager commit -m "feat(verdict): persist pause_reason_code in ledger entries (BACKLOG #12)"`. **Standard prompt feedback protocol** → `bellows/knowledge/research/agent-prompt-feedback.md`.
>
> **Deposits:**
> - `bellows/knowledge/development/ledger-pause-reason-code-dev-log-2026-04-30.md`
>
> **STOP. Do NOT proceed to Step 2. Do NOT move the plan to Done. Wait for CEO confirmation before continuing.**

---
---

## STEP 2 — Bellows QA

---

> **Before starting, read `bellows/knowledge/development/ledger-pause-reason-code-dev-log-2026-04-30.md` and check the Output Receipt status field. If status is not Complete, stop and report the issue to the CEO before proceeding.** Read your specialist file at `bellows/agents/BELLOWS_QA.md` first. **Skip glossary read — this is mechanical QA for a schema additive change.** All commands run from `/Users/marklehn/Desktop/GitHub/bellows/`.
>
> **FIRST — Deliverable Verification.** Read the Step 1 dev log "Files Created or Modified (Code)" list. For every listed file, verify the change exists on disk via grep. Produce a verification table: | Deliverable | Expected | Status (✅/❌) | Evidence |. If ANY item is ❌, attempt to fix; if unfixable, stop and report.
>
> **Verification checks (each deposits literal output to `bellows/knowledge/qa/evidence/parallel-1-executable-ledger-pause-reason-code-2026-04-30/`):**
>
> (1) Grep for `pause_reason_code` in verdict.py — expect at least 2 matches (parameter declaration + entry dict assignment): `grep -n "pause_reason_code" verdict.py > knowledge/qa/evidence/parallel-1-executable-ledger-pause-reason-code-2026-04-30/grep_verdict_field.txt 2>&1`.
>
> (2) Grep for `pause_reason_code` in bellows.py — expect at least 1 match (call site update): `grep -n "pause_reason_code" bellows.py > knowledge/qa/evidence/parallel-1-executable-ledger-pause-reason-code-2026-04-30/grep_bellows_callsites.txt 2>&1`.
>
> (3) Grep for `log_to_ledger(` in bellows.py to enumerate call sites: `grep -n "log_to_ledger(" bellows.py > knowledge/qa/evidence/parallel-1-executable-ledger-pause-reason-code-2026-04-30/grep_logger_calls.txt 2>&1`. The dev log should enumerate the same call sites; cross-check.
>
> (4) Run targeted test suite: `python3 -m pytest tests/test_verdict.py --tb=short > knowledge/qa/evidence/parallel-1-executable-ledger-pause-reason-code-2026-04-30/pytest_targeted.txt 2>&1`. Expect all tests pass — the prior baseline included the 6 Rule 26 deposit-parser tests shipped 2026-04-28; this plan adds at least 3 new tests, so expect ≥9 verdict-related tests passing within the test_verdict.py file.
>
> (5) Behavioral smoke — call `log_to_ledger` with a `pause_reason_code` argument, then read the last line of `verdicts/ledger.jsonl` and assert the field round-trips. Write the script to `knowledge/qa/evidence/parallel-1-executable-ledger-pause-reason-code-2026-04-30/smoke.py` with content that imports `verdict` from the bellows package, calls `verdict.log_to_ledger(plan_path="/tmp/test-plan.md", step_number=1, gate_result={"failures": [], "files_changed": []}, verdict="continue", reason="smoke test", pause_reason_code="qa_checkpoint")`, then reads the last line of `verdicts/ledger.jsonl`, parses it as JSON, and asserts `entry["pause_reason_code"] == "qa_checkpoint"`. Print SUCCESS or FAILURE with the parsed entry. Run it: `python3 knowledge/qa/evidence/parallel-1-executable-ledger-pause-reason-code-2026-04-30/smoke.py > knowledge/qa/evidence/parallel-1-executable-ledger-pause-reason-code-2026-04-30/smoke_output.txt 2>&1`. Expect "SUCCESS" in output.
>
> (6) Git log — last commit on verdict.py: `cd /Users/marklehn/Desktop/GitHub/bellows && git --no-pager log -1 --name-only -- verdict.py > knowledge/qa/evidence/parallel-1-executable-ledger-pause-reason-code-2026-04-30/git_commit.txt 2>&1`. Expect commit message references BACKLOG #12.
>
> **Deposit QA report** to `bellows/knowledge/qa/ledger-pause-reason-code-qa-2026-04-30.md` with the verification table citing each evidence file path in the Evidence column. Include the literal stdout of the Rule 20 self-check block in the QA report body. Mark any check that cannot be completed as ❌ with a reason; do NOT mark ✅ with hedging language.
>
> **Mandatory Rule 20 self-check block (execute verbatim, include literal stdout in QA report):**
>
> ```python
> import os, sys
> plan_slug = "parallel-1-executable-ledger-pause-reason-code-2026-04-30"
> qa_report_path = "knowledge/qa/ledger-pause-reason-code-qa-2026-04-30.md"
> evidence_dir = f"knowledge/qa/evidence/{plan_slug}/"
> required_evidence_files = [
>     "grep_verdict_field.txt",
>     "grep_bellows_callsites.txt",
>     "grep_logger_calls.txt",
>     "pytest_targeted.txt",
>     "smoke.py",
>     "smoke_output.txt",
>     "git_commit.txt",
> ]
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
>
> If the self-check prints `FAILED`, STOP — do not update PROJECT_STATUS, do not move plan to Done, report to CEO. If `PASSED`, proceed with closeout in this exact order per Rule 23.
>
> **Final — PROJECT_STATUS update.** Use `Filesystem:edit_file` to add a completed milestone entry under PROJECT_STATUS.md's `## Completed` section. Anchor: insert the new entry as the FIRST bullet under the `## Completed` header (immediately after the header line). New entry verbatim: `- 2026-04-30: BACKLOG #12 closed — ledger pause_reason_code schema enhancement. Fix: log_to_ledger() in verdict.py now accepts and persists a pause_reason_code field; bellows.py call sites updated to pass the appropriate code per call site context. Closes the schema gap surfaced by the 2026-04-30 verdict mechanization distribution audit. +3 unit tests. Reference: parallel-1-executable-ledger-pause-reason-code-2026-04-30. REMINDER: restart Bellows daemon to load fix.`
>
> **Final — BACKLOG move-to-Closed.** Use `Filesystem:edit_file` on `bellows/knowledge/BACKLOG.md` to mark BACKLOG #12 as closed. Find the verbatim line beginning `- 2026-04-30: ledger.jsonl schema gap` and replace its leading `- ` with `- ~~` and append `~~ **[CLOSED 2026-04-30 — see Closed section below]**` immediately before the entry's terminating period. Then append a new Closed entry to the `## Closed` section verbatim: `- **Closed 2026-04-30:** BACKLOG #12 (ledger.jsonl schema gap — pause_reason_code not persisted). Fix: log_to_ledger() extended with optional pause_reason_code parameter; field added to JSONL entry dict; all bellows.py call sites updated to pass appropriate codes (auto_close_disabled, qa_checkpoint, gate_failure, header_pause, agent_verdict_request, auto_close). +3 unit tests. Resolves the inference unreliability for continue verdicts noted in verdict-mechanization-distribution-audit-2026-04-30.md. Reference: parallel-1-executable-ledger-pause-reason-code-2026-04-30. REMINDER: restart Bellows daemon to load.`
>
> **Step A — Feedback append.** Standard prompt feedback protocol → append entry to `bellows/knowledge/research/agent-prompt-feedback.md`.
>
> **Step B — Final commit.** `cd /Users/marklehn/Desktop/GitHub/bellows && git add knowledge/qa/ knowledge/research/agent-prompt-feedback.md PROJECT_STATUS.md knowledge/BACKLOG.md && git --no-pager commit -m "chore: QA + status + BACKLOG close for ledger pause_reason_code (BACKLOG #12)"`.
>
> **STOP. Plan complete after this step. Do NOT move plan to Done — Planner performs Done/ move after Rule 22 verification per Rule 25 terminal-step resolution.**
>
> **Deposits:**
> - `bellows/knowledge/qa/ledger-pause-reason-code-qa-2026-04-30.md`
> - `bellows/knowledge/qa/evidence/parallel-1-executable-ledger-pause-reason-code-2026-04-30/grep_verdict_field.txt`
> - `bellows/knowledge/qa/evidence/parallel-1-executable-ledger-pause-reason-code-2026-04-30/grep_bellows_callsites.txt`
> - `bellows/knowledge/qa/evidence/parallel-1-executable-ledger-pause-reason-code-2026-04-30/grep_logger_calls.txt`
> - `bellows/knowledge/qa/evidence/parallel-1-executable-ledger-pause-reason-code-2026-04-30/pytest_targeted.txt`
> - `bellows/knowledge/qa/evidence/parallel-1-executable-ledger-pause-reason-code-2026-04-30/smoke.py`
> - `bellows/knowledge/qa/evidence/parallel-1-executable-ledger-pause-reason-code-2026-04-30/smoke_output.txt`
> - `bellows/knowledge/qa/evidence/parallel-1-executable-ledger-pause-reason-code-2026-04-30/git_commit.txt`
