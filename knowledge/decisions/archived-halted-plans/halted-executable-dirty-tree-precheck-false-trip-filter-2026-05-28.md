# Bellows — Dirty-Tree Pre-Check False-Trip Filter

**Date:** 2026-05-28 | **Tier:** Small | **Dispatch Mode:** bellows | **Test Scope:** targeted | **Execution:** Step 1 (DEV) → Step 2 (QA) | **qa_steps:** 2 | **pause_for_verdict:** after_step_1

## Context

Closes BACKLOG #1 (and #2 by subsumption). The `worktree_teardown_dirty_tree` pre-check shipped session 12 (commit `6252f8c`) fires on any non-empty `git status --porcelain` output before the teardown cherry-pick. Session 13 observed three false-trips across two plans, every trip on Bellows's own untracked lifecycle bookkeeping artifacts — none on real cherry-pick conflicts. Session 14 reproduced the same trip on the diagnostic that characterized this surface (recovery via R2 sub-variant A).

The session-14 SA diagnostic at `bellows/knowledge/research/dirty-tree-precheck-false-trip-surface-2026-05-28.md` produced a verified filter-rule table. Section 1 enumerates 8 lifecycle artifact patterns exhaustively against source code. Section 2 classifies each against cherry-pick conflict semantics (case-A modification, case-B untracked-overwrite) — all 8 are safe-to-ignore; `PROJECT_STATUS.md`, tracked source files, `knowledge/research/` tracked files, and submodule pointers correctly remain in the must-still-block category. Section 3 specifies the `_LIFECYCLE_IGNORE_RE` regex and `_is_lifecycle_artifact()` predicate. Section 6 specifies the test surface, including the critical negative test `test_teardown_blocks_on_non_lifecycle_untracked` proving the filter does NOT mask real conflicts.

**This executable mechanizes the diagnostic's filter spec directly.** No design decisions — those were made in the diagnostic. The executable's job is faithful implementation plus the test surface that proves both directions: false-trips closed, real conflicts still caught.

**BACKLOG #2 (failed teardown strands worktree → blocks next step's worktree creation) closes by subsumption** when this ships. The session-13 cascade was caused entirely by the false-trip — the diagnostic's Section 4 confirmed via timestamp chain that fixing #1 eliminates the cascade. Real-source-conflict cascade case is correctly preserved as feature (worktree preservation for manual recovery).

**Out of scope:**
- No governance changes (PLANNER_TEMPLATE, agent files). The Rule 25 routing sub-note for `worktree_teardown_dirty_tree` remains a separate deferred item.
- No copy-back logic changes (operates post-cherry-pick; diagnostic confirmed no interaction).
- No submodule-pointer-specific rule (block by default per diagnostic Section 5.2; revisit if governance-root plans are added).

**Daemon restart required after Step 2** to load the new `bellows.py`.

## How to Run This Plan

Two-step plan, sequential. Step 1 ships the filter in `bellows.py`; Step 2 verifies the filter closes the false-trip without masking real conflicts.

---
---

## STEP 1 — DEV

---

