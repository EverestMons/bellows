# Bellows — runner.py Retry on Transient Failure (Lessons Forge Proposal 4)
**Date:** 2026-05-13 | **Tier:** Small | **Test Scope:** targeted | **Execution:** Step 1 (BELLOWS_DEVELOPER) → Step 2 (BELLOWS_QA) | **pause_for_verdict:** after_step_1

## How to Run This Plan

Paste the bootstrap prompt into Claude Code. The agent reads the full plan file and executes Step 1 ONLY. After completing Step 1, the agent STOPS and waits for CEO confirmation ("ok") before proceeding to Step 2.

**Bootstrap prompt:**
```
Read the plan at bellows/knowledge/decisions/executable-runner-retry-transient-failure-2026-05-13.md. Execute Step 1 ONLY. After completing Step 1, STOP and wait for my confirmation. Do NOT proceed to Step 2 or move the plan to Done.
```

## CEO Context

Implements Lessons Forge proposal 4 (entry 4, `status='accepted'`, lesson_proposals.id=4): add retry-on-transient-failure to agent dispatch in `bellows/runner.py`. Proposal text quoted verbatim from the entry: *"If claude -p returns a 401 or other transient error before any tokens are consumed (cost == 0, no permission denials), retry once with a 5s delay."*

### Diagnostic citation (Rule 27)

State diagnostic `bellows/knowledge/decisions/Done/diagnostic-bellows-runner-retry-state-2026-05-13.md` (shipped 2026-05-13, 1-of-1-step Done) verified:

- Three commits to `runner.py` in the last 14 days: `08fa9e8` (2026-05-12, intermediate decision detector), `b11ecc4` (2026-05-12, terminal output / log capture), `1256879` (2026-05-06, Failure 3 Mode A closure). None of the three commits mention retry, transient, or 401.
- `grep -n -i -E "retry|transient|backoff|401|cost.*==.*0|time\.sleep" runner.py` returns ONE hit at line 109 (`time.sleep(1)` inside the streaming-read poll loop — not a retry). Zero retry mechanism exists.
- `run_step` (the dispatch function) returns `{is_error: True, escalate: True, receipt_status: "Blocked"}` on every error path (subprocess spawn failure, inactivity timeout, wall-clock timeout, non-zero exit, no_result_event, parse_error). No retry on any path.

Branch resolution: Proposal 4 is still valid as written. Insertion point: the non-zero exit branch starting at `if proc.returncode != 0:` (line 162 in the 2026-05-13 snapshot — actual line may have drifted, agent must verify).

### Implementation shape locked

**Detection mechanism:** stderr text scan. Proposal 4's cost-condition (`cost == 0, no permission denials`) describes the *eligibility* — no tokens consumed yet, no permission decisions made. The actual transient *detection* happens by scanning `result_stderr` for known transient indicators. Eligibility holds inside the non-zero-exit branch because cost/permission decisions only land on the success path (parsed result event). Inside the non-zero-exit branch, no parsed `cost_usd` exists yet, so by construction `cost == 0` and `permission_denials == []` — the eligibility check is implicit.

**Transient indicators:** Two patterns scanned in `result_stderr` (case-insensitive):
1. HTTP 401 (authentication failure) — typically reported by `claude -p` as `"401"`, `"Unauthorized"`, or `"authentication"` in stderr
2. HTTP 429 (rate limit) — typically `"429"`, `"rate limit"`, `"too many requests"`

If stderr is empty or contains none of these patterns, NO retry — proceed to the existing Blocked-return path. This keeps retry scoped to network-class errors that are credibly transient. Non-zero exits from agent logic errors, killed processes, or unrelated subprocess failures fall through to the existing escalation behavior unchanged.

**Retry mechanics:**
- ONE retry only (proposal says "retry once with 5s delay")
- 5-second `time.sleep` before retry
- Same `cmd`, same `cwd`, same `timeout`, same `model`, same `allowed_tools` — full re-dispatch
- Retry attempt counted in a local `retry_attempt` flag; if retry also fails non-zero (regardless of reason), proceed to Blocked-return — no second retry
- Log lines emitted at INFO via `_log` for: retry decision (with detected transient pattern), retry sleep, retry attempt outcome (success or fail)

**No retry on other error paths.** Subprocess spawn failure, timeout, no_result_event, and parse_error remain unchanged. Retry only applies inside the non-zero exit branch.

### Caveats

