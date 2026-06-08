# Bellows — Dirty-Tree Pre-Check Filter QA

**Date:** 2026-05-28 | **Tier:** Small | **Dispatch Mode:** bellows | **Test Scope:** targeted | **Execution:** Step 1 (QA) | **qa_steps:** 1 | **pause_for_verdict:** always

## Context

QA-only follow-on for the lifecycle-artifact filter shipped at commit `7bb05ae` (cherry-picked onto main after `executable-dirty-tree-precheck-false-trip-filter-2026-05-28` was halted Planner-direct — its Step 1 DEV substance landed via R2 recovery, but the QA step never ran because of a cascade from the very pre-check the filter is designed to fix).

**The shipped filter** at `bellows.py` lines 32-51 (regex + predicate) and 885-916 (pre-check filter integration) is in production but untested in the suite. The session-13 `_seen` fix had the same status; this plan exists so the dirty-tree filter doesn't carry the same "shipped-but-untested" tag past session-14 close.

**Critical load-bearing test:** Deliverable C — the filter-negative tests proving the filter does NOT mask real cherry-pick conflicts. If C fails, the filter is over-permissive and would silently hide real source-tree conflicts during teardown. C is the safety check on the entire ship.

**Why this should ship cleanly now:** The new filter is loaded in the running daemon (confirmed `bellows.py @ git:7bb05ae` at session restart 14:07:41). Lifecycle artifacts from this plan's own claim-rename, `verdict-pending-*`, etc. will be ignored by the pre-check on teardown — no false-trip, no cascade.

