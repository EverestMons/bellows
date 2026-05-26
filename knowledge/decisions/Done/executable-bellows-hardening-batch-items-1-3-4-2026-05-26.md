# Bellows Hardening Batch — Items 1, 3, 4
**Project:** bellows
**Date:** 2026-05-26
**Author:** Planner
**Dispatch Mode:** bellows
**Total Steps:** 2
**pause_for_verdict:** after_step_1
**auto_close:** false
**qa_steps:** 2
**Test Scope:** full-suite

---

## CEO Context

Batch close of three confirmed-Open BACKLOG items. All three are small, independent (Q6 of `bellows-hardening-batch-freshness-2026-05-26.md` confirms no merge churn risk), and ground in verified line numbers from the 2026-05-26 SA freshness audit.

**Item 1** — `_gate_rule_20_self_check` ambiguous evidence string at `gates.py:441` and `gates.py:464`. Both branches emit byte-identical evidence `"no QA deposit contains Rule 20 self-check banner"` for structurally-distinct failure modes (a) no `.md` paths parsed from deposits block, vs (b) banner literally absent from QA report content. Fix: change line 441's string to disambiguate; leave line 464 unchanged.

**Item 3** — `_seen` slug-keyed cache (NOT a dedicated dispatch_mode_validator cache, per SA re-characterization) at `bellows.py:1047` is not invalidated when watchdog's `on_modified` handler fires at `bellows.py:1032-1034`. Result: corrected re-deposit at same filename after `dispatch_mode_validator` rejection (or any other rejection routing through `_seen`) gets silently skipped on subsequent scans. Workaround today: rename the file. Fix: invalidate `_seen` entry on `on_modified` when the modified file's slug is in `_seen` AND the file is a runnable plan whose current path is NOT prefixed with `in-progress-`, `verdict-pending-`, or `halted-` (the three Bellows-managed lifecycle prefixes). The exclusion guard prevents re-dispatch loops on Bellows's own lifecycle renames.

**Item 4** — `_apply_defensive_header_defaults` at `bellows.py:382` mutates the pre-gate `header` dict, but `header` is reassigned at `bellows.py:498` from `gate_result.get("plan_header", {})` (fresh dict from `gates.check()` re-parse). The defensive default never propagates to `header_says_pause()` consumers at `bellows.py:506` (intermediate steps) and `bellows.py:596` (final step). Fix: call `_apply_defensive_header_defaults(header, total_steps)` again after line 498 so the re-parsed header inherits the default too.

**Note on Item 2:** Already shipped 2026-05-25 via `executable-extract-plan-required-deposits-set-to-list-2026-05-25` (Option a). BACKLOG hygiene closure landed earlier this session. No code change in this batch.

**Diagnostic findings cited (Rule 27):**
- `bellows/knowledge/research/bellows-hardening-batch-freshness-2026-05-26.md` — Gap Assessment table rows 1, 3, 4; Q5 verification block (line numbers); Q6 ordering analysis (independence confirmed).

**Test scope justification:** `full-suite`. Item 1 touches gate evidence in a code path exercised by `test_rule_20_self_check_gate_*` tests. Item 3 touches `PlanHandler._handle` which is integration-tested across `test_bellows.py` and `test_consume_verdicts.py`. Item 4 touches `run_plan()` pause routing which is integration-tested across `test_bellows.py`, `test_verdict.py`, and `test_consume_verdicts.py`. The combined surface warrants full-suite verification.

Pre-edit baseline expectation: 407 collected / 5 known carry-over failures (4 worktree-context `test_decisions.py` + 1 long-standing `test_run_step_timeout`). Post-edit expectation: same pass count + new regression tests pass cleanly, zero regressions.

---
---

## STEP 1 — DEV

---