1. **Anchor freshness.** Yesterday's commits added `_log` calls throughout `run_step`. Line numbers will have drifted from any pre-2026-05-12 reference. The DEV step MUST re-grep for `if proc.returncode != 0:` to find the live line number before editing.

2. **Daemon restart required.** Bellows has no hot-reload. The retry logic only takes effect after a daemon restart following the commit. CEO must restart Bellows after this plan moves to Done/ for the fix to be live.

3. **Test scope: targeted.** Two new tests targeting the new retry behavior. Existing 268+ tests remain in place. Per Rule 21, targeted scope is appropriate here — the change is localized to one branch of one function.

### Bellows BACKLOG note

The 2026-05-13 BACKLOG addition for `_extract_step_text` regex case-sensitivity (Lessons Forge proposal 8's secondary defect) is unrelated to this plan and remains deferred per its own disposition recommendation.

---
---

## STEP 1 — BELLOWS_DEVELOPER

---

> **FIRST — before doing anything else, claim this plan:** `import shutil; shutil.move("bellows/knowledge/decisions/executable-runner-retry-transient-failure-2026-05-13.md", "bellows/knowledge/decisions/in-progress-executable-runner-retry-transient-failure-2026-05-13.md")`. You are the Bellows Developer. Read your specialist file at `bellows/agents/BELLOWS_DEVELOPER.md`. Skip glossary read — this is a focused code change in one function. **Read context BEFORE editing:** (a) read `bellows/runner.py` in full to confirm current shape (the diagnostic citation in this plan's Context is reliable as of 2026-05-13 but verify line numbers haven't drifted from the 269-line snapshot). (b) read `bellows/src/test_runner.py` if it exists, OR `bellows/test_runner.py` — locate the existing test file for runner.py first via `find bellows -name "test_runner*"` and report the path. (c) note the `_log` helper signature by reading lines 1-22 of `runner.py` and confirming the `from bellows import _log` import. **Edit task:** modify `run_step` in `bellows/runner.py` to add retry-on-transient-failure inside the non-zero exit branch. Specific change spec follows. **Anchor verification first:** run `grep -n "if proc.returncode != 0:" bellows/runner.py` to locate the live anchor line. Report the line number. **Edit shape:** locate the block that begins with `if proc.returncode != 0:` and contains the stderr log + `_write_log` call + the Blocked-return. Wrap this block so that BEFORE constructing the Blocked-return, the retry guard fires. Pseudocode of the new structure (the agent translates to actual Python using the precise variable names found in current runner.py):
>
> ```python
> if proc.returncode != 0:
>     # NEW: Transient-failure retry guard. Eligibility is implicit inside this branch
>     # (no parsed result event yet means no cost or permission decisions have landed).
>     # Detection: stderr contains known transient indicators (401/Unauthorized/429/rate limit/too many requests).
>     transient_patterns = ["401", "Unauthorized", "authentication", "429", "rate limit", "too many requests"]
>     stderr_lower = (result_stderr or "").lower()
>     transient_hit = next((p for p in transient_patterns if p.lower() in stderr_lower), None)
>     if transient_hit is not None and not _retry_attempted:
>         _log("INFO", f"runner: transient failure detected ({transient_hit!r} in stderr); retrying once in 5s (step {step_num})", slug=plan_slug)
>         time.sleep(5)
>         _log("INFO", f"runner: retry dispatch starting (step {step_num})", slug=plan_slug)
>         # Single recursive-style retry by re-invoking run_step with the same args and a sentinel flag.
>         # Implementation note: use an inner helper or a local _retry_attempted guard to prevent infinite recursion.
>         # The cleanest shape is a top-of-function bool that flips True on retry, OR a private kwarg _retry_attempted=False
>         # propagated through one re-call. The agent picks the implementation that fits cleanest.
>         return run_step(prompt, project_path, model, session_id, allowed_tools, timeout, plan_slug, step_num, _retry_attempted=True)
>     # ... existing stderr log, _write_log, Blocked-return ...
> ```
>
> **Implementation note on the retry mechanism:** the cleanest shape is to add a private kwarg `_retry_attempted: bool = False` to `run_step`'s signature (after `step_num`), use it as the guard, and pass `_retry_attempted=True` on the recursive call. Document the kwarg as private (leading underscore) and as "internal retry guard — do NOT pass externally." Do NOT use a module-level flag (race conditions with concurrent steps) and do NOT use a `nonlocal` closure (run_step is a module-level function, not nested). **Edit constraints:** (a) preserve the existing stderr log line, `_write_log` call, and Blocked-return structure unchanged — they fire when no retry triggers OR when the retry attempt itself fails. (b) the new retry block must be ABOVE the existing stderr log inside the same `if proc.returncode != 0:` branch — early-return on retry, otherwise fall through to existing behavior. (c) on retry, the second invocation gets `_retry_attempted=True`, so even if it also hits non-zero exit with a transient pattern, the guard prevents a third attempt. (d) no other error paths get retry — timeout, spawn failure, no_result_event, and parse_error remain unchanged. **Use `Desktop Commander:edit_block`** for the edit with an anchor that includes the `if proc.returncode != 0:` line and 2-3 lines of context, replaced with the new structure. The `claim` import via shutil already imported at the top of your bash session is unrelated — runner.py edits use edit_block, not shutil.
>
> **Add tests:** locate the runner.py test file (path found in pre-edit context-read step), add TWO new regression tests at the end of the file:
>
> 1. `test_run_step_retries_on_transient_401`: patches subprocess to return non-zero exit with stderr containing `"401 Unauthorized"` on the first call and success (zero exit, valid result event JSON) on the second call. Asserts the return dict has `is_error=False` (retry succeeded). Asserts `time.sleep(5)` was called exactly once.
> 2. `test_run_step_does_not_retry_on_non_transient_error`: patches subprocess to return non-zero exit with stderr containing `"Permission denied"` (no transient indicator). Asserts the return dict has `is_error=True`, `escalate=True`, `receipt_status="Blocked"`. Asserts `time.sleep(5)` was NOT called.
>
> Tests use the existing patching pattern from neighboring tests in the same file (look at how other tests patch subprocess.Popen — replicate the pattern). If no patching pattern exists for runner.py tests, the agent uses `unittest.mock.patch` on `subprocess.Popen` and `time.sleep` to inject behavior.
>
> **Run targeted tests:** `cd bellows && python3 -m pytest test_runner.py -v` (or whichever path the test file lives at). Both new tests MUST pass. If any pre-existing test in the same file regresses, STOP and report — do not attempt to fix unrelated test failures.
>
> **Commit:** `cd /Users/marklehn/Desktop/GitHub/bellows && git --no-pager add runner.py [test-file-path] && git --no-pager commit -m "feat(runner): retry once on transient claude -p failures (401/429) — lessons forge proposal 4"`. Capture the commit SHA.
>
> **Dev log:** append a dev log to `bellows/knowledge/development/runner-retry-transient-failure-2026-05-13.md` recording: anchor line number (the verified `if proc.returncode != 0:` location), edit summary (added retry guard with kwarg-based one-shot mechanism, transient patterns list), two new tests by name, pre-edit and post-edit test counts (`pytest --collect-only | tail -1`), commit SHA recorded in body (no self-reference per 2026-05-13 LESSONS entry on dev-log SHA loops). Note that daemon restart is required for the change to take effect — record this explicitly in the dev log. Output Receipt status Complete only if all of: (a) edit landed with correct anchor, (b) both new tests pass, (c) no pre-existing test in runner.py test file regressed, (d) commit landed cleanly.
>
> After your output receipt, read `bellows/knowledge/research/agent-prompt-feedback.md` and append a dated entry per the standard protocol. Commit the feedback entry with message: `docs: prompt feedback — DEV runner-retry-transient-failure`.
>
> **Deposits:**
> - `bellows/runner.py`
> - `bellows/[test-file-path]` (path determined during pre-edit context-read)
> - `bellows/knowledge/development/runner-retry-transient-failure-2026-05-13.md`
> - `bellows/knowledge/research/agent-prompt-feedback.md`
>
> **STOP. Do NOT proceed to Step 2. Do NOT move the plan to Done. Wait for CEO confirmation before continuing.**

---
---

## STEP 2 — BELLOWS_QA

---

> Before starting, read `bellows/knowledge/development/runner-retry-transient-failure-2026-05-13.md` and check the Output Receipt status. If status is not Complete, stop and report the blocker before proceeding. You are the Bellows QA Analyst. Skip glossary read.
>
> **FIRST — Deliverable Verification (Rule 17).** Read the prior DEV step's dev log Files Modified list. For `bellows/runner.py`:
>
> (a) `grep -n "transient_patterns" runner.py` — verify the new patterns list landed (expected: 1 match)
> (b) `grep -n "_retry_attempted" runner.py` — verify the retry-guard kwarg landed (expected: ≥2 matches: signature + check + recursive call)
> (c) `grep -n "retry dispatch starting" runner.py` — verify the retry log line landed (expected: 1 match)
> (d) `grep -n "time.sleep(5)" runner.py` — verify the 5-second retry sleep landed (expected: 1 match; NOTE this is distinct from the pre-existing `time.sleep(1)` poll-loop sleep)
>
> For the test file:
>
> (e) `grep -n "test_run_step_retries_on_transient_401\|test_run_step_does_not_retry_on_non_transient_error" [test-file-path]` — verify both new test functions exist (expected: 2 matches)
>
> For the dev log:
>
> (f) verify file exists at declared path; (g) verify it lists the commit SHA in body text (cite by SHA from dev log, per 2026-04-30 LESSONS entry on HEAD-anchor brittleness — do NOT assume `git log HEAD~1` style positional anchors)
>
> Produce a verification table: `| Deliverable | Expected | Status (✅/❌) | Evidence |`.
>
> **Test re-run (independent confirmation):** `cd bellows && python3 -m pytest test_runner.py -v 2>&1 | tee /Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/evidence/executable-runner-retry-transient-failure-2026-05-13/test-runner-rerun.txt`. Both new tests MUST pass on this fresh run. Capture full output.
>
> **Full-suite test run (Rule 21 — targeted scope means targeted tests must pass + full suite must not regress):** `cd bellows && python3 -m pytest 2>&1 | tee /Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/evidence/executable-runner-retry-transient-failure-2026-05-13/full-suite.txt | tail -20`. Capture the summary line. The pre-existing `test_run_step_timeout` failure (documented in PROJECT_STATUS history) is permitted; any OTHER failure halts QA and reports to CEO.
>
> **Daemon-restart reminder in QA report.** The retry mechanism does NOT take effect on the running daemon — Bellows has no hot-reload. The QA report MUST include a top-level callout: `**DAEMON RESTART REQUIRED.** The retry logic is committed but not loaded. CEO must restart Bellows after Done/ move for the fix to be live.` This is not a hedging keyword — it's an operational fact the next session must see.
>
> **Rule 20 self-check:** run the canonical Python block from `/Users/marklehn/Desktop/GitHub/RULE_20_SELF_CHECK_BLOCK.md` with these values: `plan_slug = "executable-runner-retry-transient-failure-2026-05-13"`, `qa_report_path = "/Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/runner-retry-transient-failure-qa-2026-05-13.md"`, `evidence_dir = "/Users/marklehn/Desktop/GitHub/bellows/knowledge/qa/evidence/executable-runner-retry-transient-failure-2026-05-13/"`, `required_evidence_files = ["test-runner-rerun.txt", "full-suite.txt"]`. Include literal stdout output of the block in the QA report; halt and report to CEO if FAILED.
>
> **PROJECT_STATUS update:** append a 2026-05-13 entry to `bellows/PROJECT_STATUS.md` covering this ship: runner.py retry-on-transient-failure (Lessons Forge proposal 4 implementation), Bellows code commit SHA recorded (cite from dev log), daemon restart required, test counts (pre- and post-DEV), no regressions on full suite outside the known pre-existing failure.
>
> **Deposit QA report at `bellows/knowledge/qa/runner-retry-transient-failure-qa-2026-05-13.md`** with verification table, test re-run summary, full-suite summary, daemon-restart callout at top, Rule 20 self-check banner, Output Receipt Complete.
>
> Commit the QA artifacts: `cd /Users/marklehn/Desktop/GitHub/bellows && git --no-pager add knowledge/qa/runner-retry-transient-failure-qa-2026-05-13.md knowledge/qa/evidence/executable-runner-retry-transient-failure-2026-05-13/ PROJECT_STATUS.md && git --no-pager commit -m "qa: runner-retry-transient-failure — verification PASS, daemon restart required"`.
>
> After your output receipt, read `bellows/knowledge/research/agent-prompt-feedback.md` and append a dated entry per the standard protocol. Commit the feedback entry with message: `docs: prompt feedback — QA runner-retry-transient-failure`.
>
> **Deposits:**
> - `bellows/knowledge/qa/runner-retry-transient-failure-qa-2026-05-13.md`
> - `bellows/knowledge/qa/evidence/executable-runner-retry-transient-failure-2026-05-13/`
> - `bellows/PROJECT_STATUS.md`
> - `bellows/knowledge/research/agent-prompt-feedback.md`
>
> **STOP. Do NOT move the plan to Done — that is the Planner's responsibility after Rule 22 verification.**
