# Bellows — Merge-FF Teardown Model (P0+P1+P2, retire cherry-pick)
**Date:** 2026-06-05 | **Tier:** Executable | **Dispatch Mode:** bellows | **Test Scope:** full | **Execution:** Step 1 (SA) → Step 2 (DEV) → Step 3 (QA) | **Priority:** 1

**auto_close:** false
**pause_for_verdict:** always

## Execution Map
Step 1 (SA: edit map + step-d consumer gate + invariant/migration mapping + regression-test plan) → Step 2 (DEV: implement) → Step 3 (QA: full regression + 6 teardown scenarios + Rule 20). Sequential.

## Context

Implements the root-cause verdict from `knowledge/research/teardown-dirty-main-rootcause-2026-06-05.md`: replace cherry-pick-onto-the-live-main-working-tree with `git merge` on a named worktree branch. Cherry-pick onto a checked-out tree is what makes working-tree dirtiness able to block landing; merge dissolves the entire dirty-tree failure class (pre-check, lifecycle filter, dirty-tree retry, parallel-SHA divergence).

Bundles three changes to the same two functions (split would leave dead code referencing removed paths):
- **P0** — landing: cherry-pick loop (`:999-1008`) → merge; `_create_worktree` (`:863`) creates a named branch `bellows-wt/<slug>` instead of detached HEAD.
- **P1** — remove step (d) dirty-file copy-back (GATED on Step 1 consumer trace).
- **P2** — remove the now-dead `_LIFECYCLE_IGNORE_RE` (`:42-48`), `_is_lifecycle_artifact()` (`:50-58`), and the (b2) dirty-tree pre-check (`:950-992`).
- **Also cut** `_retry_recoverable_teardown` (`:1055`) + its caller (`~:1438`): its trigger keys on `worktree_teardown_dirty_tree`, which can no longer occur — dead code referencing a removed concept.

**Precondition (satisfied by Plan A):** the anvil cycle report now writes to the worktree, so the common cycle no longer advances main mid-run → the ff happy path applies. Other main-advancers (manual CEO commits, agent origin pushes) remain, so the no-ff fallback is a permanent necessary path, not an edge.

**Landing + fallback policy (REVISED — no rebase):**
- Primary: `git merge --ff-only bellows-wt/<slug>` (cwd=project_path). Linear history, SHAs identical, when main has not advanced.
- Fallback when main advanced (ff impossible): `git merge --no-ff --no-edit bellows-wt/<slug>`. This adds a merge commit whose second parent is the worktree branch tip — **the worktree commit SHAs are preserved in history** (reachable via the merge), so the ledger / `processed-verdict` / gate-result SHAs remain valid. **No rebase, no SHA rewrite** — this deliberately avoids reintroducing the parallel-SHA divergence the redesign exists to kill.
- True content conflict (either merge path): `git merge --abort` and raise `WorktreeTeardownError` (worktree left alive for manual resolution → Gap 1b routing). A clean abort with no conflict markers, SHAs intact.
- SHAs are preserved on BOTH paths; the only history difference is a merge commit appears when (and only when) main advanced mid-run. Do not claim linear history in that case — claim SHA-stability, which is what matters for the ledger.

**Future-proofing — leave a tripwire, not just remove the guard.** We delete the pre-check/filter because merge makes working-tree dirtiness irrelevant *to landing*. That is a load-bearing assumption about all future teardown paths, not a permanent fact. A permanent named regression test must assert the invariant "landing does not require a clean main working tree," so if someone later reintroduces a checkout-based teardown step, a test goes red instead of a production teardown.

**Migration safety (one-time, on restart).** Worktrees created by the OLD daemon are detached-HEAD with no `bellows-wt/<slug>` branch; the new teardown would look for a branch that does not exist. `_teardown_worktree` must detect a branchless legacy worktree and raise a descriptive error (not fail undefined). Operationally, confirm zero live/stranded worktrees before the post-land daemon restart, and run the canary from a worktree-free state.

