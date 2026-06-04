# Bellows — Re-Attempt Teardown on Continue-Resume (Gap 1c, ship)
**Date:** 2026-06-04 | **Tier:** Small | **Dispatch Mode:** bellows | **Test Scope:** full-suite | **Execution:** Step 1 (DEV) → Step 2 (QA) | **qa_steps:** 2 | **pause_for_verdict:** always | **auto_close:** false

## Execution Map

Step 1 (DEV) → Step 2 (QA). Sequential. DEV adds a new module-level helper `_retry_recoverable_teardown(...)` and calls it at the TOP of the `if v == "continue":` branch in `_consume_verdicts` (`bellows.py`), BEFORE the existing Gap-1b `worktree_teardown` halt guard. The helper re-attempts a recoverable (dirty-tree-only) teardown; on success it clears the `worktree_teardown` failure from `gate_result["failures"]` so the normal continue/advance proceeds; otherwise it leaves the failure for the Gap-1b guard to halt. Plus regression tests in `tests/test_consume_verdicts.py`. QA is code-level ONLY — no live multi-step daemon run.

## How to Run This Plan

Paste the bootstrap prompt into Claude Code. The agent reads the full plan file and executes Step 1 ONLY, then STOPS and waits for CEO verdict before Step 2. Bootstrap: `Read the plan at bellows/knowledge/decisions/executable-reattempt-teardown-on-continue-resume-2026-06-04.md. Execute Step 1 ONLY. After completing Step 1, STOP and wait for my confirmation. Do NOT proceed to Step 2 or move the plan to Done.`

## CEO Context

**Bug family (full mechanism in `knowledge/research/worktree-teardown-resume-regression-2026-05-31.md`).** When `_teardown_worktree` aborts (most commonly the dirty-tree pre-check (b2): local `main` carries uncommitted non-lifecycle files that would conflict with the cherry-pick), Step N's commits never land on `main` and the worktree is left alive. Gap 1(b) (shipped `8b2f952`) then blocks the continue verdict and routes the plan to `halted-` for manual R2 recovery. That stops the silent cascade — but it leaves the operator to recover by hand on every dirty-`main` re-dispatch, which recurred 2026-06-03 (lessons-forge cycle).

**This plan ships Gap 1(c) ONLY** — re-attempt the teardown at verdict-consume time, before the Gap-1b halt decision. By the time the CEO issues the continue verdict, the operator has almost always already committed the stray dirty file (the documented LESSONS 2026-06-03 mitigation). A retry then passes the dirty-tree pre-check, cherry-picks Step N's commits to `main`, and removes the worktree — so the normal continue advances and the fresh resume worktree is created at a `HEAD` that now contains Step N's work. This closes the loop Gap 1(b) opened: 1(b) halts safely, 1(c) recovers automatically for the common (dirty-tree) case.

**Scope is deliberately narrow — retry the DIRTY-TREE variant ONLY.** A `worktree_teardown` failure whose evidence is a cherry-pick *content conflict* will NOT self-heal on a plain retry (the conflicting state persists) — retrying it is wasteful and risks a confusing partial state. The helper retries ONLY when every `worktree_teardown` failure is the `worktree_teardown_dirty_tree` variant. Content conflicts, a destroyed/missing worktree, or a retry that still fails all fall through to the existing Gap-1b halt → R2. OUT of scope: Gap 2(b)/(c) functional resume recovery; Gap 3 teardown auto-stash. The Gap-1b guard is NOT modified — it runs unchanged, against a `failures` list the helper may have cleared.

