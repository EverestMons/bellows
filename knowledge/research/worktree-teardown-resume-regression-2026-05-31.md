# Worktree Teardown / Resume Regression — Diagnostic Findings

**Date:** 2026-05-31
**Author:** Planner (direct investigation, live during the no-match-dedup A/B session)
**Severity:** High — silently regresses multi-step plans at the Step-2 boundary and orphans un-landed commits.
**Status:** Root cause CONFIRMED via live reproduction + inverse confirmation. Fix is Opus-class (multi-file git-lifecycle reasoning). This document is the blueprint input for that executable.
**Reconciles BACKLOG items:** 2026-05-22 "Worktree teardown cherry-pick conflict on dirty PROJECT_STATUS.md (sequential-Planner-edit variant)" and 2026-05-30 (session 18) "Worktree re-creation on resume checks out main HEAD." These are the SAME failure family viewed from two angles.

---

## Summary

A multi-step Bellows plan loses Step 1's work at the Step-2 boundary when teardown fails at the Step-1 pause and a continue verdict is then issued. The trigger is a stray uncommitted non-lifecycle file on local main; the escalation path converts recoverable worktree commits into dangling commits. It is NOT restart-only (the 2026-05-30 framing) — it fires on a normal continue-resume.

---

## Confirmed mechanism (code, current as of this session)

Symbols, not line numbers (numbers drift; verify by symbol):

1. **`_create_worktree` (≈bellows.py:786)** creates every worktree with `git worktree add <wt_path> HEAD --detach` (≈:825) — always from local main HEAD, never from the step's branch/commit.

2. **`_create_worktree` stranded-cleanup (shipped commit `93b18ec`):** when `wt_path` already exists, it unconditionally treats it as "stranded from a prior failed dispatch" and removes it (`git worktree remove --force` → `shutil.rmtree(ignore_errors=True)` → `git worktree prune`), then recreates at HEAD. **It cannot distinguish a stranded worktree (failed dispatch, safe to nuke) from a live inter-step worktree (mid-plan, holds un-landed commits).**

3. **Pause path in `run_plan` (≈:547–551)** calls `_teardown_worktree` BEFORE posting the verdict-request. The intended inter-step model is teardown-per-pause: Step N's commits cherry-pick to local main, worktree is removed, and Step N+1's fresh worktree (from HEAD) inherits the work.