**Self-rewrite safety:** this plan rewrites the functions managing its own worktree. The running daemon uses in-memory (old, cherry-pick) code, so THIS plan's own teardown uses the pre-change model. The new model goes live only on **daemon restart** (manual, post-land) + **canary** (an anvil cycle, which now writes report-in-worktree per Plan A — exercising the ff happy path). QA validates the new code in-worktree; it cannot validate the restarted daemon. Rollback: canary fails → revert the bellows commit + restart.

## How to Run This Plan
Bellows dispatches normally; pauses after every step. Keep bellows main clean for the duration. **Before the post-land restart: confirm `git worktree list` shows no `.bellows-worktrees/` entries on any watched repo (no stranded legacy worktrees).** Then restart the daemon and run a canary anvil cycle from that clean state before trusting the new model. Revert + restart if the canary fails.

---
---

## STEP 1 — BELLOWS SYSTEMS ANALYST

---

> **Identity:** You are the Bellows Systems Analyst. Begin with `SA claim: merge-ff teardown edit map` BEFORE any reads. **Reads (in order):** `agents/BELLOWS_SYSTEMS_ANALYST.md`; `knowledge/research/teardown-dirty-main-rootcause-2026-06-05.md`; `bellows.py` lines 38-60, 140, 792-880, 881-1054, 1055-1090, ~1430-1445. Ack each read.
>
> **Task:** Produce a precise edit map + regression-test plan. No source changes. Sandbox git checks in a /tmp throwaway repo. Prefix each section with a 1-line marker.
>
> (1) **Step-(d) consumer trace — HARD GATE.** Prove nothing reads the files step (d) copies back off main (`grep -rn "shutil.copy" bellows.py`; trace `gates.py`, `bellows.py`, runner). **Verdict line:** REMOVE-SAFE or KEEP-AS-LOG, with evidence.
> (2) **`_create_worktree` edit map.** Replace the add cmd (`:863`, `HEAD --detach`) to create branch `bellows-wt/<slug>`. Confirm slug→git-ref-name safety (sanitize illegal chars); note code assuming detached HEAD. Add sequential-invariant fail-fast: if `bellows-wt/<slug>` already exists, fail loudly at creation.
> (3) **`_teardown_worktree` edit map.** Exact old→new for: (a) REMOVE the (b2) pre-check (`:950-992`); (b) REPLACE cherry-pick loop (`:999-1008`) with `git merge --ff-only bellows-wt/<slug>` (cwd=project_path); (c) **ff-fail fallback = `git merge --no-ff --no-edit bellows-wt/<slug>`** (NOT rebase — preserves worktree SHAs as merge parents); (d) on true content conflict (either merge), `git merge --abort` and raise `WorktreeTeardownError`; (e) **branch-cleanup ordering AND lifecycle**: on success, ff/no-ff merge (project_path) → remove worktree → `git branch -d bellows-wt/<slug>`; on halt (conflict raise), the worktree + branch persist for manual resolution — specify how stranded-worktree cleanup also deletes the branch so branches do not leak over time; (f) **legacy-worktree migration**: if `bellows-wt/<slug>` does not exist (a pre-merge-model detached-HEAD worktree), raise a descriptive `WorktreeTeardownError` naming the legacy condition rather than failing undefined; (g) step (d) per gate (1). Preserve the step (b) commit-enumeration.
> (4) **Cut `_retry_recoverable_teardown`** (`:1055`) + caller (`~:1438`); confirm no other callers. Document rebase-conflict path no longer exists; teardown conflict → `WorktreeTeardownError` → Gap-1b halt is the only recovery.
> (5) **P2 dead-code removal map.** Exact ranges: `_LIFECYCLE_IGNORE_RE` (`:42-48`), `_is_lifecycle_artifact()` (`:50-58`). Grep-confirm zero remaining callers after pre-check removal.
> (6) **Regression-test plan (permanent, tmp-repo fixtures, NO writes outside tmp).** Specify these pytest cases for `tests/test_worktree.py`: (i) **`test_landing_tolerates_dirty_main_invariant`** — dirty non-overlapping main → lands clean, dirty preserved; docstring states the INVARIANT "landing must never require a clean main working tree; if this breaks, a checkout-based teardown step was reintroduced"; (ii) dirty overlapping main → clean abort, NO conflict markers, raises; (iii) main advanced, no conflict → ff fails → `--no-ff` merge lands, worktree commit SHAs still present in history; (iv) main advanced, true conflict → `merge --abort` → raises, no partial state; (v) SHA identity: ff path main tip == worktree tip; no-ff path worktree SHAs reachable from merge commit; (vi) legacy branchless worktree → descriptive `WorktreeTeardownError`. Plus a test-impact list for existing tests in `tests/test_worktree.py`, `tests/test_bellows.py`, `tests/test_consume_verdicts.py` (keep/update/delete + new expectations).
> (7) **Contract composition check.** Verify the 2026-06-05 raise-on-log-failure contract still composes with merge semantics (it was written against cherry-pick) — confirm it triggers correctly on the merge path or specify the adjustment. State findings; mark OPEN if unsure.
>
> Mark anything unsettled OPEN — do not let DEV guess. Standard prompt-feedback protocol.
>
> **Deposits:**
> - `knowledge/architecture/teardown-merge-model-blueprint-2026-06-05.md`

