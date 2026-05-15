# Bellows — Stream-JSON Minimal Switch
**Date:** 2026-04-23 | **Tier:** Small | **Test Scope:** full-suite | **Execution:** Step 1 (SA) → Step 2 (DEV) → Step 3 (QA)

## How to Run This Plan

Paste the bootstrap prompt into Claude Code. The agent reads the full plan file and executes Step 1 ONLY. After completing Step 1, the agent STOPS and waits for CEO confirmation ("ok") before proceeding to Step 2. This continues step by step until the plan is complete.

**Bootstrap:**
```
Read the plan at bellows/knowledge/decisions/executable-stream-json-minimal-switch-2026-04-23.md. Execute Step 1 ONLY. After completing Step 1, STOP and wait for my confirmation. Do NOT proceed to Step 2 or move the plan to Done.
```

**REMINDER:** Bellows does not hot-reload after runner.py changes. CEO must restart Bellows after this plan ships before dispatching any plan that depends on the new output format. QA verification in Step 3 is code-level only — live smoke testing happens in a follow-up plan after restart.

---
---

## STEP 1 — BELLOWS SYSTEMS ANALYST

---

> **FIRST — before doing anything else, claim this plan:** `import shutil; shutil.move("bellows/knowledge/decisions/executable-stream-json-minimal-switch-2026-04-23.md", "bellows/knowledge/decisions/in-progress-executable-stream-json-minimal-switch-2026-04-23.md")`. You are the Bellows Systems Analyst. Read your specialist file at `bellows/agents/BELLOWS_SYSTEMS_ANALYST.md` first. Skip the domain glossary — this is infrastructure blueprint work. Also read: `bellows/knowledge/research/stream-json-feasibility-2026-04-23.md` (your own prior diagnostic — the blast radius table and event catalog are the authoritative spec input), `bellows/runner.py` (full file), `bellows/parser.py` (full file), `bellows/tests/test_runner.py` (full file — enumerate every test that asserts against `json.loads` output or constructs mock stdout as a single JSON string). **Your job.** Produce an implementation blueprint for the minimal stream-json switch. The blueprint is a spec for DEV — not a summary of the feasibility diagnostic. The feasibility diagnostic says WHAT needs to change; this blueprint says EXACTLY HOW it should change, with edge cases enumerated and acceptance criteria stated. **Required blueprint contents.** (1) The exact command-line change in runner.py: old `--output-format json`, new `--output-format stream-json --verbose`. Confirm `--verbose` is mandatory from the diagnostic. Specify whether `--include-partial-messages` is included (your feasibility diagnostic noted it in the test command — decide if Bellows needs it and justify). (2) The NDJSON parse logic replacing `json.loads(result_stdout)` in run_step's success path. Specify: line-by-line iteration over stdout_buf, per-line `json.loads()` with try/except to skip malformed lines (log but don't crash), accumulate events into a list OR extract only the terminal `type: "result"` event — pick one and justify which approach DEV should implement. Specify what happens when no `result` event appears in the stream (timeout case, crash case) — this MUST be a distinct error path from "result event has is_error=True." (3) Raw output log preservation. Currently runner.py:234-239 logs `raw_output` as the single JSON string. Under stream-json, `raw_output` should be the full NDJSON stream (all lines joined with newlines). This is the foundation for future corpus/telemetry work — it MUST be preserved verbatim, not post-processed. Specify the exact log field name and format. (4) Resume compatibility. Your feasibility diagnostic's follow-up question #3 asked whether `--output-format stream-json --verbose --resume <id>` works correctly. The blueprint must specify: DEV will empirically test this during implementation by running a two-step test dispatch (first call gets session_id, second call uses --resume). If resume fails under stream-json, that is a HARD BLOCKER — stop the plan and escalate, do not ship. Specify the exact test command DEV should use (substitute `claude-sonnet-4-20250514` or whatever model alias is current for Bellows dispatch). (5) Test update enumeration. List every test in `tests/test_runner.py` that will break under stream-json, by test function name, with a one-line description of why and how to fix. Also list any new tests that MUST be added: (a) NDJSON parsing with valid stream, (b) NDJSON parsing with malformed line (skip-and-continue behavior), (c) NDJSON parsing with missing result event (timeout/crash distinction), (d) resume-session compatibility test. Specify new test function names. (6) Acceptance criteria — a numbered list DEV can self-check against before declaring Step 2 Complete. Example: "1. `--output-format stream-json --verbose` is passed on every claude -p invocation in runner.py. 2. run_step's success path extracts the type: result event and returns a dict with identical schema to the current implementation. 3. Malformed NDJSON lines are logged and skipped, not fatal. 4. Missing result event produces a distinct error path logged as 'no_result_event' rather than decode_error. 5. Resume test passes (session_id from first call accepted by second call). 6. All existing test_runner.py tests updated and passing. 7. New tests (a)-(d) added and passing. 8. Full test suite passes (targeted run + full suite both clean)." **Out of scope — do NOT include in blueprint.** No per-event gating design. No parser.py changes (field schema is identical — parser.py stays untouched, confirm this explicitly in the blueprint). No gates.py changes. No corpus/telemetry layer. No documentation changes to PLANNER_TEMPLATE or specialist files. This blueprint is for the minimal switch only. **Deliverable.** Deposit blueprint to `bellows/knowledge/architecture/stream-json-minimal-switch-blueprint-2026-04-23.md`. Structure: (1) Summary — 3 sentences, (2) Exact command-line change, (3) NDJSON parse logic spec with edge case handling, (4) Raw output log spec, (5) Resume compatibility test spec, (6) Test enumeration (existing tests to update + new tests to add), (7) Acceptance criteria numbered list, (8) Explicit confirmation that parser.py and gates.py are untouched. **Canonical file write pattern.** Use `Filesystem:write_file` or `Desktop Commander:write_file` directly. If Python: `content = """..."""` then `with open("/Users/marklehn/Desktop/GitHub/bellows/knowledge/architecture/stream-json-minimal-switch-blueprint-2026-04-23.md", "w") as f: f.write(content)`. No heredoc. **No git commits in this step.** Blueprint deposit only. **Prompt feedback.** Standard prompt feedback protocol → `bellows/knowledge/research/agent-prompt-feedback.md`. **Deposits:**
>
> - `bellows/knowledge/architecture/stream-json-minimal-switch-blueprint-2026-04-23.md`
>
> **STOP. Do NOT proceed to Step 2. Do NOT move the plan to Done. Wait for CEO confirmation before continuing.**

---
---

## STEP 2 — BELLOWS DEVELOPER

---

> **Before starting, read `bellows/knowledge/architecture/stream-json-minimal-switch-blueprint-2026-04-23.md` and check the Output Receipt status field. If status is not Complete, stop and report the issue to the CEO before proceeding.** You are the Bellows Developer. Read your specialist file at `bellows/agents/BELLOWS_DEVELOPER.md` first. Skip the domain glossary — this is infrastructure implementation, no Bellows-specific domain vocabulary required. Also read: the SA blueprint from Step 1 (`bellows/knowledge/architecture/stream-json-minimal-switch-blueprint-2026-04-23.md`) — this is your authoritative spec, implement to the acceptance criteria. `bellows/runner.py` (the file you will modify), `bellows/tests/test_runner.py` (existing tests you will update + where new tests will go). **Your job.** Implement the stream-json minimal switch per the blueprint's acceptance criteria. Do NOT deviate from the blueprint — if a detail is underspecified, stop and ask the CEO rather than improvising. The blueprint is the spec. **Implementation order.** (1) Modify runner.py command-line construction to add stream-json and verbose flags. (2) Replace the single `json.loads` success path with the NDJSON parser specified in blueprint section 3, including malformed-line skip and missing-result-event distinct error path. (3) Update the raw output log to preserve the full NDJSON stream per blueprint section 4. (4) Update existing test_runner.py tests enumerated in blueprint section 6. (5) Add new tests (a)-(d) per blueprint section 6. (6) Run the resume compatibility test per blueprint section 5 — execute the two-step test dispatch empirically using `claude -p --output-format stream-json --verbose --model <current-model> "say hello"`, capture session_id from the result event, then invoke `claude -p --output-format stream-json --verbose --resume <session_id> "say goodbye"`, verify the second call succeeds and returns a result event. Cost of the resume test: ~$0.05. If the resume test FAILS, stop immediately — do NOT commit anything, do NOT proceed to housekeeping, report the failure to the CEO as a HARD BLOCKER. The plan cannot ship if resume is broken. **Run tests.** After all code changes, run `pytest bellows/tests/test_runner.py -v` (targeted) first. If clean, run the full suite `pytest bellows/tests/ -v`. Deposit raw output of the targeted run to `bellows/knowledge/qa/evidence/executable-stream-json-minimal-switch-2026-04-23/pytest_targeted.txt` and the full suite to `bellows/knowledge/qa/evidence/executable-stream-json-minimal-switch-2026-04-23/pytest_full.txt`. If any tests fail that are NOT in the enumerated update list, stop and report — do not fix unrelated failures in this plan. **Commit.** One commit for the implementation + test updates + new tests. Message format: `feat: switch runner to stream-json output format — minimal switch (same schema, per-event gating deferred)`. Do NOT commit to a branch; commit to main per Bellows convention. **Deposit the dev log.** `bellows/knowledge/development/stream-json-minimal-switch-2026-04-23.md` covering: (i) summary of code changes by file/line, (ii) resume compatibility test result (PASSED/FAILED with evidence), (iii) acceptance criteria self-check (each of the 8 criteria from blueprint with PASS/FAIL status), (iv) commit SHA, (v) test results (targeted + full suite pass/fail counts), (vi) any deviations from the blueprint (should be zero — if any, flag them). **Canonical file write pattern.** Use `Filesystem:write_file` or `Desktop Commander:write_file` for the dev log. For runner.py edits, use `Desktop Commander:edit_block` with anchored old_string values. No heredoc. **Prompt feedback.** Standard prompt feedback protocol → `bellows/knowledge/research/agent-prompt-feedback.md`. **Deposits:**
>
> - `bellows/knowledge/development/stream-json-minimal-switch-2026-04-23.md`
> - `bellows/knowledge/qa/evidence/executable-stream-json-minimal-switch-2026-04-23/pytest_targeted.txt`
> - `bellows/knowledge/qa/evidence/executable-stream-json-minimal-switch-2026-04-23/pytest_full.txt`
>
> **STOP. Do NOT proceed to Step 3. Do NOT move the plan to Done. Wait for CEO confirmation before continuing.**

---
---

## STEP 3 — BELLOWS QA

---

> **Before starting, read `bellows/knowledge/development/stream-json-minimal-switch-2026-04-23.md` and check the Output Receipt status field. If status is not Complete, stop and report the issue to the CEO before proceeding.** You are the Bellows QA Specialist. Read your specialist file at `bellows/agents/BELLOWS_QA.md` first. Skip the domain glossary — this is code-level verification. Also read: the Step 2 dev log (your primary evidence source), the SA blueprint (`bellows/knowledge/architecture/stream-json-minimal-switch-blueprint-2026-04-23.md`) to compare blueprint acceptance criteria vs. dev log self-check claims. **Rule 17 Deliverable Verification — execute FIRST before any other QA work.** Read the Step 2 Output Receipt's "Files Created or Modified (Code)" list. For EVERY listed deliverable, verify it exists on disk with the described change. Specifically: (a) `grep -n "stream-json" bellows/runner.py` — must show the flag change. (b) `grep -n "verbose" bellows/runner.py` — must show `--verbose` added to the command. (c) `grep -n "json.loads" bellows/runner.py` — the old single-JSON parse should be REMOVED or replaced; count occurrences before/after. (d) NDJSON parse logic: grep for the function/block described in the dev log and confirm its implementation matches the blueprint's specified approach (malformed-line skip, missing-result-event distinct error path). (e) Raw output log preservation: grep the log-writing block for the field storing NDJSON stream. (f) New test functions: `grep -n "def test_" bellows/tests/test_runner.py` and confirm the four new tests (a)-(d) from blueprint section 6 are present by name. (g) Commit SHA: `cd bellows && git --no-pager log -1 --format="%H %s"` — must match the SHA the dev log claims. Produce a verification table: `| Deliverable | Expected | Status (✅/❌) | Evidence |`. If ANY item is ❌, attempt to fix (re-commit, re-create file) before proceeding. If unfixable, STOP and report as HARD BLOCKER — do NOT move plan to Done. Deposit the grep outputs to `bellows/knowledge/qa/evidence/executable-stream-json-minimal-switch-2026-04-23/grep_deliverables.txt`. **Resume test verification.** The dev log claims PASSED on the resume compatibility test per blueprint section 5. Verify this by reading the dev log's resume test evidence section. If the dev log cannot produce concrete evidence (session_id captured, second invocation output), mark this row ❌ — the resume test is a HARD requirement per the plan header. Do NOT re-run the test yourself — this step is verification of the DEV agent's work, not re-execution. **Acceptance criteria cross-check.** Read the SA blueprint's acceptance criteria (8 items) and compare against the dev log's self-check. Each item must be PASS in the dev log. If any is FAIL or missing, mark ❌. Produce a second table: `| Criterion | DEV self-check | QA verification | Status |`. **Test regression check.** Read `bellows/knowledge/qa/evidence/executable-stream-json-minimal-switch-2026-04-23/pytest_targeted.txt` and `pytest_full.txt` (deposited by Step 2). Count passing/failing/skipped tests. Compare full suite pass count to the most recent baseline — `cd bellows && git --no-pager log --oneline --all | head -20` will help identify recent full-suite runs. If the full suite's pass count dropped, enumerate which tests are newly failing. Unrelated pre-existing failures carry forward and are NOT blockers — identify them by name in the QA report and mark as "pre-existing, not introduced by this plan." Newly introduced failures ARE blockers. **Deposit QA report.** `bellows/knowledge/qa/executable-stream-json-minimal-switch-qa-2026-04-23.md` containing: (1) Rule 17 deliverable verification table (above), (2) Resume test verification (above), (3) Acceptance criteria cross-check (above), (4) Test regression summary (pass/fail counts, newly-failing tests if any, pre-existing failures carried forward), (5) Overall verdict: PASS / BLOCK with reason. **Rule 19 note:** Any ✅ row containing hedging keywords ("pending", "inferred", "extrapolated", "estimated", "approximate", "skipped", "assumed", "close enough", "should pass", "would pass", "not run") auto-fails the Rule 20 self-check below. If you cannot complete a check, mark it ❌ with a reason — do NOT mark it ✅ and explain why you couldn't verify. **Rule 20 Mandatory QA Self-Check.** Run the following Python block verbatim (substitute the plan slug and required_evidence_files list):
>
> ```python
> # Rule 20 — Mandatory QA Self-Check
> import os, sys
> plan_slug = "executable-stream-json-minimal-switch-2026-04-23"
> qa_report_path = "bellows/knowledge/qa/executable-stream-json-minimal-switch-qa-2026-04-23.md"
> evidence_dir = f"bellows/knowledge/qa/evidence/{plan_slug}/"
> required_evidence_files = ["pytest_targeted.txt", "pytest_full.txt", "grep_deliverables.txt"]
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
>     for f in failures: print(f"  - {f}")
>     print("\nPlan CANNOT close. Fix issues and re-run QA.")
>     sys.exit(1)
> else:
>     print("PASSED — SELF-CHECK PASSED — all evidence files present, no hedging keywords found.")
>     print(f"Evidence folder: {evidence_dir}")
>     print(f"Files verified: {len(required_evidence_files)}")
> ```
>
> Include the literal stdout of the self-check in the QA report. If the self-check prints FAILED, STOP — do NOT update PROJECT_STATUS.md, do NOT move the plan to Done, report the failure to the CEO and wait. If the self-check prints PASSED, proceed with housekeeping. **Housekeeping ordering per Rule 23 — feedback → commit → move-to-Done (move is the LAST operation).** (A) Append entry to `bellows/knowledge/research/agent-prompt-feedback.md` with the QA agent's feedback on this prompt, plus review of the Patterns Identified section. (B) Update `bellows/PROJECT_STATUS.md` — add a Completed Milestones entry: `- 2026-04-23: Stream-JSON minimal switch shipped. Bellows now invokes claude -p with --output-format stream-json --verbose; runner.py extracts the terminal result event from the NDJSON stream; parser.py and gates.py untouched (identical field schema). Resume compatibility verified. Full NDJSON stream preserved in raw_output log for future corpus/telemetry work. CEO must restart Bellows to load. Commit: <SHA>.` Use `Desktop Commander:edit_block` with anchored old_string for the Completed Milestones section. (C) Final commit: `cd bellows && git add knowledge/qa/ knowledge/research/agent-prompt-feedback.md PROJECT_STATUS.md && git --no-pager commit -m "chore: QA + status update — stream-json minimal switch"`. (D) Move plan to Done: `import shutil; shutil.move("bellows/knowledge/decisions/in-progress-executable-stream-json-minimal-switch-2026-04-23.md", "bellows/knowledge/decisions/Done/executable-stream-json-minimal-switch-2026-04-23.md")`. Then final housekeeping commit: `cd bellows && git add knowledge/decisions/ && git --no-pager commit -m "chore: move stream-json minimal switch plan to Done"`. **Final CEO reminder in QA report:** "Bellows MUST be restarted to load the new runner.py. Until restart, the running daemon continues to invoke claude -p with --output-format json. Subsequent Bellows-dispatched plans will not benefit from the stream-json change until restart." **Prompt feedback.** Standard prompt feedback protocol → `bellows/knowledge/research/agent-prompt-feedback.md` (covered by housekeeping step A). **Deposits:**
>
> - `bellows/knowledge/qa/executable-stream-json-minimal-switch-qa-2026-04-23.md`
> - `bellows/knowledge/qa/evidence/executable-stream-json-minimal-switch-2026-04-23/grep_deliverables.txt`