**Out of scope:**
- No production code edits. Tests-only.
- No new BACKLOG entries from this plan (close #1 and #2 in the QA report's Flags-for-CEO section).
- No PROJECT_STATUS.md edit beyond Rule 8's one-line at close (PROJECT_STATUS may itself be retired soon per a deferred decision).

## How to Run This Plan

Single QA step. Pauses for verdict per `pause_for_verdict: always`. Daemon owns dispatch — no manual bootstrap needed.

---
---

## STEP 1 — QA

---

> **FIRST — before doing anything else, claim this plan:** rename `executable-dirty-tree-precheck-filter-qa-2026-05-28.md` to `in-progress-executable-dirty-tree-precheck-filter-qa-2026-05-28.md` using `mv` in the worktree. **THEN, immediately and BEFORE any other reads or work: post a short visible message to chat (1-2 sentences) confirming you have claimed the plan and stating your immediate next action.** This is a liveness anchor. **AFTER posting confirmation:** read `bellows/agents/BELLOWS_QA.md` first, then read the files listed below.
>
> Acting as Bellows QA, verify the lifecycle-artifact filter shipped at `bellows.py` lines 32-51 (regex + predicate) and lines 885-916 (pre-check integration) closes the false-trip without masking real cherry-pick conflicts. The diagnostic at `bellows/knowledge/research/dirty-tree-precheck-false-trip-surface-2026-05-28.md` Section 6 is the authoritative test-surface spec; the halted executable's DEV log at `bellows/knowledge/development/dirty-tree-precheck-false-trip-filter-2026-05-28.md` documents the shipped code.
>
> **Files to read (post a 1-line "Read X." acknowledgment after each):**
>
> 1. `bellows/agents/BELLOWS_QA.md` — specialist scope.
> 2. `bellows/knowledge/research/dirty-tree-precheck-false-trip-surface-2026-05-28.md` — diagnostic. Section 3 (filter spec), Section 6 (test surface).
> 3. `bellows/knowledge/development/dirty-tree-precheck-false-trip-filter-2026-05-28.md` — DEV log documenting the shipped filter.
> 4. `bellows/bellows.py` — verify the filter is present. Locate `_LIFECYCLE_IGNORE_RE` at lines 32-51 and the modified pre-check at lines 885-916.
> 5. `bellows/tests/test_bellows.py` — locate existing teardown tests for fixture inspection and identify the appropriate insertion point for new tests.
>
> **Drafting markers:** Post a 1-line "Verifying Deliverable X." marker at the start of each deliverable below.
>
> ### Verification Checks
>
> | Check | Result | Detail |
> |---|---|---|
> | A — Code shape verification | (fill) | (fill) |
> | B — Filter-positive tests | (fill) | (fill) |
> | C — Filter-negative tests (critical safety) | (fill) | (fill) |
> | D — Existing-test regression | (fill) | (fill) |
> | E — Rule 20 self-check | (fill) | (fill) |
>
> **Deliverable A — Code shape verification (cite line numbers, paste snippets):**
>
> - `_LIFECYCLE_IGNORE_RE` regex exists in `bellows.py` at lines 36-40 matching the diagnostic Section 3 spec byte-for-byte. Paste the regex literal.
> - `_is_lifecycle_artifact()` at lines 43-51 with the signature and body from the diagnostic Section 3 (length guard, rename-arrow split, regex match).
> - The pre-check block at lines 885-916 uses `[line for line in dirty_lines if not _is_lifecycle_artifact(line)]` filter and `if blocking_lines:` predicate.
> - The evidence string contains the filtered-count annotation line `({len(dirty_lines) - len(blocking_lines)} lifecycle artifacts filtered, {len(blocking_lines)} blocking file(s) remain)`.
> - `_create_worktree` is unchanged. Cite `git --no-pager log --oneline -5 bellows.py` and confirm the filter commit `7bb05ae` is the most recent functional change.
> - The copy-back logic at lines ~939-960 is unchanged.
>
> **Deliverable B — Filter-positive tests (false-trip closure):**
>
> Add new tests in `tests/test_bellows.py`:
>
> 1. `test_teardown_ignores_lifecycle_artifacts` (~15 LOC). Mock `subprocess.run` so `git status --porcelain` with `cwd=project_path` returns ONLY lifecycle artifact lines (at minimum: `?? knowledge/decisions/in-progress-foo.md`, `?? knowledge/decisions/verdict-pending-foo.md`, `?? knowledge/decisions/halted-foo.md`, `?? knowledge/decisions/Done/foo.md`, `?? verdicts/pending/verdict-request-foo-step-1.md`, `?? verdicts/resolved/processed-verdict-foo-step-1.md`). Assert NO `WorktreeTeardownError` is raised. Assert the cherry-pick subprocess call IS attempted (the rest of teardown proceeds).
>
> 2. `test_teardown_ignores_deletion_porcelain_codes` (~10 LOC). Mock porcelain to return ` D knowledge/decisions/executable-foo.md` and `D  knowledge/decisions/diagnostic-foo.md` (deletion side of claim-rename). Assert NO `WorktreeTeardownError`. The diagnostic's Section 1 #5 pattern; session trips were all `??` codes, but the filter must handle deletion codes too.
>
> 3. `test_lifecycle_artifact_regex_coverage` (~20 LOC). Unit test for `_is_lifecycle_artifact()`. Verify positive matches for: `?? knowledge/decisions/in-progress-foo.md`, `?? knowledge/decisions/verdict-pending-foo.md`, `?? knowledge/decisions/halted-foo.md`, `?? knowledge/decisions/executable-foo.md`, `?? knowledge/decisions/diagnostic-foo.md`, `?? knowledge/decisions/Done/foo.md`, `?? knowledge/decisions/Done/nested/foo.md`, `?? verdicts/pending/anything.md`, `?? verdicts/resolved/anything.md`. Verify negative matches (must NOT be ignored) for: `?? knowledge/decisions/roadmap-foo.md`, `?? knowledge/decisions/parallel-1-executable-foo.md` (parallel prefix — flag if this is unexpectedly ignored), `?? knowledge/research/foo.md`, ` M PROJECT_STATUS.md`, ` M bellows.py`, ` M bellows` (submodule pointer).
>
> **Deliverable C — Filter-negative tests (CRITICAL SAFETY — proves filter does NOT mask real conflicts):**
>
> Add new tests in `tests/test_bellows.py`:
>
> 1. `test_teardown_blocks_on_non_lifecycle_untracked` (~15 LOC). Mock porcelain to return `?? knowledge/research/unexpected.md` (untracked but NOT lifecycle). Assert `WorktreeTeardownError` IS raised. Assert the evidence string contains the path. This is the MOST IMPORTANT test in this plan — it proves the filter is not over-permissive.
>
> 2. `test_teardown_blocks_on_dirty_project_status` (~12 LOC). Mock porcelain to return ` M PROJECT_STATUS.md`. Assert `WorktreeTeardownError` IS raised. Assert evidence string contains `PROJECT_STATUS.md`.
>
> 3. `test_teardown_blocks_on_real_dirty_mixed_with_lifecycle` (~15 LOC). Mock porcelain to return a mix: `?? knowledge/decisions/in-progress-foo.md` PLUS ` M PROJECT_STATUS.md`. Assert `WorktreeTeardownError` IS raised. Assert evidence string contains `PROJECT_STATUS.md` but does NOT contain `in-progress-foo.md` (the lifecycle artifact was filtered out of the blocking list).
>
> 4. `test_teardown_blocks_on_dirty_source_file` (~10 LOC). Mock porcelain to return ` M bellows.py`. Assert `WorktreeTeardownError` IS raised. Confirms the original failure mode the pre-check was designed to catch is still caught.
>
> **Deliverable D — Existing-test regression check:**
>
> Per the original surface diagnostic, existing teardown tests may need fixture updates. Specifically:
> - `test_teardown_pauses_when_local_main_dirty`: if its mock porcelain output uses a path that now matches the lifecycle filter, the test will fail. Update the fixture to use ` M PROJECT_STATUS.md` (non-lifecycle) so the test still exercises the dirty-tree pause. Document any fixture change in the QA report.
> - `test_teardown_dirty_tree_evidence_contains_recovery_commands`: same potential fixture issue.
> - `test_teardown_proceeds_when_local_main_clean`: no change expected (empty porcelain → no blocking lines).
> - The four index.lock / worktree-removal tests: unaffected (mock porcelain returns empty string).
>
> Run the full `tests/` suite (`pytest tests/` from the bellows directory). Paste the last 25 lines of pytest output. Required: zero NEW failures beyond known carry-overs (the 4 worktree-context `test_decisions.py` failures + 1 long-standing `test_run_step_timeout`).
>
> **Deliverable E — Rule 20 self-check.**
>
> Run the canonical Rule 20 self-check from `RULE_20_SELF_CHECK_BLOCK.md` at the governance root. Use these values when filling in the template:
>
> - `plan_slug`: `executable-dirty-tree-precheck-filter-qa-2026-05-28`
> - `qa_report_path`: `/Users/marklehn/Developer/GitHub/bellows/knowledge/qa/executable-dirty-tree-precheck-filter-qa-2026-05-28.md`
> - `evidence_dir`: `/Users/marklehn/Developer/GitHub/bellows/knowledge/qa/evidence/executable-dirty-tree-precheck-filter-qa-2026-05-28/`
> - `required_evidence_files`: `["filter_positive_output.txt", "filter_negative_output.txt", "regex_coverage_output.txt", "full_suite_output.txt"]`
>
> Each evidence file captures the relevant pytest output (one per pytest invocation against the relevant test class or marker). Include the literal stdout output of the Rule 20 block in the QA report. If the block prints `FAILED`, do not proceed with closure.
>
> ### Output Receipt requirements
>
> - Deliverables A-E each with a section header.
> - Verification Checks table at the top filled with PASS/FAIL/N/A per deliverable.
> - For Deliverable D, report total test count, passed/failed/skipped, time elapsed.
> - Flags for CEO: any test fixture modification beyond the documented PROJECT_STATUS.md substitution, any negative-match in Deliverable B that the regex unexpectedly matched or unexpectedly rejected, any failed test in Deliverable C (this would indicate the filter is over-permissive — CRITICAL escalation), confirmation that BACKLOG #1 and #2 can be closed.
> - At final-step close, update `PROJECT_STATUS.md` with one line summarizing the ship (per Rule 8).
>
> Standard prompt feedback protocol → `bellows/knowledge/research/agent-prompt-feedback.md`.
>
> **Deposits:**
> - `bellows/knowledge/qa/executable-dirty-tree-precheck-filter-qa-2026-05-28.md`
> - `bellows/knowledge/qa/evidence/executable-dirty-tree-precheck-filter-qa-2026-05-28/` (multiple files per Rule 20 self-check)
> - `bellows/tests/test_bellows.py`

---

## BACKLOG closures (on QA pass)

- **BACKLOG #1** (Dirty-tree pre-check false-trips on Bellows's own lifecycle artifacts) — closes.
- **BACKLOG #2** (Failed teardown strands worktree → next-step worktree-creation cascade) — closes as subsumed by #1 per diagnostic Section 4 (cascade chain verified during session-14 reproduction).