---
---

## STEP 2 — BELLOWS DEVELOPER

---

> Before starting, read `knowledge/architecture/teardown-merge-model-blueprint-2026-06-05.md`; if any item is OPEN (esp. the step-(d) gate or §7 contract check), STOP and report.
>
> **Identity:** You are the Bellows Developer. Begin with `DEV claim: merge-ff teardown impl`. **Reads:** `agents/BELLOWS_DEVELOPER.md`, the blueprint, the cited `bellows.py` regions. Ack each.
>
> **Scope — you will edit exactly these files:** `bellows.py`, `tests/test_worktree.py`, `tests/test_bellows.py`, `tests/test_consume_verdicts.py`. Nothing else.
>
> **Task:** Implement the blueprint exactly, `python3 -m pytest tests/ -q` after each logical change:
> 1. `_create_worktree` → named branch `bellows-wt/<slug>` + sequential-invariant fail-fast (§2).
> 2. `_teardown_worktree` → `--ff-only` primary, `--no-ff` fallback, `merge --abort`+raise on conflict, branch-cleanup ordering + stranded-branch cleanup, legacy-worktree descriptive raise (§3 a–g).
> 3. Step (d): remove or log-only per §1 gate.
> 4. Remove the (b2) pre-check, `_LIFECYCLE_IGNORE_RE`, `_is_lifecycle_artifact()` (§5); grep-confirm zero callers.
> 5. Cut `_retry_recoverable_teardown` + caller (§4).
> 6. Add the 6 permanent regression tests to `tests/test_worktree.py` using tmp-repo fixtures (§6); update affected existing tests.
> 7. Apply any §7 adjustment to the raise-on-log-failure contract; do NOT silently drop it.
>
> **Self-verify before deposit:** full `pytest tests/` green (baseline 460 — record exact, count rises by the 6 new tests); grep shows zero live references to `_is_lifecycle_artifact`, `_LIFECYCLE_IGNORE_RE`, `_retry_recoverable_teardown`, `cherry-pick`/`cherry_pick`; the SHA-identity test (v) and the invariant test (i) pass; no `rebase` introduced anywhere in the teardown path.
>
> If blueprint and code disagree, STOP and flag — do not reconcile silently. Standard prompt-feedback protocol.
>
> **Deposits:**
> - `bellows.py`
> - `tests/test_worktree.py`
> - `tests/test_bellows.py`
> - `tests/test_consume_verdicts.py`
> - `knowledge/development/teardown-merge-model-impl-2026-06-05.md` (changes, per-edit pytest, final count, SHA-identity note, dead-symbol grep, confirmation no `rebase` in teardown). Output Receipt.