> **FIRST — before doing anything else, claim this plan:** rename `executable-dirty-tree-precheck-false-trip-filter-2026-05-28.md` to `in-progress-executable-dirty-tree-precheck-false-trip-filter-2026-05-28.md` using `mv` in the worktree. **THEN, immediately and BEFORE any other reads or work: post a short visible message to chat (1-2 sentences) confirming you have claimed the plan and stating your immediate next action.** This is a liveness anchor. **AFTER posting confirmation:** read `bellows/agents/BELLOWS_DEVELOPER.md` first, then read the files listed below.
>
> Acting as the Bellows Developer, implement the lifecycle-artifact filter for the `worktree_teardown_dirty_tree` pre-check per the diagnostic spec. The diagnostic at `bellows/knowledge/research/dirty-tree-precheck-false-trip-surface-2026-05-28.md` is the authoritative source for the filter pattern, the predicate function shape, and the test surface. Cite it for any design choice.
>
> **Files to read (post a 1-line "Read X." acknowledgment after each):**
>
> 1. `bellows/agents/BELLOWS_DEVELOPER.md` — specialist scope.
> 2. `bellows/knowledge/research/dirty-tree-precheck-false-trip-surface-2026-05-28.md` — diagnostic spec. Section 3 (filter predicate + implementation), Section 5 (edge cases), Section 6 (test surface). These are the spec.
> 3. `bellows/bellows.py` — current state of `_teardown_worktree` (lines 799-914), with focus on the pre-check at lines ~857-896 (the existing blanket `if dt_result.stdout.strip()` predicate, the `WorktreeTeardownError` evidence string construction, and the recovery instructions).
> 4. `bellows/tests/test_bellows.py` — locate existing teardown tests: `test_teardown_pauses_when_local_main_dirty`, `test_teardown_proceeds_when_local_main_clean`, `test_teardown_dirty_tree_evidence_contains_recovery_commands`, and the four index.lock / worktree-removal teardown tests cited in the original surface diagnostic at `worktree-teardown-dirty-tree-precheck-surface-2026-05-27.md` Section 4.
>
> **Drafting markers:** Post a 1-line "Implementing Fix N." marker at the start of each implementation section below.
>
> **Implementation 1 — `_LIFECYCLE_IGNORE_RE` and `_is_lifecycle_artifact()` helper.**
>
> Add a module-private regex and helper near the top of `bellows.py` (group with other module-level constants/helpers; the diagnostic suggests adjacency to the `_teardown_worktree` function but module-level is also acceptable — DEV's discretion based on existing code organization). The regex must cover all 8 patterns from the diagnostic Section 3 table. Verbatim from the diagnostic:
>
> ```python
> _LIFECYCLE_IGNORE_RE = re.compile(
>     r'^knowledge/decisions/(in-progress-|verdict-pending-|halted-|executable-|diagnostic-).*\.md$'
>     r'|^knowledge/decisions/Done/'
>     r'|^verdicts/(pending|resolved)/'
> )
>
> def _is_lifecycle_artifact(porcelain_line: str) -> bool:
>     """Return True if the porcelain line is a daemon-managed lifecycle artifact."""
>     if len(porcelain_line) < 4:
>         return False
>     path = porcelain_line[3:]
>     # Handle renamed files: "R  old -> new"
>     if " -> " in path:
>         path = path.split(" -> ", 1)[1]
>     return bool(_LIFECYCLE_IGNORE_RE.match(path.strip()))
> ```
>
> Confirm `import re` is already at the top of `bellows.py`; add if missing.
>
> **Implementation 2 — Pre-check filter integration.**
>
> In `_teardown_worktree` at the pre-check site (lines ~857-896, the block immediately before the cherry-pick loop), replace the blanket dirty-tree predicate with a filter pass. Current behavior raises `WorktreeTeardownError` if `dt_result.stdout.strip()` is non-empty. New behavior:
>
> ```python
> dirty_lines = dt_result.stdout.strip().splitlines()
> blocking_lines = [line for line in dirty_lines if not _is_lifecycle_artifact(line)]
> if blocking_lines:
>     # raise WorktreeTeardownError with blocking_lines in evidence
>     ...
> ```
>
> Preserve the existing evidence-string format and recovery instructions for the `blocking_lines` content. Update the evidence string's dirty-file count to use `len(blocking_lines)` (not the total `dirty_lines` count). ADD a single line to the evidence string noting filtered count: e.g., `"({len(dirty_lines) - len(blocking_lines)} lifecycle artifacts filtered, {len(blocking_lines)} blocking file(s) remain)"`. The recovery instructions (Sub-variant A / Sub-variant B) stay unchanged.
>
> The fail-open behavior on `git status` subprocess failure (existing handling at the original surface diagnostic Section 7 #3 recommendation) is unchanged.
>
> ### Constraints
>
> - No edits outside `bellows.py`.
> - The helper and regex must be module-private (underscore prefix).
> - No changes to the copy-back logic (lines ~915-938) — diagnostic Section 5.3 confirmed no interaction.
> - No changes to `_create_worktree` — BACKLOG #2 closes by subsumption per diagnostic Section 4.
> - `import re` at top of file (add if absent).
> - The filter regex must be EXACTLY the diagnostic's spec — do not rewrite for "clarity" or "performance." Byte-for-byte fidelity to the diagnostic.
>
> ### Output Receipt requirements
>
> - List exact post-edit line ranges for: the `_LIFECYCLE_IGNORE_RE` definition, the `_is_lifecycle_artifact()` function, the modified pre-check block.
> - Paste the final `_is_lifecycle_artifact()` function signature + docstring (no body).
> - Paste the final evidence-string format (the `f"worktree_teardown_dirty_tree: ..."` block) showing the new filtered-count line.
> - Confirm `_create_worktree` was NOT modified.
> - Confirm the copy-back logic at lines ~915-938 was NOT modified.
> - Run `python3 -c "import bellows; print('ok')"` from the bellows directory; paste stdout. Catches import errors before QA.
>
> Standard prompt feedback protocol → `bellows/knowledge/research/agent-prompt-feedback.md`.
>
> **Deposits:**
> - `bellows/bellows.py`
> - `bellows/knowledge/development/dirty-tree-precheck-false-trip-filter-2026-05-28.md`
>
> **STOP. Do NOT proceed to Step 2. Do NOT move the plan to Done. Wait for CEO confirmation before continuing.**

---
---

## STEP 2 — QA

---

> Before starting, read `bellows/knowledge/development/dirty-tree-precheck-false-trip-filter-2026-05-28.md` and check the Output Receipt status field. If status is not Complete, stop and report the issue to the CEO before proceeding.
>
> Acting as Bellows QA, verify the lifecycle-artifact filter closes the false-trip without masking real cherry-pick conflicts. The diagnostic at `bellows/knowledge/research/dirty-tree-precheck-false-trip-surface-2026-05-28.md` Section 6 is the authoritative test-surface spec.
>
> **Files to read (post a 1-line "Read X." acknowledgment after each):**
>
> 1. `bellows/agents/BELLOWS_QA.md` — specialist scope.
> 2. `bellows/knowledge/research/dirty-tree-precheck-false-trip-surface-2026-05-28.md` — diagnostic. Section 6 is the test-surface spec.
> 3. `bellows/knowledge/development/dirty-tree-precheck-false-trip-filter-2026-05-28.md` — DEV log from Step 1. Verify Step 1's claimed line ranges.
> 4. `bellows/bellows.py` — post-Step-1 state. Locate `_LIFECYCLE_IGNORE_RE`, `_is_lifecycle_artifact()`, and the modified pre-check block.
> 5. `bellows/tests/test_bellows.py` — locate existing teardown tests for fixture updates (per diagnostic Section 6).
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
> - `_LIFECYCLE_IGNORE_RE` regex exists in `bellows.py` matching the diagnostic Section 3 spec byte-for-byte. Paste the regex.
> - `_is_lifecycle_artifact()` exists with the signature and body from the diagnostic Section 3.
> - The pre-check block uses `[line for line in dirty_lines if not _is_lifecycle_artifact(line)]` filter and `if blocking_lines:` predicate.
> - The evidence string contains the new filtered-count annotation.
> - `_create_worktree` is unchanged (cite `git --no-pager diff HEAD~1 bellows.py` output focused on `_create_worktree` — should show no changes to that function).
> - The copy-back logic at lines ~915-938 is unchanged.
>
> **Deliverable B — Filter-positive tests (false-trip closure):**
>
> Add new tests in `tests/test_bellows.py`:
>
> 1. `test_teardown_ignores_lifecycle_artifacts` (~15 LOC). Mock `subprocess.run` so `git status --porcelain` with `cwd=project_path` returns ONLY lifecycle artifact lines (at minimum: `?? knowledge/decisions/in-progress-foo.md`, `?? knowledge/decisions/verdict-pending-foo.md`, `?? knowledge/decisions/halted-foo.md`, `?? knowledge/decisions/Done/foo.md`, `?? verdicts/pending/verdict-request-foo-step-1.md`, `?? verdicts/resolved/processed-verdict-foo-step-1.md`). Assert NO `WorktreeTeardownError` is raised. Assert the cherry-pick subprocess call IS attempted (the rest of teardown proceeds).
>
> 2. `test_teardown_ignores_deletion_porcelain_codes` (~10 LOC). Mock porcelain to return ` D knowledge/decisions/executable-foo.md` and `D  knowledge/decisions/diagnostic-foo.md` (deletion side of claim-rename). Assert NO `WorktreeTeardownError`. This test exercises the diagnostic's Section 1 #5 deletion pattern explicitly — the session-13 trips were all `??` codes, but the filter must handle deletion codes too.
>
> 3. `test_lifecycle_artifact_regex_coverage` (~20 LOC). Unit test for `_is_lifecycle_artifact()`. Verify positive matches for: `?? knowledge/decisions/in-progress-foo.md`, `?? knowledge/decisions/verdict-pending-foo.md`, `?? knowledge/decisions/halted-foo.md`, `?? knowledge/decisions/executable-foo.md`, `?? knowledge/decisions/diagnostic-foo.md`, `?? knowledge/decisions/Done/foo.md`, `?? knowledge/decisions/Done/nested/foo.md`, `?? verdicts/pending/anything.md`, `?? verdicts/resolved/anything.md`. Verify negative matches (must NOT be ignored) for: `?? knowledge/decisions/roadmap-foo.md`, `?? knowledge/decisions/parallel-1-executable-foo.md` (parallel prefix — diagnostic should clarify in QA's flags if this is a gap), `?? knowledge/research/foo.md`, ` M PROJECT_STATUS.md`, ` M bellows.py`, ` M bellows` (submodule pointer).
>
> **Deliverable C — Filter-negative tests (critical safety — proves filter does NOT mask real conflicts):**
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
> Per diagnostic Section 6, existing teardown tests may need fixture updates. Specifically:
> - `test_teardown_pauses_when_local_main_dirty` (added by session-12 executable): if the test's mock porcelain output uses a path that now matches the lifecycle filter, the test will fail. Update the fixture to use ` M PROJECT_STATUS.md` (a non-lifecycle path) so the test still exercises the dirty-tree pause. Document any fixture changes in the QA report.
> - `test_teardown_dirty_tree_evidence_contains_recovery_commands`: same potential fixture issue. Update if needed.
> - `test_teardown_proceeds_when_local_main_clean`: no change expected (empty porcelain → no blocking lines).
> - The four index.lock / worktree-removal tests: unaffected (mock porcelain returns empty string).
>
> Run the full `tests/test_bellows.py` suite (or `pytest tests/` for the project). Paste the last 20 lines of pytest output. Required: zero NEW failures beyond known carry-overs (the 4 worktree-context `test_decisions.py` failures + 1 long-standing `test_run_step_timeout`).
>
> **Deliverable E — Rule 20 self-check.**
>
> Run the canonical Rule 20 self-check from `RULE_20_SELF_CHECK_BLOCK.md` at the governance root. Use these values when filling in the template:
>
> - `plan_slug`: `executable-dirty-tree-precheck-false-trip-filter-2026-05-28`
> - `qa_report_path`: `/Users/marklehn/Developer/GitHub/bellows/knowledge/qa/executable-dirty-tree-precheck-false-trip-filter-2026-05-28.md`
> - `evidence_dir`: `/Users/marklehn/Developer/GitHub/bellows/knowledge/qa/evidence/executable-dirty-tree-precheck-false-trip-filter-2026-05-28/`
> - `required_evidence_files`: `["filter_positive_output.txt", "filter_negative_output.txt", "regex_coverage_output.txt", "full_suite_output.txt"]`
>
> Each evidence file captures the relevant pytest output. Include the literal stdout output of the Rule 20 block in the QA report. If the block prints `FAILED`, do not proceed with closure.
>
> ### Output Receipt requirements
>
> - Deliverables A-E each with a section header.
> - Verification Checks table filled with PASS/FAIL/N/A per deliverable.
> - For Deliverable D, report total test count, passed/failed/skipped, time elapsed.
> - Flags for CEO: any test fixture modification needed beyond the documented PROJECT_STATUS.md substitution, any negative-match in Deliverable B that the regex unexpectedly matched or unexpectedly rejected, any failed test in Deliverable C (this would indicate the filter is over-permissive — CRITICAL escalation).
> - At final-step close, update `PROJECT_STATUS.md` with one line summarizing the ship (per Rule 8).
>
> Standard prompt feedback protocol → `bellows/knowledge/research/agent-prompt-feedback.md`.
>
> **Deposits:**
> - `bellows/knowledge/qa/executable-dirty-tree-precheck-false-trip-filter-2026-05-28.md`
> - `bellows/knowledge/qa/evidence/executable-dirty-tree-precheck-false-trip-filter-2026-05-28/` (multiple files per Rule 20 self-check)
> - `bellows/tests/test_bellows.py`

---

## Daemon restart

After Step 2 ships and verdict continues to Done, the daemon MUST be restarted to load the new `bellows.py`. Bellows does not hot-reload code. Restart command: `pkill -f bellows.py && cd /Users/marklehn/Developer/GitHub/bellows && nohup python3 bellows.py >/dev/null 2>&1 &`.

## BACKLOG closures

When this ships:
- **BACKLOG #1** (Dirty-tree pre-check false-trips on Bellows's own lifecycle artifacts) — closes.
- **BACKLOG #2** (Failed teardown strands worktree → next-step worktree-creation cascade) — closes as subsumed by #1 per diagnostic Section 4.
