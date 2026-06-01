# Bellows — Block Continue Over Uncleared Worktree-Teardown Failure (ship)
**Date:** 2026-06-01 | **Tier:** Small | **Dispatch Mode:** bellows | **Test Scope:** full-suite | **Execution:** Step 1 (DEV) → Step 2 (QA) | **qa_steps:** 2 | **pause_for_verdict:** always | **auto_close:** false

## Execution Map

Step 1 (DEV) → Step 2 (QA). Sequential. DEV adds a guard at the TOP of the `continue`-verdict branch in `_consume_verdicts` (`bellows.py`): if the prior step's Gate Result JSON carries an uncleared `worktree_teardown` failure, the continue is REJECTED — the plan routes to `halted-` for manual R2 recovery instead of advancing. The guard sits before the final/non-final split, so it covers BOTH inter-step resume AND final-step continue-to-done (a teardown failure means Step N's commits were never landed in either case). Loud ERROR + CEO notification + blocked-continue ledger entry. Plus three regression tests. QA is code-level ONLY — no live multi-step daemon run.

## CEO Context

**Bug (full mechanism in `knowledge/research/worktree-teardown-resume-regression-2026-05-31.md`).** When `_teardown_worktree` step (b2) raises `worktree_teardown_dirty_tree` at a step pause, the failure is appended to the Gate Result AFTER the `gates step N: passed=True` log line, so it is invisible in the daemon log. A continue verdict issued over that hidden failure then advances the plan — and `_create_worktree`'s stranded-cleanup nukes the still-alive worktree (which holds Step N's un-landed commits), recreating from `HEAD --detach` minus those commits. Step N's work becomes dangling. This is the silent-skip → orphaned-commits cascade reproduced live this session.

**This plan ships Gap 1(b) only** — the cheapest, highest-safety cut from the findings doc: *block the continue when the prior step's gate result carries an uncleared `worktree_teardown` failure.* It stops the silent advance at the consumption gate. Explicitly OUT of scope (later, separate plans): Gap 1(c) re-attempt-teardown-on-resume, Gap 2 preserve-un-landed-commits-on-stranded-cleanup, Gap 3 teardown auto-stash.