---
---

## STEP 3 — BELLOWS QA

---

> Before starting, read `knowledge/development/teardown-merge-model-impl-2026-06-05.md`; if Status not Complete, STOP.
>
> **Identity:** You are the Bellows QA Analyst. Begin with `QA claim: merge-ff teardown regression`. **Reads:** `agents/BELLOWS_QA.md`, blueprint, dev log. Evidence → `knowledge/qa/evidence/executable-bellows-teardown-merge-model-2026-06-05/` (`mkdir -p`).
>
> **MANDATORY — DO NOT SKIP (gate-enforced):** This step is REJECTED by the daemon's `rule_20_self_check` gate unless your QA report contains the literal banner `Rule 20 — QA Self-Check Results` followed by `PASSED — SELF-CHECK PASSED`. The verification table does NOT satisfy this. You MUST run the canonical Rule 20 block (check (6)) and paste its FULL stdout into the report under a `## Rule 20 Self-Check` heading. Before finishing, grep your own report for the banner; if absent, you have NOT completed this step.
>
> (1) **Full suite (Rule 21).** `pytest tests/ -q > .../pytest_full.txt 2>&1`. All green; count ≥ 466 (460 + 6 new); flag unexpected baseline moves.
> (2) **Dead-symbol + no-rebase.** `grep -rn "_is_lifecycle_artifact\|_LIFECYCLE_IGNORE_RE\|_retry_recoverable_teardown\|cherry-pick\|cherry_pick\|rebase" bellows.py > .../dead_symbols.txt 2>&1`. Expected: no live references and NO `rebase` in the teardown path (history comment acceptable; flag a live call).
> (3) **6 scenario tests present + passing.** `pytest tests/test_worktree.py -q -k "invariant or dirty or merge or ff or sha or legacy or conflict" > .../scenarios.txt 2>&1`. Confirm all six exist and pass; record names. Explicitly confirm `test_landing_tolerates_dirty_main_invariant` is present (the future-proofing tripwire).
> (4) **Clean abort, no markers.** From the overlapping-conflict and true-conflict tests, confirm assertions for no conflict markers + clean raise + no partial state. Evidence to `.../abort_clean.txt`.
> (5) **QA report** `knowledge/qa/2026-06-05-teardown-merge-model-qa.md` with `| Check | Expected | Status | Evidence |` over (1)-(4). Hedging in a ✅ row auto-fails.
> (6) **Rule 20 self-check — REQUIRED, gate-enforced.** Copy `/Users/marklehn/Developer/GitHub/RULE_20_SELF_CHECK_BLOCK.md` VERBATIM, replace ONLY the four placeholders: `plan_slug = "executable-bellows-teardown-merge-model-2026-06-05"`, `qa_report_path = "/Users/marklehn/Developer/GitHub/bellows/knowledge/qa/2026-06-05-teardown-merge-model-qa.md"`, `evidence_dir = "/Users/marklehn/Developer/GitHub/bellows/knowledge/qa/evidence/executable-bellows-teardown-merge-model-2026-06-05/"`, `required_evidence_files = ["pytest_full.txt","dead_symbols.txt","scenarios.txt","abort_clean.txt"]`. Run with `python3`; paste FULL stdout (banner + PASSED line) under `## Rule 20 Self-Check`. If FAILED, fix and re-run. Agent does NOT move to Done — Planner issues the terminal verdict.
>
> **Final self-verify:** `grep -c "Rule 20 — QA Self-Check Results" knowledge/qa/2026-06-05-teardown-merge-model-qa.md` ≥1.
>
> Standard prompt-feedback protocol.
>
> **Deposits:**
> - `knowledge/qa/2026-06-05-teardown-merge-model-qa.md` (MUST contain the Rule 20 banner + PASSED line)
> - `knowledge/qa/evidence/executable-bellows-teardown-merge-model-2026-06-05/`
