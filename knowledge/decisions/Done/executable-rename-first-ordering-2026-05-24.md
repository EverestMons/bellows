# Bellows — Rename-first ordering at all four pause sites (RV-1 boundary closure, Shape A)
**Date:** 2026-05-24 | **Tier:** Small | **Dispatch Mode:** bellows | **Test Scope:** full | **Execution:** Step 1 (DEV) → Step 2 (QA) | **pause_for_verdict:** after_step_1 | **auto_close:** false

## Context

Per the 2026-05-24 daemon-restart-state-divergence diagnostic at `bellows/knowledge/architecture/daemon-restart-state-divergence-2026-05-24.md`, BACKLOG items #2 (daemon-restart recovery shape) and #3 (final-step gate_failure rename-skip) share root cause RV-1: the daemon performs verdict-request post (`verdict.post_verdict_request`) and plan rename (`in-progress-*` → `verdict-pending-*`) as separate non-atomic operations, with Pushover HTTP calls or other work in the gap. A daemon restart between verdict-post and rename leaves the verdict-request file in `verdicts/pending/` but the plan still named `in-progress-*`. Post-restart, `_consume_verdicts` matching predicate at bellows.py:1184 requires the `verdict-pending-` prefix, so the verdict cannot be paired — Bellows emits `[WARN] [<slug>] ⚠️ no verdict-pending plan found step N — leaving in resolved/ for retry` every 30s indefinitely.

**Shape A (rename-first):** reorder the rename to happen BEFORE the verdict-post at all four pause sites. New ordering: (a) plan renamed to `verdict-pending-*`, (b) verdict-request file written, (c) Pushover notification sent, (d) DB record written. If daemon dies anywhere in this sequence:
- After (a) but before (b): plan is `verdict-pending-*`, no verdict-request exists. Planner sees no request; daemon restart will not auto-recover (no automated startup scan covers this case yet), but the failure mode is recoverable by re-deposit or by the existing manual recovery procedure.
- After (b) but before (c): plan is `verdict-pending-*`, verdict-request exists. This is the normal "paused awaiting verdict" state. No symptom.
- After (c) but before (d): same as previous — no DB record is a tolerable degradation given DB is currently write-only per the 2026-05-24 diagnostic Section A.

**Why this is the right hardening shape:**
- Eliminates the RV-1 boundary entirely. Items #2 and #3 are both closed by this one change.
- ~10 LOC reordered, no new infrastructure. Matches the hardening-not-feature discipline (reduces ways the system can fail, does not add a new capability).
- The alternative (Shape B: startup recovery scan) heals symptoms but does not close the underlying gap. It would also require maintaining new recovery code.
- The alternative (Shape C: unified `_pause_for_verdict()` helper) is a refactor — feature-shaped, larger surface, deferred under current hardening discipline.

**Four pause sites to fix** (Planner-verified by grep against origin/main immediately before authoring):

| # | Site | Lines | Notes |
|---|---|---|---|
| 1 | Worktree-creation failure | `bellows.py:437-444` | Small gap — no Pushover call between post and rename. Still reordered for consistency. |
| 2 | Intermediate-step gate_failure pause | `bellows.py:519-528` | Pushover call in gap. Primary item #2 trigger site. |
| 3 | Final-step gate_failure pause | `bellows.py:610-617` | Pushover call in gap. Item #3 confirmed reproduction site. |
| 4 | Auto-close-failure pause (teardown error on auto-close path) | `bellows.py:639-644` | No Pushover call. Discovered by SA during 2026-05-24 diagnostic. |

**What gets reordered at each site:** the `verdict_pending_path = ... ; if os.path.exists(inprogress_path): shutil.move(...)` block moves from AFTER the `verdict.post_verdict_request(...)` call to BEFORE it. The `notifier.notify_verdict_request(...)` call (where present) stays in its current position relative to `verdict.post_verdict_request`. The `record_run(...)` call (where present) stays at the end of the block.

