# Bellows — _seen Discard on Dispatch-Mode Rejection

**Date:** 2026-05-28 | **Tier:** Executable | **Dispatch Mode:** bellows | **Test Scope:** tests/test_bellows.py (or tests/test_consume_verdicts.py) — _seen lifecycle on validator rejection | **Execution:** Step 1 (DEV) → Step 2 (QA) | **qa_steps:** 2 | **pause_for_verdict:** always

## Execution Map

Step 1 (DEV) → Step 2 (QA). Sequential.

## Context

Diagnostic `Done/diagnostic-rescan-miss-disposition-2026-05-28.md` (findings: `knowledge/research/rescan-miss-disposition-2026-05-28.md`) confirmed the root cause of the session-12 plan-claim miss: the dispatch-mode validator rejection path in `run_plan` moves the plan to `halted-*` and returns WITHOUT calling `bellows._seen.discard()`. It is the ONLY early-exit in `run_plan` that strands the slug. Because `verdict.slug_from_path` strips both `diagnostic-` and `executable-` prefixes, a follow-on executable sharing a rejected diagnostic's base name inherits the stranded slug and is silently skipped by the `_handle` `_seen` guard on every rescan tick until a daemon restart clears the in-memory set.

Fix: add the discard call to the rejection path, mirroring the existing precedent at `bellows.py:668` (auto-close path: `bellows._seen.discard(verdict.slug_from_path(plan_path))`).

## STEP 1 — DEV: add _seen.discard to the rejection path

> Acting as the Bellows Developer, apply a 2-line fix to `bellows/bellows.py`.
>
> **Read first (post a 1-line "Read X." acknowledgment after each):**
> 1. `bellows/agents/BELLOWS_DEVELOPER.md` — specialist scope.
> 2. `bellows/bellows.py` — read `run_plan` (def at line 334, `bellows=None` param). Read the dispatch-mode-validator rejection block (currently lines 386–394, inside `if validation_result["rejected"]:`). Read the existing discard precedent at line 668 (auto-close path) to match its exact form.
> 3. `bellows/knowledge/research/rescan-miss-disposition-2026-05-28.md` — the diagnostic, Section 4 (fix spec).
>
> **The change.** In the rejection block, after `shutil.move(plan_path, halted_path)` and BEFORE `return`, add a guarded discard. Current block:
> ```python
> if validation_result["rejected"]:
>     halted_path = os.path.join(plan_dir, f"halted-{base_filename}")
>     shutil.move(plan_path, halted_path)
>     _log("ERROR", f"plan rejected by dispatch-mode validator: {validation_result['reject_reason']}", slug=slug_for(plan_name))
>     notifier.push(app_key, user_key, "Bellows — Plan Rejected", f"Plan: {plan_name}\nReason: {validation_result['reject_reason']}")
>     return
> ```
> Insert after the `shutil.move` line:
> ```python
>     if bellows is not None:
>         bellows._seen.discard(verdict.slug_from_path(plan_path))
> ```
> Match the form at line 668 exactly (same guard style, same slug expression). Note `plan_path` still points at the pre-move path string at this point — line 668 uses `plan_path` the same way, so the slug derivation is consistent. Do NOT change anything else in the block.
>
> **Scope guard:** this is a 2-line addition. Do NOT refactor the rejection block, do NOT touch any other `return` path in `run_plan`, do NOT modify the validator. If you notice another early-exit that appears to strand `_seen`, FLAG it in your Output Receipt — do NOT fix it in this plan (it is out of scope; a separate audit is queued).
>
> **Commit** (do NOT push): `git add bellows.py && git commit -m "fix(bellows): discard _seen slug on dispatch-mode rejection"`. Report the commit SHA.
>
> **Deposits:**
> - `bellows/knowledge/development/seen-discard-rejection-path-2026-05-28.md` — brief dev log: the diff, the line-668 precedent match, and any flagged out-of-scope strand sites.

## STEP 2 — QA: regression tests for slug cleanup on rejection

> **FIRST — verify Step 1's Output Receipt:** confirm the DEV commit landed and the 2-line discard is present in the rejection block (read `bellows.py` directly). If the discard is missing or malformed, HALT and report.
>
> Acting as the Bellows QA Engineer, add regression tests proving the fix and run the suite.
>
> **Read first (post a 1-line "Read X." acknowledgment after each):**
> 1. `bellows/agents/BELLOWS_QA.md` — specialist scope.
> 2. `bellows/bellows.py` — the rejection block with the new discard (verify it is present).
> 3. `bellows/knowledge/research/rescan-miss-disposition-2026-05-28.md` — Section 4 regression-test surface.
> 4. Existing tests touching the dispatch-mode validator and `_seen` (grep `tests/` for `validate_at_claim`, `dispatch_mode`, `_seen`, `rejected`) to match fixture style and find the right test file.
>
> **Tests to add** (place in the test file that already exercises validator rejection or `_seen`; match existing fixture conventions):
> 1. **Slug cleanup on rejection:** dispatch a plan with an invalid/missing dispatch mode through the rejection path with a `bellows` instance passed; assert the plan is moved to `halted-*` AND the plan's slug is NOT in `bellows._seen` after `run_plan` returns.
> 2. **Cross-plan-type slug collision (the real-world repro):** reject a `diagnostic-<base>.md` plan, then deposit/dispatch an `executable-<base>.md` plan sharing the same base name; assert the executable is NOT skipped by the `_seen` guard (i.e., the stranded-slug path is closed). Use `verdict.slug_from_path` to confirm both filenames resolve to the same slug.
>
> Confirm existing `_seen` tests (on_modified invalidation, auto-close discard, verdict discard) still pass — the new discard call site must not regress them.
>
> **Run the full suite.** Report pass/fail counts and confirm zero new regressions against the known carry-overs.
>
> **Rule 20 self-check:** run the canonical block from `RULE_20_SELF_CHECK_BLOCK.md` (governance root) and include its literal stdout in the QA report. The report MUST contain the canonical banner `Rule 20 — QA Self-Check Results` and, on a passing run, the line `PASSED — SELF-CHECK PASSED` (em-dashes, exact). Do NOT paraphrase the banner.
>
> **Deposits:**
> - `bellows/knowledge/qa/executable-seen-discard-rejection-path-2026-05-28.md` — QA report: test additions, full-suite counts, Rule 20 self-check stdout.