> You are the Bellows Developer. Read your specialist file at `agents/BELLOWS_DEVELOPER.md` and `governance/GUARDRAILS.md` first. **Skip glossary read — domain terminology is fully covered in the specialist file.** Note: worktree root IS the bellows project root — strip the `bellows/` prefix from any path references in this prompt when running commands.
>
> **Reads (mandatory, in order):** (1) `agents/BELLOWS_DEVELOPER.md` — your specialist file; (2) `knowledge/research/bellows-hardening-batch-freshness-2026-05-26.md` — SA findings, the source-of-truth for line numbers and fix shapes; (3) `gates.py` lines 430–470 — Item 1's `_gate_rule_20_self_check` function with both failure branches; (4) `bellows.py` lines 990–1060 — Item 3's `PlanHandler` class including `_seen` set, `_handle` method, `on_created`/`on_modified` handlers; (5) `bellows.py` lines 315–510 — Item 4's `_apply_defensive_header_defaults` definition (~line 318), first call site (~line 382), `gates.check()` invocation, and the `header` reassignment (~line 498).
>
> **Pre-edit verification (Rule 39).** Before any edits, re-run these three SA verification queries:
>
> 1. **Claim:** `gates.py:441` and `gates.py:464` emit byte-identical evidence strings.
>    **Query:** `grep -n 'no QA deposit contains Rule 20 self-check banner' gates.py`
>    **Expected output:** exactly two hits at lines 441 and 464.
>
> 2. **Claim:** `_seen` is initialized at `bellows.py:1047` and the `on_modified` handler at `bellows.py:1032-1034` calls `_handle` without invalidating `_seen`.
>    **Query:** `grep -n 'self._seen' bellows.py` and `grep -n 'on_modified' bellows.py`
>    **Expected output:** `self._seen = set()` at line 1047; `on_modified` handler at line 1032-1034 calling `self._handle(event.src_path)`; `self._seen.add(slug)` at line 1024 inside `_handle`.
>
> 3. **Claim:** `header` is reassigned at `bellows.py:498` from `gate_result.get("plan_header", {})` after `gates.check()`.
>    **Query:** `grep -n 'header = gate_result.get' bellows.py`
>    **Expected output:** exactly one hit at line 498.
>
> If any query's actual output differs materially from expected, **STOP** — do not proceed with edits. Deposit a verification-mismatch report to `knowledge/flags/verification-mismatch-bellows-hardening-batch-2026-05-26-step-1.md` and report to CEO.
>
> **Task — three independent edits.**
>
> **Change 1 — Item 1 evidence string disambiguation (`gates.py`).** Locate `_gate_rule_20_self_check`. The function has two distinct failure branches that currently emit identical evidence:
> - Line ~441 — branch fires when `not md_paths` (deposits-block parse returned no `.md` paths). This is a **Planner-authoring** discipline failure: the plan's `**Deposits:**` block is malformed (e.g., inline-format without backticks, or `**Deposits:**` field omitted entirely).
> - Line ~464 — branch fires when `banner not in content` (banner literally absent from QA report). This is a **QA-agent** discipline failure: agent didn't run the canonical Rule 20 block or paraphrased the banner.
>
> Replace the evidence string at line ~441 with: `"deposits block declares no .md paths (check **Deposits:** block format — must be multi-line bullets)"`. Leave line ~464 unchanged. The two branches now route the Planner to distinct discipline-rules at verdict-read time.
>
> **Change 2 — Item 3 `_seen` invalidation on `on_modified` (`bellows.py`).** Locate `PlanHandler.on_modified` (~line 1032-1034). Currently it calls `self._handle(event.src_path)` unconditionally. The fix invalidates the `_seen` entry when the modified file is a runnable plan whose slug is in `_seen` AND the current filename is NOT prefixed with `in-progress-`, `verdict-pending-`, or `halted-` (Bellows-managed lifecycle prefixes — re-dispatching during these states would loop).
>
> The exclusion guard is critical: Bellows itself fires `on_modified` events when it renames plans to `in-progress-*` (claim), `verdict-pending-*` (pause), or `halted-*` (terminal). Without the guard, the invalidation would re-dispatch the plan on Bellows's own lifecycle moves and create dispatch loops.
>
> Implementation shape:
> ```python
> def on_modified(self, event):
>     if event.is_directory:
>         return
>     path = event.src_path
>     filename = os.path.basename(path)
>     # Guard: don't invalidate _seen on Bellows-managed lifecycle renames
>     LIFECYCLE_PREFIXES = ("in-progress-", "verdict-pending-", "halted-")
>     if not any(filename.startswith(p) for p in LIFECYCLE_PREFIXES):
>         slug = verdict.slug_from_path(path)
>         if slug in self._seen:
>             self._seen.discard(slug)
>     self._handle(path)
> ```
>
> Adapt the snippet to match the existing code style and import conventions (e.g., if `verdict.slug_from_path` is already imported at module level, use it as-is; if a local helper exists for slug extraction, use that instead). Verify by reading the actual current handler — the diff should be ~5-7 LOC.
>
> **Change 3 — Item 4 defensive default propagation to re-parsed header (`bellows.py`).** Locate the `header = gate_result.get("plan_header", {})` reassignment at line ~498. Insert immediately after it:
>
> ```python
> _apply_defensive_header_defaults(header, total_steps)
> ```
>
> This mirrors the pre-gate call at line ~382. Both `header` (now the re-parsed dict) and `total_steps` (set during pre-gate parsing, still in scope) are available. After this insertion, the re-parsed header inherits the defensive default before being passed to `header_says_pause()` at lines ~506 and ~596.
>
> **Verify `total_steps` is in scope at the insertion point** before editing. If it isn't, halt and report — the fix shape needs re-scoping. Per SA findings, it should be in scope, but confirm with a quick read of the surrounding ~15 lines.
>
> **Regression tests (add new, do not modify existing unless required by the changes).**
>
> 1. **For Item 1** — `tests/test_gates.py` (or wherever `_gate_rule_20_self_check` tests live): add `test_rule_20_self_check_distinguishes_no_md_paths_from_missing_banner` that constructs two failing fixtures (one with deposits-block declaring zero `.md` paths, one with `.md` paths declared but banner missing from the QA report content) and asserts the two evidence strings differ.
>
> 2. **For Item 3** — `tests/test_bellows.py` (or `test_consume_verdicts.py`, wherever PlanHandler watchdog tests live): add `test_on_modified_invalidates_seen_for_runnable_plan` that (a) adds a slug to `_seen`, (b) fires `on_modified` against a file with the matching slug and non-lifecycle prefix, (c) asserts the slug was removed from `_seen` and `_handle` was called. Also add `test_on_modified_preserves_seen_for_lifecycle_renames` that (a) adds a slug to `_seen`, (b) fires `on_modified` against `in-progress-<slug>.md` (or `verdict-pending-*`, or `halted-*`), (c) asserts the slug remains in `_seen` (guard fired) AND `_handle` was still called for normal handler routing.
>
> 3. **For Item 4** — `tests/test_bellows.py`: add `test_apply_defensive_header_defaults_propagates_to_reparsed_header` that (a) authors a multi-step plan with a sparse header missing `pause_for_verdict`, (b) runs through `run_plan()` to the point where `header` has been reassigned from `gate_result`, (c) asserts the re-parsed `header` now contains the defensive default `pause_for_verdict: after_step_1`. Use mocking as needed to isolate from the full subprocess execution path — the test scope is the defensive-default propagation, not full dispatch.
>
> **Test execution.** Run full test suite: `python3 -m pytest tests/ -v 2>&1 | tail -100`. Capture pass/fail counts. Expected: 407 + 3 new tests = 410 passed / 5 carry-over failures, zero regressions.
>
> **Anchor verification before commit.** Run these greps and verify expected output:
> - `grep -n 'deposits block declares no .md paths' gates.py` — expected: exactly 1 hit (the new Item 1 string).
> - `grep -n 'no QA deposit contains Rule 20 self-check banner' gates.py` — expected: exactly 1 hit (the unchanged line 464 string).
> - `grep -n 'self._seen.discard' bellows.py` — expected: at least 1 new hit in the `on_modified` handler (plus any pre-existing discards from `_seen` lifecycle terminal events).
> - `grep -n '_apply_defensive_header_defaults' bellows.py` — expected: exactly 3 hits (definition + 2 call sites: the original at line ~382 and the new one after line ~498).
>
> **Deposit:** Author a dev log to `knowledge/development/bellows-hardening-batch-items-1-3-4-2026-05-26.md` documenting: the three changes with before/after snippets (3-5 lines of context each), the three pre-edit verification query results, the three new regression test functions with their assertions, full-suite pytest output (pass/fail counts), the four anchor-verification grep results, and the Output Receipt per your specialist file.
>
> **Commit:** stage code changes (gates.py, bellows.py), test additions (test_gates.py, test_bellows.py), and dev log with message `fix(bellows): hardening batch — items 1, 3, 4 (evidence string disambiguation, _seen on_modified invalidation, defensive default re-parse propagation)`. **DO NOT push to origin** — the Planner handles session-wrap commits.
>
> **Standard prompt feedback protocol** → append entry to `knowledge/research/agent-prompt-feedback.md`. Second commit: `docs: prompt feedback — bellows DEV hardening batch items 1, 3, 4`. **DO NOT push.**
>
> **Deposits:**
> - `bellows/knowledge/development/bellows-hardening-batch-items-1-3-4-2026-05-26.md`
> - `bellows/knowledge/research/agent-prompt-feedback.md`
> - `bellows/gates.py` (modified)
> - `bellows/bellows.py` (modified)
> - `bellows/tests/test_gates.py` (modified)
> - `bellows/tests/test_bellows.py` (modified)