**What stays:**
- All matching predicates in `_consume_verdicts` (no widening needed — rename-first ensures the predicate's `verdict-pending-` requirement is always satisfied at the moment a verdict could be posted).
- `record_run` call sites and DB write semantics (DB is still write-only post-fix; the Phase 3b read-side is a separate Open BACKLOG item).
- Pushover notification timing (still fires after verdict-post, which is appropriate — Pushover notifies the CEO that a verdict is needed, and the verdict-request file IS what they will review).
- All 4 sites' pause-reason-code and gate-result construction logic.

**Test coverage:** the diagnostic Section F20 noted no existing test covers the RV-1 boundary. The reordering itself enables a new test shape: "assert that plan is `verdict-pending-*` BEFORE the verdict-request file is created in `pending/`." DEV will add one regression test per site (4 new tests) using monkeypatching to assert ordering. Existing pytest suite must continue passing.

**Acknowledged scope:** This executable does NOT fix BACKLOG item #5 (step-counter loop after precondition-failure verdict). That is an independent logic defect in `_consume_verdicts` step-advancement and will be addressed in a separate plan post-RV-1.

**Daemon-restart note:** This fix touches `bellows.py`, which Bellows does not hot-reload. The running daemon will continue executing pre-fix code through this plan's lifecycle. After plan close + daemon restart, the rename-first ordering becomes effective for all future paused plans.

## Execution Map

```
Step 1 (DEV) → Step 2 (QA)
```

Sequential. Step 1 reorders 4 pause sites in `bellows.py`, adds 4 regression tests, commits everything as one atomic commit, deposits dev log. Step 2 verifies the reordering and runs full pytest.

---
---

## STEP 1 — Bellows Developer

---

> You are the Bellows Developer. Read your specialist file at `agents/BELLOWS_DEVELOPER.md` first. **Skip glossary read — this is a precise code-reorder task.** **Authority:** the 2026-05-24 daemon-restart-state-divergence diagnostic at `knowledge/architecture/daemon-restart-state-divergence-2026-05-24.md` (Section E16 classifies items #2 and #3 as sharing root cause RV-1; Section F18 Shape A recommends rename-first ordering at all 4 pause sites). Read Section E and Section F (Shape A) before editing. **PATH CONVENTION: bare paths in all commands. Your cwd is the bellows project root within your worktree. Do NOT prefix paths with `bellows/`. Do NOT `cd bellows`. Files are at `bellows.py`, `tests/test_*.py`, `knowledge/...` — bare, relative to cwd.** **Pre-edit verification.** Confirm the expected starting state. Run each of the following and confirm the listed expected output. If any check fails, STOP — deposit a flag at `knowledge/flags/state-mismatch-rename-first-ordering-2026-05-24-step-1.md` documenting actual output, and halt. Check (i): `grep -c 'verdict.post_verdict_request' bellows.py` — expected: 4. Check (ii): `grep -n 'verdict.post_verdict_request' bellows.py` — expected: lines 437 (or 438), 519 (or 520), 610 (or 611), 639 (or 640) — line numbers approximate; the four matches should fall in those four neighborhoods. Check (iii): `python -c "import bellows"` from cwd — expected: exits cleanly. Check (iv): `pytest tests/test_bellows.py tests/test_consume_verdicts.py -q 2>&1 | tail -5` — expected: passes with the pre-existing carry-over failures noted in BACKLOG (4 `test_decisions.py` worktree artifacts + 1 `test_run_step_timeout`). If significantly more failures appear, STOP and flag.
>
> **Task A — reorder Site 1 (worktree-creation failure, bellows.py:437-444).** Use `Desktop Commander:edit_block` with the following anchor. Match exactly (preserve indentation):
>
> `old_string`:
> ```
>             gate_result = {"failures": [{"gate": "worktree_creation", "evidence": str(e)}], "files_changed": [], "passed": False, "is_qa_step": False}
>             verdict.post_verdict_request(plan_path, project_path, 1, log_path, gate_result,
>                                          pause_reason="gate_failure", total_steps=total_steps, step_text=plan_text)
>             verdict_pending_path = os.path.join(plan_dir, f"verdict-pending-{base_filename}")
>             if os.path.exists(inprogress_path):
>                 shutil.move(inprogress_path, verdict_pending_path)
>             _log("PAUSE", f"⏸️ worktree creation failed, awaiting CEO verdict", slug=slug_for(plan_name))
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
>             verdict.post_verdict_request(plan_path, project_path, 1, log_path, gate_result,
>                                          pause_reason="gate_failure", total_steps=total_steps, step_text=plan_text)
>             _log("PAUSE", f"⏸️ worktree creation failed, awaiting CEO verdict", slug=slug_for(plan_name))
> ```
>
> **Task B — reorder Site 2 (intermediate-step gate_failure pause, bellows.py:519-528).** Use `Desktop Commander:edit_block` with the following anchor. Match exactly (preserve indentation):
>
> `old_string`:
> ```
>                 verdict.post_verdict_request(plan_path, project_path, current_step, log_path, gate_result, pause_reason=_pause_reason, total_steps=total_steps, step_text=plan_text, intermediate_decisions=parsed.get("intermediate_decisions", []))
>                 notifier.notify_verdict_request(
>                     app_key, user_key, plan_name, current_step, gate_result["failures"]
>                 )
>                 # Rename plan to verdict-pending
>                 verdict_pending_path = os.path.join(plan_dir, f"verdict-pending-{base_filename}")
>                 if os.path.exists(inprogress_path):
>                     shutil.move(inprogress_path, verdict_pending_path)
>                 record_run(db_path, plan_path, project_path,
>                            parsed.get("session_id", ""), current_step, "VerdictPending", parsed["cost_usd"], plan_slug)
>                 _log("PAUSE", f"⏸️ step {current_step} — waiting for CEO verdict", slug=slug_for(plan_name))
> ```
>
> `new_string`:
> ```
>                 # Rename-first ordering (RV-1 closure, 2026-05-24): rename plan BEFORE posting verdict-request,
>                 # so a daemon restart between these ops cannot leave plan as in-progress-* with a verdict-request pending.
>                 verdict_pending_path = os.path.join(plan_dir, f"verdict-pending-{base_filename}")
>                 if os.path.exists(inprogress_path):
>                     shutil.move(inprogress_path, verdict_pending_path)
>                 verdict.post_verdict_request(plan_path, project_path, current_step, log_path, gate_result, pause_reason=_pause_reason, total_steps=total_steps, step_text=plan_text, intermediate_decisions=parsed.get("intermediate_decisions", []))
>                 notifier.notify_verdict_request(
>                     app_key, user_key, plan_name, current_step, gate_result["failures"]
>                 )
>                 record_run(db_path, plan_path, project_path,
>                            parsed.get("session_id", ""), current_step, "VerdictPending", parsed["cost_usd"], plan_slug)
>                 _log("PAUSE", f"⏸️ step {current_step} — waiting for CEO verdict", slug=slug_for(plan_name))
> ```
>
> **Task C — reorder Site 3 (final-step gate_failure pause, bellows.py:610-617).** Use `Desktop Commander:edit_block` with the following anchor. Match exactly (preserve indentation):
>
> `old_string`:
> ```
>             verdict.post_verdict_request(plan_path, project_path, current_step, log_path, gate_result, pause_reason=_pause_reason, total_steps=total_steps, step_text=plan_text, intermediate_decisions=parsed.get("intermediate_decisions", []))
>             notifier.notify_verdict_request(
>                 app_key, user_key, plan_name, current_step, gate_result["failures"]
>             )
>             verdict_pending_path = os.path.join(plan_dir, f"verdict-pending-{base_filename}")
>             if os.path.exists(inprogress_path):
>                 shutil.move(inprogress_path, verdict_pending_path)
>             record_run(db_path, plan_path, project_path,
>                        parsed.get("session_id", ""), current_step, "VerdictPending", parsed["cost_usd"], plan_slug)
>             _log("PAUSE", f"⏸️ step {current_step} — waiting for CEO verdict", slug=slug_for(plan_name))
>             return
> ```
>
> `new_string`:
> ```
>             # Rename-first ordering (RV-1 closure, 2026-05-24): rename plan BEFORE posting verdict-request,
>             # so a daemon restart between these ops cannot leave plan as in-progress-* with a verdict-request pending.
>             verdict_pending_path = os.path.join(plan_dir, f"verdict-pending-{base_filename}")
>             if os.path.exists(inprogress_path):
>                 shutil.move(inprogress_path, verdict_pending_path)
>             verdict.post_verdict_request(plan_path, project_path, current_step, log_path, gate_result, pause_reason=_pause_reason, total_steps=total_steps, step_text=plan_text, intermediate_decisions=parsed.get("intermediate_decisions", []))
>             notifier.notify_verdict_request(
>                 app_key, user_key, plan_name, current_step, gate_result["failures"]
>             )
>             record_run(db_path, plan_path, project_path,
>                        parsed.get("session_id", ""), current_step, "VerdictPending", parsed["cost_usd"], plan_slug)
>             _log("PAUSE", f"⏸️ step {current_step} — waiting for CEO verdict", slug=slug_for(plan_name))
>             return
> ```
>
> **Task D — reorder Site 4 (auto-close-failure pause, bellows.py:639-644).** Use `Desktop Commander:edit_block` with the following anchor. Match exactly (preserve indentation):
>
> `old_string`:
> ```
>                 verdict.post_verdict_request(plan_path, project_path, current_step, log_path, gate_result,
>                                              pause_reason="gate_failure", total_steps=total_steps, step_text=plan_text, intermediate_decisions=parsed.get("intermediate_decisions", []))
>                 verdict_pending_path = os.path.join(plan_dir, f"verdict-pending-{base_filename}")
>                 if os.path.exists(inprogress_path):
>                     shutil.move(inprogress_path, verdict_pending_path)
>                 _log("PAUSE", f"⏸️ worktree teardown failed, awaiting CEO verdict", slug=slug_for(plan_name))
> ```
>
> `new_string`:
> ```
>                 # Rename-first ordering (RV-1 closure, 2026-05-24): rename plan BEFORE posting verdict-request,
>                 # so a daemon restart between these ops cannot leave plan as in-progress-* with a verdict-request pending.
>                 verdict_pending_path = os.path.join(plan_dir, f"verdict-pending-{base_filename}")
>                 if os.path.exists(inprogress_path):
>                     shutil.move(inprogress_path, verdict_pending_path)
>                 verdict.post_verdict_request(plan_path, project_path, current_step, log_path, gate_result,
>                                              pause_reason="gate_failure", total_steps=total_steps, step_text=plan_text, intermediate_decisions=parsed.get("intermediate_decisions", []))
>                 _log("PAUSE", f"⏸️ worktree teardown failed, awaiting CEO verdict", slug=slug_for(plan_name))
> ```
>
> **Task E — post-edit smoke check.** Run `python -c "import bellows"` from cwd and confirm clean exit. If import fails, paste traceback into `knowledge/flags/import-failure-rename-first-ordering-2026-05-24-step-1.md` and halt. Run `grep -c 'verdict.post_verdict_request' bellows.py` and confirm it still returns 4 (no accidental over-reorder). Run `grep -n 'Rename-first ordering (RV-1 closure' bellows.py` and confirm exactly 4 matches (one comment per reordered site, in line-number order). Run `grep -B 2 'verdict.post_verdict_request' bellows.py | head -40` and visually verify that EACH of the 4 sites shows the rename block (`verdict_pending_path = ...` and `shutil.move(...)`) immediately BEFORE the `verdict.post_verdict_request(...)` call — not after.
>
> **Task F — add four regression tests to `tests/test_bellows.py`.** Each test exercises one of the four pause sites and asserts the rename-first ordering. Use monkeypatching to capture the order of `shutil.move` and `verdict.post_verdict_request` invocations. The tests should be self-contained — create a minimal plan file in a tempdir, set up the watcher fixtures already used by neighboring tests in `test_bellows.py` (search the file for `def test_run_plan_strict_pause_on_creation_failure` for a working pattern that exercises Site 1 — borrow its fixture setup wholesale). For each test: (a) seed a plan as `in-progress-*` (claim already happened), (b) trigger the specific pause site (different triggers per site — see hints below), (c) record the order of `shutil.move` calls (filtered to those moving to `verdict-pending-*`) and `verdict.post_verdict_request` calls, (d) assert `shutil.move` index < `verdict.post_verdict_request` index. Test names: `test_pause_site_1_worktree_creation_failure_renames_before_post`, `test_pause_site_2_intermediate_step_gate_failure_renames_before_post`, `test_pause_site_3_final_step_gate_failure_renames_before_post`, `test_pause_site_4_auto_close_teardown_failure_renames_before_post`. **Trigger hints per site** (these are not exhaustive — use the existing test patterns in `test_bellows.py` as scaffolding): Site 1 triggers via `_create_worktree` raising `WorktreeCreationError` (existing test mocks this). Site 2 triggers via gate failure on an intermediate step (mock `gates.check` to return `{"passed": False, ...}` on step < total_steps). Site 3 triggers via gate failure on the final step (same as site 2 but with step == total_steps). Site 4 triggers via teardown failure (`_teardown_worktree` raising `WorktreeTeardownError`) on a plan with `auto_close: true` header. If you cannot trigger Site 4 reliably (auto-close-on-failure may require additional fixture setup), document the difficulty in the dev log and skip the test for that site with a `pytest.skip(...)` and a TODO comment — partial coverage is better than blocked progress. If you cannot trigger ANY site reliably, STOP — deposit a flag at `knowledge/flags/test-fixture-blocking-rename-first-ordering-2026-05-24-step-1.md` and halt.
>
> **Task G — run full pytest to verify no regressions.** Run `pytest 2>&1 | tee /tmp/pytest_rename_first.txt` and confirm: (a) all 4 new tests pass (or at most 1 skip with documented TODO per Task F), (b) pre-existing carry-over failures stay carry-over (4 `test_decisions.py` worktree artifacts + 1 `test_run_step_timeout` if present in this environment — these are not regressions), (c) no NEW failures appear elsewhere. If new failures appear, STOP — paste pytest tail into a flag at `knowledge/flags/regression-rename-first-ordering-2026-05-24-step-1.md` and halt.
>
> **Task H — deposit dev log.** Write to `knowledge/development/rename-first-ordering-2026-05-24.md` documenting: (a) pre-edit verification stdout (checks i-iv); (b) before/after snippets for each of the 4 reordered sites (~5 lines context each); (c) the 4 new test function names with one-line description each; (d) Task E grep verification stdout; (e) Task G pytest summary (test counts: passed, failed, skipped); (f) one-paragraph summary citing the 2026-05-24 daemon-restart-state-divergence diagnostic findings as authority, identifying which BACKLOG items this closes (#2 and #3), and noting that BACKLOG item #5 is explicitly out of scope for this plan.
>
> **Task I — commit everything as ONE commit.** Stage `bellows.py`, `tests/test_bellows.py`, and the dev log. Verify with `git status --porcelain` that these are the staged paths. Commit with message `fix(bellows): rename-first ordering at all 4 pause sites — closes RV-1 boundary (items #2, #3)`. **DO NOT push.**
>
> **Standard prompt feedback protocol** → append entry to `knowledge/research/agent-prompt-feedback.md`. The entry should note: (1) which of the 4 sites had pre-edit anchor matches that required adjustment (line numbers shifting during edits, etc.), (2) whether Task F's test fixture borrowing approach worked or hit obstacles, (3) any observations about the existing test_bellows.py fixture patterns that future plans should know. Second commit: `docs: prompt feedback — bellows DEV rename-first ordering`. **DO NOT push.**
>
> **Deposits:**
> - `bellows/bellows.py` (modified)
> - `bellows/tests/test_bellows.py` (modified)
> - `bellows/knowledge/development/rename-first-ordering-2026-05-24.md`
> - `bellows/knowledge/research/agent-prompt-feedback.md`

---
---

## STEP 2 — Bellows QA

---

> You are the Bellows QA Agent. Read your specialist file at `agents/BELLOWS_QA.md` first. **Skip glossary read — this is a code-reorder QA task.** **PATH CONVENTION: bare paths in all commands. Your cwd is the bellows project root within your worktree. Do NOT prefix paths with `bellows/`. Do NOT `cd bellows`. Files are at `bellows.py`, `tests/test_*.py`, `knowledge/...` — bare, relative to cwd.** **Before starting, read `knowledge/development/rename-first-ordering-2026-05-24.md` (DEV Step 1 deposit) and check its Output Receipt status; if not Complete, stop and report the blocker.** **FIRST — Deliverable Verification (Rule 17).** Verification table: | Deliverable | Expected | Status (✅/❌) | Evidence |. Capture each grep to evidence under `knowledge/qa/evidence/executable-rename-first-ordering-2026-05-24/`. Verifications: (1) `grep -c 'Rename-first ordering (RV-1 closure' bellows.py` returns exactly 4 — evidence file `rename_first_comments_count.txt`; (2) `grep -c 'verdict.post_verdict_request' bellows.py` returns exactly 4 — evidence file `post_verdict_count.txt`; (3) for each of the 4 sites, the rename block (containing `verdict_pending_path` and `shutil.move`) appears BEFORE the `verdict.post_verdict_request` call in textual order. Verify by reading the 4 site regions (use approximate line numbers from the plan Context: site 1 ~lines 432-445, site 2 ~lines 515-530, site 3 ~lines 605-620, site 4 ~lines 635-650 — line numbers may shift slightly after edit, search by anchor strings). For each site, capture a `git --no-pager show <DEV-commit-sha> -- bellows.py | grep -A 15 '<site-anchor>'` to evidence files `site_1_ordering.txt`, `site_2_ordering.txt`, `site_3_ordering.txt`, `site_4_ordering.txt`. Use these site anchors: site 1 = `gate_result = {"failures": [{"gate": "worktree_creation"`; site 2 = `gate_result["failures"].append({"gate": "worktree_teardown"` (first occurrence — the intermediate-step one); site 3 = `gate_result["failures"].append({"gate": "worktree_teardown"` (second occurrence — the final-step one); site 4 = `gate_result["passed"] = False` (in the auto-close-failure block). For each site evidence file, manually verify the diff shows `verdict_pending_path = ...` BEFORE `verdict.post_verdict_request(...)` — mark ❌ and halt if any site has the wrong order. (4) `python -c "import bellows"` exits cleanly — evidence file `import_smoke.txt`; (5) the 4 new test function names exist in `tests/test_bellows.py` — `grep -n 'def test_pause_site_' tests/test_bellows.py` returns 4 matches (or 3 with one skip per Task F's exception clause; the dev log should document which) — evidence file `new_tests_present.txt`; (6) dev log exists with all six documentation items (a-f) — evidence file `dev_log_present.txt`; (7) `agent-prompt-feedback.md` has a new 2026-05-24 entry from DEV — evidence file `feedback_entry.txt`. **Full pytest suite (Test Scope: full).** Run `pytest 2>&1 | tee knowledge/qa/evidence/executable-rename-first-ordering-2026-05-24/pytest_full.txt`. Expected: all tests pass EXCEPT pre-existing carry-over failures (4 `test_decisions.py` worktree artifacts if present + 1 `test_run_step_timeout` if present). The 4 new `test_pause_site_*` tests should pass (or at most 1 skip with TODO per Task F). If any test fails that isn't on the carry-over list AND isn't a new pause-site test, mark ❌ and halt. Capture pytest summary line (test count, passes, fails, skips) to evidence. **Structural compliance check.** Identify the DEV commit SHA (the code-reorder commit, NOT the prompt-feedback commit). Run `git --no-pager show --stat <DEV-commit-sha> 2>&1 | tee knowledge/qa/evidence/executable-rename-first-ordering-2026-05-24/dev_commit.txt` and confirm exactly three paths in the commit: `bellows.py`, `tests/test_bellows.py`, and `knowledge/development/rename-first-ordering-2026-05-24.md`. Run `git --no-pager show <DEV-commit-sha> -- bellows.py 2>&1 | tee knowledge/qa/evidence/executable-rename-first-ordering-2026-05-24/diff_bellows.txt` and verify the diff is balanced — each removed `verdict.post_verdict_request(...)` line should have a corresponding added one further up the function, AND each removed `shutil.move(inprogress_path, ...)` block should have a corresponding added one further down (or at top, depending on viewpoint). The net change should be near-zero LOC (no additions/deletions of substantive logic, only reordering plus 4 new comment lines). If the diff shows additions or deletions of LOGIC (not just reorder + comments), mark ❌ and halt. **Rule 20 self-check** — run the canonical Rule 20 self-check from `RULE_20_SELF_CHECK_BLOCK.md` at governance root. Use these values: `plan_slug` = `executable-rename-first-ordering-2026-05-24`; `qa_report_path` = `knowledge/qa/executable-rename-first-ordering-2026-05-24.md`; `evidence_dir` = `knowledge/qa/evidence/executable-rename-first-ordering-2026-05-24/`; `required_evidence_files` = `["rename_first_comments_count.txt", "post_verdict_count.txt", "site_1_ordering.txt", "site_2_ordering.txt", "site_3_ordering.txt", "site_4_ordering.txt", "import_smoke.txt", "new_tests_present.txt", "dev_log_present.txt", "feedback_entry.txt", "pytest_full.txt", "dev_commit.txt", "diff_bellows.txt"]`. Include literal stdout in QA report. If FAILED, halt — report to CEO. **Final.** Update `PROJECT_STATUS.md` — prepend a 2026-05-24 entry under Completed for "Rename-first ordering at all 4 pause sites — closes RV-1 boundary (BACKLOG items #2, #3)" with a one-paragraph summary citing the 2026-05-24 daemon-restart-state-divergence diagnostic as authority. Use `Desktop Commander:edit_block` with the existing topmost Completed entry as the anchor (insert immediately before it). **Commit:** stage QA report, evidence files, and `PROJECT_STATUS.md` update with message `qa(bellows): rename-first ordering at all 4 pause sites`. **DO NOT push.** **Standard prompt feedback protocol** → append entry to `knowledge/research/agent-prompt-feedback.md`. Second commit: `docs: prompt feedback — bellows QA rename-first ordering`. **DO NOT push.**
>
> **Deposits:**
> - `bellows/knowledge/qa/executable-rename-first-ordering-2026-05-24.md`
> - `bellows/knowledge/qa/evidence/executable-rename-first-ordering-2026-05-24/` (13 evidence files per Rule 20 self-check list)
> - `bellows/PROJECT_STATUS.md` (modified)
> - `bellows/knowledge/research/agent-prompt-feedback.md`
