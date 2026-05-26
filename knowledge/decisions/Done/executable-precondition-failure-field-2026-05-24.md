# Bellows — Precondition-Failure verdict-request field (Shape E, BACKLOG item #5)
**Date:** 2026-05-24 | **Tier:** Small | **Dispatch Mode:** bellows | **Test Scope:** full | **Execution:** Step 1 (DEV) → Step 2 (QA) | **pause_for_verdict:** after_step_1 | **auto_close:** false

## Context

Per the 2026-05-24 daemon-restart-state-divergence diagnostic at `bellows/knowledge/architecture/daemon-restart-state-divergence-2026-05-24.md` Section E16, BACKLOG item #5 (step-counter loop after precondition-failure verdict) is an independent logic defect in `_consume_verdicts` — distinct from the RV-1 boundary closed by the rename-first-ordering plan. When the daemon pauses on a precondition gate (e.g., worktree creation failure at bellows.py:434) and the Planner verdict-continues, `_consume_verdicts` advances to `resume_step = step_number + 1` despite step N never having run. Subsequent step re-runs encounter the parallel-SHA pattern (work already on origin), produce empty/no-op commits, gate-fail, re-pause, and loop.

Reproduction (2026-05-21): `executable-fuel-continuation-inference-ui-2026-05-21` looped three iterations through step counter advancement before Planner verdict: stop.

**Shape E (Precondition Failure field):** add an explicit `**Precondition Failure:**` field to the verdict-request format. The producer side (`run_plan` worktree-creation failure path at bellows.py:438) writes `true`. All other pause sites omit the field (defaulting to `false`). The consumer side (`_consume_verdicts` at bellows.py:1230 area) reads the field and conditionally computes `resume_step`:
- `precondition_failure: true` → `resume_step = step_number` (retry same step)
- `precondition_failure: false` or absent → `resume_step = step_number + 1` (advance, existing behavior)

**Why Shape E over D or F:**
- **Shape D** (gate-name parsing) would couple the consumer to gate-name strings. Every future precondition gate would require touching this code. Brittle.
- **Shape F** (Step-field semantics change — `Step` = "next step to dispatch") ripples through filename patterns, ledger entries, existing tests, and other call sites. Larger blast radius for this problem.
- **Shape E** adds one explicit signal at the source. The `run_plan` precondition-failure path KNOWS it's a precondition failure — no inference required. Producer writes one boolean, consumer reads it. Minimum surface area for maximum correctness gain.

**Backward compatibility:** existing verdict-request files in `verdicts/pending/archived/` and `verdicts/resolved/` lack the `**Precondition Failure:**` field. The parser must default to `false` when the field is absent. This preserves replay/diagnostic behavior on historical files.

**What gets changed (Planner-verified by grep against origin/main immediately before authoring):**

| File | Site | Change |
|---|---|---|
| `verdict.py:178` | `post_verdict_request` signature | Add `precondition_failure: bool = False` parameter |
| `verdict.py` (content block ~line 226-236) | Verdict-request content template | Add `**Precondition Failure:** {true/false}` line after `**Pause Reason Code:**` |
| `bellows.py:438` | Site 1 — worktree-creation failure call | Pass `precondition_failure=True` |
| `bellows.py:1157-1175` | Verdict-request parsing block | Add parser for `**Precondition Failure:**`, init to `False` |
| `bellows.py:1230-1237` | Non-final-step continue dispatch | Conditionally compute `resume_step` based on precondition_failure flag |

**What stays unchanged:**
- All other call sites of `post_verdict_request` (sites 2, 3, 4 from the rename-first-ordering plan) — they get the default `False` value, which encodes their semantics correctly (step ran, gate failed or step completed).
- The verdict-request filename pattern, the verdict response format, the ledger entries, all matching predicates.
- The `Pause Reason Code` field and its parsing/logging (this fix is additive, not a replacement).
- All other behavior in `_consume_verdicts`.

**Acknowledged scope:** This executable closes BACKLOG item #5. It does NOT address Phase 3b read-side (separate Open BACKLOG item, deferred capability addition).