**Destroyed-worktree interaction with Gap 2(a) (shipped `9e129eb`).** If the worktree was already destroyed (e.g., a restart triggered `_create_worktree`'s stranded-cleanup), `wt_path` no longer exists. The helper detects this and SKIPS the retry → Gap-1b halts. This is safe: Gap 2(a) preserved the un-landed commits on a `bellows-preserved/*` branch, so R2 recovery from halt is non-destructive. The helper never fabricates a worktree.

**Injection site (verified live this session, locate by symbol — numbers drift).** In `_consume_verdicts` (`bellows.py`), inside the `for decisions_path in search_dirs:` loop, the `if v == "continue":` branch opens with the Gap-1b guard (`if any(f.get("gate") == "worktree_teardown" for f in gate_result.get("failures", [])):`). In scope at that point: `decisions_path`, `cleanup_slug` (= `verdict.slug_from_path(original_name)`), `gate_result`, `plan_slug`. The new helper call goes at the very TOP of the `if v == "continue":` block, IMMEDIATELY BEFORE the Gap-1b `if any(...)` guard. Reconstruct the worktree paths from in-scope values: `project_path = os.path.dirname(os.path.dirname(decisions_path))` (matches run_plan's `project_path = str(plan_p.parents[2])`); `wt_path = os.path.join(project_path, ".bellows-worktrees", cleanup_slug)` (matches `_create_worktree`, which builds `os.path.join(project_path, ".bellows-worktrees", slug)` with `slug = plan_slug = verdict.slug_from_path(base_filename)` — identical to `cleanup_slug`).

**Why a helper (not inline).** `_consume_verdicts` is a very large method; inlining retry logic there is hard to unit-test without driving the whole verdict loop. A small module-level helper isolates the decision and is directly testable with a constructed `gate_result` + a monkeypatched `_teardown_worktree` — which is what makes the code-level-only QA feasible. The helper mutates `gate_result["failures"]` in place on success and returns a bool (cleared / not).

**Bellows-modifies-Bellows / self-trip.** This plan edits `_consume_verdicts`. The running daemon executes THIS plan under PRE-edit code, so the new helper is NOT active during this plan's own DEV→QA close/resume; the new behavior activates only on the next plan dispatched AFTER a daemon restart. This plan must NOT trip the very bug it fixes: keep local `main` CLEAN at both pauses (standard discipline) so this plan's own teardowns succeed and no `worktree_teardown` failure is produced. QA flags the restart for the CEO.

**Why QA is code-level only.** Exercising the retry path live would require an actual dirty-tree-teardown-failure-then-continue state — i.e., tripping the bug during the plan's own close/resume. QA verifies the helper by reading the code and running unit/regression tests with a constructed `gate_result` and a monkeypatched `_teardown_worktree`, NOT by dispatching a real multi-step plan through the daemon.

---
---

## STEP 1 — DEV

---

> **FIRST — before any reads or work: post a short visible message to chat (1-2 sentences) confirming you are starting this plan and stating your immediate next action.** This is the liveness anchor. Do NOT rename the plan file — Bellows already claimed it before invoking you.
>
> You are the Bellows Developer. Read your specialist file at `agents/BELLOWS_DEVELOPER.md` and `governance/GUARDRAILS.md` first. Skip glossary read — domain terminology is fully covered in the specialist file. Note: the worktree root IS the bellows project root — strip the `bellows/` prefix from any path references in this prompt when running commands.
>
> **Reads (mandatory, in order):** (1) `agents/BELLOWS_DEVELOPER.md` — your specialist file; (2) `knowledge/research/worktree-teardown-resume-regression-2026-05-31.md` — the diagnostic blueprint (read the Confirmed Mechanism section and the "Gap 1" fix-shape options; you implement Gap 1(c) ONLY); (3) the target regions of `bellows.py` and `tests/test_consume_verdicts.py`, located via the Pre-edit verification queries below (do NOT trust line numbers — locate by symbol/string).
>
> **Pre-edit verification (Rule 39).** Before any edits, run each query and confirm the symbol exists. Line numbers drift; locate by string. Post a 1-line marker after each query result.
>
> 1. **Claim:** the `if v == "continue":` branch in `_consume_verdicts` opens with the Gap-1b guard — `if any(f.get("gate") == "worktree_teardown" for f in gate_result.get("failures", [])):` — which logs `continue verdict REJECTED`, moves the plan to `halted-`, and `break`s. **Query:** `grep -n 'if v == "continue":' bellows.py` then read the ~25 lines below it. **Expected:** the Gap-1b `if any(...)` guard is the FIRST statement inside the continue branch; your helper call goes IMMEDIATELY ABOVE it.
> 2. **Claim:** `_teardown_worktree(project_path, wt_path, slug)` raises `WorktreeTeardownError` on the dirty-tree pre-check, and the error message begins `worktree_teardown_dirty_tree:`; the worktree is left ALIVE on that raise. **Query:** `grep -n "def _teardown_worktree\|class WorktreeTeardownError\|worktree_teardown_dirty_tree" bellows.py` and read the `(b2) Pre-cherry-pick dirty-tree check` region. **Expected:** the dirty-tree branch `raise WorktreeTeardownError("worktree_teardown_dirty_tree: ...")`; no `worktree remove` runs before that raise.
> 3. **Claim:** at the continue-branch insertion point, `cleanup_slug` and `decisions_path` and `gate_result` are in scope, and `cleanup_slug` equals the worktree directory name `_create_worktree` used. **Query:** `grep -n "cleanup_slug = \|project_path = str(plan_p.parents\|plan_slug = verdict.slug_from_path\|os.path.join(project_path, \".bellows-worktrees\"" bellows.py`. **Expected:** `cleanup_slug = verdict.slug_from_path(original_name)`; run_plan computes `plan_slug = verdict.slug_from_path(base_filename)` and `_create_worktree` builds `os.path.join(project_path, ".bellows-worktrees", slug)` — confirm `cleanup_slug` is the same slug value (both are `slug_from_path` of the bare plan name).
> 4. **Claim:** run_plan derives `project_path = str(plan_p.parents[2])` from the plan FILE, so for a decisions DIRECTORY `decisions_path` the equivalent is `os.path.dirname(os.path.dirname(decisions_path))`. **Query:** `grep -n "project_path = str(plan_p.parents" bellows.py`. **Expected:** confirms `parents[2]` = three levels up from the plan file = `<project>` (file is `<project>/knowledge/decisions/<name>.md`); a decisions dir is two `dirname`s below the project root.
> 5. **Claim:** module-level scope has `os`, `subprocess`, `_log`, `_teardown_worktree`, and `WorktreeTeardownError` available for a new helper. **Query:** read the top-of-file imports + the `_teardown_worktree` / `WorktreeTeardownError` definitions. **Expected:** all present; the helper needs only `os.path`, `_teardown_worktree`, `WorktreeTeardownError`, and `_log`.
>
> If any symbol is absent or materially differs from expected, **STOP** — do not edit. Deposit a verification-mismatch report to `knowledge/flags/verification-mismatch-reattempt-teardown-on-continue-resume-2026-06-04-step-1.md` (claim, expected, actual, timestamp) and report to CEO.
>
> **Task — add one module-level helper and one call site. Do NOT modify the Gap-1b guard, `_teardown_worktree`, or `_create_worktree`.**
>
> **(A) New module-level helper** (place near `_teardown_worktree`):
> `def _retry_recoverable_teardown(gate_result: dict, project_path: str, wt_path: str, slug: str) -> bool:`
> Behavior, in this exact order:
> - Collect `wt_fails = [f for f in gate_result.get("failures", []) if f.get("gate") == "worktree_teardown"]`. If empty → `return False` (nothing to retry).
> - If `not os.path.isdir(wt_path)` → `_log("INFO", f"continue-resume: worktree gone at {wt_path} — skipping teardown retry (commits, if any, are on a bellows-preserved/* branch); leaving failure for Gap-1b halt", slug=slug)` and `return False`.
> - If NOT every wt_fail is the dirty-tree variant — i.e. `not all("worktree_teardown_dirty_tree" in (f.get("evidence") or "") for f in wt_fails)` → `_log("INFO", f"continue-resume: non-dirty-tree teardown failure (content conflict) — not retrying; leaving failure for Gap-1b halt", slug=slug)` and `return False`.
> - Otherwise attempt recovery inside `try:` — `_teardown_worktree(project_path, wt_path, slug)`:
>   - On success (no raise): remove ALL worktree_teardown failures in place — `gate_result["failures"] = [f for f in gate_result.get("failures", []) if f.get("gate") != "worktree_teardown"]`; `_log("EVENT", f"continue-resume: dirty-tree teardown retry SUCCEEDED — commits landed on main, worktree removed; clearing worktree_teardown failure so resume advances", slug=slug)`; `return True`.
>   - `except WorktreeTeardownError as e:` → `_log("WARN", f"continue-resume: teardown retry still failing ({e}) — leaving failure for Gap-1b halt", slug=slug)`; `return False`.
>   - `except Exception as e:` → `_log("WARN", f"continue-resume: teardown retry errored ({e}) — leaving failure for Gap-1b halt", slug=slug)`; `return False`.
> The helper must NEVER raise and must NEVER remove a non-worktree_teardown failure.
>
> **(B) Call site** — at the TOP of the `if v == "continue":` branch, IMMEDIATELY BEFORE the Gap-1b `if any(...)` guard, add:
> ```
> # Gap 1c: re-attempt a recoverable (dirty-tree) teardown before the Gap-1b halt decision.
> # By verdict time the operator has usually committed the stray dirty file, so the retry
> # lands Step N's commits and clears the failure — letting the normal advance proceed.
> _c_project_path = os.path.dirname(os.path.dirname(decisions_path))
> _c_wt_path = os.path.join(_c_project_path, ".bellows-worktrees", cleanup_slug)
> _retry_recoverable_teardown(gate_result, _c_project_path, _c_wt_path, cleanup_slug)
> ```
> The existing Gap-1b guard then runs UNCHANGED against the possibly-cleared `gate_result["failures"]`.
>
> **(C) Regression tests** in `tests/test_consume_verdicts.py` (mirror the existing fixture/monkeypatch style; target the helper directly — do NOT drive the full consume loop):
> - `test_retry_clears_dirty_tree_teardown_on_success` — `gate_result` with one `{"gate": "worktree_teardown", "evidence": "worktree_teardown_dirty_tree: ..."}` failure; `wt_path` = an existing tmp dir; monkeypatch `_teardown_worktree` to no-op (success). Assert helper returns `True` AND `gate_result["failures"]` no longer contains any `worktree_teardown` entry.
> - `test_retry_skips_content_conflict` — failure evidence is a cherry-pick content conflict (no `worktree_teardown_dirty_tree` token); `wt_path` exists. Assert returns `False`, failure RETAINED, and `_teardown_worktree` was NOT called (spy/monkeypatch to record calls).
> - `test_retry_skips_when_worktree_missing` — dirty-tree failure but `wt_path` does NOT exist. Assert returns `False`, failure RETAINED, `_teardown_worktree` NOT called.
> - `test_retry_keeps_failure_when_teardown_raises_again` — dirty-tree failure, `wt_path` exists, monkeypatch `_teardown_worktree` to raise `WorktreeTeardownError`. Assert returns `False` and the worktree_teardown failure is RETAINED (so Gap-1b still halts).
>
> **Pre-edit baseline:** run `python3 -m pytest tests/ 2>&1 | tail -15` and record the pass/fail counts (note the known carry-over failures) BEFORE editing. Re-run AFTER editing; the only delta must be the new tests passing — ZERO new failures.
>
> **Commit** (do NOT push — Planner handles session-wrap): stage `bellows.py`, `tests/test_consume_verdicts.py`, the dev log, and `knowledge/research/agent-prompt-feedback.md`; message `feat(bellows): re-attempt recoverable dirty-tree teardown on continue-resume (Gap 1c)`.
>
> **Dev log** → `knowledge/development/reattempt-teardown-on-continue-resume-2026-06-04.md`: helper placement, the exact predicate order, the dirty-tree-only / missing-worktree / repeat-failure skip rules, the call-site location relative to the Gap-1b guard, pre-edit verification results, both pytest runs (before/after counts). Include an **Output Receipt** with a "Files Created or Modified" list.
>
> **Standard prompt feedback protocol** → append an entry to `knowledge/research/agent-prompt-feedback.md`.
>
> **Deposits:**
> - `bellows/knowledge/development/reattempt-teardown-on-continue-resume-2026-06-04.md`
> - `bellows/knowledge/research/agent-prompt-feedback.md`
> - `bellows/bellows.py` (modified)
> - `bellows/tests/test_consume_verdicts.py` (modified)
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
> **Scope note — code-level ONLY.** Do NOT dispatch or simulate a live multi-step plan through the daemon to test this. Exercising the retry path live would require an actual dirty-tree-teardown-failure-then-continue state, which means tripping the teardown/resume bug during this plan's own close/resume. Verify by reading the code and running the unit/regression suite against the helper with a constructed `gate_result` and a monkeypatched `_teardown_worktree`. Nothing in this step should start the daemon or move a plan into a watched `decisions/` directory.
>
> **Before starting, read `knowledge/development/reattempt-teardown-on-continue-resume-2026-06-04.md` (DEV's Step 1 deposit) and check its Output Receipt status; if not Complete, stop and report the blocker.**
>
> **Deliverable Verification (Rule 17).** Read DEV's Output Receipt "Files Created or Modified" list. For each, verify the file exists and the declared change is present. Produce a verification table `| # | Deliverable | Expected | Status (PASS/FAIL) | Evidence |` (use the literal words PASS / FAIL in the Status column — not glyphs). Specifically:
>
> 1. **Helper present and correct** — `_retry_recoverable_teardown(gate_result, project_path, wt_path, slug)` exists near `_teardown_worktree`; collects `worktree_teardown` failures; returns `False` early when none / when `wt_path` missing / when any failure is NOT the `worktree_teardown_dirty_tree` variant; on retry success clears ALL worktree_teardown failures in place and returns `True`; never raises. Capture the full helper body to `evidence/retry_helper.txt`.
> 2. **Dirty-tree discriminator gate** — the retry fires ONLY when every worktree_teardown failure's evidence contains `worktree_teardown_dirty_tree`; a content-conflict failure is skipped and `_teardown_worktree` is not called. Capture the predicate to `evidence/discriminator_gate.txt`.
> 3. **Failure-clearing is scoped** — only `worktree_teardown` entries are removed from `gate_result["failures"]`; any other failure is preserved. Capture the list-comprehension to `evidence/failure_clearing.txt`.
> 4. **Call-site order** — the `_retry_recoverable_teardown(...)` call sits at the TOP of the `if v == "continue":` branch, IMMEDIATELY BEFORE the Gap-1b `if any(f.get("gate") == "worktree_teardown" ...)` guard; the Gap-1b guard itself is byte-unchanged. Capture the call site + the unchanged guard to `evidence/guard_order.txt`.
> 5. **Out-of-scope code untouched** — `git --no-pager diff -- bellows.py` shows changes confined to (i) the new helper and (ii) the 6-line call block at the top of the continue branch; `_teardown_worktree`, `_create_worktree`, and the Gap-1b guard body are byte-unchanged. Capture the diff scope to `evidence/diff_scope.txt`.
> 6. **Four regression tests exist** — grep `tests/test_consume_verdicts.py` for `test_retry_clears_dirty_tree_teardown_on_success`, `test_retry_skips_content_conflict`, `test_retry_skips_when_worktree_missing`, `test_retry_keeps_failure_when_teardown_raises_again` → all four present. Capture to `evidence/new_tests_grep.txt`.
> 7. **Dev log complete** — the dev log exists with helper placement, predicate order, skip rules, call-site location, pre-edit verification, both pytest runs. Capture filesize + first/last 5 lines to `evidence/dev_log_check.txt`.
>
> Any FAIL blocks plan close — report to CEO.
>
> **Test execution.** Run the full suite: `python3 -m pytest tests/ -v 2>&1 | tail -200`. Capture to `evidence/pytest_full.txt`. Verify: (a) all four new tests appear in verbose output and PASS; (b) ZERO NEW failures beyond the carry-over present in DEV's pre-edit baseline; (c) total pass count == DEV's reported post-edit number.
>
> **Behavioral spot-checks (read the test assertions, do not invent new live runs).** Confirm from the test bodies: (i) the success test asserts the worktree_teardown failure is GONE from `gate_result["failures"]` after the helper returns `True`; (ii) the content-conflict and missing-worktree tests assert `_teardown_worktree` was NOT called and the failure is RETAINED; (iii) the raises-again test asserts the failure is RETAINED so Gap-1b still halts. Capture to `evidence/behavior_spotcheck.txt`.
>
> **Rule 20 self-check** — run the canonical Rule 20 self-check from `RULE_20_SELF_CHECK_BLOCK.md` at governance root. Values: `plan_slug` = `executable-reattempt-teardown-on-continue-resume-2026-06-04`; `qa_report_path` = `bellows/knowledge/qa/reattempt-teardown-on-continue-resume-2026-06-04.md`; `evidence_dir` = `bellows/knowledge/qa/evidence/reattempt-teardown-on-continue-resume-2026-06-04/`; `required_evidence_files` = `["retry_helper.txt", "discriminator_gate.txt", "failure_clearing.txt", "guard_order.txt", "diff_scope.txt", "new_tests_grep.txt", "dev_log_check.txt", "pytest_full.txt", "behavior_spotcheck.txt"]`. Include literal stdout in the QA report. If FAILED, halt — report to CEO.
>
> **Final:** Update `bellows/PROJECT_STATUS.md` — prepend a 2026-06-04 entry under Completed for "Re-attempt recoverable dirty-tree teardown on continue-resume (Gap 1c)" with a one-paragraph summary, using `Filesystem:edit_file` (find the existing topmost Completed entry as anchor and insert immediately before it).
>
> **DAEMON RESTART REMINDER — put in the QA deposit under "Flags for CEO":** "REMINDER: restart the Bellows daemon to activate the Gap 1c retry. The running daemon executed this plan with pre-edit `_consume_verdicts`; the helper activates on the next continue-resume after restart. Also owed: capture this plan's organic Opus baseline (turns/wall/cost) from the step logs for the Opus↔Sonnet A/B."
>
> **Commit:** stage `knowledge/qa/reattempt-teardown-on-continue-resume-2026-06-04.md`, the `knowledge/qa/evidence/reattempt-teardown-on-continue-resume-2026-06-04/` evidence files, and `PROJECT_STATUS.md` with message `qa(bellows): reattempt-teardown-on-continue-resume verified — dirty-tree-only retry, scoped failure-clearing, zero new regressions (Gap 1c)`. **DO NOT push to origin** — the Planner handles session-wrap commits.
>
> **Standard prompt feedback protocol** → append an entry to `knowledge/research/agent-prompt-feedback.md`. Second commit: `docs: prompt feedback — bellows QA reattempt-teardown-on-continue-resume`. **DO NOT push.**
>
> **Deposits:**
> - `bellows/knowledge/qa/reattempt-teardown-on-continue-resume-2026-06-04.md`
> - `bellows/knowledge/qa/evidence/reattempt-teardown-on-continue-resume-2026-06-04/`
> - `bellows/PROJECT_STATUS.md` (modified)
> - `bellows/knowledge/research/agent-prompt-feedback.md`