**Injection site (verified live this session, locate by symbol — numbers drift).** In `_consume_verdicts` (`bellows.py`), the verdict-request's `**Gate Result JSON:**` line is parsed into `gate_result_from_request`, and inside the matched-plan loop `gate_result = gate_result_from_request or {...}` is established immediately before `if v == "continue":`. So the prior step's failures list IS available at continue time — no reload needed. The existing `precondition_failure_from_request` handling (item #5, 2026-05-24) is the precedent: it already inspects request-derived state and alters resume behavior. The new guard mirrors that shape but routes to `halted-`.

**"Uncleared" = present.** This minimal fix defines an uncleared failure as: a `{"gate": "worktree_teardown", ...}` entry present in `gate_result["failures"]`. There is no separate clearing mechanism yet and DEV must NOT invent one — recovery is manual R2 (out of scope).

**Bellows-modifies-Bellows / restart.** The running daemon executes THIS plan under PRE-edit code, so the new guard is NOT active during this plan's own DEV→QA close/resume (no self-trip — same property as the no-match-dedup ship). The guard activates only on the next plan dispatched AFTER a daemon restart. QA flags the restart for the CEO.

**Why QA is code-level only.** A live multi-step integration smoke test inside this plan would trip the very teardown/resume bug during its own close/resume. QA verifies the guard by reading the code and running unit/regression tests against `_consume_verdicts`, NOT by dispatching a real multi-step plan through the daemon.

---
---

## STEP 1 — DEV

---

> **FIRST — before any reads or work: post a short visible message to chat (1-2 sentences) confirming you are starting this plan and stating your immediate next action.** This is the liveness anchor. Do NOT rename the plan file — Bellows already claimed it before invoking you.
>
> You are the Bellows Developer. Read your specialist file at `agents/BELLOWS_DEVELOPER.md` and `governance/GUARDRAILS.md` first. Skip glossary read — domain terminology is fully covered in the specialist file. Note: the worktree root IS the bellows project root — strip the `bellows/` prefix from any path references in this prompt when running commands.
>
> **Reads (mandatory, in order):** (1) `agents/BELLOWS_DEVELOPER.md` — your specialist file; (2) `knowledge/research/worktree-teardown-resume-regression-2026-05-31.md` — the diagnostic blueprint this fix implements (read the Confirmed Mechanism and Gap 1 sections); (3) the target region of `bellows.py` and the test file, located via the Pre-edit verification queries below (do NOT trust line numbers — locate by symbol/string).
>
> **Pre-edit verification (Rule 39).** Before any edits, run each query and confirm the symbol exists. Line numbers drift; locate by string. Post a 1-line marker after each query result.
>
> 1. **Claim:** `_consume_verdicts` parses the prior step's gate result from the verdict-request and binds it before the continue branch. **Query:** `grep -n "gate_result_from_request\|if v == \"continue\"" bellows.py`. **Expected:** `gate_result_from_request` is parsed from a `**Gate Result JSON:**` line, and a `gate_result = gate_result_from_request or` assignment appears inside the matched-plan loop immediately before `if v == "continue":`.
> 2. **Claim:** worktree-teardown failures are recorded as dicts with a `"gate"` key equal to `"worktree_teardown"`. **Query:** `grep -n "\"gate\": \"worktree_teardown\"" bellows.py`. **Expected:** ≥1 hit appending `{"gate": "worktree_teardown", "evidence": str(e)}` to `gate_result["failures"]`. This is the exact shape the new guard matches on.
> 3. **Claim:** the continue branch has two exits — final-step `continue-to-done` (moves plan to `Done/`) and non-final resume (moves to `in-progress-`, calls `handle_new_plan(..., resume_step=...)`). **Query:** read the full `if v == "continue":` block. **Expected:** confirm both exits and note the housekeeping each performs (`verdict.log_to_ledger`, the `shutil.move` of the plan file, `_cleanup_verdicts_for_slug`, `self._seen.discard`, the verdict-file move out of `resolved/`, and the CEO notification mechanism). The block path you add will mirror this housekeeping but route to `halted-`.
>
> If any symbol is absent or materially differs from expected, **STOP** — do not edit. Deposit a verification-mismatch report to `knowledge/flags/verification-mismatch-block-continue-over-worktree-teardown-failure-2026-06-01-step-1.md` (claim, expected, actual, timestamp) and report to CEO.
>
> **Task — one guard in `bellows.py`, at the TOP of the `if v == "continue":` block, before the final/non-final split.**
>
> Add a guard that fires when the prior step's gate result carries an uncleared worktree-teardown failure. Detection predicate (use exactly this shape, matching query 2): `any(f.get("gate") == "worktree_teardown" for f in gate_result.get("failures", []))`. "Uncleared" = simply present in `failures`; do NOT invent a separate clearing mechanism.
>
> When the predicate is TRUE, REJECT the continue — do NOT advance to the next step and do NOT move to `Done/`. Instead, perform the block path, mirroring the housekeeping the existing `continue-to-done` exit performs but routing to `halted-`:
> - Emit a loud `_log("ERROR", ...)` stating the continue was rejected because the prior step's worktree teardown failed (commits not landed) and manual R2 recovery is required. Include the plan slug and step number.
> - Ledger it: `verdict.log_to_ledger(full_plan_path, step_number, gate_result, "continue-blocked-worktree-teardown", "continue verdict rejected — prior-step worktree_teardown failure uncleared; Step N commits not landed; manual R2 recovery required", pause_reason_code=pause_reason_code_from_request)`. (Confirm the `log_to_ledger` signature by reading the existing call sites; match it.)
> - Move the plan file from `verdict-pending-{original_name}` to `halted-{original_name}` in `decisions_path` (mirror the `shutil.move` used by the `continue-to-done` exit, but build the destination path with the `halted-` prefix, NOT `Done/`).
> - Run the same slug cleanup the other exits run: `_cleanup_verdicts_for_slug(cleanup_slug)` and `self._seen.discard(cleanup_slug)`.
> - Move the consumed verdict file out of `resolved/` to `processed-{fname}` using the SAME processed-move pattern the surrounding code uses (locate it by reading; do not transcribe a path from memory).
> - Notify the CEO using the SAME notifier mechanism the other exits in `_consume_verdicts` use (e.g. the plan-complete / malformed notifications — locate the call by reading; reuse `app_key`/`user_key` already in scope).
> - Then SKIP the rest of the continue branch for this plan (e.g. `continue` to the next file / break out of the matched-plan loop as the surrounding control flow requires — confirm the correct skip mechanism by reading the loop structure).
>
> Do NOT touch `_teardown_worktree`, `_create_worktree`, or the stranded-cleanup — those are Gap 2/3, out of scope. This change is confined to the `continue` branch of `_consume_verdicts`.
>
> **Regression tests — add to the test module that covers `_consume_verdicts` (locate it: `grep -rln "_consume_verdicts" tests/`; it is the same module the no-match-dedup tests landed in). Mirror that module's existing fixture/setup style** (resolved/ + verdicts/pending/ construction, verdict-pending plan placement, log capture, and any autouse reset in `conftest.py`). Add exactly three:
>
> 1. `test_continue_blocked_on_worktree_teardown_failure_interstep` — construct a multi-step (total_steps ≥ 2) verdict-pending plan, a step-1 `continue` verdict in `resolved/`, and a matching verdict-request whose `**Gate Result JSON:**` `failures` contains `{"gate": "worktree_teardown", "evidence": "..."}`. Call `_consume_verdicts()`. Assert: (a) the plan file is now `halted-<original_name>` (NOT `in-progress-*`, NOT `Done/`); (b) the next step was NOT dispatched (no `in-progress-*` for the slug; if the module mocks/observes `handle_new_plan`, assert it was not called to advance); (c) a ledger entry with action `continue-blocked-worktree-teardown` was written; (d) the verdict file left `resolved/` (moved to `processed-*`).
> 2. `test_continue_to_done_blocked_on_worktree_teardown_failure_final_step` — same setup but the verdict is on the FINAL step (`step_number >= total_steps`). Assert the plan is routed to `halted-` and is NOT in `Done/`. This proves the guard sits before the final/non-final split (scope A).
> 3. `test_continue_advances_normally_without_teardown_failure` — identical inter-step setup but the Gate Result JSON `failures` is empty (or contains a non-teardown gate). Assert the guard does NOT trip: the plan advances normally (moves to `in-progress-*` / next step dispatched per the existing path) and is NOT routed to `halted-`. This proves the guard is specific and does not false-trip on clean continues.
>
> **Test-count note:** three is the minimum that covers the two guarded exits (scope A) plus the negative/specificity case. Do not enumerate further permutations.
>
> **Reset module/global state between tests** following the module's existing pattern (autouse fixture or explicit teardown). Confirm no existing `_consume_verdicts` test breaks from leaked state.
>
> **Test execution.** Run the full suite pre-edit and capture the baseline: `python3 -m pytest tests/ -v 2>&1 | tail -160`. Record the pass count and the EXACT set of pre-existing failures (capture them empirically — do not assume which tests are red). After edits, run the full suite again. Expected post-edit: your three new tests PASS and ZERO NEW failures appear beyond the pre-edit carry-over baseline. Capture both runs verbatim.
>
> **Anchor verification before commit.** Run and confirm: `grep -n "continue-blocked-worktree-teardown" bellows.py` (≥1 — the ledger action); `grep -n "worktree_teardown\" for f in" bellows.py` (the guard predicate); confirm `_teardown_worktree` and `_create_worktree` are byte-unchanged (`git --no-pager diff -- bellows.py` touches only the `continue` branch of `_consume_verdicts`).
>
> **Deposit:** author a dev log to `knowledge/development/block-continue-over-worktree-teardown-failure-2026-06-01.md` documenting: the guard's placement (with a 5-8 line before/after snippet of the top of the `continue` branch), the detection predicate, the block-path housekeeping (ledger action, halted- move, verdict-file move, notify), the Pre-edit verification query results, the three new regression-test functions with their assertions, the pre-edit and post-edit full-suite pytest output (pass/fail counts + the carry-over failure baseline), the anchor-verification grep results, and the Output Receipt per your specialist file.
>
> **Commit:** stage `bellows.py`, the test additions, and the dev log with message `fix(bellows): block continue verdict over uncleared worktree_teardown failure — route to halted- for manual R2 instead of silent advance (Gap 1b)`. **DO NOT push to origin** — the Planner handles session-wrap commits.
>
> **Standard prompt feedback protocol** → append an entry to `knowledge/research/agent-prompt-feedback.md`. Second commit: `docs: prompt feedback — bellows DEV block-continue-over-teardown-failure`. **DO NOT push.**
>
> **Deposits:**
> - `bellows/knowledge/development/block-continue-over-worktree-teardown-failure-2026-06-01.md`
> - `bellows/knowledge/research/agent-prompt-feedback.md`
> - `bellows/bellows.py` (modified)
> - the `_consume_verdicts` test module (modified)
>
> **STOP. Do NOT proceed to Step 2. Do NOT move the plan to Done. Wait for CEO verdict before continuing.**

---
---

## STEP 2 — QA

---

> **FIRST — before any reads or work: post a short visible message to chat (1-2 sentences) confirming you are starting this step and stating your immediate next action.** This is the liveness anchor. Do NOT rename the plan file — Bellows already claimed it before invoking you.
>
> You are the Bellows QA Agent. Read your specialist file at `agents/BELLOWS_QA.md` and `governance/GUARDRAILS.md` first. Skip glossary read — domain terminology is fully covered in the specialist file. Note: the worktree root IS the bellows project root — strip the `bellows/` prefix from any path references in this prompt when running commands.
>
> **Scope note — code-level ONLY.** Do NOT dispatch or simulate a live multi-step plan through the daemon to test this. A real close/resume would trip the very teardown/resume bug this guard addresses. Verify by reading the code and running the unit/regression suite against `_consume_verdicts`. Nothing in this step should start the daemon or move a plan into a watched `decisions/` directory.
>
> **Before starting, read `knowledge/development/block-continue-over-worktree-teardown-failure-2026-06-01.md` (DEV's Step 1 deposit) and check its Output Receipt status; if not Complete, stop and report the blocker.**
>
> **Deliverable Verification (Rule 17).** Read DEV's Output Receipt "Files Created or Modified" list. For each, verify the file exists and the declared change is present. Produce a verification table `| # | Deliverable | Expected | Status (✅/❌) | Evidence |`. Specifically:
>
> 1. **Guard present at top of continue branch** — the `if v == "continue":` block opens with a worktree-teardown check using `any(f.get("gate") == "worktree_teardown" for f in gate_result.get("failures", []))`, BEFORE the `step_number >= total_steps_c` final/non-final split. Capture the branch top to `evidence/guard_placement.txt`.
> 2. **Block path routes to `halted-`** — when the predicate trips, the plan is `shutil.move`d to `halted-<original_name>` (NOT `Done/`, NOT `in-progress-`), with a `continue-blocked-worktree-teardown` ledger action, the verdict file moved to `processed-*`, slug cleanup (`_cleanup_verdicts_for_slug` + `_seen.discard`), a CEO notification, and a loud `_log("ERROR", ...)`. Capture the block path to `evidence/block_path.txt`.
> 3. **Skip is correct** — after the block path, control skips the rest of the continue branch (no advance, no Done move). Confirm by reading the control flow. Note the skip mechanism in the QA report.
> 4. **Out-of-scope code untouched** — `git --no-pager diff -- bellows.py` shows changes confined to the `continue` branch of `_consume_verdicts`; `_teardown_worktree`, `_create_worktree`, and stranded-cleanup are byte-unchanged. Capture the diff scope to `evidence/diff_scope.txt`.
> 5. **Three regression tests exist** — grep the `_consume_verdicts` test module for `test_continue_blocked_on_worktree_teardown_failure_interstep`, `test_continue_to_done_blocked_on_worktree_teardown_failure_final_step`, `test_continue_advances_normally_without_teardown_failure` → all three present. Capture to `evidence/new_tests_grep.txt`.
> 6. **Dev log complete** — the dev log exists with guard placement (before/after), predicate, block-path housekeeping, pre-edit verification, both pytest runs. Capture filesize + first/last 5 lines to `evidence/dev_log_check.txt`.
>
> Any ❌ blocks plan close — report to CEO.
>
> **Test execution.** Run the full suite: `python3 -m pytest tests/ -v 2>&1 | tail -200`. Capture to `evidence/pytest_full.txt`. Verify: (a) all three new tests appear in verbose output and PASS; (b) ZERO NEW failures beyond the carry-over present in DEV's pre-edit baseline; (c) total pass count = DEV's reported post-edit number.
>
> **Specificity check (no false-trip).** Confirm `test_continue_advances_normally_without_teardown_failure` proves a clean continue still advances — read its assertions and confirm it routes to `in-progress-`/advance, not `halted-`. Capture to `evidence/no_false_trip.txt`.
>
> **Rule 20 self-check** — run the canonical Rule 20 self-check from `RULE_20_SELF_CHECK_BLOCK.md` at governance root. Values: `plan_slug` = `executable-block-continue-over-worktree-teardown-failure-2026-06-01`; `qa_report_path` = `bellows/knowledge/qa/block-continue-over-worktree-teardown-failure-2026-06-01.md`; `evidence_dir` = `bellows/knowledge/qa/evidence/block-continue-over-worktree-teardown-failure-2026-06-01/`; `required_evidence_files` = `["guard_placement.txt", "block_path.txt", "diff_scope.txt", "new_tests_grep.txt", "dev_log_check.txt", "pytest_full.txt", "no_false_trip.txt"]`. Include literal stdout in the QA report. If FAILED, halt — report to CEO.
>
> **Final:** Update `bellows/PROJECT_STATUS.md` — prepend a 2026-06-01 entry under Completed for "Block continue verdict over uncleared `worktree_teardown` failure — route to `halted-` for manual R2 instead of silent advance (Gap 1b)" with a one-paragraph summary, using `Filesystem:edit_file` (find the existing topmost Completed entry as anchor and insert immediately before it).
>
> **DAEMON RESTART REMINDER — put in the QA deposit under "Flags for CEO":** "REMINDER: restart the Bellows daemon to activate the guard. The running daemon executed this plan with pre-edit code; the guard activates on the next plan dispatched after restart. Also owed: capture the organic Opus baseline (turns/wall) from this plan's step logs for the Opus↔Sonnet A/B."
>
> **Commit:** stage the QA report, evidence files, and PROJECT_STATUS update with message `qa(bellows): block-continue-over-teardown-failure verified — guard routes to halted-, no false-trip, zero new regressions (Gap 1b)`. **DO NOT push to origin** — the Planner handles session-wrap commits.
>
> **Standard prompt feedback protocol** → append an entry to `knowledge/research/agent-prompt-feedback.md`. Second commit: `docs: prompt feedback — bellows QA block-continue-over-teardown-failure`. **DO NOT push.**
>
> **Deposits:**
> - `bellows/knowledge/qa/block-continue-over-worktree-teardown-failure-2026-06-01.md`
> - `bellows/knowledge/qa/evidence/block-continue-over-worktree-teardown-failure-2026-06-01/`
> - `bellows/PROJECT_STATUS.md` (modified)
> - `bellows/knowledge/research/agent-prompt-feedback.md`