---
---

## STEP 2 — QA

---

> You are the Bellows QA Agent. Read your specialist file at `agents/BELLOWS_QA.md` and `governance/GUARDRAILS.md` first. **Skip glossary read — domain terminology is fully covered in the specialist file.** Note: worktree root IS the bellows project root — strip the `bellows/` prefix from any path references in this prompt when running commands.
>
> **Before starting, read `knowledge/development/bellows-hardening-batch-items-1-3-4-2026-05-26.md` (DEV's Step 1 deposit) and check its Output Receipt status; if not Complete, stop and report the blocker.**
>
> **Deliverable Verification (Rule 17).** Read DEV's Output Receipt "Files Created or Modified (Code)" list. For each entry, verify the file exists and the declared changes are present. Produce verification table `| # | Deliverable | Expected | Status (✅/❌) | Evidence |`. Specifically:
>
> 1. **Item 1 evidence string** — `gates.py:441` contains the new disambiguated string `"deposits block declares no .md paths (check **Deposits:** block format — must be multi-line bullets)"`. Grep with `grep -n 'deposits block declares no .md paths' gates.py` — expected 1 hit at line ~441. Capture to `evidence/gates_441_grep.txt`.
> 2. **Item 1 line 464 preserved** — `gates.py:464` still contains the original `"no QA deposit contains Rule 20 self-check banner"`. Grep with `grep -n 'no QA deposit contains Rule 20 self-check banner' gates.py` — expected 1 hit at line ~464. Capture to `evidence/gates_464_grep.txt`.
> 3. **Item 3 invalidation logic** — `bellows.py` `PlanHandler.on_modified` contains the lifecycle-prefix guard and `self._seen.discard(slug)` call. Read the handler (10-15 lines starting at ~line 1032) and confirm: (a) the three lifecycle prefixes `in-progress-`, `verdict-pending-`, `halted-` appear in the guard; (b) `self._seen.discard(slug)` is called only when the guard passes AND the slug is in `_seen`; (c) `self._handle(path)` is still called at the end of the handler regardless of guard outcome. Capture handler text to `evidence/on_modified_handler.txt`.
> 4. **Item 4 default re-application** — `bellows.py` has 3 occurrences of `_apply_defensive_header_defaults` (definition + 2 call sites). Grep with `grep -n '_apply_defensive_header_defaults' bellows.py` — expected 3 hits. Capture to `evidence/defensive_default_callsites.txt`. The new call site should be 1-2 lines after the `header = gate_result.get("plan_header", {})` reassignment.
> 5. **Item 1 regression test exists** — `tests/test_gates.py` contains `test_rule_20_self_check_distinguishes_no_md_paths_from_missing_banner`. Grep with `grep -n 'distinguishes_no_md_paths' tests/test_gates.py` — expected 1 hit. Capture to `evidence/test_item_1_grep.txt`.
> 6. **Item 3 regression tests exist** — `tests/test_bellows.py` (or wherever DEV placed them) contains `test_on_modified_invalidates_seen_for_runnable_plan` AND `test_on_modified_preserves_seen_for_lifecycle_renames`. Grep with `grep -n 'on_modified_invalidates_seen\|on_modified_preserves_seen' tests/` — expected 2 hits. Capture to `evidence/test_item_3_grep.txt`.
> 7. **Item 4 regression test exists** — `tests/test_bellows.py` contains `test_apply_defensive_header_defaults_propagates_to_reparsed_header`. Grep with `grep -n 'propagates_to_reparsed_header' tests/` — expected 1 hit. Capture to `evidence/test_item_4_grep.txt`.
> 8. **Dev log exists** — `knowledge/development/bellows-hardening-batch-items-1-3-4-2026-05-26.md` exists, contains three change-block sections with before/after snippets, pre-edit verification results, and pytest output. Verify by reading the file. Capture filesize and first/last 5 lines to `evidence/dev_log_check.txt`.
>
> Any ❌ blocks plan close — report to CEO.
>
> **Test execution.** Run full test suite: `python3 -m pytest tests/ -v 2>&1 | tail -120`. Capture to `evidence/pytest_full.txt`. Verify: (a) total passes = DEV's reported number (expect 410 = 407 baseline + 3 new tests, or similar with the 5 known carry-over failures still failing); (b) zero new failures beyond the 5 carry-overs; (c) zero regressions; (d) the 3 new tests appear in the verbose output and all 3 PASS.
>
> **Structural-compliance checks.**
>
> (a) **Single-file scope for Item 1 fix** — confirm Item 1's change is bounded to `gates.py` (no incidental edits to bellows.py, verdict.py, or elsewhere). Run `git diff HEAD~2 HEAD -- gates.py` (or HEAD~1 if only one DEV commit) and verify the only gates.py change is the line 441 string. Capture to `evidence/item_1_scope.txt`.
>
> (b) **Lifecycle-prefix list completeness for Item 3** — confirm the guard's prefix list matches the three prefixes documented in `bellows/PROJECT_BRIEF.md` (or `CLAUDE.md`) lifecycle section. If a fourth prefix exists in the project documentation that DEV missed, flag it. Read the project documentation, list all documented Bellows-managed lifecycle prefixes, and compare against the guard. Capture to `evidence/lifecycle_prefix_audit.txt`.
>
> (c) **Defensive default call symmetry for Item 4** — the two `_apply_defensive_header_defaults` call sites should pass identical arguments (`header, total_steps`). Capture both call lines side-by-side to `evidence/defensive_default_symmetry.txt`. If the new call site uses different parameters than the pre-gate call site, flag it.
>
> **Rule 20 self-check** — run the canonical Rule 20 self-check from `RULE_20_SELF_CHECK_BLOCK.md` at governance root. Use these values: `plan_slug` = `executable-bellows-hardening-batch-items-1-3-4-2026-05-26`; `qa_report_path` = `bellows/knowledge/qa/executable-bellows-hardening-batch-items-1-3-4-2026-05-26.md`; `evidence_dir` = `bellows/knowledge/qa/evidence/executable-bellows-hardening-batch-items-1-3-4-2026-05-26/`; `required_evidence_files` = `["gates_441_grep.txt", "gates_464_grep.txt", "on_modified_handler.txt", "defensive_default_callsites.txt", "test_item_1_grep.txt", "test_item_3_grep.txt", "test_item_4_grep.txt", "dev_log_check.txt", "pytest_full.txt", "item_1_scope.txt", "lifecycle_prefix_audit.txt", "defensive_default_symmetry.txt"]`. Include literal stdout in QA report. If FAILED, halt — report to CEO.
>
> **Final:** Update `bellows/PROJECT_STATUS.md` — prepend a 2026-05-26 entry under Completed for "Bellows hardening batch — items 1, 3, 4 (evidence string disambiguation, _seen on_modified invalidation, defensive default re-parse propagation)" with a one-paragraph summary using `Filesystem:edit_file` (find the existing topmost Completed entry as the anchor and insert immediately before it).
>
> **DAEMON RESTART REMINDER goes in the QA deposit** under Flags for CEO: "REMINDER: restart Bellows daemon to load (a) the new Item 1 evidence string for verdict-read disambiguation, (b) the new Item 3 `_seen` invalidation logic for corrected-redeposit recovery, and (c) the new Item 4 defensive-default propagation. The running daemon executed this plan with pre-edit code; the three fixes activate on next plan dispatched after restart."
>
> **Commit:** stage QA report, evidence files, and PROJECT_STATUS update with message `qa(bellows): hardening batch items 1, 3, 4 verified — 3 new regression tests pass, zero regressions`. **DO NOT push to origin** — Planner handles session-wrap commits.
>
> **Standard prompt feedback protocol** → append entry to `bellows/knowledge/research/agent-prompt-feedback.md`. Second commit: `docs: prompt feedback — bellows QA hardening batch items 1, 3, 4`. **DO NOT push.**
>
> **Deposits:**
> - `bellows/knowledge/qa/executable-bellows-hardening-batch-items-1-3-4-2026-05-26.md`
> - `bellows/knowledge/qa/evidence/executable-bellows-hardening-batch-items-1-3-4-2026-05-26/`
> - `bellows/PROJECT_STATUS.md` (modified)
> - `bellows/knowledge/research/agent-prompt-feedback.md`