**Daemon-restart note:** This fix touches `bellows.py` and `verdict.py`, neither of which Bellows hot-reloads. The running daemon will continue executing pre-fix code through this plan's lifecycle. After plan close + daemon restart, the precondition-failure handling becomes effective for all future paused plans.

## Execution Map

```
Step 1 (DEV) → Step 2 (QA)
```

Sequential. Step 1 changes `verdict.py` (signature + format), `bellows.py` (call site + parser + dispatch), adds regression tests, commits everything as one atomic commit, deposits dev log. Step 2 verifies the changes and runs full pytest.

---
---

## STEP 1 — Bellows Developer

---

> You are the Bellows Developer. Read your specialist file at `agents/BELLOWS_DEVELOPER.md` first. **Skip glossary read — this is a precise code-change task.** **Authority:** the 2026-05-24 daemon-restart-state-divergence diagnostic at `knowledge/architecture/daemon-restart-state-divergence-2026-05-24.md` (Section D classifies the root cause; Section F18 Shape E recommends this design). Read Section D and Section F (Shape E) before editing. **PATH CONVENTION: bare paths in all commands. Your cwd is the bellows project root within your worktree. Do NOT prefix paths with `bellows/`. Do NOT `cd bellows`. Files are at `bellows.py`, `verdict.py`, `tests/test_*.py`, `knowledge/...` — bare, relative to cwd.** **Pre-edit verification.** Confirm the expected starting state. Run each of the following and confirm the listed expected output. If any check fails, STOP — deposit a flag at `knowledge/flags/state-mismatch-precondition-failure-field-2026-05-24-step-1.md` documenting actual output, and halt. Check (i): `grep -n 'def post_verdict_request' verdict.py` — expected: one match at line 178 (signature). Check (ii): `grep -c 'precondition_failure' verdict.py bellows.py` — expected: 0 (no references exist yet). Check (iii): `grep -n 'Pause Reason Code' verdict.py` — expected: two matches (~lines 230-231, in the content template). Check (iv): `grep -n 'pause_reason_code_from_request' bellows.py` — expected: ~3 matches in `_consume_verdicts` parsing and logging. Check (v): `grep -n 'resume_step=step_number + 1' bellows.py` — expected: one match at ~line 1237. Check (vi): `python3 -c "import bellows; import verdict"` from cwd — expected: exits cleanly. Check (vii): `python3 -m pytest tests/test_bellows.py tests/test_consume_verdicts.py tests/test_verdict.py -q 2>&1 | tail -5` — expected: passes with the pre-existing carry-over failures.
>
> **Task A — modify `verdict.py` signature.** Use `Desktop Commander:edit_block` with this anchor (match exactly):
>
> `old_string`:
> ```
> def post_verdict_request(plan_path, project_path, step_number, log_path, gate_result, pause_reason="auto_close_disabled", planner_py_decision=None, total_steps=None, step_text="", intermediate_decisions=None):
> ```
>
> `new_string`:
> ```
> def post_verdict_request(plan_path, project_path, step_number, log_path, gate_result, pause_reason="auto_close_disabled", planner_py_decision=None, total_steps=None, step_text="", intermediate_decisions=None, precondition_failure=False):
> ```
>
> **Task B — modify `verdict.py` content template.** Use `Desktop Commander:edit_block` with this anchor. Match exactly:
>
> `old_string`:
> ```
>         f"**Pause Reason:** {pause_reason_label}\n"
>         f"**Pause Reason Code:** {pause_reason}\n"
>         f"**Deposit:** {extract_primary_deposit(current_step_text) or 'none'}\n"
> ```
>
> `new_string`:
> ```
>         f"**Pause Reason:** {pause_reason_label}\n"
>         f"**Pause Reason Code:** {pause_reason}\n"
>         f"**Precondition Failure:** {'true' if precondition_failure else 'false'}\n"
>         f"**Deposit:** {extract_primary_deposit(current_step_text) or 'none'}\n"
> ```
>
> **Task C — pass `precondition_failure=True` at Site 1 in `bellows.py`.** Use `Desktop Commander:edit_block` with this anchor. Match exactly (preserve indentation):
>
> `old_string`:
> ```
>             gate_result = {"failures": [{"gate": "worktree_creation", "evidence": str(e)}], "files_changed": [], "passed": False, "is_qa_step": False}
>             # Rename-first ordering (RV-1 closure, 2026-05-24): rename plan BEFORE posting verdict-request,
>             # so a daemon restart between these ops cannot leave plan as in-progress-* with a verdict-request pending.
>             verdict_pending_path = os.path.join(plan_dir, f"verdict-pending-{base_filename}")
>             if os.path.exists(inprogress_path):
>                 shutil.move(inprogress_path, verdict_pending_path)
>             verdict.post_verdict_request(plan_path, project_path, 1, log_path, gate_result,
>                                          pause_reason="gate_failure", total_steps=total_steps, step_text=plan_text)
> ```
>
> `new_string`:
> ```
>             gate_result = {"failures": [{"gate": "worktree_creation", "evidence": str(e)}], "files_changed": [], "passed": False, "is_qa_step": False}
>             # Rename-first ordering (RV-1 closure, 2026-05-24): rename plan BEFORE posting verdict-request,
>             # so a daemon restart between these ops cannot leave plan as in-progress-* with a verdict-request pending.
>             verdict_pending_path = os.path.join(plan_dir, f"verdict-pending-{base_filename}")
>             if os.path.exists(inprogress_path):
>                 shutil.move(inprogress_path, verdict_pending_path)
>             # Precondition-failure signal (item #5, 2026-05-24): worktree creation failed → step never ran → consumer must retry, not advance.
>             verdict.post_verdict_request(plan_path, project_path, 1, log_path, gate_result,
>                                          pause_reason="gate_failure", total_steps=total_steps, step_text=plan_text,
>                                          precondition_failure=True)
> ```
>
> **Task D — add `**Precondition Failure:**` parser to `_consume_verdicts`.** The current verdict-request parsing block initializes several variables and parses fields line-by-line. Add a `precondition_failure_from_request` variable initialized to `False`, and a parser that reads the new field. Use `Desktop Commander:edit_block` with this anchor. Match exactly:
>
> `old_string`:
> ```
>             total_steps_from_request = None
>             pause_reason_code_from_request = None
>             if pending_req_file.exists():
> ```
>
> `new_string`:
> ```
>             total_steps_from_request = None
>             pause_reason_code_from_request = None
>             precondition_failure_from_request = False
>             if pending_req_file.exists():
> ```
>
> Then add the parser line. Use `Desktop Commander:edit_block` with this anchor. Match exactly:
>
> `old_string`:
> ```
>                     if req_line.startswith("**Pause Reason Code:**"):
>                         pause_reason_code_from_request = req_line.split(":**", 1)[1].strip() or None
> ```
>
> `new_string`:
> ```
>                     if req_line.startswith("**Pause Reason Code:**"):
>                         pause_reason_code_from_request = req_line.split(":**", 1)[1].strip() or None
>                     if req_line.startswith("**Precondition Failure:**"):
>                         precondition_failure_from_request = req_line.split(":**", 1)[1].strip().lower() == "true"
> ```
>
> **Task E — conditional `resume_step` dispatch.** In the non-final-step continue branch at bellows.py:1230-1237, the dispatch is currently `self.handle_new_plan(inprogress_path, resume_step=step_number + 1)`. Change this to compute `resume_step` based on `precondition_failure_from_request`. Use `Desktop Commander:edit_block` with this anchor. Match exactly (preserve indentation):
>
> `old_string`:
> ```
>                             else:
>                                 verdict.log_to_ledger(full_plan_path, step_number, gate_result, v, reason,
>                                                       pause_reason_code=pause_reason_code_from_request)
>                                 inprogress_name = f"in-progress-{original_name}"
>                                 inprogress_path = os.path.join(decisions_path, inprogress_name)
>                                 shutil.move(full_plan_path, inprogress_path)
>                                 _log("EVENT", f"verdict continue — resuming", slug=slug_for(original_name))
>                                 # Dispatch next step
>                                 self.handle_new_plan(inprogress_path, resume_step=step_number + 1)
> ```
>
> `new_string`:
> ```
>                             else:
>                                 verdict.log_to_ledger(full_plan_path, step_number, gate_result, v, reason,
>                                                       pause_reason_code=pause_reason_code_from_request)
>                                 inprogress_name = f"in-progress-{original_name}"
>                                 inprogress_path = os.path.join(decisions_path, inprogress_name)
>                                 shutil.move(full_plan_path, inprogress_path)
>                                 # Precondition-failure handling (item #5, 2026-05-24): if the prior step never ran due to
>                                 # a precondition gate failure (e.g., worktree creation), retry the same step rather than advance.
>                                 if precondition_failure_from_request:
>                                     next_step = step_number
>                                     _log("EVENT", f"verdict continue — retrying step {step_number} (precondition failure)", slug=slug_for(original_name))
>                                 else:
>                                     next_step = step_number + 1
>                                     _log("EVENT", f"verdict continue — resuming", slug=slug_for(original_name))
>                                 self.handle_new_plan(inprogress_path, resume_step=next_step)
> ```
>
> **Task F — post-edit verification.** Run `python3 -c "import bellows; import verdict"` from cwd and confirm clean exit. If import fails, paste traceback into `knowledge/flags/import-failure-precondition-failure-field-2026-05-24-step-1.md` and halt. Run `grep -c 'precondition_failure' verdict.py bellows.py` and confirm at least 7 matches total (signature param, content template, Site 1 call, init line, parser line, conditional dispatch keyword × 2, comment). Run `grep -n '**Precondition Failure:**' verdict.py` and confirm exactly one match in the content template. Run `grep -n 'resume_step=step_number + 1' bellows.py` and confirm ZERO matches (the old unconditional advance line has been replaced). Run `grep -n 'resume_step=next_step' bellows.py` and confirm exactly one match (the new conditional dispatch).
>
> **Task G — add regression tests.** Add tests to `tests/test_consume_verdicts.py` (the consumer-side fix has the highest test-coverage value). Add these test function names:
>
> 1. `test_consume_verdict_continue_advances_step_when_precondition_failure_absent` — seed a `verdict-pending-*` plan with a verdict-request that does NOT contain `**Precondition Failure:**`, deposit a `continue` verdict, run `_consume_verdicts`, verify `handle_new_plan` is called with `resume_step=step_number + 1` (existing behavior preserved for backward-compat).
> 2. `test_consume_verdict_continue_advances_step_when_precondition_failure_false` — same as above but verdict-request contains `**Precondition Failure:** false`. Confirm advance behavior.
> 3. `test_consume_verdict_continue_retries_step_when_precondition_failure_true` — verdict-request contains `**Precondition Failure:** true`. Confirm `handle_new_plan` is called with `resume_step=step_number` (retry, not advance).
> 4. Add a test to `tests/test_verdict.py`: `test_post_verdict_request_writes_precondition_failure_field` — call `post_verdict_request` with `precondition_failure=True`, confirm the resulting file contains `**Precondition Failure:** true`. Call again with `precondition_failure=False` (or default), confirm the file contains `**Precondition Failure:** false`.
>
> Use existing test fixtures and patterns in `test_consume_verdicts.py` and `test_verdict.py` as scaffolding. Search for `def test_consume_verdict_` to find working patterns. Each test should be self-contained. If you cannot reliably trigger any test, STOP — deposit a flag at `knowledge/flags/test-fixture-blocking-precondition-failure-field-2026-05-24-step-1.md` and halt.
>
> **Task H — run full pytest to verify no regressions.** Run `python3 -m pytest 2>&1 | tee /tmp/pytest_precondition_failure.txt` and confirm: (a) all 4 new tests pass, (b) pre-existing carry-over failures stay carry-over (4 `test_decisions.py` worktree artifacts + 1 `test_run_step_timeout`), (c) no NEW failures appear elsewhere. If new failures appear, STOP — paste pytest tail into a flag at `knowledge/flags/regression-precondition-failure-field-2026-05-24-step-1.md` and halt.
>
> **Task I — deposit dev log.** Write to `knowledge/development/precondition-failure-field-2026-05-24.md` documenting: (a) pre-edit verification stdout for all 7 checks; (b) before/after snippets for each of the 5 edit sites (~3-5 lines context each); (c) the 4 new test function names with one-line description each; (d) Task F grep verification stdout; (e) Task H pytest summary (test counts: passed, failed, skipped); (f) one-paragraph summary citing the 2026-05-24 daemon-restart-state-divergence diagnostic findings as authority, identifying which BACKLOG item this closes (#5), and noting that all other call sites of `post_verdict_request` retain backward-compatible default behavior (`precondition_failure=False`).
>
> **Task J — commit everything as ONE commit.** Stage `bellows.py`, `verdict.py`, `tests/test_consume_verdicts.py`, `tests/test_verdict.py`, and the dev log. Verify with `git status --porcelain` that these are the staged paths. Commit with message `fix(bellows): precondition-failure verdict-request field — retries step instead of advancing (item #5)`. **DO NOT push.**
>
> **Standard prompt feedback protocol** → append entry to `knowledge/research/agent-prompt-feedback.md`. The entry should note: (1) any anchor strings that required adjustment, (2) test-fixture borrowing observations (which existing tests served as scaffolding), (3) backward-compatibility validation results (does the parser correctly default to `False` when the field is absent?). Second commit: `docs: prompt feedback — bellows DEV precondition-failure field`. **DO NOT push.**
>
> **Deposits:**
> - `bellows/bellows.py` (modified)
> - `bellows/verdict.py` (modified)
> - `bellows/tests/test_consume_verdicts.py` (modified)
> - `bellows/tests/test_verdict.py` (modified)
> - `bellows/knowledge/development/precondition-failure-field-2026-05-24.md`
> - `bellows/knowledge/research/agent-prompt-feedback.md`

---
---

## STEP 2 — Bellows QA

---

> You are the Bellows QA Agent. Read your specialist file at `agents/BELLOWS_QA.md` first. **Skip glossary read — this is a code-change QA task.** **PATH CONVENTION: bare paths in all commands. Your cwd is the bellows project root within your worktree. Do NOT prefix paths with `bellows/`. Do NOT `cd bellows`. Files are at `bellows.py`, `verdict.py`, `tests/test_*.py`, `knowledge/...` — bare, relative to cwd.** **Before starting, read `knowledge/development/precondition-failure-field-2026-05-24.md` (DEV Step 1 deposit) and check its Output Receipt status; if not Complete, stop and report the blocker.** **FIRST — Deliverable Verification (Rule 17).** Verification table: | Deliverable | Expected | Status (✅/❌) | Evidence |. Capture each grep to evidence under `knowledge/qa/evidence/executable-precondition-failure-field-2026-05-24/`. Verifications: (1) `grep -n 'precondition_failure=False' verdict.py` returns one match (signature default) — evidence file `verdict_signature.txt`; (2) `grep -n '**Precondition Failure:**' verdict.py` returns exactly one match (content template) — evidence file `verdict_content_template.txt`; (3) `grep -n 'precondition_failure=True' bellows.py` returns exactly one match (Site 1 worktree-creation failure call) — evidence file `site_1_passes_true.txt`; (4) `grep -n 'precondition_failure_from_request' bellows.py` returns at least 3 matches (init, parser, conditional dispatch) — evidence file `consumer_uses_field.txt`; (5) `grep -n 'resume_step=step_number + 1' bellows.py` returns ZERO matches — evidence file `old_dispatch_absent.txt`; (6) `grep -n 'resume_step=next_step' bellows.py` returns exactly one match — evidence file `new_dispatch_present.txt`; (7) `python3 -c "import bellows; import verdict"` exits cleanly — evidence file `import_smoke.txt`; (8) the 4 new test function names exist: `grep -n 'def test_consume_verdict_continue_advances_step_when_precondition_failure_absent\\|def test_consume_verdict_continue_advances_step_when_precondition_failure_false\\|def test_consume_verdict_continue_retries_step_when_precondition_failure_true' tests/test_consume_verdicts.py` returns 3 matches, AND `grep -n 'def test_post_verdict_request_writes_precondition_failure_field' tests/test_verdict.py` returns 1 match — combined evidence file `new_tests_present.txt`; (9) dev log exists with all six documentation items (a-f) — evidence file `dev_log_present.txt`; (10) `agent-prompt-feedback.md` has a new 2026-05-24 entry from DEV — evidence file `feedback_entry.txt`. **Full pytest suite (Test Scope: full).** Run `python3 -m pytest 2>&1 | tee knowledge/qa/evidence/executable-precondition-failure-field-2026-05-24/pytest_full.txt`. Expected: all tests pass EXCEPT pre-existing carry-over failures (4 `test_decisions.py` + 1 `test_run_step_timeout`). The 4 new tests should pass. If any test fails that isn't on the carry-over list AND isn't a new test name, mark ❌ and halt. Capture pytest summary line to evidence. **Structural compliance check.** Identify the DEV commit SHA (the code-change commit, NOT the prompt-feedback commit). Run `git --no-pager show --stat <DEV-commit-sha> 2>&1 | tee knowledge/qa/evidence/executable-precondition-failure-field-2026-05-24/dev_commit.txt` and confirm exactly five paths in the commit: `bellows.py`, `verdict.py`, `tests/test_consume_verdicts.py`, `tests/test_verdict.py`, and `knowledge/development/precondition-failure-field-2026-05-24.md`. Run `git --no-pager show <DEV-commit-sha> -- bellows.py 2>&1 | tee knowledge/qa/evidence/executable-precondition-failure-field-2026-05-24/diff_bellows.txt` and confirm changes are additive and scoped (1 line for Site 1 keyword arg addition, init line, parser line, conditional dispatch block). Run `git --no-pager show <DEV-commit-sha> -- verdict.py 2>&1 | tee knowledge/qa/evidence/executable-precondition-failure-field-2026-05-24/diff_verdict.txt` and confirm changes are additive and scoped (1 line for signature keyword arg, 1 line for content template field). If diffs show unscoped or unrelated modifications, mark ❌ and halt. **Backward compatibility verification.** Verify the new parser handles missing field gracefully: read the diff_bellows.txt and confirm `precondition_failure_from_request = False` is the initial value (not None or undefined) — this is the default that persists if the verdict-request file lacks the `**Precondition Failure:**` line. Capture confirmation to evidence file `backward_compat_default_false.txt`. **Rule 20 self-check** — run the canonical Rule 20 self-check from `RULE_20_SELF_CHECK_BLOCK.md` at governance root. Use these values: `plan_slug` = `executable-precondition-failure-field-2026-05-24`; `qa_report_path` = `knowledge/qa/executable-precondition-failure-field-2026-05-24.md`; `evidence_dir` = `knowledge/qa/evidence/executable-precondition-failure-field-2026-05-24/`; `required_evidence_files` = `["verdict_signature.txt", "verdict_content_template.txt", "site_1_passes_true.txt", "consumer_uses_field.txt", "old_dispatch_absent.txt", "new_dispatch_present.txt", "import_smoke.txt", "new_tests_present.txt", "dev_log_present.txt", "feedback_entry.txt", "pytest_full.txt", "dev_commit.txt", "diff_bellows.txt", "diff_verdict.txt", "backward_compat_default_false.txt"]`. Include literal stdout in QA report. If FAILED, halt — report to CEO. **Final.** Update `PROJECT_STATUS.md` — prepend a 2026-05-24 entry under Completed for "Precondition-failure verdict-request field — closes BACKLOG item #5 (step-counter loop)" with a one-paragraph summary citing the 2026-05-24 daemon-restart-state-divergence diagnostic as authority. Use `Desktop Commander:edit_block` with the existing topmost Completed entry as the anchor (insert immediately before it). **Commit:** stage QA report, evidence files, and `PROJECT_STATUS.md` update with message `qa(bellows): precondition-failure verdict-request field`. **DO NOT push.** **Standard prompt feedback protocol** → append entry to `knowledge/research/agent-prompt-feedback.md`. Second commit: `docs: prompt feedback — bellows QA precondition-failure field`. **DO NOT push.**
>
> **Deposits:**
> - `bellows/knowledge/qa/executable-precondition-failure-field-2026-05-24.md`
> - `bellows/knowledge/qa/evidence/executable-precondition-failure-field-2026-05-24/` (15 evidence files per Rule 20 self-check list)
> - `bellows/PROJECT_STATUS.md` (modified)
> - `bellows/knowledge/research/agent-prompt-feedback.md`