4. **`_teardown_worktree` (≈bellows.py:843)** step **(b2)** is a dirty-tree pre-check: if local main has uncommitted NON-lifecycle changes (`_is_lifecycle_artifact` filters in-progress-/verdict-pending-/halted-/Done//verdicts/ etc.), it raises `WorktreeTeardownError("worktree_teardown_dirty_tree: ...")` BEFORE the cherry-pick (c) and BEFORE worktree removal (e). Result: commits NOT landed on main, worktree LEFT ALIVE.

5. **Visibility gap:** a teardown failure appends to `gate_result["failures"]` AFTER the `gates step N: passed=True` terminal-log line is emitted. So the daemon log shows "passed=True"; the failure is visible only in the verdict-request **Gate Result JSON** and the verdicts ledger.

---

## Confirmed cascade (this session's reproduction)

1. Untracked non-lifecycle file on main: `bellows-speed-research-2026-05-29.md` in the repo root.
2. Step 1 (DEV) ran, committed the dedup work on the worktree's detached HEAD.
3. At the Step-1 pause, `_teardown_worktree` (b2) raised `worktree_teardown_dirty_tree` → cherry-pick skipped, worktree left alive. **Evidence:** verdicts/ledger.jsonl step-1 entry shows `gate_failures: [worktree_teardown — worktree_teardown_dirty_tree: local main has uncommitted changes]`.
4. Continue verdict issued over the failure (the gate JSON was not read before the verdict — see Discipline below).
5. Step-2 resume: `run_plan` → `_create_worktree` found the still-alive worktree → stranded-cleaned it (removed) → recreated at main HEAD (`99ad13f`, lacking Step 1's commit). **Step 1's commits became dangling** (recovered as `git fsck` dangling chain tipped at `858ab10`).
6. Step 2 (QA) ran against the regressed tree → `passed=False, failures=[deposit_exists×2, rule_20_self_check, rule_22_verification×2], files_changed=0` (accurate environmental blocker, not a QA-substance failure).

## Inverse confirmation (clean re-run)

After committing the stray doc (main clean), the identical plan re-ran: Step-1 teardown succeeded (`Pause Reason Code: header_pause`, no `worktree_teardown` failure), cherry-picked to main, removed the worktree; Step-2 resume created a fresh worktree from main HEAD that CONTAINED the dedup code (`grep -c _warned_no_match = 5`) and the dev log, and NO "stranded worktree found" warning fired. QA verified correctly. This confirms (b2) success ⇒ correct resume, and isolates the trigger to teardown failure.

---

## Pre/post-`93b18ec` symptom analysis (HYPOTHESIS — confirm during implementation)

- Pre-`93b18ec`, `_create_worktree` had no stranded-cleanup, so on a resume with an existing (un-removed) worktree it would error `fatal: '<path>' already exists` → `WorktreeCreationError` → a LOUD `worktree_creation` gate failure.
- Post-`93b18ec`, the same precondition is silently "cleaned" and recreated at HEAD → a SILENT regression of the tree.
- So `93b18ec` likely did not introduce the teardown-failure resume break; it changed the symptom from loud-failure to silent-regression — arguably worse. Multi-step plans only ever worked when teardown SUCCEEDED (worktree removed at pause ⇒ no collision at resume).

---

## Three contributing gaps + fix-shape options

**Gap 1 — continue silently advances past a failed teardown.**
- (a) Planner discipline: always read the verdict-request Gate Result JSON before issuing a verdict; a `worktree_teardown` failure routes to R2 recovery, never a plain continue. (process — see Discipline below)
- (b) Bellows refuses/blocks a continue when the prior step's gate result carries an uncleared `worktree_teardown` failure (force R2). (code)
- (c) On continue-resume, re-attempt teardown before advancing. (code)

**Gap 2 — stranded-cleanup orphans un-landed commits (2026-05-30 item).**
- (a) Before removing a "stranded" worktree, detect un-landed commits (worktree HEAD ahead of main) and reattach/preserve on a branch rather than destroy.
- (b) Recreate from the step's branch/commit instead of `HEAD --detach` when un-landed commits exist.
- (c) On resume, cherry-pick prior-step commits into the freshly-created worktree before running the next step.

**Gap 3 — dirty-tree teardown ergonomics / trigger (2026-05-22 item).**
- (a) Teardown auto-stashes local non-lifecycle changes before cherry-pick, unstashes after (risk: unstash conflict).
- (b) Clearer pause-for-CEO (partly present — the error already carries recovery instructions).
- (c) Planner discipline: never leave stray uncommitted non-lifecycle files in a watched repo root.

---

## Discipline points (for LESSONS)

1. **Read the verdict-request Gate Result JSON before every verdict.** The `gates step N: passed=True` daemon-log line is emitted BEFORE teardown; a `worktree_teardown` failure appends after it and is invisible there. Substance-checking the deposit is not sufficient — the mechanical gate result must be read. Issuing continue over a hidden teardown failure is what turned a recoverable state into the dangling-commit cascade this session.
2. **Never leave stray uncommitted non-lifecycle files in a watched repo root.** They trip `_teardown_worktree` (b2) on EVERY plan's teardown until cleared.

---

## Recommended sequencing for the fix executable (Opus-class)

Smallest-first, each independently shippable:
1. Gap 1(b) — block continue over an uncleared `worktree_teardown` failure (cheapest, highest safety value; stops the silent skip).
2. Gap 2(a/b) — preserve un-landed commits on stranded-cleanup (prevents the dangling-commit escalation / data-at-risk).
3. Gap 3(a) — teardown auto-stash (removes the most common trigger) — optional, evaluate against discipline point 2.

Note: this is a Bellows close/resume-path fix — the QA must be code-level only (a live multi-step integration smoke test inside the fix plan would trip the very bug during its own close/resume). Keep the fix plan single-pause where possible.

---

## Open items spun off (NOT part of this bug)

- 4× `test_decisions.py` failures (`TestLoadPhrases` ×3, `TestExtractDecisionBlocks::test_s_class_blocks_from_ground_truth`) + `test_run_step_timeout` — pre-existing carry-over, unrelated to `_consume_verdicts`. Separate hygiene item.
- QA step-log result-object anomaly (1 turn / 1.75s reported for a ~426s step) — logging oddity in `logs/*-step.json`, worth a glance, unrelated.
